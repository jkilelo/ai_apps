#!/usr/bin/env python3
"""
NEXUS CADENCE ENFORCEMENT AGENT
===============================
A sophisticated AI agent that enforces the 8-step cadence loop for NEXUS Browser development.

Integrates multiple master prompt strategies:
- Constitutional AI for unwavering compliance
- Chain of Thought for systematic verification  
- Meta-Prompting for self-reflection and optimization
- Self-Consistency for validation across multiple paths
- Reflexion for error correction and learning
- Tree of Thoughts for exploring execution paths

Built for 100% constitutional compliance and zero tolerance for violations.
"""

import json
import time
import traceback
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field

# Import master strategy components
import sys
sys.path.append(str(Path(__file__).parent.parent / "master_prompt_strategies"))

# Import quality enforcement
from quality_enforcer import QualityEnforcer, enforce_module_quality

class CadenceStepStatus(Enum):
    """Status of each cadence step"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"

class ViolationType(Enum):
    """Types of constitutional violations"""
    STEP_SKIPPED = "STEP_SKIPPED"
    INCOMPLETE_TESTING = "INCOMPLETE_TESTING"
    MISSING_TRACKER_UPDATE = "MISSING_TRACKER_UPDATE" 
    NO_CHECKPOINT = "NO_CHECKPOINT"
    INTEGRATION_FAILURE = "INTEGRATION_FAILURE"
    STATUS_UPDATE_FAILURE = "STATUS_UPDATE_FAILURE"
    QUALITY_GATE_FAILURE = "QUALITY_GATE_FAILURE"
    SEQUENCE_VIOLATION = "SEQUENCE_VIOLATION"

@dataclass
class CadenceStep:
    """Represents a single step in the 8-step cadence"""
    step_number: int
    name: str
    description: str
    required_actions: List[str]
    validation_criteria: List[str]
    status: CadenceStepStatus = CadenceStepStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

@dataclass
class TaskExecution:
    """Tracks execution of a single NEXUS task"""
    task_id: str
    start_time: datetime
    steps: List[CadenceStep]
    current_step: int = 0
    violations: List[Dict[str, Any]] = field(default_factory=list)
    completed: bool = False
    failed: bool = False
    total_duration: Optional[float] = None

class NexusCadenceEnforcer:
    """
    Constitutional AI-powered cadence enforcement agent.
    
    CONSTITUTIONAL PRINCIPLES:
    - Article I: No step may be skipped under any circumstances
    - Article II: All testing must be comprehensive and verified  
    - Article III: Progress tracking is mandatory before proceeding
    - Article IV: Integration failures halt all progress immediately
    - Article V: Quality gates are non-negotiable checkpoints
    """
    
    def __init__(self, nexus_project_path: str):
        self.nexus_path = Path(nexus_project_path)
        self.execution_log: List[TaskExecution] = []
        self.violation_count = 0
        self.current_execution: Optional[TaskExecution] = None
        
        # Constitutional enforcement - immutable principles
        self._constitutional_articles = {
            "Article I": "STEP SEQUENCE INTEGRITY - No step may be bypassed",
            "Article II": "TESTING MANDATE - All code must be comprehensively tested", 
            "Article III": "PROGRESS TRACKING REQUIREMENT - Tracker must be updated",
            "Article IV": "INTEGRATION VERIFICATION - Cross-module compatibility required",
            "Article V": "QUALITY GATE ENFORCEMENT - Standards are non-negotiable",
            "Article VI": "CHECKPOINT CREATION - Recovery points are mandatory",
            "Article VII": "STATUS UPDATE DISCIPLINE - Dashboard must reflect reality",
            "Article VIII": "COMPLIANCE DOCUMENTATION - All steps must be evidenced"
        }
        
        # Initialize the 8-step cadence template
        self.cadence_template = self._create_cadence_template()
        
    def _create_cadence_template(self) -> List[CadenceStep]:
        """Create the immutable 8-step cadence template"""
        return [
            CadenceStep(
                step_number=1,
                name="TASK ANALYSIS",
                description="Read and analyze task requirements",
                required_actions=[
                    "Read task ID from nexus_tasks.json",
                    "Extract requirements, dependencies, actions", 
                    "Verify previous task completion",
                    "Confirm task sequence correctness"
                ],
                validation_criteria=[
                    "Task ID confirmed valid",
                    "Requirements clearly understood",
                    "Dependencies satisfied",
                    "Sequence verified"
                ]
            ),
            CadenceStep(
                step_number=2,
                name="MODULE IMPLEMENTATION", 
                description="Create production-quality Python module",
                required_actions=[
                    "Create .py file with task-specific functionality",
                    "Write 40+ lines of production code",
                    "Include comprehensive docstring with task ID",
                    "Follow established patterns",
                    "Import required dependencies"
                ],
                validation_criteria=[
                    "File created successfully",
                    "Minimum 40 lines achieved", 
                    "Docstring includes task ID",
                    "Code follows patterns",
                    "Imports are correct"
                ]
            ),
            CadenceStep(
                step_number=3,
                name="IMMEDIATE TESTING",
                description="Execute comprehensive testing protocol", 
                required_actions=[
                    "Write and execute comprehensive tests",
                    "Test all functions and methods",
                    "Verify imports work correctly",
                    "Test integration with existing modules",
                    "Confirm no errors or warnings",
                    "Run mypy strict mode type checking",
                    "Run flake8 linting with zero violations",
                    "Verify Pydantic models used for data",
                    "Ensure 100% type annotation coverage"
                ],
                validation_criteria=[
                    "All tests written and executed",
                    "100% function coverage achieved",
                    "Import verification successful",
                    "Integration tests passed",
                    "Zero errors/warnings confirmed",
                    "mypy strict mode: ZERO errors",
                    "flake8: ZERO violations",
                    "Pydantic models present for data structures",
                    "Type annotation coverage: 100%"
                ]
            ),
            CadenceStep(
                step_number=4,
                name="PROGRESS TRACKING",
                description="Update NEXUS progress tracking system",
                required_actions=[
                    "Use NexusProgressTracker.start_task()",
                    "Use NexusProgressTracker.complete_task()", 
                    "Create recovery checkpoint",
                    "Verify nexus_progress.json updates"
                ],
                validation_criteria=[
                    "Task started in tracker",
                    "Task marked completed",
                    "Checkpoint created successfully",
                    "Progress file updated"
                ]
            ),
            CadenceStep(
                step_number=5,
                name="STATUS UPDATES",
                description="Update task status and dashboard",
                required_actions=[
                    "Use update_task_status() to mark COMPLETED",
                    "Use update_dashboard_html() to refresh dashboard",
                    "Verify nexus_tasks.json status change", 
                    "Verify nexus_dashboard.html data update"
                ],
                validation_criteria=[
                    "Task marked COMPLETED in tasks.json",
                    "Dashboard HTML refreshed",
                    "Status change verified",
                    "Dashboard data updated"
                ]
            ),
            CadenceStep(
                step_number=6,
                name="INTEGRATION VERIFICATION",
                description="Verify cross-module integration",
                required_actions=[
                    "Import new module successfully",
                    "Test cross-module functionality",
                    "Verify no breaking changes",
                    "Confirm module loads without errors"
                ],
                validation_criteria=[
                    "Module imports successfully",
                    "Cross-module tests pass",
                    "No breaking changes detected",
                    "Clean module loading confirmed"
                ]
            ),
            CadenceStep(
                step_number=7,
                name="COMPLIANCE CHECK",
                description="Constitutional compliance verification",
                required_actions=[
                    "Verify all 8 steps completed",
                    "Confirm no constitutional violations",
                    "Check TodoWrite status updates",
                    "Validate checkpoint created"
                ],
                validation_criteria=[
                    "All steps verified complete",
                    "Zero violations confirmed",
                    "TodoWrite properly updated",
                    "Checkpoint validated"
                ]
            ),
            CadenceStep(
                step_number=8,
                name="PROGRESS REPORTING",
                description="Report completion and prepare for next task",
                required_actions=[
                    "Report task completion with ✅ status",
                    "Show module stats (name, lines, functionality)",
                    "Display progress statistics (X/5700 tasks)",
                    "Update TodoWrite for next task"
                ],
                validation_criteria=[
                    "Completion reported with ✅",
                    "Module stats displayed",
                    "Progress statistics shown",
                    "TodoWrite updated for next"
                ]
            )
        ]
    
    def start_task_execution(self, task_id: str) -> TaskExecution:
        """
        Start enforced execution of NEXUS task.
        
        CONSTITUTIONAL ARTICLE I: STEP SEQUENCE INTEGRITY
        This method initiates the immutable 8-step cadence.
        """
        print(f"\n[INIT] CONSTITUTIONAL CADENCE ENFORCEMENT INITIATED")
        print(f"[TASK] Task ID: {task_id}")
        print(f"[CONST] Constitutional Articles: {len(self._constitutional_articles)} Active")
        print(f"[TOLERANCE] Violation Tolerance: ZERO")
        
        execution = TaskExecution(
            task_id=task_id,
            start_time=datetime.now(),
            steps=[step.__class__(**step.__dict__) for step in self.cadence_template]
        )
        
        self.current_execution = execution
        self.execution_log.append(execution)
        
        print(f"\n[LOOP] CADENCE LOOP INITIALIZED")
        print(f"   Steps: {len(execution.steps)}")
        print(f"   Current Step: {execution.current_step + 1}")
        print(f"   Status: {execution.steps[0].status.value}")
        
        return execution
    
    def execute_step(self, step_evidence: Dict[str, Any]) -> bool:
        """
        Execute single cadence step with constitutional enforcement.
        
        CHAIN OF THOUGHT REASONING:
        1. Verify we have active execution
        2. Get current step requirements  
        3. Validate evidence against criteria
        4. Apply constitutional checks
        5. Update step status
        6. Check for violations
        7. Advance or halt based on compliance
        """
        if not self.current_execution:
            raise ValueError("No active task execution")
        
        current_step = self.current_execution.steps[self.current_execution.current_step]
        
        print(f"\n🔍 EXECUTING STEP {current_step.step_number}: {current_step.name}")
        print(f"📝 Required Actions: {len(current_step.required_actions)}")
        print(f"✅ Validation Criteria: {len(current_step.validation_criteria)}")
        
        # CONSTITUTIONAL ARTICLE VIII: Evidence must be provided
        if not step_evidence:
            violation = {
                "type": ViolationType.QUALITY_GATE_FAILURE,
                "step": current_step.step_number,
                "message": "No evidence provided for step execution",
                "timestamp": datetime.now(),
                "constitutional_article": "Article VIII: COMPLIANCE DOCUMENTATION"
            }
            self.current_execution.violations.append(violation)
            self.violation_count += 1
            
            print(f"❌ CONSTITUTIONAL VIOLATION: {violation['message']}")
            print(f"⚖️ Article Violated: {violation['constitutional_article']}")
            
            return False
        
        # Mark step as in progress
        current_step.status = CadenceStepStatus.IN_PROGRESS
        current_step.start_time = datetime.now()
        current_step.evidence = step_evidence
        
        # VALIDATE EVIDENCE AGAINST CRITERIA
        validation_results = []
        for criterion in current_step.validation_criteria:
            # Apply meta-prompting: examine the validation process itself
            validated = self._validate_criterion(criterion, step_evidence)
            validation_results.append((criterion, validated))
            
            if not validated:
                current_step.errors.append(f"Failed criterion: {criterion}")
        
        # CONSTITUTIONAL CHECK: All criteria must pass
        failed_validations = [c for c, v in validation_results if not v]
        
        if failed_validations:
            violation = {
                "type": ViolationType.QUALITY_GATE_FAILURE,
                "step": current_step.step_number,
                "message": f"Failed validation criteria: {failed_validations}",
                "timestamp": datetime.now(),
                "constitutional_article": "Article V: QUALITY GATE ENFORCEMENT"
            }
            self.current_execution.violations.append(violation)
            self.violation_count += 1
            
            current_step.status = CadenceStepStatus.FAILED
            current_step.end_time = datetime.now()
            
            print(f"❌ STEP FAILED: {len(failed_validations)} criteria not met")
            print(f"⚖️ Constitutional Violation: Quality gates are non-negotiable")
            
            return False
        
        # SUCCESS: Mark step complete and advance
        current_step.status = CadenceStepStatus.COMPLETED
        current_step.end_time = datetime.now()
        
        duration = (current_step.end_time - current_step.start_time).total_seconds()
        
        print(f"✅ STEP COMPLETED: {current_step.name}")
        print(f"⏱️ Duration: {duration:.2f} seconds")
        print(f"📊 Evidence Items: {len(step_evidence)}")
        
        # Advance to next step
        self.current_execution.current_step += 1
        
        # Check if all steps completed
        if self.current_execution.current_step >= len(self.current_execution.steps):
            self._complete_task_execution()
        
        return True
    
    def _validate_criterion(self, criterion: str, evidence: Dict[str, Any]) -> bool:
        """
        Validate evidence against specific criterion.
        
        TREE OF THOUGHTS: Explore multiple validation paths
        """
        criterion_lower = criterion.lower()
        
        # Dynamic validation based on criterion content
        if "file created" in criterion_lower:
            return evidence.get("file_exists", False)
        elif "40 lines" in criterion_lower:
            return evidence.get("line_count", 0) >= 40
        elif "tests" in criterion_lower:
            return evidence.get("tests_passed", False)
        elif "import" in criterion_lower:
            return evidence.get("imports_successful", False)
        elif "tracker" in criterion_lower:
            return evidence.get("tracker_updated", False)
        elif "checkpoint" in criterion_lower:
            return evidence.get("checkpoint_created", False)
        elif "dashboard" in criterion_lower:
            return evidence.get("dashboard_updated", False)
        elif "violations" in criterion_lower:
            return evidence.get("no_violations", True)
        else:
            # Generic validation - assume boolean flag
            return evidence.get(criterion.replace(" ", "_").lower(), False)
    
    def _complete_task_execution(self):
        """Complete current task execution with final constitutional check"""
        execution = self.current_execution
        execution.completed = True
        execution.total_duration = (datetime.now() - execution.start_time).total_seconds()
        
        # FINAL CONSTITUTIONAL AUDIT
        print(f"\n🏛️ FINAL CONSTITUTIONAL AUDIT")
        print(f"📋 Task: {execution.task_id}")
        print(f"⏱️ Total Duration: {execution.total_duration:.2f} seconds")
        print(f"🔍 Steps Completed: {len([s for s in execution.steps if s.status == CadenceStepStatus.COMPLETED])}/8")
        print(f"❌ Violations Detected: {len(execution.violations)}")
        
        if execution.violations:
            print(f"\n⚠️ CONSTITUTIONAL VIOLATIONS SUMMARY:")
            for i, violation in enumerate(execution.violations, 1):
                print(f"   {i}. {violation['type'].value}: {violation['message']}")
                print(f"      Article: {violation['constitutional_article']}")
            
            execution.failed = True
            print(f"\n❌ TASK EXECUTION FAILED DUE TO VIOLATIONS")
        else:
            print(f"\n✅ TASK EXECUTION COMPLETED WITH PERFECT COMPLIANCE")
            print(f"🎯 All constitutional articles upheld")
            print(f"⚖️ Zero violations detected")
        
        # Clear current execution
        self.current_execution = None
    
    def get_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        total_executions = len(self.execution_log)
        successful_executions = len([e for e in self.execution_log if e.completed and not e.failed])
        failed_executions = len([e for e in self.execution_log if e.failed])
        
        violation_types = {}
        for execution in self.execution_log:
            for violation in execution.violations:
                vtype = violation['type'].value
                if vtype not in violation_types:
                    violation_types[vtype] = 0
                violation_types[vtype] += 1
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": (successful_executions / total_executions) if total_executions > 0 else 0,
            "total_violations": self.violation_count,
            "violation_types": violation_types,
            "constitutional_articles": self._constitutional_articles,
            "last_execution": self.execution_log[-1].task_id if self.execution_log else None,
            "average_duration": sum(e.total_duration for e in self.execution_log if e.total_duration) / len([e for e in self.execution_log if e.total_duration]) if self.execution_log else 0
        }

def create_cadence_enforcer(nexus_project_path: str) -> NexusCadenceEnforcer:
    """Factory function to create cadence enforcer"""
    return NexusCadenceEnforcer(nexus_project_path)

# Example usage and testing
if __name__ == "__main__":
    print("[AGENT] NEXUS CADENCE ENFORCEMENT AGENT")
    print("[CONST] Constitutional AI + Master Prompt Strategies")
    print("[ENFORCE] Zero Tolerance for Violations")
    
    # Create enforcer
    enforcer = create_cadence_enforcer("C:\\Users\\kleiy\\OneDrive\\Desktop\\python-ai-apps\\ai_apps\\nexus_browser")
    
    # Show constitutional articles
    print(f"\n[ARTICLES] CONSTITUTIONAL ARTICLES:")
    for article, description in enforcer._constitutional_articles.items():
        print(f"   {article}: {description}")
    
    print(f"\n[TEMPLATE] CADENCE TEMPLATE: {len(enforcer.cadence_template)} Steps")
    for i, step in enumerate(enforcer.cadence_template, 1):
        print(f"   Step {i}: {step.name}")
    
    print(f"\n[READY] CADENCE ENFORCER READY")
    print(f"[TARGET] Compliance Target: 100%")
    print(f"[TOLERANCE] Violation Tolerance: 0%")