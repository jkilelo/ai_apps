"""
Security utilities for the AI-first browser system.
Provides input validation, sanitization, rate limiting and security enforcement.

Extracted and enhanced from the existing agents system with additional
AI-specific security considerations.
"""

import os
import re
import hashlib
import secrets
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Tuple
from urllib.parse import urlparse, quote
from datetime import datetime, timedelta
import json
from functools import lru_cache

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Security configuration and constants."""
    
    # Input size limits
    MAX_URL_LENGTH = 2048
    MAX_SELECTOR_LENGTH = 500
    MAX_TEXT_INPUT_LENGTH = 10000
    MAX_SCRIPT_LENGTH = 50000
    MAX_PROMPT_LENGTH = 20000  # Increased for AI prompts
    MAX_FILE_PATH_LENGTH = 260  # Windows MAX_PATH
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE = 60
    MAX_LLM_CALLS_PER_MINUTE = 30  # Increased for AI workloads
    MAX_BROWSER_ACTIONS_PER_MINUTE = 100
    
    # File operation restrictions
    ALLOWED_FILE_EXTENSIONS = {
        '.json', '.yaml', '.yml', '.txt', '.csv', '.log', 
        '.png', '.jpg', '.jpeg', '.gif', '.webp',  # Images
        '.html', '.htm', '.xml'  # Web formats
    }
    FORBIDDEN_PATHS = {'/etc', '/sys', '/proc', 'C:\\Windows', 'C:\\Program Files'}
    FORBIDDEN_PATTERNS = [
        'etc/passwd', 'System32', 'system32', '.ssh/', 'id_rsa', 
        'shadow', 'hosts', 'boot.ini', 'pagefile.sys'
    ]
    
    # URL restrictions
    ALLOWED_PROTOCOLS = {'http', 'https'}
    BLOCKED_DOMAINS = {'localhost', '127.0.0.1', '0.0.0.0', '::1'}
    
    # Dangerous patterns for prompt injection and XSS
    PROMPT_INJECTION_PATTERNS = [
        r'ignore.*previous.*instructions',
        r'disregard.*above',
        r'forget.*everything',
        r'new.*instructions.*follow',
        r'system.*prompt',
        r'<script',
        r'javascript:',
        r'data:text/html',
        r'onerror=',
        r'onclick=',
        r'eval\(',
        r'document\.write',
        r'innerHTML',
        r'outerHTML'
    ]


class InputValidator:
    """Validates and sanitizes user inputs with AI-specific considerations."""
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate URL for safety and correctness.
        
        Returns:
            Tuple of (is_valid, sanitized_url, error_message)
        """
        if not url or not isinstance(url, str):
            return False, None, "URL must be a non-empty string"
        
        url = url.strip()
        if len(url) > SecurityConfig.MAX_URL_LENGTH:
            return False, None, f"URL exceeds maximum length of {SecurityConfig.MAX_URL_LENGTH}"
        
        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            return False, None, f"Invalid URL format: {e}"
        
        # Check protocol
        if parsed.scheme not in SecurityConfig.ALLOWED_PROTOCOLS:
            return False, None, f"Protocol {parsed.scheme} not allowed. Use http or https"
        
        # Check for blocked domains
        hostname = parsed.hostname or ""
        if hostname in SecurityConfig.BLOCKED_DOMAINS:
            return False, None, f"Access to {hostname} is blocked for security reasons"
        
        # Check for private IP addresses
        if InputValidator._is_private_ip(hostname):
            return False, None, "Access to private IP addresses is not allowed"
        
        # Additional security: Check for suspicious patterns
        if any(pattern in url.lower() for pattern in ['file://', 'ftp://', 'data:']):
            return False, None, "Suspicious URL scheme detected"
        
        # Sanitize URL - remove dangerous fragments
        sanitized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            # Basic query sanitization
            safe_query = re.sub(r'[<>"\']', '', parsed.query)
            sanitized += f"?{safe_query}"
        
        return True, sanitized, None
    
    @staticmethod
    def _is_private_ip(hostname: str) -> bool:
        """Check if hostname is a private IP address."""
        import ipaddress
        
        try:
            ip = ipaddress.ip_address(hostname)
            return ip.is_private or ip.is_loopback or ip.is_link_local
        except ValueError:
            # Not an IP address, probably a domain name
            return False
    
    @staticmethod
    def validate_selector(selector: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate CSS selector or XPath with enhanced security.
        
        Returns:
            Tuple of (is_valid, sanitized_selector, error_message)
        """
        if not selector or not isinstance(selector, str):
            return False, None, "Selector must be a non-empty string"
        
        selector = selector.strip()
        if len(selector) > SecurityConfig.MAX_SELECTOR_LENGTH:
            return False, None, f"Selector exceeds maximum length of {SecurityConfig.MAX_SELECTOR_LENGTH}"
        
        # Enhanced dangerous pattern detection
        dangerous_patterns = [
            '<script', 'javascript:', 'onerror', 'onclick', 'onload', 'onmouseover',
            'eval(', 'document.write', 'innerHTML', 'outerHTML', 'insertAdjacentHTML'
        ]
        selector_lower = selector.lower()
        for pattern in dangerous_patterns:
            if pattern in selector_lower:
                return False, None, f"Selector contains dangerous pattern: {pattern}"
        
        # Check for potential XSS vectors
        if re.search(r'[<>"\']', selector):
            # Basic XSS prevention
            sanitized = re.sub(r'[<>"\']', '', selector)
            return True, sanitized, "Selector sanitized: removed potentially dangerous characters"
        
        return True, selector, None
    
    @staticmethod
    def validate_text_input(text: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate text input for form fields with comprehensive sanitization.
        
        Returns:
            Tuple of (is_valid, sanitized_text, error_message)
        """
        if not isinstance(text, str):
            return False, None, "Text must be a string"
        
        if len(text) > SecurityConfig.MAX_TEXT_INPUT_LENGTH:
            return False, None, f"Text exceeds maximum length of {SecurityConfig.MAX_TEXT_INPUT_LENGTH}"
        
        # Remove control characters except newlines and tabs
        sanitized = ''.join(char for char in text if char in '\n\t' or ord(char) >= 32)
        
        # Enhanced HTML entity escaping
        html_escape_table = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;',
            '/': '&#x2F;',  # Forward slash for script tag protection
        }
        
        for char, escape in html_escape_table.items():
            sanitized = sanitized.replace(char, escape)
        
        # Check for potential script injection
        dangerous_in_text = ['<script', '</script>', 'javascript:', 'eval(']
        for pattern in dangerous_in_text:
            if pattern.lower() in sanitized.lower():
                return False, None, f"Text contains potentially dangerous content: {pattern}"
        
        return True, sanitized, None
    
    @staticmethod
    def validate_javascript(script: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate JavaScript code for execution with strict security.
        
        Returns:
            Tuple of (is_valid, sanitized_script, error_message)
        """
        if not isinstance(script, str):
            return False, None, "Script must be a string"
        
        if len(script) > SecurityConfig.MAX_SCRIPT_LENGTH:
            return False, None, f"Script exceeds maximum length of {SecurityConfig.MAX_SCRIPT_LENGTH}"
        
        # Comprehensive dangerous pattern detection
        dangerous_patterns = [
            'eval(', 'Function(', 'setTimeout(', 'setInterval(',
            'document.write', 'innerHTML', 'outerHTML', 'insertAdjacentHTML',
            '.cookie', 'localStorage', 'sessionStorage', 'indexedDB',
            'XMLHttpRequest', 'fetch(', 'import(', 'Worker(',
            'location.href', 'location.replace', 'window.open',
            'document.domain', 'postMessage', 'addEventListener',
            '__proto__', 'constructor', 'prototype'
        ]
        
        script_lower = script.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in script_lower:
                logger.warning(f"Script contains potentially dangerous pattern: {pattern}")
                return False, None, f"Script contains forbidden pattern: {pattern}"
        
        # Additional checks for common attack vectors
        if re.search(r'[<>]', script):
            return False, None, "Script contains HTML-like tags"
        
        if 'data:' in script_lower or 'blob:' in script_lower:
            return False, None, "Script contains data/blob URLs"
        
        return True, script, None
    
    @staticmethod
    def validate_file_path(path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate file path for safety with enhanced security.
        
        Returns:
            Tuple of (is_valid, sanitized_path, error_message)
        """
        if not isinstance(path, str):
            return False, None, "Path must be a string"
        
        path = path.strip()
        if len(path) > SecurityConfig.MAX_FILE_PATH_LENGTH:
            return False, None, f"Path exceeds maximum length of {SecurityConfig.MAX_FILE_PATH_LENGTH}"
        
        # Convert to Path object and resolve
        try:
            path_obj = Path(path).resolve()
        except Exception as e:
            return False, None, f"Invalid path: {e}"
        
        # Check against forbidden paths
        str_path = str(path_obj)
        str_path_lower = str_path.lower()
        
        # Check exact forbidden paths
        for forbidden in SecurityConfig.FORBIDDEN_PATHS:
            if str_path.startswith(forbidden) or str_path_lower.startswith(forbidden.lower()):
                return False, None, f"Access to {forbidden} is forbidden"
        
        # Check forbidden patterns
        for pattern in SecurityConfig.FORBIDDEN_PATTERNS:
            if pattern.lower() in str_path_lower:
                return False, None, f"Path contains forbidden pattern: {pattern}"
        
        # Additional system directory checks
        dangerous_paths = ['/root', '/home', '/Users', 'C:\\Users', '/var', '/opt']
        if any(str_path.startswith(p) for p in dangerous_paths):
            logger.warning(f"Accessing potentially sensitive directory: {str_path}")
        
        # Check file extension if it's a file
        if path_obj.suffix and path_obj.suffix not in SecurityConfig.ALLOWED_FILE_EXTENSIONS:
            return False, None, f"File extension {path_obj.suffix} is not allowed"
        
        # Prevent directory traversal
        if '..' in str(path_obj) or '~' in str(path_obj):
            return False, None, "Directory traversal or home directory access detected"
        
        return True, str(path_obj), None


class PromptSanitizer:
    """Sanitizes AI prompts to prevent injection attacks."""
    
    @staticmethod
    def sanitize_prompt(prompt: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Sanitize prompt to prevent injection attacks with enhanced AI security.
        
        Returns:
            Tuple of (is_safe, sanitized_prompt, warning_message)
        """
        if not isinstance(prompt, str):
            return False, None, "Prompt must be a string"
        
        if len(prompt) > SecurityConfig.MAX_PROMPT_LENGTH:
            return False, None, f"Prompt exceeds maximum length of {SecurityConfig.MAX_PROMPT_LENGTH}"
        
        # Check for injection patterns
        prompt_lower = prompt.lower()
        for pattern in SecurityConfig.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, prompt_lower):
                logger.warning(f"Potential prompt injection detected: {pattern}")
                return False, None, f"Prompt contains suspicious pattern"
        
        # Enhanced AI-specific security checks
        ai_dangerous_patterns = [
            'system:', 'assistant:', 'human:', 'user:',  # Role manipulation
            '```', '###', '---',  # Markdown injection
            '[INST]', '[/INST]', '<|im_start|>', '<|im_end|>',  # Model tokens
            'jailbreak', 'break out', 'override', 'bypass'
        ]
        
        for pattern in ai_dangerous_patterns:
            if pattern in prompt_lower:
                logger.warning(f"AI-specific dangerous pattern detected: {pattern}")
        
        # Remove special tokens that might be used for injection
        sanitized = prompt
        special_tokens = [
            '<|im_end|>', '<|im_start|>', '[INST]', '[/INST]', 
            '<<SYS>>', '<</SYS>>', '### System:', '### Human:', '### Assistant:'
        ]
        for token in special_tokens:
            sanitized = sanitized.replace(token, '')
        
        # Escape any remaining HTML-like tags
        sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        # Add safety prefix for tracking
        safety_prefix = "[SAFE] User request: "
        sanitized = safety_prefix + sanitized
        
        return True, sanitized, None
    
    @staticmethod
    def validate_llm_response(response: str, expected_format: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate LLM response for safety and expected format.
        
        Args:
            response: LLM response to validate
            expected_format: Expected format (json, text, etc.)
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not response:
            return False, "Empty response"
        
        # Check for script injection in response
        dangerous_patterns = [
            '<script', 'javascript:', 'eval(', 'onerror=', 'onclick=',
            'document.write', 'innerHTML', 'outerHTML'
        ]
        response_lower = response.lower()
        for pattern in dangerous_patterns:
            if pattern in response_lower:
                logger.warning(f"Dangerous pattern in LLM response: {pattern}")
                return False, f"Response contains dangerous pattern: {pattern}"
        
        # Validate expected format
        if expected_format == 'json':
            try:
                json.loads(response)
            except json.JSONDecodeError as e:
                return False, f"Invalid JSON format: {str(e)}"
        
        # Check response length
        if len(response) > 100000:  # 100KB limit
            return False, "Response too large"
        
        return True, None


class RateLimiter:
    """Enhanced rate limiting for API calls and browser actions."""
    
    def __init__(self):
        self._request_history: Dict[str, List[datetime]] = {}
        self._cleanup_interval = timedelta(minutes=5)
        self._last_cleanup = datetime.now()
    
    def check_rate_limit(self, key: str, max_requests: int, window_seconds: int = 60) -> bool:
        """
        Check if request is within rate limit with dynamic scaling.
        
        Args:
            key: Identifier for rate limiting
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
        
        Returns:
            True if within rate limit, False otherwise
        """
        self._cleanup_old_entries()
        
        now = datetime.now()
        window_start = now - timedelta(seconds=window_seconds)
        
        if key not in self._request_history:
            self._request_history[key] = []
        
        # Remove entries outside window
        self._request_history[key] = [
            timestamp for timestamp in self._request_history[key]
            if timestamp > window_start
        ]
        
        # Check rate limit
        if len(self._request_history[key]) >= max_requests:
            logger.warning(f"Rate limit exceeded for {key}: {len(self._request_history[key])}/{max_requests}")
            return False
        
        # Add current request
        self._request_history[key].append(now)
        return True
    
    def get_rate_status(self, key: str, window_seconds: int = 60) -> Dict[str, Any]:
        """Get current rate limit status."""
        if key not in self._request_history:
            return {'requests': 0, 'window_seconds': window_seconds}
        
        now = datetime.now()
        window_start = now - timedelta(seconds=window_seconds)
        
        current_requests = [
            timestamp for timestamp in self._request_history[key]
            if timestamp > window_start
        ]
        
        return {
            'requests': len(current_requests),
            'window_seconds': window_seconds,
            'last_request': max(current_requests) if current_requests else None
        }
    
    def _cleanup_old_entries(self):
        """Periodically cleanup old entries from history."""
        now = datetime.now()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        
        cutoff = now - timedelta(minutes=10)
        for key in list(self._request_history.keys()):
            self._request_history[key] = [
                timestamp for timestamp in self._request_history[key]
                if timestamp > cutoff
            ]
            if not self._request_history[key]:
                del self._request_history[key]
        
        self._last_cleanup = now


class SecureFileOperations:
    """Secure file operations with validation and atomic operations."""
    
    @staticmethod
    def safe_read(file_path: str, encoding: str = 'utf-8', max_size: int = 100 * 1024 * 1024) -> Optional[str]:
        """
        Safely read file with validation and size limits.
        
        Args:
            file_path: Path to file
            encoding: File encoding
            max_size: Maximum file size in bytes
            
        Returns:
            File contents or None if invalid/error
        """
        is_valid, safe_path, error = InputValidator.validate_file_path(file_path)
        if not is_valid:
            logger.error(f"Invalid file path: {error}")
            return None
        
        try:
            path = Path(safe_path)
            if not path.exists():
                logger.error(f"File does not exist: {safe_path}")
                return None
            
            if not path.is_file():
                logger.error(f"Path is not a file: {safe_path}")
                return None
            
            # Check file size
            if path.stat().st_size > max_size:
                logger.error(f"File too large: {path.stat().st_size} bytes (max: {max_size})")
                return None
            
            with open(path, 'r', encoding=encoding) as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Error reading file {safe_path}: {e}")
            return None
    
    @staticmethod
    def safe_write(file_path: str, content: str, encoding: str = 'utf-8', backup: bool = True) -> bool:
        """
        Safely write to file with validation and atomic operations.
        
        Args:
            file_path: Path to file
            content: Content to write
            encoding: File encoding
            backup: Whether to create backup of existing file
            
        Returns:
            True if successful
        """
        is_valid, safe_path, error = InputValidator.validate_file_path(file_path)
        if not is_valid:
            logger.error(f"Invalid file path: {error}")
            return False
        
        try:
            path = Path(safe_path)
            
            # Create backup if file exists and backup is requested
            if backup and path.exists():
                backup_path = path.with_suffix(path.suffix + '.backup')
                path.replace(backup_path)
            
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write with temporary file for atomicity
            temp_path = path.with_suffix(path.suffix + '.tmp')
            with open(temp_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            # Atomic rename
            temp_path.replace(path)
            
            return True
            
        except Exception as e:
            logger.error(f"Error writing file {safe_path}: {e}")
            return False
    
    @staticmethod
    def get_safe_temp_path(prefix: str = "ai_browser_", suffix: str = ".tmp") -> Path:
        """Get a safe temporary file path."""
        import tempfile
        temp_dir = Path(tempfile.gettempdir())
        random_name = secrets.token_hex(8)
        return temp_dir / f"{prefix}{random_name}{suffix}"


# Singleton instances for global use
_input_validator = InputValidator()
_prompt_sanitizer = PromptSanitizer()
_rate_limiter = RateLimiter()


def get_input_validator() -> InputValidator:
    """Get input validator instance."""
    return _input_validator


def get_prompt_sanitizer() -> PromptSanitizer:
    """Get prompt sanitizer instance."""
    return _prompt_sanitizer


def get_rate_limiter() -> RateLimiter:
    """Get rate limiter instance."""
    return _rate_limiter


def validate_and_sanitize_input(input_type: str, value: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Convenience function to validate and sanitize different input types.
    
    Args:
        input_type: Type of input ('url', 'selector', 'text', 'script', 'prompt', 'file')
        value: Input value to validate
        
    Returns:
        Tuple of (is_valid, sanitized_value, error_message)
    """
    validator = get_input_validator()
    
    if input_type == 'url':
        return validator.validate_url(value)
    elif input_type == 'selector':
        return validator.validate_selector(value)
    elif input_type == 'text':
        return validator.validate_text_input(value)
    elif input_type == 'script':
        return validator.validate_javascript(value)
    elif input_type == 'prompt':
        return get_prompt_sanitizer().sanitize_prompt(value)
    elif input_type == 'file':
        return validator.validate_file_path(value)
    else:
        return False, None, f"Unknown input type: {input_type}"