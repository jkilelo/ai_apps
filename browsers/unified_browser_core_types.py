"""
Type definitions for unified browser.

This module contains all type definitions, enums, protocols, and dataclasses
used throughout the browser implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Protocol,
    TypeVar,
    Union,
)

# Type variables for generic types
T = TypeVar("T")
ElementT = TypeVar("ElementT", bound="ElementData")


# ============================================================================
# ENUMS
# ============================================================================
class BrowserEngine(Enum):
    """Browser automation engine types."""
    
    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    PUPPETEER = "puppeteer"
    UNDETECTED = "undetected"
    NODRIVER = "nodriver"
    DRISSIONPAGE = "drissionpage"
    SCRAPY_SPLASH = "scrapy_splash"


class StealthLevel(Enum):
    """Stealth level configuration."""

    NONE = "none"
    BASIC = "basic"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"


class ContentType(Enum):
    """Content types for extraction."""
    
    TEXT = "text"
    TABLE = "table"
    FORM = "form"
    LINK = "link"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    METADATA = "metadata"
    STRUCTURED_DATA = "structured_data"
    COMMENTS = "comments"


class ExtractionMethod(Enum):
    """Methods for content extraction."""
    
    CSS_SELECTOR = "css_selector"
    XPATH = "xpath"
    BEAUTIFUL_SOUP = "beautiful_soup"
    PLAYWRIGHT = "playwright"
    REGEX = "regex"
    LLM_VISION = "llm_vision"
    HYBRID = "hybrid"


class ElementType(Enum):
    """Types of DOM elements."""

    BUTTON = auto()
    LINK = auto()
    INPUT = auto()
    TEXTAREA = auto()
    SELECT = auto()
    IMAGE = auto()
    VIDEO = auto()
    FORM = auto()
    CHECKBOX = auto()
    RADIO = auto()
    DIV = auto()
    SPAN = auto()
    OTHER = auto()


class BrowserState(Enum):
    """Browser instance state."""

    UNINITIALIZED = auto()
    INITIALIZING = auto()
    READY = auto()
    NAVIGATING = auto()
    EXECUTING = auto()
    ERROR = auto()
    CLOSED = auto()


class NavigationStrategy(Enum):
    """Navigation waiting strategies."""

    LOAD = "load"
    DOM_CONTENT_LOADED = "domcontentloaded"
    NETWORK_IDLE = "networkidle"
    COMMIT = "commit"


class ExtractionStrategy(Enum):
    """Element extraction strategies."""

    STANDARD_DOM = auto()
    SHADOW_DOM = auto()
    VISUAL_INDEXED = auto()
    ECOMMERCE = auto()
    ALL = auto()


class LLMProvider(Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GEMINI = "gemini"
    XAI = "xai"


class CaptchaType(Enum):
    """Types of CAPTCHA detected."""

    NONE = auto()
    RECAPTCHA = auto()
    HCAPTCHA = auto()
    CLOUDFLARE = auto()
    CUSTOM = auto()


class FrameworkType(Enum):
    """Web framework types."""

    NONE = auto()
    REACT = auto()
    ANGULAR = auto()
    VUE = auto()
    SVELTE = auto()
    JQUERY = auto()
    UNKNOWN = auto()


# ============================================================================
# DATACLASSES
# ============================================================================
@dataclass
class Point:
    """Represents a 2D point."""

    x: float
    y: float


@dataclass
class BoundingBox:
    """Element bounding box."""

    x: float
    y: float
    width: float
    height: float

    @property
    def center(self) -> Point:
        """Get center point of bounding box."""
        return Point(x=self.x + self.width / 2, y=self.y + self.height / 2)

    @property
    def area(self) -> float:
        """Calculate area of bounding box."""
        return self.width * self.height


@dataclass
class ElementData:
    """Represents a DOM element with all its properties."""

    # Core identifiers
    index: int
    element_id: str
    tag_name: str
    element_type: ElementType

    # Selectors
    css_selector: str
    xpath: str

    # Content
    text: str = ""
    inner_html: str = ""
    outer_html: str = ""

    # Attributes
    attributes: Dict[str, str] = field(default_factory=dict)
    aria_label: Optional[str] = None
    role: Optional[str] = None

    # State
    is_visible: bool = True
    is_clickable: bool = False
    is_input: bool = False
    is_disabled: bool = False
    is_readonly: bool = False

    # Position
    bounding_box: Optional[BoundingBox] = None

    # Hierarchy
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    shadow_root: bool = False

    # Metadata
    confidence: float = 1.0
    extraction_timestamp: Optional[float] = None


@dataclass
class ExtractionResult:
    """Result of element extraction operation."""

    elements: List[ElementData]
    total_count: int
    extraction_time: float
    strategy_used: ExtractionStrategy
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """Check if extraction was successful."""
        return len(self.errors) == 0 and self.total_count > 0

    def get_by_type(self, element_type: ElementType) -> List[ElementData]:
        """Get elements by type."""
        return [e for e in self.elements if e.element_type == element_type]

    def get_clickable(self) -> List[ElementData]:
        """Get all clickable elements."""
        return [e for e in self.elements if e.is_clickable]

    def get_inputs(self) -> List[ElementData]:
        """Get all input elements."""
        return [e for e in self.elements if e.is_input]


@dataclass
class NavigationResult:
    """Result of navigation operation."""

    success: bool
    url: str
    status_code: Optional[int] = None
    load_time: Optional[float] = None
    error: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BrowserAction:
    """Represents a browser action to be executed."""

    action_type: str
    target: Optional[str] = None
    value: Optional[Any] = None
    options: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[int] = None


@dataclass
class TaskPlan:
    """Execution plan for a task."""

    task_id: str
    description: str
    steps: List[BrowserAction]
    estimated_duration: float
    priority: int = 0
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityViolation:
    """Security violation details."""

    violation_type: str
    severity: str  # "low", "medium", "high", "critical"
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[float] = None


@dataclass
class PerformanceMetrics:
    """Browser performance metrics."""

    navigation_count: int = 0
    total_navigation_time: float = 0.0
    extraction_count: int = 0
    total_extraction_time: float = 0.0
    error_count: int = 0
    success_rate: float = 1.0
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None

    @property
    def avg_navigation_time(self) -> float:
        """Calculate average navigation time."""
        if self.navigation_count == 0:
            return 0.0
        return self.total_navigation_time / self.navigation_count

    @property
    def avg_extraction_time(self) -> float:
        """Calculate average extraction time."""
        if self.extraction_count == 0:
            return 0.0
        return self.total_extraction_time / self.extraction_count


# ============================================================================
# PROTOCOLS
# ============================================================================
class BrowserProtocol(Protocol):
    """Protocol for browser implementations."""

    async def initialize(self) -> None:
        """Initialize browser instance."""
        ...

    async def navigate(self, url: str, **kwargs) -> NavigationResult:
        """Navigate to URL."""
        ...

    async def extract_elements(self, **kwargs) -> ExtractionResult:
        """Extract elements from page."""
        ...

    async def click(self, selector: str, **kwargs) -> bool:
        """Click an element."""
        ...

    async def type_text(self, selector: str, text: str, **kwargs) -> bool:
        """Type text into element."""
        ...

    async def close(self) -> None:
        """Close browser instance."""
        ...


class ExtractorProtocol(Protocol):
    """Protocol for element extractors."""

    async def extract(self, page: Any) -> List[ElementData]:
        """Extract elements from page."""
        ...


class StealthInjectorProtocol(Protocol):
    """Protocol for stealth injectors."""

    async def inject(self, page: Any, level: StealthLevel) -> None:
        """Inject stealth measures."""
        ...


class NavigatorProtocol(Protocol):
    """Protocol for navigation strategies."""

    async def navigate(self, page: Any, url: str, strategy: NavigationStrategy) -> NavigationResult:
        """Navigate using specific strategy."""
        ...


class ValidatorProtocol(Protocol):
    """Protocol for input validators."""

    def validate_url(self, url: str) -> tuple[bool, Optional[str]]:
        """Validate URL."""
        ...

    def validate_selector(self, selector: str) -> tuple[bool, Optional[str]]:
        """Validate CSS selector."""
        ...

    def validate_path(self, path: str) -> tuple[bool, Optional[str]]:
        """Validate file path."""
        ...


class LLMClientProtocol(Protocol):
    """Protocol for LLM clients."""

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from prompt."""
        ...

    async def analyze_image(self, image_data: bytes, prompt: str, **kwargs) -> str:
        """Analyze image with prompt."""
        ...


# ============================================================================
# TYPE ALIASES
# ============================================================================
# Callback types
NavigationCallback = Callable[[NavigationResult], Awaitable[None]]
ExtractionCallback = Callable[[ExtractionResult], Awaitable[None]]
ErrorCallback = Callable[[Exception], Awaitable[None]]

# Configuration types
ConfigDict = Dict[str, Any]
HeadersDict = Dict[str, str]
CookiesDict = Dict[str, str]

# Element selector types
Selector = Union[str, ElementData]
SelectorList = List[Selector]

# JavaScript types
JSFunction = str
JSResult = Any

# Coordinates
Coordinates = tuple[float, float]
CoordinatesList = List[Coordinates]
