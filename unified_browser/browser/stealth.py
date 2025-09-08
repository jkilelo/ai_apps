"""
Stealth and anti-detection features for browser automation.

Extracted and enhanced from the existing /agents system to provide
comprehensive bot detection evasion capabilities.
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from playwright.async_api import Page, BrowserContext
from ..core.js_library import JSLibrary


@dataclass
class StealthConfig:
    """Configuration for stealth features."""
    
    # Core stealth features
    override_webdriver: bool = True
    randomize_user_agent: bool = True
    override_navigator: bool = True
    override_permissions: bool = True
    
    # Advanced evasion
    randomize_viewport: bool = True
    inject_canvas_noise: bool = True
    spoof_timezone: bool = True
    block_webrtc: bool = True
    
    # User agents pool
    user_agents: List[str] = None
    
    def __post_init__(self):
        if self.user_agents is None:
            self.user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36", 
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
            ]


class StealthManager:
    """Advanced stealth and anti-detection manager."""
    
    def __init__(self, config: Optional[StealthConfig] = None):
        self.config = config or StealthConfig()
        self.js_lib = JSLibrary()
        
    async def apply_stealth_to_context(self, context: BrowserContext) -> None:
        """Apply stealth measures to browser context using JS files."""
        
        # Use the new stealth bundle method for cleaner code
        stealth_bundle = self.js_lib.get_stealth_bundle(
            webdriver=self.config.override_webdriver,
            navigator=self.config.override_navigator,
            canvas=self.config.inject_canvas_noise,
            webrtc=self.config.block_webrtc,
            permissions=self.config.override_permissions
        )
        
        # Inject the bundle as init script
        await context.add_init_script(stealth_bundle)
    
    async def apply_stealth_to_page(self, page: Page) -> None:
        """Apply stealth measures to a specific page."""
        
        # Use shared JS library for human-like behavior
        await page.add_init_script(self.js_lib.get_human_like_mouse_movement())
        
        # Override user agent if needed
        if self.config.randomize_user_agent:
            user_agent = self._get_random_user_agent()
            await page.set_extra_http_headers({"User-Agent": user_agent})
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent from the pool."""
        return random.choice(self.config.user_agents)
    
    
    def get_stealth_launch_args(self) -> List[str]:
        """Get Chrome launch arguments for stealth mode."""
        return [
            "--no-sandbox",
            "--disable-setuid-sandbox", 
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--no-first-run",
            "--no-zygote",
            "--disable-gpu",
            "--disable-dev-tools",
            "--disable-extensions",
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-breakpad",
            "--disable-client-side-phishing-detection",
            "--disable-component-extensions-with-background-pages",
            "--disable-default-apps",
            "--disable-extensions-file-access-check",
            "--disable-features=TranslateUI,VizDisplayCompositor",
            "--disable-hang-monitor",
            "--disable-ipc-flooding-protection",
            "--disable-popup-blocking", 
            "--disable-prompt-on-repost",
            "--disable-renderer-backgrounding",
            "--disable-sync",
            "--force-device-scale-factor=1",
            "--no-default-browser-check",
            "--password-store=basic",
            "--use-mock-keychain",
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--disable-notifications",
            "--disable-web-security",
        ]
    
    def get_random_viewport(self) -> Dict[str, int]:
        """Get a randomized viewport size."""
        if not self.config.randomize_viewport:
            return {"width": 1920, "height": 1080}
        
        # Common viewport sizes with slight randomization
        common_sizes = [
            (1920, 1080), (1366, 768), (1440, 900),
            (1536, 864), (1280, 720), (1024, 768)
        ]
        
        width, height = random.choice(common_sizes)
        
        # Add slight randomization
        width += random.randint(-20, 20)
        height += random.randint(-20, 20)
        
        return {"width": max(800, width), "height": max(600, height)}