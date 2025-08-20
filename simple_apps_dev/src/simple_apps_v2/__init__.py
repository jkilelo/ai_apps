"""
Simple Apps v2 - Modern Web Automation Testing Application

A clean, modular web automation testing application with consolidated dependencies
and modern Python architecture.
"""

__version__ = "1.0.0"
__author__ = "AI Apps Team"
__email__ = "team@ai-apps.com"

from simple_apps_v2.core.config import Settings
from simple_apps_v2.core.logging import setup_logging

# Package exports
__all__ = [
    "Settings",
    "setup_logging",
    "__version__",
    "__author__",
    "__email__",
]