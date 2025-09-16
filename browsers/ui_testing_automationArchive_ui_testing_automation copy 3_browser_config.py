"""
Browser Configuration with 2025 Anti-Detection Settings
Configurable stealth settings for browser automation that work with Chrome, Chromium, and other browsers
"""

import os
import random
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

# Add parent directory to path for platform_utils import
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from utils.platform_utils import (
    get_chrome_executable_path,
    get_platform_info,
    get_temp_directory
)


class BrowserStealthConfig:
    """
    Advanced Playwright configuration for 2025 anti-detection
    Based on latest research for bypassing Cloudflare, DataDome, and other bot detection systems
    """
    
    def __init__(self, stealth_level: str = "maximum"):
        """
        Initialize stealth configuration
        
        Args:
            stealth_level: One of 'none', 'basic', 'moderate', 'advanced', 'maximum'
                          (matches StealthLevel enum in browser_contracts.py)
        """
        # Validate stealth level
        valid_levels = ['none', 'basic', 'moderate', 'advanced', 'maximum']
        if stealth_level not in valid_levels:
            print(f"[WARN] Invalid stealth level '{stealth_level}', using 'maximum'")
            stealth_level = 'maximum'
        
        self.stealth_level = stealth_level
        self.platform_info = get_platform_info()
        
    def get_launch_args(self) -> List[str]:
        """
        Get comprehensive browser launch arguments for anti-detection
        Updated for 2025 with latest evasion techniques
        """
        
        # Base arguments for all stealth levels
        base_args = [
            # Core anti-detection flags
            '--disable-blink-features=AutomationControlled',  # Remove automation indicators
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
        """
        Get browser context options with anti-detection settings
        """
        
        # User agents for different stealth levels
        user_agents = {
            'none': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'basic': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'moderate': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'advanced': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.85 Safari/537.36',
            'maximum': self._generate_random_user_agent()  # Maximum stealth uses random user agent
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
            
            # Geolocation (random major city)
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
            context_options['extra_http_headers'].update({
                'Sec-Ch-Ua-Platform-Version': '"15.0.0"',
                'Sec-Ch-Ua-Full-Version': '"131.0.6778.85"',
                'Sec-Ch-Ua-Full-Version-List': '"Chromium";v="131.0.6778.85", "Not_A Brand";v="24.0.0.0", "Google Chrome";v="131.0.6778.85"',
                'Sec-Ch-Ua-Arch': '"x86"',
                'Sec-Ch-Ua-Bitness': '"64"',
                'Sec-Ch-Ua-Model': '""',
            })
        
        return context_options
    
    def get_cdp_session_config(self) -> Dict[str, Any]:
        """
        Get CDP session configuration to avoid detection
        Based on 2025 research for bypassing CDP detection
        """
        return {
            'enable_runtime': False,  # Avoid Runtime.Enable detection
            'override_commands': {
                # Override CDP commands that leak automation
                'Runtime.enable': {'skip': True},  # Most critical for avoiding detection
                'Page.addScriptToEvaluateOnNewDocument': {'modify': True},
                'Network.setUserAgentOverride': {'modify': True},
            },
            'stealth_cdp': True,
            'minimize_cdp_usage': self.stealth_level == 'maximum'
        }
    
    def get_complete_config(self) -> Dict[str, Any]:
        """
        Get complete browser configuration with all anti-detection settings
        Works with Chrome, Chromium, and other Chromium-based browsers
        """
        
        # Initialize launch options with our enhanced args
        launch_options = {
            'args': self.get_launch_args(),
            'headless': True  # Always run headless for better performance
        }
        
        # Try to find Chrome or Chromium executable
        browser_path = self._find_browser_executable()
        if browser_path:
            launch_options['executable_path'] = browser_path
            print(f"[INFO] Using browser at: {browser_path}")
        else:
            print("[INFO] No system Chrome/Chromium found, will use Playwright's bundled Chromium")
            print("[INFO] Stealth settings will still be applied to bundled Chromium")
        
        # Additional launch options - these work with any Chromium-based browser
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
            'browser_type': 'chrome' if 'chrome' in str(browser_path).lower() else 'chromium'
        }
    
    def _find_browser_executable(self) -> Optional[str]:
        """
        Find Chrome or Chromium executable path
        Checks for both Chrome and Chromium installations
        """
        system = self.platform_info['system']
        
        if system == "Windows":
            paths = [
                # Chrome paths
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
                # Chromium paths
                r"C:\Program Files\Chromium\Application\chrome.exe",
                r"C:\Program Files (x86)\Chromium\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Chromium\Application\chrome.exe"),
            ]
        elif system == "Darwin":  # macOS
            paths = [
                # Chrome paths
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                # Chromium paths
                "/Applications/Chromium.app/Contents/MacOS/Chromium",
            ]
        else:  # Linux
            paths = [
                # Chrome paths
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                # Chromium paths
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser",
                "/snap/bin/chromium",
            ]
        
        for path in paths:
            if os.path.exists(path):
                return path
        
        return None
    
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


# Export main function
def get_browser_config(level: str = "maximum") -> Dict[str, Any]:
    """
    Get complete browser configuration for given stealth level
    Works with Chrome, Chromium, and Playwright's bundled browser
    
    Returns:
        Dict containing:
        - launch_options: Browser launch arguments
        - context_options: Browser context settings
        - cdp_config: CDP session configuration
        - stealth_level: Current stealth level
        - platform: Platform information
        - browser_type: Type of browser (chrome/chromium)
    """
    config = BrowserStealthConfig(level)
    return config.get_complete_config()


if __name__ == "__main__":
    # Test configuration generation
    print("[BROWSER CONFIG TEST]")
    print("=" * 60)
    
    for level in ['none', 'basic', 'moderate', 'advanced', 'maximum']:
        print(f"\n[{level.upper()}] Browser Stealth Configuration")
        print("-" * 40)
        config = get_browser_config(level)
        print(f"Launch args count: {len(config['launch_options']['args'])}")
        print(f"Headless: {config['launch_options']['headless']}")
        print(f"CDP Runtime disabled: {not config['cdp_config']['enable_runtime']}")
        print(f"Browser type: {config.get('browser_type', 'unknown')}")
        if 'executable_path' in config['launch_options']:
            print(f"Browser path: {config['launch_options']['executable_path']}")
        else:
            print("Browser path: Will use Playwright's bundled Chromium")
        print(f"User agent: {config['context_options']['user_agent'][:50]}...")
    
    print("\n" + "=" * 60)
    print("[INFO] All stealth settings work with:")
    print("  - Google Chrome (if installed)")
    print("  - Chromium (if installed)")
    print("  - Playwright's bundled Chromium (fallback)")
    print("  - Any Chromium-based browser")
    print("\n[INFO] Stealth settings are applied regardless of browser!")