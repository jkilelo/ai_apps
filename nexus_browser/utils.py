#!/usr/bin/env python3
"""
NEXUS Browser Utilities Module.

Task: ENV-006
Common utility functions for the NEXUS Browser system.
Full compliance with mypy --strict, flake8, and 100% type coverage.
Uses Pydantic v2 for data validation where appropriate.
"""

import hashlib
import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, TypeVar, Callable, Final, Tuple
from datetime import datetime
from functools import wraps
import base64
import re
from pydantic import BaseModel, Field, field_validator, ConfigDict


# Type variables for generic functions
T = TypeVar("T")
R = TypeVar("R")

# Module constants
TASK_ID: Final[str] = "ENV-006"
MODULE_NAME: Final[str] = "utils"
QUALITY_ENFORCED: Final[bool] = True


class TimerResult(BaseModel):
    """Result from timer operations."""

    model_config = ConfigDict(frozen=True)

    elapsed_seconds: float = Field(ge=0.0)
    elapsed_ms: float = Field(ge=0.0)
    start_time: float
    end_time: float
    formatted: str

    @field_validator("formatted")
    @classmethod
    def validate_formatted(cls, v: str) -> str:
        """Validate formatted time string."""
        if not v:
            raise ValueError("Formatted time cannot be empty")
        return v


class FileInfo(BaseModel):
    """File information structure."""

    model_config = ConfigDict(frozen=True)

    path: Path
    size_bytes: int = Field(ge=0)
    modified_time: datetime
    created_time: datetime
    is_file: bool
    is_dir: bool
    exists: bool
    extension: str
    mime_type: Optional[str] = None


class ValidationResult(BaseModel):
    """Result from validation operations."""

    model_config = ConfigDict(frozen=True)

    is_valid: bool
    value: Any
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


def generate_uuid() -> str:
    """
    Generate a UUID string.

    Returns:
        str: A new UUID string
    """
    return str(uuid.uuid4())


def generate_task_id(prefix: str, number: int) -> str:
    """
    Generate a formatted task ID.

    Args:
        prefix: Task prefix (e.g., 'ENV')
        number: Task number

    Returns:
        str: Formatted task ID (e.g., 'ENV-001')
    """
    return f"{prefix}-{number:03d}"


def get_timestamp() -> str:
    """
    Get current ISO format timestamp.

    Returns:
        str: Current timestamp in ISO format
    """
    return datetime.now().isoformat()


def get_timestamp_ms() -> int:
    """
    Get current timestamp in milliseconds.

    Returns:
        int: Current timestamp in milliseconds since epoch
    """
    return int(time.time() * 1000)


def format_bytes(size_bytes: int) -> str:
    """
    Format bytes to human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        str: Human-readable size (e.g., '1.5 MB')
    """
    size_float: float = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_float < 1024.0:
            return f"{size_float:.2f} {unit}"
        size_float /= 1024.0
    return f"{size_float:.2f} PB"


def format_duration(seconds: float) -> str:
    """
    Format duration to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        str: Human-readable duration (e.g., '2h 30m 15s')
    """
    if seconds < 0:
        return "0s"

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs:.2f}s")

    return " ".join(parts)


def calculate_hash(data: Union[str, bytes], algorithm: str = "sha256") -> str:
    """
    Calculate hash of data.

    Args:
        data: Data to hash
        algorithm: Hash algorithm (sha256, sha512, md5)

    Returns:
        str: Hex digest of the hash
    """
    if isinstance(data, str):
        data = data.encode("utf-8")

    if algorithm == "sha256":
        hasher = hashlib.sha256()
    elif algorithm == "sha512":
        hasher = hashlib.sha512()
    elif algorithm == "md5":
        hasher = hashlib.md5()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    hasher.update(data)
    return hasher.hexdigest()


def encode_base64(data: Union[str, bytes]) -> str:
    """
    Encode data to base64.

    Args:
        data: Data to encode

    Returns:
        str: Base64 encoded string
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    return base64.b64encode(data).decode("ascii")


def decode_base64(encoded: str) -> bytes:
    """
    Decode base64 string.

    Args:
        encoded: Base64 encoded string

    Returns:
        bytes: Decoded data
    """
    return base64.b64decode(encoded)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system usage.

    Args:
        filename: Original filename

    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # Remove control characters
    sanitized = re.sub(r"[\x00-\x1f\x7f]", "", sanitized)
    # Limit length
    if len(sanitized) > 255:
        name, ext = Path(sanitized).stem, Path(sanitized).suffix
        max_name_len = 255 - len(ext)
        sanitized = name[:max_name_len] + ext
    return sanitized or "unnamed"


def ensure_directory(path: Path) -> Path:
    """
    Ensure directory exists, creating if necessary.

    Args:
        path: Directory path

    Returns:
        Path: The directory path
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json_file(path: Path) -> Dict[str, Any]:
    """
    Read JSON file safely.

    Args:
        path: Path to JSON file

    Returns:
        Dict[str, Any]: Parsed JSON data
    """
    with open(path, "r", encoding="utf-8") as f:
        data: Dict[str, Any] = json.load(f)
        return data


def write_json_file(path: Path, data: Dict[str, Any], indent: int = 2) -> None:
    """
    Write data to JSON file.

    Args:
        path: Path to JSON file
        data: Data to write
        indent: JSON indentation
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def get_file_info(path: Path) -> FileInfo:
    """
    Get detailed file information.

    Args:
        path: File path

    Returns:
        FileInfo: File information
    """
    path = Path(path)
    exists = path.exists()

    if exists:
        stat = path.stat()
        size = stat.st_size
        modified = datetime.fromtimestamp(stat.st_mtime)
        created = datetime.fromtimestamp(stat.st_ctime)
    else:
        size = 0
        modified = datetime.now()
        created = datetime.now()

    return FileInfo(
        path=path,
        size_bytes=size,
        modified_time=modified,
        created_time=created,
        is_file=path.is_file() if exists else False,
        is_dir=path.is_dir() if exists else False,
        exists=exists,
        extension=path.suffix,
        mime_type=None,  # Could be extended with mimetypes module
    )


def retry_with_backoff(
    func: Callable[[], T],
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
) -> Optional[T]:
    """
    Retry function with exponential backoff.

    Args:
        func: Function to retry
        max_attempts: Maximum retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Delay multiplication factor

    Returns:
        Optional[T]: Function result or None if all attempts failed
    """
    delay = initial_delay

    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise e
            time.sleep(delay)
            delay *= backoff_factor

    return None


def timer() -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Decorator to time function execution.

    Returns:
        Callable: Decorator function
    """

    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> R:
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            print(f"[TIMER] {func.__name__} took {elapsed:.3f}s")
            return result

        return wrapper

    return decorator


def measure_time(func: Callable[[], T]) -> Tuple[T, TimerResult]:
    """
    Measure execution time of a function.

    Args:
        func: Function to measure

    Returns:
        Tuple[T, TimerResult]: Function result and timing information
    """
    start_time = time.time()
    result = func()
    end_time = time.time()

    elapsed_seconds = end_time - start_time
    elapsed_ms = elapsed_seconds * 1000

    timer_result = TimerResult(
        elapsed_seconds=elapsed_seconds,
        elapsed_ms=elapsed_ms,
        start_time=start_time,
        end_time=end_time,
        formatted=format_duration(elapsed_seconds),
    )

    return result, timer_result


def validate_email(email: str) -> ValidationResult:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        ValidationResult: Validation result
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    is_valid = bool(re.match(pattern, email))

    errors = []
    if not is_valid:
        errors.append("Invalid email format")

    return ValidationResult(
        is_valid=is_valid,
        value=email,
        errors=errors,
        warnings=[],
    )


def validate_url(url: str) -> ValidationResult:
    """
    Validate URL format.

    Args:
        url: URL to validate

    Returns:
        ValidationResult: Validation result
    """
    pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    is_valid = bool(re.match(pattern, url, re.IGNORECASE))

    errors = []
    if not is_valid:
        errors.append("Invalid URL format")

    warnings = []
    if is_valid and not url.startswith("https://"):
        warnings.append("URL uses HTTP instead of HTTPS")

    return ValidationResult(
        is_valid=is_valid,
        value=url,
        errors=errors,
        warnings=warnings,
    )


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp value between min and max.

    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value

    Returns:
        float: Clamped value
    """
    return max(min_val, min(value, max_val))


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.

    Args:
        dict1: First dictionary
        dict2: Second dictionary (overwrites dict1)

    Returns:
        Dict[str, Any]: Merged dictionary
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def chunk_list(lst: List[T], chunk_size: int) -> List[List[T]]:
    """
    Split list into chunks.

    Args:
        lst: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List[List[T]]: List of chunks
    """
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")

    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_list(nested: List[List[T]]) -> List[T]:
    """
    Flatten nested list.

    Args:
        nested: Nested list

    Returns:
        List[T]: Flattened list
    """
    return [item for sublist in nested for item in sublist]


if __name__ == "__main__":
    print(f"[UTILS] NEXUS Browser Utilities Module (Task: {TASK_ID})")
    print(f"[UTILS] Quality Enforcement: {QUALITY_ENFORCED}")

    # Test utility functions
    print("\n[UTILS] Testing utility functions:")

    # Test UUID generation
    test_uuid = generate_uuid()
    print(f"  Generated UUID: {test_uuid}")

    # Test timestamp
    print(f"  Current timestamp: {get_timestamp()}")

    # Test byte formatting
    print(f"  Formatted bytes: {format_bytes(1536)}")

    # Test duration formatting
    print(f"  Formatted duration: {format_duration(3665.5)}")

    # Test hash calculation
    test_hash = calculate_hash("test data")
    print(f"  SHA256 hash: {test_hash[:16]}...")

    # Test email validation
    email_result = validate_email("test@example.com")
    print(f"  Email validation: {email_result.is_valid}")

    print("\n[UTILS] Module initialized successfully")
