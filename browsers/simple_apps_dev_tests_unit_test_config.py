"""
Tests for application configuration.
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from simple_apps_v2.core.config import Settings, get_settings


class TestSettings:
    """Test Settings class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        settings = Settings()
        
        assert settings.app_name == "Simple Apps v2"
        assert settings.version == "1.0.0"
        assert settings.debug is False
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 5175
        assert settings.browser_headless is True
        assert settings.log_level == "INFO"
    
    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        with patch.dict(os.environ, {
            "APP_NAME": "Test App",
            "DEBUG": "true",
            "API_PORT": "8000",
            "LOG_LEVEL": "DEBUG"
        }):
            settings = Settings()
            
            assert settings.app_name == "Test App"
            assert settings.debug is True
            assert settings.api_port == 8000
            assert settings.log_level == "DEBUG"
    
    def test_cors_origins_parsing(self):
        """Test CORS origins parsing from string."""
        with patch.dict(os.environ, {
            "CORS_ORIGINS": "http://localhost:3000,http://localhost:3001"
        }):
            settings = Settings()
            
            expected_origins = ["http://localhost:3000", "http://localhost:3001"]
            assert settings.cors_origins == expected_origins
    
    def test_path_validation(self):
        """Test path field validation."""
        with patch.dict(os.environ, {
            "TEST_OUTPUT_DIR": "/tmp/test",
            "SCREENSHOT_DIR": "/tmp/screenshots"
        }):
            settings = Settings()
            
            assert isinstance(settings.test_output_dir, Path)
            assert isinstance(settings.screenshot_dir, Path)
            assert str(settings.test_output_dir) == "/tmp/test"
    
    def test_create_directories(self, tmp_path):
        """Test directory creation."""
        with patch.dict(os.environ, {
            "TEST_OUTPUT_DIR": str(tmp_path / "test_output"),
            "SCREENSHOT_DIR": str(tmp_path / "screenshots")
        }):
            settings = Settings()
            settings.create_directories()
            
            assert settings.test_output_dir.exists()
            assert settings.screenshot_dir.exists()
    
    def test_llm_config_property(self):
        """Test LLM configuration property."""
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-openai-key",
            "GOOGLE_API_KEY": "test-google-key",
            "DEFAULT_LLM_PROVIDER": "openai",
            "DEFAULT_LLM_MODEL": "gpt-4"
        }):
            settings = Settings()
            llm_config = settings.llm_config
            
            assert llm_config["provider"] == "openai"
            assert llm_config["model"] == "gpt-4"
            assert llm_config["api_keys"]["openai"] == "test-openai-key"
            assert llm_config["api_keys"]["google"] == "test-google-key"
    
    def test_browser_config_property(self):
        """Test browser configuration property."""
        with patch.dict(os.environ, {
            "BROWSER_HEADLESS": "false",
            "BROWSER_TIMEOUT": "60000"
        }):
            settings = Settings()
            browser_config = settings.browser_config
            
            assert browser_config["headless"] is False
            assert browser_config["timeout"] == 60000


class TestGetSettings:
    """Test get_settings function."""
    
    def test_caching(self):
        """Test that get_settings returns cached instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2
    
    def test_environment_changes_not_reflected(self):
        """Test that environment changes don't affect cached settings."""
        # Get initial settings
        initial_settings = get_settings()
        initial_app_name = initial_settings.app_name
        
        # Change environment (this won't affect cached settings)
        with patch.dict(os.environ, {"APP_NAME": "Changed App"}):
            current_settings = get_settings()
            # Should still have the original value due to caching
            assert current_settings.app_name == initial_app_name
    
    @pytest.fixture(autouse=True)
    def clear_settings_cache(self):
        """Clear settings cache before each test."""
        # Clear the lru_cache
        get_settings.cache_clear()
        yield
        get_settings.cache_clear()