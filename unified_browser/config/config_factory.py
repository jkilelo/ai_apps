"""
Configuration factory module.

This module provides a factory for creating and managing all browser configurations
with preset profiles and custom combinations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from ..core import BrowserEngine, LLMProvider

from .ai_config import AIConfig
from .browser_config import BrowserConfig, DebugConfig
from .extraction_config import ExtractionConfig
from .navigation_config import NavigationConfig
from .performance_config import PerformanceConfig
from .security_config import SecurityConfig
from .stealth_config import StealthConfig


class ConfigProfile(Enum):
    """Predefined configuration profiles."""

    # Basic profiles
    DEFAULT = "default"
    MINIMAL = "minimal"
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

    # Use-case specific
    SCRAPING = "scraping"
    AUTOMATION = "automation"
    MONITORING = "monitoring"
    DEBUGGING = "debugging"

    # Performance profiles
    FAST = "fast"
    BALANCED = "balanced"
    QUALITY = "quality"

    # Security profiles
    SECURE = "secure"
    STEALTH = "stealth"
    ANONYMOUS = "anonymous"

    # AI-enhanced profiles
    INTELLIGENT = "intelligent"
    AUTONOMOUS = "autonomous"
    VISION_ENABLED = "vision_enabled"


@dataclass
class UnifiedConfig:
    """Unified configuration combining all sub-configurations."""

    browser: BrowserConfig
    navigation: NavigationConfig
    extraction: ExtractionConfig
    stealth: StealthConfig
    security: SecurityConfig
    performance: PerformanceConfig
    ai: AIConfig

    # Global settings
    profile: ConfigProfile = ConfigProfile.DEFAULT
    name: Optional[str] = None
    description: Optional[str] = None

    # Paths
    data_dir: Optional[Path] = None
    cache_dir: Optional[Path] = None
    download_dir: Optional[Path] = None
    screenshot_dir: Optional[Path] = None
    log_dir: Optional[Path] = None

    # Feature flags
    features: Dict[str, bool] = field(default_factory=dict)

    # Custom overrides
    overrides: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "profile": self.profile.value,
            "name": self.name,
            "description": self.description,
            "browser": self.browser.__dict__,
            "navigation": self.navigation.__dict__,
            "extraction": self.extraction.__dict__,
            "stealth": self.stealth.__dict__,
            "security": self.security.__dict__,
            "performance": self.performance.__dict__,
            "ai": self.ai.__dict__,
            "features": self.features,
            "overrides": self.overrides,
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> UnifiedConfig:
        """Create configuration from dictionary."""
        return cls(
            profile=ConfigProfile(config_dict.get("profile", "default")),
            name=config_dict.get("name"),
            description=config_dict.get("description"),
            browser=BrowserConfig(**config_dict.get("browser", {})),
            navigation=NavigationConfig(**config_dict.get("navigation", {})),
            extraction=ExtractionConfig(**config_dict.get("extraction", {})),
            stealth=StealthConfig(**config_dict.get("stealth", {})),
            security=SecurityConfig(**config_dict.get("security", {})),
            performance=PerformanceConfig(**config_dict.get("performance", {})),
            ai=AIConfig(**config_dict.get("ai", {})),
            features=config_dict.get("features", {}),
            overrides=config_dict.get("overrides", {}),
        )


class ConfigFactory:
    """Factory for creating browser configurations."""

    _profiles: Dict[ConfigProfile, UnifiedConfig] = {}

    @classmethod
    def create_config(cls, profile: ConfigProfile = ConfigProfile.DEFAULT) -> UnifiedConfig:
        """Create configuration for a specific profile."""
        if profile not in cls._profiles:
            cls._profiles[profile] = cls._build_profile(profile)
        return cls._profiles[profile]

    @classmethod
    def _build_profile(cls, profile: ConfigProfile) -> UnifiedConfig:
        """Build configuration for a specific profile."""
        if profile == ConfigProfile.DEFAULT:
            return cls._default_config()
        elif profile == ConfigProfile.MINIMAL:
            return cls._minimal_config()
        elif profile == ConfigProfile.DEVELOPMENT:
            return cls._development_config()
        elif profile == ConfigProfile.TESTING:
            return cls._testing_config()
        elif profile == ConfigProfile.PRODUCTION:
            return cls._production_config()
        elif profile == ConfigProfile.SCRAPING:
            return cls._scraping_config()
        elif profile == ConfigProfile.AUTOMATION:
            return cls._automation_config()
        elif profile == ConfigProfile.MONITORING:
            return cls._monitoring_config()
        elif profile == ConfigProfile.DEBUGGING:
            return cls._debugging_config()
        elif profile == ConfigProfile.FAST:
            return cls._fast_config()
        elif profile == ConfigProfile.BALANCED:
            return cls._balanced_config()
        elif profile == ConfigProfile.QUALITY:
            return cls._quality_config()
        elif profile == ConfigProfile.SECURE:
            return cls._secure_config()
        elif profile == ConfigProfile.STEALTH:
            return cls._stealth_config()
        elif profile == ConfigProfile.ANONYMOUS:
            return cls._anonymous_config()
        elif profile == ConfigProfile.INTELLIGENT:
            return cls._intelligent_config()
        elif profile == ConfigProfile.AUTONOMOUS:
            return cls._autonomous_config()
        elif profile == ConfigProfile.VISION_ENABLED:
            return cls._vision_enabled_config()
        else:
            return cls._default_config()

    @classmethod
    def _default_config(cls) -> UnifiedConfig:
        """Create default configuration."""
        return UnifiedConfig(
            profile=ConfigProfile.DEFAULT,
            name="Default Configuration",
            description="Balanced configuration for general use",
            browser=BrowserConfig(),
            navigation=NavigationConfig(),
            extraction=ExtractionConfig(),
            stealth=StealthConfig(),
            security=SecurityConfig.medium_security(),
            performance=PerformanceConfig.balanced_mode(),
            ai=AIConfig.basic_config(),
        )

    @classmethod
    def _minimal_config(cls) -> UnifiedConfig:
        """Create minimal configuration."""
        return UnifiedConfig(
            profile=ConfigProfile.MINIMAL,
            name="Minimal Configuration",
            description="Minimal resource usage configuration",
            browser=BrowserConfig(
                headless=True,
                engine=BrowserEngine.PLAYWRIGHT,
            ),
            navigation=NavigationConfig.fast_navigation(),
            extraction=ExtractionConfig.minimal_extraction(),
            stealth=StealthConfig.basic_stealth(),
            security=SecurityConfig.low_security(),
            performance=PerformanceConfig.minimal_mode(),
            ai=AIConfig(
                vision=AIConfig.basic_config().vision,
                agents=AIConfig.basic_config().agents,
            ),
        )

    @classmethod
    def _development_config(cls) -> UnifiedConfig:
        """Create development configuration."""
        return UnifiedConfig(
            profile=ConfigProfile.DEVELOPMENT,
            name="Development Configuration",
            description="Configuration optimized for development",
            browser=BrowserConfig(
                headless=False,
                debug=DebugConfig(
                    devtools=True,
                    debug_mode=True,
                    verbose=True,
                    slow_mo=100,
                ),
            ),
            navigation=NavigationConfig.debug_navigation(),
            extraction=ExtractionConfig(),
            stealth=StealthConfig.basic_stealth(),
            security=SecurityConfig.low_security(),
            performance=PerformanceConfig.balanced_mode(),
            ai=AIConfig.basic_config(),
        )

    @classmethod
    def _testing_config(cls) -> UnifiedConfig:
        """Create testing configuration."""
        return UnifiedConfig(
            profile=ConfigProfile.TESTING,
            name="Testing Configuration",
            description="Configuration for automated testing",
            browser=BrowserConfig(
                headless=True,
                devtools=False,
                incognito=True,
            ),
            navigation=NavigationConfig.reliable_navigation(),
            extraction=ExtractionConfig.full_extraction(),
            stealth=StealthConfig.moderate_stealth(),
            security=SecurityConfig.medium_security(),
            performance=PerformanceConfig.fast_mode(),
            ai=AIConfig.basic_config(),
        )

    @classmethod
    def _production_config(cls) -> UnifiedConfig:
        """Create production configuration."""
        return UnifiedConfig(
            profile=ConfigProfile.PRODUCTION,
            name="Production Configuration",
            description="Secure and reliable production configuration",
            browser=BrowserConfig(
                headless=True,
                incognito=True,
                disable_blink=True,
            ),
            navigation=NavigationConfig.reliable_navigation(),
            extraction=ExtractionConfig(),
            stealth=StealthConfig.enhanced_stealth(),
            security=SecurityConfig.high_security(),
            performance=PerformanceConfig.balanced_mode(),
            ai=AIConfig.advanced_config(),
        )

    @classmethod
    def _scraping_config(cls) -> UnifiedConfig:
        """Create web scraping configuration."""
        return UnifiedConfig(
            profile=ConfigProfile.SCRAPING,
            name="Scraping Configuration",
            description="Optimized for web scraping",
            browser=BrowserConfig(
                headless=True,
                engine=BrowserEngine.PLAYWRIGHT,
                disable_blink=True,
            ),
            navigation=NavigationConfig(
                wait_strategy=NavigationConfig().wait_strategy,
                retry=NavigationConfig().retry,
                throttle_navigations=True,
            ),
            extraction=ExtractionConfig.full_extraction(),
            stealth=StealthConfig.maximum_stealth(),
            security=SecurityConfig.medium_security(),
            performance=PerformanceConfig.fast_mode(),
            ai=AIConfig.basic_config(),
        )

    @classmethod
    def _automation_config(cls) -> UnifiedConfig:
        """Create automation configuration."""
        return UnifiedConfig(
            profile=ConfigProfile.AUTOMATION,
            name="Automation Configuration",
            description="For browser automation tasks",
            browser=BrowserConfig(
                headless=False,
                engine=BrowserEngine.UNDETECTED,
            ),
            navigation=NavigationConfig.reliable_navigation(),
            extraction=ExtractionConfig(),
            stealth=StealthConfig.enhanced_stealth(),
            security=SecurityConfig.medium_security(),
            performance=PerformanceConfig.balanced_mode(),
            ai=AIConfig.advanced_config(),
        )

    @classmethod
    def _monitoring_config(cls) -> UnifiedConfig:
        """Create monitoring configuration."""
        return UnifiedConfig(
            profile=ConfigProfile.MONITORING,
            name="Monitoring Configuration",
            description="For performance and availability monitoring",
            browser=BrowserConfig(
                headless=True,
                disable_gpu=True,
            ),
            navigation=NavigationConfig(
                wait_strategy=NavigationConfig().wait_strategy,
                retry=NavigationConfig().retry,
            ),
            extraction=ExtractionConfig.minimal_extraction(),
            stealth=StealthConfig.basic_stealth(),
            security=SecurityConfig.low_security(),
            performance=PerformanceConfig.monitoring_mode(),
            ai=AIConfig.basic_config(),
        )

    @classmethod
    def _debugging_config(cls) -> UnifiedConfig:
        """Create debugging configuration."""
        return UnifiedConfig(
            profile=ConfigProfile.DEBUGGING,
            name="Debugging Configuration",
            description="Maximum debugging information",
            browser=BrowserConfig(
                headless=False,
                devtools=True,
                verbose=True,
                debug_level=3,
                slow_mo=500,
            ),
            navigation=NavigationConfig.debug_navigation(),
            extraction=ExtractionConfig(
                include_screenshot=True,
                include_source_html=True,
            ),
            stealth=StealthConfig.basic_stealth(),
            security=SecurityConfig.low_security(),
            performance=PerformanceConfig.monitoring_mode(),
            ai=AIConfig.basic_config(),
        )

    @classmethod
    def _fast_config(cls) -> UnifiedConfig:
        """Create fast performance configuration."""
        return UnifiedConfig(
            profile=ConfigProfile.FAST,
            name="Fast Configuration",
            description="Maximum speed, minimal features",
            browser=BrowserConfig(
                headless=True,
                disable_gpu=True,
                disable_blink=True,
            ),
            navigation=NavigationConfig.fast_navigation(),
            extraction=ExtractionConfig.fast_extraction(),
            stealth=StealthConfig.basic_stealth(),
            security=SecurityConfig.low_security(),
            performance=PerformanceConfig.fast_mode(),
            ai=AIConfig.basic_config(),
        )

    @classmethod
    def _balanced_config(cls) -> UnifiedConfig:
        """Create balanced configuration."""
        return UnifiedConfig(
            profile=ConfigProfile.BALANCED,
            name="Balanced Configuration",
            description="Balance between features and performance",
            browser=BrowserConfig(),
            navigation=NavigationConfig(),
            extraction=ExtractionConfig(),
            stealth=StealthConfig.moderate_stealth(),
            security=SecurityConfig.medium_security(),
            performance=PerformanceConfig.balanced_mode(),
            ai=AIConfig.basic_config(),
        )

    @classmethod
    def _quality_config(cls) -> UnifiedConfig:
        """Create quality configuration."""
        return UnifiedConfig(
            profile=ConfigProfile.QUALITY,
            name="Quality Configuration",
            description="Best quality, full features",
            browser=BrowserConfig(
                headless=False,
                disable_gpu=False,
                disable_blink=False,
            ),
            navigation=NavigationConfig.reliable_navigation(),
            extraction=ExtractionConfig.full_extraction(),
            stealth=StealthConfig.moderate_stealth(),
            security=SecurityConfig.high_security(),
            performance=PerformanceConfig.quality_mode(),
            ai=AIConfig.advanced_config(),
        )

    @classmethod
    def _secure_config(cls) -> UnifiedConfig:
        """Create secure configuration."""
        return UnifiedConfig(
            profile=ConfigProfile.SECURE,
            name="Secure Configuration",
            description="Maximum security settings",
            browser=BrowserConfig(
                incognito=True,
                disable_webrtc=True,
            ),
            navigation=NavigationConfig(),
            extraction=ExtractionConfig(),
            stealth=StealthConfig.enhanced_stealth(),
            security=SecurityConfig.maximum_security(),
            performance=PerformanceConfig.balanced_mode(),
            ai=AIConfig.basic_config(),
        )

    @classmethod
    def _stealth_config(cls) -> UnifiedConfig:
        """Create stealth configuration."""
        return UnifiedConfig(
            profile=ConfigProfile.STEALTH,
            name="Stealth Configuration",
            description="Maximum anti-detection",
            browser=BrowserConfig(
                headless=False,
            ),
            navigation=NavigationConfig.stealth_navigation(),
            extraction=ExtractionConfig(),
            stealth=StealthConfig.maximum_stealth(),
            security=SecurityConfig.high_security(),
            performance=PerformanceConfig.balanced_mode(),
            ai=AIConfig.basic_config(),
        )

    @classmethod
    def _anonymous_config(cls) -> UnifiedConfig:
        """Create anonymous configuration."""
        return UnifiedConfig(
            profile=ConfigProfile.ANONYMOUS,
            name="Anonymous Configuration",
            description="Anonymous browsing with proxy",
            browser=BrowserConfig(
                incognito=True,
                disable_webrtc=True,
                proxy="socks5://localhost:9050",  # Tor proxy
            ),
            navigation=NavigationConfig.stealth_navigation(),
            extraction=ExtractionConfig(),
            stealth=StealthConfig.paranoid_stealth(),
            security=SecurityConfig.maximum_security(),
            performance=PerformanceConfig.balanced_mode(),
            ai=AIConfig.basic_config(),
        )

    @classmethod
    def _intelligent_config(cls) -> UnifiedConfig:
        """Create AI-enhanced configuration."""
        return UnifiedConfig(
            profile=ConfigProfile.INTELLIGENT,
            name="Intelligent Configuration",
            description="AI-powered browser automation",
            browser=BrowserConfig(),
            navigation=NavigationConfig(),
            extraction=ExtractionConfig.ai_extraction(),
            stealth=StealthConfig.moderate_stealth(),
            security=SecurityConfig.medium_security(),
            performance=PerformanceConfig.balanced_mode(),
            ai=AIConfig.advanced_config(),
        )

    @classmethod
    def _autonomous_config(cls) -> UnifiedConfig:
        """Create autonomous configuration."""
        return UnifiedConfig(
            profile=ConfigProfile.AUTONOMOUS,
            name="Autonomous Configuration",
            description="Fully autonomous browser control",
            browser=BrowserConfig(
                headless=True,
            ),
            navigation=NavigationConfig.reliable_navigation(),
            extraction=ExtractionConfig.ai_extraction(),
            stealth=StealthConfig.enhanced_stealth(),
            security=SecurityConfig.high_security(),
            performance=PerformanceConfig.balanced_mode(),
            ai=AIConfig.autonomous_config(),
        )

    @classmethod
    def _vision_enabled_config(cls) -> UnifiedConfig:
        """Create vision-enabled configuration."""
        return UnifiedConfig(
            profile=ConfigProfile.VISION_ENABLED,
            name="Vision-Enabled Configuration",
            description="Computer vision and OCR enabled",
            browser=BrowserConfig(),
            navigation=NavigationConfig(),
            extraction=ExtractionConfig(
                include_screenshot=True,
            ),
            stealth=StealthConfig.moderate_stealth(),
            security=SecurityConfig.medium_security(),
            performance=PerformanceConfig.quality_mode(),
            ai=AIConfig(
                primary_provider=LLMProvider.GEMINI,
                primary_model="gemini-2.5-flash",
                vision=AIConfig.advanced_config().vision,
                agents=AIConfig.advanced_config().agents,
            ),
        )

    @classmethod
    def custom_config(
        cls, base_profile: ConfigProfile = ConfigProfile.DEFAULT, **overrides: Any
    ) -> UnifiedConfig:
        """Create custom configuration with overrides."""
        config = cls.create_config(base_profile)

        # Apply overrides
        for key, value in overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                config.overrides[key] = value

        return config
