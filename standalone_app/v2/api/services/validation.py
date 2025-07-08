"""Input validation service for security and data integrity"""
import re
from typing import Dict, Any, List, Optional
import bleach
from urllib.parse import urlparse

# Patterns for validation
URL_PATTERN = re.compile(
    r'^https?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE
)

EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# Dangerous patterns to check for
SQL_INJECTION_PATTERNS = [
    r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
    r"(--|#|/\*|\*/)",
    r"(\bor\b\s*\d+\s*=\s*\d+)",
    r"(\band\b\s*\d+\s*=\s*\d+)",
    r"('|\"|`)\s*(or|and)\s*('|\"|`)?\s*\d+\s*=\s*\d+"
]

XSS_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"on\w+\s*=",
    r"<iframe",
    r"<object",
    r"<embed"
]

def validate_prompt(prompt: str) -> Dict[str, Any]:
    """Validate LLM prompt for safety and appropriateness"""
    result = {"valid": True, "reason": None, "sanitized": prompt}
    
    # Check length
    if len(prompt) < 3:
        result["valid"] = False
        result["reason"] = "Prompt too short"
        return result
    
    if len(prompt) > 4000:
        result["valid"] = False
        result["reason"] = "Prompt too long (max 4000 characters)"
        return result
    
    # Check for SQL injection patterns
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, prompt, re.IGNORECASE):
            result["valid"] = False
            result["reason"] = "Potential SQL injection detected"
            return result
    
    # Check for XSS patterns
    for pattern in XSS_PATTERNS:
        if re.search(pattern, prompt, re.IGNORECASE):
            result["valid"] = False
            result["reason"] = "Potential XSS detected"
            return result
    
    # Sanitize HTML (allow basic formatting)
    result["sanitized"] = bleach.clean(
        prompt,
        tags=['b', 'i', 'u', 'strong', 'em', 'code', 'pre'],
        strip=True
    )
    
    return result

def validate_url(url: str) -> Dict[str, Any]:
    """Validate URL for web automation"""
    result = {"valid": True, "reason": None, "parsed": None}
    
    # Check format
    if not URL_PATTERN.match(url):
        result["valid"] = False
        result["reason"] = "Invalid URL format"
        return result
    
    # Parse URL
    try:
        parsed = urlparse(url)
        result["parsed"] = {
            "scheme": parsed.scheme,
            "domain": parsed.netloc,
            "path": parsed.path,
            "params": parsed.params,
            "query": parsed.query
        }
        
        # Check for localhost/private IPs in production
        if parsed.hostname:
            if parsed.hostname == "localhost" or parsed.hostname.startswith("127."):
                result["warning"] = "Localhost URL detected"
            elif parsed.hostname.startswith("192.168.") or parsed.hostname.startswith("10."):
                result["warning"] = "Private network URL detected"
        
        # Check scheme
        if parsed.scheme not in ["http", "https"]:
            result["valid"] = False
            result["reason"] = "Only HTTP/HTTPS URLs are allowed"
            return result
            
    except Exception as e:
        result["valid"] = False
        result["reason"] = f"URL parsing error: {str(e)}"
        return result
    
    return result

def validate_data_sample(data: str, format_hint: Optional[str] = None) -> Dict[str, Any]:
    """Validate data sample for profiling"""
    result = {"valid": True, "reason": None, "format": None, "rows": 0}
    
    # Check if empty
    if not data or not data.strip():
        result["valid"] = False
        result["reason"] = "Data sample is empty"
        return result
    
    # Try to detect format
    lines = data.strip().split('\n')
    result["rows"] = len(lines)
    
    # Check for CSV
    if ',' in lines[0] or '\t' in lines[0]:
        result["format"] = "csv"
        # Validate CSV structure
        if len(lines) < 2:
            result["warning"] = "CSV should have at least header and one data row"
    
    # Check for JSON
    elif data.strip().startswith('{') or data.strip().startswith('['):
        result["format"] = "json"
        try:
            import json
            json.loads(data)
        except:
            result["valid"] = False
            result["reason"] = "Invalid JSON format"
            return result
    
    # Check for SQL
    elif any(keyword in data.upper() for keyword in ['CREATE TABLE', 'INSERT INTO']):
        result["format"] = "sql"
        # Basic SQL validation
        for pattern in SQL_INJECTION_PATTERNS[:2]:  # Only check basic patterns
            if re.search(pattern, data, re.IGNORECASE | re.MULTILINE):
                result["warning"] = "SQL contains potentially dangerous patterns"
    
    else:
        result["format"] = "text"
        result["warning"] = "Could not detect data format"
    
    # Size check
    if len(data) > 100000:
        result["valid"] = False
        result["reason"] = "Data sample too large (max 100KB)"
        return result
    
    return result

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove path components
    filename = filename.replace('/', '').replace('\\', '')
    
    # Remove special characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    
    # Limit length
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    if len(name) > 100:
        name = name[:100]
    
    return f"{name}.{ext}" if ext else name

def validate_code_input(code: str, language: str = "python") -> Dict[str, Any]:
    """Validate code input for execution"""
    result = {"valid": True, "reason": None, "warnings": []}
    
    # Check for dangerous patterns
    dangerous_patterns = {
        "python": [
            r"\b(exec|eval|compile|__import__)\s*\(",
            r"\bos\.(system|popen|exec)",
            r"\bsubprocess\.(run|call|Popen)",
            r"\bopen\s*\([^)]*['\"]w['\"]",  # File write operations
            r"\b(requests|urllib|socket)\.",  # Network operations
        ]
    }
    
    if language in dangerous_patterns:
        for pattern in dangerous_patterns[language]:
            if re.search(pattern, code, re.IGNORECASE):
                result["warnings"].append(f"Potentially dangerous pattern detected: {pattern}")
    
    # Size check
    if len(code) > 50000:
        result["valid"] = False
        result["reason"] = "Code too large (max 50KB)"
        return result
    
    return result