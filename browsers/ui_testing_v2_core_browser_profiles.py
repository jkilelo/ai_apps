"""
Browser Profiles for Stealth Browser

This module defines different browser profiles that can be used to configure
the stealth browser behavior to match specific requirements.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import random


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
    # Element analysis delays
    element_analysis_delay: tuple = (10, 50)  # min, max in ms
    
    # Page interaction delays
    cookie_consent_wait: tuple = (1500, 2500)
    cookie_button_hover: tuple = (300, 700)
    cookie_post_click: tuple = (500, 1000)
    
    # Trust building delays
    trust_initial_wait: tuple = (2000, 4000)
    trust_link_hover: tuple = (500, 1000)
    trust_scroll_pause: tuple = (500, 2000)
    
    # Page stability delays
    stability_initial: tuple = (500, 1500)
    network_idle_timeout: int = 15000
    
    # Challenge handling delays
    challenge_wait: tuple = (3000, 5000)
    challenge_complete: tuple = (2000, 3000)
    
    # Selector batch delays
    selector_batch_delay: tuple = (50, 150)
    event_extraction_delay: tuple = (100, 300)
    
    # Dynamic content delays
    dynamic_content_wait: tuple = (1000, 2000)
    dynamic_content_trigger: tuple = (500, 1000)
    
    # Mouse movement
    mouse_move_steps: tuple = (15, 25)  # number of steps for B-spline
    mouse_step_delay: tuple = (10, 30)  # delay between steps in ms
    
    # Typing delays
    typing_base_delay: tuple = (80, 150)
    typing_variation: tuple = (-30, 30)
    typing_pause_chance: float = 0.1
    typing_pause_duration: tuple = (300, 800)
    
    # Scrolling
    scroll_distance: tuple = (100, 400)
    scroll_pause: tuple = (300, 1500)
    scroll_back_chance: float = 0.2
    scroll_back_distance: tuple = (50, 150)


@dataclass
class StealthProfile:
    """Stealth configuration for anti-detection"""
    # CDP evasion
    hide_webdriver: bool = True
    hide_automation_indicators: bool = True
    hide_cdp_properties: bool = True
    
    # Navigator spoofing
    spoof_plugins: bool = True
    spoof_languages: bool = True
    spoof_chrome_runtime: bool = True
    spoof_permissions: bool = True
    
    # Advanced spoofing
    prevent_webrtc_leak: bool = True
    spoof_canvas_fingerprint: bool = True
    spoof_battery_api: bool = True
    randomize_hardware_concurrency: bool = True
    randomize_device_memory: bool = True
    normalize_screen_properties: bool = True
    spoof_webgl: bool = True
    
    # Trust building
    build_trust: bool = True
    trust_safe_domains: List[str] = field(default_factory=lambda: [
        'google.com', 'wikipedia.org', 'github.com', 'youtube.com'
    ])
    trust_visit_pages: int = 3
    
    # Cookie handling
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
    
    # Challenge handling
    handle_cloudflare: bool = True
    challenge_timeout: int = 30000
    
    # Viewport randomization
    randomize_viewport: bool = True
    viewport_base: tuple = (1920, 1080)
    viewport_variation: tuple = (40, 40)  # +/- variation
    
    # User agents
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
    
    # Browser launch args
    launch_args: List[str] = field(default_factory=lambda: [
        '--disable-blink-features=AutomationControlled',
        '--disable-features=IsolateOrigins,site-per-process',
        '--disable-web-security',
        '--disable-features=CrossSiteDocumentBlockingIfIsolating',
        '--disable-site-isolation-trials',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--no-zygote',
        '--single-process',
        '--disable-gpu'
    ])
    
    # Extra HTTP headers
    extra_headers: Dict[str, str] = field(default_factory=lambda: {
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1'
    })
    
    def get_viewport(self) -> Dict[str, int]:
        """Get viewport with optional randomization"""
        if self.stealth.randomize_viewport:
            width = self.stealth.viewport_base[0] + random.randint(
                -self.stealth.viewport_variation[0], 
                self.stealth.viewport_variation[0]
            )
            height = self.stealth.viewport_base[1] + random.randint(
                -self.stealth.viewport_variation[1], 
                self.stealth.viewport_variation[1]
            )
            return {'width': width, 'height': height}
        return {'width': self.stealth.viewport_base[0], 'height': self.stealth.viewport_base[1]}
    
    def get_user_agent(self) -> str:
        """Get a random user agent"""
        return random.choice(self.stealth.user_agents)


# Pre-defined profiles
PROFILES = {
    ProfileType.BOT: BrowserProfile(
        name="Bot Profile",
        profile_type=ProfileType.BOT,
        timing=TimingProfile(
            element_analysis_delay=(0, 0),
            cookie_consent_wait=(0, 0),
            trust_initial_wait=(0, 0),
            stability_initial=(0, 0),
            mouse_move_steps=(1, 1),
            typing_base_delay=(0, 0)
        ),
        stealth=StealthProfile(
            hide_webdriver=False,
            hide_automation_indicators=False,
            build_trust=False,
            auto_handle_cookies=False,
            randomize_viewport=False
        )
    ),
    
    ProfileType.HUMAN: BrowserProfile(
        name="Human Profile",
        profile_type=ProfileType.HUMAN,
        timing=TimingProfile(
            element_analysis_delay=(50, 150),
            cookie_consent_wait=(2000, 4000),
            trust_initial_wait=(3000, 5000),
            typing_base_delay=(100, 200)
        ),
        stealth=StealthProfile(
            hide_webdriver=True,
            hide_automation_indicators=True,
            build_trust=False,
            auto_handle_cookies=True,
            randomize_viewport=True
        )
    ),
    
    ProfileType.STEALTH: BrowserProfile(
        name="Stealth Profile",
        profile_type=ProfileType.STEALTH,
        timing=TimingProfile(
            element_analysis_delay=(20, 80),
            cookie_consent_wait=(1000, 2000),
            trust_initial_wait=(2000, 3000)
        ),
        stealth=StealthProfile(
            hide_webdriver=True,
            hide_automation_indicators=True,
            spoof_plugins=True,
            spoof_languages=True,
            build_trust=False,
            auto_handle_cookies=True
        )
    ),
    
    ProfileType.ULTRA_STEALTH: BrowserProfile(
        name="Ultra-Stealth Profile (Exact Match)",
        profile_type=ProfileType.ULTRA_STEALTH,
        timing=TimingProfile(
            # Exact timings from ultra-stealth strategy
            element_analysis_delay=(10, 50),
            cookie_consent_wait=(1500, 2500),
            cookie_button_hover=(300, 700),
            cookie_post_click=(500, 1000),
            trust_initial_wait=(2000, 4000),
            trust_link_hover=(500, 1000),
            trust_scroll_pause=(500, 2000),
            stability_initial=(500, 1500),
            network_idle_timeout=15000,
            challenge_wait=(3000, 5000),
            challenge_complete=(2000, 3000),
            selector_batch_delay=(50, 150),
            event_extraction_delay=(100, 300),
            dynamic_content_wait=(1000, 2000),
            dynamic_content_trigger=(500, 1000),
            mouse_move_steps=(20, 20),  # Fixed as in ultra-stealth
            mouse_step_delay=(10, 30),
            typing_base_delay=(80, 150),
            typing_variation=(-30, 30),
            typing_pause_chance=0.1,
            typing_pause_duration=(300, 800),
            scroll_distance=(100, 400),
            scroll_pause=(300, 1500),
            scroll_back_chance=0.2,
            scroll_back_distance=(50, 150)
        ),
        stealth=StealthProfile(
            # All features enabled as in ultra-stealth
            hide_webdriver=True,
            hide_automation_indicators=True,
            hide_cdp_properties=True,
            spoof_plugins=True,
            spoof_languages=True,
            spoof_chrome_runtime=True,
            spoof_permissions=True,
            prevent_webrtc_leak=True,
            spoof_canvas_fingerprint=True,
            spoof_battery_api=True,
            randomize_hardware_concurrency=True,
            randomize_device_memory=True,
            normalize_screen_properties=True,
            spoof_webgl=True,
            build_trust=True,
            trust_visit_pages=3,
            auto_handle_cookies=True,
            handle_cloudflare=True,
            randomize_viewport=True,
            viewport_variation=(40, 40)
        )
    )
}


def get_profile(profile_type: ProfileType) -> BrowserProfile:
    """Get a predefined browser profile"""
    return PROFILES.get(profile_type, PROFILES[ProfileType.HUMAN])


def create_custom_profile(
    name: str,
    base_profile: ProfileType = ProfileType.HUMAN,
    **overrides
) -> BrowserProfile:
    """Create a custom profile based on an existing one"""
    profile = get_profile(base_profile)
    profile.name = name
    profile.profile_type = ProfileType.CUSTOM
    
    # Apply overrides
    for key, value in overrides.items():
        if hasattr(profile, key):
            setattr(profile, key, value)
        elif hasattr(profile.timing, key):
            setattr(profile.timing, key, value)
        elif hasattr(profile.stealth, key):
            setattr(profile.stealth, key, value)
    
    return profile