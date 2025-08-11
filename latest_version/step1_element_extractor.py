#!/usr/bin/env python3
"""
Ultimate Element Extractor Final - Complete consolidated implementation.
Single file with all extraction and stealth features following CODER strategy.
"""

import asyncio
import json
import logging
import math
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
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
    """Complete configuration for element extraction with all features."""
    # Core settings
    max_elements: int = 50
    timeout: int = 60
    headless: bool = False  # False for better stealth
    
    # Stealth settings
    enable_stealth: bool = True
    enable_human_simulation: bool = True
    enable_context_recovery: bool = True
    enable_runtime_bypass: bool = True
    
    # Advanced stealth features
    enable_webrtc_protection: bool = True
    enable_canvas_protection: bool = True
    enable_webgl_spoofing: bool = True
    enable_hardware_spoofing: bool = True
    enable_chrome_runtime_complete: bool = True
    
    # Detection features
    enable_framework_detection: bool = True
    enable_captcha_detection: bool = True
    enable_cookie_handling: bool = True
    
    # Trust building
    enable_trust_building: bool = False  # Off by default for speed
    trust_visit_pages: int = 2
    trust_safe_domains: List[str] = field(default_factory=lambda: ['google.com', 'github.com'])
    
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
    typing_simulation: bool = True
    use_bspline_mouse: bool = True
    use_lognormal_delays: bool = True
    
    # Browser settings
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: Optional[str] = None
    locale: str = 'en-US'
    timezone: str = 'America/New_York'
    
    # Cookie consent selectors
    cookie_selectors: List[str] = field(default_factory=lambda: [
        'button[id*="accept"]', 'button[class*="accept"]',
        'button[class*="consent"]', 'button[class*="agree"]',
        'button:has-text("Accept")', 'button:has-text("OK")'
    ])

@dataclass
class ElementData:
    """Comprehensive element data with all attributes."""
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
    interaction_type: str = "unknown"
    framework_detected: Optional[str] = None
    
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
            'framework_detected': self.framework_detected
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
    
    async def create_browser(self) -> Browser:
        """Create browser instance with complete stealth settings."""
        browser_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-site-isolation-trials',
            '--disable-web-security',
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
            '--disable-ipc-flooding-protection',
            '--disable-infobars',
            '--disable-dev-tools'
        ]
        
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.config.headless,
            args=browser_args
        )
        return self.browser
    
    async def create_context(self, browser: Browser) -> BrowserContext:
        """Create browser context with complete stealth configuration."""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
        user_agent = self.config.user_agent or random.choice(user_agents)
        
        self.context = await browser.new_context(
            viewport={'width': self.config.viewport_width, 'height': self.config.viewport_height},
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
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"'
            }
        )
        return self.context
    
    async def cleanup(self):
        """Clean up browser resources."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

# ============================================================================
# STEALTH LAYER
# ============================================================================

class HumanSimulator:
    """Complete human behavior simulation."""
    
    @staticmethod
    def get_human_delay(config: ExtractionConfig) -> int:
        """Generate human delays based on configuration."""
        if config.use_lognormal_delays:
            mean = random.uniform(3.0, 4.0)
            sigma = random.uniform(0.3, 0.7)
            try:
                delay = np.random.lognormal(mean=mean, sigma=sigma)
            except:
                # Fallback if numpy has issues
                delay = random.uniform(mean * 10, mean * 100)
            return int(max(config.human_delay_range[0], 
                          min(config.human_delay_range[1], delay * 100)))
        else:
            try:
                delay = np.random.lognormal(mean=3.5, sigma=0.5)
            except:
                delay = random.uniform(35, 350)
            return int(max(config.human_delay_range[0], 
                          min(config.human_delay_range[1], delay * 100)))
    
    @staticmethod
    async def human_mouse_movement(page: Page, config: ExtractionConfig):
        """Simulate human mouse movement."""
        try:
            viewport = page.viewport_size
            if not viewport:
                return
            
            if config.use_bspline_mouse:
                # B-spline curve movement
                target_x = random.randint(100, viewport['width'] - 100)
                target_y = random.randint(100, viewport['height'] - 100)
                await HumanSimulator._bspline_mouse_move(page, target_x, target_y)
            else:
                # Simple movement
                num_points = random.randint(3, 7)
                for _ in range(num_points):
                    x = random.randint(0, viewport['width'])
                    y = random.randint(0, viewport['height'])
                    steps = random.randint(5, 15)
                    await page.mouse.move(x, y, steps=steps)
                    await page.wait_for_timeout(random.randint(50, 150))
        except Exception as e:
            logger.debug(f"Mouse movement failed: {e}")
    
    @staticmethod
    async def _bspline_mouse_move(page: Page, target_x: float, target_y: float):
        """B-spline curve mouse movement."""
        start_x, start_y = 0, 0
        steps = 20 + random.randint(-5, 10)
        
        # Control points for cubic Bezier
        cp1x = start_x + (target_x - start_x) * 0.3 + (random.random() - 0.5) * 50
        cp1y = start_y + (target_y - start_y) * 0.3 + (random.random() - 0.5) * 50
        cp2x = start_x + (target_x - start_x) * 0.7 + (random.random() - 0.5) * 50
        cp2y = start_y + (target_y - start_y) * 0.7 + (random.random() - 0.5) * 50
        
        for i in range(steps):
            t = i / (steps - 1)
            x = (1-t)**3 * start_x + 3*(1-t)**2*t * cp1x + 3*(1-t)*t**2 * cp2x + t**3 * target_x
            y = (1-t)**3 * start_y + 3*(1-t)**2*t * cp1y + 3*(1-t)*t**2 * cp2y + t**3 * target_y
            await page.mouse.move(round(x), round(y))
            await asyncio.sleep(random.uniform(0.01, 0.03))
    
    @staticmethod
    async def human_scroll(page: Page):
        """Simulate human scrolling."""
        try:
            scroll_distance = random.randint(100, 500)
            await page.evaluate(f'window.scrollBy({{top: {scroll_distance}, behavior: "smooth"}})')
            await page.wait_for_timeout(random.randint(500, 1500))
            
            # Occasional back-scroll
            if random.random() < 0.2:
                back_scroll = random.randint(50, 150)
                await page.evaluate(f'window.scrollBy({{top: -{back_scroll}, behavior: "smooth"}})')
                await page.wait_for_timeout(random.randint(200, 600))
        except Exception as e:
            logger.debug(f"Scroll simulation failed: {e}")
    
    @staticmethod
    async def human_typing(page: Page, selector: str, text: str):
        """Type with human-like patterns."""
        element = await page.query_selector(selector)
        if not element:
            return
        
        await element.focus()
        for char in text:
            await element.type(char)
            base_delay = random.randint(80, 150)
            variation = random.randint(-30, 30)
            await asyncio.sleep((base_delay + variation) / 1000)
            
            if random.random() < 0.1:  # Occasional pause
                await asyncio.sleep(random.uniform(0.3, 0.8))
    
    @staticmethod
    async def add_micro_behaviors(page: Page):
        """Add subtle human micro-behaviors."""
        try:
            # Random viewport adjustments
            if random.random() < 0.1:
                viewport = page.viewport_size
                if viewport:
                    width = viewport['width'] + random.randint(-50, 50)
                    height = viewport['height'] + random.randint(-25, 25)
                    await page.set_viewport_size({'width': width, 'height': height})
            
            # Simulate reading time
            await page.wait_for_timeout(random.randint(1000, 3000))
        except Exception as e:
            logger.debug(f"Micro-behavior failed: {e}")

class ContextStabilityMonitor:
    """Monitor and maintain context stability."""
    
    def __init__(self, page: Page):
        self.page = page
        self.context_stable = True
        self.context_destroyed_count = 0
        self.last_check = time.time()
    
    async def start_monitoring(self):
        """Start monitoring context stability."""
        try:
            self.page.on('crash', self._on_context_destroyed)
            self.page.on('framenavigated', self._on_navigation)
            asyncio.create_task(self._periodic_check())
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
    
    def _on_context_destroyed(self):
        """Handle context destruction."""
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
    """Complete stealth script injection."""
    
    @staticmethod
    async def inject_all_stealth(page: Page, config: ExtractionConfig):
        """Inject all stealth scripts based on configuration."""
        
        # Base stealth always applied
        base_script = """
        () => {
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {}};
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({state: Notification.permission}) :
                    originalQuery(parameters)
            );
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            delete window.navigator.__proto__.webdriver;
            Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
        }
        """
        await page.add_init_script(base_script)
        
        # WebRTC Protection
        if config.enable_webrtc_protection:
            await page.add_init_script("""
            () => {
                const RTCPeerConnectionOriginal = window.RTCPeerConnection;
                window.RTCPeerConnection = new Proxy(RTCPeerConnectionOriginal, {
                    construct(target, args) {
                        const pc = new target(...args);
                        pc.createDataChannel = new Proxy(pc.createDataChannel, {
                            apply: function() {
                                return {
                                    send: () => {},
                                    close: () => {},
                                    addEventListener: () => {},
                                    removeEventListener: () => {}
                                };
                            }
                        });
                        return pc;
                    }
                });
            }
            """)
        
        # Canvas Protection
        if config.enable_canvas_protection:
            await page.add_init_script("""
            () => {
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(...args) {
                    const context = this.getContext('2d');
                    if (context) {
                        const imageData = context.getImageData(0, 0, this.width, this.height);
                        for (let i = 0; i < imageData.data.length; i += 4) {
                            imageData.data[i] += Math.random() * 2 - 1;
                            imageData.data[i+1] += Math.random() * 2 - 1;
                            imageData.data[i+2] += Math.random() * 2 - 1;
                        }
                        context.putImageData(imageData, 0, 0);
                    }
                    return originalToDataURL.apply(this, args);
                };
            }
            """)
        
        # Hardware Spoofing
        if config.enable_hardware_spoofing:
            await page.add_init_script("""
            () => {
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 4 + Math.floor(Math.random() * 4) * 2
                });
                if (navigator.deviceMemory) {
                    Object.defineProperty(navigator, 'deviceMemory', {
                        get: () => [4, 8, 16, 32][Math.floor(Math.random() * 4)]
                    });
                }
                if (navigator.getBattery) {
                    navigator.getBattery = async () => ({
                        charging: Math.random() > 0.5,
                        chargingTime: Math.random() > 0.5 ? 0 : Infinity,
                        dischargingTime: Math.random() > 0.5 ? Infinity : Math.floor(Math.random() * 28800),
                        level: 0.5 + Math.random() * 0.5,
                        addEventListener: () => {},
                        removeEventListener: () => {},
                        dispatchEvent: () => true
                    });
                }
            }
            """)
        
        # Chrome Runtime Complete
        if config.enable_chrome_runtime_complete:
            await page.add_init_script("""
            () => {
                window.chrome = {
                    runtime: {
                        connect: () => {},
                        sendMessage: () => {},
                        onMessage: {
                            addListener: () => {},
                            removeListener: () => {},
                            hasListener: () => false
                        }
                    },
                    loadTimes: () => ({
                        requestTime: Date.now() / 1000 - Math.random() * 100,
                        startLoadTime: Date.now() / 1000 - Math.random() * 100,
                        commitLoadTime: Date.now() / 1000 - Math.random() * 80,
                        finishDocumentLoadTime: Date.now() / 1000 - Math.random() * 60,
                        finishLoadTime: Date.now() / 1000 - Math.random() * 40,
                        firstPaintTime: Date.now() / 1000 - Math.random() * 30,
                        firstPaintAfterLoadTime: 0,
                        navigationType: "Other",
                        wasFetchedViaSpdy: false,
                        wasNpnNegotiated: true,
                        npnNegotiatedProtocol: "h2",
                        wasAlternateProtocolAvailable: false,
                        connectionInfo: "h2"
                    })
                };
                window.navigator.permissions.query.toString = () => 'function query() { [native code] }';
                if (window.chrome.runtime.sendMessage) {
                    window.chrome.runtime.sendMessage.toString = () => 'function sendMessage() { [native code] }';
                }
            }
            """)
        
        # WebGL Spoofing
        if config.enable_webgl_spoofing:
            await page.add_init_script("""
            () => {
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) return 'Intel Inc.';
                    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                    return getParameter.apply(this, arguments);
                };
            }
            """)
        
        # F5 Networks Bypass
        if config.bypass_f5_networks:
            await page.add_init_script("""
            () => {
                const originalDescriptor = Object.getOwnPropertyDescriptor(Element.prototype, 'innerHTML');
                if (originalDescriptor) {
                    Object.defineProperty(Element.prototype, 'innerHTML', {
                        ...originalDescriptor,
                        get: function() {
                            return originalDescriptor.get.call(this);
                        },
                        set: function(value) {
                            return originalDescriptor.set.call(this, value);
                        }
                    });
                }
                
                const originalSetTimeout = window.setTimeout;
                window.setTimeout = function(callback, delay, ...args) {
                    if (delay === 0) {
                        delay = Math.random() * 4 + 1;
                    }
                    return originalSetTimeout.call(window, callback, delay, ...args);
                };
                
                let lastX = 0, lastY = 0;
                document.addEventListener('mousemove', (e) => {
                    const deltaX = Math.abs(e.clientX - lastX);
                    const deltaY = Math.abs(e.clientY - lastY);
                    if (deltaX === deltaY && deltaX > 0) {
                        e.stopPropagation();
                    }
                    lastX = e.clientX;
                    lastY = e.clientY;
                }, true);
                
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function() {
                    const dataURL = originalToDataURL.apply(this, arguments);
                    return dataURL.substring(0, dataURL.length - 1) + '1';
                };
            }
            """)
        
        logger.debug("All stealth scripts injected")

# ============================================================================
# DETECTION LAYER
# ============================================================================

class FrameworkDetector:
    """Detect JavaScript frameworks."""
    
    @staticmethod
    async def detect(page: Page) -> Optional[str]:
        """Detect framework on page."""
        try:
            framework = await page.evaluate("""
                () => {
                    if (window.React || window.ReactDOM || 
                        document.querySelector('[data-reactroot], #root')) {
                        return 'react';
                    }
                    if (window.angular || window.ng || 
                        document.querySelector('[ng-app], [ng-version]')) {
                        return 'angular';
                    }
                    if (window.Vue || document.querySelector('[data-v-]')) {
                        return 'vue';
                    }
                    if (document.querySelector('[class*="svelte-"]')) {
                        return 'svelte';
                    }
                    if (document.querySelector('#__next')) {
                        return 'nextjs';
                    }
                    return null;
                }
            """)
            
            if framework:
                logger.info(f"Detected {framework} framework")
                # Framework-specific wait
                if framework == 'react':
                    await asyncio.sleep(0.5)
                elif framework == 'angular':
                    await asyncio.sleep(0.7)
                elif framework == 'vue':
                    await page.evaluate("() => window.Vue && Vue.nextTick ? Vue.nextTick() : null")
            
            return framework
            
        except Exception as e:
            logger.debug(f"Framework detection error: {e}")
            return None

class CaptchaDetector:
    """Detect CAPTCHA systems."""
    
    @staticmethod
    async def detect(page: Page) -> Dict[str, Any]:
        """Detect CAPTCHA on page."""
        captcha_info = {
            'detected': False,
            'type': None,
            'selector': None,
            'timestamp': datetime.now()
        }
        
        captcha_selectors = [
            ('recaptcha', 'iframe[src*="recaptcha"], .g-recaptcha'),
            ('hcaptcha', 'iframe[src*="hcaptcha"], .h-captcha'),
            ('cloudflare', '.cf-browser-verification, #cf-challenge-running'),
            ('funcaptcha', 'div[id*="arkose"], iframe[src*="funcaptcha"]'),
        ]
        
        for captcha_type, selector in captcha_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    captcha_info['detected'] = True
                    captcha_info['type'] = captcha_type
                    captcha_info['selector'] = selector
                    logger.warning(f"CAPTCHA detected: {captcha_type}")
                    break
            except:
                continue
        
        return captcha_info

class CookieHandler:
    """Handle cookie consent."""
    
    @staticmethod
    async def handle(page: Page, config: ExtractionConfig) -> bool:
        """Handle cookie consent popups."""
        if not config.enable_cookie_handling:
            return False
        
        await asyncio.sleep(random.uniform(1, 2))
        
        for selector in config.cookie_selectors:
            try:
                button = page.locator(selector).first
                if await button.is_visible():
                    box = await button.bounding_box()
                    if box:
                        if config.use_bspline_mouse:
                            await HumanSimulator._bspline_mouse_move(
                                page,
                                box['x'] + box['width'] / 2,
                                box['y'] + box['height'] / 2
                            )
                        await asyncio.sleep(random.uniform(0.2, 0.5))
                        await button.click()
                        logger.info(f"Clicked cookie consent: {selector}")
                        await asyncio.sleep(random.uniform(0.5, 1))
                        return True
            except:
                continue
        
        return False

class TrustBuilder:
    """Build trust with websites."""
    
    def __init__(self):
        self.trust_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def build(self, page: Page, domain: str, config: ExtractionConfig):
        """Build trust by visiting pages."""
        if not config.enable_trust_building:
            return
        
        if any(safe in domain for safe in config.trust_safe_domains):
            logger.info(f"Skipping trust for safe domain: {domain}")
            return
        
        if domain in self.trust_sessions:
            session = self.trust_sessions[domain]
            if (datetime.now() - session['built_at']).total_seconds() < 3600:
                logger.info(f"Using existing trust session for {domain}")
                return
        
        logger.info(f"Building trust for {domain}")
        
        try:
            await page.goto(f"https://{domain}", wait_until='domcontentloaded')
            await asyncio.sleep(random.uniform(2, 4))
            
            for _ in range(3):
                scroll_distance = random.randint(100, 400)
                await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
                await asyncio.sleep(random.uniform(0.5, 1.5))
            
            links = await page.query_selector_all('a[href^="/"]')
            pages_to_visit = min(config.trust_visit_pages, len(links))
            
            for i in range(pages_to_visit):
                if not links:
                    break
                link = random.choice(links)
                try:
                    await link.click()
                    await page.wait_for_load_state('domcontentloaded')
                    await asyncio.sleep(random.uniform(1, 3))
                    await page.go_back()
                except:
                    pass
            
            self.trust_sessions[domain] = {
                'built_at': datetime.now(),
                'pages_visited': pages_to_visit
            }
            
            logger.info(f"Trust building completed for {domain}")
            
        except Exception as e:
            logger.debug(f"Trust building error: {e}")

# ============================================================================
# STRATEGY LAYER - Extraction Strategies
# ============================================================================

class ExtractionStrategy(ABC):
    """Abstract base for extraction strategies."""
    
    @abstractmethod
    async def extract(self, page: Page) -> List[ElementData]:
        """Extract elements using specific strategy."""
        pass
    
    @abstractmethod
    def can_handle(self, page: Page) -> bool:
        """Check if strategy can handle page."""
        pass

class DOMExtractionStrategy(ExtractionStrategy):
    """DOM-based extraction."""
    
    async def extract(self, page: Page) -> List[ElementData]:
        """Extract elements from DOM."""
        elements = []
        
        try:
            dom_elements = await page.evaluate("""
                () => {
                    const elements = [];
                    const selectors = [
                        'a', 'button', 'input', 'select', 'textarea',
                        '[role="button"]', '[role="link"]', '[onclick]',
                        '.btn', '.button', '[type="submit"]'
                    ];
                    
                    const getXPath = (element) => {
                        if (!element) return '';
                        if (element.id) return `//*[@id="${element.id}"]`;
                        if (element === document.body) return '/html/body';
                        
                        let ix = 0;
                        const siblings = element.parentNode.childNodes;
                        for (let i = 0; i < siblings.length; i++) {
                            const sibling = siblings[i];
                            if (sibling === element) {
                                return getXPath(element.parentNode) + '/' + 
                                       element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                            }
                            if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                                ix++;
                            }
                        }
                    };
                    
                    const allElements = document.querySelectorAll(selectors.join(', '));
                    
                    allElements.forEach((el, index) => {
                        if (index >= 50) return;
                        
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        
                        elements.push({
                            tagName: el.tagName.toLowerCase(),
                            id: el.id || null,
                            className: el.className || '',
                            textContent: (el.textContent || '').substring(0, 100).trim(),
                            href: el.href || null,
                            type: el.type || el.tagName.toLowerCase(),
                            name: el.name || null,
                            placeholder: el.placeholder || null,
                            value: el.value || null,
                            isVisible: rect.width > 0 && rect.height > 0 &&
                                      style.visibility !== 'hidden' &&
                                      style.display !== 'none',
                            isClickable: el.tagName === 'BUTTON' || el.tagName === 'A' || 
                                        el.onclick !== null || el.role === 'button',
                            x: Math.round(rect.x),
                            y: Math.round(rect.y),
                            width: Math.round(rect.width),
                            height: Math.round(rect.height),
                            role: el.getAttribute('role'),
                            ariaLabel: el.getAttribute('aria-label'),
                            tabIndex: el.tabIndex,
                            xpath: getXPath(el)
                        });
                    });
                    
                    return elements;
                }
            """)
            
            for elem_data in dom_elements:
                element = ElementData(
                    tag_name=elem_data['tagName'],
                    element_type=elem_data['type'],
                    xpath=elem_data.get('xpath', f"//{elem_data['tagName']}"),
                    css_selector=f"#{elem_data['id']}" if elem_data['id'] else elem_data['tagName'],
                    text_content=elem_data['textContent'],
                    id=elem_data['id'],
                    class_names=elem_data['className'].split() if elem_data['className'] else [],
                    name=elem_data['name'],
                    href=elem_data['href'],
                    placeholder=elem_data['placeholder'],
                    value=elem_data['value'],
                    is_visible=elem_data['isVisible'],
                    is_clickable=elem_data['isClickable'],
                    x=elem_data['x'],
                    y=elem_data['y'],
                    width=elem_data['width'],
                    height=elem_data['height'],
                    role=elem_data['role'],
                    aria_label=elem_data['ariaLabel'],
                    tab_index=elem_data['tabIndex'],
                    extraction_strategy='DOM',
                    confidence_score=0.9
                )
                elements.append(element)
                
        except Exception as e:
            logger.error(f"DOM extraction failed: {e}")
        
        return elements
    
    def can_handle(self, page: Page) -> bool:
        return True

class AccessibilityExtractionStrategy(ExtractionStrategy):
    """Accessibility-focused extraction."""
    
    async def extract(self, page: Page) -> List[ElementData]:
        """Extract elements with accessibility focus."""
        elements = []
        
        try:
            aria_elements = await page.evaluate("""
                () => {
                    const elements = [];
                    const selectors = [
                        '[aria-label]', '[aria-describedby]', '[role]',
                        '[aria-expanded]', '[aria-hidden="false"]'
                    ];
                    
                    selectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach((el, index) => {
                            if (index >= 30) return;
                            
                            const rect = el.getBoundingClientRect();
                            
                            elements.push({
                                tagName: el.tagName.toLowerCase(),
                                role: el.getAttribute('role'),
                                ariaLabel: el.getAttribute('aria-label'),
                                ariaExpanded: el.getAttribute('aria-expanded'),
                                ariaHidden: el.getAttribute('aria-hidden'),
                                tabIndex: el.tabIndex,
                                textContent: (el.textContent || '').substring(0, 100).trim(),
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
            
            for elem_data in aria_elements:
                element = ElementData(
                    tag_name=elem_data['tagName'],
                    element_type=elem_data['tagName'],
                    xpath=f"//{elem_data['tagName']}[@aria-label='{elem_data['ariaLabel']}']" if elem_data['ariaLabel'] else f"//{elem_data['tagName']}",
                    css_selector=f"[aria-label='{elem_data['ariaLabel']}']" if elem_data['ariaLabel'] else elem_data['tagName'],
                    text_content=elem_data['textContent'],
                    role=elem_data['role'],
                    aria_label=elem_data['ariaLabel'],
                    aria_expanded=elem_data['ariaExpanded'] == 'true' if elem_data['ariaExpanded'] else None,
                    aria_hidden=elem_data['ariaHidden'] == 'true' if elem_data['ariaHidden'] else None,
                    tab_index=elem_data['tabIndex'],
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
        return True

class VisualExtractionStrategy(ExtractionStrategy):
    """Visual-based extraction."""
    
    async def extract(self, page: Page) -> List[ElementData]:
        """Extract visually prominent elements."""
        elements = []
        
        try:
            visual_elements = await page.evaluate("""
                () => {
                    const elements = [];
                    const minSize = 20;
                    const allElements = document.querySelectorAll('*');
                    
                    allElements.forEach((el, index) => {
                        if (index >= 50) return;
                        
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        
                        if (rect.width >= minSize && rect.height >= minSize &&
                            style.visibility !== 'hidden' &&
                            style.display !== 'none' &&
                            style.opacity !== '0') {
                            
                            elements.push({
                                tagName: el.tagName.toLowerCase(),
                                id: el.id || null,
                                textContent: (el.textContent || '').substring(0, 100).trim(),
                                x: Math.round(rect.x),
                                y: Math.round(rect.y),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height),
                                zIndex: style.zIndex || '0'
                            });
                        }
                    });
                    
                    return elements.sort((a, b) => {
                        const aScore = (a.width * a.height) + (parseInt(a.zIndex) * 1000);
                        const bScore = (b.width * b.height) + (parseInt(b.zIndex) * 1000);
                        return bScore - aScore;
                    }).slice(0, 30);
                }
            """)
            
            for elem_data in visual_elements:
                element = ElementData(
                    tag_name=elem_data['tagName'],
                    element_type=elem_data['tagName'],
                    xpath=f"//{elem_data['tagName']}[@id='{elem_data['id']}']" if elem_data['id'] else f"//{elem_data['tagName']}",
                    css_selector=f"#{elem_data['id']}" if elem_data['id'] else elem_data['tagName'],
                    text_content=elem_data['textContent'],
                    id=elem_data['id'],
                    x=elem_data['x'],
                    y=elem_data['y'],
                    width=elem_data['width'],
                    height=elem_data['height'],
                    is_visible=True,
                    extraction_strategy='Visual',
                    confidence_score=0.8
                )
                elements.append(element)
                
        except Exception as e:
            logger.error(f"Visual extraction failed: {e}")
        
        return elements
    
    def can_handle(self, page: Page) -> bool:
        return True

# ============================================================================
# ORCHESTRATION LAYER - Main Extractor
# ============================================================================

class UltimateElementExtractor:
    """Main extractor coordinating all operations."""
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        self.browser_manager = BrowserManager(config)
        self.trust_builder = TrustBuilder()
        self.strategies = [
            DOMExtractionStrategy(),
            AccessibilityExtractionStrategy(),
            VisualExtractionStrategy()
        ]
        self.detected_framework: Optional[str] = None
        self.captcha_info: Dict[str, Any] = {}
    
    async def extract(self, url: str):
        """Extract elements and return ElementExtraction contract.
        
        Args:
            url: URL to extract from
            
        Returns:
            ElementExtraction: Contract-compliant output
        """
        from data_contracts import ElementExtraction, ExtractedElement
        from dataclasses import asdict
        from datetime import datetime
        
        start_time = time.time()
        success = True
        error_message = None
        elements = []
        
        try:
            # Use internal extraction method
            element_data_list = await self._extract_internal(url)
            
            # Convert ElementData to ExtractedElement contracts
            for elem_data in element_data_list:
                elem_dict = asdict(elem_data)
                # Filter to valid fields for ExtractedElement
                valid_fields = {k: v for k, v in elem_dict.items() 
                               if k in ExtractedElement.model_fields}
                elements.append(ExtractedElement(**valid_fields))
                
        except Exception as e:
            success = False
            error_message = str(e)
            logger.error(f"Extraction failed: {e}")
        
        # Return contract
        return ElementExtraction(
            url=url,
            timestamp=datetime.now().isoformat(),
            success=success,
            elements=elements,
            metadata={
                "extractor_version": "1.0.0",
                "config": {
                    "headless": self.config.headless,
                    "stealth_enabled": self.config.enable_stealth,
                    "max_elements": self.config.max_elements
                }
            },
            error_message=error_message,
            extraction_time=time.time() - start_time
        )
    
    async def _extract_internal(self, url: str) -> List[ElementData]:
        """Internal extraction method with all features."""
        browser = None
        try:
            # Validate URL
            if not self._validate_url(url):
                raise ValueError(f"Invalid URL: {url}")
            
            # Setup browser
            browser = await self._setup_browser()
            
            # Build trust if needed
            parsed_url = urlparse(url)
            if parsed_url.netloc and self.config.enable_trust_building:
                context = await self.browser_manager.create_context(browser)
                trust_page = await context.new_page()
                await self.trust_builder.build(trust_page, parsed_url.netloc, self.config)
                await trust_page.close()
            
            # Navigate to URL
            page = await self._navigate_to_url(browser, url)
            
            # Apply stealth
            if self.config.enable_stealth:
                await self._apply_stealth_measures(page)
            
            # Detect framework
            if self.config.enable_framework_detection:
                self.detected_framework = await FrameworkDetector.detect(page)
            
            # Handle cookies
            if self.config.enable_cookie_handling:
                await CookieHandler.handle(page, self.config)
            
            # Detect CAPTCHA
            if self.config.enable_captcha_detection:
                self.captcha_info = await CaptchaDetector.detect(page)
                if self.captcha_info['detected']:
                    logger.warning(f"CAPTCHA detected: {self.captcha_info['type']}")
            
            # Extract elements
            elements = await self._extract_elements(page)
            
            # Enrich with framework info
            for element in elements:
                element.framework_detected = self.detected_framework
            
            # Post-process
            elements = await self._post_process(elements)
            
            return elements
            
        except Exception as e:
            logger.error(f"Extraction failed for {url}: {e}")
            
            if self.config.use_mobile_fallback:
                logger.info("Attempting mobile fallback...")
                return await self._extract_with_mobile_fallback_internal(url)
            
            raise
            
        finally:
            if browser:
                await self._cleanup(browser)
    
    # Removed extract_with_contract - using only extract method per CODER principles
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        if url.startswith('data:'):
            return True
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    
    async def _setup_browser(self) -> Browser:
        """Setup browser with stealth."""
        return await self.browser_manager.create_browser()
    
    async def _navigate_to_url(self, browser: Browser, url: str) -> Page:
        """Navigate with stability monitoring."""
        context = await self.browser_manager.create_context(browser)
        page = await context.new_page()
        
        # Apply stealth scripts before navigation
        if self.config.enable_stealth:
            await StealthInjector.inject_all_stealth(page, self.config)
        
        # Setup monitoring
        monitor = ContextStabilityMonitor(page)
        await monitor.start_monitoring()
        
        # Navigate with retries
        for attempt in range(self.config.max_retry_attempts):
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=self.config.timeout * 1000)
                await asyncio.sleep(2)
                
                if monitor.is_stable():
                    return page
                    
            except PlaywrightError as e:
                if 'context' in str(e).lower() and attempt < self.config.max_retry_attempts - 1:
                    logger.warning(f"Context destroyed, retrying... (attempt {attempt + 1})")
                    page = await context.new_page()
                    continue
                raise
        
        return page
    
    async def _apply_stealth_measures(self, page: Page):
        """Apply all stealth measures."""
        # Human simulation
        if self.config.enable_human_simulation:
            delay = HumanSimulator.get_human_delay(self.config)
            await asyncio.sleep(delay / 1000)
            
            await HumanSimulator.add_micro_behaviors(page)
            
            if self.config.scroll_behavior:
                await HumanSimulator.human_scroll(page)
            
            if self.config.mouse_movement:
                await HumanSimulator.human_mouse_movement(page, self.config)
        
        # Script blocking
        if self.config.block_tracking_scripts:
            await self._setup_script_blocking(page)
    
    async def _setup_script_blocking(self, page: Page):
        """Block tracking scripts."""
        async def handle_route(route):
            url = route.request.url.lower()
            
            blocking_patterns = [
                'adobe', 'dtm', 'ensighten', 'segment',
                'google-analytics', 'googletagmanager',
                'hotjar', 'fullstory', 'f5-cspm', 'shape',
                'datadome', 'perimeter', 'cloudflare', 'recaptcha',
                'kasada', 'distil', 'incapsula', 'akamai'
            ]
            
            if any(pattern in url for pattern in blocking_patterns):
                await route.fulfill(body='// Blocked', content_type='application/javascript')
            else:
                await route.continue_()
        
        await page.route('**/*.js', handle_route)
    
    async def _extract_elements(self, page: Page) -> List[ElementData]:
        """Execute extraction strategies."""
        if self.config.parallel_strategies:
            tasks = [
                strategy.extract(page)
                for strategy in self.strategies
                if strategy.can_handle(page)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            elements = []
            for result in results:
                if isinstance(result, list):
                    elements.extend(result)
        else:
            elements = []
            for strategy in self.strategies:
                if strategy.can_handle(page):
                    strategy_elements = await strategy.extract(page)
                    elements.extend(strategy_elements)
        
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
        
        # Limit to max_elements
        if len(elements) > self.config.max_elements:
            elements = elements[:self.config.max_elements]
        
        # Enrich with interaction types
        for element in elements:
            element.interaction_type = self._determine_interaction_type(element)
        
        return elements
    
    def _deduplicate(self, elements: List[ElementData]) -> List[ElementData]:
        """Remove duplicate elements."""
        seen_xpaths = set()
        unique_elements = []
        
        for element in elements:
            if element.xpath not in seen_xpaths:
                seen_xpaths.add(element.xpath)
                unique_elements.append(element)
        
        return unique_elements
    
    def _determine_interaction_type(self, element: ElementData) -> str:
        """Determine interaction type."""
        if element.tag_name == 'input':
            if element.input_type in ['text', 'email', 'password', 'search']:
                return 'type'
            elif element.input_type in ['checkbox', 'radio']:
                return 'check'
            elif element.input_type in ['submit', 'button']:
                return 'click'
        elif element.tag_name in ['button', 'a']:
            return 'click'
        elif element.tag_name == 'select':
            return 'select'
        elif element.tag_name == 'textarea':
            return 'type'
        elif element.role == 'button':
            return 'click'
        
        return 'unknown'
    
    async def _extract_with_mobile_fallback_internal(self, url: str) -> List[ElementData]:
        """Mobile fallback extraction."""
        logger.info("Attempting mobile fallback extraction")
        
        original_viewport = (self.config.viewport_width, self.config.viewport_height)
        original_ua = self.config.user_agent
        
        self.config.viewport_width = 375
        self.config.viewport_height = 812
        self.config.user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15'
        
        try:
            return await self.extract(url)
        finally:
            self.config.viewport_width, self.config.viewport_height = original_viewport
            self.config.user_agent = original_ua
    
    async def _cleanup(self, browser: Browser):
        """Clean up resources."""
        try:
            await browser.close()
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
    Extract elements from a web page with comprehensive stealth and detection.
    
    This is the main entry point providing all extraction capabilities in one call.
    
    Features:
    - WebRTC leak prevention
    - Canvas fingerprinting protection  
    - Framework detection (React, Angular, Vue)
    - CAPTCHA awareness
    - Trust building
    - B-spline mouse movements
    - F5 Networks bypass
    
    Args:
        url: The URL to extract elements from
        config: Optional extraction configuration
        
    Returns:
        List of ElementData with comprehensive element information
        
    Raises:
        ValueError: If URL is invalid
        TimeoutError: If extraction exceeds timeout
        PlaywrightError: If browser automation fails
    """
    if config is None:
        config = ExtractionConfig()
    
    extractor = UltimateElementExtractor(config)
    return await extractor.extract(url)

# ============================================================================
# CLI Interface
# ============================================================================

if __name__ == "__main__":
    import sys
    
    async def main():
        if len(sys.argv) < 2:
            print("Usage: python ultimate_element_extractor_final.py <url>")
            sys.exit(1)
        
        url = sys.argv[1]
        
        config = ExtractionConfig(
            enable_stealth=True,
            enable_human_simulation=True,
            bypass_f5_networks=True,
            parallel_strategies=True,
            enable_webrtc_protection=True,
            enable_canvas_protection=True,
            enable_webgl_spoofing=True,
            enable_hardware_spoofing=True,
            enable_chrome_runtime_complete=True,
            enable_framework_detection=True,
            enable_captcha_detection=True,
            enable_cookie_handling=True
        )
        
        try:
            elements = await extract_elements(url, config)
            print(f"Extracted {len(elements)} elements from {url}")
            
            if elements and elements[0].framework_detected:
                print(f"Framework: {elements[0].framework_detected}")
            
            for i, element in enumerate(elements[:5], 1):
                print(f"\n{i}. {element.tag_name} - {element.text_content[:50]}")
                print(f"   XPath: {element.xpath}")
                print(f"   Interaction: {element.interaction_type}")
                
        except Exception as e:
            print(f"Extraction failed: {e}")
            sys.exit(1)
    
    asyncio.run(main())