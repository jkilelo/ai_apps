"""Core functionality and configuration."""

from simple_apps_v2.core.config import Settings
from simple_apps_v2.core.logging import setup_logging

__all__ = [
    "Settings",
    "setup_logging",
]