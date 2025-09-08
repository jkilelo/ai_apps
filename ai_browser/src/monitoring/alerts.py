"""Alert system for monitoring critical events and thresholds"""
import asyncio
import json
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

from loguru import logger


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status"""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    metric_name: str
    condition: str  # ">", "<", ">=", "<=", "==", "!="
    threshold: Union[int, float]
    severity: AlertSeverity
    message_template: str
    check_interval: int = 60  # seconds
    cooldown: int = 300  # seconds between repeated alerts
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class Alert:
    """Active alert instance"""
    id: str
    rule_name: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    metric_value: Union[int, float]
    threshold: Union[int, float]
    status: AlertStatus = AlertStatus.OPEN
    tags: Dict[str, str] = field(default_factory=dict)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class AlertManager:
    """Manages alert rules and active alerts"""
    
    def __init__(self, metrics_collector=None):
        self.metrics_collector = metrics_collector
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.handlers: List[Callable[[Alert], None]] = []
        self.last_check: Dict[str, datetime] = {}
        self.last_alert: Dict[str, datetime] = {}
        
        # Default alert rules
        self._setup_default_rules()
        logger.info("Alert manager initialized")
    
    def _setup_default_rules(self):
        """Setup default monitoring rules"""
        default_rules = [
            AlertRule(
                name="high_memory_usage",
                metric_name="memory_usage_mb",
                condition=">",
                threshold=1000.0,
                severity=AlertSeverity.WARNING,
                message_template="High memory usage: {value}MB (threshold: {threshold}MB)",
                check_interval=30
            ),
            AlertRule(
                name="slow_page_load",
                metric_name="page_load_time",
                condition=">",
                threshold=10000.0,  # 10 seconds in ms
                severity=AlertSeverity.WARNING,
                message_template="Slow page load: {value}ms (threshold: {threshold}ms)",
                check_interval=60
            ),
            AlertRule(
                name="action_failure_rate",
                metric_name="action_failure_rate",
                condition=">",
                threshold=0.2,  # 20% failure rate
                severity=AlertSeverity.ERROR,
                message_template="High action failure rate: {value:.1%} (threshold: {threshold:.1%})",
                check_interval=120
            ),
            AlertRule(
                name="stealth_detection",
                metric_name="stealth_detection_rate",
                condition=">",
                threshold=0.1,  # 10% detection rate
                severity=AlertSeverity.CRITICAL,
                message_template="Stealth detection rate too high: {value:.1%} (threshold: {threshold:.1%})",
                check_interval=300
            ),
            AlertRule(
                name="llm_cost_spike",
                metric_name="llm_cost_per_hour",
                condition=">",
                threshold=10.0,  # $10/hour
                severity=AlertSeverity.WARNING,
                message_template="LLM cost spike: ${value:.2f}/hour (threshold: ${threshold:.2f}/hour)",
                check_interval=300
            )
        ]
        
        for rule in default_rules:
            self.add_rule(rule)
    
    def add_rule(self, rule: AlertRule):
        """Add an alert rule"""
        self.rules[rule.name] = rule
        logger.info(f"Added alert rule: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """Remove an alert rule"""
        if rule_name in self.rules:
            del self.rules[rule_name]
            logger.info(f"Removed alert rule: {rule_name}")
    
    def add_handler(self, handler: Callable[[Alert], None]):
        """Add alert handler function"""
        self.handlers.append(handler)
        logger.info("Added alert handler")
    
    async def check_rules(self):
        """Check all alert rules against current metrics"""
        if not self.metrics_collector:
            return
        
        current_time = datetime.now()
        
        for rule_name, rule in self.rules.items():
            # Check if it's time to evaluate this rule
            if (rule_name in self.last_check and 
                (current_time - self.last_check[rule_name]).total_seconds() < rule.check_interval):
                continue
            
            try:
                await self._evaluate_rule(rule, current_time)
                self.last_check[rule_name] = current_time
                
            except Exception as e:
                logger.error(f"Error evaluating rule {rule_name}: {e}")
    
    async def _evaluate_rule(self, rule: AlertRule, current_time: datetime):
        """Evaluate a single alert rule"""
        # Get metric value
        metric_value = await self._get_metric_value(rule.metric_name)
        if metric_value is None:
            return
        
        # Check condition
        condition_met = self._check_condition(metric_value, rule.condition, rule.threshold)
        
        alert_id = f"{rule.name}_{rule.metric_name}"
        
        if condition_met:
            # Check cooldown period
            if (rule.name in self.last_alert and 
                (current_time - self.last_alert[rule.name]).total_seconds() < rule.cooldown):
                return
            
            # Create or update alert
            if alert_id not in self.active_alerts:
                alert = Alert(
                    id=alert_id,
                    rule_name=rule.name,
                    severity=rule.severity,
                    message=rule.message_template.format(
                        value=metric_value,
                        threshold=rule.threshold
                    ),
                    timestamp=current_time,
                    metric_value=metric_value,
                    threshold=rule.threshold,
                    tags=rule.tags
                )
                
                self.active_alerts[alert_id] = alert
                self.alert_history.append(alert)
                self.last_alert[rule.name] = current_time
                
                # Notify handlers
                await self._notify_handlers(alert)
                logger.warning(f"Alert triggered: {alert.message}")
        
        else:
            # Resolve alert if it exists
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = current_time
                del self.active_alerts[alert_id]
                
                await self._notify_handlers(alert)
                logger.info(f"Alert resolved: {alert.rule_name}")
    
    async def _get_metric_value(self, metric_name: str) -> Optional[Union[int, float]]:
        """Get current value for a metric"""
        if not self.metrics_collector:
            return None
        
        # Check gauges first
        if metric_name in self.metrics_collector.gauges:
            return self.metrics_collector.gauges[metric_name]
        
        # Check counters
        if metric_name in self.metrics_collector.counters:
            return self.metrics_collector.counters[metric_name]
        
        # Check calculated metrics
        if metric_name == "action_failure_rate":
            total_actions = self.metrics_collector.counters.get("actions_total", 0)
            failed_actions = self.metrics_collector.counters.get("actions_failed", 0)
            return failed_actions / max(total_actions, 1)
        
        if metric_name == "stealth_detection_rate":
            total_tests = self.metrics_collector.counters.get("stealth_tests", 0)
            detected_tests = self.metrics_collector.counters.get("stealth_detected", 0)
            return detected_tests / max(total_tests, 1)
        
        if metric_name == "llm_cost_per_hour":
            # Calculate cost per hour based on recent usage
            total_cost = self.metrics_collector.gauges.get("llm_cost_usd", 0)
            uptime_hours = (datetime.now() - datetime.fromtimestamp(
                self.metrics_collector.start_time)).total_seconds() / 3600
            return total_cost / max(uptime_hours, 1)
        
        # Check histogram averages
        if metric_name in self.metrics_collector.histograms:
            values = self.metrics_collector.histograms[metric_name]
            if values:
                return sum(values) / len(values)
        
        return None
    
    def _check_condition(self, value: Union[int, float], condition: str, threshold: Union[int, float]) -> bool:
        """Check if condition is met"""
        if condition == ">":
            return value > threshold
        elif condition == "<":
            return value < threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return value == threshold
        elif condition == "!=":
            return value != threshold
        else:
            logger.error(f"Unknown condition: {condition}")
            return False
    
    async def _notify_handlers(self, alert: Alert):
        """Notify all alert handlers"""
        for handler in self.handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                logger.error(f"Alert handler error: {e}")
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an active alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            logger.info(f"Alert acknowledged: {alert_id}")
            return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Manually resolve an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            del self.active_alerts[alert_id]
            logger.info(f"Alert manually resolved: {alert_id}")
            return True
        return False
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get all active alerts, optionally filtered by severity"""
        alerts = list(self.active_alerts.values())
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)
    
    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get recent alert history"""
        return sorted(self.alert_history[-limit:], key=lambda a: a.timestamp, reverse=True)
    
    async def export_alerts(self, filepath: Optional[Path] = None) -> Path:
        """Export alerts to JSON file"""
        if not filepath:
            filepath = Path(".claude/monitoring/alerts.json")
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "active_alerts": [
                {
                    "id": alert.id,
                    "rule_name": alert.rule_name,
                    "severity": alert.severity.value,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "metric_value": alert.metric_value,
                    "threshold": alert.threshold,
                    "status": alert.status.value,
                    "tags": alert.tags
                }
                for alert in self.active_alerts.values()
            ],
            "recent_history": [
                {
                    "id": alert.id,
                    "rule_name": alert.rule_name,
                    "severity": alert.severity.value,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "status": alert.status.value,
                    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
                }
                for alert in self.get_alert_history(50)
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Alerts exported to {filepath}")
        return filepath


# Default alert handlers
class LogAlertHandler:
    """Log alerts to structured logs"""
    
    def __init__(self):
        self.logger = logger.bind(component="alerts")
    
    def __call__(self, alert: Alert):
        if alert.status == AlertStatus.OPEN:
            self.logger.log(
                alert.severity.value.upper(),
                f"ALERT: {alert.message}",
                extra={
                    "alert_id": alert.id,
                    "rule_name": alert.rule_name,
                    "metric_value": alert.metric_value,
                    "threshold": alert.threshold,
                    "tags": alert.tags
                }
            )
        elif alert.status == AlertStatus.RESOLVED:
            self.logger.info(
                f"ALERT RESOLVED: {alert.rule_name}",
                extra={
                    "alert_id": alert.id,
                    "duration": (alert.resolved_at - alert.timestamp).total_seconds()
                }
            )


class FileAlertHandler:
    """Write alerts to file"""
    
    def __init__(self, filepath: Path = Path(".claude/monitoring/alerts.log")):
        self.filepath = filepath
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
    
    def __call__(self, alert: Alert):
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "alert": {
                "id": alert.id,
                "rule_name": alert.rule_name,
                "severity": alert.severity.value,
                "message": alert.message,
                "status": alert.status.value,
                "metric_value": alert.metric_value,
                "tags": alert.tags
            }
        }
        
        with open(self.filepath, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")


# Convenience function
def setup_default_monitoring(metrics_collector=None) -> AlertManager:
    """Setup default alert monitoring with handlers"""
    alert_manager = AlertManager(metrics_collector)
    
    # Add default handlers
    alert_manager.add_handler(LogAlertHandler())
    alert_manager.add_handler(FileAlertHandler())
    
    logger.info("Default monitoring setup complete")
    return alert_manager