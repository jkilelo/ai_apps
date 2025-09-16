"""
Custom exceptions for unified browser.

This module contains all custom exceptions used throughout the browser implementation,
providing specific error types for different failure scenarios.
"""

from __future__ import annotations

from typing import Any, Optional, Dict


# ============================================================================
# BASE EXCEPTIONS
# ============================================================================
class UnifiedBrowserError(Exception):
    """Base exception for all browser-related errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


# ============================================================================
# NAVIGATION EXCEPTIONS
# ============================================================================
class NavigationError(UnifiedBrowserError):
    """Raised when navigation fails."""

    def __init__(
        self, message: str, url: Optional[str] = None, status_code: Optional[int] = None, **kwargs
    ) -> None:
        if "error_code" not in kwargs:
            kwargs["error_code"] = "NAV_ERROR"
        super().__init__(message, **kwargs)
        self.url = url
        self.status_code = status_code
        if url:
            self.details["url"] = url
        if status_code:
            self.details["status_code"] = status_code


class TimeoutError(NavigationError):
    """Raised when operation times out."""

    def __init__(self, message: str, timeout_ms: Optional[int] = None, **kwargs) -> None:
        kwargs["error_code"] = "TIMEOUT"  # Set error_code in kwargs
        super().__init__(message, **kwargs)
        self.timeout_ms = timeout_ms
        if timeout_ms:
            self.details["timeout_ms"] = timeout_ms


class PageLoadError(NavigationError):
    """Raised when page fails to load properly."""

    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(message, error_code="PAGE_LOAD", **kwargs)


# ============================================================================
# EXTRACTION EXCEPTIONS
# ============================================================================
class ExtractionError(UnifiedBrowserError):
    """Raised when element extraction fails."""

    def __init__(self, message: str, selector: Optional[str] = None, **kwargs) -> None:
        super().__init__(message, error_code="EXTRACT_ERROR", **kwargs)
        self.selector = selector
        if selector:
            self.details["selector"] = selector


class ElementNotFoundError(ExtractionError):
    """Raised when element cannot be found."""

    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(message, error_code="ELEMENT_NOT_FOUND", **kwargs)


class ShadowDOMError(ExtractionError):
    """Raised when shadow DOM extraction fails."""

    def __init__(self, message: str, depth: Optional[int] = None, **kwargs) -> None:
        super().__init__(message, error_code="SHADOW_DOM", **kwargs)
        self.depth = depth
        if depth:
            self.details["depth"] = depth


class InvalidSelectorError(ExtractionError):
    """Raised when CSS selector or XPath is invalid."""

    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(message, error_code="INVALID_SELECTOR", **kwargs)


# ============================================================================
# STEALTH EXCEPTIONS
# ============================================================================
class StealthError(UnifiedBrowserError):
    """Raised when stealth operations fail."""

    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(message, error_code="STEALTH_ERROR", **kwargs)


class BotDetectionError(StealthError):
    """Raised when bot detection is triggered."""

    def __init__(self, message: str, detection_type: Optional[str] = None, **kwargs) -> None:
        super().__init__(message, error_code="BOT_DETECTED", **kwargs)
        self.detection_type = detection_type
        if detection_type:
            self.details["detection_type"] = detection_type


class CaptchaDetectedError(StealthError):
    """Raised when CAPTCHA is detected."""

    def __init__(self, message: str, captcha_type: Optional[str] = None, **kwargs) -> None:
        super().__init__(message, error_code="CAPTCHA", **kwargs)
        self.captcha_type = captcha_type
        if captcha_type:
            self.details["captcha_type"] = captcha_type


class FingerprintMismatchError(StealthError):
    """Raised when fingerprint inconsistency is detected."""

    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(message, error_code="FINGERPRINT_MISMATCH", **kwargs)


# ============================================================================
# SECURITY EXCEPTIONS
# ============================================================================
class SecurityError(UnifiedBrowserError):
    """Raised when security violation occurs."""

    def __init__(self, message: str, severity: str = "high", **kwargs) -> None:
        if "error_code" not in kwargs:
            kwargs["error_code"] = "SECURITY"
        super().__init__(message, **kwargs)
        self.severity = severity
        self.details["severity"] = severity


class ValidationError(SecurityError):
    """Raised when input validation fails."""

    def __init__(
        self, message: str, field: Optional[str] = None, value: Optional[Any] = None, **kwargs
    ) -> None:
        super().__init__(message, error_code="VALIDATION", **kwargs)
        self.field = field
        if field:
            self.details["field"] = field
        if value is not None:
            self.details["value"] = str(value)


class RateLimitError(SecurityError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str,
        limit: Optional[int] = None,
        window_seconds: Optional[int] = None,
        **kwargs,
    ) -> None:
        super().__init__(message, error_code="RATE_LIMIT", severity="medium", **kwargs)
        self.limit = limit
        self.window_seconds = window_seconds
        if limit:
            self.details["limit"] = limit
        if window_seconds:
            self.details["window_seconds"] = window_seconds


class PathTraversalError(SecurityError):
    """Raised when path traversal is attempted."""

    def __init__(self, message: str, path: Optional[str] = None, **kwargs) -> None:
        kwargs["error_code"] = "PATH_TRAVERSAL"  # Set error_code in kwargs
        super().__init__(message, severity="critical", **kwargs)
        if path:
            self.details["path"] = path


# ============================================================================
# AI/LLM EXCEPTIONS
# ============================================================================
class AIError(UnifiedBrowserError):
    """Raised when AI operations fail."""

    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(message, error_code="AI_ERROR", **kwargs)


class LLMConnectionError(AIError):
    """Raised when LLM connection fails."""

    def __init__(self, message: str, provider: Optional[str] = None, **kwargs) -> None:
        super().__init__(message, error_code="LLM_CONNECTION", **kwargs)
        self.provider = provider
        if provider:
            self.details["provider"] = provider


class LLMResponseError(AIError):
    """Raised when LLM response is invalid."""

    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(message, error_code="LLM_RESPONSE", **kwargs)


class VisionAnalysisError(AIError):
    """Raised when vision analysis fails."""

    def __init__(self, message: str, image_path: Optional[str] = None, **kwargs) -> None:
        super().__init__(message, error_code="VISION_ANALYSIS", **kwargs)
        if image_path:
            self.details["image_path"] = image_path


class TaskPlanningError(AIError):
    """Raised when task planning fails."""

    def __init__(self, message: str, task: Optional[str] = None, **kwargs) -> None:
        super().__init__(message, error_code="TASK_PLANNING", **kwargs)
        if task:
            self.details["task"] = task


# ============================================================================
# BROWSER STATE EXCEPTIONS
# ============================================================================
class BrowserStateError(UnifiedBrowserError):
    """Raised when browser is in invalid state."""

    def __init__(
        self,
        message: str,
        current_state: Optional[str] = None,
        expected_state: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(message, error_code="BROWSER_STATE", **kwargs)
        if current_state:
            self.details["current_state"] = current_state
        if expected_state:
            self.details["expected_state"] = expected_state


class BrowserNotInitializedError(BrowserStateError):
    """Raised when browser is not initialized."""

    def __init__(self, message: str = "Browser not initialized", **kwargs) -> None:
        super().__init__(message, error_code="NOT_INITIALIZED", **kwargs)


class BrowserClosedError(BrowserStateError):
    """Raised when attempting operations on closed browser."""

    def __init__(self, message: str = "Browser is closed", **kwargs) -> None:
        super().__init__(message, error_code="BROWSER_CLOSED", **kwargs)


# ============================================================================
# CONFIGURATION EXCEPTIONS
# ============================================================================
class ConfigurationError(UnifiedBrowserError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs) -> None:
        super().__init__(message, error_code="CONFIG_ERROR", **kwargs)
        if config_key:
            self.details["config_key"] = config_key


class InvalidConfigError(ConfigurationError):
    """Raised when configuration values are invalid."""

    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(message, error_code="INVALID_CONFIG", **kwargs)


class MissingConfigError(ConfigurationError):
    """Raised when required configuration is missing."""

    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(message, error_code="MISSING_CONFIG", **kwargs)


# ============================================================================
# PLUGIN EXCEPTIONS
# ============================================================================
class PluginError(UnifiedBrowserError):
    """Raised when plugin operations fail."""

    def __init__(self, message: str, plugin_name: Optional[str] = None, **kwargs) -> None:
        super().__init__(message, error_code="PLUGIN_ERROR", **kwargs)
        self.plugin_name = plugin_name
        if plugin_name:
            self.details["plugin_name"] = plugin_name


class PluginLoadError(PluginError):
    """Raised when plugin cannot be loaded."""

    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(message, error_code="PLUGIN_LOAD", **kwargs)


class PluginExecutionError(PluginError):
    """Raised when plugin execution fails."""

    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(message, error_code="PLUGIN_EXEC", **kwargs)


# ============================================================================
# PERFORMANCE EXCEPTIONS
# ============================================================================
class PerformanceError(UnifiedBrowserError):
    """Raised when performance issues occur."""

    def __init__(
        self,
        message: str,
        metric: Optional[str] = None,
        threshold: Optional[float] = None,
        actual: Optional[float] = None,
        **kwargs,
    ) -> None:
        super().__init__(message, error_code="PERFORMANCE", **kwargs)
        if metric:
            self.details["metric"] = metric
        if threshold is not None:
            self.details["threshold"] = threshold
        if actual is not None:
            self.details["actual"] = actual


class MemoryLimitError(PerformanceError):
    """Raised when memory limit is exceeded."""

    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(message, error_code="MEMORY_LIMIT", **kwargs)


class ResourceExhaustedError(PerformanceError):
    """Raised when resources are exhausted."""

    def __init__(self, message: str, resource_type: Optional[str] = None, **kwargs) -> None:
        super().__init__(message, error_code="RESOURCE_EXHAUSTED", **kwargs)
        if resource_type:
            self.details["resource_type"] = resource_type


# ============================================================================
# RECOVERY EXCEPTIONS
# ============================================================================
class RecoveryError(UnifiedBrowserError):
    """Raised when recovery attempts fail."""

    def __init__(
        self,
        message: str,
        attempts: Optional[int] = None,
        strategies_tried: Optional[list] = None,
        **kwargs,
    ) -> None:
        super().__init__(message, error_code="RECOVERY_FAILED", **kwargs)
        if attempts:
            self.details["attempts"] = attempts
        if strategies_tried:
            self.details["strategies_tried"] = strategies_tried


class UnrecoverableError(RecoveryError):
    """Raised when error cannot be recovered from."""

    def __init__(self, message: str, original_error: Optional[Exception] = None, **kwargs) -> None:
        super().__init__(message, error_code="UNRECOVERABLE", **kwargs)
        if original_error:
            self.details["original_error"] = str(original_error)
