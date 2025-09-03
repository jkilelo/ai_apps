#!/usr/bin/env python3
"""
NEXUS Browser Exception Module.

Task: ENV-004
Provides a comprehensive exception hierarchy with structured error handling.
Full compliance with mypy --strict, flake8, and 100% type coverage.
Uses Pydantic v2 for error details and validation.
"""

from typing import Optional, Dict, Any, List, Final
from enum import Enum
from traceback import format_tb
import sys
from pydantic import BaseModel, Field, field_validator, ConfigDict


class ErrorSeverity(str, Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Error categorization."""

    CONFIGURATION = "configuration"
    VALIDATION = "validation"
    NETWORK = "network"
    FILESYSTEM = "filesystem"
    QUANTUM = "quantum"
    HOLOGRAPHIC = "holographic"
    EVOLUTION = "evolution"
    CONSCIOUSNESS = "consciousness"
    MCP = "mcp"
    INTEGRATION = "integration"
    SECURITY = "security"
    PERFORMANCE = "performance"
    UNKNOWN = "unknown"


class ErrorContext(BaseModel):
    """Structured error context information."""

    model_config = ConfigDict(frozen=True)

    task_id: Optional[str] = None
    phase: Optional[str] = None
    module: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    correlation_id: Optional[str] = None
    user_message: Optional[str] = None
    technical_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("line_number")
    @classmethod
    def validate_line_number(cls, v: Optional[int]) -> Optional[int]:
        """Validate line number is positive."""
        if v is not None and v <= 0:
            raise ValueError("Line number must be positive")
        return v


class ErrorDetails(BaseModel):
    """Detailed error information."""

    model_config = ConfigDict(frozen=True)

    error_code: str = Field(min_length=1, max_length=50)
    category: ErrorCategory
    severity: ErrorSeverity
    message: str = Field(min_length=1)
    context: Optional[ErrorContext] = None
    cause: Optional[str] = None
    suggestions: List[str] = Field(default_factory=list)
    traceback: Optional[List[str]] = None
    timestamp: Optional[str] = None

    @field_validator("error_code")
    @classmethod
    def validate_error_code(cls, v: str) -> str:
        """Validate error code format."""
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Error code must be alphanumeric with - or _")
        return v.upper()


class NexusException(Exception):
    """
    Base exception for all NEXUS Browser errors.

    Provides structured error information with context and suggestions.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "NEXUS-001",
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        """Initialize NEXUS exception with structured details."""
        super().__init__(message)

        # Extract traceback if available
        tb_list: Optional[List[str]] = None
        if sys.exc_info()[2]:
            tb_list = format_tb(sys.exc_info()[2])

        self.details = ErrorDetails(
            error_code=error_code,
            category=category,
            severity=severity,
            message=message,
            context=context,
            cause=str(cause) if cause else None,
            suggestions=suggestions or [],
            traceback=tb_list,
        )
        self.cause = cause

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return self.details.model_dump()

    def add_suggestion(self, suggestion: str) -> None:
        """Add a suggestion for resolving the error."""
        # Create a new details object since it's frozen
        current_dict = self.details.model_dump()
        current_dict["suggestions"].append(suggestion)
        self.details = ErrorDetails(**current_dict)


# Specific exception classes


class ConfigurationError(NexusException):
    """Configuration-related errors."""

    def __init__(
        self,
        message: str,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize configuration error."""
        super().__init__(
            message=message,
            error_code="CONFIG-001",
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            context=context,
            cause=cause,
            suggestions=[
                "Check configuration file syntax",
                "Verify environment variables are set",
                "Ensure configuration file exists and is readable",
            ],
        )


class ValidationError(NexusException):
    """Data validation errors."""

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        invalid_value: Optional[Any] = None,
        context: Optional[ErrorContext] = None,
    ) -> None:
        """Initialize validation error."""
        if field_name:
            message = f"{message} (field: {field_name})"

        super().__init__(
            message=message,
            error_code="VALID-001",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            context=context,
            suggestions=[
                "Check input data format",
                "Verify data types match expected schema",
                "Ensure required fields are present",
            ],
        )


class NetworkError(NexusException):
    """Network and connectivity errors."""

    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize network error."""
        if url:
            message = f"{message} (URL: {url})"
        if status_code:
            message = f"{message} [Status: {status_code}]"

        super().__init__(
            message=message,
            error_code="NET-001",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            context=context,
            cause=cause,
            suggestions=[
                "Check network connectivity",
                "Verify the URL is correct",
                "Check firewall and proxy settings",
                "Retry the operation",
            ],
        )


class FileSystemError(NexusException):
    """File system operation errors."""

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        operation: Optional[str] = None,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize file system error."""
        if file_path:
            message = f"{message} (Path: {file_path})"
        if operation:
            message = f"{message} [Operation: {operation}]"

        super().__init__(
            message=message,
            error_code="FS-001",
            category=ErrorCategory.FILESYSTEM,
            severity=ErrorSeverity.MEDIUM,
            context=context,
            cause=cause,
            suggestions=[
                "Check file/directory permissions",
                "Verify the path exists",
                "Ensure sufficient disk space",
                "Check file is not locked by another process",
            ],
        )


class QuantumError(NexusException):
    """Quantum module specific errors."""

    def __init__(
        self,
        message: str,
        quantum_state: Optional[str] = None,
        context: Optional[ErrorContext] = None,
    ) -> None:
        """Initialize quantum error."""
        if quantum_state:
            message = f"{message} (State: {quantum_state})"

        super().__init__(
            message=message,
            error_code="QUA-001",
            category=ErrorCategory.QUANTUM,
            severity=ErrorSeverity.HIGH,
            context=context,
            suggestions=[
                "Check quantum state coherence",
                "Verify entanglement parameters",
                "Review quantum circuit configuration",
            ],
        )


class SecurityError(NexusException):
    """Security-related errors."""

    def __init__(
        self,
        message: str,
        security_context: Optional[str] = None,
        context: Optional[ErrorContext] = None,
    ) -> None:
        """Initialize security error."""
        super().__init__(
            message=message,
            error_code="SEC-001",
            category=ErrorCategory.SECURITY,
            severity=ErrorSeverity.CRITICAL,
            context=context,
            suggestions=[
                "Verify authentication credentials",
                "Check authorization permissions",
                "Review security configuration",
                "Contact system administrator",
            ],
        )


class IntegrationError(NexusException):
    """Module integration errors."""

    def __init__(
        self,
        message: str,
        source_module: Optional[str] = None,
        target_module: Optional[str] = None,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize integration error."""
        if source_module and target_module:
            message = f"{message} ({source_module} -> {target_module})"

        super().__init__(
            message=message,
            error_code="INT-001",
            category=ErrorCategory.INTEGRATION,
            severity=ErrorSeverity.HIGH,
            context=context,
            cause=cause,
            suggestions=[
                "Check module compatibility",
                "Verify interface contracts",
                "Review module dependencies",
                "Ensure proper initialization order",
            ],
        )


# Error handling utilities


def create_error_context(
    task_id: Optional[str] = None,
    phase: Optional[str] = None,
    module: Optional[str] = None,
    **kwargs: Any,
) -> ErrorContext:
    """
    Create an error context with common fields.

    Args:
        task_id: Current task identifier
        phase: Current phase
        module: Current module
        **kwargs: Additional context fields

    Returns:
        ErrorContext: Structured error context
    """
    return ErrorContext(
        task_id=task_id,
        phase=phase,
        module=module,
        metadata=kwargs,
    )


def handle_exception(
    exc: Exception,
    context: Optional[ErrorContext] = None,
    reraise: bool = True,
) -> Optional[ErrorDetails]:
    """
    Handle an exception with structured error reporting.

    Args:
        exc: The exception to handle
        context: Optional error context
        reraise: Whether to re-raise the exception

    Returns:
        Optional[ErrorDetails]: Error details if not re-raising

    Raises:
        Exception: The original or wrapped exception if reraise=True
    """
    if isinstance(exc, NexusException):
        error_details = exc.details
    else:
        # Wrap in NexusException
        nexus_exc = NexusException(
            message=str(exc),
            error_code="GENERIC-001",
            category=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.MEDIUM,
            context=context,
            cause=exc,
        )
        error_details = nexus_exc.details

    if reraise:
        if isinstance(exc, NexusException):
            raise exc
        else:
            raise nexus_exc

    return error_details


# Module constants
TASK_ID: Final[str] = "ENV-004"
MODULE_NAME: Final[str] = "exceptions"
QUALITY_ENFORCED: Final[bool] = True


if __name__ == "__main__":
    print(f"[EXCEPTIONS] NEXUS Browser Exception Module (Task: {TASK_ID})")
    print(f"[EXCEPTIONS] Quality Enforcement: {QUALITY_ENFORCED}")

    # Test exception creation
    context = create_error_context(
        task_id=TASK_ID,
        phase="ENV-000",
        module=MODULE_NAME,
    )

    # Test different exception types
    config_error = ConfigurationError(
        "Configuration file not found",
        context=context,
    )

    print("\n[EXCEPTIONS] Example error details:")
    print(f"  Code: {config_error.details.error_code}")
    print(f"  Category: {config_error.details.category.value}")
    print(f"  Severity: {config_error.details.severity.value}")
    print(f"  Suggestions: {len(config_error.details.suggestions)} available")

    print("\n[EXCEPTIONS] Module initialized successfully")
