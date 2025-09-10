"""
Centralized Type Definitions for UI Testing Framework
Single source of truth for all data types, enums, and models
STRICT DRY: No other module should define its own types
"""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
import hashlib

# Try to import Pydantic, fall back to dataclasses if not available
try:
    from pydantic import BaseModel, Field, ConfigDict
    PYDANTIC_AVAILABLE = True
except ImportError:
    # Fallback for non-Pydantic environments
    BaseModel = object
    Field = lambda default=None, **kwargs: default
    ConfigDict = lambda **kwargs: None
    PYDANTIC_AVAILABLE = False


# ==============================================================================
# ENUM DEFINITIONS - Single source of truth
# ==============================================================================

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
    CANVAS = "canvas"
    
    # Layout Elements
    DIV = "div"
    SPAN = "span"
    HEADER = "header"
    FOOTER = "footer"
    NAV = "nav"
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


# ==============================================================================
# BROWSER CONFIGURATION MODELS
# ==============================================================================

if PYDANTIC_AVAILABLE:
    class TimingProfile(BaseModel):
        """Browser timing configuration"""
        model_config = ConfigDict(arbitrary_types_allowed=True)
        
        page_load_timeout: int = Field(30000, description="Page load timeout in ms")
        script_timeout: int = Field(10000, description="Script execution timeout in ms")
        wait_for_selector_timeout: int = Field(5000, description="Element wait timeout in ms")
        network_idle_timeout: int = Field(2000, description="Network idle timeout in ms")
        animation_timeout: int = Field(1000, description="Animation completion timeout in ms")

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

    class StealthConfig(BaseModel):
        """Complete stealth configuration"""
        model_config = ConfigDict(arbitrary_types_allowed=True)
        
        profile: StealthProfile = Field(default_factory=StealthProfile)
        timing: TimingProfile = Field(default_factory=TimingProfile)
        headers: Dict[str, str] = Field(default_factory=dict)
        viewport: Dict[str, int] = Field(default_factory=lambda: {"width": 1920, "height": 1080})
else:
    # Dataclass fallback
    @dataclass
    class TimingProfile:
        page_load_timeout: int = 30000
        script_timeout: int = 10000
        wait_for_selector_timeout: int = 5000
        network_idle_timeout: int = 2000
        animation_timeout: int = 1000

    @dataclass
    class StealthProfile:
        level: StealthLevel = StealthLevel.MEDIUM
        randomize_viewport: bool = True
        randomize_user_agent: bool = True
        mask_webdriver: bool = True
        disable_automation_features: bool = True
        human_like_delays: bool = True
        min_delay: int = 100
        max_delay: int = 2000

    @dataclass
    class StealthConfig:
        profile: StealthProfile = field(default_factory=StealthProfile)
        timing: TimingProfile = field(default_factory=TimingProfile)
        headers: Dict[str, str] = field(default_factory=dict)
        viewport: Dict[str, int] = field(default_factory=lambda: {"width": 1920, "height": 1080})


# ==============================================================================
# ELEMENT DATA MODELS
# ==============================================================================

if PYDANTIC_AVAILABLE:
    class BoundingBox(BaseModel):
        """Element bounding box"""
        x: float
        y: float
        width: float
        height: float
        top: float
        right: float
        bottom: float
        left: float

    class ComputedStyle(BaseModel):
        """Computed CSS styles"""
        display: Optional[str] = None
        visibility: Optional[str] = None
        opacity: Optional[str] = None
        position: Optional[str] = None
        zIndex: Optional[str] = None
        overflow: Optional[str] = None
        color: Optional[str] = None
        backgroundColor: Optional[str] = None
        fontSize: Optional[str] = None
        fontWeight: Optional[str] = None
        cursor: Optional[str] = None

    class ElementSelector(BaseModel):
        """Element selector information"""
        css: Optional[str] = None
        xpath: Optional[str] = None
        id: Optional[str] = None
        classes: List[str] = Field(default_factory=list)
        attributes: Dict[str, str] = Field(default_factory=dict)
        testId: Optional[str] = None
        ariaLabel: Optional[str] = None
        role: Optional[str] = None

    class ElementData(BaseModel):
        """Comprehensive element data from browser"""
        model_config = ConfigDict(arbitrary_types_allowed=True)
        
        # Basic properties
        tag_name: str
        element_type: ElementType
        text: Optional[str] = None
        value: Optional[str] = None
        
        # Selectors
        selector: ElementSelector
        xpath: str
        css_selector: str
        
        # Attributes
        attributes: Dict[str, Any] = Field(default_factory=dict)
        data_attributes: Dict[str, str] = Field(default_factory=dict)
        aria_attributes: Dict[str, str] = Field(default_factory=dict)
        
        # State
        is_visible: bool = True
        is_enabled: bool = True
        is_clickable: bool = False
        is_editable: bool = False
        is_focusable: bool = False
        is_checked: Optional[bool] = None
        is_selected: Optional[bool] = None
        
        # Layout
        bounding_box: Optional[BoundingBox] = None
        computed_style: Optional[ComputedStyle] = None
        
        # Hierarchy
        parent_tag: Optional[str] = None
        children_count: int = 0
        depth: int = 0
        
        # Confidence
        confidence: float = Field(1.0, ge=0.0, le=1.0)
        extraction_method: ExtractionMethod = ExtractionMethod.DOM

    class ExtractedElement(BaseModel):
        """Element extracted from DOM"""
        model_config = ConfigDict(arbitrary_types_allowed=True)
        
        # Core identification
        element_id: str
        tag_name: str
        element_type: Optional[ElementType] = None
        
        # Content
        text: Optional[str] = None
        inner_html: Optional[str] = None
        outer_html: Optional[str] = None
        
        # Selectors
        selector: str
        xpath: str
        css_selector: Optional[str] = None
        
        # Attributes
        attributes: Dict[str, Any] = Field(default_factory=dict)
        
        # State
        is_visible: bool = True
        is_clickable: bool = False
        is_editable: bool = False
        
        # Metadata
        confidence_score: float = 0.95
        extraction_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
else:
    # Dataclass fallback
    @dataclass
    class BoundingBox:
        x: float
        y: float
        width: float
        height: float
        top: float
        right: float
        bottom: float
        left: float

    @dataclass
    class ComputedStyle:
        display: Optional[str] = None
        visibility: Optional[str] = None
        opacity: Optional[str] = None
        position: Optional[str] = None
        zIndex: Optional[str] = None
        overflow: Optional[str] = None
        color: Optional[str] = None
        backgroundColor: Optional[str] = None
        fontSize: Optional[str] = None
        fontWeight: Optional[str] = None
        cursor: Optional[str] = None

    @dataclass
    class ElementSelector:
        css: Optional[str] = None
        xpath: Optional[str] = None
        id: Optional[str] = None
        classes: List[str] = field(default_factory=list)
        attributes: Dict[str, str] = field(default_factory=dict)
        testId: Optional[str] = None
        ariaLabel: Optional[str] = None
        role: Optional[str] = None

    @dataclass
    class ElementData:
        tag_name: str
        element_type: ElementType
        xpath: str
        css_selector: str
        selector: ElementSelector
        text: Optional[str] = None
        value: Optional[str] = None
        attributes: Dict[str, Any] = field(default_factory=dict)
        data_attributes: Dict[str, str] = field(default_factory=dict)
        aria_attributes: Dict[str, str] = field(default_factory=dict)
        is_visible: bool = True
        is_enabled: bool = True
        is_clickable: bool = False
        is_editable: bool = False
        is_focusable: bool = False
        is_checked: Optional[bool] = None
        is_selected: Optional[bool] = None
        bounding_box: Optional[BoundingBox] = None
        computed_style: Optional[ComputedStyle] = None
        parent_tag: Optional[str] = None
        children_count: int = 0
        depth: int = 0
        confidence: float = 1.0
        extraction_method: ExtractionMethod = ExtractionMethod.DOM

    @dataclass
    class ExtractedElement:
        element_id: str
        tag_name: str
        selector: str
        xpath: str
        element_type: Optional[ElementType] = None
        text: Optional[str] = None
        inner_html: Optional[str] = None
        outer_html: Optional[str] = None
        css_selector: Optional[str] = None
        attributes: Dict[str, Any] = field(default_factory=dict)
        is_visible: bool = True
        is_clickable: bool = False
        is_editable: bool = False
        confidence_score: float = 0.95
        extraction_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ==============================================================================
# CONTEXT AND ENRICHMENT MODELS
# ==============================================================================

if PYDANTIC_AVAILABLE:
    class ElementContext(BaseModel):
        """Comprehensive element context"""
        model_config = ConfigDict(arbitrary_types_allowed=True)
        
        # Hierarchy
        parent_hierarchy: List[str] = Field(default_factory=list)
        siblings_count: int = 0
        position_in_parent: int = 0
        
        # Semantic
        semantic_role: Optional[str] = None
        business_purpose: Optional[str] = None
        data_implications: Optional[str] = None
        user_journey_stage: Optional[str] = None
        
        # Form context
        form_context: Optional[Dict[str, Any]] = None
        section_context: Optional[Dict[str, Any]] = None
        
        # Position
        page_position: Optional[str] = None
        visual_prominence: float = 0.0
        
        # Interaction
        interaction_likelihood: float = 0.0
        accessibility_score: float = 0.0

    class EnrichedElement(BaseModel):
        """Element enriched with LLM analysis"""
        model_config = ConfigDict(arbitrary_types_allowed=True)
        
        base_element: Union[Dict[str, Any], ElementData, ExtractedElement]
        context: ElementContext
        llm_analysis: Dict[str, Any] = Field(default_factory=dict)
        
        # Testing
        test_categories: List[TestCategory] = Field(default_factory=list)
        test_scenarios: List[str] = Field(default_factory=list)
        test_priority: TestPriority = TestPriority.MEDIUM
        
        # Purpose
        functional_purpose: Optional[str] = None
        business_criticality: Optional[str] = None
        
        # Validation
        validation_rules: List[str] = Field(default_factory=list)
        
        # Accessibility
        accessibility_considerations: List[str] = Field(default_factory=list)
        accessibility_notes: Optional[str] = None
        
        # Confidence
        confidence_score: float = 0.95
        extraction_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

    class PageAnalysis(BaseModel):
        """Complete page analysis"""
        model_config = ConfigDict(arbitrary_types_allowed=True)
        
        url: str
        title: str = ""
        page_type: str = "unknown"
        framework_detected: Optional[str] = None
        
        # Elements
        total_elements: int = 0
        interactive_elements: int = 0
        form_elements: int = 0
        navigation_elements: int = 0
        enriched_elements: List[EnrichedElement] = Field(default_factory=list)
        
        # Insights
        llm_insights: Dict[str, Any] = Field(default_factory=dict)
        qa_test_plan: Dict[str, List[str]] = Field(default_factory=dict)
        
        # Timing
        extraction_time: float = 0.0
        llm_processing_time: float = 0.0
else:
    # Dataclass fallback
    @dataclass
    class ElementContext:
        parent_hierarchy: List[str] = field(default_factory=list)
        siblings_count: int = 0
        position_in_parent: int = 0
        semantic_role: Optional[str] = None
        business_purpose: Optional[str] = None
        data_implications: Optional[str] = None
        user_journey_stage: Optional[str] = None
        form_context: Optional[Dict[str, Any]] = None
        section_context: Optional[Dict[str, Any]] = None
        page_position: Optional[str] = None
        visual_prominence: float = 0.0
        interaction_likelihood: float = 0.0
        accessibility_score: float = 0.0

    @dataclass
    class EnrichedElement:
        base_element: Any
        context: ElementContext
        llm_analysis: Dict[str, Any] = field(default_factory=dict)
        test_categories: List[TestCategory] = field(default_factory=list)
        test_scenarios: List[str] = field(default_factory=list)
        test_priority: TestPriority = TestPriority.MEDIUM
        functional_purpose: Optional[str] = None
        business_criticality: Optional[str] = None
        validation_rules: List[str] = field(default_factory=list)
        accessibility_considerations: List[str] = field(default_factory=list)
        accessibility_notes: Optional[str] = None
        confidence_score: float = 0.95
        extraction_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @dataclass
    class PageAnalysis:
        url: str
        title: str = ""
        page_type: str = "unknown"
        framework_detected: Optional[str] = None
        total_elements: int = 0
        interactive_elements: int = 0
        form_elements: int = 0
        navigation_elements: int = 0
        enriched_elements: List[EnrichedElement] = field(default_factory=list)
        llm_insights: Dict[str, Any] = field(default_factory=dict)
        qa_test_plan: Dict[str, List[str]] = field(default_factory=dict)
        extraction_time: float = 0.0
        llm_processing_time: float = 0.0


# ==============================================================================
# TEST GENERATION MODELS
# ==============================================================================

if PYDANTIC_AVAILABLE:
    class GherkinStep(BaseModel):
        """Gherkin step representation"""
        keyword: str = Field(..., description="Step keyword (Given, When, Then, And, But)")
        text: str = Field(..., description="Step text")
        data_table: Optional[List[List[str]]] = Field(None, description="Data table for step")
        
        def to_gherkin(self) -> str:
            """Convert to Gherkin format"""
            lines = [f"{self.keyword} {self.text}"]
            if self.data_table:
                for row in self.data_table:
                    lines.append("  | " + " | ".join(row) + " |")
            return "\n".join(lines)

    class TestScenario(BaseModel):
        """Complete test scenario"""
        model_config = ConfigDict(use_enum_values=True)
        
        name: str = Field(..., description="Scenario name")
        description: str = Field(..., description="Detailed description")
        category: TestCategory = Field(..., description="Test category")
        priority: TestPriority = Field(TestPriority.MEDIUM, description="Priority level")
        steps: List[GherkinStep] = Field(..., description="Gherkin test steps")
        test_data: Dict[str, Any] = Field(default_factory=dict, description="Test data")
        expected_results: List[str] = Field(default_factory=list, description="Expected results")
        tags: List[str] = Field(default_factory=list, description="Tags for filtering")
        confidence_score: float = Field(0.95, ge=0, le=1, description="AI confidence score")
        
        def to_gherkin(self) -> str:
            """Convert to Gherkin scenario"""
            lines = []
            if self.tags:
                lines.append("  " + " ".join(f"@{tag}" for tag in self.tags))
            lines.append(f"  @{self.priority} @{self.category}")
            lines.append(f"  Scenario: {self.name}")
            if self.description:
                lines.append(f"    # {self.description}")
            for step in self.steps:
                step_lines = step.to_gherkin().split('\n')
                for line in step_lines:
                    lines.append(f"    {line}")
            return "\n".join(lines)

    class TestSuite(BaseModel):
        """Complete test suite"""
        model_config = ConfigDict(use_enum_values=True)
        
        feature_name: str = Field(..., description="Feature name")
        feature_description: str = Field(..., description="Feature description")
        url: Optional[str] = Field(None, description="URL being tested")
        scenarios: List[TestScenario] = Field(..., description="Test scenarios")
        total_scenarios: int = Field(..., description="Total scenarios")
        generation_time: float = Field(..., description="Generation time in seconds")
        
        def to_gherkin(self) -> str:
            """Convert entire suite to Gherkin feature file"""
            lines = [
                f"Feature: {self.feature_name}",
                f"  {self.feature_description}",
                ""
            ]
            if self.url:
                lines.extend([f"  # URL: {self.url}", ""])
            for scenario in self.scenarios:
                lines.append(scenario.to_gherkin())
                lines.append("")
            return "\n".join(lines)
else:
    # Dataclass fallback
    @dataclass
    class GherkinStep:
        keyword: str
        text: str
        data_table: Optional[List[List[str]]] = None
        
        def to_gherkin(self) -> str:
            lines = [f"{self.keyword} {self.text}"]
            if self.data_table:
                for row in self.data_table:
                    lines.append("  | " + " | ".join(row) + " |")
            return "\n".join(lines)

    @dataclass
    class TestScenario:
        name: str
        description: str
        category: TestCategory
        priority: TestPriority = TestPriority.MEDIUM
        steps: List[GherkinStep] = field(default_factory=list)
        test_data: Dict[str, Any] = field(default_factory=dict)
        expected_results: List[str] = field(default_factory=list)
        tags: List[str] = field(default_factory=list)
        confidence_score: float = 0.95
        
        def to_gherkin(self) -> str:
            lines = []
            if self.tags:
                lines.append("  " + " ".join(f"@{tag}" for tag in self.tags))
            lines.append(f"  @{self.priority} @{self.category}")
            lines.append(f"  Scenario: {self.name}")
            if self.description:
                lines.append(f"    # {self.description}")
            for step in self.steps:
                step_lines = step.to_gherkin().split('\n')
                for line in step_lines:
                    lines.append(f"    {line}")
            return "\n".join(lines)

    @dataclass
    class TestSuite:
        feature_name: str
        feature_description: str
        scenarios: List[TestScenario]
        total_scenarios: int
        generation_time: float
        url: Optional[str] = None
        
        def to_gherkin(self) -> str:
            lines = [
                f"Feature: {self.feature_name}",
                f"  {self.feature_description}",
                ""
            ]
            if self.url:
                lines.extend([f"  # URL: {self.url}", ""])
            for scenario in self.scenarios:
                lines.append(scenario.to_gherkin())
                lines.append("")
            return "\n".join(lines)


# ==============================================================================
# EXTRACTION CONFIGURATION AND RESULTS
# ==============================================================================

if PYDANTIC_AVAILABLE:
    class DOMExtractionConfig(BaseModel):
        """Configuration for DOM element extraction"""
        model_config = ConfigDict(use_enum_values=True)
        
        # Element selection
        include_invisible: bool = Field(False, description="Include invisible elements")
        include_iframes: bool = Field(True, description="Include iframe content")
        max_depth: int = Field(10, description="Maximum DOM traversal depth")
        element_limit: int = Field(1000, description="Maximum elements to extract")
        
        # Extraction features
        extract_styles: bool = Field(True, description="Extract computed styles")
        extract_animations: bool = Field(False, description="Extract animation details")
        extract_accessibility: bool = Field(True, description="Extract accessibility info")
        
        # Performance
        wait_for_network_idle: bool = Field(True, description="Wait for network idle")
        screenshot_enabled: bool = Field(False, description="Take element screenshots")
        parallel_extraction: bool = Field(True, description="Use parallel extraction")
        
        # Timing
        timeout: int = Field(30000, description="Overall timeout in ms")
        retry_on_failure: bool = Field(True, description="Retry failed extractions")
        
        # Caching
        enable_caching: bool = Field(False, description="Enable extraction cache")
        cache_ttl: int = Field(3600, description="Cache TTL in seconds")

    class BrowserExtractionConfig(BaseModel):
        """Configuration for browser-based extraction"""
        model_config = ConfigDict(use_enum_values=True)
        
        # Browser settings
        headless: bool = Field(True, description="Run browser in headless mode")
        stealth_config: Optional[StealthConfig] = None
        profile_type: ProfileType = ProfileType.QA
        
        # Extraction
        strategy: ExtractionStrategy = ExtractionStrategy.THOROUGH
        max_elements: int = Field(100, description="Maximum elements to extract")
        enable_stealth: bool = Field(True, description="Enable stealth mode")
        enable_shadow_dom: bool = Field(True, description="Extract from shadow DOM")
        
        # Timing
        timeout: int = Field(30000, description="Page load timeout in ms")
        wait_for_dynamic: bool = Field(True, description="Wait for dynamic content")
        
        # Caching
        enable_caching: bool = Field(True, description="Enable extraction cache")
        cache_ttl: int = Field(3600, description="Cache TTL in seconds")
        
        # QA mode
        qa_mode: bool = Field(False, description="Extract only QA-relevant interactive elements")
        qa_priority_tags: List[str] = Field(default_factory=lambda: ["button", "input", "select", "a", "textarea"])
        
        # Additional extraction settings from elements_extractor_no_llm
        enable_iframe_traversal: bool = Field(default=True)
        enable_dynamic_wait: bool = Field(default=True)
        enable_mutation_observer: bool = Field(default=False)
        max_depth: int = Field(default=10, ge=1, le=100)
        extraction_timeout: int = Field(default=30000, ge=1000, le=120000)
        filter_invisible: bool = Field(default=True)
        filter_duplicates: bool = Field(default=True)
        min_element_size: int = Field(default=5, ge=0)
        randomize_delays: bool = Field(default=True)
        min_delay: float = Field(default=0.1, ge=0.0, le=10.0)
        max_delay: float = Field(default=0.5, ge=0.0, le=10.0)
        batch_size: int = Field(default=100, ge=1, le=1000)
        include_computed_styles: bool = Field(default=True)
        include_accessibility_info: bool = Field(default=True)
        include_event_listeners: bool = Field(default=False)
        capture_screenshots: bool = Field(default=False)
        screenshot_full_page: bool = Field(default=True)
        screenshot_format: str = Field(default="png", pattern="^(png|jpeg|jpg)$")
        screenshot_quality: int = Field(default=90, ge=1, le=100)
        highlight_elements: bool = Field(default=True)
        highlight_color: str = Field(default="red")
        highlight_width: int = Field(default=2, ge=1, le=10)

    class ScreenshotData(BaseModel):
        """Screenshot information"""
        element_id: str
        base64_data: str
        mime_type: str = "image/png"
        width: int
        height: int
        timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

    class CrawlResult(BaseModel):
        """Result of page crawl"""
        url: str
        depth: int
        links_found: List[str] = Field(default_factory=list)
        forms_found: List[Dict[str, Any]] = Field(default_factory=list)
        errors: List[str] = Field(default_factory=list)
        timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

    class BrowserExtractionResult(BaseModel):
        """Result from browser extraction"""
        model_config = ConfigDict(arbitrary_types_allowed=True)
        
        url: str
        success: bool
        elements: List[ElementData] = Field(default_factory=list)
        
        # Page metadata
        page_title: Optional[str] = None
        page_description: Optional[str] = None
        page_keywords: List[str] = Field(default_factory=list)
        
        # Detection
        framework_detected: Optional[str] = None
        captcha_detected: bool = False
        login_detected: bool = False
        
        # Performance
        extraction_duration_ms: int = 0
        elements_found: int = 0
        elements_filtered: int = 0
        
        # Errors
        errors: List[str] = Field(default_factory=list)
        warnings: List[str] = Field(default_factory=list)
        
        # Metadata
        timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
        browser_version: Optional[str] = None
        extraction_strategy: Optional[ExtractionStrategy] = None

    class DOMExtractionResult(BaseModel):
        """Result from DOM extraction"""
        model_config = ConfigDict(arbitrary_types_allowed=True)
        
        url: str
        success: bool
        elements: List[ExtractedElement] = Field(default_factory=list)
        
        # Page info
        page_info: Dict[str, Any] = Field(default_factory=dict)
        
        # Metadata
        extraction_metadata: Dict[str, Any] = Field(default_factory=dict)
        performance_metrics: Dict[str, float] = Field(default_factory=dict)
        errors: List[str] = Field(default_factory=list)
        
        # Timing
        extraction_duration_ms: int = 0
        timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

    class TestGenerationContract(BaseModel):
        """Contract for test generation"""
        model_config = ConfigDict(use_enum_values=True)
        
        url: str = Field(..., description="URL to generate tests for")
        test_frameworks: List[TestFramework] = Field(
            default=[TestFramework.PLAYWRIGHT],
            description="Target test frameworks"
        )
        test_categories: List[TestCategory] = Field(
            default_factory=list,
            description="Specific test categories to focus on"
        )
        max_scenarios_per_category: int = Field(5, description="Max scenarios per category")
        include_edge_cases: bool = Field(True, description="Include edge case scenarios")
        include_negative_tests: bool = Field(True, description="Include negative test cases")
        generate_test_data: bool = Field(True, description="Generate test data")
        output_format: str = Field("gherkin", description="Output format")

    class TestGenerationResult(BaseModel):
        """Result of test generation"""
        model_config = ConfigDict(use_enum_values=True)
        
        url: str = Field(..., description="URL tested")
        test_suite: TestSuite = Field(..., description="Generated test suite")
        page_analysis: PageAnalysis = Field(..., description="Page analysis used")
        total_scenarios: int = Field(..., description="Total scenarios generated")
        categories_covered: List[str] = Field(..., description="Test categories covered")
        generation_time: float = Field(..., description="Total generation time")
        llm_processing_time: float = Field(..., description="LLM processing time")
        strategies_used: List[str] = Field(..., description="Prompt strategies used")
        confidence_score: float = Field(0.95, description="Overall confidence")
else:
    # Dataclass fallback - simplified versions
    @dataclass
    class DOMExtractionConfig:
        include_invisible: bool = False
        include_iframes: bool = True
        max_depth: int = 10
        element_limit: int = 1000
        extract_styles: bool = True
        extract_animations: bool = False
        extract_accessibility: bool = True
        wait_for_network_idle: bool = True
        screenshot_enabled: bool = False
        parallel_extraction: bool = True
        timeout: int = 30000
        retry_on_failure: bool = True
        enable_caching: bool = False
        cache_ttl: int = 3600

    @dataclass
    class BrowserExtractionConfig:
        headless: bool = True
        stealth_config: Optional[StealthConfig] = None
        profile_type: ProfileType = ProfileType.QA
        strategy: ExtractionStrategy = ExtractionStrategy.THOROUGH
        max_elements: int = 100
        enable_stealth: bool = True
        enable_shadow_dom: bool = True
        timeout: int = 30000
        wait_for_dynamic: bool = True

    @dataclass
    class ScreenshotData:
        element_id: str
        base64_data: str
        mime_type: str = "image/png"
        width: int = 0
        height: int = 0
        timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @dataclass
    class CrawlResult:
        url: str
        depth: int
        links_found: List[str] = field(default_factory=list)
        forms_found: List[Dict[str, Any]] = field(default_factory=list)
        errors: List[str] = field(default_factory=list)
        timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @dataclass
    class BrowserExtractionResult:
        url: str
        success: bool
        elements: List[ElementData] = field(default_factory=list)
        page_title: Optional[str] = None
        page_description: Optional[str] = None
        page_keywords: List[str] = field(default_factory=list)
        framework_detected: Optional[str] = None
        captcha_detected: bool = False
        login_detected: bool = False
        extraction_duration_ms: int = 0
        elements_found: int = 0
        elements_filtered: int = 0
        errors: List[str] = field(default_factory=list)
        warnings: List[str] = field(default_factory=list)
        timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
        browser_version: Optional[str] = None
        extraction_strategy: Optional[ExtractionStrategy] = None

    @dataclass
    class DOMExtractionResult:
        url: str
        success: bool
        elements: List[ExtractedElement] = field(default_factory=list)
        page_info: Dict[str, Any] = field(default_factory=dict)
        extraction_metadata: Dict[str, Any] = field(default_factory=dict)
        performance_metrics: Dict[str, float] = field(default_factory=dict)
        errors: List[str] = field(default_factory=list)
        extraction_duration_ms: int = 0
        timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @dataclass
    class TestGenerationContract:
        url: str
        test_frameworks: List[TestFramework] = field(default_factory=lambda: [TestFramework.PLAYWRIGHT])
        test_categories: List[TestCategory] = field(default_factory=list)
        max_scenarios_per_category: int = 5
        include_edge_cases: bool = True
        include_negative_tests: bool = True
        generate_test_data: bool = True
        output_format: str = "gherkin"

    @dataclass
    class TestGenerationResult:
        url: str
        test_suite: TestSuite
        page_analysis: PageAnalysis
        total_scenarios: int
        categories_covered: List[str]
        generation_time: float
        llm_processing_time: float
        strategies_used: List[str]
        confidence_score: float = 0.95


# ==============================================================================
# PROMPT STRATEGY MODELS
# ==============================================================================

@dataclass(frozen=True)
class PromptStrategy:
    """Prompt strategy with optimized content"""
    name: str
    title: str
    core_principle: str
    universal_prompt: str
    axiom: str = ""
    usage_example: str = ""
    remember_quote: str = ""
    
    @property
    def hash_id(self) -> str:
        """Generate unique hash"""
        content = f"{self.name}{self.universal_prompt}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    @property
    def short_description(self) -> str:
        """Get first line of core principle"""
        lines = self.core_principle.split("\n")
        return lines[0] if lines else ""
    
    def render(self, task: str, **kwargs: Any) -> str:
        """Render prompt with task"""
        prompt = self.universal_prompt
        if task and task not in prompt:
            prompt = f"Task: {task}\n\n{prompt}"
        if kwargs and "{" in prompt and "}" in prompt:
            prompt = prompt.format(task=task, **kwargs)
        return prompt.strip()


# ==============================================================================
# EXCEPTION CLASSES
# ==============================================================================

class BrowserError(Exception):
    """Base exception for browser operations"""
    pass

class NavigationError(BrowserError):
    """Navigation failed"""
    pass

class ExtractionError(BrowserError):
    """Element extraction failed"""
    pass

class TimeoutError(BrowserError):
    """Operation timed out"""
    pass


# ==============================================================================
# TYPE ALIASES AND UNIONS
# ==============================================================================

# Element type unions
AnyElement = Union[ElementData, ExtractedElement, EnrichedElement]
AnyExtractionResult = Union[BrowserExtractionResult, DOMExtractionResult]
AnyExtractionConfig = Union[DOMExtractionConfig, BrowserExtractionConfig]

# Collection types
ElementList = List[AnyElement]
TestScenarioList = List[TestScenario]
CategoryList = List[TestCategory]

# Mapping types
AttributeMap = Dict[str, Any]
TestPlanMap = Dict[str, List[str]]
InsightsMap = Dict[str, Any]


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def map_category_string_to_enum(category: str) -> Optional[TestCategory]:
    """Map a string to TestCategory enum"""
    category_lower = category.lower().replace(" ", "_").replace("-", "_")
    
    for cat in TestCategory:
        if cat.value == category_lower:
            return cat
    
    # Fuzzy mapping
    mapping = {
        "functional": TestCategory.FUNCTIONAL,
        "function": TestCategory.FUNCTIONAL,
        "validation": TestCategory.VALIDATION,
        "validate": TestCategory.VALIDATION,
        "accessibility": TestCategory.ACCESSIBILITY,
        "a11y": TestCategory.ACCESSIBILITY,
        "security": TestCategory.SECURITY,
        "secure": TestCategory.SECURITY,
        "performance": TestCategory.PERFORMANCE,
        "perf": TestCategory.PERFORMANCE,
        "usability": TestCategory.USABILITY,
        "ux": TestCategory.USABILITY,
        "compatibility": TestCategory.COMPATIBILITY,
        "compat": TestCategory.COMPATIBILITY,
        "error": TestCategory.ERROR_HANDLING,
        "error_handling": TestCategory.ERROR_HANDLING,
        "localization": TestCategory.LOCALIZATION,
        "i18n": TestCategory.LOCALIZATION,
        "data": TestCategory.DATA_INTEGRITY,
    }
    
    return mapping.get(category_lower)


def get_element_type(tag: str, attributes: Dict[str, Any] = None) -> ElementType:
    """Determine element type from tag and attributes"""
    tag_lower = tag.lower()
    attributes = attributes or {}
    
    # Check input types
    if tag_lower == "input":
        input_type = attributes.get("type", "text").lower()
        type_mapping = {
            "text": ElementType.TEXT_INPUT,
            "password": ElementType.PASSWORD,
            "email": ElementType.EMAIL,
            "number": ElementType.NUMBER,
            "checkbox": ElementType.CHECKBOX,
            "radio": ElementType.RADIO,
            "file": ElementType.FILE_INPUT,
            "date": ElementType.DATE_INPUT,
            "time": ElementType.TIME_INPUT,
            "search": ElementType.SEARCH,
            "tel": ElementType.TEL,
            "url": ElementType.URL_INPUT,
            "range": ElementType.RANGE,
            "color": ElementType.COLOR,
            "submit": ElementType.SUBMIT,
        }
        return type_mapping.get(input_type, ElementType.TEXT_INPUT)
    
    # Direct tag mapping
    tag_mapping = {
        "button": ElementType.BUTTON,
        "a": ElementType.LINK,
        "select": ElementType.SELECT,
        "textarea": ElementType.TEXTAREA,
        "form": ElementType.FORM,
        "img": ElementType.IMAGE,
        "video": ElementType.VIDEO,
        "audio": ElementType.AUDIO,
        "canvas": ElementType.CANVAS,
        "table": ElementType.TABLE,
        "tr": ElementType.TABLE_ROW,
        "td": ElementType.TABLE_CELL,
        "th": ElementType.TABLE_HEADER,
        "ul": ElementType.LIST,
        "ol": ElementType.LIST,
        "li": ElementType.LIST_ITEM,
        "nav": ElementType.NAV,
        "header": ElementType.HEADER,
        "footer": ElementType.FOOTER,
        "section": ElementType.SECTION,
        "article": ElementType.ARTICLE,
        "aside": ElementType.ASIDE,
        "main": ElementType.MAIN,
        "dialog": ElementType.DIALOG,
        "iframe": ElementType.IFRAME,
        "label": ElementType.LABEL,
        "h1": ElementType.HEADING,
        "h2": ElementType.HEADING,
        "h3": ElementType.HEADING,
        "h4": ElementType.HEADING,
        "h5": ElementType.HEADING,
        "h6": ElementType.HEADING,
        "p": ElementType.PARAGRAPH,
        "code": ElementType.CODE,
        "pre": ElementType.PRE,
        "div": ElementType.DIV,
        "span": ElementType.SPAN,
        "menu": ElementType.MENU,
    }
    
    return tag_mapping.get(tag_lower, ElementType.UNKNOWN)


# ==============================================================================
# EXPORT ALL PUBLIC INTERFACES
# ==============================================================================

__all__ = [
    # Enums
    'ElementType',
    'TestCategory',
    'QACategory',
    'TestPriority',
    'TestFramework',
    'ProfileType',
    'StealthLevel',
    'ExtractionStrategy',
    'InteractionType',
    'LocatorStrategy',
    'ExtractionMethod',
    'ConfidenceLevel',
    'StrategyName',
    
    # Browser models
    'TimingProfile',
    'StealthProfile',
    'StealthConfig',
    
    # Element models
    'BoundingBox',
    'ComputedStyle',
    'ElementSelector',
    'ElementData',
    'ExtractedElement',
    
    # Context models
    'ElementContext',
    'EnrichedElement',
    'PageAnalysis',
    
    # Test models
    'GherkinStep',
    'TestScenario',
    'TestSuite',
    
    # Extraction models
    'DOMExtractionConfig',
    'BrowserExtractionConfig',
    'ScreenshotData',
    'CrawlResult',
    'BrowserExtractionResult',
    'DOMExtractionResult',
    
    # Contracts
    'TestGenerationContract',
    'TestGenerationResult',
    
    # Prompt models
    'PromptStrategy',
    
    # Exceptions
    'BrowserError',
    'NavigationError',
    'ExtractionError',
    'TimeoutError',
    
    # Type aliases
    'AnyElement',
    'AnyExtractionResult',
    'AnyExtractionConfig',
    'ElementList',
    'TestScenarioList',
    'CategoryList',
    'AttributeMap',
    'TestPlanMap',
    'InsightsMap',
    
    # Helper functions
    'map_category_string_to_enum',
    'get_element_type',
]