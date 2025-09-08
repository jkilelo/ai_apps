"""Centralized logging configuration for AI-First Smart Browser"""
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
from contextvars import ContextVar

# Context variables for structured logging
request_id: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
task_id: ContextVar[Optional[str]] = ContextVar('task_id', default=None)
user_agent: ContextVar[Optional[str]] = ContextVar('user_agent', default=None)


class StructuredFormatter:
    """Custom formatter for structured JSON logging"""
    
    def __init__(self, include_extra: bool = True):
        self.include_extra = include_extra
    
    def __call__(self, record: Dict[str, Any]) -> str:
        """Format log record as structured JSON"""
        # Base log structure
        log_entry = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "logger": record["name"],
            "function": record["function"],
            "line": record["line"],
            "message": record["message"],
        }
        
        # Add context variables
        if request_id.get():
            log_entry["request_id"] = request_id.get()
        if task_id.get():
            log_entry["task_id"] = task_id.get()
        if user_agent.get():
            log_entry["user_agent"] = user_agent.get()
        
        # Add extra fields from record
        if self.include_extra and "extra" in record:
            extra = record["extra"]
            if isinstance(extra, dict):
                log_entry.update(extra)
        
        # Add exception info if present
        if record.get("exception"):
            log_entry["exception"] = {
                "type": record["exception"].type.__name__ if record["exception"].type else None,
                "value": str(record["exception"].value) if record["exception"].value else None,
                "traceback": record["exception"].traceback if record["exception"].traceback else None
            }
        
        return json.dumps(log_entry, default=str)


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    enable_console: bool = True,
    enable_file: bool = True,
    enable_json: bool = True,
    max_file_size: str = "10 MB",
    retention_days: int = 7
):
    """Setup comprehensive logging configuration"""
    
    # Remove default handler
    logger.remove()
    
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Console logging (human-readable)
    if enable_console:
        def console_formatter(record):
            # Build format with optional fields
            req_id = record["extra"].get("request_id", "") if "extra" in record else ""
            if req_id:
                req_id = f" | <cyan>{req_id}</cyan>"
            return (
                f"<green>{record['time']:YYYY-MM-DD HH:mm:ss}</green> | "
                f"<level>{record['level'].name: <8}</level>"
                f"{req_id} | "
                f"<cyan>{record['name']}</cyan>:<cyan>{record['function']}</cyan>:<cyan>{record['line']}</cyan> | "
                f"<level>{record['message']}</level>\n"
            )
        
        logger.add(
            sys.stderr,
            format=console_formatter,
            level=log_level,
            colorize=True,
            backtrace=True,
            diagnose=True
        )
    
    # File logging (human-readable)
    if enable_file:
        def file_formatter(record):
            # Build format with optional fields
            req_id = record["extra"].get("request_id", "") if "extra" in record else ""
            if req_id:
                req_id = f" | {req_id}"
            return (
                f"{record['time']:YYYY-MM-DD HH:mm:ss} | "
                f"{record['level'].name: <8}"
                f"{req_id} | "
                f"{record['name']}:{record['function']}:{record['line']} | "
                f"{record['message']}\n"
            )
        
        logger.add(
            log_path / "app.log",
            format=file_formatter,
            level=log_level,
            rotation=max_file_size,
            retention=f"{retention_days} days",
            compression="gz",
            backtrace=True,
            diagnose=True,
            enqueue=True  # Async logging for better performance
        )
    
    # JSON logging (structured)
    if enable_json:
        logger.add(
            log_path / "app.json",
            format=StructuredFormatter(),
            level=log_level,
            rotation=max_file_size,
            retention=f"{retention_days} days",
            compression="gz",
            serialize=False,  # Custom formatter handles serialization
            enqueue=True
        )
    
    # Error-only file
    logger.add(
        log_path / "errors.log",
        format=file_formatter if enable_file else "{time} | {level} | {message}",
        level="ERROR",
        rotation=max_file_size,
        retention=f"{retention_days * 4} days",  # Keep errors longer
        compression="gz",
        backtrace=True,
        diagnose=True,
        enqueue=True
    )
    
    # Performance/metrics logging
    logger.add(
        log_path / "performance.log",
        format=StructuredFormatter(),
        level="INFO",
        rotation=max_file_size,
        retention=f"{retention_days} days",
        compression="gz",
        filter=lambda record: record["extra"].get("metric") is not None,
        enqueue=True
    )
    
    # Security events logging
    logger.add(
        log_path / "security.log",
        format=StructuredFormatter(),
        level="WARNING",
        rotation=max_file_size,
        retention=f"{retention_days * 8} days",  # Keep security logs longer
        compression="gz",
        filter=lambda record: record["extra"].get("security") is not None,
        enqueue=True
    )


class LogContext:
    """Context manager for structured logging"""
    
    def __init__(self, **kwargs):
        self.context = kwargs
        self.tokens = {}
    
    def __enter__(self):
        # Set context variables
        for key, value in self.context.items():
            if key == "request_id":
                self.tokens[key] = request_id.set(value)
            elif key == "task_id":
                self.tokens[key] = task_id.set(value)
            elif key == "user_agent":
                self.tokens[key] = user_agent.set(value)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Reset context variables
        for key, token in self.tokens.items():
            if key == "request_id":
                request_id.reset(token)
            elif key == "task_id":
                task_id.reset(token)
            elif key == "user_agent":
                user_agent.reset(token)


class BrowserLogger:
    """Specialized logger for browser automation events"""
    
    def __init__(self, name: str = "browser"):
        self.logger = logger.bind(component=name)
    
    def page_loaded(self, url: str, load_time: float, **kwargs):
        """Log page load event"""
        self.logger.info(
            "Page loaded",
            extra={
                "event": "page_loaded",
                "url": url,
                "load_time_ms": load_time * 1000,
                "metric": True,
                **kwargs
            }
        )
    
    def action_executed(self, action_type: str, selector: str, success: bool, duration: float, **kwargs):
        """Log browser action execution"""
        level = "info" if success else "warning"
        self.logger.log(
            level.upper(),
            f"Action {action_type} {'succeeded' if success else 'failed'}",
            extra={
                "event": "action_executed",
                "action_type": action_type,
                "selector": selector,
                "success": success,
                "duration_ms": duration * 1000,
                "metric": True,
                **kwargs
            }
        )
    
    def stealth_detection(self, site: str, detected: bool, details: Dict[str, Any]):
        """Log stealth detection results"""
        level = "warning" if detected else "info"
        self.logger.log(
            level.upper(),
            f"Stealth test on {site}: {'DETECTED' if detected else 'PASSED'}",
            extra={
                "event": "stealth_detection",
                "site": site,
                "detected": detected,
                "details": details,
                "security": True
            }
        )
    
    def navigation(self, from_url: str, to_url: str, method: str = "navigate"):
        """Log navigation between pages"""
        self.logger.info(
            f"Navigation: {from_url} -> {to_url}",
            extra={
                "event": "navigation",
                "from_url": from_url,
                "to_url": to_url,
                "method": method
            }
        )


class LLMLogger:
    """Specialized logger for LLM interactions"""
    
    def __init__(self, name: str = "llm"):
        self.logger = logger.bind(component=name)
    
    def request_sent(self, provider: str, model: str, prompt_tokens: int, **kwargs):
        """Log LLM request"""
        self.logger.info(
            f"LLM request to {provider}",
            extra={
                "event": "llm_request",
                "provider": provider,
                "model": model,
                "prompt_tokens": prompt_tokens,
                "metric": True,
                **kwargs
            }
        )
    
    def response_received(self, provider: str, completion_tokens: int, total_tokens: int, duration: float, cost: Optional[float] = None):
        """Log LLM response"""
        self.logger.info(
            f"LLM response from {provider}",
            extra={
                "event": "llm_response",
                "provider": provider,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "duration_ms": duration * 1000,
                "cost_usd": cost,
                "metric": True
            }
        )
    
    def error(self, provider: str, error_type: str, error_message: str, **kwargs):
        """Log LLM error"""
        self.logger.error(
            f"LLM error from {provider}: {error_type}",
            extra={
                "event": "llm_error",
                "provider": provider,
                "error_type": error_type,
                "error_message": error_message,
                **kwargs
            }
        )


class SecurityLogger:
    """Specialized logger for security events"""
    
    def __init__(self, name: str = "security"):
        self.logger = logger.bind(component=name)
    
    def api_key_exposed(self, key_type: str, location: str):
        """Log potential API key exposure"""
        self.logger.critical(
            f"Potential {key_type} key exposure detected",
            extra={
                "event": "api_key_exposure",
                "key_type": key_type,
                "location": location,
                "security": True
            }
        )
    
    def suspicious_activity(self, activity_type: str, details: Dict[str, Any]):
        """Log suspicious activity"""
        self.logger.warning(
            f"Suspicious activity detected: {activity_type}",
            extra={
                "event": "suspicious_activity",
                "activity_type": activity_type,
                "details": details,
                "security": True
            }
        )
    
    def rate_limit_exceeded(self, service: str, limit: int, current: int):
        """Log rate limit exceeded"""
        self.logger.warning(
            f"Rate limit exceeded for {service}",
            extra={
                "event": "rate_limit_exceeded",
                "service": service,
                "limit": limit,
                "current": current,
                "security": True
            }
        )


# Pre-configured logger instances
browser_logger = BrowserLogger()
llm_logger = LLMLogger()
security_logger = SecurityLogger()

# Initialize logging on import
setup_logging()

# Export main logger and utilities
__all__ = [
    "logger",
    "setup_logging", 
    "LogContext",
    "BrowserLogger", 
    "LLMLogger", 
    "SecurityLogger",
    "browser_logger", 
    "llm_logger", 
    "security_logger"
]