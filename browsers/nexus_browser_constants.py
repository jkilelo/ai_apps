#!/usr/bin/env python3
"""
NEXUS Browser Constants Module.

Task: ENV-005
Centralized constants and configuration values for the NEXUS Browser system.
Full compliance with mypy --strict, flake8, and 100% type coverage.
Uses Pydantic v2 for complex constant structures.
"""

from typing import Final, Dict, Tuple, FrozenSet
from pathlib import Path
from enum import Enum, IntEnum
from pydantic import BaseModel, Field, ConfigDict


# Version Information
VERSION: Final[str] = "0.0.1"
VERSION_MAJOR: Final[int] = 0
VERSION_MINOR: Final[int] = 0
VERSION_PATCH: Final[int] = 1
VERSION_TUPLE: Final[Tuple[int, int, int]] = (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)

# Task Information
TASK_ID: Final[str] = "ENV-005"
MODULE_NAME: Final[str] = "constants"
QUALITY_ENFORCED: Final[bool] = True
TOTAL_TASKS: Final[int] = 5700

# System Limits
MAX_RETRIES: Final[int] = 3
DEFAULT_TIMEOUT: Final[int] = 300  # seconds
MAX_CONCURRENT_WORKERS: Final[int] = 10
MAX_QUEUE_SIZE: Final[int] = 1000
MAX_CACHE_SIZE: Final[int] = 100 * 1024 * 1024  # 100MB
MAX_LOG_SIZE: Final[int] = 10 * 1024 * 1024  # 10MB
MAX_MEMORY_USAGE: Final[int] = 2 * 1024 * 1024 * 1024  # 2GB

# Network Constants
DEFAULT_PORT: Final[int] = 8080
DEFAULT_HOST: Final[str] = "127.0.0.1"
API_VERSION: Final[str] = "v1"
USER_AGENT: Final[str] = f"NEXUS-Browser/{VERSION}"
CONNECTION_POOL_SIZE: Final[int] = 20
SOCKET_TIMEOUT: Final[int] = 60  # seconds

# File System Constants
BASE_DIR: Final[Path] = Path(__file__).parent.absolute()
LOGS_DIR: Final[Path] = BASE_DIR / "logs"
CACHE_DIR: Final[Path] = BASE_DIR / ".cache"
TEMP_DIR: Final[Path] = BASE_DIR / ".tmp"
DATA_DIR: Final[Path] = BASE_DIR / "data"
CHECKPOINTS_DIR: Final[Path] = BASE_DIR / "nexus_checkpoints"

# File Extensions
PYTHON_EXTENSIONS: Final[FrozenSet[str]] = frozenset({".py", ".pyw", ".pyx"})
DATA_EXTENSIONS: Final[FrozenSet[str]] = frozenset({".json", ".yaml", ".yml", ".toml", ".xml"})
IMAGE_EXTENSIONS: Final[FrozenSet[str]] = frozenset({".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg"})
ALLOWED_EXTENSIONS: Final[FrozenSet[str]] = PYTHON_EXTENSIONS | DATA_EXTENSIONS | IMAGE_EXTENSIONS

# Quantum Module Constants
QUANTUM_DIMENSIONS: Final[int] = 11
QUANTUM_STATES: Final[int] = 256
QUANTUM_ENTANGLEMENT_THRESHOLD: Final[float] = 0.95
QUANTUM_COHERENCE_TIME: Final[float] = 1.5  # seconds
QUANTUM_ERROR_RATE: Final[float] = 0.001
QUANTUM_GATE_FIDELITY: Final[float] = 0.999

# Holographic Module Constants
HOLOGRAM_RESOLUTION: Final[Tuple[int, int]] = (4096, 4096)
HOLOGRAM_DEPTH: Final[int] = 256
FOURIER_SAMPLES: Final[int] = 1024
INTERFERENCE_PATTERNS: Final[int] = 128
RECONSTRUCTION_ITERATIONS: Final[int] = 100
HOLOGRAM_COMPRESSION_RATIO: Final[float] = 0.1

# Evolution Module Constants
POPULATION_SIZE: Final[int] = 100
GENERATIONS: Final[int] = 1000
MUTATION_RATE: Final[float] = 0.01
CROSSOVER_RATE: Final[float] = 0.7
ELITE_SIZE: Final[int] = 10
FITNESS_THRESHOLD: Final[float] = 0.95

# Consciousness Module Constants
CONSCIOUSNESS_LAYERS: Final[int] = 7
AWARENESS_LEVELS: Final[int] = 5
SYNCHRONIZATION_FREQUENCY: Final[float] = 40.0  # Hz
INTEGRATION_THRESHOLD: Final[float] = 0.8
EMERGENCE_ITERATIONS: Final[int] = 500
CONSCIOUSNESS_DECAY_RATE: Final[float] = 0.1

# MCP Neural Constants
NEURAL_LAYERS: Final[int] = 12
NEURONS_PER_LAYER: Final[int] = 768
ATTENTION_HEADS: Final[int] = 12
DROPOUT_RATE: Final[float] = 0.1
LEARNING_RATE: Final[float] = 0.001
BATCH_SIZE: Final[int] = 32


class Priority(IntEnum):
    """Task priority levels."""

    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    MINIMAL = 4


class Status(str, Enum):
    """Task and module status values."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    RETRY = "retry"


class ModuleType(str, Enum):
    """NEXUS module types."""

    ENVIRONMENT = "ENV"
    HOLOGRAPHIC = "HOL"
    EVOLUTION = "EVO"
    CONSCIOUSNESS = "CON"
    QUANTUM = "QUA"
    MCP = "MCP"
    NEXUS = "NEX"


class QuantumState(str, Enum):
    """Quantum state representations."""

    SUPERPOSITION = "superposition"
    ENTANGLED = "entangled"
    COLLAPSED = "collapsed"
    COHERENT = "coherent"
    DECOHERENT = "decoherent"


class SystemLimits(BaseModel):
    """System resource limits configuration."""

    model_config = ConfigDict(frozen=True)

    max_memory_mb: int = Field(default=2048, ge=128)
    max_cpu_percent: float = Field(default=80.0, ge=1.0, le=100.0)
    max_disk_io_mbps: float = Field(default=100.0, ge=1.0)
    max_network_mbps: float = Field(default=100.0, ge=1.0)
    max_threads: int = Field(default=100, ge=1)
    max_processes: int = Field(default=10, ge=1)


class PerformanceMetrics(BaseModel):
    """Performance metric thresholds."""

    model_config = ConfigDict(frozen=True)

    latency_ms_p50: float = Field(default=100.0, ge=0.0)
    latency_ms_p95: float = Field(default=500.0, ge=0.0)
    latency_ms_p99: float = Field(default=1000.0, ge=0.0)
    throughput_rps: float = Field(default=1000.0, ge=0.0)
    error_rate_percent: float = Field(default=1.0, ge=0.0, le=100.0)
    availability_percent: float = Field(default=99.9, ge=0.0, le=100.0)


class FeatureFlags(BaseModel):
    """Feature flag configuration."""

    model_config = ConfigDict(frozen=True)

    enable_quantum: bool = Field(default=True)
    enable_holographic: bool = Field(default=True)
    enable_evolution: bool = Field(default=True)
    enable_consciousness: bool = Field(default=True)
    enable_mcp: bool = Field(default=True)
    enable_caching: bool = Field(default=True)
    enable_compression: bool = Field(default=True)
    enable_encryption: bool = Field(default=True)
    enable_monitoring: bool = Field(default=True)
    enable_profiling: bool = Field(default=False)
    enable_debug: bool = Field(default=False)


# Regex Patterns
TASK_ID_PATTERN: Final[str] = r"^[A-Z]{3}-\d{3,4}$"
MODULE_NAME_PATTERN: Final[str] = r"^[a-z_]+$"
VERSION_PATTERN: Final[str] = r"^\d+\.\d+\.\d+$"
UUID_PATTERN: Final[str] = (
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)

# Error Messages
ERROR_MESSAGES: Final[Dict[str, str]] = {
    "CONFIG_NOT_FOUND": "Configuration file not found: {path}",
    "INVALID_CONFIG": "Invalid configuration: {error}",
    "MODULE_NOT_FOUND": "Module not found: {module}",
    "TASK_NOT_FOUND": "Task not found: {task_id}",
    "QUANTUM_ERROR": "Quantum operation failed: {error}",
    "HOLOGRAM_ERROR": "Holographic processing failed: {error}",
    "EVOLUTION_ERROR": "Evolution process failed: {error}",
    "CONSCIOUSNESS_ERROR": "Consciousness integration failed: {error}",
    "MCP_ERROR": "MCP neural operation failed: {error}",
    "INTEGRATION_ERROR": "Module integration failed: {source} -> {target}",
}

# Success Messages
SUCCESS_MESSAGES: Final[Dict[str, str]] = {
    "MODULE_LOADED": "Module loaded successfully: {module}",
    "TASK_COMPLETED": "Task completed: {task_id}",
    "CONFIG_LOADED": "Configuration loaded from: {path}",
    "SYSTEM_READY": "NEXUS Browser system ready",
    "QUANTUM_INITIALIZED": "Quantum subsystem initialized",
    "HOLOGRAM_CREATED": "Holographic matrix created",
    "EVOLUTION_COMPLETE": "Evolution cycle complete",
    "CONSCIOUSNESS_ACHIEVED": "Consciousness integration achieved",
    "MCP_CONNECTED": "MCP neural network connected",
}

# Environment Variables
ENV_VARS: Final[Dict[str, str]] = {
    "NEXUS_HOME": "NEXUS_HOME",
    "NEXUS_CONFIG": "NEXUS_CONFIG_PATH",
    "NEXUS_LOG_LEVEL": "NEXUS_LOG_LEVEL",
    "NEXUS_DEBUG": "NEXUS_DEBUG",
    "NEXUS_API_KEY": "NEXUS_API_KEY",
    "NEXUS_MODE": "NEXUS_MODE",
    "NEXUS_WORKERS": "NEXUS_MAX_WORKERS",
    "NEXUS_TIMEOUT": "NEXUS_TIMEOUT",
}

# HTTP Headers
HTTP_HEADERS: Final[Dict[str, str]] = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json",
    "Content-Type": "application/json",
    "X-NEXUS-Version": VERSION,
    "X-NEXUS-API-Version": API_VERSION,
}

# MIME Types
MIME_TYPES: Final[Dict[str, str]] = {
    ".json": "application/json",
    ".yaml": "application/x-yaml",
    ".yml": "application/x-yaml",
    ".xml": "application/xml",
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".py": "text/x-python",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
}

# Color Codes (for terminal output)
COLORS: Final[Dict[str, str]] = {
    "RESET": "\033[0m",
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "MAGENTA": "\033[95m",
    "CYAN": "\033[96m",
    "WHITE": "\033[97m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m",
}


def get_module_prefix(module_type: ModuleType) -> str:
    """
    Get the prefix for a module type.

    Args:
        module_type: The module type enum

    Returns:
        str: The module prefix
    """
    return module_type.value


def get_task_id(module_type: ModuleType, task_number: int) -> str:
    """
    Generate a task ID from module type and number.

    Args:
        module_type: The module type
        task_number: The task number

    Returns:
        str: The formatted task ID
    """
    return f"{module_type.value}-{task_number:03d}"


def validate_task_id(task_id: str) -> bool:
    """
    Validate a task ID format.

    Args:
        task_id: The task ID to validate

    Returns:
        bool: True if valid, False otherwise
    """
    import re

    return bool(re.match(TASK_ID_PATTERN, task_id))


# Global instances for common use
DEFAULT_LIMITS: Final[SystemLimits] = SystemLimits()
DEFAULT_METRICS: Final[PerformanceMetrics] = PerformanceMetrics()
DEFAULT_FLAGS: Final[FeatureFlags] = FeatureFlags()


if __name__ == "__main__":
    print(f"[CONSTANTS] NEXUS Browser Constants Module (Task: {TASK_ID})")
    print(f"[CONSTANTS] Version: {VERSION}")
    print(f"[CONSTANTS] Quality Enforcement: {QUALITY_ENFORCED}")

    # Display some key constants
    print("\n[CONSTANTS] System Configuration:")
    print(f"  Total Tasks: {TOTAL_TASKS}")
    print(f"  Max Workers: {MAX_CONCURRENT_WORKERS}")
    print(f"  Default Timeout: {DEFAULT_TIMEOUT}s")
    print(f"  Quantum Dimensions: {QUANTUM_DIMENSIONS}")
    print(f"  Neural Layers: {NEURAL_LAYERS}")

    # Test utility functions
    test_id = get_task_id(ModuleType.ENVIRONMENT, 5)
    print(f"\n[CONSTANTS] Generated task ID: {test_id}")
    print(f"[CONSTANTS] Valid format: {validate_task_id(test_id)}")

    print("\n[CONSTANTS] Module initialized successfully")
