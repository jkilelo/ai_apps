"""
Centralized Type Definitions for UI Testing Framework
Single source of truth for all data types, enums, and models
STRICT DRY: No other module should define its own types
"""

import time
import functools
import gc
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
from threading import Lock

# Pydantic v2 is REQUIRED - no fallbacks
from pydantic import BaseModel, Field, ConfigDict


# =============================================================================
# ENUM DEFINITIONS - Single source of truth
# =============================================================================


class ElementType(str, Enum):
    """Comprehensive element types - unified from browser.py (most complete)"""

    # Form Elements
    INPUT = "input"  # Generic input type for compatibility
    TEXT_INPUT = "text_input"
    PASSWORD = "password"
    EMAIL = "email"
    NUMBER = "number"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    SELECT = "select"
    TEXTAREA = "textarea"
    FILE_INPUT = "file_input"
    DATE_INPUT = "date_input"
    TIME_INPUT = "time_input"
    SEARCH = "search"
    TEL = "tel"
    URL_INPUT = "url"
    RANGE = "range"
    COLOR = "color"

    # Interactive Elements
    BUTTON = "button"
    LINK = "link"
    SUBMIT = "submit"

    # Media Elements
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    MEDIA = "media"  # Generic media type
    CANVAS = "canvas"
    SVG = "svg"  # SVG graphics

    # Layout Elements
    DIV = "div"
    SPAN = "span"
    HEADER = "header"
    FOOTER = "footer"
    NAV = "nav"
    NAVIGATION = "navigation"  # Navigation element
    SECTION = "section"
    ARTICLE = "article"
    ASIDE = "aside"
    MAIN = "main"
    DIALOG = "dialog"

    # List Elements
    LIST = "list"
    LIST_ITEM = "list_item"
    MENU = "menu"

    # Table Elements
    TABLE = "table"
    TABLE_ROW = "table_row"
    TABLE_CELL = "table_cell"
    TABLE_HEADER = "table_header"

    # Other Elements
    IFRAME = "iframe"
    FORM = "form"
    LABEL = "label"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    CODE = "code"
    PRE = "pre"
    TAB = "tab"
    TOOLBAR = "toolbar"

    # UI Components (missing but referenced)
    CARD = "card"
    MODAL = "modal"
    TOOLTIP = "tooltip"
    ALERT = "alert"
    BANNER = "banner"
    SWITCH = "switch"
    SLIDER = "slider"

    # Generic
    UNKNOWN = "unknown"
    OTHER = "other"


class TestCategory(str, Enum):
    """Unified test/QA categories - single source"""

    FUNCTIONAL = "functional"
    VALIDATION = "validation"
    ACCESSIBILITY = "accessibility"
    SECURITY = "security"
    PERFORMANCE = "performance"
    USABILITY = "usability"
    COMPATIBILITY = "compatibility"
    ERROR_HANDLING = "error_handling"
    LOCALIZATION = "localization"
    DATA_INTEGRITY = "data_integrity"
    NAVIGATION = "navigation"
    FORM_INTERACTION = "form_interaction"
    DATA_HANDLING = "data_handling"
    ERROR_SCENARIOS = "error_scenarios"
    EDGE_CASES = "edge_cases"


# Alias for backward compatibility
QACategory = TestCategory


class TestPriority(str, Enum):
    """Test priority levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestFramework(str, Enum):
    """Supported test frameworks"""

    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    CYPRESS = "cypress"
    PYTEST = "pytest"
    JEST = "jest"
    CUCUMBER = "cucumber"
    PUPPETEER = "puppeteer"


class ProfileType(str, Enum):
    """Browser profile types"""

    QA = "qa"
    DEVELOPER = "developer"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USER = "user"
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"


class StealthLevel(str, Enum):
    """Browser stealth levels"""

    OFF = "off"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


class ExtractionStrategy(str, Enum):
    """Element extraction strategies"""

    FAST = "fast"
    THOROUGH = "thorough"
    INTERACTIVE = "interactive"
    VISUAL = "visual"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"


class InteractionType(str, Enum):
    """Types of element interactions"""

    CLICK = "click"
    TYPE = "type"
    SELECT = "select"
    HOVER = "hover"
    DRAG = "drag"
    DROP = "drop"
    SCROLL = "scroll"
    FOCUS = "focus"
    BLUR = "blur"
    SUBMIT = "submit"
    CLEAR = "clear"
    UPLOAD = "upload"


class LocatorStrategy(str, Enum):
    """Element locator strategies"""

    CSS = "css"
    XPATH = "xpath"
    ID = "id"
    NAME = "name"
    CLASS = "class"
    TAG = "tag"
    TEXT = "text"
    PARTIAL_TEXT = "partial_text"
    LINK_TEXT = "link_text"
    PARTIAL_LINK_TEXT = "partial_link_text"
    ROLE = "role"
    TESTID = "testid"
    LABEL = "label"
    PLACEHOLDER = "placeholder"
    TITLE = "title"
    ALT = "alt"


class ExtractionMethod(str, Enum):
    """Methods for extracting elements"""

    DOM = "dom"
    VISUAL = "visual"
    ACCESSIBILITY = "accessibility"
    COMPUTED = "computed"
    SCREENSHOT = "screenshot"
    AI_VISION = "ai_vision"


class ConfidenceLevel(str, Enum):
    """Confidence levels for extraction/analysis"""

    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CERTAIN = "certain"


class StrategyName(str, Enum):
    """LLM prompt strategy names"""

    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    REACT = "react"
    CONSTITUTIONAL_AI = "constitutional_ai"
    SELF_CONSISTENCY = "self_consistency"
    META_PROMPTING = "meta_prompting"
    DEBATE = "debate"
    REFLEXION = "reflexion"
    SCRATCHPAD = "scratchpad"
    FEW_SHOT = "few_shot"
    ZERO_SHOT = "zero_shot"
    OPRO = "opro"
    MIXTURE_OF_EXPERTS = "mixture_of_experts"
    QUANTUM_PROMPTING = "quantum_prompting"
    REVERSE_PROMPTING = "reverse_prompting"
    EVOLUTIONARY_OPTIMIZATION = "evolutionary_optimization"
    PSYCHOLOGICAL_TRIGGERS = "psychological_triggers"
    UNIVERSAL_SELF_CONSISTENCY = "universal_self_consistency"
    PROGRAM_AIDED_LANGUAGE = "program_aided_language"
    CHAIN_OF_TABLE = "chain_of_table"
    META_COGNITIVE_FRAMEWORK = "meta_cognitive_framework"
    QA_ENGINEER_AGENT = "qa_engineer_agent"


# =============================================================================
# BROWSER CONFIGURATION MODELS
# =============================================================================


class TimingProfile(BaseModel):
    """Browser timing configuration"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    page_load_timeout: int = Field(
        30000, description="Page load timeout in ms"
    )
    script_timeout: int = Field(
        10000, description="Script execution timeout in ms"
    )
    wait_for_selector_timeout: int = Field(
        5000, description="Element wait timeout in ms"
    )
    network_idle_timeout: int = Field(
        2000, description="Network idle timeout in ms"
    )
    animation_timeout: int = Field(
        1000, description="Animation completion timeout in ms"
    )
    action_timeout: int = Field(
        5000, description="Default action timeout in ms"
    )
    screenshot_timeout: int = Field(
        3000, description="Screenshot capture timeout in ms"
    )


class StealthProfile(BaseModel):
    """Browser stealth profile configuration"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    level: StealthLevel = Field(StealthLevel.MEDIUM)
    randomize_viewport: bool = Field(True)
    randomize_user_agent: bool = Field(True)
    mask_webdriver: bool = Field(True)
    disable_automation_features: bool = Field(True)
    human_like_delays: bool = Field(True)
    min_delay: int = Field(100, description="Minimum delay in ms")
    max_delay: int = Field(2000, description="Maximum delay in ms")
    disable_web_security: bool = Field(
        False, description="Disable web security features"
    )
    disable_features: List[str] = Field(
        default_factory=lambda: ["VizDisplayCompositor"],
        description="Browser features to disable",
    )


class StealthConfig(BaseModel):
    """Complete stealth configuration with browser settings"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Core configurations
    profile: StealthProfile = Field(default_factory=StealthProfile)
    timing: TimingProfile = Field(default_factory=TimingProfile)

    # Browser display settings
    headless: bool = Field(False, description="Run browser in headless mode")
    viewport_width: int = Field(968, description="Browser viewport width")
    viewport_height: int = Field(540, description="Browser viewport height")
    viewport: Dict[str, int] = Field(
        default_factory=lambda: {"width": 968, "height": 540},
        description="Browser viewport dimensions",
    )

    # Network and headers
    headers: Dict[str, str] = Field(
        default_factory=dict, description="Custom HTTP headers"
    )
    user_agent: Optional[str] = Field(
        None, description="Custom user agent string"
    )

    # Proxy settings
    proxy_server: Optional[str] = Field(None, description="Proxy server URL")
    proxy_username: Optional[str] = Field(None, description="Proxy username")
    proxy_password: Optional[str] = Field(None, description="Proxy password")

    # Stealth behaviors
    enable_stealth: bool = Field(True, description="Enable stealth mode")
    level: StealthLevel = Field(
        StealthLevel.MEDIUM, description="Stealth level"
    )

    bypass_csp: bool = Field(
        True, description="Bypass Content Security Policy"
    )
    ignore_https_errors: bool = Field(
        True, description="Ignore HTTPS certificate errors"
    )

    # Localization
    locale: str = Field("en-US", description="Browser locale")
    timezone: str = Field("America/New_York", description="Browser timezone")

    # Advanced bypass options
    bypass_cloudflare: bool = Field(
        False, description="Bypass Cloudflare detection"
    )
    bypass_f5_networks: bool = Field(
        False, description="Bypass F5 Networks detection"
    )
    prevent_webrtc_leak: bool = Field(
        True, description="Prevent WebRTC IP leak"
    )

    # Spoofing options
    spoof_canvas_fingerprint: bool = Field(
        True, description="Spoof canvas fingerprint"
    )
    spoof_webgl: bool = Field(True, description="Spoof WebGL fingerprint")
    spoof_battery: bool = Field(True, description="Spoof battery API")
    spoof_hardware: bool = Field(
        True, description="Spoof hardware information"
    )

    # Additional bypass options
    bypass_shape_security: bool = Field(
        False, description="Bypass Shape Security detection"
    )
    bypass_datadome: bool = Field(
        False, description="Bypass DataDome detection"
    )
    bypass_kasada: bool = Field(False, description="Bypass Kasada detection")

    # Human behavior simulation
    enable_human_delays: bool = Field(
        True, description="Enable human-like delays"
    )
    enable_human_mouse: bool = Field(
        True, description="Enable human-like mouse movements"
    )
    enable_human_scrolling: bool = Field(
        True, description="Enable human-like scrolling"
    )
    enable_human_typing: bool = Field(
        True, description="Enable human-like typing"
    )
    enable_micro_behaviors: bool = Field(
        False, description="Enable micro-behaviors"
    )
    use_bspline_mouse: bool = Field(
        False, description="Use B-spline for mouse movements"
    )
    use_lognormal_delays: bool = Field(
        False, description="Use lognormal distribution for delays"
    )
    human_delay_range: Tuple[int, int] = Field(
        (100, 2000), description="Human delay range in ms"
    )
    typing_delay_range: Tuple[int, int] = Field(
        (50, 150), description="Typing delay range in ms"
    )

    # Timeout settings
    default_timeout: int = Field(
        30000, description="Default timeout for operations"
    )

    # Browser launch args
    args: List[str] = Field(
        default_factory=list, description="Additional browser launch arguments"
    )
    ignore_default_args: List[str] = Field(
        default_factory=list, description="Default args to ignore"
    )

    # Performance settings
    slow_mo: int = Field(0, description="Slow down operations by specified ms")
    timeout: int = Field(30000, description="Default timeout for operations")

    # Shadow DOM extraction settings
    enable_shadow_dom_extraction: bool = Field(
        True, description="Enable shadow DOM element extraction"
    )
    shadow_dom_max_depth: int = Field(
        5, description="Maximum shadow DOM traversal depth"
    )
    shadow_dom_element_limit: int = Field(
        100, description="Maximum elements per shadow root"
    )


# ==================== DATA MODELS ====================


class BoundingBox(BaseModel):
    """Element bounding box"""

    x: float
    y: float
    width: float
    height: float

    def is_visible(self) -> bool:
        return self.width > 0 and self.height > 0


class ComputedStyle(BaseModel):
    """Computed CSS styles"""

    display: Optional[str] = None
    visibility: Optional[str] = None
    opacity: Optional[str] = None
    position: Optional[str] = None
    zIndex: Optional[str] = None
    backgroundColor: Optional[str] = None
    color: Optional[str] = None
    fontSize: Optional[str] = None

    def is_visible(self) -> bool:
        return (
            self.display != "none"
            and self.visibility != "hidden"
            and self.opacity != "0"
        )


class ElementSelector(BaseModel):
    """Element selector strategy"""

    strategy: LocatorStrategy
    value: str
    score: float = 0.5
    is_unique: bool = False


class Element(BaseModel):
    """Unified element data structure - single source of truth"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Core identification (required)
    id: str = Field(description="Unique element identifier")
    tag_name: str = Field(description="HTML tag name")
    element_type: ElementType = Field(
        default=ElementType.UNKNOWN, description="Element type classification"
    )

    # Content
    text: Optional[str] = Field(default=None, description="Text content")
    inner_html: Optional[str] = Field(default=None, description="Inner HTML")
    outer_html: Optional[str] = Field(default=None, description="Outer HTML")
    value: Optional[str] = Field(default=None, description="Value attribute")

    # Key attributes
    name: Optional[str] = Field(default=None, description="Name attribute")
    classes: List[str] = Field(default_factory=list, description="CSS classes")
    href: Optional[str] = Field(default=None, description="Href for links")
    src: Optional[str] = Field(
        default=None, description="Source for images/scripts"
    )
    alt: Optional[str] = Field(default=None, description="Alt text")
    title: Optional[str] = Field(default=None, description="Title attribute")
    placeholder: Optional[str] = Field(
        default=None, description="Placeholder text"
    )
    type: Optional[str] = Field(default=None, description="Type attribute")
    role: Optional[str] = Field(default=None, description="ARIA role")
    aria_label: Optional[str] = Field(default=None, description="ARIA label")
    data_testid: Optional[str] = Field(default=None, description="Test ID")
    attributes: Dict[str, Any] = Field(
        default_factory=dict, description="All attributes"
    )

    # State
    is_visible: bool = Field(default=True, description="Visibility state")
    is_enabled: bool = Field(default=True, description="Enabled state")
    is_selected: bool = Field(default=False, description="Selected state")
    is_checked: bool = Field(default=False, description="Checked state")
    is_focused: bool = Field(default=False, description="Focus state")
    is_required: bool = Field(default=False, description="Required field")
    is_readonly: bool = Field(default=False, description="Read-only state")

    # Interaction capabilities
    is_clickable: bool = Field(default=False, description="Can be clicked")
    is_editable: bool = Field(default=False, description="Can be edited")
    interaction_types: List[InteractionType] = Field(
        default_factory=list, description="Possible interactions"
    )

    # Position and style
    bounding_box: Optional[BoundingBox] = Field(
        default=None, description="Element position"
    )
    computed_style: Optional[ComputedStyle] = Field(
        default=None, description="Computed styles"
    )

    # Selectors
    selector: Optional[str] = Field(
        default=None, description="Primary selector"
    )
    xpath: Optional[str] = Field(default=None, description="XPath selector")
    css_selector: Optional[str] = Field(
        default=None, description="CSS selector"
    )
    full_xpath: Optional[str] = Field(
        default=None, description="Full XPath from root"
    )
    selectors: List[ElementSelector] = Field(
        default_factory=list, description="All selector strategies"
    )

    # Hierarchy
    parent_id: Optional[str] = Field(
        default=None, description="Parent element ID"
    )
    children_ids: List[str] = Field(
        default_factory=list, description="Child element IDs"
    )
    depth: int = Field(default=0, description="DOM tree depth")
    shadow_dom_path: List[str] = Field(
        default_factory=list, description="Shadow DOM path"
    )

    # Classification and scoring
    confidence: float = Field(default=0.5, description="Extraction confidence")
    importance_score: float = Field(
        default=0.5, description="Element importance"
    )

    # Metadata
    extraction_method: Optional[ExtractionMethod] = Field(
        default=None, description="How element was extracted"
    )
    extraction_timestamp: Optional[float] = Field(
        default=None, description="When element was extracted"
    )
    is_shadow_element: bool = Field(
        default=False, description="Is in shadow DOM"
    )
    is_iframe_element: bool = Field(default=False, description="Is in iframe")

    # Validation
    is_valid: bool = Field(default=True, description="Validation state")
    validation_errors: List[str] = Field(
        default_factory=list, description="Validation errors"
    )

    # AI/LLM fields
    ai_description: Optional[str] = Field(
        default=None, description="AI-generated description"
    )
    ai_confidence: Optional[float] = Field(
        default=None, description="AI confidence score"
    )
    ai_suggested_actions: List[str] = Field(
        default_factory=list, description="AI-suggested actions"
    )

    def get_best_selector(self) -> Optional[ElementSelector]:
        """Get the best selector based on score"""
        if not self.selectors:
            return None
        return max(self.selectors, key=lambda s: s.score)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump(exclude_none=True)


# ExtractedElement merged into Element above - single source of truth


class ScreenshotData(BaseModel):
    """Screenshot information"""

    format: str = "png"
    width: int
    height: int
    data: str  # Base64 encoded
    timestamp: float
    url: Optional[str] = None
    highlighted_elements: List[str] = Field(default_factory=list)
    annotations: Dict[str, Any] = Field(default_factory=dict)


class ElementContext(BaseModel):
    """Context information for an element"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    parent_hierarchy: List[str] = Field(default_factory=list)
    siblings_count: int = 0
    position_in_parent: int = 0
    visual_prominence: float = 0.0
    interaction_likelihood: float = 0.0
    semantic_role: Optional[str] = None
    accessibility_score: float = 0.0


class EnrichedElement(BaseModel):
    """Element enriched with LLM analysis"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    base_element: Dict[str, Any] = Field(default_factory=dict)
    llm_analysis: Dict[str, Any] = Field(default_factory=dict)
    context: ElementContext = Field(default_factory=ElementContext)
    test_categories: List[TestCategory] = Field(default_factory=list)
    test_scenarios: List[str] = Field(default_factory=list)
    confidence_score: float = 0.0
    extraction_timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )


class PageAnalysis(BaseModel):
    """Comprehensive page analysis result"""

    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    lang: Optional[str] = None
    viewport: Optional[Dict[str, Any]] = None

    # Element counts
    total_elements: int = 0
    interactive_elements: int = 0
    form_elements: int = 0
    navigation_elements: int = 0
    element_count: int = 0  # Legacy field for compatibility

    # Content analysis
    has_forms: bool = False
    has_tables: bool = False
    has_media: bool = False
    has_iframes: bool = False
    has_shadow_dom: bool = False

    # LLM Analysis
    enriched_elements: List[Any] = Field(default_factory=list)
    page_type: Optional[str] = None
    framework_detected: Optional[str] = None
    llm_insights: Optional[Dict[str, Any]] = None

    # Performance metrics
    dom_ready_time: Optional[float] = None
    load_time: Optional[float] = None
    extraction_time: float = 0.0
    llm_processing_time: float = 0.0

    # Accessibility
    has_aria: bool = False
    has_semantic_html: bool = False
    accessibility_score: Optional[float] = None


class InteractionResult(BaseModel):
    """Result of element interaction"""

    success: bool
    action: InteractionType
    element_selector: str
    timestamp: float

    # Outcomes
    page_changed: bool = False
    new_elements: List[str] = Field(default_factory=list)
    removed_elements: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)

    # Screenshots
    before_screenshot: Optional[ScreenshotData] = None
    after_screenshot: Optional[ScreenshotData] = None


class ValidationResult(BaseModel):
    """Element validation result"""

    element_selector: str
    is_valid: bool
    validation_type: str

    # Details
    expected: Any = None
    actual: Any = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class GherkinStep(BaseModel):
    """Gherkin test step"""

    keyword: str  # Given, When, Then, And, But
    text: str


class TestScenario(BaseModel):
    """Test scenario definition"""

    name: str
    description: Optional[str] = None
    category: TestCategory
    priority: TestPriority = TestPriority.MEDIUM

    # Steps - supports both Gherkin and dict formats
    preconditions: List[str] = Field(default_factory=list)
    steps: List[Union[GherkinStep, Dict[str, Any]]] = Field(
        default_factory=list
    )
    expected_results: List[str] = Field(default_factory=list)

    # Elements involved
    target_elements: List[str] = Field(default_factory=list)

    # Validation
    validations: List[ValidationResult] = Field(default_factory=list)

    # Metadata
    created_at: float = Field(default_factory=lambda: time.time())
    framework: Optional[TestFramework] = None
    tags: List[str] = Field(default_factory=list)

    # Additional fields for compatibility
    test_data: Optional[Dict[str, Any]] = None
    confidence_score: float = 0.95
    assertions: List[str] = Field(default_factory=list)


class TestSuite(BaseModel):
    """Test suite containing multiple scenarios"""

    feature_name: str
    feature_description: str = ""
    url: str
    scenarios: List[TestScenario] = Field(default_factory=list)
    total_scenarios: int = 0
    generation_time: float = 0.0

    def to_gherkin(self) -> str:
        """Convert to Gherkin feature file format"""
        lines = []
        lines.append(f"Feature: {self.feature_name}")
        if self.feature_description:
            lines.append(f"  {self.feature_description}")
        lines.append("")

        for scenario in self.scenarios:
            lines.append(f"  Scenario: {scenario.name}")
            if scenario.description:
                lines.append(f"    {scenario.description}")
            for step in scenario.steps:
                if isinstance(step, GherkinStep):
                    lines.append(f"    {step.keyword} {step.text}")
                elif (
                    isinstance(step, dict)
                    and "keyword" in step
                    and "text" in step
                ):
                    lines.append(f"    {step['keyword']} {step['text']}")
            lines.append("")

        return "\n".join(lines)


class TestGenerationContract(BaseModel):
    """Contract for test generation"""

    url: str
    frameworks: List[str] = Field(default_factory=lambda: ["playwright"])
    categories: List[str] = Field(default_factory=lambda: ["functional"])
    max_scenarios: int = 10
    max_elements: int = 10
    include_code: bool = False


class TestGenerationResult(BaseModel):
    """Result of test generation"""

    url: str
    test_suite: TestSuite
    page_analysis: PageAnalysis
    total_scenarios: int = 0
    categories_covered: List[str] = Field(default_factory=list)
    generation_time: float = 0.0
    llm_processing_time: float = 0.0
    code_snippets: Dict[str, str] = Field(default_factory=dict)


# Configuration classes


class ExtractionConfig(BaseModel):
    """Configuration for browser-based extraction"""

    # Browser settings
    headless: bool = False
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: Optional[str] = None

    # Extraction settings
    enable_shadow_dom: bool = True
    enable_iframe_traversal: bool = True
    enable_stealth: bool = True
    wait_for_network_idle: bool = True
    timeout: int = 30000

    # Element filtering
    filter_invisible: bool = True
    filter_duplicates: bool = True
    min_element_size: int = 5
    max_elements: int = 1000
    min_confidence: float = 0.0

    # Screenshots
    capture_screenshots: bool = False
    screenshot_format: str = "png"
    screenshot_quality: int = 80
    screenshot_full_page: bool = False
    highlight_elements: bool = False
    highlight_color: str = "red"
    highlight_width: int = 2

    # Caching
    enable_caching: bool = True
    cache_ttl: int = 3600

    # Performance
    parallel_extraction: bool = False
    batch_size: int = 10

    # QA Mode settings
    qa_mode: bool = False
    qa_priority_tags: List[str] = Field(
        default_factory=lambda: [
            "button",
            "input",
            "select",
            "textarea",
            "a",
            "form",
        ]
    )
    qa_interaction_indicators: List[str] = Field(
        default_factory=lambda: ["click", "submit", "change", "focus", "blur"]
    )
    qa_min_interaction_score: float = 0.3
    qa_include_disabled: bool = True
    qa_include_hidden_toggles: bool = True

    # Extraction strategies
    extraction_strategy: ExtractionStrategy = ExtractionStrategy.THOROUGH
    fallback_strategies: List[ExtractionStrategy] = Field(default_factory=list)


# DOMExtractionConfig removed - use ExtractionConfig directly


class ExtractionResult(BaseModel):
    """Result from browser extraction"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    url: str
    success: bool
    elements: List[Element] = Field(default_factory=list)
    page_title: Optional[str] = None
    page_description: Optional[str] = None
    page_analysis: Optional[PageAnalysis] = None

    # Timing
    extraction_time: float = 0.0
    network_time: float = 0.0

    # Statistics
    total_elements_found: int = 0
    elements_filtered: int = 0
    shadow_dom_elements: int = 0
    iframe_elements: int = 0

    # Screenshots
    screenshots: List[ScreenshotData] = Field(default_factory=list)

    # Metadata
    browser_version: Optional[str] = None
    extraction_strategy: Optional[ExtractionStrategy] = None
    config: Optional[Dict[str, Any]] = None

    # Errors
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    # Additional data
    statistics: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def save_screenshots(self, directory: Path) -> List[Path]:
        """Save screenshots to directory"""
        import base64

        saved_paths = []

        directory.mkdir(parents=True, exist_ok=True)

        for i, screenshot in enumerate(self.screenshots):
            filename = f"screenshot_{i + 1}.{screenshot.format}"
            filepath = directory / filename

            # Decode and save
            image_data = base64.b64decode(screenshot.data)
            filepath.write_bytes(image_data)
            saved_paths.append(filepath)

        return saved_paths


class CrawlResult(BaseModel):
    """Crawl result for multi-page extraction"""

    start_url: str = Field(..., description="Starting URL for crawl")
    pages_visited: List[str] = Field(
        default_factory=list, description="URLs visited during crawl"
    )
    extraction_results: List[ExtractionResult] = Field(
        default_factory=list, description="Extraction results for each page"
    )
    total_elements: int = Field(
        default=0,
        ge=0,
        description="Total elements extracted across all pages",
    )
    crawl_time: float = Field(
        ..., ge=0.0, description="Total crawl time in seconds"
    )
    max_depth_reached: int = Field(
        default=0, ge=0, description="Maximum depth reached during crawl"
    )
    errors: List[str] = Field(
        default_factory=list, description="Errors encountered during crawl"
    )


# ==================== EXCEPTIONS ====================


class BrowserError(Exception):
    """Base exception for browser-related errors"""

    pass


class NavigationError(BrowserError):
    """Navigation-specific errors"""

    pass


class ExtractionError(BrowserError):
    """Element extraction errors"""

    pass


class TimeoutError(BrowserError):
    """Timeout-related errors"""

    pass


# ==================== SHARED UTILITIES ====================


class ElementSelectorUtils:
    """Shared utilities for element selector generation"""

    @staticmethod
    def determine_element_type(
        tag_name: str,
        elem_type: Optional[str] = None,
        role: Optional[str] = None,
        input_type: Optional[str] = None,
    ) -> ElementType:
        """Determine element type from tag and attributes"""
        tag_lower = tag_name.lower()

        # Priority 1: Explicit type mapping
        if elem_type:
            type_map = {
                "button": ElementType.BUTTON,
                "link": ElementType.LINK,
                "input": ElementType.INPUT,
                "text": ElementType.TEXT_INPUT,  # Use TEXT_INPUT
                "image": ElementType.IMAGE,
                "video": ElementType.VIDEO,
                "form": ElementType.FORM,
                "table": ElementType.TABLE,
                "list": ElementType.LIST,
                "navigation": ElementType.NAVIGATION,
                "heading": ElementType.HEADING,
                "select": ElementType.SELECT,
                "checkbox": ElementType.CHECKBOX,
                "radio": ElementType.RADIO,
                "textarea": ElementType.TEXTAREA,
                "iframe": ElementType.IFRAME,
                "canvas": ElementType.CANVAS,
                "svg": ElementType.SVG,
                "dialog": ElementType.DIALOG,
                "menu": ElementType.MENU,
                "tab": ElementType.TAB,
                "card": ElementType.CARD,
                "modal": ElementType.MODAL,
                "tooltip": ElementType.TOOLTIP,
                "alert": ElementType.ALERT,
                "banner": ElementType.BANNER,
                "search": ElementType.SEARCH,
                "switch": ElementType.SWITCH,
                "slider": ElementType.SLIDER,
                "code": ElementType.CODE,
            }
            if elem_type.lower() in type_map:
                return type_map[elem_type.lower()]

        # Priority 2: Role-based detection
        if role:
            role_map = {
                "button": ElementType.BUTTON,
                "link": ElementType.LINK,
                "navigation": ElementType.NAVIGATION,
                "heading": ElementType.HEADING,
                "img": ElementType.IMAGE,
                "form": ElementType.FORM,
                "search": ElementType.SEARCH,
                "alert": ElementType.ALERT,
                "dialog": ElementType.DIALOG,
                "menu": ElementType.MENU,
                "menuitem": ElementType.MENU,
                "tab": ElementType.TAB,
                "tabpanel": ElementType.TAB,
                "tooltip": ElementType.TOOLTIP,
                "banner": ElementType.BANNER,
                "switch": ElementType.SWITCH,
                "slider": ElementType.SLIDER,
            }
            if role.lower() in role_map:
                return role_map[role.lower()]

        # Priority 3: Tag-based detection
        tag_map = {
            "a": ElementType.LINK,
            "button": ElementType.BUTTON,
            "input": ElementType.INPUT,
            "textarea": ElementType.TEXTAREA,
            "select": ElementType.SELECT,
            "img": ElementType.IMAGE,
            "video": ElementType.VIDEO,
            "audio": ElementType.MEDIA,
            "form": ElementType.FORM,
            "table": ElementType.TABLE,
            "ul": ElementType.LIST,
            "ol": ElementType.LIST,
            "nav": ElementType.NAVIGATION,
            "h1": ElementType.HEADING,
            "h2": ElementType.HEADING,
            "h3": ElementType.HEADING,
            "h4": ElementType.HEADING,
            "h5": ElementType.HEADING,
            "h6": ElementType.HEADING,
            "iframe": ElementType.IFRAME,
            "canvas": ElementType.CANVAS,
            "svg": ElementType.SVG,
            "dialog": ElementType.DIALOG,
            "code": ElementType.CODE,
            "pre": ElementType.CODE,
        }

        if tag_lower in tag_map:
            element_type = tag_map[tag_lower]

            # Special handling for input elements
            if tag_lower == "input" and input_type:
                input_type_map = {
                    "checkbox": ElementType.CHECKBOX,
                    "radio": ElementType.RADIO,
                    "button": ElementType.BUTTON,
                    "submit": ElementType.BUTTON,
                    "reset": ElementType.BUTTON,
                    "search": ElementType.SEARCH,
                    "range": ElementType.SLIDER,
                }
                if input_type.lower() in input_type_map:
                    return input_type_map[input_type.lower()]

            return element_type

        # Default to OTHER
        return ElementType.OTHER

    @staticmethod
    def generate_xpath(
        elem_id: Optional[str] = None,
        elem_classes: Optional[List[str]] = None,
        tag_name: str = "div",
        text_content: Optional[str] = None,
    ) -> str:
        """Generate XPath selector for element"""
        if elem_id:
            return f"//{tag_name}[@id='{elem_id}']"
        elif elem_classes:
            class_condition = " and ".join(
                [f"contains(@class, '{cls}')" for cls in elem_classes[:2]]
            )
            return f"//{tag_name}[{class_condition}]"
        elif text_content and len(text_content) < 50:
            return f"//{tag_name}[contains(text(), '{text_content[:30]}')]"
        else:
            return f"//{tag_name}"

    @staticmethod
    def generate_css_selector(
        elem_id: Optional[str] = None,
        elem_classes: Optional[List[str]] = None,
        tag_name: str = "div",
    ) -> str:
        """Generate CSS selector for element"""
        if elem_id:
            return f"#{elem_id}"
        elif elem_classes:
            return f"{tag_name}.{'.'.join(elem_classes[:2])}"
        else:
            return tag_name


# Shared Utilities and Constants


# Scoring Constants
CONFIDENCE_BASE = 0.5
CONFIDENCE_INCREMENT = 0.1
SELECTOR_SCORE_ID = 1.0
SELECTOR_SCORE_DATA_TESTID = 0.9
SELECTOR_SCORE_ARIA_LABEL = 0.8
SELECTOR_SCORE_CLASS = 0.7
SELECTOR_SCORE_TEXT = 0.6
SELECTOR_SCORE_TAG = 0.5
SELECTOR_SCORE_XPATH = 0.4
SELECTOR_SCORE_POSITION = 0.3

# Element Interaction Mappings
ELEMENT_INTERACTIONS = {
    ElementType.BUTTON: [
        InteractionType.CLICK,
        InteractionType.HOVER,
        InteractionType.FOCUS,
    ],
    ElementType.LINK: [InteractionType.CLICK, InteractionType.HOVER],
    ElementType.INPUT: [
        InteractionType.TYPE,
        InteractionType.CLEAR,
        InteractionType.FOCUS,
    ],
    ElementType.TEXTAREA: [
        InteractionType.TYPE,
        InteractionType.CLEAR,
        InteractionType.FOCUS,
    ],
    ElementType.SELECT: [InteractionType.SELECT, InteractionType.FOCUS],
    ElementType.CHECKBOX: [InteractionType.CLICK, InteractionType.FOCUS],
    ElementType.RADIO: [InteractionType.CLICK, InteractionType.FOCUS],
    ElementType.IMAGE: [InteractionType.HOVER],
    ElementType.VIDEO: [InteractionType.CLICK, InteractionType.HOVER],
    ElementType.FORM: [InteractionType.SUBMIT, InteractionType.FOCUS],
    ElementType.HEADING: [InteractionType.HOVER],
    ElementType.TABLE: [InteractionType.HOVER],
    ElementType.LIST: [InteractionType.HOVER],
    ElementType.NAV: [InteractionType.HOVER],
    ElementType.DIV: [InteractionType.HOVER],
    ElementType.SPAN: [InteractionType.HOVER],
    ElementType.IFRAME: [InteractionType.FOCUS, InteractionType.SCROLL],
    ElementType.LABEL: [InteractionType.CLICK, InteractionType.HOVER],
    ElementType.MEDIA: [InteractionType.CLICK, InteractionType.HOVER],
    ElementType.NAVIGATION: [InteractionType.HOVER],
    ElementType.SVG: [InteractionType.HOVER],
    ElementType.OTHER: [InteractionType.HOVER],
}


def retry_with_backoff(retries=3, backoff_factor=2):
    """Decorator for retry with exponential backoff"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt == retries - 1:
                        raise
                    wait_time = backoff_factor**attempt
                    time.sleep(wait_time)
            return None

        return wrapper

    return decorator


class ThreadSafeCache:
    """Thread-safe cache implementation"""

    def __init__(self, max_size=1000):
        self._cache = {}
        self._lock = Lock()
        self._max_size = max_size
        self._access_count = {}

    def get(self, key):
        with self._lock:
            if key in self._cache:
                self._access_count[key] = self._access_count.get(key, 0) + 1
                return self._cache[key]
            return None

    def set(self, key, value):
        with self._lock:
            if len(self._cache) >= self._max_size:
                # Remove least accessed item
                if self._access_count:
                    min_key = min(
                        self._access_count, key=self._access_count.get
                    )
                    del self._cache[min_key]
                    del self._access_count[min_key]
            self._cache[key] = value
            self._access_count[key] = 1

    def clear(self):
        with self._lock:
            self._cache.clear()
            self._access_count.clear()


def memory_cleanup():
    """Force garbage collection and memory cleanup"""
    gc.collect()
    # Force collection of all generations
    for _ in range(3):
        gc.collect(2)


def remove_nulls(obj, remove_empty=True):
    """
    Recursively remove null values from dictionaries and lists.

    Args:
        obj: The object to clean (dict, list, or any value)
        remove_empty: Also remove empty lists and dicts

    Returns:
        Cleaned object without null values
    """
    if isinstance(obj, dict):
        # Process dictionary
        cleaned = {}
        for key, value in obj.items():
            # Recursively clean the value
            cleaned_value = remove_nulls(value, remove_empty)

            # Skip null values
            if cleaned_value is None:
                continue

            # Skip empty collections if requested
            if remove_empty:
                if isinstance(cleaned_value, (dict, list)) and len(cleaned_value) == 0:
                    continue

            cleaned[key] = cleaned_value
        return cleaned

    elif isinstance(obj, list):
        # Process list
        cleaned = []
        for item in obj:
            cleaned_item = remove_nulls(item, remove_empty)
            # Keep non-null items
            if cleaned_item is not None:
                cleaned.append(cleaned_item)
        return cleaned

    else:
        # Return the value as-is
        return obj


def clean_for_llm(data):
    """
    Clean data structure for LLM processing.
    Removes nulls, empty collections, and converts Pydantic models.

    Args:
        data: Data to clean (can be Pydantic model, dict, list, etc.)

    Returns:
        Cleaned data optimized for LLM processing
    """
    # Convert Pydantic models to dict first
    if hasattr(data, 'model_dump'):
        data = data.model_dump()
    elif hasattr(data, 'dict'):  # Fallback for older Pydantic
        data = data.dict()

    # Remove nulls and empty collections
    return remove_nulls(data, remove_empty=True)


# Interactive Element Classification
INTERACTIVE_TAGS = {
    "button",
    "a",
    "input",
    "select",
    "textarea",
    "label",
    "option",
}
INTERACTIVE_ROLES = {
    "button",
    "link",
    "checkbox",
    "radio",
    "textbox",
    "combobox",
    "listbox",
}
INTERACTIVE_ELEMENT_TYPES = {
    ElementType.BUTTON,
    ElementType.LINK,
    ElementType.INPUT,
    ElementType.SELECT,
    ElementType.TEXTAREA,
    ElementType.CHECKBOX,
    ElementType.RADIO,
}
INTERACTIVE_ATTRIBUTES = [
    "onclick",
    "href",
    "ng-click",
    "@click",
    "v-on:click",
]


class ElementClassifier:
    """Utilities for classifying elements"""

    @staticmethod
    def is_interactive(element) -> bool:
        """
        Determine if an element is interactive

        Args:
            element: Element to check

        Returns:
            True if element is interactive
        """
        # Skip null or invalid elements
        if not element or not hasattr(element, "tag_name"):
            return False

        # Check by tag name
        if element.tag_name.lower() in INTERACTIVE_TAGS:
            return True

        # Check by element type
        if (
            hasattr(element, "element_type")
            and element.element_type in INTERACTIVE_ELEMENT_TYPES
        ):
            return True

        # Check by attributes (role, onclick, href, etc.)
        if hasattr(element, "attributes"):
            attrs = element.attributes or {}
            if attrs.get("role") in INTERACTIVE_ROLES:
                return True
            if any(attrs.get(attr) for attr in INTERACTIVE_ATTRIBUTES):
                return True
            if attrs.get("tabindex", "-1") != "-1":
                return True

        # Check by clickable/editable flags
        if hasattr(element, "is_clickable") and element.is_clickable:
            return True
        if hasattr(element, "is_editable") and element.is_editable:
            return True

        return False

    @staticmethod
    def get_functional_purpose(element) -> str:
        """
        Determine the functional purpose of an element

        Args:
            element: Element to analyze

        Returns:
            Functional purpose string
        """
        tag = element.tag_name.lower() if hasattr(element, "tag_name") else ""
        elem_type = getattr(element, "element_type", None)

        if tag == "button" or elem_type == ElementType.BUTTON:
            return "trigger_action"
        elif tag == "a" or elem_type == ElementType.LINK:
            return "navigate"
        elif tag in ["input", "textarea"] or elem_type in [
            ElementType.INPUT,
            ElementType.TEXTAREA,
        ]:
            return "input_data"
        elif tag == "select" or elem_type == ElementType.SELECT:
            return "select_option"
        elif elem_type in [ElementType.CHECKBOX, ElementType.RADIO]:
            return "toggle_option"
        elif tag == "form" or elem_type == ElementType.FORM:
            return "submit_form"
        else:
            return "unknown"


class ElementPrioritizer:
    """Utilities for prioritizing elements"""

    @staticmethod
    def prioritize_elements(elements: List, max_count: int) -> List:
        """
        Prioritize elements for processing when there are too many
        Priority: forms/inputs > buttons > links > others

        Args:
            elements: List of elements
            max_count: Maximum number to return

        Returns:
            Prioritized list of elements limited to max_count
        """
        if len(elements) <= max_count:
            return elements

        # Categorize elements by priority
        forms_inputs = []
        buttons = []
        links = []
        others = []

        for elem in elements:
            tag = elem.tag_name.lower() if hasattr(elem, "tag_name") else ""
            elem_type = getattr(elem, "element_type", None)

            if tag in ["input", "textarea", "select"] or elem_type in [
                ElementType.INPUT,
                ElementType.TEXTAREA,
                ElementType.SELECT,
            ]:
                forms_inputs.append(elem)
            elif tag == "button" or elem_type == ElementType.BUTTON:
                buttons.append(elem)
            elif tag == "a" or elem_type == ElementType.LINK:
                links.append(elem)
            else:
                others.append(elem)

        # Build prioritized list
        prioritized = []

        # Add forms/inputs first (most important for testing)
        prioritized.extend(forms_inputs[:max_count])

        # Add buttons if we have room
        remaining = max_count - len(prioritized)
        if remaining > 0:
            prioritized.extend(buttons[:remaining])

        # Add links if we still have room
        remaining = max_count - len(prioritized)
        if remaining > 0:
            prioritized.extend(links[:remaining])

        # Add others if we still have room
        remaining = max_count - len(prioritized)
        if remaining > 0:
            prioritized.extend(others[:remaining])

        return prioritized[:max_count]


class ElementSerializer:
    """Utilities for serializing elements"""

    @staticmethod
    def element_to_dict(element) -> Dict[str, Any]:
        """
        Convert an Element to dictionary format

        Args:
            element: Element to convert

        Returns:
            Dictionary representation
        """
        if hasattr(element, "model_dump"):
            # Pydantic v2 model
            return element.model_dump()
        elif hasattr(element, "dict"):
            # Pydantic v1 model
            return element.dict()
        elif hasattr(element, "__dict__"):
            # Regular object
            result = element.__dict__.copy()
            # Convert enums to values
            if "element_type" in result and hasattr(
                result["element_type"], "value"
            ):
                result["element_type"] = result["element_type"].value
            return result
        else:
            # Create minimal dict representation
            return {
                "tag_name": getattr(element, "tag_name", "unknown"),
                "element_type": getattr(element, "element_type", None),
                "attributes": getattr(element, "attributes", {}),
                "text": getattr(element, "text", ""),
                "xpath": getattr(element, "xpath", ""),
                "selector": getattr(element, "selector", ""),
                "is_clickable": getattr(element, "is_clickable", False),
                "is_editable": getattr(element, "is_editable", False),
                "is_visible": getattr(element, "is_visible", True),
            }

    @staticmethod
    def element_summary(element) -> Dict[str, Any]:
        """
        Create a summary of element for analysis

        Args:
            element: Element to summarize

        Returns:
            Summary dictionary
        """
        return {
            "tag": (
                element.tag_name if hasattr(element, "tag_name") else "unknown"
            ),
            "type": (
                element.element_type.value
                if hasattr(element, "element_type") and element.element_type
                else None
            ),
            "text": (
                element.text[:50]
                if hasattr(element, "text") and element.text
                else None
            ),
            "interactive": ElementClassifier.is_interactive(element),
        }


# Test Generation Utilities
class CodeExtractor:
    """Utilities for extracting code from LLM responses"""

    @staticmethod
    def extract_code_from_response(
        response: str, language: Optional[str] = None
    ) -> str:
        """
        Extract code from LLM response

        Args:
            response: LLM response text
            language: Optional language hint (python, javascript, etc.)

        Returns:
            Extracted code or empty string
        """
        import re

        # Try to find code block with language marker
        if language:
            pattern = rf"```{language}\n(.*?)```"
            match = re.search(pattern, response, re.DOTALL)
            if match:
                return match.group(1).strip()

        # Try generic code block
        code_match = re.search(
            r"```(?:python|javascript|typescript)?\n(.*?)```",
            response,
            re.DOTALL,
        )
        if code_match:
            return code_match.group(1).strip()

        # Try to find function/test definition
        func_match = re.search(
            r"((?:async\s+)?(?:def|function|test|describe).*?(?=\n\n|\Z))",
            response,
            re.DOTALL,
        )
        if func_match:
            return func_match.group(1).strip()

        # Return as-is if it looks like code
        code_keywords = [
            "async",
            "def",
            "function",
            "test",
            "describe",
            "it(",
            "expect",
        ]
        if any(keyword in response for keyword in code_keywords):
            return response.strip()

        return ""


class TestRelevanceAnalyzer:
    """Utilities for analyzing test relevance"""

    @staticmethod
    def get_relevant_elements(
        scenario: Any, elements: List[Any], max_relevant: int = 10
    ) -> List[Any]:
        """
        Get elements relevant to a test scenario

        Args:
            scenario: Test scenario
            elements: List of elements
            max_relevant: Maximum number of relevant elements to return

        Returns:
            List of relevant elements
        """
        if not elements:
            return []

        # Build scenario context
        scenario_text = ""
        if hasattr(scenario, "name"):
            scenario_text += f"{scenario.name} "
        if hasattr(scenario, "description"):
            scenario_text += f"{scenario.description} "
        scenario_text = scenario_text.lower()

        scored_elements = []

        for element in elements:
            score = 0.0

            # Check text relevance
            elem_text = ""
            if hasattr(element, "base_element"):
                elem_text = str(element.base_element.get("text", "")).lower()
            elif hasattr(element, "text"):
                elem_text = str(element.text).lower()

            if elem_text and elem_text[:50] in scenario_text:
                score += 0.5

            # Check type relevance
            elem_type = ""
            if hasattr(element, "base_element"):
                elem_type = str(
                    element.base_element.get("element_type", "")
                ).lower()
            elif hasattr(element, "element_type"):
                elem_type = str(element.element_type).lower()

            if elem_type and elem_type in scenario_text:
                score += 0.3

            # Check interaction likelihood
            if hasattr(element, "context") and hasattr(
                element.context, "interaction_likelihood"
            ):
                if element.context.interaction_likelihood > 0.7:
                    score += 0.2

            if score > 0:
                scored_elements.append((score, element))

        # Sort by score and return top N
        scored_elements.sort(key=lambda x: x[0], reverse=True)
        return [elem for _, elem in scored_elements[:max_relevant]]


class ScenarioTemplates:
    """Templates for generating basic test scenarios"""

    @staticmethod
    def get_basic_scenario(
        element: Any, url: str, index: int = 0
    ) -> Dict[str, Any]:
        """
        Get basic scenario template for an element

        Args:
            element: Element to create scenario for
            url: Page URL
            index: Scenario index

        Returns:
            Scenario template dictionary
        """
        from .data_types import TestCategory, TestPriority

        tag = element.tag_name.lower() if hasattr(element, "tag_name") else ""
        elem_type = ElementClassifier.get_functional_purpose(element)

        # Button scenario
        if tag == "button" or elem_type == "trigger_action":
            return {
                "name": f"Test Button Click {index + 1}",
                "description": "Verify button functionality",
                "category": TestCategory.FUNCTIONAL,
                "priority": TestPriority.HIGH,
                "steps": [
                    {"keyword": "Given", "text": f"the user is on {url}"},
                    {"keyword": "When", "text": "the user clicks the button"},
                    {
                        "keyword": "Then",
                        "text": "the expected action should occur",
                    },
                ],
            }

        # Link scenario
        elif tag == "a" or elem_type == "navigate":
            return {
                "name": f"Test Link Navigation {index + 1}",
                "description": "Verify link navigation",
                "category": TestCategory.FUNCTIONAL,
                "priority": TestPriority.HIGH,
                "steps": [
                    {"keyword": "Given", "text": f"the user is on {url}"},
                    {"keyword": "When", "text": "the user clicks the link"},
                    {
                        "keyword": "Then",
                        "text": "the browser should navigate to the correct page",
                    },
                ],
            }

        # Input scenario
        elif tag in ["input", "textarea"] or elem_type == "input_data":
            return {
                "name": f"Test Input Field {index + 1}",
                "description": "Verify input field functionality",
                "category": TestCategory.FUNCTIONAL,
                "priority": TestPriority.MEDIUM,
                "steps": [
                    {"keyword": "Given", "text": f"the user is on {url}"},
                    {
                        "keyword": "When",
                        "text": "the user enters text in the input field",
                    },
                    {
                        "keyword": "Then",
                        "text": "the text should be accepted and displayed",
                    },
                ],
            }

        # Select scenario
        elif tag == "select" or elem_type == "select_option":
            return {
                "name": f"Test Dropdown Selection {index + 1}",
                "description": "Verify dropdown functionality",
                "category": TestCategory.FUNCTIONAL,
                "priority": TestPriority.MEDIUM,
                "steps": [
                    {"keyword": "Given", "text": f"the user is on {url}"},
                    {
                        "keyword": "When",
                        "text": "the user selects an option from the dropdown",
                    },
                    {
                        "keyword": "Then",
                        "text": "the selection should be registered",
                    },
                ],
            }

        # Form scenario
        elif tag == "form" or elem_type == "submit_form":
            return {
                "name": f"Test Form Submission {index + 1}",
                "description": "Verify form submission",
                "category": TestCategory.FUNCTIONAL,
                "priority": TestPriority.CRITICAL,
                "steps": [
                    {"keyword": "Given", "text": f"the user is on {url}"},
                    {
                        "keyword": "When",
                        "text": "the user fills and submits the form",
                    },
                    {
                        "keyword": "Then",
                        "text": "the form should be processed successfully",
                    },
                ],
            }

        # Default scenario
        else:
            return {
                "name": f"Test Element Interaction {index + 1}",
                "description": "Verify element functionality",
                "category": TestCategory.FUNCTIONAL,
                "priority": TestPriority.LOW,
                "steps": [
                    {"keyword": "Given", "text": f"the user is on {url}"},
                    {
                        "keyword": "When",
                        "text": "the user interacts with the element",
                    },
                    {
                        "keyword": "Then",
                        "text": "the element should respond appropriately",
                    },
                ],
            }


class TestPriorityAssigner:
    """Utilities for assigning test priorities"""

    @staticmethod
    def assign_priority(element: Any, category: Any) -> Any:
        """
        Assign priority to a test based on element and category

        Args:
            element: Element being tested
            category: Test category

        Returns:
            Test priority
        """
        from .data_types import TestPriority

        # Get element purpose
        purpose = ElementClassifier.get_functional_purpose(element)

        # Critical priority for forms and security tests
        if purpose == "submit_form":
            return TestPriority.CRITICAL
        if hasattr(category, "value") and category.value == "security":
            return TestPriority.CRITICAL

        # High priority for navigation and buttons
        if purpose in ["trigger_action", "navigate"]:
            return TestPriority.HIGH

        # Medium priority for inputs and validation
        if purpose in ["input_data", "select_option", "toggle_option"]:
            return TestPriority.MEDIUM
        if hasattr(category, "value") and category.value == "validation":
            return TestPriority.MEDIUM

        # Default to low
        return TestPriority.LOW


class TestContextBuilder:
    """Utilities for building test context"""

    @staticmethod
    def build_test_context(page_analysis: Any) -> Dict[str, Any]:
        """
        Build test context from page analysis

        Args:
            page_analysis: Page analysis data

        Returns:
            Test context dictionary
        """
        context: Dict[str, Any] = {
            "url": page_analysis.url if hasattr(page_analysis, "url") else "",
            "total_elements": (
                page_analysis.total_elements
                if hasattr(page_analysis, "total_elements")
                else 0
            ),
            "interactive_elements": (
                page_analysis.interactive_elements
                if hasattr(page_analysis, "interactive_elements")
                else 0
            ),
            "form_elements": (
                page_analysis.form_elements
                if hasattr(page_analysis, "form_elements")
                else 0
            ),
            "navigation_elements": (
                page_analysis.navigation_elements
                if hasattr(page_analysis, "navigation_elements")
                else 0
            ),
            "element_types": [],
            "key_features": [],
        }

        # Analyze enriched elements if available
        if (
            hasattr(page_analysis, "enriched_elements")
            and page_analysis.enriched_elements
        ):
            element_types = set()
            high_interaction = []

            # Limit for context
            for element in page_analysis.enriched_elements[:20]:
                if hasattr(element, "base_element"):
                    elem_data = element.base_element
                    element_types.add(elem_data.get("tag_name", "unknown"))

                    if hasattr(element, "context") and hasattr(
                        element.context, "interaction_likelihood"
                    ):
                        if element.context.interaction_likelihood > 0.7:
                            high_interaction.append(elem_data.get("tag_name"))

            context["element_types"] = list(element_types)
            context["high_interaction_elements"] = high_interaction

        # Add page type and framework if available
        if hasattr(page_analysis, "page_type"):
            context["page_type"] = page_analysis.page_type
        if hasattr(page_analysis, "framework_detected"):
            context["framework"] = page_analysis.framework_detected

        return context


# Aliases for backward compatibility
BrowserExtractionConfig = ExtractionConfig
