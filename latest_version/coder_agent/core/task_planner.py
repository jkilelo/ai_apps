#!/usr/bin/env python3
"""
Task Planner - Implements B.R.E.A.K. methodology for task planning
Based on CODER v3.1 TODO list management contract
"""

import uuid
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import structlog

from ..contracts.base import (
    TaskPlan, TodoItem, TaskStatus, TaskPriority,
    AgentRequest
)


logger = structlog.get_logger()


class TaskPlanner:
    """
    Implements B.R.E.A.K. methodology for task planning.
    B - Break down complex tasks
    R - Review dependencies
    E - Establish priorities
    A - Analyze complexity
    K - Keep track of progress
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.plans_created = 0
        self.task_patterns = self._load_task_patterns()
        
    async def create_plan(
        self, 
        request: AgentRequest, 
        context: Dict[str, Any]
    ) -> TaskPlan:
        """
        Create a comprehensive task plan using B.R.E.A.K.
        """
        logger.info("Creating task plan", task=request.task)
        
        # B - Break down the task
        tasks = await self._break_down_task(request, context)
        
        # R - Review and establish dependencies
        tasks = self._establish_dependencies(tasks)
        
        # E - Establish priorities
        tasks = self._prioritize_tasks(tasks)
        
        # A - Analyze complexity and estimate tokens
        tasks = self._analyze_complexity(tasks)
        
        # K - Create tracking structure
        plan = TaskPlan(
            plan_id=str(uuid.uuid4()),
            objective=request.task,
            tasks=tasks,
            total_estimated_tokens=sum(t.estimated_tokens for t in tasks),
            max_parallel_tasks=self._determine_parallelism(tasks)
        )
        
        self.plans_created += 1
        logger.info("Task plan created", 
                   plan_id=plan.plan_id,
                   task_count=len(tasks),
                   estimated_tokens=plan.total_estimated_tokens)
        
        return plan
    
    async def revise_plan(
        self, 
        plan: TaskPlan, 
        issues: List[Dict[str, Any]]
    ) -> TaskPlan:
        """
        Revise plan based on validation issues.
        """
        logger.info("Revising task plan", plan_id=plan.plan_id, issues=len(issues))
        
        for issue in issues:
            if issue.get("type") == "missing_dependency":
                # Add missing dependency
                self._add_dependency(plan, issue)
            elif issue.get("type") == "circular_dependency":
                # Break circular dependency
                self._break_circular_dependency(plan, issue)
            elif issue.get("type") == "resource_conflict":
                # Adjust parallelism
                plan.max_parallel_tasks = 1
            elif issue.get("type") == "complexity_too_high":
                # Further break down complex tasks
                plan = await self._reduce_complexity(plan, issue)
        
        return plan
    
    async def _break_down_task(
        self, 
        request: AgentRequest, 
        context: Dict[str, Any]
    ) -> List[TodoItem]:
        """
        B - Break down complex task into manageable subtasks.
        """
        tasks = []
        
        # Determine task type and apply appropriate pattern
        task_type = self._classify_task(request.task)
        pattern = self.task_patterns.get(task_type, self.task_patterns["generic"])
        
        # Apply CODER phases as tasks
        if request.require_tests:
            # Phase 0: Pre-flight
            tasks.append(TodoItem(
                content="Run pre-flight checks",
                priority=TaskPriority.CRITICAL,
                estimated_tokens=100
            ))
        
        # Phase 1: Context gathering
        if task_type in ["refactor", "debug", "optimize"]:
            tasks.append(TodoItem(
                content="Analyze existing codebase and gather context",
                priority=TaskPriority.HIGH,
                estimated_tokens=500
            ))
        
        # Phase 2: Objectives (always needed)
        tasks.append(TodoItem(
            content="Define clear objectives and success criteria",
            priority=TaskPriority.HIGH,
            estimated_tokens=200
        ))
        
        # Phase 3: Design
        if task_type in ["feature", "refactor", "system"]:
            # TDD: Write tests first
            if request.require_tests:
                tasks.append(TodoItem(
                    content="Write tests for the new functionality (TDD)",
                    priority=TaskPriority.CRITICAL,
                    estimated_tokens=1000
                ))
            
            tasks.append(TodoItem(
                content="Design solution architecture",
                priority=TaskPriority.HIGH,
                estimated_tokens=300
            ))
        
        # Phase 4: Execute - Core implementation tasks
        core_tasks = self._generate_core_tasks(request, task_type, context)
        tasks.extend(core_tasks)
        
        # Phase 5: Review
        if request.require_tests:
            tasks.append(TodoItem(
                content="Run test suite and verify all tests pass",
                priority=TaskPriority.CRITICAL,
                estimated_tokens=500
            ))
        
        tasks.append(TodoItem(
            content="Validate code quality and run linters",
            priority=TaskPriority.HIGH,
            estimated_tokens=300
        ))
        
        tasks.append(TodoItem(
            content="Review changes and document if needed",
            priority=TaskPriority.MEDIUM,
            estimated_tokens=200
        ))
        
        return tasks
    
    def _establish_dependencies(self, tasks: List[TodoItem]) -> List[TodoItem]:
        """
        R - Review and establish task dependencies.
        """
        # Map tasks by content patterns for dependency linking
        task_map = {task.id: task for task in tasks}
        
        for i, task in enumerate(tasks):
            # Pre-flight must complete first
            if "pre-flight" in task.content.lower():
                continue  # No dependencies
            
            # Tests depend on pre-flight
            if "write tests" in task.content.lower():
                preflight = self._find_task_by_pattern(tasks, "pre-flight")
                if preflight:
                    task.dependencies.append(preflight.id)
            
            # Implementation depends on tests (TDD)
            if any(word in task.content.lower() for word in ["implement", "create", "build"]):
                test_task = self._find_task_by_pattern(tasks, "write tests")
                if test_task:
                    task.dependencies.append(test_task.id)
                design_task = self._find_task_by_pattern(tasks, "design")
                if design_task:
                    task.dependencies.append(design_task.id)
            
            # Testing depends on implementation
            if "run test" in task.content.lower():
                impl_tasks = [t for t in tasks if any(
                    word in t.content.lower() 
                    for word in ["implement", "create", "build", "fix", "refactor"]
                )]
                for impl_task in impl_tasks:
                    if impl_task.id not in task.dependencies:
                        task.dependencies.append(impl_task.id)
            
            # Review depends on testing
            if "review" in task.content.lower() or "validate" in task.content.lower():
                test_task = self._find_task_by_pattern(tasks, "run test")
                if test_task and test_task.id not in task.dependencies:
                    task.dependencies.append(test_task.id)
        
        return tasks
    
    def _prioritize_tasks(self, tasks: List[TodoItem]) -> List[TodoItem]:
        """
        E - Establish task priorities.
        """
        for task in tasks:
            # Already set priorities are kept
            if task.priority != TaskPriority.MEDIUM:
                continue
            
            # Determine priority based on content
            content_lower = task.content.lower()
            
            if any(word in content_lower for word in ["critical", "error", "fix", "bug"]):
                task.priority = TaskPriority.CRITICAL
            elif any(word in content_lower for word in ["test", "validate", "check"]):
                task.priority = TaskPriority.HIGH
            elif any(word in content_lower for word in ["implement", "create", "build"]):
                task.priority = TaskPriority.HIGH
            elif any(word in content_lower for word in ["document", "comment", "review"]):
                task.priority = TaskPriority.LOW
            else:
                task.priority = TaskPriority.MEDIUM
        
        return tasks
    
    def _analyze_complexity(self, tasks: List[TodoItem]) -> List[TodoItem]:
        """
        A - Analyze complexity and estimate resource usage.
        """
        for task in tasks:
            # Estimate tokens based on task type
            content_lower = task.content.lower()
            
            # Already estimated tasks
            if task.estimated_tokens > 0:
                continue
            
            # Estimate based on operation type
            if "search" in content_lower or "find" in content_lower:
                task.estimated_tokens = 500
            elif "implement" in content_lower or "create" in content_lower:
                task.estimated_tokens = 2000
            elif "test" in content_lower:
                task.estimated_tokens = 1000
            elif "refactor" in content_lower:
                task.estimated_tokens = 3000
            elif "analyze" in content_lower:
                task.estimated_tokens = 1500
            elif "document" in content_lower:
                task.estimated_tokens = 500
            else:
                task.estimated_tokens = 300
        
        return tasks
    
    def _determine_parallelism(self, tasks: List[TodoItem]) -> int:
        """
        Determine maximum parallel execution based on dependencies.
        """
        # Build dependency graph
        dependency_graph = {task.id: task.dependencies for task in tasks}
        
        # Find maximum width of independent tasks
        max_parallel = 1
        
        # Group tasks by dependency depth
        depths = self._calculate_dependency_depths(tasks)
        depth_groups = {}
        
        for task_id, depth in depths.items():
            if depth not in depth_groups:
                depth_groups[depth] = []
            depth_groups[depth].append(task_id)
        
        # Maximum parallel is the largest group at any depth
        for depth, group in depth_groups.items():
            max_parallel = max(max_parallel, len(group))
        
        # Cap at configured maximum
        max_parallel = min(max_parallel, self.config.get("max_parallel", 3))
        
        return max_parallel
    
    def _calculate_dependency_depths(self, tasks: List[TodoItem]) -> Dict[str, int]:
        """
        Calculate dependency depth for each task.
        """
        depths = {}
        task_map = {task.id: task for task in tasks}
        
        def get_depth(task_id: str, visited: Set[str]) -> int:
            if task_id in depths:
                return depths[task_id]
            
            if task_id in visited:
                # Circular dependency detected
                return 0
            
            visited.add(task_id)
            task = task_map.get(task_id)
            
            if not task or not task.dependencies:
                depth = 0
            else:
                depth = 1 + max(get_depth(dep, visited.copy()) 
                              for dep in task.dependencies)
            
            depths[task_id] = depth
            return depth
        
        for task in tasks:
            get_depth(task.id, set())
        
        return depths
    
    def _classify_task(self, task_description: str) -> str:
        """
        Classify task type based on description.
        """
        task_lower = task_description.lower()
        
        if any(word in task_lower for word in ["fix", "bug", "error", "issue"]):
            return "bugfix"
        elif any(word in task_lower for word in ["add", "implement", "create", "new"]):
            return "feature"
        elif any(word in task_lower for word in ["refactor", "improve", "optimize"]):
            return "refactor"
        elif any(word in task_lower for word in ["test", "testing", "coverage"]):
            return "testing"
        elif any(word in task_lower for word in ["document", "docs", "readme"]):
            return "documentation"
        elif any(word in task_lower for word in ["debug", "investigate", "analyze"]):
            return "debug"
        elif any(word in task_lower for word in ["deploy", "release", "publish"]):
            return "deployment"
        else:
            return "generic"
    
    def _generate_core_tasks(
        self, 
        request: AgentRequest, 
        task_type: str, 
        context: Dict[str, Any]
    ) -> List[TodoItem]:
        """
        Generate core implementation tasks based on type.
        """
        tasks = []
        
        if task_type == "bugfix":
            tasks.extend([
                TodoItem(
                    content="Reproduce the bug and understand root cause",
                    priority=TaskPriority.CRITICAL,
                    estimated_tokens=1000
                ),
                TodoItem(
                    content="Implement fix for the bug",
                    priority=TaskPriority.CRITICAL,
                    estimated_tokens=1500
                ),
                TodoItem(
                    content="Add regression test to prevent recurrence",
                    priority=TaskPriority.HIGH,
                    estimated_tokens=800
                )
            ])
        
        elif task_type == "feature":
            tasks.extend([
                TodoItem(
                    content="Implement core functionality",
                    priority=TaskPriority.HIGH,
                    estimated_tokens=3000
                ),
                TodoItem(
                    content="Add error handling and edge cases",
                    priority=TaskPriority.HIGH,
                    estimated_tokens=1500
                ),
                TodoItem(
                    content="Integrate with existing codebase",
                    priority=TaskPriority.HIGH,
                    estimated_tokens=1000
                )
            ])
        
        elif task_type == "refactor":
            tasks.extend([
                TodoItem(
                    content="Analyze current implementation",
                    priority=TaskPriority.HIGH,
                    estimated_tokens=1000
                ),
                TodoItem(
                    content="Refactor code while maintaining functionality",
                    priority=TaskPriority.HIGH,
                    estimated_tokens=2500
                ),
                TodoItem(
                    content="Ensure all tests still pass",
                    priority=TaskPriority.CRITICAL,
                    estimated_tokens=500
                )
            ])
        
        else:
            # Generic implementation task
            tasks.append(TodoItem(
                content=f"Execute main task: {request.task[:100]}",
                priority=TaskPriority.HIGH,
                estimated_tokens=2000
            ))
        
        return tasks
    
    def _find_task_by_pattern(self, tasks: List[TodoItem], pattern: str) -> Optional[TodoItem]:
        """Find a task by content pattern."""
        pattern_lower = pattern.lower()
        for task in tasks:
            if pattern_lower in task.content.lower():
                return task
        return None
    
    def _load_task_patterns(self) -> Dict[str, Any]:
        """Load common task patterns."""
        return {
            "bugfix": {
                "phases": ["reproduce", "fix", "test", "verify"],
                "priority": TaskPriority.CRITICAL
            },
            "feature": {
                "phases": ["design", "implement", "test", "integrate", "document"],
                "priority": TaskPriority.HIGH
            },
            "refactor": {
                "phases": ["analyze", "plan", "refactor", "test", "optimize"],
                "priority": TaskPriority.MEDIUM
            },
            "testing": {
                "phases": ["analyze_coverage", "write_tests", "run_tests", "verify"],
                "priority": TaskPriority.HIGH
            },
            "generic": {
                "phases": ["analyze", "implement", "test", "review"],
                "priority": TaskPriority.MEDIUM
            }
        }