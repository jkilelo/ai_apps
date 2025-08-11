"""
Enhanced Stealth Extractor with F5 Networks Shape Security Bypass
Implements advanced context stability, human simulation, and runtime protection bypass
"""

import asyncio
import hashlib
import json
import logging
import random
import time
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from urllib.parse import urlparse

from playwright.async_api import Page, Browser, BrowserContext, async_playwright, Error as PlaywrightError

logger = logging.getLogger(__name__)


@dataclass
class EnhancedExtractionConfig:
    """Enhanced configuration with F5 bypass features."""
    max_elements: int = 50
    timeout: int = 60
    enable_ai_analysis: bool = False
    stealth_mode: bool = True
    enable_context_recovery: bool = True
    enable_human_simulation: bool = True
    enable_session_warming: bool = False
    enable_runtime_bypass: bool = True
    use_mobile_fallback: bool = False
    max_retry_attempts: int = 3
    context_stability_check_interval: int = 1000  # ms
    human_delay_range: Tuple[int, int] = (100, 2000)
    scroll_behavior: bool = True
    mouse_movement: bool = True
    

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
            points = []
            for _ in range(num_points):
                x = random.randint(0, viewport['width'])
                y = random.randint(0, viewport['height'])
                points.append((x, y))
            
            # Move mouse along path
            for x, y in points:
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


class EnhancedStealthExtractor:
    """Enhanced extractor with F5 Networks bypass capabilities."""
    
    def __init__(self, config: Optional[EnhancedExtractionConfig] = None):
        self.config = config or EnhancedExtractionConfig()
        self.extraction_attempts = 0
        self.warmup_completed = False
        
    async def inject_advanced_stealth(self, page: Page):
        """Inject advanced stealth scripts before navigation."""
        
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
    
    async def warm_session(self, browser: Browser) -> BrowserContext:
        """Warm up browser session to appear legitimate."""
        
        if not self.config.enable_session_warming:
            return await self.create_stealth_context(browser)
        
        logger.info("Warming up browser session...")
        
        # Create context
        context = await self.create_stealth_context(browser)
        page = await context.new_page()
        
        # Visit legitimate sites
        warmup_sites = [
            'https://www.google.com',
            'https://www.yahoo.com',
            'https://www.msn.com',
            'https://www.wikipedia.org'
        ]
        
        for site in warmup_sites:
            try:
                await page.goto(site, wait_until='domcontentloaded', timeout=10000)
                
                # Human-like interaction
                if self.config.enable_human_simulation:
                    await HumanSimulator.human_scroll(page)
                    await HumanSimulator.human_mouse_movement(page)
                
                # Random dwell time
                await page.wait_for_timeout(random.randint(2000, 5000))
                
            except Exception as e:
                logger.debug(f"Warmup site {site} failed: {e}")
        
        await page.close()
        self.warmup_completed = True
        logger.info("Session warming completed")
        
        return context
    
    async def create_stealth_context(self, browser: Browser) -> BrowserContext:
        """Create browser context with maximum stealth."""
        
        # Rotating user agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        # Create context with enhanced settings
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=random.choice(user_agents),
            locale='en-US',
            timezone_id='America/New_York',
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
        
        return context
    
    async def navigate_with_stability(self, page: Page, url: str) -> bool:
        """Navigate with context stability monitoring and redirect handling."""
        
        monitor = ContextStabilityMonitor(page)
        await monitor.start_monitoring()
        
        try:
            # Pre-navigation stealth
            await self.inject_advanced_stealth(page)
            
            # Add enhanced route interception
            if self.config.enable_runtime_bypass:
                await self.setup_enhanced_runtime_bypass(page)
            
            # Human-like delay before navigation
            if self.config.enable_human_simulation:
                await page.wait_for_timeout(HumanSimulator.get_human_delay())
            
            # Enhanced navigation with redirect handling
            navigation_success = await self._navigate_with_redirect_handling(page, url, monitor)
            
            if not navigation_success:
                return False
            
            # Post-navigation stability wait
            await asyncio.sleep(3)
            
            # Post-navigation human behavior
            if self.config.enable_human_simulation:
                await HumanSimulator.add_micro_behaviors(page)
                await HumanSimulator.human_scroll(page)
                await HumanSimulator.human_mouse_movement(page)
            
            # Final stability check with longer wait
            await asyncio.sleep(2)
            return monitor.is_stable()
            
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False
    
    async def _navigate_with_redirect_handling(self, page: Page, url: str, monitor) -> bool:
        """Handle navigation with redirect tracking and context preservation."""
        
        # Track navigation events
        navigation_count = 0
        final_url = None
        
        def track_navigation(frame):
            nonlocal navigation_count, final_url
            if frame == page.main_frame:
                navigation_count += 1
                final_url = frame.url
                logger.debug(f"Navigation #{navigation_count} to: {final_url}")
        
        # Add navigation tracking
        page.on('framenavigated', track_navigation)
        
        try:
            # Enhanced navigation strategies
            strategies = [
                ('commit', 30000),      # Fast commit with longer timeout
                ('domcontentloaded', 45000),  # Standard load
                ('load', 60000),        # Full load with max timeout
                ('networkidle', 30000)  # Network idle as last resort
            ]
            
            navigation_success = False
            
            for strategy, timeout in strategies:
                try:
                    logger.debug(f"Attempting navigation with strategy: {strategy}")
                    
                    # Reset navigation tracking
                    navigation_count = 0
                    final_url = None
                    
                    # Navigate with specific strategy
                    await page.goto(url, wait_until=strategy, timeout=timeout)
                    
                    # Wait for potential redirects to settle
                    await asyncio.sleep(2)
                    
                    # Check if we have too many redirects (possible loop)
                    if navigation_count > 5:
                        logger.warning(f"Too many redirects ({navigation_count}), skipping strategy")
                        continue
                    
                    # Check context stability after navigation
                    if monitor.is_stable():
                        logger.debug(f"Navigation successful with {strategy} after {navigation_count} redirects")
                        navigation_success = True
                        break
                    else:
                        logger.debug(f"Context unstable after {strategy}")
                        
                except PlaywrightError as e:
                    error_msg = str(e).lower()
                    if 'context' in error_msg or 'destroyed' in error_msg:
                        logger.warning(f"Context destroyed with strategy {strategy}")
                        break  # Don't try other strategies if context is destroyed
                    elif 'timeout' in error_msg:
                        logger.debug(f"Timeout with {strategy}: {e}")
                    else:
                        logger.debug(f"Navigation failed with {strategy}: {e}")
            
            # Log final navigation result
            if navigation_success:
                current_url = page.url
                if url not in current_url:
                    logger.info(f"Navigation succeeded with redirect: {url} -> {current_url}")
                else:
                    logger.info(f"Navigation succeeded: {url}")
            
            return navigation_success
            
        finally:
            # Remove navigation tracking
            page.remove_listener('framenavigated', track_navigation)
    
    async def setup_enhanced_runtime_bypass(self, page: Page):
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
            await page.route('**/*', self._enhanced_request_filter)
            
        except Exception as e:
            logger.error(f"Failed to setup enhanced runtime bypass: {e}")
    
    async def _enhanced_request_filter(self, route):
        """Enhanced request filtering for better compatibility."""
        
        url = route.request.url.lower()
        resource_type = route.request.resource_type
        
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
    
    async def setup_runtime_bypass(self, page: Page):
        """Setup runtime protection bypass."""
        
        try:
            # Intercept Shape Security scripts
            async def handle_shape_request(route):
                url = route.request.url
                
                # Block or modify Shape Security scripts
                if any(keyword in url.lower() for keyword in ['shape', 'f5-', 'antibot', 'challenge']):
                    logger.debug(f"Intercepting protection script: {url}")
                    
                    # Option 1: Block the script
                    # await route.fulfill(body='// Blocked', content_type='application/javascript')
                    
                    # Option 2: Modify the script
                    response = await route.fetch()
                    body = await response.text()
                    
                    # Neutralize detection functions
                    modifications = [
                        ('detectAutomation()', 'function detectAutomation(){return false;}'),
                        ('isHeadless()', 'function isHeadless(){return false;}'),
                        ('checkWebDriver()', 'function checkWebDriver(){return false;}'),
                        ('validateContext()', 'function validateContext(){return true;}'),
                    ]
                    
                    for original, replacement in modifications:
                        body = body.replace(original, replacement)
                    
                    await route.fulfill(body=body, content_type='application/javascript')
                else:
                    await route.continue_()
            
            await page.route('**/*.js', handle_shape_request)
            
        except Exception as e:
            logger.error(f"Failed to setup runtime bypass: {e}")
    
    async def recover_from_destruction(self, browser: Browser, url: str, attempt: int = 1) -> Optional[Page]:
        """Recover from context destruction."""
        
        if attempt > self.config.max_retry_attempts:
            logger.error(f"Max recovery attempts ({self.config.max_retry_attempts}) reached")
            return None
        
        logger.info(f"Attempting recovery (attempt {attempt}/{self.config.max_retry_attempts})")
        
        try:
            # Create fresh context
            context = await self.create_stealth_context(browser)
            page = await context.new_page()
            
            # Extra stealth for recovery
            await self.inject_advanced_stealth(page)
            
            # Longer delay between attempts
            await page.wait_for_timeout(5000 * attempt)
            
            # Try navigation
            success = await self.navigate_with_stability(page, url)
            
            if success:
                logger.info("Recovery successful")
                return page
            else:
                await page.close()
                await context.close()
                return await self.recover_from_destruction(browser, url, attempt + 1)
                
        except Exception as e:
            logger.error(f"Recovery attempt {attempt} failed: {e}")
            return None
    
    async def extract_with_enhanced_stealth(self, url: str) -> List[Dict[str, Any]]:
        """Main extraction method with all enhancements."""
        
        logger.info(f"Starting enhanced extraction for {url}")
        
        async with async_playwright() as p:
            # Launch browser
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
                '--window-size=1920,1080',
                '--start-maximized',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection'
            ]
            
            browser = await p.chromium.launch(
                headless=False,  # Headful for better stealth
                args=browser_args
            )
            
            try:
                # Warm session if enabled
                if self.config.enable_session_warming:
                    context = await self.warm_session(browser)
                else:
                    context = await self.create_stealth_context(browser)
                
                # Create page
                page = await context.new_page()
                
                # Navigate with stability
                navigation_success = await self.navigate_with_stability(page, url)
                
                if not navigation_success:
                    logger.warning("Initial navigation failed, attempting recovery")
                    page = await self.recover_from_destruction(browser, url)
                    
                    if not page:
                        logger.error("Recovery failed, trying mobile fallback")
                        
                        if self.config.use_mobile_fallback:
                            return await self.extract_with_mobile_fallback(url)
                        else:
                            return []
                
                # Extract elements
                elements = await self.extract_elements_from_page(page)
                
                logger.info(f"Successfully extracted {len(elements)} elements")
                return elements
                
            finally:
                await browser.close()
    
    async def extract_elements_from_page(self, page: Page) -> List[Dict[str, Any]]:
        """Extract elements from the page with enhanced error handling."""
        
        try:
            # Wait for content to load with multiple strategies
            await self._wait_for_page_stability(page)
            
            # Try extraction with multiple approaches
            extraction_attempts = [
                self._extract_with_javascript,
                self._extract_with_selectors,
                self._extract_basic_elements
            ]
            
            for attempt_func in extraction_attempts:
                try:
                    elements_data = await attempt_func(page)
                    if elements_data and len(elements_data) > 0:
                        logger.debug(f"Extraction successful with {attempt_func.__name__}: {len(elements_data)} elements")
                        return elements_data
                except Exception as e:
                    logger.debug(f"Extraction attempt {attempt_func.__name__} failed: {e}")
                    continue
            
            logger.warning("All extraction attempts failed, returning empty list")
            return []
            
        except Exception as e:
            logger.error(f"Element extraction completely failed: {e}")
            return []
    
    async def _wait_for_page_stability(self, page: Page):
        """Wait for page to stabilize with multiple strategies."""
        
        stability_checks = [
            ('body', 10000),
            ('a, button', 5000),
            ('[role="button"], [role="link"]', 5000)
        ]
        
        for selector, timeout in stability_checks:
            try:
                await page.wait_for_selector(selector, timeout=timeout)
                logger.debug(f"Page stability confirmed with selector: {selector}")
                break
            except Exception as e:
                logger.debug(f"Stability check failed for {selector}: {e}")
                continue
        
        # Additional wait for dynamic content
        await asyncio.sleep(2)
    
    async def _extract_with_javascript(self, page: Page) -> List[Dict[str, Any]]:
        """Primary extraction method using JavaScript evaluation."""
        
        return await page.evaluate("""
            () => {
                const elements = [];
                const selectors = [
                    'a', 'button', 'input', 'select', 'textarea', 'form',
                    '[role="button"]', '[role="link"]', '[tabindex="0"]',
                    '.btn', '.button', '.link', '[onclick]'
                ];
                
                const allElements = document.querySelectorAll(selectors.join(', '));
                
                allElements.forEach((el, index) => {
                    if (index >= 50) return;  // Limit to 50 elements
                    
                    try {
                        const rect = el.getBoundingClientRect();
                        const computedStyle = window.getComputedStyle(el);
                        
                        elements.push({
                            tag_name: el.tagName.toLowerCase(),
                            element_type: el.type || el.tagName.toLowerCase(),
                            text_content: (el.textContent || el.innerText || '').substring(0, 100).trim(),
                            href: el.href || null,
                            id: el.id || null,
                            class_name: el.className || null,
                            name: el.name || null,
                            value: el.value || null,
                            placeholder: el.placeholder || null,
                            aria_label: el.getAttribute('aria-label') || null,
                            role: el.getAttribute('role') || null,
                            is_visible: rect.width > 0 && rect.height > 0 && 
                                      computedStyle.visibility !== 'hidden' && 
                                      computedStyle.display !== 'none',
                            position: {
                                x: Math.round(rect.x),
                                y: Math.round(rect.y),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height)
                            },
                            xpath: null  // Placeholder for xpath if needed
                        });
                    } catch (e) {
                        console.warn('Error processing element:', e);
                    }
                });
                
                return elements;
            }
        """)
    
    async def _extract_with_selectors(self, page: Page) -> List[Dict[str, Any]]:
        """Fallback extraction using Playwright selectors."""
        
        elements = []
        selectors = ['a', 'button', 'input', 'select', 'textarea', 'form']
        
        for selector in selectors:
            try:
                locators = page.locator(selector)
                count = await locators.count()
                
                for i in range(min(count, 20)):  # Limit per selector
                    try:
                        element = locators.nth(i)
                        
                        # Get basic attributes
                        tag_name = selector
                        text_content = await element.text_content() if await element.is_visible() else ''
                        
                        elements.append({
                            'tag_name': tag_name,
                            'element_type': tag_name,
                            'text_content': (text_content or '').strip()[:100],
                            'is_visible': await element.is_visible(),
                            'position': {'x': 0, 'y': 0, 'width': 0, 'height': 0}
                        })
                        
                        if len(elements) >= 50:
                            break
                            
                    except Exception as e:
                        logger.debug(f"Error extracting {selector}[{i}]: {e}")
                        continue
                        
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue
        
        return elements
    
    async def _extract_basic_elements(self, page: Page) -> List[Dict[str, Any]]:
        """Last resort: basic element extraction."""
        
        try:
            # Just get page info if elements can't be extracted
            title = await page.title()
            url = page.url
            
            return [{
                'tag_name': 'page',
                'element_type': 'page_info',
                'text_content': f"Page: {title}",
                'href': url,
                'is_visible': True,
                'position': {'x': 0, 'y': 0, 'width': 0, 'height': 0}
            }]
            
        except Exception:
            return []
    
    async def extract_with_mobile_fallback(self, url: str) -> List[Dict[str, Any]]:
        """Try extraction with mobile user agent."""
        
        logger.info("Attempting mobile fallback extraction")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            # Mobile context
            context = await browser.new_context(
                viewport={'width': 375, 'height': 812},
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
                is_mobile=True,
                has_touch=True
            )
            
            page = await context.new_page()
            
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                elements = await self.extract_elements_from_page(page)
                logger.info(f"Mobile fallback extracted {len(elements)} elements")
                return elements
                
            except Exception as e:
                logger.error(f"Mobile fallback failed: {e}")
                return []
                
            finally:
                await browser.close()


# Public API function
async def extract_with_enhanced_stealth(
    url: str,
    config: Optional[EnhancedExtractionConfig] = None
) -> List[Dict[str, Any]]:
    """
    Extract elements with enhanced stealth capabilities.
    
    Args:
        url: Target URL
        config: Optional enhanced configuration
        
    Returns:
        List of extracted elements
    """
    extractor = EnhancedStealthExtractor(config or EnhancedExtractionConfig())
    return await extractor.extract_with_enhanced_stealth(url)