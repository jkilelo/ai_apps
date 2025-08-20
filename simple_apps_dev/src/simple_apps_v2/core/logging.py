"""
Centralized logging configuration.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

from simple_apps_v2.core.config import get_settings


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
    rich_console: bool = True
) -> logging.Logger:
    """
    Set up application logging with rich formatting.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        rich_console: Whether to use rich console formatting
        
    Returns:
        Configured logger instance
    """
    settings = get_settings()
    
    # Determine log level
    log_level = level or settings.log_level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Clear existing handlers
    logging.getLogger().handlers = []
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Create console handler with rich formatting
    if rich_console:
        console = Console(file=sys.stdout, width=120)
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=True,
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
        )
        console_handler.setLevel(numeric_level)
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        formatter = logging.Formatter(settings.log_format)
        console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # File gets all messages
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Set specific logger levels
    _configure_third_party_loggers()
    
    # Log startup message
    app_logger = logging.getLogger("simple_apps_v2")
    app_logger.info(f"Logging initialized - Level: {log_level}")
    
    return logger


def _configure_third_party_loggers() -> None:
    """Configure third-party library loggers to reduce noise."""
    # Playwright can be quite verbose
    logging.getLogger("playwright").setLevel(logging.WARNING)
    
    # FastAPI/Uvicorn loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    
    # HTTP libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    
    # OpenAI client can be verbose
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx._client").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)