#!/usr/bin/env python3
"""

# AI-FIRST: This module requires live LLM connections, no mock support
SHARED MODULE - Shared Libraries and Data Contracts for UI Testing Automation
Implements data contracts, async helpers, and common types
Part of PHASE2 implementation following QUANTUM_ENHANCED_PROMPT specifications
"""

import sys
import asyncio
import logging
from typing import List, Dict, Any, Optional, Union, Callable, TypeVar, Generic
from pathlib import Path
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict, field
from pydantic import BaseModel, Field, ConfigDict, field_validator
import json
import time
import hashlib

# Import utils for shared functionality
from utils import Logger, PlatformUtils
__all__ = ['AsyncioConfig', 'ComponentStatus', 'TestStatus', 'FileType', 'ElementType', 'InteractionType', 'ExtractedElement', 'ElementExtractionContract', 'ElementExtractionResult', 'GherkinStep', 'GherkinScenario', 'GherkinFeature', 'GherkinGenerationContract', 'GherkinGenerationResult', 'GeneratedFile', 'CodeGenerationResult', 'TestStatus', 'ExecutionMode', 'CodeExecutionContract', 'TestResult', 'CodeExecutionResult']



# ============================================================================
# ASYNCIO CONFIGURATION (Python 3.13+ Compatibility)
# ============================================================================

class AsyncioConfig:
    """Asyncio configuration for cross-platform compatibility"""
    
    _configured = False
    
    @classmethod
    def setup_event_loop_policy(cls):
        """Setup the correct asyncio event loop policy for the current platform"""
        if cls._configured:
            return
        
        logger = Logger.get_logger("AsyncioConfig")
        
        if sys.platform == 'win32':
            # Windows requires special handling
            if sys.version_info >= (3, 13):
                # Python 3.13+ on Windows needs ProactorEventLoop for subprocesses
                try:
                    loop = asyncio.get_running_loop()
                    if not isinstance(loop, asyncio.ProactorEventLoop):
                        logger.warning("Current loop is not ProactorEventLoop, setting policy")
                        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                except RuntimeError:
                    # No running loop, set the policy for future loops
                    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                    logger.info("Set Windows ProactorEventLoop policy for Python 3.13+")
            elif sys.version_info >= (3, 8):
                # Python 3.8-3.12 on Windows
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                logger.info("Set Windows ProactorEventLoop policy")
        else:
            # Unix-like systems
            try:
                # Try to use uvloop for better performance
                import uvloop
                asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
                logger.info("Using uvloop for better performance")
            except ImportError:
                # Use default policy
                pass
        
        cls._configured = True
    
    @classmethod
    def get_or_create_event_loop(cls) -> asyncio.AbstractEventLoop:
        """Get the current event loop or create a new one with the correct policy"""
        cls.setup_event_loop_policy()
        
        try:
            loop = asyncio.get_running_loop()
            
            # On Windows with Python 3.13+, verify it's the right type
            if sys.platform == 'win32' and sys.version_info >= (3, 13):
                if not isinstance(loop, asyncio.ProactorEventLoop):
                    logger = Logger.get_logger("AsyncioConfig")
                    logger.warning("Current loop is not ProactorEventLoop, creating new one")
                    raise RuntimeError("Need ProactorEventLoop")
            
            return loop
        except RuntimeError:
            # No running loop, create one with correct policy
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            logger = Logger.get_logger("AsyncioConfig")
            logger.info(f"Created new event loop: {type(loop).__name__}")
            return loop
    
    @classmethod
    def run_async(cls, coro):
        """Run an async coroutine with proper event loop configuration"""
        cls.setup_event_loop_policy()
        return asyncio.run(coro)


# Auto-configure on import
AsyncioConfig.setup_event_loop_policy()


# ============================================================================
# COMMON ENUMS AND TYPES
# ============================================================================

class ComponentStatus(str, Enum):
    """Component status for tracking"""
    INITIALIZED = "initialized"
    READY = "ready"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


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
    REPORT = "report"


class ElementType(str, Enum):
    """UI element types"""
    BUTTON = "button"
    INPUT = "input"
    LINK = "link"
    TEXT = "text"
    IMAGE = "image"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TEXTAREA = "textarea"
    FORM = "form"
    TABLE = "table"
    LIST = "list"
    NAVIGATION = "navigation"
    UNKNOWN = "unknown"


class InteractionType(str, Enum):
    """Element interaction types"""
    CLICK = "click"
    TYPE = "type"
    SELECT = "select"
    CHECK = "check"
    UNCHECK = "uncheck"
    HOVER = "hover"
    DRAG = "drag"
    DROP = "drop"
    SCROLL = "scroll"
    WAIT = "wait"
    ASSERT = "assert"


# ============================================================================
# DATA CONTRACTS - ELEMENT EXTRACTION
# ============================================================================

class ExtractedElement(BaseModel):
    """Contract for a single extracted element"""
    model_config = ConfigDict(extra="ignore")
    
    # Required fields
    tag_name: str = Field(..., description="HTML tag name")
    element_type: ElementType = Field(..., description="Element type")
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
    interaction_type: InteractionType = Field(default=InteractionType.CLICK, description="Type of interaction")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence")
    bounds: Optional[Dict[str, float]] = Field(default=None, description="Element bounding box")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata including validation, relationships, etc.")
    
    @field_validator('confidence_score')
    @classmethod
    def validate_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Confidence score must be between 0 and 1')
        return v


class ElementExtractionContract(BaseModel):
    """Input contract for element extraction"""
    url: str = Field(..., description="URL to extract elements from")
    extract_forms: bool = Field(default=True, description="Extract form elements")
    extract_buttons: bool = Field(default=True, description="Extract buttons")
    extract_links: bool = Field(default=True, description="Extract links")
    extract_inputs: bool = Field(default=True, description="Extract input fields")
    include_hidden: bool = Field(default=False, description="Include hidden elements")
    max_depth: int = Field(default=3, description="Maximum depth for nested elements")


class ElementExtractionResult(BaseModel):
    """Output contract for element extraction"""
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    # Required fields
    url: str = Field(..., description="URL that was extracted")
    timestamp: datetime = Field(default_factory=datetime.now, description="Extraction timestamp")
    success: bool = Field(..., description="Whether extraction succeeded")
    
    # Extracted data
    elements: List[ExtractedElement] = Field(default_factory=list, description="Extracted elements")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    extraction_time: Optional[float] = Field(default=None, description="Time taken in seconds")
    extraction_method: str = Field(default="unknown", description="Method used for extraction")
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


# ============================================================================
# DATA CONTRACTS - GHERKIN GENERATION
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
    scenarios: List[GherkinScenario] = Field(..., description="Feature scenarios")
    background: Optional[List[GherkinStep]] = Field(default=None, description="Background steps")
    tags: List[str] = Field(default_factory=list, description="Feature tags")


class GherkinGenerationContract(BaseModel):
    """Input contract for Gherkin generation"""
    elements: List[ExtractedElement] = Field(..., description="Extracted elements to generate tests for")
    feature_name: str = Field(..., description="Name of the feature")
    feature_description: Optional[str] = Field(default=None, description="Feature description")
    generate_negative_tests: bool = Field(default=True, description="Generate negative test cases")
    generate_edge_cases: bool = Field(default=True, description="Generate edge case tests")
    generate_security_tests: bool = Field(default=False, description="Generate security tests")
    max_scenarios: int = Field(default=20, description="Maximum scenarios to generate")


class GherkinGenerationResult(BaseModel):
    """Output contract for Gherkin generation"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Required fields
    source_url: str = Field(..., description="Source URL from extraction")
    timestamp: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    success: bool = Field(..., description="Whether generation succeeded")
    
    # Generated data
    features: List[GherkinFeature] = Field(default_factory=list, description="Generated features")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    generation_time: Optional[float] = Field(default=None, description="Time taken in seconds")
    llm_model: Optional[str] = Field(default=None, description="LLM model used")


# ============================================================================
# DATA CONTRACTS - CODE GENERATION
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


class CodeGenerationResult(BaseModel):
    """Output contract for code generation"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Required fields
    source_feature: str = Field(..., description="Source feature name")
    timestamp: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    success: bool = Field(..., description="Whether generation succeeded")
    
    # Generated files
    test_files: List[GeneratedFile] = Field(default_factory=list, description="Generated test files")
    page_objects: List[GeneratedFile] = Field(default_factory=list, description="Generated page objects")
    fixtures: List[GeneratedFile] = Field(default_factory=list, description="Generated fixtures")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    generation_time: Optional[float] = Field(default=None, description="Time taken in seconds")
    llm_model: Optional[str] = Field(default=None, description="LLM model used")
    framework: str = Field(default="pytest", description="Test framework used")


# ============================================================================
# DATA CONTRACTS - TEST EXECUTION
# ============================================================================

class TestStatus(str, Enum):
    """Test execution status"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    PENDING = "pending"


class ExecutionMode(str, Enum):
    """Code execution mode"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    CI_CD = "ci_cd"


class CodeExecutionContract(BaseModel):
    """Input contract for code execution"""
    code: Union[str, List[str]] = Field(..., description="Code to execute (single or multiple)")
    test_name: str = Field(..., description="Test name or suite name")
    framework: str = Field(default="pytest", description="Test framework")
    timeout: Optional[int] = Field(default=300, description="Timeout in seconds")
    environment: Optional[Dict[str, str]] = Field(default_factory=dict, description="Environment variables")
    dependencies: Optional[List[str]] = Field(default_factory=list, description="Required dependencies")


class TestResult(BaseModel):
    """Result of a single test execution"""
    test_name: str = Field(..., description="Test name")
    status: TestStatus = Field(..., description="Test status")
    execution_time: float = Field(default=0.0, description="Test execution time in seconds")
    output: str = Field(default="", description="Test output")
    error: str = Field(default="", description="Error message if failed")
    test_file: Optional[str] = Field(default="", description="Test file path")
    stack_trace: Optional[str] = Field(default=None, description="Stack trace if failed")
    artifacts: List[str] = Field(default_factory=list, description="Generated artifacts")


class CodeExecutionResult(BaseModel):
    """Output contract for code execution"""
    success: bool = Field(..., description="Whether execution succeeded")
    results: List[TestResult] = Field(default_factory=list, description="Test results")
    total_tests: int = Field(default=0, description="Total number of tests")
    passed_tests: int = Field(default=0, description="Number of passed tests")
    failed_tests: int = Field(default=0, description="Number of failed tests")
    execution_time: float = Field(..., description="Total execution time")
    reports: Dict[str, str] = Field(default_factory=dict, description="Generated reports")
    metrics: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Execution metrics")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class TestExecutionResult(BaseModel):
    """Output contract for test execution"""
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    # Required fields
    test_suite: str = Field(..., description="Test suite name")
    timestamp: datetime = Field(default_factory=datetime.now, description="Execution timestamp")
    success: bool = Field(..., description="Whether all tests passed")
    
    # Test results
    results: List[TestResult] = Field(default_factory=list, description="Individual test results")
    
    # Statistics
    total_tests: int = Field(default=0, description="Total number of tests")
    passed: int = Field(default=0, description="Number of passed tests")
    failed: int = Field(default=0, description="Number of failed tests")
    skipped: int = Field(default=0, description="Number of skipped tests")
    error: int = Field(default=0, description="Number of tests with errors")
    
    # Metadata
    execution_time: float = Field(..., description="Total execution time in seconds")
    report_path: Optional[Path] = Field(default=None, description="Path to HTML report")
    coverage: Optional[float] = Field(default=None, description="Code coverage percentage")


# ============================================================================
# SHARED BASE CLASSES
# ============================================================================

T = TypeVar('T')

class SingletonMeta(type):
    """Metaclass for singleton pattern"""
    _instances = {}
    
    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class BaseComponent(metaclass=SingletonMeta):
    """Base class for framework components"""
    
    def __init__(self, name: str) -> None:
        self.name = name
        self.status = ComponentStatus.INITIALIZED
        self.logger = Logger.get_logger(name)
        self._start_time = None
        
    async def initialize(self) -> None:
        """Initialize the component"""
        self.logger.info(f"Initializing {self.name}")
        self.status = ComponentStatus.READY
        
    async def start(self):
        """Start the component"""
        self.logger.info(f"Starting {self.name}")
        self._start_time = time.time()
        self.status = ComponentStatus.RUNNING
        
    async def stop(self):
        """Stop the component"""
        self.logger.info(f"Stopping {self.name}")
        if self._start_time:
            duration = time.time() - self._start_time
            self.logger.info(f"{self.name} ran for {duration:.2f} seconds")
        self.status = ComponentStatus.STOPPED
        
    def get_status(self) -> ComponentStatus:
        """Get component status"""
        return self.status


# ============================================================================
# SHARED UTILITIES
# ============================================================================

class DataValidator:
    """Validate data contracts between components"""
    
    @staticmethod
    def validate_extraction_to_gherkin(extraction: ElementExtractionResult) -> bool:
        """Validate data can flow from extraction to Gherkin generation"""
        if not extraction.success:
            return False
        if not extraction.elements:
            return False
        return True
    
    @staticmethod
    def validate_gherkin_to_code(gherkin: GherkinGenerationResult) -> bool:
        """Validate data can flow from Gherkin to code generation"""
        if not gherkin.success:
            return False
        if not gherkin.features:
            return False
        return True
    
    @staticmethod
    def validate_code_to_execution(code: CodeGenerationResult) -> bool:
        """Validate data can flow from code generation to execution"""
        if not code.success:
            return False
        if not code.test_files:
            return False
        return True


class ContractSerializer:
    """Serialize and deserialize data contracts"""
    
    @staticmethod
    def to_json(obj: BaseModel) -> str:
        """Serialize contract to JSON"""
        return obj.model_dump_json(indent=2)
    
    @staticmethod
    def from_json(json_str: str, model_class: type[BaseModel]) -> BaseModel:
        """Deserialize contract from JSON"""
        return model_class.model_validate_json(json_str)
    
    @staticmethod
    def to_dict(obj: BaseModel) -> Dict[str, Any]:
        """Convert contract to dictionary"""
        return obj.model_dump()
    
    @staticmethod
    def from_dict(data: Dict[str, Any], model_class: type[BaseModel]) -> BaseModel:
        """Create contract from dictionary"""
        return model_class.model_validate(data)


class ImportResolver:
    """Resolve imports and module paths"""
    
    @staticmethod
    def add_parent_to_path():
        """Add parent directory to Python path for imports"""
        current_dir = Path(__file__).parent
        parent_dir = current_dir.parent
        if str(parent_dir) not in sys.path:
            sys.path.insert(0, str(parent_dir))
    
    @staticmethod
    def resolve_module_path(module_name: str) -> Optional[Path]:
        """Resolve a module name to its file path"""
        try:
            import importlib.util
            spec = importlib.util.find_spec(module_name)
            if spec and spec.origin:
                return Path(spec.origin)
        except ImportError:
            pass
        return None


# ============================================================================
# SELF-TEST AND EXAMPLE USAGE
# ============================================================================

def run_self_test():
    """Run comprehensive self-test of shared module"""
    logger = Logger.get_logger("SharedTest")
    logger.info("[TEST] Starting shared module self-test")
    
    results = {
        "asyncio_config": False,
        "data_contracts": False,
        "validation": False,
        "serialization": False,
        "base_component": False
    }
    
    try:
        # Test Asyncio Configuration
        logger.info("[TEST] Testing Asyncio Configuration...")
        AsyncioConfig.setup_event_loop_policy()
        
        async def test_async():
            await asyncio.sleep(0.01)
            return True
        
        result = AsyncioConfig.run_async(test_async())
        assert result == True
        results["asyncio_config"] = True
        
        # Test Data Contracts
        logger.info("[TEST] Testing Data Contracts...")
        
        # Create element
        element = ExtractedElement(
            tag_name="button",
            element_type=ElementType.BUTTON,
            xpath="//button[@id='submit']",
            css_selector="#submit",
            text_content="Submit",
            id="submit",
            is_clickable=True
        )
        
        # Create extraction result
        extraction = ElementExtractionResult(
            url="https://example.com",
            success=True,
            elements=[element]
        )
        
        assert extraction.success
        assert len(extraction.elements) == 1
        results["data_contracts"] = True
        
        # Test Validation
        logger.info("[TEST] Testing Data Validation...")
        assert DataValidator.validate_extraction_to_gherkin(extraction)
        results["validation"] = True
        
        # Test Serialization
        logger.info("[TEST] Testing Serialization...")
        json_str = ContractSerializer.to_json(extraction)
        restored = ContractSerializer.from_json(json_str, ElementExtractionResult)
        assert restored.url == extraction.url
        assert len(restored.elements) == len(extraction.elements)
        results["serialization"] = True
        
        # Test Base Component
        logger.info("[TEST] Testing Base Component...")
        
        class TestComponent(BaseComponent):
            pass
        
        async def test_component():
            comp = TestComponent("TestComponent")
            await comp.initialize()
            assert comp.status == ComponentStatus.READY
            await comp.start()
            assert comp.status == ComponentStatus.RUNNING
            await comp.stop()
            assert comp.status == ComponentStatus.STOPPED
            return True
        
        assert AsyncioConfig.run_async(test_component())
        results["base_component"] = True
        
    except Exception as e:
        logger.error(f"[TEST] Self-test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    # Report results
    logger.info("[TEST] Self-test Results:")
    all_passed = True
    for component, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        logger.info(f"  {status} {component}")
        if not passed:
            all_passed = False
    
    if all_passed:
        logger.info("[TEST] All tests passed successfully!")
    else:
        logger.error("[TEST] Some tests failed!")
    
    return all_passed


if __name__ == "__main__":
    # Quick test mode for compliance checking
    import os
    if os.environ.get("STANDALONE_TEST") == "1":
        print(f"[OK] {__name__} module loads successfully")
        sys.exit(0)
    
    print("=" * 60)
    print("UI TESTING AUTOMATION FRAMEWORK - SHARED MODULE")
    print("=" * 60)
    
    # Run self-test
    success = run_self_test()
    
    # Demo usage
    print("\n" + "=" * 60)
    print("DEMO: Example Usage")
    print("=" * 60)
    
    # Create sample element
    element = ExtractedElement(
        tag_name="input",
        element_type=ElementType.INPUT,
        xpath="//input[@name='email']",
        css_selector="input[name='email']",
        name="email",
        placeholder="Enter your email",
        input_type="email"
    )
    
    print(f"\nCreated Element:")
    print(f"  Type: {element.element_type.value}")
    print(f"  XPath: {element.xpath}")
    print(f"  Placeholder: {element.placeholder}")
    
    # Create extraction result
    extraction = ElementExtractionResult(
        url="https://example.com/login",
        success=True,
        elements=[element],
        extraction_time=0.5
    )
    
    print(f"\nExtraction Result:")
    print(f"  URL: {extraction.url}")
    print(f"  Success: {extraction.success}")
    print(f"  Elements: {len(extraction.elements)}")
    print(f"  Time: {extraction.extraction_time}s")
    
    # Serialize to JSON
    json_data = ContractSerializer.to_json(extraction)
    print(f"\nSerialized (first 200 chars):")
    print(json_data[:200] + "...")
    
    print("\n" + "=" * 60)
    if success:
        print("[SUCCESS] Shared module is ready for use!")
    else:
        print("[WARNING] Some tests failed - review logs above")
    print("=" * 60)