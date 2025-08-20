"""
Validation utilities for the application.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

from pydantic import HttpUrl, ValidationError

from simple_apps_v2.core.logging import get_logger

logger = get_logger(__name__)


def validate_url(url: str) -> bool:
    """
    Validate if a URL is properly formatted.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Use Pydantic's HttpUrl for validation
        HttpUrl(url)
        
        # Additional checks
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # Ensure scheme is http or https
        if parsed.scheme not in ('http', 'https'):
            return False
        
        return True
        
    except (ValidationError, ValueError) as e:
        logger.debug(f"URL validation failed for '{url}': {e}")
        return False


def validate_json(data: Union[str, Dict, List]) -> bool:
    """
    Validate if data is valid JSON.
    
    Args:
        data: Data to validate (string, dict, or list)
        
    Returns:
        True if valid JSON, False otherwise
    """
    try:
        if isinstance(data, str):
            json.loads(data)
        else:
            json.dumps(data)
        return True
    except (json.JSONDecodeError, TypeError) as e:
        logger.debug(f"JSON validation failed: {e}")
        return False


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid format, False otherwise
    """
    # Check for consecutive dots which are invalid
    if '..' in email:
        return False
    
    # More strict email pattern
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]*[a-zA-Z0-9]@[a-zA-Z0-9][a-zA-Z0-9.-]*\.[a-zA-Z]{2,}$'
    
    # Handle single character usernames
    if '@' in email:
        username = email.split('@')[0]
        if len(username) == 1:
            pattern = r'^[a-zA-Z0-9]@[a-zA-Z0-9][a-zA-Z0-9.-]*\.[a-zA-Z]{2,}$'
    
    return bool(re.match(pattern, email))


def validate_selector(selector: str) -> bool:
    """
    Validate CSS selector format.
    
    Args:
        selector: CSS selector to validate
        
    Returns:
        True if appears to be a valid selector, False otherwise
    """
    if not selector or not isinstance(selector, str):
        return False
    
    # Allow most CSS selectors including attribute selectors
    # Only reject obviously invalid patterns
    invalid_patterns = [
        r'^\s*$',  # Empty or whitespace only
        r'^[\d]',  # Starts with digit
        r'[<>]',   # Contains HTML tags
    ]
    
    for pattern in invalid_patterns:
        if re.search(pattern, selector):
            return False
    
    # Check for basic CSS selector characters
    # Allow: letters, numbers, -, _, ., #, [, ], =, ', ", :, (, ), *, >, +, ~, space, comma, |
    valid_chars = re.match(r'^[\w\-\.#\[\]=\'\":(),\s>+~*|]+$', selector)
    return valid_chars is not None


def validate_test_priority(priority: Optional[str]) -> bool:
    """
    Validate test priority value.
    
    Args:
        priority: Priority string to validate
        
    Returns:
        True if valid priority, False otherwise
    """
    if priority is None:
        return False
    valid_priorities = {'critical', 'high', 'medium', 'low'}
    return priority.lower() in valid_priorities


def validate_element_category(category: str) -> bool:
    """
    Validate element category value.
    
    Args:
        category: Category string to validate
        
    Returns:
        True if valid category, False otherwise
    """
    valid_categories = {
        'navigation', 'form_input', 'button', 'link', 
        'text_display', 'media', 'interactive', 'container', 'other'
    }
    return category.lower() in valid_categories


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Validate file extension.
    
    Args:
        filename: Filename to validate
        allowed_extensions: List of allowed extensions (e.g., ['.py', '.js'])
        
    Returns:
        True if extension is allowed, False otherwise
    """
    if not filename or not isinstance(filename, str):
        return False
    
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    normalized_extensions = [ext.lower().lstrip('.') for ext in allowed_extensions]
    
    return extension in normalized_extensions


def validate_port(port: Union[int, str]) -> bool:
    """
    Validate network port number.
    
    Args:
        port: Port number to validate
        
    Returns:
        True if valid port, False otherwise
    """
    try:
        port_int = int(port)
        return 1 <= port_int <= 65535
    except (ValueError, TypeError):
        return False


def validate_timeout(timeout: Union[int, float]) -> bool:
    """
    Validate timeout value.
    
    Args:
        timeout: Timeout value in milliseconds or seconds
        
    Returns:
        True if valid timeout, False otherwise
    """
    try:
        timeout_num = float(timeout)
        # Standard timeout validation: must be positive and <= 3600 seconds
        return 0 < timeout_num <= 3600
    except (ValueError, TypeError):
        return False


def validate_coordinates(x: Union[int, float], y: Union[int, float]) -> bool:
    """
    Validate screen coordinates.
    
    Args:
        x: X coordinate
        y: Y coordinate
        
    Returns:
        True if valid coordinates, False otherwise
    """
    try:
        x_num = float(x)
        y_num = float(y)
        return x_num >= 0 and y_num >= 0 and x_num <= 10000 and y_num <= 10000
    except (ValueError, TypeError):
        return False


def validate_browser_config(config: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate browser configuration dictionary.
    
    Args:
        config: Browser configuration to validate
        
    Returns:
        Dictionary with validation errors by field
    """
    errors = {}
    
    # Validate headless
    if 'headless' in config and not isinstance(config['headless'], bool):
        errors.setdefault('headless', []).append('Must be a boolean')
    
    # Validate timeout
    if 'timeout' in config and not validate_timeout(config['timeout']):
        errors.setdefault('timeout', []).append('Must be a positive number <= 3600')
    
    # Validate viewport dimensions
    if 'viewport_width' in config:
        try:
            width = int(config['viewport_width'])
            if not (100 <= width <= 5000):
                errors.setdefault('viewport_width', []).append('Must be between 100 and 5000')
        except (ValueError, TypeError):
            errors.setdefault('viewport_width', []).append('Must be an integer')
    
    if 'viewport_height' in config:
        try:
            height = int(config['viewport_height'])
            if not (100 <= height <= 5000):
                errors.setdefault('viewport_height', []).append('Must be between 100 and 5000')
        except (ValueError, TypeError):
            errors.setdefault('viewport_height', []).append('Must be an integer')
    
    return errors


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove/replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Trim whitespace and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure not empty
    if not sanitized:
        sanitized = 'untitled'
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        name = name[:250 - len(ext)]
        sanitized = f"{name}.{ext}" if ext else name
    
    return sanitized


def validate_extraction_request(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate element extraction request data.
    
    Args:
        data: Request data to validate
        
    Returns:
        Dictionary with validation errors by field
    """
    errors = {}
    
    # Validate URL
    if 'url' not in data:
        errors.setdefault('url', []).append('URL is required')
    elif not validate_url(data['url']):
        errors.setdefault('url', []).append('Invalid URL format')
    
    # Validate headless flag
    if 'headless' in data and not isinstance(data['headless'], bool):
        errors.setdefault('headless', []).append('Must be a boolean')
    
    # Validate analyze_with_llm flag
    if 'analyze_with_llm' in data and not isinstance(data['analyze_with_llm'], bool):
        errors.setdefault('analyze_with_llm', []).append('Must be a boolean')
    
    # Validate categories
    if 'categories' in data:
        if not isinstance(data['categories'], list):
            errors.setdefault('categories', []).append('Must be a list')
        else:
            invalid_categories = [
                cat for cat in data['categories'] 
                if not validate_element_category(cat)
            ]
            if invalid_categories:
                errors.setdefault('categories', []).append(
                    f'Invalid categories: {invalid_categories}'
                )
    
    return errors


def is_safe_path(path: str, allowed_dirs: Optional[List[str]] = None) -> bool:
    """
    Check if a file path is safe (no directory traversal).
    
    Args:
        path: File path to check
        allowed_dirs: List of allowed base directories
        
    Returns:
        True if path is safe, False otherwise
    """
    try:
        # Normalize path
        normalized = str(Path(path).resolve())
        
        # Check for directory traversal
        if '..' in path or path.startswith('/'):
            return False
        
        # Check against allowed directories if provided
        if allowed_dirs:
            return any(
                normalized.startswith(str(Path(allowed_dir).resolve()))
                for allowed_dir in allowed_dirs
            )
        
        return True
        
    except (ValueError, OSError):
        return False