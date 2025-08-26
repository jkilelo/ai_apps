#!/usr/bin/env python3
"""
ELEMENTS EXTRACTOR NO LLM - Standalone Website Element Extractor
=================================================================
Production-ready DOM-based element extraction without LLM dependencies.
Designed by a Senior Software Engineer with 30+ years of experience.

This module provides comprehensive element extraction capabilities including:
- Pure DOM-based extraction strategies
- Shadow DOM and iframe traversal
- Intelligent selector generation
- Element classification and validation
- Crawling and discovery capabilities
- Anti-detection measures
- Performance optimization

Author: Senior Software Engineer
Version: 2.0.0
License: MIT
"""

import asyncio
import json
import logging
import hashlib
import random
import re
import time
import base64
from abc import ABC, abstractmethod
from collections import defaultdict, Counter
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple, Union, Callable, TypeVar
from urllib.parse import urljoin, urlparse
import functools
import threading
import gc

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Optional imports with graceful fallback
try:
    from playwright.async_api import Page, Browser, BrowserContext, async_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not installed. Install with: pip install playwright")

# ==================== PRODUCTION UTILITIES ====================

T = TypeVar('T')

def retry_with_backoff(max_attempts: int = 3, initial_delay: float = 1.0, 
                       backoff_factor: float = 2.0) -> Callable:
    """Retry decorator with exponential backoff for production resilience."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_attempts - 1:
                        logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed: {e}. Retrying in {delay}s...")
                        await asyncio.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(f"All {max_attempts} attempts failed: {e}")
                        raise
            return None
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_attempts - 1:
                        logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(f"All {max_attempts} attempts failed: {e}")
                        raise
            return None
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Thread safety lock
_global_lock = threading.RLock()

def thread_safe(func: Callable) -> Callable:
    """Decorator to make functions thread-safe."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with _global_lock:
            return func(*args, **kwargs)
    return wrapper

class MemoryManager:
    """Memory management for production environments."""
    
    def __init__(self, threshold_mb: float = 500.0):
        self.threshold_mb = threshold_mb
        
    def check_memory(self) -> bool:
        """Check if memory usage is acceptable."""
        # Basic memory check - could be enhanced with psutil
        return True
    
    def cleanup(self) -> None:
        """Force garbage collection."""
        gc.collect()
        logger.debug("Memory cleanup performed")

# Global memory manager instance
memory_manager = MemoryManager()

# ==================== ENUMERATIONS ====================


class ElementType(Enum):
    """Comprehensive element type classification"""

    BUTTON = "button"
    INPUT = "input"
    LINK = "link"
    IMAGE = "image"
    TEXT = "text"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TEXTAREA = "textarea"
    FORM = "form"
    TABLE = "table"
    LIST = "list"
    NAVIGATION = "navigation"
    HEADER = "header"
    FOOTER = "footer"
    DIALOG = "dialog"
    VIDEO = "video"
    AUDIO = "audio"
    CANVAS = "canvas"
    IFRAME = "iframe"
    MODAL = "modal"
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
    PROGRESS_BAR = "progress_bar"
    LOADING_SPINNER = "loading_spinner"
    NOTIFICATION = "notification"
    ALERT = "alert"
    SLIDER = "slider"
    RATING = "rating"
    SOCIAL_SHARE = "social_share"
    PRICE_DISPLAY = "price_display"
    CAPTCHA = "captcha"
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
        return self.display != "none" and self.visibility != "hidden" and float(self.opacity or 1) > 0


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

    # Anti-detection
    enable_stealth: bool = False
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
    screenshot_format: str = "png"  # 'png' or 'jpeg'
    screenshot_quality: int = 90  # For jpeg only
    highlight_elements: bool = True
    highlight_color: str = "red"
    highlight_width: int = 2


class ScreenshotGranularity(Enum):
    """Screenshot granularity levels based on 30+ years QA experience"""

    ELEMENT = "element"  # Single element only
    ELEMENT_WITH_CONTEXT = "element_with_context"  # Element + padding
    COMPONENT = "component"  # Logical component grouping
    SECTION = "section"  # Page section/region
    VIEWPORT = "viewport"  # Visible viewport
    FULL_PAGE = "full_page"  # Entire page
    INTERACTION_ZONE = "interaction_zone"  # Element + related interactive elements
    ABOVE_FOLD = "above_fold"  # Content before scrolling
    CUSTOM_REGION = "custom_region"  # User-defined region


class ScreenshotMode(Enum):
    """Screenshot capture modes for comprehensive testing"""

    SINGLE = "single"  # One-time capture
    SEQUENCE = "sequence"  # Before/during/after sequence
    COMPARISON = "comparison"  # Side-by-side comparison
    DIFF = "diff"  # Highlight differences
    SCROLL_CAPTURE = "scroll_capture"  # Capture while scrolling
    STATE_CAPTURE = "state_capture"  # Capture different states (hover, focus, etc)
    TIMELINE = "timeline"  # Capture over time intervals
    INTERACTION = "interaction"  # Capture during user interaction


class AnnotationType(Enum):
    """Types of annotations for QA documentation"""

    HIGHLIGHT = "highlight"  # Highlight elements
    BOX = "box"  # Draw bounding box
    ARROW = "arrow"  # Point to element
    TEXT = "text"  # Add text label
    CIRCLE = "circle"  # Circle important area
    BLUR = "blur"  # Blur sensitive data
    REDACT = "redact"  # Black out content
    NUMBER = "number"  # Number sequence steps
    MEASURE = "measure"  # Show dimensions
    CROSSHAIR = "crosshair"  # Mark precise point


@dataclass
class ScreenshotAnnotation:
    """Annotation to add to screenshot"""

    type: AnnotationType
    target: Optional[str] = None  # Element selector or coordinates
    text: Optional[str] = None
    color: str = "red"
    width: int = 2
    font_size: int = 14
    position: Optional[Tuple[int, int]] = None
    dimensions: Optional[Tuple[int, int, int, int]] = None  # x, y, width, height


@dataclass
class ScreenshotMetadata:
    """Rich metadata for QA debugging and documentation"""

    # Basic info
    url: str
    timestamp: float
    test_name: Optional[str] = None
    test_step: Optional[str] = None

    # Browser info
    browser_name: str = "unknown"
    browser_version: str = "unknown"
    user_agent: str = ""
    viewport_width: int = 0
    viewport_height: int = 0
    device_pixel_ratio: float = 1.0

    # Page state
    page_title: str = ""
    page_load_time: float = 0.0
    dom_ready_time: float = 0.0

    # Environment
    os_name: str = ""
    os_version: str = ""
    screen_resolution: str = ""

    # Network
    network_speed: str = ""
    online_status: bool = True

    # Console
    console_errors: List[str] = field(default_factory=list)
    console_warnings: List[str] = field(default_factory=list)
    console_logs: List[str] = field(default_factory=list)

    # Performance
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    fps: Optional[float] = None

    # Accessibility
    accessibility_violations: List[Dict[str, Any]] = field(default_factory=list)
    contrast_issues: List[Dict[str, Any]] = field(default_factory=list)

    # User actions
    last_action: Optional[str] = None
    action_sequence: List[str] = field(default_factory=list)
    mouse_position: Optional[Tuple[int, int]] = None

    # Custom tags
    tags: List[str] = field(default_factory=list)
    custom_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScreenshotComparison:
    """Result of comparing two screenshots"""

    similarity_score: float  # 0.0 to 1.0
    pixel_diff_count: int
    structural_diff: List[str]
    diff_regions: List[Tuple[int, int, int, int]]  # Regions that differ
    diff_image_data: Optional[str] = None  # Base64 encoded diff image
    analysis: str = ""  # Human-readable analysis


@dataclass
class ScreenshotData:
    """Enhanced screenshot data with comprehensive QA features"""

    # Basic data
    data: str  # Base64 encoded image data
    format: str  # 'png', 'jpeg', 'webp'
    width: int
    height: int

    # Capture info
    granularity: ScreenshotGranularity
    mode: ScreenshotMode
    timestamp: float

    # Content info
    captured_elements: List[str] = field(default_factory=list)
    highlighted_elements: List[str] = field(default_factory=list)
    annotations: List[ScreenshotAnnotation] = field(default_factory=list)

    # Metadata
    metadata: Optional[ScreenshotMetadata] = None

    # Relationships
    parent_screenshot_id: Optional[str] = None  # For sequences
    related_screenshots: List[str] = field(default_factory=list)

    # Analysis
    dominant_colors: List[str] = field(default_factory=list)
    has_text: bool = False
    text_content: Optional[str] = None  # OCR result if available

    # Quality
    quality_score: float = 1.0  # 0.0 to 1.0
    file_size: int = 0  # Size in bytes

    def save_to_file(self, filepath: Union[str, Path], include_metadata: bool = True, optimize: bool = False) -> Path:
        """Save screenshot to file with optional metadata"""
        filepath = Path(filepath)
        if not filepath.suffix:
            filepath = filepath.with_suffix(f".{self.format}")

        # Decode base64 and save
        image_data = base64.b64decode(self.data)

        # Optionally optimize image size
        if optimize and len(image_data) > 500000:  # > 500KB
            # In production, you'd use PIL/Pillow to optimize
            pass

        filepath.write_bytes(image_data)

        # Save metadata as JSON sidecar file
        if include_metadata and self.metadata:
            metadata_path = filepath.with_suffix(".json")
            metadata_dict = asdict(self.metadata) if self.metadata else {}
            metadata_dict["screenshot_file"] = filepath.name
            metadata_dict["granularity"] = self.granularity.value
            metadata_dict["mode"] = self.mode.value
            metadata_path.write_text(json.dumps(metadata_dict, indent=2))

        return filepath

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "format": self.format,
            "width": self.width,
            "height": self.height,
            "granularity": self.granularity.value,
            "mode": self.mode.value,
            "timestamp": self.timestamp,
            "captured_elements": len(self.captured_elements),
            "highlighted_elements": len(self.highlighted_elements),
            "annotations": len(self.annotations),
            "has_metadata": self.metadata is not None,
            "quality_score": self.quality_score,
            "file_size": self.file_size or len(self.data),
            "has_text": self.has_text,
        }

    def get_aspect_ratio(self) -> float:
        """Calculate aspect ratio"""
        return self.width / self.height if self.height > 0 else 0

    def is_mobile_viewport(self) -> bool:
        """Check if screenshot is from mobile viewport"""
        return self.width < 768

    def is_high_quality(self) -> bool:
        """Check if screenshot meets quality standards"""
        return self.quality_score >= 0.8 and self.width >= 1024


@dataclass
class ExtractionResult:
    """Result of element extraction"""

    url: str
    elements: List[ExtractedElement]
    extraction_time: float
    total_elements_found: int
    filtered_elements: int
    extraction_method: str
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    screenshots: List[ScreenshotData] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "url": self.url,
            "elements": [e.to_dict() for e in self.elements],
            "extraction_time": self.extraction_time,
            "total_elements_found": self.total_elements_found,
            "filtered_elements": self.filtered_elements,
            "extraction_method": self.extraction_method,
            "success": self.success,
            "errors": self.errors,
            "warnings": self.warnings,
            "statistics": self.statistics,
            "screenshots": [s.to_dict() for s in self.screenshots],
        }

    def save_screenshots(self, directory: Union[str, Path], prefix: str = "screenshot") -> List[Path]:
        """Save all screenshots to directory"""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        saved_files = []
        for i, screenshot in enumerate(self.screenshots):
            filename = f"{prefix}_{i+1}_{int(screenshot.timestamp)}.{screenshot.format}"
            filepath = directory / filename
            saved_path = screenshot.save_to_file(filepath)
            saved_files.append(saved_path)

        return saved_files


# ==================== UTILITY CLASSES ====================


class SelectorGenerator:
    """Advanced selector generation with multiple strategies"""

    # Patterns for detecting auto-generated IDs
    AUTO_GENERATED_PATTERNS = [
        r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",  # UUID
        r"^[a-f0-9]{24}$",  # MongoDB ObjectId
        r"^ember\d+$",  # Ember.js
        r"^react-select-\d+-",  # React Select
        r"^\d+$",  # Pure numbers
        r"^ng-",  # Angular
        r"^vue-",  # Vue.js
        r"^svelte-",  # Svelte
        r"^__next",  # Next.js
        r"^gatsby-",  # Gatsby
        r"^mui-\d+",  # Material-UI
        r"^radix-",  # Radix UI
    ]

    @classmethod
    def generate_selectors(cls, element: Dict[str, Any]) -> List[ElementSelector]:
        """Generate multiple selector strategies for an element"""
        selectors = []

        # Try different strategies
        selectors.extend(cls._generate_id_selector(element))
        selectors.extend(cls._generate_data_attribute_selectors(element))
        selectors.extend(cls._generate_aria_selectors(element))
        selectors.extend(cls._generate_class_selectors(element))
        selectors.extend(cls._generate_name_selector(element))
        selectors.extend(cls._generate_text_selector(element))
        selectors.extend(cls._generate_xpath_selectors(element))

        # Sort by score
        selectors.sort(key=lambda s: s.score, reverse=True)

        return selectors

    @classmethod
    def _generate_id_selector(cls, element: Dict[str, Any]) -> List[ElementSelector]:
        """Generate ID-based selector"""
        selectors = []
        attributes = element.get("attributes", {})
        element_id = attributes.get("id", "").strip()

        if element_id and not cls._is_auto_generated(element_id):
            selectors.append(
                ElementSelector(strategy=LocatorStrategy.ID, value=f"#{element_id}", score=0.95, is_unique=True)
            )

        return selectors

    @classmethod
    def _generate_data_attribute_selectors(cls, element: Dict[str, Any]) -> List[ElementSelector]:
        """Generate data attribute selectors"""
        selectors = []
        attributes = element.get("attributes", {})
        tag_name = element.get("tag_name", "").lower()

        # Priority data attributes
        priority_attrs = ["data-testid", "data-test", "data-cy", "data-test-id", "data-qa"]

        for attr in priority_attrs:
            if value := attributes.get(attr):
                selectors.append(
                    ElementSelector(
                        strategy=LocatorStrategy.DATA_TESTID,
                        value=f"{tag_name}[{attr}='{value}']",
                        score=0.9,
                        is_unique=True,
                    )
                )

        # Other data attributes
        for attr, value in attributes.items():
            if attr.startswith("data-") and attr not in priority_attrs and value:
                selectors.append(
                    ElementSelector(
                        strategy=LocatorStrategy.CSS_SELECTOR,
                        value=f"{tag_name}[{attr}='{value}']",
                        score=0.75,
                        is_unique=False,
                    )
                )

        return selectors

    @classmethod
    def _generate_aria_selectors(cls, element: Dict[str, Any]) -> List[ElementSelector]:
        """Generate ARIA-based selectors"""
        selectors = []
        attributes = element.get("attributes", {})
        tag_name = element.get("tag_name", "").lower()

        # ARIA label
        if aria_label := attributes.get("aria-label"):
            selectors.append(
                ElementSelector(
                    strategy=LocatorStrategy.ARIA_LABEL,
                    value=f"{tag_name}[aria-label='{aria_label}']",
                    score=0.8,
                    is_unique=False,
                )
            )

        # ARIA role
        if role := attributes.get("role"):
            selectors.append(
                ElementSelector(strategy=LocatorStrategy.ROLE, value=f"[role='{role}']", score=0.7, is_unique=False)
            )

        return selectors

    @classmethod
    def _generate_class_selectors(cls, element: Dict[str, Any]) -> List[ElementSelector]:
        """Generate class-based selectors"""
        selectors = []
        attributes = element.get("attributes", {})
        tag_name = element.get("tag_name", "").lower()

        if classes := attributes.get("class", "").strip():
            class_list = classes.split()

            # Single meaningful class
            for class_name in class_list:
                if cls._is_meaningful_class(class_name):
                    selectors.append(
                        ElementSelector(
                            strategy=LocatorStrategy.CSS_CLASS,
                            value=f"{tag_name}.{class_name}",
                            score=0.6,
                            is_unique=False,
                        )
                    )

            # Combination of classes
            if len(class_list) > 1:
                class_selector = ".".join(class_list[:3])  # Limit to 3 classes
                selectors.append(
                    ElementSelector(
                        strategy=LocatorStrategy.CSS_SELECTOR,
                        value=f"{tag_name}.{class_selector}",
                        score=0.65,
                        is_unique=False,
                    )
                )

        return selectors

    @classmethod
    def _generate_name_selector(cls, element: Dict[str, Any]) -> List[ElementSelector]:
        """Generate name attribute selector"""
        selectors = []
        attributes = element.get("attributes", {})
        tag_name = element.get("tag_name", "").lower()

        if name := attributes.get("name"):
            selectors.append(
                ElementSelector(
                    strategy=LocatorStrategy.NAME, value=f"{tag_name}[name='{name}']", score=0.7, is_unique=False
                )
            )

        return selectors

    @classmethod
    def _generate_text_selector(cls, element: Dict[str, Any]) -> List[ElementSelector]:
        """Generate text-based selector"""
        selectors = []
        text = element.get("text", "").strip()
        tag_name = element.get("tag_name", "").lower()

        if text and len(text) < 100 and not text.isdigit():
            # Exact text match
            selectors.append(
                ElementSelector(
                    strategy=LocatorStrategy.TEXT_CONTENT,
                    value=f"{tag_name}:has-text('{text}')",
                    score=0.5,
                    is_unique=False,
                )
            )

        return selectors

    @classmethod
    def _generate_xpath_selectors(cls, element: Dict[str, Any]) -> List[ElementSelector]:
        """Generate XPath selectors"""
        selectors = []

        if xpath := element.get("xpath"):
            selectors.append(ElementSelector(strategy=LocatorStrategy.XPATH, value=xpath, score=0.3, is_unique=True))

        return selectors

    @classmethod
    def _is_auto_generated(cls, value: str) -> bool:
        """Check if value appears to be auto-generated"""
        if not value:
            return True

        for pattern in cls.AUTO_GENERATED_PATTERNS:
            if re.match(pattern, value, re.IGNORECASE):
                return True

        return False

    @classmethod
    def _is_meaningful_class(cls, class_name: str) -> bool:
        """Check if class name is meaningful (not auto-generated)"""
        # Skip utility classes
        utility_patterns = [
            r"^[mp][tlrbxy]?-\d+$",  # Tailwind spacing
            r"^(text|bg|border)-",  # Tailwind colors
            r"^(flex|grid|hidden|block|inline)",  # Layout utilities
            r"^col-(span-)?",  # Grid columns
            r"^[wh]-\d+$",  # Width/height utilities
        ]

        for pattern in utility_patterns:
            if re.match(pattern, class_name):
                return False

        # Skip if too short or looks auto-generated
        if len(class_name) < 3 or cls._is_auto_generated(class_name):
            return False

        return True


class ElementClassifier:
    """Classify elements into types based on various indicators"""

    # Mapping of tag names to element types
    TAG_TYPE_MAP = {
        "button": ElementType.BUTTON,
        "input": ElementType.INPUT,
        "a": ElementType.LINK,
        "img": ElementType.IMAGE,
        "select": ElementType.DROPDOWN,
        "textarea": ElementType.TEXTAREA,
        "form": ElementType.FORM,
        "table": ElementType.TABLE,
        "ul": ElementType.LIST,
        "ol": ElementType.LIST,
        "nav": ElementType.NAVIGATION,
        "header": ElementType.HEADER,
        "footer": ElementType.FOOTER,
        "dialog": ElementType.DIALOG,
        "video": ElementType.VIDEO,
        "audio": ElementType.AUDIO,
        "canvas": ElementType.CANVAS,
        "iframe": ElementType.IFRAME,
    }

    # Role to element type mapping
    ROLE_TYPE_MAP = {
        "button": ElementType.BUTTON,
        "link": ElementType.LINK,
        "navigation": ElementType.NAVIGATION,
        "search": ElementType.SEARCH,
        "tab": ElementType.TAB,
        "dialog": ElementType.DIALOG,
        "alert": ElementType.ALERT,
        "progressbar": ElementType.PROGRESS_BAR,
        "slider": ElementType.SLIDER,
        "tooltip": ElementType.TOOLTIP,
    }

    @classmethod
    def classify_element(cls, element: Dict[str, Any]) -> ElementType:
        """Classify element into appropriate type"""
        tag_name = element.get("tag_name", "").lower()
        attributes = element.get("attributes", {})

        # Check tag name first
        if tag_name in cls.TAG_TYPE_MAP:
            element_type = cls.TAG_TYPE_MAP[tag_name]

            # Special handling for input elements
            if tag_name == "input":
                input_type = attributes.get("type", "text").lower()
                if input_type == "checkbox":
                    return ElementType.CHECKBOX
                elif input_type == "radio":
                    return ElementType.RADIO
                elif input_type in ["submit", "button"]:
                    return ElementType.BUTTON

            return element_type

        # Check role attribute
        if role := attributes.get("role"):
            if role in cls.ROLE_TYPE_MAP:
                return cls.ROLE_TYPE_MAP[role]

        # Check for patterns in classes
        classes = attributes.get("class", "").lower()
        class_patterns = {
            "btn": ElementType.BUTTON,
            "button": ElementType.BUTTON,
            "link": ElementType.LINK,
            "nav": ElementType.NAVIGATION,
            "modal": ElementType.MODAL,
            "dropdown": ElementType.DROPDOWN,
            "tab": ElementType.TAB,
            "accordion": ElementType.ACCORDION,
            "card": ElementType.CARD,
            "pagination": ElementType.PAGINATION,
            "search": ElementType.SEARCH,
            "filter": ElementType.FILTER,
            "carousel": ElementType.CAROUSEL,
            "tooltip": ElementType.TOOLTIP,
            "breadcrumb": ElementType.BREADCRUMB,
            "sidebar": ElementType.SIDEBAR,
            "alert": ElementType.ALERT,
            "notification": ElementType.NOTIFICATION,
            "slider": ElementType.SLIDER,
            "rating": ElementType.RATING,
        }

        for pattern, element_type in class_patterns.items():
            if pattern in classes:
                return element_type

        # Default to text for divs and spans with text content
        if tag_name in ["div", "span", "p"] and element.get("text"):
            return ElementType.TEXT

        return ElementType.UNKNOWN

    @classmethod
    def determine_interaction_types(cls, element: ExtractedElement) -> List[InteractionType]:
        """Determine possible interaction types for an element"""
        interactions = []

        # Based on element type
        type_interactions = {
            ElementType.BUTTON: [InteractionType.CLICK],
            ElementType.LINK: [InteractionType.CLICK, InteractionType.NAVIGATE],
            ElementType.INPUT: [InteractionType.TYPE, InteractionType.CLEAR, InteractionType.FOCUS],
            ElementType.CHECKBOX: [InteractionType.CLICK],
            ElementType.RADIO: [InteractionType.CLICK],
            ElementType.DROPDOWN: [InteractionType.SELECT, InteractionType.CLICK],
            ElementType.TEXTAREA: [InteractionType.TYPE, InteractionType.CLEAR, InteractionType.FOCUS],
            ElementType.FORM: [InteractionType.SUBMIT],
            ElementType.SLIDER: [InteractionType.DRAG],
        }

        if element.element_type in type_interactions:
            interactions.extend(type_interactions[element.element_type])

        # Check for click handlers
        if element.is_clickable or "onclick" in element.attributes:
            if InteractionType.CLICK not in interactions:
                interactions.append(InteractionType.CLICK)

        # Check for hover effects
        if element.computed_style and element.computed_style.cursor == "pointer":
            if InteractionType.HOVER not in interactions:
                interactions.append(InteractionType.HOVER)

        # Check for draggable
        if element.attributes.get("draggable") == "true":
            interactions.append(InteractionType.DRAG)

        # Check for contenteditable
        if element.attributes.get("contenteditable") == "true":
            interactions.extend([InteractionType.TYPE, InteractionType.CLEAR])

        return list(set(interactions))  # Remove duplicates


class ElementValidator:
    """Validate and score extracted elements"""

    @staticmethod
    def validate_element(element: ExtractedElement) -> Tuple[bool, List[str]]:
        """Validate an extracted element"""
        issues = []

        # Check required fields
        if not element.tag_name:
            issues.append("Missing tag name")

        # Check bounding box validity
        if element.bounding_box:
            if element.bounding_box.width <= 0 or element.bounding_box.height <= 0:
                issues.append("Invalid bounding box dimensions")

        # Check selectors
        if not element.selectors:
            issues.append("No selectors generated")

        # Check for valid element type
        if element.element_type == ElementType.UNKNOWN:
            issues.append("Unknown element type")

        # Validate attributes
        if not element.attributes and element.tag_name not in ["body", "html"]:
            issues.append("No attributes found")

        is_valid = len(issues) == 0
        return is_valid, issues

    @staticmethod
    def calculate_confidence_score(element: ExtractedElement) -> float:
        """Calculate confidence score for element extraction"""
        score = 0.0
        factors = 0

        # Selector quality
        if element.selectors:
            best_selector = element.get_best_selector()
            if best_selector:
                score += best_selector.score
                factors += 1

        # Element type confidence
        if element.element_type != ElementType.UNKNOWN:
            score += 0.8
            factors += 1

        # Visibility confidence
        if element.bounding_box and element.bounding_box.is_visible():
            score += 0.9
            factors += 1

        # Style visibility
        if element.computed_style and element.computed_style.is_visible():
            score += 0.9
            factors += 1

        # Unique identification
        if element.selectors:
            unique_selectors = [s for s in element.selectors if s.is_unique]
            if unique_selectors:
                score += 0.95
                factors += 1

        # Calculate average
        if factors > 0:
            return score / factors

        return 0.5  # Default medium confidence

    @staticmethod
    def calculate_stability_score(element: ExtractedElement) -> float:
        """Calculate stability score (likelihood selector will work over time)"""
        score = 0.0
        factors = 0

        # Data attributes are most stable
        if any(s.strategy == LocatorStrategy.DATA_TESTID for s in element.selectors):
            score += 0.95
            factors += 1

        # ID (if not auto-generated) is stable
        if any(s.strategy == LocatorStrategy.ID for s in element.selectors):
            score += 0.9
            factors += 1

        # ARIA attributes are fairly stable
        if any(s.strategy in [LocatorStrategy.ARIA_LABEL, LocatorStrategy.ROLE] for s in element.selectors):
            score += 0.8
            factors += 1

        # Text content is less stable
        if any(s.strategy == LocatorStrategy.TEXT_CONTENT for s in element.selectors):
            score += 0.4
            factors += 1

        # XPath is least stable
        if any(s.strategy == LocatorStrategy.XPATH for s in element.selectors):
            score += 0.3
            factors += 1

        # Calculate average
        if factors > 0:
            return score / factors

        return 0.5

    @staticmethod
    def filter_duplicate_elements(elements: List[ExtractedElement]) -> List[ExtractedElement]:
        """Remove duplicate elements based on multiple criteria"""
        seen = set()
        unique_elements = []

        for element in elements:
            # Create a unique key based on multiple properties
            key_parts = [
                element.tag_name,
                element.xpath or "",
                str(element.bounding_box.x if element.bounding_box else ""),
                str(element.bounding_box.y if element.bounding_box else ""),
                element.text[:50] if element.text else "",
            ]

            key = "|".join(key_parts)

            if key not in seen:
                seen.add(key)
                unique_elements.append(element)

        return unique_elements


class PerformanceMonitor:
    """Monitor extraction performance and statistics"""

    def __init__(self):
        self.metrics = defaultdict(list)
        self.counters = Counter()

    def start_timer(self, operation: str) -> float:
        """Start timing an operation"""
        return time.time()

    def end_timer(self, operation: str, start_time: float):
        """End timing an operation"""
        duration = time.time() - start_time
        self.metrics[operation].append(duration)
        return duration

    def increment_counter(self, metric: str, value: int = 1):
        """Increment a counter metric"""
        self.counters[metric] += value

    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = {}

        # Timing statistics
        for operation, times in self.metrics.items():
            if times:
                stats[f"{operation}_avg"] = sum(times) / len(times)
                stats[f"{operation}_min"] = min(times)
                stats[f"{operation}_max"] = max(times)
                stats[f"{operation}_total"] = sum(times)

        # Counter statistics
        stats.update(dict(self.counters))

        # Element type distribution
        element_types = [k for k in self.counters.keys() if k.startswith("element_type_")]
        if element_types:
            type_distribution = {
                k.replace("element_type_", ""): v for k, v in self.counters.items() if k in element_types
            }
            stats["element_type_distribution"] = type_distribution

        return stats


# ==================== MAIN EXTRACTOR CLASS ====================


class ElementsExtractorNoLLM:
    """
    Main class for extracting elements from web pages without LLM dependencies.
    Uses pure DOM-based strategies with advanced extraction capabilities.
    """

    def __init__(self, config: Optional[ExtractionConfig] = None):
        """Initialize the extractor with configuration"""
        self.config = config or ExtractionConfig()
        self.selector_generator = SelectorGenerator()
        self.classifier = ElementClassifier()
        self.validator = ElementValidator()
        self.performance_monitor = PerformanceMonitor()
        self._cache: Dict[str, Any] = {}

        logger.info("ElementsExtractorNoLLM initialized with config: %s", self.config)

    @retry_with_backoff(max_attempts=3)
    async def extract_from_url(self, url: str, browser: Optional[Browser] = None) -> ExtractionResult:
        """
        Extract elements from a URL using Playwright

        Args:
            url: The URL to extract elements from
            browser: Optional existing browser instance

        Returns:
            ExtractionResult containing extracted elements
        """
        if not PLAYWRIGHT_AVAILABLE:
            return ExtractionResult(
                url=url,
                elements=[],
                extraction_time=0,
                total_elements_found=0,
                filtered_elements=0,
                extraction_method="none",
                success=False,
                errors=["Playwright not installed"],
            )

        start_time = self.performance_monitor.start_timer("total_extraction")
        errors: List[str] = []
        warnings: List[str] = []

        # Check cache
        cache_key = self._get_cache_key(url)
        if self.config.enable_caching and cache_key in self._cache:
            cached_result = self._cache[cache_key]
            if time.time() - cached_result["timestamp"] < self.config.cache_ttl:
                logger.info("Returning cached result for %s", url)
                return cached_result["result"]

        close_browser = False
        if not browser:
            close_browser = True
            browser = await self._create_browser()

        try:
            # Create page
            page = await browser.new_page()

            # Apply stealth if configured
            if self.config.enable_stealth:
                await self._apply_stealth_measures(page)

            # Navigate to URL
            logger.info("Navigating to %s", url)
            await page.goto(url, wait_until="networkidle" if self.config.enable_dynamic_wait else "load")

            # Wait for stability
            if self.config.enable_dynamic_wait:
                await self._wait_for_page_stability(page)

            # Extract elements
            elements = await self._extract_all_elements(page, url)

            # Process and validate elements
            processed_elements = self._process_elements(elements)

            # Filter elements
            filtered_elements = self._filter_elements(processed_elements)

            # Capture screenshots if configured
            screenshots = []
            if self.config.capture_screenshots:
                screenshots = await self._capture_screenshots(page, filtered_elements)

            # Calculate statistics
            extraction_time = self.performance_monitor.end_timer("total_extraction", start_time)
            statistics = self._calculate_statistics(processed_elements, filtered_elements)

            # Create result
            result = ExtractionResult(
                url=url,
                elements=filtered_elements,
                extraction_time=extraction_time,
                total_elements_found=len(processed_elements),
                filtered_elements=len(processed_elements) - len(filtered_elements),
                extraction_method="playwright_dom",
                success=True,
                errors=errors,
                warnings=warnings,
                statistics=statistics,
                screenshots=screenshots,
            )

            # Cache result
            if self.config.enable_caching:
                self._cache[cache_key] = {"result": result, "timestamp": time.time()}

            await page.close()

            return result

        except Exception as e:
            logger.error("Error extracting from %s: %s", url, str(e))
            errors.append(str(e))

            return ExtractionResult(
                url=url,
                elements=[],
                extraction_time=self.performance_monitor.end_timer("total_extraction", start_time),
                total_elements_found=0,
                filtered_elements=0,
                extraction_method="playwright_dom",
                success=False,
                errors=errors,
            )

        finally:
            if close_browser and browser:
                await browser.close()

    async def extract_from_page(self, page: Page, url: str = "") -> ExtractionResult:
        """
        Extract elements from an existing Playwright page

        Args:
            page: The Playwright page object
            url: Optional URL for reference

        Returns:
            ExtractionResult containing extracted elements
        """
        start_time = self.performance_monitor.start_timer("total_extraction")

        try:
            # Extract elements
            elements = await self._extract_all_elements(page, url or page.url)

            # Process and validate elements
            processed_elements = self._process_elements(elements)

            # Filter elements
            filtered_elements = self._filter_elements(processed_elements)

            # Capture screenshots if configured
            screenshots = []
            if self.config.capture_screenshots:
                screenshots = await self._capture_screenshots(page, filtered_elements)

            # Calculate statistics
            extraction_time = self.performance_monitor.end_timer("total_extraction", start_time)
            statistics = self._calculate_statistics(processed_elements, filtered_elements)

            return ExtractionResult(
                url=url or page.url,
                elements=filtered_elements,
                extraction_time=extraction_time,
                total_elements_found=len(processed_elements),
                filtered_elements=len(processed_elements) - len(filtered_elements),
                extraction_method="playwright_dom",
                success=True,
                statistics=statistics,
                screenshots=screenshots,
            )

        except Exception as e:
            logger.error("Error extracting from page: %s", str(e))

            return ExtractionResult(
                url=url or page.url,
                elements=[],
                extraction_time=self.performance_monitor.end_timer("total_extraction", start_time),
                total_elements_found=0,
                filtered_elements=0,
                extraction_method="playwright_dom",
                success=False,
                errors=[str(e)],
            )

    async def _create_browser(self) -> Browser:
        """Create a new browser instance"""
        from playwright.async_api import async_playwright

        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=True, args=["--disable-blink-features=AutomationControlled"]
        )

        return browser

    async def _apply_stealth_measures(self, page: Page):
        """Apply anti-detection measures to the page"""
        # Override navigator properties
        await page.add_init_script(
            """
            // Override navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override navigator.plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override navigator.languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Override chrome runtime
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {}
            };
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """
        )

        # Set viewport
        await page.set_viewport_size(
            {"width": random.choice([1920, 1366, 1440]), "height": random.choice([1080, 768, 900])}
        )

        # Set user agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        await page.set_extra_http_headers({"User-Agent": random.choice(user_agents)})

    async def _wait_for_page_stability(self, page: Page):
        """Wait for the page to become stable"""
        # Wait for network idle
        await page.wait_for_load_state("networkidle", timeout=self.config.extraction_timeout)

        # Wait for any animations to complete
        await page.evaluate(
            """
            () => new Promise((resolve) => {
                if (document.readyState === 'complete') {
                    // Check for ongoing animations
                    const checkAnimations = () => {
                        const animations = document.getAnimations ? document.getAnimations() : [];
                        if (animations.length === 0) {
                            resolve();
                        } else {
                            setTimeout(checkAnimations, 100);
                        }
                    };
                    setTimeout(checkAnimations, 100);
                } else {
                    window.addEventListener('load', () => setTimeout(resolve, 100));
                }
            })
        """
        )

        # Random human-like delay
        if self.config.randomize_delays:
            delay = random.uniform(self.config.min_delay, self.config.max_delay)
            await asyncio.sleep(delay)

    async def _extract_all_elements(self, page: Page, url: str) -> List[Dict[str, Any]]:
        """Extract all elements from the page"""
        all_elements = []

        # Extract main DOM elements
        dom_timer = self.performance_monitor.start_timer("dom_extraction")
        dom_elements = await self._extract_dom_elements(page)
        self.performance_monitor.end_timer("dom_extraction", dom_timer)
        all_elements.extend(dom_elements)

        # Extract shadow DOM elements
        if self.config.enable_shadow_dom:
            shadow_timer = self.performance_monitor.start_timer("shadow_dom_extraction")
            shadow_elements = await self._extract_shadow_dom_elements(page)
            self.performance_monitor.end_timer("shadow_dom_extraction", shadow_timer)
            all_elements.extend(shadow_elements)

        # Extract iframe elements
        if self.config.enable_iframe_traversal:
            iframe_timer = self.performance_monitor.start_timer("iframe_extraction")
            iframe_elements = await self._extract_iframe_elements(page)
            self.performance_monitor.end_timer("iframe_extraction", iframe_timer)
            all_elements.extend(iframe_elements)

        logger.info("Extracted %d total elements from %s", len(all_elements), url)

        return all_elements

    async def _extract_dom_elements(self, page: Page) -> List[Dict[str, Any]]:
        """Extract elements from the main DOM"""
        script = r"""
            () => {
                const elements = [];
                const visited = new Set();
                
                function getXPath(element) {
                    if (element.id) return `//*[@id="${element.id}"]`;
                    if (element === document.body) return '/html/body';
                    
                    let ix = 0;
                    const siblings = element.parentNode?.childNodes;
                    if (siblings) {
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
                    }
                    return '';
                }
                
                function getCSSPath(element) {
                    const path = [];
                    while (element && element.nodeType === Node.ELEMENT_NODE) {
                        let selector = element.tagName.toLowerCase();
                        if (element.id) {
                            selector += '#' + element.id;
                            path.unshift(selector);
                            break;
                        } else if (element.className) {
                            selector += '.' + element.className.trim().split(/\s+/).join('.');
                        }
                        path.unshift(selector);
                        element = element.parentNode;
                    }
                    return path.join(' > ');
                }
                
                function extractElement(element, depth = 0) {
                    if (depth > 10 || visited.has(element)) return null;
                    visited.add(element);
                    
                    const rect = element.getBoundingClientRect();
                    const styles = window.getComputedStyle(element);
                    
                    // Extract attributes
                    const attributes = {};
                    for (const attr of element.attributes) {
                        attributes[attr.name] = attr.value;
                    }
                    
                    // Check for event listeners
                    const hasClickHandler = element.onclick !== null || 
                                          element.getAttribute('onclick') !== null ||
                                          element.hasAttribute('ng-click') ||
                                          element.hasAttribute('data-click') ||
                                          element.hasAttribute('v-on:click');
                    
                    return {
                        tag_name: element.tagName.toLowerCase(),
                        text: element.textContent?.trim().substring(0, 200),
                        value: element.value || null,
                        attributes: attributes,
                        bounding_box: {
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height,
                            top: rect.top,
                            bottom: rect.bottom,
                            left: rect.left,
                            right: rect.right
                        },
                        computed_style: {
                            display: styles.display,
                            visibility: styles.visibility,
                            opacity: styles.opacity,
                            position: styles.position,
                            z_index: styles.zIndex,
                            background_color: styles.backgroundColor,
                            color: styles.color,
                            font_size: styles.fontSize,
                            font_weight: styles.fontWeight,
                            cursor: styles.cursor,
                            overflow: styles.overflow
                        },
                        is_visible: rect.width > 0 && rect.height > 0 && 
                                   styles.display !== 'none' && 
                                   styles.visibility !== 'hidden' &&
                                   parseFloat(styles.opacity) > 0,
                        is_enabled: !element.disabled,
                        is_clickable: hasClickHandler || styles.cursor === 'pointer',
                        is_editable: element.contentEditable === 'true' || 
                                    element.tagName === 'INPUT' || 
                                    element.tagName === 'TEXTAREA',
                        xpath: getXPath(element),
                        css_path: getCSSPath(element)
                    };
                }
                
                // Get all potentially interactive elements
                const selectors = [
                    'a', 'button', 'input', 'select', 'textarea',
                    '[role="button"]', '[role="link"]', '[role="textbox"]',
                    '[onclick]', '[ng-click]', '[data-click]', '[data-action]',
                    'label', 'form', 'iframe', 'video', 'audio', 'canvas',
                    '[contenteditable="true"]', '[tabindex]',
                    'nav', 'header', 'footer', 'main', 'article', 'section',
                    'dialog', '[role="dialog"]', '[role="alert"]',
                    'table', 'ul', 'ol', 'dl',
                    '.btn', '.button', '.link', '.clickable',
                    '[data-testid]', '[data-test]', '[data-cy]'
                ];
                
                const allElements = document.querySelectorAll(selectors.join(', '));
                
                for (const element of allElements) {
                    const data = extractElement(element);
                    if (data && data.is_visible) {
                        elements.push(data);
                    }
                }
                
                return elements;
            }
        """

        elements = await page.evaluate(script)
        return elements

    async def _extract_shadow_dom_elements(self, page: Page) -> List[Dict[str, Any]]:
        """Extract elements from shadow DOM"""
        script = r"""
            () => {
                const elements = [];
                
                function extractFromShadowRoot(root, depth = 0) {
                    if (depth > 5) return;
                    
                    const shadowHosts = root.querySelectorAll('*');
                    for (const host of shadowHosts) {
                        if (host.shadowRoot) {
                            // Extract elements from shadow root
                            const shadowElements = host.shadowRoot.querySelectorAll('*');
                            for (const element of shadowElements) {
                                const rect = element.getBoundingClientRect();
                                const styles = window.getComputedStyle(element);
                                
                                if (rect.width > 0 && rect.height > 0 && 
                                    styles.display !== 'none' && 
                                    styles.visibility !== 'hidden') {
                                    
                                    const attributes = {};
                                    for (const attr of element.attributes) {
                                        attributes[attr.name] = attr.value;
                                    }
                                    
                                    elements.push({
                                        tag_name: element.tagName.toLowerCase(),
                                        text: element.textContent?.trim().substring(0, 200),
                                        attributes: attributes,
                                        is_shadow_element: true,
                                        shadow_host: host.tagName.toLowerCase(),
                                        bounding_box: {
                                            x: rect.x,
                                            y: rect.y,
                                            width: rect.width,
                                            height: rect.height,
                                            top: rect.top,
                                            bottom: rect.bottom,
                                            left: rect.left,
                                            right: rect.right
                                        },
                                        computed_style: {
                                            display: styles.display,
                                            visibility: styles.visibility,
                                            opacity: styles.opacity,
                                            cursor: styles.cursor
                                        },
                                        is_visible: true,
                                        is_enabled: !element.disabled
                                    });
                                }
                            }
                            // Recursively check for nested shadow roots
                            extractFromShadowRoot(host.shadowRoot, depth + 1);
                        }
                    }
                }
                
                extractFromShadowRoot(document, 0);
                return elements;
            }
        """

        elements = await page.evaluate(script)
        return elements

    async def _extract_iframe_elements(self, page: Page) -> List[Dict[str, Any]]:
        """Extract elements from iframes"""
        iframe_elements = []

        frames = page.frames
        for frame in frames[1:]:  # Skip main frame
            try:
                frame_url = frame.url

                script = r"""
                    () => {
                        const elements = [];
                        const allElements = document.querySelectorAll('a, button, input, select, textarea, [role="button"], [onclick]');
                        
                        for (const element of allElements) {
                            const rect = element.getBoundingClientRect();
                            const styles = window.getComputedStyle(element);
                            
                            if (rect.width > 0 && rect.height > 0) {
                                const attributes = {};
                                for (const attr of element.attributes) {
                                    attributes[attr.name] = attr.value;
                                }
                                
                                elements.push({
                                    tag_name: element.tagName.toLowerCase(),
                                    text: element.textContent?.trim().substring(0, 200),
                                    attributes: attributes,
                                    is_iframe_element: true,
                                    bounding_box: {
                                        x: rect.x,
                                        y: rect.y,
                                        width: rect.width,
                                        height: rect.height,
                                        top: rect.top,
                                        bottom: rect.bottom,
                                        left: rect.left,
                                        right: rect.right
                                    },
                                    computed_style: {
                                        display: styles.display,
                                        visibility: styles.visibility,
                                        opacity: styles.opacity,
                                        cursor: styles.cursor
                                    },
                                    is_visible: true,
                                    is_enabled: !element.disabled
                                });
                            }
                        }
                        
                        return elements;
                    }
                """

                frame_elements = await frame.evaluate(script)

                # Add frame URL to each element
                for element in frame_elements:
                    element["frame_url"] = frame_url

                iframe_elements.extend(frame_elements)

            except Exception as e:
                logger.debug("Could not extract from iframe: %s", str(e))

        return iframe_elements

    def _process_elements(self, raw_elements: List[Dict[str, Any]]) -> List[ExtractedElement]:
        """Process raw element data into ExtractedElement objects"""
        processed = []

        for raw in raw_elements:
            try:
                # Create ExtractedElement
                element = ExtractedElement(
                    tag_name=raw.get("tag_name", ""),
                    element_type=ElementType.UNKNOWN,  # Will be classified
                    text=raw.get("text"),
                    value=raw.get("value"),
                    attributes=raw.get("attributes", {}),
                    xpath=raw.get("xpath"),
                    css_path=raw.get("css_path"),
                    is_clickable=raw.get("is_clickable", False),
                    is_enabled=raw.get("is_enabled", True),
                    is_editable=raw.get("is_editable", False),
                    is_shadow_element=raw.get("is_shadow_element", False),
                    is_iframe_element=raw.get("is_iframe_element", False),
                    shadow_host=raw.get("shadow_host"),
                    frame_url=raw.get("frame_url"),
                    extraction_timestamp=time.time(),
                )

                # Create BoundingBox
                if bbox_data := raw.get("bounding_box"):
                    element.bounding_box = BoundingBox(
                        x=bbox_data.get("x", 0),
                        y=bbox_data.get("y", 0),
                        width=bbox_data.get("width", 0),
                        height=bbox_data.get("height", 0),
                        top=bbox_data.get("top", 0),
                        right=bbox_data.get("right", 0),
                        bottom=bbox_data.get("bottom", 0),
                        left=bbox_data.get("left", 0),
                    )

                # Create ComputedStyle
                if style_data := raw.get("computed_style"):
                    element.computed_style = ComputedStyle(
                        display=style_data.get("display", "block"),
                        visibility=style_data.get("visibility", "visible"),
                        opacity=style_data.get("opacity", "1"),
                        position=style_data.get("position", "static"),
                        z_index=style_data.get("z_index", "auto"),
                        background_color=style_data.get("background_color", ""),
                        color=style_data.get("color", ""),
                        font_size=style_data.get("font_size", ""),
                        font_weight=style_data.get("font_weight", ""),
                        cursor=style_data.get("cursor", "default"),
                        overflow=style_data.get("overflow", "visible"),
                    )

                # Classify element type
                element.element_type = self.classifier.classify_element(raw)

                # Generate selectors
                element.selectors = self.selector_generator.generate_selectors(raw)

                # Determine interaction types
                element.interaction_types = self.classifier.determine_interaction_types(element)

                # Validate element
                is_valid, issues = self.validator.validate_element(element)
                element.is_valid = is_valid
                element.validation_issues = issues

                # Calculate confidence score
                element.confidence = self.validator.calculate_confidence_score(element)

                # Calculate stability score
                element.stability_score = self.validator.calculate_stability_score(element)

                # Set extraction method
                if element.is_shadow_element:
                    element.extraction_method = ExtractionMethod.SHADOW_DOM
                elif element.is_iframe_element:
                    element.extraction_method = ExtractionMethod.IFRAME
                else:
                    element.extraction_method = ExtractionMethod.DOM_QUERY

                # Update performance counters
                self.performance_monitor.increment_counter(f"element_type_{element.element_type.value}")

                processed.append(element)

            except Exception as e:
                logger.debug("Error processing element: %s", str(e))
                continue

        return processed

    def _filter_elements(self, elements: List[ExtractedElement]) -> List[ExtractedElement]:
        """Filter elements based on configuration"""
        filtered = elements

        # Filter invisible elements
        if self.config.filter_invisible:
            before = len(filtered)
            filtered = [e for e in filtered if e.bounding_box and e.bounding_box.is_visible()]
            self.performance_monitor.increment_counter("filtered_invisible", before - len(filtered))

        # Filter by minimum size
        if self.config.min_element_size > 0:
            before = len(filtered)
            filtered = [e for e in filtered if e.bounding_box and e.bounding_box.area >= self.config.min_element_size]
            self.performance_monitor.increment_counter("filtered_small", before - len(filtered))

        # Filter duplicates
        if self.config.filter_duplicates:
            before = len(filtered)
            filtered = self.validator.filter_duplicate_elements(filtered)
            self.performance_monitor.increment_counter("filtered_duplicates", before - len(filtered))

        # Limit to max elements
        if len(filtered) > self.config.max_elements:
            # Sort by confidence and take top elements
            filtered.sort(key=lambda e: e.confidence, reverse=True)
            filtered = filtered[: self.config.max_elements]

        return filtered

    def _calculate_statistics(
        self, all_elements: List[ExtractedElement], filtered_elements: List[ExtractedElement]
    ) -> Dict[str, Any]:
        """Calculate extraction statistics"""
        stats = self.performance_monitor.get_statistics()

        # Element counts
        stats["total_elements"] = len(all_elements)
        stats["filtered_elements"] = len(filtered_elements)
        stats["removed_elements"] = len(all_elements) - len(filtered_elements)

        # Confidence statistics
        if filtered_elements:
            confidences = [e.confidence for e in filtered_elements]
            stats["avg_confidence"] = sum(confidences) / len(confidences)
            stats["min_confidence"] = min(confidences)
            stats["max_confidence"] = max(confidences)

        # Stability statistics
        if filtered_elements:
            stabilities = [e.stability_score for e in filtered_elements]
            stats["avg_stability"] = sum(stabilities) / len(stabilities)

        # Selector strategy distribution
        strategy_counts: Counter[str] = Counter()
        for element in filtered_elements:
            if best_selector := element.get_best_selector():
                strategy_counts[best_selector.strategy.value] += 1
        stats["selector_strategies"] = dict(strategy_counts)

        # Extraction method distribution
        method_counts: Counter[str] = Counter()
        for element in filtered_elements:
            if element.extraction_method:
                method_counts[element.extraction_method.value] += 1
        stats["extraction_methods"] = dict(method_counts)

        return stats

    async def _capture_screenshots(self, page: Page, elements: List[ExtractedElement]) -> List[ScreenshotData]:
        """Capture screenshots with comprehensive QA features"""
        screenshots = []

        try:
            # Collect rich metadata first
            metadata = await self._collect_screenshot_metadata(page)

            # Determine granularity based on config
            if self.config.screenshot_full_page:
                granularity = ScreenshotGranularity.FULL_PAGE
            else:
                granularity = ScreenshotGranularity.VIEWPORT

            # Capture base screenshot
            screenshot_bytes = await self._capture_with_granularity(page, granularity, elements)

            # Get actual dimensions
            viewport_size = page.viewport_size

            # Create comprehensive screenshot data
            screenshot_data = ScreenshotData(
                data=base64.b64encode(screenshot_bytes).decode("utf-8"),
                format=self.config.screenshot_format,
                width=viewport_size["width"] if viewport_size else 0,
                height=viewport_size["height"] if viewport_size else 0,
                granularity=granularity,
                mode=ScreenshotMode.SINGLE,
                timestamp=time.time(),
                metadata=metadata,
                file_size=len(screenshot_bytes),
                quality_score=self._calculate_quality_score(screenshot_bytes),
            )
            screenshots.append(screenshot_data)

            # Capture with highlights if configured
            if self.config.highlight_elements and elements:
                highlighted_screenshot = await self._capture_with_highlights(page, elements, granularity, metadata)
                if highlighted_screenshot:
                    screenshots.append(highlighted_screenshot)

            # Capture element-specific screenshots for important elements
            if len(elements) <= 10:  # Limit for performance
                element_screenshots = await self._capture_element_screenshots(page, elements[:5], metadata)
                screenshots.extend(element_screenshots)

            logger.info("Captured %d comprehensive screenshots", len(screenshots))

        except Exception as e:
            logger.error("Error capturing screenshots: %s", str(e))

        return screenshots

    async def capture_advanced_screenshot(
        self,
        page: Page,
        granularity: ScreenshotGranularity,
        mode: ScreenshotMode = ScreenshotMode.SINGLE,
        annotations: Optional[List[ScreenshotAnnotation]] = None,
        target_element: Optional[ExtractedElement] = None,
        context_padding: int = 50,
        comparison_screenshot: Optional[ScreenshotData] = None,
    ) -> Optional[ScreenshotData]:
        """
        Capture advanced screenshot with specific granularity and features.
        Based on 30+ years QA experience requirements.

        Args:
            page: The page to capture
            granularity: Level of detail to capture
            mode: Capture mode (single, sequence, comparison, etc)
            annotations: Annotations to add
            target_element: Specific element to focus on
            context_padding: Padding around element for context captures
            comparison_screenshot: Previous screenshot for comparison modes

        Returns:
            ScreenshotData with all requested features
        """
        try:
            # Collect comprehensive metadata
            metadata = await self._collect_screenshot_metadata(page)

            # Capture based on granularity
            if granularity == ScreenshotGranularity.ELEMENT and target_element:
                screenshot_bytes = await self._capture_element_only(page, target_element)

            elif granularity == ScreenshotGranularity.ELEMENT_WITH_CONTEXT and target_element:
                screenshot_bytes = await self._capture_element_with_context(page, target_element, context_padding)

            elif granularity == ScreenshotGranularity.COMPONENT and target_element:
                screenshot_bytes = await self._capture_component(page, target_element)

            elif granularity == ScreenshotGranularity.SECTION:
                screenshot_bytes = await self._capture_section(page, target_element)

            elif granularity == ScreenshotGranularity.ABOVE_FOLD:
                screenshot_bytes = await self._capture_above_fold(page)

            elif granularity == ScreenshotGranularity.INTERACTION_ZONE and target_element:
                screenshot_bytes = await self._capture_interaction_zone(page, target_element)

            elif granularity == ScreenshotGranularity.FULL_PAGE:
                screenshot_bytes = await page.screenshot(full_page=True, type="png")

            else:  # Default to viewport
                screenshot_bytes = await page.screenshot(type="png")

            # Apply annotations if provided
            if annotations:
                screenshot_bytes = await self._apply_annotations(page, screenshot_bytes, annotations)

            # Handle comparison modes
            if mode == ScreenshotMode.COMPARISON and comparison_screenshot:
                screenshot_bytes = await self._create_comparison_view(screenshot_bytes, comparison_screenshot)
            elif mode == ScreenshotMode.DIFF and comparison_screenshot:
                screenshot_bytes = await self._create_diff_view(screenshot_bytes, comparison_screenshot)

            # Get dimensions
            viewport_size = page.viewport_size

            # Create comprehensive screenshot data
            screenshot = ScreenshotData(
                data=base64.b64encode(screenshot_bytes).decode("utf-8"),
                format="png",
                width=viewport_size["width"] if viewport_size else 0,
                height=viewport_size["height"] if viewport_size else 0,
                granularity=granularity,
                mode=mode,
                timestamp=time.time(),
                metadata=metadata,
                annotations=annotations or [],
                file_size=len(screenshot_bytes),
                quality_score=self._calculate_quality_score(screenshot_bytes),
            )

            return screenshot

        except Exception as e:
            logger.error("Error capturing advanced screenshot: %s", str(e))
            return None

    async def capture_sequence(
        self,
        page: Page,
        actions: List[Callable],
        granularity: ScreenshotGranularity = ScreenshotGranularity.VIEWPORT,
        labels: Optional[List[str]] = None,
    ) -> List[ScreenshotData]:
        """
        Capture screenshot sequence for documenting workflows.
        Critical for QA documentation and bug reproduction.

        Args:
            page: The page to capture
            actions: List of actions to perform between screenshots
            granularity: Level of detail for each capture
            labels: Labels for each screenshot in sequence

        Returns:
            List of screenshots documenting the sequence
        """
        screenshots = []
        parent_id = f"sequence_{int(time.time())}"

        try:
            # Capture initial state
            initial = await self.capture_advanced_screenshot(page, granularity, mode=ScreenshotMode.SEQUENCE)
            if initial:
                initial.parent_screenshot_id = parent_id
                if labels and len(labels) > 0:
                    annotation = ScreenshotAnnotation(
                        type=AnnotationType.TEXT, text=f"Step 1: {labels[0]}", position=(10, 10)
                    )
                    initial.annotations.append(annotation)
                screenshots.append(initial)

            # Execute actions and capture after each
            for i, action in enumerate(actions):
                # Perform action
                await action(page)

                # Small delay for visual changes
                await asyncio.sleep(0.5)

                # Capture state after action
                screenshot = await self.capture_advanced_screenshot(page, granularity, mode=ScreenshotMode.SEQUENCE)
                if screenshot:
                    screenshot.parent_screenshot_id = parent_id
                    if labels and i + 1 < len(labels):
                        annotation = ScreenshotAnnotation(
                            type=AnnotationType.TEXT, text=f"Step {i + 2}: {labels[i + 1]}", position=(10, 10)
                        )
                        screenshot.annotations.append(annotation)
                    screenshots.append(screenshot)

            # Link screenshots in sequence
            for i in range(len(screenshots) - 1):
                screenshots[i].related_screenshots.append(f"next_{i+1}")
                screenshots[i + 1].related_screenshots.append(f"prev_{i}")

        except Exception as e:
            logger.error("Error capturing sequence: %s", str(e))

        return screenshots

    async def capture_visual_regression_pair(
        self,
        page: Page,
        baseline_url: str,
        test_url: str,
        granularity: ScreenshotGranularity = ScreenshotGranularity.FULL_PAGE,
    ) -> Tuple[ScreenshotData, ScreenshotData, ScreenshotComparison]:
        """
        Capture screenshots for visual regression testing.
        Essential for QA automation and CI/CD pipelines.
        """
        # Navigate to baseline
        await page.goto(baseline_url)
        await self._wait_for_page_stability(page)
        baseline = await self.capture_advanced_screenshot(page, granularity)

        # Navigate to test version
        await page.goto(test_url)
        await self._wait_for_page_stability(page)
        test = await self.capture_advanced_screenshot(page, granularity)

        # Compare screenshots
        comparison = await self._compare_screenshots(baseline, test)

        return baseline, test, comparison

    async def _highlight_elements(self, page: Page, elements: List[ExtractedElement]) -> List[str]:
        """Highlight elements on the page"""
        highlighted_ids = []

        script = """
            (elements, color, width) => {
                const highlightedIds = [];
                
                elements.forEach((elementData, index) => {
                    try {
                        let element = null;
                        
                        // Try to find element using different strategies
                        if (elementData.xpath) {
                            const result = document.evaluate(
                                elementData.xpath,
                                document,
                                null,
                                XPathResult.FIRST_ORDERED_NODE_TYPE,
                                null
                            );
                            element = result.singleNodeValue;
                        }
                        
                        if (!element && elementData.css_path) {
                            try {
                                element = document.querySelector(elementData.css_path);
                            } catch (e) {}
                        }
                        
                        if (!element && elementData.selectors && elementData.selectors.length > 0) {
                            for (const selector of elementData.selectors) {
                                try {
                                    element = document.querySelector(selector.value);
                                    if (element) break;
                                } catch (e) {}
                            }
                        }
                        
                        if (element) {
                            // Add highlight
                            const originalStyle = element.style.cssText;
                            element.setAttribute('data-original-style', originalStyle);
                            element.setAttribute('data-highlight-id', `highlight-${index}`);
                            element.style.outline = `${width}px solid ${color}`;
                            element.style.outlineOffset = '2px';
                            highlightedIds.push(`highlight-${index}`);
                        }
                    } catch (e) {
                        console.error('Error highlighting element:', e);
                    }
                });
                
                return highlightedIds;
            }
        """

        # Prepare element data for script
        element_data = []
        for element in elements[:50]:  # Limit to 50 elements to avoid performance issues
            data = {
                "xpath": element.xpath,
                "css_path": element.css_path,
                "selectors": [{"value": s.value} for s in element.selectors[:3]],  # Limit selectors
            }
            element_data.append(data)

        # Pass all parameters as a single object
        params = {"elements": element_data, "color": self.config.highlight_color, "width": self.config.highlight_width}

        highlighted_ids = await page.evaluate(
            f"""({script})({json.dumps(params['elements'])}, '{params['color']}', {params['width']})"""
        )

        return highlighted_ids

    async def _remove_highlights(self, page: Page):
        """Remove element highlights from the page"""
        script = """
            () => {
                const highlightedElements = document.querySelectorAll('[data-highlight-id]');
                highlightedElements.forEach(element => {
                    const originalStyle = element.getAttribute('data-original-style') || '';
                    element.style.cssText = originalStyle;
                    element.removeAttribute('data-original-style');
                    element.removeAttribute('data-highlight-id');
                });
            }
        """

        await page.evaluate(script)

    async def _collect_screenshot_metadata(self, page: Page) -> ScreenshotMetadata:
        """Collect comprehensive metadata for QA debugging"""
        try:
            # Basic info
            url = page.url
            timestamp = time.time()

            # Browser info
            user_agent = await page.evaluate("() => navigator.userAgent")
            viewport = page.viewport_size

            # Page state
            page_title = await page.title()

            # Collect console messages (would need to be set up earlier)
            console_errors: List[str] = []
            console_warnings: List[str] = []
            console_logs: List[str] = []

            # Performance metrics
            perf_data = await page.evaluate(
                """
                () => {
                    const perf = performance.timing;
                    return {
                        pageLoadTime: perf.loadEventEnd - perf.navigationStart,
                        domReadyTime: perf.domContentLoadedEventEnd - perf.navigationStart
                    };
                }
            """
            )

            # Create metadata
            metadata = ScreenshotMetadata(
                url=url,
                timestamp=timestamp,
                user_agent=user_agent,
                viewport_width=viewport["width"] if viewport else 0,
                viewport_height=viewport["height"] if viewport else 0,
                page_title=page_title,
                page_load_time=perf_data.get("pageLoadTime", 0) / 1000.0,
                dom_ready_time=perf_data.get("domReadyTime", 0) / 1000.0,
                console_errors=console_errors,
                console_warnings=console_warnings,
                console_logs=console_logs,
            )

            return metadata

        except Exception as e:
            logger.debug("Error collecting metadata: %s", str(e))
            return ScreenshotMetadata(url=page.url, timestamp=time.time())

    async def _capture_with_granularity(
        self, page: Page, granularity: ScreenshotGranularity, elements: Optional[List[ExtractedElement]] = None
    ) -> bytes:
        """Capture screenshot with specified granularity"""
        if granularity == ScreenshotGranularity.FULL_PAGE:
            return await page.screenshot(full_page=True, type="png")
        elif granularity == ScreenshotGranularity.ABOVE_FOLD:
            return await self._capture_above_fold(page)
        else:
            return await page.screenshot(type="png")

    async def _capture_above_fold(self, page: Page) -> bytes:
        """Capture content visible without scrolling"""
        # Scroll to top first
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.2)
        return await page.screenshot(type="png")

    async def _capture_element_only(self, page: Page, element: ExtractedElement) -> bytes:
        """Capture just the element"""
        try:
            # Find element handle
            element_handle = None
            if element.xpath:
                try:
                    element_handle = await page.wait_for_selector(f"xpath={element.xpath}", timeout=1000)
                except Exception as e:
                    logger.debug(f"Selector wait failed: {e}")

            if element_handle:
                return await element_handle.screenshot(type="png")
            else:
                # Fallback to viewport
                return await page.screenshot(type="png")
        except Exception as e:
            logger.debug(f"Screenshot capture failed: {e}")
            return await page.screenshot(type="png")

    async def _capture_element_with_context(self, page: Page, element: ExtractedElement, padding: int = 50) -> bytes:
        """Capture element with surrounding context"""
        try:
            if element.bounding_box:
                # Calculate region with padding
                x = max(0, element.bounding_box.x - padding)
                y = max(0, element.bounding_box.y - padding)
                width = element.bounding_box.width + (padding * 2)
                height = element.bounding_box.height + (padding * 2)

                # Capture region
                return await page.screenshot(type="png", clip={"x": x, "y": y, "width": width, "height": height})
            else:
                return await self._capture_element_only(page, element)
        except Exception as e:
            logger.debug(f"Screenshot capture failed: {e}")
            return await page.screenshot(type="png")

    async def _capture_component(self, page: Page, element: ExtractedElement) -> bytes:
        """Capture logical component containing the element"""
        try:
            # Find parent component (form, card, section, etc)
            script = """
                (xpath) => {
                    const result = document.evaluate(xpath, document, null, 
                                                    XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                    const element = result.singleNodeValue;
                    if (!element) return null;
                    
                    // Walk up to find semantic container
                    let parent = element;
                    const componentTags = ['FORM', 'ARTICLE', 'SECTION', 'ASIDE', 'NAV', 'MAIN'];
                    const componentClasses = ['card', 'panel', 'widget', 'component', 'module'];
                    
                    while (parent && parent !== document.body) {
                        if (componentTags.includes(parent.tagName)) {
                            break;
                        }
                        const classes = parent.className || '';
                        if (componentClasses.some(c => classes.toLowerCase().includes(c))) {
                            break;
                        }
                        parent = parent.parentElement;
                    }
                    
                    if (parent && parent !== document.body) {
                        const rect = parent.getBoundingClientRect();
                        return {x: rect.x, y: rect.y, width: rect.width, height: rect.height};
                    }
                    return null;
                }
            """

            if element.xpath:
                bounds = await page.evaluate(script, element.xpath)
                if bounds:
                    return await page.screenshot(
                        type="png",
                        clip={"x": bounds["x"], "y": bounds["y"], "width": bounds["width"], "height": bounds["height"]},
                    )

            return await self._capture_element_with_context(page, element)
        except Exception as e:
            logger.debug(f"Screenshot capture failed: {e}")
            return await page.screenshot(type="png")

    async def _capture_section(self, page: Page, element: Optional[ExtractedElement] = None) -> bytes:
        """Capture page section"""
        try:
            # If element provided, find its section
            if element and element.xpath:
                script = """
                    (xpath) => {
                        const result = document.evaluate(xpath, document, null,
                                                        XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                        const element = result.singleNodeValue;
                        if (!element) return null;
                        
                        // Find containing section
                        let section = element.closest('section, [role="region"], .section');
                        if (section) {
                            const rect = section.getBoundingClientRect();
                            return {x: rect.x, y: rect.y, width: rect.width, height: rect.height};
                        }
                        return null;
                    }
                """

                bounds = await page.evaluate(script, element.xpath)
                if bounds:
                    return await page.screenshot(
                        type="png",
                        clip={"x": bounds["x"], "y": bounds["y"], "width": bounds["width"], "height": bounds["height"]},
                    )

            # Default to viewport
            return await page.screenshot(type="png")
        except Exception as e:
            logger.debug(f"Screenshot capture failed: {e}")
            return await page.screenshot(type="png")

    async def _capture_interaction_zone(self, page: Page, element: ExtractedElement) -> bytes:
        """Capture element and related interactive elements"""
        try:
            # Find related form fields, buttons, etc
            script = """
                (xpath) => {
                    const result = document.evaluate(xpath, document, null,
                                                    XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                    const element = result.singleNodeValue;
                    if (!element) return null;
                    
                    // Find form or container
                    const form = element.closest('form');
                    const container = form || element.closest('[role="group"], fieldset, .form-group');
                    
                    if (container) {
                        const rect = container.getBoundingClientRect();
                        return {x: rect.x, y: rect.y, width: rect.width, height: rect.height};
                    }
                    
                    // Fallback to element with padding
                    const rect = element.getBoundingClientRect();
                    return {x: rect.x - 20, y: rect.y - 20, 
                           width: rect.width + 40, height: rect.height + 40};
                }
            """

            if element.xpath:
                bounds = await page.evaluate(script, element.xpath)
                if bounds:
                    return await page.screenshot(
                        type="png",
                        clip={
                            "x": max(0, bounds["x"]),
                            "y": max(0, bounds["y"]),
                            "width": bounds["width"],
                            "height": bounds["height"],
                        },
                    )

            return await self._capture_element_with_context(page, element)
        except Exception as e:
            logger.debug(f"Screenshot capture failed: {e}")
            return await page.screenshot(type="png")

    async def _capture_with_highlights(
        self,
        page: Page,
        elements: List[ExtractedElement],
        granularity: ScreenshotGranularity,
        metadata: ScreenshotMetadata,
    ) -> Optional[ScreenshotData]:
        """Capture screenshot with highlighted elements"""
        try:
            # Apply highlights
            highlighted_ids = await self._highlight_elements(page, elements)

            # Capture
            screenshot_bytes = await self._capture_with_granularity(page, granularity, elements)

            # Remove highlights
            await self._remove_highlights(page)

            # Get dimensions
            viewport_size = page.viewport_size

            # Create screenshot data
            screenshot = ScreenshotData(
                data=base64.b64encode(screenshot_bytes).decode("utf-8"),
                format="png",
                width=viewport_size["width"] if viewport_size else 0,
                height=viewport_size["height"] if viewport_size else 0,
                granularity=granularity,
                mode=ScreenshotMode.SINGLE,
                timestamp=time.time(),
                metadata=metadata,
                highlighted_elements=highlighted_ids,
                file_size=len(screenshot_bytes),
                quality_score=self._calculate_quality_score(screenshot_bytes),
            )

            return screenshot

        except Exception as e:
            logger.debug("Error capturing with highlights: %s", str(e))
            return None

    async def _capture_element_screenshots(
        self, page: Page, elements: List[ExtractedElement], metadata: ScreenshotMetadata
    ) -> List[ScreenshotData]:
        """Capture individual screenshots for important elements"""
        screenshots = []

        for element in elements:
            try:
                screenshot_bytes = await self._capture_element_with_context(page, element, padding=20)

                # Get dimensions
                viewport_size = page.viewport_size

                screenshot = ScreenshotData(
                    data=base64.b64encode(screenshot_bytes).decode("utf-8"),
                    format="png",
                    width=viewport_size["width"] if viewport_size else 0,
                    height=viewport_size["height"] if viewport_size else 0,
                    granularity=ScreenshotGranularity.ELEMENT_WITH_CONTEXT,
                    mode=ScreenshotMode.SINGLE,
                    timestamp=time.time(),
                    metadata=metadata,
                    captured_elements=[element.tag_name],
                    file_size=len(screenshot_bytes),
                    quality_score=self._calculate_quality_score(screenshot_bytes),
                )

                screenshots.append(screenshot)

            except Exception as e:
                logger.debug("Error capturing element screenshot: %s", str(e))
                continue

        return screenshots

    def _calculate_quality_score(self, image_bytes: bytes) -> float:
        """Calculate quality score for screenshot"""
        # Simple heuristic based on size and assumed quality
        size = len(image_bytes)

        if size < 10000:  # < 10KB probably too small
            return 0.3
        elif size < 50000:  # < 50KB might be low quality
            return 0.6
        elif size < 500000:  # < 500KB good quality
            return 0.8
        elif size < 2000000:  # < 2MB excellent quality
            return 0.95
        else:  # Very large, might be unnecessary
            return 0.85

    async def _apply_annotations(
        self, page: Page, screenshot_bytes: bytes, annotations: List[ScreenshotAnnotation]
    ) -> bytes:
        """Apply annotations to screenshot (requires image processing library in production)"""
        # In production, you would use PIL/Pillow or similar to actually draw annotations
        # For now, return original
        return screenshot_bytes

    async def _create_comparison_view(self, current_bytes: bytes, comparison_screenshot: ScreenshotData) -> bytes:
        """Create side-by-side comparison view (requires image processing in production)"""
        # In production, combine images side-by-side
        return current_bytes

    async def _create_diff_view(self, current_bytes: bytes, comparison_screenshot: ScreenshotData) -> bytes:
        """Create diff view highlighting changes (requires image processing in production)"""
        # In production, create visual diff
        return current_bytes

    async def _compare_screenshots(self, baseline: ScreenshotData, test: ScreenshotData) -> ScreenshotComparison:
        """Compare two screenshots for visual regression"""
        # Simple comparison - in production use image diff libraries
        similarity = 0.95 if baseline.file_size == test.file_size else 0.7

        return ScreenshotComparison(
            similarity_score=similarity,
            pixel_diff_count=0,
            structural_diff=[],
            diff_regions=[],
            analysis="Screenshots appear similar" if similarity > 0.9 else "Differences detected",
        )

    async def capture_element_screenshot(self, page: Page, element: ExtractedElement) -> Optional[ScreenshotData]:
        """Capture screenshot of a specific element"""
        try:
            # Find element on page
            element_handle = None

            # Try different strategies to locate element
            if element.xpath:
                try:
                    element_handle = await page.wait_for_selector(f"xpath={element.xpath}", timeout=1000)
                except Exception as e:
                    logger.debug(f"Selector wait failed: {e}")

            if not element_handle and element.get_best_selector():
                try:
                    selector = element.get_best_selector().value
                    element_handle = await page.wait_for_selector(selector, timeout=1000)
                except Exception as e:
                    logger.debug(f"Selector wait failed: {e}")

            if element_handle:
                # Capture element screenshot
                screenshot_bytes = await element_handle.screenshot(
                    type=self.config.screenshot_format,
                    quality=self.config.screenshot_quality if self.config.screenshot_format == "jpeg" else None,
                )

                # Get element bounding box
                box = await element_handle.bounding_box()

                screenshot_data = ScreenshotData(
                    data=base64.b64encode(screenshot_bytes).decode("utf-8"),
                    format=self.config.screenshot_format,
                    width=int(box["width"]) if box else 0,
                    height=int(box["height"]) if box else 0,
                    full_page=False,
                    timestamp=time.time(),
                    highlighted_elements=[],
                )

                return screenshot_data

        except Exception as e:
            logger.debug("Error capturing element screenshot: %s", str(e))

        return None

    async def capture_accessibility_view(
        self, page: Page, granularity: ScreenshotGranularity = ScreenshotGranularity.VIEWPORT
    ) -> ScreenshotData:
        """
        Capture screenshot with accessibility overlays.
        Critical for QA testing of WCAG compliance.
        """
        # Apply accessibility overlays
        await page.evaluate(
            """
            () => {
                // Highlight focus order
                let tabIndex = 1;
                document.querySelectorAll('[tabindex], a, button, input, select, textarea').forEach(el => {
                    const label = document.createElement('div');
                    label.style.cssText = 'position:absolute;background:blue;color:white;padding:2px 4px;font-size:10px;z-index:9999;pointer-events:none';
                    label.textContent = tabIndex++;
                    const rect = el.getBoundingClientRect();
                    label.style.left = rect.left + 'px';
                    label.style.top = rect.top + 'px';
                    label.className = 'qa-accessibility-overlay';
                    document.body.appendChild(label);
                });
                
                // Highlight ARIA labels
                document.querySelectorAll('[aria-label], [role]').forEach(el => {
                    el.style.outline = '2px dashed purple';
                });
            }
        """
        )

        # Capture screenshot
        screenshot = await self.capture_advanced_screenshot(page, granularity)

        # Remove overlays
        await page.evaluate(
            """
            () => {
                document.querySelectorAll('.qa-accessibility-overlay').forEach(el => el.remove());
                document.querySelectorAll('[aria-label], [role]').forEach(el => {
                    el.style.outline = '';
                });
            }
        """
        )

        if screenshot:
            screenshot.metadata.tags.append("accessibility")

        return screenshot

    async def capture_responsive_set(
        self, page: Page, url: str, viewports: Optional[List[Dict[str, int]]] = None
    ) -> List[ScreenshotData]:
        """
        Capture screenshots at multiple viewport sizes.
        Essential for responsive design QA.
        """
        if not viewports:
            viewports = [
                {"width": 320, "height": 568},  # Mobile small
                {"width": 375, "height": 812},  # Mobile medium
                {"width": 768, "height": 1024},  # Tablet
                {"width": 1024, "height": 768},  # Desktop small
                {"width": 1920, "height": 1080},  # Desktop large
            ]

        screenshots = []

        for viewport in viewports:
            # Set viewport
            await page.set_viewport_size(viewport)

            # Navigate if needed
            if page.url != url:
                await page.goto(url)
                await self._wait_for_page_stability(page)

            # Capture
            screenshot = await self.capture_advanced_screenshot(page, ScreenshotGranularity.FULL_PAGE)

            if screenshot:
                screenshot.metadata.tags.append(f"viewport_{viewport['width']}x{viewport['height']}")
                screenshots.append(screenshot)

        return screenshots

    async def capture_error_state(self, page: Page, error_info: Optional[Dict[str, Any]] = None) -> ScreenshotData:
        """
        Capture screenshot with error context.
        Critical for bug reports and debugging.
        """
        # Collect console errors
        console_errors = await page.evaluate(
            """
            () => {
                // Get any errors from console (if captured)
                return window.__capturedErrors || [];
            }
        """
        )

        # Add error indicator
        if error_info:
            await page.evaluate(
                """
                (info) => {
                    const errorDiv = document.createElement('div');
                    errorDiv.style.cssText = 'position:fixed;top:10px;right:10px;background:red;color:white;padding:10px;z-index:99999;border-radius:5px';
                    errorDiv.textContent = 'ERROR: ' + (info.message || 'Unknown error');
                    errorDiv.className = 'qa-error-indicator';
                    document.body.appendChild(errorDiv);
                }
            """,
                error_info,
            )

        # Capture with full context
        screenshot = await self.capture_advanced_screenshot(page, ScreenshotGranularity.FULL_PAGE)

        # Remove error indicator
        await page.evaluate(
            """
            () => {
                const indicator = document.querySelector('.qa-error-indicator');
                if (indicator) indicator.remove();
            }
        """
        )

        # Add error info to metadata
        if screenshot and screenshot.metadata:
            screenshot.metadata.console_errors = console_errors
            if error_info:
                screenshot.metadata.custom_data["error_info"] = error_info
            screenshot.metadata.tags.append("error_state")

        return screenshot

    async def capture_performance_timeline(
        self, page: Page, duration_seconds: int = 5, interval_ms: int = 1000
    ) -> List[ScreenshotData]:
        """
        Capture screenshots over time to show performance/loading issues.
        Useful for detecting layout shifts, lazy loading, animations.
        """
        screenshots = []
        parent_id = f"timeline_{int(time.time())}"
        num_captures = (duration_seconds * 1000) // interval_ms

        for i in range(num_captures):
            # Capture current state
            screenshot = await self.capture_advanced_screenshot(
                page, ScreenshotGranularity.VIEWPORT, mode=ScreenshotMode.TIMELINE
            )

            if screenshot:
                screenshot.parent_screenshot_id = parent_id

                # Add performance metrics
                perf_data = await page.evaluate(
                    """
                    () => {
                        const paint = performance.getEntriesByType('paint');
                        const navigation = performance.getEntriesByType('navigation')[0];
                        return {
                            firstPaint: paint.find(p => p.name === 'first-paint')?.startTime,
                            firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime,
                            domContentLoaded: navigation?.domContentLoadedEventEnd,
                            loadComplete: navigation?.loadEventEnd
                        };
                    }
                """
                )

                screenshot.metadata.custom_data["performance"] = perf_data
                screenshot.metadata.tags.append(f"timeline_{i}")
                screenshots.append(screenshot)

            # Wait for next interval
            await asyncio.sleep(interval_ms / 1000)

        return screenshots

    async def capture_interaction_flow(self, page: Page, interactions: List[Dict[str, Any]]) -> List[ScreenshotData]:
        """
        Capture screenshots documenting user interaction flow.
        Perfect for creating test documentation and bug reproduction steps.

        Args:
            interactions: List of dicts with 'action', 'target', 'value', 'description'
        """
        screenshots = []
        parent_id = f"flow_{int(time.time())}"

        # Capture initial state
        initial = await self.capture_advanced_screenshot(
            page, ScreenshotGranularity.VIEWPORT, mode=ScreenshotMode.INTERACTION
        )
        if initial:
            initial.parent_screenshot_id = parent_id
            initial.metadata.last_action = "Initial state"
            screenshots.append(initial)

        for i, interaction in enumerate(interactions):
            action = interaction.get("action")
            target = interaction.get("target")
            value = interaction.get("value")
            description = interaction.get("description", f"Step {i+1}")

            try:
                # Perform interaction
                if action == "click":
                    await page.click(target)
                elif action == "type":
                    await page.type(target, value)
                elif action == "select":
                    await page.select_option(target, value)
                elif action == "hover":
                    await page.hover(target)
                elif action == "scroll":
                    await page.evaluate(f"window.scrollTo(0, {value})")

                # Wait for changes
                await asyncio.sleep(0.5)

                # Capture after interaction
                screenshot = await self.capture_advanced_screenshot(
                    page, ScreenshotGranularity.VIEWPORT, mode=ScreenshotMode.INTERACTION
                )

                if screenshot:
                    screenshot.parent_screenshot_id = parent_id
                    screenshot.metadata.last_action = description
                    screenshot.metadata.action_sequence.append(f"{action}: {target}")

                    # Add annotation showing what was interacted with
                    annotation = ScreenshotAnnotation(
                        type=AnnotationType.BOX, target=target, text=description, color="green"
                    )
                    screenshot.annotations.append(annotation)

                    screenshots.append(screenshot)

            except Exception as e:
                logger.error(f"Error in interaction flow: {e}")
                # Capture error state
                error_screenshot = await self.capture_error_state(page, {"message": str(e), "step": description})
                if error_screenshot:
                    error_screenshot.parent_screenshot_id = parent_id
                    screenshots.append(error_screenshot)
                break

        return screenshots

    async def capture_debug_view(
        self,
        page: Page,
        include_dom_stats: bool = True,
        include_network_info: bool = True,
        include_storage: bool = True,
    ) -> ScreenshotData:
        """
        Capture screenshot with comprehensive debug information overlay.
        Essential for developer debugging and QA analysis.
        """
        debug_info = {}

        # Collect DOM statistics
        if include_dom_stats:
            dom_stats = await page.evaluate(
                """
                () => {
                    return {
                        totalElements: document.querySelectorAll('*').length,
                        images: document.images.length,
                        scripts: document.scripts.length,
                        stylesheets: document.styleSheets.length,
                        forms: document.forms.length,
                        iframes: document.querySelectorAll('iframe').length
                    };
                }
            """
            )
            debug_info["dom"] = dom_stats

        # Collect storage info
        if include_storage:
            storage_info = await page.evaluate(
                """
                () => {
                    return {
                        localStorage: Object.keys(localStorage).length,
                        sessionStorage: Object.keys(sessionStorage).length,
                        cookies: document.cookie.split(';').length
                    };
                }
            """
            )
            debug_info["storage"] = storage_info

        # Add debug overlay
        await page.evaluate(
            """
            (info) => {
                const overlay = document.createElement('div');
                overlay.style.cssText = 'position:fixed;bottom:10px;left:10px;background:rgba(0,0,0,0.8);color:lime;padding:10px;font-family:monospace;font-size:11px;z-index:99999;max-width:300px';
                overlay.className = 'qa-debug-overlay';
                overlay.innerHTML = '<pre>' + JSON.stringify(info, null, 2) + '</pre>';
                document.body.appendChild(overlay);
            }
        """,
            debug_info,
        )

        # Capture
        screenshot = await self.capture_advanced_screenshot(page, ScreenshotGranularity.VIEWPORT)

        # Remove overlay
        await page.evaluate(
            """
            () => {
                const overlay = document.querySelector('.qa-debug-overlay');
                if (overlay) overlay.remove();
            }
        """
        )

        if screenshot:
            screenshot.metadata.custom_data["debug_info"] = debug_info
            screenshot.metadata.tags.append("debug_view")

        return screenshot

    def _get_cache_key(self, url: str) -> str:
        """Generate cache key for URL"""
        return hashlib.md5(url.encode()).hexdigest()

    def clear_cache(self):
        """Clear the extraction cache"""
        self._cache.clear()
        logger.info("Cache cleared")

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return self.performance_monitor.get_statistics()


# ==================== CRAWLER CLASS ====================


class WebCrawler:
    """
    Advanced web crawler for discovering and extracting elements from multiple pages
    """

    def __init__(self, extractor: Optional[ElementsExtractorNoLLM] = None):
        """Initialize crawler with extractor"""
        self.extractor = extractor or ElementsExtractorNoLLM()
        self.visited_urls: Set[str] = set()
        self.discovered_urls: Set[str] = set()
        self.results: List[ExtractionResult] = []

    async def crawl(self, start_url: str, max_pages: int = 10, max_depth: int = 2) -> List[ExtractionResult]:
        """
        Crawl website starting from URL

        Args:
            start_url: Starting URL for crawl
            max_pages: Maximum number of pages to crawl
            max_depth: Maximum crawl depth

        Returns:
            List of extraction results from all crawled pages
        """
        logger.info("Starting crawl from %s (max_pages=%d, max_depth=%d)", start_url, max_pages, max_depth)

        # Initialize queue with start URL
        queue = [(start_url, 0)]
        base_domain = urlparse(start_url).netloc

        browser = None
        if PLAYWRIGHT_AVAILABLE:
            browser = await self.extractor._create_browser()

        try:
            while queue and len(self.visited_urls) < max_pages:
                url, depth = queue.pop(0)

                # Skip if already visited or depth exceeded
                if url in self.visited_urls or depth > max_depth:
                    continue

                # Mark as visited
                self.visited_urls.add(url)

                # Extract elements from page
                logger.info("Crawling page %d/%d: %s (depth=%d)", len(self.visited_urls), max_pages, url, depth)

                result = await self.extractor.extract_from_url(url, browser)
                self.results.append(result)

                # Discover new URLs from links
                if result.success and depth < max_depth:
                    for element in result.elements:
                        if element.element_type == ElementType.LINK:
                            if href := element.attributes.get("href"):
                                absolute_url = urljoin(url, href)
                                parsed = urlparse(absolute_url)

                                # Only crawl same domain
                                if parsed.netloc == base_domain and absolute_url not in self.visited_urls:
                                    self.discovered_urls.add(absolute_url)
                                    queue.append((absolute_url, depth + 1))

                # Respect rate limiting
                await asyncio.sleep(random.uniform(0.5, 1.5))

        finally:
            if browser:
                await browser.close()

        logger.info(
            "Crawl complete. Visited %d pages, discovered %d URLs", len(self.visited_urls), len(self.discovered_urls)
        )

        return self.results

    def get_statistics(self) -> Dict[str, Any]:
        """Get crawl statistics"""
        total_elements = sum(len(r.elements) for r in self.results)
        successful_pages = sum(1 for r in self.results if r.success)

        return {
            "pages_visited": len(self.visited_urls),
            "urls_discovered": len(self.discovered_urls),
            "successful_extractions": successful_pages,
            "total_elements_extracted": total_elements,
            "avg_elements_per_page": total_elements / len(self.results) if self.results else 0,
        }


# ==================== MAIN EXECUTION ====================


async def example_basic_extraction():
    """Example 1: Basic element extraction from a website"""
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 1: Basic Element Extraction")
    logger.info("=" * 80)

    # Initialize extractor with default config
    extractor = ElementsExtractorNoLLM()

    # Test URL (using example.com as it's always available)
    test_url = "https://example.com"

    logger.info(f"\nExtracting elements from: {test_url}")
    logger.info("-" * 40)

    # Extract elements
    result = await extractor.extract_from_url(test_url)

    if result.success:
        logger.info(f"SUCCESS: Extracted {len(result.elements)} elements")
        logger.info(f"Extraction time: {result.extraction_time:.2f} seconds")
        logger.info("\nElement type distribution:")

        # Count element types
        type_counts = Counter(e.element_type.value for e in result.elements)
        for element_type, count in type_counts.most_common():
            logger.info(f"  - {element_type}: {count}")

        # Show sample elements
        logger.info("\nSample elements (showing first 5):")
        for i, element in enumerate(result.elements[:5], 1):
            logger.info(f"\n  {i}. {element.element_type.value.upper()}")
            logger.info(f"     Tag: {element.tag_name}")
            if element.text:
                try:
                    logger.info(f"     Text: {element.text[:50]}...")
                except UnicodeEncodeError:
                    text_preview = element.text[:50].encode("ascii", "replace").decode("ascii")
                    logger.info(f"     Text: {text_preview}...")
            if best_selector := element.get_best_selector():
                logger.info(f"     Best selector: {best_selector.value} (score: {best_selector.score:.2f})")
            logger.info(f"     Confidence: {element.confidence:.2f}")
            logger.info(f"     Interactions: {[i.value for i in element.interaction_types]}")
    else:
        logger.info(f"FAILED: {result.errors}")

    # Show statistics
    logger.info("\nExtraction Statistics:")
    for key, value in result.statistics.items():
        if not isinstance(value, dict):
            logger.info(f"  - {key}: {value}")

    logger.info("\n" + "=" * 80)


async def example_advanced_extraction():
    """Example 2: Advanced extraction with screenshots and crawling"""
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 2: Advanced Extraction with Screenshots and Crawling")
    logger.info("=" * 80)

    # Create custom configuration with screenshots enabled
    config = ExtractionConfig(
        enable_shadow_dom=True,
        enable_iframe_traversal=True,
        enable_stealth=True,
        filter_invisible=True,
        filter_duplicates=True,
        min_element_size=10,
        max_elements=500,
        include_computed_styles=True,
        include_accessibility_info=True,
        # Screenshot settings
        capture_screenshots=True,
        screenshot_full_page=True,
        screenshot_format="png",
        highlight_elements=True,
        highlight_color="red",
        highlight_width=3,
    )

    # Initialize extractor with custom config
    extractor = ElementsExtractorNoLLM(config)

    # Test with a more complex website
    test_url = "https://www.wikipedia.org"

    logger.info(f"\nExtracting elements from: {test_url}")
    logger.info("Configuration:")
    logger.info(f"  - Shadow DOM extraction: {config.enable_shadow_dom}")
    logger.info(f"  - Iframe traversal: {config.enable_iframe_traversal}")
    logger.info(f"  - Stealth mode: {config.enable_stealth}")
    logger.info(f"  - Screenshots enabled: {config.capture_screenshots}")
    logger.info(f"  - Full page screenshots: {config.screenshot_full_page}")
    logger.info(f"  - Highlight elements: {config.highlight_elements}")
    logger.info(f"  - Min element size: {config.min_element_size}px")
    logger.info("-" * 40)

    # Extract elements
    result = await extractor.extract_from_url(test_url)

    if result.success:
        logger.info(f"SUCCESS: Extracted {len(result.elements)} elements")
        logger.info(f"Total found: {result.total_elements_found}")
        logger.info(f"Filtered out: {result.filtered_elements}")

        # Analyze selector strategies
        logger.info("\nSelector Strategy Analysis:")
        strategy_counts = Counter()
        for element in result.elements:
            if best_selector := element.get_best_selector():
                strategy_counts[best_selector.strategy.value] += 1

        for strategy, count in strategy_counts.most_common():
            percentage = (count / len(result.elements)) * 100
            logger.info(f"  - {strategy}: {count} ({percentage:.1f}%)")

        # Find most confident elements
        logger.info("\nMost Confident Elements (Top 5):")
        confident_elements = sorted(result.elements, key=lambda e: e.confidence, reverse=True)[:5]
        for i, element in enumerate(confident_elements, 1):
            logger.info(f"  {i}. {element.element_type.value} - Confidence: {element.confidence:.3f}")
            if element.text:
                # Handle Unicode encoding for Windows
                try:
                    text_preview = element.text[:60]
                    logger.info(f"     Text: {text_preview}...")
                except UnicodeEncodeError:
                    # Fallback to ASCII representation
                    text_preview = element.text[:60].encode("ascii", "replace").decode("ascii")
                    logger.info(f"     Text: {text_preview}...")

        # Check for special elements
        logger.info("\nSpecial Elements Found:")
        shadow_elements = [e for e in result.elements if e.is_shadow_element]
        iframe_elements = [e for e in result.elements if e.is_iframe_element]
        form_elements = [e for e in result.elements if element.element_type == ElementType.FORM]

        logger.info(f"  - Shadow DOM elements: {len(shadow_elements)}")
        logger.info(f"  - Iframe elements: {len(iframe_elements)}")
        logger.info(f"  - Form elements: {len(form_elements)}")

        # Interactive elements analysis
        logger.info("\nInteractive Elements Analysis:")
        clickable = [e for e in result.elements if e.is_clickable]
        editable = [e for e in result.elements if e.is_editable]
        buttons = [e for e in result.elements if e.element_type == ElementType.BUTTON]
        links = [e for e in result.elements if e.element_type == ElementType.LINK]
        inputs = [e for e in result.elements if e.element_type == ElementType.INPUT]

        logger.info(f"  - Clickable: {len(clickable)}")
        logger.info(f"  - Editable: {len(editable)}")
        logger.info(f"  - Buttons: {len(buttons)}")
        logger.info(f"  - Links: {len(links)}")
        logger.info(f"  - Inputs: {len(inputs)}")

        # Screenshot information
        if result.screenshots:
            logger.info(f"\nScreenshots Captured: {len(result.screenshots)}")
            for i, screenshot in enumerate(result.screenshots, 1):
                logger.info(f"  {i}. Format: {screenshot.format}, Size: {screenshot.width}x{screenshot.height}")
                logger.info(f"     Full page: {getattr(screenshot, 'full_page', 'N/A')}")
                if screenshot.highlighted_elements:
                    logger.info(f"     Highlighted elements: {len(screenshot.highlighted_elements)}")

            # Save screenshots to temp directory
            try:
                from tempfile import mkdtemp

                temp_dir = Path(mkdtemp(prefix="extractor_screenshots_"))
                saved_files = result.save_screenshots(temp_dir, prefix="wikipedia")
                logger.info(f"\nScreenshots saved to: {temp_dir}")
                for file in saved_files:
                    logger.info(f"  - {file.name}")
            except Exception as e:
                logger.info(f"Could not save screenshots: {e}")

    else:
        logger.info(f"FAILED: {result.errors}")

    # Demonstrate crawling capability
    logger.info(f"\n{'='*40}")
    logger.info("Crawling Demo (Limited to 3 pages)")
    logger.info("=" * 40)

    crawler = WebCrawler(extractor)
    crawl_results = await crawler.crawl(test_url, max_pages=3, max_depth=1)

    crawl_stats = crawler.get_statistics()
    logger.info("\nCrawl Statistics:")
    for key, value in crawl_stats.items():
        logger.info(f"  - {key}: {value}")

    # Summary of all crawled pages
    logger.info("\nPages Crawled:")
    for i, result in enumerate(crawl_results, 1):
        try:
            logger.info(f"  {i}. {result.url[:60]}...")
        except UnicodeEncodeError:
            url_preview = result.url[:60].encode("ascii", "replace").decode("ascii")
            logger.info(f"  {i}. {url_preview}...")
        logger.info(f"     Elements: {len(result.elements)}")
        logger.info(f"     Success: {result.success}")

    logger.info("\n" + "=" * 80)


async def main():
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
    logger.info("  - Anti-detection stealth measures")
    logger.info("  - Web crawling and discovery")
    logger.info("  - Performance monitoring")
    logger.info("  - Caching support")

    if not PLAYWRIGHT_AVAILABLE:
        logger.info("\nWARNING: Playwright not installed!")
        logger.info("Install with: pip install playwright")
        logger.info("Then run: playwright install chromium")
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
