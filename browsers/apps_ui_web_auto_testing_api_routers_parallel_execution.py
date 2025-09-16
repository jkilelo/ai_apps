"""
Parallel Execution API Router
Provides endpoints for parallel test execution with resource management
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from ...parallel_execution.parallel_runner import (
    ParallelTestRunner, ExecutionStrategy, ResourceLimits
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Active parallel execution jobs
parallel_jobs = {}


class ParallelExecutionRequest(BaseModel):
    """Request model for parallel test execution"""
    tests: List[Dict[str, Any]] = Field(..., description="List of tests to execute")
    strategy: str = Field(
        default="smart_batching",
        description="Execution strategy: sequential, parallel_threads, parallel_processes, parallel_async, smart_batching"
    )
    resource_limits: Optional[Dict[str, Any]] = Field(
        None,
        description="Resource limits configuration"
    )
    test_timeout: int = Field(default=300, description="Timeout per test in seconds")
    
    model_config = {
        "example": {
            "tests": [
                {"id": "test1", "name": "Login Test", "url": "https://example.com/login"},
                {"id": "test2", "name": "Search Test", "url": "https://example.com/search"}
            ],
            "strategy": "smart_batching",
            "resource_limits": {
                "max_workers": 4,
                "max_memory_percent": 70.0,
                "max_browser_instances": 8
            }
        }
    }


class ParallelExecutionResponse(BaseModel):
    """Response model for parallel execution"""
    job_id: str
    status: str
    message: str


class ParallelExecutionStatus(BaseModel):
    """Status model for parallel execution job"""
    job_id: str
    status: str
    progress: Dict[str, Any]
    metrics: Optional[Dict[str, Any]] = None
    resource_stats: Optional[Dict[str, Any]] = None
    results: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class ExecutionOptimizationRequest(BaseModel):
    """Request to optimize execution strategy"""
    tests: List[Dict[str, Any]]
    target_duration: Optional[int] = Field(None, description="Target duration in seconds")
    max_cost: Optional[float] = Field(None, description="Maximum cost constraint")


async def execute_parallel_job(job_id: str, request: ParallelExecutionRequest):
    """Execute tests in parallel"""
    try:
        parallel_jobs[job_id]["status"] = "running"
        parallel_jobs[job_id]["started_at"] = datetime.now()
        
        logger.info(f"Starting parallel execution job {job_id} with {len(request.tests)} tests")
        
        # Initialize parallel runner
        runner_config = {}
        if request.resource_limits:
            runner_config["resource_limits"] = request.resource_limits
        
        runner = ParallelTestRunner(runner_config)
        
        # Get execution strategy
        strategy = ExecutionStrategy[request.strategy.upper()]
        
        # Define test runner function
        async def test_runner(test: Dict[str, Any]) -> Dict[str, Any]:
            # This is a placeholder - in production, integrate with actual test runner
            # For now, simulate test execution
            await asyncio.sleep(2)  # Simulate test duration
            
            return {
                "passed": True,
                "output": f"Test {test['id']} executed successfully"
            }
        
        # Execute tests
        result = await runner.execute_tests(
            request.tests,
            strategy=strategy,
            test_runner_func=test_runner
        )
        
        # Update job with results
        parallel_jobs[job_id].update({
            "status": "completed",
            "completed_at": datetime.now(),
            "results": result["results"],
            "metrics": result["metrics"],
            "resource_stats": result["resource_stats"]
        })
        
        logger.info(f"Completed parallel execution job {job_id}")
        
    except Exception as e:
        logger.error(f"Parallel execution job {job_id} failed: {e}", exc_info=True)
        
        parallel_jobs[job_id].update({
            "status": "failed",
            "completed_at": datetime.now(),
            "error": str(e)
        })


@router.post("/execute", response_model=ParallelExecutionResponse)
async def start_parallel_execution(
    request: ParallelExecutionRequest,
    background_tasks: BackgroundTasks
):
    """Start parallel test execution with specified strategy"""
    try:
        job_id = str(uuid.uuid4())
        
        # Initialize job
        parallel_jobs[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "test_count": len(request.tests),
            "strategy": request.strategy
        }
        
        # Start background execution
        background_tasks.add_task(
            execute_parallel_job,
            job_id,
            request
        )
        
        return ParallelExecutionResponse(
            job_id=job_id,
            status="started",
            message=f"Parallel execution started with {len(request.tests)} tests using {request.strategy} strategy"
        )
        
    except Exception as e:
        logger.error(f"Failed to start parallel execution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}", response_model=ParallelExecutionStatus)
async def get_execution_status(job_id: str):
    """Get parallel execution job status"""
    if job_id not in parallel_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = parallel_jobs[job_id]
    
    # Calculate progress
    progress = {
        "status": job["status"],
        "test_count": job["test_count"],
        "strategy": job["strategy"]
    }
    
    if job.get("metrics"):
        progress.update({
            "executed_tests": job["metrics"]["executed_tests"],
            "passed_tests": job["metrics"]["passed_tests"],
            "failed_tests": job["metrics"]["failed_tests"],
            "progress_percent": (
                job["metrics"]["executed_tests"] / job["test_count"] * 100
                if job["test_count"] > 0 else 0
            )
        })
    
    return ParallelExecutionStatus(
        job_id=job_id,
        status=job["status"],
        progress=progress,
        metrics=job.get("metrics"),
        resource_stats=job.get("resource_stats"),
        results=job.get("results") if job["status"] == "completed" else None,
        error=job.get("error")
    )


@router.post("/optimize", response_model=Dict[str, Any])
async def optimize_execution_strategy(request: ExecutionOptimizationRequest):
    """Analyze tests and recommend optimal execution strategy"""
    try:
        test_count = len(request.tests)
        
        # Simple optimization logic - can be enhanced with ML
        recommendations = []
        
        if test_count <= 5:
            recommended_strategy = ExecutionStrategy.SEQUENTIAL
            recommendations.append("Small test suite - sequential execution is optimal")
        elif test_count <= 20:
            recommended_strategy = ExecutionStrategy.PARALLEL_ASYNC
            recommendations.append("Medium test suite - async parallel execution recommended")
        elif test_count <= 100:
            recommended_strategy = ExecutionStrategy.SMART_BATCHING
            recommendations.append("Large test suite - smart batching for optimal resource usage")
        else:
            recommended_strategy = ExecutionStrategy.PARALLEL_PROCESSES
            recommendations.append("Very large test suite - process-based parallelism for isolation")
        
        # Calculate estimated duration and resources
        avg_test_duration = 5  # seconds (placeholder)
        
        if recommended_strategy == ExecutionStrategy.SEQUENTIAL:
            estimated_duration = test_count * avg_test_duration
            max_concurrent = 1
        elif recommended_strategy == ExecutionStrategy.PARALLEL_ASYNC:
            max_concurrent = min(10, test_count)
            estimated_duration = (test_count / max_concurrent) * avg_test_duration
        elif recommended_strategy == ExecutionStrategy.SMART_BATCHING:
            max_concurrent = min(8, test_count)
            estimated_duration = (test_count / max_concurrent) * avg_test_duration * 1.2  # Overhead
        else:
            max_concurrent = min(4, test_count)  # Process overhead
            estimated_duration = (test_count / max_concurrent) * avg_test_duration * 1.5
        
        # Resource recommendations
        resource_limits = {
            "max_workers": max_concurrent,
            "max_memory_percent": min(80, 20 + (max_concurrent * 5)),
            "max_browser_instances": max_concurrent,
            "memory_per_worker_mb": 512 if test_count < 50 else 1024
        }
        
        # Check against constraints
        if request.target_duration and estimated_duration > request.target_duration:
            recommendations.append(
                f"Warning: Estimated duration ({estimated_duration}s) exceeds target ({request.target_duration}s)"
            )
            recommendations.append("Consider increasing parallelism or reducing test scope")
        
        return {
            "recommended_strategy": recommended_strategy.value,
            "estimated_duration_seconds": estimated_duration,
            "max_concurrent_tests": max_concurrent,
            "resource_limits": resource_limits,
            "recommendations": recommendations,
            "cost_estimate": {
                "compute_hours": estimated_duration / 3600,
                "estimated_cost": (estimated_duration / 3600) * 0.10  # $0.10 per hour
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to optimize execution strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/report", response_model=Dict[str, Any])
async def get_performance_report(limit: int = 10):
    """Get performance report for recent parallel executions"""
    try:
        # Get completed jobs
        completed_jobs = [
            job for job in parallel_jobs.values()
            if job["status"] == "completed" and job.get("metrics")
        ]
        
        # Sort by completion time
        completed_jobs.sort(
            key=lambda x: x.get("completed_at", datetime.min),
            reverse=True
        )
        
        # Limit results
        completed_jobs = completed_jobs[:limit]
        
        if not completed_jobs:
            return {
                "message": "No completed jobs found",
                "executions": []
            }
        
        # Calculate aggregate statistics
        total_tests = sum(job["test_count"] for job in completed_jobs)
        total_duration = sum(job["metrics"]["duration"] for job in completed_jobs)
        avg_throughput = sum(
            job["metrics"].get("throughput", 0) for job in completed_jobs
        ) / len(completed_jobs)
        
        # Strategy performance
        strategy_stats = {}
        for job in completed_jobs:
            strategy = job["strategy"]
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {
                    "count": 0,
                    "total_duration": 0,
                    "total_tests": 0,
                    "success_rates": []
                }
            
            stats = strategy_stats[strategy]
            stats["count"] += 1
            stats["total_duration"] += job["metrics"]["duration"]
            stats["total_tests"] += job["test_count"]
            stats["success_rates"].append(job["metrics"].get("success_rate", 0))
        
        # Calculate strategy averages
        for strategy, stats in strategy_stats.items():
            stats["avg_duration"] = stats["total_duration"] / stats["count"]
            stats["avg_throughput"] = stats["total_tests"] / stats["total_duration"]
            stats["avg_success_rate"] = sum(stats["success_rates"]) / len(stats["success_rates"])
            del stats["success_rates"]  # Remove raw data
        
        return {
            "summary": {
                "total_executions": len(completed_jobs),
                "total_tests_executed": total_tests,
                "total_duration_seconds": total_duration,
                "average_throughput_per_second": avg_throughput
            },
            "strategy_performance": strategy_stats,
            "recent_executions": [
                {
                    "job_id": job["job_id"],
                    "strategy": job["strategy"],
                    "test_count": job["test_count"],
                    "duration": job["metrics"]["duration"],
                    "throughput": job["metrics"].get("throughput", 0),
                    "success_rate": job["metrics"].get("success_rate", 0),
                    "resource_efficiency": {
                        "avg_cpu": job.get("resource_stats", {}).get("average_cpu_percent", 0),
                        "avg_memory": job.get("resource_stats", {}).get("average_memory_percent", 0)
                    }
                }
                for job in completed_jobs
            ],
            "recommendations": _generate_performance_recommendations(strategy_stats)
        }
        
    except Exception as e:
        logger.error(f"Failed to generate performance report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_performance_recommendations(strategy_stats: Dict[str, Any]) -> List[str]:
    """Generate performance recommendations based on statistics"""
    recommendations = []
    
    # Find best performing strategy
    if strategy_stats:
        best_strategy = max(
            strategy_stats.items(),
            key=lambda x: x[1]["avg_throughput"]
        )
        recommendations.append(
            f"Best performing strategy: {best_strategy[0]} "
            f"(avg throughput: {best_strategy[1]['avg_throughput']:.2f} tests/sec)"
        )
    
    # Check for low success rates
    for strategy, stats in strategy_stats.items():
        if stats["avg_success_rate"] < 80:
            recommendations.append(
                f"Low success rate for {strategy} strategy ({stats['avg_success_rate']:.1f}%) - "
                "consider investigating test stability"
            )
    
    return recommendations


@router.delete("/{job_id}")
async def cancel_parallel_execution(job_id: str):
    """Cancel a parallel execution job"""
    if job_id not in parallel_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = parallel_jobs[job_id]
    
    if job["status"] in ["completed", "failed", "cancelled"]:
        raise HTTPException(
            status_code=400,
            detail=f"Job already {job['status']}"
        )
    
    job["status"] = "cancelled"
    job["cancelled_at"] = datetime.now().isoformat()
    
    return {"success": True, "message": f"Job {job_id} cancelled"}