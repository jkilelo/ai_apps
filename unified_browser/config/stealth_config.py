"""
Stealth configuration module.

This module defines stealth-related configuration for anti-detection and
fingerprinting evasion.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..core import (
    AUDIO_CONTEXT_SPOOFING,
    CANVAS_NOISE_LEVEL,
    CDP_COORDINATE_LEAK_PREVENTION,
    FINGERPRINT_ROTATION_INTERVAL,
    FONT_FINGERPRINT_PROTECTION,
    NODRIVER_MODE,
    NODRIVER_PATCH_LEVEL,
    RUNTIME_ENABLE_BYPASS,
    StealthLevel,
    WEBDRIVER_EXECUTE_CDP_OVERRIDE,
    WEBGL_VENDOR_SPOOFING,
)


@dataclass
class FingerprintConfig:
    """Browser fingerprint configuration."""

    # Canvas fingerprinting
    canvas_noise: bool = True
    canvas_noise_level: float = CANVAS_NOISE_LEVEL

    # WebGL fingerprinting
    webgl_vendor: Optional[str] = "Intel Inc."
    webgl_renderer: Optional[str] = "Intel Iris OpenGL Engine"
    webgl_vendor_spoofing: bool = WEBGL_VENDOR_SPOOFING

    # Audio fingerprinting
    audio_context_spoofing: bool = AUDIO_CONTEXT_SPOOFING
    audio_noise_level: float = 0.0001

    # Font fingerprinting
    font_protection: bool = FONT_FINGERPRINT_PROTECTION
    font_list: Optional[List[str]] = None

    # Screen resolution
    screen_resolution: Optional[tuple[int, int]] = None
    available_screen_resolution: Optional[tuple[int, int]] = None

    # Hardware
    hardware_concurrency: Optional[int] = None
    device_memory: Optional[int] = None

    # Battery API
    battery_spoofing: bool = True
    charging: bool = True
    charging_time: float = 0.0
    discharging_time: float = float("inf")
    level: float = 1.0

    # Timezone
    timezone_spoofing: bool = False
    timezone_offset: Optional[int] = None

    # Language
    languages: List[str] = field(default_factory=lambda: ["en-US", "en"])

    # Platform
    platform: str = "Win32"
    platform_version: Optional[str] = None

    # Rotation interval (ms)
    rotation_interval: int = FINGERPRINT_ROTATION_INTERVAL
    auto_rotate: bool = False


@dataclass
class NavigatorOverrides:
    """Navigator object overrides."""

    webdriver: bool = False  # Remove webdriver flag
    vendor: str = "Google Inc."
    vendor_sub: str = ""
    product_sub: str = "20030107"
    max_touch_points: int = 0
    hardware_concurrency: Optional[int] = None
    device_memory: Optional[int] = None
    languages: Optional[List[str]] = None
    language: Optional[str] = None
    platform: Optional[str] = None
    user_agent: Optional[str] = None
    app_version: Optional[str] = None
    connection: Optional[Dict[str, Any]] = None
    plugins: List[Dict[str, str]] = field(default_factory=list)
    mime_types: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class ChromeOverrides:
    """Chrome-specific overrides."""

    runtime_enable_bypass: bool = RUNTIME_ENABLE_BYPASS
    cdp_coordinate_leak_prevention: bool = CDP_COORDINATE_LEAK_PREVENTION
    webdriver_execute_cdp_override: bool = WEBDRIVER_EXECUTE_CDP_OVERRIDE

    # Chrome.runtime properties
    runtime: Dict[str, Any] = field(
        default_factory=lambda: {
            "OnInstalledReason": "install",
            "OnRestartRequiredReason": "update",
            "PlatformArch": "x86-64",
            "PlatformNaclArch": "x86-64",
            "PlatformOs": "win",
        }
    )

    # Chrome.app properties
    app: Dict[str, Any] = field(
        default_factory=lambda: {
            "isInstalled": False,
            "InstallState": {
                "DISABLED": "disabled",
                "INSTALLED": "installed",
                "NOT_INSTALLED": "not_installed",
            },
            "RunningState": {
                "CANNOT_RUN": "cannot_run",
                "READY_TO_RUN": "ready_to_run",
                "RUNNING": "running",
            },
        }
    )

    # Chrome.csi properties
    csi: Dict[str, Any] = field(default_factory=dict)

    # Chrome.loadTimes properties
    load_times: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WebGLOverrides:
    """WebGL-specific overrides."""

    vendor: str = "Intel Inc."
    renderer: str = "Intel Iris OpenGL Engine"
    unmasked_vendor: str = "Intel Inc."
    unmasked_renderer: str = "Intel Iris OpenGL Engine"
    shading_language_version: str = "WebGL GLSL ES 1.0"
    version: str = "WebGL 1.0"

    # WebGL extensions to report
    extensions: List[str] = field(
        default_factory=lambda: [
            "ANGLE_instanced_arrays",
            "EXT_blend_minmax",
            "EXT_color_buffer_half_float",
            "EXT_disjoint_timer_query",
            "EXT_float_blend",
            "EXT_frag_depth",
            "EXT_shader_texture_lod",
            "EXT_texture_compression_bptc",
            "EXT_texture_compression_rgtc",
            "EXT_texture_filter_anisotropic",
            "WEBKIT_EXT_texture_filter_anisotropic",
            "EXT_sRGB",
            "KHR_parallel_shader_compile",
            "OES_element_index_uint",
            "OES_fbo_render_mipmap",
            "OES_standard_derivatives",
            "OES_texture_float",
            "OES_texture_float_linear",
            "OES_texture_half_float",
            "OES_texture_half_float_linear",
            "OES_vertex_array_object",
            "WEBGL_color_buffer_float",
            "WEBGL_compressed_texture_s3tc",
            "WEBKIT_WEBGL_compressed_texture_s3tc",
            "WEBGL_compressed_texture_s3tc_srgb",
            "WEBGL_debug_renderer_info",
            "WEBGL_debug_shaders",
            "WEBGL_depth_texture",
            "WEBKIT_WEBGL_depth_texture",
            "WEBGL_draw_buffers",
            "WEBGL_lose_context",
            "WEBKIT_WEBGL_lose_context",
            "WEBGL_multi_draw",
        ]
    )


@dataclass
class MediaDevicesOverrides:
    """Media devices overrides."""

    # Enumerate devices response
    video_inputs: List[Dict[str, str]] = field(default_factory=list)
    audio_inputs: List[Dict[str, str]] = field(default_factory=list)
    audio_outputs: List[Dict[str, str]] = field(default_factory=list)

    # Permissions
    camera_permission: str = "denied"
    microphone_permission: str = "denied"

    # WebRTC
    disable_webrtc: bool = False
    webrtc_ip_handling_policy: str = "disable_non_proxied_udp"

    # Media codecs
    supported_codecs: List[str] = field(
        default_factory=lambda: [
            'video/webm; codecs="vp8"',
            'video/webm; codecs="vp9"',
            'video/mp4; codecs="avc1.42E01E"',
            'audio/webm; codecs="opus"',
            'audio/webm; codecs="vorbis"',
            "audio/mpeg",
        ]
    )


@dataclass
class StealthConfig:
    """Main stealth configuration."""

    # Stealth level
    level: StealthLevel = StealthLevel.ENHANCED

    # Nodriver mode
    nodriver_mode: bool = NODRIVER_MODE
    nodriver_patch_level: int = NODRIVER_PATCH_LEVEL

    # Core evasions
    hide_webdriver: bool = True
    hide_automation_controlled: bool = True
    disable_blink_features: bool = True

    # Advanced evasions
    mock_permissions: bool = True
    mock_plugins: bool = True
    mock_languages: bool = True
    mock_webgl: bool = True
    mock_battery: bool = True
    mock_connection: bool = True

    # CDP detection bypass
    bypass_cdp_detection: bool = True
    patch_cdp_leak: bool = True

    # Iframe/frame evasion
    iframe_content_window: bool = True
    frame_content_window: bool = True

    # Console detection
    disable_console_debug: bool = True
    mock_console: bool = False

    # Error stack trace
    clean_error_stack: bool = True

    # Mouse movement
    human_mouse: bool = True
    human_typing: bool = True
    human_scrolling: bool = True

    # Sub-configurations
    fingerprint: FingerprintConfig = field(default_factory=FingerprintConfig)
    navigator: NavigatorOverrides = field(default_factory=NavigatorOverrides)
    chrome: ChromeOverrides = field(default_factory=ChromeOverrides)
    webgl: WebGLOverrides = field(default_factory=WebGLOverrides)
    media_devices: MediaDevicesOverrides = field(default_factory=MediaDevicesOverrides)

    # Custom evasion scripts
    custom_scripts: List[str] = field(default_factory=list)

    @classmethod
    def basic_stealth(cls) -> StealthConfig:
        """Create basic stealth configuration."""
        return cls(
            level=StealthLevel.BASIC,
            hide_webdriver=True,
            hide_automation_controlled=True,
            disable_blink_features=True,
            mock_permissions=False,
            mock_plugins=False,
            mock_webgl=False,
            human_mouse=False,
            human_typing=False,
        )

    @classmethod
    def enhanced_stealth(cls) -> StealthConfig:
        """Create enhanced stealth configuration."""
        return cls(
            level=StealthLevel.ENHANCED,
            hide_webdriver=True,
            hide_automation_controlled=True,
            disable_blink_features=True,
            mock_permissions=True,
            mock_plugins=True,
            mock_webgl=True,
            bypass_cdp_detection=True,
            human_mouse=True,
            human_typing=True,
        )

    @classmethod
    def maximum_stealth(cls) -> StealthConfig:
        """Create maximum stealth configuration."""
        return cls(
            level=StealthLevel.MAXIMUM,
            nodriver_mode=True,
            nodriver_patch_level=2,
            hide_webdriver=True,
            hide_automation_controlled=True,
            disable_blink_features=True,
            mock_permissions=True,
            mock_plugins=True,
            mock_languages=True,
            mock_webgl=True,
            mock_battery=True,
            mock_connection=True,
            bypass_cdp_detection=True,
            patch_cdp_leak=True,
            iframe_content_window=True,
            frame_content_window=True,
            disable_console_debug=True,
            clean_error_stack=True,
            human_mouse=True,
            human_typing=True,
            human_scrolling=True,
            fingerprint=FingerprintConfig(
                auto_rotate=True,
                canvas_noise=True,
                webgl_vendor_spoofing=True,
                audio_context_spoofing=True,
                font_protection=True,
                battery_spoofing=True,
            ),
        )

    def should_apply_evasion(self, evasion_name: str) -> bool:
        """Check if specific evasion should be applied based on level."""
        basic_evasions = {
            "hide_webdriver",
            "hide_automation_controlled",
            "disable_blink_features",
        }

        enhanced_evasions = basic_evasions | {
            "mock_permissions",
            "mock_plugins",
            "mock_webgl",
            "bypass_cdp_detection",
            "human_mouse",
            "human_typing",
        }

        if self.level == StealthLevel.BASIC:
            return evasion_name in basic_evasions
        elif self.level == StealthLevel.ENHANCED:
            return evasion_name in enhanced_evasions
        else:  # MAXIMUM
            return True  # Apply all evasions
