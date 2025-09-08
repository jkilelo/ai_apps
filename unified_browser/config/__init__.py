"""
Configuration module for unified browser.

This module provides all configuration classes and factories for managing
browser settings, including browser engine, navigation, extraction, stealth,
security, performance, and AI configurations.
"""

from .ai_config import (
    AgentConfig,
    AIConfig,
    ConversationConfig,
    DecisionConfig,
    ModelConfig,
    PromptConfig,
    ProviderAPIConfig,
    VisionConfig,
)
from .browser_config import (
    BrowserConfig,
    ViewportConfig,
    ProxyConfig,
    GeolocationConfig,
    ResourceBlockingConfig,
    ProfileConfig,
    DownloadConfig,
    NetworkConfig,
    PermissionsConfig,
    EmulationConfig,
    DebugConfig,
    CacheConfig,
)
from .config_factory import (
    ConfigFactory,
    ConfigProfile,
    UnifiedConfig,
)
from .extraction_config import (
    BatchExtractionConfig,
    ExtractionConfig,
    ExtractionPerformanceConfig,
    FormExtractionConfig,
    LinkExtractionConfig,
    MediaExtractionConfig,
    MetadataExtractionConfig,
    ShadowDOMConfig,
    TableExtractionConfig,
    TextExtractionConfig,
    XPathConfig,
)
from .navigation_config import (
    HistoryConfig,
    InterceptionConfig,
    NavigationConfig,
    PerformanceConfig as NavPerformanceConfig,
    RedirectConfig,
    RetryConfig,
    ScrollConfig,
    WaitStrategyConfig,
)
from .performance_config import (
    CachingConfig,
    MemoryConfig,
    MetricsConfig,
    NetworkConfig as PerfNetworkConfig,
    OptimizationConfig,
    PerformanceConfig,
    PreloadConfig,
    RenderingConfig,
    ResourceBlockingConfig,
    ThrottlingConfig,
)
from .security_config import (
    AuditConfig,
    AuthenticationConfig,
    ContentSecurityConfig,
    EncryptionConfig,
    RateLimitConfig,
    SandboxConfig,
    SecurityConfig,
    ValidationConfig,
)
from .stealth_config import (
    FingerprintConfig,
    NavigatorOverrides,
    ChromeOverrides,
    WebGLOverrides,
    MediaDevicesOverrides,
    StealthConfig,
)

__all__ = [
    # Main factory and profiles
    "ConfigFactory",
    "ConfigProfile",
    "UnifiedConfig",
    # Browser configuration
    "BrowserConfig",
    "ViewportConfig",
    "ProxyConfig",
    "GeolocationConfig",
    "ResourceBlockingConfig",
    "ProfileConfig",
    "DownloadConfig",
    "NetworkConfig",
    "PermissionsConfig",
    "EmulationConfig",
    "DebugConfig",
    "CacheConfig",
    # Navigation configuration
    "NavigationConfig",
    "WaitStrategyConfig",
    "RetryConfig",
    "RedirectConfig",
    "ScrollConfig",
    "HistoryConfig",
    "NavPerformanceConfig",
    "InterceptionConfig",
    # Extraction configuration
    "ExtractionConfig",
    "TextExtractionConfig",
    "TableExtractionConfig",
    "FormExtractionConfig",
    "LinkExtractionConfig",
    "MediaExtractionConfig",
    "MetadataExtractionConfig",
    "ShadowDOMConfig",
    "XPathConfig",
    "BatchExtractionConfig",
    "ExtractionPerformanceConfig",
    # Stealth configuration
    "StealthConfig",
    "FingerprintConfig",
    "NavigatorOverrides",
    "ChromeOverrides",
    "WebGLOverrides",
    "MediaDevicesOverrides",
    # Security configuration
    "SecurityConfig",
    "ValidationConfig",
    "RateLimitConfig",
    "SandboxConfig",
    "AuthenticationConfig",
    "EncryptionConfig",
    "AuditConfig",
    "ContentSecurityConfig",
    # Performance configuration
    "PerformanceConfig",
    "ResourceBlockingConfig",
    "CachingConfig",
    "PerfNetworkConfig",
    "RenderingConfig",
    "MemoryConfig",
    "PreloadConfig",
    "MetricsConfig",
    "OptimizationConfig",
    "ThrottlingConfig",
    # AI configuration
    "AIConfig",
    "ModelConfig",
    "VisionConfig",
    "AgentConfig",
    "PromptConfig",
    "ConversationConfig",
    "DecisionConfig",
    "ProviderAPIConfig",
]
