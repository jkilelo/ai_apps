#!/usr/bin/env python3
"""
CODER Agent Core Engine - Implements Claude's reasoning patterns
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import structlog

from ..contracts.base import (
    AgentRequest, AgentResponse, TaskPlan, TodoItem, TaskStatus,
    ToolCall, ToolResult, ToolType, ContextWindow, ContextItem,
    ValidationResult, PreflightResult
)
from .metacognition import MetacognitionEngine
from .context_manager import ContextManager
from .tool_executor import ToolExecutor
from .task_planner import TaskPlanner
from .engine_helpers import EngineHelpers
from .code_generator import CodeGenerator


logger = structlog.get_logger()


class CoderEngine:
    """
    Core engine implementing Claude's internal reasoning patterns.
    This is the heart of the CODER Agent.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.context_manager = ContextManager(config.get("context", {}))
        self.tool_executor = ToolExecutor(config.get("tools", {}))
        self.task_planner = TaskPlanner(config.get("planner", {}))
        self.metacognition = MetacognitionEngine(config.get("meta", {}))
        self.code_generator = CodeGenerator(config.get("llm", {}))
        
        # State tracking
        self.current_plan: Optional[TaskPlan] = None
        self.execution_history: List[Dict[str, Any]] = []
        self.total_tokens_used = 0
        
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Main execution flow following CODER v3.1 principles.
        """
        start_time = time.time()
        logger.info("Starting CODER Agent execution", task=request.task)
        
        try:
            # Phase 0: Pre-flight checks
            preflight = await self._run_preflight_checks(request)
            if not preflight.can_proceed:
                return self._create_error_response(
                    request, 
                    "Pre-flight checks failed", 
                    preflight.errors,
                    time.time() - start_time
                )
            
            # Phase 1: Context - Understand the request
            context = await self._understand_context(request)
            
            # Phase 2: Objectives - Create task plan using B.R.E.A.K.
            self.current_plan = await self.task_planner.create_plan(request, context)
            logger.info("Created task plan", tasks=len(self.current_plan.tasks))
            
            # Phase 3: Design - Validate and optimize plan
            validation = await self._validate_plan(self.current_plan)
            if not validation.passed:
                self.current_plan = await self.task_planner.revise_plan(
                    self.current_plan, 
                    validation.failures
                )
            
            # Phase 4: Execute - Run the plan
            execution_result = await self._execute_plan(self.current_plan)
            
            # Phase 5: Review - Validate results
            review_result = await self._review_execution(execution_result)
            
            # Create response
            return AgentResponse(
                success=review_result.get("success", False),
                result=execution_result,
                changes=self._extract_changes(execution_result),
                tests_run=self._extract_tests(execution_result),
                errors=review_result.get("errors", []),
                warnings=review_result.get("warnings", []),
                duration_seconds=time.time() - start_time,
                tokens_used=self.total_tokens_used
            )
            
        except Exception as e:
            logger.error("Execution failed", error=str(e))
            return self._create_error_response(
                request,
                f"Execution failed: {str(e)}",
                [str(e)],
                time.time() - start_time
            )
    
    async def _run_preflight_checks(self, request: AgentRequest) -> PreflightResult:
        """
        Run comprehensive pre-flight checks (CODER v3.1 requirement).
        """
        checks = []
        
        # Check 1: Virtual environment
        venv_check = await self._check_virtual_environment()
        checks.append(venv_check)
        
        # Check 2: LLM connectivity
        llm_check = await self._check_llm_connection()
        checks.append(llm_check)
        
        # Check 3: Project directory
        if request.project_path:
            project_check = await self._check_project_directory(request.project_path)
            checks.append(project_check)
        
        # Check 4: Required tools
        tools_check = await self._check_required_tools()
        checks.append(tools_check)
        
        # Check 5: Platform compatibility
        if request.platform != "any":
            platform_check = await self._check_platform(request.platform)
            checks.append(platform_check)
        
        all_passed = all(c.passed for c in checks if c.severity == "critical")
        warnings = [c.message for c in checks if not c.passed and c.severity == "warning"]
        errors = [c.message for c in checks if not c.passed and c.severity == "critical"]
        
        return PreflightResult(
            all_passed=all_passed,
            checks=checks,
            can_proceed=all_passed,
            warnings=warnings,
            errors=errors
        )
    
    async def _understand_context(self, request: AgentRequest) -> Dict[str, Any]:
        """
        Phase 1: Context - Deep understanding of the request.
        Implements Claude's multi-layer understanding.
        """
        context = {
            "literal_request": request.task,
            "inferred_intent": await self._infer_intent(request),
            "required_capabilities": await self._assess_capabilities(request),
            "constraints": request.constraints,
            "confidence_level": 0.0
        }
        
        # Use metacognition to assess understanding
        meta_assessment = await self.metacognition.assess_understanding(context)
        context["confidence_level"] = meta_assessment.get("confidence", 0.5)
        
        # If low confidence, gather more context
        if context["confidence_level"] < 0.7:
            additional_context = await self._gather_additional_context(request)
            context.update(additional_context)
        
        return context
    
    async def _execute_plan(self, plan: TaskPlan) -> Dict[str, Any]:
        """
        Phase 4: Execute - Run the task plan.
        Implements intelligent task execution with parallelization.
        """
        results = []
        completed_tasks = set()
        failed_tasks = set()
        
        while len(completed_tasks) + len(failed_tasks) < len(plan.tasks):
            # Get next executable tasks
            next_tasks = [
                t for t in plan.get_next_tasks()
                if t.id not in completed_tasks and t.id not in failed_tasks
            ]
            
            if not next_tasks:
                # Check for deadlock
                if self._detect_deadlock(plan, completed_tasks, failed_tasks):
                    logger.error("Deadlock detected in task execution")
                    break
                await asyncio.sleep(0.1)
                continue
            
            # Execute tasks (potentially in parallel)
            if len(next_tasks) == 1:
                result = await self._execute_single_task(next_tasks[0])
            else:
                result = await self._execute_parallel_tasks(next_tasks)
            
            # Update task statuses
            for task_result in result if isinstance(result, list) else [result]:
                task_id = task_result.get("task_id")
                if task_result.get("success"):
                    completed_tasks.add(task_id)
                    self._update_task_status(plan, task_id, TaskStatus.COMPLETED)
                else:
                    failed_tasks.add(task_id)
                    self._update_task_status(plan, task_id, TaskStatus.FAILED)
                    
                    # Attempt recovery
                    recovery = await self._attempt_recovery(task_result)
                    if recovery.get("success"):
                        completed_tasks.add(task_id)
                        failed_tasks.remove(task_id)
                        self._update_task_status(plan, task_id, TaskStatus.COMPLETED)
                
                results.append(task_result)
            
            # Metacognitive check
            meta_check = await self.metacognition.check_execution_quality(results)
            if meta_check.get("needs_adjustment"):
                await self._adjust_execution_strategy(meta_check)
        
        return {
            "plan": plan,
            "results": results,
            "completed": list(completed_tasks),
            "failed": list(failed_tasks)
        }
    
    async def _execute_single_task(self, task: TodoItem) -> Dict[str, Any]:
        """
        Execute a single task with full monitoring.
        """
        logger.info("Executing task", task_id=task.id, content=task.content)
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()
        
        try:
            # Determine required tools
            tools = await self._determine_tools_for_task(task)
            
            # Execute tools in sequence (following my contract rules)
            tool_results = []
            for tool_call in tools:
                # Check context before each tool
                if not self.context_manager.can_add_tokens(tool_call.estimated_tokens):
                    await self.context_manager.compress_context()
                
                result = await self.tool_executor.execute(tool_call)
                tool_results.append(result)
                
                # Update token usage
                self.total_tokens_used += result.tokens_used
                task.actual_tokens = (task.actual_tokens or 0) + result.tokens_used
                
                # Check for early failure
                if not result.success and tool_call.tool in [ToolType.TEST, ToolType.VALIDATE]:
                    break
            
            success = all(r.success for r in tool_results)
            task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
            task.completed_at = datetime.now()
            
            return {
                "task_id": task.id,
                "success": success,
                "tool_results": tool_results,
                "duration": (task.completed_at - task.started_at).total_seconds()
            }
            
        except Exception as e:
            logger.error("Task execution failed", task_id=task.id, error=str(e))
            task.status = TaskStatus.FAILED
            task.error = str(e)
            return {
                "task_id": task.id,
                "success": False,
                "error": str(e)
            }
    
    async def _execute_parallel_tasks(self, tasks: List[TodoItem]) -> List[Dict[str, Any]]:
        """
        Execute multiple tasks in parallel (simulated).
        Real parallel execution would require true async tools.
        """
        # In reality, I execute sequentially but simulate parallelization
        # by batching similar operations
        logger.info("Executing parallel tasks", count=len(tasks))
        
        # Group by tool type for efficiency
        grouped_tasks = self._group_tasks_by_type(tasks)
        results = []
        
        for tool_type, task_group in grouped_tasks.items():
            if tool_type in [ToolType.READ, ToolType.GREP, ToolType.BASH]:
                # These can be batched
                batch_result = await self._execute_batch(task_group, tool_type)
                results.extend(batch_result)
            else:
                # Execute sequentially
                for task in task_group:
                    result = await self._execute_single_task(task)
                    results.append(result)
        
        return results
    
    async def _review_execution(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 5: Review - Validate execution results.
        """
        review = {
            "success": False,
            "errors": [],
            "warnings": []
        }
        
        # Check if all required tasks completed
        plan = execution_result.get("plan")
        completed = execution_result.get("completed", [])
        failed = execution_result.get("failed", [])
        
        if failed:
            review["errors"].append(f"Failed tasks: {failed}")
        
        # Run tests if required
        if self.config.get("require_tests", True):
            test_results = await self._run_test_suite(execution_result)
            if not test_results.get("all_passed"):
                review["errors"].append("Tests failed")
                review["test_failures"] = test_results.get("failures", [])
        
        # Validate code quality
        quality_check = await self._check_code_quality(execution_result)
        if quality_check.get("issues"):
            review["warnings"].extend(quality_check.get("issues", []))
        
        # Overall success determination
        review["success"] = len(review["errors"]) == 0
        
        # Metacognitive final check
        meta_review = await self.metacognition.final_review(review)
        if meta_review.get("concerns"):
            review["warnings"].extend(meta_review.get("concerns", []))
        
        return review
    
    # Helper methods
    
    def _create_error_response(
        self, 
        request: AgentRequest, 
        message: str, 
        errors: List[str],
        duration: float
    ) -> AgentResponse:
        """Create error response."""
        return AgentResponse(
            success=False,
            result=None,
            changes=[],
            tests_run=[],
            errors=[message] + errors,
            warnings=[],
            duration_seconds=duration,
            tokens_used=self.total_tokens_used
        )
    
    def _update_task_status(self, plan: TaskPlan, task_id: str, status: TaskStatus):
        """Update task status in plan."""
        for task in plan.tasks:
            if task.id == task_id:
                task.status = status
                break
    
    def _detect_deadlock(
        self, 
        plan: TaskPlan, 
        completed: set, 
        failed: set
    ) -> bool:
        """Detect if execution is deadlocked."""
        remaining = [
            t for t in plan.tasks 
            if t.id not in completed and t.id not in failed
        ]
        
        if not remaining:
            return False
        
        # Check if any remaining task can execute
        for task in remaining:
            deps_satisfied = all(
                dep_id in completed for dep_id in task.dependencies
            )
            if deps_satisfied:
                return False
        
        return True
    
    def _extract_changes(self, execution_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract file changes from execution results."""
        changes = []
        for result in execution_result.get("results", []):
            for tool_result in result.get("tool_results", []):
                if tool_result.get("tool") in [ToolType.WRITE, ToolType.EDIT]:
                    changes.append({
                        "file": tool_result.get("file"),
                        "operation": tool_result.get("tool"),
                        "success": tool_result.get("success")
                    })
        return changes
    
    def _extract_tests(self, execution_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract test results from execution."""
        tests = []
        for result in execution_result.get("results", []):
            for tool_result in result.get("tool_results", []):
                if tool_result.get("tool") == ToolType.TEST:
                    tests.append({
                        "test": tool_result.get("test_name"),
                        "passed": tool_result.get("success"),
                        "output": tool_result.get("output")
                    })
        return tests
    
    # Helper method implementations using EngineHelpers
    
    async def _check_virtual_environment(self):
        return await EngineHelpers.check_virtual_environment()
    
    async def _check_llm_connection(self):
        return await EngineHelpers.check_llm_connection()
    
    async def _check_project_directory(self, project_path: str):
        return await EngineHelpers.check_project_directory(project_path)
    
    async def _check_required_tools(self):
        return await EngineHelpers.check_required_tools()
    
    async def _check_platform(self, platform: str):
        return await EngineHelpers.check_platform(platform)
    
    async def _infer_intent(self, request: AgentRequest):
        return await EngineHelpers.infer_intent(request)
    
    async def _assess_capabilities(self, request: AgentRequest):
        return await EngineHelpers.assess_capabilities(request)
    
    async def _gather_additional_context(self, request: AgentRequest):
        return await EngineHelpers.gather_additional_context(request)
    
    async def _determine_tools_for_task(self, task: TodoItem):
        return await EngineHelpers.determine_tools_for_task(task)
    
    def _group_tasks_by_type(self, tasks: List[TodoItem]):
        return EngineHelpers.group_tasks_by_type(tasks)
    
    async def _attempt_recovery(self, task_result: Dict[str, Any]):
        return await EngineHelpers.attempt_recovery(task_result)
    
    async def _adjust_execution_strategy(self, meta_check: Dict[str, Any]):
        """Adjust execution strategy based on metacognitive feedback"""
        adjustments = meta_check.get("adjustments", [])
        for adjustment in adjustments:
            logger.info(f"Applying adjustment: {adjustment}")
    
    async def _execute_batch(self, tasks: List[TodoItem], tool_type: str):
        """Execute a batch of similar tasks"""
        results = []
        for task in tasks:
            result = await self._execute_single_task(task)
            results.append(result)
        return results
    
    async def _run_test_suite(self, execution_result: Dict[str, Any]):
        return await EngineHelpers.run_test_suite(execution_result)
    
    async def _check_code_quality(self, execution_result: Dict[str, Any]):
        return await EngineHelpers.check_code_quality(execution_result)
    
    async def _validate_plan(self, plan: TaskPlan) -> ValidationResult:
        """Validate the task plan"""
        from ..contracts.base import ValidationResult
        
        failures = []
        warnings = []
        
        # Check for circular dependencies
        for task in plan.tasks:
            if task.id in task.dependencies:
                failures.append({
                    "type": "circular_dependency",
                    "task": task.id,
                    "message": "Task depends on itself"
                })
        
        # Check for missing dependencies
        all_task_ids = {t.id for t in plan.tasks}
        for task in plan.tasks:
            for dep in task.dependencies:
                if dep not in all_task_ids:
                    failures.append({
                        "type": "missing_dependency",
                        "task": task.id,
                        "dependency": dep,
                        "message": f"Dependency {dep} not found"
                    })
        
        # Check token estimates
        if plan.total_estimated_tokens > 150000:
            warnings.append("Plan may exceed context window")
        
        return ValidationResult(
            passed=len(failures) == 0,
            rules_checked=3,
            failures=failures,
            warnings=warnings,
            duration_ms=10
        )
    
    async def _reduce_complexity(self, plan: TaskPlan, issue: Dict[str, Any]) -> TaskPlan:
        """Reduce complexity of plan"""
        # Simplified implementation
        logger.info("Reducing plan complexity", issue=issue)
        return plan
    
    def _add_dependency(self, plan: TaskPlan, issue: Dict[str, Any]):
        """Add missing dependency to plan"""
        task_id = issue.get("task")
        dep_id = issue.get("dependency")
        
        for task in plan.tasks:
            if task.id == task_id and dep_id not in task.dependencies:
                task.dependencies.append(dep_id)
    
    def _break_circular_dependency(self, plan: TaskPlan, issue: Dict[str, Any]):
        """Break circular dependency in plan"""
        task_id = issue.get("task")
        
        for task in plan.tasks:
            if task.id == task_id and task_id in task.dependencies:
                task.dependencies.remove(task_id)