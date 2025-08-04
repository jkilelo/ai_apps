"""
Visual Regression Testing API Router
Provides endpoints for visual regression testing in the web automation pipeline
"""

import asyncio
import base64
import io
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from pydantic import BaseModel, Field
from PIL import Image

from ...visual_regression.visual_comparator import (
    VisualComparator, ComparisonStrategy, DiffSeverity,
    VisualRegressionResult, VisualDiff
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Job storage for async operations
visual_regression_jobs = {}


class VisualRegressionRequest(BaseModel):
    """Request model for visual regression testing"""
    test_id: str = Field(..., description="Unique test identifier")
    baseline_image: Optional[str] = Field(None, description="Base64 encoded baseline image")
    current_image: str = Field(..., description="Base64 encoded current image")
    ignore_regions: List[List[int]] = Field(
        default=[], 
        description="Regions to ignore [x, y, width, height]"
    )
    strategies: List[str] = Field(
        default=["pixel_diff", "structural_similarity"],
        description="Comparison strategies to use"
    )
    config: Optional[Dict[str, Any]] = Field(
        None,
        description="Custom configuration for comparison"
    )


class VisualRegressionResponse(BaseModel):
    """Response model for visual regression testing"""
    job_id: str
    status: str
    message: str


class VisualRegressionJobStatus(BaseModel):
    """Job status model"""
    job_id: str
    status: str
    progress: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BaselineUpdateRequest(BaseModel):
    """Request to update baseline image"""
    test_id: str
    image: str  # Base64 encoded image


class BatchVisualTestRequest(BaseModel):
    """Request for batch visual testing"""
    tests: List[Dict[str, Any]] = Field(..., description="List of tests to run")
    parallel: bool = Field(default=True, description="Run tests in parallel")
    config: Optional[Dict[str, Any]] = None


# Initialize comparator
comparator = VisualComparator()


async def process_visual_regression(
    job_id: str,
    test_id: str,
    baseline_image_data: Optional[str],
    current_image_data: str,
    ignore_regions: List[List[int]],
    strategies: List[str],
    config: Optional[Dict[str, Any]]
):
    """Process visual regression test asynchronously"""
    try:
        # Update job status
        visual_regression_jobs[job_id]["status"] = "processing"
        visual_regression_jobs[job_id]["progress"] = 10
        
        # Decode images
        current_image = Image.open(io.BytesIO(base64.b64decode(current_image_data)))
        
        # Get or create baseline
        if baseline_image_data:
            baseline_image = Image.open(io.BytesIO(base64.b64decode(baseline_image_data)))
        else:
            baseline_image = await comparator.get_baseline(test_id)
            if not baseline_image:
                # First run - save current as baseline
                await comparator.update_baseline(test_id, current_image)
                visual_regression_jobs[job_id]["status"] = "completed"
                visual_regression_jobs[job_id]["progress"] = 100
                visual_regression_jobs[job_id]["result"] = {
                    "message": "Baseline created for first run",
                    "test_id": test_id,
                    "baseline_created": True
                }
                return
        
        visual_regression_jobs[job_id]["progress"] = 30
        
        # Configure comparator
        if config:
            comparator.config.update(config)
        
        # Set comparison strategies
        if strategies:
            comparator.config["strategies"] = [
                ComparisonStrategy[s.upper()] for s in strategies
            ]
        
        # Convert ignore regions format
        ignore_regions_tuples = [tuple(r) for r in ignore_regions]
        
        visual_regression_jobs[job_id]["progress"] = 50
        
        # Run comparison
        result = await comparator.compare_images(
            baseline_image,
            current_image,
            test_id,
            ignore_regions_tuples
        )
        
        visual_regression_jobs[job_id]["progress"] = 90
        
        # Convert result to dict
        result_dict = {
            "test_id": result.test_id,
            "passed": result.passed,
            "overall_similarity": result.overall_similarity,
            "execution_time": result.execution_time,
            "timestamp": result.timestamp.isoformat(),
            "baseline_path": result.baseline_path,
            "current_path": result.current_path,
            "diffs": [
                {
                    "severity": diff.severity.value,
                    "confidence": diff.confidence,
                    "diff_percentage": diff.diff_percentage,
                    "affected_regions": diff.affected_regions,
                    "diff_image_path": diff.diff_image_path,
                    "description": diff.description,
                    "suggestions": diff.suggestions
                }
                for diff in result.diffs
            ],
            "metadata": result.metadata
        }
        
        visual_regression_jobs[job_id]["status"] = "completed"
        visual_regression_jobs[job_id]["progress"] = 100
        visual_regression_jobs[job_id]["result"] = result_dict
        
    except Exception as e:
        logger.error(f"Visual regression processing failed: {str(e)}")
        visual_regression_jobs[job_id]["status"] = "failed"
        visual_regression_jobs[job_id]["error"] = str(e)


@router.post("/visual-regression/compare", response_model=VisualRegressionResponse)
async def compare_images(
    request: VisualRegressionRequest,
    background_tasks: BackgroundTasks
):
    """
    Start visual regression comparison
    """
    try:
        job_id = str(uuid.uuid4())
        
        # Initialize job
        visual_regression_jobs[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "test_id": request.test_id
        }
        
        # Start background processing
        background_tasks.add_task(
            process_visual_regression,
            job_id,
            request.test_id,
            request.baseline_image,
            request.current_image,
            request.ignore_regions,
            request.strategies,
            request.config
        )
        
        return VisualRegressionResponse(
            job_id=job_id,
            status="started",
            message=f"Visual regression test started for {request.test_id}"
        )
        
    except Exception as e:
        logger.error(f"Failed to start visual regression test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/visual-regression/{job_id}/status", response_model=VisualRegressionJobStatus)
async def get_job_status(job_id: str):
    """Get visual regression job status"""
    if job_id not in visual_regression_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = visual_regression_jobs[job_id]
    
    return VisualRegressionJobStatus(
        job_id=job_id,
        status=job["status"],
        progress=job.get("progress", 0),
        result=job.get("result"),
        error=job.get("error")
    )


@router.post("/visual-regression/baseline/update")
async def update_baseline(request: BaselineUpdateRequest):
    """Update baseline image for a test"""
    try:
        # Decode image
        image_data = base64.b64decode(request.image)
        image = Image.open(io.BytesIO(image_data))
        
        # Update baseline
        await comparator.update_baseline(request.test_id, image)
        
        return {
            "success": True,
            "message": f"Baseline updated for test {request.test_id}"
        }
        
    except Exception as e:
        logger.error(f"Failed to update baseline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/visual-regression/baseline/{test_id}")
async def get_baseline(test_id: str):
    """Get baseline image for a test"""
    try:
        baseline = await comparator.get_baseline(test_id)
        
        if not baseline:
            raise HTTPException(status_code=404, detail="Baseline not found")
        
        # Convert to base64
        buffer = io.BytesIO()
        baseline.save(buffer, format="PNG")
        baseline_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "test_id": test_id,
            "baseline_image": baseline_b64,
            "size": baseline.size,
            "format": "PNG"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get baseline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/visual-regression/batch", response_model=VisualRegressionResponse)
async def batch_visual_tests(
    request: BatchVisualTestRequest,
    background_tasks: BackgroundTasks
):
    """Run batch visual regression tests"""
    try:
        batch_id = str(uuid.uuid4())
        
        # Initialize batch job
        visual_regression_jobs[batch_id] = {
            "job_id": batch_id,
            "status": "pending",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "type": "batch",
            "total_tests": len(request.tests),
            "completed_tests": 0,
            "sub_jobs": []
        }
        
        # Start batch processing
        background_tasks.add_task(
            process_batch_visual_tests,
            batch_id,
            request.tests,
            request.parallel,
            request.config
        )
        
        return VisualRegressionResponse(
            job_id=batch_id,
            status="started",
            message=f"Batch visual regression started with {len(request.tests)} tests"
        )
        
    except Exception as e:
        logger.error(f"Failed to start batch visual tests: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_batch_visual_tests(
    batch_id: str,
    tests: List[Dict[str, Any]],
    parallel: bool,
    config: Optional[Dict[str, Any]]
):
    """Process batch visual regression tests"""
    try:
        visual_regression_jobs[batch_id]["status"] = "processing"
        
        sub_job_ids = []
        
        # Create sub-jobs
        for test in tests:
            sub_job_id = str(uuid.uuid4())
            visual_regression_jobs[sub_job_id] = {
                "job_id": sub_job_id,
                "status": "pending",
                "progress": 0,
                "parent_job": batch_id,
                "test_id": test.get("test_id", sub_job_id)
            }
            sub_job_ids.append(sub_job_id)
        
        visual_regression_jobs[batch_id]["sub_jobs"] = sub_job_ids
        
        # Process tests
        if parallel:
            # Run tests in parallel
            tasks = []
            for test, sub_job_id in zip(tests, sub_job_ids):
                task = process_visual_regression(
                    sub_job_id,
                    test.get("test_id", sub_job_id),
                    test.get("baseline_image"),
                    test["current_image"],
                    test.get("ignore_regions", []),
                    test.get("strategies", ["pixel_diff", "structural_similarity"]),
                    config
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks)
        else:
            # Run tests sequentially
            for test, sub_job_id in zip(tests, sub_job_ids):
                await process_visual_regression(
                    sub_job_id,
                    test.get("test_id", sub_job_id),
                    test.get("baseline_image"),
                    test["current_image"],
                    test.get("ignore_regions", []),
                    test.get("strategies", ["pixel_diff", "structural_similarity"]),
                    config
                )
                
                # Update progress
                completed = sub_job_ids.index(sub_job_id) + 1
                visual_regression_jobs[batch_id]["completed_tests"] = completed
                visual_regression_jobs[batch_id]["progress"] = int(
                    (completed / len(tests)) * 100
                )
        
        # Collect results
        results = []
        for sub_job_id in sub_job_ids:
            sub_job = visual_regression_jobs.get(sub_job_id, {})
            if sub_job.get("result"):
                results.append(sub_job["result"])
        
        # Generate batch report
        report = comparator.generate_report([
            VisualRegressionResult(
                test_id=r["test_id"],
                baseline_path=r["baseline_path"],
                current_path=r["current_path"],
                timestamp=datetime.fromisoformat(r["timestamp"]),
                passed=r["passed"],
                diffs=[],  # Simplified for report
                overall_similarity=r["overall_similarity"],
                execution_time=r["execution_time"],
                metadata=r["metadata"]
            )
            for r in results
        ])
        
        visual_regression_jobs[batch_id]["status"] = "completed"
        visual_regression_jobs[batch_id]["progress"] = 100
        visual_regression_jobs[batch_id]["result"] = {
            "individual_results": results,
            "report": report
        }
        
    except Exception as e:
        logger.error(f"Batch visual regression failed: {str(e)}")
        visual_regression_jobs[batch_id]["status"] = "failed"
        visual_regression_jobs[batch_id]["error"] = str(e)


@router.get("/visual-regression/report/{batch_id}")
async def get_batch_report(batch_id: str):
    """Get batch visual regression report"""
    if batch_id not in visual_regression_jobs:
        raise HTTPException(status_code=404, detail="Batch job not found")
    
    job = visual_regression_jobs[batch_id]
    
    if job.get("type") != "batch":
        raise HTTPException(status_code=400, detail="Not a batch job")
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Batch job not completed")
    
    return job["result"]["report"]


@router.delete("/visual-regression/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a visual regression job"""
    if job_id not in visual_regression_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = visual_regression_jobs[job_id]
    
    if job["status"] in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Job already finished")
    
    job["status"] = "cancelled"
    
    return {"success": True, "message": f"Job {job_id} cancelled"}


@router.get("/visual-regression/history/{test_id}")
async def get_test_history(test_id: str, limit: int = 10):
    """Get visual regression history for a test"""
    # In a real implementation, this would query a database
    # For now, return mock data
    return {
        "test_id": test_id,
        "history": [
            {
                "timestamp": datetime.now().isoformat(),
                "passed": True,
                "similarity": 0.98,
                "diff_count": 0
            }
        ]
    }