"""
Common data models for the UI Testing Framework v2
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class StatusEnum(str, Enum):
    """Status enumeration for various operations"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class ElementType(str, Enum):
    """Types of UI elements"""
    BUTTON = "button"
    INPUT = "input"
    LINK = "link"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    IFRAME = "iframe"
    FORM = "form"
    TABLE = "table"
    LIST = "list"
    NAVIGATION = "navigation"
    HEADER = "header"
    FOOTER = "footer"
    SECTION = "section"
    ARTICLE = "article"
    ASIDE = "aside"
    UNKNOWN = "unknown"


class TestType(str, Enum):
    """Types of tests"""
    FUNCTIONAL = "functional"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    VISUAL = "visual"
    SECURITY = "security"
    USABILITY = "usability"
    COMPATIBILITY = "compatibility"
    NEGATIVE = "negative"
    EDGE_CASE = "edge_case"


class BrowserType(str, Enum):
    """Supported browser types"""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"
    CHROME = "chrome"
    EDGE = "edge"
    SAFARI = "safari"


class FrameworkType(str, Enum):
    """Supported test frameworks"""
    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    CYPRESS = "cypress"
    PUPPETEER = "puppeteer"
    TESTCAFE = "testcafe"


class LanguageType(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CSHARP = "csharp"


class SelectorType(str, Enum):
    """Types of element selectors"""
    CSS = "css"
    XPATH = "xpath"
    ID = "id"
    CLASS = "class"
    TAG = "tag"
    NAME = "name"
    LINK_TEXT = "link_text"
    PARTIAL_LINK_TEXT = "partial_link_text"
    TEXT = "text"


class ActionType(str, Enum):
    """Types of test actions"""
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
    SUBMIT = "submit"
    CLEAR = "clear"
    FOCUS = "focus"
    BLUR = "blur"


class PriorityEnum(str, Enum):
    """Test priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    TRIVIAL = "trivial"


class Coordinates(BaseModel):
    """Screen coordinates"""
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")


class Dimensions(BaseModel):
    """Element dimensions"""
    width: float = Field(..., ge=0, description="Width in pixels")
    height: float = Field(..., ge=0, description="Height in pixels")


class BoundingBox(BaseModel):
    """Element bounding box"""
    x: float = Field(..., description="X coordinate of top-left corner")
    y: float = Field(..., description="Y coordinate of top-left corner")
    width: float = Field(..., ge=0, description="Width in pixels")
    height: float = Field(..., ge=0, description="Height in pixels")


class ElementSelector(BaseModel):
    """Element selector information"""
    css: Optional[str] = Field(None, description="CSS selector")
    xpath: Optional[str] = Field(None, description="XPath selector")
    text: Optional[str] = Field(None, description="Text-based selector")
    aria_label: Optional[str] = Field(None, description="ARIA label selector")
    data_testid: Optional[str] = Field(None, description="Data test ID selector")
    role: Optional[str] = Field(None, description="ARIA role selector")
    priority: int = Field(default=0, description="Selector priority score")
    
    @validator("priority")
    def validate_priority(cls, v: int) -> int:
        return max(0, min(100, v))  # Clamp between 0-100


class ElementData(BaseModel):
    """Extracted element data"""
    id: str = Field(..., description="Unique element identifier")
    type: ElementType = Field(..., description="Element type")
    tag_name: str = Field(..., description="HTML tag name")
    text: Optional[str] = Field(None, description="Element text content")
    attributes: Dict[str, str] = Field(default_factory=dict, description="HTML attributes")
    selectors: List[ElementSelector] = Field(default_factory=list, description="Selectors")
    bounding_box: Optional[BoundingBox] = Field(None, description="Element bounding box")
    screenshot_path: Optional[str] = Field(None, description="Element screenshot path")
    accessibility: Dict[str, Any] = Field(default_factory=dict, description="Accessibility info")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Detection confidence")
    extraction_timestamp: datetime = Field(default_factory=datetime.now)
    
    def get_best_selector(self) -> Optional[ElementSelector]:
        """Get the highest priority selector"""
        if not self.selectors:
            return None
        return max(self.selectors, key=lambda s: s.priority)


class TestStep(BaseModel):
    """Individual test step"""
    id: str = Field(..., description="Step identifier")
    action: str = Field(..., description="Action to perform")
    target: Optional[str] = Field(None, description="Target element selector")
    value: Optional[str] = Field(None, description="Input value")
    expected: Optional[str] = Field(None, description="Expected result")
    timeout: Optional[int] = Field(None, description="Step timeout in seconds")
    retry_count: int = Field(default=0, description="Number of retries")
    description: Optional[str] = Field(None, description="Step description")


class TestCase(BaseModel):
    """Test case definition"""
    id: str = Field(..., description="Unique test case identifier")
    name: str = Field(..., description="Test case name")
    description: Optional[str] = Field(None, description="Test case description")
    type: TestType = Field(default=TestType.FUNCTIONAL, description="Test type")
    priority: int = Field(default=1, ge=1, le=5, description="Test priority (1=highest)")
    tags: List[str] = Field(default_factory=list, description="Test tags")
    steps: List[TestStep] = Field(default_factory=list, description="Test steps")
    setup_steps: List[TestStep] = Field(default_factory=list, description="Setup steps")
    cleanup_steps: List[TestStep] = Field(default_factory=list, description="Cleanup steps")
    data: Dict[str, Any] = Field(default_factory=dict, description="Test data")
    expected_result: Optional[str] = Field(None, description="Expected test result")
    timeout: int = Field(default=300, description="Test timeout in seconds")
    retry_count: int = Field(default=3, description="Retry attempts")
    browser_requirements: List[BrowserType] = Field(default_factory=list)
    framework: Optional[FrameworkType] = Field(None, description="Target framework")
    language: Optional[LanguageType] = Field(None, description="Target language")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class GeneratedCode(BaseModel):
    """Generated test code"""
    framework: FrameworkType = Field(..., description="Target framework")
    language: LanguageType = Field(..., description="Programming language")
    test_file: str = Field(..., description="Main test file content")
    support_files: Dict[str, str] = Field(default_factory=dict, description="Supporting files")
    dependencies: List[str] = Field(default_factory=list, description="Required dependencies")
    setup_commands: List[str] = Field(default_factory=list, description="Setup commands")
    run_commands: List[str] = Field(default_factory=list, description="Run commands")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Code metadata")


class TestResult(BaseModel):
    """Individual test execution result"""
    test_case_id: str = Field(..., description="Test case identifier")
    test_name: str = Field(..., description="Test name")
    status: StatusEnum = Field(..., description="Test execution status")
    start_time: datetime = Field(..., description="Test start time")
    end_time: Optional[datetime] = Field(None, description="Test end time")
    duration: Optional[float] = Field(None, description="Test duration in seconds")
    browser: Optional[BrowserType] = Field(None, description="Browser used")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    stack_trace: Optional[str] = Field(None, description="Stack trace if failed")
    screenshots: List[str] = Field(default_factory=list, description="Screenshot paths")
    video_path: Optional[str] = Field(None, description="Video recording path")
    logs: List[str] = Field(default_factory=list, description="Test execution logs")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")
    retry_count: int = Field(default=0, description="Number of retries performed")


class ExecutionResult(BaseModel):
    """Test execution session result"""
    session_id: str = Field(..., description="Execution session identifier")
    start_time: datetime = Field(..., description="Execution start time")
    end_time: Optional[datetime] = Field(None, description="Execution end time")
    duration: Optional[float] = Field(None, description="Total duration in seconds")
    status: StatusEnum = Field(..., description="Overall execution status")
    test_results: List[TestResult] = Field(default_factory=list, description="Individual test results")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Execution summary")
    environment: Dict[str, Any] = Field(default_factory=dict, description="Execution environment")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Execution configuration")
    artifacts: Dict[str, str] = Field(default_factory=dict, description="Generated artifacts")
    
    @property
    def total_tests(self) -> int:
        """Total number of tests"""
        return len(self.test_results)
    
    @property
    def passed_tests(self) -> int:
        """Number of passed tests"""
        return len([r for r in self.test_results if r.status == StatusEnum.COMPLETED])
    
    @property
    def failed_tests(self) -> int:
        """Number of failed tests"""
        return len([r for r in self.test_results if r.status == StatusEnum.FAILED])
    
    @property
    def success_rate(self) -> float:
        """Test success rate as percentage"""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100


class WorkflowResult(BaseModel):
    """Complete workflow execution result"""
    workflow_id: str = Field(..., description="Workflow identifier")
    start_time: datetime = Field(..., description="Workflow start time")
    end_time: Optional[datetime] = Field(None, description="Workflow end time")
    duration: Optional[float] = Field(None, description="Total duration in seconds")
    status: StatusEnum = Field(..., description="Overall workflow status")
    
    # Step results
    extraction_result: Optional[Dict[str, Any]] = Field(None, description="Element extraction result")
    generation_result: Optional[Dict[str, Any]] = Field(None, description="Test generation result")
    code_result: Optional[Dict[str, Any]] = Field(None, description="Code generation result")
    execution_result: Optional[ExecutionResult] = Field(None, description="Execution result")
    
    # Summary data
    total_elements: int = Field(default=0, description="Total elements extracted")
    total_test_cases: int = Field(default=0, description="Total test cases generated")
    total_code_files: int = Field(default=0, description="Total code files generated")
    
    # Metadata
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Workflow configuration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @property
    def success_rate(self) -> float:
        """Overall workflow success rate"""
        if self.execution_result:
            return self.execution_result.success_rate
        return 0.0


class JobStatus(BaseModel):
    """Background job status"""
    job_id: str = Field(..., description="Job identifier")
    status: StatusEnum = Field(..., description="Job status")
    progress: float = Field(default=0.0, ge=0.0, le=100.0, description="Progress percentage")
    message: Optional[str] = Field(None, description="Status message")
    result: Optional[Dict[str, Any]] = Field(None, description="Job result")
    error: Optional[str] = Field(None, description="Error message")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = Field(None, description="Job start time")
    completed_at: Optional[datetime] = Field(None, description="Job completion time")
