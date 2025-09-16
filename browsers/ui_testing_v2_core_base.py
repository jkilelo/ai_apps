"""
Base component implementations
"""

import logging
from abc import ABC
from typing import Any, Dict, List, Optional

from .interfaces import (
    ElementExtractorInterface,
    TestGeneratorInterface,
    CodeGeneratorInterface,
    CodeExecutorInterface,
    AIServiceInterface,
    StorageInterface,
    CacheInterface,
    EventInterface,
)
from .exceptions import UITestingError
from ..models.common import (
    ElementData,
    TestCase,
    GeneratedCode,
    ExecutionResult,
    BrowserType,
    FrameworkType,
    LanguageType,
)

logger = logging.getLogger(__name__)


class BaseComponent(ABC):
    """Base class for all framework components"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self._initialized = False
        self._health_status = "unknown"
    
    async def initialize(self) -> None:
        """Initialize component"""
        if self._initialized:
            return
        
        logger.info(f"Initializing {self.__class__.__name__}")
        await self._initialize_impl()
        self._initialized = True
        self._health_status = "healthy"
        logger.info(f"{self.__class__.__name__} initialized successfully")
    
    async def cleanup(self) -> None:
        """Cleanup component resources"""
        if not self._initialized:
            return
        
        logger.info(f"Cleaning up {self.__class__.__name__}")
        await self._cleanup_impl()
        self._initialized = False
        self._health_status = "stopped"
        logger.info(f"{self.__class__.__name__} cleanup completed")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check component health"""
        base_health = {
            "component": self.__class__.__name__,
            "initialized": self._initialized,
            "status": self._health_status,
        }
        
        try:
            custom_health = await self._health_check_impl()
            return {**base_health, **custom_health}
        except Exception as e:
            return {
                **base_health,
                "status": "unhealthy",
                "error": str(e),
            }
    
    async def _initialize_impl(self) -> None:
        """Component-specific initialization"""
        pass
    
    async def _cleanup_impl(self) -> None:
        """Component-specific cleanup"""
        pass
    
    async def _health_check_impl(self) -> Dict[str, Any]:
        """Component-specific health check"""
        return {}


class BaseElementExtractor(BaseComponent, ElementExtractorInterface):
    """Base class for element extractors"""
    
    async def extract_elements(
        self,
        url: str,
        strategies: Optional[List[str]] = None,
        browser: Optional[BrowserType] = None,
        **kwargs: Any,
    ) -> List[ElementData]:
        """Extract elements from webpage"""
        if not self._initialized:
            raise UITestingError(f"{self.__class__.__name__} not initialized")
        
        return await self._extract_elements_impl(url, strategies, browser, **kwargs)
    
    async def _extract_elements_impl(
        self,
        url: str,
        strategies: Optional[List[str]] = None,
        browser: Optional[BrowserType] = None,
        **kwargs: Any,
    ) -> List[ElementData]:
        """Implementation-specific element extraction"""
        raise NotImplementedError


class BaseTestGenerator(BaseComponent, TestGeneratorInterface):
    """Base class for test generators"""
    
    async def generate_test_cases(
        self,
        elements: List[ElementData],
        requirements: Optional[str] = None,
        test_types: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[TestCase]:
        """Generate test cases from elements"""
        if not self._initialized:
            raise UITestingError(f"{self.__class__.__name__} not initialized")
        
        return await self._generate_test_cases_impl(elements, requirements, test_types, **kwargs)
    
    async def _generate_test_cases_impl(
        self,
        elements: List[ElementData],
        requirements: Optional[str] = None,
        test_types: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[TestCase]:
        """Implementation-specific test case generation"""
        raise NotImplementedError


class BaseCodeGenerator(BaseComponent, CodeGeneratorInterface):
    """Base class for code generators"""
    
    async def generate_code(
        self,
        test_cases: List[TestCase],
        framework: FrameworkType,
        language: LanguageType,
        **kwargs: Any,
    ) -> GeneratedCode:
        """Generate test code"""
        if not self._initialized:
            raise UITestingError(f"{self.__class__.__name__} not initialized")
        
        return await self._generate_code_impl(test_cases, framework, language, **kwargs)
    
    async def _generate_code_impl(
        self,
        test_cases: List[TestCase],
        framework: FrameworkType,
        language: LanguageType,
        **kwargs: Any,
    ) -> GeneratedCode:
        """Implementation-specific code generation"""
        raise NotImplementedError


class BaseCodeExecutor(BaseComponent, CodeExecutorInterface):
    """Base class for code executors"""
    
    async def execute_tests(
        self,
        generated_code: GeneratedCode,
        browsers: Optional[List[BrowserType]] = None,
        parallel: bool = True,
        **kwargs: Any,
    ) -> ExecutionResult:
        """Execute generated test code"""
        if not self._initialized:
            raise UITestingError(f"{self.__class__.__name__} not initialized")
        
        return await self._execute_tests_impl(generated_code, browsers, parallel, **kwargs)
    
    async def _execute_tests_impl(
        self,
        generated_code: GeneratedCode,
        browsers: Optional[List[BrowserType]] = None,
        parallel: bool = True,
        **kwargs: Any,
    ) -> ExecutionResult:
        """Implementation-specific test execution"""
        raise NotImplementedError


class BaseAIService(BaseComponent, AIServiceInterface):
    """Base class for AI/LLM services"""
    
    async def generate_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> str:
        """Generate AI response"""
        if not self._initialized:
            raise UITestingError(f"{self.__class__.__name__} not initialized")
        
        return await self._generate_response_impl(prompt, context, **kwargs)
    
    async def analyze_elements(
        self,
        elements: List[ElementData],
        context: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Analyze elements using AI"""
        if not self._initialized:
            raise UITestingError(f"{self.__class__.__name__} not initialized")
        
        return await self._analyze_elements_impl(elements, context, **kwargs)
    
    async def _generate_response_impl(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> str:
        """Implementation-specific response generation"""
        raise NotImplementedError
    
    async def _analyze_elements_impl(
        self,
        elements: List[ElementData],
        context: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Implementation-specific element analysis"""
        raise NotImplementedError


class BaseStorage(BaseComponent, StorageInterface):
    """Base class for storage backends"""
    
    async def save(self, key: str, data: Dict[str, Any]) -> bool:
        """Save data"""
        if not self._initialized:
            raise UITestingError(f"{self.__class__.__name__} not initialized")
        
        return await self._save_impl(key, data)
    
    async def load(self, key: str) -> Optional[Dict[str, Any]]:
        """Load data"""
        if not self._initialized:
            raise UITestingError(f"{self.__class__.__name__} not initialized")
        
        return await self._load_impl(key)
    
    async def delete(self, key: str) -> bool:
        """Delete data"""
        if not self._initialized:
            raise UITestingError(f"{self.__class__.__name__} not initialized")
        
        return await self._delete_impl(key)
    
    async def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """List keys"""
        if not self._initialized:
            raise UITestingError(f"{self.__class__.__name__} not initialized")
        
        return await self._list_keys_impl(prefix)
    
    async def _save_impl(self, key: str, data: Dict[str, Any]) -> bool:
        """Implementation-specific save"""
        raise NotImplementedError
    
    async def _load_impl(self, key: str) -> Optional[Dict[str, Any]]:
        """Implementation-specific load"""
        raise NotImplementedError
    
    async def _delete_impl(self, key: str) -> bool:
        """Implementation-specific delete"""
        raise NotImplementedError
    
    async def _list_keys_impl(self, prefix: Optional[str] = None) -> List[str]:
        """Implementation-specific list keys"""
        raise NotImplementedError


class BaseCache(BaseComponent, CacheInterface):
    """Base class for cache backends"""
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if not self._initialized:
            raise UITestingError(f"{self.__class__.__name__} not initialized")
        
        return await self._get_impl(key)
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set cached value"""
        if not self._initialized:
            raise UITestingError(f"{self.__class__.__name__} not initialized")
        
        return await self._set_impl(key, value, ttl)
    
    async def delete(self, key: str) -> bool:
        """Delete cached value"""
        if not self._initialized:
            raise UITestingError(f"{self.__class__.__name__} not initialized")
        
        return await self._delete_impl(key)
    
    async def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache"""
        if not self._initialized:
            raise UITestingError(f"{self.__class__.__name__} not initialized")
        
        return await self._clear_impl(pattern)
    
    async def _get_impl(self, key: str) -> Optional[Any]:
        """Implementation-specific get"""
        raise NotImplementedError
    
    async def _set_impl(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Implementation-specific set"""
        raise NotImplementedError
    
    async def _delete_impl(self, key: str) -> bool:
        """Implementation-specific delete"""
        raise NotImplementedError
    
    async def _clear_impl(self, pattern: Optional[str] = None) -> int:
        """Implementation-specific clear"""
        raise NotImplementedError


class BaseEventBus(BaseComponent, EventInterface):
    """Base class for event systems"""
    
    async def emit(self, event: str, data: Dict[str, Any]) -> None:
        """Emit event"""
        if not self._initialized:
            raise UITestingError(f"{self.__class__.__name__} not initialized")
        
        await self._emit_impl(event, data)
    
    async def subscribe(self, event: str, callback) -> str:
        """Subscribe to event"""
        if not self._initialized:
            raise UITestingError(f"{self.__class__.__name__} not initialized")
        
        return await self._subscribe_impl(event, callback)
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from event"""
        if not self._initialized:
            raise UITestingError(f"{self.__class__.__name__} not initialized")
        
        return await self._unsubscribe_impl(subscription_id)
    
    async def _emit_impl(self, event: str, data: Dict[str, Any]) -> None:
        """Implementation-specific emit"""
        raise NotImplementedError
    
    async def _subscribe_impl(self, event: str, callback) -> str:
        """Implementation-specific subscribe"""
        raise NotImplementedError
    
    async def _unsubscribe_impl(self, subscription_id: str) -> bool:
        """Implementation-specific unsubscribe"""
        raise NotImplementedError
