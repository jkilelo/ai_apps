"""Comprehensive metrics collection and monitoring system"""
import time
import asyncio
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from contextlib import asynccontextmanager
import json
from pathlib import Path

from loguru import logger


@dataclass
class MetricPoint:
    """Single metric measurement"""
    name: str
    value: Union[int, float]
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = "count"


@dataclass
class PerformanceMetrics:
    """Performance tracking metrics"""
    browser_init_time: float = 0.0
    page_load_time: float = 0.0
    action_execution_time: float = 0.0
    llm_response_time: float = 0.0
    total_task_time: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0


class MetricsCollector:
    """Centralized metrics collection and aggregation"""
    
    def __init__(self, buffer_size: int = 1000, flush_interval: int = 60):
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        
        # Metric storage
        self.metrics_buffer: deque = deque(maxlen=buffer_size)
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        
        # Performance tracking
        self.performance_metrics = PerformanceMetrics()
        self.active_timers: Dict[str, float] = {}
        
        # System metrics
        self.start_time = time.time()
        self.last_flush = time.time()
        
        logger.info("Metrics collector initialized")
    
    def increment(self, metric_name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        self.counters[metric_name] += value
        self.record_metric(MetricPoint(
            name=metric_name,
            value=value,
            tags=tags or {},
            unit="count"
        ))
        logger.debug(f"Counter incremented: {metric_name} += {value}")
    
    def gauge(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge metric value"""
        self.gauges[metric_name] = value
        self.record_metric(MetricPoint(
            name=metric_name,
            value=value,
            tags=tags or {},
            unit="gauge"
        ))
        logger.debug(f"Gauge set: {metric_name} = {value}")
    
    def histogram(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a histogram value"""
        self.histograms[metric_name].append(value)
        # Keep only recent values to prevent memory bloat
        if len(self.histograms[metric_name]) > 1000:
            self.histograms[metric_name] = self.histograms[metric_name][-500:]
        
        self.record_metric(MetricPoint(
            name=metric_name,
            value=value,
            tags=tags or {},
            unit="histogram"
        ))
        logger.debug(f"Histogram recorded: {metric_name} = {value}")
    
    def record_metric(self, metric: MetricPoint):
        """Record a metric point in the buffer"""
        self.metrics_buffer.append(metric)
        
        # Auto-flush if buffer is full or enough time has passed
        if (len(self.metrics_buffer) >= self.buffer_size or 
            time.time() - self.last_flush > self.flush_interval):
            asyncio.create_task(self.flush_metrics())
    
    @asynccontextmanager
    async def timer(self, metric_name: str, tags: Optional[Dict[str, str]] = None):
        """Context manager for timing operations"""
        start_time = time.time()
        self.active_timers[metric_name] = start_time
        
        try:
            yield
        finally:
            duration = time.time() - start_time
            del self.active_timers[metric_name]
            self.histogram(f"{metric_name}_duration", duration * 1000, tags)  # ms
            logger.debug(f"Timer completed: {metric_name} took {duration:.3f}s")
    
    def start_timer(self, timer_name: str):
        """Start a named timer"""
        self.active_timers[timer_name] = time.time()
        logger.debug(f"Timer started: {timer_name}")
    
    def stop_timer(self, timer_name: str, tags: Optional[Dict[str, str]] = None) -> Optional[float]:
        """Stop a named timer and record duration"""
        if timer_name not in self.active_timers:
            logger.warning(f"Timer {timer_name} not found")
            return None
        
        start_time = self.active_timers.pop(timer_name)
        duration = time.time() - start_time
        self.histogram(f"{timer_name}_duration", duration * 1000, tags)
        logger.debug(f"Timer stopped: {timer_name} took {duration:.3f}s")
        return duration
    
    def track_browser_init(self, duration: float):
        """Track browser initialization time"""
        self.performance_metrics.browser_init_time = duration
        self.histogram("browser_init_time", duration * 1000)
    
    def track_page_load(self, url: str, duration: float):
        """Track page load performance"""
        self.performance_metrics.page_load_time = duration
        self.histogram("page_load_time", duration * 1000, {"url": url})
    
    def track_action_execution(self, action_type: str, duration: float, success: bool):
        """Track action execution metrics"""
        self.performance_metrics.action_execution_time = duration
        tags = {"action_type": action_type, "success": str(success)}
        self.histogram("action_execution_time", duration * 1000, tags)
        self.increment("actions_total", tags=tags)
        
        if success:
            self.increment("actions_successful", tags={"action_type": action_type})
        else:
            self.increment("actions_failed", tags={"action_type": action_type})
    
    def track_llm_usage(self, provider: str, model: str, tokens: int, duration: float, cost: Optional[float] = None):
        """Track LLM usage and costs"""
        self.performance_metrics.llm_response_time = duration
        tags = {"provider": provider, "model": model}
        
        self.histogram("llm_response_time", duration * 1000, tags)
        self.increment("llm_tokens_used", tokens, tags)
        self.increment("llm_requests", tags=tags)
        
        if cost:
            self.gauge("llm_cost_usd", cost, tags)
    
    def track_memory_usage(self, usage_mb: float):
        """Track memory usage"""
        self.performance_metrics.memory_usage_mb = usage_mb
        self.gauge("memory_usage_mb", usage_mb)
    
    def track_stealth_detection(self, site: str, detected: bool, details: Dict[str, Any]):
        """Track stealth detection results"""
        tags = {"site": site, "detected": str(detected)}
        self.increment("stealth_tests", tags=tags)
        
        if detected:
            self.increment("stealth_detected", tags={"site": site})
            logger.warning(f"Stealth detection on {site}: {details}")
        else:
            self.increment("stealth_passed", tags={"site": site})
    
    def get_histogram_stats(self, metric_name: str) -> Dict[str, float]:
        """Calculate histogram statistics"""
        values = self.histograms.get(metric_name, [])
        if not values:
            return {}
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        return {
            "count": n,
            "min": min(sorted_values),
            "max": max(sorted_values),
            "mean": sum(sorted_values) / n,
            "median": sorted_values[n // 2],
            "p95": sorted_values[int(n * 0.95)],
            "p99": sorted_values[int(n * 0.99)]
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary"""
        uptime = time.time() - self.start_time
        
        return {
            "uptime_seconds": uptime,
            "performance": {
                "browser_init_ms": self.performance_metrics.browser_init_time * 1000,
                "page_load_ms": self.performance_metrics.page_load_time * 1000,
                "action_execution_ms": self.performance_metrics.action_execution_time * 1000,
                "llm_response_ms": self.performance_metrics.llm_response_time * 1000,
                "memory_usage_mb": self.performance_metrics.memory_usage_mb,
            },
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {
                name: self.get_histogram_stats(name) 
                for name in self.histograms.keys()
            },
            "buffer_size": len(self.metrics_buffer),
            "active_timers": len(self.active_timers)
        }
    
    async def flush_metrics(self):
        """Flush metrics to persistent storage"""
        if not self.metrics_buffer:
            return
        
        try:
            # Create metrics directory
            metrics_dir = Path(".claude/metrics")
            metrics_dir.mkdir(exist_ok=True, parents=True)
            
            # Write metrics to file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            metrics_file = metrics_dir / f"metrics_{timestamp}.json"
            
            # Convert metrics to JSON serializable format
            metrics_data = []
            while self.metrics_buffer:
                metric = self.metrics_buffer.popleft()
                metrics_data.append({
                    "name": metric.name,
                    "value": metric.value,
                    "timestamp": metric.timestamp.isoformat(),
                    "tags": metric.tags,
                    "unit": metric.unit
                })
            
            # Write to file
            with open(metrics_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "metrics": metrics_data,
                    "summary": self.get_performance_summary()
                }, f, indent=2)
            
            self.last_flush = time.time()
            logger.info(f"Flushed {len(metrics_data)} metrics to {metrics_file}")
            
        except Exception as e:
            logger.error(f"Failed to flush metrics: {e}")
    
    async def export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        timestamp = int(time.time() * 1000)
        
        # Export counters
        for name, value in self.counters.items():
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name} {value} {timestamp}")
        
        # Export gauges
        for name, value in self.gauges.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {value} {timestamp}")
        
        # Export histograms (basic stats)
        for name, values in self.histograms.items():
            if values:
                stats = self.get_histogram_stats(name)
                lines.append(f"# TYPE {name} histogram")
                lines.append(f"{name}_count {stats['count']} {timestamp}")
                lines.append(f"{name}_sum {sum(values)} {timestamp}")
        
        return "\n".join(lines)
    
    def reset_metrics(self):
        """Reset all metrics (useful for testing)"""
        self.metrics_buffer.clear()
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
        self.active_timers.clear()
        self.performance_metrics = PerformanceMetrics()
        logger.info("All metrics reset")


class HealthChecker:
    """System health monitoring"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.health_checks = {}
        self.last_check = {}
    
    def register_health_check(self, name: str, check_func, interval: int = 60):
        """Register a health check function"""
        self.health_checks[name] = {
            "func": check_func,
            "interval": interval,
            "last_run": 0,
            "last_result": None
        }
        logger.info(f"Registered health check: {name}")
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        current_time = time.time()
        
        for name, check_config in self.health_checks.items():
            # Skip if not time for this check
            if current_time - check_config["last_run"] < check_config["interval"]:
                results[name] = check_config["last_result"]
                continue
            
            try:
                result = await check_config["func"]()
                check_config["last_result"] = result
                check_config["last_run"] = current_time
                results[name] = result
                
                # Record health metrics
                if isinstance(result, dict) and "healthy" in result:
                    self.metrics.gauge(f"health_check_{name}", 1.0 if result["healthy"] else 0.0)
                
                logger.debug(f"Health check {name}: {result}")
                
            except Exception as e:
                error_result = {"healthy": False, "error": str(e)}
                check_config["last_result"] = error_result
                check_config["last_run"] = current_time
                results[name] = error_result
                
                self.metrics.gauge(f"health_check_{name}", 0.0)
                logger.error(f"Health check {name} failed: {e}")
        
        return results


# Global metrics instance
_metrics_collector = None

def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


# Convenience functions
def increment(metric_name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
    """Increment a counter metric"""
    get_metrics_collector().increment(metric_name, value, tags)


def gauge(metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
    """Set a gauge metric value"""
    get_metrics_collector().gauge(metric_name, value, tags)


def histogram(metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
    """Record a histogram value"""
    get_metrics_collector().histogram(metric_name, value, tags)


@asynccontextmanager
async def timer(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """Context manager for timing operations"""
    async with get_metrics_collector().timer(metric_name, tags):
        yield


def track_performance(func_name: str):
    """Decorator for tracking function performance"""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                async with timer(f"function_{func_name}"):
                    return await func(*args, **kwargs)
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = (time.time() - start_time) * 1000
                    histogram(f"function_{func_name}_duration", duration)
                    return result
                except Exception as e:
                    duration = (time.time() - start_time) * 1000
                    histogram(f"function_{func_name}_duration", duration, {"error": "true"})
                    increment(f"function_{func_name}_errors")
                    raise
            return sync_wrapper
    return decorator