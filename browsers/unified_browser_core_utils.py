"""
Utility functions for unified browser.

This module contains shared utility functions used throughout the browser implementation,
eliminating code duplication and providing reusable functionality.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import random
import re
import time
from functools import wraps
from pathlib import Path
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    TypeVar,
    Union,
    cast,
)
from urllib.parse import urlparse, quote, unquote

import numpy as np
from scipy import interpolate

from .constants import (
    ALLOWED_PROTOCOLS,
    BLOCKED_FILE_EXTENSIONS,
    DEFAULT_ENCODING,
    DEFAULT_ELEMENT_HASH_LENGTH,
    MAX_PATH_LENGTH,
    MAX_SELECTOR_LENGTH,
    MAX_TYPING_DELAY,
    MAX_URL_LENGTH,
    MIN_TYPING_DELAY,
)
from .exceptions import (
    PathTraversalError,
    SecurityError,
    TimeoutError,
    ValidationError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")
AsyncFunc = TypeVar("AsyncFunc", bound=Callable[..., Awaitable[Any]])


# ============================================================================
# DECORATORS
# ============================================================================
def retry_on_error(
    max_attempts: int = 3,
    delay_ms: int = 1000,
    exponential_backoff: bool = True,
    exceptions: tuple = (Exception,),
) -> Callable[[AsyncFunc], AsyncFunc]:
    """Decorator to retry async function on error with configurable backoff."""

    def decorator(func: AsyncFunc) -> AsyncFunc:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        wait_time = delay_ms
                        if exponential_backoff:
                            wait_time = delay_ms * (2**attempt)

                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {wait_time}ms..."
                        )
                        await asyncio.sleep(wait_time / 1000)
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")

            raise last_exception

        return cast(AsyncFunc, wrapper)

    return decorator


def measure_time(func: AsyncFunc) -> AsyncFunc:
    """Decorator to measure execution time of async functions."""

    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        start_time = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            elapsed = (time.perf_counter() - start_time) * 1000
            logger.debug(f"{func.__name__} took {elapsed:.2f}ms")

    return cast(AsyncFunc, wrapper)


def validate_input(func: Callable) -> Callable:
    """Decorator to validate function inputs for security."""

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Validate all string inputs for potential security issues
        for arg in args:
            if isinstance(arg, str):
                sanitize_input(arg)
        for key, value in kwargs.items():
            if isinstance(value, str):
                sanitize_input(value)

        return func(*args, **kwargs)

    return wrapper


# ============================================================================
# DELAY & TIMING UTILITIES
# ============================================================================
async def human_delay(
    min_ms: int = MIN_TYPING_DELAY, max_ms: int = MAX_TYPING_DELAY, distribution: str = "normal"
) -> None:
    """Generate human-like delay with various distributions."""
    if distribution == "normal":
        # Normal distribution centered between min and max
        mean = (min_ms + max_ms) / 2
        std = (max_ms - min_ms) / 4
        delay = np.random.normal(mean, std)
        delay = np.clip(delay, min_ms, max_ms)
    elif distribution == "exponential":
        # Exponential distribution for burst typing
        scale = (max_ms - min_ms) / 3
        delay = np.random.exponential(scale) + min_ms
        delay = min(delay, max_ms)
    else:  # uniform
        delay = random.uniform(min_ms, max_ms)

    await asyncio.sleep(delay / 1000)


def generate_typing_delays(text: str) -> List[float]:
    """Generate realistic typing delays for each character."""
    delays = []

    for i, char in enumerate(text):
        if char == " ":
            # Spaces are typed faster
            delay = random.uniform(30, 80)
        elif char in ".,!?;:":
            # Punctuation causes slight pause
            delay = random.uniform(100, 200)
        elif i > 0 and text[i - 1] == char:
            # Same character repeated is faster
            delay = random.uniform(40, 90)
        else:
            # Normal character
            delay = random.uniform(MIN_TYPING_DELAY, MAX_TYPING_DELAY)

        # Add occasional micro-pauses (thinking)
        if random.random() < 0.05:
            delay += random.uniform(200, 500)

        delays.append(delay / 1000)  # Convert to seconds

    return delays


def generate_mouse_path(
    start: tuple[float, float], end: tuple[float, float], num_points: int = 20
) -> List[tuple[float, float]]:
    """Generate human-like curved mouse movement path using B-spline interpolation."""
    x_start, y_start = start
    x_end, y_end = end

    # Add control points for natural curve
    distance = np.sqrt((x_end - x_start) ** 2 + (y_end - y_start) ** 2)
    num_control = max(3, int(distance / 100))

    # Generate control points with some randomness
    control_x = np.linspace(x_start, x_end, num_control)
    control_y = np.linspace(y_start, y_end, num_control)

    # Add perpendicular offset to middle points for curve
    for i in range(1, num_control - 1):
        offset = random.gauss(0, distance / 20)
        angle = np.arctan2(y_end - y_start, x_end - x_start)
        control_x[i] += offset * np.sin(angle)
        control_y[i] += offset * np.cos(angle)

    # Create B-spline
    try:
        tck, _ = interpolate.splprep([control_x, control_y], s=0, k=min(3, num_control - 1))
        u = np.linspace(0, 1, num_points)
        smooth_x, smooth_y = interpolate.splev(u, tck)

        # Add micro jitter for realism
        path = []
        for x, y in zip(smooth_x, smooth_y):
            jitter_x = random.gauss(0, 1)
            jitter_y = random.gauss(0, 1)
            path.append((x + jitter_x, y + jitter_y))

        return path
    except:
        # Fallback to linear path if spline fails
        return [
            (
                x_start + (x_end - x_start) * i / num_points,
                y_start + (y_end - y_start) * i / num_points,
            )
            for i in range(num_points)
        ]


# ============================================================================
# HASH & ID GENERATION
# ============================================================================
def generate_element_hash(
    element_data: Dict[str, Any], length: int = DEFAULT_ELEMENT_HASH_LENGTH
) -> str:
    """Generate unique hash for element identification."""
    # Create deterministic string from element properties
    hash_input = json.dumps(
        {
            "tag": element_data.get("tagName", ""),
            "id": element_data.get("id", ""),
            "class": element_data.get("className", ""),
            "text": element_data.get("innerText", "")[:50],  # Limit text length
            "href": element_data.get("href", ""),
        },
        sort_keys=True,
    )

    # Generate SHA-256 hash
    hash_obj = hashlib.sha256(hash_input.encode())
    full_hash = hash_obj.hexdigest()

    # Return requested length
    return full_hash[:length]


def generate_unique_id(prefix: str = "elem") -> str:
    """Generate unique identifier with prefix."""
    timestamp = int(time.time() * 1000000)
    random_part = random.randint(1000, 9999)
    return f"{prefix}_{timestamp}_{random_part}"


# ============================================================================
# VALIDATION & SANITIZATION
# ============================================================================
def validate_url(url: str) -> tuple[bool, Optional[str]]:
    """Validate URL for security and correctness."""
    if not url:
        return False, "URL cannot be empty"

    if len(url) > MAX_URL_LENGTH:
        return False, f"URL exceeds maximum length of {MAX_URL_LENGTH}"

    try:
        parsed = urlparse(url)

        # Check protocol
        if parsed.scheme not in ALLOWED_PROTOCOLS:
            return False, f"Protocol {parsed.scheme} not allowed"

        # Check for basic URL structure
        if not parsed.netloc:
            return False, "Invalid URL structure"

        # Check for suspicious patterns
        suspicious_patterns = [
            r"javascript:",
            r"data:",
            r"vbscript:",
            r"file:",
            r"about:",
            r"<script",
            r"onclick=",
            r"onerror=",
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False, f"Suspicious pattern detected: {pattern}"

        return True, None

    except Exception as e:
        return False, f"URL parsing error: {str(e)}"


def validate_selector(selector: str) -> tuple[bool, Optional[str]]:
    """Validate CSS selector for security."""
    if not selector:
        return False, "Selector cannot be empty"

    if len(selector) > MAX_SELECTOR_LENGTH:
        return False, f"Selector exceeds maximum length of {MAX_SELECTOR_LENGTH}"

    # Check for script injection attempts
    dangerous_patterns = [
        r"<script",
        r"javascript:",
        r"on\w+=",  # Event handlers
        r"expression\(",
        r"@import",
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, selector, re.IGNORECASE):
            return False, f"Dangerous pattern detected: {pattern}"

    # Basic CSS selector validation
    try:
        # Check for balanced brackets
        if selector.count("[") != selector.count("]"):
            return False, "Unbalanced brackets in selector"
        if selector.count("(") != selector.count(")"):
            return False, "Unbalanced parentheses in selector"

        return True, None

    except Exception as e:
        return False, f"Selector validation error: {str(e)}"


def validate_path(path: str) -> tuple[bool, Optional[str]]:
    """Validate file path for security."""
    if not path:
        return False, "Path cannot be empty"

    if len(path) > MAX_PATH_LENGTH:
        return False, f"Path exceeds maximum length of {MAX_PATH_LENGTH}"

    try:
        path_obj = Path(path)

        # Check for path traversal attempts
        if ".." in path_obj.parts:
            return False, "Path traversal detected"

        # Check for blocked extensions
        if path_obj.suffix.lower() in BLOCKED_FILE_EXTENSIONS:
            return False, f"File extension {path_obj.suffix} is blocked"

        # Ensure path is not absolute to system directories
        system_dirs = ["/etc", "/sys", "/proc", "C:\\Windows", "C:\\Program Files"]
        for sys_dir in system_dirs:
            if str(path_obj).startswith(sys_dir):
                return False, f"Access to system directory denied: {sys_dir}"

        return True, None

    except Exception as e:
        return False, f"Path validation error: {str(e)}"


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input for security."""
    if not text:
        return ""

    # Limit length
    text = text[:max_length]

    # Remove null bytes
    text = text.replace("\x00", "")

    # Escape HTML special characters
    html_escapes = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#x27;",
        "/": "&#x2F;",
    }

    for char, escape in html_escapes.items():
        text = text.replace(char, escape)

    # Remove control characters except newline and tab
    text = "".join(char for char in text if char == "\n" or char == "\t" or ord(char) >= 32)

    return text


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations."""
    # Remove path components
    filename = os.path.basename(filename)

    # Remove dangerous characters
    dangerous_chars = '<>:"|?*\x00'
    for char in dangerous_chars:
        filename = filename.replace(char, "_")

    # Remove leading/trailing dots and spaces
    filename = filename.strip(". ")

    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 200:
        name = name[:200]
    filename = name + ext

    # Ensure non-empty
    if not filename:
        filename = "unnamed"

    return filename


# ============================================================================
# STRING UTILITIES
# ============================================================================
def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix."""
    if len(text) <= max_length:
        return text

    truncate_at = max_length - len(suffix)
    return text[:truncate_at] + suffix


def extract_numbers(text: str) -> List[float]:
    """Extract all numbers from text."""
    # First handle comma-separated thousands
    text_normalized = text.replace(",", "")

    # Match integers, decimals, and negative numbers
    pattern = r"[-+]?\d+\.?\d*"
    matches = re.findall(pattern, text_normalized)

    numbers = []
    for match in matches:
        try:
            num = float(match)
            # Filter out year-like numbers that are too large to be prices
            if num != 0:  # Keep all non-zero numbers
                numbers.append(num)
        except ValueError:
            continue

    return numbers


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
    # Replace multiple spaces with single space
    text = re.sub(r"\s+", " ", text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case."""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def snake_to_camel(name: str, capitalize_first: bool = False) -> str:
    """Convert snake_case to camelCase."""
    components = name.split("_")
    if capitalize_first:
        return "".join(x.title() for x in components)
    else:
        return components[0] + "".join(x.title() for x in components[1:])


# ============================================================================
# CSS/XPATH UTILITIES
# ============================================================================
def element_to_selector(element_data: Dict[str, Any]) -> str:
    """Generate CSS selector from element data."""
    selector_parts = []

    # Tag name
    tag = element_data.get("tagName", "").lower()
    if tag:
        selector_parts.append(tag)

    # ID
    element_id = element_data.get("id", "")
    if element_id:
        selector_parts.append(f"#{element_id}")
        return "".join(selector_parts)  # ID is unique enough

    # Classes
    classes = element_data.get("className", "").strip()
    if classes:
        class_list = classes.split()
        for cls in class_list:
            selector_parts.append(f".{cls}")

    # Attributes
    attributes = element_data.get("attributes", {})
    for attr, value in attributes.items():
        if attr not in ["id", "class"]:
            selector_parts.append(f'[{attr}="{value}"]')

    return "".join(selector_parts) if selector_parts else "*"


def element_to_xpath(element_data: Dict[str, Any]) -> str:
    """Generate XPath from element data."""
    tag = element_data.get("tagName", "*").lower()
    conditions = []

    # ID
    element_id = element_data.get("id", "")
    if element_id:
        return f'//{tag}[@id="{element_id}"]'

    # Classes
    classes = element_data.get("className", "").strip()
    if classes:
        conditions.append(f'@class="{classes}"')

    # Text content
    text = element_data.get("innerText", "").strip()
    if text and len(text) < 50:
        conditions.append(f'text()="{text}"')

    # Other attributes
    attributes = element_data.get("attributes", {})
    for attr, value in attributes.items():
        if attr not in ["id", "class"]:
            conditions.append(f'@{attr}="{value}"')

    if conditions:
        condition_str = " and ".join(conditions)
        return f"//{tag}[{condition_str}]"

    return f"//{tag}"


# ============================================================================
# ASYNC UTILITIES
# ============================================================================
async def run_with_timeout(
    coro: Awaitable[T], timeout_seconds: float, timeout_message: str = "Operation timed out"
) -> T:
    """Run coroutine with timeout."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        raise TimeoutError(timeout_message, timeout_ms=int(timeout_seconds * 1000))


async def gather_with_errors(*coros: Awaitable[Any], return_exceptions: bool = True) -> List[Any]:
    """Gather coroutines and handle errors gracefully."""
    results = await asyncio.gather(*coros, return_exceptions=return_exceptions)

    # Log any exceptions
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Coroutine {i} failed: {result}")

    return results


# ============================================================================
# RATE LIMITING
# ============================================================================
class RateLimiter:
    """Simple rate limiter using token bucket algorithm."""

    def __init__(self, rate: float, burst: int):
        """
        Initialize rate limiter.

        Args:
            rate: Tokens per second
            burst: Maximum burst size
        """
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last_update = time.monotonic()
        self.lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> None:
        """Acquire tokens, blocking if necessary."""
        async with self.lock:
            while tokens > self.tokens:
                now = time.monotonic()
                elapsed = now - self.last_update
                self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
                self.last_update = now

                if tokens > self.tokens:
                    sleep_time = (tokens - self.tokens) / self.rate
                    await asyncio.sleep(sleep_time)

            self.tokens -= tokens


# ============================================================================
# FILE UTILITIES
# ============================================================================
def ensure_directory(path: Path) -> None:
    """Ensure directory exists, create if not."""
    path.mkdir(parents=True, exist_ok=True)


def safe_write_file(path: Path, content: str, encoding: str = DEFAULT_ENCODING) -> None:
    """Safely write file with atomic operation."""
    # Validate path
    is_valid, error = validate_path(str(path))
    if not is_valid:
        raise PathTraversalError(f"Invalid path: {error}", path=str(path))

    # Write to temporary file first
    temp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        temp_path.write_text(content, encoding=encoding)
        # Atomic rename
        temp_path.replace(path)
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise


def safe_read_file(path: Path, encoding: str = DEFAULT_ENCODING) -> str:
    """Safely read file with validation."""
    # Validate path
    is_valid, error = validate_path(str(path))
    if not is_valid:
        raise PathTraversalError(f"Invalid path: {error}", path=str(path))

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return path.read_text(encoding=encoding)


# ============================================================================
# JSON UTILITIES
# ============================================================================
def safe_json_loads(text: str, default: Any = None) -> Any:
    """Safely parse JSON with default value."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        logger.warning(f"Failed to parse JSON: {text[:100]}...")
        return default


def safe_json_dumps(obj: Any, default: Optional[Callable] = None) -> str:
    """Safely serialize object to JSON."""
    try:
        return json.dumps(obj, default=default, indent=2)
    except (TypeError, ValueError) as e:
        logger.warning(f"Failed to serialize to JSON: {e}")
        return "{}"
