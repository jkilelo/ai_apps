"""
Performance Monitoring Utility

This module provides comprehensive monitoring and metrics collection
for the reverse prompting engine, tracking performance, resource usage,
and operational insights.
"""

import time
import psutil
import threading
import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


class MetricType(Enum):
    """Types of metrics to track."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class MetricValue:
    """A single metric value with timestamp."""

    value: Union[int, float]
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class OperationMetrics:
    """Metrics for a specific operation."""

    name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def finish(self, success: bool = True, error: Optional[str] = None):
        """Mark the operation as finished."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.error = error


class PerformanceMonitor:
    """Main performance monitoring class."""

    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        self.logger = logging.getLogger(__name__)

        # Metrics storage
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.operations: Dict[str, OperationMetrics] = {}
        self.operation_history: deque = deque(maxlen=max_history)

        # System monitoring
        self.system_metrics: deque = deque(maxlen=max_history)
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_interval = 5.0  # seconds

        # Aggregated statistics
        self.stats_cache: Dict[str, Any] = {}
        self.stats_cache_time = 0.0
        self.stats_cache_ttl = 30.0  # seconds

    def start_monitoring(self, interval: float = 5.0):
        """Start system resource monitoring."""
        if self.monitoring_active:
            return

        self.monitoring_interval = interval
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitor_system, daemon=True
        )
        self.monitoring_thread.start()
        self.logger.info("Performance monitoring started")

    def stop_monitoring(self):
        """Stop system resource monitoring."""
        if not self.monitoring_active:
            return

        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=1.0)
        self.logger.info("Performance monitoring stopped")

    def _monitor_system(self):
        """Monitor system resources in background thread."""
        while self.monitoring_active:
            try:
                # Get system metrics
                cpu_percent = psutil.cpu_percent(interval=None)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage("/")

                # Get process metrics
                process = psutil.Process()
                process_memory = process.memory_info()
                process_cpu = process.cpu_percent()

                system_metric = {
                    "timestamp": datetime.now(),
                    "system": {
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "memory_available": memory.available,
                        "memory_total": memory.total,
                        "disk_percent": (disk.total - disk.free) / disk.total * 100,
                        "disk_free": disk.free,
                        "disk_total": disk.total,
                    },
                    "process": {
                        "cpu_percent": process_cpu,
                        "memory_rss": process_memory.rss,
                        "memory_vms": process_memory.vms,
                        "memory_percent": process.memory_percent(),
                    },
                }

                self.system_metrics.append(system_metric)

                # Record as metrics
                self.record_metric("system.cpu_percent", cpu_percent)
                self.record_metric("system.memory_percent", memory.percent)
                self.record_metric("process.cpu_percent", process_cpu)
                self.record_metric("process.memory_percent", process.memory_percent())

            except Exception as e:
                self.logger.warning(f"System monitoring error: {e}")

            time.sleep(self.monitoring_interval)

    def start_operation(
        self, operation_name: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Start tracking an operation."""
        operation_id = f"{operation_name}_{int(time.time() * 1000000)}"

        operation = OperationMetrics(
            name=operation_name, start_time=time.time(), metadata=metadata or {}
        )

        self.operations[operation_id] = operation
        return operation_id

    def end_operation(
        self, operation_id: str, success: bool = True, error: Optional[str] = None
    ):
        """End tracking an operation."""
        if operation_id not in self.operations:
            self.logger.warning(f"Operation {operation_id} not found")
            return

        operation = self.operations[operation_id]
        operation.finish(success=success, error=error)

        # Move to history
        self.operation_history.append(operation)
        del self.operations[operation_id]

        # Record metrics
        self.record_metric(f"operation.{operation.name}.duration", operation.duration)
        self.record_metric(f"operation.{operation.name}.success", 1 if success else 0)

        if not success:
            self.record_metric(f"operation.{operation.name}.errors", 1)

    def record_metric(
        self, name: str, value: Union[int, float], tags: Optional[Dict[str, str]] = None
    ):
        """Record a metric value."""
        metric = MetricValue(value=value, timestamp=datetime.now(), tags=tags or {})

        self.metrics[name].append(metric)

        # Invalidate stats cache
        self.stats_cache_time = 0.0

    def increment_counter(
        self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None
    ):
        """Increment a counter metric."""
        self.record_metric(name, value, tags)

    def set_gauge(
        self, name: str, value: Union[int, float], tags: Optional[Dict[str, str]] = None
    ):
        """Set a gauge metric."""
        self.record_metric(name, value, tags)

    def time_operation(self, operation_name: str):
        """Context manager for timing operations."""
        return TimedOperation(self, operation_name)

    def get_metrics_summary(
        self, metric_name: str, time_window: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Get summary statistics for a metric."""
        if metric_name not in self.metrics:
            return {}

        values = self.metrics[metric_name]
        if not values:
            return {}

        # Filter by time window if specified
        if time_window:
            cutoff_time = datetime.now() - time_window
            values = [v for v in values if v.timestamp >= cutoff_time]

        if not values:
            return {}

        numeric_values = [v.value for v in values]

        return {
            "count": len(numeric_values),
            "min": min(numeric_values),
            "max": max(numeric_values),
            "mean": sum(numeric_values) / len(numeric_values),
            "sum": sum(numeric_values),
            "latest": numeric_values[-1],
            "latest_timestamp": values[-1].timestamp.isoformat(),
        }

    def get_operation_stats(
        self,
        operation_name: Optional[str] = None,
        time_window: Optional[timedelta] = None,
    ) -> Dict[str, Any]:
        """Get statistics for operations."""
        # Get operations from history
        operations = list(self.operation_history)

        # Filter by name if specified
        if operation_name:
            operations = [op for op in operations if op.name == operation_name]

        # Filter by time window if specified
        if time_window:
            cutoff_time = datetime.now() - time_window
            operations = [
                op
                for op in operations
                if datetime.fromtimestamp(op.start_time) >= cutoff_time
            ]

        if not operations:
            return {}

        # Calculate statistics
        total_operations = len(operations)
        successful_operations = sum(1 for op in operations if op.success)
        failed_operations = total_operations - successful_operations

        durations = [op.duration for op in operations if op.duration is not None]

        stats = {
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "success_rate": (
                successful_operations / total_operations
                if total_operations > 0
                else 0.0
            ),
            "failure_rate": (
                failed_operations / total_operations if total_operations > 0 else 0.0
            ),
        }

        if durations:
            stats.update(
                {
                    "avg_duration": sum(durations) / len(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "total_duration": sum(durations),
                }
            )

        return stats

    def get_system_stats(
        self, time_window: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Get system resource statistics."""
        metrics = list(self.system_metrics)

        if time_window:
            cutoff_time = datetime.now() - time_window
            metrics = [m for m in metrics if m["timestamp"] >= cutoff_time]

        if not metrics:
            return {}

        # Calculate averages
        cpu_values = [m["system"]["cpu_percent"] for m in metrics]
        memory_values = [m["system"]["memory_percent"] for m in metrics]
        process_cpu_values = [m["process"]["cpu_percent"] for m in metrics]
        process_memory_values = [m["process"]["memory_percent"] for m in metrics]

        return {
            "sample_count": len(metrics),
            "time_range": {
                "start": metrics[0]["timestamp"].isoformat() if metrics else None,
                "end": metrics[-1]["timestamp"].isoformat() if metrics else None,
            },
            "system": {
                "avg_cpu_percent": (
                    sum(cpu_values) / len(cpu_values) if cpu_values else 0.0
                ),
                "max_cpu_percent": max(cpu_values) if cpu_values else 0.0,
                "avg_memory_percent": (
                    sum(memory_values) / len(memory_values) if memory_values else 0.0
                ),
                "max_memory_percent": max(memory_values) if memory_values else 0.0,
                "latest": metrics[-1]["system"] if metrics else {},
            },
            "process": {
                "avg_cpu_percent": (
                    sum(process_cpu_values) / len(process_cpu_values)
                    if process_cpu_values
                    else 0.0
                ),
                "max_cpu_percent": (
                    max(process_cpu_values) if process_cpu_values else 0.0
                ),
                "avg_memory_percent": (
                    sum(process_memory_values) / len(process_memory_values)
                    if process_memory_values
                    else 0.0
                ),
                "max_memory_percent": (
                    max(process_memory_values) if process_memory_values else 0.0
                ),
                "latest": metrics[-1]["process"] if metrics else {},
            },
        }

    def get_comprehensive_stats(
        self, time_window: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Get comprehensive statistics across all monitored metrics."""
        # Check cache
        current_time = time.time()
        if (
            current_time - self.stats_cache_time
        ) < self.stats_cache_ttl and not time_window:
            return self.stats_cache

        stats = {
            "timestamp": datetime.now().isoformat(),
            "monitoring": {
                "active": self.monitoring_active,
                "interval": self.monitoring_interval,
                "max_history": self.max_history,
            },
            "metrics": {},
            "operations": {},
            "system": {},
        }

        # Get metrics summaries
        for metric_name in self.metrics:
            stats["metrics"][metric_name] = self.get_metrics_summary(
                metric_name, time_window
            )

        # Get operation stats by name
        operation_names = set(op.name for op in self.operation_history)
        for op_name in operation_names:
            stats["operations"][op_name] = self.get_operation_stats(
                op_name, time_window
            )

        # Get overall operation stats
        stats["operations"]["overall"] = self.get_operation_stats(
            time_window=time_window
        )

        # Get system stats
        stats["system"] = self.get_system_stats(time_window)

        # Cache results if no time window specified
        if not time_window:
            self.stats_cache = stats
            self.stats_cache_time = current_time

        return stats

    def export_metrics(self, format_type: str = "json") -> str:
        """Export metrics in various formats."""
        stats = self.get_comprehensive_stats()

        if format_type.lower() == "json":
            import json

            return json.dumps(stats, indent=2, default=str)
        elif format_type.lower() == "csv":
            # Simple CSV export for metrics
            lines = ["metric_name,timestamp,value"]
            for metric_name, metric_values in self.metrics.items():
                for metric in metric_values:
                    lines.append(
                        f"{metric_name},{metric.timestamp.isoformat()},{metric.value}"
                    )
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def clear_metrics(self, older_than: Optional[timedelta] = None):
        """Clear old metrics to free memory."""
        if older_than:
            cutoff_time = datetime.now() - older_than

            # Clear old metrics
            for metric_name in self.metrics:
                self.metrics[metric_name] = deque(
                    (
                        m
                        for m in self.metrics[metric_name]
                        if m.timestamp >= cutoff_time
                    ),
                    maxlen=self.max_history,
                )

            # Clear old operations
            self.operation_history = deque(
                (
                    op
                    for op in self.operation_history
                    if datetime.fromtimestamp(op.start_time) >= cutoff_time
                ),
                maxlen=self.max_history,
            )

            # Clear old system metrics
            self.system_metrics = deque(
                (m for m in self.system_metrics if m["timestamp"] >= cutoff_time),
                maxlen=self.max_history,
            )
        else:
            # Clear all metrics
            self.metrics.clear()
            self.operation_history.clear()
            self.system_metrics.clear()

        # Invalidate cache
        self.stats_cache_time = 0.0
        self.logger.info("Metrics cleared")


class TimedOperation:
    """Context manager for timing operations."""

    def __init__(
        self,
        monitor: PerformanceMonitor,
        operation_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.monitor = monitor
        self.operation_name = operation_name
        self.metadata = metadata
        self.operation_id: Optional[str] = None

    def __enter__(self):
        self.operation_id = self.monitor.start_operation(
            self.operation_name, self.metadata
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.operation_id:
            success = exc_type is None
            error = str(exc_val) if exc_val else None
            self.monitor.end_operation(self.operation_id, success=success, error=error)


# Singleton instance for global use
_global_monitor: Optional[PerformanceMonitor] = None


def get_global_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


def start_global_monitoring(interval: float = 5.0):
    """Start global performance monitoring."""
    monitor = get_global_monitor()
    monitor.start_monitoring(interval)


def stop_global_monitoring():
    """Stop global performance monitoring."""
    global _global_monitor
    if _global_monitor:
        _global_monitor.stop_monitoring()


# For easy importing
__all__ = [
    "PerformanceMonitor",
    "TimedOperation",
    "MetricValue",
    "OperationMetrics",
    "get_global_monitor",
    "start_global_monitoring",
    "stop_global_monitoring",
]
