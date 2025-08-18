"""
Browser Integration Adapter
============================
This module provides integration between auto-generated test code and the existing
UltimateStealthBrowser infrastructure, ensuring tests use the existing browser
instead of creating their own instances.

Key Features:
- Adapts generated tests to use existing browser infrastructure
- Provides singleton browser management for resource efficiency
- Maintains stealth capabilities across all tests
- Works generically with any website
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Union, Callable
from contextlib import asynccontextmanager
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import the existing browser infrastructure
from base import (
    UltimateStealthBrowser,
    StealthConfig,
    StealthLevel,
    ExtractionResult,
    ElementData
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BrowserIntegrationAdapter:
    """
    Adapter that bridges generated test code with the existing browser infrastructure.
    This ensures all tests use the same browser instance with stealth capabilities.
    """
    
    _instance: Optional['BrowserIntegrationAdapter'] = None
    _browser: Optional[UltimateStealthBrowser] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton pattern to ensure only one browser instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the adapter (only runs once due to singleton)."""
        if not self._initialized:
            # Create StealthConfig with proper attributes
            self.config = StealthConfig()
            self.config.level = StealthLevel.MAXIMUM
            self.config.headless = False  # Can be configured
            self.config.block_resources = False  # Allow all resources for testing
            self.config.enable_human_simulation = True
            self.config.enable_human_delays = True
            self._initialized = True
            logger.info("Browser Integration Adapter initialized")
    
    async def get_browser(self) -> UltimateStealthBrowser:
        """
        Get or create the singleton browser instance.
        
        Returns:
            The shared UltimateStealthBrowser instance
        """
        if self._browser is None:
            logger.info("Creating new UltimateStealthBrowser instance")
            self._browser = UltimateStealthBrowser(self.config)
            await self._browser.initialize()
        return self._browser
    
    async def get_page(self):
        """
        Get the page object from the browser.
        
        Returns:
            The Playwright Page object with stealth capabilities
        """
        browser = await self.get_browser()
        if browser.page is None:
            # Create a new page if needed
            browser.page = await browser.context.new_page()
            await browser._setup_stealth_scripts(browser.page)
        return browser.page
    
    async def navigate_to(self, url: str, wait_for: str = "domcontentloaded") -> bool:
        """
        Navigate to a URL using the existing browser.
        
        Args:
            url: The URL to navigate to
            wait_for: Wait condition for navigation
            
        Returns:
            True if navigation successful
        """
        browser = await self.get_browser()
        return await browser.navigate(url, wait_for)
    
    async def extract_elements(self, url: Optional[str] = None) -> ExtractionResult:
        """
        Extract elements from the current page or navigate to URL first.
        
        Args:
            url: Optional URL to navigate to before extraction
            
        Returns:
            ExtractionResult with all found elements
        """
        browser = await self.get_browser()
        return await browser.extract_elements(url)
    
    @asynccontextmanager
    async def test_context(self, url: str):
        """
        Context manager for test execution with automatic setup and cleanup.
        
        Args:
            url: The URL to test
            
        Yields:
            Tuple of (browser, page) for test use
        """
        browser = await self.get_browser()
        page = await self.get_page()
        
        try:
            # Navigate to the test URL
            await self.navigate_to(url)
            yield browser, page
        except Exception as e:
            logger.error(f"Error in test context: {e}")
            # Take screenshot for debugging
            if page:
                await page.screenshot(path=f"error_{int(asyncio.get_event_loop().time())}.png")
            raise
        finally:
            # Optional: Clear cookies/storage between tests
            if browser.context:
                await browser.context.clear_cookies()
    
    async def cleanup(self):
        """Clean up browser resources."""
        if self._browser:
            await self._browser.cleanup()
            self._browser = None
            logger.info("Browser resources cleaned up")
    
    @classmethod
    def reset(cls):
        """Reset the singleton instance (useful for testing)."""
        if cls._instance and cls._instance._browser:
            asyncio.create_task(cls._instance.cleanup())
        cls._instance = None
        cls._initialized = False


class PlaywrightCompatibilityLayer:
    """
    Compatibility layer that makes the UltimateStealthBrowser compatible
    with standard Playwright API expected by generated tests.
    """
    
    def __init__(self, adapter: BrowserIntegrationAdapter):
        self.adapter = adapter
        self._page = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.adapter.get_browser()
        self._page = await self.adapter.get_page()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Cleanup handled by adapter
        pass
    
    @property
    async def page(self):
        """Get the page object."""
        if self._page is None:
            self._page = await self.adapter.get_page()
        return self._page
    
    async def goto(self, url: str, **kwargs):
        """Navigate to URL (Playwright-compatible method)."""
        return await self.adapter.navigate_to(url)
    
    async def locator(self, selector: str):
        """Get locator (Playwright-compatible method)."""
        page = await self.page
        return page.locator(selector)
    
    async def fill(self, selector: str, value: str):
        """Fill input field (Playwright-compatible method)."""
        page = await self.page
        await page.fill(selector, value)
    
    async def click(self, selector: str):
        """Click element (Playwright-compatible method)."""
        page = await self.page
        await page.click(selector)
    
    async def wait_for_selector(self, selector: str, **kwargs):
        """Wait for selector (Playwright-compatible method)."""
        page = await self.page
        return await page.wait_for_selector(selector, **kwargs)
    
    async def screenshot(self, **kwargs):
        """Take screenshot (Playwright-compatible method)."""
        page = await self.page
        return await page.screenshot(**kwargs)


def generate_browser_context_for_llm(target_url: str) -> str:
    """
    Generate context information for LLM to understand how to use the existing browser.
    
    Args:
        target_url: The target website URL for testing
        
    Returns:
        Context string to include in LLM prompts
    """
    context = f"""
IMPORTANT: Use the existing UltimateStealthBrowser infrastructure instead of creating new browser instances.

The test framework provides a pre-configured browser with advanced stealth capabilities at:
`C:\\Users\\kleiy\\OneDrive\\Desktop\\python-ai-apps\\ai_apps\\browser`

To use the existing browser in your tests, follow this pattern:

```python
from browser.browser_integration_adapter import BrowserIntegrationAdapter, PlaywrightCompatibilityLayer
import asyncio

async def test_example():
    # Get the shared browser adapter
    adapter = BrowserIntegrationAdapter()
    
    # Use the browser with stealth capabilities
    async with adapter.test_context("{target_url}") as (browser, page):
        # The page is already navigated to {target_url}
        # Use standard Playwright API
        await page.fill("#input-selector", "test value")
        await page.click("#submit-button")
        
        # Or use the browser's extraction capabilities
        elements = await browser.extract_elements()
        
        # Assertions and test logic here
        assert page.url == "{target_url}"

# For synchronous tests (pytest)
def test_sync_example():
    asyncio.run(test_example())
```

Alternative pattern using compatibility layer:

```python
async def test_with_compatibility():
    adapter = BrowserIntegrationAdapter()
    compat = PlaywrightCompatibilityLayer(adapter)
    
    async with compat as browser_compat:
        page = await browser_compat.page
        await browser_compat.goto("{target_url}")
        await browser_compat.fill("#email", "test@example.com")
        await browser_compat.click("#submit")
```

Key benefits of using the existing browser:
1. **Stealth Mode**: Advanced anti-detection capabilities built-in
2. **Resource Efficiency**: Reuses browser instance across tests
3. **Human Simulation**: Automatic human-like behavior patterns
4. **Element Extraction**: AI-powered element detection and extraction
5. **Performance Monitoring**: Built-in metrics and monitoring
6. **Error Recovery**: Automatic context stability and recovery

DO NOT create new browser instances with:
- `playwright.chromium.launch()` 
- `Browser()`
- `sync_playwright()`

ALWAYS use:
- `BrowserIntegrationAdapter()`
- `adapter.get_browser()`
- `adapter.test_context(url)`

The browser automatically handles:
- Stealth scripts injection
- Canvas/WebGL fingerprinting protection
- WebRTC leak prevention
- Timezone spoofing
- Human-like mouse movements
- Random delays and interactions
"""
    return context


def modify_llm_prompt_for_browser_integration(
    original_prompt: str,
    target_url: str
) -> str:
    """
    Modify LLM prompts to include browser integration context.
    
    Args:
        original_prompt: The original prompt for test generation
        target_url: The target website URL
        
    Returns:
        Modified prompt with browser integration context
    """
    browser_context = generate_browser_context_for_llm(target_url)
    
    modified_prompt = f"""
{browser_context}

ORIGINAL REQUEST:
{original_prompt}

IMPORTANT MODIFICATIONS:
1. Use the BrowserIntegrationAdapter instead of creating new browsers
2. Import from 'browser.browser_integration_adapter' for browser access
3. Use async/await patterns with the adapter.test_context() method
4. Leverage browser.extract_elements() for intelligent element detection
5. The browser has stealth mode enabled - no need for additional anti-detection

Generate test code that integrates with the existing browser infrastructure.
"""
    
    return modified_prompt


class TestGenerationContext:
    """
    Context provider for test generation that ensures proper browser usage.
    """
    
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.adapter = BrowserIntegrationAdapter()
    
    def get_imports(self) -> str:
        """Get the required imports for generated tests."""
        return """
import asyncio
from pathlib import Path
import sys

# Add browser directory to path
sys.path.insert(0, r'C:\\Users\\kleiy\\OneDrive\\Desktop\\python-ai-apps\\ai_apps')

from browser.browser_integration_adapter import (
    BrowserIntegrationAdapter,
    PlaywrightCompatibilityLayer
)
from browser.base import ExtractionResult, ElementData
"""
    
    def get_test_template(self) -> str:
        """Get a test template that uses the existing browser."""
        return f"""
async def test_{{test_name}}():
    '''Test for {self.target_url}'''
    adapter = BrowserIntegrationAdapter()
    
    async with adapter.test_context("{self.target_url}") as (browser, page):
        # Test implementation here
        {{test_body}}
        
def test_{{test_name}}_sync():
    '''Synchronous wrapper for pytest'''
    asyncio.run(test_{{test_name}}())
"""
    
    def get_page_object_template(self) -> str:
        """Get a page object template that uses the existing browser."""
        return f"""
class {{PageName}}:
    '''Page object for {self.target_url}'''
    
    def __init__(self):
        self.adapter = BrowserIntegrationAdapter()
        self.url = "{self.target_url}"
    
    async def navigate(self):
        '''Navigate to the page'''
        return await self.adapter.navigate_to(self.url)
    
    async def get_page(self):
        '''Get the page object'''
        return await self.adapter.get_page()
    
    async def extract_all_elements(self):
        '''Extract all elements using AI-powered detection'''
        return await self.adapter.extract_elements(self.url)
"""


# Example usage function
async def demonstrate_integration():
    """Demonstrate how the integration works."""
    
    # Create adapter
    adapter = BrowserIntegrationAdapter()
    
    # Example 1: Basic navigation and extraction
    async with adapter.test_context("https://example.com") as (browser, page):
        print(f"Navigated to: {page.url}")
        
        # Extract elements using the browser's AI capabilities
        results = await browser.extract_elements()
        print(f"Found {len(results.elements)} elements")
        
        # Use standard Playwright API
        title = await page.title()
        print(f"Page title: {title}")
    
    # Example 2: Using compatibility layer
    compat = PlaywrightCompatibilityLayer(adapter)
    async with compat as browser:
        await browser.goto("https://example.com")
        page = await browser.page
        
        # Standard Playwright operations
        await browser.screenshot(path="example.png")
        
    # Cleanup
    await adapter.cleanup()


if __name__ == "__main__":
    # Run demonstration
    asyncio.run(demonstrate_integration())