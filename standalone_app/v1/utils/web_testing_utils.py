"""
Shared utilities for web testing functionality
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from pathlib import Path


class WebTestingLogger:
    """Centralized logging for web testing components"""
    
    @staticmethod
    def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
        """Setup a logger with consistent formatting"""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger


class JobManager:
    """Manages async job tracking across the system"""
    
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.logger = WebTestingLogger.setup_logger("JobManager")
    
    def create_job(self, job_id: str, job_type: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new job entry"""
        job_data = {
            "id": job_id,
            "type": job_type,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": metadata,
            "result": None,
            "error": None
        }
        self.jobs[job_id] = job_data
        self.logger.info(f"Created job {job_id} of type {job_type}")
        return job_data
    
    def update_job_status(self, job_id: str, status: str, result: Any = None, error: str = None):
        """Update job status"""
        if job_id in self.jobs:
            self.jobs[job_id]["status"] = status
            self.jobs[job_id]["updated_at"] = datetime.now().isoformat()
            if result is not None:
                self.jobs[job_id]["result"] = result
            if error is not None:
                self.jobs[job_id]["error"] = error
            self.logger.info(f"Updated job {job_id} status to {status}")
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job details"""
        return self.jobs.get(job_id)
    
    def cleanup_old_jobs(self, hours: int = 24):
        """Remove jobs older than specified hours"""
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        jobs_to_remove = []
        
        for job_id, job_data in self.jobs.items():
            job_time = datetime.fromisoformat(job_data["created_at"]).timestamp()
            if job_time < cutoff_time:
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.jobs[job_id]
            self.logger.info(f"Cleaned up old job {job_id}")


class TestDataGenerator:
    """Generates realistic test data for different input types"""
    
    @staticmethod
    def generate_test_data(input_type: str, field_name: str) -> Any:
        """Generate appropriate test data based on input type and field name"""
        
        # Email patterns
        if "email" in field_name.lower() or input_type == "email":
            return f"test.user{datetime.now().timestamp():.0f}@example.com"
        
        # URL patterns
        if "url" in field_name.lower() or input_type == "url":
            return "https://example.com/test-page"
        
        # Phone patterns
        if "phone" in field_name.lower() or input_type == "tel":
            return "+1-555-123-4567"
        
        # Name patterns
        if "name" in field_name.lower():
            if "first" in field_name.lower():
                return "John"
            elif "last" in field_name.lower():
                return "Doe"
            else:
                return "John Doe"
        
        # Address patterns
        if "address" in field_name.lower():
            return "123 Test Street, Test City, TC 12345"
        
        # Number patterns
        if input_type == "number":
            return 42
        
        # Date patterns
        if input_type == "date":
            return datetime.now().strftime("%Y-%m-%d")
        
        # Default text
        return f"Test input for {field_name}"


class ResultFormatter:
    """Formats test results for consistent output"""
    
    @staticmethod
    def format_element_data(element: Dict[str, Any]) -> Dict[str, Any]:
        """Format element data for API response"""
        return {
            "id": element.get("id", ""),
            "type": element.get("type", "unknown"),
            "tag": element.get("tag", ""),
            "text": element.get("text", ""),
            "href": element.get("href"),
            "selector": element.get("selector", ""),
            "xpath": element.get("xpath", ""),
            "attributes": element.get("attributes", {}),
            "is_visible": element.get("is_visible", True),
            "is_interactive": element.get("is_interactive", False),
            "bounds": element.get("bounds"),
            "screenshot": element.get("screenshot"),
            "confidence": element.get("confidence", 1.0),
            "detection_method": element.get("detection_method", "unknown")
        }
    
    @staticmethod
    def format_test_result(test: Dict[str, Any]) -> Dict[str, Any]:
        """Format test execution result"""
        return {
            "test_id": test.get("id", ""),
            "test_name": test.get("name", ""),
            "status": test.get("status", "unknown"),
            "duration": test.get("duration", 0),
            "started_at": test.get("started_at"),
            "completed_at": test.get("completed_at"),
            "error": test.get("error"),
            "error_type": test.get("error_type"),
            "screenshot": test.get("screenshot"),
            "logs": test.get("logs", []),
            "assertions": test.get("assertions", [])
        }


class AsyncTaskRunner:
    """Utilities for running async tasks with timeout and error handling"""
    
    @staticmethod
    async def run_with_timeout(coro, timeout: int, task_name: str = "task"):
        """Run an async task with timeout"""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"{task_name} timed out after {timeout} seconds")
    
    @staticmethod
    async def run_parallel_tasks(tasks: List[asyncio.Task], max_concurrent: int = 5):
        """Run tasks in parallel with concurrency limit"""
        results = []
        for i in range(0, len(tasks), max_concurrent):
            batch = tasks[i:i + max_concurrent]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            results.extend(batch_results)
        return results


# Global instances for shared access
job_manager = JobManager()
test_data_generator = TestDataGenerator()
result_formatter = ResultFormatter()
async_runner = AsyncTaskRunner()