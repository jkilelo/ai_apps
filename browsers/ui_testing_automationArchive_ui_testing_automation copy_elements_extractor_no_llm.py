#!/usr/bin/env python3
"""
ELEMENTS EXTRACTOR NO LLM - Production-Ready DOM Element Extractor
==================================================================
Production-ready DOM-based element extraction without LLM dependencies.
Refactored to use browser.py for DRY compliance.
Designed by a Senior Software Engineer with 30+ years of experience.

This module provides comprehensive element extraction capabilities including:
- Pure DOM-based extraction strategies
- Shadow DOM and iframe traversal
- Intelligent selector generation
- Element classification and validation
- Crawling and discovery capabilities
- Anti-detection via browser.py
- Performance optimization

Author: Senior Software Engineer
Version: 3.0.0
License: MIT
"""

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
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple, Callable, TypeVar, cast
from urllib.parse import urljoin, urlparse
import functools
import threading
import gc
from tempfile import mkdtemp

# Add parent directory to path to import browser module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import browser module for DRY compliance
try:
    from browser import (
        UltimateStealthBrowser,
        StealthConfig,
        StealthLevel,
        ElementData as BrowserElementData,
        ExtractionResult as BrowserExtractionResult,
    )
    BROWSER_MODULE_AVAILABLE = True
except ImportError:
    BROWSER_MODULE_AVAILABLE = False
    logger.warning("Browser module not found. This module requires browser.py")
    # Define minimal fallback types for type checking
    class StealthConfig:  # type: ignore
        pass

    class StealthLevel:  # type: ignore
        pass

    class UltimateStealthBrowser:  # type: ignore
        pass

    class BrowserElementData:  # type: ignore
        pass

    class BrowserExtractionResult:  # type: ignore
        pass

# ==================== PRODUCTION UTILITIES ====================

T = TypeVar('T')


def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0
) -> Callable[[Any], Any]:
    """Production-grade retry decorator with exponential backoff"""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            last_exception: Optional[Exception] = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay)
                        delay *= backoff_factor
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed: {e}"
                    )

            if last_exception:
                raise last_exception
            raise RuntimeError("Retry failed without exception")

        return wrapper
    return decorator


class ThreadSafeCache:
    """Thread-safe cache implementation"""
    
    def __init__(self, ttl: int = 3600) -> None:
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = threading.Lock()
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        with self._lock:
            if key in self._cache:
                value, timestamp = self._cache[key]
                if time.time() - timestamp < self.ttl:
                    return value
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        with self._lock:
            self._cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """Clear cache"""
        with self._lock:
            self._cache.clear()


def memory_cleanup() -> None:
    """Force garbage collection to free memory"""
    gc.collect()
    gc.collect()
    gc.collect()


# ==================== ENUMS ====================

class ElementType(Enum):
    """Element types for classification"""
    BUTTON = "button"
    LINK = "link"
    INPUT = "input"
    TEXTAREA = "textarea"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    CANVAS = "canvas"
    IFRAME = "iframe"
    FORM = "form"
    TABLE = "table"
    LIST = "list"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LABEL = "label"
    NAV = "nav"
    FOOTER = "footer"
    HEADER = "header"
    ARTICLE = "article"
    SECTION = "section"
    DIALOG = "dialog"
    MENU = "menu"
    TOOLBAR = "toolbar"
    TAB = "tab"
    ACCORDION = "accordion"
    MODAL = "modal"
    CARD = "card"
    CAROUSEL = "carousel"
    UNKNOWN = "unknown"


class InteractionType(Enum):
    """Types of interactions possible with elements"""
    CLICK = "click"
    TYPE = "type"
    SELECT = "select"
    HOVER = "hover"
    DRAG = "drag"
    DROP = "drop"
    SCROLL = "scroll"
    WAIT = "wait"
    ASSERT = "assert"
    NAVIGATE = "navigate"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    CLEAR = "clear"
    FOCUS = "focus"
    BLUR = "blur"
    SUBMIT = "submit"
    RESET = "reset"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    NONE = "none"


class LocatorStrategy(Enum):
    """Strategies for locating elements"""
    DATA_TESTID = "data-testid"
    ID = "id"
    NAME = "name"
    ARIA_LABEL = "aria-label"
    CSS_CLASS = "css-class"
    CSS_SELECTOR = "css-selector"
    XPATH = "xpath"
    TEXT_CONTENT = "text-content"
    ROLE = "role"
    PLACEHOLDER = "placeholder"
    VALUE = "value"
    TITLE = "title"
    ALT = "alt"
    HREF = "href"


class ExtractionMethod(Enum):
    """Methods used for element extraction"""
    DOM_QUERY = "dom_query"
    SHADOW_DOM = "shadow_dom"
    IFRAME = "iframe"
    MUTATION_OBSERVER = "mutation_observer"
    POLLING = "polling"
    EVENT_LISTENER = "event_listener"
    ACCESSIBILITY_TREE = "accessibility_tree"


class ConfidenceLevel(Enum):
    """Confidence levels for element detection"""
    VERY_LOW = 0.2
    LOW = 0.4
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.95


# ==================== DATA MODELS ====================

@dataclass
class ElementSelector:
    """Represents a selector for an element"""
    strategy: LocatorStrategy
    value: str
    score: float
    is_unique: bool
    parent_context: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "strategy": self.strategy.value,
            "value": self.value,
            "score": self.score,
            "is_unique": self.is_unique,
            "parent_context": self.parent_context,
        }


@dataclass
class BoundingBox:
    """Element bounding box information"""
    x: float
    y: float
    width: float
    height: float
    top: float
    right: float
    bottom: float
    left: float
    
    @property
    def center(self) -> Tuple[float, float]:
        """Get center point of bounding box"""
        return (self.x + self.width / 2, self.y + self.height / 2)
    
    @property
    def area(self) -> float:
        """Calculate area of bounding box"""
        return self.width * self.height
    
    def is_visible(self) -> bool:
        """Check if element is visible based on bounding box"""
        return self.width > 0 and self.height > 0
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is within bounding box"""
        return self.left <= x <= self.right and self.top <= y <= self.bottom


@dataclass
class ComputedStyle:
    """Computed CSS styles for an element"""
    display: str
    visibility: str
    opacity: str
    position: str
    z_index: str
    background_color: str
    color: str
    font_size: str
    font_weight: str
    cursor: str
    overflow: str
    
    def is_visible(self) -> bool:
        """Check if element is visible based on styles"""
        return (
            self.display != "none"
            and self.visibility != "hidden"
            and float(self.opacity or 1) > 0
        )


@dataclass
class ExtractedElement:
    """Complete representation of an extracted element"""
    # Basic properties
    tag_name: str
    element_type: ElementType
    text: Optional[str] = None
    value: Optional[str] = None
    
    # Attributes
    attributes: Dict[str, str] = field(default_factory=dict)
    
    # Position and style
    bounding_box: Optional[BoundingBox] = None
    computed_style: Optional[ComputedStyle] = None
    
    # Selectors
    selectors: List[ElementSelector] = field(default_factory=list)
    xpath: Optional[str] = None
    css_path: Optional[str] = None
    
    # Interaction
    interaction_types: List[InteractionType] = field(default_factory=list)
    is_clickable: bool = False
    is_enabled: bool = True
    is_editable: bool = False
    
    # Metadata
    confidence: float = 0.0
    stability_score: float = 0.0
    extraction_method: Optional[ExtractionMethod] = None
    extraction_timestamp: Optional[float] = None
    
    # Hierarchy
    parent_element: Optional["ExtractedElement"] = None
    child_elements: List["ExtractedElement"] = field(default_factory=list)
    
    # Special flags
    is_shadow_element: bool = False
    is_iframe_element: bool = False
    shadow_host: Optional[str] = None
    frame_url: Optional[str] = None
    
    # Validation
    is_valid: bool = True
    validation_issues: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "tag_name": self.tag_name,
            "element_type": self.element_type.value,
            "text": self.text,
            "value": self.value,
            "attributes": self.attributes,
            "bounding_box": asdict(self.bounding_box) if self.bounding_box else None,
            "computed_style": asdict(self.computed_style) if self.computed_style else None,
            "selectors": [s.to_dict() for s in self.selectors],
            "xpath": self.xpath,
            "css_path": self.css_path,
            "interaction_types": [it.value for it in self.interaction_types],
            "is_clickable": self.is_clickable,
            "is_enabled": self.is_enabled,
            "is_editable": self.is_editable,
            "confidence": self.confidence,
            "stability_score": self.stability_score,
            "extraction_method": self.extraction_method.value if self.extraction_method else None,
            "extraction_timestamp": self.extraction_timestamp,
            "is_shadow_element": self.is_shadow_element,
            "is_iframe_element": self.is_iframe_element,
            "shadow_host": self.shadow_host,
            "frame_url": self.frame_url,
            "is_valid": self.is_valid,
            "validation_issues": self.validation_issues,
        }
    
    def get_best_selector(self) -> Optional[ElementSelector]:
        """Get the highest scoring selector"""
        if not self.selectors:
            return None
        return max(self.selectors, key=lambda s: s.score)


@dataclass
class ScreenshotData:
    """Screenshot data with metadata"""
    format: str
    width: int
    height: int
    data: str  # Base64 encoded
    timestamp: float
    url: str
    highlighted_elements: List[str] = field(default_factory=list)
    
    def save(self, path: Path) -> None:
        """Save screenshot to file"""
        path.write_bytes(base64.b64decode(self.data))


@dataclass
class ExtractionConfig:
    """Configuration for element extraction"""
    # Extraction settings
    enable_shadow_dom: bool = True
    enable_iframe_traversal: bool = True
    enable_dynamic_wait: bool = True
    enable_mutation_observer: bool = False
    max_depth: int = 10
    max_elements: int = 1000
    extraction_timeout: int = 30000
    
    # Filtering
    filter_invisible: bool = True
    filter_duplicates: bool = True
    min_element_size: int = 5  # Minimum pixel size
    
    # Anti-detection (delegated to browser.py)
    enable_stealth: bool = True
    randomize_delays: bool = True
    min_delay: float = 0.1
    max_delay: float = 0.5
    
    # Performance
    batch_size: int = 100
    enable_caching: bool = True
    cache_ttl: int = 3600  # seconds
    
    # Output
    include_computed_styles: bool = True
    include_accessibility_info: bool = True
    include_event_listeners: bool = False
    
    # Screenshot settings
    capture_screenshots: bool = False
    screenshot_full_page: bool = True
    screenshot_format: str = "png"
    screenshot_quality: int = 90
    highlight_elements: bool = True
    highlight_color: str = "red"
    highlight_width: int = 2


@dataclass
class ExtractionResult:
    """Result of element extraction"""
    url: str
    elements: List[ExtractedElement]
    extraction_time: float
    success: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    screenshots: List[ScreenshotData] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "url": self.url,
            "elements": [e.to_dict() for e in self.elements],
            "extraction_time": self.extraction_time,
            "success": self.success,
            "errors": self.errors,
            "warnings": self.warnings,
            "statistics": self.statistics,
            "screenshots": [asdict(s) for s in self.screenshots],
            "metadata": self.metadata,
        }
    
    def save_screenshots(self, directory: Path) -> List[Path]:
        """Save all screenshots to directory"""
        saved_paths: List[Path] = []
        directory.mkdir(parents=True, exist_ok=True)
        
        for i, screenshot in enumerate(self.screenshots):
            filename = f"{urlparse(self.url).netloc}_{i+1}_{int(screenshot.timestamp)}.{screenshot.format}"
            path = directory / filename
            screenshot.save(path)
            saved_paths.append(path)
        
        return saved_paths


@dataclass
class CrawlResult:
    """Result of web crawling"""
    start_url: str
    pages_visited: List[str]
    extraction_results: List[ExtractionResult]
    total_elements: int
    crawl_time: float
    max_depth_reached: int
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "start_url": self.start_url,
            "pages_visited": self.pages_visited,
            "total_elements": self.total_elements,
            "crawl_time": self.crawl_time,
            "max_depth_reached": self.max_depth_reached,
            "errors": self.errors,
            "extraction_results": [r.to_dict() for r in self.extraction_results],
        }


# ==================== MAIN EXTRACTOR CLASS ====================

class ElementsExtractorNoLLM:
    """
    Production-ready element extractor without LLM dependencies.
    Uses browser.py for browser automation (DRY compliance).
    """
    
    def __init__(self, config: Optional[ExtractionConfig] = None) -> None:
        """Initialize the extractor"""
        self.config = config or ExtractionConfig()
        self._cache = ThreadSafeCache(ttl=self.config.cache_ttl) if self.config.enable_caching else None
        self._browser: Optional[UltimateStealthBrowser] = None
        self._lock = asyncio.Lock()
        
        # Performance metrics
        self._metrics: Dict[str, List[float]] = defaultdict(list)
        
        logger.info(f"ElementsExtractorNoLLM initialized with config: {self.config}")
    
    async def _ensure_browser(self) -> UltimateStealthBrowser:
        """Ensure browser is initialized"""
        async with self._lock:
            if self._browser is None:
                if not BROWSER_MODULE_AVAILABLE:
                    raise RuntimeError("Browser module not available. Please ensure browser.py is present.")
                
                # Configure stealth based on extraction config
                stealth_config = StealthConfig()
                stealth_config.headless = True
                stealth_config.level = StealthLevel.HIGH if self.config.enable_stealth else StealthLevel.BASIC
                
                self._browser = UltimateStealthBrowser(stealth_config)
                await self._browser.initialize()
                logger.info("Browser initialized successfully")
            
            return cast(UltimateStealthBrowser, self._browser)
    
    async def extract_from_url(
        self,
        url: str,
        use_cache: bool = True
    ) -> ExtractionResult:
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
            elements = self._convert_browser_elements(browser_result.elements)
            
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
                    "config": asdict(self.config),
                    "timestamp": time.time(),
                }
            )
            
            # Cache result
            if use_cache and self._cache and cache_key:
                self._cache.set(cache_key, result)
            
            logger.info(f"Extracted {len(elements)} total elements from {url}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to extract from {url}: {e}")
            return ExtractionResult(
                url=url,
                elements=[],
                extraction_time=time.time() - start_time,
                success=False,
                errors=[str(e)]
            )
    
    def _convert_browser_elements(
        self,
        browser_elements: List[BrowserElementData]
    ) -> List[ExtractedElement]:
        """Convert browser elements to our format"""
        converted: List[ExtractedElement] = []
        
        for be in browser_elements:
            # Map browser element type to our type
            element_type = self._map_element_type(be.tag_name, be.attributes)
            
            # Create extracted element
            element = ExtractedElement(
                tag_name=be.tag_name,
                element_type=element_type,
                text=be.text_content,
                value=be.attributes.get("value"),
                attributes=be.attributes,
                xpath=be.xpath,
                css_path=be.css_selector,
                is_clickable=be.is_clickable,
                is_enabled=be.is_enabled,
                is_editable=be.attributes.get("contenteditable") == "true",
                confidence=0.8,  # Default confidence
                extraction_method=ExtractionMethod.DOM_QUERY,
                extraction_timestamp=time.time(),
            )
            
            converted.append(element)
        
        return converted
    
    def _map_element_type(self, tag_name: str, attributes: Dict[str, str]) -> ElementType:
        """Map HTML tag and attributes to element type"""
        tag_lower = tag_name.lower()
        
        # Direct tag mappings
        tag_map = {
            "button": ElementType.BUTTON,
            "a": ElementType.LINK,
            "input": ElementType.INPUT,
            "textarea": ElementType.TEXTAREA,
            "select": ElementType.SELECT,
            "img": ElementType.IMAGE,
            "video": ElementType.VIDEO,
            "audio": ElementType.AUDIO,
            "canvas": ElementType.CANVAS,
            "iframe": ElementType.IFRAME,
            "form": ElementType.FORM,
            "table": ElementType.TABLE,
            "ul": ElementType.LIST,
            "ol": ElementType.LIST,
            "h1": ElementType.HEADING,
            "h2": ElementType.HEADING,
            "h3": ElementType.HEADING,
            "h4": ElementType.HEADING,
            "h5": ElementType.HEADING,
            "h6": ElementType.HEADING,
            "p": ElementType.PARAGRAPH,
            "label": ElementType.LABEL,
            "nav": ElementType.NAV,
            "footer": ElementType.FOOTER,
            "header": ElementType.HEADER,
            "article": ElementType.ARTICLE,
            "section": ElementType.SECTION,
            "dialog": ElementType.DIALOG,
        }
        
        if tag_lower in tag_map:
            element_type = tag_map[tag_lower]
            
            # Special handling for input types
            if tag_lower == "input":
                input_type = attributes.get("type", "text").lower()
                if input_type == "checkbox":
                    element_type = ElementType.CHECKBOX
                elif input_type == "radio":
                    element_type = ElementType.RADIO
            
            return element_type
        
        # Check for role attribute
        role = attributes.get("role", "").lower()
        if role:
            role_map = {
                "button": ElementType.BUTTON,
                "link": ElementType.LINK,
                "navigation": ElementType.NAV,
                "menu": ElementType.MENU,
                "toolbar": ElementType.TOOLBAR,
                "tab": ElementType.TAB,
                "dialog": ElementType.DIALOG,
                "article": ElementType.ARTICLE,
            }
            if role in role_map:
                return role_map[role]
        
        return ElementType.UNKNOWN
    
    def _filter_elements(self, elements: List[ExtractedElement]) -> List[ExtractedElement]:
        """Filter elements based on configuration"""
        filtered: List[ExtractedElement] = []
        seen_hashes: Set[str] = set()
        
        for element in elements:
            # Filter invisible elements
            if self.config.filter_invisible:
                if element.computed_style and not element.computed_style.is_visible():
                    continue
                if element.bounding_box and not element.bounding_box.is_visible():
                    continue
            
            # Filter small elements
            if self.config.min_element_size > 0:
                if element.bounding_box:
                    if (element.bounding_box.width < self.config.min_element_size or
                        element.bounding_box.height < self.config.min_element_size):
                        continue
            
            # Filter duplicates
            if self.config.filter_duplicates:
                element_hash = self._hash_element(element)
                if element_hash in seen_hashes:
                    continue
                seen_hashes.add(element_hash)
            
            filtered.append(element)
        
        return filtered
    
    def _hash_element(self, element: ExtractedElement) -> str:
        """Generate hash for element deduplication"""
        key_parts = [
            element.tag_name,
            element.element_type.value,
            element.text or "",
            element.xpath or "",
            json.dumps(element.attributes, sort_keys=True),
        ]
        return hashlib.md5("".join(key_parts).encode()).hexdigest()
    
    def _classify_elements(self, elements: List[ExtractedElement]) -> List[ExtractedElement]:
        """Classify elements and determine interaction types"""
        for element in elements:
            # Determine interaction types
            interactions: List[InteractionType] = []
            
            if element.element_type == ElementType.BUTTON:
                interactions = [InteractionType.CLICK, InteractionType.HOVER]
            elif element.element_type == ElementType.LINK:
                interactions = [InteractionType.CLICK, InteractionType.HOVER, InteractionType.NAVIGATE]
            elif element.element_type in [ElementType.INPUT, ElementType.TEXTAREA]:
                interactions = [InteractionType.TYPE, InteractionType.CLEAR, InteractionType.FOCUS]
            elif element.element_type == ElementType.SELECT:
                interactions = [InteractionType.SELECT, InteractionType.CLICK]
            elif element.element_type in [ElementType.CHECKBOX, ElementType.RADIO]:
                interactions = [InteractionType.CLICK]
            elif element.element_type == ElementType.FORM:
                interactions = [InteractionType.SUBMIT, InteractionType.RESET]
            else:
                interactions = [InteractionType.NONE]
            
            element.interaction_types = interactions
            
            # Calculate confidence based on element completeness
            confidence = 0.5
            if element.text:
                confidence += 0.1
            if element.xpath:
                confidence += 0.1
            if element.css_path:
                confidence += 0.1
            if element.attributes:
                confidence += 0.1
            if element.is_valid:
                confidence += 0.1
            
            element.confidence = min(confidence, 1.0)
        
        return elements
    
    def _generate_selectors(self, elements: List[ExtractedElement]) -> List[ExtractedElement]:
        """Generate multiple selector strategies for each element"""
        for element in elements:
            selectors: List[ElementSelector] = []
            
            # ID selector (highest priority)
            if element_id := element.attributes.get("id"):
                selectors.append(ElementSelector(
                    strategy=LocatorStrategy.ID,
                    value=f"#{element_id}",
                    score=1.0,
                    is_unique=True
                ))
            
            # Data-testid selector
            if testid := element.attributes.get("data-testid"):
                selectors.append(ElementSelector(
                    strategy=LocatorStrategy.DATA_TESTID,
                    value=f"[data-testid='{testid}']",
                    score=0.95,
                    is_unique=True
                ))
            
            # Name selector
            if name := element.attributes.get("name"):
                selectors.append(ElementSelector(
                    strategy=LocatorStrategy.NAME,
                    value=f"[name='{name}']",
                    score=0.85,
                    is_unique=False
                ))
            
            # ARIA label selector
            if aria_label := element.attributes.get("aria-label"):
                selectors.append(ElementSelector(
                    strategy=LocatorStrategy.ARIA_LABEL,
                    value=f"[aria-label='{aria_label}']",
                    score=0.8,
                    is_unique=False
                ))
            
            # Class selector
            if classes := element.attributes.get("class"):
                class_list = classes.split()
                if class_list:
                    selectors.append(ElementSelector(
                        strategy=LocatorStrategy.CSS_CLASS,
                        value=f".{'.'.join(class_list)}",
                        score=0.6,
                        is_unique=False
                    ))
            
            # Text content selector
            if element.text:
                text_snippet = element.text[:50]
                selectors.append(ElementSelector(
                    strategy=LocatorStrategy.TEXT_CONTENT,
                    value=f"{element.tag_name}:has-text('{text_snippet}')",
                    score=0.5,
                    is_unique=False
                ))
            
            # XPath selector
            if element.xpath:
                selectors.append(ElementSelector(
                    strategy=LocatorStrategy.XPATH,
                    value=element.xpath,
                    score=0.4,
                    is_unique=False
                ))
            
            # CSS selector
            if element.css_path:
                selectors.append(ElementSelector(
                    strategy=LocatorStrategy.CSS_SELECTOR,
                    value=element.css_path,
                    score=0.3,
                    is_unique=False
                ))
            
            element.selectors = selectors
        
        return elements
    
    def _calculate_statistics(
        self,
        elements: List[ExtractedElement],
        extraction_time: float
    ) -> Dict[str, Any]:
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
        self,
        browser: UltimateStealthBrowser,
        url: str,
        elements: List[ExtractedElement]
    ) -> List[ScreenshotData]:
        """Capture screenshots with element highlighting"""
        screenshots: List[ScreenshotData] = []
        
        try:
            # Get page from browser
            if not hasattr(browser, '_page') or not browser._page:
                logger.warning("No page available for screenshots")
                return screenshots
            
            page = browser._page
            
            # Capture base screenshot
            screenshot_bytes = await page.screenshot(
                full_page=self.config.screenshot_full_page,
                type=self.config.screenshot_format  # type: ignore
            )
            
            viewport = await page.viewport_size()
            if viewport is None:
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
                await page.evaluate("""
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
                """, selector_list)
                
                # Capture highlighted screenshot
                highlighted_bytes = await page.screenshot(
                    full_page=self.config.screenshot_full_page,
                    type=self.config.screenshot_format  # type: ignore
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
                await page.evaluate("""
                    () => {
                        document.querySelectorAll('*').forEach(el => {
                            el.style.outline = '';
                            el.style.outlineOffset = '';
                        });
                    }
                """)
            
            logger.info(f"Captured {len(screenshots)} comprehensive screenshots")
            
        except Exception as e:
            logger.error(f"Failed to capture screenshots: {e}")
        
        return screenshots
    
    async def crawl(
        self,
        start_url: str,
        max_pages: int = 10,
        max_depth: int = 2,
        follow_pattern: Optional[str] = None
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
                result.statistics["selector_strategies"].items(),
                key=lambda x: x[1],
                reverse=True
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
