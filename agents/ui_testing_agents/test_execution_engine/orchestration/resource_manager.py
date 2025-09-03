"""
Resource Manager for Nexus Executor
Manages system resources, monitors usage, and enforces limits
"""

import asyncio
import psutil
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging

from ..core.models import (
    ResourceType, ResourceLimits, MetricType,
    ExecutionRequest, ExecutionJob, WorkerStatus
)

logger = logging.getLogger(__name__)


# ============================================================================
# RESOURCE MONITORING
# ============================================================================

@dataclass
class ResourceSnapshot:
    """Snapshot of system resources at a point in time"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_io_read: int
    disk_io_write: int
    network_sent: int
    network_recv: int
    process_count: int
    thread_count: int
    
    @classmethod
    def capture(cls) -> 'ResourceSnapshot':
        """Capture current system resource state"""
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        net_io = psutil.net_io_counters()
        
        return cls(
            timestamp=datetime.now(),
            cpu_percent=psutil.cpu_percent(interval=0.1),
            memory_percent=memory.percent,
            memory_mb=memory.used / (1024 * 1024),
            disk_io_read=disk_io.read_bytes if disk_io else 0,
            disk_io_write=disk_io.write_bytes if disk_io else 0,
            network_sent=net_io.bytes_sent if net_io else 0,
            network_recv=net_io.bytes_recv if net_io else 0,
            process_count=len(psutil.pids()),
            thread_count=threading.active_count()
        )


class ResourceMonitor:
    """Continuously monitors system resources"""
    
    def __init__(self, interval: float = 1.0, history_size: int = 60):
        self.interval = interval
        self.history_size = history_size
        self.history: deque[ResourceSnapshot] = deque(maxlen=history_size)
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
    
    def start(self):
        """Start monitoring resources"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Resource monitoring started")
    
    def stop(self):
        """Stop monitoring resources"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Resource monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                snapshot = ResourceSnapshot.capture()
                with self._lock:
                    self.history.append(snapshot)
            except Exception as e:
                logger.error(f"Error capturing resource snapshot: {e}")
            
            time.sleep(self.interval)
    
    def get_current(self) -> Optional[ResourceSnapshot]:
        """Get most recent resource snapshot"""
        with self._lock:
            return self.history[-1] if self.history else None
    
    def get_average(self, duration_seconds: int = 60) -> Dict[str, float]:
        """Get average resource usage over duration"""
        with self._lock:
            if not self.history:
                return {}
            
            cutoff = datetime.now() - timedelta(seconds=duration_seconds)
            relevant = [s for s in self.history if s.timestamp >= cutoff]
            
            if not relevant:
                return {}
            
            return {
                'cpu_percent': sum(s.cpu_percent for s in relevant) / len(relevant),
                'memory_percent': sum(s.memory_percent for s in relevant) / len(relevant),
                'memory_mb': sum(s.memory_mb for s in relevant) / len(relevant),
            }
    
    def get_peak(self, duration_seconds: int = 60) -> Dict[str, float]:
        """Get peak resource usage over duration"""
        with self._lock:
            if not self.history:
                return {}
            
            cutoff = datetime.now() - timedelta(seconds=duration_seconds)
            relevant = [s for s in self.history if s.timestamp >= cutoff]
            
            if not relevant:
                return {}
            
            return {
                'cpu_percent': max(s.cpu_percent for s in relevant),
                'memory_percent': max(s.memory_percent for s in relevant),
                'memory_mb': max(s.memory_mb for s in relevant),
            }


# ============================================================================
# RESOURCE ALLOCATION
# ============================================================================

class ResourceAllocator:
    """Allocates and tracks resources for execution jobs"""
    
    def __init__(self, system_limits: Optional[ResourceLimits] = None):
        self.system_limits = system_limits or self._detect_system_limits()
        self.allocations: Dict[str, ResourceLimits] = {}
        self.available = self._calculate_available()
        self._lock = asyncio.Lock()
    
    def _detect_system_limits(self) -> ResourceLimits:
        """Detect system resource limits"""
        memory = psutil.virtual_memory()
        cpu_count = psutil.cpu_count()
        
        return ResourceLimits(
            max_memory_mb=int(memory.total / (1024 * 1024) * 0.8),  # 80% of total
            max_cpu_percent=100.0 * cpu_count,  # Total CPU capacity
            max_threads=1000,
            max_processes=500,
            max_file_descriptors=1024,
            max_disk_mb=10000,  # 10GB default
            max_network_kb=100000,  # 100MB default
        )
    
    def _calculate_available(self) -> ResourceLimits:
        """Calculate currently available resources"""
        available = ResourceLimits(
            max_memory_mb=self.system_limits.max_memory_mb,
            max_cpu_percent=self.system_limits.max_cpu_percent,
            max_threads=self.system_limits.max_threads,
            max_processes=self.system_limits.max_processes,
            max_file_descriptors=self.system_limits.max_file_descriptors,
            max_disk_mb=self.system_limits.max_disk_mb,
            max_network_kb=self.system_limits.max_network_kb,
        )
        
        # Subtract allocated resources
        for allocation in self.allocations.values():
            available.max_memory_mb -= allocation.max_memory_mb
            available.max_cpu_percent -= allocation.max_cpu_percent
            available.max_threads -= allocation.max_threads
            available.max_processes -= allocation.max_processes
        
        return available
    
    async def allocate(self, job_id: str, requested: ResourceLimits) -> bool:
        """Allocate resources for a job"""
        async with self._lock:
            # Check if resources are available
            if not self._can_allocate(requested):
                return False
            
            # Allocate resources
            self.allocations[job_id] = requested
            self.available = self._calculate_available()
            
            logger.info(f"Allocated resources for job {job_id}: {requested.max_memory_mb}MB memory, "
                       f"{requested.max_cpu_percent}% CPU")
            return True
    
    async def release(self, job_id: str):
        """Release resources allocated to a job"""
        async with self._lock:
            if job_id in self.allocations:
                allocation = self.allocations.pop(job_id)
                self.available = self._calculate_available()
                logger.info(f"Released resources for job {job_id}")
    
    def _can_allocate(self, requested: ResourceLimits) -> bool:
        """Check if requested resources can be allocated"""
        return (
            requested.max_memory_mb <= self.available.max_memory_mb and
            requested.max_cpu_percent <= self.available.max_cpu_percent and
            requested.max_threads <= self.available.max_threads and
            requested.max_processes <= self.available.max_processes
        )
    
    async def wait_for_resources(self, requested: ResourceLimits, timeout: float = 60) -> bool:
        """Wait for resources to become available"""
        start = time.time()
        
        while time.time() - start < timeout:
            if await self.allocate("temp_check", requested):
                await self.release("temp_check")
                return True
            await asyncio.sleep(1)
        
        return False
    
    def get_utilization(self) -> Dict[str, float]:
        """Get current resource utilization percentages"""
        total_allocated_memory = sum(a.max_memory_mb for a in self.allocations.values())
        total_allocated_cpu = sum(a.max_cpu_percent for a in self.allocations.values())
        
        return {
            'memory_utilization': (total_allocated_memory / self.system_limits.max_memory_mb) * 100,
            'cpu_utilization': (total_allocated_cpu / self.system_limits.max_cpu_percent) * 100,
            'active_allocations': len(self.allocations),
        }


# ============================================================================
# RESOURCE MANAGER
# ============================================================================

class NexusResourceManager:
    """Main resource management system"""
    
    def __init__(self, config: Optional[ResourceLimits] = None):
        self.config = config or ResourceLimits()
        self.monitor = ResourceMonitor()
        self.allocator = ResourceAllocator(config)
        self.job_resources: Dict[str, Dict[str, Any]] = {}
        self.enforcement_enabled = True
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        """Initialize resource manager"""
        self.monitor.start()
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Resource manager initialized")
    
    async def shutdown(self):
        """Shutdown resource manager"""
        self.monitor.stop()
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Resource manager shut down")
    
    async def allocate_for_job(self, job: ExecutionJob) -> bool:
        """Allocate resources for an execution job"""
        requested = job.request.config.resources
        
        # Try to allocate
        if await self.allocator.allocate(job.id, requested):
            self.job_resources[job.id] = {
                'allocated': requested,
                'start_time': datetime.now(),
                'snapshots': []
            }
            return True
        
        # If allocation failed, try waiting
        logger.info(f"Resources not available for job {job.id}, waiting...")
        if await self.allocator.wait_for_resources(requested, timeout=30):
            return await self.allocate_for_job(job)
        
        logger.warning(f"Failed to allocate resources for job {job.id}")
        return False
    
    async def release_for_job(self, job_id: str):
        """Release resources for a job"""
        await self.allocator.release(job_id)
        
        if job_id in self.job_resources:
            job_data = self.job_resources.pop(job_id)
            duration = (datetime.now() - job_data['start_time']).total_seconds()
            logger.info(f"Job {job_id} completed, used resources for {duration:.2f}s")
    
    def check_job_limits(self, job_id: str) -> Tuple[bool, Optional[str]]:
        """Check if a job is within its resource limits"""
        if not self.enforcement_enabled:
            return True, None
        
        if job_id not in self.job_resources:
            return True, None
        
        job_data = self.job_resources[job_id]
        limits = job_data['allocated']
        current = self.monitor.get_current()
        
        if not current:
            return True, None
        
        # Check memory limit
        if current.memory_mb > limits.max_memory_mb:
            return False, f"Memory limit exceeded: {current.memory_mb}MB > {limits.max_memory_mb}MB"
        
        # Check CPU limit (averaged over last 5 seconds)
        avg_cpu = self.monitor.get_average(5).get('cpu_percent', 0)
        if avg_cpu > limits.max_cpu_percent:
            return False, f"CPU limit exceeded: {avg_cpu:.1f}% > {limits.max_cpu_percent}%"
        
        # Check execution time
        elapsed = (datetime.now() - job_data['start_time']).total_seconds()
        if elapsed > limits.max_execution_time:
            return False, f"Execution time limit exceeded: {elapsed:.1f}s > {limits.max_execution_time}s"
        
        return True, None
    
    async def enforce_limits(self, job_id: str, process: Optional[psutil.Process] = None):
        """Enforce resource limits for a job"""
        if not self.enforcement_enabled:
            return
        
        within_limits, violation = self.check_job_limits(job_id)
        
        if not within_limits:
            logger.warning(f"Job {job_id} violated limits: {violation}")
            
            # Terminate the process if provided
            if process:
                try:
                    process.terminate()
                    await asyncio.sleep(1)
                    if process.is_running():
                        process.kill()
                except psutil.NoSuchProcess:
                    pass
            
            # Release resources
            await self.release_for_job(job_id)
    
    async def _cleanup_loop(self):
        """Periodic cleanup of stale allocations"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Find and clean up stale allocations
                now = datetime.now()
                stale_jobs = []
                
                for job_id, job_data in self.job_resources.items():
                    elapsed = (now - job_data['start_time']).total_seconds()
                    max_time = job_data['allocated'].max_execution_time
                    
                    # If job has been running for more than 2x its limit, consider it stale
                    if elapsed > max_time * 2:
                        stale_jobs.append(job_id)
                
                for job_id in stale_jobs:
                    logger.warning(f"Cleaning up stale job {job_id}")
                    await self.release_for_job(job_id)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get resource manager status"""
        return {
            'monitor': {
                'running': self.monitor.monitoring,
                'history_size': len(self.monitor.history),
                'current': self.monitor.get_current().__dict__ if self.monitor.get_current() else None,
                'average_1min': self.monitor.get_average(60),
                'peak_1min': self.monitor.get_peak(60),
            },
            'allocator': {
                'utilization': self.allocator.get_utilization(),
                'available': self.allocator.available.to_dict(),
                'active_jobs': len(self.allocator.allocations),
            },
            'jobs': {
                'active': len(self.job_resources),
                'job_ids': list(self.job_resources.keys()),
            }
        }
    
    def get_job_metrics(self, job_id: str) -> Dict[MetricType, float]:
        """Get resource metrics for a specific job"""
        if job_id not in self.job_resources:
            return {}
        
        job_data = self.job_resources[job_id]
        duration = (datetime.now() - job_data['start_time']).total_seconds()
        
        # Get average resource usage for the job duration
        avg = self.monitor.get_average(int(duration))
        peak = self.monitor.get_peak(int(duration))
        
        return {
            MetricType.EXECUTION_TIME: duration,
            MetricType.MEMORY_USAGE: avg.get('memory_mb', 0),
            MetricType.CPU_USAGE: avg.get('cpu_percent', 0),
        }


# ============================================================================
# RESOURCE POOL
# ============================================================================

class ResourcePool:
    """Pool of pre-allocated resources for faster allocation"""
    
    def __init__(self, pool_size: int = 10, resource_template: Optional[ResourceLimits] = None):
        self.pool_size = pool_size
        self.template = resource_template or ResourceLimits(
            max_memory_mb=256,
            max_cpu_percent=25,
            max_execution_time=30
        )
        self.pool: List[ResourceLimits] = []
        self.allocated: Dict[str, ResourceLimits] = {}
        self._lock = asyncio.Lock()
        
        # Pre-allocate pool
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize resource pool"""
        for _ in range(self.pool_size):
            self.pool.append(ResourceLimits(
                max_memory_mb=self.template.max_memory_mb,
                max_cpu_percent=self.template.max_cpu_percent,
                max_execution_time=self.template.max_execution_time,
                max_threads=self.template.max_threads,
                max_processes=self.template.max_processes,
            ))
    
    async def acquire(self, job_id: str) -> Optional[ResourceLimits]:
        """Acquire resources from pool"""
        async with self._lock:
            if self.pool:
                resources = self.pool.pop()
                self.allocated[job_id] = resources
                return resources
            return None
    
    async def release(self, job_id: str):
        """Release resources back to pool"""
        async with self._lock:
            if job_id in self.allocated:
                resources = self.allocated.pop(job_id)
                if len(self.pool) < self.pool_size:
                    self.pool.append(resources)
    
    def get_status(self) -> Dict[str, int]:
        """Get pool status"""
        return {
            'available': len(self.pool),
            'allocated': len(self.allocated),
            'total': self.pool_size,
        }