"""
Parallel Test Execution Engine
Executes tests concurrently with intelligent resource management
"""

import asyncio
import logging
import multiprocessing
import os
import psutil
import sys
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
import json
import tempfile
import subprocess

logger = logging.getLogger(__name__)


class ExecutionStrategy(Enum):
    """Test execution strategies"""
    SEQUENTIAL = "sequential"
    PARALLEL_THREADS = "parallel_threads"
    PARALLEL_PROCESSES = "parallel_processes"
    PARALLEL_ASYNC = "parallel_async"
    DISTRIBUTED = "distributed"
    SMART_BATCHING = "smart_batching"


class ResourceType(Enum):
    """System resource types"""
    CPU = "cpu"
    MEMORY = "memory"
    BROWSER_INSTANCES = "browser_instances"
    NETWORK_BANDWIDTH = "network_bandwidth"


@dataclass
class ResourceLimits:
    """Resource limits for parallel execution"""
    max_workers: int = field(default_factory=lambda: multiprocessing.cpu_count())
    max_memory_percent: float = 80.0  # Max 80% of system memory
    max_browser_instances: int = 10
    cpu_threshold_percent: float = 90.0
    memory_per_worker_mb: int = 512


@dataclass
class TestBatch:
    """Batch of tests to execute together"""
    batch_id: str
    tests: List[Dict[str, Any]]
    estimated_duration: float
    resource_requirements: Dict[ResourceType, float]
    priority: int = 0


@dataclass
class ExecutionMetrics:
    """Metrics for execution performance"""
    total_tests: int
    executed_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    throughput: Optional[float] = None  # Tests per second
    resource_utilization: Dict[str, float] = field(default_factory=dict)
    worker_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)


class ParallelTestRunner:
    """Advanced parallel test execution engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.resource_limits = ResourceLimits(**self.config.get("resource_limits", {}))
        self.execution_metrics = None
        self.resource_monitor = ResourceMonitor(self.resource_limits)
        self.test_queue = asyncio.Queue()
        self.result_queue = asyncio.Queue()
        self.worker_pool = None
        self.active_workers = {}
        
    async def execute_tests(
        self,
        tests: List[Dict[str, Any]],
        strategy: ExecutionStrategy = ExecutionStrategy.SMART_BATCHING,
        test_runner_func: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Execute tests using specified strategy"""
        logger.info(f"Starting parallel test execution with {len(tests)} tests using {strategy.value}")
        
        # Initialize metrics
        self.execution_metrics = ExecutionMetrics(
            total_tests=len(tests),
            executed_tests=0,
            passed_tests=0,
            failed_tests=0,
            skipped_tests=0,
            start_time=datetime.now()
        )
        
        # Start resource monitoring
        monitor_task = asyncio.create_task(self.resource_monitor.start_monitoring())
        
        try:
            # Execute based on strategy
            if strategy == ExecutionStrategy.SEQUENTIAL:
                results = await self._execute_sequential(tests, test_runner_func)
            elif strategy == ExecutionStrategy.PARALLEL_THREADS:
                results = await self._execute_parallel_threads(tests, test_runner_func)
            elif strategy == ExecutionStrategy.PARALLEL_PROCESSES:
                results = await self._execute_parallel_processes(tests, test_runner_func)
            elif strategy == ExecutionStrategy.PARALLEL_ASYNC:
                results = await self._execute_parallel_async(tests, test_runner_func)
            elif strategy == ExecutionStrategy.SMART_BATCHING:
                results = await self._execute_smart_batching(tests, test_runner_func)
            else:
                raise ValueError(f"Unknown execution strategy: {strategy}")
            
            # Finalize metrics
            self.execution_metrics.end_time = datetime.now()
            self.execution_metrics.duration = (
                self.execution_metrics.end_time - self.execution_metrics.start_time
            ).total_seconds()
            
            if self.execution_metrics.duration > 0:
                self.execution_metrics.throughput = (
                    self.execution_metrics.executed_tests / self.execution_metrics.duration
                )
            
            # Stop resource monitoring
            monitor_task.cancel()
            
            return {
                "results": results,
                "metrics": self._serialize_metrics(),
                "resource_stats": await self.resource_monitor.get_stats()
            }
            
        except Exception as e:
            logger.error(f"Parallel execution failed: {e}")
            monitor_task.cancel()
            raise
    
    async def _execute_sequential(
        self, tests: List[Dict[str, Any]], test_runner_func: Callable
    ) -> List[Dict[str, Any]]:
        """Execute tests sequentially"""
        results = []
        
        for test in tests:
            result = await self._run_single_test(test, test_runner_func)
            results.append(result)
            self._update_metrics(result)
        
        return results
    
    async def _execute_parallel_threads(
        self, tests: List[Dict[str, Any]], test_runner_func: Callable
    ) -> List[Dict[str, Any]]:
        """Execute tests using thread pool"""
        max_workers = min(self.resource_limits.max_workers, len(tests))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tests
            futures = []
            for test in tests:
                future = executor.submit(
                    asyncio.run,
                    self._run_single_test(test, test_runner_func)
                )
                futures.append((test["id"], future))
            
            # Collect results
            results = []
            for test_id, future in futures:
                try:
                    result = future.result(timeout=300)  # 5 min timeout
                    results.append(result)
                    self._update_metrics(result)
                except Exception as e:
                    logger.error(f"Test {test_id} failed: {e}")
                    result = {
                        "test_id": test_id,
                        "passed": False,
                        "error": str(e),
                        "duration": 0
                    }
                    results.append(result)
                    self._update_metrics(result)
            
            return results
    
    async def _execute_parallel_processes(
        self, tests: List[Dict[str, Any]], test_runner_func: Callable
    ) -> List[Dict[str, Any]]:
        """Execute tests using process pool"""
        max_workers = min(self.resource_limits.max_workers, len(tests))
        
        # Create worker processes
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Since we can't pass async functions to processes,
            # we need to use a wrapper that runs tests in subprocess
            futures = []
            for test in tests:
                future = executor.submit(self._run_test_subprocess, test)
                futures.append((test["id"], future))
            
            # Collect results
            results = []
            for test_id, future in futures:
                try:
                    result = future.result(timeout=300)
                    results.append(result)
                    self._update_metrics(result)
                except Exception as e:
                    logger.error(f"Test {test_id} failed: {e}")
                    result = {
                        "test_id": test_id,
                        "passed": False,
                        "error": str(e),
                        "duration": 0
                    }
                    results.append(result)
                    self._update_metrics(result)
            
            return results
    
    async def _execute_parallel_async(
        self, tests: List[Dict[str, Any]], test_runner_func: Callable
    ) -> List[Dict[str, Any]]:
        """Execute tests using async concurrency"""
        # Determine optimal concurrency
        max_concurrent = min(
            self.resource_limits.max_workers,
            self.resource_limits.max_browser_instances,
            len(tests)
        )
        
        # Create worker tasks
        workers = []
        for i in range(max_concurrent):
            worker = asyncio.create_task(
                self._async_worker(f"worker-{i}", test_runner_func)
            )
            workers.append(worker)
            self.active_workers[f"worker-{i}"] = {"status": "idle", "current_test": None}
        
        # Add tests to queue
        for test in tests:
            await self.test_queue.put(test)
        
        # Add sentinel values to stop workers
        for _ in range(max_concurrent):
            await self.test_queue.put(None)
        
        # Wait for all workers to complete
        await asyncio.gather(*workers)
        
        # Collect results
        results = []
        while not self.result_queue.empty():
            result = await self.result_queue.get()
            results.append(result)
        
        return results
    
    async def _execute_smart_batching(
        self, tests: List[Dict[str, Any]], test_runner_func: Callable
    ) -> List[Dict[str, Any]]:
        """Execute tests using intelligent batching based on resource requirements"""
        # Analyze tests and create optimal batches
        batches = self._create_smart_batches(tests)
        
        # Execute batches with dynamic resource allocation
        results = []
        for batch in batches:
            # Wait for resources to be available
            await self.resource_monitor.wait_for_resources(batch.resource_requirements)
            
            # Execute batch
            batch_results = await self._execute_batch(batch, test_runner_func)
            results.extend(batch_results)
        
        return results
    
    async def _async_worker(self, worker_id: str, test_runner_func: Callable):
        """Async worker for processing tests"""
        while True:
            test = await self.test_queue.get()
            
            if test is None:  # Sentinel value
                break
            
            # Update worker status
            self.active_workers[worker_id]["status"] = "running"
            self.active_workers[worker_id]["current_test"] = test["id"]
            
            try:
                # Run test
                result = await self._run_single_test(test, test_runner_func)
                await self.result_queue.put(result)
                self._update_metrics(result)
            except Exception as e:
                logger.error(f"Worker {worker_id} failed on test {test['id']}: {e}")
                result = {
                    "test_id": test["id"],
                    "passed": False,
                    "error": str(e),
                    "duration": 0
                }
                await self.result_queue.put(result)
                self._update_metrics(result)
            finally:
                # Update worker status
                self.active_workers[worker_id]["status"] = "idle"
                self.active_workers[worker_id]["current_test"] = None
    
    async def _run_single_test(
        self, test: Dict[str, Any], test_runner_func: Optional[Callable]
    ) -> Dict[str, Any]:
        """Run a single test"""
        start_time = datetime.now()
        
        try:
            if test_runner_func:
                # Use provided test runner
                result = await test_runner_func(test)
            else:
                # Default test execution (placeholder)
                await asyncio.sleep(1)  # Simulate test execution
                result = {
                    "passed": True,
                    "output": "Test executed successfully"
                }
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "test_id": test.get("id", "unknown"),
                "test_name": test.get("name", ""),
                "passed": result.get("passed", True),
                "duration": duration,
                "output": result.get("output", ""),
                "error": result.get("error"),
                "timestamp": start_time.isoformat()
            }
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "test_id": test.get("id", "unknown"),
                "test_name": test.get("name", ""),
                "passed": False,
                "duration": duration,
                "error": str(e),
                "timestamp": start_time.isoformat()
            }
    
    def _run_test_subprocess(self, test: Dict[str, Any]) -> Dict[str, Any]:
        """Run test in subprocess (for process-based parallelism)"""
        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            test_code = f"""
import asyncio
import sys
import json

async def run_test():
    # Placeholder test execution
    await asyncio.sleep(1)
    return {{
        "test_id": "{test.get('id', 'unknown')}",
        "passed": True,
        "duration": 1.0
    }}

if __name__ == "__main__":
    result = asyncio.run(run_test())
    print(json.dumps(result))
"""
            f.write(test_code)
            temp_file = f.name
        
        try:
            # Run test in subprocess
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {
                    "test_id": test.get("id", "unknown"),
                    "passed": False,
                    "error": result.stderr,
                    "duration": 0
                }
        finally:
            # Cleanup
            os.unlink(temp_file)
    
    def _create_smart_batches(self, tests: List[Dict[str, Any]]) -> List[TestBatch]:
        """Create intelligent test batches based on characteristics"""
        # Group tests by estimated duration and resource requirements
        batches = []
        
        # Simple batching strategy - can be enhanced with ML
        batch_size = max(1, len(tests) // self.resource_limits.max_workers)
        
        for i in range(0, len(tests), batch_size):
            batch_tests = tests[i:i + batch_size]
            
            batch = TestBatch(
                batch_id=f"batch-{i // batch_size}",
                tests=batch_tests,
                estimated_duration=len(batch_tests) * 2.0,  # Rough estimate
                resource_requirements={
                    ResourceType.CPU: 20.0,  # 20% CPU per batch
                    ResourceType.MEMORY: 512.0,  # 512 MB per batch
                    ResourceType.BROWSER_INSTANCES: min(len(batch_tests), 3)
                },
                priority=0
            )
            batches.append(batch)
        
        return batches
    
    async def _execute_batch(
        self, batch: TestBatch, test_runner_func: Callable
    ) -> List[Dict[str, Any]]:
        """Execute a batch of tests"""
        logger.info(f"Executing batch {batch.batch_id} with {len(batch.tests)} tests")
        
        # Allocate resources
        await self.resource_monitor.allocate_resources(batch.resource_requirements)
        
        try:
            # Execute tests in batch
            if len(batch.tests) <= 3:
                # Small batch - run sequentially
                results = []
                for test in batch.tests:
                    result = await self._run_single_test(test, test_runner_func)
                    results.append(result)
                    self._update_metrics(result)
            else:
                # Large batch - run with limited concurrency
                results = await self._execute_parallel_async(batch.tests, test_runner_func)
            
            return results
            
        finally:
            # Release resources
            await self.resource_monitor.release_resources(batch.resource_requirements)
    
    def _update_metrics(self, result: Dict[str, Any]):
        """Update execution metrics"""
        self.execution_metrics.executed_tests += 1
        
        if result.get("passed"):
            self.execution_metrics.passed_tests += 1
        else:
            self.execution_metrics.failed_tests += 1
    
    def _serialize_metrics(self) -> Dict[str, Any]:
        """Serialize execution metrics"""
        return {
            "total_tests": self.execution_metrics.total_tests,
            "executed_tests": self.execution_metrics.executed_tests,
            "passed_tests": self.execution_metrics.passed_tests,
            "failed_tests": self.execution_metrics.failed_tests,
            "skipped_tests": self.execution_metrics.skipped_tests,
            "start_time": self.execution_metrics.start_time.isoformat(),
            "end_time": self.execution_metrics.end_time.isoformat() if self.execution_metrics.end_time else None,
            "duration": self.execution_metrics.duration,
            "throughput": self.execution_metrics.throughput,
            "success_rate": (
                self.execution_metrics.passed_tests / self.execution_metrics.executed_tests * 100
                if self.execution_metrics.executed_tests > 0 else 0
            )
        }


class ResourceMonitor:
    """Monitor and manage system resources"""
    
    def __init__(self, limits: ResourceLimits):
        self.limits = limits
        self.current_usage = {
            ResourceType.CPU: 0.0,
            ResourceType.MEMORY: 0.0,
            ResourceType.BROWSER_INSTANCES: 0
        }
        self.monitoring = False
        self.stats_history = []
    
    async def start_monitoring(self):
        """Start resource monitoring"""
        self.monitoring = True
        
        while self.monitoring:
            # Get current resource usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            stats = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / 1024 / 1024,
                "browser_instances": self.current_usage[ResourceType.BROWSER_INSTANCES]
            }
            
            self.stats_history.append(stats)
            
            # Keep only last 100 entries
            if len(self.stats_history) > 100:
                self.stats_history.pop(0)
            
            await asyncio.sleep(5)  # Monitor every 5 seconds
    
    async def wait_for_resources(self, requirements: Dict[ResourceType, float]):
        """Wait until required resources are available"""
        while True:
            if self._check_resource_availability(requirements):
                return
            
            logger.info("Waiting for resources to become available...")
            await asyncio.sleep(2)
    
    async def allocate_resources(self, requirements: Dict[ResourceType, float]):
        """Allocate resources for a test batch"""
        # Update current usage
        for resource_type, amount in requirements.items():
            if resource_type in self.current_usage:
                self.current_usage[resource_type] += amount
    
    async def release_resources(self, requirements: Dict[ResourceType, float]):
        """Release allocated resources"""
        # Update current usage
        for resource_type, amount in requirements.items():
            if resource_type in self.current_usage:
                self.current_usage[resource_type] = max(
                    0, self.current_usage[resource_type] - amount
                )
    
    def _check_resource_availability(self, requirements: Dict[ResourceType, float]) -> bool:
        """Check if required resources are available"""
        # Check CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        if cpu_percent > self.limits.cpu_threshold_percent:
            return False
        
        # Check memory
        memory = psutil.virtual_memory()
        if memory.percent > self.limits.max_memory_percent:
            return False
        
        required_memory_mb = requirements.get(ResourceType.MEMORY, 0)
        if memory.available / 1024 / 1024 < required_memory_mb:
            return False
        
        # Check browser instances
        required_browsers = requirements.get(ResourceType.BROWSER_INSTANCES, 0)
        current_browsers = self.current_usage[ResourceType.BROWSER_INSTANCES]
        if current_browsers + required_browsers > self.limits.max_browser_instances:
            return False
        
        return True
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get resource monitoring statistics"""
        if not self.stats_history:
            return {}
        
        # Calculate averages
        avg_cpu = sum(s["cpu_percent"] for s in self.stats_history) / len(self.stats_history)
        avg_memory = sum(s["memory_percent"] for s in self.stats_history) / len(self.stats_history)
        
        return {
            "average_cpu_percent": avg_cpu,
            "average_memory_percent": avg_memory,
            "peak_cpu_percent": max(s["cpu_percent"] for s in self.stats_history),
            "peak_memory_percent": max(s["memory_percent"] for s in self.stats_history),
            "monitoring_duration": len(self.stats_history) * 5,  # seconds
            "resource_history": self.stats_history[-10:]  # Last 10 entries
        }