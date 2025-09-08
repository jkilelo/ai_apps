"""
Browser integration module.

This module provides the Playwright browser integration and context
management for AI agents.
"""

from .browser_context import BrowserContext, PageInfo, ElementInfo

__all__ = [
    "BrowserContext",
    "PageInfo", 
    "ElementInfo",
]