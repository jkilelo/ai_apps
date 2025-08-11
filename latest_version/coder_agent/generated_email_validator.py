```python
# 1. Pydantic v2 input/output contracts

from pydantic import BaseModel, Field

class EmailValidationInput(BaseModel):
    """
    Input contract for email validation.

    Attributes:
        email (str): The email address to validate.
    """
    email: str = Field(..., description="The email address to validate.")

class EmailValidationOutput(BaseModel):
    """
    Output contract for email validation.

    Attributes:
        is_valid (bool): Whether the email address is valid.
        message (str): A message describing the validation result.
    """
    is_valid: bool = Field(..., description="Whether the email address is valid.")
    message: str = Field(..., description="A message describing the validation result.")

# 2. Comprehensive tests (TDD style)

import pytest

@pytest.mark.parametrize(
    "email,expected_valid",
    [
        ("test@example.com", True),
        ("user.name+tag+sorting@example.com", True),
        ("user_name@example.co.uk", True),
        ("user-name@sub.example.com", True),
        ("user@localhost", False),  # localhost is not a valid domain for most cases
        ("plainaddress", False),
        ("@missingusername.com", False),
        ("username@.com", False),
        ("username@com", False),
        ("username@.com.", False),
        ("username@-example.com", False),
        ("username@example..com", False),
        ("username@example.c", False),  # TLD too short
        ("username@example.123", False),  # Numeric TLD
        ("", False),
        ("user@exam_ple.com", False),  # Underscore in domain
        ("user@.example.com", False),
        ("user@exam..ple.com", False),
        ("user@.com.com", False),
        ("user@%*.com", False),
        ("user..name@example.com", False),  # Double dot in local part
        ("user.@example.com", False),  # Dot at end of local part
        ("user@.example.com", False),  # Dot at start of domain
        ("user@sub_domain.example.com", False),  # Underscore in domain
    ]
)
def test_validate_email(email, expected_valid):
    from email_validator import validate_email_address
    input_data = EmailValidationInput(email=email)
    output = validate_email_address(input_data)
    assert output.is_valid == expected_valid, f"Failed for email: {email}"

def test_invalid_input_type():
    from email_validator import validate_email_address
    with pytest.raises(Exception):
        # Passing an int instead of str should raise a validation error
        validate_email_address(EmailValidationInput(email=12345))

def test_output_contract_fields():
    from email_validator import validate_email_address
    input_data = EmailValidationInput(email="test@example.com")
    output = validate_email_address(input_data)
    assert hasattr(output, "is_valid")
    assert hasattr(output, "message")
    assert isinstance(output.is_valid, bool)
    assert isinstance(output.message, str)

# 3. Production-ready implementation

import re

def validate_email_address(input_data: EmailValidationInput) -> EmailValidationOutput:
    """
    Validates an email address using a regular expression.

    Args:
        input_data (EmailValidationInput): The input data containing the email address.

    Returns:
        EmailValidationOutput: The result of the validation.
    """
    # RFC 5322 Official Standard regex is too complex and not practical for most use cases.
    # We'll use a simplified, robust regex for general validation.
    # This regex checks:
    # - Local part: letters, digits, underscores, dots, plus, hyphen (no consecutive dots, no dot at start/end)
    # - Domain: letters, digits, hyphens (no hyphen at start/end), at least one dot, TLD at least 2 chars
    email_regex = re.compile(
        r"^(?!\.)[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+"
        r"(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*"
        r"@"
        r"(?:(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.)+"
        r"[A-Za-z]{2,}$"
    )

    email = input_data.email

    # Defensive: Check for empty string or non-str (should be handled by Pydantic, but double check)
    if not isinstance(email, str) or not email:
        return EmailValidationOutput(
            is_valid=False,
            message="Email address must be a non-empty string."
        )

    # Check for consecutive dots in local or domain part
    try:
        local_part, domain_part = email.rsplit("@", 1)
    except ValueError:
        return EmailValidationOutput(
            is_valid=False,
            message="Email address must contain a single '@' character."
        )
    if ".." in local_part or ".." in domain_part:
        return EmailValidationOutput(
            is_valid=False,
            message="Email address cannot contain consecutive dots."
        )
    if local_part.startswith(".") or local_part.endswith("."):
        return EmailValidationOutput(
            is_valid=False,
            message="Local part of email cannot start or end with a dot."
        )
    if domain_part.startswith(".") or domain_part.endswith("."):
        return EmailValidationOutput(
            is_valid=False,
            message="Domain part of email cannot start or end with a dot."
        )
    if "_" in domain_part:
        return EmailValidationOutput(
            is_valid=False,
            message="Domain part of email cannot contain underscores."
        )

    if not email_regex.fullmatch(email):
        return EmailValidationOutput(
            is_valid=False,
            message="Invalid email address format."
        )

    return EmailValidationOutput(
        is_valid=True,
        message="Valid email address."
    )

# 4. Complete documentation

"""
Email Validator Module
=====================

This module provides a function to validate email addresses using regular expressions,
with Pydantic v2 input/output contracts.

Contracts:
----------
- EmailValidationInput: Input contract with a single field 'email' (str).
- EmailValidationOutput: Output contract with fields 'is_valid' (bool) and 'message' (str).

Function:
---------
- validate_email_address(input_data: EmailValidationInput) -> EmailValidationOutput

    Validates the provided email address for correct format and common edge cases.

    Args:
        input_data (EmailValidationInput): The input data containing the email address.

    Returns:
        EmailValidationOutput: The result of the validation, including a boolean flag and a message.

Testing:
--------
Comprehensive tests are provided using pytest, covering valid, invalid, and edge-case email addresses.

Security:
---------
- The function does not execute or resolve external domains.
- Only format is checked, not deliverability.

Performance:
------------
- The function uses compiled regex and simple string checks for high performance.

Usage Example:
--------------
    from email_validator import EmailValidationInput, validate_email_address

    input_data = EmailValidationInput(email="user@example.com")
    result = validate_email_address(input_data)
    print(result.is_valid)  # True or False
    print(result.message)   # Validation message

"""

# For module-level import
__all__ = [
    "EmailValidationInput",
    "EmailValidationOutput",
    "validate_email_address",
]
```