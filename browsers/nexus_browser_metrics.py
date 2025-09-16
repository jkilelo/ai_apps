#!/usr/bin/env python3
"""
NEXUS Browser Metrics Module.

Task: ENV-010
Comprehensive metrics collection and monitoring for the NEXUS Browser system.
Full compliance with mypy --strict, flake8, and 100% type coverage.
Uses Pydantic v2 for all data structures.
"""

import time
import json
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Any, Final, Tuple
from enum import Enum
from datetime import datetime
from threading import Lock, Thread
from pydantic import BaseModel, Field, field_validator, ConfigDict, computed_field

from logger import NexusLogger, LogLevel, LoggerConfig, HandlerConfig, HandlerType, LogFormat


# Module constants
TASK_ID: Final[str] = "ENV-010"
MODULE_NAME: Final[str] = "metrics"
QUALITY_ENFORCED: Final[bool] = True


class MetricType(str, Enum):
    """Types of metrics."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"


class AggregationType(str, Enum):
    """Types of aggregations."""

    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    P50 = "p50"
    P90 = "p90"
    P95 = "p95"
    P99 = "p99"
    STDDEV = "stddev"


class ExportFormat(str, Enum):
    """Export format types."""

    JSON = "json"
    PROMETHEUS = "prometheus"
    CSV = "csv"
    GRAPHITE = "graphite"


class AlertCondition(str, Enum):
    """Alert condition types."""

    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    EQUAL = "eq"
    NOT_EQUAL = "ne"
    GREATER_EQUAL = "ge"
    LESS_EQUAL = "le"


class MetricLabel(BaseModel):
    """Metric label for categorization."""

    model_config = ConfigDict(frozen=True)

    key: str = Field(description="Label key")
    value: str = Field(description="Label value")

    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str) -> str:
        """Validate label key."""
        if not v or not v.replace("_", "").isalnum():
            raise ValueError(f"Invalid label key: {v}")
        return v.lower()


class MetricPoint(BaseModel):
    """Single metric data point."""

    model_config = ConfigDict(frozen=True)

    timestamp: float = Field(description="Unix timestamp")
    value: float = Field(description="Metric value")
    labels: List[MetricLabel] = Field(default_factory=list, description="Metric labels")

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: float) -> float:
        """Validate timestamp."""
        if v <= 0:
            raise ValueError(f"Invalid timestamp: {v}")
        return v

    @computed_field  # type: ignore[prop-decorator]
    @property
    def datetime(self) -> datetime:
        """Convert timestamp to datetime."""
        return datetime.fromtimestamp(self.timestamp)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "datetime": self.datetime.isoformat(),
            "value": self.value,
            "labels": {label.key: label.value for label in self.labels}
        }


class MetricSeries(BaseModel):
    """Time series collection of metric points."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(description="Metric name")
    type: MetricType = Field(description="Metric type")
    points: List[MetricPoint] = Field(default_factory=list, description="Data points")
    max_points: int = Field(default=10000, description="Maximum points to retain")
    _lock: Lock = Lock()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate metric name."""
        if not v or not v.replace("_", "").replace(".", "").isalnum():
            raise ValueError(f"Invalid metric name: {v}")
        return v.lower()

    def add_point(self, value: float, labels: Optional[List[MetricLabel]] = None) -> None:
        """Add a new data point."""
        with self._lock:
            point = MetricPoint(
                timestamp=time.time(),
                value=value,
                labels=labels or []
            )
            self.points.append(point)

            # Maintain max points limit
            if len(self.points) > self.max_points:
                self.points = self.points[-self.max_points:]

    def get_recent(self, seconds: int = 60) -> List[MetricPoint]:
        """Get recent points within specified seconds."""
        cutoff = time.time() - seconds
        with self._lock:
            return [p for p in self.points if p.timestamp >= cutoff]

    def clear(self) -> None:
        """Clear all points."""
        with self._lock:
            self.points.clear()


class MetricAggregation(BaseModel):
    """Aggregation result for metrics."""

    model_config = ConfigDict(frozen=True)

    metric_name: str = Field(description="Metric name")
    aggregation_type: AggregationType = Field(description="Aggregation type")
    value: float = Field(description="Aggregated value")
    sample_count: int = Field(description="Number of samples")
    time_window: float = Field(description="Time window in seconds")
    timestamp: float = Field(default_factory=time.time, description="Aggregation timestamp")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric": self.metric_name,
            "type": self.aggregation_type.value,
            "value": self.value,
            "samples": self.sample_count,
            "window_seconds": self.time_window,
            "timestamp": self.timestamp
        }


class AlertConfiguration(BaseModel):
    """Alert configuration for metrics."""

    model_config = ConfigDict(frozen=True)

    metric_name: str = Field(description="Metric to monitor")
    condition: AlertCondition = Field(description="Alert condition")
    threshold: float = Field(description="Threshold value")
    duration: int = Field(default=60, description="Duration in seconds")
    message: str = Field(description="Alert message template")
    enabled: bool = Field(default=True, description="Alert enabled state")

    def check_condition(self, value: float) -> bool:
        """Check if alert condition is met."""
        if self.condition == AlertCondition.GREATER_THAN:
            return value > self.threshold
        elif self.condition == AlertCondition.LESS_THAN:
            return value < self.threshold
        elif self.condition == AlertCondition.EQUAL:
            return abs(value - self.threshold) < 0.0001
        elif self.condition == AlertCondition.NOT_EQUAL:
            return abs(value - self.threshold) >= 0.0001
        elif self.condition == AlertCondition.GREATER_EQUAL:
            return value >= self.threshold
        elif self.condition == AlertCondition.LESS_EQUAL:
            return value <= self.threshold
        return False


class ExportConfiguration(BaseModel):
    """Configuration for metric export."""

    model_config = ConfigDict(frozen=True)

    format: ExportFormat = Field(description="Export format")
    destination: str = Field(description="Export destination (file path or URL)")
    interval: int = Field(default=60, description="Export interval in seconds")
    include_labels: bool = Field(default=True, description="Include labels in export")
    compress: bool = Field(default=False, description="Compress export data")


class Counter:
    """Thread-safe counter metric."""

    def __init__(self, name: str, initial_value: float = 0) -> None:
        """Initialize counter."""
        self.name = name
        self._value = initial_value
        self._lock = Lock()
        self.series = MetricSeries(name=name, type=MetricType.COUNTER)

    def increment(self, amount: float = 1, labels: Optional[List[MetricLabel]] = None) -> None:
        """Increment counter."""
        with self._lock:
            self._value += amount
            self.series.add_point(self._value, labels)

    def reset(self) -> None:
        """Reset counter to zero."""
        with self._lock:
            self._value = 0
            self.series.add_point(0)

    @property
    def value(self) -> float:
        """Get current value."""
        with self._lock:
            return self._value


class Gauge:
    """Thread-safe gauge metric."""

    def __init__(self, name: str, initial_value: float = 0) -> None:
        """Initialize gauge."""
        self.name = name
        self._value = initial_value
        self._lock = Lock()
        self.series = MetricSeries(name=name, type=MetricType.GAUGE)

    def set(self, value: float, labels: Optional[List[MetricLabel]] = None) -> None:
        """Set gauge value."""
        with self._lock:
            self._value = value
            self.series.add_point(value, labels)

    def increment(self, amount: float = 1) -> None:
        """Increment gauge."""
        with self._lock:
            self._value += amount
            self.series.add_point(self._value)

    def decrement(self, amount: float = 1) -> None:
        """Decrement gauge."""
        with self._lock:
            self._value -= amount
            self.series.add_point(self._value)

    @property
    def value(self) -> float:
        """Get current value."""
        with self._lock:
            return self._value


class Histogram:
    """Thread-safe histogram metric."""

    def __init__(self, name: str, buckets: Optional[List[float]] = None) -> None:
        """Initialize histogram."""
        self.name = name
        self.buckets = buckets or [0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
        self._values: List[float] = []
        self._lock = Lock()
        self.series = MetricSeries(name=name, type=MetricType.HISTOGRAM)

    def observe(self, value: float, labels: Optional[List[MetricLabel]] = None) -> None:
        """Add observation to histogram."""
        with self._lock:
            self._values.append(value)
            self.series.add_point(value, labels)

    def get_percentile(self, percentile: float) -> float:
        """Get percentile value."""
        with self._lock:
            if not self._values:
                return 0.0
            sorted_values = sorted(self._values)
            index = int(len(sorted_values) * percentile / 100)
            return sorted_values[min(index, len(sorted_values) - 1)]

    def get_statistics(self) -> Dict[str, float]:
        """Get histogram statistics."""
        with self._lock:
            if not self._values:
                return {"count": 0, "sum": 0, "avg": 0, "min": 0, "max": 0}

            return {
                "count": float(len(self._values)),
                "sum": sum(self._values),
                "avg": statistics.mean(self._values),
                "min": min(self._values),
                "max": max(self._values),
                "stddev": statistics.stdev(self._values) if len(self._values) > 1 else 0,
                "p50": self.get_percentile(50),
                "p90": self.get_percentile(90),
                "p95": self.get_percentile(95),
                "p99": self.get_percentile(99)
            }


class Timer:
    """Context manager for timing operations."""

    def __init__(self, name: str, histogram: Optional[Histogram] = None) -> None:
        """Initialize timer."""
        self.name = name
        self.histogram = histogram or Histogram(f"{name}_duration")
        self.start_time: float = 0

    def __enter__(self) -> "Timer":
        """Start timing."""
        self.start_time = time.time()
        return self

    def __exit__(self, *args: Any) -> None:
        """Stop timing and record duration."""
        duration = time.time() - self.start_time
        self.histogram.observe(duration)


class MetricsCollector:
    """Central metrics collector and manager."""

    def __init__(self, logger: Optional[NexusLogger] = None) -> None:
        """Initialize metrics collector."""
        if logger is None:
            config = LoggerConfig(
                name="metrics_collector",
                level=LogLevel.INFO,
                handlers=[
                    HandlerConfig(
                        handler_type=HandlerType.CONSOLE,
                        level=LogLevel.INFO,
                        format_type=LogFormat.STANDARD
                    )
                ]
            )
            self.logger = NexusLogger(config)
        else:
            self.logger = logger
        self._counters: Dict[str, Counter] = {}
        self._gauges: Dict[str, Gauge] = {}
        self._histograms: Dict[str, Histogram] = {}
        self._alerts: List[AlertConfiguration] = []
        self._lock = Lock()
        self._export_threads: List[Thread] = []
        self._running = True

    def counter(self, name: str) -> Counter:
        """Get or create counter."""
        with self._lock:
            if name not in self._counters:
                self._counters[name] = Counter(name)
            return self._counters[name]

    def gauge(self, name: str) -> Gauge:
        """Get or create gauge."""
        with self._lock:
            if name not in self._gauges:
                self._gauges[name] = Gauge(name)
            return self._gauges[name]

    def histogram(self, name: str, buckets: Optional[List[float]] = None) -> Histogram:
        """Get or create histogram."""
        with self._lock:
            if name not in self._histograms:
                self._histograms[name] = Histogram(name, buckets)
            return self._histograms[name]

    def timer(self, name: str) -> Timer:
        """Create timer context manager."""
        return Timer(name, self.histogram(f"{name}_timer"))

    def add_alert(self, alert: AlertConfiguration) -> None:
        """Add alert configuration."""
        with self._lock:
            self._alerts.append(alert)

    def check_alerts(self) -> List[Tuple[AlertConfiguration, float]]:
        """Check all alerts and return triggered ones."""
        triggered: List[Tuple[AlertConfiguration, float]] = []

        for alert in self._alerts:
            if not alert.enabled:
                continue

            # Get metric value based on type
            value: Optional[float] = None

            if alert.metric_name in self._counters:
                value = self._counters[alert.metric_name].value
            elif alert.metric_name in self._gauges:
                value = self._gauges[alert.metric_name].value
            elif alert.metric_name in self._histograms:
                stats = self._histograms[alert.metric_name].get_statistics()
                value = stats.get("avg", 0)

            if value is not None and alert.check_condition(value):
                triggered.append((alert, value))
                self.logger.warning(
                    f"Alert triggered: {alert.message.format(value=value)}"
                )

        return triggered

    def aggregate(
        self,
        metric_name: str,
        aggregation_type: AggregationType,
        time_window: int = 60
    ) -> Optional[MetricAggregation]:
        """Aggregate metric values."""
        series: Optional[MetricSeries] = None

        # Find metric series
        if metric_name in self._counters:
            series = self._counters[metric_name].series
        elif metric_name in self._gauges:
            series = self._gauges[metric_name].series
        elif metric_name in self._histograms:
            series = self._histograms[metric_name].series

        if not series:
            return None

        # Get recent points
        points = series.get_recent(time_window)
        if not points:
            return None

        values = [p.value for p in points]

        # Calculate aggregation
        result_value: float = 0
        if aggregation_type == AggregationType.SUM:
            result_value = sum(values)
        elif aggregation_type == AggregationType.AVG:
            result_value = statistics.mean(values)
        elif aggregation_type == AggregationType.MIN:
            result_value = min(values)
        elif aggregation_type == AggregationType.MAX:
            result_value = max(values)
        elif aggregation_type == AggregationType.COUNT:
            result_value = float(len(values))
        elif aggregation_type == AggregationType.STDDEV:
            result_value = statistics.stdev(values) if len(values) > 1 else 0
        elif aggregation_type in [
            AggregationType.P50, AggregationType.P90,
            AggregationType.P95, AggregationType.P99
        ]:
            percentile = int(aggregation_type.value[1:])
            sorted_values = sorted(values)
            index = int(len(sorted_values) * percentile / 100)
            result_value = sorted_values[min(index, len(sorted_values) - 1)]

        return MetricAggregation(
            metric_name=metric_name,
            aggregation_type=aggregation_type,
            value=result_value,
            sample_count=len(values),
            time_window=float(time_window)
        )

    def export_json(self, file_path: Path) -> None:
        """Export metrics to JSON file."""
        data: Dict[str, Any] = {
            "timestamp": time.time(),
            "counters": {},
            "gauges": {},
            "histograms": {}
        }

        with self._lock:
            # Export counters
            for name, counter in self._counters.items():
                data["counters"][name] = {
                    "value": counter.value,
                    "points": [p.to_dict() for p in counter.series.get_recent(300)]
                }

            # Export gauges
            for name, gauge in self._gauges.items():
                data["gauges"][name] = {
                    "value": gauge.value,
                    "points": [p.to_dict() for p in gauge.series.get_recent(300)]
                }

            # Export histograms
            for name, histogram in self._histograms.items():
                data["histograms"][name] = {
                    "statistics": histogram.get_statistics(),
                    "points": [p.to_dict() for p in histogram.series.get_recent(300)]
                }

        # Write to file
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines: List[str] = []
        timestamp = int(time.time() * 1000)

        with self._lock:
            # Export counters
            for name, counter in self._counters.items():
                lines.append(f"# TYPE {name} counter")
                lines.append(f"{name} {counter.value} {timestamp}")

            # Export gauges
            for name, gauge in self._gauges.items():
                lines.append(f"# TYPE {name} gauge")
                lines.append(f"{name} {gauge.value} {timestamp}")

            # Export histograms
            for name, histogram in self._histograms.items():
                stats = histogram.get_statistics()
                lines.append(f"# TYPE {name} histogram")
                lines.append(f"{name}_count {stats['count']} {timestamp}")
                lines.append(f"{name}_sum {stats['sum']} {timestamp}")

                # Buckets
                for bucket in histogram.buckets:
                    count = sum(1 for v in histogram._values if v <= bucket)
                    lines.append(f'{name}_bucket{{le="{bucket}"}} {count} {timestamp}')
                lines.append(f'{name}_bucket{{le="+Inf"}} {stats["count"]} {timestamp}')

        return "\n".join(lines)

    def start_export(self, config: ExportConfiguration) -> None:
        """Start automatic metric export."""
        def export_loop() -> None:
            while self._running:
                try:
                    if config.format == ExportFormat.JSON:
                        self.export_json(Path(config.destination))
                    elif config.format == ExportFormat.PROMETHEUS:
                        with open(config.destination, "w") as f:
                            f.write(self.export_prometheus())

                    time.sleep(config.interval)
                except Exception as e:
                    self.logger.error(f"Export failed: {e}")

        thread = Thread(target=export_loop, daemon=True)
        thread.start()
        self._export_threads.append(thread)

    def shutdown(self) -> None:
        """Shutdown metrics collector."""
        self._running = False
        for thread in self._export_threads:
            thread.join(timeout=5)


class PerformanceMetrics:
    """System performance metrics collector."""

    def __init__(self, collector: MetricsCollector) -> None:
        """Initialize performance metrics."""
        self.collector = collector
        self.latency = collector.histogram("system.latency", [0.01, 0.05, 0.1, 0.5, 1.0])
        self.throughput = collector.counter("system.throughput")
        self.errors = collector.counter("system.errors")
        self.cpu_usage = collector.gauge("system.cpu_usage")
        self.memory_usage = collector.gauge("system.memory_usage")
        self.active_connections = collector.gauge("system.connections")

    def record_request(self, duration: float, success: bool = True) -> None:
        """Record request metrics."""
        self.latency.observe(duration)
        self.throughput.increment()
        if not success:
            self.errors.increment()

    def update_resources(self, cpu: float, memory: float) -> None:
        """Update resource usage metrics."""
        self.cpu_usage.set(cpu)
        self.memory_usage.set(memory)


def main() -> None:
    """Demonstrate metrics functionality."""
    print("NEXUS Browser Metrics Module")
    print(f"Task ID: {TASK_ID}")
    print(f"Module: {MODULE_NAME}")
    print(f"Quality Enforced: {QUALITY_ENFORCED}")
    print("-" * 50)

    # Initialize collector
    collector = MetricsCollector()

    # Create performance metrics
    perf = PerformanceMetrics(collector)

    # Simulate some metrics
    print("\nSimulating metrics collection...")

    # Record some requests
    for i in range(10):
        duration = 0.1 * (i % 3 + 1)
        perf.record_request(duration, success=(i % 5 != 0))
        time.sleep(0.01)

    # Update resources
    perf.update_resources(cpu=45.5, memory=62.3)
    perf.active_connections.set(25)

    # Add alert
    alert = AlertConfiguration(
        metric_name="system.errors",
        condition=AlertCondition.GREATER_THAN,
        threshold=2,
        message="Error rate too high: {value}"
    )
    collector.add_alert(alert)

    # Check alerts
    triggered = collector.check_alerts()
    if triggered:
        print(f"\nTriggered alerts: {len(triggered)}")

    # Get aggregations
    print("\nAggregation Results:")
    for metric in ["system.latency", "system.throughput", "system.errors"]:
        for agg_type in [AggregationType.AVG, AggregationType.MAX, AggregationType.COUNT]:
            result = collector.aggregate(metric, agg_type, 60)
            if result:
                print(f"  {metric} {agg_type.value}: {result.value:.2f}")

    # Export metrics
    print("\nExporting metrics...")
    json_path = Path("metrics_export.json")
    collector.export_json(json_path)
    print(f"  JSON export: {json_path}")

    prometheus_data = collector.export_prometheus()
    print(f"  Prometheus format: {len(prometheus_data)} bytes")

    # Cleanup
    collector.shutdown()
    print("\nMetrics module demonstration complete!")


if __name__ == "__main__":
    main()
