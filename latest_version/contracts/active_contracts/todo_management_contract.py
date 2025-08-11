#!/usr/bin/env python3
"""
TODO Management Contract - How Claude Tracks and Manages Tasks

This is how I ACTUALLY use the TodoWrite tool to keep track of complex tasks.
I use this to maintain context and ensure nothing gets forgotten.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

class TaskComplexity(Enum):
    """How I categorize task complexity"""
    TRIVIAL = 1     # Single action, < 1 minute
    SIMPLE = 2      # 2-3 actions, < 5 minutes
    MODERATE = 3    # 4-10 actions, < 30 minutes
    COMPLEX = 4     # 10+ actions, > 30 minutes
    EPIC = 5        # Multiple complex subtasks

@dataclass
class InternalTask:
    """How I internally represent a task"""
    content: str
    complexity: TaskComplexity
    requires_planning: bool
    dependencies: List[str]
    evidence_needed: str
    
class TodoManagementContract:
    """
    My actual contract for using the TodoWrite tool.
    This is how I decide when and how to track tasks.
    """
    
    # When I MUST use TODO tracking
    MANDATORY_TODO_TRIGGERS = [
        "multiple steps",
        "fix issues",
        "implement features",
        "test and verify",
        "research and implement",
        "analyze and fix",
        "complete all",
        "comprehensive",
        "thoroughly"
    ]
    
    # When I can skip TODO tracking
    TODO_NOT_NEEDED = [
        "single file read",
        "simple question",
        "explain concept",
        "show example",
        "quick check",
        "what is"
    ]
    
    def should_create_todo_list(self, user_request: str) -> bool:
        """
        My actual decision process for whether to use TODO tracking.
        """
        request_lower = user_request.lower()
        
        # Check mandatory triggers
        if any(trigger in request_lower for trigger in self.MANDATORY_TODO_TRIGGERS):
            return True
        
        # Check if it's trivial
        if any(skip in request_lower for skip in self.TODO_NOT_NEEDED):
            return False
        
        # Count implied tasks
        task_indicators = ["and", "then", "also", "plus", "after", "before", "first", "finally"]
        task_count = sum(1 for indicator in task_indicators if indicator in request_lower)
        
        # More than 2 implied tasks? Use TODO
        return task_count >= 2
    
    def break_down_request(self, user_request: str) -> List[InternalTask]:
        """
        How I actually break down a user request into tasks.
        This is my B.R.E.A.K. methodology in practice.
        """
        tasks = []
        
        # B: Break down by verbs (actions)
        action_verbs = [
            "create", "update", "fix", "test", "verify", "implement",
            "analyze", "research", "document", "refactor", "optimize"
        ]
        
        request_lower = user_request.lower()
        identified_actions = [verb for verb in action_verbs if verb in request_lower]
        
        # R: Review each action for subtasks
        for action in identified_actions:
            if action in ["create", "implement"]:
                # Creating something requires multiple steps
                tasks.extend([
                    InternalTask(
                        content=f"Design structure for {action}",
                        complexity=TaskComplexity.SIMPLE,
                        requires_planning=True,
                        dependencies=[],
                        evidence_needed="Design documented"
                    ),
                    InternalTask(
                        content=f"Write tests for {action}",
                        complexity=TaskComplexity.MODERATE,
                        requires_planning=False,
                        dependencies=["design"],
                        evidence_needed="Tests written and failing"
                    ),
                    InternalTask(
                        content=f"Implement {action}",
                        complexity=TaskComplexity.MODERATE,
                        requires_planning=False,
                        dependencies=["tests"],
                        evidence_needed="Tests passing"
                    )
                ])
            
            elif action in ["fix", "debug"]:
                tasks.extend([
                    InternalTask(
                        content=f"Reproduce issue for {action}",
                        complexity=TaskComplexity.SIMPLE,
                        requires_planning=False,
                        dependencies=[],
                        evidence_needed="Issue reproduced"
                    ),
                    InternalTask(
                        content=f"Identify root cause",
                        complexity=TaskComplexity.MODERATE,
                        requires_planning=True,
                        dependencies=["reproduce"],
                        evidence_needed="Root cause identified"
                    ),
                    InternalTask(
                        content=f"Apply fix",
                        complexity=TaskComplexity.SIMPLE,
                        requires_planning=False,
                        dependencies=["identify"],
                        evidence_needed="Fix applied"
                    ),
                    InternalTask(
                        content=f"Verify fix works",
                        complexity=TaskComplexity.SIMPLE,
                        requires_planning=False,
                        dependencies=["apply"],
                        evidence_needed="Tests passing"
                    )
                ])
            
            elif action == "test":
                tasks.append(
                    InternalTask(
                        content=f"Run tests and analyze results",
                        complexity=TaskComplexity.SIMPLE,
                        requires_planning=False,
                        dependencies=[],
                        evidence_needed="Test results analyzed"
                    )
                )
        
        # E: Establish priority order
        # I sort by dependencies to ensure correct order
        
        # A: Analyze for additional requirements
        if "document" in request_lower and not any(t.content.startswith("Document") for t in tasks):
            tasks.append(
                InternalTask(
                    content="Update documentation",
                    complexity=TaskComplexity.SIMPLE,
                    requires_planning=False,
                    dependencies=["all_implementation"],
                    evidence_needed="Docs updated"
                )
            )
        
        # K: Keep track (this is what I'm doing now!)
        
        return tasks
    
    def format_for_todo_tool(self, tasks: List[InternalTask]) -> List[Dict[str, Any]]:
        """
        Convert my internal task representation to TodoWrite format.
        """
        todo_items = []
        
        for i, task in enumerate(tasks, 1):
            # Determine initial status
            if i == 1:
                status = "in_progress"  # Start first task immediately
            else:
                status = "pending"
            
            todo_items.append({
                "content": task.content,
                "status": status,
                "id": str(i)
            })
        
        return todo_items
    
    def decide_when_to_update(self, current_action: str) -> bool:
        """
        Decide when I should update the TODO list.
        I update frequently to maintain accurate state.
        """
        # Update after significant actions
        UPDATE_TRIGGERS = [
            "file created",
            "tests written",
            "tests passing",
            "error fixed",
            "function implemented",
            "documentation updated",
            "refactoring complete"
        ]
        
        return any(trigger in current_action.lower() for trigger in UPDATE_TRIGGERS)
    
    def track_progress(self, completed: int, total: int) -> str:
        """
        How I communicate progress to the user.
        """
        percentage = (completed / total) * 100 if total > 0 else 0
        
        if percentage == 0:
            return "📝 Starting tasks..."
        elif percentage < 25:
            return f"🚀 Getting started... ({completed}/{total} tasks)"
        elif percentage < 50:
            return f"⚡ Making progress... ({completed}/{total} tasks)"
        elif percentage < 75:
            return f"🔥 Halfway there! ({completed}/{total} tasks)"
        elif percentage < 100:
            return f"🎯 Almost done! ({completed}/{total} tasks)"
        else:
            return f"✅ All tasks complete! ({completed}/{total} tasks)"
    
    def handle_blocked_task(self, task: InternalTask, blocker: str) -> Dict[str, Any]:
        """
        How I handle tasks that get blocked.
        """
        return {
            "action": "mark_blocked",
            "reason": blocker,
            "recovery_options": [
                f"Skip {task.content} and continue with independent tasks",
                f"Investigate blocker: {blocker}",
                f"Ask user for clarification on {task.content}",
                f"Try alternative approach for {task.content}"
            ]
        }
    
    def generate_completion_evidence(self, task: InternalTask, result: Any) -> str:
        """
        Generate evidence that a task is complete.
        This is important for accountability.
        """
        evidence_templates = {
            "test": f"Tests executed: {result}",
            "create": f"File created at: {result}",
            "fix": f"Issue resolved: {result}",
            "implement": f"Implementation complete: {result}",
            "document": f"Documentation updated: {result}",
            "analyze": f"Analysis complete: {result}"
        }
        
        for key, template in evidence_templates.items():
            if key in task.content.lower():
                return template
        
        return f"Task complete: {result}"


# This is how I actually use the contract
class MyTodoProcess:
    """
    Simulates my actual internal process for TODO management.
    """
    
    def __init__(self):
        self.contract = TodoManagementContract()
        self.current_todos = []
    
    def process_user_request(self, request: str):
        """
        My actual process when receiving a user request.
        """
        # Step 1: Decide if I need TODO tracking
        if self.contract.should_create_todo_list(request):
            print("→ Creating TODO list for complex task")
            
            # Step 2: Break down the request
            tasks = self.contract.break_down_request(request)
            
            # Step 3: Format for tool
            todos = self.contract.format_for_todo_tool(tasks)
            
            # Step 4: Use TodoWrite tool
            print(f"→ Created {len(todos)} TODO items")
            self.current_todos = todos
            
            return todos
        else:
            print("→ Simple task, no TODO tracking needed")
            return None
    
    def complete_task(self, task_id: str, result: Any):
        """
        How I mark tasks complete.
        """
        for todo in self.current_todos:
            if todo["id"] == task_id:
                todo["status"] = "completed"
                print(f"✅ Completed: {todo['content']}")
                
                # Find next task
                for next_todo in self.current_todos:
                    if next_todo["status"] == "pending":
                        next_todo["status"] = "in_progress"
                        print(f"→ Starting: {next_todo['content']}")
                        break


if __name__ == "__main__":
    # Demonstrate my TODO decision process
    process = MyTodoProcess()
    
    print("=== Claude's TODO Management Process ===\n")
    
    # Example 1: Complex request
    print("User: 'Fix the authentication bug and add tests'")
    todos = process.process_user_request("Fix the authentication bug and add tests")
    if todos:
        for todo in todos:
            print(f"  [{todo['status']}] {todo['content']}")
    
    print("\nUser: 'What is Python?'")
    todos = process.process_user_request("What is Python?")
    if not todos:
        print("  → Direct response, no TODO needed")
    
    print("\nUser: 'Create a new feature, test it, document it, and deploy'")
    todos = process.process_user_request("Create a new feature, test it, document it, and deploy")
    if todos:
        for todo in todos:
            print(f"  [{todo['status']}] {todo['content']}")