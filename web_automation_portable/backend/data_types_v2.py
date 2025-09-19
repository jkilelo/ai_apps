"""
Data Types v2 - Single Source of Truth
All Pydantic v2 models for the entire web automation system
100% DRY compliance - NO module defines its own types
ASCII-only enforcement throughout
"""

from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re
import json


# ==============================================================================
# ASCII ENFORCEMENT UTILITIES
# ==============================================================================

def enforce_ascii(value: str) -> str:
    """Enforce ASCII-only strings by removing non-ASCII characters"""
    if value is None:
        return value
    return ''.join(char for char in value if ord(char) < 128)


def validate_ascii(value: str) -> str:
    """Validate and clean string to ASCII-only"""
    if value is None:
        return value
    cleaned = enforce_ascii(value)
    if len(cleaned) != len(value):
        # Non-ASCII characters were removed
        pass  # Silent cleanup
    return cleaned


# ==============================================================================
# ENUMERATIONS
# ==============================================================================

class BrowserType(str, Enum):
    """Supported browser types"""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"
    CHROME = "chrome"
    EDGE = "edge"
    SAFARI = "safari"


class ProtocolType(str, Enum):
    """Browser automation protocols"""
    WEBDRIVER_BIDI = "webdriver_bidi"  # 2025 standard
    CDP = "cdp"  # Chrome DevTools Protocol
    WEBDRIVER = "webdriver"  # Legacy


class ElementType(str, Enum):
    """Types of web elements"""
    BUTTON = "button"
    LINK = "link"
    INPUT = "input"
    SELECT = "select"
    TEXTAREA = "textarea"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    IMAGE = "image"
    VIDEO = "video"
    FORM = "form"
    DIV = "div"
    SPAN = "span"
    NAVIGATION = "navigation"
    HEADER = "header"
    FOOTER = "footer"
    UNKNOWN = "unknown"


class TestCategory(str, Enum):
    """Test categories for generation"""
    FUNCTIONAL = "functional"
    VALIDATION = "validation"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USABILITY = "usability"
    COMPATIBILITY = "compatibility"
    LOCALIZATION = "localization"
    ERROR_HANDLING = "error_handling"
    BOUNDARY = "boundary"
    REGRESSION = "regression"
    SMOKE = "smoke"
    INTEGRATION = "integration"
    E2E = "e2e"


class TestPriority(str, Enum):
    """Test priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    TRIVIAL = "trivial"


class TestFramework(str, Enum):
    """Supported test frameworks"""
    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    CYPRESS = "cypress"
    PUPPETEER = "puppeteer"
    WEBDRIVERIO = "webdriverio"
    TESTCAFE = "testcafe"
    ROBOT = "robot"


class ExecutionStatus(str, Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    TIMEOUT = "timeout"


class PageType(str, Enum):
    """Types of web pages"""
    LOGIN = "login"
    DASHBOARD = "dashboard"
    FORM = "form"
    ECOMMERCE = "ecommerce"
    BLOG = "blog"
    LANDING = "landing"
    SEARCH = "search"
    PROFILE = "profile"
    SETTINGS = "settings"
    CHECKOUT = "checkout"
    DOCUMENTATION = "documentation"
    UNKNOWN = "unknown"


# ==============================================================================
# CONFIGURATION MODELS
# ==============================================================================

class BrowserConfig(BaseModel):
    """Browser configuration"""
    model_config = ConfigDict(validate_assignment=True, use_enum_values=True)

    browser_type: BrowserType = Field(default=BrowserType.CHROMIUM)
    protocol: ProtocolType = Field(default=ProtocolType.WEBDRIVER_BIDI)
    headless: bool = Field(default=True)
    viewport_width: int = Field(default=1920, ge=800, le=3840)
    viewport_height: int = Field(default=1080, ge=600, le=2160)
    timeout: int = Field(default=30000, ge=1000, le=120000, description="Timeout in ms")
    enable_stealth: bool = Field(default=True)
    enable_javascript: bool = Field(default=True)
    enable_cookies: bool = Field(default=True)
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    extra_args: List[str] = Field(default_factory=list)

    @field_validator('user_agent', 'proxy')
    @classmethod
    def validate_ascii_fields(cls, v):
        return validate_ascii(v) if v else v


class ExtractionConfig(BaseModel):
    """Element extraction configuration"""
    model_config = ConfigDict(validate_assignment=True)

    max_elements: int = Field(default=100, ge=1, le=1000)
    include_invisible: bool = Field(default=False)
    include_iframes: bool = Field(default=True)
    include_shadow_dom: bool = Field(default=True)
    wait_for_network: bool = Field(default=True)
    screenshot_enabled: bool = Field(default=False)
    interaction_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    element_timeout: int = Field(default=5000, ge=100, le=30000, description="ms")
    selectors_strategy: List[str] = Field(
        default_factory=lambda: ["css", "xpath", "accessibility", "text"]
    )


class LLMConfig(BaseModel):
    """LLM configuration for AI enrichment"""
    model_config = ConfigDict(validate_assignment=True)

    model: str = Field(default="gpt-4", description="LLM model to use")
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4000, ge=100, le=8000)
    batch_size: int = Field(default=10, ge=1, le=50)
    cache_enabled: bool = Field(default=True)
    cache_ttl: int = Field(default=3600, ge=60, le=86400, description="Cache TTL in seconds")
    retry_attempts: int = Field(default=3, ge=0, le=5)
    parallel_calls: int = Field(default=3, ge=1, le=10)
    prompt_optimization: bool = Field(default=True)
    response_format: str = Field(default="json")


class TestConfig(BaseModel):
    """Test generation configuration"""
    model_config = ConfigDict(validate_assignment=True)

    categories: List[TestCategory] = Field(
        default_factory=lambda: [TestCategory.FUNCTIONAL, TestCategory.VALIDATION]
    )
    max_scenarios_per_category: int = Field(default=5, ge=1, le=20)
    include_negative_tests: bool = Field(default=True)
    include_edge_cases: bool = Field(default=True)
    generate_test_data: bool = Field(default=True)
    coverage_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    prioritization_enabled: bool = Field(default=True)


class ExecutionConfig(BaseModel):
    """Test execution configuration"""
    model_config = ConfigDict(validate_assignment=True)

    parallel_workers: int = Field(default=4, ge=1, le=16)
    retry_failed: bool = Field(default=True)
    max_retries: int = Field(default=2, ge=0, le=5)
    timeout_per_test: int = Field(default=60000, ge=5000, le=300000, description="ms")
    screenshot_on_failure: bool = Field(default=True)
    video_recording: bool = Field(default=False)
    detailed_logging: bool = Field(default=True)
    stop_on_failure: bool = Field(default=False)
    environment: str = Field(default="test")


class PipelineConfig(BaseModel):
    """Main pipeline configuration"""
    model_config = ConfigDict(validate_assignment=True)

    browser: BrowserConfig = Field(default_factory=BrowserConfig)
    extraction: ExtractionConfig = Field(default_factory=ExtractionConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    test: TestConfig = Field(default_factory=TestConfig)
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)
    frameworks: List[TestFramework] = Field(
        default_factory=lambda: [TestFramework.PLAYWRIGHT]
    )
    auto_execute: bool = Field(default=False)
    streaming_enabled: bool = Field(default=True)
    save_artifacts: bool = Field(default=True)
    output_directory: str = Field(default="./test_output")

    @field_validator('output_directory')
    @classmethod
    def validate_output_dir(cls, v):
        return validate_ascii(v)


# ==============================================================================
# CONTRACT MODELS (Input/Output for each module)
# ==============================================================================

class BrowserContract(BaseModel):
    """Input contract for Browser Manager"""
    model_config = ConfigDict(validate_assignment=True)

    url: str
    config: BrowserConfig = Field(default_factory=BrowserConfig)
    session_id: Optional[str] = None
    reuse_session: bool = Field(default=False)

    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        # Basic URL validation and ASCII enforcement
        v = validate_ascii(v)
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class BrowserResult(BaseModel):
    """Output from Browser Manager"""
    model_config = ConfigDict(validate_assignment=True)

    session_id: str
    browser_type: BrowserType
    protocol: ProtocolType
    page_title: str
    page_url: str
    viewport: Dict[str, int]
    cookies_count: int = 0
    console_messages: List[str] = Field(default_factory=list)
    network_requests: List[Dict[str, Any]] = Field(default_factory=list)
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    screenshots: List[str] = Field(default_factory=list)

    @field_validator('page_title', 'page_url')
    @classmethod
    def validate_ascii_fields(cls, v):
        return validate_ascii(v)


class ExtractContract(BaseModel):
    """Input contract for Element Extractor"""
    model_config = ConfigDict(validate_assignment=True)

    browser_session: str
    config: ExtractionConfig = Field(default_factory=ExtractionConfig)
    target_elements: Optional[List[str]] = None
    exclude_selectors: List[str] = Field(default_factory=list)


class ElementResult(BaseModel):
    """Output from Element Extractor"""
    model_config = ConfigDict(validate_assignment=True)

    url: str
    total_elements: int
    interactive_elements: int
    elements: List[Element] = Field(default_factory=list)
    element_tree: Optional[Dict[str, Any]] = None
    extraction_time: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EnrichContract(BaseModel):
    """Input contract for AI Enricher"""
    model_config = ConfigDict(validate_assignment=True)

    elements: List[Element]
    config: LLMConfig = Field(default_factory=LLMConfig)
    page_context: Optional[Dict[str, Any]] = None
    enrichment_level: str = Field(default="full", pattern="^(basic|standard|full)$")


class EnrichedResult(BaseModel):
    """Output from AI Enricher"""
    model_config = ConfigDict(validate_assignment=True)

    elements: List[EnrichedElement]
    page_insights: PageInsights
    enrichment_time: float
    llm_tokens_used: int = 0
    cache_hits: int = 0
    confidence_scores: Dict[str, float] = Field(default_factory=dict)


class TestContract(BaseModel):
    """Input contract for Test Generator"""
    model_config = ConfigDict(validate_assignment=True)

    enriched_elements: List[EnrichedElement]
    page_insights: PageInsights
    config: TestConfig = Field(default_factory=TestConfig)
    custom_scenarios: Optional[List[Dict[str, Any]]] = None


class TestSuiteResult(BaseModel):
    """Output from Test Generator"""
    model_config = ConfigDict(validate_assignment=True)

    feature_name: str
    feature_description: str
    scenarios: List[TestScenario]
    total_scenarios: int
    coverage_percentage: float
    risk_assessment: Dict[str, Any] = Field(default_factory=dict)
    generation_time: float

    @field_validator('feature_name', 'feature_description')
    @classmethod
    def validate_ascii_fields(cls, v):
        return validate_ascii(v)


class CodeContract(BaseModel):
    """Input contract for Code Generator"""
    model_config = ConfigDict(validate_assignment=True)

    test_suite: TestSuiteResult
    framework: TestFramework
    language: str = Field(default="python", pattern="^(python|javascript|typescript|java|csharp)$")
    include_helpers: bool = Field(default=True)
    include_page_objects: bool = Field(default=True)


class CodeArtifact(BaseModel):
    """Output from Code Generator"""
    model_config = ConfigDict(validate_assignment=True)

    framework: TestFramework
    language: str
    test_files: Dict[str, str] = Field(default_factory=dict)  # filename -> code
    helper_files: Dict[str, str] = Field(default_factory=dict)
    page_objects: Dict[str, str] = Field(default_factory=dict)
    config_files: Dict[str, str] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    setup_instructions: str = ""

    @field_validator('setup_instructions')
    @classmethod
    def validate_ascii(cls, v):
        return validate_ascii(v)


class ExecutionContract(BaseModel):
    """Input contract for Test Executor"""
    model_config = ConfigDict(validate_assignment=True)

    code_artifacts: List[CodeArtifact]
    config: ExecutionConfig = Field(default_factory=ExecutionConfig)
    test_filter: Optional[str] = None
    environment_variables: Dict[str, str] = Field(default_factory=dict)


class ExecutionResult(BaseModel):
    """Output from Test Executor"""
    model_config = ConfigDict(validate_assignment=True)

    total_tests: int
    passed: int
    failed: int
    skipped: int
    execution_time: float
    test_results: List[TestResult] = Field(default_factory=list)
    coverage_report: Optional[Dict[str, Any]] = None
    artifacts: Dict[str, str] = Field(default_factory=dict)  # screenshots, logs, etc.
    error_summary: List[str] = Field(default_factory=list)


# ==============================================================================
# ELEMENT MODELS
# ==============================================================================

class ElementSelector(BaseModel):
    """Multiple selector strategies for an element"""
    model_config = ConfigDict(validate_assignment=True)

    css: Optional[str] = None
    xpath: Optional[str] = None
    accessibility: Optional[str] = None  # ARIA selector
    text: Optional[str] = None
    id: Optional[str] = None
    data_testid: Optional[str] = None

    @field_validator('css', 'xpath', 'accessibility', 'text', 'id', 'data_testid')
    @classmethod
    def validate_selectors(cls, v):
        return validate_ascii(v) if v else v


class Element(BaseModel):
    """Base element model"""
    model_config = ConfigDict(validate_assignment=True)

    tag_name: str
    element_type: ElementType
    selectors: ElementSelector
    text_content: Optional[str] = None
    attributes: Dict[str, str] = Field(default_factory=dict)
    is_visible: bool = Field(default=True)
    is_clickable: bool = Field(default=False)
    is_editable: bool = Field(default=False)
    is_focusable: bool = Field(default=False)
    bounding_box: Optional[Dict[str, float]] = None
    parent_selector: Optional[str] = None
    children_count: int = Field(default=0)

    @field_validator('tag_name', 'text_content', 'parent_selector')
    @classmethod
    def validate_ascii_fields(cls, v):
        return validate_ascii(v) if v else v


class ElementContext(BaseModel):
    """Context information for an element"""
    model_config = ConfigDict(validate_assignment=True)

    semantic_role: str = Field(default="unknown")
    page_section: str = Field(default="main")
    interaction_probability: float = Field(default=0.5, ge=0.0, le=1.0)
    accessibility_score: float = Field(default=0.5, ge=0.0, le=1.0)
    parent_chain: List[str] = Field(default_factory=list)
    related_elements: List[str] = Field(default_factory=list)

    @field_validator('semantic_role', 'page_section')
    @classmethod
    def validate_ascii_fields(cls, v):
        return validate_ascii(v)


class EnrichedElement(BaseModel):
    """Element enriched with AI insights"""
    model_config = ConfigDict(validate_assignment=True)

    base_element: Element
    context: ElementContext
    ai_insights: Dict[str, Any] = Field(default_factory=dict)
    test_relevance: float = Field(default=0.5, ge=0.0, le=1.0)
    suggested_tests: List[str] = Field(default_factory=list)
    potential_issues: List[str] = Field(default_factory=list)
    best_selector: str = ""
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0)

    @field_validator('best_selector')
    @classmethod
    def validate_selector(cls, v):
        return validate_ascii(v)


# ==============================================================================
# TEST MODELS
# ==============================================================================

class TestStep(BaseModel):
    """Single test step"""
    model_config = ConfigDict(validate_assignment=True)

    action: str  # click, type, select, assert, etc.
    target: str  # Element selector
    value: Optional[str] = None
    description: str = ""
    wait_before: int = Field(default=0, ge=0, le=10000, description="ms")
    wait_after: int = Field(default=0, ge=0, le=10000, description="ms")
    screenshot: bool = Field(default=False)
    optional: bool = Field(default=False)

    @field_validator('action', 'target', 'value', 'description')
    @classmethod
    def validate_ascii_fields(cls, v):
        return validate_ascii(v) if v else v


class TestAssertion(BaseModel):
    """Test assertion"""
    model_config = ConfigDict(validate_assignment=True)

    type: str  # equals, contains, visible, enabled, etc.
    target: str
    expected: Any
    message: str = ""
    soft: bool = Field(default=False, description="Continue on failure")

    @field_validator('type', 'target', 'message')
    @classmethod
    def validate_ascii_fields(cls, v):
        return validate_ascii(v) if isinstance(v, str) else v


class TestScenario(BaseModel):
    """Complete test scenario"""
    model_config = ConfigDict(validate_assignment=True)

    id: str
    name: str
    description: str
    category: TestCategory
    priority: TestPriority
    steps: List[TestStep]
    assertions: List[TestAssertion] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    test_data: Dict[str, Any] = Field(default_factory=dict)
    expected_results: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    estimated_duration: int = Field(default=60000, description="ms")
    flaky_threshold: int = Field(default=3, ge=1, le=10)

    @field_validator('id', 'name', 'description')
    @classmethod
    def validate_ascii_fields(cls, v):
        return validate_ascii(v)


class TestResult(BaseModel):
    """Result of a single test execution"""
    model_config = ConfigDict(validate_assignment=True)

    scenario_id: str
    status: ExecutionStatus
    duration: float  # seconds
    start_time: datetime
    end_time: datetime
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    screenshots: List[str] = Field(default_factory=list)
    logs: List[str] = Field(default_factory=list)
    retry_count: int = Field(default=0)

    @field_validator('error_message', 'stack_trace')
    @classmethod
    def validate_ascii_fields(cls, v):
        return validate_ascii(v) if v else v


# ==============================================================================
# PAGE ANALYSIS MODELS
# ==============================================================================

class PageInsights(BaseModel):
    """AI-generated page insights"""
    model_config = ConfigDict(validate_assignment=True)

    page_type: PageType
    detected_framework: Optional[str] = None
    functionality: List[str] = Field(default_factory=list)
    ui_patterns: List[str] = Field(default_factory=list)
    accessibility_level: str = Field(default="medium", pattern="^(low|medium|high)$")
    mobile_friendly: bool = Field(default=False)
    performance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    security_concerns: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

    @field_validator('detected_framework', 'accessibility_level')
    @classmethod
    def validate_ascii_fields(cls, v):
        return validate_ascii(v) if v else v


class PageAnalysis(BaseModel):
    """Complete page analysis"""
    model_config = ConfigDict(validate_assignment=True)

    url: str
    timestamp: datetime = Field(default_factory=datetime.now)
    page_insights: PageInsights
    total_elements: int
    interactive_elements: int
    form_elements: int = 0
    navigation_elements: int = 0
    media_elements: int = 0
    element_distribution: Dict[str, int] = Field(default_factory=dict)
    complexity_score: float = Field(default=0.5, ge=0.0, le=1.0)

    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        return validate_ascii(v)


# ==============================================================================
# PIPELINE RESULT MODEL
# ==============================================================================

class PipelineResult(BaseModel):
    """Complete pipeline execution result"""
    model_config = ConfigDict(validate_assignment=True)

    # Input
    url: str
    config: PipelineConfig

    # Stage results
    browser_result: BrowserResult
    element_result: ElementResult
    enriched_result: EnrichedResult
    test_suite: TestSuiteResult
    code_artifacts: List[CodeArtifact]
    execution_result: Optional[ExecutionResult] = None

    # Summary
    total_time: float
    stage_times: Dict[str, float] = Field(default_factory=dict)
    success: bool = Field(default=True)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    # Metrics
    metrics: Dict[str, Any] = Field(default_factory=dict)

    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        return validate_ascii(v)


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def serialize_to_json(obj: BaseModel) -> str:
    """Serialize Pydantic model to JSON with ASCII enforcement"""
    json_str = obj.model_dump_json(indent=2)
    # Final ASCII enforcement on output
    return enforce_ascii(json_str)


def deserialize_from_json(json_str: str, model_class: type[BaseModel]) -> BaseModel:
    """Deserialize JSON to Pydantic model with validation"""
    # Parse JSON and create model instance
    data = json.loads(json_str)
    return model_class(**data)


# ==============================================================================
# VALIDATION HELPERS
# ==============================================================================

class ModelValidator:
    """Utilities for validating models"""

    @staticmethod
    def validate_contract(contract: BaseModel) -> List[str]:
        """Validate a contract and return any errors"""
        errors = []
        try:
            contract.model_validate(contract.model_dump())
        except Exception as e:
            errors.append(str(e))
        return errors

    @staticmethod
    def ensure_ascii(obj: Any) -> Any:
        """Recursively ensure all strings in object are ASCII"""
        if isinstance(obj, str):
            return validate_ascii(obj)
        elif isinstance(obj, dict):
            return {k: ModelValidator.ensure_ascii(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [ModelValidator.ensure_ascii(item) for item in obj]
        elif isinstance(obj, BaseModel):
            data = obj.model_dump()
            cleaned = ModelValidator.ensure_ascii(data)
            return obj.__class__(**cleaned)
        return obj


# ==============================================================================
# CONSTANTS
# ==============================================================================

class SystemConstants:
    """System-wide constants"""

    # Thresholds
    SIMPLE_PAGE_THRESHOLD = 5
    MAX_ELEMENT_TEXT_LENGTH = 1000
    MAX_SELECTOR_LENGTH = 500

    # Timeouts (ms)
    DEFAULT_TIMEOUT = 30000
    ELEMENT_TIMEOUT = 5000
    PAGE_LOAD_TIMEOUT = 60000

    # Limits
    MAX_ELEMENTS_PER_PAGE = 1000
    MAX_SCENARIOS_PER_SUITE = 100
    MAX_STEPS_PER_SCENARIO = 50

    # Cache
    CACHE_TTL_DEFAULT = 3600
    CACHE_KEY_PREFIX = "web_automation"

    # File paths
    OUTPUT_DIR = "./output"
    SCREENSHOTS_DIR = "./screenshots"
    LOGS_DIR = "./logs"