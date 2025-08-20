"""
Core data models using Pydantic and dataclasses.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, HttpUrl, field_validator


class ElementCategory(str, Enum):
    """Categories for web elements."""
    NAVIGATION = "navigation"
    FORM_INPUT = "form_input"
    BUTTON = "button"
    LINK = "link"
    TEXT_DISPLAY = "text_display"
    MEDIA = "media"
    INTERACTIVE = "interactive"
    CONTAINER = "container"
    OTHER = "other"


class TestPriority(str, Enum):
    """Priority levels for test scenarios."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class InteractionPattern(str, Enum):
    """Common interaction patterns for elements."""
    CLICK = "click"
    TYPE = "type"
    SELECT = "select"
    HOVER = "hover"
    DRAG_DROP = "drag_drop"
    SCROLL = "scroll"
    UPLOAD = "upload"
    DOWNLOAD = "download"


class ValidationRule(str, Enum):
    """Validation rules for elements."""
    VISIBLE = "visible"
    ENABLED = "enabled"
    CONTAINS_TEXT = "contains_text"
    HAS_ATTRIBUTE = "has_attribute"
    HAS_CLASS = "has_class"
    URL_MATCHES = "url_matches"


@dataclass
class BrowserConfig:
    """Configuration for browser automation."""
    headless: bool = True
    stealth_level: str = "maximum"
    enable_stealth: bool = True
    enable_human_simulation: bool = True
    timeout: int = 30000
    navigation_timeout: int = 60000
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: Optional[str] = None
    extra_args: List[str] = field(default_factory=list)


class ExtractedElement(BaseModel):
    """Model for extracted web elements."""
    selector: str = Field(..., description="CSS selector for the element")
    tag_name: str = Field(..., description="HTML tag name")
    element_type: str = Field(..., description="Type of element (input, button, etc.)")
    category: ElementCategory = Field(..., description="Element category")
    priority: TestPriority = Field(default=TestPriority.MEDIUM, description="Test priority")
    
    # Element properties
    text: Optional[str] = Field(None, description="Visible text content")
    placeholder: Optional[str] = Field(None, description="Placeholder text")
    value: Optional[str] = Field(None, description="Input value")
    href: Optional[str] = Field(None, description="Link URL")
    src: Optional[str] = Field(None, description="Image/media source")
    
    # Visual properties
    visible: bool = Field(default=True, description="Whether element is visible")
    enabled: bool = Field(default=True, description="Whether element is enabled")
    x: int = Field(default=0, description="X coordinate")
    y: int = Field(default=0, description="Y coordinate")
    width: int = Field(default=0, description="Element width")
    height: int = Field(default=0, description="Element height")
    
    # Interaction properties
    clickable: bool = Field(default=False, description="Whether element is clickable")
    interaction_patterns: List[InteractionPattern] = Field(
        default_factory=list, 
        description="Possible interaction patterns"
    )
    
    # Testing properties
    description: Optional[str] = Field(None, description="Human-readable description")
    test_scenarios: List[str] = Field(default_factory=list, description="Suggested test scenarios")
    validation_rules: List[ValidationRule] = Field(
        default_factory=list,
        description="Validation rules to check"
    )
    
    # Metadata
    extracted_at: datetime = Field(default_factory=datetime.now, description="Extraction timestamp")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence")


class ExtractionRequest(BaseModel):
    """Request model for element extraction."""
    url: HttpUrl = Field(..., description="URL to extract elements from")
    headless: bool = Field(default=True, description="Run browser in headless mode")
    analyze_with_llm: bool = Field(default=True, description="Use LLM for element analysis")
    categories: Optional[List[ElementCategory]] = Field(
        None, 
        description="Filter by element categories"
    )
    
    @field_validator("url")
    @classmethod
    def validate_url(cls, v: HttpUrl) -> HttpUrl:
        """Validate URL format."""
        if not str(v).startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class ExtractionResponse(BaseModel):
    """Response model for element extraction."""
    success: bool = Field(..., description="Whether extraction succeeded")
    url: str = Field(..., description="Extracted URL")
    total_elements: int = Field(default=0, description="Total elements found")
    elements: List[ExtractedElement] = Field(default_factory=list, description="Extracted elements")
    elements_by_category: Dict[ElementCategory, List[ExtractedElement]] = Field(
        default_factory=dict,
        description="Elements grouped by category"
    )
    llm_analysis: Optional[Dict[str, Any]] = Field(None, description="LLM analysis results")
    extraction_time: float = Field(default=0.0, description="Time taken for extraction")
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TestScenario(BaseModel):
    """Model for test scenarios."""
    id: str = Field(..., description="Unique scenario ID")
    title: str = Field(..., description="Scenario title")
    description: str = Field(..., description="Detailed description")
    category: ElementCategory = Field(..., description="Element category")
    priority: TestPriority = Field(..., description="Test priority")
    
    # Test steps
    given: List[str] = Field(default_factory=list, description="Given conditions")
    when: List[str] = Field(default_factory=list, description="When actions")
    then: List[str] = Field(default_factory=list, description="Then assertions")
    
    # Element references
    target_elements: List[str] = Field(
        default_factory=list,
        description="Element selectors involved"
    )
    
    # Test properties
    estimated_duration: float = Field(default=30.0, description="Estimated test duration in seconds")
    dependencies: List[str] = Field(default_factory=list, description="Dependent scenario IDs")
    tags: List[str] = Field(default_factory=list, description="Test tags")


class GenerateTestsRequest(BaseModel):
    """Request model for test generation."""
    extraction_data: Dict[str, Any] = Field(..., description="Element extraction data")
    test_categories: Optional[List[ElementCategory]] = Field(
        None,
        description="Categories to generate tests for"
    )
    max_scenarios_per_category: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum scenarios per category"
    )
    priority_filter: Optional[List[TestPriority]] = Field(
        None,
        description="Filter by test priorities"
    )


class GenerateTestsResponse(BaseModel):
    """Response model for test generation."""
    success: bool = Field(..., description="Whether generation succeeded")
    url: str = Field(..., description="Target URL")
    scenarios: List[TestScenario] = Field(default_factory=list, description="Generated scenarios")
    scenarios_by_category: Dict[ElementCategory, List[TestScenario]] = Field(
        default_factory=dict,
        description="Scenarios grouped by category"
    )
    total_scenarios: int = Field(default=0, description="Total scenarios generated")
    generation_time: float = Field(default=0.0, description="Time taken for generation")
    statistics: Dict[str, Any] = Field(default_factory=dict, description="Generation statistics")
    error: Optional[str] = Field(None, description="Error message if failed")


class CodeGenerationRequest(BaseModel):
    """Request model for code generation."""
    extraction_data: Dict[str, Any] = Field(..., description="Element extraction data")
    test_data: Dict[str, Any] = Field(..., description="Test scenarios data")
    code_type: str = Field(default="pytest", description="Type of code to generate")
    language: str = Field(default="python", description="Programming language")
    framework: str = Field(default="playwright", description="Testing framework")
    
    @field_validator("code_type")
    @classmethod
    def validate_code_type(cls, v: str) -> str:
        """Validate code type."""
        allowed_types = ["pytest", "playwright", "selenium", "cypress"]
        if v not in allowed_types:
            raise ValueError(f"Code type must be one of {allowed_types}")
        return v


class GeneratedFile(BaseModel):
    """Model for generated code files."""
    filepath: str = Field(..., description="Relative file path")
    content: str = Field(..., description="File content")
    language: str = Field(default="python", description="Programming language")
    file_type: str = Field(..., description="Type of file (test, page_object, config, etc.)")
    line_count: int = Field(default=0, description="Number of lines in file")
    estimated_complexity: str = Field(default="medium", description="Estimated complexity")


class CodeGenerationResponse(BaseModel):
    """Response model for code generation."""
    success: bool = Field(..., description="Whether generation succeeded")
    url: str = Field(..., description="Target URL")
    generated_files: List[GeneratedFile] = Field(
        default_factory=list,
        description="Generated code files"
    )
    file_structure: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Project file structure"
    )
    total_files: int = Field(default=0, description="Total files generated")
    total_lines: int = Field(default=0, description="Total lines of code")
    generation_time: float = Field(default=0.0, description="Time taken for generation")
    statistics: Dict[str, Any] = Field(default_factory=dict, description="Generation statistics")
    error: Optional[str] = Field(None, description="Error message if failed")


@dataclass
class TestResult:
    """Result of test execution."""
    name: str
    status: str  # passed, failed, skipped
    duration: float
    message: Optional[str] = None
    screenshot_path: Optional[Path] = None
    error_trace: Optional[str] = None


class ExecuteTestsRequest(BaseModel):
    """Request model for test execution."""
    generated_files: List[GeneratedFile] = Field(..., description="Generated test files")
    url: str = Field(..., description="Target URL")
    test_type: str = Field(default="pytest", description="Test execution type")
    parallel: bool = Field(default=False, description="Run tests in parallel")
    browser_count: int = Field(default=1, ge=1, le=5, description="Number of browser instances")


class ExecuteTestsResponse(BaseModel):
    """Response model for test execution."""
    success: bool = Field(..., description="Whether execution succeeded")
    total_tests: int = Field(default=0, description="Total tests executed")
    passed: int = Field(default=0, description="Number of passed tests")
    failed: int = Field(default=0, description="Number of failed tests")
    skipped: int = Field(default=0, description="Number of skipped tests")
    duration: float = Field(default=0.0, description="Total execution time")
    test_results: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Detailed test results"
    )
    logs: List[str] = Field(default_factory=list, description="Execution logs")
    artifacts: Dict[str, str] = Field(
        default_factory=dict,
        description="Generated artifacts (screenshots, reports, etc.)"
    )
    error: Optional[str] = Field(None, description="Error message if failed")