"""
Unified Browser - AI-Agent-First Web Automation

A modern Python library for intelligent web automation powered by pydantic-ai,
combining Playwright browser control with AI agents for natural language
web interaction.

Example Usage:
    # Simple task execution
    from unified_browser import quick_task
    result = await quick_task("Go to Amazon and find laptops under $500")
    
    # Persistent browser session
    from unified_browser import AIBrowser
    async with AIBrowser() as browser:
        await browser.run("Navigate to Google")
        products = await browser.run("Search for 'AI automation tools' and get top 5 results")
        
    # Specialized agent workflows
    browser = AIBrowser()
    async with browser:
        # Use specialized agents
        nav_result = await browser.navigate("Go to ecommerce site")
        interaction_result = await browser.interact("Add product to cart")
        data = await browser.extract("Get cart total and items")
"""

from __future__ import annotations

# Version info
__version__ = "1.0.0-alpha"
__author__ = "Unified Browser Team"
__license__ = "MIT"

# Core AI Browser Interface
from .ai_browser import (
    AIBrowser,
    quick_task,
    create_browser,
)

# Configuration system
from .config import (
    ConfigProfile,
    ConfigFactory,
    UnifiedConfig,
    BrowserConfig,
    StealthConfig, 
    NavigationConfig,
    ExtractionConfig,
    SecurityConfig,
    PerformanceConfig,
    AIConfig,
)

# Core types and utilities
from .core import (
    # Enums
    BrowserEngine,
    BrowserState,
    StealthLevel,
    ContentType,
    ExtractionMethod,
    NavigationStrategy,
    LLMProvider,
    
    # Data structures
    NavigationResult,
    ExtractionResult,
    ElementData,
    BoundingBox,
    Point,
    
    # Exceptions
    UnifiedBrowserError,
    NavigationError,
    ExtractionError,
    AIError,
    
    # Constants
    DEFAULT_TIMEOUT,
)

# Agent system (for advanced users)
from .agents.base_agent import (
    AgentFactory,
    NavigationAgent,
    InteractionAgent,
    ExtractionAgent,
    AnalysisAgent,
)

# Browser context (for advanced users)
from .browser.browser_context import BrowserContext

__all__ = [
    # Version info
    "__version__",
    "__author__", 
    "__license__",
    
    # Main AI Browser Interface
    "AIBrowser",
    "quick_task", 
    "create_browser",
    
    # Configuration
    "ConfigProfile",
    "ConfigFactory",
    "UnifiedConfig",
    "BrowserConfig",
    "StealthConfig",
    "NavigationConfig", 
    "ExtractionConfig",
    "SecurityConfig",
    "PerformanceConfig",
    "AIConfig",
    
    # Core Types
    "BrowserEngine",
    "BrowserState",
    "StealthLevel",
    "ContentType",
    "ExtractionMethod", 
    "NavigationStrategy",
    "LLMProvider",
    "NavigationResult",
    "ExtractionResult", 
    "ElementData",
    "BoundingBox",
    "Point",
    
    # Exceptions
    "UnifiedBrowserError",
    "NavigationError", 
    "ExtractionError",
    "AIError",
    
    # Constants
    "DEFAULT_TIMEOUT",
    
    # Advanced interfaces  
    "AgentFactory",
    "NavigationAgent",
    "InteractionAgent",
    "ExtractionAgent", 
    "AnalysisAgent",
    "BrowserContext",
]

# Package metadata
__package_name__ = "unified-browser"
__description__ = "AI-Agent-First Web Automation with pydantic-ai and Playwright"
__keywords__ = [
    "web automation",
    "ai agents", 
    "pydantic-ai",
    "playwright",
    "browser automation",
    "web scraping",
    "natural language",
    "intelligent automation"
]

# Convenience aliases for common patterns
WebBrowser = AIBrowser  # Alternative name
Browser = AIBrowser     # Short name

# Quick configuration presets
def debug_browser() -> AIBrowser:
    """Create browser instance optimized for debugging."""
    return create_browser(
        profile=ConfigProfile.DEVELOPMENT,
        headless=False,
        debug=True
    )

def stealth_browser() -> AIBrowser:
    """Create browser instance optimized for stealth."""
    return create_browser(
        profile=ConfigProfile.STEALTH,
        headless=True
    )

def production_browser() -> AIBrowser:
    """Create browser instance optimized for production."""
    return create_browser(
        profile=ConfigProfile.PRODUCTION,
        headless=True
    )

# Add convenience functions to __all__
__all__.extend([
    "WebBrowser",
    "Browser", 
    "debug_browser",
    "stealth_browser",
    "production_browser",
])

# Package information for introspection
def get_package_info() -> dict:
    """Get package information."""
    return {
        "name": __package_name__,
        "version": __version__,
        "description": __description__,
        "author": __author__,
        "license": __license__,
        "keywords": __keywords__,
    }

# Runtime availability checks
def check_dependencies() -> dict:
    """Check availability of optional dependencies."""
    dependencies = {}
    
    # Check Playwright
    try:
        import playwright
        dependencies['playwright'] = True
    except ImportError:
        dependencies['playwright'] = False
    
    # Check pydantic-ai  
    try:
        import pydantic_ai
        dependencies['pydantic_ai'] = True
    except ImportError:
        dependencies['pydantic_ai'] = False
    
    # Check AI providers
    providers = {}
    for provider in ['openai', 'anthropic', 'google-generativeai']:
        try:
            __import__(provider.replace('-', '_'))
            providers[provider] = True
        except ImportError:
            providers[provider] = False
    
    dependencies['ai_providers'] = providers
    return dependencies

# Add to __all__
__all__.extend([
    "get_package_info",
    "check_dependencies",
])

# Initialize logging configuration
import logging

# Set up package logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Only add handler if none exists
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Package welcome message for interactive use
def _show_welcome():
    """Show welcome message in interactive environments."""
    try:
        # Only show in IPython/Jupyter
        if hasattr(__builtins__, '__IPYTHON__'):
            print(f"🤖 Unified Browser v{__version__} - AI-Agent-First Web Automation")
            print("📚 Quick start: await quick_task('Go to Google and search for Python')")
            print("🔗 Docs: https://github.com/unified-browser/unified-browser")
    except Exception:
        pass

# Show welcome in interactive environments
_show_welcome()