#!/usr/bin/env python3
"""
Data contracts for UI Testing Framework pipeline (Steps 1-4)
Using Pydantic v2 for robust validation and serialization

Each step has clearly defined input and output contracts to ensure
data integrity across the pipeline.
"""
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ============================================================================
# COMMON ENUMS AND TYPES
# ============================================================================

class TestStatus(str, Enum):
    """Test execution status"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    PENDING = "pending"


class FileType(str, Enum):
    """Generated file types"""
    TEST = "test"
    PAGE_OBJECT = "page_object"
    FIXTURE = "fixture"
    DATA_PROVIDER = "data_provider"
    CONFIG = "config"


# ============================================================================
# STEP 1: ELEMENT EXTRACTION CONTRACTS
# ============================================================================

class ExtractedElement(BaseModel):
    """
    Contract for a single extracted element
    Compatible with Step 1's ElementData but with clear contract
    """
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields from ElementData
    
    # Required fields
    tag_name: str = Field(..., description="HTML tag name")
    element_type: str = Field(..., description="Element type (button, input, etc)")
    xpath: str = Field(..., description="XPath selector")
    css_selector: str = Field(..., description="CSS selector")
    
    # Optional content fields
    text_content: str = Field(default="", description="Visible text content")
    id: Optional[str] = Field(default=None, description="Element ID")
    class_names: List[str] = Field(default_factory=list, description="CSS classes")
    name: Optional[str] = Field(default=None, description="Name attribute")
    href: Optional[str] = Field(default=None, description="Link href")
    src: Optional[str] = Field(default=None, description="Image/script src")
    alt: Optional[str] = Field(default=None, description="Alt text")
    title: Optional[str] = Field(default=None, description="Title attribute")
    
    # State fields
    is_clickable: bool = Field(default=False, description="Is element clickable")
    is_visible: bool = Field(default=True, description="Is element visible")
    is_enabled: bool = Field(default=True, description="Is element enabled")
    
    # Accessibility fields
    role: Optional[str] = Field(default=None, description="ARIA role")
    aria_label: Optional[str] = Field(default=None, description="ARIA label")
    placeholder: Optional[str] = Field(default=None, description="Input placeholder")
    value: Optional[str] = Field(default=None, description="Input value")
    input_type: Optional[str] = Field(default=None, description="Input type")
    
    # Metadata
    interaction_type: str = Field(default="unknown", description="Type of interaction")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence")
    
    @field_validator('confidence_score')
    @classmethod
    def validate_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Confidence score must be between 0 and 1')
        return v


class ElementExtraction(BaseModel):
    """
    Output contract for Step 1: Element Extraction
    Input: URL
    Output: This contract
    """
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    # Required fields
    url: str = Field(..., description="URL that was extracted")
    timestamp: str = Field(..., description="ISO timestamp of extraction")
    success: bool = Field(..., description="Whether extraction succeeded")
    
    # Extracted data
    elements: List[ExtractedElement] = Field(default_factory=list, description="Extracted elements")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    extraction_time: Optional[float] = Field(default=None, description="Time taken in seconds")
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


# ============================================================================
# STEP 2: GHERKIN GENERATION CONTRACTS
# ============================================================================

class GherkinStep(BaseModel):
    """A single Gherkin step"""
    keyword: str = Field(..., description="Step keyword (Given/When/Then/And/But)")
    text: str = Field(..., description="Step text")
    parameters: List[str] = Field(default_factory=list, description="Step parameters")
    
    @field_validator('keyword')
    @classmethod
    def validate_keyword(cls, v):
        valid = ['Given', 'When', 'Then', 'And', 'But']
        if v not in valid:
            raise ValueError(f'Keyword must be one of {valid}')
        return v


class GherkinScenario(BaseModel):
    """A Gherkin scenario"""
    name: str = Field(..., description="Scenario name")
    steps: List[GherkinStep] = Field(..., description="Scenario steps")
    tags: List[str] = Field(default_factory=list, description="Scenario tags")
    examples: Optional[Dict[str, List]] = Field(default=None, description="Data table for scenario outline")


class GherkinFeature(BaseModel):
    """A complete Gherkin feature"""
    name: str = Field(..., description="Feature name")
    description: str = Field(default="", description="Feature description")
    scenarios: List[Union[GherkinScenario, Dict[str, Any]]] = Field(..., description="Feature scenarios")
    background: Optional[List[GherkinStep]] = Field(default=None, description="Background steps")
    tags: List[str] = Field(default_factory=list, description="Feature tags")


class GherkinGeneration(BaseModel):
    """
    Output contract for Step 2: Gherkin Generation
    Input: ElementExtraction
    Output: This contract
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Required fields
    source_url: str = Field(..., description="Source URL from Step 1")
    timestamp: str = Field(..., description="ISO timestamp of generation")
    success: bool = Field(..., description="Whether generation succeeded")
    
    # Generated data
    features: List[GherkinFeature] = Field(default_factory=list, description="Generated features")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    generation_time: Optional[float] = Field(default=None, description="Time taken in seconds")
    llm_model: Optional[str] = Field(default=None, description="LLM model used")


# ============================================================================
# STEP 3: CODE GENERATION CONTRACTS
# ============================================================================

class GeneratedFile(BaseModel):
    """A generated test file"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = Field(..., description="File name")
    path: Path = Field(..., description="File path")
    content: str = Field(..., description="File content")
    file_type: FileType = Field(..., description="Type of file")
    size_bytes: Optional[int] = Field(default=None, description="File size")
    
    def save(self) -> None:
        """Save file to disk"""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(self.content)
        self.size_bytes = len(self.content)


class CodeGeneration(BaseModel):
    """
    Output contract for Step 3: Code Generation
    Input: GherkinGeneration
    Output: This contract
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Required fields
    source_features: List[GherkinFeature] = Field(..., description="Source features from Step 2")
    timestamp: str = Field(..., description="ISO timestamp of generation")
    success: bool = Field(..., description="Whether generation succeeded")
    
    # Generated data
    files: List[GeneratedFile] = Field(default_factory=list, description="Generated files")
    
    # Configuration
    test_framework: str = Field(default="pytest", description="Test framework used")
    language: str = Field(default="python", description="Programming language")
    browser_framework: Optional[str] = Field(default="playwright", description="Browser automation framework")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    generation_time: Optional[float] = Field(default=None, description="Time taken in seconds")
    total_tests: Optional[int] = Field(default=None, description="Total test cases generated")


# ============================================================================
# STEP 4: TEST EXECUTION CONTRACTS
# ============================================================================

class TestResult(BaseModel):
    """Result of a single test"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    test_name: str = Field(..., description="Test name")
    test_file: Path = Field(..., description="Test file path")
    status: TestStatus = Field(..., description="Test status")
    duration: float = Field(..., ge=0, description="Duration in seconds")
    
    # Optional details
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    stack_trace: Optional[str] = Field(default=None, description="Stack trace if failed")
    screenshots: List[str] = Field(default_factory=list, description="Screenshot paths")
    logs: List[str] = Field(default_factory=list, description="Log messages")
    retries: int = Field(default=0, ge=0, description="Number of retries")


class ExecutionResult(BaseModel):
    """
    Output contract for Step 4: Test Execution
    Input: CodeGeneration
    Output: This contract
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Required fields
    test_files: List[Path] = Field(..., description="Test files executed")
    timestamp: str = Field(..., description="ISO timestamp of execution")
    success: bool = Field(..., description="Whether execution succeeded")
    
    # Results
    results: List[TestResult] = Field(default_factory=list, description="Individual test results")
    summary: Dict[str, int] = Field(..., description="Summary statistics")
    
    # Reports
    reports: Dict[str, Path] = Field(default_factory=dict, description="Generated report paths")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    execution_time: Optional[float] = Field(default=None, description="Total time taken in seconds")
    environment: Optional[str] = Field(default="test", description="Execution environment")
    
    @field_validator('summary')
    @classmethod
    def validate_summary(cls, v):
        required_keys = {'total', 'passed', 'failed', 'skipped'}
        if not required_keys.issubset(v.keys()):
            raise ValueError(f'Summary must contain keys: {required_keys}')
        return v


# ============================================================================
# PIPELINE CONTRACTS
# ============================================================================

class PipelineInput(BaseModel):
    """Input contract for the entire pipeline"""
    urls: List[str] = Field(..., min_length=1, description="URLs to test")
    config: Dict[str, Any] = Field(default_factory=dict, description="Pipeline configuration")
    
    @field_validator('urls')
    @classmethod
    def validate_urls(cls, v):
        for url in v:
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f'Invalid URL: {url}')
        return v


class PipelineOutput(BaseModel):
    """Output contract for the entire pipeline"""
    input: PipelineInput = Field(..., description="Original input")
    step1_results: List[ElementExtraction] = Field(..., description="Step 1 results")
    step2_results: List[GherkinGeneration] = Field(..., description="Step 2 results")
    step3_results: CodeGeneration = Field(..., description="Step 3 results")
    step4_results: ExecutionResult = Field(..., description="Step 4 results")
    
    success: bool = Field(..., description="Overall pipeline success")
    total_time: float = Field(..., ge=0, description="Total pipeline time")
    
    def save_results(self, output_dir: Path) -> None:
        """Save all results to directory"""
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "pipeline_results.json").write_text(
            self.model_dump_json(indent=2)
        )