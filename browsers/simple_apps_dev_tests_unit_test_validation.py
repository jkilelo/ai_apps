"""
Tests for validation utilities.
"""

import pytest

from simple_apps_v2.utils.validation import (
    validate_url, validate_json, validate_email, validate_selector,
    validate_test_priority, validate_element_category, validate_file_extension,
    validate_port, validate_timeout, validate_coordinates,
    validate_browser_config, sanitize_filename, validate_extraction_request,
    is_safe_path
)


class TestValidateUrl:
    """Test URL validation."""
    
    @pytest.mark.parametrize("url", [
        "https://example.com",
        "http://localhost:3000",
        "https://sub.domain.com/path?query=value",
        "http://192.168.1.1:8080",
    ])
    def test_valid_urls(self, url):
        """Test valid URL formats."""
        assert validate_url(url) is True
    
    @pytest.mark.parametrize("url", [
        "not-a-url",
        "ftp://example.com",  # Wrong scheme
        "https://",  # No domain
        "example.com",  # No scheme
        "",  # Empty
        "javascript:alert('xss')",  # Dangerous scheme
    ])
    def test_invalid_urls(self, url):
        """Test invalid URL formats."""
        assert validate_url(url) is False


class TestValidateJson:
    """Test JSON validation."""
    
    def test_valid_json_string(self):
        """Test valid JSON string."""
        assert validate_json('{"key": "value"}') is True
    
    def test_valid_json_dict(self):
        """Test valid JSON dict."""
        assert validate_json({"key": "value"}) is True
    
    def test_valid_json_list(self):
        """Test valid JSON list."""
        assert validate_json([1, 2, 3]) is True
    
    @pytest.mark.parametrize("data", [
        "not json",
        '{"invalid": json}',  # Invalid JSON
        '{key: "value"}',  # Unquoted key
    ])
    def test_invalid_json(self, data):
        """Test invalid JSON."""
        assert validate_json(data) is False


class TestValidateEmail:
    """Test email validation."""
    
    @pytest.mark.parametrize("email", [
        "test@example.com",
        "user.name@domain.co.uk",
        "user+tag@example.org",
        "123@456.com",
    ])
    def test_valid_emails(self, email):
        """Test valid email formats."""
        assert validate_email(email) is True
    
    @pytest.mark.parametrize("email", [
        "notanemail",
        "@example.com",  # Missing local part
        "test@",  # Missing domain
        "test..test@example.com",  # Double dot
        "test@example",  # Missing TLD
    ])
    def test_invalid_emails(self, email):
        """Test invalid email formats."""
        assert validate_email(email) is False


class TestValidateSelector:
    """Test CSS selector validation."""
    
    @pytest.mark.parametrize("selector", [
        "#myid",
        ".myclass",
        "div",
        "input[type='text']",
        "div.class#id",
        "nav > ul > li",
        ".class1.class2",
    ])
    def test_valid_selectors(self, selector):
        """Test valid CSS selectors."""
        assert validate_selector(selector) is True
    
    @pytest.mark.parametrize("selector", [
        "",
        None,
        123,  # Not a string
        ">>>invalid",  # Invalid syntax
    ])
    def test_invalid_selectors(self, selector):
        """Test invalid CSS selectors."""
        assert validate_selector(selector) is False


class TestValidateTestPriority:
    """Test test priority validation."""
    
    @pytest.mark.parametrize("priority", [
        "critical", "high", "medium", "low",
        "CRITICAL", "High", "Medium", "LOW",  # Case insensitive
    ])
    def test_valid_priorities(self, priority):
        """Test valid test priorities."""
        assert validate_test_priority(priority) is True
    
    @pytest.mark.parametrize("priority", [
        "invalid", "urgent", "", None
    ])
    def test_invalid_priorities(self, priority):
        """Test invalid test priorities."""
        assert validate_test_priority(priority) is False


class TestValidateElementCategory:
    """Test element category validation."""
    
    @pytest.mark.parametrize("category", [
        "navigation", "form_input", "button", "link", "text_display",
        "media", "interactive", "container", "other",
        "NAVIGATION", "Form_Input",  # Case insensitive
    ])
    def test_valid_categories(self, category):
        """Test valid element categories."""
        assert validate_element_category(category) is True
    
    def test_invalid_categories(self):
        """Test invalid element categories."""
        assert validate_element_category("invalid") is False


class TestValidateFileExtension:
    """Test file extension validation."""
    
    def test_valid_extension(self):
        """Test valid file extension."""
        assert validate_file_extension("test.py", [".py", ".js"]) is True
    
    def test_case_insensitive(self):
        """Test case insensitive extension matching."""
        assert validate_file_extension("test.PY", [".py"]) is True
    
    def test_invalid_extension(self):
        """Test invalid file extension."""
        assert validate_file_extension("test.txt", [".py", ".js"]) is False
    
    def test_no_extension(self):
        """Test file without extension."""
        assert validate_file_extension("test", [".py"]) is False


class TestValidatePort:
    """Test port validation."""
    
    @pytest.mark.parametrize("port", [1, 80, 443, 8080, 65535])
    def test_valid_ports(self, port):
        """Test valid port numbers."""
        assert validate_port(port) is True
    
    @pytest.mark.parametrize("port", [0, -1, 65536, "invalid", None])
    def test_invalid_ports(self, port):
        """Test invalid port numbers."""
        assert validate_port(port) is False


class TestValidateTimeout:
    """Test timeout validation."""
    
    @pytest.mark.parametrize("timeout", [1, 30, 60.5, 3600])
    def test_valid_timeouts(self, timeout):
        """Test valid timeout values."""
        assert validate_timeout(timeout) is True
    
    @pytest.mark.parametrize("timeout", [0, -1, 3601, "invalid", None])
    def test_invalid_timeouts(self, timeout):
        """Test invalid timeout values."""
        assert validate_timeout(timeout) is False


class TestValidateCoordinates:
    """Test coordinate validation."""
    
    def test_valid_coordinates(self):
        """Test valid coordinates."""
        assert validate_coordinates(100, 200) is True
        assert validate_coordinates(0, 0) is True
        assert validate_coordinates(1920.5, 1080.0) is True
    
    @pytest.mark.parametrize("x,y", [
        (-1, 100),  # Negative x
        (100, -1),  # Negative y
        (10001, 100),  # X too large
        (100, 10001),  # Y too large
        ("invalid", 100),  # Invalid type
    ])
    def test_invalid_coordinates(self, x, y):
        """Test invalid coordinates."""
        assert validate_coordinates(x, y) is False


class TestValidateBrowserConfig:
    """Test browser configuration validation."""
    
    def test_valid_config(self):
        """Test valid browser configuration."""
        config = {
            "headless": True,
            "timeout": 30000,
            "viewport_width": 1920,
            "viewport_height": 1080,
        }
        errors = validate_browser_config(config)
        assert not errors
    
    def test_invalid_config(self):
        """Test invalid browser configuration."""
        config = {
            "headless": "true",  # Should be boolean
            "timeout": -1,  # Invalid timeout
            "viewport_width": 50,  # Too small
            "viewport_height": "invalid",  # Invalid type
        }
        errors = validate_browser_config(config)
        
        assert "headless" in errors
        assert "timeout" in errors
        assert "viewport_width" in errors
        assert "viewport_height" in errors


class TestSanitizeFilename:
    """Test filename sanitization."""
    
    @pytest.mark.parametrize("filename,expected", [
        ("normal.txt", "normal.txt"),
        ("with spaces.txt", "with spaces.txt"),
        ("with<invalid>chars.txt", "with_invalid_chars.txt"),
        ("", "untitled"),
        ("   .   ", "untitled"),
    ])
    def test_sanitize_filename(self, filename, expected):
        """Test filename sanitization."""
        assert sanitize_filename(filename) == expected
    
    def test_long_filename(self):
        """Test very long filename truncation."""
        long_name = "a" * 300 + ".txt"
        sanitized = sanitize_filename(long_name)
        assert len(sanitized) <= 255
        assert sanitized.endswith(".txt")


class TestValidateExtractionRequest:
    """Test extraction request validation."""
    
    def test_valid_request(self):
        """Test valid extraction request."""
        data = {
            "url": "https://example.com",
            "headless": True,
            "analyze_with_llm": False,
            "categories": ["button", "form_input"]
        }
        errors = validate_extraction_request(data)
        assert not errors
    
    def test_missing_url(self):
        """Test request missing URL."""
        data = {"headless": True}
        errors = validate_extraction_request(data)
        assert "url" in errors
    
    def test_invalid_url(self):
        """Test request with invalid URL."""
        data = {"url": "not-a-url"}
        errors = validate_extraction_request(data)
        assert "url" in errors
    
    def test_invalid_categories(self):
        """Test request with invalid categories."""
        data = {
            "url": "https://example.com",
            "categories": ["invalid_category"]
        }
        errors = validate_extraction_request(data)
        assert "categories" in errors


class TestIsSafePath:
    """Test safe path validation."""
    
    def test_safe_relative_path(self):
        """Test safe relative path."""
        assert is_safe_path("tests/test_file.py") is True
    
    def test_directory_traversal(self):
        """Test directory traversal prevention."""
        assert is_safe_path("../../../etc/passwd") is False
        assert is_safe_path("tests/../../../etc/passwd") is False
    
    def test_absolute_path(self):
        """Test absolute path rejection."""
        assert is_safe_path("/etc/passwd") is False
    
    def test_allowed_directories(self, tmp_path):
        """Test path validation with allowed directories."""
        allowed_dirs = [str(tmp_path)]
        test_file = tmp_path / "test.txt"
        
        # This would be safe if the path resolves within allowed dir
        # For now, our simple implementation rejects all paths with ..
        assert is_safe_path("../test.txt", allowed_dirs) is False