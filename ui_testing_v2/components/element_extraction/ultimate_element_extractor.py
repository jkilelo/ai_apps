#!/usr/bin/env python3
"""
Ultimate Element Extractor - Consolidated implementation of all extraction features.
Combines enhanced_stealth_extractor, optimized_extractor_v2, unified_extractor, 
and element_extraction_component into a single, powerful Playwright-only extractor.

Author: UI Testing Framework Team
Version: 1.0.0
Python: 3.10+
Dependencies: playwright>=1.40, numpy>=1.24
"""

import asyncio
import hashlib
import json
import logging
import random
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from urllib.parse import urlparse

import numpy as np
from playwright.async_api import (
    Browser,
    BrowserContext,
    Error as PlaywrightError,
    Page,
    async_playwright
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# FOUNDATION LAYER - Configuration and Data Models
# ============================================================================

@dataclass
class ExtractionConfig:
    """Unified configuration for element extraction."""
    # Core settings
    max_elements: int = 50
    timeout: int = 60
    headless: bool = False  # False for better stealth
    
    # Stealth settings
    enable_stealth: bool = True
    enable_human_simulation: bool = True
    enable_context_recovery: bool = True
    enable_runtime_bypass: bool = True
    enable_session_warming: bool = False
    
    # Strategy settings
    parallel_strategies: bool = True
    confidence_threshold: float = 0.5
    extract_shadow_dom: bool = True
    extract_aria: bool = True
    
    # Advanced features
    bypass_f5_networks: bool = True
    block_tracking_scripts: bool = True
    use_mobile_fallback: bool = True
    max_retry_attempts: int = 3
    
    # Human simulation
    human_delay_range: Tuple[int, int] = (100, 2000)
    scroll_behavior: bool = True
    mouse_movement: bool = True
    
    # Browser settings
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: Optional[str] = None
    locale: str = 'en-US'
    timezone: str = 'America/New_York'

@dataclass
class ElementData:
    """Comprehensive element data with 30+ attributes."""
    # Core identification
    tag_name: str
    element_type: str
    xpath: str
    css_selector: str
    
    # Content
    text_content: str = ""
    inner_html: str = ""
    outer_html: str = ""
    
    # Attributes
    id: Optional[str] = None
    class_names: List[str] = field(default_factory=list)
    name: Optional[str] = None
    href: Optional[str] = None
    src: Optional[str] = None
    alt: Optional[str] = None
    title: Optional[str] = None
    
    # State
    is_clickable: bool = False
    is_visible: bool = False
    is_enabled: bool = True
    is_focusable: bool = False
    is_checked: Optional[bool] = None
    is_selected: Optional[bool] = None
    
    # Position & Dimensions
    x: float = 0
    y: float = 0
    width: float = 0
    height: float = 0
    
    # Relationships
    parent_xpath: Optional[str] = None
    children_count: int = 0
    sibling_index: int = 0
    depth_in_dom: int = 0
    
    # ARIA & Accessibility
    role: Optional[str] = None
    aria_label: Optional[str] = None
    aria_description: Optional[str] = None
    aria_expanded: Optional[bool] = None
    aria_hidden: Optional[bool] = None
    tab_index: Optional[int] = None
    
    # Form specific
    input_type: Optional[str] = None
    placeholder: Optional[str] = None
    value: Optional[str] = None
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    pattern: Optional[str] = None
    required: Optional[bool] = None
    options: Optional[List[str]] = None
    
    # Metadata
    confidence_score: float = 1.0
    extraction_strategy: str = "unknown"
    extraction_timestamp: datetime = field(default_factory=datetime.now)
    interaction_type: str = "unknown"  # click, type, select, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'tag_name': self.tag_name,
            'element_type': self.element_type,
            'xpath': self.xpath,
            'css_selector': self.css_selector,
            'text_content': self.text_content,
            'id': self.id,
            'class_names': self.class_names,
            'href': self.href,
            'is_visible': self.is_visible,
            'is_clickable': self.is_clickable,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'role': self.role,
            'aria_label': self.aria_label,
            'confidence_score': self.confidence_score,
            'extraction_strategy': self.extraction_strategy,
            'interaction_type': self.interaction_type
        }

# ============================================================================
# BROWSER MANAGEMENT LAYER
# ============================================================================

class BrowserManager:
    """Manages browser lifecycle and configuration."""
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.playwright = None
    
    async def create_browser(self) -> Browser:
        """Create browser instance with stealth settings."""
        browser_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-site-isolation-trials',
            '--disable-web-security',
            '--disable-features=CrossSiteDocumentBlockingIfIsolating',
            '--disable-features=CrossSiteDocumentBlockingAlways',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu',
            f'--window-size={self.config.viewport_width},{self.config.viewport_height}',
            '--start-maximized',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection'
        ]
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.config.headless,
            args=browser_args
        )
        return self.browser
    
    async def create_context(self, browser: Browser) -> BrowserContext:
        """Create browser context with stealth configuration."""
        # Rotating user agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        user_agent = self.config.user_agent or random.choice(user_agents)
        
        self.context = await browser.new_context(
            viewport={
                'width': self.config.viewport_width,
                'height': self.config.viewport_height
            },
            user_agent=user_agent,
            locale=self.config.locale,
            timezone_id=self.config.timezone,
            permissions=['geolocation', 'notifications'],
            color_scheme='light',
            device_scale_factor=1.0 + random.random() * 0.5,
            has_touch=False,
            java_script_enabled=True,
            bypass_csp=True,
            ignore_https_errors=True,
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Cache-Control': 'max-age=0'
            }
        )
        return self.context
    
    async def cleanup(self):
        """Clean up browser resources."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

class NavigationHandler:
    """Handles complex navigation scenarios."""
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        self.navigation_count = 0
        self.final_url = None
    
    async def navigate_with_stability(self, page: Page, url: str) -> bool:
        """Navigate with context stability monitoring and redirect handling."""
        
        # Track navigation events
        def track_navigation(frame):
            if frame == page.main_frame:
                self.navigation_count += 1
                self.final_url = frame.url
                logger.debug(f"Navigation #{self.navigation_count} to: {self.final_url}")
        
        page.on('framenavigated', track_navigation)
        
        try:
            # Enhanced navigation strategies
            strategies = [
                ('commit', 30000),      # Fast commit with longer timeout
                ('domcontentloaded', 45000),  # Standard load
                ('load', 60000),        # Full load with max timeout
                ('networkidle', 30000)  # Network idle as last resort
            ]
            
            for strategy, timeout in strategies:
                try:
                    logger.debug(f"Attempting navigation with strategy: {strategy}")
                    
                    # Reset navigation tracking
                    self.navigation_count = 0
                    self.final_url = None
                    
                    # Navigate with specific strategy
                    await page.goto(url, wait_until=strategy, timeout=timeout)
                    
                    # Wait for potential redirects to settle
                    await asyncio.sleep(2)
                    
                    # Check if we have too many redirects (possible loop)
                    if self.navigation_count > 5:
                        logger.warning(f"Too many redirects ({self.navigation_count}), skipping strategy")
                        continue
                    
                    # Success
                    if self.final_url and url not in self.final_url:
                        logger.info(f"Navigation succeeded with redirect: {url} -> {self.final_url}")
                    else:
                        logger.info(f"Navigation succeeded: {url}")
                    
                    return True
                    
                except PlaywrightError as e:
                    error_msg = str(e).lower()
                    if 'context' in error_msg or 'destroyed' in error_msg:
                        logger.warning(f"Context destroyed with strategy {strategy}")
                        break  # Don't try other strategies if context is destroyed
                    elif 'timeout' in error_msg:
                        logger.debug(f"Timeout with {strategy}: {e}")
                    else:
                        logger.debug(f"Navigation failed with {strategy}: {e}")
            
            return False
            
        finally:
            # Remove navigation tracking
            page.remove_listener('framenavigated', track_navigation)

# ============================================================================
# STEALTH LAYER
# ============================================================================

class HumanSimulator:
    """Simulates realistic human behavior patterns."""
    
    @staticmethod
    def get_human_delay() -> int:
        """Generate realistic human delays using log-normal distribution."""
        delay = np.random.lognormal(mean=3.5, sigma=0.5)
        return int(max(100, min(2000, delay * 100)))
    
    @staticmethod
    async def human_mouse_movement(page: Page):
        """Simulate realistic mouse movements with bezier curves."""
        try:
            viewport = page.viewport_size
            if not viewport:
                return
            
            # Generate bezier curve points
            num_points = random.randint(3, 7)
            for _ in range(num_points):
                x = random.randint(0, viewport['width'])
                y = random.randint(0, viewport['height'])
                steps = random.randint(5, 15)
                await page.mouse.move(x, y, steps=steps)
                await page.wait_for_timeout(random.randint(50, 150))
                
        except Exception as e:
            logger.debug(f"Mouse movement simulation failed: {e}")
    
    @staticmethod
    async def human_scroll(page: Page):
        """Simulate human scrolling patterns."""
        try:
            # Variable scroll distance
            scroll_distance = random.randint(100, 500)
            
            # Smooth scroll
            await page.evaluate(f'''
                window.scrollBy({{
                    top: {scroll_distance},
                    behavior: 'smooth'
                }});
            ''')
            
            # Random pause after scroll
            await page.wait_for_timeout(random.randint(500, 1500))
            
        except Exception as e:
            logger.debug(f"Scroll simulation failed: {e}")
    
    @staticmethod
    async def add_micro_behaviors(page: Page):
        """Add subtle human micro-behaviors."""
        try:
            # Random viewport adjustments (10% chance)
            if random.random() < 0.1:
                viewport = page.viewport_size
                if viewport:
                    width = viewport['width'] + random.randint(-50, 50)
                    height = viewport['height'] + random.randint(-25, 25)
                    await page.set_viewport_size({'width': width, 'height': height})
            
            # Random focus changes (20% chance)
            if random.random() < 0.2:
                await page.evaluate('document.body && document.body.focus()')
                await page.wait_for_timeout(random.randint(100, 300))
                await page.evaluate('document.body && document.body.blur()')
            
            # Simulate reading time
            await page.wait_for_timeout(random.randint(1000, 3000))
            
        except Exception as e:
            logger.debug(f"Micro-behavior simulation failed: {e}")
    
    @staticmethod
    async def human_typing(page: Page, selector: str, text: str):
        """Type text with human-like delays."""
        try:
            await page.click(selector)
            
            for char in text:
                await page.type(selector, char)
                # Variable typing speed
                delay = random.randint(50, 250)
                await page.wait_for_timeout(delay)
                
        except Exception as e:
            logger.debug(f"Human typing simulation failed: {e}")

class ContextStabilityMonitor:
    """Monitors and maintains page context stability."""
    
    def __init__(self, page: Page):
        self.page = page
        self.context_stable = True
        self.context_destroyed_count = 0
        self.last_check = time.time()
    
    async def start_monitoring(self):
        """Start monitoring context stability."""
        try:
            # Add crash listener
            self.page.on('crash', self._on_context_destroyed)
            
            # Monitor for navigation that destroys context
            self.page.on('framenavigated', self._on_navigation)
            
            # Periodic stability check
            asyncio.create_task(self._periodic_check())
            
        except Exception as e:
            logger.error(f"Failed to start context monitoring: {e}")
    
    def _on_context_destroyed(self):
        """Handle context destruction event."""
        self.context_stable = False
        self.context_destroyed_count += 1
        logger.warning("Context destroyed detected")
    
    def _on_navigation(self, frame):
        """Monitor navigation events."""
        if frame == self.page.main_frame:
            logger.debug("Main frame navigation detected")
    
    async def _periodic_check(self):
        """Periodically check context stability."""
        while self.context_stable:
            try:
                # Try to execute simple JavaScript
                await self.page.evaluate('1 + 1')
                self.last_check = time.time()
            except:
                self.context_stable = False
                logger.warning("Context stability check failed")
                break
            
            await asyncio.sleep(1)
    
    def is_stable(self) -> bool:
        """Check if context is stable."""
        return self.context_stable and (time.time() - self.last_check < 5)

class StealthInjector:
    """Injects stealth scripts to bypass detection."""
    
    @staticmethod
    async def inject_advanced_stealth(page: Page):
        """Inject comprehensive stealth scripts before navigation."""
        
        stealth_script = """
        () => {
            // Advanced Function.prototype.toString override
            const nativeToString = Function.prototype.toString;
            Function.prototype.toString = new Proxy(nativeToString, {
                apply(target, thisArg, args) {
                    // Spoof native functions
                    if (thisArg === window.navigator.permissions.query) {
                        return 'function query() { [native code] }';
                    }
                    if (thisArg === window.navigator.getBattery) {
                        return 'function getBattery() { [native code] }';
                    }
                    return target.apply(thisArg, args);
                }
            });
            
            // Advanced timing attack prevention
            const originalDate = Date;
            let lastTime = originalDate.now();
            window.Date = new Proxy(originalDate, {
                construct(target, args) {
                    // Add micro-delays to prevent timing fingerprinting
                    const now = originalDate.now();
                    if (now - lastTime < 10) {
                        const delay = Math.random() * 5;
                        const start = performance.now();
                        while (performance.now() - start < delay) {}
                    }
                    lastTime = now;
                    return new target(...args);
                }
            });
            
            // Deep WebDriver property removal
            const cleanObject = (obj, prop) => {
                try {
                    if (obj && obj[prop] !== undefined) {
                        delete obj[prop];
                    }
                    if (obj && obj.__proto__ && obj.__proto__[prop] !== undefined) {
                        delete obj.__proto__[prop];
                    }
                    if (obj && obj.__proto__.__proto__ && obj.__proto__.__proto__[prop] !== undefined) {
                        delete obj.__proto__.__proto__[prop];
                    }
                } catch (e) {}
            };
            
            cleanObject(window.navigator, 'webdriver');
            cleanObject(document, '__webdriver_evaluate');
            cleanObject(document, '__selenium_evaluate');
            cleanObject(document, '__webdriver_script_function');
            
            // Override CDP detection
            if (window.chrome) {
                window.chrome.runtime = new Proxy(window.chrome.runtime || {}, {
                    get(target, prop) {
                        if (prop === 'id') return undefined;
                        if (prop === 'onMessage') return undefined;
                        return target[prop];
                    }
                });
            }
            
            // Add realistic performance entries
            if (window.performance && window.performance.getEntries) {
                const originalGetEntries = window.performance.getEntries;
                window.performance.getEntries = function() {
                    const entries = originalGetEntries.call(this);
                    
                    // Add fake navigation history
                    if (entries.length < 5) {
                        entries.push({
                            name: 'https://www.google.com',
                            entryType: 'navigation',
                            startTime: Date.now() - 600000,
                            duration: 2345
                        });
                        entries.push({
                            name: 'https://www.yahoo.com',
                            entryType: 'navigation',
                            startTime: Date.now() - 300000,
                            duration: 1876
                        });
                    }
                    return entries;
                };
            }
            
            // Override automation detection in Error stack
            const originalError = Error;
            Error = new Proxy(originalError, {
                construct(target, args) {
                    const error = new target(...args);
                    const stack = error.stack;
                    if (stack) {
                        error.stack = stack
                            .replace(/selenium/gi, 'element')
                            .replace(/webdriver/gi, 'webrunner')
                            .replace(/puppet/gi, 'pet');
                    }
                    return error;
                }
            });
            
            // Add realistic window properties
            window.devicePixelRatio = 1.0 + (Math.random() * 0.5);
            window.outerWidth = window.innerWidth + Math.floor(Math.random() * 100);
            window.outerHeight = window.innerHeight + Math.floor(Math.random() * 100);
            
            // Override Notification permissions
            if (window.Notification) {
                const originalPermission = window.Notification.permission;
                Object.defineProperty(window.Notification, 'permission', {
                    get: () => 'default'
                });
            }
            
            // Add battery API
            if (!navigator.getBattery) {
                navigator.getBattery = () => Promise.resolve({
                    charging: Math.random() > 0.5,
                    chargingTime: Math.random() > 0.5 ? 0 : Infinity,
                    dischargingTime: Math.random() * 10000,
                    level: 0.5 + Math.random() * 0.5,
                    onchargingchange: null,
                    onchargingtimechange: null,
                    ondischargingtimechange: null,
                    onlevelchange: null
                });
            }
            
            // Add MediaDevices if missing
            if (!navigator.mediaDevices) {
                navigator.mediaDevices = {
                    enumerateDevices: () => Promise.resolve([
                        {deviceId: "default", kind: "audioinput", label: "Microphone", groupId: "audio"},
                        {deviceId: "communications", kind: "audioinput", label: "Communications", groupId: "audio"},
                        {deviceId: "default", kind: "videoinput", label: "Camera", groupId: "video"}
                    ])
                };
            }
            
            // Override permissions.query
            const originalQuery = navigator.permissions.query;
            navigator.permissions.query = function(parameters) {
                if (parameters.name === 'notifications' || parameters.name === 'push') {
                    return Promise.resolve({state: 'prompt'});
                }
                return originalQuery.apply(this, arguments);
            };
            
            // Add touch support indicators (but not actual touch)
            window.ontouchstart = null;
            window.DocumentTouch = Document;
            
            // Override WebGL vendor and renderer
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                if (parameter === 7936) {
                    return 'WebKit';
                }
                if (parameter === 7937) {
                    return 'WebKit WebGL';
                }
                return getParameter.call(this, parameter);
            };
            
            // Add realistic plugins with detailed mimeTypes
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    return [
                        {
                            0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                            description: "Portable Document Format",
                            filename: "internal-pdf-viewer",
                            length: 1,
                            name: "Chrome PDF Plugin"
                        },
                        {
                            0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
                            description: "Portable Document Format",
                            filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                            length: 1,
                            name: "Chrome PDF Viewer"
                        },
                        {
                            0: {type: "application/x-nacl", suffixes: "", description: "Native Client Executable"},
                            1: {type: "application/x-pnacl", suffixes: "", description: "Portable Native Client Executable"},
                            description: "Native Client",
                            filename: "internal-nacl-plugin",
                            length: 2,
                            name: "Native Client"
                        }
                    ];
                }
            });
        }
        """
        
        try:
            await page.add_init_script(stealth_script)
            logger.debug("Advanced stealth scripts injected")
        except Exception as e:
            logger.error(f"Failed to inject stealth scripts: {e}")

class RuntimeBypassManager:
    """Manages runtime protection bypass."""
    
    @staticmethod
    async def setup_enhanced_runtime_bypass(page: Page):
        """Enhanced runtime protection bypass with tracking script blocking."""
        
        try:
            # Comprehensive script blocking and modification
            async def handle_request(route):
                url = route.request.url.lower()
                
                # Block or modify problematic scripts
                blocking_patterns = [
                    # Anti-bot and shape security
                    'shape', 'f5-', 'antibot', 'challenge', 'botguard',
                    # Tracking and analytics that interfere
                    'adobe', 'dtm', 'ensighten', 'tealium', 'segment',
                    # Known bot detection
                    'perimeterx', 'datadome', 'imperva', 'cloudflare',
                    # Specific problematic domains
                    'nexus.ensighten.com', 'assets.adobedtm.com'
                ]
                
                should_block = any(pattern in url for pattern in blocking_patterns)
                
                if should_block:
                    logger.debug(f"Blocking problematic script: {url}")
                    # Return empty script instead of blocking completely
                    await route.fulfill(
                        content_type='application/javascript',
                        body='// Script blocked by stealth browser'
                    )
                else:
                    # Allow other requests
                    await route.continue_()
            
            # Intercept all script requests
            await page.route('**/*.js', handle_request)
            
            # Also block specific problematic resource types
            async def enhanced_request_filter(route):
                url = route.request.url.lower()
                
                # Block specific tracking and analytics
                tracking_domains = [
                    'google-analytics.com',
                    'googletagmanager.com',
                    'doubleclick.net',
                    'facebook.com/tr',
                    'hotjar.com',
                    'fullstory.com',
                    'logrocket.com',
                    'bugsnag.com'
                ]
                
                # Block if it's a tracking domain
                if any(domain in url for domain in tracking_domains):
                    logger.debug(f"Blocking tracking request: {url}")
                    await route.abort()
                    return
                
                # Continue with normal request
                await route.continue_()
            
            await page.route('**/*', enhanced_request_filter)
            
        except Exception as e:
            logger.error(f"Failed to setup enhanced runtime bypass: {e}")

# ============================================================================
# STRATEGY LAYER - Extraction Strategies  
# ============================================================================

class ExtractionStrategy(ABC):
    """Abstract base class for extraction strategies."""
    
    @abstractmethod
    async def extract(self, page: Page) -> List[ElementData]:
        """Extract elements using specific strategy."""
        pass
    
    @abstractmethod
    def can_handle(self, page: Page) -> bool:
        """Check if strategy can handle current page."""
        pass

class DOMExtractionStrategy(ExtractionStrategy):
    """DOM-based element extraction strategy."""
    
    async def extract(self, page: Page) -> List[ElementData]:
        """Extract elements using DOM traversal."""
        elements = []
        
        try:
            # Comprehensive JavaScript extraction script
            dom_elements = await page.evaluate("""
                () => {
                    const elements = [];
                    const selectors = [
                        'a', 'button', 'input', 'select', 'textarea', 'form',
                        '[role="button"]', '[role="link"]', '[tabindex="0"]',
                        '.btn', '.button', '.link', '[onclick]'
                    ];
                    
                    const allElements = document.querySelectorAll(selectors.join(', '));
                    
                    allElements.forEach((el, index) => {
                        if (index >= 50) return;
                        
                        try {
                            const rect = el.getBoundingClientRect();
                            const computedStyle = window.getComputedStyle(el);
                            
                            // Get parent information
                            const parent = el.parentElement;
                            const parentTag = parent ? parent.tagName.toLowerCase() : null;
                            
                            // Get sibling index
                            let siblingIndex = 0;
                            if (parent) {
                                const siblings = Array.from(parent.children);
                                siblingIndex = siblings.indexOf(el);
                            }
                            
                            // Calculate depth in DOM
                            let depth = 0;
                            let current = el;
                            while (current.parentElement) {
                                depth++;
                                current = current.parentElement;
                            }
                            
                            elements.push({
                                tagName: el.tagName.toLowerCase(),
                                id: el.id || null,
                                className: el.className || '',
                                textContent: (el.textContent || '').substring(0, 100).trim(),
                                innerHTML: (el.innerHTML || '').substring(0, 200),
                                href: el.href || null,
                                src: el.src || null,
                                alt: el.alt || null,
                                title: el.title || null,
                                type: el.type || el.tagName.toLowerCase(),
                                name: el.name || null,
                                placeholder: el.placeholder || null,
                                value: el.value || null,
                                min: el.min || null,
                                max: el.max || null,
                                pattern: el.pattern || null,
                                required: el.required || null,
                                checked: el.checked || null,
                                selected: el.selected || null,
                                disabled: el.disabled || false,
                                readonly: el.readonly || false,
                                isVisible: rect.width > 0 && rect.height > 0 &&
                                          computedStyle.visibility !== 'hidden' &&
                                          computedStyle.display !== 'none',
                                isClickable: el.onclick !== null || 
                                           el.tagName === 'BUTTON' || 
                                           el.tagName === 'A' ||
                                           el.role === 'button' ||
                                           el.role === 'link',
                                x: Math.round(rect.x),
                                y: Math.round(rect.y),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height),
                                role: el.getAttribute('role'),
                                ariaLabel: el.getAttribute('aria-label'),
                                ariaDescription: el.getAttribute('aria-describedby'),
                                ariaExpanded: el.getAttribute('aria-expanded'),
                                ariaHidden: el.getAttribute('aria-hidden'),
                                tabIndex: el.tabIndex,
                                parentTag: parentTag,
                                childrenCount: el.children.length,
                                siblingIndex: siblingIndex,
                                depth: depth
                            });
                        } catch (e) {
                            console.warn('Error processing element:', e);
                        }
                    });
                    
                    return elements;
                }
            """)
            
            # Convert to ElementData objects
            for elem_data in dom_elements:
                element = ElementData(
                    tag_name=elem_data['tagName'],
                    element_type=elem_data['type'],
                    xpath=self._generate_xpath(elem_data),
                    css_selector=self._generate_css_selector(elem_data),
                    text_content=elem_data['textContent'],
                    inner_html=elem_data['innerHTML'],
                    id=elem_data['id'],
                    class_names=elem_data['className'].split() if elem_data['className'] else [],
                    name=elem_data['name'],
                    href=elem_data['href'],
                    src=elem_data['src'],
                    alt=elem_data['alt'],
                    title=elem_data['title'],
                    placeholder=elem_data['placeholder'],
                    value=elem_data['value'],
                    min_value=elem_data['min'],
                    max_value=elem_data['max'],
                    pattern=elem_data['pattern'],
                    required=elem_data['required'],
                    is_visible=elem_data['isVisible'],
                    is_clickable=elem_data['isClickable'],
                    is_enabled=not elem_data['disabled'],
                    is_checked=elem_data['checked'],
                    is_selected=elem_data['selected'],
                    x=elem_data['x'],
                    y=elem_data['y'],
                    width=elem_data['width'],
                    height=elem_data['height'],
                    parent_xpath=f"//{elem_data['parentTag']}" if elem_data['parentTag'] else None,
                    children_count=elem_data['childrenCount'],
                    sibling_index=elem_data['siblingIndex'],
                    depth_in_dom=elem_data['depth'],
                    role=elem_data['role'],
                    aria_label=elem_data['ariaLabel'],
                    aria_description=elem_data['ariaDescription'],
                    aria_expanded=elem_data['ariaExpanded'] == 'true' if elem_data['ariaExpanded'] else None,
                    aria_hidden=elem_data['ariaHidden'] == 'true' if elem_data['ariaHidden'] else None,
                    tab_index=elem_data['tabIndex'],
                    extraction_strategy='DOM',
                    confidence_score=0.9
                )
                elements.append(element)
                
        except Exception as e:
            logger.error(f"DOM extraction failed: {e}")
        
        return elements
    
    def _generate_xpath(self, elem_data: dict) -> str:
        """Generate XPath for element."""
        if elem_data['id']:
            return f"//{elem_data['tagName']}[@id='{elem_data['id']}']"
        elif elem_data['className']:
            classes = elem_data['className'].split()[0] if elem_data['className'] else ''
            return f"//{elem_data['tagName']}[@class='{classes}']"
        else:
            return f"//{elem_data['tagName']}"
    
    def _generate_css_selector(self, elem_data: dict) -> str:
        """Generate CSS selector for element."""
        if elem_data['id']:
            return f"#{elem_data['id']}"
        elif elem_data['className']:
            classes = '.'.join(elem_data['className'].split()[:2])
            return f"{elem_data['tagName']}.{classes}" if classes else elem_data['tagName']
        else:
            return elem_data['tagName']
    
    def can_handle(self, page: Page) -> bool:
        """DOM strategy can handle any page."""
        return True

class AccessibilityExtractionStrategy(ExtractionStrategy):
    """Accessibility-focused extraction strategy."""
    
    async def extract(self, page: Page) -> List[ElementData]:
        """Extract elements focusing on accessibility attributes."""
        elements = []
        
        try:
            # Extract elements with accessibility focus
            aria_elements = await page.evaluate("""
                () => {
                    const elements = [];
                    const ariaSelectors = [
                        '[aria-label]', '[aria-describedby]', '[aria-labelledby]',
                        '[role]', '[aria-expanded]', '[aria-hidden="false"]',
                        '[aria-controls]', '[aria-live]', '[aria-atomic]'
                    ];
                    
                    const processedElements = new Set();
                    
                    ariaSelectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach((el, index) => {
                            // Avoid duplicates
                            if (processedElements.has(el) || index >= 30) return;
                            processedElements.add(el);
                            
                            const rect = el.getBoundingClientRect();
                            const computedStyle = window.getComputedStyle(el);
                            
                            elements.push({
                                tagName: el.tagName.toLowerCase(),
                                id: el.id || null,
                                className: el.className || '',
                                role: el.getAttribute('role'),
                                ariaLabel: el.getAttribute('aria-label'),
                                ariaDescribedBy: el.getAttribute('aria-describedby'),
                                ariaLabelledBy: el.getAttribute('aria-labelledby'),
                                ariaExpanded: el.getAttribute('aria-expanded'),
                                ariaHidden: el.getAttribute('aria-hidden'),
                                ariaControls: el.getAttribute('aria-controls'),
                                ariaLive: el.getAttribute('aria-live'),
                                ariaAtomic: el.getAttribute('aria-atomic'),
                                tabIndex: el.tabIndex,
                                textContent: (el.textContent || '').substring(0, 100).trim(),
                                isVisible: rect.width > 0 && rect.height > 0 &&
                                          computedStyle.visibility !== 'hidden' &&
                                          computedStyle.display !== 'none',
                                isFocusable: el.tabIndex >= 0,
                                x: Math.round(rect.x),
                                y: Math.round(rect.y),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height)
                            });
                        });
                    });
                    
                    return elements;
                }
            """)
            
            # Convert to ElementData objects
            for elem_data in aria_elements:
                element = ElementData(
                    tag_name=elem_data['tagName'],
                    element_type=elem_data['tagName'],
                    xpath=f"//{elem_data['tagName']}[@aria-label='{elem_data['ariaLabel']}']" if elem_data['ariaLabel'] else f"//{elem_data['tagName']}",
                    css_selector=f"[aria-label='{elem_data['ariaLabel']}']" if elem_data['ariaLabel'] else elem_data['tagName'],
                    text_content=elem_data['textContent'],
                    id=elem_data['id'],
                    class_names=elem_data['className'].split() if elem_data['className'] else [],
                    role=elem_data['role'],
                    aria_label=elem_data['ariaLabel'],
                    aria_description=elem_data['ariaDescribedBy'],
                    aria_expanded=elem_data['ariaExpanded'] == 'true' if elem_data['ariaExpanded'] else None,
                    aria_hidden=elem_data['ariaHidden'] == 'true' if elem_data['ariaHidden'] else None,
                    tab_index=elem_data['tabIndex'],
                    is_visible=elem_data['isVisible'],
                    is_focusable=elem_data['isFocusable'],
                    x=elem_data['x'],
                    y=elem_data['y'],
                    width=elem_data['width'],
                    height=elem_data['height'],
                    extraction_strategy='Accessibility',
                    confidence_score=0.85
                )
                elements.append(element)
                
        except Exception as e:
            logger.error(f"Accessibility extraction failed: {e}")
        
        return elements
    
    def can_handle(self, page: Page) -> bool:
        """Can handle any page."""
        return True

class ShadowDOMExtractionStrategy(ExtractionStrategy):
    """Shadow DOM extraction strategy."""
    
    async def extract(self, page: Page) -> List[ElementData]:
        """Extract elements from shadow DOM."""
        elements = []
        
        try:
            shadow_elements = await page.evaluate("""
                () => {
                    const elements = [];
                    
                    function extractFromShadowRoot(root, depth = 0) {
                        if (depth > 5) return; // Limit recursion depth
                        
                        root.querySelectorAll('*').forEach(el => {
                            // Check if element has shadow root
                            if (el.shadowRoot) {
                                extractFromShadowRoot(el.shadowRoot, depth + 1);
                            }
                            
                            // Process element
                            const rect = el.getBoundingClientRect();
                            if (rect.width > 0 && rect.height > 0) {
                                elements.push({
                                    tagName: el.tagName.toLowerCase(),
                                    textContent: (el.textContent || '').substring(0, 100).trim(),
                                    inShadowDOM: true,
                                    depth: depth,
                                    x: Math.round(rect.x),
                                    y: Math.round(rect.y),
                                    width: Math.round(rect.width),
                                    height: Math.round(rect.height)
                                });
                            }
                        });
                    }
                    
                    // Find all elements with shadow roots
                    document.querySelectorAll('*').forEach(el => {
                        if (el.shadowRoot) {
                            extractFromShadowRoot(el.shadowRoot);
                        }
                    });
                    
                    return elements.slice(0, 20); // Limit results
                }
            """)
            
            # Convert to ElementData objects
            for elem_data in shadow_elements:
                element = ElementData(
                    tag_name=elem_data['tagName'],
                    element_type=elem_data['tagName'],
                    xpath=f"//{elem_data['tagName']}",
                    css_selector=elem_data['tagName'],
                    text_content=elem_data['textContent'],
                    x=elem_data['x'],
                    y=elem_data['y'],
                    width=elem_data['width'],
                    height=elem_data['height'],
                    depth_in_dom=elem_data['depth'],
                    extraction_strategy='ShadowDOM',
                    confidence_score=0.75
                )
                elements.append(element)
                
        except Exception as e:
            logger.debug(f"Shadow DOM extraction failed (may not exist): {e}")
        
        return elements
    
    def can_handle(self, page: Page) -> bool:
        """Check if page has shadow DOM elements."""
        try:
            # Quick check for shadow DOM
            return asyncio.run(page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('*')).some(el => el.shadowRoot);
                }
            """))
        except:
            return False

# ============================================================================
# ORCHESTRATION LAYER - Main Extractor
# ============================================================================

class UltimateElementExtractor:
    """Main extractor coordinating all operations."""
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        self.browser_manager = BrowserManager(config)
        self.navigation_handler = NavigationHandler(config)
        self.strategies = [
            DOMExtractionStrategy(),
            AccessibilityExtractionStrategy()
        ]
        
        # Add shadow DOM strategy if enabled
        if config.extract_shadow_dom:
            self.strategies.append(ShadowDOMExtractionStrategy())
    
    async def extract(self, url: str) -> List[ElementData]:
        """
        Main extraction method implementing Template Method pattern.
        
        Args:
            url: Target URL to extract elements from
            
        Returns:
            List of ElementData objects with comprehensive element information
        """
        browser = None
        try:
            # 1. Validate URL
            if not self._validate_url(url):
                raise ValueError(f"Invalid URL: {url}")
            
            # 2. Setup browser
            browser = await self._setup_browser()
            
            # 3. Create context and page
            context = await self.browser_manager.create_context(browser)
            page = await context.new_page()
            
            # 4. Apply stealth measures if enabled
            if self.config.enable_stealth:
                await self._apply_stealth_measures(page)
            
            # 5. Navigate to URL
            success = await self._navigate_to_url(page, url)
            if not success:
                logger.warning("Navigation failed, attempting recovery")
                # Try recovery
                page = await self._recover_navigation(browser, url)
                if not page:
                    raise Exception("Navigation failed after recovery attempts")
            
            # 6. Extract elements
            elements = await self._extract_elements(page)
            
            # 7. Post-process results
            elements = await self._post_process(elements)
            
            return elements
            
        except Exception as e:
            logger.error(f"Extraction failed for {url}: {e}")
            
            # Try mobile fallback if enabled
            if self.config.use_mobile_fallback:
                logger.info("Attempting mobile fallback...")
                return await self._extract_with_mobile_fallback(url)
            
            raise
            
        finally:
            # 8. Cleanup
            if browser:
                await self._cleanup()
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        if url.startswith('data:'):
            return True
        
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    
    async def _setup_browser(self) -> Browser:
        """Setup browser with stealth configuration."""
        return await self.browser_manager.create_browser()
    
    async def _apply_stealth_measures(self, page: Page):
        """Apply all stealth measures."""
        # Inject stealth scripts
        await StealthInjector.inject_advanced_stealth(page)
        
        # Setup runtime bypass
        if self.config.enable_runtime_bypass:
            await RuntimeBypassManager.setup_enhanced_runtime_bypass(page)
        
        # Human simulation
        if self.config.enable_human_simulation:
            await HumanSimulator.add_micro_behaviors(page)
            
            if self.config.scroll_behavior:
                await HumanSimulator.human_scroll(page)
            
            if self.config.mouse_movement:
                await HumanSimulator.human_mouse_movement(page)
    
    async def _navigate_to_url(self, page: Page, url: str) -> bool:
        """Navigate to URL with stability monitoring."""
        # Setup context monitoring
        if self.config.enable_context_recovery:
            monitor = ContextStabilityMonitor(page)
            await monitor.start_monitoring()
        
        # Navigate with enhanced handler
        success = await self.navigation_handler.navigate_with_stability(page, url)
        
        # Check stability if monitoring
        if self.config.enable_context_recovery and hasattr(self, 'monitor'):
            if not monitor.is_stable():
                logger.warning("Context unstable after navigation")
                return False
        
        return success
    
    async def _recover_navigation(self, browser: Browser, url: str) -> Optional[Page]:
        """Recover from navigation failure."""
        for attempt in range(self.config.max_retry_attempts):
            try:
                logger.info(f"Recovery attempt {attempt + 1}/{self.config.max_retry_attempts}")
                
                # Create new context
                context = await self.browser_manager.create_context(browser)
                page = await context.new_page()
                
                # Apply stealth
                if self.config.enable_stealth:
                    await self._apply_stealth_measures(page)
                
                # Try navigation
                success = await self._navigate_to_url(page, url)
                if success:
                    return page
                    
            except Exception as e:
                logger.error(f"Recovery attempt {attempt + 1} failed: {e}")
        
        return None
    
    async def _extract_elements(self, page: Page) -> List[ElementData]:
        """Execute extraction strategies."""
        if self.config.parallel_strategies:
            # Execute strategies in parallel
            tasks = [
                strategy.extract(page)
                for strategy in self.strategies
                if strategy.can_handle(page)
            ]
            
            if not tasks:
                logger.warning("No strategies can handle this page")
                return []
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Flatten results
            elements = []
            for result in results:
                if isinstance(result, list):
                    elements.extend(result)
                elif isinstance(result, Exception):
                    logger.warning(f"Strategy failed: {result}")
        else:
            # Execute strategies sequentially
            elements = []
            for strategy in self.strategies:
                if strategy.can_handle(page):
                    try:
                        strategy_elements = await strategy.extract(page)
                        elements.extend(strategy_elements)
                    except Exception as e:
                        logger.warning(f"Strategy {strategy.__class__.__name__} failed: {e}")
        
        return elements
    
    async def _post_process(self, elements: List[ElementData]) -> List[ElementData]:
        """Post-process extracted elements."""
        # Remove duplicates
        elements = self._deduplicate(elements)
        
        # Filter by confidence
        elements = [
            e for e in elements
            if e.confidence_score >= self.config.confidence_threshold
        ]
        
        # Sort by position (top to bottom, left to right)
        elements.sort(key=lambda e: (e.y, e.x))
        
        # Limit to max_elements
        if len(elements) > self.config.max_elements:
            elements = elements[:self.config.max_elements]
        
        # Enrich with interaction types
        for element in elements:
            element.interaction_type = self._determine_interaction_type(element)
        
        return elements
    
    def _deduplicate(self, elements: List[ElementData]) -> List[ElementData]:
        """Remove duplicate elements based on xpath and position."""
        seen = set()
        unique_elements = []
        
        for element in elements:
            # Create unique key based on xpath and position
            key = (element.xpath, element.x, element.y)
            if key not in seen:
                seen.add(key)
                unique_elements.append(element)
        
        return unique_elements
    
    def _determine_interaction_type(self, element: ElementData) -> str:
        """Determine the interaction type for an element."""
        if element.tag_name == 'input':
            if element.input_type in ['text', 'email', 'password', 'search', 'tel', 'url']:
                return 'type'
            elif element.input_type in ['checkbox', 'radio']:
                return 'check'
            elif element.input_type in ['submit', 'button', 'reset']:
                return 'click'
            elif element.input_type == 'file':
                return 'upload'
        elif element.tag_name == 'button':
            return 'click'
        elif element.tag_name == 'a':
            return 'click'
        elif element.tag_name == 'select':
            return 'select'
        elif element.tag_name == 'textarea':
            return 'type'
        elif element.role == 'button':
            return 'click'
        elif element.role == 'link':
            return 'click'
        elif element.role == 'textbox':
            return 'type'
        
        return 'unknown'
    
    async def _extract_with_mobile_fallback(self, url: str) -> List[ElementData]:
        """Fallback extraction using mobile viewport."""
        logger.info("Attempting mobile fallback extraction")
        
        # Create new config for mobile
        mobile_config = ExtractionConfig(
            viewport_width=375,
            viewport_height=812,
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            headless=self.config.headless,
            enable_stealth=self.config.enable_stealth,
            max_elements=self.config.max_elements,
            timeout=self.config.timeout
        )
        
        # Create new extractor with mobile config
        mobile_extractor = UltimateElementExtractor(mobile_config)
        
        try:
            return await mobile_extractor.extract(url)
        except Exception as e:
            logger.error(f"Mobile fallback failed: {e}")
            return []
    
    async def _cleanup(self):
        """Clean up browser resources."""
        try:
            await self.browser_manager.cleanup()
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

# ============================================================================
# PUBLIC API LAYER (Facade)
# ============================================================================

async def extract_elements(
    url: str,
    config: Optional[ExtractionConfig] = None
) -> List[ElementData]:
    """
    Extract elements from a web page with advanced stealth and extraction capabilities.
    
    This is the main entry point for element extraction, providing a simple interface
    to the complex extraction system.
    
    Args:
        url: The URL to extract elements from
        config: Optional extraction configuration. If not provided, uses defaults.
        
    Returns:
        A list of ElementData objects containing comprehensive element information
        
    Raises:
        ValueError: If the URL is invalid
        TimeoutError: If extraction exceeds the configured timeout
        PlaywrightError: If browser automation fails
        
    Example:
        >>> elements = await extract_elements("https://example.com")
        >>> for element in elements:
        ...     print(f"{element.tag_name}: {element.text_content}")
    """
    if config is None:
        config = ExtractionConfig()
    
    extractor = UltimateElementExtractor(config)
    return await extractor.extract(url)

# Backward compatibility (deprecated, will be removed)
extract_elements_for_test_generation = extract_elements

# ============================================================================
# CLI Interface (Optional)
# ============================================================================

if __name__ == "__main__":
    import sys
    
    async def main():
        if len(sys.argv) < 2:
            print("Usage: python ultimate_element_extractor.py <url>")
            sys.exit(1)
        
        url = sys.argv[1]
        
        # Configure for maximum stealth
        config = ExtractionConfig(
            enable_stealth=True,
            enable_human_simulation=True,
            bypass_f5_networks=True,
            parallel_strategies=True,
            headless=False  # Show browser for debugging
        )
        
        try:
            print(f"Extracting elements from {url}...")
            elements = await extract_elements(url, config)
            print(f"\n✅ Extracted {len(elements)} elements from {url}\n")
            
            # Print first 10 elements
            for i, element in enumerate(elements[:10], 1):
                print(f"{i}. {element.tag_name}")
                print(f"   Text: {element.text_content[:50]}")
                print(f"   Type: {element.interaction_type}")
                print(f"   XPath: {element.xpath}")
                print(f"   Visible: {element.is_visible}")
                print(f"   Position: ({element.x}, {element.y})")
                print(f"   Strategy: {element.extraction_strategy}")
                print()
                
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            sys.exit(1)
    
    asyncio.run(main())