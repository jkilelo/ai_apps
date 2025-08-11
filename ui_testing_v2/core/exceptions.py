"""
Core exceptions for the UI Testing Framework v2
"""

from typing import Any, Dict, Optional


class UITestingError(Exception):
    """Base exception for all UI Testing Framework errors"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        super().__init__(message)
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ElementExtractionError(UITestingError):
    """Raised when element extraction fails"""
    
    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        selector: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        context = kwargs.get("context", {})
        if url:
            context["url"] = url
        if selector:
            context["selector"] = selector
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class TestGenerationError(UITestingError):
    """Raised when test generation fails"""
    
    def __init__(
        self,
        message: str,
        test_type: Optional[str] = None,
        element_count: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        context = kwargs.get("context", {})
        if test_type:
            context["test_type"] = test_type
        if element_count is not None:
            context["element_count"] = element_count
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class CodeGenerationError(UITestingError):
    """Raised when code generation fails"""
    
    def __init__(
        self,
        message: str,
        framework: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        context = kwargs.get("context", {})
        if framework:
            context["framework"] = framework
        if language:
            context["language"] = language
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class CodeExecutionError(UITestingError):
    """Raised when code execution fails"""
    
    def __init__(
        self,
        message: str,
        test_name: Optional[str] = None,
        browser: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        context = kwargs.get("context", {})
        if test_name:
            context["test_name"] = test_name
        if browser:
            context["browser"] = browser
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class ConfigurationError(UITestingError):
    """Raised when configuration is invalid"""
    pass


class ValidationError(UITestingError):
    """Raised when data validation fails"""
    pass


class AIServiceError(UITestingError):
    """Raised when AI service interactions fail"""
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        context = kwargs.get("context", {})
        if provider:
            context["provider"] = provider
        if model:
            context["model"] = model
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class TimeoutError(UITestingError):
    """Raised when operations timeout"""
    
    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        context = kwargs.get("context", {})
        if timeout_seconds:
            context["timeout_seconds"] = timeout_seconds
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class RetryExhaustedError(UITestingError):
    """Raised when retry attempts are exhausted"""
    
    def __init__(
        self,
        message: str,
        max_retries: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        context = kwargs.get("context", {})
        if max_retries is not None:
            context["max_retries"] = max_retries
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class StorageError(UITestingError):
    """Raised when storage operations fail"""
    pass


class CacheError(UITestingError):
    """Raised when cache operations fail"""
    pass


class DatabaseError(UITestingError):
    """Raised when database operations fail"""
    pass
