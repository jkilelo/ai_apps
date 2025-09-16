"""
NEXUS Browser Logging Configuration
====================================
Centralized logging configuration for the entire NEXUS Browser system.
Supports structured logging, multiple handlers, and environment-specific settings.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from pythonjsonlogger import jsonlogger
from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install as install_rich_traceback

# Install rich traceback for better error visualization
install_rich_traceback(show_locals=True)

# Create logs directory if it doesn't exist
LOGS_DIR = Path("./logs")
LOGS_DIR.mkdir(exist_ok=True)


class NexusLoggerConfig:
    """Centralized logging configuration for NEXUS Browser."""

    def __init__(
        self,
        level: str = "INFO",
        format_type: str = "structured",
        output: str = "both",
        log_file: Optional[str] = None,
    ):
        """
        Initialize logging configuration.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format_type: Format type (json, plain, structured)
            output: Output destination (console, file, both)
            log_file: Path to log file
        """
        self.level = getattr(logging, level.upper(), logging.INFO)
        self.format_type = format_type
        self.output = output
        self.log_file = log_file or str(LOGS_DIR / "nexus.log")
        self.console = Console()

    def setup_standard_logging(self) -> None:
        """Set up standard Python logging."""
        root_logger = logging.getLogger()
        root_logger.setLevel(self.level)

        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Console handler
        if self.output in ("console", "both"):
            if self.format_type == "plain":
                console_handler = logging.StreamHandler(sys.stdout)
                console_formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
                console_handler.setFormatter(console_formatter)
            elif self.format_type == "json":
                console_handler = logging.StreamHandler(sys.stdout)
                console_formatter = jsonlogger.JsonFormatter(
                    "%(timestamp)s %(level)s %(name)s %(message)s",
                    rename_fields={
                        "timestamp": "@timestamp",
                        "level": "log.level",
                        "name": "log.logger",
                    },
                )
                console_handler.setFormatter(console_formatter)
            else:  # structured with rich
                console_handler = RichHandler(
                    console=self.console,
                    show_time=True,
                    show_path=True,
                    enable_link_path=True,
                    markup=True,
                    rich_tracebacks=True,
                    tracebacks_show_locals=True,
                )
                console_handler.setFormatter(logging.Formatter("%(message)s"))

            root_logger.addHandler(console_handler)

        # File handler
        if self.output in ("file", "both"):
            # Rotating file handler (10MB max, keep 5 backups)
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding="utf-8",
            )

            if self.format_type == "json":
                file_formatter = jsonlogger.JsonFormatter(
                    "%(timestamp)s %(level)s %(name)s %(message)s %(pathname)s %(lineno)d",
                    rename_fields={
                        "timestamp": "@timestamp",
                        "level": "log.level",
                        "name": "log.logger",
                        "pathname": "log.file.path",
                        "lineno": "log.file.line",
                    },
                )
            else:
                file_formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )

            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)

    def setup_structlog(self) -> None:
        """Set up structlog for structured logging."""
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
        ]

        if self.format_type == "json":
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.append(structlog.dev.ConsoleRenderer())

        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

    def get_logger(self, name: str) -> Any:
        """
        Get a logger instance.

        Args:
            name: Logger name (usually __name__)

        Returns:
            Logger instance
        """
        if self.format_type == "structured":
            return structlog.get_logger(name)
        else:
            return logging.getLogger(name)


class NexusLogger:
    """
    Wrapper class for NEXUS-specific logging functionality.
    """

    def __init__(self, name: str, config: Optional[NexusLoggerConfig] = None):
        """
        Initialize NEXUS logger.

        Args:
            name: Logger name
            config: Logger configuration
        """
        self.config = config or NexusLoggerConfig()
        self.logger = self.config.get_logger(name)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message."""
        self.logger.critical(message, **kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        """Log exception with traceback."""
        self.logger.exception(message, **kwargs)

    def log_quantum_event(self, event: str, **kwargs: Any) -> None:
        """Log quantum-specific events."""
        self.logger.info(f"[QUANTUM] {event}", component="quantum", **kwargs)

    def log_consciousness_event(self, event: str, **kwargs: Any) -> None:
        """Log consciousness-specific events."""
        self.logger.info(f"[CONSCIOUSNESS] {event}", component="consciousness", **kwargs)

    def log_evolution_event(self, event: str, **kwargs: Any) -> None:
        """Log evolution-specific events."""
        self.logger.info(f"[EVOLUTION] {event}", component="evolution", **kwargs)

    def log_holographic_event(self, event: str, **kwargs: Any) -> None:
        """Log holographic storage events."""
        self.logger.info(f"[HOLOGRAPHIC] {event}", component="holographic", **kwargs)

    def log_mcp_neural_event(self, event: str, **kwargs: Any) -> None:
        """Log MCP Neural events."""
        self.logger.info(f"[MCP_NEURAL] {event}", component="mcp_neural", **kwargs)

    def log_performance(self, operation: str, duration: float, **kwargs: Any) -> None:
        """Log performance metrics."""
        self.logger.info(
            f"[PERFORMANCE] {operation}",
            operation=operation,
            duration_ms=duration * 1000,
            component="performance",
            **kwargs,
        )

    def log_security_event(self, event: str, severity: str = "info", **kwargs: Any) -> None:
        """Log security-related events."""
        log_method = getattr(self.logger, severity, self.logger.info)
        log_method(f"[SECURITY] {event}", component="security", severity=severity, **kwargs)


# Global configuration instance
_global_config: Optional[NexusLoggerConfig] = None


def initialize_logging(
    level: str = "INFO",
    format_type: str = "structured",
    output: str = "both",
    log_file: Optional[str] = None,
) -> NexusLoggerConfig:
    """
    Initialize global logging configuration.

    Args:
        level: Log level
        format_type: Format type
        output: Output destination
        log_file: Log file path

    Returns:
        Logger configuration instance
    """
    global _global_config
    _global_config = NexusLoggerConfig(level, format_type, output, log_file)
    _global_config.setup_standard_logging()
    _global_config.setup_structlog()
    return _global_config


def get_logger(name: str) -> NexusLogger:
    """
    Get a NEXUS logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        NexusLogger instance
    """
    global _global_config
    if _global_config is None:
        initialize_logging()
    return NexusLogger(name, _global_config)


# Example usage and testing
if __name__ == "__main__":
    # Initialize logging
    initialize_logging(level="DEBUG", format_type="structured", output="both")

    # Get logger
    logger = get_logger(__name__)

    # Test different log levels
    logger.debug("Debug message", extra_data={"key": "value"})
    logger.info("Info message", user_id=123, action="login")
    logger.warning("Warning message", threshold=0.8, current=0.9)
    logger.error("Error message", error_code="E001", details="Something went wrong")

    # Test component-specific logging
    logger.log_quantum_event("Quantum entanglement achieved", qubits=10, fidelity=0.98)
    logger.log_consciousness_event("Consciousness threshold reached", level=0.85)
    logger.log_evolution_event("Generation evolved", generation=5, fitness=0.92)
    logger.log_holographic_event("Memory stored", size_mb=2.5, compression=0.1)
    logger.log_mcp_neural_event("Neural network trained", epochs=100, accuracy=0.95)

    # Test performance logging
    logger.log_performance("database_query", 0.125, query="SELECT * FROM users")

    # Test security logging
    logger.log_security_event("Unauthorized access attempt", severity="warning", ip="192.168.1.1")

    # Test exception logging
    try:
        raise ValueError("Test exception")
    except Exception:
        logger.exception("An error occurred during testing")

    print("\n✅ Logging configuration test completed successfully!")
    print(f"📁 Log file created at: {LOGS_DIR / 'nexus.log'}")