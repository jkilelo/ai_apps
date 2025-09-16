"""
Configuration management using TOML
Zero external dependencies - uses built-in tomllib (Python 3.11+)
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any


class ConfigurationError(Exception):
    """Configuration validation error"""

    def __init__(self, section: str) -> None:
        super().__init__(f"Missing required config section: {section}")


class ValidationError(Exception):
    """Configuration value validation error"""

    def __init__(self, field: str, message: str) -> None:
        super().__init__(f"{field} {message}")


class ConfigManager:
    """
    Centralized configuration management

    Features:
    - TOML-based configuration
    - Environment override support
    - Validation
    - Caching for performance
    """

    def __init__(self, config_path: Path = Path("config/config.toml")):
        """Initialize with config path"""
        self.config_path = config_path
        self._config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load and validate configuration"""
        if not self.config_path.exists():
            # Return defaults if no config
            return self._get_defaults()

        try:
            with open(self.config_path, "rb") as f:
                config = tomllib.load(f)
        except Exception as e:
            print(f"Warning: Failed to load config from {self.config_path}: {e}")
            return self._get_defaults()

        # Validate and merge with defaults
        defaults = self._get_defaults()
        merged_config = self._merge_configs(defaults, config)
        self._validate_config(merged_config)

        return merged_config

    def _get_defaults(self) -> dict[str, Any]:
        """Get default configuration"""
        return {
            "framework": {
                "version": "3.0.0",
                "name": "UI Testing Framework V3",
            },
            "browser": {
                "default": "stealth",
                "headless": False,  # ALWAYS False for debugging
                "timeout": 30000,
                "max_instances": 3,
                "anti_bot_level": "maximum",
                "shadow_dom_enabled": True,
                "shadow_dom_max_depth": 5,
            },
            "extraction": {
                "default_profile": "qa",  # QA-first mindset
                "cache_size": 100,
                "max_elements": 100,
                "cache_ttl": 3600,
            },
            "formatter": {
                "default": "llm_test",
                "token_optimization": True,
                "max_tokens": 4000,
            },
            "test_generator": {
                "default": "simple",
                "provider": "gemini",
                "model": "gemini-2.5-pro",
                "temperature": 0.7,
                "max_tests_per_page": 20,
            },
            "storage": {
                "default": "sqlite",
                "type": "sqlite",
                "path": "data/storage.db",
                "cleanup_days": 30,
                "deduplication": True,
            },
            "logging": {
                "level": "INFO",
                "format": "json",
                "file": "logs/framework.log",
                "max_size": "10MB",
                "max_files": 5,
            },
            "events": {
                "history_size": 1000,
                "emit_metrics": True,
            },
            "performance": {
                "enable_profiling": False,
                "cache_strategy": "lru",
                "async_timeout": 60,
            },
        }

    def _merge_configs(self, defaults: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
        """Merge user config with defaults"""
        merged = defaults.copy()

        for section, values in config.items():
            if section in merged and isinstance(values, dict):
                merged[section].update(values)
            else:
                merged[section] = values

        return merged

    def _validate_config(self, config: dict[str, Any]) -> None:
        """Validate configuration"""
        # Ensure headless is False (critical for debugging)
        if config.get("browser", {}).get("headless", False):
            print("WARNING: headless=True detected, overriding to False for debugging")
            config["browser"]["headless"] = False

        # Validate required sections
        required = ["browser", "extraction", "storage"]
        for section in required:
            if section not in config:
                raise ConfigurationError(section)

        # Validate timeout values
        timeout = config.get("browser", {}).get("timeout", 30000)
        if not isinstance(timeout, int) or timeout <= 0:
            raise ValidationError("browser.timeout", "must be a positive integer")

        # Validate cache sizes
        cache_size = config.get("extraction", {}).get("cache_size", 100)
        if not isinstance(cache_size, int) or cache_size <= 0:
            raise ValidationError("extraction.cache_size", "must be a positive integer")

    def get(self, path: str, default: Any = None) -> Any:
        """
        Get config value by dot notation

        Example: config.get('browser.timeout', 30000)
        """
        keys = path.split(".")
        value = self._config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, path: str, value: Any) -> None:
        """
        Set config value by dot notation

        Example: config.set('browser.headless', False)
        """
        keys = path.split(".")
        current = self._config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def reload(self) -> None:
        """Reload configuration from file"""
        self._config = self._load_config()

    def to_dict(self) -> dict[str, Any]:
        """Get full configuration as dictionary"""
        return self._config.copy()


# Global configuration manager
config_manager = ConfigManager()
