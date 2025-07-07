"""
Test Execution API Router
Step 3: Execute the generated test cases
"""

import asyncio
import logging
import uuid
import subprocess
import tempfile
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

# Import Playwright test runner
import sys
sys.path.append('/var/www/ai_apps')
from utils.playwright_test_runner import PlaywrightTestRunner, create_playwright_test_from_generated

logger = logging.getLogger(__name__)

router = APIRouter()

# Active executions
active_executions = {}


class TestExecutionRequest(BaseModel):
    """Request model for test execution"""
    test_cases: List[Dict[str, Any]] = Field(..., description="List of generated test cases")
    test_files: Optional[Dict[str, str]] = Field(None, description="Generated test files")
    execution_mode: Optional[str] = Field(default="sequential", description="Execution mode: sequential or parallel")
    timeout: Optional[int] = Field(default=300, description="Timeout in seconds")
    browser: Optional[str] = Field(default="chromium", description="Browser to use for testing")
    
    model_config = {
            "example": {
                "test_cases": [
                    {
                        "id": "test_button_click_0",
                        "name": "Test clicking Submit button",
                        "type": "functional"
                    }
                ],
                "execution_mode": "sequential",
                "timeout": 300,
                "browser": "chromium"
            }
        }


class TestExecutionResponse(BaseModel):
    """Response model for test execution"""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status")
    message: str = Field(..., description="Status message")
    started_at: datetime = Field(..., description="Job start time")


class TestExecutionResult(BaseModel):
    """Result model for test execution"""
    job_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    test_results: Optional[List[Dict[str, Any]]] = None
    summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post("/execute", response_model=TestExecutionResponse)
async def start_test_execution(
    request: TestExecutionRequest,
    background_tasks: BackgroundTasks
):
    """Start test case execution"""
    job_id = f"exec_{uuid.uuid4().hex[:8]}"
    started_at = datetime.now()
    
    # Validate input
    if not request.test_cases:
        raise HTTPException(
            status_code=400,
            detail="No test cases provided"
        )
    
    # Store job info
    active_executions[job_id] = {
        "status": "running",
        "started_at": started_at,
        "request": request.model_dump()
    }
    
    # Start execution in background
    background_tasks.add_task(
        execute_tests_task,
        job_id,
        request
    )
    
    logger.info(f"Started test execution job {job_id} for {len(request.test_cases)} test cases")
    
    return TestExecutionResponse(
        job_id=job_id,
        status="started",
        message="Test execution started successfully",
        started_at=started_at
    )


@router.get("/execute/{job_id}", response_model=TestExecutionResult)
async def get_execution_status(job_id: str):
    """Get the status and results of a test execution job"""
    
    if job_id not in active_executions:
        raise HTTPException(
            status_code=404,
            detail=f"Execution job '{job_id}' not found"
        )
    
    job_data = active_executions[job_id]
    
    return TestExecutionResult(
        job_id=job_id,
        status=job_data["status"],
        started_at=job_data["started_at"],
        completed_at=job_data.get("completed_at"),
        duration=job_data.get("duration"),
        test_results=job_data.get("test_results"),
        summary=job_data.get("summary"),
        error=job_data.get("error"),
        metadata=job_data.get("metadata")
    )


async def execute_tests_task(job_id: str, request: TestExecutionRequest):
    """Background task to execute test cases"""
    started_at = datetime.now()
    
    try:
        logger.info(f"Executing test job {job_id} with {len(request.test_cases)} test cases")
        
        # Convert test cases to Playwright-executable format
        executable_tests = []
        for test_case in request.test_cases:
            executable_test = create_playwright_test_from_generated(test_case)
            executable_tests.append(executable_test)
        
        # Initialize Playwright test runner
        runner = PlaywrightTestRunner(
            browser_type=request.browser,
            timeout=request.timeout * 1000  # Convert to milliseconds
        )
        
        # Run the test suite
        test_suite_result = await runner.run_test_suite(
            executable_tests,
            execution_mode=request.execution_mode
        )
        
        # Extract results
        test_results = test_suite_result["results"]
        summary = test_suite_result["summary"]
        
        completed_at = datetime.now()
        duration = (completed_at - started_at).total_seconds()
        
        # Update job data
        active_executions[job_id].update({
            "status": "completed",
            "completed_at": completed_at,
            "duration": duration,
            "test_results": test_results,
            "summary": summary,
            "metadata": {
                "execution_mode": request.execution_mode,
                "browser": request.browser,
                "timeout": request.timeout,
                "playwright_version": "latest"
            }
        })
        
        logger.info(f"Completed test execution job {job_id}: {summary}")
        
    except Exception as e:
        logger.error(f"Test execution job {job_id} failed: {e}", exc_info=True)
        
        active_executions[job_id].update({
            "status": "failed",
            "completed_at": datetime.now(),
            "duration": (datetime.now() - started_at).total_seconds(),
            "error": str(e)
        })


def execute_playwright_tests(test_files: Dict[str, str], browser: str, timeout: int) -> Dict[str, Any]:
    """Execute Playwright tests using pytest"""
    # This is a placeholder for actual test execution
    # In a real implementation:
    # 1. Create temporary directory
    # 2. Write test files
    # 3. Run pytest with appropriate plugins
    # 4. Parse and return results
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write test files
        for filename, content in test_files.items():
            filepath = os.path.join(tmpdir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(content)
        
        # Run pytest (simplified example)
        cmd = [
            "pytest",
            tmpdir,
            "--browser", browser,
            "--timeout", str(timeout),
            "--json-report",
            "--json-report-file=report.json"
        ]
        
        # Execute tests
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parse results
        # ... parse JSON report and return structured results
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }


@router.delete("/execute/{job_id}")
async def cancel_execution(job_id: str):
    """Cancel an active execution job"""
    
    if job_id not in active_executions:
        raise HTTPException(
            status_code=404,
            detail=f"Execution job '{job_id}' not found"
        )
    
    job_data = active_executions[job_id]
    
    if job_data["status"] != "running":
        raise HTTPException(
            status_code=400,
            detail=f"Job '{job_id}' is not running (status: {job_data['status']})"
        )
    
    # Mark as cancelled
    job_data["status"] = "cancelled"
    job_data["completed_at"] = datetime.now()
    
    logger.info(f"Cancelled execution job {job_id}")
    
    return {"message": f"Execution job '{job_id}' cancelled successfully"}


@router.get("/results/{job_id}/report", response_model=Dict[str, Any])
async def get_execution_report(job_id: str, format: Optional[str] = "json"):
    """Get detailed execution report"""
    
    if job_id not in active_executions:
        raise HTTPException(
            status_code=404,
            detail=f"Execution job '{job_id}' not found"
        )
    
    job_data = active_executions[job_id]
    
    if job_data["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job '{job_id}' is not completed (status: {job_data['status']})"
        )
    
    # Generate report based on format
    if format == "json":
        return {
            "job_id": job_id,
            "execution_time": job_data["started_at"].isoformat(),
            "duration": job_data["duration"],
            "summary": job_data["summary"],
            "test_results": job_data["test_results"],
            "metadata": job_data["metadata"]
        }
    else:
        # Could support other formats like HTML, PDF, etc.
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported report format: {format}"
        )