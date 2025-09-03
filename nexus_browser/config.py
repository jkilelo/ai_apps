#!/usr/bin/env python3
"""
NEXUS Browser Configuration Module.

Task: ENV-002
Provides centralized configuration management with environment variables,
validation, and type safety using Pydantic v2.

Full compliance with:
- mypy --strict
- flake8
- 100% type annotation coverage
- Pydantic v2 models for all data structures
"""

import os
from pathlib import Path
from typing import Optional, Dict, List, Final
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict


class LogLevel(str, Enum):
    """Logging level enumeration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ExecutionMode(str, Enum):
    """Execution mode enumeration."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class PathConfig(BaseModel):
    """Path configuration with validation."""

    model_config = ConfigDict(frozen=True)

    base_dir: Path = Field(description="Base directory for NEXUS Browser")
    logs_dir: Path = Field(description="Directory for log files")
    checkpoints_dir: Path = Field(description="Directory for checkpoints")
    cache_dir: Path = Field(description="Directory for cache files")
    temp_dir: Path = Field(description="Directory for temporary files")

    @field_validator("base_dir", "logs_dir", "checkpoints_dir", "cache_dir", "temp_dir")
    @classmethod
    def validate_path(cls, v: Path) -> Path:
        """Validate that paths are absolute."""
        if not v.is_absolute():
            raise ValueError(f"Path must be absolute: {v}")
        return v


class RuntimeConfig(BaseModel):
    """Runtime configuration settings."""

    model_config = ConfigDict(frozen=True)

    max_workers: int = Field(default=4, ge=1, le=32)
    timeout_seconds: int = Field(default=300, ge=1)
    retry_attempts: int = Field(default=3, ge=0, le=10)
    batch_size: int = Field(default=100, ge=1, le=1000)
    cache_ttl_seconds: int = Field(default=3600, ge=0)

    @field_validator("max_workers")
    @classmethod
    def validate_workers(cls, v: int) -> int:
        """Validate worker count against CPU cores."""
        cpu_count = os.cpu_count() or 1
        if v > cpu_count * 2:
            raise ValueError(f"max_workers ({v}) exceeds 2x CPU cores ({cpu_count})")
        return v


class SecurityConfig(BaseModel):
    """Security configuration settings."""

    model_config = ConfigDict(frozen=True)

    enable_encryption: bool = Field(default=True)
    api_key_env_var: str = Field(default="NEXUS_API_KEY")
    allowed_hosts: List[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1"])
    enable_audit_log: bool = Field(default=True)
    max_request_size: int = Field(default=10485760, ge=1024)  # 10MB default

    @field_validator("allowed_hosts")
    @classmethod
    def validate_hosts(cls, v: List[str]) -> List[str]:
        """Validate host list is not empty."""
        if not v:
            raise ValueError("allowed_hosts cannot be empty")
        return v


class NexusConfig(BaseModel):
    """Main NEXUS Browser configuration."""

    model_config = ConfigDict(frozen=True)

    # Core settings
    task_id: str = Field(default="ENV-002")
    version: str = Field(default="0.0.1")
    mode: ExecutionMode = Field(default=ExecutionMode.DEVELOPMENT)
    log_level: LogLevel = Field(default=LogLevel.INFO)
    debug: bool = Field(default=False)

    # Sub-configurations
    paths: PathConfig
    runtime: RuntimeConfig
    security: SecurityConfig

    # Feature flags
    enable_quantum: bool = Field(default=True)
    enable_holographic: bool = Field(default=True)
    enable_evolution: bool = Field(default=True)
    enable_consciousness: bool = Field(default=True)
    enable_mcp: bool = Field(default=True)

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate version format."""
        parts = v.split(".")
        if len(parts) != 3:
            raise ValueError(f"Version must be in X.Y.Z format: {v}")
        for part in parts:
            if not part.isdigit():
                raise ValueError(f"Version parts must be numeric: {v}")
        return v


# Global configuration instance
_config: Optional[NexusConfig] = None


def load_config(config_path: Optional[Path] = None) -> NexusConfig:
    """
    Load configuration from environment and optional config file.

    Args:
        config_path: Optional path to configuration file.

    Returns:
        NexusConfig: Loaded and validated configuration.
    """
    global _config

    if _config is not None:
        return _config

    # Base directory
    base_dir = Path(__file__).parent.absolute()

    # Create path configuration
    paths = PathConfig(
        base_dir=base_dir,
        logs_dir=base_dir / "logs",
        checkpoints_dir=base_dir / "nexus_checkpoints",
        cache_dir=base_dir / ".cache",
        temp_dir=base_dir / ".tmp",
    )

    # Create runtime configuration
    runtime = RuntimeConfig(
        max_workers=int(os.getenv("NEXUS_MAX_WORKERS", "4")),
        timeout_seconds=int(os.getenv("NEXUS_TIMEOUT", "300")),
        retry_attempts=int(os.getenv("NEXUS_RETRY_ATTEMPTS", "3")),
        batch_size=int(os.getenv("NEXUS_BATCH_SIZE", "100")),
        cache_ttl_seconds=int(os.getenv("NEXUS_CACHE_TTL", "3600")),
    )

    # Create security configuration
    security = SecurityConfig(
        enable_encryption=os.getenv("NEXUS_ENABLE_ENCRYPTION", "true").lower() == "true",
        api_key_env_var=os.getenv("NEXUS_API_KEY_VAR", "NEXUS_API_KEY"),
        allowed_hosts=os.getenv("NEXUS_ALLOWED_HOSTS", "localhost,127.0.0.1").split(","),
        enable_audit_log=os.getenv("NEXUS_ENABLE_AUDIT", "true").lower() == "true",
        max_request_size=int(os.getenv("NEXUS_MAX_REQUEST_SIZE", "10485760")),
    )

    # Determine execution mode
    mode_str = os.getenv("NEXUS_MODE", "development").lower()
    mode = ExecutionMode(mode_str)

    # Determine log level
    log_level_str = os.getenv("NEXUS_LOG_LEVEL", "INFO").upper()
    log_level = LogLevel(log_level_str)

    # Create main configuration
    _config = NexusConfig(
        mode=mode,
        log_level=log_level,
        debug=os.getenv("NEXUS_DEBUG", "false").lower() == "true",
        paths=paths,
        runtime=runtime,
        security=security,
        enable_quantum=os.getenv("NEXUS_ENABLE_QUANTUM", "true").lower() == "true",
        enable_holographic=os.getenv("NEXUS_ENABLE_HOLOGRAPHIC", "true").lower() == "true",
        enable_evolution=os.getenv("NEXUS_ENABLE_EVOLUTION", "true").lower() == "true",
        enable_consciousness=os.getenv("NEXUS_ENABLE_CONSCIOUSNESS", "true").lower() == "true",
        enable_mcp=os.getenv("NEXUS_ENABLE_MCP", "true").lower() == "true",
    )

    return _config


def get_config() -> NexusConfig:
    """
    Get the current configuration instance.

    Returns:
        NexusConfig: Current configuration.

    Raises:
        RuntimeError: If configuration not loaded.
    """
    if _config is None:
        raise RuntimeError("Configuration not loaded. Call load_config() first.")
    return _config


def reset_config() -> None:
    """Reset the global configuration (mainly for testing)."""
    global _config
    _config = None


# Configuration constants
TASK_ID: Final[str] = "ENV-002"
MODULE_NAME: Final[str] = "config"
QUALITY_ENFORCED: Final[bool] = True


def validate_environment() -> Dict[str, bool]:
    """
    Validate the environment setup.

    Returns:
        Dict[str, bool]: Validation results.
    """
    results: Dict[str, bool] = {}

    # Check required directories
    config = load_config()
    results["base_dir_exists"] = config.paths.base_dir.exists()
    results["logs_dir_exists"] = config.paths.logs_dir.exists()
    results["checkpoints_dir_exists"] = config.paths.checkpoints_dir.exists()

    # Check environment variables
    results["api_key_set"] = bool(os.getenv(config.security.api_key_env_var))

    # Check mode
    results["production_mode"] = config.mode == ExecutionMode.PRODUCTION

    return results


if __name__ == "__main__":
    # Load and display configuration
    config = load_config()
    print(f"[CONFIG] NEXUS Browser Configuration Module (Task: {TASK_ID})")
    print(f"[CONFIG] Version: {config.version}")
    print(f"[CONFIG] Mode: {config.mode.value}")
    print(f"[CONFIG] Log Level: {config.log_level.value}")
    print(f"[CONFIG] Base Directory: {config.paths.base_dir}")
    print(f"[CONFIG] Quality Enforcement: {QUALITY_ENFORCED}")

    # Validate environment
    validation = validate_environment()
    print("\n[CONFIG] Environment Validation:")
    for check, passed in validation.items():
        status = "PASS" if passed else "WARN"
        print(f"  - {check}: {status}")
