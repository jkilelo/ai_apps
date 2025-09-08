"""
Core foundation module for unified browser.

This module provides the foundational layer (Layer 0) containing constants,
types, exceptions, and utilities used throughout the browser implementation.
"""

from __future__ import annotations

# Version info
__version__ = "1.0.0"
__author__ = "Unified Browser Team"

# Import all constants
from .constants import *

# Import all types
from .types import (
    # Enums
    BrowserEngine,
    StealthLevel,
    ContentType,
    ExtractionMethod,
    ElementType,
    BrowserState,
    NavigationStrategy,
    ExtractionStrategy,
    LLMProvider,
    CaptchaType,
    FrameworkType,
    # Dataclasses
    Point,
    BoundingBox,
    ElementData,
    ExtractionResult,
    NavigationResult,
    BrowserAction,
    TaskPlan,
    SecurityViolation,
    PerformanceMetrics,
    # Protocols
    BrowserProtocol,
    ExtractorProtocol,
    StealthInjectorProtocol,
    NavigatorProtocol,
    ValidatorProtocol,
    LLMClientProtocol,
    # Type aliases
    NavigationCallback,
    ExtractionCallback,
    ErrorCallback,
    ConfigDict,
    HeadersDict,
    CookiesDict,
    Selector,
    SelectorList,
    JSFunction,
    JSResult,
    Coordinates,
    CoordinatesList,
)

# Import all exceptions
from .exceptions import (
    # Base
    UnifiedBrowserError,
    # Navigation
    NavigationError,
    TimeoutError,
    PageLoadError,
    # Extraction
    ExtractionError,
    ElementNotFoundError,
    ShadowDOMError,
    InvalidSelectorError,
    # Stealth
    StealthError,
    BotDetectionError,
    CaptchaDetectedError,
    FingerprintMismatchError,
    # Security
    SecurityError,
    ValidationError,
    RateLimitError,
    PathTraversalError,
    # AI/LLM
    AIError,
    LLMConnectionError,
    LLMResponseError,
    VisionAnalysisError,
    TaskPlanningError,
    # Browser State
    BrowserStateError,
    BrowserNotInitializedError,
    BrowserClosedError,
    # Configuration
    ConfigurationError,
    InvalidConfigError,
    MissingConfigError,
    # Plugin
    PluginError,
    PluginLoadError,
    PluginExecutionError,
    # Performance
    PerformanceError,
    MemoryLimitError,
    ResourceExhaustedError,
    # Recovery
    RecoveryError,
    UnrecoverableError,
)

# Import utilities
from .utils import (
    # Decorators
    retry_on_error,
    measure_time,
    validate_input,
    # Delay utilities
    human_delay,
    generate_typing_delays,
    generate_mouse_path,
    # Hash utilities
    generate_element_hash,
    generate_unique_id,
    # Validation
    validate_url,
    validate_selector,
    validate_path,
    sanitize_input,
    sanitize_filename,
    # String utilities
    truncate_text,
    extract_numbers,
    normalize_whitespace,
    camel_to_snake,
    snake_to_camel,
    # CSS/XPath utilities
    element_to_selector,
    element_to_xpath,
    # Async utilities
    run_with_timeout,
    gather_with_errors,
    # Rate limiting
    RateLimiter,
    # File utilities
    ensure_directory,
    safe_write_file,
    safe_read_file,
    # JSON utilities
    safe_json_loads,
    safe_json_dumps,
)

__all__ = [
    # Version
    "__version__",
    "__author__",
    # From constants (selected important ones)
    "DEFAULT_TIMEOUT",
    "DEFAULT_VIEWPORT_WIDTH",
    "DEFAULT_VIEWPORT_HEIGHT",
    "STEALTH_BROWSER_ARGS",
    "DEFAULT_USER_AGENTS",
    "INTERACTIVE_SELECTORS",
    "RUNTIME_ENABLE_BYPASS",
    "NODRIVER_MODE",
    # From types
    "BrowserEngine",
    "StealthLevel",
    "ContentType", 
    "ExtractionMethod",
    "ElementType",
    "BrowserState",
    "NavigationStrategy",
    "ExtractionStrategy",
    "LLMProvider",
    "CaptchaType",
    "FrameworkType",
    "Point",
    "BoundingBox",
    "ElementData",
    "ExtractionResult",
    "NavigationResult",
    "BrowserAction",
    "TaskPlan",
    "SecurityViolation",
    "PerformanceMetrics",
    "BrowserProtocol",
    "ExtractorProtocol",
    "StealthInjectorProtocol",
    "NavigatorProtocol",
    "ValidatorProtocol",
    "LLMClientProtocol",
    # From exceptions
    "UnifiedBrowserError",
    "NavigationError",
    "TimeoutError",
    "ExtractionError",
    "ElementNotFoundError",
    "StealthError",
    "BotDetectionError",
    "SecurityError",
    "ValidationError",
    "AIError",
    "LLMConnectionError",
    "BrowserStateError",
    "ConfigurationError",
    "PluginError",
    # From utils
    "retry_on_error",
    "measure_time",
    "human_delay",
    "generate_typing_delays",
    "generate_mouse_path",
    "generate_element_hash",
    "validate_url",
    "validate_selector",
    "validate_path",
    "sanitize_input",
    "element_to_selector",
    "element_to_xpath",
    "run_with_timeout",
    "RateLimiter",
]
