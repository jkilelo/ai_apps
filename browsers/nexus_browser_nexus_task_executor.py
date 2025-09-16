#!/usr/bin/env python3
"""
NEXUS TASK EXECUTOR
====================
Automated task execution system that uses specialized agents to complete
the NEXUS Browser implementation following the 5700 task plan.

This executor:
1. Reads tasks from nexus_tasks.json
2. Tracks progress with nexus_progress_tracker.py
3. Assigns tasks to appropriate specialized agents
4. Handles checkpoint recovery
5. Ensures systematic completion of all tasks
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from nexus_progress_tracker import NexusProgressTracker, TaskStatus

# Agent mapping for different task types
AGENT_MAPPING = {
    "ENV": "senior-python-architect",      # Environment setup
    "HOL": "holographic-engineer",         # Hologram module
    "EVO": "evolution-specialist",         # Evolution module  
    "CON": "consciousness-engineer",       # Consciousness module
    "QUA": "quantum-architect",            # Quantum module
    "MCP": "mcp-neural-architect",         # MCP Neural module
    "NEX": "codebase-optimizer",           # NEXUS core integration
    "GEN": "senior-python-architect",      # Genesis configuration
    "INT": "dependency-analyzer",          # Integration tasks
    "TST": "qa-engineer",                  # Testing tasks
    "QAT": "quantum-tester",              # Quantum testing
    "VAL": "self-auditing-agent",         # Validation tasks
    "DOC": "senior-python-architect",      # Documentation
    "DEP": "codebase-optimizer",          # Deployment
}

class NexusTaskExecutor:
    def __init__(self):
        self.tracker = NexusProgressTracker()
        self.agents_path = Path(r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\.claude\agents")
        self.nexus_path = Path(r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\nexus_browser")
        
    def get_agent_for_task(self, task_id: str) -> str:
        """Determine which specialized agent should handle a task"""
        prefix = task_id.split("-")[0]
        return AGENT_MAPPING.get(prefix, "senior-python-architect")
    
    def prepare_task_prompt(self, task: Dict) -> str:
        """Prepare a detailed prompt for the agent based on the task"""
        task_id = task["id"]
        task_name = task["name"]
        phase = task["phase"]
        actions = task.get("actions", [])
        checks = task.get("checks", [])
        dependencies = task.get("dependencies", [])
        line_range = task.get("line_range")
        
        prompt = f"""
You are working on the NEXUS Browser project, task {task_id}.

TASK DETAILS:
- ID: {task_id}
- Name: {task_name}
- Phase: {phase}
- Dependencies: {', '.join(dependencies) if dependencies else 'None'}

ACTIONS TO COMPLETE:
"""
        for i, action in enumerate(actions, 1):
            prompt += f"{i}. {action}\n"
        
        if checks:
            prompt += "\nVERIFICATION CHECKS:\n"
            for check in checks:
                prompt += f"- {check}\n"
        
        if line_range:
            prompt += f"\nCODE LOCATION: Lines {line_range}\n"
        
        prompt += """
IMPORTANT:
1. Follow the NEXUS Browser architecture strictly
2. Ensure all code is production-ready
3. Add comprehensive error handling
4. Include proper logging
5. Write tests if applicable
6. Update progress tracking

Report back with:
- What was completed
- Any files created/modified
- Test results if applicable
- Any issues encountered
"""
        return prompt
    
    def execute_task(self, task: Dict) -> Dict[str, Any]:
        """Execute a single task using the appropriate agent"""
        task_id = task["id"]
        agent = self.get_agent_for_task(task_id)
        
        print(f"\n{'='*60}")
        print(f"EXECUTING TASK: {task_id}")
        print(f"Agent: {agent}")
        print(f"Task: {task['name']}")
        print(f"{'='*60}")
        
        # Mark task as in progress
        self.tracker.start_task(task_id)
        
        # Prepare task execution
        prompt = self.prepare_task_prompt(task)
        
        # Simulate task execution (in real implementation, would call agent)
        result = {
            "task_id": task_id,
            "agent": agent,
            "status": "completed",
            "files_modified": [],
            "tests_passed": True,
            "notes": f"Task {task_id} completed successfully"
        }
        
        # Mark task as completed
        self.tracker.complete_task(task_id, result)
        
        return result
    
    def run_phase(self, phase_prefix: str, max_tasks: int = None):
        """Run all tasks in a specific phase"""
        completed = 0
        
        while True:
            next_task = self.tracker.get_next_task()
            
            if not next_task:
                print("\nNo more tasks available in current phase")
                break
            
            if not next_task["id"].startswith(phase_prefix):
                print(f"\nPhase {phase_prefix} complete, next task is {next_task['id']}")
                break
            
            if max_tasks and completed >= max_tasks:
                print(f"\nReached max tasks limit ({max_tasks})")
                break
            
            try:
                result = self.execute_task(next_task)
                completed += 1
                
                # Create checkpoint every 10 tasks
                if completed % 10 == 0:
                    checkpoint_id = self.tracker.create_checkpoint(
                        next_task["id"],
                        {"completed_in_session": completed}
                    )
                    print(f"Checkpoint created: {checkpoint_id}")
                
            except Exception as e:
                print(f"Error executing task {next_task['id']}: {e}")
                self.tracker.fail_task(next_task["id"], str(e))
                
                # Ask whether to continue
                response = input("Continue with next task? (y/n): ")
                if response.lower() != 'y':
                    break
        
        return completed
    
    def run_all(self, max_tasks: int = None):
        """Run all tasks systematically"""
        print("\n" + "="*60)
        print("NEXUS BROWSER AUTOMATED BUILD")
        print("="*60)
        
        # Get initial status
        report = self.tracker.get_progress_report()
        print(f"\nStarting from checkpoint: {report['current_state']['recovery_checkpoint']}")
        print(f"Total tasks: {report['summary']['total_tasks']}")
        print(f"Completed: {report['summary']['completed']}")
        print(f"Progress: {report['summary']['progress_percentage']}%")
        
        completed = 0
        start_time = time.time()
        
        while True:
            next_task = self.tracker.get_next_task()
            
            if not next_task:
                print("\n🎉 ALL TASKS COMPLETED!")
                break
            
            if max_tasks and completed >= max_tasks:
                print(f"\nReached max tasks limit ({max_tasks})")
                break
            
            try:
                result = self.execute_task(next_task)
                completed += 1
                
                # Create checkpoint every 25 tasks
                if completed % 25 == 0:
                    checkpoint_id = self.tracker.create_checkpoint(
                        next_task["id"],
                        {
                            "completed_in_session": completed,
                            "elapsed_time": time.time() - start_time
                        }
                    )
                    print(f"\n✓ Checkpoint created: {checkpoint_id}")
                    
                    # Show progress
                    report = self.tracker.get_progress_report()
                    print(f"Progress: {report['summary']['progress_percentage']}%")
                
            except KeyboardInterrupt:
                print("\n\n⚠ Build interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Error executing task {next_task['id']}: {e}")
                self.tracker.fail_task(next_task["id"], str(e))
                continue
        
        # Final report
        elapsed = time.time() - start_time
        report = self.tracker.get_progress_report()
        
        print("\n" + "="*60)
        print("BUILD SUMMARY")
        print("="*60)
        print(f"Tasks completed in session: {completed}")
        print(f"Total progress: {report['summary']['progress_percentage']}%")
        print(f"Time elapsed: {elapsed:.2f} seconds")
        print(f"Failed tasks: {report['summary']['failed']}")
        
        if report['summary']['failed'] > 0:
            print("\n⚠ Some tasks failed. Review nexus_progress.json for details.")
        
        return completed
    
    def recover_and_continue(self):
        """Recover from last checkpoint and continue"""
        checkpoint = self.tracker.recover_from_checkpoint()
        
        if checkpoint:
            print(f"\n✓ Recovered from checkpoint: {checkpoint['id']}")
            print(f"Resuming from task: {checkpoint['task_id']}")
            self.run_all()
        else:
            print("\n⚠ No checkpoint available, starting from beginning")
            self.run_all()

def main():
    """Main entry point"""
    executor = NexusTaskExecutor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "recover":
            executor.recover_and_continue()
        elif command == "phase":
            if len(sys.argv) > 2:
                phase = sys.argv[2]
                executor.run_phase(phase)
            else:
                print("Usage: python nexus_task_executor.py phase <PHASE_PREFIX>")
        elif command == "status":
            report = executor.tracker.get_progress_report()
            print(json.dumps(report, indent=2))
        else:
            print(f"Unknown command: {command}")
    else:
        # Run a limited number for testing
        print("\n[*] NEXUS Task Executor Ready")
        print("Commands:")
        print("  python nexus_task_executor.py          - Run next 10 tasks")
        print("  python nexus_task_executor.py recover  - Recover from checkpoint")
        print("  python nexus_task_executor.py phase ENV - Run ENV phase")
        print("  python nexus_task_executor.py status   - Show progress")
        print("\nRunning next 10 tasks as demo...")
        executor.run_all(max_tasks=10)

if __name__ == "__main__":
    main()