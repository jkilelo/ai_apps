"""
Browser configuration module.

This module defines the main browser configuration dataclass with all settings
needed to initialize and control browser behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..core import (
    DEFAULT_DOWNLOAD_TIMEOUT,
    DEFAULT_LOCALE,
    DEFAULT_SLOW_MO,
    DEFAULT_TIMEOUT,
    DEFAULT_TIMEZONE,
    DEFAULT_USER_AGENTS,
    DEFAULT_VIEWPORT_HEIGHT,
    DEFAULT_VIEWPORT_WIDTH,
    INCOGNITO_MODE_DEFAULT,
    NODRIVER_MODE,
    PROFILE_PERSISTENCE,
    RESOURCE_BLOCKING_ENABLED,
    STEALTH_BROWSER_ARGS,
    BLOCKED_RESOURCE_TYPES,
)


@dataclass
class ViewportConfig:
    """Viewport configuration."""

    width: int = DEFAULT_VIEWPORT_WIDTH
    height: int = DEFAULT_VIEWPORT_HEIGHT
    device_scale_factor: float = 1.0
    is_mobile: bool = False
    has_touch: bool = False
    is_landscape: bool = True


@dataclass
class ProxyConfig:
    """Proxy configuration."""

    server: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    bypass: List[str] = field(default_factory=list)


@dataclass
class GeolocationConfig:
    """Geolocation configuration."""

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[float] = None


@dataclass
class ResourceBlockingConfig:
    """Resource blocking configuration."""

    enabled: bool = RESOURCE_BLOCKING_ENABLED
    blocked_types: List[str] = field(default_factory=lambda: BLOCKED_RESOURCE_TYPES.copy())
    blocked_domains: List[str] = field(default_factory=list)
    allowed_domains: List[str] = field(default_factory=list)


@dataclass
class ProfileConfig:
    """Browser profile configuration."""

    persist: bool = PROFILE_PERSISTENCE
    profile_dir: Optional[Path] = None
    rotate_profiles: bool = False
    profile_count: int = 5
    clear_on_start: bool = False
    preserve_cookies: bool = True
    preserve_local_storage: bool = True
    preserve_session_storage: bool = False


@dataclass
class DownloadConfig:
    """Download configuration."""

    download_dir: Optional[Path] = None
    accept_downloads: bool = True
    timeout: int = DEFAULT_DOWNLOAD_TIMEOUT
    save_as: Optional[str] = None


@dataclass
class NetworkConfig:
    """Network configuration."""

    timeout: int = DEFAULT_TIMEOUT
    extra_headers: Dict[str, str] = field(default_factory=dict)
    user_agent: Optional[str] = None
    accept_language: str = "en-US,en;q=0.9"
    bypass_csp: bool = False
    ignore_https_errors: bool = False
    offline: bool = False
    http_credentials: Optional[Dict[str, str]] = None
    max_redirects: int = 10


@dataclass
class PermissionsConfig:
    """Browser permissions configuration."""

    geolocation: str = "prompt"  # "grant", "deny", "prompt"
    notifications: str = "deny"
    camera: str = "deny"
    microphone: str = "deny"
    clipboard_read: str = "deny"
    clipboard_write: str = "grant"
    payment_handler: str = "deny"


@dataclass
class EmulationConfig:
    """Device emulation configuration."""

    device: Optional[str] = None  # e.g., "iPhone 12", "Pixel 5"
    locale: str = DEFAULT_LOCALE
    timezone: str = DEFAULT_TIMEZONE
    color_scheme: str = "light"  # "light", "dark", "no-preference"
    reduced_motion: str = "no-preference"  # "reduce", "no-preference"
    forced_colors: str = "none"  # "active", "none"


@dataclass
class DebugConfig:
    """Debug configuration."""

    devtools: bool = False
    slow_mo: int = DEFAULT_SLOW_MO
    debug_mode: bool = False
    verbose: bool = False
    log_level: str = "INFO"
    log_file: Optional[Path] = None
    screenshot_on_error: bool = True
    trace_dir: Optional[Path] = None
    record_video: bool = False
    record_har: bool = False


@dataclass
class CacheConfig:
    """Cache configuration."""

    enabled: bool = True
    cache_dir: Optional[Path] = None
    max_size_mb: int = 100
    ttl_seconds: int = 3600
    clear_on_start: bool = False


@dataclass
class BrowserConfig:
    """Main browser configuration."""

    # Core settings
    headless: bool = True
    incognito: bool = INCOGNITO_MODE_DEFAULT
    sandbox: bool = True
    executable_path: Optional[Path] = None
    browser_type: str = "chromium"  # "chromium", "firefox", "webkit"

    # Advanced mode
    nodriver_mode: bool = NODRIVER_MODE
    use_subprocess: bool = False

    # Launch arguments
    args: List[str] = field(default_factory=lambda: STEALTH_BROWSER_ARGS.copy())
    env: Dict[str, str] = field(default_factory=dict)

    # Sub-configurations
    viewport: ViewportConfig = field(default_factory=ViewportConfig)
    proxy: ProxyConfig = field(default_factory=ProxyConfig)
    geolocation: GeolocationConfig = field(default_factory=GeolocationConfig)
    resource_blocking: ResourceBlockingConfig = field(default_factory=ResourceBlockingConfig)
    profile: ProfileConfig = field(default_factory=ProfileConfig)
    download: DownloadConfig = field(default_factory=DownloadConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    permissions: PermissionsConfig = field(default_factory=PermissionsConfig)
    emulation: EmulationConfig = field(default_factory=EmulationConfig)
    debug: DebugConfig = field(default_factory=DebugConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)

    # Context options
    context_options: Dict[str, Any] = field(default_factory=dict)

    def to_playwright_options(self) -> Dict[str, Any]:
        """Convert to Playwright launch options."""
        options = {
            "headless": self.headless,
            "args": self.args.copy(),
            "slow_mo": self.debug.slow_mo,
        }

        if self.executable_path:
            options["executable_path"] = str(self.executable_path)

        if self.proxy.server:
            options["proxy"] = {
                "server": self.proxy.server,
                "username": self.proxy.username,
                "password": self.proxy.password,
                "bypass": ",".join(self.proxy.bypass),
            }

        if self.debug.devtools:
            options["devtools"] = True

        if self.env:
            options["env"] = self.env

        return options

    def to_context_options(self) -> Dict[str, Any]:
        """Convert to Playwright context options."""
        options = self.context_options.copy()

        # Viewport
        options["viewport"] = {
            "width": self.viewport.width,
            "height": self.viewport.height,
        }

        # Device scale
        options["device_scale_factor"] = self.viewport.device_scale_factor

        # Mobile emulation
        options["is_mobile"] = self.viewport.is_mobile
        options["has_touch"] = self.viewport.has_touch

        # Network
        if self.network.user_agent:
            options["user_agent"] = self.network.user_agent
        elif DEFAULT_USER_AGENTS:
            import random

            options["user_agent"] = random.choice(DEFAULT_USER_AGENTS)

        options["extra_http_headers"] = self.network.extra_headers
        options["bypass_csp"] = self.network.bypass_csp
        options["ignore_https_errors"] = self.network.ignore_https_errors
        options["offline"] = self.network.offline

        if self.network.http_credentials:
            options["http_credentials"] = self.network.http_credentials

        # Locale and timezone
        options["locale"] = self.emulation.locale
        options["timezone_id"] = self.emulation.timezone

        # Color scheme
        options["color_scheme"] = self.emulation.color_scheme
        options["reduced_motion"] = self.emulation.reduced_motion
        options["forced_colors"] = self.emulation.forced_colors

        # Permissions
        permissions = []
        if self.permissions.geolocation == "grant":
            permissions.append("geolocation")
        if self.permissions.notifications == "grant":
            permissions.append("notifications")
        if self.permissions.camera == "grant":
            permissions.append("camera")
        if self.permissions.microphone == "grant":
            permissions.append("microphone")
        if self.permissions.clipboard_read == "grant":
            permissions.append("clipboard-read")
        if self.permissions.clipboard_write == "grant":
            permissions.append("clipboard-write")

        if permissions:
            options["permissions"] = permissions

        # Geolocation
        if self.geolocation.latitude is not None:
            options["geolocation"] = {
                "latitude": self.geolocation.latitude,
                "longitude": self.geolocation.longitude,
                "accuracy": self.geolocation.accuracy or 100,
            }

        # Downloads
        if self.download.accept_downloads:
            options["accept_downloads"] = True
            if self.download.download_dir:
                options["downloads_path"] = str(self.download.download_dir)

        # Recording
        if self.debug.record_video:
            options["record_video_dir"] = str(self.debug.trace_dir or Path("./videos"))

        if self.debug.record_har:
            options["record_har_path"] = str(self.debug.trace_dir or Path("./har"))

        return options

    @classmethod
    def default_config(cls) -> BrowserConfig:
        """Create default browser configuration."""
        return cls()

    @classmethod
    def headless_config(cls) -> BrowserConfig:
        """Create headless browser configuration."""
        return cls(headless=True, debug=DebugConfig(devtools=False))

    @classmethod
    def debug_config(cls) -> BrowserConfig:
        """Create debug browser configuration."""
        return cls(
            headless=False,
            debug=DebugConfig(
                devtools=True,
                slow_mo=100,
                debug_mode=True,
                verbose=True,
                screenshot_on_error=True,
            ),
        )

    @classmethod
    def stealth_config(cls) -> BrowserConfig:
        """Create stealth browser configuration."""
        from random import choice

        return cls(
            headless=False,
            incognito=True,
            network=NetworkConfig(
                user_agent=choice(DEFAULT_USER_AGENTS),
                accept_language="en-US,en;q=0.9",
            ),
            viewport=ViewportConfig(
                width=1920,
                height=1080,
            ),
            profile=ProfileConfig(
                persist=True,
                rotate_profiles=True,
            ),
        )

    @classmethod
    def mobile_config(cls, device: str = "iPhone 12") -> BrowserConfig:
        """Create mobile browser configuration."""
        return cls(
            headless=False,
            viewport=ViewportConfig(
                width=390,
                height=844,
                device_scale_factor=3,
                is_mobile=True,
                has_touch=True,
            ),
            emulation=EmulationConfig(
                device=device,
            ),
        )
