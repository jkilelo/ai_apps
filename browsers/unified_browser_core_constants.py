"""
Constants module for unified browser.

This module contains all constants used throughout the browser implementation,
eliminating magic numbers and providing a single source of truth for configuration values.
"""

from __future__ import annotations

from typing import Final, List, Tuple

# ============================================================================
# TIMING CONSTANTS (milliseconds)
# ============================================================================
DEFAULT_TIMEOUT: Final[int] = 30000
DEFAULT_NAVIGATION_TIMEOUT: Final[int] = 30000
DEFAULT_ELEMENT_TIMEOUT: Final[int] = 5000
DEFAULT_WAIT_TIMEOUT: Final[int] = 10000

# Retry configuration
DEFAULT_RETRY_COUNT: Final[int] = 3
DEFAULT_RETRY_DELAY: Final[int] = 1000
MAX_RETRY_COUNT: Final[int] = 5

# Human simulation delays (ms)
MIN_TYPING_DELAY: Final[int] = 50
MAX_TYPING_DELAY: Final[int] = 150
MIN_MOUSE_DELAY: Final[int] = 100
MAX_MOUSE_DELAY: Final[int] = 300
MIN_SCROLL_DELAY: Final[int] = 200
MAX_SCROLL_DELAY: Final[int] = 500
MICRO_BEHAVIOR_DELAY: Final[int] = 100

# ============================================================================
# BROWSER CONFIGURATION
# ============================================================================
# Viewport dimensions
DEFAULT_VIEWPORT_WIDTH: Final[int] = 1920
DEFAULT_VIEWPORT_HEIGHT: Final[int] = 1080

VIEWPORT_SIZES: Final[List[Tuple[int, int]]] = [
    (1920, 1080),  # Full HD
    (1366, 768),  # Most common laptop
    (1536, 864),  # Common desktop
    (1440, 900),  # MacBook Pro
    (1680, 1050),  # Common desktop
    (2560, 1440),  # QHD
]

MIN_VIEWPORT_WIDTH: Final[int] = 800
MIN_VIEWPORT_HEIGHT: Final[int] = 600
MAX_VIEWPORT_WIDTH: Final[int] = 2560
MAX_VIEWPORT_HEIGHT: Final[int] = 1440

# Browser launch arguments
STEALTH_BROWSER_ARGS: Final[List[str]] = [
    "--disable-blink-features=AutomationControlled",
    "--disable-dev-shm-usage",
    "--enable-features=NetworkService,NetworkServiceInProcess",
    "--force-color-profile=srgb",
    "--metrics-recording-only",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-breakpad",
    "--disable-client-side-phishing-detection",
    "--disable-component-extensions-with-background-pages",
    "--disable-default-apps",
    "--disable-extensions",
    "--disable-features=TranslateUI",
    "--disable-hang-monitor",
    "--disable-ipc-flooding-protection",
    "--disable-popup-blocking",
    "--disable-prompt-on-repost",
    "--disable-renderer-backgrounding",
    "--disable-sync",
    "--force-device-scale-factor=1",
    "--no-default-browser-check",
    "--no-first-run",
    "--password-store=basic",
    "--use-mock-keychain",
    "--disable-infobars",
    "--disable-notifications",
]

# User agents
DEFAULT_USER_AGENTS: Final[List[str]] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
]

# ============================================================================
# ELEMENT SELECTION
# ============================================================================
INTERACTIVE_SELECTORS: Final[List[str]] = [
    "button",
    "a",
    "input",
    "select",
    "textarea",
    "[role='button']",
    "[role='link']",
    "[role='tab']",
    "[onclick]",
    "[ng-click]",
    "[data-action]",
    "[href]",
    "label",
    "form",
    "[type='submit']",
    "[type='button']",
]

FORM_INPUT_SELECTORS: Final[List[str]] = [
    "input[type='text']",
    "input[type='email']",
    "input[type='password']",
    "input[type='search']",
    "input[type='tel']",
    "input[type='url']",
    "input[type='number']",
    "textarea",
    "select",
]

# ============================================================================
# EXTRACTION & HASHING
# ============================================================================
DEFAULT_ELEMENT_HASH_LENGTH: Final[int] = 12
MAX_ELEMENT_TEXT_LENGTH: Final[int] = 100
MAX_EXTRACTION_ELEMENTS: Final[int] = 1000
SHADOW_DOM_MAX_DEPTH: Final[int] = 5
DEFAULT_ELEMENT_LIMIT: Final[int] = 100

# ============================================================================
# STEALTH LEVELS
# ============================================================================
STEALTH_LEVEL_BASIC: Final[str] = "basic"
STEALTH_LEVEL_ENHANCED: Final[str] = "enhanced"
STEALTH_LEVEL_MAXIMUM: Final[str] = "maximum"

# ============================================================================
# NAVIGATION STRATEGIES
# ============================================================================
NAVIGATION_WAIT_LOAD: Final[str] = "load"
NAVIGATION_WAIT_DOMCONTENTLOADED: Final[str] = "domcontentloaded"
NAVIGATION_WAIT_NETWORKIDLE: Final[str] = "networkidle"
NAVIGATION_WAIT_COMMIT: Final[str] = "commit"

# ============================================================================
# SECURITY & VALIDATION
# ============================================================================
MAX_URL_LENGTH: Final[int] = 2048
MAX_SELECTOR_LENGTH: Final[int] = 500
MAX_PATH_LENGTH: Final[int] = 260  # Windows MAX_PATH
ALLOWED_PROTOCOLS: Final[List[str]] = ["http", "https"]
BLOCKED_FILE_EXTENSIONS: Final[List[str]] = [".exe", ".bat", ".cmd", ".com", ".scr", ".vbs"]

# Rate limiting
MAX_REQUESTS_PER_SECOND: Final[int] = 10
MAX_NAVIGATION_PER_MINUTE: Final[int] = 30
MAX_LLM_CALLS_PER_MINUTE: Final[int] = 20

# ============================================================================
# AI & LLM CONFIGURATION
# ============================================================================
DEFAULT_LLM_TEMPERATURE: Final[float] = 0.7
DEFAULT_LLM_MAX_TOKENS: Final[int] = 4000
LLM_TIMEOUT: Final[int] = 30000
MAX_CONVERSATION_HISTORY: Final[int] = 50

# Supported LLM providers
LLM_PROVIDERS: Final[List[str]] = [
    "openai",
    "anthropic",
    "google",
    "gemini",
    "xai",
]

# ============================================================================
# CAPTCHA DETECTION
# ============================================================================
CAPTCHA_PATTERNS: Final[List[str]] = [
    "g-recaptcha",
    "h-captcha",
    "cf-challenge",
    "captcha",
    "robot-check",
]

# ============================================================================
# FRAMEWORK DETECTION
# ============================================================================
FRAMEWORK_INDICATORS: Final[dict[str, List[str]]] = {
    "react": ["_reactRootContainer", "__reactInternalInstance", "__REACT_DEVTOOLS_GLOBAL_HOOK__"],
    "angular": ["ng-version", "ng-app", "__ng_debug__"],
    "vue": ["__vue__", "__VUE_DEVTOOLS_GLOBAL_HOOK__", "__VUE__"],
    "jquery": ["jQuery", "$"],
    "svelte": ["__svelte__"],
}

# ============================================================================
# PERFORMANCE & CONCURRENCY
# ============================================================================
MAX_CONCURRENT_OPERATIONS: Final[int] = 10
MAX_CONCURRENT_EXTRACTIONS: Final[int] = 5
MAX_CONCURRENT_NAVIGATIONS: Final[int] = 1  # Usually serialize navigation
DEFAULT_SLOW_MO: Final[int] = 0  # milliseconds

# ============================================================================
# FILE OPERATIONS
# ============================================================================
MAX_FILE_SIZE: Final[int] = 100 * 1024 * 1024  # 100MB
DEFAULT_DOWNLOAD_TIMEOUT: Final[int] = 60000  # 60 seconds
ALLOWED_DOWNLOAD_EXTENSIONS: Final[List[str]] = [
    ".pdf",
    ".txt",
    ".csv",
    ".json",
    ".xml",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
]

# ============================================================================
# LOGGING & MONITORING
# ============================================================================
LOG_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"
LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
MAX_LOG_SIZE: Final[int] = 10 * 1024 * 1024  # 10MB
MAX_LOG_BACKUPS: Final[int] = 5

# ============================================================================
# ECOMMERCE SPECIFIC
# ============================================================================
AMAZON_DOMAINS: Final[List[str]] = [
    "amazon.com",
    "amazon.co.uk",
    "amazon.de",
    "amazon.fr",
    "amazon.it",
    "amazon.es",
    "amazon.co.jp",
    "amazon.ca",
]

PRODUCT_PRICE_PATTERNS: Final[List[str]] = [
    r"\$[\d,]+\.?\d*",
    r"£[\d,]+\.?\d*",
    r"€[\d,]+\.?\d*",
    r"¥[\d,]+\.?\d*",
]

# ============================================================================
# ADVANCED STEALTH & DETECTION BYPASS (2025 Features)
# ============================================================================
# Runtime.enable detection bypass
RUNTIME_ENABLE_BYPASS: Final[bool] = True
CDP_COORDINATE_LEAK_PREVENTION: Final[bool] = True
WEBDRIVER_EXECUTE_CDP_OVERRIDE: Final[bool] = True

# Nodriver compatibility flags
NODRIVER_MODE: Final[bool] = False  # Enable for undetected browser
NODRIVER_PATCH_LEVEL: Final[int] = 2  # 0=none, 1=basic, 2=advanced

# Advanced fingerprinting evasion
FINGERPRINT_ROTATION_INTERVAL: Final[int] = 300000  # 5 minutes
CANVAS_NOISE_LEVEL: Final[float] = 0.02  # 2% noise injection
WEBGL_VENDOR_SPOOFING: Final[bool] = True
AUDIO_CONTEXT_SPOOFING: Final[bool] = True
FONT_FINGERPRINT_PROTECTION: Final[bool] = True

# Browser profile persistence
PROFILE_PERSISTENCE: Final[bool] = True
PROFILE_ROTATION_COUNT: Final[int] = 5
COOKIE_PRESERVATION: Final[bool] = True

# ============================================================================
# HIERARCHICAL AGENT ARCHITECTURE
# ============================================================================
AGENT_HIERARCHY_LEVELS: Final[int] = 3
PLANNER_AGENT_ENABLED: Final[bool] = True
EXECUTOR_AGENT_ENABLED: Final[bool] = True
VERIFIER_AGENT_ENABLED: Final[bool] = True
REFLECTOR_AGENT_ENABLED: Final[bool] = True

# Agent coordination
AGENT_COMMUNICATION_TIMEOUT: Final[int] = 5000
AGENT_RETRY_ON_FAILURE: Final[bool] = True
AGENT_CONSENSUS_REQUIRED: Final[bool] = False

# ============================================================================
# COMPUTER VISION CONFIGURATION
# ============================================================================
VISION_ENABLED: Final[bool] = True
OCR_ENABLED: Final[bool] = True
VISUAL_GROUNDING_ENABLED: Final[bool] = True
SCREENSHOT_QUALITY: Final[int] = 95  # JPEG quality
VISION_MODEL_PROVIDER: Final[str] = "gemini"  # gemini, openai, anthropic

# Element detection thresholds
VISUAL_CONFIDENCE_THRESHOLD: Final[float] = 0.85
OCR_CONFIDENCE_THRESHOLD: Final[float] = 0.90
BOUNDING_BOX_OVERLAP_THRESHOLD: Final[float] = 0.5

# ============================================================================
# MULTI-MODAL INTERACTION
# ============================================================================
MULTI_MODAL_ENABLED: Final[bool] = True
VISION_LANGUAGE_MODEL: Final[str] = "gemini-2.5-flash"
SCREENSHOT_BEFORE_ACTION: Final[bool] = True
SCREENSHOT_AFTER_ACTION: Final[bool] = True
ACTION_REPLAY_ENABLED: Final[bool] = True

# ============================================================================
# ADVANCED NAVIGATION PATTERNS
# ============================================================================
# Page state detection
PAGE_STABILITY_CHECK: Final[bool] = True
PAGE_STABILITY_TIMEOUT: Final[int] = 2000
MUTATION_OBSERVER_ENABLED: Final[bool] = True
LAZY_LOAD_DETECTION: Final[bool] = True
INFINITE_SCROLL_DETECTION: Final[bool] = True

# Smart waiting strategies
ADAPTIVE_WAIT_ENABLED: Final[bool] = True
PREDICTIVE_WAIT_MODEL: Final[bool] = True
WAIT_STRATEGY_LEARNING: Final[bool] = True

# ============================================================================
# BROWSER CONTEXT ISOLATION
# ============================================================================
CONTEXT_ISOLATION_ENABLED: Final[bool] = True
INCOGNITO_MODE_DEFAULT: Final[bool] = True
SEPARATE_CONTEXT_PER_TASK: Final[bool] = True
CONTEXT_CLEANUP_ON_ERROR: Final[bool] = True

# ============================================================================
# ADVANCED ERROR RECOVERY
# ============================================================================
SMART_RETRY_ENABLED: Final[bool] = True
EXPONENTIAL_BACKOFF: Final[bool] = True
ERROR_SCREENSHOT_CAPTURE: Final[bool] = True
DOM_SNAPSHOT_ON_ERROR: Final[bool] = True
NETWORK_LOG_ON_ERROR: Final[bool] = True

# Recovery strategies
RECOVERY_STRATEGIES: Final[List[str]] = [
    "retry_with_different_selector",
    "wait_and_retry",
    "refresh_and_retry",
    "navigate_back_and_retry",
    "clear_cookies_and_retry",
    "new_context_and_retry",
]

# ============================================================================
# PERFORMANCE OPTIMIZATION
# ============================================================================
RESOURCE_BLOCKING_ENABLED: Final[bool] = True
BLOCKED_RESOURCE_TYPES: Final[List[str]] = [
    "image",
    "media",
    "font",
    "stylesheet",  # Optional, may break some sites
]

# Caching
PAGE_CACHE_ENABLED: Final[bool] = True
CACHE_SIZE_MB: Final[int] = 100
CACHE_TTL_SECONDS: Final[int] = 3600

# Connection pooling
CONNECTION_POOL_SIZE: Final[int] = 10
KEEP_ALIVE_TIMEOUT: Final[int] = 30000

# ============================================================================
# MISC CONSTANTS
# ============================================================================
DEFAULT_LOCALE: Final[str] = "en-US"
DEFAULT_TIMEZONE: Final[str] = "America/New_York"
DEFAULT_LANGUAGE: Final[str] = "en"
DEFAULT_ENCODING: Final[str] = "utf-8"

# ============================================================================
# EXTRACTION CONSTANTS  
# ============================================================================
EXTRACTION_BATCH_SIZE: Final[int] = 50
MAX_EXTRACTION_WORKERS: Final[int] = 4
MAX_EXTRACTION_DEPTH: Final[int] = 5
SHADOW_DOM_DEPTH: Final[int] = 3
USE_ASYNC_EXTRACTION: Final[bool] = True
USE_BATCH_EXTRACTION: Final[bool] = True
USE_PARALLEL_EXTRACTION: Final[bool] = True
MAX_RETRIES: Final[int] = 3

# ============================================================================
# PERFORMANCE CONSTANTS
# ============================================================================  
CACHE_SIZE_MB: Final[int] = 100
CONNECTION_POOL_SIZE: Final[int] = 10
MAX_CONCURRENT_DOWNLOADS: Final[int] = 3
MAX_MEMORY_MB: Final[int] = 1024
METRICS_ENABLED: Final[bool] = True
PERFORMANCE_MONITORING: Final[bool] = True
PRELOAD_RESOURCES: Final[bool] = False
RESOURCE_TIMEOUT: Final[int] = 30000

