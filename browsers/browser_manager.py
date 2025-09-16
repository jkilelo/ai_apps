"""Browser lifecycle management with Playwright"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright
from loguru import logger
import asyncio
from .stealth_manager import StealthManager


@dataclass
class BrowserConfig:
    """Configuration for browser instance"""
    browser_type: str = "chromium"  # chromium, firefox, webkit
    headless: bool = False
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: Optional[str] = None
    locale: str = "en-US"
    timezone: str = "America/New_York"
    color_scheme: str = "light"
    device_scale_factor: float = 1.0
    is_mobile: bool = False
    has_touch: bool = False
    javascript_enabled: bool = True
    bypass_csp: bool = False
    user_data_dir: Optional[str] = None
    downloads_path: Optional[str] = None
    storage_state: Optional[str] = None  # Path to saved auth state
    proxy: Optional[Dict[str, Any]] = None
    extra_http_headers: Optional[Dict[str, str]] = None
    record_video: bool = False
    record_video_dir: Optional[str] = None
    slow_mo: int = 0  # Milliseconds to slow down operations


class IBrowserManager(ABC):
    """Abstract interface for browser management"""
    
    @abstractmethod
    async def launch(self, config: Optional[BrowserConfig] = None) -> Browser:
        """Launch a browser instance"""
        pass
    
    @abstractmethod
    async def new_context(self, **kwargs) -> BrowserContext:
        """Create a new browser context"""
        pass
    
    @abstractmethod
    async def new_page(self, context: Optional[BrowserContext] = None) -> Page:
        """Create a new page in context"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close browser and cleanup resources"""
        pass
    
    @abstractmethod
    async def close_context(self, context: BrowserContext) -> None:
        """Close specific context"""
        pass
    
    @abstractmethod
    async def save_storage_state(self, context: BrowserContext, path: str) -> None:
        """Save authentication state"""
        pass
    
    @abstractmethod
    async def load_storage_state(self, path: str) -> Dict:
        """Load authentication state"""
        pass


class BrowserManager(IBrowserManager):
    """Concrete implementation of browser manager using Playwright"""
    
    def __init__(self, enable_stealth: bool = True):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.contexts: List[BrowserContext] = []
        self.config: Optional[BrowserConfig] = None
        self._lock = asyncio.Lock()
        self.stealth_manager = StealthManager() if enable_stealth else None
        
    async def launch(self, config: Optional[BrowserConfig] = None) -> Browser:
        """Launch browser with configuration"""
        async with self._lock:
            if self.browser:
                logger.warning("Browser already launched, returning existing instance")
                return self.browser
            
            self.config = config or BrowserConfig()
            logger.info(f"Launching {self.config.browser_type} browser (headless={self.config.headless})")
            
            try:
                # Start playwright
                self.playwright = await async_playwright().start()
                
                # Select browser type
                browser_launcher = getattr(self.playwright, self.config.browser_type)
                
                # Prepare launch options
                launch_options = {
                    "headless": self.config.headless,
                    "slow_mo": self.config.slow_mo,
                }
                
                # Add proxy if configured
                if self.config.proxy:
                    launch_options["proxy"] = self.config.proxy
                
                # Add downloads path
                if self.config.downloads_path:
                    launch_options["downloads_path"] = self.config.downloads_path
                
                # Launch browser
                self.browser = await browser_launcher.launch(**launch_options)
                logger.success(f"Browser launched successfully")
                
                return self.browser
                
            except Exception as e:
                logger.error(f"Failed to launch browser: {e}")
                await self.cleanup_on_error()
                raise
    
    async def new_context(self, **kwargs) -> BrowserContext:
        """Create new browser context with configuration"""
        if not self.browser:
            await self.launch()
        
        # Prepare context options
        context_options = {}
        
        if self.config:
            # Apply viewport settings
            context_options["viewport"] = {
                "width": self.config.viewport_width,
                "height": self.config.viewport_height
            }
            
            # Apply other settings
            if self.config.user_agent:
                context_options["user_agent"] = self.config.user_agent
            
            context_options.update({
                "locale": self.config.locale,
                "timezone_id": self.config.timezone,
                "color_scheme": self.config.color_scheme,
                "device_scale_factor": self.config.device_scale_factor,
                "is_mobile": self.config.is_mobile,
                "has_touch": self.config.has_touch,
                "java_script_enabled": self.config.javascript_enabled,
                "bypass_csp": self.config.bypass_csp,
            })
            
            # Add extra headers
            if self.config.extra_http_headers:
                context_options["extra_http_headers"] = self.config.extra_http_headers
            
            # Load storage state if available
            if self.config.storage_state:
                context_options["storage_state"] = self.config.storage_state
            
            # Record video if configured
            if self.config.record_video and self.config.record_video_dir:
                context_options["record_video_dir"] = self.config.record_video_dir
                context_options["record_video_size"] = {
                    "width": self.config.viewport_width,
                    "height": self.config.viewport_height
                }
        
        # Override with any provided kwargs
        context_options.update(kwargs)
        
        # Create context
        context = await self.browser.new_context(**context_options)
        self.contexts.append(context)
        
        # Apply stealth measures if enabled
        if self.stealth_manager:
            logger.info("Applying stealth measures to new context")
            await self.stealth_manager.apply_to_context(context)
        
        # Set default timeout
        context.set_default_timeout(30000)  # 30 seconds
        context.set_default_navigation_timeout(30000)
        
        logger.info(f"Created new browser context (total contexts: {len(self.contexts)})")
        return context
    
    async def new_page(self, context: Optional[BrowserContext] = None) -> Page:
        """Create new page in context"""
        if context is None:
            # Create new context if not provided
            context = await self.new_context()
        
        page = await context.new_page()
        
        # Configure page settings
        await page.set_viewport_size({
            "width": self.config.viewport_width if self.config else 1920,
            "height": self.config.viewport_height if self.config else 1080
        })
        
        # Add console message handler for debugging
        page.on("console", lambda msg: logger.debug(f"Browser console: {msg.text}"))
        
        # Add page error handler
        page.on("pageerror", lambda err: logger.error(f"Page error: {err}"))
        
        # Add request failed handler
        page.on("requestfailed", lambda req: logger.warning(f"Request failed: {req.url}"))
        
        # Apply page-level stealth measures
        if self.stealth_manager:
            await self.stealth_manager.apply_to_page(page)
        
        logger.info(f"Created new page: {page.url}")
        return page
    
    async def close_context(self, context: BrowserContext) -> None:
        """Close specific browser context"""
        try:
            await context.close()
            if context in self.contexts:
                self.contexts.remove(context)
            logger.info(f"Closed browser context (remaining: {len(self.contexts)})")
        except Exception as e:
            logger.error(f"Error closing context: {e}")
    
    async def save_storage_state(self, context: BrowserContext, path: str) -> None:
        """Save authentication state to file"""
        try:
            state = await context.storage_state(path=path)
            logger.info(f"Saved storage state to {path}")
            return state
        except Exception as e:
            logger.error(f"Failed to save storage state: {e}")
            raise
    
    async def load_storage_state(self, path: str) -> Dict:
        """Load authentication state from file"""
        import json
        try:
            with open(path, 'r') as f:
                state = json.load(f)
            logger.info(f"Loaded storage state from {path}")
            return state
        except Exception as e:
            logger.error(f"Failed to load storage state: {e}")
            raise
    
    async def close(self) -> None:
        """Close browser and cleanup all resources"""
        async with self._lock:
            try:
                # Close all contexts
                for context in self.contexts.copy():
                    await self.close_context(context)
                
                # Close browser
                if self.browser:
                    await self.browser.close()
                    logger.info("Browser closed")
                
                # Stop playwright
                if self.playwright:
                    await self.playwright.stop()
                    logger.info("Playwright stopped")
                
                # Reset state
                self.browser = None
                self.playwright = None
                self.contexts = []
                
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
                raise
    
    async def cleanup_on_error(self) -> None:
        """Emergency cleanup on error"""
        try:
            if self.playwright:
                await self.playwright.stop()
            self.browser = None
            self.playwright = None
            self.contexts = []
        except:
            pass
    
    async def __aenter__(self):
        """Context manager entry"""
        await self.launch()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()
    
    def is_running(self) -> bool:
        """Check if browser is running"""
        return self.browser is not None and self.browser.is_connected()