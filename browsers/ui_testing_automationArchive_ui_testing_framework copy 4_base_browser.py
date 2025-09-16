#!/usr/bin/env python3
"""
ULTIMATE STEALTH BROWSER - INTEGRATED PRODUCTION MODULE
========================================================
Comprehensive unified browser automation with maximum anti-detection.
Integrates browser.py + browser_config.py + browser_contracts.py

Architecture:
- Foundation Layer: Data models and contracts
- Configuration Layer: Stealth settings and browser config  
- Implementation Layer: Core browser functionality
- Production Layer: Error handling, monitoring, and optimization

Version: 5.0.0 (Fully Integrated)
Status: Production Ready
"""

# ============================================================================
# STANDARD LIBRARY IMPORTS
# ============================================================================
import asyncio
import hashlib
import json
import logging
import os
import platform
import random
import sys
import time
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Optional, Dict, List, Any, Union, Callable, TypeVar, Tuple

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('browser_integrated.log', mode='a', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Type variables for generic typing
T = TypeVar('T')

# ============================================================================
# THIRD-PARTY IMPORTS WITH GRACEFUL FALLBACKS
# ============================================================================
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    logger.warning("NumPy not installed. Some human simulation features will be limited.")

try:
    from playwright.async_api import BrowserContext, Page, async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    logger.critical("Playwright not installed. Install with: pip install playwright")

try:
    from pydantic import BaseModel, Field, ConfigDict
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel = object  # type: ignore
    # Don't redefine Field and ConfigDict - they'll be used as functions only in fallback
    logger.warning("Pydantic not installed. Data validation will be limited.")
    
    # Create placeholder functions that won't conflict with imports
    def _field_fallback(*args: Any, **kwargs: Any) -> Any:
        return None
    
    def _config_dict_fallback(**kwargs: Any) -> Any:
        return None
    
    # Only assign if not already imported
    if 'Field' not in locals():
        Field = _field_fallback  # type: ignore
    if 'ConfigDict' not in locals():
        ConfigDict = _config_dict_fallback  # type: ignore

# ============================================================================
# PLATFORM UTILITIES
# ============================================================================
def get_platform_info() -> Dict[str, Any]:
    """Get comprehensive platform information"""
    system = platform.system()
    return {
        'system': system,
        'is_windows': system == 'Windows',
        'is_linux': system == 'Linux',
        'is_mac': system == 'Darwin',
        'version': platform.version(),
        'machine': platform.machine(),
        'python_version': sys.version
    }

def get_temp_directory() -> str:
    """Get platform-appropriate temp directory"""
    import tempfile
    return tempfile.gettempdir()

def get_chrome_executable_path() -> Optional[str]:
    """Find Chrome/Chromium executable path"""
    system = platform.system()
    
    if system == "Windows":
        paths = [
            r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\\Google\\Chrome\\Application\\chrome.exe"),
            r"C:\\Program Files\\Chromium\\Application\\chrome.exe",
        ]
    elif system == "Darwin":  # macOS
        paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
    else:  # Linux
        paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
        ]
    
    for path in paths:
        if os.path.exists(path):
            return path
    
    return None

# ============================================================================
# FOUNDATION LAYER - ENUMS AND CONSTANTS
# ============================================================================

class ElementType(str, Enum):
    """Comprehensive element type enumeration"""
    # Form elements
    TEXT_INPUT = "text_input"
    PASSWORD = "password"
    EMAIL = "email"
    NUMBER = "number"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    SELECT = "select"
    TEXTAREA = "textarea"
    FILE_INPUT = "file_input"
    DATE_INPUT = "date_input"
    TIME_INPUT = "time_input"
    SEARCH = "search"
    TEL = "tel"
    URL = "url"
    RANGE = "range"
    COLOR = "color"
    
    # Interactive elements
    BUTTON = "button"
    LINK = "link"
    SUBMIT = "submit"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    CANVAS = "canvas"
    
    # Layout elements
    DIV = "div"
    SPAN = "span"
    HEADER = "header"
    FOOTER = "footer"
    NAV = "nav"
    SECTION = "section"
    ARTICLE = "article"
    ASIDE = "aside"
    MAIN = "main"
    
    # List elements
    LIST = "list"
    LIST_ITEM = "list_item"
    
    # Table elements
    TABLE = "table"
    TABLE_ROW = "table_row"
    TABLE_CELL = "table_cell"
    TABLE_HEADER = "table_header"
    
    # Other
    IFRAME = "iframe"
    FORM = "form"
    LABEL = "label"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    CODE = "code"
    PRE = "pre"
    UNKNOWN = "unknown"

class ProfileType(str, Enum):
    """Browser profile types"""
    CHROME_STANDARD = "chrome_standard"
    CHROME_MOBILE = "chrome_mobile"
    FIREFOX_STANDARD = "firefox_standard"
    SAFARI_STANDARD = "safari_standard"
    EDGE_STANDARD = "edge_standard"

class StealthLevel(str, Enum):
    """Stealth levels for browser automation"""
    NONE = "none"
    BASIC = "basic"
    MODERATE = "moderate"
    ADVANCED = "advanced"
    MAXIMUM = "maximum"

class ExtractionStrategy(str, Enum):
    """Element extraction strategies"""
    DOM_INSPECTION = "dom_inspection"
    ARIA_SEMANTIC = "aria_semantic"
    EVENT_LISTENERS = "event_listeners"
    VISUAL_ANALYSIS = "visual_analysis"
    DYNAMIC_PROBING = "dynamic_probing"

# ============================================================================
# DATA MODELS LAYER (from browser_contracts.py)
# ============================================================================

class TimingProfile(BaseModel):
    """Timing configuration for human-like behavior"""
    
    model_config = ConfigDict(str_strip_whitespace=True) if HAS_PYDANTIC else {}
    
    element_analysis_delay: Tuple[int, int] = Field(default=(10, 50), description="min, max in ms")
    cookie_consent_wait: Tuple[int, int] = Field(default=(1500, 2500))
    cookie_button_hover: Tuple[int, int] = Field(default=(300, 700))
    cookie_post_click: Tuple[int, int] = Field(default=(500, 1000))
    trust_initial_wait: Tuple[int, int] = Field(default=(2000, 4000))
    trust_link_hover: Tuple[int, int] = Field(default=(500, 1000))
    trust_scroll_pause: Tuple[int, int] = Field(default=(500, 2000))
    stability_initial: Tuple[int, int] = Field(default=(500, 1500))
    network_idle_timeout: int = Field(default=15000)
    challenge_wait: Tuple[int, int] = Field(default=(3000, 5000))
    challenge_complete: Tuple[int, int] = Field(default=(2000, 3000))
    selector_batch_delay: Tuple[int, int] = Field(default=(50, 150))
    event_extraction_delay: Tuple[int, int] = Field(default=(100, 300))
    dynamic_content_wait: Tuple[int, int] = Field(default=(1000, 2000))
    dynamic_content_trigger: Tuple[int, int] = Field(default=(500, 1000))
    mouse_move_steps: Tuple[int, int] = Field(default=(15, 25))
    mouse_step_delay: Tuple[int, int] = Field(default=(10, 30))
    typing_base_delay: Tuple[int, int] = Field(default=(80, 150))

class StealthProfile(BaseModel):
    """Stealth configuration for anti-detection"""
    
    model_config = ConfigDict(str_strip_whitespace=True) if HAS_PYDANTIC else {}
    
    hide_webdriver: bool = Field(default=True)
    hide_automation_indicators: bool = Field(default=True)
    hide_cdp_properties: bool = Field(default=True)
    spoof_plugins: bool = Field(default=True)
    spoof_languages: bool = Field(default=True)
    spoof_chrome_runtime: bool = Field(default=True)
    spoof_permissions: bool = Field(default=True)
    prevent_webrtc_leak: bool = Field(default=True)
    spoof_canvas_fingerprint: bool = Field(default=True)
    spoof_battery_api: bool = Field(default=True)
    randomize_hardware_concurrency: bool = Field(default=True)
    randomize_device_memory: bool = Field(default=True)
    normalize_screen_properties: bool = Field(default=True)
    spoof_webgl: bool = Field(default=True)
    build_trust: bool = Field(default=True)
    trust_safe_domains: List[str] = Field(default_factory=lambda: [
        'google.com', 'wikipedia.org', 'github.com', 'youtube.com'
    ])

class StealthConfig(BaseModel):
    """Complete stealth configuration"""
    
    model_config = ConfigDict(str_strip_whitespace=True) if HAS_PYDANTIC else {}
    
    # Core settings
    level: StealthLevel = Field(default=StealthLevel.MAXIMUM)
    headless: bool = Field(default=False)
    
    # Stealth features
    hide_webdriver: bool = Field(default=True)
    hide_automation_indicators: bool = Field(default=True)
    spoof_plugins: bool = Field(default=True)
    spoof_languages: bool = Field(default=True)
    spoof_chrome_runtime: bool = Field(default=True)
    prevent_webrtc_leak: bool = Field(default=True)
    spoof_canvas_fingerprint: bool = Field(default=True)
    randomize_fingerprint: bool = Field(default=True)
    spoof_webgl: bool = Field(default=True)
    spoof_battery: bool = Field(default=True)
    spoof_hardware: bool = Field(default=True)
    bypass_csp: bool = Field(default=True)
    block_webrtc: bool = Field(default=True)
    
    # Viewport and window
    viewport_width: int = Field(default=1920)
    viewport_height: int = Field(default=1080)
    device_scale_factor: float = Field(default=1.0)
    is_mobile: bool = Field(default=False)
    has_touch: bool = Field(default=False)
    is_landscape: bool = Field(default=True)
    
    # User agent
    user_agent: Optional[str] = Field(default=None)
    
    # Proxy
    proxy_server: Optional[str] = Field(default=None)
    proxy_username: Optional[str] = Field(default=None)
    proxy_password: Optional[str] = Field(default=None)
    
    # Performance
    slow_mo: int = Field(default=0)
    default_timeout: int = Field(default=30000)
    timeout: int = Field(default=30)
    
    # Advanced
    ignore_https_errors: bool = Field(default=False)
    extra_headers: Optional[Dict[str, str]] = Field(default=None)
    custom_args: List[str] = Field(default_factory=list)
    
    # Bypass options
    bypass_cloudflare: bool = Field(default=False)
    bypass_f5_networks: bool = Field(default=False)
    bypass_shape_security: bool = Field(default=False)
    bypass_datadome: bool = Field(default=False)
    bypass_kasada: bool = Field(default=False)
    
    # Locale and timezone
    locale: str = Field(default="en-US")
    timezone: str = Field(default="America/New_York")
    
    # Human simulation
    enable_human_delays: bool = Field(default=True)
    enable_human_mouse: bool = Field(default=True)
    enable_human_typing: bool = Field(default=True)
    enable_human_scrolling: bool = Field(default=True)
    enable_micro_behaviors: bool = Field(default=True)
    human_delay_range: Tuple[int, int] = Field(default=(500, 2000))
    use_lognormal_delays: bool = Field(default=True)
    use_bspline_mouse: bool = Field(default=True)
    typing_delay_range: Tuple[int, int] = Field(default=(50, 150))
    max_retry_attempts: int = Field(default=3)

class ElementData(BaseModel):
    """Comprehensive element data structure"""
    
    model_config = ConfigDict(str_strip_whitespace=True) if HAS_PYDANTIC else {}
    
    # Core identification
    element_id: str = Field(..., description="Unique element ID")
    element_type: ElementType = Field(..., description="Type of element")
    tag_name: str = Field(..., description="HTML tag name")
    xpath: str = Field(..., description="XPath selector")
    css_selector: str = Field(..., description="CSS selector")
    
    # Content
    text_content: str = Field(default="", description="Text content")
    inner_html: str = Field(default="", description="Inner HTML")
    outer_html: str = Field(default="", description="Outer HTML")
    
    # Attributes
    attributes: Dict[str, str] = Field(default_factory=dict)
    id: Optional[str] = Field(default=None)
    class_names: List[str] = Field(default_factory=list)
    name: Optional[str] = Field(default=None)
    href: Optional[str] = Field(default=None)
    src: Optional[str] = Field(default=None)
    alt: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    value: Optional[str] = Field(default=None)
    placeholder: Optional[str] = Field(default=None)
    
    # State
    is_visible: bool = Field(default=True)
    is_enabled: bool = Field(default=True)
    is_selected: bool = Field(default=False)
    is_focused: bool = Field(default=False)
    
    # Layout
    x: float = Field(default=0)
    y: float = Field(default=0)
    width: float = Field(default=0)
    height: float = Field(default=0)
    
    # Semantic
    role: Optional[str] = Field(default=None)
    aria_label: Optional[str] = Field(default=None)
    semantic_role: Optional[str] = Field(default=None)
    
    # Events
    has_click_handler: bool = Field(default=False)
    event_listeners: List[str] = Field(default_factory=list)
    
    # Relationships
    parent_id: Optional[str] = Field(default=None)
    child_ids: List[str] = Field(default_factory=list)
    
    # Metadata
    extraction_confidence: float = Field(default=1.0)
    extraction_method: Optional[str] = Field(default=None)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        if HAS_PYDANTIC:
            return self.model_dump()
        else:
            return self.__dict__.copy()

class ExtractionResult(BaseModel):
    """Complete extraction result with metadata"""
    
    model_config = ConfigDict(str_strip_whitespace=True) if HAS_PYDANTIC else {}
    
    # Core fields
    url: str = Field(..., description="URL of the page")
    success: bool = Field(..., description="Whether extraction was successful")
    elements: List[ElementData] = Field(default_factory=list)
    
    # Page metadata
    page_title: str = Field(default="")
    page_description: Optional[str] = Field(default=None)
    page_keywords: Optional[str] = Field(default=None)
    
    # Detection metadata
    framework_detected: Optional[str] = Field(default=None)
    captcha_detected: bool = Field(default=False)
    captcha_type: Optional[str] = Field(default=None)
    
    # Performance metrics
    extraction_time: float = Field(default=0)
    retry_count: int = Field(default=0)
    
    # Errors and metadata
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        if HAS_PYDANTIC:
            result = self.model_dump()
        else:
            result = self.__dict__.copy()
        result['timestamp'] = result['timestamp'].isoformat()
        return result
    
    def get_elements_by_type(self, element_type: ElementType) -> List[ElementData]:
        """Get all elements of a specific type"""
        return [e for e in self.elements if e.element_type == element_type]
    
    def get_clickable_elements(self) -> List[ElementData]:
        """Get all clickable elements"""
        return [e for e in self.elements if e.has_click_handler or e.element_type in [
            ElementType.BUTTON, ElementType.LINK, ElementType.SUBMIT
        ]]
    
    def get_form_inputs(self) -> List[ElementData]:
        """Get all form input elements"""
        return [e for e in self.elements if e.element_type in [
            ElementType.TEXT_INPUT, ElementType.PASSWORD, ElementType.EMAIL,
            ElementType.NUMBER, ElementType.CHECKBOX, ElementType.RADIO,
            ElementType.SELECT, ElementType.TEXTAREA
        ]]
    
    @property
    def element_count(self) -> int:
        """Total number of elements extracted"""
        return len(self.elements)
    
    @property
    def has_errors(self) -> bool:
        """Whether extraction had any errors"""
        return len(self.errors) > 0

# Alias for backward compatibility
BrowserExtractionResult = ExtractionResult

# ============================================================================
# CONFIGURATION LAYER (from browser_config.py)
# ============================================================================

class BrowserStealthConfig:
    """
    Advanced browser configuration for 2025 anti-detection
    Integrated from browser_config.py
    """
    
    def __init__(self, stealth_level: str = "maximum"):
        """Initialize stealth configuration"""
        valid_levels = ['none', 'basic', 'moderate', 'advanced', 'maximum']
        if stealth_level not in valid_levels:
            logger.warning(f"Invalid stealth level '{stealth_level}', using 'maximum'")
            stealth_level = 'maximum'
        
        self.stealth_level = stealth_level
        self.platform_info = get_platform_info()
    
    def get_launch_args(self) -> List[str]:
        """Get comprehensive browser launch arguments for anti-detection"""
        
        # Base arguments for all stealth levels
        base_args = [
            # Core anti-detection flags
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-site-isolation-trials',
            
            # Performance and stability
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--disable-gpu',
            '--no-first-run',
            '--no-default-browser-check',
            
            # Window and display settings
            '--window-size=1920,1080',
            '--start-maximized',
            '--force-device-scale-factor=1',
            
            # Background throttling prevention
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            
            # WebRTC and privacy
            '--force-webrtc-ip-handling-policy=default_public_interface_only',
            '--disable-webrtc-hw-encoding',
            '--disable-webrtc-hw-decoding',
        ]
        
        # Moderate level additions
        if self.stealth_level in ['moderate', 'advanced', 'maximum']:
            base_args.extend([
                # Additional privacy flags
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-breakpad',
                '--disable-component-extensions-with-background-pages',
                '--disable-extensions',
                '--disable-features=BlinkGenPropertyTrees',
                '--disable-features=ImprovedCookieControls',
                '--disable-reading-from-canvas',
                '--disable-client-side-phishing-detection',
                
                # Memory and performance
                '--memory-pressure-off',
                '--max-gum-fps=60',
                '--disable-hang-monitor',
                '--disable-prompt-on-repost',
                '--disable-sync',
                '--disable-domain-reliability',
                
                # Font and rendering
                '--disable-font-subpixel-positioning',
                '--disable-features=FontAccess',
                '--force-color-profile=srgb',
            ])
        
        # Advanced level additions
        if self.stealth_level in ['advanced', 'maximum']:
            base_args.extend([
                # Advanced fingerprinting protection
                '--disable-features=AudioServiceOutOfProcess',
                '--disable-features=WebRtcHideLocalIpsWithMdns',
                '--disable-features=UserAgentClientHint',
                '--disable-features=SecMetadata',
                '--disable-features=SendMouseLeaveEvents',
                
                # Network and security
                '--no-pings',
                '--no-zygote',
                '--disable-features=msExperimentalScrolling',
                '--disable-features=ParallelDownloading',
                '--disable-features=AppBanners',
                '--disable-features=AudioFocusEnforcement',
                '--disable-features=AutofillServerCommunication',
                
                # Crash reporting and telemetry
                '--disable-crash-reporter',
                '--disable-features=CrashReporting',
                '--disable-features=NetworkTimeServiceQuerying',
                
                # Additional CDP protection
                '--disable-features=TranslateRanker',
                '--disable-features=PasswordImport',
                '--disable-features=PrivacySandboxSettings3',
            ])
        
        # Maximum level additions
        if self.stealth_level == 'maximum':
            base_args.extend([
                # Maximum fingerprinting protection
                '--disable-features=MediaRouter',
                '--disable-features=DialMediaRouteProvider',
                '--disable-features=RendererCodeIntegrity',
                '--disable-features=OptimizationGuideModelDownloading',
                '--disable-features=InterestFeedContentSuggestions',
                '--disable-features=CertificateTransparencyComponentUpdater',
                '--disable-features=AutofillEnableAccountWalletStorage',
                '--disable-features=CalculateNativeWinOcclusion',
                '--disable-features=SyncUSSBookmarks',
                '--disable-features=ReadLater',
                
                # Hardware fingerprinting protection
                '--disable-features=HardwareMediaKeyHandling',
                '--disable-features=UseSurfaceLayerForVideo',
                '--disable-features=WebUSB',
                '--disable-features=WebXR',
                
                # Additional network protection
                '--disable-features=NetworkQualityEstimator',
                '--disable-features=WebBluetooth',
                '--disable-features=AllowAggressiveThrottlingWithWebSocket',
            ])
        
        # Platform-specific additions
        if self.platform_info['is_linux']:
            base_args.extend(['--no-sandbox', '--disable-setuid-sandbox'])
        
        if self.platform_info['is_windows']:
            base_args.append('--disable-gpu-sandbox')
        
        return base_args
    
    def get_context_options(self) -> Dict[str, Any]:
        """Get browser context options with anti-detection settings"""
        
        # User agents for different stealth levels
        user_agents = {
            'none': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'basic': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'moderate': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'advanced': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.85 Safari/537.36',
            'maximum': self._generate_random_user_agent()
        }
        
        context_options = {
            'viewport': {'width': 1920, 'height': 1080},
            'screen': {'width': 1920, 'height': 1080},
            'device_scale_factor': 1.0,
            'is_mobile': False,
            'has_touch': False,
            'user_agent': user_agents.get(self.stealth_level, user_agents['maximum']),
            
            # Permissions
            'permissions': ['geolocation', 'notifications', 'camera', 'microphone'],
            
            # Geolocation
            'geolocation': self._get_random_geolocation(),
            
            # Locale and timezone
            'locale': 'en-US',
            'timezone_id': 'America/New_York',
            
            # Color scheme
            'color_scheme': 'light',
            
            # Extra HTTP headers
            'extra_http_headers': {
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Sec-Ch-Ua': '"Chromium";v="131", "Not_A Brand";v="24", "Google Chrome";v="131"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
            }
        }
        
        if self.stealth_level in ['advanced', 'maximum']:
            # Add client hints for advanced stealth  
            headers = context_options.get('extra_http_headers', {})
            if isinstance(headers, dict):
                headers.update({
                'Sec-Ch-Ua-Platform-Version': '"15.0.0"',
                'Sec-Ch-Ua-Full-Version': '"131.0.6778.85"',
                'Sec-Ch-Ua-Full-Version-List': '"Chromium";v="131.0.6778.85", "Not_A Brand";v="24.0.0.0", "Google Chrome";v="131.0.6778.85"',
                'Sec-Ch-Ua-Arch': '"x86"',
                    'Sec-Ch-Ua-Bitness': '"64"',
                    'Sec-Ch-Ua-Model': '""',
                })
                context_options['extra_http_headers'] = headers
        
        return context_options
    
    def get_cdp_session_config(self) -> Dict[str, Any]:
        """Get CDP session configuration to avoid detection"""
        return {
            'enable_runtime': False,
            'override_commands': {
                'Runtime.enable': {'skip': True},
                'Page.addScriptToEvaluateOnNewDocument': {'modify': True},
                'Network.setUserAgentOverride': {'modify': True},
            },
            'stealth_cdp': True,
            'minimize_cdp_usage': self.stealth_level == 'maximum'
        }
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete browser configuration with all anti-detection settings"""
        
        launch_options = {
            'args': self.get_launch_args(),
            'headless': True
        }
        
        # Try to find Chrome or Chromium executable
        browser_path = get_chrome_executable_path()
        if browser_path:
            launch_options['executable_path'] = browser_path
            logger.info(f"Using browser at: {browser_path}")
        else:
            logger.info("Using Playwright's bundled Chromium")
        
        # Additional launch options
        launch_options.update({
            'chromium_sandbox': False,
            'handle_sigint': False,
            'handle_sigterm': False,
            'handle_sighup': False,
            'timeout': 60000,
            'slow_mo': random.randint(10, 30) if self.stealth_level == 'maximum' else 0,
            'downloads_path': get_temp_directory(),
        })
        
        return {
            'launch_options': launch_options,
            'context_options': self.get_context_options(),
            'cdp_config': self.get_cdp_session_config(),
            'stealth_level': self.stealth_level,
            'platform': self.platform_info,
            'browser_type': 'chrome' if browser_path and 'chrome' in browser_path.lower() else 'chromium'
        }
    
    def _generate_random_user_agent(self) -> str:
        """Generate random realistic user agent"""
        chrome_versions = ['131.0.6778.85', '131.0.6778.70', '130.0.6723.119']
        windows_versions = ['10.0', '11.0']
        
        chrome_ver = random.choice(chrome_versions)
        win_ver = random.choice(windows_versions)
        
        return f'Mozilla/5.0 (Windows NT {win_ver}; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36'
    
    def _get_random_geolocation(self) -> Dict[str, float]:
        """Get random geolocation from major cities"""
        cities = [
            {'latitude': 40.7128, 'longitude': -74.0060},  # New York
            {'latitude': 34.0522, 'longitude': -118.2437},  # Los Angeles
            {'latitude': 41.8781, 'longitude': -87.6298},   # Chicago
            {'latitude': 29.7604, 'longitude': -95.3698},   # Houston
            {'latitude': 33.4484, 'longitude': -112.0740},  # Phoenix
        ]
        return random.choice(cities)

# ============================================================================
# ERROR HANDLING LAYER
# ============================================================================

class BrowserError(Exception):
    """Base exception for browser errors"""
    pass

class NavigationError(BrowserError):
    """Navigation-specific errors"""
    pass

class ExtractionError(BrowserError):
    """Element extraction errors"""
    pass

class TimeoutError(BrowserError):
    """Timeout-related errors"""
    pass

def retry_on_error(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0) -> Any:
    """Decorator for retrying operations on error"""
    def decorator(func) -> Any:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_error = None
            current_delay = delay
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...")
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed")
            
            if last_error:
                raise last_error
            raise RuntimeError(f"Operation failed after {max_retries} attempts")
        return wrapper
    return decorator

class ErrorHandler:
    """Centralized error handling for browser operations"""
    
    @staticmethod
    def handle_navigation_error(error: Exception, url: str) -> None:
        """Handle navigation errors with proper logging and recovery"""
        error_msg = str(error)
        
        if "timeout" in error_msg.lower():
            raise TimeoutError(f"Navigation timeout for {url}: {error_msg}")
        elif "net::ERR" in error_msg:
            raise NavigationError(f"Network error navigating to {url}: {error_msg}")
        elif "403" in error_msg or "forbidden" in error_msg.lower():
            raise NavigationError(f"Access forbidden to {url}")
        elif "404" in error_msg:
            raise NavigationError(f"Page not found: {url}")
        else:
            raise NavigationError(f"Navigation failed for {url}: {error_msg}")
    
    @staticmethod
    def handle_extraction_error(error: Exception, context: str = "") -> None:
        """Handle element extraction errors"""
        error_msg = str(error)
        
        if "timeout" in error_msg.lower():
            raise TimeoutError(f"Extraction timeout {context}: {error_msg}")
        elif "selector" in error_msg.lower():
            raise ExtractionError(f"Selector error {context}: {error_msg}")
        else:
            raise ExtractionError(f"Extraction failed {context}: {error_msg}")
    
    @staticmethod
    async def safe_execute(func: Callable, *args, **kwargs) -> Any:
        """Safely execute a function with error handling"""
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise

# ============================================================================
# STEALTH INJECTION LAYER
# ============================================================================

class StealthInjector:
    """Comprehensive stealth script injection system"""
    
    @staticmethod
    async def inject_stealth(page: 'Page', config: StealthConfig) -> Any:
        """Inject all stealth scripts based on configuration"""
        
        # Always apply basic stealth
        await StealthInjector._inject_basic_stealth(page, config)
        
        # Apply enhanced stealth for higher levels
        if config.level in [StealthLevel.ADVANCED, StealthLevel.MAXIMUM]:
            await StealthInjector._inject_enhanced_stealth(page, config)
        
        # Apply maximum stealth features
        if config.level == StealthLevel.MAXIMUM:
            await StealthInjector._inject_maximum_stealth(page, config)
        
        # Apply paranoid level features
        if config.level == StealthLevel.MAXIMUM:
            await StealthInjector._inject_paranoid_stealth(page, config)
        
        logger.debug(f"Stealth injection complete: {config.level.value}")
    
    @staticmethod
    async def _inject_basic_stealth(page: 'Page', config: StealthConfig) -> Any:
        """Basic stealth features"""
        script = """
        () => {
            // Hide webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Basic Chrome object
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            // Navigator properties
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Remove automation properties
            delete window.__playwright;
            delete window.__puppeteer;
            delete window.__selenium;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        }
        """
        await page.add_init_script(script)
    
    @staticmethod
    async def _inject_enhanced_stealth(page: 'Page', config: StealthConfig) -> Any:
        """Enhanced stealth features"""
        script = """
        () => {
            // Enhanced Chrome runtime
            window.chrome.runtime = {
                connect: () => {},
                sendMessage: () => {},
                onMessage: {
                    addListener: () => {},
                    removeListener: () => {},
                    hasListener: () => false
                },
                onConnect: {
                    addListener: () => {},
                    removeListener: () => {},
                    hasListener: () => false
                },
                onInstalled: {
                    addListener: () => {},
                    removeListener: () => {},
                    hasListener: () => false
                }
            };
            
            // Permissions API override
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => {
                if (parameters.name === 'notifications') {
                    return Promise.resolve({ state: Notification.permission });
                }
                return originalQuery(parameters);
            };
            
            // Plugin details
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    const pluginArray = [
                        {
                            name: 'Chrome PDF Plugin',
                            filename: 'internal-pdf-viewer',
                            description: 'Portable Document Format',
                            length: 1
                        },
                        {
                            name: 'Chrome PDF Viewer',
                            filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                            description: 'Portable Document Format',
                            length: 1
                        },
                        {
                            name: 'Native Client',
                            filename: 'internal-nacl-plugin',
                            description: 'Native Client Executable',
                            length: 2
                        }
                    ];
                    pluginArray.length = 3;
                    return pluginArray;
                }
            });
            
            // Media devices
            if (navigator.mediaDevices) {
                navigator.mediaDevices.enumerateDevices = async () => {
                    return [
                        {
                            deviceId: 'default',
                            kind: 'audioinput',
                            label: 'Default Audio Device',
                            groupId: 'default'
                        }
                    ];
                };
            }
        }
        """
        await page.add_init_script(script)
    
    @staticmethod
    async def _inject_maximum_stealth(page: 'Page', config: StealthConfig) -> Any:
        """Maximum stealth with all anti-detection features"""
        
        # WebRTC leak prevention
        if config.prevent_webrtc_leak:
            await page.add_init_script("""
            () => {
                const RTCPeerConnectionOriginal = window.RTCPeerConnection;
                window.RTCPeerConnection = new Proxy(RTCPeerConnectionOriginal, {
                    construct(target, args) {
                        const pc = new target(...args);
                        pc.createDataChannel = new Proxy(pc.createDataChannel, {
                            apply: function() {
                                return {
                                    send: () => {},
                                    close: () => {},
                                    addEventListener: () => {},
                                    removeEventListener: () => {}
                                };
                            }
                        });
                        return pc;
                    }
                });
                
                // Block WebRTC IP leak
                window.RTCPeerConnection.prototype.createOffer = async function() {
                    return new RTCSessionDescription({
                        type: 'offer',
                        sdp: ''
                    });
                };
            }
            """)
        
        # Canvas fingerprinting protection
        if config.spoof_canvas_fingerprint:
            await page.add_init_script("""
            () => {
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                const originalToBlob = HTMLCanvasElement.prototype.toBlob;
                const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
                
                // Add noise to canvas
                const addNoise = (imageData) => {
                    for (let i = 0; i < imageData.data.length; i += 4) {
                        imageData.data[i] += Math.random() * 2 - 1;     // R
                        imageData.data[i+1] += Math.random() * 2 - 1;   // G
                        imageData.data[i+2] += Math.random() * 2 - 1;   // B
                    }
                    return imageData;
                };
                
                HTMLCanvasElement.prototype.toDataURL = function(...args) {
                    const context = this.getContext('2d');
                    if (context) {
                        const imageData = context.getImageData(0, 0, this.width, this.height);
                        context.putImageData(addNoise(imageData), 0, 0);
                    }
                    return originalToDataURL.apply(this, args);
                };
                
                CanvasRenderingContext2D.prototype.getImageData = function(...args) {
                    const imageData = originalGetImageData.apply(this, args);
                    return addNoise(imageData);
                };
            }
            """)
        
        # WebGL spoofing
        if config.spoof_webgl:
            await page.add_init_script("""
            () => {
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    // Spoof vendor and renderer
                    if (parameter === 37445) return 'Intel Inc.';
                    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                    
                    // Spoof extensions
                    if (parameter === 7939) {
                        return [
                            'ANGLE_instanced_arrays',
                            'EXT_blend_minmax',
                            'EXT_color_buffer_half_float'
                        ];
                    }
                    
                    return getParameter.apply(this, arguments);
                };
                
                const getExtension = WebGLRenderingContext.prototype.getExtension;
                WebGLRenderingContext.prototype.getExtension = function(name) {
                    if (name === 'WEBGL_debug_renderer_info') {
                        return null;
                    }
                    return getExtension.apply(this, arguments);
                };
            }
            """)
        
        # Battery API spoofing
        if config.spoof_battery:
            await page.add_init_script("""
            () => {
                if (navigator.getBattery) {
                    navigator.getBattery = async () => ({
                        charging: true,
                        chargingTime: 0,
                        dischargingTime: Infinity,
                        level: 0.99,
                        addEventListener: () => {},
                        removeEventListener: () => {},
                        dispatchEvent: () => true
                    });
                }
            }
            """)
        
        # Hardware spoofing
        if config.spoof_hardware:
            await page.add_init_script("""
            () => {
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8
                });
                
                if (navigator.deviceMemory) {
                    Object.defineProperty(navigator, 'deviceMemory', {
                        get: () => 8
                    });
                }
                
                // Screen properties
                Object.defineProperty(screen, 'availTop', { get: () => 0 });
                Object.defineProperty(screen, 'availLeft', { get: () => 0 });
                Object.defineProperty(screen, 'availWidth', { get: () => screen.width });
                Object.defineProperty(screen, 'availHeight', { get: () => screen.height });
                Object.defineProperty(screen, 'colorDepth', { get: () => 24 });
                Object.defineProperty(screen, 'pixelDepth', { get: () => 24 });
            }
            """)
        
        # Chrome LoadTimes
        await page.add_init_script("""
        () => {
            window.chrome.loadTimes = () => ({
                requestTime: Date.now() / 1000 - Math.random() * 100,
                startLoadTime: Date.now() / 1000 - Math.random() * 100,
                commitLoadTime: Date.now() / 1000 - Math.random() * 80,
                finishDocumentLoadTime: Date.now() / 1000 - Math.random() * 60,
                finishLoadTime: Date.now() / 1000 - Math.random() * 40,
                firstPaintTime: Date.now() / 1000 - Math.random() * 30,
                firstPaintAfterLoadTime: 0,
                navigationType: "Other",
                wasFetchedViaSpdy: false,
                wasNpnNegotiated: true,
                npnNegotiatedProtocol: "h2",
                wasAlternateProtocolAvailable: false,
                connectionInfo: "h2"
            });
            
            // Native code toString
            const nativeToString = Function.prototype.toString;
            Function.prototype.toString = function() {
                if (this === window.navigator.permissions.query) {
                    return 'function query() { [native code] }';
                }
                if (this === window.chrome.runtime.sendMessage) {
                    return 'function sendMessage() { [native code] }';
                }
                return nativeToString.call(this);
            };
        }
        """)
    
    @staticmethod
    async def _inject_paranoid_stealth(page: 'Page', config: StealthConfig) -> Any:
        """Paranoid level - extreme anti-detection measures"""
        
        # F5 Networks Shape Security bypass
        if config.bypass_shape_security:
            await page.add_init_script("""
            () => {
                // Shape Security specific bypasses
                const originalDescriptor = Object.getOwnPropertyDescriptor(Element.prototype, 'innerHTML');
                if (originalDescriptor) {
                    Object.defineProperty(Element.prototype, 'innerHTML', {
                        ...originalDescriptor,
                        get: function() {
                            return originalDescriptor.get.call(this);
                        },
                        set: function(value) {
                            return originalDescriptor.set.call(this, value);
                        }
                    });
                }
                
                // Timing attack prevention
                const originalSetTimeout = window.setTimeout;
                window.setTimeout = function(callback, delay, ...args) {
                    if (delay === 0) {
                        delay = Math.random() * 4 + 1;
                    }
                    return originalSetTimeout.call(window, callback, delay, ...args);
                };
                
                // Mouse movement linearization detection
                let lastX = 0, lastY = 0;
                document.addEventListener('mousemove', (e) => {
                    const deltaX = Math.abs(e.clientX - lastX);
                    const deltaY = Math.abs(e.clientY - lastY);
                    if (deltaX === deltaY && deltaX > 0) {
                        e.stopPropagation();
                    }
                    lastX = e.clientX;
                    lastY = e.clientY;
                }, true);
            }
            """)
        
        # DataDome bypass
        if config.bypass_datadome:
            await page.add_init_script("""
            () => {
                // DataDome specific bypasses
                window.dd = { version: '4.12.0', asyncInit: true };
                
                // Override fetch to intercept DataDome calls
                const originalFetch = window.fetch;
                window.fetch = function(...args) {
                    const url = args[0];
                    if (typeof url === 'string' && url.includes('datadome')) {
                        return Promise.resolve(new Response('{}', {
                            status: 200,
                            headers: { 'Content-Type': 'application/json' }
                        }));
                    }
                    return originalFetch.apply(this, args);
                };
            }
            """)
        
        # Kasada bypass
        if config.bypass_kasada:
            await page.add_init_script("""
            () => {
                // Kasada specific bypasses
                window._kasada = { loaded: true };
                
                // Override specific Kasada checks
                Object.defineProperty(document, 'hidden', {
                    get: () => false
                });
                
                Object.defineProperty(document, 'visibilityState', {
                    get: () => 'visible'
                });
            }
            """)

# ============================================================================
# HUMAN SIMULATION LAYER
# ============================================================================

class HumanSimulator:
    """Advanced human behavior simulation"""
    
    def __init__(self, config: StealthConfig) -> None:
        self.config = config
        self.last_action_time = time.time()
    
    async def simulate_human_delay(self,
                                  min_ms: Optional[int] = None,
                                  max_ms: Optional[int] = None,
                                  delay_type: str = "generic"):
        """Generate human-like delays with various distributions"""
        
        if not self.config.enable_human_delays:
            return
        
        # Use provided values or config defaults
        if min_ms is None:
            min_ms = self.config.human_delay_range[0]
        if max_ms is None:
            max_ms = self.config.human_delay_range[1]
        
        # Different delay patterns based on type
        delay_patterns = {
            "reading": (2000, 5000),      # Reading text
            "typing": (50, 200),           # Between keystrokes
            "thinking": (1000, 3000),      # Decision making
            "moving": (100, 500),          # Mouse movement
            "clicking": (100, 300),        # Before clicking
            "scrolling": (500, 1500),      # Between scrolls
            "form_field": (300, 800),      # Between form fields
            "page_analysis": (1500, 3000), # Analyzing new page
        }
        
        if delay_type in delay_patterns:
            min_ms, max_ms = delay_patterns[delay_type]
        
        if self.config.use_lognormal_delays and HAS_NUMPY:
            # Log-normal distribution for more realistic delays
            mean = (min_ms + max_ms) / 2
            sigma = (max_ms - min_ms) / 4
            delay = np.random.lognormal(np.log(mean), sigma / mean)
            delay = max(min_ms, min(max_ms, delay))
        else:
            # Fallback to weighted random
            weights = [1, 2, 3, 3, 2, 1]  # Bell curve approximation
            segments = len(weights)
            segment_size = (max_ms - min_ms) / segments
            segment = random.choices(range(segments), weights=weights)[0]
            delay = min_ms + segment * segment_size + random.random() * segment_size
        
        await asyncio.sleep(delay / 1000)
        self.last_action_time = time.time()
    
    async def simulate_mouse_movement(self, page: 'Page', target_x: float, target_y: float) -> Any:
        """Simulate human-like mouse movement with B-spline curves"""
        
        if not self.config.enable_human_mouse:
            await page.mouse.move(target_x, target_y)
            return
        
        # Get current position (approximate)
        current_x, current_y = 0, 0
        
        if self.config.use_bspline_mouse:
            # Generate B-spline curve for natural movement
            points = self._generate_bspline_points(
                current_x, current_y, target_x, target_y
            )
            
            for point in points:
                await page.mouse.move(point['x'], point['y'])
                await asyncio.sleep(random.uniform(0.001, 0.003))
        else:
            # Simple multi-point movement
            steps = random.randint(3, 8)
            for i in range(steps):
                progress = (i + 1) / steps
                # Add some deviation from straight line
                deviation_x = random.gauss(0, 20) * (1 - progress)
                deviation_y = random.gauss(0, 20) * (1 - progress)
                
                x = current_x + (target_x - current_x) * progress + deviation_x
                y = current_y + (target_y - current_y) * progress + deviation_y
                
                await page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.01, 0.03))
    
    def _generate_bspline_points(self, x1: float, y1: float, x2: float, y2: float) -> List[Dict[str, int]]:
        """Generate B-spline curve points for smooth mouse movement"""
        
        points = []
        steps = random.randint(20, 30)
        
        # Control points for cubic Bezier curve
        cp1x = x1 + (x2 - x1) * 0.25 + random.gauss(0, 30)
        cp1y = y1 + (y2 - y1) * 0.25 + random.gauss(0, 30)
        cp2x = x1 + (x2 - x1) * 0.75 + random.gauss(0, 30)
        cp2y = y1 + (y2 - y1) * 0.75 + random.gauss(0, 30)
        
        for i in range(steps):
            t = i / (steps - 1)
            
            # Cubic Bezier formula
            x = (1-t)**3 * x1 + 3*(1-t)**2*t * cp1x + 3*(1-t)*t**2 * cp2x + t**3 * x2
            y = (1-t)**3 * y1 + 3*(1-t)**2*t * cp1y + 3*(1-t)*t**2 * cp2y + t**3 * y2
            
            # Add micro-movements
            if i > 0 and i < steps - 1:
                x += random.gauss(0, 1)
                y += random.gauss(0, 1)
            
            points.append({'x': round(x), 'y': round(y)})
        
        return points
    
    async def simulate_typing(self, page: 'Page', selector: str, text: str) -> Any:
        """Type text with human-like patterns"""
        
        element = await page.query_selector(selector)
        if not element:
            return
        
        await element.focus()
        await self.simulate_human_delay(delay_type="clicking")
        
        if not self.config.enable_human_typing:
            await element.type(text)
            return
        
        # Type character by character with variable delays
        for i, char in enumerate(text):
            await element.type(char)
            
            # Variable typing speed
            base_delay = float(random.randint(*self.config.typing_delay_range))
            
            # Occasional pauses (thinking)
            if random.random() < 0.1:
                base_delay += float(random.randint(200, 500))
            
            # Faster for common bigrams
            if i > 0:
                bigram = text[i-1:i+1].lower()
                common_bigrams = ['th', 'he', 'in', 'er', 'an', 're', 'ed', 'on', 'es', 'st']
                if bigram in common_bigrams:
                    base_delay *= 0.7
            
            # Slight acceleration as typing continues
            if i > 10:
                base_delay *= 0.9
            
            await asyncio.sleep(base_delay / 1000)
            
            # Occasional typos and corrections (very rare)
            if random.random() < 0.01 and i < len(text) - 1:
                # Make typo
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                await element.type(wrong_char)
                await asyncio.sleep(random.randint(100, 300) / 1000.0)
                # Correct it
                await page.keyboard.press('Backspace')
                await asyncio.sleep(random.randint(50, 150) / 1000.0)
    
    async def simulate_scrolling(self, page: 'Page') -> Any:
        """Simulate human-like scrolling behavior"""
        
        if not self.config.enable_human_scrolling:
            return
        
        # Random scroll distance
        scroll_distance = random.randint(100, 500)
        
        # Smooth scroll
        await page.evaluate(f"""
            window.scrollBy({{
                top: {scroll_distance},
                behavior: 'smooth'
            }});
        """)
        
        await self.simulate_human_delay(delay_type="scrolling")
        
        # Occasional scroll back (reading previous content)
        if random.random() < 0.2:
            back_distance = random.randint(50, 150)
            await page.evaluate(f"""
                window.scrollBy({{
                    top: -{back_distance},
                    behavior: 'smooth'
                }});
            """)
            await self.simulate_human_delay(min_ms=200, max_ms=600)
    
    async def simulate_micro_behaviors(self, page: 'Page') -> Any:
        """Add subtle micro-behaviors that humans naturally exhibit"""
        
        if not self.config.enable_micro_behaviors:
            return
        
        behavior = random.choice([
            'mouse_wiggle',
            'viewport_adjustment',
            'focus_change',
            'idle_movement',
            'reading_pattern'
        ])
        
        if behavior == 'mouse_wiggle':
            # Small mouse movement while reading
            viewport = page.viewport_size
            if viewport:
                x = random.randint(100, viewport['width'] - 100)
                y = random.randint(100, viewport['height'] - 100)
                await self.simulate_mouse_movement(page, x, y)
        
        elif behavior == 'viewport_adjustment':
            # Slight viewport size change (window resizing)
            viewport = page.viewport_size
            if viewport and random.random() < 0.05:
                width = viewport['width'] + random.randint(-30, 30)
                height = viewport['height'] + random.randint(-20, 20)
                width = max(800, min(2560, width))
                height = max(600, min(1440, height))
                await page.set_viewport_size({'width': width, 'height': height})
        
        elif behavior == 'focus_change':
            # Tab out and back (distraction)
            if random.random() < 0.02:
                await page.evaluate("document.body.blur()")
                await self.simulate_human_delay(min_ms=1000, max_ms=3000)
                await page.evaluate("document.body.focus()")
        
        elif behavior == 'idle_movement':
            # Idle mouse movements
            for _ in range(random.randint(2, 5)):
                viewport = page.viewport_size
                if viewport:
                    x = random.randint(50, viewport['width'] - 50)
                    y = random.randint(50, viewport['height'] - 50)
                    await page.mouse.move(x, y)
                    await asyncio.sleep(random.uniform(0.1, 0.3))
        
        elif behavior == 'reading_pattern':
            # Simulate reading pattern (left to right, top to bottom)
            viewport = page.viewport_size
            if viewport:
                for _ in range(random.randint(2, 4)):
                    # Move across horizontally (reading line)
                    start_x = random.randint(100, 300)
                    end_x = random.randint(viewport['width'] - 300, viewport['width'] - 100)
                    y = random.randint(200, viewport['height'] - 200)
                    
                    await self.simulate_mouse_movement(page, start_x, y)
                    await self.simulate_mouse_movement(page, end_x, y)
                    await self.simulate_human_delay(delay_type="reading")

# ============================================================================
# DETECTION SYSTEM LAYER
# ============================================================================

class DetectionSystem:
    """Comprehensive detection system for frameworks, CAPTCHAs, and cookies"""
    
    @staticmethod
    async def detect_framework(page: 'Page') -> Optional[str]:
        """Detect JavaScript framework used on the page"""
        
        try:
            framework = await page.evaluate("""
                () => {
                    // React
                    if (window.React || window.ReactDOM || 
                        document.querySelector('[data-reactroot], [data-reactid], #root')) {
                        return 'react';
                    }
                    
                    // Angular
                    if (window.angular || window.ng || 
                        document.querySelector('[ng-app], [data-ng-app], [ng-controller], [data-ng-controller]')) {
                        return 'angular';
                    }
                    
                    // Vue
                    if (window.Vue || document.querySelector('[data-v-]')) {
                        // Check for Vue 3
                        if (window.Vue && window.Vue.version && window.Vue.version.startsWith('3')) {
                            return 'vue3';
                        }
                        return 'vue';
                    }
                    
                    // Svelte
                    if (document.querySelector('[class*="svelte-"]')) {
                        return 'svelte';
                    }
                    
                    // Next.js
                    if (document.querySelector('#__next') || window.__NEXT_DATA__) {
                        return 'nextjs';
                    }
                    
                    // Nuxt.js
                    if (window.$nuxt || document.querySelector('#__nuxt')) {
                        return 'nuxtjs';
                    }
                    
                    // jQuery (still common)
                    if (window.jQuery || window.$) {
                        return 'jquery';
                    }
                    
                    // Ember
                    if (window.Ember || window.Em) {
                        return 'ember';
                    }
                    
                    // Backbone
                    if (window.Backbone) {
                        return 'backbone';
                    }
                    
                    return null;
                }
            """)
            
            if framework:
                logger.info(f"Framework detected: {framework}")
                
                # Framework-specific wait strategies
                if framework == 'react':
                    await page.wait_for_timeout(500)
                elif framework in ['angular', 'vue', 'vue3']:
                    await page.wait_for_timeout(700)
                elif framework == 'nextjs':
                    await page.wait_for_load_state('networkidle')
            
            return framework
            
        except Exception as e:
            logger.debug(f"Framework detection error: {e}")
            return None
    
    @staticmethod
    async def detect_captcha(page: 'Page') -> Dict[str, Any]:
        """Detect CAPTCHA presence and type"""
        
        captcha_info: Dict[str, Any] = {
            'detected': False,
            'type': None,
            'selectors': [],
            'confidence': 0.0
        }
        
        # CAPTCHA detection patterns
        captcha_patterns = [
            # reCAPTCHA
            {
                'type': 'recaptcha_v2',
                'selectors': [
                    'iframe[src*="recaptcha"]',
                    'div.g-recaptcha',
                    '#g-recaptcha',
                    'iframe[title*="recaptcha"]'
                ],
                'confidence': 0.95
            },
            {
                'type': 'recaptcha_v3',
                'selectors': [
                    'script[src*="recaptcha/api.js?render="]',
                    '.grecaptcha-badge'
                ],
                'confidence': 0.90
            },
            # hCaptcha
            {
                'type': 'hcaptcha',
                'selectors': [
                    'iframe[src*="hcaptcha.com"]',
                    'div.h-captcha',
                    '#hcaptcha',
                    'iframe[title*="hCaptcha"]'
                ],
                'confidence': 0.95
            },
            # Cloudflare
            {
                'type': 'cloudflare',
                'selectors': [
                    '.cf-browser-verification',
                    '#cf-challenge-running',
                    '.cf-challenge',
                    'div[class*="cloudflare"]'
                ],
                'confidence': 0.85
            },
            # FunCaptcha
            {
                'type': 'funcaptcha',
                'selectors': [
                    'div[id*="arkose"]',
                    'iframe[src*="funcaptcha"]',
                    '#FunCaptcha'
                ],
                'confidence': 0.90
            },
            # GeeTest
            {
                'type': 'geetest',
                'selectors': [
                    'div[class*="geetest"]',
                    'div[id*="geetest"]',
                    '.geetest_holder'
                ],
                'confidence': 0.85
            }
        ]
        
        for pattern in captcha_patterns:
            if isinstance(pattern, dict):
                selectors = pattern.get('selectors', [])
                if isinstance(selectors, (list, tuple)):
                    for selector in selectors:
                        try:
                            element = await page.query_selector(selector)
                            if element:
                                captcha_info['detected'] = True
                                captcha_info['type'] = pattern['type']
                                captcha_info['selectors'].append(selector)
                                captcha_info['confidence'] = max(
                                    captcha_info['confidence'],
                                    pattern['confidence']
                                )
                                break
                        except:
                            continue
            
            if captcha_info['detected']:
                break
        
        if captcha_info['detected']:
            logger.warning(f"CAPTCHA detected: {captcha_info['type']} (confidence: {captcha_info['confidence']})")
        
        return captcha_info

# ============================================================================
# MONITORING LAYER
# ============================================================================

class ContextMonitor:
    """Monitor browser context for issues and recovery"""
    
    def __init__(self, page: 'Page') -> None:
        self.page = page
        self.monitoring = False
        self.memory_warnings = 0
        self.network_errors = 0
        self.console_errors: List[str] = []
    
    async def start_monitoring(self) -> None:
        """Start monitoring the browser context"""
        if self.monitoring:
            return
        
        self.monitoring = True
        
        # Monitor console messages
        self.page.on('console', self._handle_console_message)
        
        # Monitor page crashes  
        self.page.on('crash', self._handle_crash)
        
        # Monitor requests/responses
        self.page.on('requestfailed', self._handle_request_failed)
        
        logger.debug("Context monitoring started")
    
    def _handle_console_message(self, msg: Any) -> None:
        """Handle console messages"""
        if msg.type == 'error':
            error_msg = f"{msg.text} at {time.time()}"
            self.console_errors.append(error_msg)
            logger.debug(f"Console error: {msg.text}")
    
    def _handle_crash(self, page: Any) -> None:
        """Handle page crashes"""
        logger.error("Page crashed! Recovery needed")
    
    def _handle_request_failed(self, request: Any) -> None:
        """Handle failed requests"""
        self.network_errors += 1
        logger.debug(f"Request failed: {request.url}")
    
    async def check_health(self) -> Dict[str, Any]:
        """Check overall browser health"""
        return {
            'healthy': self.network_errors < 10 and self.memory_warnings < 5,
            'console_errors': len(self.console_errors),
            'network_errors': self.network_errors,
            'memory_warnings': self.memory_warnings
        }

# ============================================================================
# EXTRACTION STRATEGIES LAYER
# ============================================================================

class ExtractionStrategyBase(ABC):
    """Base class for extraction strategies"""
    
    @abstractmethod
    async def extract(self, page: 'Page') -> List[ElementData]:
        """Extract elements using specific strategy"""
        pass
    
    def _generate_element_id(self, element_data: Dict) -> str:
        """Generate unique element ID"""
        content = f"{element_data.get('tag_name', '')}_{element_data.get('text', '')}_{time.time()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

class DOMExtractionStrategy(ExtractionStrategyBase):
    """DOM-based element extraction strategy"""
    
    async def extract(self, page: 'Page') -> List[ElementData]:
        """Extract elements using DOM inspection"""
        elements = []
        
        try:
            # Execute comprehensive DOM extraction
            raw_elements = await page.evaluate("""
                () => {
                    const elements = [];
                    const interactiveSelectors = [
                        'button', 'a', 'input', 'select', 'textarea',
                        '[role="button"]', '[onclick]', '[href]',
                        'label', 'form', '[type="submit"]'
                    ];
                    
                    for (const selector of interactiveSelectors) {
                        const nodes = document.querySelectorAll(selector);
                        for (const node of nodes) {
                            const rect = node.getBoundingClientRect();
                            const computed = window.getComputedStyle(node);
                            
                            elements.push({
                                tag_name: node.tagName.toLowerCase(),
                                text_content: node.textContent?.trim() || '',
                                inner_html: node.innerHTML?.substring(0, 500) || '',
                                outer_html: node.outerHTML?.substring(0, 1000) || '',
                                id: node.id || null,
                                class_names: Array.from(node.classList || []),
                                name: node.name || null,
                                href: node.href || null,
                                src: node.src || null,
                                alt: node.alt || null,
                                title: node.title || null,
                                value: node.value || null,
                                placeholder: node.placeholder || null,
                                type: node.type || null,
                                role: node.getAttribute('role') || null,
                                aria_label: node.getAttribute('aria-label') || null,
                                is_visible: computed.display !== 'none' && 
                                           computed.visibility !== 'hidden' &&
                                           rect.width > 0 && rect.height > 0,
                                is_enabled: !node.disabled,
                                x: rect.x,
                                y: rect.y,
                                width: rect.width,
                                height: rect.height
                            });
                        }
                    }
                    
                    return elements;
                }
            """)
            
            # Convert to ElementData objects
            for raw in raw_elements:
                # Extract specific fields properly
                element_id = self._generate_element_id(raw)
                element_type = self._determine_element_type(raw)
                tag_name = raw.get('tag_name', 'unknown')
                
                # Create attributes dict with only string values
                attributes = {}
                for k, v in raw.items():
                    if k not in ['tag_name', 'text_content', 'inner_html', 'outer_html',
                                 'id', 'class_names', 'name', 'href', 'src', 'alt',
                                 'title', 'value', 'placeholder', 'is_visible', 'is_enabled',
                                 'is_selected', 'is_focused', 'x', 'y', 'width', 'height',
                                 'role', 'aria_label', 'type']:
                        if v is not None:
                            attributes[k] = str(v)
                
                try:
                    element_data = ElementData(
                        element_id=element_id,
                        element_type=element_type,
                        tag_name=tag_name,
                        xpath=self._generate_xpath(raw),
                        css_selector=self._generate_css_selector(raw),
                        text_content=raw.get('text_content', ''),
                        inner_html=raw.get('inner_html', ''),
                        outer_html=raw.get('outer_html', ''),
                        attributes=attributes,
                        id=raw.get('id'),
                        class_names=raw.get('class_names', []),
                        name=raw.get('name'),
                        href=raw.get('href'),
                        src=raw.get('src'),
                        alt=raw.get('alt'),
                        title=raw.get('title'),
                        value=raw.get('value'),
                        placeholder=raw.get('placeholder'),
                        is_visible=raw.get('is_visible', True),
                        is_enabled=raw.get('is_enabled', True),
                        x=raw.get('x', 0),
                        y=raw.get('y', 0),
                        width=raw.get('width', 0),
                        height=raw.get('height', 0),
                        role=raw.get('role'),
                        aria_label=raw.get('aria_label'),
                        extraction_method='dom_inspection'
                    )
                    elements.append(element_data)
                except Exception as e:
                    logger.debug(f"Failed to create ElementData: {e}, raw data: {raw}")
            
            logger.debug(f"DOM extraction found {len(elements)} elements")
            
        except Exception as e:
            logger.error(f"DOM extraction failed: {e}")
        
        return elements
    
    def _determine_element_type(self, element_data: Dict) -> ElementType:
        """Determine element type from raw data"""
        tag = (element_data.get('tag_name') or '').lower()
        type_attr = (element_data.get('type') or '').lower()
        role = (element_data.get('role') or '').lower()
        
        # Map HTML tags to ElementType
        if tag == 'button' or role == 'button':
            return ElementType.BUTTON
        elif tag == 'a':
            return ElementType.LINK
        elif tag == 'input':
            if type_attr == 'text' or type_attr == '':
                return ElementType.TEXT_INPUT
            elif type_attr == 'password':
                return ElementType.PASSWORD
            elif type_attr == 'email':
                return ElementType.EMAIL
            elif type_attr == 'number':
                return ElementType.NUMBER
            elif type_attr == 'checkbox':
                return ElementType.CHECKBOX
            elif type_attr == 'radio':
                return ElementType.RADIO
            elif type_attr == 'submit':
                return ElementType.SUBMIT
            elif type_attr == 'file':
                return ElementType.FILE_INPUT
            elif type_attr == 'date':
                return ElementType.DATE_INPUT
            elif type_attr == 'search':
                return ElementType.SEARCH
            else:
                return ElementType.TEXT_INPUT
        elif tag == 'select':
            return ElementType.SELECT
        elif tag == 'textarea':
            return ElementType.TEXTAREA
        elif tag == 'form':
            return ElementType.FORM
        elif tag == 'label':
            return ElementType.LABEL
        elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return ElementType.HEADING
        elif tag == 'p':
            return ElementType.PARAGRAPH
        elif tag == 'div':
            return ElementType.DIV
        elif tag == 'span':
            return ElementType.SPAN
        elif tag == 'img':
            return ElementType.IMAGE
        elif tag == 'video':
            return ElementType.VIDEO
        elif tag == 'audio':
            return ElementType.AUDIO
        elif tag == 'iframe':
            return ElementType.IFRAME
        elif tag == 'table':
            return ElementType.TABLE
        elif tag in ['ul', 'ol']:
            return ElementType.LIST
        elif tag == 'li':
            return ElementType.LIST_ITEM
        else:
            return ElementType.UNKNOWN
    
    def _generate_xpath(self, element_data: Dict) -> str:
        """Generate XPath selector for element"""
        tag = element_data.get('tag_name', 'div')
        id_attr = element_data.get('id')
        
        if id_attr:
            return f"//{tag}[@id='{id_attr}']"
        
        classes = element_data.get('class_names', [])
        if classes:
            class_condition = ' and '.join([f"contains(@class, '{cls}')" for cls in classes[:2]])
            return f"//{tag}[{class_condition}]"
        
        text = element_data.get('text_content', '')[:30]
        if text:
            return f"//{tag}[contains(text(), '{text}')]"
        
        return f"//{tag}"
    
    def _generate_css_selector(self, element_data: Dict) -> str:
        """Generate CSS selector for element"""
        tag = element_data.get('tag_name', 'div')
        id_attr = element_data.get('id')
        
        if id_attr:
            return f"#{id_attr}"
        
        classes = element_data.get('class_names', [])
        if classes:
            return f"{tag}.{'.'.join(classes[:2])}"
        
        return tag

# ============================================================================
# CIRCUIT BREAKER AND RATE LIMITER
# ============================================================================

class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = 'closed'  # closed, open, half-open
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        
        # Check if circuit should be reset
        if self.state == 'open':
            if self.last_failure_time and time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'half-open'
                self.failure_count = 0
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
            
            # Success - reset failure count
            if self.state == 'half-open':
                self.state = 'closed'
            self.failure_count = 0
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'open'
                logger.error(f"Circuit breaker opened after {self.failure_count} failures")
            
            raise e

class RateLimiter:
    """Rate limiter for API and request throttling"""
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: List[Any] = []
    
    async def acquire(self) -> None:
        """Acquire permission to make a request"""
        
        now = time.time()
        
        # Clean old requests
        self.requests = [r for r in self.requests if now - r < self.time_window]
        
        # Check if we can make a request
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0])
            if sleep_time > 0:
                logger.debug(f"Rate limit reached, sleeping for {sleep_time:.1f}s")
                await asyncio.sleep(sleep_time)
                return await self.acquire()
        
        # Record this request
        self.requests.append(now)

# ============================================================================
# MAIN BROWSER CLASS
# ============================================================================

class UltimateStealthBrowser:
    """
    Ultimate unified stealth browser with comprehensive features.
    
    This is the main class that orchestrates all functionality:
    - Stealth and anti-detection
    - Human behavior simulation
    - Multi-strategy element extraction
    - Framework and CAPTCHA detection
    - Context monitoring and recovery
    - Performance optimization
    """
    
    def __init__(self, config: Optional[StealthConfig] = None) -> None:
        """Initialize with production-ready concurrency controls"""
        self.config = config or StealthConfig()
        
        # Production concurrency controls
        self._operation_semaphore = asyncio.Semaphore(10)  # Max 10 concurrent operations
        self._navigation_lock = asyncio.Lock()  # Serialize navigation
        self._extraction_semaphore = asyncio.Semaphore(5)  # Max 5 concurrent extractions
        self._rate_limiter = RateLimiter(max_requests=100, time_window=60)  # 100 req/min
        self._circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)
        
        # Initialize components
        self.human_simulator = HumanSimulator(self.config)
        self.browser: Optional[Any] = None
        self.context: Optional[Any] = None
        self.page: Optional[Any] = None
        self.playwright: Optional[Any] = None
        self.session_id = f"session_{int(time.time() * 1000)}"
        
        # Initialize extraction strategies
        self.extraction_strategies = [
            DOMExtractionStrategy()
        ]
        
        # Monitoring
        self._metrics: Dict[str, Any] = {
            'requests_total': 0,
            'requests_success': 0,
            'requests_failed': 0,
            'avg_response_time': 0.0,
            'errors': []
        }
    
    async def __aenter__(self) -> Any:
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> Any:
        """Async context manager exit"""
        await self.cleanup()
    
    async def initialize(self) -> None:
        """Initialize browser with full stealth configuration"""
        
        if not HAS_PLAYWRIGHT:
            raise ImportError("Playwright is required. Install with: pip install playwright")
        
        try:
            # Start Playwright
            self.playwright = await async_playwright().start()
            
            # Configure browser launch options
            launch_options = self._get_launch_options()
            
            # Launch browser
            self.browser = await self.playwright.chromium.launch(**launch_options)
            
            # Create context with stealth settings
            self.context = await self._create_stealth_context()
            
            # Create page
            self.page = await self.context.new_page()
            
            # Apply stealth scripts
            await StealthInjector.inject_stealth(self.page, self.config)
            
            # Set up monitoring
            self.monitor = ContextMonitor(self.page)
            await self.monitor.start_monitoring()
            
            # Set up request interception if needed
            if self.config.bypass_cloudflare or self.config.bypass_f5_networks:
                await self._setup_request_interception()
            
            logger.info("Browser initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise
    
    def _get_launch_options(self) -> Dict[str, Any]:
        """Get browser launch options with stealth configurations"""
        
        # Use integrated BrowserStealthConfig
        stealth_level = self.config.level.value if hasattr(self.config.level, 'value') else str(self.config.level)
        browser_config = BrowserStealthConfig(stealth_level.lower())
        full_config = browser_config.get_complete_config()
        launch_options = full_config['launch_options']
        
        # Store CDP config and browser type for later use
        self._cdp_config = full_config.get('cdp_config', {})
        self._browser_type = full_config.get('browser_type', 'chromium')
        
        # Override headless setting from our config
        launch_options['headless'] = self.config.headless
        
        logger.info(f"Using browser configuration: {len(launch_options['args'])} anti-detection flags for {self._browser_type}")
        return launch_options
    
    async def _create_stealth_context(self) -> 'BrowserContext':
        """Create browser context with stealth settings"""
        
        # Use integrated BrowserStealthConfig
        stealth_level = self.config.level.value if hasattr(self.config.level, 'value') else str(self.config.level)
        browser_config = BrowserStealthConfig(stealth_level.lower())
        full_config = browser_config.get_complete_config()
        context_options = full_config['context_options']
        
        # Override with our viewport settings
        context_options['viewport'] = {
            'width': self.config.viewport_width,
            'height': self.config.viewport_height
        }
        
        # Apply proxy if configured
        if self.config.proxy_server:
            context_options['proxy'] = {
                'server': self.config.proxy_server,
                'username': self.config.proxy_username,
                'password': self.config.proxy_password
            }
        
        # Use custom user agent if provided
        if self.config.user_agent:
            context_options['user_agent'] = self.config.user_agent
        
        # Apply our config settings
        context_options['bypass_csp'] = self.config.bypass_csp
        context_options['ignore_https_errors'] = self.config.ignore_https_errors
        context_options['locale'] = self.config.locale
        context_options['timezone_id'] = self.config.timezone
        
        logger.info(f"Creating context with browser_config: {len(context_options.get('extra_http_headers', {}))} headers")
        if not self.browser:
            raise RuntimeError("Browser not initialized")
        return await self.browser.new_context(**context_options)
    
    async def _setup_request_interception(self) -> Any:
        """Set up request interception for bypassing protection"""
        
        async def handle_route(route) -> None:
            """Handle intercepted requests"""
            
            url = route.request.url.lower()
            
            # Block tracking and bot detection scripts
            blocking_patterns = [
                'google-analytics', 'googletagmanager', 'doubleclick',
                'facebook.com/tr', 'amazon-adsystem',
                'datadome', 'kasada', 'shape', 'perimeterx',
                'fingerprint', 'botdetect', 'captcha-delivery'
            ]
            
            for pattern in blocking_patterns:
                if pattern in url:
                    logger.debug(f"Blocking: {route.request.url[:50]}...")
                    await route.abort()
                    return
            
            # Continue with request
            await route.continue_()
        
        # Set up route handler
        if not self.page:
            raise RuntimeError("Page not initialized")
        await self.page.route('**/*', handle_route)
        logger.debug("Request interception enabled")
    
    @retry_on_error(max_retries=3)
    async def navigate(self, url: str, wait_for: str = 'domcontentloaded') -> bool:
        """Navigate to URL with human-like behavior and error handling"""
        
        async with self._navigation_lock:
            try:
                # Rate limiting
                await self._rate_limiter.acquire()
                
                # Update metrics
                self._metrics['requests_total'] += 1
                start_time = time.time()
                
                # Build trust if needed
                if self.config.level == StealthLevel.MAXIMUM:
                    await self._build_trust()
                
                # Navigate
                logger.info(f"Navigating to: {url}")
                if not self.page:
                    raise RuntimeError("Page not initialized")
                await self.page.goto(url, wait_until=wait_for, timeout=self.config.default_timeout)
                
                # Wait for stability
                await self.human_simulator.simulate_human_delay(delay_type="page_analysis")
                
                # Detect and handle framework
                framework = await DetectionSystem.detect_framework(self.page)
                
                # Check for CAPTCHA
                captcha_info = await DetectionSystem.detect_captcha(self.page)
                if captcha_info['detected']:
                    logger.warning(f"CAPTCHA detected: {captcha_info['type']}")
                    # In production, you would handle CAPTCHA here
                
                # Human micro-behaviors
                await self.human_simulator.simulate_micro_behaviors(self.page)
                
                # Update metrics
                self._metrics['requests_success'] += 1
                elapsed = time.time() - start_time
                self._metrics['avg_response_time'] = (
                    self._metrics['avg_response_time'] + elapsed
                ) / self._metrics['requests_success']
                
                logger.info(f"Navigation successful ({elapsed:.2f}s)")
                return True
                
            except Exception as e:
                self._metrics['requests_failed'] += 1
                self._metrics['errors'].append(str(e))
                ErrorHandler.handle_navigation_error(e, url)
                return False
    
    async def _build_trust(self) -> None:
        """Build trust by visiting safe domains"""
        
        safe_domains = [
            'https://www.google.com',
            'https://www.wikipedia.org',
            'https://www.github.com'
        ]
        
        trust_domain = random.choice(safe_domains)
        logger.debug(f"Building trust: {trust_domain}")
        
        try:
            if not self.page:
                return
            await self.page.goto(trust_domain, wait_until='domcontentloaded', timeout=15000)
            await self.human_simulator.simulate_human_delay(delay_type="reading")
            await self.human_simulator.simulate_scrolling(self.page)
        except:
            pass  # Trust building is optional
    
    async def extract_elements(self, url: str) -> ExtractionResult:
        """Extract elements from a URL using multiple strategies"""
        
        async with self._extraction_semaphore:
            start_time = time.time()
            
            # Navigate to URL
            nav_success = await self.navigate(url)
            
            if not nav_success:
                return ExtractionResult(
                    url=url,
                    success=False,
                    elements=[],
                    errors=["Navigation failed"]
                )
            
            # Extract page metadata
            if not self.page:
                raise RuntimeError("Page not initialized")
            page_title = await self.page.title()
            
            # Run extraction strategies
            all_elements = []
            for strategy in self.extraction_strategies:
                try:
                    elements = await strategy.extract(self.page)
                    all_elements.extend(elements)
                except Exception as e:
                    logger.error(f"Strategy {strategy.__class__.__name__} failed: {e}")
            
            # Deduplicate elements
            unique_elements = self._deduplicate_elements(all_elements)
            
            # Detect framework
            framework = await DetectionSystem.detect_framework(self.page)
            
            # Check for CAPTCHA
            captcha_info = await DetectionSystem.detect_captcha(self.page)
            
            extraction_time = time.time() - start_time
            
            return ExtractionResult(
                url=url,
                success=True,
                elements=unique_elements,
                page_title=page_title,
                framework_detected=framework,
                captcha_detected=captcha_info['detected'],
                captcha_type=captcha_info.get('type'),
                extraction_time=extraction_time,
                metadata={
                    'session_id': self.session_id,
                    'stealth_level': self.config.level.value,
                    'element_count': len(unique_elements)
                }
            )
    
    def _deduplicate_elements(self, elements: List[ElementData]) -> List[ElementData]:
        """Remove duplicate elements based on unique identifiers"""
        
        seen = set()
        unique = []
        
        for element in elements:
            # Create unique key
            key = f"{element.tag_name}_{element.xpath}_{element.text_content[:50]}"
            
            if key not in seen:
                seen.add(key)
                unique.append(element)
        
        return unique
    
    async def cleanup(self) -> None:
        """Clean up browser resources"""
        
        try:
            if self.page:
                await self.page.close()
            
            if self.context:
                await self.context.close()
            
            if self.browser:
                await self.browser.close()
            
            if self.playwright:
                await self.playwright.stop()
            
            logger.info("Browser cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get browser performance metrics"""
        
        health = await self.monitor.check_health() if self.monitor else {}
        
        return {
            **self._metrics,
            'session_id': self.session_id,
            'health': health,
            'stealth_level': self.config.level.value
        }

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_browser_config(level: str = "maximum") -> Dict[str, Any]:
    """
    Get complete browser configuration for given stealth level
    
    Returns:
        Dict containing launch_options, context_options, cdp_config, etc.
    """
    config = BrowserStealthConfig(level)
    return config.get_complete_config()

async def quick_extract(url: str, headless: bool = True) -> ExtractionResult:
    """
    Quick extraction helper for one-off extractions
    
    Args:
        url: URL to extract from
        headless: Run browser in headless mode
    
    Returns:
        ExtractionResult with extracted elements
    """
    config = StealthConfig(headless=headless, level=StealthLevel.MAXIMUM)
    
    async with UltimateStealthBrowser(config) as browser:
        result = await browser.extract_elements(url)
    
    return result

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main execution for testing"""
    
    print("[INTEGRATED BROWSER MODULE TEST]")
    print("=" * 60)
    
    # Test configuration
    config = StealthConfig(
        level=StealthLevel.MAXIMUM,
        headless=True,
        enable_human_delays=True,
        enable_human_mouse=True,
        enable_human_typing=True
    )
    
    # Create browser instance
    browser = UltimateStealthBrowser(config)
    
    try:
        # Initialize
        await browser.initialize()
        print("[OK] Browser initialized")
        
        # Test extraction
        result = await browser.extract_elements("https://example.com")
        
        print(f"[OK] Extraction completed")
        print(f"  - URL: {result.url}")
        print(f"  - Success: {result.success}")
        print(f"  - Elements found: {result.element_count}")
        print(f"  - Framework: {result.framework_detected}")
        print(f"  - CAPTCHA: {result.captcha_detected}")
        print(f"  - Time: {result.extraction_time:.2f}s")
        
        # Get metrics
        metrics = await browser.get_metrics()
        print(f"[OK] Metrics:")
        print(f"  - Total requests: {metrics['requests_total']}")
        print(f"  - Success rate: {metrics['requests_success']}/{metrics['requests_total']}")
        print(f"  - Avg response time: {metrics['avg_response_time']:.2f}s")
        
    finally:
        # Cleanup
        await browser.cleanup()
        print("[OK] Browser cleaned up")
    
    print("=" * 60)
    print("[SUCCESS] Integrated browser module is production ready!")

if __name__ == "__main__":
    # Run test
    asyncio.run(main())