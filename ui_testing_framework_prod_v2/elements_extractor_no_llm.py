import asyncio
import json
import logging
import hashlib
import re
import time
import base64
import sys
import os
from collections import defaultdict, Counter
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple, Callable, TypeVar, cast
from urllib.parse import urljoin, urlparse
import functools
import threading
import gc
from tempfile import mkdtemp
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator

# Add parent directory to path to import browser module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Import ALL data types from data_types.py for DRY compliance
try:
    # Try relative import first (when used as a module)
    from .data_types import (
        # Core enums
        ElementType,
        InteractionType,
        LocatorStrategy,
        ExtractionMethod,
        ConfidenceLevel,
        StealthLevel,
        # Data models
        ElementSelector,
        BoundingBox,
        ComputedStyle,
        Element,
        ScreenshotData,
        CrawlResult,
        StealthConfig,
        # Configs and results
        ExtractionConfig,
        ExtractionResult,
        # Utilities
        ElementSelectorUtils,
        retry_with_backoff,
        ThreadSafeCache,
        memory_cleanup,
        # Constants
        CONFIDENCE_BASE,
        CONFIDENCE_INCREMENT,
        SELECTOR_SCORE_ID,
        SELECTOR_SCORE_DATA_TESTID,
        SELECTOR_SCORE_ARIA_LABEL,
        SELECTOR_SCORE_CLASS,
        SELECTOR_SCORE_TEXT,
        SELECTOR_SCORE_TAG,
        SELECTOR_SCORE_XPATH,
        SELECTOR_SCORE_POSITION,
        ELEMENT_INTERACTIONS
    )
except ImportError:
    # Fall back to absolute import (when run directly)
    from data_types import (
        # Core enums
        ElementType,
        InteractionType,
        LocatorStrategy,
        ExtractionMethod,
        ConfidenceLevel,
        StealthLevel,
        # Data models
        ElementSelector,
        BoundingBox,
        ComputedStyle,
        Element,
        ScreenshotData,
        CrawlResult,
        StealthConfig,
        # Configs and results
        ExtractionConfig,
        ExtractionResult,
        # Utilities
        ElementSelectorUtils,
        retry_with_backoff,
        ThreadSafeCache,
        memory_cleanup,
        # Constants
        CONFIDENCE_BASE,
        CONFIDENCE_INCREMENT,
        SELECTOR_SCORE_ID,
        SELECTOR_SCORE_DATA_TESTID,
        SELECTOR_SCORE_ARIA_LABEL,
        SELECTOR_SCORE_CLASS,
        SELECTOR_SCORE_TEXT,
        SELECTOR_SCORE_TAG,
        SELECTOR_SCORE_XPATH,
        SELECTOR_SCORE_POSITION,
        ELEMENT_INTERACTIONS
    )

# Import browser module for DRY compliance
try:
    # Try relative import first (when used as a module)
    from .browser import (
        UltimateStealthBrowser,
    )
    BROWSER_MODULE_AVAILABLE = True
except ImportError:
    # Fall back to absolute import (when run directly)
    try:
        from browser import (
            UltimateStealthBrowser,
        )
        BROWSER_MODULE_AVAILABLE = True
    except ImportError:
        BROWSER_MODULE_AVAILABLE = False
        logger.warning("Browser module not found. This module requires browser.py")

        # Define minimal fallback types for type checking
        class UltimateStealthBrowser:  # type: ignore
            pass


# ==================== PRODUCTION UTILITIES ====================
# All utilities are now imported from data_types.py for DRY compliance

T = TypeVar("T")


# ==================== ENUMS ====================
# All enums are now imported from data_types.py for DRY compliance


# ==================== CONSTANTS ====================
# All constants are now imported from data_types.py for DRY compliance
# Using ELEMENT_INTERACTIONS from data_types.py
# ElementSelectorUtils provides type determination logic


# ==================== DATA MODELS ====================
# All data models are now imported from data_types.py for DRY compliance


# ==================== MAIN EXTRACTOR CLASS ====================


class ElementsExtractorNoLLM:
    """
    Production-ready element extractor without LLM dependencies.
    Uses browser.py for browser automation (DRY compliance).
    """

    def __init__(self, config: Optional[ExtractionConfig] = None) -> None:
        """Initialize the extractor"""
        self.config = config or ExtractionConfig()
        self._cache = ThreadSafeCache(max_size=1000) if self.config.enable_caching else None
        self._browser: Optional[UltimateStealthBrowser] = None
        self._lock = asyncio.Lock()

        # Performance metrics
        self._metrics: Dict[str, List[float]] = defaultdict(list)

        logger.debug("ElementsExtractorNoLLM initialized")

    async def _ensure_browser(self) -> UltimateStealthBrowser:
        """Ensure browser is initialized"""
        async with self._lock:
            if self._browser is None:
                if not BROWSER_MODULE_AVAILABLE:
                    raise RuntimeError("Browser module not available. Please ensure browser.py is present.")

                # Configure stealth based on extraction config
                stealth_config = StealthConfig()
                stealth_config.headless = False
                stealth_config.level = StealthLevel.HIGH if self.config.enable_stealth else StealthLevel.LOW

                self._browser = UltimateStealthBrowser(stealth_config)
                await self._browser.initialize()
                logger.info("Browser initialized successfully")

            return self._browser

    async def extract_from_url(self, url: str, use_cache: bool = True) -> ExtractionResult:
        """
        Extract elements from a URL

        Args:
            url: The URL to extract elements from
            use_cache: Whether to use cached results

        Returns:
            ExtractionResult containing extracted elements
        """
        start_time = time.time()

        # Check cache
        cache_key = ""
        if use_cache and self._cache:
            cache_key = hashlib.md5(url.encode()).hexdigest()
            cached = self._cache.get(cache_key)
            if cached:
                logger.info(f"Returning cached result for {url}")
                return cast(ExtractionResult, cached)

        try:
            # Ensure browser is ready
            browser = await self._ensure_browser()

            # Extract elements using browser module
            logger.info(f"Navigating to {url}")
            browser_result = await browser.extract_elements(url)

            # Convert browser result to our format
            elements = self._process_browser_elements(browser_result.elements)

            # Apply additional filtering and processing
            elements = self._filter_elements(elements)
            elements = self._classify_elements(elements)
            elements = self._generate_selectors(elements)

            # Calculate statistics
            stats = self._calculate_statistics(elements, time.time() - start_time)

            # Create screenshots if configured
            screenshots: List[ScreenshotData] = []
            if self.config.capture_screenshots:
                screenshots = await self._capture_screenshots(browser, url, elements)

            # Create result
            result = ExtractionResult(
                url=url,
                elements=elements,
                extraction_time=time.time() - start_time,
                success=True,
                statistics=stats,
                screenshots=screenshots,
                metadata={
                    "config": self.config.model_dump(),
                    "timestamp": time.time(),
                },
            )

            # Cache result
            if use_cache and self._cache and cache_key:
                self._cache.set(cache_key, result)

            logger.info(f"Extracted {len(elements)} total elements from {url}")

            return result

        except Exception as e:
            logger.error(f"Failed to extract from {url}: {e}")
            return ExtractionResult(
                url=url, elements=[], extraction_time=time.time() - start_time, success=False, errors=[str(e)]
            )

    def _process_browser_elements(self, browser_elements: List[Element]) -> List[Element]:
        """Process browser elements - browser already returns Element objects"""
        # Browser already returns Element objects with correct types
        # Just update element types using ElementSelectorUtils if needed
        for element in browser_elements:
            # Ensure element type is correctly determined using shared utils
            element.element_type = ElementSelectorUtils.determine_element_type(
                tag_name=element.tag_name,
                elem_type=element.attributes.get("type"),
                role=element.attributes.get("role"),
                input_type=element.attributes.get("type") if element.tag_name.lower() == "input" else None
            )
        return browser_elements

    def _determine_element_type(self, element: Element) -> ElementType:
        """Determine element type using shared utilities"""
        return ElementSelectorUtils.determine_element_type(
            tag_name=element.tag_name,
            elem_type=element.attributes.get("type"),
            role=element.attributes.get("role"),
            input_type=element.attributes.get("type") if element.tag_name.lower() == "input" else None
        )

    def _filter_elements(self, elements: List[Element]) -> List[Element]:
        """Filter elements based on configuration"""
        filtered: List[Element] = []
        seen_hashes: Set[str] = set()

        for element in elements:
            # QA mode filtering - only include QA-relevant elements
            if self.config.qa_mode:
                if not self._is_qa_relevant_element(element):
                    continue
            
            # Filter invisible elements
            if self.config.filter_invisible:
                if element.computed_style and not element.computed_style.is_visible():
                    continue
                if element.bounding_box and not element.bounding_box.is_visible():
                    continue

            # Filter small elements
            if self.config.min_element_size > 0:
                if element.bounding_box:
                    if (
                        element.bounding_box.width < self.config.min_element_size
                        or element.bounding_box.height < self.config.min_element_size
                    ):
                        continue

            # Filter duplicates
            if self.config.filter_duplicates:
                element_hash = self._hash_element(element)
                if element_hash in seen_hashes:
                    continue
                seen_hashes.add(element_hash)

            filtered.append(element)

        return filtered

    def _hash_element(self, element: Element) -> str:
        """Generate hash for element deduplication"""
        key_parts = [
            element.tag_name,
            element.element_type.value,
            element.text or "",
            element.xpath or "",
            json.dumps(element.attributes, sort_keys=True),
        ]
        return hashlib.md5("".join(key_parts).encode()).hexdigest()

    def _classify_elements(self, elements: List[Element]) -> List[Element]:
        """Classify elements and determine interaction types"""
        for element in elements:
            # Use shared ELEMENT_INTERACTIONS mapping from data_types.py
            element.interaction_types = ELEMENT_INTERACTIONS.get(
                element.element_type,
                [InteractionType.HOVER]  # Default to hover if not in mapping
            )

            # Calculate confidence based on element completeness
            confidence = 0.5
            if element.text:
                confidence += 0.1
            if element.xpath:
                confidence += 0.1
            if element.css_selector:
                confidence += 0.1
            if element.attributes:
                confidence += 0.1
            if element.is_valid:
                confidence += 0.1

            element.confidence = min(confidence, 1.0)

        return elements

    def _generate_selectors(self, elements: List[Element]) -> List[Element]:
        """Generate multiple selector strategies for each element"""
        for element in elements:
            element.selectors = self._create_selectors_for_element(element)
        return elements

    def _create_selectors_for_element(self, element: Element) -> List[ElementSelector]:
        """Create selector strategies for a single element"""
        selectors: List[ElementSelector] = []
        attrs = element.attributes

        # Define selector generation strategies
        selector_strategies = [
            # (attribute_key, strategy, value_formatter, score, is_unique)
            ("id", LocatorStrategy.ID, lambda v: f"#{v}", SELECTOR_SCORE_ID, True),
            ("data-testid", LocatorStrategy.TESTID,
             lambda v: f"[data-testid='{v}']", SELECTOR_SCORE_DATA_TESTID, True),
            ("name", LocatorStrategy.NAME,
             lambda v: f"[name='{v}']", 0.85, False),
            ("aria-label", LocatorStrategy.LABEL,
             lambda v: f"[aria-label='{v}']", SELECTOR_SCORE_ARIA_LABEL, False),
        ]

        # Generate attribute-based selectors
        for attr_key, strategy, formatter, score, is_unique in selector_strategies:
            if attr_value := attrs.get(attr_key):
                selectors.append(
                    ElementSelector(
                        strategy=strategy,
                        value=formatter(attr_value),
                        score=score,
                        is_unique=is_unique
                    )
                )

        # Class selector
        if classes := attrs.get("class"):
            class_list = classes.split()
            if class_list:
                selectors.append(
                    ElementSelector(
                        strategy=LocatorStrategy.CSS_CLASS,
                        value=f".{'.'.join(class_list)}",
                        score=SELECTOR_SCORE_CLASS,
                        is_unique=False
                    )
                )

        # Text content selector
        if element.text:
            text_snippet = element.text[:50]
            selectors.append(
                ElementSelector(
                    strategy=LocatorStrategy.TEXT,
                    value=f"{element.tag_name}:has-text('{text_snippet}')",
                    score=SELECTOR_SCORE_TEXT,
                    is_unique=False
                )
            )

        # Primary selector (XPath or CSS)
        if element.selector:
            is_xpath = element.selector.startswith(("//", "/"))
            selectors.append(
                ElementSelector(
                    strategy=LocatorStrategy.XPATH if is_xpath else LocatorStrategy.CSS_SELECTOR,
                    value=element.selector,
                    score=0.4,
                    is_unique=False
                )
            )

        return selectors

    def _calculate_statistics(self, elements: List[Element], extraction_time: float) -> Dict[str, Any]:
        """Calculate extraction statistics"""
        stats: Dict[str, Any] = {
            "total_elements": len(elements),
            "extraction_time": extraction_time,
        }

        # Element type distribution
        type_counts: Counter[str] = Counter(e.element_type.value for e in elements)
        stats["element_types"] = dict(type_counts)

        # Confidence statistics
        if elements:
            confidences = [e.confidence for e in elements]
            stats["avg_confidence"] = sum(confidences) / len(confidences)
            stats["min_confidence"] = min(confidences)
            stats["max_confidence"] = max(confidences)

        # Selector strategy distribution
        strategy_counts: Counter[str] = Counter()
        for element in elements:
            if best_selector := element.get_best_selector():
                strategy_counts[best_selector.strategy.value] += 1
        stats["selector_strategies"] = dict(strategy_counts)

        # Extraction method distribution
        method_counts: Counter[str] = Counter()
        for element in elements:
            if element.extraction_method:
                method_counts[element.extraction_method.value] += 1
        stats["extraction_methods"] = dict(method_counts)

        # Special element counts
        stats["shadow_elements"] = sum(1 for e in elements if e.is_shadow_element)
        stats["iframe_elements"] = sum(1 for e in elements if e.is_iframe_element)
        stats["clickable_elements"] = sum(1 for e in elements if e.is_clickable)
        stats["editable_elements"] = sum(1 for e in elements if e.is_editable)

        return stats

    async def _capture_screenshots(
        self, browser: UltimateStealthBrowser, url: str, elements: List[Element]
    ) -> List[ScreenshotData]:
        """Capture screenshots with element highlighting"""
        screenshots: List[ScreenshotData] = []

        try:
            # Get page from browser
            if not hasattr(browser, "page") or not browser.page:
                logger.warning("No page available for screenshots")
                return screenshots

            page = browser.page

            # Capture base screenshot
            screenshot_bytes = await page.screenshot(
                full_page=self.config.screenshot_full_page, type=self.config.screenshot_format  # type: ignore
            )

            viewport = page.viewport_size
            if viewport is None or callable(viewport):
                viewport = {"width": 1366, "height": 768}

            base_screenshot = ScreenshotData(
                format=self.config.screenshot_format,
                width=viewport["width"],
                height=viewport["height"],
                data=base64.b64encode(screenshot_bytes).decode(),
                timestamp=time.time(),
                url=url,
            )
            screenshots.append(base_screenshot)

            # Capture with highlights if configured
            if self.config.highlight_elements and elements:
                # Build selector list
                selector_list = []
                for e in elements[:50]:
                    if best_sel := e.get_best_selector():
                        selector_list.append(best_sel.value)

                # Inject highlighting script
                await page.evaluate(
                    """
                    (elements) => {
                        elements.forEach(selector => {
                            try {
                                const el = document.querySelector(selector);
                                if (el) {
                                    el.style.outline = '3px solid red';
                                    el.style.outlineOffset = '2px';
                                }
                            } catch (e) {}
                        });
                    }
                """,
                    selector_list,
                )

                # Capture highlighted screenshot
                highlighted_bytes = await page.screenshot(
                    full_page=self.config.screenshot_full_page, type=self.config.screenshot_format  # type: ignore
                )

                highlighted_screenshot = ScreenshotData(
                    format=self.config.screenshot_format,
                    width=viewport["width"],
                    height=viewport["height"],
                    data=base64.b64encode(highlighted_bytes).decode(),
                    timestamp=time.time(),
                    url=url,
                    highlighted_elements=[e.tag_name for e in elements[:50]],
                )
                screenshots.append(highlighted_screenshot)

                # Remove highlights
                await page.evaluate(
                    """
                    () => {
                        document.querySelectorAll('*').forEach(el => {
                            el.style.outline = '';
                            el.style.outlineOffset = '';
                        });
                    }
                """
                )

            logger.info(f"Captured {len(screenshots)} comprehensive screenshots")

        except Exception as e:
            logger.error(f"Failed to capture screenshots: {e}")

        return screenshots

    async def crawl(
        self, start_url: str, max_pages: int = 10, max_depth: int = 2, follow_pattern: Optional[str] = None
    ) -> CrawlResult:
        """
        Crawl website starting from URL

        Args:
            start_url: Starting URL
            max_pages: Maximum pages to visit
            max_depth: Maximum depth to crawl
            follow_pattern: Optional regex pattern for URLs to follow

        Returns:
            CrawlResult with all extraction results
        """
        start_time = time.time()
        visited: Set[str] = set()
        to_visit: List[Tuple[str, int]] = [(start_url, 0)]
        extraction_results: List[ExtractionResult] = []
        total_elements = 0
        max_depth_reached = 0
        errors: List[str] = []

        while to_visit and len(visited) < max_pages:
            url, depth = to_visit.pop(0)

            if url in visited or depth > max_depth:
                continue

            logger.info(f"Crawling page {len(visited) + 1}/{max_pages}: {url} (depth={depth})")

            try:
                # Extract elements from page
                result = await self.extract_from_url(url)
                extraction_results.append(result)
                visited.add(url)
                total_elements += len(result.elements)
                max_depth_reached = max(max_depth_reached, depth)

                # Extract links for crawling
                if depth < max_depth:
                    for element in result.elements:
                        if element.element_type == ElementType.LINK:
                            href = element.attributes.get("href")
                            if href:
                                absolute_url = urljoin(url, href)

                                # Check if URL matches pattern
                                if follow_pattern:
                                    if not re.match(follow_pattern, absolute_url):
                                        continue

                                # Check if same domain
                                if urlparse(absolute_url).netloc == urlparse(start_url).netloc:
                                    if absolute_url not in visited:
                                        to_visit.append((absolute_url, depth + 1))

            except Exception as e:
                logger.error(f"Failed to crawl {url}: {e}")
                errors.append(f"{url}: {str(e)}")

        crawl_time = time.time() - start_time

        logger.info(f"Crawl complete. Visited {len(visited)} pages, discovered {len(to_visit)} URLs")

        return CrawlResult(
            start_url=start_url,
            pages_visited=list(visited),
            extraction_results=extraction_results,
            total_elements=total_elements,
            crawl_time=crawl_time,
            max_depth_reached=max_depth_reached,
            errors=errors,
        )

    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            if self._browser:
                await self._browser.cleanup()
                self._browser = None

            if self._cache:
                self._cache.clear()

            memory_cleanup()
            logger.info("Cleanup completed successfully")

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

    # ==================== QA-FOCUSED METHODS ====================
    
    def _calculate_qa_interaction_score(self, element: Element) -> float:
        """
        Calculate QA relevance score for an element (0.0 to 1.0)
        Senior QA perspective: Focus on testability and user interaction points
        """
        score = 0.0
        
        # Core interactive elements (highest priority)
        if element.is_clickable or element.is_editable:
            score += 0.4
        
        # Form-related elements
        if element.tag_name in ['input', 'button', 'select', 'textarea']:
            score += 0.3
        elif element.tag_name == 'form':
            score += 0.2
        elif element.tag_name in ['label', 'fieldset', 'legend']:
            score += 0.1
            
        # Check for validation attributes (critical for QA)
        validation_attrs = ['required', 'pattern', 'min', 'max', 'minlength', 
                           'maxlength', 'step', 'readonly', 'disabled']
        if element.attributes:
            for attr in validation_attrs:
                if attr in element.attributes:
                    score += 0.1
                    break
        
        # ARIA interactive roles
        if element.attributes and element.attributes.get('role'):
            interactive_roles = ['button', 'link', 'checkbox', 'radio', 'textbox',
                               'combobox', 'listbox', 'slider', 'switch', 'tab',
                               'menuitem', 'option', 'searchbox', 'spinbutton']
            if element.attributes['role'] in interactive_roles:
                score += 0.2
        
        # Keyboard accessibility (important for QA)
        if element.attributes:
            if 'tabindex' in element.attributes:
                tabindex = element.attributes.get('tabindex', '0')
                if tabindex != '-1':  # Element is keyboard accessible
                    score += 0.1
        
        # Event handlers (indicates interactivity)
        event_indicators = ['onclick', 'onchange', 'oninput', 'onsubmit', 
                           'ng-click', 'data-action', 'data-toggle']
        if element.attributes:
            for indicator in event_indicators:
                if indicator in element.attributes:
                    score += 0.2
                    break
        
        # Navigation elements
        if element.tag_name == 'a' and element.attributes:
            href = element.attributes.get('href', '')
            if href and href != '#' and href != 'javascript:void(0)':
                score += 0.3
        
        # Error/validation message containers (QA critical)
        if element.attributes:
            error_indicators = ['error', 'invalid', 'validation', 'alert', 'warning']
            for attr, value in element.attributes.items():
                if any(ind in str(value).lower() for ind in error_indicators):
                    score += 0.2
                    break
        
        return min(score, 1.0)  # Cap at 1.0

    def _is_qa_relevant_element(self, element: Element) -> bool:
        """
        Determine if element is relevant for QA testing
        Senior QA perspective: Filter noise, focus on testable interactions
        """
        if not self.config.qa_mode:
            return True  # If not in QA mode, include everything
        
        # Calculate interaction score
        score = self._calculate_qa_interaction_score(element)
        
        # Check minimum score threshold
        if score < self.config.qa_min_interaction_score:
            return False
        
        # Special QA considerations
        if element.attributes:
            # Include disabled elements if configured (for negative testing)
            if not self.config.qa_include_disabled:
                if element.attributes.get('disabled') or not element.is_enabled:
                    return False
            
            # Include hidden elements that might toggle
            if not element.is_visible and self.config.qa_include_hidden_toggles:
                # Check if element might become visible
                if not self._might_toggle_visibility(element):
                    return False
        
        # Exclude purely decorative or structural elements
        excluded_for_qa = ['script', 'style', 'meta', 'br', 'hr', 'noscript',
                           'svg', 'path', 'g', 'defs', 'clipPath']
        if element.tag_name in excluded_for_qa:
            return False
        
        # Exclude elements without meaningful interaction potential
        if not any([
            element.is_clickable,
            element.is_editable,
            element.tag_name in self.config.qa_priority_tags,
            element.attributes and any(
                ind in str(element.attributes) 
                for ind in self.config.qa_interaction_indicators
            )
        ]):
            return False
        
        return True
    
    def _might_toggle_visibility(self, element: Element) -> bool:
        """Check if hidden element might become visible through interaction"""
        if not element.attributes:
            return False
        
        # Check for toggle indicators
        toggle_indicators = [
            'data-toggle', 'data-target', 'aria-controls', 
            'aria-expanded', 'data-bs-toggle', 'x-show'
        ]
        
        return any(ind in element.attributes for ind in toggle_indicators)
    
    def get_qa_test_elements(self, 
                             elements: List[Element],
                             category: Optional[str] = None) -> List[Element]:
        """
        Get elements filtered by QA test category
        Categories: 'input', 'navigation', 'action', 'validation', 'form'
        """
        if not elements:
            return []
        
        category_filters = {
            'input': lambda e: e.is_editable or e.tag_name in ['input', 'textarea', 'select'],
            'navigation': lambda e: e.tag_name == 'a' or (e.attributes and 'href' in e.attributes),
            'action': lambda e: e.is_clickable or e.tag_name == 'button',
            'validation': lambda e: e.attributes and any(
                attr in e.attributes for attr in ['required', 'pattern', 'min', 'max']
            ),
            'form': lambda e: e.tag_name in ['form', 'input', 'select', 'textarea', 'button', 'label']
        }
        
        if category and category in category_filters:
            return [e for e in elements if category_filters[category](e)]
        
        return elements
    
    def get_qa_summary(self, elements: List[Element]) -> Dict[str, Any]:
        """Generate QA-focused summary of extracted elements"""
        return {
            'total_interactive': sum(1 for e in elements if e.is_clickable or e.is_editable),
            'forms': len(set(e.parent_selector for e in elements if e.tag_name == 'form' and e.parent_selector)),
            'inputs': sum(1 for e in elements if e.tag_name == 'input'),
            'buttons': sum(1 for e in elements if e.tag_name == 'button'),
            'links': sum(1 for e in elements if e.tag_name == 'a'),
            'required_fields': sum(1 for e in elements if e.attributes and 'required' in e.attributes),
            'disabled_elements': sum(1 for e in elements if not e.is_enabled),
            'hidden_interactive': sum(1 for e in elements if not e.is_visible and (e.is_clickable or e.is_editable)),
            'with_validation': sum(1 for e in elements if e.attributes and 
                                  any(v in e.attributes for v in ['pattern', 'min', 'max', 'required'])),
            'keyboard_accessible': sum(1 for e in elements if e.attributes and 
                                      'tabindex' in e.attributes and e.attributes['tabindex'] != '-1')
        }


# ==================== STANDALONE FUNCTIONS ====================

async def extract_elements(url: str, config: Optional[ExtractionConfig] = None) -> Optional[ExtractionResult]:
    """
    Standalone function to extract elements from a URL

    Args:
        url: The URL to extract elements from
        config: Optional extraction configuration

    Returns:
        ExtractionResult or None if extraction fails
    """
    extractor = ElementsExtractorNoLLM(config)
    try:
        result = await extractor.extract_from_url(url)
        return result if result.success else None
    finally:
        await extractor.cleanup()


async def crawl_website(
    start_url: str,
    max_pages: int = 10,
    max_depth: int = 2,
    config: Optional[ExtractionConfig] = None
) -> CrawlResult:
    """
    Standalone function to crawl a website and extract elements

    Args:
        start_url: The starting URL for crawling
        max_pages: Maximum number of pages to crawl
        max_depth: Maximum depth for crawling
        config: Optional extraction configuration

    Returns:
        CrawlResult containing all extraction results
    """
    extractor = ElementsExtractorNoLLM(config)
    try:
        result = await extractor.crawl(start_url, max_pages, max_depth)
        return result
    finally:
        await extractor.cleanup()


def extract_elements_sync(url: str, config: Optional[ExtractionConfig] = None) -> Optional[ExtractionResult]:
    """
    Synchronous wrapper for extract_elements

    Args:
        url: The URL to extract elements from
        config: Optional extraction configuration

    Returns:
        ExtractionResult or None if extraction fails
    """
    return asyncio.run(extract_elements(url, config))


# ==================== EXAMPLE USAGE ====================


async def example_basic_extraction() -> None:
    """Example: Basic element extraction"""
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 1: Basic Element Extraction")
    logger.info("=" * 80)

    # Create extractor with basic config
    config = ExtractionConfig(
        enable_shadow_dom=True,
        enable_iframe_traversal=True,
        filter_invisible=True,
        capture_screenshots=False,
    )

    extractor = ElementsExtractorNoLLM(config)

    # Extract elements from a simple website
    logger.info("\nExtracting elements from: https://example.com")
    logger.info("-" * 40)

    result = await extractor.extract_from_url("https://example.com")

    if result.success:
        logger.info(f"SUCCESS: Extracted {len(result.elements)} elements")
        logger.info(f"Extraction time: {result.extraction_time:.2f} seconds")

        # Show element type distribution
        logger.info("\nElement type distribution:")
        type_counts = Counter(e.element_type.value for e in result.elements)
        for element_type, count in type_counts.most_common():
            logger.info(f"  - {element_type}: {count}")

        # Show sample elements
        logger.info("\nSample elements (showing first 5):")
        for i, element in enumerate(result.elements[:5], 1):
            logger.info(f"\n  {i}. {element.element_type.value.upper()}")
            logger.info(f"     Tag: {element.tag_name}")
            if element.text:
                logger.info(f"     Text: {element.text[:50]}...")
            if best_selector := element.get_best_selector():
                logger.info(f"     Best selector: {best_selector.value} (score: {best_selector.score:.2f})")
            logger.info(f"     Confidence: {element.confidence:.2f}")
            logger.info(f"     Interactions: {[i.value for i in element.interaction_types]}")

        # Show statistics
        logger.info("\nExtraction Statistics:")
        for key, value in result.statistics.items():
            if not isinstance(value, dict):
                logger.info(f"  - {key}: {value}")
    else:
        logger.error("Failed to extract elements")
        for error in result.errors:
            logger.error(f"  - {error}")

    # Cleanup
    await extractor.cleanup()
    logger.info("\n" + "=" * 80)


async def example_advanced_extraction() -> None:
    """Example: Advanced extraction with screenshots and crawling"""
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 2: Advanced Extraction with Screenshots and Crawling")
    logger.info("=" * 80)

    # Create extractor with advanced config
    config = ExtractionConfig(
        enable_shadow_dom=True,
        enable_iframe_traversal=True,
        enable_stealth=True,
        filter_invisible=True,
        min_element_size=10,
        capture_screenshots=True,
        screenshot_full_page=False,
        highlight_elements=True,
        highlight_color="blue",
        highlight_width=3,
        max_elements=500,
    )

    extractor = ElementsExtractorNoLLM(config)

    # Extract with screenshots
    logger.info("\nExtracting elements from: https://www.wikipedia.org")
    logger.info("Configuration:")
    logger.info(f"  - Shadow DOM extraction: {config.enable_shadow_dom}")
    logger.info(f"  - Iframe traversal: {config.enable_iframe_traversal}")
    logger.info(f"  - Stealth mode: {config.enable_stealth}")
    logger.info(f"  - Screenshots enabled: {config.capture_screenshots}")
    logger.info(f"  - Full page screenshots: {config.screenshot_full_page}")
    logger.info(f"  - Highlight elements: {config.highlight_elements}")
    logger.info(f"  - Min element size: {config.min_element_size}px")
    logger.info("-" * 40)

    result = await extractor.extract_from_url("https://www.wikipedia.org")

    if result.success:
        logger.info(f"SUCCESS: Extracted {len(result.elements)} elements")
        logger.info(f"Total found: {result.statistics.get('total_elements', 0)}")

        # Selector strategy analysis
        logger.info("\nSelector Strategy Analysis:")
        if "selector_strategies" in result.statistics:
            total_strategies = sum(result.statistics["selector_strategies"].values())
            for strategy, count in sorted(
                result.statistics["selector_strategies"].items(), key=lambda x: x[1], reverse=True
            ):
                percentage = (count / total_strategies * 100) if total_strategies > 0 else 0
                logger.info(f"  - {strategy}: {count} ({percentage:.1f}%)")

        # Most confident elements
        logger.info("\nMost Confident Elements (Top 5):")
        sorted_elements = sorted(result.elements, key=lambda e: e.confidence, reverse=True)
        for i, element in enumerate(sorted_elements[:5], 1):
            logger.info(f"  {i}. {element.element_type.value} - Confidence: {element.confidence:.3f}")
            if element.text:
                logger.info(f"     Text: {element.text[:50]}...")

        # Special elements
        logger.info("\nSpecial Elements Found:")
        logger.info(f"  - Shadow DOM elements: {result.statistics.get('shadow_elements', 0)}")
        logger.info(f"  - Iframe elements: {result.statistics.get('iframe_elements', 0)}")
        logger.info(f"  - Form elements: {sum(1 for e in result.elements if e.element_type == ElementType.FORM)}")

        # Interactive elements
        logger.info("\nInteractive Elements Analysis:")
        logger.info(f"  - Clickable: {result.statistics.get('clickable_elements', 0)}")
        logger.info(f"  - Editable: {result.statistics.get('editable_elements', 0)}")
        logger.info(f"  - Buttons: {sum(1 for e in result.elements if e.element_type == ElementType.BUTTON)}")
        logger.info(f"  - Links: {sum(1 for e in result.elements if e.element_type == ElementType.LINK)}")
        logger.info(f"  - Inputs: {sum(1 for e in result.elements if e.element_type == ElementType.INPUT)}")

        # Screenshots
        if result.screenshots:
            logger.info(f"\nScreenshots Captured: {len(result.screenshots)}")
            for i, screenshot in enumerate(result.screenshots, 1):
                logger.info(f"  {i}. Format: {screenshot.format}, Size: {screenshot.width}x{screenshot.height}")
                logger.info(f"     Full page: {getattr(screenshot, 'full_page', 'N/A')}")
                if screenshot.highlighted_elements:
                    logger.info(f"     Highlighted elements: {len(screenshot.highlighted_elements)}")

            # Save screenshots to temp directory
            temp_dir = Path(mkdtemp(prefix="extractor_screenshots_"))
            saved_paths = result.save_screenshots(temp_dir)
            logger.info(f"\nScreenshots saved to: {temp_dir}")
            for path in saved_paths:
                logger.info(f"  - {path.name}")

    # Crawling demo
    logger.info("\n" + "=" * 40)
    logger.info("Crawling Demo (Limited to 3 pages)")
    logger.info("=" * 40)

    crawl_result = await extractor.crawl(
        start_url="https://www.wikipedia.org",
        max_pages=3,
        max_depth=1,
    )

    logger.info("\nCrawl Statistics:")
    logger.info(f"  - pages_visited: {len(crawl_result.pages_visited)}")
    logger.info(f"  - urls_discovered: {len(crawl_result.pages_visited)}")
    logger.info(f"  - successful_extractions: {len(crawl_result.extraction_results)}")
    logger.info(f"  - total_elements_extracted: {crawl_result.total_elements}")
    pages_count = len(crawl_result.pages_visited)
    avg_elements = crawl_result.total_elements / pages_count if pages_count > 0 else 0
    logger.info(f"  - avg_elements_per_page: {avg_elements:.1f}")

    logger.info("\nPages Crawled:")
    for i, page in enumerate(crawl_result.pages_visited, 1):
        if i <= len(crawl_result.extraction_results):
            result = crawl_result.extraction_results[i - 1]
            logger.info(f"  {i}. {page[:80]}...")
            logger.info(f"     Elements: {len(result.elements)}")
            logger.info(f"     Success: {result.success}")

    # Cleanup
    await extractor.cleanup()
    logger.info("\n" + "=" * 80)


async def main() -> None:
    """Main entry point for the module"""
    logger.info("\n" + "=" * 80)
    logger.info("ELEMENTS EXTRACTOR NO LLM - Production Module")
    logger.info("Standalone DOM-based element extraction without LLM dependencies")
    logger.info("=" * 80)
    logger.info("\nCapabilities:")
    logger.info("  - Pure DOM-based extraction")
    logger.info("  - Shadow DOM and iframe support")
    logger.info("  - Intelligent selector generation")
    logger.info("  - Element classification and validation")
    logger.info("  - Anti-detection via browser.py")
    logger.info("  - Web crawling and discovery")
    logger.info("  - Performance monitoring")
    logger.info("  - Caching support")

    if not BROWSER_MODULE_AVAILABLE:
        logger.error("\nERROR: Browser module not available!")
        logger.error("This module requires browser.py to be present.")
        return

    # Run examples
    await example_basic_extraction()
    await example_advanced_extraction()

    logger.info("\n" + "=" * 80)
    logger.info("Examples completed successfully!")
    logger.info("This module is ready for production use.")
    logger.info("=" * 80)


if __name__ == "__main__":
    # Run examples automatically
    asyncio.run(main())
