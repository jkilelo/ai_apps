#!/usr/bin/env python3
"""
Pipeline Contracts - Pydantic 2 Models for End-to-End Test Generation Flow
===========================================================================

This module defines strict input/output contracts for the entire test generation pipeline:
1. Element extraction using LLM
2. Gherkin test cases generation using LLM  
3. Playwright Python code generation using LLM
4. Code execution

Each contract enforces data structure consistency to ensure smooth integration.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime
from enum import Enum

# Import core element extraction types from the single source of truth
from elements_extractor_no_llm import (
    ElementType,
    ExtractedElement,
    ExtractionResult as ElementExtractionOutput
)


# =============================================================================
# COMMON ENUMS (ElementType imported from elements_extractor_no_llm)
# =============================================================================


class TestStatus(str, Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestType(str, Enum):
    """Types of tests"""
    FUNCTIONAL = "functional"
    REGRESSION = "regression"
    SMOKE = "smoke"
    E2E = "e2e"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    SECURITY = "security"


# =============================================================================
# STEP 1: ELEMENT EXTRACTION CONTRACTS (Using elements_extractor_no_llm)
# =============================================================================
# ExtractedElement and ElementExtractionOutput are imported from elements_extractor_no_llm


# =============================================================================
# STEP 2: TEST GENERATION CONTRACTS
# =============================================================================

class GherkinStep(BaseModel):
    """Single Gherkin step"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    keyword: Literal["Given", "When", "Then", "And", "But"] = Field(..., description="Gherkin keyword")
    text: str = Field(..., min_length=1, description="Step description")
    data_table: Optional[List[Dict[str, str]]] = Field(None, description="Data table if needed")
    element_selector: Optional[str] = Field(None, description="Related element selector")
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Ensure text is not empty"""
        if not v or not v.strip():
            raise ValueError("Step text cannot be empty")
        return v.strip()


class GherkinScenario(BaseModel):
    """Single Gherkin scenario"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: str = Field(..., min_length=1, description="Scenario name")
    description: Optional[str] = Field(None, description="Scenario description")
    tags: List[str] = Field(default_factory=list, description="Scenario tags")
    steps: List[GherkinStep] = Field(..., min_items=1, description="Scenario steps")
    test_type: TestType = Field(TestType.FUNCTIONAL, description="Type of test")
    priority: Literal["high", "medium", "low"] = Field("medium", description="Test priority")
    
    @field_validator('steps')
    @classmethod
    def validate_steps(cls, v: List[GherkinStep]) -> List[GherkinStep]:
        """Ensure at least one Given, When, Then"""
        keywords = {step.keyword for step in v}
        if not {"Given", "When", "Then"}.issubset(keywords | {"And", "But"}):
            # Allow And/But to substitute
            has_given = any(s.keyword in ["Given", "And", "But"] for s in v[:2])
            has_when = any(s.keyword in ["When", "And", "But"] for s in v[1:])
            has_then = any(s.keyword in ["Then", "And", "But"] for s in v[-2:])
            if not (has_given and has_when and has_then):
                raise ValueError("Scenario must have Given, When, and Then steps")
        return v


class TestGenerationOutput(BaseModel):
    """Output contract for Step 2: Test Generation"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    # Metadata
    feature_name: str = Field(..., min_length=1, description="Feature name")
    feature_description: str = Field(..., description="Feature description")
    timestamp: datetime = Field(default_factory=datetime.now, description="Generation time")
    
    # Input reference
    source_url: str = Field(..., description="Source page URL")
    elements_used: int = Field(0, ge=0, description="Number of elements used")
    
    # Generated content
    scenarios: List[GherkinScenario] = Field(..., min_items=1, description="Generated scenarios")
    
    # Statistics
    total_scenarios: int = Field(0, ge=0)
    total_steps: int = Field(0, ge=0)
    test_coverage: Dict[str, int] = Field(default_factory=dict, description="Coverage by test type")
    
    @model_validator(mode='after')
    def calculate_statistics(self):
        """Calculate statistics"""
        self.total_scenarios = len(self.scenarios)
        self.total_steps = sum(len(s.steps) for s in self.scenarios)
        self.test_coverage = {}
        for scenario in self.scenarios:
            test_type = scenario.test_type.value
            self.test_coverage[test_type] = self.test_coverage.get(test_type, 0) + 1
        return self


# =============================================================================
# STEP 3: CODE GENERATION CONTRACTS
# =============================================================================

class GeneratedTestMethod(BaseModel):
    """Single generated test method"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: str = Field(..., min_length=1, description="Method name")
    docstring: str = Field(..., description="Method docstring")
    code: str = Field(..., min_length=1, description="Method code")
    scenario_name: str = Field(..., description="Source scenario name")
    decorators: List[str] = Field(default_factory=list, description="Method decorators")
    
    @field_validator('name')
    @classmethod
    def validate_method_name(cls, v: str) -> str:
        """Ensure valid Python method name"""
        import re
        if not re.match(r'^test_[a-z_][a-z0-9_]*$', v):
            # Fix it
            v = "test_" + re.sub(r'[^a-z0-9_]', '_', v.lower())
        return v


class GeneratedPageObject(BaseModel):
    """Generated Page Object Model class"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    class_name: str = Field(..., min_length=1, description="Class name")
    imports: List[str] = Field(default_factory=list, description="Required imports")
    selectors: Dict[str, str] = Field(default_factory=dict, description="Element selectors")
    methods: List[str] = Field(default_factory=list, description="Page methods")
    code: str = Field(..., min_length=1, description="Complete POM code")


class CodeGenerationOutput(BaseModel):
    """Output contract for Step 3: Code Generation"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    # Metadata
    framework: Literal["pytest", "unittest"] = Field("pytest", description="Test framework")
    language: Literal["python"] = Field("python", description="Programming language")
    timestamp: datetime = Field(default_factory=datetime.now, description="Generation time")
    
    # Generated code components
    imports: List[str] = Field(default_factory=list, description="Required imports")
    fixtures: List[str] = Field(default_factory=list, description="Test fixtures")
    page_objects: List[GeneratedPageObject] = Field(default_factory=list, description="Page objects")
    test_methods: List[GeneratedTestMethod] = Field(..., min_items=1, description="Test methods")
    
    # Complete code
    full_code: str = Field(..., min_length=1, description="Complete executable code")
    
    # Dependencies
    requirements: List[str] = Field(
        default_factory=lambda: ["pytest", "pytest-playwright", "playwright"],
        description="Required packages"
    )
    
    # Validation
    is_syntactically_valid: bool = Field(False, description="Code syntax is valid")
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors")
    
    @model_validator(mode='after')
    def validate_syntax(self):
        """Validate Python syntax"""
        import ast
        try:
            ast.parse(self.full_code)
            self.is_syntactically_valid = True
            self.validation_errors = []
        except SyntaxError as e:
            self.is_syntactically_valid = False
            self.validation_errors = [f"Syntax error at line {e.lineno}: {e.msg}"]
        return self


# =============================================================================
# STEP 4: CODE EXECUTION CONTRACTS  
# =============================================================================

class TestExecutionResult(BaseModel):
    """Single test execution result"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    test_name: str = Field(..., description="Test name")
    status: TestStatus = Field(..., description="Test status")
    duration: float = Field(0.0, ge=0.0, description="Duration in seconds")
    
    # Output
    stdout: str = Field("", description="Standard output")
    stderr: str = Field("", description="Standard error")
    
    # Error details
    error_message: Optional[str] = Field(None, description="Error message if failed")
    stack_trace: Optional[str] = Field(None, description="Stack trace if error")
    
    # Artifacts
    screenshots: List[str] = Field(default_factory=list, description="Screenshot paths")
    logs: List[str] = Field(default_factory=list, description="Log file paths")


class CodeExecutionOutput(BaseModel):
    """Output contract for Step 4: Code Execution"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    # Metadata
    execution_id: str = Field(..., description="Unique execution ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Execution time")
    environment: Dict[str, str] = Field(default_factory=dict, description="Environment info")
    
    # Execution results
    test_results: List[TestExecutionResult] = Field(..., description="Individual test results")
    
    # Summary
    total_tests: int = Field(0, ge=0)
    passed: int = Field(0, ge=0)
    failed: int = Field(0, ge=0)
    skipped: int = Field(0, ge=0)
    errors: int = Field(0, ge=0)
    
    # Performance
    total_duration: float = Field(0.0, ge=0.0, description="Total execution time")
    success_rate: float = Field(0.0, ge=0.0, le=100.0, description="Success rate percentage")
    
    # Reports
    report_paths: Dict[str, str] = Field(default_factory=dict, description="Generated report paths")
    
    @model_validator(mode='after')
    def calculate_summary(self):
        """Calculate summary statistics"""
        self.total_tests = len(self.test_results)
        self.passed = sum(1 for t in self.test_results if t.status == TestStatus.PASSED)
        self.failed = sum(1 for t in self.test_results if t.status == TestStatus.FAILED)
        self.skipped = sum(1 for t in self.test_results if t.status == TestStatus.SKIPPED)
        self.errors = sum(1 for t in self.test_results if t.status == TestStatus.ERROR)
        self.total_duration = sum(t.duration for t in self.test_results)
        
        if self.total_tests > 0:
            self.success_rate = (self.passed / self.total_tests) * 100.0
        else:
            self.success_rate = 0.0
        
        return self


# =============================================================================
# COMPLETE PIPELINE CONTRACT
# =============================================================================

class PipelineInput(BaseModel):
    """Input for the complete pipeline"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    url: str = Field(..., min_length=1, description="Target URL to test")
    test_types: List[TestType] = Field(
        default_factory=lambda: [TestType.FUNCTIONAL],
        description="Types of tests to generate"
    )
    max_scenarios: int = Field(10, ge=1, le=100, description="Max scenarios to generate")
    execute_tests: bool = Field(True, description="Execute generated tests")
    generate_reports: bool = Field(True, description="Generate test reports")
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Ensure valid URL"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v


class PipelineOutput(BaseModel):
    """Output for the complete pipeline"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    # Pipeline metadata
    pipeline_id: str = Field(..., description="Unique pipeline execution ID")
    start_time: datetime = Field(..., description="Pipeline start time")
    end_time: datetime = Field(..., description="Pipeline end time")
    total_duration: float = Field(0.0, ge=0.0, description="Total pipeline duration")
    
    # Step outputs
    extraction_output: ElementExtractionOutput = Field(..., description="Step 1 output")
    test_generation_output: TestGenerationOutput = Field(..., description="Step 2 output")
    code_generation_output: CodeGenerationOutput = Field(..., description="Step 3 output")
    execution_output: Optional[CodeExecutionOutput] = Field(None, description="Step 4 output")
    
    # Overall status
    pipeline_status: Literal["success", "partial", "failed"] = Field(..., description="Pipeline status")
    errors: List[str] = Field(default_factory=list, description="Pipeline errors")
    
    @model_validator(mode='after')
    def determine_status(self):
        """Determine overall pipeline status"""
        if self.errors:
            self.pipeline_status = "failed"
        elif self.execution_output and self.execution_output.success_rate >= 90:
            self.pipeline_status = "success"
        elif self.execution_output and self.execution_output.success_rate >= 50:
            self.pipeline_status = "partial"
        elif not self.execution_output:
            self.pipeline_status = "partial"
        else:
            self.pipeline_status = "failed"
        return self