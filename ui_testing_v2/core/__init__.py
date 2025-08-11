"""
UI Testing v2 Core Module
"""

from .base import (
    BaseComponent,
    BaseElementExtractor,
    BaseTestGenerator,
    BaseCodeGenerator,
    BaseCodeExecutor,
    BaseAIService,
    BaseStorage,
    BaseCache,
    BaseEventBus,
)
from .config import Settings, get_settings
from .exceptions import (
    UITestingError,
    ValidationError,
    ElementExtractionError,
    TestGenerationError,
    CodeGenerationError,
    CodeExecutionError,
    AIServiceError,
    StorageError,
    CacheError,
    ConfigurationError,
)
from .framework import UITestingFramework
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
from .logging import (
    setup_logging,
    get_logger,
    add_workflow_context,
    PerformanceLogger,
    SecurityLogger,
    framework_logger,
    element_logger,
    test_logger,
    code_logger,
    execution_logger,
)

__all__ = [
    # Base classes
    "BaseComponent",
    "BaseElementExtractor", 
    "BaseTestGenerator",
    "BaseCodeGenerator",
    "BaseCodeExecutor",
    "BaseAIService",
    "BaseStorage",
    "BaseCache",
    "BaseEventBus",
    
    # Configuration
    "Settings",
    "get_settings",
    
    # Exceptions
    "UITestingError",
    "ValidationError",
    "ElementExtractionError",
    "TestGenerationError", 
    "CodeGenerationError",
    "CodeExecutionError",
    "AIServiceError",
    "StorageError",
    "CacheError",
    "ConfigurationError",
    
    # Main framework
    "UITestingFramework",
    
    # Interfaces
    "ElementExtractorInterface",
    "TestGeneratorInterface",
    "CodeGeneratorInterface", 
    "CodeExecutorInterface",
    "AIServiceInterface",
    "StorageInterface",
    "CacheInterface",
    "EventInterface",
    
    # Logging
    "setup_logging",
    "get_logger",
    "add_workflow_context",
    "PerformanceLogger",
    "SecurityLogger",
    "framework_logger",
    "element_logger",
    "test_logger", 
    "code_logger",
    "execution_logger",
]
