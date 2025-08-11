"""
UI Testing Framework v2
Modern AI-Powered UI Web Automation Testing Framework
"""

__version__ = "2.0.0"
__author__ = "UI Testing Team"
__email__ = "team@example.com"
__description__ = "Modern AI-Powered UI Web Automation Testing Framework"

# Core exports
from .core.framework import UITestingFramework
from .core.config import Settings, get_settings
from .core.exceptions import (
    UITestingError,
    ElementExtractionError,
    TestGenerationError,
    CodeGenerationError,
    CodeExecutionError,
)

# Component exports
from .components.element_extraction import ElementExtractor
from .components.test_generation import TestGenerator
from .components.code_generation import CodeGenerator
from .components.code_execution import CodeExecutor

# Model exports
from .models.common import (
    TestResult,
    ExecutionResult,
    WorkflowResult,
    ElementData,
    TestCase,
)

__all__ = [
    # Core
    "UITestingFramework",
    "Settings",
    "get_settings",
    
    # Components
    "ElementExtractor",
    "TestGenerator", 
    "CodeGenerator",
    "CodeExecutor",
    
    # Models
    "TestResult",
    "ExecutionResult",
    "WorkflowResult",
    "ElementData",
    "TestCase",
    
    # Exceptions
    "UITestingError",
    "ElementExtractionError",
    "TestGenerationError",
    "CodeGenerationError",
    "CodeExecutionError",
    
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__description__",
]
