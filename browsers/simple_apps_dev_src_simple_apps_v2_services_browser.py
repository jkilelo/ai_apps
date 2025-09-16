"""
Modern browser service with type safety and async support.
"""

import asyncio
import json
import sys
import time
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from playwright.async_api import Browser, BrowserContext, Page, async_playwright
from playwright.async_api import Error as PlaywrightError

from simple_apps_v2.core.config import get_settings
from simple_apps_v2.core.logging import get_logger
from simple_apps_v2.core.models import BrowserConfig

# Import platform utils for Chrome detection
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))
try:
    from utils.platform_utils import get_chrome_executable_path, setup_event_loop
except ImportError:
    # Fallback if platform_utils is not available
    def get_chrome_executable_path():
        return None
    def setup_event_loop():
        pass

logger = get_logger(__name__)


class BrowserService:
    """Modern browser automation service with stealth capabilities."""
    
    def __init__(self, config: Optional[BrowserConfig] = None):
        """Initialize browser service with configuration."""
        self.settings = get_settings()
        self.config = config or BrowserConfig()
        
        # Browser state
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._pages: Dict[str, Page] = {}
        self._is_running = False
        
        # Setup event loop for Windows compatibility
        setup_event_loop()
        
        logger.info("BrowserService initialized")
    
    async def start(self) -> None:
        """Start the browser service."""
        if self._is_running:
            logger.warning("Browser service is already running")
            return
        
        try:
            logger.info("Starting browser service...")
            
            # Start Playwright
            self._playwright = await async_playwright().start()
            
            # Get Chrome executable path if available
            chrome_path = get_chrome_executable_path()
            
            # Launch browser with configuration
            launch_options = {
                "headless": self.config.headless,
                "timeout": self.config.timeout,
            }
            
            # Use system Chrome if available
            if chrome_path:
                launch_options["executable_path"] = chrome_path
                logger.info(f"Using system Chrome: {chrome_path}")
            
            # Add stealth options
            if not self.config.headless:
                launch_options["args"] = [
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                ]
            
            self._browser = await self._playwright.chromium.launch(**launch_options)
            
            # Create browser context with stealth settings
            context_options = {
                "viewport": {
                    "width": self.config.viewport.width,
                    "height": self.config.viewport.height,
                },
                "user_agent": self.config.user_agent or self._get_realistic_user_agent(),
                "ignore_https_errors": True,
                "java_script_enabled": True,
            }
            
            # Add extra HTTP headers for stealth
            if self.config.extra_headers:
                context_options["extra_http_headers"] = self.config.extra_headers
            
            self._context = await self._browser.new_context(**context_options)
            
            # Add stealth scripts
            await self._setup_stealth()
            
            self._is_running = True
            logger.info("Browser service started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start browser service: {e}")
            await self.stop()
            raise
    
    async def stop(self) -> None:
        """Stop the browser service."""
        logger.info("Stopping browser service...")
        
        # Close all pages
        for page_id, page in self._pages.items():
            try:
                await page.close()
            except Exception as e:
                logger.error(f"Error closing page {page_id}: {e}")
        
        self._pages.clear()
        
        # Close context
        if self._context:
            try:
                await self._context.close()
            except Exception as e:
                logger.error(f"Error closing context: {e}")
            self._context = None
        
        # Close browser
        if self._browser:
            try:
                await self._browser.close()
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
            self._browser = None
        
        # Stop Playwright
        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception as e:
                logger.error(f"Error stopping Playwright: {e}")
            self._playwright = None
        
        self._is_running = False
        logger.info("Browser service stopped")
    
    async def new_page(self, url: Optional[str] = None) -> Page:
        """Create a new page and optionally navigate to URL."""
        if not self._is_running:
            await self.start()
        
        page = await self._context.new_page()
        page_id = str(id(page))
        self._pages[page_id] = page
        
        # Apply stealth to new page
        await self._apply_stealth_to_page(page)
        
        if url:
            await self.navigate(page, url)
        
        logger.debug(f"Created new page {page_id}")
        return page
    
    async def navigate(
        self, 
        page: Page, 
        url: str, 
        wait_until: str = "networkidle"
    ) -> None:
        """Navigate to URL with error handling."""
        try:
            logger.info(f"Navigating to {url}")
            await page.goto(url, wait_until=wait_until, timeout=self.config.timeout)
            
            # Wait for page to be interactive
            await page.wait_for_load_state("domcontentloaded")
            
        except PlaywrightError as e:
            logger.error(f"Navigation failed: {e}")
            raise
    
    @asynccontextmanager
    async def managed_page(self, url: Optional[str] = None):
        """Context manager for page lifecycle."""
        page = None
        try:
            page = await self.new_page(url)
            yield page
        finally:
            if page:
                page_id = str(id(page))
                try:
                    await page.close()
                    del self._pages[page_id]
                except Exception as e:
                    logger.error(f"Error closing managed page: {e}")
    
    async def take_screenshot(
        self, 
        page: Page, 
        filename: Optional[str] = None,
        full_page: bool = True
    ) -> Path:
        """Take a screenshot of the page."""
        if not filename:
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
        
        screenshot_path = self.settings.screenshot_dir / filename
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        
        await page.screenshot(path=str(screenshot_path), full_page=full_page)
        logger.info(f"Screenshot saved to {screenshot_path}")
        
        return screenshot_path
    
    async def execute_script(self, page: Page, script: str) -> Any:
        """Execute JavaScript in the page context."""
        try:
            result = await page.evaluate(script)
            return result
        except PlaywrightError as e:
            logger.error(f"Script execution failed: {e}")
            raise
    
    async def wait_for_element(
        self, 
        page: Page, 
        selector: str, 
        timeout: Optional[int] = None
    ) -> None:
        """Wait for element to appear."""
        timeout = timeout or self.config.timeout
        await page.wait_for_selector(selector, timeout=timeout)
    
    async def _setup_stealth(self) -> None:
        """Setup stealth mode for the browser context."""
        if not self._context:
            return
        
        # Add stealth initialization script
        await self._context.add_init_script("""
            // Override navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override navigator.plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override navigator.languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Override navigator.permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Override chrome runtime
            window.chrome = {
                runtime: {}
            };
            
            // Override console.debug to prevent detection
            const originalConsoleDebug = console.debug;
            console.debug = function() {
                if (arguments[0] && arguments[0].includes && arguments[0].includes('webdriver')) {
                    return;
                }
                return originalConsoleDebug.apply(console, arguments);
            };
        """)
    
    async def _apply_stealth_to_page(self, page: Page) -> None:
        """Apply stealth scripts to a specific page."""
        try:
            await page.add_init_script("""
                // Page-specific stealth overrides
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
        except Exception as e:
            logger.warning(f"Could not apply stealth to page: {e}")
    
    def _get_realistic_user_agent(self) -> str:
        """Get a realistic user agent string."""
        return (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()
    
    def __del__(self):
        """Cleanup on deletion."""
        if self._is_running:
            try:
                asyncio.create_task(self.stop())
            except Exception:
                pass