"""
Browser Module Pydantic V2 Contracts
Defines all data models for browser.py using Pydantic v2
"""

from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from pipeline_contracts import ElementType


# ============================================================================
# ENUMS
# ============================================================================

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
# CONFIGURATION MODELS
# ============================================================================

class TimingProfile(BaseModel):
    """Timing configuration for human-like behavior"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
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
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
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


class BrowserProfile(BaseModel):
    """Complete browser profile configuration"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: str = Field(..., description="Profile name")
    profile_type: ProfileType = Field(..., description="Profile type")
    timing: TimingProfile = Field(default_factory=TimingProfile)
    stealth: StealthProfile = Field(default_factory=StealthProfile)
    launch_args: List[str] = Field(default_factory=lambda: [
        '--disable-blink-features=AutomationControlled',
        '--disable-features=IsolateOrigins,site-per-process',
        '--disable-web-security',
        '--disable-site-isolation-trials',
        '--disable-dev-shm-usage',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-accelerated-2d-canvas',
        '--disable-gpu',
        '--window-size=1920,1080',
        '--start-maximized',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
    ])


class StealthConfig(BaseModel):
    """Complete stealth configuration"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    # Core settings
    level: StealthLevel = Field(default=StealthLevel.MAXIMUM)
    headless: bool = Field(default=False, description="False for better stealth")
    
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
    slow_mo: int = Field(default=0, description="Slow down by ms")
    default_timeout: int = Field(default=30000, description="Default timeout in ms")
    timeout: int = Field(default=30, description="Timeout in seconds (for compatibility)")
    
    # Advanced
    ignore_https_errors: bool = Field(default=False)
    extra_headers: Optional[Dict[str, str]] = Field(default=None)
    
    # Custom launch args
    custom_args: List[str] = Field(default_factory=list)
    
    # Additional bypass options
    bypass_cloudflare: bool = Field(default=False, description="Bypass Cloudflare detection")
    bypass_f5_networks: bool = Field(default=False, description="Bypass F5 Networks detection")
    bypass_shape_security: bool = Field(default=False, description="Bypass Shape Security detection")
    bypass_datadome: bool = Field(default=False, description="Bypass DataDome detection")
    bypass_kasada: bool = Field(default=False, description="Bypass Kasada detection")
    
    # Locale and timezone
    locale: str = Field(default="en-US", description="Browser locale")
    timezone: str = Field(default="America/New_York", description="Browser timezone")
    
    # Human simulation settings
    enable_human_delays: bool = Field(default=True, description="Enable human-like delays")
    enable_human_mouse: bool = Field(default=True, description="Enable human-like mouse movements")
    enable_human_typing: bool = Field(default=True, description="Enable human-like typing")
    enable_human_scrolling: bool = Field(default=True, description="Enable human-like scrolling")
    enable_micro_behaviors: bool = Field(default=True, description="Enable micro behaviors")
    human_delay_range: Tuple[int, int] = Field(default=(500, 2000), description="Min, max delay in ms for human simulation")
    use_lognormal_delays: bool = Field(default=True, description="Use log-normal distribution for more human-like delays")
    max_retry_attempts: int = Field(default=3, description="Maximum number of retry attempts for operations")
    
    # Detection settings
    detect_frameworks: bool = Field(default=False, description="Enable framework detection")
    
    # Mouse movement settings
    use_bspline_mouse: bool = Field(default=True, description="Use B-spline curves for mouse movement")


# ============================================================================
# DATA MODELS
# ============================================================================

class ElementData(BaseModel):
    """Comprehensive element data structure"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
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
    extraction_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    extraction_method: Optional[str] = Field(default=None)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return self.model_dump()


class BrowserExtractionResult(BaseModel):
    """Complete extraction result with metadata - Main contract for browser.py"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    # Core fields
    url: str = Field(..., description="URL of the page")
    success: bool = Field(..., description="Whether extraction was successful")
    elements: List[ElementData] = Field(default_factory=list, description="Extracted elements")
    
    # Page metadata
    page_title: str = Field(default="", description="Page title")
    page_description: Optional[str] = Field(default=None, description="Page description")
    page_keywords: Optional[str] = Field(default=None, description="Page keywords")
    
    # Detection metadata
    framework_detected: Optional[str] = Field(default=None, description="Detected framework")
    captcha_detected: bool = Field(default=False, description="Whether captcha was detected")
    captcha_type: Optional[str] = Field(default=None, description="Type of captcha detected")
    
    # Performance metrics
    extraction_time: float = Field(default=0, ge=0, description="Extraction time in seconds")
    retry_count: int = Field(default=0, ge=0, description="Number of retries")
    
    # Errors and metadata
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    warnings: List[str] = Field(default_factory=list, description="Any warnings")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.now, description="Extraction timestamp")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = self.model_dump()
        # Convert datetime to string
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


# For backward compatibility, alias the old name
ExtractionResult = BrowserExtractionResult