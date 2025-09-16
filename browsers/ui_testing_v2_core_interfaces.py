"""
Base interfaces and abstract classes for UI Testing Framework v2
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..models.common import (
    ElementData,
    TestCase,
    GeneratedCode,
    ExecutionResult,
    WorkflowResult,
    BrowserType,
    FrameworkType,
    LanguageType,
)


class BaseComponent(ABC):
    """Base component interface"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the component"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup component resources"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check component health"""
        pass


class ElementExtractorInterface(BaseComponent):
    """Interface for element extraction components"""
    
    @abstractmethod
    async def extract_elements(
        self,
        url: str,
        strategies: Optional[List[str]] = None,
        browser: Optional[BrowserType] = None,
        **kwargs: Any,
    ) -> List[ElementData]:
        """Extract elements from a webpage"""
        pass
    
    @abstractmethod
    async def extract_element_by_selector(
        self,
        url: str,
        selector: str,
        browser: Optional[BrowserType] = None,
        **kwargs: Any,
    ) -> Optional[ElementData]:
        """Extract a specific element by selector"""
        pass
    
    @abstractmethod
    async def validate_selectors(
        self,
        url: str,
        elements: List[ElementData],
        browser: Optional[BrowserType] = None,
    ) -> List[ElementData]:
        """Validate and update element selectors"""
        pass


class TestGeneratorInterface(BaseComponent):
    """Interface for test generation components"""
    
    @abstractmethod
    async def generate_test_cases(
        self,
        elements: List[ElementData],
        requirements: Optional[str] = None,
        test_types: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[TestCase]:
        """Generate test cases from elements"""
        pass
    
    @abstractmethod
    async def generate_test_data(
        self,
        test_case: TestCase,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate test data for a test case"""
        pass
    
    @abstractmethod
    async def optimize_test_suite(
        self,
        test_cases: List[TestCase],
        **kwargs: Any,
    ) -> List[TestCase]:
        """Optimize test suite for execution"""
        pass


class CodeGeneratorInterface(BaseComponent):
    """Interface for code generation components"""
    
    @abstractmethod
    async def generate_code(
        self,
        test_cases: List[TestCase],
        framework: FrameworkType,
        language: LanguageType,
        **kwargs: Any,
    ) -> GeneratedCode:
        """Generate test code for a framework"""
        pass
    
    @abstractmethod
    async def generate_page_objects(
        self,
        elements: List[ElementData],
        framework: FrameworkType,
        language: LanguageType,
        **kwargs: Any,
    ) -> Dict[str, str]:
        """Generate page object classes"""
        pass
    
    @abstractmethod
    async def validate_generated_code(
        self,
        generated_code: GeneratedCode,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Validate generated code syntax and structure"""
        pass


class CodeExecutorInterface(BaseComponent):
    """Interface for code execution components"""
    
    @abstractmethod
    async def execute_tests(
        self,
        generated_code: GeneratedCode,
        browsers: Optional[List[BrowserType]] = None,
        parallel: bool = True,
        **kwargs: Any,
    ) -> ExecutionResult:
        """Execute generated test code"""
        pass
    
    @abstractmethod
    async def execute_single_test(
        self,
        test_case: TestCase,
        browser: BrowserType,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute a single test case"""
        pass
    
    @abstractmethod
    async def get_execution_status(
        self,
        execution_id: str,
    ) -> Dict[str, Any]:
        """Get execution status"""
        pass


class AIServiceInterface(ABC):
    """Interface for AI service providers"""
    
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text using AI"""
        pass
    
    @abstractmethod
    async def analyze_image(
        self,
        image_path: str,
        prompt: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Analyze image using AI vision"""
        pass
    
    @abstractmethod
    async def extract_structured_data(
        self,
        text: str,
        schema: Dict[str, Any],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Extract structured data from text"""
        pass


class StorageInterface(ABC):
    """Interface for storage providers"""
    
    @abstractmethod
    async def save_file(
        self,
        file_path: str,
        content: bytes,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Save file and return URL"""
        pass
    
    @abstractmethod
    async def load_file(
        self,
        file_path: str,
    ) -> bytes:
        """Load file content"""
        pass
    
    @abstractmethod
    async def delete_file(
        self,
        file_path: str,
    ) -> bool:
        """Delete file"""
        pass
    
    @abstractmethod
    async def list_files(
        self,
        prefix: Optional[str] = None,
    ) -> List[str]:
        """List files with optional prefix"""
        pass


class CacheInterface(ABC):
    """Interface for cache providers"""
    
    @abstractmethod
    async def get(
        self,
        key: str,
    ) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set value in cache"""
        pass
    
    @abstractmethod
    async def delete(
        self,
        key: str,
    ) -> bool:
        """Delete value from cache"""
        pass
    
    @abstractmethod
    async def exists(
        self,
        key: str,
    ) -> bool:
        """Check if key exists"""
        pass


class EventInterface(ABC):
    """Interface for event handling"""
    
    @abstractmethod
    async def emit(
        self,
        event: str,
        data: Dict[str, Any],
    ) -> None:
        """Emit an event"""
        pass
    
    @abstractmethod
    async def subscribe(
        self,
        event: str,
        callback: callable,
    ) -> str:
        """Subscribe to an event"""
        pass
    
    @abstractmethod
    async def unsubscribe(
        self,
        subscription_id: str,
    ) -> bool:
        """Unsubscribe from an event"""
        pass
