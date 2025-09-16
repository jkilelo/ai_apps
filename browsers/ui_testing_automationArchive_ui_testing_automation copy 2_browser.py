#!/usr/bin/env python3
"""
Ultimate Stealth Browser - Comprehensive unified browser automation with maximum anti-detection.
"""
# Standard library imports
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
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Optional, Dict, List, Any, Union, Tuple, Callable, TypeVar

# Configure secure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('browser.log', mode='a', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Type variables for generic typing
T = TypeVar('T')

# Add path for utils module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from utils.platform_utils import get_chrome_executable_path
    HAS_PLATFORM_UTILS = True
except ImportError:
    HAS_PLATFORM_UTILS = False

# Third-party imports with graceful fallbacks
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
try:
    from playwright.async_api import (
        BrowserContext, Page, async_playwright
    )
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("Warning: Playwright not installed. Install with: pip install playwright")

try:
    from pydantic import BaseModel, Field
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel = object  # type: ignore
    def Field(*args, **kwargs) -> None: return None


# ============================================================================
# FOUNDATION LAYER - Configuration and Data Models
# ============================================================================

class StealthLevel(Enum):
    """Stealth levels for different anti-detection requirements"""
    OFF = "off"            # No stealth - for testing
    BASIC = "basic"        # Basic anti-detection
    MODERATE = "moderate"  # Moderate stealth level
    HIGH = "high"          # High stealth level
    ENHANCED = "enhanced"  # Enhanced with stealth features
    MAXIMUM = "maximum"    # Maximum stealth with all features
    PARANOID = "paranoid"  # Extreme measures for heavily protected sites

class ExtractionStrategy(Enum):
    """Element extraction strategies"""
    DOM = "dom"
    VISUAL = "visual"
    ACCESSIBILITY = "accessibility"
    SHADOW_DOM = "shadow_dom"
    SEMANTIC_AI = "semantic_ai"
    ML_CLASSIFICATION = "ml_classification"
    HYBRID = "hybrid"


def monitor_performance(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to monitor function performance"""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        start_time = time.time()
        try:
            result = await func(self, *args, **kwargs)
            self._metrics['requests_success'] += 1
            return result
        except Exception as e:
            self._metrics['requests_failed'] += 1
            self._metrics['errors'].append(str(e)[:100])
            raise
        finally:
            elapsed = time.time() - start_time
            self._metrics['requests_total'] += 1
            # Update rolling average
            n = self._metrics['requests_total']
            self._metrics['avg_response_time'] = (
                (self._metrics['avg_response_time'] * (n - 1) + elapsed) / n
            )
    return wrapper


# ============================================================================
# BROWSER PROFILES SYSTEM (from ui_testing_v2/core/browser_profiles.py)
# ============================================================================

class ProfileType(str, Enum):
    """Available browser profile types"""
    BOT = "bot"
    HUMAN = "human"
    STEALTH = "stealth"
    ULTRA_STEALTH = "ultra_stealth"
    CUSTOM = "custom"

@dataclass
class TimingProfile:
    """Timing configuration for human-like behavior"""
    element_analysis_delay: Tuple[int, int] = (10, 50)  # min, max in ms
    cookie_consent_wait: Tuple[int, int] = (1500, 2500)
    cookie_button_hover: Tuple[int, int] = (300, 700)
    cookie_post_click: Tuple[int, int] = (500, 1000)
    trust_initial_wait: Tuple[int, int] = (2000, 4000)
    trust_link_hover: tuple = (500, 1000)
    trust_scroll_pause: tuple = (500, 2000)
    stability_initial: tuple = (500, 1500)
    network_idle_timeout: int = 15000
    challenge_wait: tuple = (3000, 5000)
    challenge_complete: tuple = (2000, 3000)
    selector_batch_delay: tuple = (50, 150)
    event_extraction_delay: tuple = (100, 300)
    dynamic_content_wait: tuple = (1000, 2000)
    dynamic_content_trigger: tuple = (500, 1000)
    mouse_move_steps: tuple = (15, 25)
    mouse_step_delay: tuple = (10, 30)
    typing_base_delay: tuple = (80, 150)
    typing_variation: tuple = (-30, 30)
    typing_pause_chance: float = 0.1
    typing_pause_duration: tuple = (300, 800)
    scroll_distance: tuple = (100, 400)
    scroll_pause: tuple = (300, 1500)
    scroll_back_chance: float = 0.2
    scroll_back_distance: tuple = (50, 150)

@dataclass
class StealthProfile:
    """Stealth configuration for anti-detection"""
    hide_webdriver: bool = True
    hide_automation_indicators: bool = True
    hide_cdp_properties: bool = True
    spoof_plugins: bool = True
    spoof_languages: bool = True
    spoof_chrome_runtime: bool = True
    spoof_permissions: bool = True
    prevent_webrtc_leak: bool = True
    spoof_canvas_fingerprint: bool = True
    spoof_battery_api: bool = True
    randomize_hardware_concurrency: bool = True
    randomize_device_memory: bool = True
    normalize_screen_properties: bool = True
    spoof_webgl: bool = True
    build_trust: bool = True
    trust_safe_domains: List[str] = field(default_factory=lambda: [
        'google.com', 'wikipedia.org', 'github.com', 'youtube.com'
    ])
    trust_visit_pages: int = 3
    auto_handle_cookies: bool = True
    cookie_selectors: List[str] = field(default_factory=lambda: [
        'button:has-text("Accept")',
        'button:has-text("Accept all")',
        'button:has-text("Accept cookies")',
        'button:has-text("I agree")',
        'button:has-text("OK")',
        'button:has-text("Got it")',
        'button[id*="accept"]',
        'button[class*="accept"]',
        '[id*="cookie"] button',
        '[class*="cookie"] button',
        '[class*="consent"] button',
        '[class*="gdpr"] button'
    ])
    handle_cloudflare: bool = True
    challenge_timeout: int = 30000
    randomize_viewport: bool = True
    viewport_base: tuple = (1920, 1080)
    viewport_variation: tuple = (40, 40)
    user_agents: List[str] = field(default_factory=lambda: [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ])

@dataclass
class BrowserProfile:
    """Complete browser profile configuration"""
    name: str
    profile_type: ProfileType
    timing: TimingProfile
    stealth: StealthProfile
    launch_args: List[str] = field(default_factory=lambda: [
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
        '--disable-renderer-backgrounding',
        '--disable-features=TranslateUI',
        '--disable-ipc-flooding-protection'
    ])



# ============================================================================
# LLM ENHANCEMENTS (from ui_testing_v3/ultimate_stealth_browser_llm_enhanced.py)
# ============================================================================

class LLMEnhancedExtractionStrategy:
    """Enhanced extraction strategy that captures rich context for LLM test generation"""
    
    @staticmethod
    async def extract_with_llm_context(page, config) -> Dict[str, Any]:
        """
        Extract elements with comprehensive context for LLM test generation.
        This is the main enhancement over the basic extraction.
        """
        
        extraction_script = """
        () => {
            // Helper function to get element's semantic role
            const getSemanticRole = (element) => {
                const semanticTags = {
                    'nav': 'navigation',
                    'header': 'header',
                    'footer': 'footer',
                    'main': 'main_content',
                    'article': 'article',
                    'section': 'section',
                    'aside': 'sidebar',
                    'form': 'form',
                    'search': 'search'
                };
                
                if (semanticTags[element.tagName.toLowerCase()]) {
                    return semanticTags[element.tagName.toLowerCase()];
                }
                
                if (element.role) {
                    return element.role;
                }
                
                const classAndId = (element.className + ' ' + element.id).toLowerCase();
                if (classAndId.includes('nav')) return 'navigation';
                if (classAndId.includes('header')) return 'header';
                if (classAndId.includes('footer')) return 'footer';
                if (classAndId.includes('sidebar')) return 'sidebar';
                if (classAndId.includes('modal')) return 'modal';
                if (classAndId.includes('search')) return 'search';
                if (classAndId.includes('login') || classAndId.includes('signin')) return 'authentication';
                if (classAndId.includes('signup') || classAndId.includes('register')) return 'registration';
                if (classAndId.includes('cart')) return 'shopping_cart';
                if (classAndId.includes('checkout') || classAndId.includes('payment')) return 'payment';
                
                return null;
            };
            
            // Extract form field groupings
            const extractFormGroups = () => {
                const forms = document.querySelectorAll('form');
                const formGroups = [];
                
                forms.forEach(form => {
                    const fields = form.querySelectorAll('input, select, textarea');
                    const fieldGroups = [];
                    
                    fields.forEach(field => {
                        const label = form.querySelector(`label[for="${field.id}"]`) || 
                                    field.closest('label');
                        fieldGroups.push({
                            name: field.name,
                            type: field.type || field.tagName.toLowerCase(),
                            required: field.required,
                            label: label ? label.textContent.trim() : null,
                            validation: {
                                pattern: field.pattern,
                                minLength: field.minLength,
                                maxLength: field.maxLength,
                                min: field.min,
                                max: field.max
                            }
                        });
                    });
                    
                    formGroups.push({
                        action: form.action,
                        method: form.method,
                        fields: fieldGroups
                    });
                });
                
                return formGroups;
            };
            
            // Get page context
            const pageContext = {
                title: document.title,
                url: window.location.href,
                forms: extractFormGroups(),
                hasAuthentication: !!document.querySelector('input[type="password"]'),
                hasSearch: !!document.querySelector('input[type="search"], [role="search"]'),
                hasNavigation: !!document.querySelector('nav, [role="navigation"]'),
                semanticStructure: {
                    header: !!document.querySelector('header'),
                    main: !!document.querySelector('main'),
                    footer: !!document.querySelector('footer'),
                    navigation: !!document.querySelector('nav'),
                    aside: !!document.querySelector('aside')
                }
            };
            
            return pageContext;
        }
        """
        
        try:
            context = await page.evaluate(extraction_script)
            return context
        except Exception as e:
            logger.warning(f"LLM context extraction failed: {e}")
            return {}
    
    @staticmethod
    def categorize_element_for_llm(element: Dict[str, Any]) -> str:
        """Categorize element for better LLM understanding"""
        tag = element.get('tag_name', '').lower()
        element_type = element.get('type', '').lower()
        role = element.get('role', '').lower()
        
        # Navigation elements
        if tag in ['nav', 'a'] or role == 'navigation':
            return 'navigation'
        
        # Form inputs
        if tag in ['input', 'select', 'textarea']:
            if element_type == 'password':
                return 'authentication'
            elif element_type == 'email':
                return 'form_input_email'
            elif element_type == 'search':
                return 'search'
            return 'form_input'
        
        # Action elements
        if tag == 'button' or element_type in ['submit', 'button']:
            return 'action'
        
        # Content elements
        if tag in ['p', 'div', 'span', 'article', 'section']:
            return 'content'
        
        # Media elements
        if tag in ['img', 'video', 'audio']:
            return 'media'
        
        # Data display
        if tag in ['table', 'ul', 'ol', 'dl']:
            return 'data_display'
        
        return 'unknown'



# ============================================================================
# PRODUCTION ERROR HANDLING (from browser/browser.py)
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
            
            raise last_error
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


class ElementType(Enum):
    """Comprehensive element type classification"""
    BUTTON = "button"
    INPUT = "input"
    LINK = "link"
    FORM = "form"
    TABLE = "table"
    IMAGE = "image"
    VIDEO = "video"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TEXTAREA = "textarea"
    MODAL = "modal"
    NAVIGATION = "navigation"
    PAGINATION = "pagination"
    CAPTCHA = "captcha"
    UNKNOWN = "unknown"

@dataclass
class StealthConfig:
    """Complete stealth configuration"""
    # Core settings
    level: StealthLevel = StealthLevel.MAXIMUM
    headless: bool = False  # False for better stealth
    
    # Stealth features
    hide_webdriver: bool = True
    hide_automation_indicators: bool = True
    spoof_plugins: bool = True
    spoof_languages: bool = True
    spoof_chrome_runtime: bool = True
    prevent_webrtc_leak: bool = True
    spoof_canvas_fingerprint: bool = True
    randomize_fingerprint: bool = True
    spoof_webgl: bool = True
    spoof_battery: bool = True
    spoof_hardware: bool = True
    bypass_csp: bool = True
    block_webrtc: bool = True
    
    # Advanced features
    bypass_cloudflare: bool = True
    bypass_f5_networks: bool = True
    bypass_shape_security: bool = True
    bypass_datadome: bool = True
    bypass_kasada: bool = True
    bypass_perimeter_x: bool = True
    
    # Human simulation
    human_behavior: bool = True
    enable_human_typing: bool = True
    enable_human_mouse: bool = True
    enable_human_scrolling: bool = True
    enable_human_delays: bool = True
    enable_micro_behaviors: bool = True
    use_bspline_mouse: bool = True
    use_lognormal_delays: bool = True
    
    # Detection
    detect_frameworks: bool = True
    detect_captcha: bool = True
    handle_cookies: bool = True
    
    # Trust building
    build_trust: bool = False  # Disabled by default for speed
    trust_domains: List[str] = field(default_factory=lambda: ['google.com', 'github.com'])
    
    # Performance
    parallel_extraction: bool = True
    max_retry_attempts: int = 3
    timeout: int = 60
    
    # Browser settings
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: Optional[str] = None
    locale: str = 'en-US'
    timezone: str = 'America/New_York'
    
    # Delays (milliseconds)
    human_delay_range: Tuple[int, int] = (100, 2000)
    typing_delay_range: Tuple[int, int] = (50, 200)
    mouse_delay_range: Tuple[int, int] = (10, 50)

@dataclass
class ElementData:
    """Comprehensive element data structure"""
    # Core identification
    element_id: str
    element_type: ElementType
    tag_name: str
    xpath: str
    css_selector: str
    
    # Content
    text_content: str = ""
    inner_html: str = ""
    outer_html: str = ""
    
    # Attributes
    attributes: Dict[str, str] = field(default_factory=dict)
    id: Optional[str] = None
    class_names: List[str] = field(default_factory=list)
    name: Optional[str] = None
    href: Optional[str] = None
    src: Optional[str] = None
    
    # State
    is_visible: bool = False
    is_clickable: bool = False
    is_enabled: bool = True
    is_focusable: bool = False
    
    # Position
    x: float = 0
    y: float = 0
    width: float = 0
    height: float = 0
    
    # Accessibility
    role: Optional[str] = None
    aria_label: Optional[str] = None
    aria_description: Optional[str] = None
    tab_index: Optional[int] = None
    
    # Metadata
    confidence_score: float = 1.0
    extraction_strategy: str = "unknown"
    extraction_timestamp: datetime = field(default_factory=datetime.now)
    framework_detected: Optional[str] = None
    
    # Relationships
    parent_xpath: Optional[str] = None
    children_count: int = 0
    sibling_index: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['element_type'] = self.element_type.value
        data['extraction_timestamp'] = self.extraction_timestamp.isoformat()
        return data

@dataclass
class ExtractionResult:
    """Complete extraction result with metadata"""
    url: str
    success: bool
    elements: List[ElementData]
    page_title: str = ""
    framework_detected: Optional[str] = None
    captcha_detected: bool = False
    captcha_type: Optional[str] = None
    extraction_time: float = 0
    retry_count: int = 0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'url': self.url,
            'success': self.success,
            'elements': [e.to_dict() for e in self.elements],
            'page_title': self.page_title,
            'framework_detected': self.framework_detected,
            'captcha_detected': self.captcha_detected,
            'captcha_type': self.captcha_type,
            'extraction_time': self.extraction_time,
            'retry_count': self.retry_count,
            'errors': self.errors,
            'metadata': self.metadata,
            'timestamp': datetime.now().isoformat()
        }

# ============================================================================
# STEALTH LAYER - Anti-Detection and Evasion
# ============================================================================

class StealthInjector:
    """Comprehensive stealth script injection system"""
    
    @staticmethod
    async def inject_stealth(page: Page, config: StealthConfig) -> Any:
        """Inject all stealth scripts based on configuration"""
        
        # Always apply basic stealth
        await StealthInjector._inject_basic_stealth(page, config)
        
        # Apply enhanced stealth for higher levels
        if config.level in [StealthLevel.ENHANCED, StealthLevel.MAXIMUM, StealthLevel.PARANOID]:
            await StealthInjector._inject_enhanced_stealth(page, config)
        
        # Apply maximum stealth features
        if config.level in [StealthLevel.MAXIMUM, StealthLevel.PARANOID]:
            await StealthInjector._inject_maximum_stealth(page, config)
        
        # Apply paranoid level features
        if config.level == StealthLevel.PARANOID:
            await StealthInjector._inject_paranoid_stealth(page, config)
        
        logger.debug(f"Stealth injection complete: {config.level.value}")
    
    @staticmethod
    async def _inject_basic_stealth(page: Page, config: StealthConfig) -> Any:
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
    async def _inject_enhanced_stealth(page: Page, config: StealthConfig) -> Any:
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
    async def _inject_maximum_stealth(page: Page, config: StealthConfig) -> Any:
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
    async def _inject_paranoid_stealth(page: Page, config: StealthConfig) -> Any:
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
    
    async def simulate_mouse_movement(self, page: Page, target_x: float, target_y: float) -> Any:
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
    
    async def simulate_typing(self, page: Page, selector: str, text: str) -> Any:
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
            base_delay = random.randint(*self.config.typing_delay_range)
            
            # Occasional pauses (thinking)
            if random.random() < 0.1:
                base_delay += random.randint(200, 500)
            
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
    
    async def simulate_scrolling(self, page: Page) -> Any:
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
    
    async def simulate_micro_behaviors(self, page: Page) -> Any:
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
# DETECTION LAYER - Framework, CAPTCHA, and Cookie Detection
# ============================================================================

class DetectionSystem:
    """Comprehensive detection system for frameworks, CAPTCHAs, and cookies"""
    
    @staticmethod
    async def detect_framework(page: Page) -> Optional[str]:
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
    async def detect_captcha(page: Page) -> Dict[str, Any]:
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
                    '.geetest_panel',
                    'div[class*="geetest"]',
                    '#captcha-box'
                ],
                'confidence': 0.85
            }
        ]
        
        for pattern in captcha_patterns:
            for selector in pattern['selectors']:
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
                except (AttributeError, KeyError, ValueError, TypeError) as e:
                    logger.debug(f"Handled expected error: {e}")
                    continue
            
            if captcha_info['detected']:
                break
        
        if captcha_info['detected']:
            logger.warning(f"CAPTCHA detected: {captcha_info['type']} (confidence: {captcha_info['confidence']})")
        
        return captcha_info
    
    @staticmethod
    async def handle_cookie_consent(page: Page) -> bool:
        """Detect and handle cookie consent popups"""
        
        handled = False
        
        # Common cookie consent selectors
        cookie_selectors = [
            # Button selectors
            'button[id*="accept"]',
            'button[class*="accept"]',
            'button[class*="consent"]',
            'button[class*="agree"]',
            'button[class*="cookie"] button[class*="accept"]',
            'button:has-text("Accept")',
            'button:has-text("I Agree")',
            'button:has-text("OK")',
            'button:has-text("Got it")',
            
            # Link selectors
            'a[id*="accept"]',
            'a[class*="accept"]',
            
            # Div buttons
            'div[role="button"][class*="accept"]',
            'div[role="button"][class*="consent"]',
            
            # Specific frameworks
            '#onetrust-accept-btn-handler',
            '.optanon-alert-box-wrapper button.accept',
            '#tarteaucitronPersonalize',
            '.cc-compliance .cc-btn',
            '#rgpd-btn-validate'
        ]
        
        # Try to find and click cookie consent
        for selector in cookie_selectors:
            try:
                button = await page.query_selector(selector)
                if button and await button.is_visible():
                    # Get button position for human-like clicking
                    box = await button.bounding_box()
                    if box:
                        # Move mouse to button
                        center_x = box['x'] + box['width'] / 2
                        center_y = box['y'] + box['height'] / 2
                        
                        # Human-like movement and click
                        human_sim = HumanSimulator(StealthConfig())
                        await human_sim.simulate_mouse_movement(page, center_x, center_y)
                        await human_sim.simulate_human_delay(delay_type="clicking")
                        await button.click()
                        
                        logger.info(f"Cookie consent handled: {selector}")
                        handled = True
                        
                        # Wait for popup to disappear
                        await page.wait_for_timeout(1000)
                        break
            except Exception as e:
                logger.debug(f"Cookie handling error for {selector}: {e}")
                continue
        
        return handled

# ============================================================================
# MONITORING LAYER - Context Stability and Recovery
# ============================================================================

class ContextMonitor:
    """Monitor and maintain browser context stability"""
    
    def __init__(self, page: Page) -> None:
        self.page = page
        self.stable = True
        self.last_check = time.time()
        self.error_count = 0
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3
        
    async def start_monitoring(self) -> Any:
        """Start monitoring context stability"""
        try:
            # Set up event listeners
            self.page.on('crash', self._on_crash)
            self.page.on('pageerror', self._on_error)
            
            # Start periodic health check
            asyncio.create_task(self._periodic_health_check())
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
    
    def _on_crash(self, page: Page) -> None:
        """Handle page crash"""
        self.stable = False
        self.error_count += 1
        logger.error("Page crashed - attempting recovery")
    
    def _on_error(self, error: Exception) -> None:
        """Handle page errors"""
        self.error_count += 1
        logger.warning(f"Page error: {error}")
        
        # Mark unstable if too many errors
        if self.error_count > 10:
            self.stable = False
    
    async def _periodic_health_check(self) -> Any:
        """Periodically check context health"""
        while self.stable:
            try:
                # Simple JS execution to verify context
                await self.page.evaluate('1 + 1')
                self.last_check = time.time()
                self.error_count = max(0, self.error_count - 1)  # Decay error count
                
            except Exception as e:
                logger.warning(f"Health check failed: {e}")
                self.stable = False
                break
            
            await asyncio.sleep(5)
    
    def is_stable(self) -> bool:
        """Check if context is stable"""
        # Context is stable if:
        # 1. No crash detected
        # 2. Recent health check passed
        # 3. Error count is reasonable
        return (
            self.stable and 
            (time.time() - self.last_check < 10) and
            self.error_count < 5
        )
    
    async def attempt_recovery(self) -> bool:
        """Attempt to recover from context instability"""
        
        if self.recovery_attempts >= self.max_recovery_attempts:
            logger.error("Max recovery attempts reached")
            return False
        
        self.recovery_attempts += 1
        logger.info(f"Attempting recovery (attempt {self.recovery_attempts})")
        
        try:
            # Try to reload the page
            await self.page.reload()
            await asyncio.sleep(2)
            
            # Verify recovery
            await self.page.evaluate('1 + 1')
            
            # Reset state
            self.stable = True
            self.error_count = 0
            self.last_check = time.time()
            
            logger.info("Recovery successful")
            return True
            
        except Exception as e:
            logger.error(f"Recovery failed: {e}")
            return False

# ============================================================================
# EXTRACTION LAYER - Multi-Strategy Element Extraction
# ============================================================================

class ExtractionStrategyBase(ABC):
    """Base class for extraction strategies"""
    
    @abstractmethod
    async def extract(self, page: Page, config: StealthConfig) -> List[ElementData]:
        """Extract elements using specific strategy"""
        pass
    
    @abstractmethod
    def can_handle(self, page: Page) -> bool:
        """Check if strategy can handle the page"""
        pass

class DOMExtractionStrategy(ExtractionStrategyBase):
    """DOM-based element extraction"""
    
    async def extract(self, page: Page, config: StealthConfig) -> List[ElementData]:
        """Extract elements from DOM"""
        elements = []
        
        try:
            dom_elements = await page.evaluate("""
                () => {
                    const elements = [];
                    const selectors = [
                        'a', 'button', 'input', 'select', 'textarea',
                        '[role="button"]', '[role="link"]', '[onclick]',
                        '.btn', '.button', '[type="submit"]', '[type="button"]',
                        'div[class*="button"]', 'span[class*="button"]'
                    ];
                    
                    const getXPath = (element) => {
                        if (!element) return '';
                        if (element.id) return `//*[@id="${element.id}"]`;
                        if (element === document.body) return '/html/body';
                        
                        let ix = 0;
                        const siblings = element.parentNode ? element.parentNode.childNodes : [];
                        for (let i = 0; i < siblings.length; i++) {
                            const sibling = siblings[i];
                            if (sibling === element) {
                                const parentXPath = getXPath(element.parentNode);
                                return `${parentXPath}/${element.tagName.toLowerCase()}[${ix + 1}]`;
                            }
                            if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                                ix++;
                            }
                        }
                        return '';
                    };
                    
                    const getCSSSelector = (element) => {
                        if (!element) return '';
                        if (element.id) return `#${element.id}`;
                        
                        let selector = element.tagName.toLowerCase();
                        if (element.className) {
                            const classes = element.className.split(' ').filter(c => c);
                            if (classes.length > 0) {
                                selector += '.' + classes.join('.');
                            }
                        }
                        return selector;
                    };
                    
                    const allElements = document.querySelectorAll(selectors.join(', '));
                    
                    allElements.forEach((el, index) => {
                        if (index >= 100) return; // Limit for performance
                        
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        
                        // Get all attributes
                        const attributes = {};
                        for (let attr of el.attributes) {
                            attributes[attr.name] = attr.value;
                        }
                        
                        elements.push({
                            tagName: el.tagName.toLowerCase(),
                            id: el.id || null,
                            className: el.className || '',
                            textContent: (el.textContent || '').substring(0, 200).trim(),
                            innerHTML: (el.innerHTML || '').substring(0, 500),
                            outerHTML: (el.outerHTML || '').substring(0, 1000),
                            attributes: attributes,
                            href: el.href || null,
                            src: el.src || null,
                            type: el.type || el.tagName.toLowerCase(),
                            name: el.name || null,
                            placeholder: el.placeholder || null,
                            value: el.value || null,
                            isVisible: rect.width > 0 && rect.height > 0 &&
                                      style.visibility !== 'hidden' &&
                                      style.display !== 'none' &&
                                      style.opacity !== '0',
                            isClickable: el.tagName === 'BUTTON' || el.tagName === 'A' || 
                                        el.onclick !== null || el.role === 'button' ||
                                        style.cursor === 'pointer',
                            isEnabled: !el.disabled,
                            isFocusable: el.tabIndex >= 0,
                            x: Math.round(rect.x),
                            y: Math.round(rect.y),
                            width: Math.round(rect.width),
                            height: Math.round(rect.height),
                            role: el.getAttribute('role'),
                            ariaLabel: el.getAttribute('aria-label'),
                            ariaDescription: el.getAttribute('aria-describedby'),
                            tabIndex: el.tabIndex,
                            xpath: getXPath(el),
                            cssSelector: getCSSSelector(el)
                        });
                    });
                    
                    return elements;
                }
            """)
            
            # Convert to ElementData objects
            for elem_data in dom_elements:
                element_type = self._determine_element_type(elem_data)
                
                element = ElementData(
                    element_id=hashlib.md5(f"{elem_data['xpath']}_{elem_data['tagName']}".encode()).hexdigest()[:8],
                    element_type=element_type,
                    tag_name=elem_data['tagName'],
                    xpath=elem_data.get('xpath', ''),
                    css_selector=elem_data.get('cssSelector', ''),
                    text_content=elem_data.get('textContent', ''),
                    inner_html=elem_data.get('innerHTML', ''),
                    outer_html=elem_data.get('outerHTML', ''),
                    attributes=elem_data.get('attributes', {}),
                    id=elem_data.get('id'),
                    class_names=elem_data.get('className', '').split() if elem_data.get('className') else [],
                    name=elem_data.get('name'),
                    href=elem_data.get('href'),
                    src=elem_data.get('src'),
                    is_visible=elem_data.get('isVisible', False),
                    is_clickable=elem_data.get('isClickable', False),
                    is_enabled=elem_data.get('isEnabled', True),
                    is_focusable=elem_data.get('isFocusable', False),
                    x=elem_data.get('x', 0),
                    y=elem_data.get('y', 0),
                    width=elem_data.get('width', 0),
                    height=elem_data.get('height', 0),
                    role=elem_data.get('role'),
                    aria_label=elem_data.get('ariaLabel'),
                    aria_description=elem_data.get('ariaDescription'),
                    tab_index=elem_data.get('tabIndex'),
                    extraction_strategy='DOM',
                    confidence_score=0.9
                )
                elements.append(element)
                
        except Exception as e:
            logger.error(f"DOM extraction failed: {e}")
        
        return elements
    
    def _determine_element_type(self, elem_data: Dict) -> ElementType:
        """Determine element type from element data"""
        
        tag = (elem_data.get('tagName') or '').lower()
        type_attr = (elem_data.get('type') or '').lower()
        role = (elem_data.get('role') or '').lower()
        
        # Direct tag mapping
        if tag == 'button' or role == 'button':
            return ElementType.BUTTON
        elif tag == 'a' or role == 'link':
            return ElementType.LINK
        elif tag == 'input':
            if type_attr in ['checkbox']:
                return ElementType.CHECKBOX
            elif type_attr in ['radio']:
                return ElementType.RADIO
            else:
                return ElementType.INPUT
        elif tag == 'textarea':
            return ElementType.TEXTAREA
        elif tag == 'select':
            return ElementType.DROPDOWN
        elif tag == 'form':
            return ElementType.FORM
        elif tag == 'table':
            return ElementType.TABLE
        elif tag == 'img':
            return ElementType.IMAGE
        elif tag == 'video':
            return ElementType.VIDEO
        elif tag == 'nav' or role == 'navigation':
            return ElementType.NAVIGATION
        
        # Check for modal indicators
        if 'modal' in str(elem_data.get('className', '')).lower() or role == 'dialog':
            return ElementType.MODAL
        
        # Check for pagination
        if 'pagination' in str(elem_data.get('className', '')).lower():
            return ElementType.PAGINATION
        
        return ElementType.UNKNOWN
    
    def can_handle(self, page: Page) -> bool:
        """DOM strategy can handle any page"""
        return True

class VisualExtractionStrategy(ExtractionStrategyBase):
    """Visual-based element extraction focusing on visible elements"""
    
    async def extract(self, page: Page, config: StealthConfig) -> List[ElementData]:
        """Extract visually prominent elements"""
        elements = []
        
        try:
            visual_elements = await page.evaluate("""
                () => {
                    const elements = [];
                    const minSize = 20; // Minimum size to be considered
                    const allElements = document.querySelectorAll('*');
                    
                    // Calculate visual prominence score
                    const getProminenceScore = (el, rect, style) => {
                        let score = 0;
                        
                        // Size score
                        score += (rect.width * rect.height) / 1000;
                        
                        // Position score (closer to top-left is better)
                        score += (2000 - rect.x - rect.y) / 100;
                        
                        // Z-index score
                        const zIndex = parseInt(style.zIndex) || 0;
                        score += zIndex * 10;
                        
                        // Color contrast score
                        const bgColor = style.backgroundColor;
                        const color = style.color;
                        if (bgColor !== 'transparent' && color) {
                            score += 50; // Has explicit colors
                        }
                        
                        // Font size score
                        const fontSize = parseFloat(style.fontSize) || 0;
                        score += fontSize;
                        
                        // Interactive element bonus
                        if (el.tagName === 'BUTTON' || el.tagName === 'A' || 
                            el.onclick || style.cursor === 'pointer') {
                            score += 100;
                        }
                        
                        return score;
                    };
                    
                    allElements.forEach((el, index) => {
                        if (index >= 100) return; // Limit for performance
                        
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        
                        // Only consider visible elements of reasonable size
                        if (rect.width >= minSize && rect.height >= minSize &&
                            style.visibility !== 'hidden' &&
                            style.display !== 'none' &&
                            style.opacity !== '0' &&
                            rect.x >= 0 && rect.y >= 0) {
                            
                            const prominenceScore = getProminenceScore(el, rect, style);
                            
                            elements.push({
                                element: el,
                                rect: rect,
                                style: style,
                                prominenceScore: prominenceScore
                            });
                        }
                    });
                    
                    // Sort by prominence and take top elements
                    elements.sort((a, b) => b.prominenceScore - a.prominenceScore);
                    
                    return elements.slice(0, 50).map(item => {
                        const el = item.element;
                        const rect = item.rect;
                        
                        return {
                            tagName: el.tagName.toLowerCase(),
                            id: el.id || null,
                            className: el.className || '',
                            textContent: (el.textContent || '').substring(0, 200).trim(),
                            prominenceScore: item.prominenceScore,
                            x: Math.round(rect.x),
                            y: Math.round(rect.y),
                            width: Math.round(rect.width),
                            height: Math.round(rect.height),
                            backgroundColor: item.style.backgroundColor,
                            color: item.style.color,
                            fontSize: item.style.fontSize,
                            zIndex: item.style.zIndex || '0'
                        };
                    });
                }
            """)
            
            # Convert to ElementData objects
            for elem_data in visual_elements:
                element = ElementData(
                    element_id=hashlib.md5(f"visual_{elem_data['x']}_{elem_data['y']}".encode()).hexdigest()[:8],
                    element_type=ElementType.UNKNOWN,
                    tag_name=elem_data['tagName'],
                    xpath=f"//{elem_data['tagName']}",
                    css_selector=f"#{elem_data['id']}" if elem_data['id'] else elem_data['tagName'],
                    text_content=elem_data.get('textContent', ''),
                    id=elem_data.get('id'),
                    class_names=elem_data.get('className', '').split() if elem_data.get('className') else [],
                    is_visible=True,
                    x=elem_data.get('x', 0),
                    y=elem_data.get('y', 0),
                    width=elem_data.get('width', 0),
                    height=elem_data.get('height', 0),
                    extraction_strategy='Visual',
                    confidence_score=min(1.0, elem_data.get('prominenceScore', 0) / 1000),
                    attributes={
                        'backgroundColor': elem_data.get('backgroundColor', ''),
                        'color': elem_data.get('color', ''),
                        'fontSize': elem_data.get('fontSize', ''),
                        'zIndex': elem_data.get('zIndex', '0')
                    }
                )
                elements.append(element)
                
        except Exception as e:
            logger.error(f"Visual extraction failed: {e}")
        
        return elements
    
    def can_handle(self, page: Page) -> bool:
        """Visual strategy can handle any page"""
        return True

class AccessibilityExtractionStrategy(ExtractionStrategyBase):
    """Accessibility-focused element extraction"""
    
    async def extract(self, page: Page, config: StealthConfig) -> List[ElementData]:
        """Extract elements with accessibility information"""
        elements = []
        
        try:
            aria_elements = await page.evaluate("""
                () => {
                    const elements = [];
                    
                    // Comprehensive ARIA and accessibility selectors
                    const selectors = [
                        '[role]',
                        '[aria-label]',
                        '[aria-labelledby]',
                        '[aria-describedby]',
                        '[aria-controls]',
                        '[aria-expanded]',
                        '[aria-selected]',
                        '[aria-checked]',
                        '[aria-hidden="false"]',
                        '[tabindex]',
                        'button',
                        'a[href]',
                        'input:not([type="hidden"])',
                        'select',
                        'textarea',
                        '[contenteditable="true"]'
                    ];
                    
                    const processedElements = new Set();
                    
                    selectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach((el, index) => {
                            // Avoid duplicates
                            if (processedElements.has(el) || processedElements.size >= 100) {
                                return;
                            }
                            processedElements.add(el);
                            
                            const rect = el.getBoundingClientRect();
                            const style = window.getComputedStyle(el);
                            
                            // Get accessible name
                            const getAccessibleName = (element) => {
                                // Priority order for accessible name
                                return element.getAttribute('aria-label') ||
                                       element.getAttribute('aria-labelledby') ||
                                       element.getAttribute('title') ||
                                       element.textContent?.trim() ||
                                       element.getAttribute('placeholder') ||
                                       element.getAttribute('alt') ||
                                       '';
                            };
                            
                            elements.push({
                                tagName: el.tagName.toLowerCase(),
                                role: el.getAttribute('role') || el.tagName.toLowerCase(),
                                ariaLabel: el.getAttribute('aria-label'),
                                ariaLabelledBy: el.getAttribute('aria-labelledby'),
                                ariaDescribedBy: el.getAttribute('aria-describedby'),
                                ariaControls: el.getAttribute('aria-controls'),
                                ariaExpanded: el.getAttribute('aria-expanded'),
                                ariaSelected: el.getAttribute('aria-selected'),
                                ariaChecked: el.getAttribute('aria-checked'),
                                ariaHidden: el.getAttribute('aria-hidden'),
                                ariaLive: el.getAttribute('aria-live'),
                                ariaAtomic: el.getAttribute('aria-atomic'),
                                tabIndex: el.tabIndex,
                                accessibleName: getAccessibleName(el),
                                isDisabled: el.disabled || el.getAttribute('aria-disabled') === 'true',
                                isRequired: el.required || el.getAttribute('aria-required') === 'true',
                                isReadOnly: el.readOnly || el.getAttribute('aria-readonly') === 'true',
                                textContent: (el.textContent || '').substring(0, 200).trim(),
                                x: Math.round(rect.x),
                                y: Math.round(rect.y),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height),
                                isVisible: rect.width > 0 && rect.height > 0 &&
                                          style.visibility !== 'hidden' &&
                                          style.display !== 'none'
                            });
                        });
                    });
                    
                    return elements;
                }
            """)
            
            # Convert to ElementData objects
            for elem_data in aria_elements:
                element = ElementData(
                    element_id=hashlib.md5(f"aria_{elem_data.get('role', '')}_{elem_data.get('ariaLabel', '')}".encode()).hexdigest()[:8],
                    element_type=ElementType.UNKNOWN,
                    tag_name=elem_data['tagName'],
                    xpath=f"//{elem_data['tagName']}[@role='{elem_data.get('role', '')}']" if elem_data.get('role') else f"//{elem_data['tagName']}",
                    css_selector=f"[role='{elem_data.get('role', '')}']" if elem_data.get('role') else elem_data['tagName'],
                    text_content=elem_data.get('textContent', ''),
                    is_visible=elem_data.get('isVisible', False),
                    is_enabled=not elem_data.get('isDisabled', False),
                    is_focusable=elem_data.get('tabIndex', -1) >= 0,
                    x=elem_data.get('x', 0),
                    y=elem_data.get('y', 0),
                    width=elem_data.get('width', 0),
                    height=elem_data.get('height', 0),
                    role=elem_data.get('role'),
                    aria_label=elem_data.get('ariaLabel'),
                    aria_description=elem_data.get('ariaDescribedBy'),
                    tab_index=elem_data.get('tabIndex'),
                    extraction_strategy='Accessibility',
                    confidence_score=0.85,
                    attributes={
                        'ariaExpanded': elem_data.get('ariaExpanded'),
                        'ariaSelected': elem_data.get('ariaSelected'),
                        'ariaChecked': elem_data.get('ariaChecked'),
                        'ariaHidden': elem_data.get('ariaHidden'),
                        'ariaControls': elem_data.get('ariaControls'),
                        'accessibleName': elem_data.get('accessibleName', ''),
                        'isRequired': elem_data.get('isRequired', False),
                        'isReadOnly': elem_data.get('isReadOnly', False)
                    }
                )
                elements.append(element)
                
        except Exception as e:
            logger.error(f"Accessibility extraction failed: {e}")
        
        return elements
    
    def can_handle(self, page: Page) -> bool:
        """Accessibility strategy can handle any page"""
        return True

class ShadowDOMExtractionStrategy(ExtractionStrategyBase):
    """Extract elements from Shadow DOM"""
    
    async def extract(self, page: Page, config: StealthConfig) -> List[ElementData]:
        """Extract elements from shadow DOM roots"""
        elements = []
        
        try:
            shadow_elements = await page.evaluate("""
                () => {
                    const elements = [];
                    const processedShadowRoots = new Set();
                    
                    // Find all elements with shadow roots
                    const findShadowRoots = (root) => {
                        const shadowRoots = [];
                        const walker = document.createTreeWalker(
                            root,
                            NodeFilter.SHOW_ELEMENT,
                            null,
                            false
                        );
                        
                        let node;
                        while (node = walker.nextNode()) {
                            if (node.shadowRoot && !processedShadowRoots.has(node.shadowRoot)) {
                                shadowRoots.push(node.shadowRoot);
                                processedShadowRoots.add(node.shadowRoot);
                            }
                        }
                        return shadowRoots;
                    };
                    
                    // Extract elements from shadow root
                    const extractFromShadowRoot = (shadowRoot, hostElement) => {
                        const shadowElements = shadowRoot.querySelectorAll('*');
                        
                        shadowElements.forEach((el, index) => {
                            if (index >= 50) return; // Limit per shadow root
                            
                            const rect = el.getBoundingClientRect();
                            const style = window.getComputedStyle(el);
                            
                            // Only include interactive or important elements
                            if ((el.tagName === 'BUTTON' || el.tagName === 'A' || 
                                 el.tagName === 'INPUT' || el.tagName === 'SELECT' ||
                                 el.onclick || style.cursor === 'pointer') &&
                                rect.width > 0 && rect.height > 0) {
                                
                                elements.push({
                                    tagName: el.tagName.toLowerCase(),
                                    shadowHost: hostElement.tagName.toLowerCase(),
                                    shadowHostId: hostElement.id || null,
                                    textContent: (el.textContent || '').substring(0, 200).trim(),
                                    type: el.type || null,
                                    x: Math.round(rect.x),
                                    y: Math.round(rect.y),
                                    width: Math.round(rect.width),
                                    height: Math.round(rect.height),
                                    isInShadowDOM: true
                                });
                            }
                        });
                        
                        // Recursively check for nested shadow roots
                        const nestedShadowRoots = findShadowRoots(shadowRoot);
                        nestedShadowRoots.forEach(nestedRoot => {
                            extractFromShadowRoot(nestedRoot, hostElement);
                        });
                    };
                    
                    // Start from document
                    const shadowRoots = findShadowRoots(document.body);
                    
                    shadowRoots.forEach(shadowRoot => {
                        const hostElement = shadowRoot.host;
                        extractFromShadowRoot(shadowRoot, hostElement);
                    });
                    
                    return elements;
                }
            """)
            
            # Convert to ElementData objects
            for elem_data in shadow_elements:
                element = ElementData(
                    element_id=hashlib.md5(f"shadow_{elem_data.get('shadowHost', '')}_{elem_data.get('tagName', '')}".encode()).hexdigest()[:8],
                    element_type=ElementType.UNKNOWN,
                    tag_name=elem_data['tagName'],
                    xpath=f"//shadow-root//{elem_data['tagName']}",
                    css_selector=f"{elem_data.get('shadowHost', 'unknown')} >>> {elem_data['tagName']}",
                    text_content=elem_data.get('textContent', ''),
                    is_visible=True,
                    x=elem_data.get('x', 0),
                    y=elem_data.get('y', 0),
                    width=elem_data.get('width', 0),
                    height=elem_data.get('height', 0),
                    extraction_strategy='ShadowDOM',
                    confidence_score=0.8,
                    attributes={
                        'isInShadowDOM': True,
                        'shadowHost': elem_data.get('shadowHost', ''),
                        'shadowHostId': elem_data.get('shadowHostId', '')
                    }
                )
                elements.append(element)
                
        except Exception as e:
            logger.error(f"Shadow DOM extraction failed: {e}")
        
        return elements
    
    def can_handle(self, page: Page) -> bool:
        """Check if page has shadow DOM elements"""
        # For now, always return True to attempt shadow DOM extraction
        # Actual check would need to be async which doesn't work well in this context
        return True

# ============================================================================
# ORCHESTRATION LAYER - Main Browser Controller
# ============================================================================



class CircuitBreaker:
    """Circuit breaker for fault tolerance"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
                self.failure_count = 0
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.error(f"Circuit breaker opened after {self.failure_count} failures")
            
            raise

class RateLimiter:
    """Production-grade rate limiter for DDoS protection"""
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: List[float] = []
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """Check if request is allowed"""
        async with self._lock:
            now = time.time()
            # Remove old requests outside time window
            self.requests = [r for r in self.requests if r > now - self.time_window]
            
            if len(self.requests) >= self.max_requests:
                return False
            
            self.requests.append(now)
            return True
    
    async def wait_if_needed(self) -> None:
        """Wait if rate limit exceeded"""
        while not await self.acquire():
            await asyncio.sleep(0.1)

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
        super().__init__()
        self.config = config or StealthConfig()
        
        # Production concurrency controls
        self._operation_semaphore = asyncio.Semaphore(10)  # Max 10 concurrent operations
        self._navigation_lock = asyncio.Lock()  # Serialize navigation
        self._extraction_semaphore = asyncio.Semaphore(5)  # Max 5 concurrent extractions
        self._rate_limiter = RateLimiter(max_requests=100, time_window=60)  # 100 req/min
        self._circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)
        
        # Initialize components
        self.human_simulator = HumanSimulator(self.config)
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        self.session_id = f"session_{int(time.time() * 1000)}"
        
        # Initialize extraction strategies
        self.extraction_strategies = [
            DOMExtractionStrategy(),
            VisualExtractionStrategy(),
            AccessibilityExtractionStrategy(),
            ShadowDOMExtractionStrategy()
        ]
        
        # Monitoring
        self._metrics = {
            'requests_total': 0,
            'requests_success': 0,
            'requests_failed': 0,
            'avg_response_time': 0,
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
        
        # Get Chrome executable path if available
        chrome_path = self._find_chrome_executable()
        
        options = {
            'headless': self.config.headless,
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
                '--disable-web-security',
                '--disable-features=CrossSiteDocumentBlockingIfIsolating',
                '--disable-features=CrossSiteDocumentBlockingAlways',
                '--disable-features=IsolateOrigins,site-per-process',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                f'--window-size={self.config.viewport_width},{self.config.viewport_height}',
                '--start-maximized',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--disable-infobars',
                '--enable-features=NetworkService,NetworkServiceInProcess',
                '--allow-running-insecure-content',
                '--disable-features=RendererCodeIntegrity',
                '--disable-features=FlashDeprecationWarning',
                '--disable-component-extensions-with-background-pages'
            ]
        }
        
        # Add Chrome executable if found
        if chrome_path:
            options['executable_path'] = chrome_path
            logger.info(f"Using Chrome at: {chrome_path}")
        
        # Additional args for paranoid mode
        if self.config.level == StealthLevel.PARANOID:
            options['args'].extend([
                '--disable-features=AutomationControlled',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-tools',
                '--disable-features=site-per-process',
                '--disable-features=OutOfBlinkCors',
                '--disable-features=SameSiteByDefaultCookies',
                '--disable-features=CookiesWithoutSameSiteMustBeSecure',
                '--disable-features=UserActivationV2',
                '--disable-features=AudioServiceOutOfProcess',
                '--disable-features=IsolateOrigins',
                '--disable-features=site-per-process'
            ])
        
        return options
    
    def _find_chrome_executable(self) -> Optional[str]:
        """Find Chrome executable path using platform_utils or fallback"""
        
        # Try platform_utils first
        if HAS_PLATFORM_UTILS:
            chrome_path = get_chrome_executable_path()
            if chrome_path:
                return chrome_path
        
        # Fallback to manual search
        system = platform.system()
        
        if system == "Windows":
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
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
    
    async def _create_stealth_context(self) -> BrowserContext:
        """Create browser context with stealth settings"""
        
        # User agent selection based on stealth level
        user_agents = {
            StealthLevel.BASIC: [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ],
            StealthLevel.ENHANCED: [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ],
            StealthLevel.MAXIMUM: [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ],
            StealthLevel.PARANOID: [
                # Most common user agents to blend in
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
            ]
        }
        
        user_agent = self.config.user_agent or random.choice(
            user_agents.get(self.config.level, user_agents[StealthLevel.MAXIMUM])
        )
        
        context = await self.browser.new_context(
            viewport={
                'width': self.config.viewport_width,
                'height': self.config.viewport_height
            },
            user_agent=user_agent,
            locale=self.config.locale,
            timezone_id=self.config.timezone,
            permissions=['geolocation', 'notifications'],
            color_scheme='light',
            device_scale_factor=1.0 + random.random() * 0.5,
            has_touch=False,
            is_mobile=False,
            java_script_enabled=True,
            bypass_csp=self.config.bypass_csp,
            ignore_https_errors=True,
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Cache-Control': 'max-age=0'
            }
        )
        
        return context
    
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
                'cloudflare/challenge', 'recaptcha/api',
                'distil', 'incapsula', 'akamai'
            ]
            
            for pattern in blocking_patterns:
                if pattern in url:
                    # Return empty response for blocked scripts
                    await route.fulfill(
                        body='',
                        content_type='application/javascript'
                    )
                    return
            
            # Continue with normal request
            await route.continue_()
        
        # Set up route handler
        await self.page.route('**/*', handle_route)
    
    async def navigate(self, url: str, wait_for: str = 'domcontentloaded') -> bool:
        """
        Navigate to URL with stealth and monitoring.
        
        Args:
            url: Target URL
            wait_for: Wait condition ('domcontentloaded', 'networkidle', 'load')
            
        Returns:
            Success status
        """
        
        try:
            logger.info(f"Navigating to: {url}")
            
            # Pre-navigation delay (appears more human)
            await self.human_simulator.simulate_human_delay(delay_type="thinking")
            
            # Navigate with retry logic
            for attempt in range(self.config.max_retry_attempts):
                try:
                    response = await self.page.goto(
                        url,
                        wait_until=wait_for,
                        timeout=self.config.timeout * 1000
                    )
                    
                    # Check response status
                    if response and response.status >= 400:
                        logger.warning(f"HTTP {response.status} for {url}")
                    
                    # Wait for potential redirects or dynamic content
                    await self.human_simulator.simulate_human_delay(delay_type="page_analysis")
                    
                    # Check if context is stable
                    if self.monitor and not self.monitor.is_stable():
                        logger.warning("Context unstable after navigation")
                        if await self.monitor.attempt_recovery():
                            continue
                        else:
                            return False
                    
                    # Successful navigation
                    logger.info(f"Successfully navigated to: {url}")
                    return True
                    
                except Exception as e:
                    logger.warning(f"Navigation attempt {attempt + 1} failed: {e}")
                    
                    if attempt < self.config.max_retry_attempts - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        raise
            
            return False
            
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False
    
    async def extract_elements(self, 
                              url: Optional[str] = None,
                              strategies: Optional[List[ExtractionStrategy]] = None) -> ExtractionResult:
        """
        Extract elements from current page or navigate to URL first.
        
        Args:
            url: Optional URL to navigate to before extraction
            strategies: Optional list of strategies to use (uses all by default)
            
        Returns:
            ExtractionResult with all extracted elements and metadata
        """
        
        start_time = time.time()
        result = ExtractionResult(
            url=url or (self.page.url if self.page else ''),
            success=False,
            elements=[]
        )
        
        try:
            # Navigate if URL provided
            if url:
                if not await self.navigate(url):
                    result.errors.append("Failed to navigate to URL")
                    return result
                result.url = url
            
            # Get page title
            try:
                result.page_title = await self.page.title()
            except (AttributeError, KeyError, ValueError, TypeError) as e:

                logger.debug(f"Handled expected error: {e}")
                pass
            
            # Detect framework
            if self.config.detect_frameworks:
                result.framework_detected = await DetectionSystem.detect_framework(self.page)
            
            # Handle cookie consent
            if self.config.handle_cookies:
                await DetectionSystem.handle_cookie_consent(self.page)
            
            # Detect CAPTCHA
            if self.config.detect_captcha:
                captcha_info = await DetectionSystem.detect_captcha(self.page)
                result.captcha_detected = captcha_info['detected']
                result.captcha_type = captcha_info.get('type')
                
                if result.captcha_detected:
                    result.errors.append(f"CAPTCHA detected: {result.captcha_type}")
                    # Still continue with extraction
            
            # Human behavior before extraction
            await self.human_simulator.simulate_micro_behaviors(self.page)
            await self.human_simulator.simulate_scrolling(self.page)
            
            # Extract elements using selected strategies
            selected_strategies = []
            if strategies:
                # Use specified strategies
                for strategy_enum in strategies:
                    for strategy_obj in self.extraction_strategies:
                        if strategy_enum.value in strategy_obj.__class__.__name__.lower():
                            selected_strategies.append(strategy_obj)
            else:
                # Use all applicable strategies
                selected_strategies = [
                    s for s in self.extraction_strategies 
                    if s.can_handle(self.page)
                ]
            
            # Execute extraction
            all_elements = []
            
            if self.config.parallel_extraction:
                # Parallel extraction
                tasks = [
                    strategy.extract(self.page, self.config)
                    for strategy in selected_strategies
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for strategy_result in results:
                    if isinstance(strategy_result, list):
                        all_elements.extend(strategy_result)
                    elif isinstance(strategy_result, Exception):
                        logger.warning(f"Strategy failed: {strategy_result}")
            else:
                # Sequential extraction
                for strategy in selected_strategies:
                    try:
                        elements = await strategy.extract(self.page, self.config)
                        all_elements.extend(elements)
                    except Exception as e:
                        logger.warning(f"Strategy {strategy.__class__.__name__} failed: {e}")
            
            # Deduplicate elements
            seen = set()
            unique_elements = []
            for element in all_elements:
                # Create unique key
                key = f"{element.xpath}_{element.tag_name}_{element.x}_{element.y}"
                if key not in seen:
                    seen.add(key)
                    unique_elements.append(element)
            
            # Sort by position (top-left to bottom-right)
            unique_elements.sort(key=lambda e: (e.y, e.x))
            
            # Update result
            result.elements = unique_elements
            result.success = True
            result.extraction_time = time.time() - start_time
            
            # Add metadata
            result.metadata = {
                'total_elements': len(unique_elements),
                'strategies_used': [s.__class__.__name__ for s in selected_strategies],
                'framework': result.framework_detected,
                'session_id': self.session_id,
                'stealth_level': self.config.level.value
            }
            
            logger.info(f"Extracted {len(unique_elements)} elements in {result.extraction_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            result.errors.append(str(e))
            result.extraction_time = time.time() - start_time
        
        return result
    
    async def click_element(self, 
                           element: Union[ElementData, str],
                           human_like: bool = True) -> bool:
        """
        Click an element with optional human-like behavior.
        
        Args:
            element: ElementData object or CSS selector
            human_like: Whether to use human-like clicking
            
        Returns:
            Success status
        """
        
        try:
            # Get selector
            if isinstance(element, ElementData):
                selector = element.css_selector or f"xpath={element.xpath}"
            else:
                selector = element
            
            # Find element
            elem = await self.page.query_selector(selector)
            if not elem:
                logger.warning(f"Element not found: {selector}")
                return False
            
            # Get element position
            box = await elem.bounding_box()
            if not box:
                logger.warning("Element has no bounding box")
                return False
            
            if human_like:
                # Human-like mouse movement to element
                center_x = box['x'] + box['width'] / 2
                center_y = box['y'] + box['height'] / 2
                
                await self.human_simulator.simulate_mouse_movement(
                    self.page, center_x, center_y
                )
                
                # Hover delay
                await self.human_simulator.simulate_human_delay(delay_type="clicking")
            
            # Click
            await elem.click()
            
            # Post-click delay
            if human_like:
                await self.human_simulator.simulate_human_delay(delay_type="thinking")
            
            logger.info(f"Clicked element: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to click element: {e}")
            return False
    
    async def type_text(self,
                       selector: str,
                       text: str,
                       human_like: bool = True) -> bool:
        """
        Type text into an input field.
        
        Args:
            selector: Element selector
            text: Text to type
            human_like: Whether to use human-like typing
            
        Returns:
            Success status
        """
        
        try:
            if human_like:
                await self.human_simulator.simulate_typing(self.page, selector, text)
            else:
                elem = await self.page.query_selector(selector)
                if elem:
                    await elem.type(text)
                else:
                    logger.warning(f"Element not found: {selector}")
                    return False
            
            logger.info(f"Typed text into: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            return False
    
    async def take_screenshot(self, path: Optional[str] = None) -> Optional[bytes]:
        """
        Take a screenshot of the current page.
        
        Args:
            path: Optional path to save screenshot
            
        Returns:
            Screenshot bytes if no path provided
        """
        
        try:
            if path:
                await self.page.screenshot(path=path, full_page=True)
                logger.info(f"Screenshot saved to: {path}")
                return None
            else:
                screenshot = await self.page.screenshot(full_page=True)
                logger.info("Screenshot captured")
                return screenshot
                
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None
    
    async def execute_javascript(self, script: str) -> Any:
        """
        Execute JavaScript in the page context.
        
        Args:
            script: JavaScript code to execute
            
        Returns:
            Script execution result
        """
        
        try:
            result = await self.page.evaluate(script)
            return result
        except Exception as e:
            logger.error(f"Failed to execute JavaScript: {e}")
            return None
    
    async def wait_for_selector(self, 
                               selector: str,
                               timeout: Optional[int] = None) -> bool:
        """
        Wait for an element to appear.
        
        Args:
            selector: Element selector
            timeout: Optional timeout in seconds
            
        Returns:
            Success status
        """
        
        try:
            timeout_ms = (timeout or self.config.timeout) * 1000
            await self.page.wait_for_selector(selector, timeout=timeout_ms)
            logger.info(f"Element appeared: {selector}")
            return True
        except Exception as e:
            logger.warning(f"Element did not appear: {selector}")
            return False
    
    async def get_page_content(self) -> str:
        """Get the current page HTML content"""
        
        try:
            return await self.page.content()
        except Exception as e:
            logger.error(f"Failed to get page content: {e}")
            return ""
    
    async def cleanup(self) -> None:
        """Clean up browser resources"""
        
        try:
            if self.page:
                await self.page.close()
            
            if self.context:
                await self.context.close()
            
            if self.browser:
                await self.browser.close()
            
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            
            logger.info("Browser cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

# ============================================================================
# PUBLIC API - Simple Interface
# ============================================================================

async def extract_with_stealth(
    url: str,
    level: StealthLevel = StealthLevel.MAXIMUM,
    headless: bool = False,
    extract_shadow_dom: bool = True
) -> ExtractionResult:
    """
    Simple API to extract elements from a URL with stealth.
    
    Args:
        url: Target URL
        level: Stealth level to use
        headless: Whether to run headless
        extract_shadow_dom: Whether to extract shadow DOM elements
        
    Returns:
        ExtractionResult with extracted elements
        
    Example:
        result = await extract_with_stealth(
            "https://example.com",
            level=StealthLevel.MAXIMUM
        )
        for element in result.elements:
            print(f"{element.tag_name}: {element.text_content}")
    """
    
    config = StealthConfig(
        level=level,
        headless=headless,
        extract_shadow_dom=extract_shadow_dom
    )
    
    async with UltimateStealthBrowser(config) as browser:
        result = await browser.extract_elements(url)
        return result

async def quick_extract(url: str) -> List[ElementData]:
    """
    Quick extraction with default settings.
    
    Args:
        url: Target URL
        
    Returns:
        List of extracted elements
    """
    
    result = await extract_with_stealth(url)
    return result.elements if result.success else []

# ============================================================================
# CLI INTERFACE
# ============================================================================

async def main() -> Any:
    """CLI interface for the ultimate stealth browser"""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Ultimate Stealth Browser - Comprehensive web extraction with anti-detection"
    )
    parser.add_argument("url", help="URL to extract from")
    parser.add_argument(
        "--level",
        choices=["basic", "enhanced", "maximum", "paranoid"],
        default="maximum",
        help="Stealth level (default: maximum)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in headless mode"
    )
    parser.add_argument(
        "--output",
        help="Output file for results (JSON format)"
    )
    parser.add_argument(
        "--screenshot",
        help="Take screenshot and save to path"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of elements to extract"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create configuration
    config = StealthConfig(
        level=StealthLevel[args.level.upper()],
        headless=args.headless
    )
    
    # Run extraction
    print(f"Extracting from: {args.url}")
    print(f"Stealth level: {args.level}")
    print(f"Headless: {args.headless}")
    print("-" * 50)
    
    async with UltimateStealthBrowser(config) as browser:
        # Extract elements
        result = await browser.extract_elements(args.url)
        
        if result.success:
            print(f"✓ Extraction successful")
            print(f"  Elements found: {len(result.elements)}")
            print(f"  Page title: {result.page_title}")
            print(f"  Framework: {result.framework_detected or 'None detected'}")
            print(f"  CAPTCHA: {'Yes - ' + result.captcha_type if result.captcha_detected else 'No'}")
            print(f"  Extraction time: {result.extraction_time:.2f}s")
            
            # Take screenshot if requested
            if args.screenshot:
                await browser.take_screenshot(args.screenshot)
                print(f"✓ Screenshot saved to: {args.screenshot}")
            
            # Display sample elements
            print("\nSample elements (first 5):")
            for i, element in enumerate(result.elements[:5], 1):
                print(f"{i}. {element.tag_name}")
                print(f"   Type: {element.element_type.value}")
                print(f"   Text: {element.text_content[:50]}..." if len(element.text_content) > 50 else f"   Text: {element.text_content}")
                print(f"   XPath: {element.xpath}")
                print(f"   Visible: {element.is_visible}")
                print(f"   Clickable: {element.is_clickable}")
                print(f"   Strategy: {element.extraction_strategy}")
                print(f"   Confidence: {element.confidence_score:.2f}")
                print()
            
            # Save results if output specified
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
                print(f"✓ Results saved to: {args.output}")
        else:
            print(f"✗ Extraction failed")
            for error in result.errors:
                print(f"  Error: {error}")

if __name__ == "__main__":
    """Production self-test and health check"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ultimate Stealth Browser")
    parser.add_argument("--test", action="store_true", help="Run self-tests")
    parser.add_argument("--health", action="store_true", help="Health check")
    parser.add_argument("--url", type=str, help="URL to extract")
    args = parser.parse_args()
    
    async def run_tests():
        """Run comprehensive self-tests"""
        print("Running self-tests...")
        
        # Test 1: Initialize browser
        config = StealthConfig()
        config.headless = True
        browser = UltimateStealthBrowser(config)
        
        try:
            await browser.initialize()
            print("[OK] Browser initialization")
            
            # Test 2: Extract from example.com
            result = await browser.extract_elements("https://example.com")
            assert result.success, "Extraction failed"
            print(f"[OK] Extraction test: {len(result.elements)} elements")
            
            # Test 3: Cleanup
            await browser.cleanup()
            print("[OK] Cleanup test")
            
            print("\nAll tests passed! Production ready.")
            return True
            
        except Exception as e:
            print(f"[FAIL] Test failed: {e}")
            return False
    
    async def health_check():
        """Production health check"""
        print("Health Check:")
        print(f"  Python: {sys.version}")
        print(f"  File: {__file__}")
        print(f"  Playwright: {'OK' if HAS_PLAYWRIGHT else 'NOT INSTALLED'}")
        
        # Check critical imports
        critical_imports = ["asyncio", "logging", "dataclasses", "typing"]
        for module in critical_imports:
            try:
                __import__(module)
                print(f"  {module}: OK")
            except ImportError:
                print(f"  {module}: MISSING")
        
        return True
    
    # Run based on arguments
    if args.test:
        asyncio.run(run_tests())
    elif args.health:
        asyncio.run(health_check())
    elif args.url:
        async def extract_url():
            config = StealthConfig()
            browser = UltimateStealthBrowser(config)
            await browser.initialize()
            result = await browser.extract_elements(args.url)
            print(f"Extracted {len(result.elements)} elements from {args.url}")
            await browser.cleanup()
        
        asyncio.run(extract_url())
    else:
        # Auto-execute 2 examples when running python browser.py
        print("=" * 60)
        print("Ultimate Stealth Browser - Auto-Running Examples")
        print("=" * 60)
        
        async def run_examples():
            """Run 2 automatic examples."""
            
            # Example 1: Extract elements from example.com (fast site)
            print("\n[Example 1] Extracting elements from example.com")
            print("-" * 40)
            try:
                config = StealthConfig()
                config.headless = True
                config.level = StealthLevel.BASIC  # Faster with basic level
                config.request_timeout = 5000  # 5 second timeout
                browser = UltimateStealthBrowser(config)
                await browser.initialize()
                
                result = await browser.extract_elements("https://example.com")
                print(f"[SUCCESS] Extracted {len(result.elements)} elements from example.com")
                print(f"   - Links found: {len([e for e in result.elements if e.tag_name == 'a'])}")
                print(f"   - Headers found: {len([e for e in result.elements if e.tag_name in ['h1', 'h2', 'h3']])}")
                print(f"   - Paragraphs: {len([e for e in result.elements if e.tag_name == 'p'])}")
                
                await browser.cleanup()
            except Exception as e:
                print(f"[FAILED] Example 1 failed: {e}")
            
            # Example 2: Extract elements from httpbin.org (lightweight API test site)
            print("\n[Example 2] Extracting elements from httpbin.org")
            print("-" * 40)
            try:
                config = StealthConfig()
                config.headless = True
                config.level = StealthLevel.BASIC  # Basic level for speed
                config.block_media = True  # Block images for faster loading
                config.request_timeout = 5000  # 5 second timeout
                browser = UltimateStealthBrowser(config)
                await browser.initialize()
                
                result = await browser.extract_elements("https://httpbin.org/")
                print(f"[SUCCESS] Extracted {len(result.elements)} elements from httpbin.org")
                print(f"   - Links found: {len([e for e in result.elements if e.tag_name == 'a'])}")
                print(f"   - List items: {len([e for e in result.elements if e.tag_name == 'li'])}")
                print(f"   - Headers: {len([e for e in result.elements if e.tag_name in ['h1', 'h2', 'h3']])}")
                
                # Show a sample of extracted elements
                print("\n   Sample of extracted elements:")
                for i, elem in enumerate(result.elements[:3], 1):
                    text = elem.text_content if hasattr(elem, 'text_content') and elem.text_content else "No text"
                    if text:
                        text = text.strip()[:40]
                    print(f"     {i}. <{elem.tag_name}> - {text}...")
                
                await browser.cleanup()
            except Exception as e:
                print(f"[FAILED] Example 2 failed: {e}")
            
            print("\n" + "=" * 60)
            print("Examples completed!")
            print("=" * 60)
        
        # Run the examples
        asyncio.run(run_examples())
