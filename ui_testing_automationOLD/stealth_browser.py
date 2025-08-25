#!/usr/bin/env python3
"""

# AI-FIRST: This module requires live LLM connections, no mock support
STEALTH_BROWSER MODULE - Comprehensive Stealth Browser with Anti-Detection
Combines best features from ultimate_stealth_browser.py and other implementations
Part of PHASE2 implementation following QUANTUM_ENHANCED_PROMPT specifications
"""

import asyncio
import json
import random
import time
import hashlib
import platform
import os
import sys
import math
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from pathlib import Path
from contextlib import asynccontextmanager

# Import local modules
from utils import Logger, PlatformUtils, PerformanceTimer, ErrorHandler, AsyncUtils
from shared import AsyncioConfig, BaseComponent, ComponentStatus, ExtractedElement, ElementType, InteractionType
# TODO: Review unused imports: AsyncUtils, Union, Browser, asdict, PerformanceTimer, time, platform, Page, Callable, BrowserContext, hashlib, Path, field, PlaywrightError, json, datetime, ElementHandle

# Third-party imports with graceful fallbacks
try:
    from playwright.async_api import (
        Browser, BrowserContext, Page, ElementHandle,
        Error as PlaywrightError, async_playwright
    )
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("[WARNING] Playwright not installed. Install with: pip install playwright")
    print("[INFO] Then run: playwright install chromium")


# ============================================================================
# CONFIGURATION AND DATA MODELS
# ============================================================================

class StealthLevel(Enum):
    """Stealth levels for different anti-detection requirements"""
    BASIC = "basic"        # Basic anti-detection
    ENHANCED = "enhanced"  # Enhanced with stealth features
    MAXIMUM = "maximum"    # Maximum stealth with all features
    PARANOID = "paranoid"  # Extreme measures for heavily protected sites


@dataclass
class StealthConfig:
    """Complete stealth configuration"""
    # Core settings
    level: StealthLevel = StealthLevel.MAXIMUM
    headless: bool = False  # False for better stealth
    
    # Stealth features
    hide_webdriver: bool = True
    hide_automation_indicators: bool = True
    spoof_plugins: bool = True
    spoof_languages: bool = True
    prevent_webrtc_leak: bool = True
    spoof_canvas_fingerprint: bool = True
    bypass_csp: bool = True
    
    # Human simulation
    enable_human_typing: bool = True
    enable_human_mouse: bool = True
    enable_human_scrolling: bool = True
    enable_human_delays: bool = True
    
    # Performance
    max_retry_attempts: int = 3
    timeout: int = 60000  # milliseconds
    
    # Browser settings
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: Optional[str] = None
    locale: str = 'en-US'
    timezone: str = 'America/New_York'
    
    # Delays (milliseconds)
    human_delay_range: Tuple[int, int] = (100, 2000)
    typing_delay_range: Tuple[int, int] = (50, 200)
    mouse_delay_range: Tuple[int, int] = (10, 50)


# ============================================================================
# STEALTH INJECTION SYSTEM
# ============================================================================

class StealthInjector:
    """Comprehensive stealth script injection system"""
    
    @staticmethod
    async def inject_all_stealth(page: 'Page', config: StealthConfig):
        """Inject all stealth scripts based on configuration"""
        logger = Logger.get_logger("StealthInjector")
        
        try:
            # Basic stealth - always applied
            await StealthInjector._inject_webdriver_override(page)
            await StealthInjector._inject_navigator_override(page)
            
            # Enhanced stealth
            if config.level in [StealthLevel.ENHANCED, StealthLevel.MAXIMUM, StealthLevel.PARANOID]:
                await StealthInjector._inject_chrome_runtime(page)
                await StealthInjector._inject_permissions_override(page)
                
            # Maximum stealth
            if config.level in [StealthLevel.MAXIMUM, StealthLevel.PARANOID]:
                await StealthInjector._inject_webgl_override(page)
                await StealthInjector._inject_canvas_override(page)
                await StealthInjector._inject_webrtc_override(page)
                
            # Paranoid level
            if config.level == StealthLevel.PARANOID:
                await StealthInjector._inject_battery_override(page)
                await StealthInjector._inject_media_devices_override(page)
                
            logger.info(f"Stealth injection completed for level: {config.level.value}")
            
        except Exception as e:
            logger.error(f"Error injecting stealth: {e}")
    
    @staticmethod
    async def _inject_webdriver_override(page: 'Page'):
        """Hide webdriver indicators"""
        await page.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Remove automation controlled flag
            Object.defineProperty(navigator, 'automationControlled', {
                get: () => undefined
            });
            
            // Clean document properties
            if (document.documentElement) {
                delete document.documentElement.webdriver;
            }
        """)
    
    @staticmethod
    async def _inject_navigator_override(page: 'Page'):
        """Override navigator properties"""
        await page.add_init_script("""
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    return [
                        {0: {type: "application/x-google-chrome-pdf", suffixes: "pdf"}, length: 1, name: "Chrome PDF Plugin"},
                        {0: {type: "application/pdf", suffixes: "pdf"}, length: 1, name: "Chrome PDF Viewer"},
                        {0: {type: "application/x-nacl", suffixes: ""}, length: 1, name: "Native Client"}
                    ];
                }
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Override platform
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Win32'
            });
            
            // Override vendor
            Object.defineProperty(navigator, 'vendor', {
                get: () => 'Google Inc.'
            });
        """)
    
    @staticmethod
    async def _inject_chrome_runtime(page: 'Page'):
        """Inject Chrome runtime"""
        await page.add_init_script("""
            window.chrome = {
                runtime: {
                    connect: () => {},
                    sendMessage: () => {},
                    onMessage: { addListener: () => {} }
                },
                loadTimes: () => ({
                    requestTime: Date.now() / 1000,
                    startLoadTime: Date.now() / 1000,
                    commitLoadTime: Date.now() / 1000,
                    finishDocumentLoadTime: Date.now() / 1000
                }),
                csi: () => ({
                    onloadT: Date.now(),
                    startE: Date.now() - 1000,
                    pageT: Date.now() - Date.now()
                })
            };
        """)
    
    @staticmethod
    async def _inject_permissions_override(page: 'Page'):
        """Override permissions API"""
        await page.add_init_script("""
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: 'default' }) :
                    originalQuery(parameters)
            );
        """)
    
    @staticmethod
    async def _inject_webgl_override(page: 'Page'):
        """Override WebGL fingerprinting"""
        await page.add_init_script("""
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter.apply(this, arguments);
            };
        """)
    
    @staticmethod
    async def _inject_canvas_override(page: 'Page'):
        """Override canvas fingerprinting"""
        await page.add_init_script("""
            const original = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function() {
                const context = this.getContext('2d');
                const imageData = context.getImageData(0, 0, this.width, this.height);
                for (let i = 0; i < imageData.data.length; i += 4) {
                    imageData.data[i] = imageData.data[i] ^ (Math.random() * 0.1);
                }
                context.putImageData(imageData, 0, 0);
                return original.apply(this, arguments);
            };
        """)
    
    @staticmethod
    async def _inject_webrtc_override(page: 'Page'):
        """Prevent WebRTC IP leak"""
        await page.add_init_script("""
            const RTCPeerConnection = window.RTCPeerConnection 
                || window.webkitRTCPeerConnection 
                || window.mozRTCPeerConnection;
            
            if (RTCPeerConnection) {
                const original = RTCPeerConnection.prototype.createDataChannel;
                RTCPeerConnection.prototype.createDataChannel = function() {
                    return null;
                };
            }
        """)
    
    @staticmethod
    async def _inject_battery_override(page: 'Page'):
        """Override battery API"""
        await page.add_init_script("""
            navigator.getBattery = () => Promise.resolve({
                charging: true,
                chargingTime: 0,
                dischargingTime: Infinity,
                level: 0.99
            });
        """)
    
    @staticmethod
    async def _inject_media_devices_override(page: 'Page'):
        """Override media devices"""
        await page.add_init_script("""
            navigator.mediaDevices.enumerateDevices = () => Promise.resolve([
                {deviceId: "default", kind: "audioinput", label: "Default Audio Device", groupId: "default"},
                {deviceId: "default", kind: "videoinput", label: "Default Video Device", groupId: "default"}
            ]);
        """)


# ============================================================================
# HUMAN BEHAVIOR SIMULATION
# ============================================================================

class HumanSimulator:
    """Simulate human-like behavior patterns"""
    
    @staticmethod
    async def human_type(page: 'Page', selector: str, text: str, config: StealthConfig):
        """Type text with human-like delays and corrections"""
        if not config.enable_human_typing:
            await page.fill(selector, text)
            return
        
        element = await page.query_selector(selector)
        if not element:
            return
        
        await element.click()
        
        for char in text:
            # Occasionally make typos and correct them
            if random.random() < 0.02:  # 2% chance of typo
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                await element.type(wrong_char)
                await asyncio.sleep(random.uniform(0.1, 0.3))
                await element.press('Backspace')
                await asyncio.sleep(random.uniform(0.05, 0.15))
            
            await element.type(char)
            
            # Variable typing speed
            min_delay, max_delay = config.typing_delay_range
            delay = random.uniform(min_delay / 1000, max_delay / 1000)
            
            # Longer pause after punctuation
            if char in '.,!?;:':
                delay *= 2
            
            await asyncio.sleep(delay)
    
    @staticmethod
    async def human_click(page: 'Page', selector: str, config: StealthConfig):
        """Click with human-like mouse movement"""
        if not config.enable_human_mouse:
            await page.click(selector)
            return
        
        element = await page.query_selector(selector)
        if not element:
            return
        
        # Get element position
        box = await element.bounding_box()
        if not box:
            return
        
        # Add random offset within element
        x = box['x'] + box['width'] * random.uniform(0.3, 0.7)
        y = box['y'] + box['height'] * random.uniform(0.3, 0.7)
        
        # Move mouse with curve
        await HumanSimulator._curved_mouse_move(page, x, y)
        
        # Random delay before click
        await asyncio.sleep(random.uniform(0.05, 0.15))
        
        # Click
        await page.mouse.click(x, y)
    
    @staticmethod
    async def _curved_mouse_move(page: 'Page', target_x: float, target_y: float):
        """Move mouse in a curved path"""
        # Get current position (approximate)
        steps = random.randint(10, 25)
        
        for i in range(steps):
            progress = (i + 1) / steps
            
            # Add curve using sine wave
            curve = math.sin(progress * math.pi) * random.uniform(10, 50)
            
            x = target_x * progress + curve * random.choice([1, -1])
            y = target_y * progress + curve * random.choice([1, -1])
            
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.005, 0.02))
    
    @staticmethod
    async def human_scroll(page: 'Page', config: StealthConfig):
        """Scroll page with human-like patterns"""
        if not config.enable_human_scrolling:
            return
        
        # Random scroll amount
        scroll_amount = random.randint(100, 500)
        
        # Smooth scroll
        steps = random.randint(5, 15)
        for _ in range(steps):
            await page.mouse.wheel(0, scroll_amount / steps)
            await asyncio.sleep(random.uniform(0.01, 0.05))
    
    @staticmethod
    async def random_delay(config: StealthConfig):
        """Add random human-like delay"""
        if not config.enable_human_delays:
            return
        
        min_delay, max_delay = config.human_delay_range
        delay = random.uniform(min_delay / 1000, max_delay / 1000)
        await asyncio.sleep(delay)


# ============================================================================
# MAIN STEALTH BROWSER CLASS
# ============================================================================

class StealthBrowser(BaseComponent):
    """Comprehensive stealth browser with anti-detection capabilities"""
    
    def __init__(self, config: Optional[StealthConfig] = None) -> None:
        """Initialize stealth browser"""
        super().__init__("StealthBrowser")
        self.config = config or StealthConfig()
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self._human_sim = HumanSimulator()
        self._stealth_injector = StealthInjector()
    
    async def initialize(self):
        """Initialize the browser component"""
        await super().initialize()
        
        if not HAS_PLAYWRIGHT:
            raise RuntimeError("Playwright is not installed. Run: pip install playwright && playwright install chromium")
        
        # Setup asyncio for Windows
        AsyncioConfig.setup_event_loop_policy()
    
    async def start(self):
        """Start the browser"""
        await super().start()
        
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser with stealth options
            launch_options = self._get_launch_options()
            self.browser = await self.playwright.chromium.launch(**launch_options)
            
            # Create context with stealth settings
            context_options = self._get_context_options()
            self.context = await self.browser.new_context(**context_options)
            
            # Set up context-level stealth
            await self._setup_context_stealth()
            
            self.logger.info("Stealth browser started successfully")
            
        except Exception as e:
            self.status = ComponentStatus.ERROR
            ErrorHandler.log_error("StealthBrowser", e, "Failed to start browser")
            raise
    
    async def stop(self):
        """Stop the browser"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            self.logger.error(f"Error stopping browser: {e}")
        
        await super().stop()
    
    def _get_launch_options(self) -> Dict[str, Any]:
        """Get browser launch options with stealth settings"""
        options = {
            'headless': self.config.headless,
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-infobars',
                '--window-position=0,0',
                '--ignore-certificate-errors',
                '--ignore-certificate-errors-skip-list',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--hide-scrollbars',
                '--mute-audio',
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                f'--window-size={self.config.viewport_width},{self.config.viewport_height}'
            ]
        }
        
        # Add Chrome executable if available
        chrome_path = PlatformUtils.get_chrome_executable_path()
        if chrome_path:
            options['executable_path'] = chrome_path
        
        return options
    
    def _get_context_options(self) -> Dict[str, Any]:
        """Get browser context options"""
        options = {
            'viewport': {
                'width': self.config.viewport_width,
                'height': self.config.viewport_height
            },
            'user_agent': self.config.user_agent or self._generate_user_agent(),
            'locale': self.config.locale,
            'timezone_id': self.config.timezone,
            'ignore_https_errors': True,
            'java_script_enabled': True,
        }
        
        # Add permissions
        options['permissions'] = ['geolocation', 'notifications']
        
        # Add extra headers
        options['extra_http_headers'] = {
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        return options
    
    def _generate_user_agent(self) -> str:
        """Generate realistic user agent"""
        chrome_version = random.choice(['120', '121', '122', '123'])
        return f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.0.0 Safari/537.36'
    
    async def _setup_context_stealth(self):
        """Set up context-level stealth features"""
        # Add stealth scripts to all new pages
        async def on_page(page):
            await self._stealth_injector.inject_all_stealth(page, self.config)
        
        self.context.on('page', on_page)
    
    @asynccontextmanager
    async def new_page(self, url: Optional[str] = None):
        """Create a new page with stealth features"""
        page = await self.context.new_page()
        
        try:
            # Inject stealth scripts
            await self._stealth_injector.inject_all_stealth(page, self.config)
            
            # Navigate if URL provided
            if url:
                await self.goto(page, url)
            
            yield page
            
        finally:
            await page.close()
    
    async def goto(self, page: 'Page', url: str, wait_until: str = 'networkidle') -> bool:
        """Navigate to URL with retry logic"""
        for attempt in range(self.config.max_retry_attempts):
            try:
                # Add random delay before navigation
                await self._human_sim.random_delay(self.config)
                
                # Navigate
                response = await page.goto(
                    url,
                    wait_until=wait_until,
                    timeout=self.config.timeout
                )
                
                # Check response
                if response and response.status < 400:
                    self.logger.info(f"Successfully navigated to {url}")
                    
                    # Random actions after page load
                    await self._human_sim.human_scroll(page, self.config)
                    await self._human_sim.random_delay(self.config)
                    
                    return True
                
            except Exception as e:
                self.logger.warning(f"Navigation attempt {attempt + 1} failed: {e}")
                
                if attempt < self.config.max_retry_attempts - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return False
    
    async def extract_elements(self, page: 'Page') -> List[ExtractedElement]:
        """Extract elements from the page"""
        elements = []
        
        try:
            # Get all interactive elements
            selectors = [
                'button', 'a', 'input', 'select', 'textarea',
                '[role="button"]', '[role="link"]', '[onclick]'
            ]
            
            for selector in selectors:
                found_elements = await page.query_selector_all(selector)
                
                for element in found_elements:
                    try:
                        # Extract element data
                        extracted = await self._extract_element_data(element, page)
                        if extracted:
                            elements.append(extracted)
                    except Exception as e:
                        self.logger.debug(f"Error extracting element: {e}")
            
            self.logger.info(f"Extracted {len(elements)} elements")
            
        except Exception as e:
            self.logger.error(f"Error during element extraction: {e}")
        
        return elements
    
    async def _extract_element_data(self, element: 'ElementHandle', page: 'Page') -> Optional[ExtractedElement]:
        """Extract data from a single element"""
        try:
            # Get basic properties
            tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
            
            # Get attributes
            attributes = await element.evaluate("""
                el => {
                    const attrs = {};
                    for (const attr of el.attributes) {
                        attrs[attr.name] = attr.value;
                    }
                    return attrs;
                }
            """)
            
            # Get text content
            text_content = await element.evaluate('el => el.textContent || ""')
            text_content = text_content.strip()
            
            # Get position
            box = await element.bounding_box()
            
            # Determine element type
            element_type = self._determine_element_type(tag_name, attributes)
            
            # Create extracted element
            return ExtractedElement(
                tag_name=tag_name,
                element_type=element_type,
                xpath=await self._get_xpath(element),
                css_selector=await self._get_css_selector(element),
                text_content=text_content,
                id=attributes.get('id'),
                class_names=attributes.get('class', '').split(),
                name=attributes.get('name'),
                href=attributes.get('href'),
                is_clickable=await self._is_clickable(element),
                is_visible=await element.is_visible(),
                is_enabled=await element.is_enabled(),
                role=attributes.get('role'),
                aria_label=attributes.get('aria-label'),
                placeholder=attributes.get('placeholder'),
                value=attributes.get('value'),
                input_type=attributes.get('type'),
                interaction_type=self._determine_interaction_type(element_type),
                bounds=box if box else None
            )
            
        except Exception as e:
            self.logger.debug(f"Error extracting element data: {e}")
            return None
    
    def _determine_element_type(self, tag_name: str, attributes: Dict[str, str]) -> ElementType:
        """Determine the element type"""
        if tag_name == 'button' or attributes.get('role') == 'button':
            return ElementType.BUTTON
        elif tag_name == 'input':
            input_type = attributes.get('type', 'text')
            if input_type == 'checkbox':
                return ElementType.CHECKBOX
            elif input_type == 'radio':
                return ElementType.RADIO
            else:
                return ElementType.INPUT
        elif tag_name == 'a':
            return ElementType.LINK
        elif tag_name == 'select':
            return ElementType.SELECT
        elif tag_name == 'textarea':
            return ElementType.TEXTAREA
        elif tag_name == 'form':
            return ElementType.FORM
        elif tag_name == 'table':
            return ElementType.TABLE
        elif tag_name == 'img':
            return ElementType.IMAGE
        elif tag_name in ['ul', 'ol']:
            return ElementType.LIST
        elif tag_name == 'nav' or attributes.get('role') == 'navigation':
            return ElementType.NAVIGATION
        else:
            return ElementType.UNKNOWN
    
    def _determine_interaction_type(self, element_type: ElementType) -> InteractionType:
        """Determine the interaction type for an element"""
        if element_type in [ElementType.BUTTON, ElementType.LINK]:
            return InteractionType.CLICK
        elif element_type in [ElementType.INPUT, ElementType.TEXTAREA]:
            return InteractionType.TYPE
        elif element_type == ElementType.SELECT:
            return InteractionType.SELECT
        elif element_type == ElementType.CHECKBOX:
            return InteractionType.CHECK
        else:
            return InteractionType.CLICK
    
    async def _get_xpath(self, element: 'ElementHandle') -> str:
        """Get XPath for element"""
        try:
            return await element.evaluate("""
                el => {
                    const getXPath = (node) => {
                        if (node.id) return `//*[@id="${node.id}"]`;
                        if (node === document.body) return '/html/body';
                        
                        let position = 0;
                        let sibling = node;
                        while (sibling) {
                            if (sibling.nodeType === 1 && sibling.tagName === node.tagName) {
                                position++;
                            }
                            sibling = sibling.previousSibling;
                        }
                        
                        const parentPath = getXPath(node.parentNode);
                        return `${parentPath}/${node.tagName.toLowerCase()}[${position}]`;
                    };
                    return getXPath(el);
                }
            """)
        except:
            return ""
    
    async def _get_css_selector(self, element: 'ElementHandle') -> str:
        """Get CSS selector for element"""
        try:
            return await element.evaluate("""
                el => {
                    if (el.id) return `#${el.id}`;
                    if (el.className) return `.${el.className.split(' ').join('.')}`;
                    return el.tagName.toLowerCase();
                }
            """)
        except:
            return ""
    
    async def _is_clickable(self, element: 'ElementHandle') -> bool:
        """Check if element is clickable"""
        try:
            return await element.evaluate("""
                el => {
                    const tag = el.tagName.toLowerCase();
                    return tag === 'button' || tag === 'a' || 
                           el.onclick !== null || 
                           el.getAttribute('role') === 'button' ||
                           window.getComputedStyle(el).cursor === 'pointer';
                }
            """)
        except:
            return False
    
    # Human-like interaction methods
    async def click(self, page: 'Page', selector: str):
        """Click element with human-like behavior"""
        await self._human_sim.human_click(page, selector, self.config)
    
    async def type(self, page: 'Page', selector: str, text: str):
        """Type text with human-like behavior"""
        await self._human_sim.human_type(page, selector, text, self.config)
    
    async def scroll(self, page: 'Page'):
        """Scroll page with human-like behavior"""
        await self._human_sim.human_scroll(page, self.config)


# ============================================================================
# SELF-TEST AND EXAMPLE USAGE
# ============================================================================

async def run_self_test():
    """Run comprehensive self-test of stealth browser"""
    logger = Logger.get_logger("StealthBrowserTest")
    logger.info("[TEST] Starting stealth browser self-test")
    
    if not HAS_PLAYWRIGHT:
        logger.error("[TEST] Playwright not installed - skipping browser tests")
        logger.info("[TEST] Install with: pip install playwright && playwright install chromium")
        return False
    
    results = {
        "initialization": False,
        "navigation": False,
        "element_extraction": False,
        "stealth_features": False
    }
    
    browser = None
    
    try:
        # Test initialization
        logger.info("[TEST] Testing browser initialization...")
        config = StealthConfig(
            level=StealthLevel.MAXIMUM,
            headless=True  # Use headless for testing
        )
        browser = StealthBrowser(config)
        await browser.initialize()
        await browser.start()
        results["initialization"] = True
        
        # Test navigation
        logger.info("[TEST] Testing navigation...")
        async with browser.new_page() as page:
            success = await browser.goto(page, "https://example.com")
            assert success
            results["navigation"] = True
            
            # Test element extraction
            logger.info("[TEST] Testing element extraction...")
            elements = await browser.extract_elements(page)
            assert len(elements) > 0
            logger.info(f"  Extracted {len(elements)} elements")
            results["element_extraction"] = True
            
            # Test stealth features
            logger.info("[TEST] Testing stealth features...")
            webdriver_hidden = await page.evaluate("() => navigator.webdriver === undefined")
            assert webdriver_hidden
            results["stealth_features"] = True
        
    except Exception as e:
        logger.error(f"[TEST] Self-test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    finally:
        if browser:
            await browser.stop()
    
    # Report results
    logger.info("[TEST] Self-test Results:")
    all_passed = True
    for component, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        logger.info(f"  {status} {component}")
        if not passed:
            all_passed = False
    
    if all_passed:
        logger.info("[TEST] All tests passed successfully!")
    else:
        logger.error("[TEST] Some tests failed!")
    
    return all_passed


def run_demo():
    """Run demo of stealth browser capabilities"""
    print("=" * 60)
    print("UI TESTING AUTOMATION - STEALTH BROWSER DEMO")
    print("=" * 60)
    
    if not HAS_PLAYWRIGHT:
        print("\n[ERROR] Playwright is not installed!")
        print("Install with:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return
    
    async def demo():
        # Create browser with maximum stealth
        config = StealthConfig(
            level=StealthLevel.MAXIMUM,
            headless=False,  # Show browser for demo
            enable_human_typing=True,
            enable_human_mouse=True
        )
        
        browser = StealthBrowser(config)
        
        try:
            print("\n[INFO] Starting stealth browser...")
            await browser.initialize()
            await browser.start()
            
            print("[INFO] Creating new page...")
            async with browser.new_page("https://example.com") as page:
                print("[INFO] Navigated to example.com")
                
                print("[INFO] Extracting elements...")
                elements = await browser.extract_elements(page)
                
                print(f"\n[RESULTS] Found {len(elements)} elements:")
                for i, elem in enumerate(elements[:5]):  # Show first 5
                    print(f"  {i+1}. {elem.element_type.value}: {elem.text_content[:50] if elem.text_content else 'No text'}")
                
                print("\n[INFO] Stealth features active:")
                print(f"  - Level: {config.level.value}")
                print(f"  - WebDriver hidden: {await page.evaluate('() => navigator.webdriver === undefined')}")
                print(f"  - Chrome runtime: {await page.evaluate('() => window.chrome !== undefined')}")
                
        finally:
            print("\n[INFO] Closing browser...")
            await browser.stop()
    
    # Run the demo
    AsyncioConfig.run_async(demo())


if __name__ == "__main__":
    # Quick test mode for compliance checking
    import os
    if os.environ.get("STANDALONE_TEST") == "1":
        print(f"[OK] {__name__} module loads successfully")
        sys.exit(0)
    
    print("=" * 60)
    print("UI TESTING AUTOMATION FRAMEWORK - STEALTH BROWSER MODULE")
    print("=" * 60)
    
    # Run self-test
    success = AsyncioConfig.run_async(run_self_test())
    
    # Skip demo to avoid resource conflicts after test
    # Demo can be run separately if needed
    if False and success and HAS_PLAYWRIGHT:
        print("\n" + "=" * 60)
        print("Running demo...")
        print("=" * 60)
        run_demo()
    
    print("\n" + "=" * 60)
    if success:
        print("[SUCCESS] Stealth browser module is ready for use!")
    else:
        print("[WARNING] Some tests failed - review logs above")
    print("=" * 60)