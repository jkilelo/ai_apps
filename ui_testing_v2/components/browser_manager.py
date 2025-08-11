"""
Browser automation manager for coordinating Playwright and Selenium instances.
Provides unified interface for browser automation with intelligent driver selection.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse
import aiofiles
import json
from pathlib import Path

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Error as PlaywrightError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from ui_testing_v2.core.config import Config

logger = logging.getLogger(__name__)


class BrowserStrategy(ABC):
    """Abstract base class for browser automation strategies"""
    
    @abstractmethod
    async def setup(self, config: Dict[str, Any]) -> Any:
        """Setup browser instance"""
        pass
    
    @abstractmethod
    async def teardown(self) -> None:
        """Cleanup browser instance"""
        pass
    
    @abstractmethod
    async def navigate_to(self, url: str) -> None:
        """Navigate to URL"""
        pass
    
    @abstractmethod
    async def take_screenshot(self, path: Optional[str] = None) -> str:
        """Take screenshot and return path"""
        pass
    
    @abstractmethod
    async def get_page_source(self) -> str:
        """Get page source HTML"""
        pass
    
    @abstractmethod
    async def wait_for_page_load(self, timeout: int = 30) -> None:
        """Wait for page to fully load"""
        pass
    
    @abstractmethod
    def get_driver_instance(self) -> Any:
        """Get the underlying driver instance"""
        pass


class PlaywrightBrowserStrategy(BrowserStrategy):
    """Browser automation using Playwright"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self._screenshot_counter = 0
    
    async def setup(self, config: Dict[str, Any]) -> Page:
        """Setup Playwright browser"""
        try:
            self.playwright = await async_playwright().start()
            
            # Browser configuration
            browser_type = config.get('browser', 'chromium').lower()
            headless = config.get('headless', True)
            
            # Launch browser
            if browser_type == 'chromium':
                self.browser = await self.playwright.chromium.launch(
                    headless=headless,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor'
                    ]
                )
            elif browser_type == 'firefox':
                self.browser = await self.playwright.firefox.launch(headless=headless)
            elif browser_type == 'webkit':
                self.browser = await self.playwright.webkit.launch(headless=headless)
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")
            
            # Create context with additional options
            context_options = {
                'viewport': {'width': config.get('width', 1920), 'height': config.get('height', 1080)},
                'user_agent': config.get('user_agent', ''),
                'ignore_https_errors': config.get('ignore_https_errors', True),
                'java_script_enabled': config.get('javascript_enabled', True),
            }
            
            # Add proxy if configured
            if config.get('proxy'):
                context_options['proxy'] = config['proxy']
            
            self.context = await self.browser.new_context(**context_options)
            
            # Create page
            self.page = await self.context.new_page()
            
            # Set timeouts
            self.page.set_default_timeout(config.get('timeout', 30) * 1000)
            self.page.set_default_navigation_timeout(config.get('navigation_timeout', 30) * 1000)
            
            logger.info(f"Playwright {browser_type} browser setup completed")
            return self.page
            
        except Exception as e:
            logger.error(f"Playwright browser setup failed: {e}")
            await self.teardown()
            raise
    
    async def teardown(self) -> None:
        """Cleanup Playwright browser"""
        try:
            if self.page:
                await self.page.close()
                self.page = None
            
            if self.context:
                await self.context.close()
                self.context = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            logger.info("Playwright browser teardown completed")
            
        except Exception as e:
            logger.error(f"Playwright teardown error: {e}")
    
    async def navigate_to(self, url: str) -> None:
        """Navigate to URL using Playwright"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        try:
            await self.page.goto(url, wait_until='networkidle')
            logger.info(f"Navigated to: {url}")
        except Exception as e:
            logger.error(f"Navigation failed for {url}: {e}")
            raise
    
    async def take_screenshot(self, path: Optional[str] = None) -> str:
        """Take screenshot using Playwright"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        try:
            if path is None:
                self._screenshot_counter += 1
                path = f"screenshot_playwright_{self._screenshot_counter}.png"
            
            await self.page.screenshot(path=path, full_page=True)
            logger.info(f"Screenshot saved: {path}")
            return path
            
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            raise
    
    async def get_page_source(self) -> str:
        """Get page source using Playwright"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        try:
            content = await self.page.content()
            return content
        except Exception as e:
            logger.error(f"Failed to get page source: {e}")
            raise
    
    async def wait_for_page_load(self, timeout: int = 30) -> None:
        """Wait for page to fully load using Playwright"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        try:
            await self.page.wait_for_load_state('networkidle', timeout=timeout * 1000)
        except Exception as e:
            logger.warning(f"Page load wait timeout: {e}")
    
    def get_driver_instance(self) -> Page:
        """Get Playwright page instance"""
        return self.page
    
    async def execute_script(self, script: str) -> Any:
        """Execute JavaScript on the page"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        return await self.page.evaluate(script)
    
    async def wait_for_element(self, selector: str, timeout: int = 30) -> Any:
        """Wait for element to be visible"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        try:
            element = await self.page.wait_for_selector(selector, timeout=timeout * 1000)
            return element
        except Exception as e:
            logger.error(f"Element wait failed for selector '{selector}': {e}")
            raise


class SeleniumBrowserStrategy(BrowserStrategy):
    """Browser automation using Selenium"""
    
    def __init__(self):
        self.driver = None
        self._screenshot_counter = 0
    
    async def setup(self, config: Dict[str, Any]) -> webdriver.Remote:
        """Setup Selenium browser"""
        try:
            browser_type = config.get('browser', 'chrome').lower()
            headless = config.get('headless', True)
            
            if browser_type == 'chrome':
                options = ChromeOptions()
                
                if headless:
                    options.add_argument('--headless')
                
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-web-security')
                options.add_argument('--disable-gpu')
                options.add_argument(f'--window-size={config.get("width", 1920)},{config.get("height", 1080)}')
                
                # User agent
                if config.get('user_agent'):
                    options.add_argument(f'--user-agent={config["user_agent"]}')
                
                # Proxy configuration
                if config.get('proxy'):
                    proxy_config = config['proxy']
                    if 'server' in proxy_config:
                        options.add_argument(f'--proxy-server={proxy_config["server"]}')
                
                # Setup ChromeDriver
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                
            elif browser_type == 'firefox':
                options = FirefoxOptions()
                
                if headless:
                    options.add_argument('--headless')
                
                # Setup GeckoDriver
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=options)
                
                # Set window size
                self.driver.set_window_size(config.get('width', 1920), config.get('height', 1080))
                
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")
            
            # Set timeouts
            self.driver.implicitly_wait(config.get('implicit_wait', 10))
            self.driver.set_page_load_timeout(config.get('page_load_timeout', 30))
            self.driver.set_script_timeout(config.get('script_timeout', 30))
            
            logger.info(f"Selenium {browser_type} browser setup completed")
            return self.driver
            
        except Exception as e:
            logger.error(f"Selenium browser setup failed: {e}")
            await self.teardown()
            raise
    
    async def teardown(self) -> None:
        """Cleanup Selenium browser"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
            
            logger.info("Selenium browser teardown completed")
            
        except Exception as e:
            logger.error(f"Selenium teardown error: {e}")
    
    async def navigate_to(self, url: str) -> None:
        """Navigate to URL using Selenium"""
        if not self.driver:
            raise RuntimeError("Browser not initialized")
        
        try:
            self.driver.get(url)
            # Wait for page load
            await self.wait_for_page_load()
            logger.info(f"Navigated to: {url}")
        except Exception as e:
            logger.error(f"Navigation failed for {url}: {e}")
            raise
    
    async def take_screenshot(self, path: Optional[str] = None) -> str:
        """Take screenshot using Selenium"""
        if not self.driver:
            raise RuntimeError("Browser not initialized")
        
        try:
            if path is None:
                self._screenshot_counter += 1
                path = f"screenshot_selenium_{self._screenshot_counter}.png"
            
            self.driver.save_screenshot(path)
            logger.info(f"Screenshot saved: {path}")
            return path
            
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            raise
    
    async def get_page_source(self) -> str:
        """Get page source using Selenium"""
        if not self.driver:
            raise RuntimeError("Browser not initialized")
        
        try:
            return self.driver.page_source
        except Exception as e:
            logger.error(f"Failed to get page source: {e}")
            raise
    
    async def wait_for_page_load(self, timeout: int = 30) -> None:
        """Wait for page to fully load using Selenium"""
        if not self.driver:
            raise RuntimeError("Browser not initialized")
        
        try:
            # Wait for document ready state
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(self.driver, timeout)
            wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            
        except Exception as e:
            logger.warning(f"Page load wait timeout: {e}")
    
    def get_driver_instance(self) -> webdriver.Remote:
        """Get Selenium driver instance"""
        return self.driver
    
    async def execute_script(self, script: str) -> Any:
        """Execute JavaScript using Selenium"""
        if not self.driver:
            raise RuntimeError("Browser not initialized")
        
        return self.driver.execute_script(script)
    
    async def wait_for_element(self, selector: str, timeout: int = 30) -> Any:
        """Wait for element to be visible using Selenium"""
        if not self.driver:
            raise RuntimeError("Browser not initialized")
        
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
            return element
        except Exception as e:
            logger.error(f"Element wait failed for selector '{selector}': {e}")
            raise


class BrowserManager:
    """Unified browser automation manager"""
    
    def __init__(self, config: Config):
        self.config = config
        self.current_strategy = None
        self.current_browser_type = None
        self._session_data = {}
    
    async def setup_browser(
        self, 
        browser_type: str = "playwright", 
        browser_config: Optional[Dict[str, Any]] = None
    ) -> Union[Page, webdriver.Remote]:
        """
        Setup browser with specified type and configuration
        
        Args:
            browser_type: 'playwright' or 'selenium'
            browser_config: Browser-specific configuration
            
        Returns:
            Browser driver instance (Page for Playwright, WebDriver for Selenium)
        """
        try:
            # Clean up existing browser if any
            await self.cleanup()
            
            # Default configuration
            default_config = {
                'browser': 'chromium' if browser_type == 'playwright' else 'chrome',
                'headless': self.config.browser.headless,
                'width': self.config.browser.window_width,
                'height': self.config.browser.window_height,
                'timeout': self.config.browser.timeout,
                'navigation_timeout': self.config.browser.navigation_timeout,
                'user_agent': self.config.browser.user_agent,
                'ignore_https_errors': True,
                'javascript_enabled': True
            }
            
            # Merge with provided config
            if browser_config:
                default_config.update(browser_config)
            
            # Initialize strategy based on type
            if browser_type.lower() == 'playwright':
                self.current_strategy = PlaywrightBrowserStrategy()
            elif browser_type.lower() == 'selenium':
                self.current_strategy = SeleniumBrowserStrategy()
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")
            
            self.current_browser_type = browser_type.lower()
            
            # Setup browser
            driver_instance = await self.current_strategy.setup(default_config)
            
            # Store session data
            self._session_data = {
                'browser_type': browser_type,
                'config': default_config,
                'setup_time': asyncio.get_event_loop().time()
            }
            
            logger.info(f"Browser manager setup completed with {browser_type}")
            return driver_instance
            
        except Exception as e:
            logger.error(f"Browser setup failed: {e}")
            await self.cleanup()
            raise
    
    async def navigate_to(self, url: str) -> None:
        """Navigate to URL"""
        if not self.current_strategy:
            raise RuntimeError("Browser not initialized")
        
        await self.current_strategy.navigate_to(url)
    
    async def take_screenshot(self, path: Optional[str] = None) -> str:
        """Take screenshot"""
        if not self.current_strategy:
            raise RuntimeError("Browser not initialized")
        
        return await self.current_strategy.take_screenshot(path)
    
    async def get_page_source(self) -> str:
        """Get page source"""
        if not self.current_strategy:
            raise RuntimeError("Browser not initialized")
        
        return await self.current_strategy.get_page_source()
    
    async def wait_for_page_load(self, timeout: int = 30) -> None:
        """Wait for page to load"""
        if not self.current_strategy:
            raise RuntimeError("Browser not initialized")
        
        await self.current_strategy.wait_for_page_load(timeout)
    
    async def execute_script(self, script: str) -> Any:
        """Execute JavaScript"""
        if not self.current_strategy:
            raise RuntimeError("Browser not initialized")
        
        return await self.current_strategy.execute_script(script)
    
    async def wait_for_element(self, selector: str, timeout: int = 30) -> Any:
        """Wait for element"""
        if not self.current_strategy:
            raise RuntimeError("Browser not initialized")
        
        return await self.current_strategy.wait_for_element(selector, timeout)
    
    def get_driver_instance(self) -> Union[Page, webdriver.Remote]:
        """Get current browser driver instance"""
        if not self.current_strategy:
            raise RuntimeError("Browser not initialized")
        
        return self.current_strategy.get_driver_instance()
    
    def get_browser_type(self) -> Optional[str]:
        """Get current browser type"""
        return self.current_browser_type
    
    def get_session_data(self) -> Dict[str, Any]:
        """Get current session data"""
        return self._session_data.copy()
    
    async def cleanup(self) -> None:
        """Cleanup current browser"""
        if self.current_strategy:
            await self.current_strategy.teardown()
            self.current_strategy = None
            self.current_browser_type = None
            self._session_data = {}
    
    @asynccontextmanager
    async def browser_session(
        self, 
        browser_type: str = "playwright", 
        browser_config: Optional[Dict[str, Any]] = None
    ):
        """Context manager for browser sessions"""
        driver = None
        try:
            driver = await self.setup_browser(browser_type, browser_config)
            yield driver
        finally:
            await self.cleanup()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check browser manager health"""
        health_data = {
            'status': 'healthy',
            'browser_initialized': self.current_strategy is not None,
            'browser_type': self.current_browser_type,
            'session_data': self._session_data
        }
        
        # Test browser if initialized
        if self.current_strategy:
            try:
                # Simple test - get current URL or page title
                if self.current_browser_type == 'playwright':
                    page = self.get_driver_instance()
                    if page:
                        health_data['current_url'] = page.url
                elif self.current_browser_type == 'selenium':
                    driver = self.get_driver_instance()
                    if driver:
                        health_data['current_url'] = driver.current_url
                        
            except Exception as e:
                health_data['status'] = 'degraded'
                health_data['error'] = str(e)
        
        return health_data


class ElementInteractionManager:
    """Manager for element interactions across different browser types"""
    
    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager
    
    async def click_element(self, selector: str, timeout: int = 30) -> bool:
        """Click element using appropriate method"""
        try:
            browser_type = self.browser_manager.get_browser_type()
            driver = self.browser_manager.get_driver_instance()
            
            if browser_type == 'playwright':
                element = await driver.wait_for_selector(selector, timeout=timeout * 1000)
                await element.click()
            elif browser_type == 'selenium':
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                wait = WebDriverWait(driver, timeout)
                element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                element.click()
            
            logger.info(f"Clicked element: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to click element {selector}: {e}")
            return False
    
    async def type_text(self, selector: str, text: str, timeout: int = 30) -> bool:
        """Type text into element"""
        try:
            browser_type = self.browser_manager.get_browser_type()
            driver = self.browser_manager.get_driver_instance()
            
            if browser_type == 'playwright':
                element = await driver.wait_for_selector(selector, timeout=timeout * 1000)
                await element.clear()
                await element.type(text)
            elif browser_type == 'selenium':
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                wait = WebDriverWait(driver, timeout)
                element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                element.clear()
                element.send_keys(text)
            
            logger.info(f"Typed text into element: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to type text into element {selector}: {e}")
            return False
    
    async def select_option(self, selector: str, value: str, timeout: int = 30) -> bool:
        """Select option from dropdown"""
        try:
            browser_type = self.browser_manager.get_browser_type()
            driver = self.browser_manager.get_driver_instance()
            
            if browser_type == 'playwright':
                element = await driver.wait_for_selector(selector, timeout=timeout * 1000)
                await element.select_option(value=value)
            elif browser_type == 'selenium':
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait, Select
                from selenium.webdriver.support import expected_conditions as EC
                
                wait = WebDriverWait(driver, timeout)
                element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                select = Select(element)
                select.select_by_value(value)
            
            logger.info(f"Selected option {value} in element: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to select option in element {selector}: {e}")
            return False
    
    async def get_element_text(self, selector: str, timeout: int = 30) -> Optional[str]:
        """Get text content of element"""
        try:
            browser_type = self.browser_manager.get_browser_type()
            driver = self.browser_manager.get_driver_instance()
            
            if browser_type == 'playwright':
                element = await driver.wait_for_selector(selector, timeout=timeout * 1000)
                return await element.text_content()
            elif browser_type == 'selenium':
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                wait = WebDriverWait(driver, timeout)
                element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                return element.text
            
        except Exception as e:
            logger.error(f"Failed to get text from element {selector}: {e}")
            return None
    
    async def is_element_visible(self, selector: str, timeout: int = 5) -> bool:
        """Check if element is visible"""
        try:
            browser_type = self.browser_manager.get_browser_type()
            driver = self.browser_manager.get_driver_instance()
            
            if browser_type == 'playwright':
                element = await driver.query_selector(selector)
                if element:
                    return await element.is_visible()
                return False
            elif browser_type == 'selenium':
                from selenium.webdriver.common.by import By
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return elements[0].is_displayed()
                return False
            
        except Exception:
            return False
