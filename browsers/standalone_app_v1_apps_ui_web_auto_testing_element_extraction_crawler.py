"""
Advanced Web Crawler for UI Testing

This module provides comprehensive web crawling capabilities with:
- Multi-strategy element extraction
- Smart pagination detection
- Dynamic content handling
- Performance monitoring
- Accessibility compliance checking
"""

import asyncio
import json
import hashlib
import random
import re
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from urllib.parse import urljoin, urlparse
from playwright.async_api import Page, Browser, BrowserContext, ElementHandle
import time
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import difflib
import logging
from collections import defaultdict, Counter


class DetectionMethod(Enum):
    """Method used to detect element"""
    RULE_BASED = "rule_based"
    SEMANTIC_AI = "semantic_ai"
    ML_CLASSIFICATION = "ml_classification"
    VISUAL_PATTERN = "visual_pattern"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    SHADOW_DOM = "shadow_dom"
    DYNAMIC_CONTENT = "dynamic_content"


class ConfidenceLevel(Enum):
    """Confidence levels for element detection"""
    LOW = 0.3
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.95


class ElementType(Enum):
    """Enhanced element type classification"""

    BUTTON = "button"
    INPUT = "input"
    LINK = "link"
    FORM = "form"
    NAVIGATION = "navigation"
    TABLE = "table"
    LIST = "list"
    IMAGE = "image"
    MODAL = "modal"
    DROPDOWN = "dropdown"
    TAB = "tab"
    ACCORDION = "accordion"
    CARD = "card"
    PAGINATION = "pagination"
    SEARCH = "search"
    FILTER = "filter"
    CAROUSEL = "carousel"
    TOOLTIP = "tooltip"
    BREADCRUMB = "breadcrumb"
    SIDEBAR = "sidebar"
    HEADER = "header"
    FOOTER = "footer"
    PROGRESS_BAR = "progress_bar"
    LOADING_SPINNER = "loading_spinner"
    NOTIFICATION = "notification"
    ALERT = "alert"
    CHATBOT = "chatbot"
    VIDEO_PLAYER = "video_player"
    AUDIO_PLAYER = "audio_player"
    CALENDAR = "calendar"
    CHART = "chart"
    MAP = "map"
    SLIDER = "slider"
    RATING = "rating"
    SOCIAL_SHARE = "social_share"
    COMMENT_SECTION = "comment_section"
    PRICE_DISPLAY = "price_display"
    COUNTDOWN_TIMER = "countdown_timer"
    CAPTCHA = "captcha"


class LocatorStrategy(Enum):
    """Locator strategy priority"""

    DATA_TESTID = "data-testid"
    ID = "id"
    NAME = "name"
    ARIA_LABEL = "aria-label"
    CSS_CLASS = "css-class"
    CSS_SELECTOR = "css-selector"
    XPATH = "xpath"
    TEXT_CONTENT = "text-content"
    ROLE = "role"


@dataclass
class ElementLocator:
    """Element locator with strategy and reliability score"""

    strategy: LocatorStrategy
    value: str
    reliability_score: float  # 0.0 to 1.0
    is_unique: bool
    context: Optional[str] = None
    shadow_dom_path: Optional[str] = None
    requires_wait: bool = False
    wait_condition: Optional[str] = None


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


@dataclass
class ElementData:
    """Comprehensive element data structure"""

    element_id: str  # Unique identifier
    element_type: ElementType
    tag_name: str
    text_content: str
    locators: List[ElementLocator]
    attributes: Dict[str, str]
    accessibility: Dict[str, Any]
    visual_properties: Dict[str, Any]
    behavioral_properties: Dict[str, Any]
    context: Dict[str, Any]
    interactions: List[str]  # Possible interactions
    test_scenarios: List[str]  # Suggested test scenarios
    page_url: str
    extraction_timestamp: str
    detection_method: DetectionMethod
    confidence_score: float
    semantic_analysis: Dict[str, Any]
    ml_features: Dict[str, Any]
    shadow_dom_info: Optional[Dict[str, Any]] = None
    dynamic_properties: Dict[str, Any] = None
    ai_classification: Dict[str, Any] = None


@dataclass
class PageStructure:
    """Page structure analysis"""

    page_type: str
    has_navigation: bool
    has_forms: bool
    has_tables: bool
    has_modals: bool
    has_pagination: bool
    responsive_breakpoints: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    accessibility_score: float
    seo_elements: Dict[str, Any]


@dataclass
class CrawlResult:
    """Complete crawl result"""

    url: str
    title: str
    elements: List[ElementData]
    page_structure: PageStructure
    metadata: Dict[str, Any]
    linked_pages: List["CrawlResult"] = None
    crawl_duration: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


class AdvancedWebCrawler:
    """Advanced web crawler with AI-powered element extraction"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.visited_urls: Set[str] = set()
        self.crawl_stats = {"pages_crawled": 0, "elements_extracted": 0, "errors": 0}
        
        # Advanced configurations
        self.anti_detection = AntiDetectionConfig(**self.config.get('anti_detection', {}))
        self.semantic_patterns = self._initialize_semantic_patterns()
        self.ml_classifier = None
        self.retry_config = self.config.get('retry_config', {
            'max_retries': 3,
            'base_delay': 1.0,
            'max_delay': 30.0,
            'backoff_factor': 2.0
        })
        
        # Session management
        self.session_data = {}
        self.cookies_jar = {}
        self.request_history = []
        
        # User agent rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        # Logging setup
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _initialize_semantic_patterns(self) -> List[SemanticPattern]:
        """Initialize semantic patterns for AI-powered detection"""
        return [
            SemanticPattern(
                pattern_id="login_form",
                element_type=ElementType.FORM,
                semantic_keywords=["login", "sign in", "authenticate", "log in", "signin"],
                visual_characteristics={"has_password_field": True, "has_email_or_username": True},
                behavioral_indicators=["submit_action", "validation"],
                context_clues=["forgot password", "remember me", "create account"],
                confidence_threshold=0.8,
                detection_method=DetectionMethod.SEMANTIC_AI
            ),
            SemanticPattern(
                pattern_id="shopping_cart",
                element_type=ElementType.BUTTON,
                semantic_keywords=["add to cart", "buy now", "purchase", "checkout", "add to bag"],
                visual_characteristics={"contains_price": True, "near_product_info": True},
                behavioral_indicators=["cart_update", "quantity_change"],
                context_clues=["price", "quantity", "product", "total"],
                confidence_threshold=0.85,
                detection_method=DetectionMethod.SEMANTIC_AI
            ),
            SemanticPattern(
                pattern_id="search_box",
                element_type=ElementType.SEARCH,
                semantic_keywords=["search", "find", "query", "look for"],
                visual_characteristics={"is_input_field": True, "has_search_icon": True},
                behavioral_indicators=["autocomplete", "search_suggestions"],
                context_clues=["results", "filter", "sort"],
                confidence_threshold=0.9,
                detection_method=DetectionMethod.SEMANTIC_AI
            ),
            SemanticPattern(
                pattern_id="captcha",
                element_type=ElementType.CAPTCHA,
                semantic_keywords=["captcha", "recaptcha", "verify", "robot", "human"],
                visual_characteristics={"contains_puzzle": True, "has_checkbox": True},
                behavioral_indicators=["verification_required"],
                context_clues=["security", "verify", "prove", "not a robot"],
                confidence_threshold=0.95,
                detection_method=DetectionMethod.SEMANTIC_AI
            )
        ]

    async def initialize(self, playwright):
        """Initialize browser and context"""
        browser_type = self.config.get("browser", "chromium")
        headless = self.config.get("headless", True)

        if browser_type == "chromium":
            self.browser = await playwright.chromium.launch(headless=headless)
        elif browser_type == "firefox":
            self.browser = await playwright.firefox.launch(headless=headless)
        elif browser_type == "webkit":
            self.browser = await playwright.webkit.launch(headless=headless)

        # Create context with enhanced anti-detection settings
        viewport = self._get_random_viewport() if self.anti_detection.randomize_viewport else {"width": 1920, "height": 1080}
        user_agent = random.choice(self.user_agents) if self.anti_detection.rotate_user_agents else self.user_agents[0]
        
        context_options = {
            "viewport": viewport,
            "user_agent": user_agent,
            "java_script_enabled": True,
            "accept_downloads": False,
            "ignore_https_errors": True,
            "bypass_csp": True,
            "extra_http_headers": self._get_realistic_headers(),
        }
        
        # Add stealth mode configurations
        if self.anti_detection.use_stealth_mode:
            context_options.update({
                "permissions": ["geolocation"],
                "geolocation": {"latitude": 40.7128, "longitude": -74.0060},  # NYC coordinates
                "timezone_id": "America/New_York",
                "locale": "en-US",
            })
        
        self.context = await self.browser.new_context(**context_options)
        
        # Add stealth scripts to avoid detection
        if self.anti_detection.use_stealth_mode:
            await self._add_stealth_scripts()

    def _get_random_viewport(self) -> Dict[str, int]:
        """Generate random viewport size to avoid detection"""
        viewports = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1536, "height": 864},
            {"width": 1440, "height": 900},
            {"width": 1280, "height": 720},
        ]
        return random.choice(viewports)
    
    def _get_realistic_headers(self) -> Dict[str, str]:
        """Generate realistic HTTP headers"""
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }
    
    async def _add_stealth_scripts(self):
        """Add JavaScript to make the browser less detectable"""
        stealth_script = """
        // Override navigator.webdriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        // Mock plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        // Mock languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        
        // Override permission query
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Cypress.env('permissionNotification') || 'denied' }) :
                originalQuery(parameters)
        );
        
        // Add chrome runtime
        window.chrome = {
            runtime: {},
        };
        """
        await self.context.add_init_script(stealth_script)
    
    async def _human_like_delay(self):
        """Add human-like delays between actions"""
        if self.anti_detection.randomize_delays:
            delay = random.uniform(self.anti_detection.min_delay, self.anti_detection.max_delay)
            await asyncio.sleep(delay)
    
    async def _simulate_human_behavior(self, page: Page):
        """Simulate human-like behavior on the page"""
        if not self.anti_detection.simulate_human_behavior:
            return
            
        # Random mouse movements
        if self.anti_detection.randomize_mouse_movements:
            for _ in range(random.randint(1, 3)):
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                await page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # Random scrolling
        scroll_amount = random.randint(100, 500)
        await page.evaluate(f"window.scrollBy(0, {scroll_amount});")
        await asyncio.sleep(random.uniform(0.5, 1.0))
    
    async def crawl_website(
        self, url: str, max_depth: int = 2, max_pages: int = 50
    ) -> CrawlResult:
        """Main crawling method with comprehensive analysis"""
        start_time = time.time()

        try:
            # Reset stats
            self.visited_urls.clear()
            self.crawl_stats = {
                "pages_crawled": 0,
                "elements_extracted": 0,
                "errors": 0,
                "retries": 0,
                "captcha_detected": 0,
                "shadow_dom_elements": 0,
                "dynamic_elements": 0,
            }

            # Crawl the main page with retry mechanism
            result = await self._crawl_with_retry(url, max_depth, max_pages)
            result.crawl_duration = time.time() - start_time

            return result

        except Exception as e:
            return CrawlResult(
                url=url,
                title="",
                elements=[],
                page_structure=PageStructure(
                    page_type="unknown",
                    has_navigation=False,
                    has_forms=False,
                    has_tables=False,
                    has_modals=False,
                    has_pagination=False,
                    responsive_breakpoints=[],
                    performance_metrics={},
                    accessibility_score=0.0,
                    seo_elements={},
                ),
                metadata=self.crawl_stats,
                crawl_duration=time.time() - start_time,
                success=False,
                error_message=str(e),
            )

    async def _crawl_with_retry(
        self, url: str, max_depth: int, max_pages: int
    ) -> CrawlResult:
        """Crawl with intelligent retry mechanism"""
        last_exception = None
        
        for attempt in range(self.retry_config['max_retries'] + 1):
            try:
                return await self._crawl_single_page(url, max_depth, max_pages)
            except Exception as e:
                last_exception = e
                self.crawl_stats["retries"] += 1
                
                if attempt < self.retry_config['max_retries']:
                    delay = min(
                        self.retry_config['base_delay'] * (self.retry_config['backoff_factor'] ** attempt),
                        self.retry_config['max_delay']
                    )
                    
                    # Add jitter to avoid thundering herd
                    jitter = random.uniform(0, delay * 0.1)
                    await asyncio.sleep(delay + jitter)
                    
                    self.logger.warning(f"Retry attempt {attempt + 1} for {url} after error: {e}")
                else:
                    self.logger.error(f"Max retries exceeded for {url}: {e}")
                    break
        
        # Return error result if all retries failed
        return CrawlResult(
            url=url,
            title="",
            elements=[],
            page_structure=PageStructure(
                page_type="unknown",
                has_navigation=False,
                has_forms=False,
                has_tables=False,
                has_modals=False,
                has_pagination=False,
                responsive_breakpoints=[],
                performance_metrics={},
                accessibility_score=0.0,
                seo_elements={},
            ),
            metadata=self.crawl_stats,
            crawl_duration=0.0,
            success=False,
            error_message=str(last_exception),
        )
    
    async def _crawl_single_page(
        self, url: str, max_depth: int, max_pages: int
    ) -> CrawlResult:
        """Crawl a single page with full analysis"""
        if url in self.visited_urls or len(self.visited_urls) >= max_pages:
            return None

        self.visited_urls.add(url)
        page = await self.context.new_page()

        try:
            # Add human-like behavior before navigation
            await self._human_like_delay()
            
            # Navigate with performance monitoring
            start_nav = time.time()
            response = await page.goto(url, wait_until="networkidle", timeout=30000)
            nav_time = time.time() - start_nav

            # Simulate human behavior after page load
            await self._simulate_human_behavior(page)
            
            # Wait for dynamic content with smart detection
            await self._wait_for_dynamic_content(page)
            
            # Check for CAPTCHA
            if await self._detect_captcha(page):
                self.crawl_stats["captcha_detected"] += 1
                self.logger.warning(f"CAPTCHA detected on {url}")
                # Could implement CAPTCHA solving here

            # Extract page metadata
            title = await page.title()
            current_url = page.url

            # Extract all elements using advanced techniques
            elements = await self._extract_all_elements_advanced(page)

            # Analyze page structure
            page_structure = await self._analyze_page_structure(page)

            # Get performance metrics
            performance_metrics = await self._get_performance_metrics(page, nav_time)
            page_structure.performance_metrics = performance_metrics

            # Calculate accessibility score
            page_structure.accessibility_score = (
                await self._calculate_accessibility_score(elements)
            )

            # Extract SEO elements
            page_structure.seo_elements = await self._extract_seo_elements(page)

            # Crawl linked pages if depth allows
            linked_pages = []
            if max_depth > 1:
                links = await self._extract_valid_links(page, url)
                for link_url in links[:10]:  # Limit links per page
                    linked_result = await self._crawl_single_page(
                        link_url, max_depth - 1, max_pages
                    )
                    if linked_result and linked_result.success:
                        linked_pages.append(linked_result)

            # Update stats
            self.crawl_stats["pages_crawled"] += 1
            self.crawl_stats["elements_extracted"] += len(elements)

            return CrawlResult(
                url=current_url,
                title=title,
                elements=elements,
                page_structure=page_structure,
                metadata={
                    "response_status": response.status if response else None,
                    "page_size": len(await page.content()),
                    "crawl_timestamp": datetime.now().isoformat(),
                    **self.crawl_stats,
                },
                linked_pages=linked_pages,
                success=True,
            )

        except Exception as e:
            self.crawl_stats["errors"] += 1
            self._log_error(e, f"crawling {url}")
            raise e
        finally:
            await page.close()

    async def _extract_all_elements(self, page: Page) -> List[ElementData]:
        """Extract all elements with comprehensive analysis"""
        elements = []

        # Enhanced selectors with better categorization
        element_selectors = {
            ElementType.BUTTON: [
                "button",
                "input[type='button']",
                "input[type='submit']",
                "[role='button']",
                "a[onclick]",
                ".btn",
                ".button",
            ],
            ElementType.INPUT: [
                "input:not([type='button']):not([type='submit'])",
                "textarea",
                "select",
                "[contenteditable='true']",
            ],
            ElementType.LINK: ["a[href]", "[role='link']"],
            ElementType.FORM: ["form", "[role='form']"],
            ElementType.NAVIGATION: [
                "nav",
                "[role='navigation']",
                ".navbar",
                ".nav",
                ".menu",
            ],
            ElementType.TABLE: ["table", "[role='table']", ".table", ".data-table"],
            ElementType.MODAL: ["[role='dialog']", ".modal", ".popup", ".overlay"],
            ElementType.DROPDOWN: [
                "select",
                "[role='combobox']",
                ".dropdown",
                ".select",
            ],
            ElementType.TAB: ["[role='tab']", ".tab", ".tab-item"],
            ElementType.PAGINATION: [
                ".pagination",
                ".pager",
                "[aria-label*='pagination']",
            ],
            ElementType.SEARCH: [
                "input[type='search']",
                "input[placeholder*='search']",
                ".search-box",
                ".search-input",
            ],
        }

        for element_type, selectors in element_selectors.items():
            for selector in selectors:
                try:
                    page_elements = await page.query_selector_all(selector)

                    for element in page_elements:
                        element_data = await self._extract_element_data(
                            element, element_type, page
                        )
                        if element_data:
                            elements.append(element_data)

                except Exception as e:
                    print(
                        f"Failed to extract {element_type} with selector {selector}: {e}"
                    )

        # Remove duplicates based on element_id
        unique_elements = {}
        for element in elements:
            unique_elements[element.element_id] = element

        return list(unique_elements.values())
    
    async def _extract_shadow_dom_elements(self, page: Page) -> List[ElementData]:
        """Extract elements from shadow DOM"""
        shadow_elements = []
        
        try:
            # Find all elements with shadow DOM
            shadow_hosts = await page.evaluate("""
                () => {
                    const hosts = [];
                    const walker = document.createTreeWalker(
                        document.body,
                        NodeFilter.SHOW_ELEMENT,
                        {
                            acceptNode: function(node) {
                                return node.shadowRoot ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP;
                            }
                        }
                    );
                    
                    let node;
                    while (node = walker.nextNode()) {
                        hosts.push({
                            tagName: node.tagName,
                            id: node.id,
                            className: node.className,
                            outerHTML: node.outerHTML.substring(0, 500)
                        });
                    }
                    
                    return hosts;
                }
            """)
            
            for host_info in shadow_hosts:
                self.crawl_stats["shadow_dom_elements"] += 1
                # Create shadow DOM element data
                shadow_element = ElementData(
                    element_id=f"shadow_{hashlib.md5(host_info['outerHTML'].encode()).hexdigest()[:12]}",
                    element_type=ElementType.NAVIGATION,  # Default type
                    tag_name=host_info['tagName'].lower(),
                    text_content="Shadow DOM Host",
                    locators=[],
                    attributes={"class": host_info.get('className', ''), "id": host_info.get('id', '')},
                    accessibility={},
                    visual_properties={},
                    behavioral_properties={},
                    context={"is_shadow_host": True},
                    interactions=["shadow_dom_access"],
                    test_scenarios=["Verify shadow DOM content accessibility"],
                    page_url=page.url,
                    extraction_timestamp=datetime.now().isoformat(),
                    detection_method=DetectionMethod.SHADOW_DOM,
                    confidence_score=0.8,
                    semantic_analysis={},
                    ml_features={},
                    shadow_dom_info={"host_info": host_info}
                )
                shadow_elements.append(shadow_element)
                
        except Exception as e:
            self.logger.error(f"Error extracting shadow DOM elements: {e}")
        
        return shadow_elements
    
    async def _extract_semantic_elements(self, page: Page) -> List[ElementData]:
        """Extract elements using semantic AI analysis"""
        semantic_elements = []
        
        try:
            # Get page content for semantic analysis
            page_content = await page.evaluate("""
                () => {
                    const elements = [];
                    const allElements = document.querySelectorAll('*');
                    
                    allElements.forEach(el => {
                        if (el.textContent && el.textContent.trim().length > 0) {
                            elements.push({
                                tagName: el.tagName.toLowerCase(),
                                textContent: el.textContent.trim().substring(0, 200),
                                className: el.className,
                                id: el.id,
                                attributes: Array.from(el.attributes).reduce((acc, attr) => {
                                    acc[attr.name] = attr.value;
                                    return acc;
                                }, {}),
                                boundingRect: el.getBoundingClientRect(),
                                computedStyle: {
                                    display: getComputedStyle(el).display,
                                    visibility: getComputedStyle(el).visibility,
                                    position: getComputedStyle(el).position
                                }
                            });
                        }
                    });
                    
                    return elements.slice(0, 100); // Limit for performance
                }
            """)
            
            # Apply semantic patterns
            for element_info in page_content:
                for pattern in self.semantic_patterns:
                    confidence = self._calculate_semantic_confidence(element_info, pattern)
                    
                    if confidence >= pattern.confidence_threshold:
                        semantic_element = ElementData(
                            element_id=f"semantic_{hashlib.md5(str(element_info).encode()).hexdigest()[:12]}",
                            element_type=pattern.element_type,
                            tag_name=element_info['tagName'],
                            text_content=element_info['textContent'],
                            locators=[],
                            attributes=element_info['attributes'],
                            accessibility={},
                            visual_properties=element_info.get('computedStyle', {}),
                            behavioral_properties={},
                            context={"semantic_pattern": pattern.pattern_id},
                            interactions=[],
                            test_scenarios=[],
                            page_url=page.url,
                            extraction_timestamp=datetime.now().isoformat(),
                            detection_method=DetectionMethod.SEMANTIC_AI,
                            confidence_score=confidence,
                            semantic_analysis={
                                "pattern_matched": pattern.pattern_id,
                                "keywords_found": self._find_matching_keywords(element_info['textContent'], pattern.semantic_keywords),
                                "confidence": confidence
                            },
                            ml_features={}
                        )
                        semantic_elements.append(semantic_element)
                        
        except Exception as e:
            self.logger.error(f"Error in semantic element extraction: {e}")
        
        return semantic_elements
    
    def _calculate_semantic_confidence(self, element_info: Dict, pattern: SemanticPattern) -> float:
        """Calculate confidence score for semantic pattern matching"""
        confidence = 0.0
        text = element_info['textContent'].lower()
        
        # Keyword matching
        keyword_matches = sum(1 for keyword in pattern.semantic_keywords if keyword in text)
        if pattern.semantic_keywords:
            confidence += (keyword_matches / len(pattern.semantic_keywords)) * 0.4
        
        # Visual characteristics matching
        for characteristic, expected in pattern.visual_characteristics.items():
            if characteristic == "has_password_field" and expected:
                # Check if nearby elements contain password inputs
                if "password" in str(element_info.get('attributes', {})).lower():
                    confidence += 0.2
            elif characteristic == "has_email_or_username" and expected:
                if any(field in str(element_info.get('attributes', {})).lower() 
                      for field in ["email", "username", "user"]):
                    confidence += 0.2
        
        # Context clues
        context_matches = sum(1 for clue in pattern.context_clues if clue in text)
        if pattern.context_clues:
            confidence += (context_matches / len(pattern.context_clues)) * 0.2
        
        return min(1.0, confidence)
    
    def _find_matching_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Find matching keywords in text"""
        text_lower = text.lower()
        return [keyword for keyword in keywords if keyword in text_lower]
    
    async def _apply_ml_classification(self, elements: List[ElementData], page: Page) -> List[ElementData]:
        """Apply machine learning classification to enhance element detection"""
        try:
            # Extract features for ML
            features = []
            for element in elements:
                feature_vector = self._extract_ml_features(element)
                features.append(feature_vector)
            
            if not features:
                return elements
            
            # Simple clustering to identify similar elements
            if len(features) > 3:
                try:
                    # Convert to numpy array for clustering
                    feature_matrix = np.array([list(f.values()) for f in features])
                    
                    # Apply K-means clustering
                    n_clusters = min(5, len(features))
                    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                    clusters = kmeans.fit_predict(feature_matrix)
                    
                    # Update elements with cluster information
                    for i, element in enumerate(elements):
                        element.ml_features = features[i]
                        element.ai_classification = {
                            "cluster_id": int(clusters[i]),
                            "cluster_confidence": float(1.0 - min(np.linalg.norm(feature_matrix[i] - kmeans.cluster_centers_[clusters[i]]) / 10, 1.0))
                        }
                        
                except Exception as e:
                    self.logger.warning(f"ML clustering failed: {e}")
            
        except Exception as e:
            self.logger.error(f"Error in ML classification: {e}")
        
        return elements
    
    def _extract_ml_features(self, element: ElementData) -> Dict[str, float]:
        """Extract numerical features for ML classification"""
        features = {
            "text_length": len(element.text_content),
            "has_id": 1.0 if element.attributes.get("id") else 0.0,
            "has_class": 1.0 if element.attributes.get("class") else 0.0,
            "is_button": 1.0 if element.element_type == ElementType.BUTTON else 0.0,
            "is_input": 1.0 if element.element_type == ElementType.INPUT else 0.0,
            "is_link": 1.0 if element.element_type == ElementType.LINK else 0.0,
            "has_onclick": 1.0 if "onclick" in element.attributes else 0.0,
            "has_href": 1.0 if "href" in element.attributes else 0.0,
            "has_aria_label": 1.0 if element.accessibility.get("aria_label") else 0.0,
            "is_visible": 1.0 if element.visual_properties.get("is_visible") else 0.0,
            "confidence_score": element.confidence_score,
            "num_locators": len(element.locators),
            "num_interactions": len(element.interactions)
        }
        
        return features
    
    def _merge_and_deduplicate_elements(self, elements: List[ElementData]) -> List[ElementData]:
        """Merge similar elements and remove duplicates"""
        unique_elements = {}
        
        for element in elements:
            # Create a signature for similarity checking
            signature = self._create_element_signature(element)
            
            if signature in unique_elements:
                # Merge with existing element
                existing = unique_elements[signature]
                merged = self._merge_elements(existing, element)
                unique_elements[signature] = merged
            else:
                unique_elements[signature] = element
        
        return list(unique_elements.values())
    
    def _create_element_signature(self, element: ElementData) -> str:
        """Create a signature for element similarity"""
        # Use tag name, text content, and main attributes for signature
        key_parts = [
            element.tag_name,
            element.text_content[:50],  # First 50 chars
            element.attributes.get("id", ""),
            element.attributes.get("class", "")[:50]
        ]
        
        signature = "|".join(str(part) for part in key_parts)
        return hashlib.md5(signature.encode()).hexdigest()
    
    def _merge_elements(self, element1: ElementData, element2: ElementData) -> ElementData:
        """Merge two similar elements, keeping the best information"""
        # Choose the element with higher confidence
        primary = element1 if element1.confidence_score >= element2.confidence_score else element2
        secondary = element2 if element1.confidence_score >= element2.confidence_score else element1
        
        # Merge locators
        all_locators = primary.locators + secondary.locators
        unique_locators = []
        seen_locators = set()
        
        for locator in all_locators:
            locator_key = f"{locator.strategy.value}:{locator.value}"
            if locator_key not in seen_locators:
                unique_locators.append(locator)
                seen_locators.add(locator_key)
        
        # Merge other properties
        merged_element = ElementData(
            element_id=primary.element_id,
            element_type=primary.element_type,
            tag_name=primary.tag_name,
            text_content=primary.text_content if len(primary.text_content) > len(secondary.text_content) else secondary.text_content,
            locators=unique_locators,
            attributes={**secondary.attributes, **primary.attributes},  # Primary attributes override
            accessibility={**secondary.accessibility, **primary.accessibility},
            visual_properties={**secondary.visual_properties, **primary.visual_properties},
            behavioral_properties={**secondary.behavioral_properties, **primary.behavioral_properties},
            context={**secondary.context, **primary.context},
            interactions=list(set(primary.interactions + secondary.interactions)),
            test_scenarios=list(set(primary.test_scenarios + secondary.test_scenarios)),
            page_url=primary.page_url,
            extraction_timestamp=primary.extraction_timestamp,
            detection_method=primary.detection_method,
            confidence_score=max(primary.confidence_score, secondary.confidence_score),
            semantic_analysis={**secondary.semantic_analysis, **primary.semantic_analysis},
            ml_features={**secondary.ml_features, **primary.ml_features},
            shadow_dom_info=primary.shadow_dom_info or secondary.shadow_dom_info,
            dynamic_properties=primary.dynamic_properties or secondary.dynamic_properties,
            ai_classification=primary.ai_classification or secondary.ai_classification
        )
        
        return merged_element
    
    async def simulate_advanced_interactions(self, page: Page, elements: List[ElementData]) -> Dict[str, Any]:
        """Simulate advanced interactions with detected elements"""
        interaction_results = {
            "total_interactions": 0,
            "successful_interactions": 0,
            "failed_interactions": 0,
            "interaction_details": [],
            "performance_metrics": {}
        }
        
        for element in elements[:10]:  # Limit to first 10 elements for performance
            if not element.interactions:
                continue
                
            for interaction in element.interactions[:3]:  # Test up to 3 interactions per element
                try:
                    result = await self._simulate_element_interaction(page, element, interaction)
                    interaction_results["interaction_details"].append(result)
                    interaction_results["total_interactions"] += 1
                    
                    if result["success"]:
                        interaction_results["successful_interactions"] += 1
                    else:
                        interaction_results["failed_interactions"] += 1
                        
                except Exception as e:
                    interaction_results["failed_interactions"] += 1
                    interaction_results["interaction_details"].append({
                        "element_id": element.element_id,
                        "interaction": interaction,
                        "success": False,
                        "error": str(e)
                    })
        
        return interaction_results
    
    async def _simulate_element_interaction(self, page: Page, element: ElementData, interaction: str) -> Dict[str, Any]:
        """Simulate a specific interaction with an element"""
        start_time = time.time()
        result = {
            "element_id": element.element_id,
            "interaction": interaction,
            "success": False,
            "duration": 0.0,
            "error": None,
            "before_state": {},
            "after_state": {},
            "side_effects": []
        }
        
        try:
            # Find the best locator for the element
            best_locator = self._get_best_locator(element.locators)
            if not best_locator:
                result["error"] = "No viable locator found"
                return result
            
            # Wait for element to be available
            await page.wait_for_selector(best_locator.value, timeout=5000)
            element_handle = await page.query_selector(best_locator.value)
            
            if not element_handle:
                result["error"] = "Element not found"
                return result
            
            # Capture before state
            result["before_state"] = await self._capture_element_state(page, element_handle)
            
            # Perform the interaction
            success = await self._perform_interaction(page, element_handle, interaction, element)
            result["success"] = success
            
            # Add human-like delay
            await self._human_like_delay()
            
            # Capture after state
            result["after_state"] = await self._capture_element_state(page, element_handle)
            
            # Detect side effects
            result["side_effects"] = await self._detect_interaction_side_effects(page, interaction)
            
        except Exception as e:
            result["error"] = str(e)
        
        result["duration"] = time.time() - start_time
        return result
    
    def _get_best_locator(self, locators: List[ElementLocator]) -> Optional[ElementLocator]:
        """Get the best locator based on reliability score"""
        if not locators:
            return None
        
        # Sort by reliability score and return the best one
        sorted_locators = sorted(locators, key=lambda x: x.reliability_score, reverse=True)
        return sorted_locators[0]
    
    async def _capture_element_state(self, element_handle) -> Dict[str, Any]:
        """Capture the current state of an element"""
        try:
            state = await element_handle.evaluate("""
                el => {
                    const rect = el.getBoundingClientRect();
                    const style = getComputedStyle(el);
                    
                    return {
                        visible: el.offsetWidth > 0 && el.offsetHeight > 0,
                        enabled: !el.disabled,
                        focused: document.activeElement === el,
                        value: el.value || el.textContent || '',
                        checked: el.checked,
                        selected: el.selected,
                        classes: el.className,
                        styles: {
                            display: style.display,
                            visibility: style.visibility,
                            opacity: style.opacity
                        },
                        position: {
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height
                        }
                    };
                }
            """)
            return state
        except:
            return {}
    
    async def _perform_interaction(self, page: Page, element_handle, interaction: str, element_data: ElementData) -> bool:
        """Perform the actual interaction"""
        try:
            if interaction == "click":
                await element_handle.click()
                return True
            
            elif interaction == "double_click":
                await element_handle.dblclick()
                return True
            
            elif interaction == "right_click":
                await element_handle.click(button="right")
                return True
            
            elif interaction == "hover":
                await element_handle.hover()
                return True
            
            elif interaction == "focus":
                await element_handle.focus()
                return True
            
            elif interaction == "blur":
                await element_handle.blur()
                return True
            
            elif interaction in ["type", "fill"]:
                if element_data.element_type == ElementType.INPUT:
                    test_value = self._generate_test_input(element_data)
                    await element_handle.fill(test_value)
                    return True
            
            elif interaction == "clear":
                await element_handle.fill("")
                return True
            
            elif interaction in ["check", "uncheck"]:
                current_state = await element_handle.is_checked()
                if (interaction == "check" and not current_state) or (interaction == "uncheck" and current_state):
                    await element_handle.click()
                return True
            
            elif interaction == "select_option":
                if element_data.tag_name == "select":
                    options = await element_handle.query_selector_all("option")
                    if options:
                        await options[0].click()
                    return True
            
            elif interaction == "upload_file":
                # Create a dummy file for testing
                test_file_path = "/tmp/test_upload.txt"
                with open(test_file_path, "w") as f:
                    f.write("Test file content")
                await element_handle.set_input_files(test_file_path)
                return True
            
            elif interaction == "drag":
                # Simple drag simulation
                box = await element_handle.bounding_box()
                if box:
                    await page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                    await page.mouse.down()
                    await page.mouse.move(box["x"] + 50, box["y"] + 50)
                    await page.mouse.up()
                return True
            
            elif interaction == "keyboard_navigate":
                await element_handle.focus()
                await page.keyboard.press("Tab")
                return True
            
            else:
                return False
                
        except Exception as e:
            self.logger.warning(f"Interaction {interaction} failed: {e}")
            return False
    
    def _generate_test_input(self, element_data: ElementData) -> str:
        """Generate appropriate test input for different input types"""
        input_type = element_data.attributes.get("type", "text").lower()
        placeholder = element_data.attributes.get("placeholder", "").lower()
        name = element_data.attributes.get("name", "").lower()
        
        if input_type == "email" or "email" in placeholder or "email" in name:
            return "test@example.com"
        elif input_type == "password" or "password" in placeholder or "password" in name:
            return "TestPassword123!"
        elif input_type == "tel" or "phone" in placeholder or "phone" in name:
            return "+1234567890"
        elif input_type == "url" or "url" in placeholder or "website" in name:
            return "https://example.com"
        elif input_type == "number" or "number" in placeholder:
            return "42"
        elif input_type == "date":
            return "2024-01-01"
        elif "name" in placeholder or "name" in name:
            return "John Doe"
        elif "search" in placeholder or "search" in name:
            return "test search"
        else:
            return "Test input"
    
    async def _detect_interaction_side_effects(self, page: Page, interaction: str) -> List[str]:
        """Detect side effects of interactions"""
        side_effects = []
        
        try:
            # Check for page navigation
            current_url = page.url
            if hasattr(self, '_last_url') and current_url != self._last_url:
                side_effects.append("page_navigation")
            self._last_url = current_url
            
            # Check for new elements (modals, popups, etc.)
            modal_selectors = ["[role='dialog']", ".modal", ".popup", ".overlay"]
            for selector in modal_selectors:
                if await page.query_selector(selector):
                    side_effects.append("modal_opened")
                    break
            
            # Check for alerts
            try:
                await page.wait_for_event("dialog", timeout=1000)
                side_effects.append("alert_triggered")
            except:
                pass
            
            # Check for loading states
            loading_selectors = [".loading", ".spinner", "[data-loading='true']"]
            for selector in loading_selectors:
                if await page.query_selector(selector):
                    side_effects.append("loading_triggered")
                    break
            
            # Check for form validation messages
            error_selectors = [".error", ".invalid", "[aria-invalid='true']", ".field-error"]
            for selector in error_selectors:
                if await page.query_selector(selector):
                    side_effects.append("validation_error")
                    break
            
            # Check for success messages
            success_selectors = [".success", ".valid", ".confirmation", ".alert-success"]
            for selector in success_selectors:
                if await page.query_selector(selector):
                    side_effects.append("success_message")
                    break
                    
        except Exception as e:
            side_effects.append(f"detection_error: {str(e)}")
        
        return side_effects

    async def _extract_element_data(
        self, element, element_type: ElementType, page: Page
    ) -> Optional[ElementData]:
        """Extract comprehensive data for a single element"""
        try:
            # Generate unique element ID
            element_id = await self._generate_element_id(element)

            # Basic properties
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            text_content = (await element.text_content() or "").strip()[:200]

            # Extract attributes
            attributes = await self._extract_all_attributes(element)

            # Generate locators with reliability scores
            locators = await self._generate_robust_locators(element, page)

            # Extract accessibility information
            accessibility = await self._extract_accessibility_data(element)

            # Get visual properties
            visual_properties = await self._extract_visual_properties(element)

            # Analyze behavioral properties
            behavioral_properties = await self._analyze_behavioral_properties(
                element, element_type
            )

            # Get element context
            context = await self._get_element_context(element)

            # Determine possible interactions
            interactions = await self._determine_interactions(element, element_type)

            # Generate test scenarios
            test_scenarios = await self._generate_test_scenarios(
                element, element_type, text_content
            )

            return ElementData(
                element_id=element_id,
                element_type=element_type,
                tag_name=tag_name,
                text_content=text_content,
                locators=locators,
                attributes=attributes,
                accessibility=accessibility,
                visual_properties=visual_properties,
                behavioral_properties=behavioral_properties,
                context=context,
                interactions=interactions,
                test_scenarios=test_scenarios,
                page_url=page.url,
                extraction_timestamp=datetime.now().isoformat(),
                detection_method=DetectionMethod.RULE_BASED,
                confidence_score=0.7,  # Default confidence for rule-based detection
                semantic_analysis={},
                ml_features={},
                shadow_dom_info=None,
                dynamic_properties=None,
                ai_classification=None
            )

        except Exception as e:
            print(f"Failed to extract element data: {e}")
            return None

    async def _generate_element_id(self, element) -> str:
        """Generate unique element identifier"""
        try:
            # Get unique properties
            tag = await element.evaluate("el => el.tagName.toLowerCase()")
            text = (await element.text_content() or "").strip()[:50]
            id_attr = await element.get_attribute("id") or ""
            class_attr = await element.get_attribute("class") or ""

            # Create hash-based unique ID
            unique_string = f"{tag}:{text}:{id_attr}:{class_attr}"
            return hashlib.md5(unique_string.encode()).hexdigest()[:12]

        except Exception:
            return f"elem_{int(time.time() * 1000)}"

    async def _extract_all_attributes(self, element) -> Dict[str, str]:
        """Extract all element attributes"""
        try:
            return await element.evaluate(
                """
                el => {
                    const attrs = {};
                    for (let attr of el.attributes) {
                        attrs[attr.name] = attr.value;
                    }
                    return attrs;
                }
            """
            )
        except Exception:
            return {}

    async def _generate_robust_locators(
        self, element, page: Page
    ) -> List[ElementLocator]:
        """Generate multiple locator strategies with reliability scores"""
        locators = []

        try:
            # Data-testid (highest reliability)
            test_id = await element.get_attribute("data-testid")
            if test_id:
                is_unique = await self._check_locator_uniqueness(
                    page, f"[data-testid='{test_id}']"
                )
                locators.append(
                    ElementLocator(
                        strategy=LocatorStrategy.DATA_TESTID,
                        value=f"[data-testid='{test_id}']",
                        reliability_score=0.95 if is_unique else 0.7,
                        is_unique=is_unique,
                    )
                )

            # ID attribute
            element_id = await element.get_attribute("id")
            if element_id:
                is_unique = await self._check_locator_uniqueness(page, f"#{element_id}")
                locators.append(
                    ElementLocator(
                        strategy=LocatorStrategy.ID,
                        value=f"#{element_id}",
                        reliability_score=0.9 if is_unique else 0.5,
                        is_unique=is_unique,
                    )
                )

            # Name attribute
            name = await element.get_attribute("name")
            if name:
                is_unique = await self._check_locator_uniqueness(
                    page, f"[name='{name}']"
                )
                locators.append(
                    ElementLocator(
                        strategy=LocatorStrategy.NAME,
                        value=f"[name='{name}']",
                        reliability_score=0.8 if is_unique else 0.4,
                        is_unique=is_unique,
                    )
                )

            # ARIA label
            aria_label = await element.get_attribute("aria-label")
            if aria_label:
                is_unique = await self._check_locator_uniqueness(
                    page, f"[aria-label='{aria_label}']"
                )
                locators.append(
                    ElementLocator(
                        strategy=LocatorStrategy.ARIA_LABEL,
                        value=f"[aria-label='{aria_label}']",
                        reliability_score=0.75 if is_unique else 0.4,
                        is_unique=is_unique,
                    )
                )

            # Role attribute
            role = await element.get_attribute("role")
            if role:
                is_unique = await self._check_locator_uniqueness(
                    page, f"[role='{role}']"
                )
                locators.append(
                    ElementLocator(
                        strategy=LocatorStrategy.ROLE,
                        value=f"[role='{role}']",
                        reliability_score=0.6 if is_unique else 0.3,
                        is_unique=is_unique,
                    )
                )

            # CSS selector (context-aware)
            css_selector = await self._generate_css_selector(element)
            if css_selector:
                is_unique = await self._check_locator_uniqueness(page, css_selector)
                locators.append(
                    ElementLocator(
                        strategy=LocatorStrategy.CSS_SELECTOR,
                        value=css_selector,
                        reliability_score=0.7 if is_unique else 0.3,
                        is_unique=is_unique,
                    )
                )

            # Text content (if unique and meaningful)
            text = (await element.text_content() or "").strip()
            if text and len(text) > 2 and len(text) < 50:
                text_selector = f":text('{text}')"
                is_unique = await self._check_locator_uniqueness(page, text_selector)
                if is_unique:
                    locators.append(
                        ElementLocator(
                            strategy=LocatorStrategy.TEXT_CONTENT,
                            value=text_selector,
                            reliability_score=0.8,
                            is_unique=True,
                        )
                    )

            # XPath (last resort)
            xpath = await self._generate_xpath(element)
            if xpath:
                locators.append(
                    ElementLocator(
                        strategy=LocatorStrategy.XPATH,
                        value=xpath,
                        reliability_score=0.5,
                        is_unique=False,
                        context="Generated XPath",
                    )
                )

        except Exception as e:
            print(f"Failed to generate locators: {e}")

        # Sort by reliability score
        locators.sort(key=lambda x: x.reliability_score, reverse=True)
        return locators

    async def _check_locator_uniqueness(self, page: Page, selector: str) -> bool:
        """Check if a locator is unique on the page"""
        try:
            elements = await page.query_selector_all(selector)
            return len(elements) == 1
        except Exception:
            return False

    async def _generate_css_selector(self, element) -> str:
        """Generate smart CSS selector"""
        try:
            return await element.evaluate(
                """
                el => {
                    function generateSelector(element) {
                        if (element.id) return '#' + element.id;
                        
                        let path = [];
                        while (element && element.nodeType === Node.ELEMENT_NODE) {
                            let selector = element.nodeName.toLowerCase();
                            
                            if (element.className) {
                                let classes = element.className.split(' ').filter(c => c && !c.includes(' '));
                                if (classes.length > 0) {
                                    selector += '.' + classes[0];
                                }
                            }
                            
                            // Add position if needed for uniqueness
                            let siblings = Array.from(element.parentNode?.children || [])
                                .filter(sibling => sibling.nodeName === element.nodeName);
                            if (siblings.length > 1) {
                                let index = siblings.indexOf(element) + 1;
                                selector += ':nth-of-type(' + index + ')';
                            }
                            
                            path.unshift(selector);
                            element = element.parentElement;
                            
                            // Stop at container elements to keep selector shorter
                            if (path.length >= 4) break;
                        }
                        
                        return path.join(' > ');
                    }
                    
                    return generateSelector(el);
                }
            """
            )
        except Exception:
            return ""

    async def _generate_xpath(self, element) -> str:
        """Generate XPath for element"""
        try:
            return await element.evaluate(
                """
                el => {
                    function getXPath(element) {
                        if (element.id) return "//*[@id='" + element.id + "']";
                        if (element === document.body) return '/html/body';
                        
                        let ix = 0;
                        let siblings = element.parentNode.childNodes;
                        for (let i = 0; i < siblings.length; i++) {
                            let sibling = siblings[i];
                            if (sibling === element) {
                                return getXPath(element.parentNode) + '/' + 
                                       element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                            }
                            if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                                ix++;
                            }
                        }
                    }
                    return getXPath(el);
                }
            """
            )
        except Exception:
            return ""

    async def cleanup(self):
        """Cleanup browser resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

    async def _extract_accessibility_data(self, element) -> Dict[str, Any]:
        """Extract comprehensive accessibility information"""
        try:
            return {
                "aria_label": await element.get_attribute("aria-label"),
                "aria_role": await element.get_attribute("role"),
                "aria_described_by": await element.get_attribute("aria-describedby"),
                "aria_labelled_by": await element.get_attribute("aria-labelledby"),
                "aria_expanded": await element.get_attribute("aria-expanded"),
                "aria_hidden": await element.get_attribute("aria-hidden"),
                "aria_disabled": await element.get_attribute("aria-disabled"),
                "tabindex": await element.get_attribute("tabindex"),
                "alt_text": await element.get_attribute("alt"),
                "title": await element.get_attribute("title"),
                "focusable": await element.evaluate("el => el.tabIndex >= 0"),
                "has_aria_label": bool(await element.get_attribute("aria-label")),
                "has_accessible_name": await element.evaluate(
                    """
                    el => {
                        return !!(el.getAttribute('aria-label') || 
                                el.getAttribute('aria-labelledby') ||
                                el.getAttribute('title') ||
                                el.textContent?.trim());
                    }
                """
                ),
            }
        except Exception:
            return {}

    async def _extract_visual_properties(self, element) -> Dict[str, Any]:
        """Extract visual properties and positioning"""
        try:
            bounding_box = await element.bounding_box()
            is_visible = await element.is_visible()

            # Get computed styles
            styles = await element.evaluate(
                """
                el => {
                    const computed = window.getComputedStyle(el);
                    return {
                        display: computed.display,
                        visibility: computed.visibility,
                        opacity: computed.opacity,
                        position: computed.position,
                        zIndex: computed.zIndex,
                        backgroundColor: computed.backgroundColor,
                        color: computed.color,
                        fontSize: computed.fontSize,
                        fontFamily: computed.fontFamily,
                        border: computed.border,
                        margin: computed.margin,
                        padding: computed.padding
                    };
                }
            """
            )

            return {
                "bounding_box": bounding_box,
                "is_visible": is_visible,
                "is_in_viewport": await element.is_visible()
                and bounding_box is not None,
                "computed_styles": styles,
                "screenshot_path": None,  # Could implement element screenshots
            }
        except Exception:
            return {"is_visible": False, "bounding_box": None}

    async def _analyze_behavioral_properties(
        self, element, element_type: ElementType
    ) -> Dict[str, Any]:
        """Analyze element behavioral properties"""
        try:
            properties = {
                "is_clickable": await element.is_enabled()
                and await element.is_visible(),
                "is_editable": await element.is_editable(),
                "is_enabled": await element.is_enabled(),
                "is_checked": False,
                "is_selected": False,
                "has_focus": False,
                "accepts_files": False,
                "is_required": False,
                "is_readonly": False,
                "max_length": None,
                "pattern": None,
                "placeholder": None,
            }

            # Input-specific properties
            if element_type == ElementType.INPUT:
                input_type = await element.get_attribute("type") or "text"
                properties.update(
                    {
                        "input_type": input_type,
                        "is_required": bool(await element.get_attribute("required")),
                        "is_readonly": bool(await element.get_attribute("readonly")),
                        "max_length": await element.get_attribute("maxlength"),
                        "pattern": await element.get_attribute("pattern"),
                        "placeholder": await element.get_attribute("placeholder"),
                        "accepts_files": input_type == "file",
                        "is_checked": (
                            await element.is_checked()
                            if input_type in ["checkbox", "radio"]
                            else False
                        ),
                    }
                )

            # Form-specific properties
            elif element_type == ElementType.FORM:
                properties.update(
                    {
                        "method": await element.get_attribute("method") or "GET",
                        "action": await element.get_attribute("action"),
                        "enctype": await element.get_attribute("enctype"),
                        "novalidate": bool(await element.get_attribute("novalidate")),
                    }
                )

            # Link-specific properties
            elif element_type == ElementType.LINK:
                properties.update(
                    {
                        "href": await element.get_attribute("href"),
                        "target": await element.get_attribute("target"),
                        "download": await element.get_attribute("download"),
                        "is_external": await element.evaluate(
                            """
                        el => {
                            const href = el.getAttribute('href');
                            return href && (href.startsWith('http') && !href.includes(window.location.hostname));
                        }
                    """
                        ),
                    }
                )

            return properties
        except Exception:
            return {"is_clickable": False, "is_editable": False}

    async def _get_element_context(self, element) -> Dict[str, Any]:
        """Get element context and relationships"""
        try:
            context = await element.evaluate(
                """
                el => {
                    const parent = el.parentElement;
                    const siblings = parent ? Array.from(parent.children) : [];
                    const children = Array.from(el.children);
                    
                    return {
                        parent_tag: parent?.tagName?.toLowerCase(),
                        parent_class: parent?.className,
                        parent_id: parent?.id,
                        siblings_count: siblings.length,
                        children_count: children.length,
                        position_in_parent: siblings.indexOf(el),
                        has_form_ancestor: !!el.closest('form'),
                        has_table_ancestor: !!el.closest('table'),
                        has_nav_ancestor: !!el.closest('nav'),
                        nesting_level: (() => {
                            let level = 0;
                            let current = el.parentElement;
                            while (current && level < 10) {
                                level++;
                                current = current.parentElement;
                            }
                            return level;
                        })()
                    };
                }
            """
            )

            return context
        except Exception:
            return {}

    async def _determine_interactions(
        self, element, element_type: ElementType
    ) -> List[str]:
        """Determine possible interactions with the element"""
        interactions = []

        try:
            is_clickable = await element.is_enabled() and await element.is_visible()
            is_editable = await element.is_editable()
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")

            # Basic interactions
            if is_clickable:
                interactions.append("click")
                interactions.append("double_click")
                interactions.append("right_click")

            if is_editable:
                interactions.extend(["type", "fill", "clear"])

            # Element-type specific interactions
            if element_type == ElementType.INPUT:
                input_type = await element.get_attribute("type") or "text"

                if input_type in ["checkbox", "radio"]:
                    interactions.extend(["check", "uncheck"])
                elif input_type == "file":
                    interactions.append("upload_file")
                elif input_type in ["text", "email", "password", "search"]:
                    interactions.extend(["focus", "blur", "select_all"])
                elif input_type in ["number", "range"]:
                    interactions.extend(["increment", "decrement"])

            elif element_type == ElementType.DROPDOWN:
                interactions.extend(
                    ["select_option", "open_dropdown", "close_dropdown"]
                )

            elif element_type == ElementType.LINK:
                interactions.extend(["navigate", "open_in_new_tab"])

            elif element_type == ElementType.FORM:
                interactions.extend(["submit", "reset"])

            elif element_type == ElementType.TAB:
                interactions.extend(["activate_tab", "keyboard_navigate"])

            elif element_type == ElementType.MODAL:
                interactions.extend(["open_modal", "close_modal", "escape_close"])

            # Keyboard interactions
            if await element.evaluate("el => el.tabIndex >= 0"):
                interactions.extend(["focus", "blur", "keyboard_navigate"])

            # Drag and drop
            if tag_name in ["div", "span", "img"]:
                interactions.extend(["drag", "drop"])

            # Hover interactions
            interactions.append("hover")

        except Exception:
            pass

        return list(set(interactions))  # Remove duplicates

    async def _generate_test_scenarios(
        self, element, element_type: ElementType, text_content: str
    ) -> List[str]:
        """Generate test scenario suggestions for the element"""
        scenarios = []

        try:
            # Basic scenarios for all interactive elements
            if element_type in [ElementType.BUTTON, ElementType.LINK]:
                scenarios.extend(
                    [
                        f"Verify {text_content or 'element'} is clickable",
                        f"Verify {text_content or 'element'} click triggers expected action",
                        f"Verify {text_content or 'element'} is accessible via keyboard",
                        f"Verify {text_content or 'element'} has proper focus indicators",
                    ]
                )

            elif element_type == ElementType.INPUT:
                input_type = await element.get_attribute("type") or "text"
                field_name = (
                    text_content
                    or await element.get_attribute("placeholder")
                    or "input field"
                )

                if input_type in ["text", "email", "password"]:
                    scenarios.extend(
                        [
                            f"Verify {field_name} accepts valid input",
                            f"Verify {field_name} validates input format",
                            f"Verify {field_name} handles special characters",
                            f"Verify {field_name} required field validation",
                            f"Verify {field_name} maximum length validation",
                        ]
                    )
                elif input_type in ["checkbox", "radio"]:
                    scenarios.extend(
                        [
                            f"Verify {field_name} can be selected/deselected",
                            f"Verify {field_name} maintains state correctly",
                            f"Verify {field_name} keyboard accessibility",
                        ]
                    )

            elif element_type == ElementType.FORM:
                scenarios.extend(
                    [
                        "Verify form submission with valid data",
                        "Verify form validation with invalid data",
                        "Verify form reset functionality",
                        "Verify form accessibility",
                        "Verify form error handling",
                    ]
                )

            elif element_type == ElementType.NAVIGATION:
                scenarios.extend(
                    [
                        "Verify navigation menu is accessible",
                        "Verify navigation links work correctly",
                        "Verify navigation keyboard accessibility",
                        "Verify navigation responsive behavior",
                    ]
                )

            elif element_type == ElementType.TABLE:
                scenarios.extend(
                    [
                        "Verify table data displays correctly",
                        "Verify table sorting functionality",
                        "Verify table pagination if present",
                        "Verify table accessibility with screen readers",
                    ]
                )

            elif element_type == ElementType.MODAL:
                scenarios.extend(
                    [
                        "Verify modal opens correctly",
                        "Verify modal closes with close button",
                        "Verify modal closes with escape key",
                        "Verify modal focus management",
                        "Verify modal backdrop click behavior",
                    ]
                )

            # Add accessibility scenarios for all elements
            scenarios.extend(
                [
                    f"Verify {text_content or 'element'} screen reader compatibility",
                    f"Verify {text_content or 'element'} high contrast mode",
                    f"Verify {text_content or 'element'} keyboard-only navigation",
                ]
            )

        except Exception:
            pass

        return scenarios

    async def _analyze_page_structure(self, page: Page) -> PageStructure:
        """Comprehensive page structure analysis"""
        try:
            # Check for major structural elements
            has_navigation = bool(await page.query_selector("nav, [role='navigation']"))
            has_forms = bool(await page.query_selector("form"))
            has_tables = bool(await page.query_selector("table"))
            has_modals = bool(await page.query_selector("[role='dialog'], .modal"))
            has_pagination = bool(await page.query_selector(".pagination, .pager"))

            # Determine page type
            page_type = await self._determine_page_type(page)

            # Check responsive breakpoints
            responsive_breakpoints = await self._check_responsive_design(page)

            # Get performance metrics (placeholder - would need actual implementation)
            performance_metrics = {}

            # Calculate accessibility score (placeholder)
            accessibility_score = 0.0

            # Extract SEO elements
            seo_elements = await self._extract_seo_elements(page)

            return PageStructure(
                page_type=page_type,
                has_navigation=has_navigation,
                has_forms=has_forms,
                has_tables=has_tables,
                has_modals=has_modals,
                has_pagination=has_pagination,
                responsive_breakpoints=responsive_breakpoints,
                performance_metrics=performance_metrics,
                accessibility_score=accessibility_score,
                seo_elements=seo_elements,
            )

        except Exception as e:
            self.logger.error(f"Failed to analyze page structure: {e}")
            import traceback
            self.logger.debug(f"Page structure analysis traceback: {traceback.format_exc()}")
            return PageStructure(
                page_type="unknown",
                has_navigation=False,
                has_forms=False,
                has_tables=False,
                has_modals=False,
                has_pagination=False,
                responsive_breakpoints=[],
                performance_metrics={},
                accessibility_score=0.0,
                seo_elements={},
            )

    async def _determine_page_type(self, page: Page) -> str:
        """Determine the type of page using enhanced heuristics"""
        try:
            # Check for authentication pages
            if await page.query_selector("input[type='password']"):
                if await page.query_selector(
                    "input[type='email'], input[name*='email']"
                ):
                    return "login"
                elif await page.query_selector(
                    "input[name*='confirm'], input[name*='repeat']"
                ):
                    return "registration"
                else:
                    return "authentication"

            # Check for e-commerce pages
            if await page.query_selector(
                ".price, .cart, .checkout, [data-testid*='price']"
            ):
                if await page.query_selector(".product-list, .products-grid"):
                    return "product_listing"
                elif await page.query_selector(".product-detail, .product-info"):
                    return "product_detail"
                elif await page.query_selector(".cart, .shopping-cart"):
                    return "shopping_cart"
                elif await page.query_selector(".checkout, .payment"):
                    return "checkout"
                else:
                    return "ecommerce"

            # Check for admin/dashboard pages
            if await page.query_selector(".dashboard, .admin-panel, .sidebar"):
                return "dashboard"

            # Check for form pages
            form_elements = await page.query_selector_all("form")
            if len(form_elements) > 1:
                return "multi_form"
            elif len(form_elements) == 1:
                return "form"

            # Check for data display pages
            if await page.query_selector("table"):
                return "data_table"

            # Check for content pages
            if await page.query_selector("article, .article, .post, .blog"):
                return "content"

            # Check for search pages
            if await page.query_selector("input[type='search'], .search-results"):
                return "search"

            # Check for profile pages
            if await page.query_selector(".profile, .user-info, .account"):
                return "profile"

            # Default to landing page
            return "landing"

        except Exception:
            return "unknown"

    async def _check_responsive_design(self, page: Page) -> List[Dict[str, Any]]:
        """Check responsive design at different breakpoints"""
        breakpoints = [
            {"name": "mobile", "width": 375, "height": 667},
            {"name": "mobile_large", "width": 414, "height": 896},
            {"name": "tablet", "width": 768, "height": 1024},
            {"name": "desktop", "width": 1024, "height": 768},
            {"name": "desktop_large", "width": 1920, "height": 1080},
        ]

        results = []
        original_viewport = page.viewport_size

        for bp in breakpoints:
            try:
                await page.set_viewport_size(
                    {"width": bp["width"], "height": bp["height"]}
                )
                await asyncio.sleep(0.5)  # Wait for layout to adjust

                # Check for common responsive issues
                layout_analysis = await page.evaluate(
                    """
                    () => {
                        const issues = [];
                        
                        // Check for horizontal overflow
                        if (document.body.scrollWidth > window.innerWidth) {
                            issues.push('horizontal_overflow');
                        }
                        
                        // Check for overlapping elements (simplified)
                        const elements = document.querySelectorAll('*');
                        let overlapping = 0;
                        // This would need more sophisticated overlap detection
                        
                        // Check for very small text
                        const smallText = Array.from(document.querySelectorAll('*'))
                            .filter(el => {
                                const style = window.getComputedStyle(el);
                                const fontSize = parseInt(style.fontSize);
                                return fontSize > 0 && fontSize < 12;
                            }).length;
                        
                        if (smallText > 0) {
                            issues.push('small_text');
                        }
                        
                        return {
                            issues,
                            viewport_width: window.innerWidth,
                            viewport_height: window.innerHeight,
                            document_width: document.body.scrollWidth,
                            document_height: document.body.scrollHeight,
                            small_text_elements: smallText
                        };
                    }
                """
                )

                results.append(
                    {
                        "breakpoint": bp["name"],
                        "dimensions": f"{bp['width']}x{bp['height']}",
                        "layout_analysis": layout_analysis,
                        "responsive_score": 1.0
                        - (len(layout_analysis["issues"]) * 0.2),
                    }
                )

            except Exception as e:
                results.append(
                    {
                        "breakpoint": bp["name"],
                        "dimensions": f"{bp['width']}x{bp['height']}",
                        "error": str(e),
                        "responsive_score": 0.0,
                    }
                )

        # Restore original viewport
        if original_viewport:
            await page.set_viewport_size(original_viewport)

        return results

    async def _extract_seo_elements(self, page: Page) -> Dict[str, Any]:
        """Extract SEO-related elements"""
        try:
            return await page.evaluate(
                """
                () => {
                    const seo = {};
                    
                    // Meta tags
                    seo.title = document.title;
                    seo.meta_description = document.querySelector('meta[name="description"]')?.content;
                    seo.meta_keywords = document.querySelector('meta[name="keywords"]')?.content;
                    seo.canonical = document.querySelector('link[rel="canonical"]')?.href;
                    
                    // Open Graph tags
                    seo.og_title = document.querySelector('meta[property="og:title"]')?.content;
                    seo.og_description = document.querySelector('meta[property="og:description"]')?.content;
                    seo.og_image = document.querySelector('meta[property="og:image"]')?.content;
                    seo.og_url = document.querySelector('meta[property="og:url"]')?.content;
                    
                    // Twitter Card tags
                    seo.twitter_card = document.querySelector('meta[name="twitter:card"]')?.content;
                    seo.twitter_title = document.querySelector('meta[name="twitter:title"]')?.content;
                    seo.twitter_description = document.querySelector('meta[name="twitter:description"]')?.content;
                    
                    // Headings structure
                    seo.headings = {
                        h1: Array.from(document.querySelectorAll('h1')).map(h => h.textContent?.trim()),
                        h2: Array.from(document.querySelectorAll('h2')).map(h => h.textContent?.trim()),
                        h3: Array.from(document.querySelectorAll('h3')).map(h => h.textContent?.trim())
                    };
                    
                    // Links
                    seo.internal_links = Array.from(document.querySelectorAll('a[href]'))
                        .filter(a => a.href.includes(window.location.hostname)).length;
                    seo.external_links = Array.from(document.querySelectorAll('a[href]'))
                        .filter(a => !a.href.includes(window.location.hostname) && a.href.startsWith('http')).length;
                    
                    // Images
                    const images = Array.from(document.querySelectorAll('img'));
                    seo.images_without_alt = images.filter(img => !img.alt).length;
                    seo.total_images = images.length;
                    
                    return seo;
                }
            """
            )
        except Exception:
            return {}

    async def _get_performance_metrics(
        self, page: Page, nav_time: float
    ) -> Dict[str, Any]:
        """Get basic performance metrics"""
        try:
            # Get basic timing information
            timing = await page.evaluate(
                """
                () => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    if (perfData) {
                        return {
                            dom_content_loaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                            load_complete: perfData.loadEventEnd - perfData.loadEventStart,
                            first_paint: performance.getEntriesByType('paint')
                                .find(entry => entry.name === 'first-paint')?.startTime,
                            first_contentful_paint: performance.getEntriesByType('paint')
                                .find(entry => entry.name === 'first-contentful-paint')?.startTime
                        };
                    }
                    return {};
                }
            """
            )

            # Page size information
            content = await page.content()
            page_size = len(content.encode("utf-8"))

            # Resource counts
            resource_counts = await page.evaluate(
                """
                () => {
                    const resources = performance.getEntriesByType('resource');
                    const counts = {
                        total: resources.length,
                        scripts: resources.filter(r => r.initiatorType === 'script').length,
                        stylesheets: resources.filter(r => r.initiatorType === 'css').length,
                        images: resources.filter(r => r.initiatorType === 'img').length,
                        fonts: resources.filter(r => r.initiatorType === 'other' && r.name.match(/\\.woff2?$/)).length
                    };
                    return counts;
                }
            """
            )

            return {
                "navigation_time": nav_time,
                "page_size_bytes": page_size,
                "dom_timing": timing,
                "resource_counts": resource_counts,
                "performance_score": min(
                    1.0, max(0.0, (5.0 - nav_time) / 5.0)
                ),  # Simple score
            }

        except Exception:
            return {"navigation_time": nav_time}

    async def _calculate_accessibility_score(
        self, elements: List[ElementData]
    ) -> float:
        """Calculate basic accessibility score based on elements"""
        if not elements:
            return 0.0

        total_score = 0.0
        interactive_elements = [
            e
            for e in elements
            if e.element_type
            in [ElementType.BUTTON, ElementType.INPUT, ElementType.LINK]
        ]

        if not interactive_elements:
            return 0.5  # Neutral score for non-interactive pages

        for element in interactive_elements:
            element_score = 0.0

            # Check for accessible name
            if (
                element.accessibility.get("has_accessible_name")
                or element.text_content.strip()
                or element.accessibility.get("aria_label")
            ):
                element_score += 0.3

            # Check for proper role
            if element.accessibility.get("aria_role"):
                element_score += 0.2

            # Check for focusable
            if element.accessibility.get("focusable"):
                element_score += 0.2

            # Check for keyboard accessibility
            if element.behavioral_properties.get("is_clickable"):
                element_score += 0.2

            # Check for visibility
            if element.visual_properties.get("is_visible"):
                element_score += 0.1

            total_score += min(1.0, element_score)

        return total_score / len(interactive_elements)

    async def _capture_element_state(self, page: Page, element_handle) -> Dict[str, Any]:
        """Capture the current state of an element - fixed duplicate method"""
        try:
            state = await element_handle.evaluate("""
                el => {
                    const rect = el.getBoundingClientRect();
                    const style = getComputedStyle(el);
                    
                    return {
                        visible: el.offsetWidth > 0 && el.offsetHeight > 0,
                        enabled: !el.disabled,
                        focused: document.activeElement === el,
                        value: el.value || el.textContent || '',
                        checked: el.checked,
                        selected: el.selected,
                        classes: el.className,
                        styles: {
                            display: style.display,
                            visibility: style.visibility,
                            opacity: style.opacity
                        },
                        position: {
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height
                        }
                    };
                }
            """)
            return state
        except:
            return {}
    
    async def _extract_valid_links(self, page: Page, base_url: str) -> List[str]:
        """Extract valid internal links for crawling"""
        try:
            links = await page.evaluate(
                """
                (baseUrl) => {
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    const validLinks = [];
                    const baseHostname = new URL(baseUrl).hostname;
                    
                    for (const link of links) {
                        try {
                            const href = link.href;
                            const url = new URL(href);
                            
                            // Only include same-domain links
                            if (url.hostname === baseHostname && 
                                !href.includes('#') &&  // Skip anchors
                                !href.includes('mailto:') &&  // Skip email links
                                !href.includes('tel:') &&  // Skip phone links
                                !href.includes('javascript:') &&  // Skip javascript links
                                !href.match(/\\.(pdf|doc|xls|zip|exe)$/i)) {  // Skip file downloads
                                validLinks.push(href);
                            }
                        } catch (e) {
                            // Skip invalid URLs
                        }
                    }
                    
                    // Remove duplicates
                    return [...new Set(validLinks)];
                }
            """,
                base_url,
            )

            return links[:20]  # Limit to prevent excessive crawling

        except Exception:
            return []
    
    async def _wait_for_dynamic_content(self, page: Page):
        """Smart waiting for dynamic content"""
        # Wait for common dynamic content indicators
        dynamic_selectors = [
            ".loading",
            ".spinner",
            "[data-loading='true']",
            ".skeleton",
            ".placeholder"
        ]
        
        # Wait for loading indicators to disappear
        for selector in dynamic_selectors:
            try:
                await page.wait_for_selector(selector, state="detached", timeout=5000)
            except:
                continue
        
        # Wait for network idle
        await page.wait_for_load_state("networkidle", timeout=10000)
        
        # Additional wait for React/Vue/Angular apps
        await page.evaluate("""
            new Promise((resolve) => {
                if (window.React || window.Vue || window.ng) {
                    // Wait a bit more for SPA frameworks
                    setTimeout(resolve, 2000);
                } else {
                    resolve();
                }
            });
        """)
    
    async def _detect_captcha(self, page: Page) -> bool:
        """Detect CAPTCHA on the page"""
        captcha_indicators = [
            "[class*='captcha']",
            "[id*='captcha']",
            "[class*='recaptcha']",
            "[id*='recaptcha']",
            "iframe[src*='recaptcha']",
            "iframe[src*='hcaptcha']",
            ".g-recaptcha",
            ".h-captcha",
            "[data-sitekey]"
        ]
        
        for selector in captcha_indicators:
            if await page.query_selector(selector):
                return True
        
        # Check for CAPTCHA-related text
        page_text = await page.text_content('body')
        captcha_keywords = ['captcha', 'recaptcha', 'verify you are human', 'prove you are not a robot']
        
        if page_text and any(keyword in page_text.lower() for keyword in captcha_keywords):
            return True
        
        return False
    
    async def _extract_all_elements_advanced(self, page: Page) -> List[ElementData]:
        """Extract elements using advanced AI and ML techniques"""
        elements = []
        
        # First, extract using traditional methods
        traditional_elements = await self._extract_all_elements(page)
        elements.extend(traditional_elements)
        
        # Extract shadow DOM elements
        shadow_elements = await self._extract_shadow_dom_elements(page)
        elements.extend(shadow_elements)
        
        # Use semantic AI detection
        semantic_elements = await self._extract_semantic_elements(page)
        elements.extend(semantic_elements)
        
        # Apply ML classification
        ml_enhanced_elements = await self._apply_ml_classification(elements, page)
        
        # Remove duplicates and merge information
        unique_elements = self._merge_and_deduplicate_elements(ml_enhanced_elements)
        
        return unique_elements

