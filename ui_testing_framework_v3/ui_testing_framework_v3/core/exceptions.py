"""Domain-specific exceptions representing business rule violations."""


class DomainError(Exception):
    """Base exception for domain errors."""


class InvalidElementError(DomainError):
    """Raised when element violates business rules."""


class InvalidTestCaseError(DomainError):
    """Raised when test case is invalid."""


class ExtractionError(DomainError):
    """Raised when extraction fails due to business rules."""


__all__ = [
    "DomainError",
    "ExtractionError",
    "InvalidElementError",
    "InvalidTestCaseError",
]
