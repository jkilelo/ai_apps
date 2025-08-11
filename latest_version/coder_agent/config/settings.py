#!/usr/bin/env python3
"""
Configuration settings for CODER Agent
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


DEFAULT_CONFIG = {
    "engine": {
        "max_retries": 3,
        "timeout_multiplier": 1.5,
        "require_tests": True
    },
    "context": {
        "max_tokens": 200000,
        "reserved_tokens": 10000,
        "compression_threshold": 0.75
    },
    "tools": {
        "prefer_ripgrep": True,
        "batch_operations": True,
        "parallel_threshold": 3
    },
    "planner": {
        "max_parallel": 3,
        "break_complexity_threshold": 10,
        "token_estimation_multiplier": 1.2
    },
    "meta": {
        "confidence_threshold": 0.7,
        "quality_threshold": 0.8,
        "cognitive_load_threshold": 0.8
    },
    "llm": {
        "provider": os.environ.get("LLM_PROVIDER", "openai"),
        "model": os.environ.get("LLM_MODEL", "gpt-4"),
        "api_key": os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"),
        "temperature": 0.7,
        "max_tokens": 4000,
        "timeout": 60
    },
    "safety": {
        "enable_safety_checks": True,
        "allow_file_deletion": False,
        "allow_system_commands": True,
        "require_confirmation": ["delete", "rm", "format"],
        "blocked_commands": ["sudo rm -rf /", "format c:"]
    },
    "monitoring": {
        "enable_telemetry": False,
        "log_level": "INFO",
        "metrics_endpoint": None
    }
}


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from file or environment.
    
    Priority order:
    1. Provided config file
    2. CODER_CONFIG environment variable
    3. ./coder_config.json
    4. ~/.coder/config.json
    5. Default configuration
    """
    config = DEFAULT_CONFIG.copy()
    
    # Try to load from various sources
    config_files = []
    
    if config_path:
        config_files.append(Path(config_path))
    
    if os.environ.get("CODER_CONFIG"):
        config_files.append(Path(os.environ["CODER_CONFIG"]))
    
    config_files.extend([
        Path("./coder_config.json"),
        Path.home() / ".coder" / "config.json"
    ])
    
    # Load first available config file
    for config_file in config_files:
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    config = merge_configs(config, user_config)
                    break
            except Exception as e:
                print(f"Warning: Failed to load config from {config_file}: {e}")
    
    # Override with environment variables
    config = apply_env_overrides(config)
    
    # Validate configuration
    validate_config(config)
    
    return config


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge configuration dictionaries.
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result


def apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply environment variable overrides.
    
    Environment variables follow pattern: CODER_<SECTION>_<KEY>
    Example: CODER_LLM_MODEL=gpt-4-turbo
    """
    env_mapping = {
        "CODER_LLM_PROVIDER": ("llm", "provider"),
        "CODER_LLM_MODEL": ("llm", "model"),
        "CODER_LLM_API_KEY": ("llm", "api_key"),
        "CODER_LLM_TEMPERATURE": ("llm", "temperature"),
        "CODER_ENGINE_REQUIRE_TESTS": ("engine", "require_tests"),
        "CODER_CONTEXT_MAX_TOKENS": ("context", "max_tokens"),
        "CODER_SAFETY_ALLOW_DELETION": ("safety", "allow_file_deletion"),
        "CODER_MONITORING_LOG_LEVEL": ("monitoring", "log_level")
    }
    
    for env_var, (section, key) in env_mapping.items():
        if env_var in os.environ:
            value = os.environ[env_var]
            
            # Type conversion
            if value.lower() in ["true", "false"]:
                value = value.lower() == "true"
            elif value.isdigit():
                value = int(value)
            elif "." in value and value.replace(".", "").isdigit():
                value = float(value)
            
            if section in config:
                config[section][key] = value
    
    return config


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate configuration for required fields and constraints.
    """
    # Check for LLM configuration
    if not config.get("llm", {}).get("api_key"):
        if config.get("llm", {}).get("provider") != "local":
            raise ValueError(
                "No LLM API key configured. "
                "Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable."
            )
    
    # Check token limits
    max_tokens = config.get("context", {}).get("max_tokens", 200000)
    reserved = config.get("context", {}).get("reserved_tokens", 10000)
    
    if reserved >= max_tokens:
        raise ValueError(f"Reserved tokens ({reserved}) must be less than max tokens ({max_tokens})")
    
    # Check safety settings
    if config.get("safety", {}).get("allow_file_deletion"):
        print("⚠️  Warning: File deletion is enabled. Use with caution.")


def save_config(config: Dict[str, Any], path: Optional[str] = None) -> None:
    """
    Save configuration to file.
    """
    if not path:
        config_dir = Path.home() / ".coder"
        config_dir.mkdir(exist_ok=True)
        path = config_dir / "config.json"
    else:
        path = Path(path)
    
    with open(path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Configuration saved to {path}")


def create_example_config(path: Optional[str] = None) -> None:
    """
    Create an example configuration file.
    """
    example_config = {
        "llm": {
            "provider": "openai",
            "model": "gpt-4",
            "api_key": "your-api-key-here",
            "temperature": 0.7
        },
        "engine": {
            "require_tests": True
        },
        "context": {
            "max_tokens": 200000
        },
        "safety": {
            "allow_file_deletion": False
        }
    }
    
    if not path:
        path = "coder_config.example.json"
    
    with open(path, 'w') as f:
        json.dump(example_config, f, indent=2)
    
    print(f"Example configuration created at {path}")
    print("Edit this file and rename to coder_config.json")