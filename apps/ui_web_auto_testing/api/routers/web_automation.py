"""
Web Automation Router - Orchestrates the 4-step automation flow
Maps frontend steps to existing backend infrastructure
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, HttpUrl

# Import the existing routers to use their functionality
from . import element_extraction, test_generation, test_execution

logger = logging.getLogger(__name__)

router = APIRouter()

# Workflow state management
workflow_sessions = {}

# ===== REQUEST/RESPONSE MODELS =====

class TargetSetupRequest(BaseModel):
    """Step 1: Target Setup"""
    target_url: str = Field(..., description="URL to automate")
    test_name: str = Field(..., description="Name for the test")
    description: str = Field(default="", description="Test description")
    browser_type: str = Field(default="chrome", description="Browser type")
    viewport: Dict[str, int] = Field(
        default={"width": 1920, "height": 1080}, 
        description="Viewport dimensions"
    )
    user_profile: str = Field(default="qa_tester", description="User testing profile")

class WorkflowBuilderRequest(BaseModel):
    """Step 2: Workflow Builder"""
    session_id: str = Field(..., description="Workflow session ID")
    workflow_steps: List[Dict[str, Any]] = Field(
        default=[], description="Custom workflow steps"
    )
    test_types: List[str] = Field(
        default=["functional"], description="Types of tests to generate"
    )
    include_accessibility: bool = Field(default=True, description="Include accessibility tests")

class TestExecutionRequestWeb(BaseModel):
    """Step 3: Test Execution"""
    session_id: str = Field(..., description="Workflow session ID")
    execution_mode: str = Field(default="sequential", description="Execution mode")
    capture_screenshots: bool = Field(default=True, description="Capture screenshots")
    max_retries: int = Field(default=3, description="Maximum retries for failed tests")

class ResultsRequest(BaseModel):
    """Step 4: Results & Report"""
    session_id: str = Field(..., description="Workflow session ID")
    format: str = Field(default="json", description="Report format")

# Response Models
class WorkflowSession(BaseModel):
    session_id: str
    status: str
    created_at: datetime
    current_step: int
    steps_completed: List[str]
    target_data: Optional[Dict[str, Any]] = None
    elements_data: Optional[Dict[str, Any]] = None
    workflow_data: Optional[Dict[str, Any]] = None
    execution_data: Optional[Dict[str, Any]] = None
    results_data: Optional[Dict[str, Any]] = None

class StepResponse(BaseModel):
    success: bool
    session_id: str
    step: int
    job_id: Optional[str] = None
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

# ===== STEP 1: TARGET SETUP =====

@router.post("/workflow/step1/target-setup", response_model=StepResponse)
async def target_setup(request: TargetSetupRequest, background_tasks: BackgroundTasks):
    """
    Step 1: Target Setup - Initialize workflow and extract page elements
    """
    try:
        session_id = str(uuid.uuid4())
        
        # Initialize workflow session
        workflow_sessions[session_id] = {
            "session_id": session_id,
            "status": "active",
            "created_at": datetime.now(),
            "current_step": 1,
            "steps_completed": [],
            "target_data": {
                "target_url": request.target_url,
                "test_name": request.test_name,
                "description": request.description,
                "browser_type": request.browser_type,
                "viewport": request.viewport,
                "user_profile": request.user_profile
            }
        }
        
        # Create element extraction request using the existing router's model
        extraction_request = element_extraction.ElementExtractionRequest(
            web_page_url=request.target_url,
            profile=request.user_profile,
            include_screenshots=True,
            max_depth=1
        )
        
        # Start element extraction using the existing router
        extraction_response = await element_extraction.start_element_extraction(extraction_request, background_tasks)
        
        # Store extraction job ID
        workflow_sessions[session_id]["extraction_job_id"] = extraction_response.job_id
        workflow_sessions[session_id]["steps_completed"].append("target_setup_initiated")
        
        return StepResponse(
            success=True,
            session_id=session_id,
            step=1,
            job_id=extraction_response.job_id,
            status="processing",
            message="Target setup initiated. Element extraction in progress.",
            data={
                "target_url": request.target_url,
                "test_name": request.test_name,
                "extraction_job_id": extraction_response.job_id
            }
        )
        
    except Exception as e:
        logger.error(f"Target setup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Target setup failed: {str(e)}")

@router.get("/workflow/{session_id}/step1/status", response_model=StepResponse)
async def get_target_setup_status(session_id: str):
    """Get status of target setup (Step 1)"""
    try:
        if session_id not in workflow_sessions:
            raise HTTPException(status_code=404, detail="Workflow session not found")
        
        session = workflow_sessions[session_id]
        extraction_job_id = session.get("extraction_job_id")
        
        if not extraction_job_id:
            raise HTTPException(status_code=400, detail="No extraction job found")
        
        # Get extraction status using the existing router
        extraction_result = await element_extraction.get_extraction_status(extraction_job_id)
        
        if extraction_result.status == "completed":
            # Store extraction results
            session["elements_data"] = {
                "elements": extraction_result.extracted_elements or [],
                "metadata": extraction_result.metadata or {}
            }
            session["steps_completed"].append("target_setup_completed")
            session["current_step"] = 2
            
            return StepResponse(
                success=True,
                session_id=session_id,
                step=1,
                job_id=extraction_job_id,
                status="completed",
                message="Target setup completed successfully",
                data={
                    "elements_found": len(extraction_result.extracted_elements or []),
                    "extraction_summary": extraction_result.metadata or {},
                    "ready_for_workflow": True
                }
            )
        
        return StepResponse(
            success=True,
            session_id=session_id,
            step=1,
            job_id=extraction_job_id,
            status=extraction_result.status,
            message=f"Element extraction {extraction_result.status}",
            data={"progress": extraction_result.progress if hasattr(extraction_result, 'progress') else 0}
        )
        
    except Exception as e:
        logger.error(f"Failed to get target setup status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

# ===== STEP 2: WORKFLOW BUILDER =====

@router.post("/workflow/{session_id}/step2/build-workflow", response_model=StepResponse)
async def build_workflow(session_id: str, request: WorkflowBuilderRequest, background_tasks: BackgroundTasks):
    """
    Step 2: Workflow Builder - Generate test cases from extracted elements
    """
    try:
        if session_id not in workflow_sessions:
            raise HTTPException(status_code=404, detail="Workflow session not found")
        
        session = workflow_sessions[session_id]
        
        if "target_setup_completed" not in session["steps_completed"]:
            raise HTTPException(status_code=400, detail="Target setup must be completed first")
        
        elements_data = session.get("elements_data")
        if not elements_data:
            raise HTTPException(status_code=400, detail="No elements data found")
        
        # Create test generation request using the existing router's model
        generation_request = test_generation.TestGenerationRequest(
            extracted_elements=elements_data.get("elements", []),
            test_type="functional",
            framework="playwright_pytest",
            include_negative_tests=request.include_accessibility
        )
        
        # Start test generation
        generation_response = await test_generation.start_test_generation(generation_request, background_tasks)
        
        # Store generation job ID
        session["generation_job_id"] = generation_response.job_id
        session["steps_completed"].append("workflow_build_initiated")
        
        return StepResponse(
            success=True,
            session_id=session_id,
            step=2,
            job_id=generation_response.job_id,
            status="processing",
            message="Workflow building initiated. Test generation in progress.",
            data={
                "elements_count": len(elements_data.get("elements", [])),
                "test_types": request.test_types,
                "generation_job_id": generation_response.job_id
            }
        )
        
    except Exception as e:
        logger.error(f"Workflow building failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow building failed: {str(e)}")

@router.get("/workflow/{session_id}/step2/status", response_model=StepResponse)
async def get_workflow_build_status(session_id: str):
    """Get status of workflow building (Step 2)"""
    try:
        if session_id not in workflow_sessions:
            raise HTTPException(status_code=404, detail="Workflow session not found")
        
        session = workflow_sessions[session_id]
        generation_job_id = session.get("generation_job_id")
        
        if not generation_job_id:
            raise HTTPException(status_code=400, detail="No generation job found")
        
        # Get generation status
        generation_result = await test_generation.get_generation_status(generation_job_id)
        
        if generation_result.status == "completed":
            # Store workflow results
            session["workflow_data"] = {
                "test_cases": generation_result.test_cases or [],
                "test_files": generation_result.test_files or {},
                "metadata": generation_result.metadata or {}
            }
            session["steps_completed"].append("workflow_build_completed")
            session["current_step"] = 3
            
            return StepResponse(
                success=True,
                session_id=session_id,
                step=2,
                job_id=generation_job_id,
                status="completed",
                message="Workflow building completed successfully",
                data={
                    "tests_generated": len(generation_result.test_cases or []),
                    "workflow_summary": generation_result.metadata or {},
                    "ready_for_execution": True
                }
            )
        
        return StepResponse(
            success=True,
            session_id=session_id,
            step=2,
            job_id=generation_job_id,
            status=generation_result.status,
            message=f"Test generation {generation_result.status}",
            data={"progress": generation_result.progress if hasattr(generation_result, 'progress') else 0}
        )
        
    except Exception as e:
        logger.error(f"Failed to get workflow build status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

# ===== STEP 3: TEST EXECUTION =====

@router.post("/workflow/{session_id}/step3/execute-tests", response_model=StepResponse)
async def execute_tests(session_id: str, request: TestExecutionRequestWeb, background_tasks: BackgroundTasks):
    """
    Step 3: Test Execution - Execute generated test cases
    """
    try:
        if session_id not in workflow_sessions:
            raise HTTPException(status_code=404, detail="Workflow session not found")
        
        session = workflow_sessions[session_id]
        
        if "workflow_build_completed" not in session["steps_completed"]:
            raise HTTPException(status_code=400, detail="Workflow building must be completed first")
        
        workflow_data = session.get("workflow_data")
        if not workflow_data:
            raise HTTPException(status_code=400, detail="No workflow data found")
        
        # Create test execution request using the existing router's model
        execution_request = test_execution.TestExecutionRequest(
            test_cases=workflow_data.get("test_cases", []),
            test_files=workflow_data.get("test_files", {}),
            execution_mode=request.execution_mode,
            timeout=300,
            browser="chromium"
        )
        
        # Start test execution
        execution_response = await test_execution.start_test_execution(execution_request, background_tasks)
        
        # Store execution job ID
        session["execution_job_id"] = execution_response.job_id
        session["steps_completed"].append("test_execution_initiated")
        
        return StepResponse(
            success=True,
            session_id=session_id,
            step=3,
            job_id=execution_response.job_id,
            status="processing",
            message="Test execution initiated. Running automated tests.",
            data={
                "tests_count": len(workflow_data.get("test_cases", [])),
                "execution_mode": request.execution_mode,
                "execution_job_id": execution_response.job_id
            }
        )
        
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test execution failed: {str(e)}")

@router.get("/workflow/{session_id}/step3/status", response_model=StepResponse)
async def get_test_execution_status(session_id: str):
    """Get status of test execution (Step 3)"""
    try:
        if session_id not in workflow_sessions:
            raise HTTPException(status_code=404, detail="Workflow session not found")
        
        session = workflow_sessions[session_id]
        execution_job_id = session.get("execution_job_id")
        
        if not execution_job_id:
            raise HTTPException(status_code=400, detail="No execution job found")
        
        # Get execution status
        execution_result = await test_execution.get_execution_status(execution_job_id)
        
        if execution_result.status == "completed":
            # Store execution results
            session["execution_data"] = {
                "test_results": execution_result.test_results or [],
                "summary": execution_result.summary or {},
                "metadata": execution_result.metadata or {},
                "total_tests": len(execution_result.test_results or []),
                "passed_tests": len([t for t in (execution_result.test_results or []) if t.get("status") == "passed"]),
                "failed_tests": len([t for t in (execution_result.test_results or []) if t.get("status") == "failed"]),
                "execution_time": execution_result.duration or 0
            }
            session["steps_completed"].append("test_execution_completed")
            session["current_step"] = 4
            
            # Calculate metrics
            results = session["execution_data"]
            total_tests = len(results.get("test_results", []))
            passed_tests = len([t for t in results.get("test_results", []) if t.get("status") == "passed"])
            
            return StepResponse(
                success=True,
                session_id=session_id,
                step=3,
                job_id=execution_job_id,
                status="completed",
                message="Test execution completed successfully",
                data={
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "execution_time": results.get("execution_time", 0),
                    "ready_for_results": True
                }
            )
        
        return StepResponse(
            success=True,
            session_id=session_id,
            step=3,
            job_id=execution_job_id,
            status=execution_result.status,
            message=f"Test execution {execution_result.status}",
            data={"progress": execution_result.progress if hasattr(execution_result, 'progress') else 0}
        )
        
    except Exception as e:
        logger.error(f"Failed to get test execution status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

# ===== STEP 4: RESULTS & REPORT =====

@router.get("/workflow/{session_id}/step4/results", response_model=StepResponse)
async def get_results_report(session_id: str, format: str = "json"):
    """
    Step 4: Results & Report - Generate comprehensive test results
    """
    try:
        if session_id not in workflow_sessions:
            raise HTTPException(status_code=404, detail="Workflow session not found")
        
        session = workflow_sessions[session_id]
        
        if "test_execution_completed" not in session["steps_completed"]:
            raise HTTPException(status_code=400, detail="Test execution must be completed first")
        
        # Compile comprehensive results
        target_data = session.get("target_data", {})
        elements_data = session.get("elements_data", {})
        workflow_data = session.get("workflow_data", {})
        execution_data = session.get("execution_data", {})
        
        # Generate comprehensive report
        results_report = {
            "session_info": {
                "session_id": session_id,
                "created_at": session["created_at"].isoformat(),
                "completed_at": datetime.now().isoformat(),
                "target_url": target_data.get("target_url"),
                "test_name": target_data.get("test_name"),
                "description": target_data.get("description")
            },
            "element_analysis": {
                "total_elements": len(elements_data.get("elements", [])),
                "element_types": elements_data.get("summary", {}).get("element_types", {}),
                "accessibility_score": elements_data.get("summary", {}).get("accessibility_score", 0)
            },
            "test_generation": {
                "tests_generated": len(workflow_data.get("test_cases", [])),
                "test_types": workflow_data.get("summary", {}).get("test_types", []),
                "generation_time": workflow_data.get("summary", {}).get("generation_time", 0)
            },
            "test_execution": {
                "total_tests": len(execution_data.get("test_results", [])),
                "passed_tests": len([t for t in execution_data.get("test_results", []) if t.get("status") == "passed"]),
                "failed_tests": len([t for t in execution_data.get("test_results", []) if t.get("status") == "failed"]),
                "execution_time": execution_data.get("execution_time", 0),
                "test_results": execution_data.get("test_results", []),
                "screenshots": execution_data.get("screenshots", []),
                "logs": execution_data.get("logs", [])
            },
            "metrics": {
                "success_rate": 0,
                "coverage_score": 0,
                "performance_score": 0,
                "accessibility_compliance": 0
            }
        }
        
        # Calculate metrics
        total_tests = results_report["test_execution"]["total_tests"]
        passed_tests = results_report["test_execution"]["passed_tests"]
        
        if total_tests > 0:
            results_report["metrics"]["success_rate"] = (passed_tests / total_tests) * 100
            results_report["metrics"]["coverage_score"] = min(100, (total_tests / 10) * 100)  # Arbitrary calculation
        
        # Store final results
        session["results_data"] = results_report
        session["steps_completed"].append("results_generated")
        session["status"] = "completed"
        
        return StepResponse(
            success=True,
            session_id=session_id,
            step=4,
            status="completed",
            message="Results and report generated successfully",
            data=results_report
        )
        
    except Exception as e:
        logger.error(f"Failed to generate results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate results: {str(e)}")

# ===== WORKFLOW MANAGEMENT =====

@router.get("/workflow/{session_id}/status", response_model=WorkflowSession)
async def get_workflow_status(session_id: str):
    """Get overall workflow session status"""
    if session_id not in workflow_sessions:
        raise HTTPException(status_code=404, detail="Workflow session not found")
    
    session = workflow_sessions[session_id]
    
    return WorkflowSession(
        session_id=session_id,
        status=session["status"],
        created_at=session["created_at"],
        current_step=session["current_step"],
        steps_completed=session["steps_completed"],
        target_data=session.get("target_data"),
        elements_data=session.get("elements_data"),
        workflow_data=session.get("workflow_data"),
        execution_data=session.get("execution_data"),
        results_data=session.get("results_data")
    )

@router.delete("/workflow/{session_id}")
async def delete_workflow_session(session_id: str):
    """Delete workflow session and cleanup resources"""
    if session_id not in workflow_sessions:
        raise HTTPException(status_code=404, detail="Workflow session not found")
    
    session = workflow_sessions[session_id]
    
    # Cleanup any active jobs
    for job_key in ["extraction_job_id", "generation_job_id", "execution_job_id"]:
        job_id = session.get(job_key)
        if job_id:
            try:
                # Attempt to cancel/cleanup jobs
                if job_key == "extraction_job_id":
                    await element_extraction.cancel_extraction(job_id)
                elif job_key == "generation_job_id":
                    await test_generation.cancel_generation(job_id)
                elif job_key == "execution_job_id":
                    await test_execution.cancel_execution(job_id)
            except Exception as e:
                logger.warning(f"Failed to cleanup {job_key}: {str(e)}")
    
    del workflow_sessions[session_id]
    
    return {"message": "Workflow session deleted successfully"}

@router.get("/workflows", response_model=List[WorkflowSession])
async def list_workflow_sessions():
    """List all active workflow sessions"""
    return [
        WorkflowSession(
            session_id=session_id,
            status=session["status"],
            created_at=session["created_at"],
            current_step=session["current_step"],
            steps_completed=session["steps_completed"],
            target_data=session.get("target_data"),
            elements_data=session.get("elements_data"),
            workflow_data=session.get("workflow_data"),
            execution_data=session.get("execution_data"),
            results_data=session.get("results_data")
        )
        for session_id, session in workflow_sessions.items()
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(router, host="0.0.0.0", port=8002)