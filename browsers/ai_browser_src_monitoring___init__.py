"""Monitoring and observability module for AI-First Smart Browser"""

from .metrics import (
    MetricsCollector,
    PerformanceMetrics, 
    MetricPoint,
    HealthChecker,
    get_metrics_collector,
    increment,
    gauge,
    histogram,
    timer,
    track_performance
)

from .alerts import (
    AlertManager,
    Alert,
    AlertRule,
    AlertSeverity,
    AlertStatus,
    LogAlertHandler,
    FileAlertHandler,
    setup_default_monitoring
)

from .health import (
    HealthMonitor,
    SystemHealth,
    ComponentHealth
)

__all__ = [
    # Metrics
    "MetricsCollector",
    "PerformanceMetrics",
    "MetricPoint", 
    "HealthChecker",
    "get_metrics_collector",
    "increment",
    "gauge", 
    "histogram",
    "timer",
    "track_performance",
    
    # Alerts
    "AlertManager",
    "Alert",
    "AlertRule",
    "AlertSeverity",
    "AlertStatus",
    "LogAlertHandler",
    "FileAlertHandler",
    "setup_default_monitoring",
    
    # Health
    "HealthMonitor",
    "SystemHealth",
    "ComponentHealth"
]