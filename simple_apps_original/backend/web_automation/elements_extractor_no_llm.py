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

# Import from data_types for DRY compliance
from data_types import (
    ElementType,
    DOMExtractionConfig as ExtractionConfig,
    DOMExtractionResult as ExtractionResult
)

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

T = TypeVar("T")


def retry_with_backoff(
    max_attempts: int = 3, initial_delay: float = 1.0, backoff_factor: float = 2.0
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
                    logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed: {e}")

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


# ElementType is now imported from data_types.py


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


# ==================== CONSTANTS ====================

# Confidence scoring weights
CONFIDENCE_BASE = 0.5
CONFIDENCE_INCREMENT = 0.1

# Selector scoring values
SELECTOR_SCORE_ID = 1.0
SELECTOR_SCORE_TESTID = 0.95
SELECTOR_SCORE_NAME = 0.85
SELECTOR_SCORE_ARIA = 0.8
SELECTOR_SCORE_CLASS = 0.6
SELECTOR_SCORE_TEXT = 0.5
SELECTOR_SCORE_DEFAULT = 0.4

# Element type mappings
TAG_TO_ELEMENT_TYPE = {
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

ROLE_TO_ELEMENT_TYPE = {
    "button": ElementType.BUTTON,
    "link": ElementType.LINK,
    "navigation": ElementType.NAV,
    "menu": ElementType.MENU,
    "toolbar": ElementType.TOOLBAR,
    "tab": ElementType.TAB,
    "dialog": ElementType.DIALOG,
    "article": ElementType.ARTICLE,
}

# Interaction type mappings
ELEMENT_INTERACTIONS = {
    ElementType.BUTTON: [InteractionType.CLICK, InteractionType.HOVER],
    ElementType.LINK: [InteractionType.CLICK, InteractionType.HOVER, InteractionType.NAVIGATE],
    ElementType.INPUT: [InteractionType.TYPE, InteractionType.CLEAR, InteractionType.FOCUS],
    ElementType.TEXTAREA: [InteractionType.TYPE, InteractionType.CLEAR, InteractionType.FOCUS],
    ElementType.SELECT: [InteractionType.SELECT, InteractionType.CLICK],
    ElementType.CHECKBOX: [InteractionType.CLICK],
    ElementType.RADIO: [InteractionType.CLICK],
    ElementType.FORM: [InteractionType.SUBMIT, InteractionType.RESET],
}


# ==================== DATA MODELS ====================


class ElementSelector(BaseModel):
    """Represents a selector for an element"""

    model_config = ConfigDict(str_strip_whitespace=True)

    strategy: LocatorStrategy
    value: str = Field(..., min_length=1)
    score: float = Field(..., ge=0.0, le=1.0)
    is_unique: bool = Field(default=False)
    parent_context: Optional[str] = Field(default=None)


class BoundingBox(BaseModel):
    """Element bounding box information"""

    model_config = ConfigDict(str_strip_whitespace=True)

    x: float
    y: float
    width: float = Field(..., ge=0)
    height: float = Field(..., ge=0)
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


class ComputedStyle(BaseModel):
    """Computed CSS styles for an element"""

    model_config = ConfigDict(str_strip_whitespace=True)

    display: str = Field(default="block")
    visibility: str = Field(default="visible")
    opacity: str = Field(default="1")
    position: str = Field(default="static")
    z_index: str = Field(default="auto")
    background_color: str = Field(default="transparent")
    color: str = Field(default="black")
    font_size: str = Field(default="16px")
    font_weight: str = Field(default="normal")
    cursor: str = Field(default="auto")
    overflow: str = Field(default="visible")

    def is_visible(self) -> bool:
        """Check if element is visible based on styles"""
        return self.display != "none" and self.visibility != "hidden" and float(self.opacity or 1) > 0


class ScreenshotData(BaseModel):
    """Screenshot data with metadata"""

    model_config = ConfigDict(str_strip_whitespace=True)

    format: str = Field(default="png")
    width: int = Field(..., gt=0)
    height: int = Field(..., gt=0)
    data: str = Field(...)  # Base64 encoded
    timestamp: float = Field(default_factory=time.time)
    url: str = Field(...)
    highlighted_elements: List[str] = Field(default_factory=list)

    def save(self, path: Path) -> None:
        """Save screenshot to file"""
        path.write_bytes(base64.b64decode(self.data))


# ExtractionConfig is now imported from data_types.py as DOMExtractionConfig


# ExtractionResult is now imported from data_types.py as DOMExtractionResult


class CrawlResult(BaseModel):
    """Result of web crawling"""

    model_config = ConfigDict(str_strip_whitespace=True)

    start_url: str = Field(..., min_length=1)
    pages_visited: List[str] = Field(default_factory=list)
    extraction_results: List[ExtractionResult] = Field(default_factory=list)
    total_elements: int = Field(default=0, ge=0)
    crawl_time: float = Field(..., ge=0.0)
    max_depth_reached: int = Field(default=0, ge=0)
    errors: List[str] = Field(default_factory=list)


# ==================== EXTRACTED ELEMENT MODEL ====================


class ExtractedElement(BaseModel):
    """
    Core model for extracted web elements.
    This is the single source of truth for all element data in the system.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    # Core identification
    selector: str = Field(..., min_length=1, description="Primary selector (CSS or XPath)")
    element_type: ElementType = Field(..., description="Type of element")
    tag_name: str = Field(..., min_length=1, description="HTML tag name")

    # Content
    text: Optional[str] = Field(None, description="Visible text content")
    value: Optional[str] = Field(None, description="Input value")
    placeholder: Optional[str] = Field(None, description="Placeholder text")

    # Attributes
    id: Optional[str] = Field(None, description="Element ID")
    name: Optional[str] = Field(None, description="Element name attribute")
    classes: List[str] = Field(default_factory=list, description="CSS classes")
    attributes: Dict[str, str] = Field(default_factory=dict, description="All attributes")

    # Interaction capabilities
    is_clickable: bool = Field(False, description="Can be clicked")
    is_editable: bool = Field(False, description="Can accept input")
    is_visible: bool = Field(True, description="Currently visible")
    is_enabled: bool = Field(True, description="Currently enabled")

    # Advanced selectors
    xpath: Optional[str] = Field(None, description="XPath selector")
    css_path: Optional[str] = Field(None, description="CSS selector")
    selectors: List[ElementSelector] = Field(default_factory=list, description="All possible selectors")

    # Position and style
    bounding_box: Optional[BoundingBox] = Field(None, description="Element position and size")
    computed_style: Optional[ComputedStyle] = Field(None, description="Computed CSS styles")

    # Hierarchy
    parent_selector: Optional[str] = Field(None, description="Parent element selector")
    child_count: int = Field(0, ge=0, description="Number of child elements")
    depth: int = Field(0, ge=0, description="Depth in DOM tree")

    # Classification
    interaction_types: List[InteractionType] = Field(default_factory=list, description="Possible interactions")
    confidence: float = Field(0.5, ge=0.0, le=1.0, description="Extraction confidence")
    importance_score: float = Field(0.5, ge=0.0, le=1.0, description="Element importance")

    # Metadata
    extraction_method: Optional[ExtractionMethod] = Field(None, description="How element was extracted")
    extraction_timestamp: float = Field(default_factory=time.time, description="When extracted")
    is_shadow_element: bool = Field(False, description="Is inside shadow DOM")
    is_iframe_element: bool = Field(False, description="Is inside iframe")

    # Validation
    is_valid: bool = Field(True, description="Element is valid for testing")
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors")

    # AI Analysis (optional, filled by elements_extractor_with_llm)
    ai_description: Optional[str] = Field(None, description="AI-generated description")
    test_suggestions: List[str] = Field(default_factory=list, description="AI test suggestions")
    ai_confidence: Optional[float] = Field(None, description="AI analysis confidence")

    @field_validator("selector")
    @classmethod
    def validate_selector(cls, v: str) -> str:
        """Ensure selector is not empty"""
        if not v or not v.strip():
            raise ValueError("Selector cannot be empty")
        return v.strip()

    @model_validator(mode="after")
    def set_primary_selector(self):
        """Set primary selector from xpath or css_path if not provided"""
        if not self.selector:
            if self.xpath:
                self.selector = self.xpath
            elif self.css_path:
                self.selector = self.css_path
        return self

    def get_best_selector(self) -> Optional[ElementSelector]:
        """Get the best selector for this element"""
        if not self.selectors:
            return None
        return max(self.selectors, key=lambda s: s.score)

    def to_pipeline_contract(self) -> Dict[str, Any]:
        """
        Convert to simplified pipeline contract format.
        This is used by downstream modules that need less detail.
        """
        return {
            "selector": self.selector,
            "element_type": self.element_type.value,
            "tag_name": self.tag_name,
            "text": self.text,
            "value": self.value,
            "placeholder": self.placeholder,
            "id": self.id,
            "name": self.name,
            "classes": self.classes,
            "attributes": self.attributes,
            "is_clickable": self.is_clickable,
            "is_editable": self.is_editable,
            "is_visible": self.is_visible,
            "is_enabled": self.is_enabled,
            "parent_selector": self.parent_selector,
            "child_count": self.child_count,
            "ai_description": self.ai_description,
            "test_suggestions": self.test_suggestions,
            "importance_score": self.importance_score,
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
                stealth_config.level = StealthLevel.ADVANCED if self.config.enable_stealth else StealthLevel.BASIC

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

    def _convert_browser_elements(self, browser_elements: List[BrowserElementData]) -> List[ExtractedElement]:
        """Convert browser elements to our format"""
        converted: List[ExtractedElement] = []

        for be in browser_elements:
            # Map browser element type to our type
            element_type = self._map_element_type(be.tag_name, be.attributes)

            # Create extracted element with full data
            # Use xpath as selector if available, otherwise use css_selector
            selector = be.xpath if be.xpath else be.css_selector if be.css_selector else f"//{be.tag_name}"

            # Extract classes from attributes
            classes = []
            if "class" in be.attributes:
                classes = be.attributes["class"].split()

            # Determine if clickable based on tag and attributes
            is_clickable = (
                be.tag_name in ["button", "a", "input", "select"]
                or be.attributes.get("onclick") is not None
                or be.attributes.get("role") == "button"
                or element_type in [ElementType.BUTTON, ElementType.LINK]
            )

            # Determine if editable
            is_editable = (
                be.tag_name in ["input", "textarea", "select"]
                or be.attributes.get("contenteditable") == "true"
                or element_type in [ElementType.INPUT, ElementType.TEXTAREA, ElementType.SELECT]
            )

            element = ExtractedElement(
                # Required fields
                selector=selector,
                element_type=element_type,
                tag_name=be.tag_name,
                # Content fields
                text=be.text_content,
                value=be.value or be.attributes.get("value"),
                placeholder=be.placeholder or be.attributes.get("placeholder"),
                # Attributes
                id=be.id or be.attributes.get("id"),
                name=be.name or be.attributes.get("name"),
                classes=be.class_names if be.class_names else classes,
                attributes=be.attributes,
                # Interaction capabilities
                is_clickable=is_clickable,
                is_editable=is_editable,
                is_visible=be.is_visible,
                is_enabled=be.is_enabled,
                # Selectors
                xpath=be.xpath,
                css_path=be.css_selector,
                # Position (will be None by default)
                bounding_box=None,
                computed_style=None,
                # Hierarchy (using defaults)
                parent_selector=None,
                child_count=0,
                depth=0,
                # Classification
                confidence=0.8,
                importance_score=0.5,
                # Metadata
                extraction_method=ExtractionMethod.DOM_QUERY,
                is_shadow_element=False,
                is_iframe_element=False,
                # Validation
                is_valid=True,
                # AI fields (will be None by default)
                ai_description=None,
                ai_confidence=None,
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
            element.selectors = self._create_selectors_for_element(element)
        return elements

    def _create_selectors_for_element(self, element: ExtractedElement) -> List[ElementSelector]:
        """Create selector strategies for a single element"""
        selectors: List[ElementSelector] = []
        attrs = element.attributes

        # Define selector generation strategies
        selector_strategies = [
            # (attribute_key, strategy, value_formatter, score, is_unique)
            ("id", LocatorStrategy.ID, lambda v: f"#{v}", SELECTOR_SCORE_ID, True),
            ("data-testid", LocatorStrategy.DATA_TESTID,
             lambda v: f"[data-testid='{v}']", SELECTOR_SCORE_TESTID, True),
            ("name", LocatorStrategy.NAME,
             lambda v: f"[name='{v}']", SELECTOR_SCORE_NAME, False),
            ("aria-label", LocatorStrategy.ARIA_LABEL,
             lambda v: f"[aria-label='{v}']", SELECTOR_SCORE_ARIA, False),
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
                    strategy=LocatorStrategy.TEXT_CONTENT,
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
                    score=SELECTOR_SCORE_DEFAULT,
                    is_unique=False
                )
            )

        return selectors

    def _calculate_statistics(self, elements: List[ExtractedElement], extraction_time: float) -> Dict[str, Any]:
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
        self, browser: UltimateStealthBrowser, url: str, elements: List[ExtractedElement]
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
    
    def _calculate_qa_interaction_score(self, element: ExtractedElement) -> float:
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

    def _is_qa_relevant_element(self, element: ExtractedElement) -> bool:
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
    
    def _might_toggle_visibility(self, element: ExtractedElement) -> bool:
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
                             elements: List[ExtractedElement],
                             category: Optional[str] = None) -> List[ExtractedElement]:
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
    
    def get_qa_summary(self, elements: List[ExtractedElement]) -> Dict[str, Any]:
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
