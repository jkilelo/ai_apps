"""
Comprehensive logging configuration for UI Testing v2
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Dict, Optional

from .config import Settings


class UITestingFormatter(logging.Formatter):
    """Custom formatter with color support and structured output"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m',       # Reset
    }
    
    def __init__(self, use_color: bool = True, include_extra: bool = True):
        self.use_color = use_color
        self.include_extra = include_extra
        
        # Base format
        base_format = "%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s"
        
        if include_extra:
            base_format += " | %(filename)s:%(lineno)d"
        
        super().__init__(base_format, datefmt="%Y-%m-%d %H:%M:%S")
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with optional colors"""
        # Add context information
        if hasattr(record, 'workflow_id'):
            record.message = f"[{record.workflow_id}] {record.getMessage()}"
        else:
            record.message = record.getMessage()
        
        # Format the record
        formatted = super().format(record)
        
        # Add color if enabled and outputting to terminal
        if self.use_color and hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            formatted = f"{color}{formatted}{self.COLORS['RESET']}"
        
        return formatted


class WorkflowContextFilter(logging.Filter):
    """Filter to add workflow context to log records"""
    
    def __init__(self, workflow_id: Optional[str] = None):
        super().__init__()
        self.workflow_id = workflow_id
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add workflow context to record"""
        if self.workflow_id:
            record.workflow_id = self.workflow_id
        return True


def setup_logging(
    settings: Optional[Settings] = None,
    log_level: Optional[str] = None,
    log_dir: Optional[Path] = None,
    enable_file_logging: bool = True,
    enable_console_logging: bool = True,
) -> Dict[str, logging.Logger]:
    """
    Setup comprehensive logging for UI Testing v2
    
    Args:
        settings: Framework settings
        log_level: Override log level
        log_dir: Log directory path
        enable_file_logging: Enable file logging
        enable_console_logging: Enable console logging
        
    Returns:
        Dictionary of configured loggers
    """
    # Determine log level
    if log_level:
        level = getattr(logging, log_level.upper())
    elif settings and hasattr(settings, 'logging') and hasattr(settings.logging, 'level'):
        level = getattr(logging, settings.logging.level.upper())
    else:
        level = logging.INFO
    
    # Determine log directory
    if not log_dir:
        log_dir = Path("logs")
    log_dir = Path(log_dir)
    log_dir.mkdir(exist_ok=True)
    
    # Clear existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configure loggers
    loggers = {}
    
    # Main framework logger
    framework_logger = logging.getLogger("ui_testing_v2")
    framework_logger.setLevel(level)
    loggers["framework"] = framework_logger
    
    # Component loggers
    component_names = [
        "element_extraction",
        "test_generation", 
        "code_generation",
        "code_execution",
        "ai_service",
        "storage",
        "cache",
        "events",
    ]
    
    for component in component_names:
        logger_name = f"ui_testing_v2.{component}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        loggers[component] = logger
    
    # Console handler
    if enable_console_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = UITestingFormatter(use_color=True, include_extra=False)
        console_handler.setFormatter(console_formatter)
        
        # Add to all loggers
        for logger in loggers.values():
            logger.addHandler(console_handler)
    
    # File handlers
    if enable_file_logging:
        # Main log file
        main_file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "ui_testing_v2.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        main_file_handler.setLevel(level)
        main_file_formatter = UITestingFormatter(use_color=False, include_extra=True)
        main_file_handler.setFormatter(main_file_formatter)
        
        # Add to framework logger
        framework_logger.addHandler(main_file_handler)
        
        # Component-specific log files
        for component, logger in loggers.items():
            if component != "framework":
                component_handler = logging.handlers.RotatingFileHandler(
                    log_dir / f"{component}.log",
                    maxBytes=5 * 1024 * 1024,  # 5MB
                    backupCount=3,
                    encoding="utf-8",
                )
                component_handler.setLevel(level)
                component_handler.setFormatter(main_file_formatter)
                logger.addHandler(component_handler)
        
        # Error log file (errors and above only)
        error_file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "errors.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding="utf-8",
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(main_file_formatter)
        
        # Add error handler to all loggers
        for logger in loggers.values():
            logger.addHandler(error_file_handler)
    
    # Prevent propagation to avoid duplicate logs
    for logger in loggers.values():
        logger.propagate = False
    
    # Configure third-party loggers
    logging.getLogger("playwright").setLevel(logging.WARNING)
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # Log setup completion
    framework_logger.info(f"Logging configured - Level: {logging.getLevelName(level)}")
    framework_logger.info(f"Log directory: {log_dir.absolute()}")
    
    return loggers


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(f"ui_testing_v2.{name}")


def add_workflow_context(logger: logging.Logger, workflow_id: str) -> logging.Logger:
    """Add workflow context to a logger"""
    # Create a new logger with workflow context
    workflow_logger = logging.LoggerAdapter(logger, {"workflow_id": workflow_id})
    return workflow_logger


class PerformanceLogger:
    """Logger for performance metrics"""
    
    def __init__(self, name: str = "performance"):
        self.logger = get_logger(name)
    
    def log_timing(
        self,
        operation: str,
        duration: float,
        context: Optional[Dict] = None,
    ) -> None:
        """Log timing information"""
        message = f"Operation '{operation}' completed in {duration:.3f}s"
        if context:
            message += f" | Context: {context}"
        self.logger.info(message)
    
    def log_memory_usage(
        self,
        operation: str,
        memory_mb: float,
        context: Optional[Dict] = None,
    ) -> None:
        """Log memory usage information"""
        message = f"Operation '{operation}' used {memory_mb:.1f}MB"
        if context:
            message += f" | Context: {context}"
        self.logger.info(message)


class SecurityLogger:
    """Logger for security events"""
    
    def __init__(self, name: str = "security"):
        self.logger = get_logger(name)
    
    def log_url_access(self, url: str, result: str) -> None:
        """Log URL access attempts"""
        self.logger.info(f"URL access: {url} | Result: {result}")
    
    def log_file_access(self, filepath: str, operation: str, result: str) -> None:
        """Log file access attempts"""
        self.logger.info(f"File {operation}: {filepath} | Result: {result}")
    
    def log_security_event(self, event: str, details: Dict) -> None:
        """Log security events"""
        self.logger.warning(f"Security event: {event} | Details: {details}")


# Initialize default loggers on import
_default_loggers = setup_logging()

# Export commonly used loggers
framework_logger = _default_loggers["framework"]
element_logger = _default_loggers["element_extraction"]
test_logger = _default_loggers["test_generation"]
code_logger = _default_loggers["code_generation"]
execution_logger = _default_loggers["code_execution"]
