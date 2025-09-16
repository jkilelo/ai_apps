"""
Stealth Browser Module - Advanced anti-detection capabilities for browser automation

This module provides comprehensive stealth techniques to make browser automation
undetectable by modern anti-bot systems.
"""

import asyncio
import random
import math
import logging
from typing import Optional, Dict, List, Tuple, Any, Union
from datetime import datetime
from playwright.async_api import Page, BrowserContext
from urllib.parse import urlparse

from .browser_profiles import BrowserProfile, ProfileType, get_profile

logger = logging.getLogger(__name__)


class StealthBrowser:
    """
    Provides advanced stealth capabilities for browser automation.
    
    Features:
    - CDP evasion
    - Navigator property spoofing
    - WebRTC leak prevention
    - Canvas fingerprinting protection
    - Human-like behavior simulation
    - Trust building mechanisms
    - Profile-based configuration
    """
    
    def __init__(self, profile: Optional[Union[BrowserProfile, ProfileType, str]] = None):
        self.trust_sessions: Dict[str, Dict[str, Any]] = {}
        self.performance_metrics: Dict[str, Any] = {}
        self.detected_frameworks: Dict[str, str] = {}
        self.captcha_encounters: List[Dict[str, Any]] = []
        
        # Set profile
        if profile is None:
            self.profile = get_profile(ProfileType.STEALTH)
        elif isinstance(profile, BrowserProfile):
            self.profile = profile
        elif isinstance(profile, (ProfileType, str)):
            self.profile = get_profile(ProfileType(profile))
        else:
            raise ValueError(f"Invalid profile type: {type(profile)}")
        
        logger.info(f"StealthBrowser initialized with profile: {self.profile.name}")
    
    async def apply_stealth(self, page: Page, level: Optional[str] = None) -> None:
        """
        Apply stealth techniques to a page based on profile.
        
        Args:
            page: The Playwright page object
            level: Optional override for stealth level - "basic", "enhanced", or "maximum"
                  If not provided, uses profile settings
        """
        # Determine what to apply based on profile
        if level:
            # Legacy compatibility mode
            if level in ["basic", "enhanced", "maximum"]:
                await self._apply_basic_stealth(page)
            
            if level in ["enhanced", "maximum"]:
                await self._apply_enhanced_stealth(page)
            
            if level == "maximum":
                await self._apply_maximum_stealth(page)
        else:
            # Profile-based application
            if self.profile.stealth.hide_webdriver or self.profile.stealth.hide_automation_indicators:
                await self._apply_basic_stealth(page)
            
            if self.profile.stealth.spoof_plugins or self.profile.stealth.spoof_chrome_runtime:
                await self._apply_enhanced_stealth(page)
            
            if self.profile.stealth.prevent_webrtc_leak or self.profile.stealth.spoof_canvas_fingerprint:
                await self._apply_maximum_stealth(page)
    
    async def _apply_basic_stealth(self, page: Page) -> None:
        """Apply basic stealth techniques based on profile"""
        script_parts = []
        
        if self.profile.stealth.hide_webdriver:
            script_parts.append("""
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
        
        if self.profile.stealth.spoof_plugins:
            script_parts.append("""
                // Basic navigator spoofing
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """)
        
        if self.profile.stealth.spoof_languages:
            script_parts.append("""
                // Languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """)
        
        if script_parts:
            await page.add_init_script('\n'.join(script_parts))
    
    async def _apply_enhanced_stealth(self, page: Page) -> None:
        """Apply enhanced stealth techniques"""
        await page.add_init_script("""
            // Enhanced plugin spoofing
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    const plugins = [];
                    const pluginData = [
                        {
                            name: 'Chrome PDF Plugin',
                            filename: 'internal-pdf-viewer',
                            description: 'Portable Document Format'
                        },
                        {
                            name: 'Chrome PDF Viewer',
                            filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                            description: 'Portable Document Format'
                        },
                        {
                            name: 'Native Client',
                            filename: 'internal-nacl-plugin',
                            description: 'Native Client Executable'
                        }
                    ];
                    
                    pluginData.forEach(data => {
                        const plugin = Object.create(Plugin.prototype);
                        plugin.name = data.name;
                        plugin.filename = data.filename;
                        plugin.description = data.description;
                        plugin.length = 1;
                        plugins.push(plugin);
                    });
                    
                    plugins.length = pluginData.length;
                    return plugins;
                }
            });
            
            // Chrome object
            if (!window.chrome) {
                window.chrome = {};
            }
            window.chrome.runtime = {
                connect: () => {},
                sendMessage: () => {},
                onMessage: { 
                    addListener: () => {},
                    removeListener: () => {},
                    hasListener: () => false
                }
            };
            
            // Permissions API
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => {
                if (parameters.name === 'notifications') {
                    return Promise.resolve({ state: 'default' });
                }
                return originalQuery(parameters);
            };
        """)
    
    async def _apply_maximum_stealth(self, page: Page) -> None:
        """Apply maximum stealth techniques including all anti-detection measures"""
        await page.add_init_script("""
            // Remove CDP-specific properties
            delete window.__playwright;
            delete window.__puppeteer_evaluation_script__;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            
            // WebRTC leak prevention
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
            
            // Canvas fingerprinting protection
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            const originalToBlob = HTMLCanvasElement.prototype.toBlob;
            const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
            
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
            
            // Battery API spoofing
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
            
            // Hardware concurrency randomization
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 4 + Math.floor(Math.random() * 4) * 2
            });
            
            // Device memory randomization
            if (navigator.deviceMemory) {
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => [4, 8, 16, 32][Math.floor(Math.random() * 4)]
                });
            }
            
            // Screen properties normalization
            Object.defineProperty(screen, 'availTop', { get: () => 0 });
            Object.defineProperty(screen, 'availLeft', { get: () => 0 });
            Object.defineProperty(screen, 'availWidth', { get: () => screen.width });
            Object.defineProperty(screen, 'availHeight', { get: () => screen.height - 40 });
            
            // Chrome loadTimes
            window.chrome.loadTimes = () => ({
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
            });
            
            // Override toString methods
            window.navigator.permissions.query.toString = () => 'function query() { [native code] }';
            window.navigator.toString = () => '[object Navigator]';
            if (window.chrome && window.chrome.runtime && window.chrome.runtime.sendMessage) {
                window.chrome.runtime.sendMessage.toString = () => 'function sendMessage() { [native code] }';
            }
            
            // WebGL spoofing
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
    
    async def human_like_mouse_move(self, page: Page, target_x: float, target_y: float, 
                                   start_x: Optional[float] = None, start_y: Optional[float] = None) -> None:
        """
        Move mouse with human-like B-spline curve movement.
        
        Args:
            page: The page object
            target_x: Target X coordinate
            target_y: Target Y coordinate
            start_x: Starting X coordinate (optional)
            start_y: Starting Y coordinate (optional)
        """
        if start_x is None or start_y is None:
            # Get current mouse position or use default
            start_x = 0
            start_y = 0
        
        # Generate B-spline curve
        steps = 20 + random.randint(-5, 10)
        curve_points = self._generate_b_spline_curve(start_x, start_y, target_x, target_y, steps)
        
        # Move along curve
        for point in curve_points:
            await page.mouse.move(point['x'], point['y'])
            await asyncio.sleep(random.uniform(0.01, 0.03))
    
    def _generate_b_spline_curve(self, x1: float, y1: float, x2: float, y2: float, steps: int) -> List[Dict[str, float]]:
        """Generate B-spline curve points for natural mouse movement"""
        # Add control points with randomness
        cp1x = x1 + (x2 - x1) * 0.3 + (random.random() - 0.5) * 50
        cp1y = y1 + (y2 - y1) * 0.3 + (random.random() - 0.5) * 50
        cp2x = x1 + (x2 - x1) * 0.7 + (random.random() - 0.5) * 50
        cp2y = y1 + (y2 - y1) * 0.7 + (random.random() - 0.5) * 50
        
        points = []
        for i in range(steps):
            t = i / (steps - 1)
            # Cubic Bezier curve formula
            x = (1-t)**3 * x1 + 3*(1-t)**2*t * cp1x + 3*(1-t)*t**2 * cp2x + t**3 * x2
            y = (1-t)**3 * y1 + 3*(1-t)**2*t * cp1y + 3*(1-t)*t**2 * cp2y + t**3 * y2
            points.append({'x': round(x), 'y': round(y)})
        
        return points
    
    async def human_like_delay(self, min_ms: Optional[int] = None, max_ms: Optional[int] = None, 
                              delay_type: str = "generic") -> None:
        """
        Generate human-like delays with log-normal distribution.
        
        Args:
            min_ms: Minimum delay in milliseconds (uses profile if not provided)
            max_ms: Maximum delay in milliseconds (uses profile if not provided)
            delay_type: Type of delay for profile-based timing
        """
        # Get delays from profile if not provided
        if min_ms is None or max_ms is None:
            timing_map = {
                "element_analysis": self.profile.timing.element_analysis_delay,
                "cookie_wait": self.profile.timing.cookie_consent_wait,
                "cookie_hover": self.profile.timing.cookie_button_hover,
                "cookie_click": self.profile.timing.cookie_post_click,
                "trust_wait": self.profile.timing.trust_initial_wait,
                "trust_hover": self.profile.timing.trust_link_hover,
                "stability": self.profile.timing.stability_initial,
                "challenge": self.profile.timing.challenge_wait,
                "selector_batch": self.profile.timing.selector_batch_delay,
                "event_extraction": self.profile.timing.event_extraction_delay,
                "dynamic_wait": self.profile.timing.dynamic_content_wait,
                "generic": (100, 500)  # Default
            }
            
            delay_range = timing_map.get(delay_type, (100, 500))
            if min_ms is None:
                min_ms = delay_range[0]
            if max_ms is None:
                max_ms = delay_range[1]
        
        mean = (min_ms + max_ms) / 2
        
        try:
            # Generate log-normal delay
            delay = random.lognormvariate(math.log(mean), 0.3)
            delay = max(min_ms, min(max_ms, delay))
        except:
            # Fallback to uniform distribution
            delay = random.uniform(min_ms, max_ms)
        
        await asyncio.sleep(delay / 1000)
    
    async def human_like_typing(self, page: Page, selector: str, text: str) -> None:
        """
        Type text with human-like speed and patterns.
        
        Args:
            page: The page object
            selector: Element selector
            text: Text to type
        """
        element = await page.query_selector(selector)
        if not element:
            return
        
        await element.focus()
        
        for char in text:
            await element.type(char)
            # Variable typing speed
            base_delay = random.randint(80, 150)
            variation = random.randint(-30, 30)
            await asyncio.sleep((base_delay + variation) / 1000)
            
            # Occasional longer pauses
            if random.random() < 0.1:
                await asyncio.sleep(random.uniform(0.3, 0.8))
    
    async def simulate_scrolling(self, page: Page, duration: int = 5000) -> None:
        """
        Simulate human-like scrolling behavior.
        
        Args:
            page: The page object
            duration: Total scrolling duration in milliseconds
        """
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() * 1000 < duration:
            # Random scroll distance
            scroll_distance = random.randint(100, 400)
            
            # Scroll down
            await page.evaluate(f"""
                window.scrollBy({{
                    top: {scroll_distance},
                    behavior: 'smooth'
                }});
            """)
            
            # Random pause
            await self.human_like_delay(300, 1500)
            
            # Occasionally scroll up a bit
            if random.random() < 0.2:
                back_scroll = random.randint(50, 150)
                await page.evaluate(f"""
                    window.scrollBy({{
                        top: -{back_scroll},
                        behavior: 'smooth'
                    }});
                """)
                await self.human_like_delay(200, 600)
    
    async def handle_cookie_consent(self, page: Page) -> bool:
        """
        Handle cookie consent popups intelligently based on profile.
        
        Args:
            page: The page object
            
        Returns:
            bool: True if cookie consent was handled
        """
        if not self.profile.stealth.auto_handle_cookies:
            return False
        
        # Wait for potential cookie banner
        await self.human_like_delay(delay_type="cookie_wait")
        
        for selector in self.profile.stealth.cookie_selectors:
            try:
                button = page.locator(selector).first
                if await button.is_visible():
                    # Move mouse to button
                    box = await button.bounding_box()
                    if box:
                        await self.human_like_mouse_move(
                            page,
                            box['x'] + box['width'] / 2,
                            box['y'] + box['height'] / 2
                        )
                        await self.human_like_delay(delay_type="cookie_hover")
                        await button.click()
                        logger.info(f"Clicked cookie consent: {selector}")
                        await self.human_like_delay(delay_type="cookie_click")
                        return True
            except:
                continue
        
        return False
    
    async def wait_for_framework_ready(self, page: Page) -> Optional[str]:
        """
        Detect and wait for JavaScript framework to be ready.
        
        Returns:
            str: Detected framework name or None
        """
        framework_detected = None
        
        try:
            # React detection
            react_selector = '[data-reactroot], [data-react-root], #root, [data-testid]'
            if await page.query_selector(react_selector):
                framework_detected = 'react'
                try:
                    await page.wait_for_function(
                        "() => window.React || window.ReactDOM || document.querySelector('[data-reactroot]')",
                        timeout=2000
                    )
                except:
                    pass
                await asyncio.sleep(0.5)  # React render cycle
                logger.info("Detected React framework")
            
            # Angular detection
            elif await page.query_selector('[ng-app], [data-ng-app], [ng-controller], [ng-version]'):
                framework_detected = 'angular'
                try:
                    await page.wait_for_function(
                        "() => window.angular || window.ng || document.querySelector('[ng-version]')",
                        timeout=2000
                    )
                except:
                    pass
                logger.info("Detected Angular framework")
            
            # Vue detection
            elif await page.query_selector('[data-v-], #app[data-v-], [v-cloak], .vue-component'):
                framework_detected = 'vue'
                try:
                    await page.wait_for_function(
                        "() => window.Vue || document.querySelector('[data-v-]')",
                        timeout=2000
                    )
                    await page.evaluate("() => window.Vue && Vue.nextTick ? Vue.nextTick() : null")
                except:
                    pass
                logger.info("Detected Vue framework")
            
            # Svelte detection
            elif await page.query_selector('[class*="svelte-"]'):
                framework_detected = 'svelte'
                await asyncio.sleep(0.3)
                logger.info("Detected Svelte framework")
            
            # Next.js detection
            elif await page.query_selector('#__next'):
                framework_detected = 'nextjs'
                await asyncio.sleep(0.5)
                logger.info("Detected Next.js framework")
            
            # Store detected framework
            if framework_detected:
                url = page.url
                self.detected_frameworks[url] = framework_detected
            
        except Exception as e:
            logger.debug(f"Framework detection error: {e}")
        
        return framework_detected
    
    async def detect_and_handle_captcha(self, page: Page) -> Dict[str, Any]:
        """
        Detect CAPTCHA challenges on the page.
        
        Returns:
            Dict containing CAPTCHA information or None
        """
        captcha_info = {
            'detected': False,
            'type': None,
            'selector': None,
            'timestamp': datetime.now()
        }
        
        captcha_selectors = [
            ('recaptcha', 'iframe[src*="recaptcha"], iframe[title*="recaptcha"], .g-recaptcha, #g-recaptcha'),
            ('hcaptcha', 'iframe[src*="hcaptcha"], .h-captcha, [data-hcaptcha]'),
            ('cloudflare', '.cf-browser-verification, #cf-challenge-running, #cf-wrapper'),
            ('funcaptcha', 'div[id*="arkose"], iframe[src*="funcaptcha"]'),
            ('geetest', 'div[class*="geetest"], .geetest_captcha'),
            ('custom', 'div[class*="captcha"], #captcha, [data-captcha], .challenge-form')
        ]
        
        for captcha_type, selector in captcha_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    captcha_info['detected'] = True
                    captcha_info['type'] = captcha_type
                    captcha_info['selector'] = selector
                    
                    # Store CAPTCHA encounter
                    self.captcha_encounters.append({
                        'url': page.url,
                        'type': captcha_type,
                        'timestamp': datetime.now(),
                        'profile': self.profile.name
                    })
                    
                    logger.warning(f"CAPTCHA detected: {captcha_type} at {selector}")
                    
                    # Handle based on type
                    if captcha_type == 'cloudflare':
                        await self.handle_cloudflare_challenge(page)
                    
                    break
            except Exception as e:
                logger.debug(f"Error checking for CAPTCHA {captcha_type}: {e}")
        
        return captcha_info
    
    async def monitor_page_performance(self, page: Page) -> Dict[str, Any]:
        """
        Monitor and report page performance metrics.
        
        Returns:
            Dict containing performance metrics
        """
        try:
            metrics = await page.evaluate("""
                () => {
                    const timing = performance.timing;
                    const paint = performance.getEntriesByType('paint');
                    const resources = performance.getEntriesByType('resource');
                    const navigation = performance.getEntriesByType('navigation')[0];
                    
                    return {
                        // Navigation timing
                        navigationStart: timing.navigationStart,
                        domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                        loadComplete: timing.loadEventEnd - timing.navigationStart,
                        domInteractive: timing.domInteractive - timing.navigationStart,
                        
                        // Paint timing
                        firstPaint: paint.find(p => p.name === 'first-paint')?.startTime || 0,
                        firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
                        
                        // Resource timing
                        resourceCount: resources.length,
                        totalResourceSize: resources.reduce((sum, r) => sum + (r.transferSize || 0), 0),
                        slowestResource: resources.reduce((max, r) => 
                            r.duration > (max?.duration || 0) ? {
                                name: r.name,
                                duration: r.duration,
                                type: r.initiatorType
                            } : max, null),
                        
                        // JavaScript execution
                        jsHeapSize: performance.memory ? performance.memory.usedJSHeapSize : null,
                        
                        // Connection info
                        connectionType: navigator.connection ? navigator.connection.effectiveType : null,
                        
                        // Page size
                        documentSize: document.documentElement.outerHTML.length,
                        domElements: document.querySelectorAll('*').length
                    };
                }
            """)
            
            # Calculate performance score
            metrics['performance_score'] = self._calculate_performance_score(metrics)
            
            # Store metrics
            self.performance_metrics[page.url] = metrics
            
            # Log if performance is poor
            if metrics['performance_score'] < 0.5:
                logger.warning(f"Poor page performance detected: score {metrics['performance_score']:.2f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error monitoring performance: {e}")
            return {}
    
    def _calculate_performance_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall performance score"""
        score = 1.0
        
        # Penalize slow load times
        load_time = metrics.get('loadComplete', 0)
        if load_time > 5000:
            score -= 0.4
        elif load_time > 3000:
            score -= 0.2
        elif load_time > 1500:
            score -= 0.1
        
        # Penalize slow first paint
        fcp = metrics.get('firstContentfulPaint', 0)
        if fcp > 3000:
            score -= 0.3
        elif fcp > 2000:
            score -= 0.2
        elif fcp > 1000:
            score -= 0.1
        
        # Penalize too many resources
        resource_count = metrics.get('resourceCount', 0)
        if resource_count > 150:
            score -= 0.3
        elif resource_count > 100:
            score -= 0.2
        elif resource_count > 50:
            score -= 0.1
        
        # Penalize large DOM
        dom_elements = metrics.get('domElements', 0)
        if dom_elements > 3000:
            score -= 0.2
        elif dom_elements > 1500:
            score -= 0.1
        
        return max(0.0, score)
    
    async def extract_and_validate_links(self, page: Page, domain: str) -> List[Dict[str, Any]]:
        """
        Extract and validate links with quality scoring.
        
        Returns:
            List of validated and scored links
        """
        try:
            links = await page.evaluate("""
                (domain) => {
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    const baseUrl = new URL(domain);
                    
                    return links.map(link => {
                        try {
                            const href = link.href;
                            const url = new URL(href, baseUrl);
                            const rect = link.getBoundingClientRect();
                            
                            return {
                                href: href,
                                text: link.textContent.trim(),
                                title: link.title,
                                isInternal: url.hostname === baseUrl.hostname,
                                isSecure: url.protocol === 'https:',
                                hasTarget: link.target === '_blank',
                                rel: link.rel,
                                isNavigation: link.closest('nav') !== null,
                                isFooter: link.closest('footer') !== null,
                                isHeader: link.closest('header') !== null,
                                isSidebar: link.closest('aside') !== null,
                                depth: url.pathname.split('/').filter(p => p).length,
                                hasQueryParams: url.search.length > 0,
                                anchor: url.hash,
                                ariaLabel: link.getAttribute('aria-label'),
                                isAccessible: link.getAttribute('aria-label') || link.textContent.trim().length > 0,
                                isVisible: rect.width > 0 && rect.height > 0,
                                position: {
                                    x: rect.x,
                                    y: rect.y,
                                    width: rect.width,
                                    height: rect.height
                                }
                            };
                        } catch (e) {
                            return null;
                        }
                    }).filter(l => l && l.isInternal && !l.href.includes('javascript:') && !l.href.includes('mailto:') && l.isVisible);
                }
            """, domain)
            
            # Score and prioritize links
            for link in links:
                link['quality_score'] = self._calculate_link_quality(link)
            
            # Sort by quality score
            links.sort(key=lambda x: x['quality_score'], reverse=True)
            
            return links
            
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            return []
    
    def _calculate_link_quality(self, link: Dict[str, Any]) -> float:
        """Calculate link quality score for prioritization"""
        score = 0.5  # Base score
        
        # Navigation links are high priority
        if link.get('isNavigation'):
            score += 0.3
        elif link.get('isHeader'):
            score += 0.2
        elif link.get('isSidebar'):
            score += 0.1
        
        # Accessible links are better
        if link.get('isAccessible'):
            score += 0.2
        
        # Prefer shallow links
        depth = link.get('depth', 0)
        if depth <= 1:
            score += 0.2
        elif depth <= 2:
            score += 0.1
        elif depth > 4:
            score -= 0.2
        
        # Penalize footer links
        if link.get('isFooter'):
            score -= 0.3
        
        # Secure links are preferred
        if link.get('isSecure'):
            score += 0.1
        
        # Links with text are better
        if link.get('text', '').strip():
            score += 0.1
        
        # Penalize links with many query params
        if link.get('hasQueryParams'):
            score -= 0.1
        
        return min(1.0, max(0.0, score))
    
    async def handle_cloudflare_challenge(self, page: Page, timeout: int = 30000) -> bool:
        """
        Handle Cloudflare and similar anti-bot challenges.
        
        Args:
            page: The page object
            timeout: Maximum time to wait for challenge completion
            
        Returns:
            bool: True if challenge was successfully handled
        """
        challenge_selectors = [
            '.cf-browser-verification',
            '#cf-challenge-running',
            'div[class*="challenge"]',
            'div[id*="challenge"]'
        ]
        
        for selector in challenge_selectors:
            if await page.query_selector(selector):
                logger.info(f"Anti-bot challenge detected: {selector}")
                
                # Wait with human-like patience
                await self.human_like_delay(3000, 5000)
                
                try:
                    # Wait for challenge to complete
                    await page.wait_for_selector(selector, state='hidden', timeout=timeout)
                    
                    # Additional wait after challenge
                    await self.human_like_delay(2000, 3000)
                    return True
                except:
                    logger.warning("Challenge timeout or failed")
                    return False
        
        return False
    
    async def build_trust_enhanced(self, page: Page, domain: str, visit_pages: Optional[int] = None) -> None:
        """
        Enhanced trust building with intelligent navigation and framework awareness.
        
        Args:
            page: The page object
            domain: The domain to build trust for
            visit_pages: Number of pages to visit
        """
        if not self.profile.stealth.build_trust:
            return
        
        # Skip safe domains
        if any(safe in domain for safe in self.profile.stealth.trust_safe_domains):
            logger.info(f"Skipping trust building for safe domain: {domain}")
            return
        
        # Check for existing trust session
        if domain in self.trust_sessions:
            session = self.trust_sessions[domain]
            if (datetime.now() - session['built_at']).total_seconds() < 3600:
                logger.info(f"Using existing trust session for {domain}")
                return
        
        logger.info(f"Building enhanced trust for {domain}")
        
        try:
            # Visit homepage
            await page.goto(f"https://{domain}", wait_until='domcontentloaded')
            
            # Wait for framework to be ready
            framework = await self.wait_for_framework_ready(page)
            
            # Check for CAPTCHA
            captcha_info = await self.detect_and_handle_captcha(page)
            if captcha_info['detected']:
                logger.warning(f"CAPTCHA detected during trust building: {captcha_info['type']}")
                # Continue anyway, CAPTCHA might be handled
            
            # Monitor initial performance
            perf_metrics = await self.monitor_page_performance(page)
            
            # Wait for initial content
            await self.human_like_delay(delay_type="trust_wait")
            
            # Extract and validate links
            links = await self.extract_and_validate_links(page, f"https://{domain}")
            
            # Intelligent link selection
            pages_to_visit = min(
                visit_pages or self.profile.stealth.trust_visit_pages,
                len(links),
                5  # Cap at 5 for efficiency
            )
            
            selected_links = self._select_diverse_links(links, pages_to_visit)
            
            # Simulate reading and scrolling on homepage
            await self.simulate_scrolling(page, duration=3000)
            
            # Visit selected internal pages
            for i, link in enumerate(selected_links):
                try:
                    logger.debug(f"Visiting trust link {i+1}/{len(selected_links)}: {link['text'][:50]}")
                    
                    # Human-like navigation to link
                    await self._navigate_to_link(page, link)
                    
                    # Wait for content
                    await page.wait_for_load_state('domcontentloaded')
                    
                    # Simulate engagement
                    await self._simulate_page_engagement(page)
                    
                    # Back navigation
                    await page.go_back(wait_until='domcontentloaded')
                    
                except Exception as e:
                    logger.debug(f"Error visiting link during trust building: {e}")
                    continue
            
            # Calculate and store trust score
            trust_score = self._calculate_trust_score(perf_metrics, len(selected_links))
            
            # Store enhanced trust session
            self.trust_sessions[domain] = {
                'built_at': datetime.now(),
                'trust_score': trust_score,
                'framework': framework,
                'performance': perf_metrics.get('performance_score', 0),
                'pages_visited': len(selected_links),
                'captcha_encountered': captcha_info['detected']
            }
            
            logger.info(f"Trust building completed for {domain}: score={trust_score:.2f}, framework={framework}")
            
        except Exception as e:
            logger.error(f"Enhanced trust building failed: {e}")
    
    def _select_diverse_links(self, links: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
        """Select diverse high-quality links for trust building"""
        selected = []
        
        # Prioritize high-quality navigation links
        nav_links = [l for l in links if l.get('isNavigation') and l.get('quality_score', 0) > 0.7]
        selected.extend(nav_links[:min(count//2, len(nav_links))])
        
        # Add some header links
        header_links = [l for l in links if l.get('isHeader') and l not in selected]
        remaining = count - len(selected)
        selected.extend(header_links[:min(remaining//2, len(header_links))])
        
        # Add regular content links
        content_links = [l for l in links if not l.get('isFooter') and l not in selected]
        remaining = count - len(selected)
        selected.extend(content_links[:remaining])
        
        return selected
    
    async def _navigate_to_link(self, page: Page, link: Dict[str, Any]) -> None:
        """Navigate to a link with human-like behavior"""
        try:
            # Try to find the element and hover
            elements = await page.query_selector_all(f'a[href="{link["href"]}"]')
            if elements:
                element = elements[0]
                
                # Move mouse to element
                box = await element.bounding_box()
                if box:
                    await self.human_like_mouse_move(
                        page,
                        box['x'] + box['width'] / 2,
                        box['y'] + box['height'] / 2
                    )
                    await self.human_like_delay(200, 500, "trust_hover")
                    await element.click()
                else:
                    # Fallback to navigation
                    await page.goto(link['href'], wait_until='domcontentloaded')
            else:
                await page.goto(link['href'], wait_until='domcontentloaded')
                
        except Exception as e:
            logger.debug(f"Error navigating to link: {e}")
            # Fallback to direct navigation
            await page.goto(link['href'], wait_until='domcontentloaded')
    
    async def _simulate_page_engagement(self, page: Page) -> None:
        """Simulate realistic page engagement"""
        # Scroll patterns
        await self.simulate_scrolling(page, duration=2000)
        
        # Random hover actions
        try:
            elements = await page.query_selector_all('a, button, [role="button"]')
            if elements and len(elements) > 0:
                # Select a few random elements to hover
                hover_count = min(3, len(elements))
                for _ in range(hover_count):
                    element = random.choice(elements)
                    try:
                        box = await element.bounding_box()
                        if box and box['width'] > 0 and box['height'] > 0:
                            await element.hover()
                            await self.human_like_delay(100, 300)
                    except:
                        pass
        except Exception as e:
            logger.debug(f"Error during engagement simulation: {e}")
        
        # Simulate reading time based on content
        try:
            content_length = await page.evaluate("() => document.body.textContent.length")
            reading_time = min(3000, max(500, content_length / 100))  # ~100 chars per second
            await asyncio.sleep(reading_time / 1000)
        except:
            await asyncio.sleep(1)
    
    def _calculate_trust_score(self, perf_metrics: Dict[str, Any], pages_visited: int) -> float:
        """Calculate trust score based on performance and engagement"""
        base_score = 0.5
        
        # Performance contributes to trust
        perf_score = perf_metrics.get('performance_score', 0.5)
        base_score += perf_score * 0.2
        
        # Pages visited contributes to trust
        if pages_visited > 0:
            base_score += min(0.3, pages_visited * 0.1)
        
        return min(1.0, base_score)
    
    async def build_trust(self, page: Page, domain: str, visit_pages: Optional[int] = None) -> None:
        """
        Build trust score by simulating normal browsing behavior.
        
        Args:
            page: The page object
            domain: The domain to build trust for
            visit_pages: Number of pages to visit (uses profile if not provided)
        """
        if not self.profile.stealth.build_trust:
            return
        
        # Skip safe domains
        if any(safe in domain for safe in self.profile.stealth.trust_safe_domains):
            logger.info(f"Skipping trust building for safe domain: {domain}")
            return
        
        if domain in self.trust_sessions:
            # Already built trust recently
            session = self.trust_sessions[domain]
            if (datetime.now() - session['built_at']).total_seconds() < 3600:  # 1 hour
                logger.info(f"Using existing trust session for {domain}")
                return
        
        if visit_pages is None:
            visit_pages = self.profile.stealth.trust_visit_pages
        
        logger.info(f"Building trust for {domain}...")
        
        try:
            # Visit homepage
            await page.goto(f"https://{domain}", wait_until='domcontentloaded')
            await self.human_like_delay(delay_type="trust_wait")
            
            # Simulate reading behavior
            await self.simulate_scrolling(page, duration=3000)
            
            # Visit internal pages
            internal_links = await page.query_selector_all('a[href^="/"]')
            links_to_visit = min(visit_pages, len(internal_links))
            
            for _ in range(links_to_visit):
                try:
                    if not internal_links:
                        break
                    
                    link = random.choice(internal_links)
                    
                    # Move mouse to link
                    box = await link.bounding_box()
                    if box:
                        await self.human_like_mouse_move(
                            page,
                            box['x'] + box['width'] / 2,
                            box['y'] + box['height'] / 2
                        )
                        await self.human_like_delay(delay_type="trust_hover")
                        await link.click()
                        await page.wait_for_load_state('domcontentloaded')
                        await self.simulate_scrolling(page, duration=2000)
                        await page.go_back()
                except:
                    pass
            
            # Store trust session
            self.trust_sessions[domain] = {
                'built_at': datetime.now(),
                'trust_score': 0.7
            }
            
        except Exception as e:
            logger.debug(f"Trust building error: {e}")
    
    def get_random_user_agent(self) -> str:
        """Get a random user agent string from profile"""
        return self.profile.get_user_agent()
    
    def get_browser_context_options(self, stealth_level: Optional[str] = None) -> Dict[str, Any]:
        """
        Get optimized browser context options based on profile.
        
        Args:
            stealth_level: Optional legacy stealth level override
            
        Returns:
            Dict of browser context options
        """
        options = {
            'viewport': self.profile.get_viewport(),
            'user_agent': self.get_random_user_agent(),
            'locale': 'en-US',
            'timezone_id': 'America/New_York',
            'permissions': ['geolocation'],
            'extra_http_headers': self.profile.extra_headers.copy()
        }
        
        # Add enhanced headers if profile suggests it
        if (self.profile.profile_type in [ProfileType.STEALTH, ProfileType.ULTRA_STEALTH] or 
            stealth_level in ["enhanced", "maximum"]):
            options['extra_http_headers'].update({
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"'
            })
        
        return options
    
    def get_browser_launch_args(self) -> List[str]:
        """Get optimized browser launch arguments from profile"""
        return self.profile.launch_args.copy()


    async def wait_for_dynamic_content(self, page: Page, timeout: int = 5000) -> None:
        """
        Smart waiting for dynamic content to load.
        
        Args:
            page: The page object
            timeout: Maximum wait time in milliseconds
        """
        try:
            # Wait for common loading indicators to disappear
            loading_selectors = [
                '.loading', '.spinner', '.loader',
                '[class*="loading"]', '[class*="spinner"]',
                '[class*="skeleton"]', '.shimmer',
                '[aria-busy="true"]', '.placeholder',
                'div[class*="progress"]'
            ]
            
            for selector in loading_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        await page.wait_for_selector(selector, state='hidden', timeout=min(timeout, 2000))
                except:
                    pass  # Selector might not exist or timeout
            
            # Wait for network to be idle
            try:
                await page.wait_for_load_state('networkidle', timeout=timeout)
            except:
                pass
            
            # Wait for framework if detected
            await self.wait_for_framework_ready(page)
            
        except Exception as e:
            logger.debug(f"Dynamic content wait completed with: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of all performance metrics collected"""
        if not self.performance_metrics:
            return {}
        
        all_scores = [m.get('performance_score', 0) for m in self.performance_metrics.values()]
        all_load_times = [m.get('loadComplete', 0) for m in self.performance_metrics.values()]
        
        return {
            'pages_monitored': len(self.performance_metrics),
            'average_score': sum(all_scores) / len(all_scores) if all_scores else 0,
            'average_load_time': sum(all_load_times) / len(all_load_times) if all_load_times else 0,
            'slowest_page': max(self.performance_metrics.items(), 
                              key=lambda x: x[1].get('loadComplete', 0))[0] if self.performance_metrics else None,
            'fastest_page': min(self.performance_metrics.items(), 
                              key=lambda x: x[1].get('loadComplete', float('inf')))[0] if self.performance_metrics else None
        }
    
    def get_captcha_summary(self) -> Dict[str, Any]:
        """Get summary of CAPTCHA encounters"""
        if not self.captcha_encounters:
            return {'total_encounters': 0, 'types': {}}
        
        types_count = {}
        for encounter in self.captcha_encounters:
            captcha_type = encounter.get('type', 'unknown')
            types_count[captcha_type] = types_count.get(captcha_type, 0) + 1
        
        return {
            'total_encounters': len(self.captcha_encounters),
            'types': types_count,
            'last_encounter': self.captcha_encounters[-1] if self.captcha_encounters else None
        }
    
    def get_framework_summary(self) -> Dict[str, List[str]]:
        """Get summary of detected frameworks"""
        frameworks = {}
        for url, framework in self.detected_frameworks.items():
            if framework not in frameworks:
                frameworks[framework] = []
            frameworks[framework].append(url)
        return frameworks


# Default singleton instance with stealth profile
stealth_browser = StealthBrowser(ProfileType.STEALTH)

# Factory function for creating stealth browsers with specific profiles
def create_stealth_browser(profile: Union[BrowserProfile, ProfileType, str]) -> StealthBrowser:
    """Create a stealth browser with a specific profile"""
    return StealthBrowser(profile)