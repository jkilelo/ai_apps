"""Comprehensive LLM Monitoring and Observability System

This module provides enterprise-grade monitoring for multi-model LLM operations:
- Real-time performance metrics collection
- Cost tracking and budget alerting
- Quality scoring and trend analysis
- Provider comparison and benchmarking
- SLA monitoring and alerting
- Custom dashboards and reporting
- Integration with external monitoring systems
"""

from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from pydantic import BaseModel, Field
from loguru import logger
from enum import Enum
import asyncio
import time
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics
import hashlib
import aiohttp
from pathlib import Path


class MetricType(str, Enum):
    """Types of metrics collected"""
    COUNTER = "counter"          # Incremental counters
    GAUGE = "gauge"              # Current value metrics
    HISTOGRAM = "histogram"      # Distribution of values
    TIMER = "timer"              # Time-based measurements
    RATE = "rate"                # Rate of change metrics


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    SILENCED = "silenced"
    ACKNOWLEDGED = "acknowledged"


@dataclass
class MetricPoint:
    """Individual metric data point"""
    timestamp: datetime
    value: Union[int, float, str]
    labels: Dict[str, str]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MetricSeries:
    """Time series of metric points"""
    name: str
    metric_type: MetricType
    points: deque
    labels: Dict[str, str]
    description: str = ""
    unit: str = ""
    retention_hours: int = 24
    
    def __post_init__(self):
        if not isinstance(self.points, deque):
            self.points = deque(self.points, maxlen=10000)  # Limit memory usage
    
    def add_point(self, value: Union[int, float, str], labels: Optional[Dict[str, str]] = None):
        """Add a new metric point"""
        point_labels = {**self.labels, **(labels or {})}
        point = MetricPoint(
            timestamp=datetime.now(),
            value=value,
            labels=point_labels
        )
        self.points.append(point)
        self._cleanup_old_points()
    
    def _cleanup_old_points(self):
        """Remove old points beyond retention period"""
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        while self.points and self.points[0].timestamp < cutoff_time:
            self.points.popleft()
    
    def get_recent_values(self, minutes: int = 5) -> List[Union[int, float]]:
        """Get values from recent time period"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [
            point.value for point in self.points
            if point.timestamp >= cutoff_time and isinstance(point.value, (int, float))
        ]
    
    def calculate_statistics(self, minutes: int = 60) -> Dict[str, float]:
        """Calculate statistics for recent period"""
        values = self.get_recent_values(minutes)
        if not values:
            return {}
        
        return {
            "count": len(values),
            "sum": sum(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "stddev": statistics.stdev(values) if len(values) > 1 else 0.0
        }


@dataclass
class Alert:
    """Alert definition and state"""
    id: str
    name: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    condition: str  # Alert condition expression
    threshold_value: Union[int, float]
    comparison_operator: str  # ">", "<", "==", "!=", ">=", "<="
    metric_name: str
    evaluation_window_minutes: int = 5
    consecutive_violations: int = 1
    current_violations: int = 0
    created_at: datetime = None
    triggered_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    last_evaluation: Optional[datetime] = None
    notification_channels: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.notification_channels is None:
            self.notification_channels = []
        if self.metadata is None:
            self.metadata = {}


class LLMMetricsCollector:
    """Collects and stores LLM performance metrics"""
    
    def __init__(self, retention_hours: int = 24):
        self.metrics: Dict[str, MetricSeries] = {}
        self.retention_hours = retention_hours
        self._initialize_default_metrics()
    
    def _initialize_default_metrics(self):
        """Initialize standard LLM metrics"""
        default_metrics = [
            # Request metrics
            ("llm_requests_total", MetricType.COUNTER, "Total LLM requests", "requests"),
            ("llm_requests_successful", MetricType.COUNTER, "Successful LLM requests", "requests"),
            ("llm_requests_failed", MetricType.COUNTER, "Failed LLM requests", "requests"),
            
            # Latency metrics
            ("llm_request_duration_ms", MetricType.HISTOGRAM, "Request duration", "milliseconds"),
            ("llm_token_processing_rate", MetricType.GAUGE, "Tokens processed per second", "tokens/sec"),
            
            # Cost metrics
            ("llm_cost_total", MetricType.COUNTER, "Total cost", "USD"),
            ("llm_cost_per_request", MetricType.HISTOGRAM, "Cost per request", "USD"),
            ("llm_tokens_consumed", MetricType.COUNTER, "Total tokens consumed", "tokens"),
            
            # Quality metrics
            ("llm_response_quality_score", MetricType.HISTOGRAM, "Response quality score", "score"),
            ("llm_response_length", MetricType.HISTOGRAM, "Response length", "characters"),
            
            # Provider metrics
            ("llm_provider_availability", MetricType.GAUGE, "Provider availability", "percentage"),
            ("llm_provider_error_rate", MetricType.GAUGE, "Provider error rate", "percentage"),
            
            # System metrics
            ("llm_queue_depth", MetricType.GAUGE, "Request queue depth", "requests"),
            ("llm_concurrent_requests", MetricType.GAUGE, "Concurrent requests", "requests"),
            ("llm_rate_limit_hits", MetricType.COUNTER, "Rate limit violations", "hits")
        ]
        
        for name, metric_type, description, unit in default_metrics:
            self.create_metric(name, metric_type, description, unit)
    
    def create_metric(
        self,
        name: str,
        metric_type: MetricType,
        description: str = "",
        unit: str = "",
        labels: Optional[Dict[str, str]] = None
    ) -> MetricSeries:
        """Create a new metric series"""
        if name in self.metrics:
            logger.warning(f"Metric {name} already exists")
            return self.metrics[name]
        
        metric = MetricSeries(
            name=name,
            metric_type=metric_type,
            points=deque(maxlen=10000),
            labels=labels or {},
            description=description,
            unit=unit,
            retention_hours=self.retention_hours
        )
        
        self.metrics[name] = metric
        logger.debug(f"Created metric: {name} ({metric_type})")
        return metric
    
    def record_metric(
        self,
        name: str,
        value: Union[int, float, str],
        labels: Optional[Dict[str, str]] = None
    ):
        """Record a metric value"""
        if name not in self.metrics:
            logger.warning(f"Metric {name} not found, creating as gauge")
            self.create_metric(name, MetricType.GAUGE)
        
        self.metrics[name].add_point(value, labels)
    
    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        if name not in self.metrics:
            self.create_metric(name, MetricType.COUNTER)
        
        # For counters, we track the increment amount
        self.record_metric(name, value, labels)
    
    def set_gauge(self, name: str, value: Union[int, float], labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric value"""
        if name not in self.metrics:
            self.create_metric(name, MetricType.GAUGE)
        
        self.record_metric(name, value, labels)
    
    def record_histogram(self, name: str, value: Union[int, float], labels: Optional[Dict[str, str]] = None):
        """Record a histogram value"""
        if name not in self.metrics:
            self.create_metric(name, MetricType.HISTOGRAM)
        
        self.record_metric(name, value, labels)
    
    def time_operation(self, name: str, labels: Optional[Dict[str, str]] = None):
        """Context manager for timing operations"""
        return TimerContext(self, name, labels)
    
    def get_metric(self, name: str) -> Optional[MetricSeries]:
        """Get metric series by name"""
        return self.metrics.get(name)
    
    def get_all_metrics(self) -> Dict[str, MetricSeries]:
        """Get all metrics"""
        return self.metrics.copy()
    
    def export_metrics(self, format: str = "prometheus") -> str:
        """Export metrics in specified format"""
        if format == "prometheus":
            return self._export_prometheus_format()
        elif format == "json":
            return self._export_json_format()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_prometheus_format(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        for metric in self.metrics.values():
            # Add help and type comments
            lines.append(f"# HELP {metric.name} {metric.description}")
            
            metric_type_map = {
                MetricType.COUNTER: "counter",
                MetricType.GAUGE: "gauge",
                MetricType.HISTOGRAM: "histogram",
                MetricType.TIMER: "gauge",
                MetricType.RATE: "gauge"
            }
            lines.append(f"# TYPE {metric.name} {metric_type_map[metric.metric_type]}")
            
            # Get recent statistics
            stats = metric.calculate_statistics(5)  # Last 5 minutes
            
            if metric.metric_type == MetricType.HISTOGRAM and stats:
                # Export histogram buckets and statistics
                labels_str = self._format_prometheus_labels(metric.labels)
                lines.append(f"{metric.name}_sum{labels_str} {stats.get('sum', 0)}")
                lines.append(f"{metric.name}_count{labels_str} {stats.get('count', 0)}")
                lines.append(f"{metric.name}_avg{labels_str} {stats.get('mean', 0)}")
            elif stats and 'mean' in stats:
                # Export current value (mean of recent points)
                labels_str = self._format_prometheus_labels(metric.labels)
                lines.append(f"{metric.name}{labels_str} {stats['mean']}")
        
        return "\n".join(lines)
    
    def _export_json_format(self) -> str:
        """Export metrics in JSON format"""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {}
        }
        
        for name, metric in self.metrics.items():
            stats = metric.calculate_statistics(5)
            export_data["metrics"][name] = {
                "type": metric.metric_type.value,
                "description": metric.description,
                "unit": metric.unit,
                "labels": metric.labels,
                "statistics": stats,
                "recent_points": len(metric.get_recent_values(5))
            }
        
        return json.dumps(export_data, indent=2)
    
    def _format_prometheus_labels(self, labels: Dict[str, str]) -> str:
        """Format labels for Prometheus format"""
        if not labels:
            return ""
        
        label_pairs = [f'{k}="{v}"' for k, v in labels.items()]
        return "{" + ",".join(label_pairs) + "}"


class TimerContext:
    """Context manager for timing operations"""
    
    def __init__(self, collector: LLMMetricsCollector, name: str, labels: Optional[Dict[str, str]]):
        self.collector = collector
        self.name = name
        self.labels = labels
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            self.collector.record_histogram(self.name, duration_ms, self.labels)


class AlertManager:
    """Manages alerts based on metric thresholds"""
    
    def __init__(self, metrics_collector: LLMMetricsCollector):
        self.metrics_collector = metrics_collector
        self.alerts: Dict[str, Alert] = {}
        self.notification_handlers: Dict[str, Callable] = {}
        self.alert_history: deque = deque(maxlen=1000)
        self._background_task: Optional[asyncio.Task] = None
        self._start_background_evaluation()
    
    def _start_background_evaluation(self):
        """Start background alert evaluation"""
        self._background_task = asyncio.create_task(self._evaluate_alerts_loop())
    
    def create_alert(
        self,
        alert_id: str,
        name: str,
        description: str,
        metric_name: str,
        threshold_value: Union[int, float],
        comparison_operator: str,
        severity: AlertSeverity = AlertSeverity.WARNING,
        evaluation_window_minutes: int = 5,
        consecutive_violations: int = 1,
        notification_channels: Optional[List[str]] = None
    ) -> Alert:
        """Create a new alert rule"""
        alert = Alert(
            id=alert_id,
            name=name,
            description=description,
            severity=severity,
            status=AlertStatus.ACTIVE,
            condition=f"{metric_name} {comparison_operator} {threshold_value}",
            threshold_value=threshold_value,
            comparison_operator=comparison_operator,
            metric_name=metric_name,
            evaluation_window_minutes=evaluation_window_minutes,
            consecutive_violations=consecutive_violations,
            notification_channels=notification_channels or []
        )
        
        self.alerts[alert_id] = alert
        logger.info(f"Created alert: {name} ({alert_id})")
        return alert
    
    def register_notification_handler(self, channel: str, handler: Callable):
        """Register notification handler for a channel"""
        self.notification_handlers[channel] = handler
        logger.info(f"Registered notification handler for channel: {channel}")
    
    async def _evaluate_alerts_loop(self):
        """Background loop for evaluating alerts"""
        while True:
            try:
                await asyncio.sleep(30)  # Evaluate every 30 seconds
                await self._evaluate_all_alerts()
            except Exception as e:
                logger.error(f"Alert evaluation error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _evaluate_all_alerts(self):
        """Evaluate all active alerts"""
        for alert in self.alerts.values():
            if alert.status == AlertStatus.SILENCED:
                continue
            
            await self._evaluate_alert(alert)
    
    async def _evaluate_alert(self, alert: Alert):
        """Evaluate a single alert"""
        metric = self.metrics_collector.get_metric(alert.metric_name)
        if not metric:
            logger.warning(f"Metric {alert.metric_name} not found for alert {alert.id}")
            return
        
        # Get recent values for evaluation window
        recent_values = metric.get_recent_values(alert.evaluation_window_minutes)
        if not recent_values:
            return
        
        # Calculate evaluation value (mean of recent values)
        eval_value = statistics.mean(recent_values)
        
        # Check threshold condition
        threshold_violated = self._check_threshold(
            eval_value,
            alert.comparison_operator,
            alert.threshold_value
        )
        
        alert.last_evaluation = datetime.now()
        
        if threshold_violated:
            alert.current_violations += 1
            
            # Check if we need to trigger the alert
            if (alert.current_violations >= alert.consecutive_violations and
                alert.status != AlertStatus.ACTIVE):
                await self._trigger_alert(alert, eval_value)
        else:
            # Reset violation count
            if alert.current_violations > 0:
                alert.current_violations = 0
                
                # Resolve alert if it was triggered
                if alert.status == AlertStatus.ACTIVE and alert.triggered_at:
                    await self._resolve_alert(alert, eval_value)
    
    def _check_threshold(self, value: float, operator: str, threshold: float) -> bool:
        """Check if value violates threshold"""
        if operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "==":
            return abs(value - threshold) < 0.001  # Float comparison
        elif operator == "!=":
            return abs(value - threshold) >= 0.001
        else:
            logger.warning(f"Unknown comparison operator: {operator}")
            return False
    
    async def _trigger_alert(self, alert: Alert, current_value: float):
        """Trigger an alert"""
        alert.status = AlertStatus.ACTIVE
        alert.triggered_at = datetime.now()
        
        # Add to history
        self.alert_history.append({
            "alert_id": alert.id,
            "action": "triggered",
            "timestamp": alert.triggered_at,
            "current_value": current_value,
            "threshold_value": alert.threshold_value
        })
        
        logger.warning(f"Alert triggered: {alert.name} (current: {current_value}, threshold: {alert.threshold_value})")
        
        # Send notifications
        for channel in alert.notification_channels:
            if channel in self.notification_handlers:
                try:
                    await self._send_notification(alert, channel, "triggered", current_value)
                except Exception as e:
                    logger.error(f"Failed to send notification to {channel}: {e}")
    
    async def _resolve_alert(self, alert: Alert, current_value: float):
        """Resolve an alert"""
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.now()
        
        # Add to history
        self.alert_history.append({
            "alert_id": alert.id,
            "action": "resolved",
            "timestamp": alert.resolved_at,
            "current_value": current_value,
            "threshold_value": alert.threshold_value
        })
        
        logger.info(f"Alert resolved: {alert.name} (current: {current_value})")
        
        # Send resolution notifications
        for channel in alert.notification_channels:
            if channel in self.notification_handlers:
                try:
                    await self._send_notification(alert, channel, "resolved", current_value)
                except Exception as e:
                    logger.error(f"Failed to send resolution notification to {channel}: {e}")
    
    async def _send_notification(self, alert: Alert, channel: str, action: str, current_value: float):
        """Send notification through specified channel"""
        handler = self.notification_handlers[channel]
        
        notification_data = {
            "alert_id": alert.id,
            "alert_name": alert.name,
            "description": alert.description,
            "severity": alert.severity.value,
            "action": action,
            "current_value": current_value,
            "threshold_value": alert.threshold_value,
            "condition": alert.condition,
            "timestamp": datetime.now().isoformat()
        }
        
        await handler(notification_data)
    
    def silence_alert(self, alert_id: str, duration_minutes: int = 60):
        """Silence an alert for specified duration"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.SILENCED
            alert.metadata["silenced_until"] = (datetime.now() + timedelta(minutes=duration_minutes)).isoformat()
            logger.info(f"Silenced alert {alert_id} for {duration_minutes} minutes")
    
    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            logger.info(f"Acknowledged alert {alert_id}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return [alert for alert in self.alerts.values() if alert.status == AlertStatus.ACTIVE]
    
    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent alert history"""
        return list(self.alert_history)[-limit:]


class LLMMonitoringSystem:
    """Comprehensive monitoring system for multi-model LLM operations"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.metrics_collector = LLMMetricsCollector(
            retention_hours=self.config.get('metrics_retention_hours', 24)
        )
        self.alert_manager = AlertManager(self.metrics_collector)
        
        # Performance tracking
        self.request_tracker = defaultdict(list)  # Track request lifecycles
        self.provider_benchmarks = defaultdict(dict)  # Provider performance benchmarks
        
        # Quality tracking
        self.quality_scores = defaultdict(list)  # Track quality scores by provider
        
        # Cost tracking integration
        self.cost_tracker = None  # Will be injected if available
        
        # Setup default alerts
        self._setup_default_alerts()
    
    def set_cost_tracker(self, cost_tracker):
        """Set cost tracker for cost-related monitoring"""
        self.cost_tracker = cost_tracker
    
    def _setup_default_alerts(self):
        """Setup default monitoring alerts"""
        default_alerts = [
            # Error rate alerts
            {
                "id": "high_error_rate",
                "name": "High Error Rate",
                "description": "Error rate above 10%",
                "metric": "llm_provider_error_rate",
                "threshold": 10.0,
                "operator": ">",
                "severity": AlertSeverity.WARNING
            },
            {
                "id": "critical_error_rate",
                "name": "Critical Error Rate",
                "description": "Error rate above 25%",
                "metric": "llm_provider_error_rate",
                "threshold": 25.0,
                "operator": ">",
                "severity": AlertSeverity.CRITICAL
            },
            
            # Latency alerts
            {
                "id": "high_latency",
                "name": "High Response Latency",
                "description": "Average response time above 10 seconds",
                "metric": "llm_request_duration_ms",
                "threshold": 10000,
                "operator": ">",
                "severity": AlertSeverity.WARNING
            },
            
            # Availability alerts
            {
                "id": "low_availability",
                "name": "Low Provider Availability",
                "description": "Provider availability below 95%",
                "metric": "llm_provider_availability",
                "threshold": 95.0,
                "operator": "<",
                "severity": AlertSeverity.ERROR
            },
            
            # Queue depth alerts
            {
                "id": "high_queue_depth",
                "name": "High Request Queue Depth",
                "description": "Request queue depth above 50",
                "metric": "llm_queue_depth",
                "threshold": 50,
                "operator": ">",
                "severity": AlertSeverity.WARNING
            }
        ]
        
        for alert_config in default_alerts:
            self.alert_manager.create_alert(
                alert_id=alert_config["id"],
                name=alert_config["name"],
                description=alert_config["description"],
                metric_name=alert_config["metric"],
                threshold_value=alert_config["threshold"],
                comparison_operator=alert_config["operator"],
                severity=alert_config["severity"]
            )
    
    def start_request_tracking(self, request_id: str, provider: str, task_type: str) -> str:
        """Start tracking a request"""
        tracking_data = {
            "request_id": request_id,
            "provider": provider,
            "task_type": task_type,
            "start_time": time.time(),
            "status": "started"
        }
        
        self.request_tracker[request_id] = tracking_data
        
        # Record metrics
        self.metrics_collector.increment_counter(
            "llm_requests_total",
            labels={"provider": provider, "task_type": task_type}
        )
        
        return request_id
    
    def finish_request_tracking(
        self,
        request_id: str,
        success: bool,
        response_length: int = 0,
        cost: float = 0.0,
        tokens_used: int = 0,
        quality_score: Optional[float] = None,
        error: Optional[str] = None
    ):
        """Finish tracking a request"""
        if request_id not in self.request_tracker:
            logger.warning(f"Request {request_id} not found in tracker")
            return
        
        tracking_data = self.request_tracker[request_id]
        duration_ms = (time.time() - tracking_data["start_time"]) * 1000
        
        provider = tracking_data["provider"]
        task_type = tracking_data["task_type"]
        labels = {"provider": provider, "task_type": task_type}
        
        # Record completion metrics
        if success:
            self.metrics_collector.increment_counter("llm_requests_successful", labels=labels)
        else:
            self.metrics_collector.increment_counter("llm_requests_failed", labels=labels)
        
        # Record duration
        self.metrics_collector.record_histogram("llm_request_duration_ms", duration_ms, labels)
        
        # Record cost if provided
        if cost > 0:
            self.metrics_collector.record_histogram("llm_cost_per_request", cost, labels)
            self.metrics_collector.increment_counter("llm_cost_total", cost, labels)
        
        # Record tokens
        if tokens_used > 0:
            self.metrics_collector.increment_counter("llm_tokens_consumed", tokens_used, labels)
            token_rate = tokens_used / (duration_ms / 1000) if duration_ms > 0 else 0
            self.metrics_collector.set_gauge("llm_token_processing_rate", token_rate, labels)
        
        # Record quality score
        if quality_score is not None:
            self.metrics_collector.record_histogram("llm_response_quality_score", quality_score, labels)
            self.quality_scores[provider].append(quality_score)
            
            # Keep only recent quality scores
            if len(self.quality_scores[provider]) > 100:
                self.quality_scores[provider] = self.quality_scores[provider][-100:]
        
        # Record response length
        if response_length > 0:
            self.metrics_collector.record_histogram("llm_response_length", response_length, labels)
        
        # Update tracking data
        tracking_data.update({
            "status": "completed",
            "success": success,
            "duration_ms": duration_ms,
            "cost": cost,
            "tokens_used": tokens_used,
            "quality_score": quality_score,
            "response_length": response_length,
            "error": error,
            "end_time": time.time()
        })
        
        # Update provider benchmarks
        self._update_provider_benchmarks(provider, tracking_data)
        
        # Clean up old tracking data
        if len(self.request_tracker) > 1000:
            oldest_requests = sorted(self.request_tracker.items(), 
                                   key=lambda x: x[1].get("start_time", 0))[:100]
            for old_request_id, _ in oldest_requests:
                del self.request_tracker[old_request_id]
    
    def _update_provider_benchmarks(self, provider: str, tracking_data: Dict[str, Any]):
        """Update performance benchmarks for provider"""
        if provider not in self.provider_benchmarks:
            self.provider_benchmarks[provider] = {
                "request_count": 0,
                "success_count": 0,
                "total_duration_ms": 0.0,
                "total_cost": 0.0,
                "total_tokens": 0,
                "quality_scores": [],
                "recent_durations": deque(maxlen=100)
            }
        
        benchmarks = self.provider_benchmarks[provider]
        benchmarks["request_count"] += 1
        
        if tracking_data.get("success"):
            benchmarks["success_count"] += 1
        
        benchmarks["total_duration_ms"] += tracking_data.get("duration_ms", 0)
        benchmarks["total_cost"] += tracking_data.get("cost", 0)
        benchmarks["total_tokens"] += tracking_data.get("tokens_used", 0)
        benchmarks["recent_durations"].append(tracking_data.get("duration_ms", 0))
        
        if tracking_data.get("quality_score") is not None:
            benchmarks["quality_scores"].append(tracking_data["quality_score"])
            if len(benchmarks["quality_scores"]) > 100:
                benchmarks["quality_scores"] = benchmarks["quality_scores"][-100:]
    
    def update_provider_health_metrics(self, provider: str, health_data: Dict[str, Any]):
        """Update provider health metrics"""
        labels = {"provider": provider}
        
        # Update availability
        availability = health_data.get("availability", 0.0) * 100  # Convert to percentage
        self.metrics_collector.set_gauge("llm_provider_availability", availability, labels)
        
        # Update error rate
        error_rate = health_data.get("error_rate", 0.0) * 100  # Convert to percentage
        self.metrics_collector.set_gauge("llm_provider_error_rate", error_rate, labels)
    
    def update_system_metrics(self, queue_depth: int = 0, concurrent_requests: int = 0):
        """Update system-level metrics"""
        self.metrics_collector.set_gauge("llm_queue_depth", queue_depth)
        self.metrics_collector.set_gauge("llm_concurrent_requests", concurrent_requests)
    
    def record_rate_limit_hit(self, provider: str):
        """Record a rate limit violation"""
        self.metrics_collector.increment_counter(
            "llm_rate_limit_hits",
            labels={"provider": provider}
        )
    
    def get_performance_report(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "time_window_minutes": time_window_minutes,
            "providers": {},
            "system_metrics": {},
            "alerts": {
                "active_count": len(self.alert_manager.get_active_alerts()),
                "active_alerts": [alert.name for alert in self.alert_manager.get_active_alerts()]
            }
        }
        
        # Provider-specific metrics
        for provider, benchmarks in self.provider_benchmarks.items():
            if benchmarks["request_count"] == 0:
                continue
                
            success_rate = benchmarks["success_count"] / benchmarks["request_count"]
            avg_duration = benchmarks["total_duration_ms"] / benchmarks["request_count"]
            avg_cost = benchmarks["total_cost"] / benchmarks["request_count"] if benchmarks["total_cost"] > 0 else 0
            avg_quality = statistics.mean(benchmarks["quality_scores"]) if benchmarks["quality_scores"] else None
            
            # Recent performance
            recent_durations = list(benchmarks["recent_durations"])
            recent_avg_duration = statistics.mean(recent_durations) if recent_durations else 0
            
            report["providers"][provider] = {
                "request_count": benchmarks["request_count"],
                "success_rate": success_rate,
                "avg_duration_ms": avg_duration,
                "recent_avg_duration_ms": recent_avg_duration,
                "avg_cost_per_request": avg_cost,
                "total_cost": benchmarks["total_cost"],
                "total_tokens": benchmarks["total_tokens"],
                "avg_quality_score": avg_quality
            }
        
        # System metrics
        queue_depth_metric = self.metrics_collector.get_metric("llm_queue_depth")
        if queue_depth_metric:
            recent_values = queue_depth_metric.get_recent_values(time_window_minutes)
            report["system_metrics"]["avg_queue_depth"] = statistics.mean(recent_values) if recent_values else 0
        
        concurrent_requests_metric = self.metrics_collector.get_metric("llm_concurrent_requests")
        if concurrent_requests_metric:
            recent_values = concurrent_requests_metric.get_recent_values(time_window_minutes)
            report["system_metrics"]["avg_concurrent_requests"] = statistics.mean(recent_values) if recent_values else 0
        
        return report
    
    def export_metrics(self, format: str = "prometheus") -> str:
        """Export all metrics"""
        return self.metrics_collector.export_metrics(format)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for monitoring dashboard"""
        return {
            "performance_report": self.get_performance_report(60),
            "active_alerts": [asdict(alert) for alert in self.alert_manager.get_active_alerts()],
            "recent_alert_history": self.alert_manager.get_alert_history(20),
            "provider_comparison": self._generate_provider_comparison(),
            "cost_summary": self._generate_cost_summary() if self.cost_tracker else None
        }
    
    def _generate_provider_comparison(self) -> Dict[str, Any]:
        """Generate provider comparison data"""
        comparison = {}
        
        for provider, benchmarks in self.provider_benchmarks.items():
            if benchmarks["request_count"] == 0:
                continue
                
            comparison[provider] = {
                "success_rate": benchmarks["success_count"] / benchmarks["request_count"],
                "avg_duration_ms": benchmarks["total_duration_ms"] / benchmarks["request_count"],
                "avg_cost_per_request": benchmarks["total_cost"] / benchmarks["request_count"] if benchmarks["total_cost"] > 0 else 0,
                "avg_quality_score": statistics.mean(benchmarks["quality_scores"]) if benchmarks["quality_scores"] else None,
                "total_requests": benchmarks["request_count"]
            }
        
        return comparison
    
    def _generate_cost_summary(self) -> Optional[Dict[str, Any]]:
        """Generate cost summary if cost tracker is available"""
        if not self.cost_tracker:
            return None
        
        try:
            analytics = self.cost_tracker.get_cost_analytics()
            return {
                "budget_status": analytics.get("budget_status", {}),
                "provider_costs": analytics.get("provider_costs", {}),
                "optimization_opportunities": analytics.get("optimization_opportunities", [])
            }
        except Exception as e:
            logger.error(f"Failed to generate cost summary: {e}")
            return None
    
    async def shutdown(self):
        """Gracefully shutdown monitoring system"""
        logger.info("Shutting down LLM monitoring system")
        
        # Shutdown alert manager
        if self.alert_manager._background_task:
            self.alert_manager._background_task.cancel()
            try:
                await self.alert_manager._background_task
            except asyncio.CancelledError:
                pass
        
        logger.info("LLM monitoring system shutdown complete")


# Utility functions for common notification handlers

async def slack_notification_handler(webhook_url: str) -> Callable:
    """Create Slack notification handler"""
    async def handler(notification_data: Dict[str, Any]):
        async with aiohttp.ClientSession() as session:
            payload = {
                "text": f"Alert {notification_data['action']}: {notification_data['alert_name']}",
                "attachments": [
                    {
                        "color": "danger" if notification_data["severity"] in ["error", "critical"] else "warning",
                        "fields": [
                            {"title": "Description", "value": notification_data["description"], "short": False},
                            {"title": "Current Value", "value": str(notification_data["current_value"]), "short": True},
                            {"title": "Threshold", "value": str(notification_data["threshold_value"]), "short": True},
                            {"title": "Condition", "value": notification_data["condition"], "short": True},
                            {"title": "Timestamp", "value": notification_data["timestamp"], "short": True}
                        ]
                    }
                ]
            }
            
            await session.post(webhook_url, json=payload)
    
    return handler


async def email_notification_handler(
    smtp_host: str,
    smtp_port: int,
    username: str,
    password: str,
    from_email: str,
    to_emails: List[str]
) -> Callable:
    """Create email notification handler"""
    async def handler(notification_data: Dict[str, Any]):
        import aiosmtplib
        from email.message import EmailMessage
        
        msg = EmailMessage()
        msg["Subject"] = f"LLM Alert {notification_data['action']}: {notification_data['alert_name']}"
        msg["From"] = from_email
        msg["To"] = ", ".join(to_emails)
        
        body = f"""
        Alert {notification_data['action']}: {notification_data['alert_name']}
        
        Description: {notification_data['description']}
        Severity: {notification_data['severity']}
        Current Value: {notification_data['current_value']}
        Threshold: {notification_data['threshold_value']}
        Condition: {notification_data['condition']}
        Timestamp: {notification_data['timestamp']}
        """
        
        msg.set_content(body)
        
        await aiosmtplib.send(
            msg,
            hostname=smtp_host,
            port=smtp_port,
            username=username,
            password=password,
            use_tls=True
        )
    
    return handler


def console_notification_handler(notification_data: Dict[str, Any]):
    """Simple console notification handler"""
    severity_colors = {
        "info": "\033[94m",      # Blue
        "warning": "\033[93m",  # Yellow
        "error": "\033[91m",    # Red
        "critical": "\033[95m"  # Magenta
    }
    
    color = severity_colors.get(notification_data["severity"], "\033[0m")
    reset_color = "\033[0m"
    
    print(f"{color}[ALERT {notification_data['action'].upper()}] {notification_data['alert_name']}{reset_color}")
    print(f"  Description: {notification_data['description']}")
    print(f"  Current Value: {notification_data['current_value']}")
    print(f"  Threshold: {notification_data['threshold_value']}")
    print(f"  Timestamp: {notification_data['timestamp']}")
    print("---")
