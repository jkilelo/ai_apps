#!/usr/bin/env python3
"""
NEXUS Browser Validators Module.

Task: ENV-007
Comprehensive validation utilities for the NEXUS Browser system.
Full compliance with mypy --strict, flake8, and 100% type coverage.
Uses Pydantic v2 for all validation models.
"""

import re
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Final, Pattern
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from pydantic.types import conint, confloat, constr


# Module constants
TASK_ID: Final[str] = "ENV-007"
MODULE_NAME: Final[str] = "validators"
QUALITY_ENFORCED: Final[bool] = True


class ValidationType(str, Enum):
    """Types of validation operations."""

    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    BUSINESS = "business"
    SECURITY = "security"
    PERFORMANCE = "performance"


class ValidationSeverity(str, Enum):
    """Severity levels for validation issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


class ValidationIssue(BaseModel):
    """Single validation issue."""

    model_config = ConfigDict(frozen=True)

    field: str
    message: str
    severity: ValidationSeverity
    code: Optional[str] = None
    suggestion: Optional[str] = None
    value: Optional[Any] = None

    @field_validator("field")
    @classmethod
    def validate_field(cls, v: str) -> str:
        """Ensure field name is not empty."""
        if not v.strip():
            raise ValueError("Field name cannot be empty")
        return v


class ValidationResult(BaseModel):
    """Result of validation operation."""

    model_config = ConfigDict(frozen=True)

    is_valid: bool
    validation_type: ValidationType
    issues: List[ValidationIssue] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

    @model_validator(mode="after")
    def check_consistency(self) -> "ValidationResult":
        """Ensure is_valid matches issues."""
        has_errors = any(issue.severity == ValidationSeverity.ERROR for issue in self.issues)
        if has_errors and self.is_valid:
            raise ValueError("Cannot be valid with error-level issues")
        return self


class StringValidator(BaseModel):
    """String validation configuration."""

    model_config = ConfigDict(frozen=True)

    min_length: Optional[int] = Field(default=None, ge=0)
    max_length: Optional[int] = Field(default=None, ge=0)
    pattern: Optional[str] = None
    allowed_chars: Optional[str] = None
    forbidden_chars: Optional[str] = None
    must_contain: Optional[List[str]] = None
    must_not_contain: Optional[List[str]] = None
    case_sensitive: bool = Field(default=True)

    @model_validator(mode="after")
    def check_length_consistency(self) -> "StringValidator":
        """Ensure min_length <= max_length."""
        if self.min_length is not None and self.max_length is not None:
            if self.min_length > self.max_length:
                raise ValueError("min_length cannot be greater than max_length")
        return self


class NumberValidator(BaseModel):
    """Number validation configuration."""

    model_config = ConfigDict(frozen=True)

    min_value: Optional[float] = None
    max_value: Optional[float] = None
    must_be_integer: bool = Field(default=False)
    must_be_positive: bool = Field(default=False)
    must_be_negative: bool = Field(default=False)
    decimal_places: Optional[int] = Field(default=None, ge=0)
    multiples_of: Optional[float] = None

    @model_validator(mode="after")
    def check_consistency(self) -> "NumberValidator":
        """Check for logical consistency."""
        if self.must_be_positive and self.must_be_negative:
            raise ValueError("Cannot be both positive and negative")
        if self.min_value is not None and self.max_value is not None:
            if self.min_value > self.max_value:
                raise ValueError("min_value cannot be greater than max_value")
        return self


class DateTimeValidator(BaseModel):
    """DateTime validation configuration."""

    model_config = ConfigDict(frozen=True)

    min_date: Optional[datetime] = None
    max_date: Optional[datetime] = None
    must_be_future: bool = Field(default=False)
    must_be_past: bool = Field(default=False)
    date_format: Optional[str] = None
    timezone_required: bool = Field(default=False)

    @model_validator(mode="after")
    def check_consistency(self) -> "DateTimeValidator":
        """Check for logical consistency."""
        if self.must_be_future and self.must_be_past:
            raise ValueError("Cannot be both future and past")
        if self.min_date and self.max_date:
            if self.min_date > self.max_date:
                raise ValueError("min_date cannot be after max_date")
        return self


class FileValidator(BaseModel):
    """File validation configuration."""

    model_config = ConfigDict(frozen=True)

    must_exist: bool = Field(default=True)
    allowed_extensions: Optional[List[str]] = None
    forbidden_extensions: Optional[List[str]] = None
    max_size_bytes: Optional[int] = Field(default=None, ge=0)
    min_size_bytes: Optional[int] = Field(default=None, ge=0)
    mime_types: Optional[List[str]] = None
    check_readable: bool = Field(default=False)
    check_writable: bool = Field(default=False)


class JsonValidator(BaseModel):
    """JSON validation configuration."""

    model_config = ConfigDict(frozen=True)

    json_schema: Optional[Dict[str, Any]] = None
    required_fields: Optional[List[str]] = None
    forbidden_fields: Optional[List[str]] = None
    max_depth: Optional[int] = Field(default=None, ge=1)
    max_size_bytes: Optional[int] = Field(default=None, ge=0)
    strict_types: bool = Field(default=True)


def validate_string(value: str, validator: StringValidator) -> ValidationResult:
    """
    Validate a string value.

    Args:
        value: String to validate
        validator: Validation configuration

    Returns:
        ValidationResult: Validation result with any issues
    """
    issues: List[ValidationIssue] = []

    # Check length
    if validator.min_length is not None and len(value) < validator.min_length:
        issues.append(
            ValidationIssue(
                field="value",
                message=f"String length {len(value)} is below minimum {validator.min_length}",
                severity=ValidationSeverity.ERROR,
                code="STR_TOO_SHORT",
            )
        )

    if validator.max_length is not None and len(value) > validator.max_length:
        issues.append(
            ValidationIssue(
                field="value",
                message=f"String length {len(value)} exceeds maximum {validator.max_length}",
                severity=ValidationSeverity.ERROR,
                code="STR_TOO_LONG",
            )
        )

    # Check pattern
    if validator.pattern:
        pattern: Pattern[str] = re.compile(validator.pattern)
        if not pattern.match(value):
            issues.append(
                ValidationIssue(
                    field="value",
                    message=f"String does not match required pattern: {validator.pattern}",
                    severity=ValidationSeverity.ERROR,
                    code="STR_PATTERN_MISMATCH",
                )
            )

    # Check allowed chars
    if validator.allowed_chars:
        for char in value:
            if char not in validator.allowed_chars:
                issues.append(
                    ValidationIssue(
                        field="value",
                        message=f"Character '{char}' is not allowed",
                        severity=ValidationSeverity.ERROR,
                        code="STR_INVALID_CHAR",
                    )
                )
                break

    # Check forbidden chars
    if validator.forbidden_chars:
        for char in validator.forbidden_chars:
            if char in value:
                issues.append(
                    ValidationIssue(
                        field="value",
                        message=f"Forbidden character '{char}' found",
                        severity=ValidationSeverity.ERROR,
                        code="STR_FORBIDDEN_CHAR",
                    )
                )
                break

    # Check must contain
    if validator.must_contain:
        test_value = value if validator.case_sensitive else value.lower()
        for required in validator.must_contain:
            test_required = required if validator.case_sensitive else required.lower()
            if test_required not in test_value:
                issues.append(
                    ValidationIssue(
                        field="value",
                        message=f"String must contain '{required}'",
                        severity=ValidationSeverity.ERROR,
                        code="STR_MISSING_REQUIRED",
                    )
                )

    # Check must not contain
    if validator.must_not_contain:
        test_value = value if validator.case_sensitive else value.lower()
        for forbidden in validator.must_not_contain:
            test_forbidden = forbidden if validator.case_sensitive else forbidden.lower()
            if test_forbidden in test_value:
                issues.append(
                    ValidationIssue(
                        field="value",
                        message=f"String must not contain '{forbidden}'",
                        severity=ValidationSeverity.ERROR,
                        code="STR_CONTAINS_FORBIDDEN",
                    )
                )

    return ValidationResult(
        is_valid=not any(issue.severity == ValidationSeverity.ERROR for issue in issues),
        validation_type=ValidationType.SYNTAX,
        issues=issues,
    )


def validate_number(value: Union[int, float, Decimal], validator: NumberValidator) -> ValidationResult:
    """
    Validate a numeric value.

    Args:
        value: Number to validate
        validator: Validation configuration

    Returns:
        ValidationResult: Validation result with any issues
    """
    issues: List[ValidationIssue] = []
    float_value = float(value)

    # Check integer requirement
    if validator.must_be_integer and not isinstance(value, int):
        if float_value != int(float_value):
            issues.append(
                ValidationIssue(
                    field="value",
                    message=f"Value {value} must be an integer",
                    severity=ValidationSeverity.ERROR,
                    code="NUM_NOT_INTEGER",
                )
            )

    # Check positive/negative
    if validator.must_be_positive and float_value <= 0:
        issues.append(
            ValidationIssue(
                field="value",
                message=f"Value {value} must be positive",
                severity=ValidationSeverity.ERROR,
                code="NUM_NOT_POSITIVE",
            )
        )

    if validator.must_be_negative and float_value >= 0:
        issues.append(
            ValidationIssue(
                field="value",
                message=f"Value {value} must be negative",
                severity=ValidationSeverity.ERROR,
                code="NUM_NOT_NEGATIVE",
            )
        )

    # Check range
    if validator.min_value is not None and float_value < validator.min_value:
        issues.append(
            ValidationIssue(
                field="value",
                message=f"Value {value} is below minimum {validator.min_value}",
                severity=ValidationSeverity.ERROR,
                code="NUM_TOO_SMALL",
            )
        )

    if validator.max_value is not None and float_value > validator.max_value:
        issues.append(
            ValidationIssue(
                field="value",
                message=f"Value {value} exceeds maximum {validator.max_value}",
                severity=ValidationSeverity.ERROR,
                code="NUM_TOO_LARGE",
            )
        )

    # Check decimal places
    if validator.decimal_places is not None:
        decimal_str = str(value)
        if "." in decimal_str:
            decimal_part = decimal_str.split(".")[1]
            if len(decimal_part) > validator.decimal_places:
                issues.append(
                    ValidationIssue(
                        field="value",
                        message=f"Value has {len(decimal_part)} decimal places, maximum is {validator.decimal_places}",
                        severity=ValidationSeverity.ERROR,
                        code="NUM_TOO_MANY_DECIMALS",
                    )
                )

    # Check multiples
    if validator.multiples_of is not None:
        if float_value % validator.multiples_of != 0:
            issues.append(
                ValidationIssue(
                    field="value",
                    message=f"Value {value} must be a multiple of {validator.multiples_of}",
                    severity=ValidationSeverity.ERROR,
                    code="NUM_NOT_MULTIPLE",
                )
            )

    return ValidationResult(
        is_valid=not any(issue.severity == ValidationSeverity.ERROR for issue in issues),
        validation_type=ValidationType.SYNTAX,
        issues=issues,
    )


def validate_file(path: Path, validator: FileValidator) -> ValidationResult:
    """
    Validate a file path.

    Args:
        path: File path to validate
        validator: Validation configuration

    Returns:
        ValidationResult: Validation result with any issues
    """
    issues: List[ValidationIssue] = []

    # Check existence
    if validator.must_exist and not path.exists():
        issues.append(
            ValidationIssue(
                field="path",
                message=f"File does not exist: {path}",
                severity=ValidationSeverity.ERROR,
                code="FILE_NOT_FOUND",
            )
        )
        # Can't check other properties if file doesn't exist
        return ValidationResult(
            is_valid=False,
            validation_type=ValidationType.SYNTAX,
            issues=issues,
        )

    if path.exists():
        # Check if it's actually a file
        if not path.is_file():
            issues.append(
                ValidationIssue(
                    field="path",
                    message=f"Path is not a file: {path}",
                    severity=ValidationSeverity.ERROR,
                    code="NOT_A_FILE",
                )
            )

        # Check extension
        extension = path.suffix.lower()
        if validator.allowed_extensions and extension not in validator.allowed_extensions:
            issues.append(
                ValidationIssue(
                    field="extension",
                    message=f"Extension {extension} not in allowed list",
                    severity=ValidationSeverity.ERROR,
                    code="FILE_INVALID_EXT",
                )
            )

        if validator.forbidden_extensions and extension in validator.forbidden_extensions:
            issues.append(
                ValidationIssue(
                    field="extension",
                    message=f"Extension {extension} is forbidden",
                    severity=ValidationSeverity.ERROR,
                    code="FILE_FORBIDDEN_EXT",
                )
            )

        # Check size
        if path.is_file():
            size = path.stat().st_size
            if validator.min_size_bytes is not None and size < validator.min_size_bytes:
                issues.append(
                    ValidationIssue(
                        field="size",
                        message=f"File size {size} bytes is below minimum {validator.min_size_bytes}",
                        severity=ValidationSeverity.ERROR,
                        code="FILE_TOO_SMALL",
                    )
                )

            if validator.max_size_bytes is not None and size > validator.max_size_bytes:
                issues.append(
                    ValidationIssue(
                        field="size",
                        message=f"File size {size} bytes exceeds maximum {validator.max_size_bytes}",
                        severity=ValidationSeverity.ERROR,
                        code="FILE_TOO_LARGE",
                    )
                )

        # Check permissions
        if validator.check_readable:
            try:
                with open(path, "r"):
                    pass
            except PermissionError:
                issues.append(
                    ValidationIssue(
                        field="permissions",
                        message=f"File is not readable: {path}",
                        severity=ValidationSeverity.ERROR,
                        code="FILE_NOT_READABLE",
                    )
                )

        if validator.check_writable:
            try:
                with open(path, "a"):
                    pass
            except PermissionError:
                issues.append(
                    ValidationIssue(
                        field="permissions",
                        message=f"File is not writable: {path}",
                        severity=ValidationSeverity.ERROR,
                        code="FILE_NOT_WRITABLE",
                    )
                )

    return ValidationResult(
        is_valid=not any(issue.severity == ValidationSeverity.ERROR for issue in issues),
        validation_type=ValidationType.SYNTAX,
        issues=issues,
    )


def validate_json(data: Union[str, Dict[str, Any]], validator: JsonValidator) -> ValidationResult:
    """
    Validate JSON data.

    Args:
        data: JSON string or parsed dictionary
        validator: Validation configuration

    Returns:
        ValidationResult: Validation result with any issues
    """
    issues: List[ValidationIssue] = []

    # Parse if string
    if isinstance(data, str):
        try:
            parsed: Dict[str, Any] = json.loads(data)
        except json.JSONDecodeError as e:
            issues.append(
                ValidationIssue(
                    field="json",
                    message=f"Invalid JSON: {str(e)}",
                    severity=ValidationSeverity.ERROR,
                    code="JSON_PARSE_ERROR",
                )
            )
            return ValidationResult(
                is_valid=False,
                validation_type=ValidationType.SYNTAX,
                issues=issues,
            )
    else:
        parsed = data

    # Check required fields
    if validator.required_fields:
        for field in validator.required_fields:
            if field not in parsed:
                issues.append(
                    ValidationIssue(
                        field=field,
                        message=f"Required field '{field}' is missing",
                        severity=ValidationSeverity.ERROR,
                        code="JSON_MISSING_FIELD",
                    )
                )

    # Check forbidden fields
    if validator.forbidden_fields:
        for field in validator.forbidden_fields:
            if field in parsed:
                issues.append(
                    ValidationIssue(
                        field=field,
                        message=f"Forbidden field '{field}' is present",
                        severity=ValidationSeverity.ERROR,
                        code="JSON_FORBIDDEN_FIELD",
                    )
                )

    # Check depth
    if validator.max_depth is not None:
        def check_depth(obj: Any, current_depth: int = 0) -> int:
            if isinstance(obj, dict):
                if not obj:
                    return current_depth
                return max(check_depth(v, current_depth + 1) for v in obj.values())
            elif isinstance(obj, list):
                if not obj:
                    return current_depth
                return max(check_depth(item, current_depth + 1) for item in obj)
            return current_depth

        depth = check_depth(parsed)
        if depth > validator.max_depth:
            issues.append(
                ValidationIssue(
                    field="structure",
                    message=f"JSON depth {depth} exceeds maximum {validator.max_depth}",
                    severity=ValidationSeverity.ERROR,
                    code="JSON_TOO_DEEP",
                )
            )

    return ValidationResult(
        is_valid=not any(issue.severity == ValidationSeverity.ERROR for issue in issues),
        validation_type=ValidationType.SYNTAX,
        issues=issues,
    )


def validate_email(email: str) -> ValidationResult:
    """
    Validate an email address.

    Args:
        email: Email address to validate

    Returns:
        ValidationResult: Validation result
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    issues: List[ValidationIssue] = []

    if not re.match(pattern, email):
        issues.append(
            ValidationIssue(
                field="email",
                message="Invalid email format",
                severity=ValidationSeverity.ERROR,
                code="EMAIL_INVALID",
                suggestion="Ensure email follows format: user@domain.com",
            )
        )

    # Additional checks
    if ".." in email:
        issues.append(
            ValidationIssue(
                field="email",
                message="Email contains consecutive dots",
                severity=ValidationSeverity.ERROR,
                code="EMAIL_CONSECUTIVE_DOTS",
            )
        )

    if email.startswith(".") or email.startswith("@"):
        issues.append(
            ValidationIssue(
                field="email",
                message="Email cannot start with '.' or '@'",
                severity=ValidationSeverity.ERROR,
                code="EMAIL_INVALID_START",
            )
        )

    return ValidationResult(
        is_valid=not any(issue.severity == ValidationSeverity.ERROR for issue in issues),
        validation_type=ValidationType.SYNTAX,
        issues=issues,
    )


def validate_url(url: str) -> ValidationResult:
    """
    Validate a URL.

    Args:
        url: URL to validate

    Returns:
        ValidationResult: Validation result
    """
    pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    issues: List[ValidationIssue] = []

    if not re.match(pattern, url, re.IGNORECASE):
        issues.append(
            ValidationIssue(
                field="url",
                message="Invalid URL format",
                severity=ValidationSeverity.ERROR,
                code="URL_INVALID",
                suggestion="Ensure URL starts with http:// or https://",
            )
        )

    # Security warning for HTTP
    if url.lower().startswith("http://") and "localhost" not in url.lower():
        issues.append(
            ValidationIssue(
                field="url",
                message="URL uses insecure HTTP protocol",
                severity=ValidationSeverity.WARNING,
                code="URL_INSECURE",
                suggestion="Consider using HTTPS for security",
            )
        )

    return ValidationResult(
        is_valid=not any(issue.severity == ValidationSeverity.ERROR for issue in issues),
        validation_type=ValidationType.SECURITY,
        issues=issues,
    )


def validate_task_id(task_id: str) -> ValidationResult:
    """
    Validate a NEXUS task ID.

    Args:
        task_id: Task ID to validate (e.g., 'ENV-001')

    Returns:
        ValidationResult: Validation result
    """
    pattern = r"^[A-Z]{3}-\d{3,4}$"
    issues: List[ValidationIssue] = []

    if not re.match(pattern, task_id):
        issues.append(
            ValidationIssue(
                field="task_id",
                message=f"Invalid task ID format: {task_id}",
                severity=ValidationSeverity.ERROR,
                code="TASK_ID_INVALID",
                suggestion="Use format: XXX-000 (e.g., ENV-001)",
            )
        )

    return ValidationResult(
        is_valid=not issues,
        validation_type=ValidationType.BUSINESS,
        issues=issues,
    )


# Convenience validators using Pydantic's constrained types
PositiveInt = conint(gt=0)
NonNegativeInt = conint(ge=0)
PositiveFloat = confloat(gt=0.0)
NonNegativeFloat = confloat(ge=0.0)
NonEmptyStr = constr(min_length=1)
EmailStr = constr(pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


if __name__ == "__main__":
    print(f"[VALIDATORS] NEXUS Browser Validators Module (Task: {TASK_ID})")
    print(f"[VALIDATORS] Quality Enforcement: {QUALITY_ENFORCED}")

    # Test validators
    print("\n[VALIDATORS] Testing validation functions:")

    # Test string validation
    string_validator = StringValidator(
        min_length=3,
        max_length=10,
        pattern=r"^[A-Z]+$",
    )
    result = validate_string("TEST", string_validator)
    print(f"  String 'TEST' validation: {result.is_valid}")

    # Test number validation
    number_validator = NumberValidator(
        min_value=0,
        max_value=100,
        must_be_positive=True,
    )
    result = validate_number(50, number_validator)
    print(f"  Number 50 validation: {result.is_valid}")

    # Test email validation
    result = validate_email("test@example.com")
    print(f"  Email validation: {result.is_valid}")

    # Test task ID validation
    result = validate_task_id("ENV-007")
    print(f"  Task ID validation: {result.is_valid}")

    print("\n[VALIDATORS] Module initialized successfully")
