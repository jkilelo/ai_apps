"""
Stealth Element Extractor with Anti-Detection Capabilities
Incorporates advanced stealth features from ui_web_auto_testing
"""

import asyncio
import json
import random
import hashlib
import logging
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from playwright.async_api import Browser, BrowserContext, Page, Error as PlaywrightError

from ui_testing_v2.models.database import ExtractedElement, ElementType, ElementInteractionType
from ui_testing_v2.services.ai_services import AIService, AIServiceFactory
from ui_testing_v2.services.cache import CacheService, CacheKey
from ui_testing_v2.core.config import Config
from ui_testing_v2.components.element_extractor import (
    PlaywrightExtractionStrategy,
    ElementExtractor
)

logger = logging.getLogger(__name__)


class DetectionMethod(Enum):
    """Method used to detect element"""
    RULE_BASED = "rule_based"
    SEMANTIC_AI = "semantic_ai"
    ML_CLASSIFICATION = "ml_classification"
    VISUAL_PATTERN = "visual_pattern"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    SHADOW_DOM = "shadow_dom"
    DYNAMIC_CONTENT = "dynamic_content"


@dataclass
class AntiDetectionConfig:
    """Configuration for anti-detection measures"""
    randomize_delays: bool = True
    min_delay: float = 0.5
    max_delay: float = 3.0
    randomize_viewport: bool = True
    rotate_user_agents: bool = True
    use_stealth_mode: bool = True
    simulate_human_behavior: bool = True
    avoid_bot_patterns: bool = True
    randomize_mouse_movements: bool = True
    use_canvas_fingerprint_protection: bool = True
    spoof_timezone: bool = True
    hide_automation_indicators: bool = True


@dataclass
class SemanticPattern:
    """Semantic pattern for AI-powered element detection"""
    pattern_id: str
    element_type: ElementType
    semantic_keywords: List[str]
    visual_characteristics: Dict[str, Any]
    behavioral_indicators: List[str]
    context_clues: List[str]
    confidence_threshold: float
    detection_method: DetectionMethod


class StealthElementExtractor(PlaywrightExtractionStrategy):
    """
    Enhanced element extractor with stealth capabilities
    Combines best practices from ui_web_auto_testing with our AI-powered analysis
    """
    
    def __init__(self, config: Config, anti_detection_config: Optional[AntiDetectionConfig] = None):
        super().__init__(config)
        self.anti_detection = anti_detection_config or AntiDetectionConfig()
        
        # User agents for rotation
        self.user_agents = [
            # Chrome on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # Chrome on Mac
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # Firefox on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            # Safari on Mac
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            # Edge on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0"
        ]
        
        # Viewport sizes for randomization
        self.viewports = [
            {"width": 1920, "height": 1080},  # Full HD
            {"width": 1366, "height": 768},   # Popular laptop
            {"width": 1440, "height": 900},   # MacBook
            {"width": 1536, "height": 864},   # Surface
            {"width": 1600, "height": 900},   # HD+
            {"width": 1680, "height": 1050},  # WSXGA+
            {"width": 2560, "height": 1440},  # QHD
        ]
        
        # Initialize semantic patterns
        self.semantic_patterns = self._initialize_semantic_patterns()
        
        # Track human behavior simulation
        self.last_action_time = None
        self.action_count = 0
        
    def _initialize_semantic_patterns(self) -> List[SemanticPattern]:
        """Initialize semantic patterns for enhanced detection"""
        return [
            SemanticPattern(
                pattern_id="login_form",
                element_type=ElementType.FORM,
                semantic_keywords=["login", "sign in", "authenticate", "log in", "signin", "username", "password"],
                visual_characteristics={"has_password_field": True, "has_username_field": True},
                behavioral_indicators=["submit_action", "validation", "form_submission"],
                context_clues=["forgot password", "remember me", "create account", "stay signed in"],
                confidence_threshold=0.85,
                detection_method=DetectionMethod.SEMANTIC_AI
            ),
            SemanticPattern(
                pattern_id="search_box",
                element_type=ElementType.INPUT,
                semantic_keywords=["search", "find", "query", "look for", "browse", "filter"],
                visual_characteristics={"is_input_field": True, "has_search_icon": True, "has_placeholder": True},
                behavioral_indicators=["autocomplete", "search_suggestions", "instant_results"],
                context_clues=["results", "filter", "sort", "categories"],
                confidence_threshold=0.9,
                detection_method=DetectionMethod.SEMANTIC_AI
            ),
            SemanticPattern(
                pattern_id="shopping_cart",
                element_type=ElementType.BUTTON,
                semantic_keywords=["add to cart", "buy now", "purchase", "checkout", "add to bag", "add to basket"],
                visual_characteristics={"contains_price": True, "near_product_info": True, "has_icon": True},
                behavioral_indicators=["cart_update", "quantity_change", "price_calculation"],
                context_clues=["price", "quantity", "product", "total", "shipping"],
                confidence_threshold=0.88,
                detection_method=DetectionMethod.SEMANTIC_AI
            ),
            SemanticPattern(
                pattern_id="navigation_menu",
                element_type=ElementType.OTHER,
                semantic_keywords=["menu", "navigation", "nav", "home", "about", "contact", "products", "services"],
                visual_characteristics={"is_list": True, "horizontal_or_vertical": True, "has_links": True},
                behavioral_indicators=["hover_effects", "dropdown", "active_state"],
                context_clues=["main menu", "site navigation", "quick links"],
                confidence_threshold=0.82,
                detection_method=DetectionMethod.SEMANTIC_AI
            ),
            SemanticPattern(
                pattern_id="modal_dialog",
                element_type=ElementType.OTHER,
                semantic_keywords=["modal", "dialog", "popup", "overlay", "lightbox"],
                visual_characteristics={"has_overlay": True, "centered": True, "has_close_button": True},
                behavioral_indicators=["dismiss_action", "overlay_click", "escape_key"],
                context_clues=["close", "cancel", "confirm", "ok"],
                confidence_threshold=0.87,
                detection_method=DetectionMethod.SEMANTIC_AI
            ),
            SemanticPattern(
                pattern_id="cookie_banner",
                element_type=ElementType.OTHER,
                semantic_keywords=["cookie", "privacy", "gdpr", "consent", "accept cookies", "cookie policy"],
                visual_characteristics={"fixed_position": True, "bottom_or_top": True, "has_buttons": True},
                behavioral_indicators=["accept_action", "reject_action", "settings_action"],
                context_clues=["accept", "reject", "manage", "preferences", "necessary"],
                confidence_threshold=0.92,
                detection_method=DetectionMethod.SEMANTIC_AI
            )
        ]
    
    def get_random_user_agent(self) -> str:
        """Get a random user agent for rotation"""
        return random.choice(self.user_agents) if self.anti_detection.rotate_user_agents else self.user_agents[0]
    
    def get_random_viewport(self) -> Dict[str, int]:
        """Get a random viewport size"""
        return random.choice(self.viewports) if self.anti_detection.randomize_viewport else self.viewports[0]
    
    async def setup_stealth_context(self, context: BrowserContext):
        """Setup stealth mode for browser context"""
        if not self.anti_detection.use_stealth_mode:
            return
        
        logger.info("Setting up stealth browser context")
        
        # Inject stealth scripts
        await self._inject_stealth_scripts(context)
        
        # Set random user agent if not already set
        if self.anti_detection.rotate_user_agents:
            # User agent should be set during context creation
            logger.debug(f"User agent rotation enabled")
        
        # Configure permissions
        await context.grant_permissions(["geolocation"])
        
    async def _inject_stealth_scripts(self, context: BrowserContext):
        """Inject comprehensive stealth JavaScript"""
        stealth_script = """
        // Override webdriver detection
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
            configurable: true
        });
        
        // Remove automation indicators
        delete navigator.__proto__.webdriver;
        
        // Mock plugins to appear more human
        Object.defineProperty(navigator, 'plugins', {
            get: () => {
                return [
                    { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                    { name: 'Chrome PDF Viewer', filename: 'internal-pdf-viewer' },
                    { name: 'Native Client', filename: 'internal-nacl-plugin' }
                ];
            },
            configurable: true
        });
        
        // Mock languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en', 'zh-CN', 'zh'],
            configurable: true
        });
        
        // Mock hardware concurrency
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8,
            configurable: true
        });
        
        // Mock device memory
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8,
            configurable: true
        });
        
        // Canvas fingerprinting protection
        if (""" + str(self.anti_detection.use_canvas_fingerprint_protection).lower() + """) {
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            const originalToBlob = HTMLCanvasElement.prototype.toBlob;
            const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
            
            // Add noise to canvas
            const addNoise = (data) => {
                for (let i = 0; i < data.length; i += 4) {
                    data[i] = data[i] + (Math.random() * 0.5 - 0.25);
                    data[i + 1] = data[i + 1] + (Math.random() * 0.5 - 0.25);
                    data[i + 2] = data[i + 2] + (Math.random() * 0.5 - 0.25);
                }
                return data;
            };
            
            HTMLCanvasElement.prototype.toDataURL = function() {
                const context = this.getContext('2d');
                if (context) {
                    const imageData = context.getImageData(0, 0, this.width, this.height);
                    imageData.data = addNoise(imageData.data);
                    context.putImageData(imageData, 0, 0);
                }
                return originalToDataURL.apply(this, arguments);
            };
        }
        
        // WebGL fingerprinting protection
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) return 'Intel Inc.';
            if (parameter === 37446) return 'Intel Iris OpenGL Engine';
            return getParameter.apply(this, arguments);
        };
        
        // Chrome runtime object
        window.chrome = {
            runtime: {
                connect: () => {},
                sendMessage: () => {},
                onMessage: { addListener: () => {} }
            },
            loadTimes: function() {
                return {
                    requestTime: Date.now() / 1000,
                    startLoadTime: Date.now() / 1000,
                    commitLoadTime: Date.now() / 1000,
                    finishLoadTime: Date.now() / 1000
                };
            },
            csi: function() { return {}; },
            app: {}
        };
        
        // Notification permission override
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => {
            if (parameters.name === 'notifications') {
                return Promise.resolve({ state: 'default' });
            }
            return originalQuery(parameters);
        };
        
        // Battery API spoofing
        if ('getBattery' in navigator) {
            navigator.getBattery = () => {
                return Promise.resolve({
                    charging: true,
                    chargingTime: 0,
                    dischargingTime: Infinity,
                    level: 0.99,
                    onchargingchange: null,
                    onchargingtimechange: null,
                    ondischargingtimechange: null,
                    onlevelchange: null
                });
            };
        }
        
        // Timezone spoofing
        if (""" + str(self.anti_detection.spoof_timezone).lower() + """) {
            Date.prototype.getTimezoneOffset = function() { return -300; };  // EST
            Intl.DateTimeFormat.prototype.resolvedOptions = function() {
                return {
                    timeZone: 'America/New_York',
                    locale: 'en-US'
                };
            };
        }
        
        // Console.debug removal (many detection scripts use it)
        const originalConsoleDebug = console.debug;
        console.debug = () => {};
        
        // Remove Cypress and Selenium indicators
        delete window.Cypress;
        delete window.__selenium_unwrapped;
        delete window.__webdriver_evaluate;
        delete window.__driver_evaluate;
        delete window.__webdriver_unwrapped;
        delete window.__driver_unwrapped;
        delete window.__selenium_evaluate;
        delete window.__fxdriver_evaluate;
        delete window.__fxdriver_unwrapped;
        """
        
        await context.add_init_script(stealth_script)
        logger.debug("Stealth scripts injected successfully")
    
    async def simulate_human_behavior(self, page: Page):
        """Simulate human-like behavior on the page"""
        if not self.anti_detection.simulate_human_behavior:
            return
        
        try:
            # Add human-like delay since last action
            await self._human_like_delay()
            
            # Random mouse movements
            if self.anti_detection.randomize_mouse_movements:
                await self._simulate_mouse_movements(page)
            
            # Natural scrolling pattern
            await self._simulate_scrolling(page)
            
            # Simulate reading time
            await self._simulate_reading_pause()
            
            # Update action tracking
            self.last_action_time = datetime.now()
            self.action_count += 1
            
        except Exception as e:
            logger.debug(f"Error simulating human behavior: {e}")
    
    async def _human_like_delay(self):
        """Add human-like delays between actions"""
        if not self.anti_detection.randomize_delays:
            return
        
        # Calculate delay based on action count (humans slow down over time)
        base_delay = self.anti_detection.min_delay
        fatigue_factor = min(1.5, 1 + (self.action_count * 0.05))
        
        delay = random.uniform(
            base_delay * fatigue_factor,
            self.anti_detection.max_delay * fatigue_factor
        )
        
        await asyncio.sleep(delay)
    
    async def _simulate_mouse_movements(self, page: Page):
        """Simulate natural mouse movements"""
        try:
            # Get page dimensions
            viewport = page.viewport_size
            if not viewport:
                return
            
            width = viewport['width']
            height = viewport['height']
            
            # Generate smooth mouse path
            movements = random.randint(2, 5)
            
            for i in range(movements):
                # Use bezier curve-like movements
                x = random.randint(int(width * 0.1), int(width * 0.9))
                y = random.randint(int(height * 0.1), int(height * 0.9))
                
                # Add micro-movements (human jitter)
                for _ in range(random.randint(1, 3)):
                    micro_x = x + random.randint(-5, 5)
                    micro_y = y + random.randint(-5, 5)
                    await page.mouse.move(micro_x, micro_y, steps=random.randint(5, 10))
                    await asyncio.sleep(random.uniform(0.01, 0.05))
                
                await page.mouse.move(x, y, steps=random.randint(10, 20))
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
        except Exception as e:
            logger.debug(f"Error in mouse movement simulation: {e}")
    
    async def _simulate_scrolling(self, page: Page):
        """Simulate natural scrolling patterns"""
        try:
            # Get page height
            page_height = await page.evaluate("() => document.body.scrollHeight")
            viewport_height = await page.evaluate("() => window.innerHeight")
            
            if page_height <= viewport_height:
                return  # No need to scroll
            
            # Simulate reading pattern (scroll down, sometimes back up)
            scroll_positions = []
            current_pos = 0
            
            # Generate natural scroll positions
            while current_pos < page_height - viewport_height:
                # Usually scroll down 
                next_pos = current_pos + random.randint(100, 500)
                
                # Sometimes scroll back up a bit (re-reading)
                if random.random() < 0.2 and len(scroll_positions) > 0:
                    next_pos = current_pos - random.randint(50, 150)
                
                next_pos = max(0, min(next_pos, page_height - viewport_height))
                scroll_positions.append(next_pos)
                current_pos = next_pos
                
                if len(scroll_positions) > 10:  # Limit scrolling
                    break
            
            # Execute scrolling
            for pos in scroll_positions:
                await page.evaluate(f"window.scrollTo({{top: {pos}, behavior: 'smooth'}})")
                await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # Scroll back to top sometimes
            if random.random() < 0.3:
                await page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
                
        except Exception as e:
            logger.debug(f"Error in scrolling simulation: {e}")
    
    async def _simulate_reading_pause(self):
        """Simulate reading pause"""
        if random.random() < 0.3:  # 30% chance of reading pause
            await asyncio.sleep(random.uniform(1.0, 3.0))
    
    async def extract_shadow_dom_elements(self, page: Page) -> List[Dict[str, Any]]:
        """Extract elements from shadow DOM"""
        try:
            shadow_elements = await page.evaluate("""
                () => {
                    const elements = [];
                    const extractFromShadow = (root, hostPath = '') => {
                        const allElements = root.querySelectorAll('*');
                        
                        allElements.forEach(element => {
                            // Check if element has shadow root
                            if (element.shadowRoot) {
                                const shadowPath = hostPath + ' > ' + element.tagName.toLowerCase();
                                extractFromShadow(element.shadowRoot, shadowPath);
                            }
                            
                            // Extract element info
                            const rect = element.getBoundingClientRect();
                            if (rect.width > 0 && rect.height > 0) {
                                elements.push({
                                    tagName: element.tagName.toLowerCase(),
                                    text: element.textContent?.trim() || '',
                                    id: element.id || '',
                                    className: element.className || '',
                                    attributes: Array.from(element.attributes || []).reduce((acc, attr) => {
                                        acc[attr.name] = attr.value;
                                        return acc;
                                    }, {}),
                                    shadowPath: hostPath,
                                    boundingBox: {
                                        x: rect.x,
                                        y: rect.y,
                                        width: rect.width,
                                        height: rect.height
                                    },
                                    isVisible: rect.width > 0 && rect.height > 0,
                                    isShadowElement: true
                                });
                            }
                        });
                    };
                    
                    // Start from document and check all elements for shadow roots
                    document.querySelectorAll('*').forEach(element => {
                        if (element.shadowRoot) {
                            extractFromShadow(element.shadowRoot, element.tagName.toLowerCase());
                        }
                    });
                    
                    return elements;
                }
            """)
            
            logger.info(f"Extracted {len(shadow_elements)} shadow DOM elements")
            return shadow_elements
            
        except Exception as e:
            logger.error(f"Error extracting shadow DOM elements: {e}")
            return []
    
    async def detect_semantic_patterns(self, page: Page, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply semantic pattern detection to identify element purposes"""
        enhanced_elements = []
        
        for element in elements:
            element_copy = element.copy()
            matched_patterns = []
            
            # Check each semantic pattern
            for pattern in self.semantic_patterns:
                confidence = self._calculate_pattern_confidence(element, pattern)
                
                if confidence >= pattern.confidence_threshold:
                    matched_patterns.append({
                        'pattern_id': pattern.pattern_id,
                        'confidence': confidence,
                        'element_type': pattern.element_type.value,
                        'detection_method': pattern.detection_method.value
                    })
            
            # Add semantic analysis to element
            if matched_patterns:
                # Sort by confidence and take the best match
                best_match = max(matched_patterns, key=lambda x: x['confidence'])
                element_copy['semantic_pattern'] = best_match
                element_copy['detection_method'] = best_match['detection_method']
                
                # Update element type based on semantic pattern
                if best_match['element_type'] != 'other':
                    element_copy['element_type'] = ElementType[best_match['element_type'].upper()]
            
            enhanced_elements.append(element_copy)
        
        return enhanced_elements
    
    def _calculate_pattern_confidence(self, element: Dict[str, Any], pattern: SemanticPattern) -> float:
        """Calculate confidence score for pattern matching"""
        confidence = 0.0
        factors = 0
        
        # Check semantic keywords
        element_text = (element.get('text', '') + ' ' + 
                       element.get('inner_text', '') + ' ' + 
                       str(element.get('attributes', {}))).lower()
        
        keyword_matches = sum(1 for keyword in pattern.semantic_keywords if keyword in element_text)
        if keyword_matches > 0:
            confidence += (keyword_matches / len(pattern.semantic_keywords)) * 0.4
            factors += 1
        
        # Check visual characteristics
        visual_matches = 0
        for char_key, char_value in pattern.visual_characteristics.items():
            if char_key == 'has_password_field' and char_value:
                if element.get('attributes', {}).get('type') == 'password':
                    visual_matches += 1
            elif char_key == 'is_input_field' and char_value:
                if element.get('tag_name') in ['input', 'textarea']:
                    visual_matches += 1
            elif char_key == 'has_search_icon' and char_value:
                if 'search' in element_text or '🔍' in element_text:
                    visual_matches += 1
        
        if len(pattern.visual_characteristics) > 0:
            confidence += (visual_matches / len(pattern.visual_characteristics)) * 0.3
            factors += 1
        
        # Check context clues
        context_matches = sum(1 for clue in pattern.context_clues if clue in element_text)
        if context_matches > 0:
            confidence += (context_matches / len(pattern.context_clues)) * 0.3
            factors += 1
        
        return confidence if factors > 0 else 0.0
    
    async def wait_for_dynamic_content(self, page: Page):
        """Smart waiting for dynamic content to load"""
        try:
            # Wait for common loading indicators to disappear
            loading_selectors = [
                '.loading', '.spinner', '.loader',
                '[class*="loading"]', '[class*="spinner"]',
                '[class*="skeleton"]', '.shimmer',
                '[aria-busy="true"]'
            ]
            
            for selector in loading_selectors:
                try:
                    await page.wait_for_selector(selector, state='hidden', timeout=1000)
                except:
                    pass  # Selector might not exist
            
            # Wait for network to be idle
            await page.wait_for_load_state('networkidle', timeout=5000)
            
            # Additional wait for JavaScript frameworks
            await self._wait_for_framework_ready(page)
            
        except Exception as e:
            logger.debug(f"Dynamic content wait completed with: {e}")
    
    async def _wait_for_framework_ready(self, page: Page):
        """Wait for JavaScript frameworks to be ready"""
        try:
            # Angular
            await page.evaluate("""
                () => {
                    if (window.angular) {
                        return new Promise(resolve => {
                            angular.element(document).ready(() => resolve());
                        });
                    }
                }
            """)
            
            # React
            await page.evaluate("""
                () => {
                    if (window.React || document.querySelector('[data-reactroot]')) {
                        return new Promise(resolve => setTimeout(resolve, 500));
                    }
                }
            """)
            
            # Vue
            await page.evaluate("""
                () => {
                    if (window.Vue || document.querySelector('[data-v-]')) {
                        return new Promise(resolve => {
                            if (window.Vue) {
                                Vue.nextTick(() => resolve());
                            } else {
                                setTimeout(resolve, 500);
                            }
                        });
                    }
                }
            """)
            
        except Exception as e:
            logger.debug(f"Framework ready check: {e}")
    
    async def extract_elements(
        self, 
        page: Page, 
        selectors: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Enhanced element extraction with stealth features
        """
        try:
            # Simulate human behavior before extraction
            await self.simulate_human_behavior(page)
            
            # Wait for dynamic content
            await self.wait_for_dynamic_content(page)
            
            # Extract regular DOM elements
            regular_elements = await super().extract_elements(page, selectors)
            
            # Extract shadow DOM elements
            shadow_elements = await self.extract_shadow_dom_elements(page)
            
            # Combine all elements
            all_elements = regular_elements + shadow_elements
            
            # Apply semantic pattern detection
            enhanced_elements = await self.detect_semantic_patterns(page, all_elements)
            
            # Add stealth metadata
            for element in enhanced_elements:
                element['extraction_metadata'] = {
                    'stealth_mode': self.anti_detection.use_stealth_mode,
                    'user_agent': page.context.browser.version if hasattr(page.context, 'browser') else 'unknown',
                    'detection_method': element.get('detection_method', 'rule_based'),
                    'is_shadow_element': element.get('isShadowElement', False),
                    'semantic_pattern': element.get('semantic_pattern', None)
                }
            
            logger.info(f"Extracted {len(enhanced_elements)} elements with stealth mode")
            return enhanced_elements
            
        except Exception as e:
            logger.error(f"Stealth element extraction failed: {e}")
            # Fallback to regular extraction
            return await super().extract_elements(page, selectors)


class StealthBrowserManager:
    """Manager for stealth browser contexts"""
    
    def __init__(self, config: Config, anti_detection_config: Optional[AntiDetectionConfig] = None):
        self.config = config
        self.anti_detection = anti_detection_config or AntiDetectionConfig()
        self.extractor = StealthElementExtractor(config, self.anti_detection)
    
    async def create_stealth_context(self, browser: Browser) -> BrowserContext:
        """Create a browser context with stealth configuration"""
        
        # Get random configuration
        viewport = self.extractor.get_random_viewport()
        user_agent = self.extractor.get_random_user_agent()
        
        # Create context with stealth options
        context_options = {
            "viewport": viewport,
            "user_agent": user_agent,
            "locale": "en-US",
            "timezone_id": "America/New_York" if self.anti_detection.spoof_timezone else None,
            "permissions": ["geolocation"],
            "color_scheme": "light",
            "reduced_motion": "no-preference",
            "forced_colors": "none",
            # Additional privacy options
            "accept_downloads": True,
            "has_touch": False,
            "is_mobile": False,
            "device_scale_factor": 1,
            "offline": False,
            "http_credentials": None,
            "ignore_https_errors": False,
            "java_script_enabled": True,
            "bypass_csp": False,
            "extra_http_headers": {
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1"
            }
        }
        
        # Create context
        context = await browser.new_context(**context_options)
        
        # Setup stealth scripts
        await self.extractor.setup_stealth_context(context)
        
        logger.info(f"Created stealth browser context with viewport {viewport} and UA: {user_agent[:50]}...")
        
        return context
    
    async def extract_with_stealth(
        self,
        url: str,
        browser: Browser,
        selectors: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Extract elements from URL using stealth browser"""
        
        context = None
        page = None
        
        try:
            # Create stealth context
            context = await self.create_stealth_context(browser)
            
            # Create new page
            page = await context.new_page()
            
            # Navigate to URL with stealth behavior
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Extract elements with stealth features
            elements = await self.extractor.extract_elements(page, selectors)
            
            return elements
            
        finally:
            if page:
                await page.close()
            if context:
                await context.close()


# Export main classes
__all__ = [
    'StealthElementExtractor',
    'StealthBrowserManager',
    'AntiDetectionConfig',
    'SemanticPattern',
    'DetectionMethod'
]