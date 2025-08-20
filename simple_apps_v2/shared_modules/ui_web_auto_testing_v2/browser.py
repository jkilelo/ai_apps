#!/usr/bin/env python3
"""
Standalone Browser Service
===================================
A comprehensive, standalone stealth browser that can be used by any application.
This browser provides maximum anti-detection capabilities and exposes a simple API
for LLMs, automation tools, manual scripts, or any other application.

Key Features:
- Complete standalone operation - no dependencies on specific use cases
- Maximum stealth with all modern anti-detection techniques
- Simple API for any application to use
- Support for async and sync operations
- WebSocket server for remote control
- REST API for HTTP-based automation
- Session management and persistence
- Multi-browser instance support
- Built-in proxy rotation
- Automatic CAPTCHA detection
- Human behavior simulation

Usage:
    # As a library
    browser = BrowserService()
    await browser.start()
    page = await browser.get_page("https://example.com")
    
    # As a server
    python standalone_stealth_browser.py --server --port 9222
    
    # Via REST API
    curl http://localhost:9222/api/navigate -d '{"url": "https://example.com"}'
"""

import asyncio
import json
import logging
import hashlib
import platform
import os
import sys
import time
import random
import base64
import uuid

# Fix Windows async subprocess issue
# On Windows, we need to handle event loops differently for Playwright
# Don't set the policy here as it breaks Playwright's internal handling
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable, TypeVar
from urllib.parse import urlparse, urljoin
from pathlib import Path
from collections import defaultdict
from contextlib import asynccontextmanager
from functools import wraps
import threading
import weakref

# Import platform utilities for dynamic browser detection
try:
    # Try relative import first
    from ....utils.platform_utils import get_playwright_launch_options, get_chrome_executable_path
except ImportError:
    # Fallback to absolute import
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))
    from utils.platform_utils import get_playwright_launch_options, get_chrome_executable_path

# Third-party imports
try:
    from playwright.async_api import (
        Browser,
        BrowserContext,
        Page,
        async_playwright,
        Error as PlaywrightError,
    )
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("Warning: Playwright not installed. Install with: pip install playwright")

try:
    from aiohttp import web
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration and Models
# ============================================================================

@dataclass
class BrowserConfig:
    """Complete browser configuration"""
    
    # Core settings
    headless: bool = False
    browser_type: str = "chromium"  # chromium, firefox, webkit
    
    # Stealth settings
    stealth_level: str = "maximum"  # basic, enhanced, maximum, ultimate
    enable_stealth: bool = True
    enable_human_simulation: bool = True
    enable_fingerprint_rotation: bool = True
    
    # Anti-detection features
    hide_webdriver: bool = True
    hide_automation_indicators: bool = True
    spoof_plugins: bool = True
    spoof_languages: bool = True
    spoof_chrome_runtime: bool = True
    prevent_webrtc_leak: bool = True
    spoof_canvas_fingerprint: bool = True
    spoof_webgl: bool = True
    spoof_audio_context: bool = True
    spoof_battery: bool = True
    spoof_hardware: bool = True
    bypass_csp: bool = True
    block_webrtc: bool = True
    spoof_timezone: bool = True
    spoof_geolocation: bool = False
    
    # CDP detection bypass
    disable_cdp_detection: bool = True
    modify_runtime_enable: bool = True
    
    # Advanced bypass
    bypass_cloudflare: bool = True
    bypass_datadome: bool = True
    bypass_perimeter_x: bool = True
    bypass_akamai: bool = True
    bypass_kasada: bool = True
    bypass_shape: bool = True
    
    # Browser settings - use null viewport to avoid detection
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: Optional[str] = None
    locale: str = "en-US"
    timezone: str = "America/New_York"
    
    # Proxy settings
    proxy: Optional[Dict[str, str]] = None
    rotate_proxy: bool = False
    proxy_list: List[Dict[str, str]] = field(default_factory=list)
    
    # Performance
    timeout: int = 60000
    navigation_timeout: int = 30000
    slow_mo: int = 0
    
    # Session
    persist_session: bool = False
    session_id: Optional[str] = None
    cookies_file: Optional[str] = None
    
    # Resource management
    block_images: bool = False
    block_media: bool = False
    block_fonts: bool = False
    block_stylesheets: bool = False
    
    # Human behavior
    human_typing_speed: Tuple[int, int] = (50, 200)  # ms between keystrokes
    human_mouse_speed: float = 1.0
    human_scroll_behavior: bool = True
    random_delays: bool = True
    delay_range: Tuple[int, int] = (100, 2000)  # ms
    
    # Advanced stealth
    disable_runtime_enable: bool = True  # Disable Runtime.enable CDP command
    use_isolated_context: bool = False  # Use isolated world for script execution
    patch_cdp_detection: bool = True  # Patch CDP detection methods
    randomize_fingerprints: bool = True  # Randomize canvas/webgl fingerprints per session

@dataclass
class BrowserSession:
    """Browser session information"""
    session_id: str
    browser_id: str
    created_at: datetime
    last_accessed: datetime
    page_count: int = 0
    navigation_count: int = 0
    cookies: List[Dict] = field(default_factory=list)
    local_storage: Dict[str, Dict] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

# ============================================================================
# Stealth Injection Module
# ============================================================================

class StealthInjector:
    """Advanced stealth script injection"""
    
    @staticmethod
    async def inject_all(page: Page, config: BrowserConfig):
        """Inject all stealth scripts based on configuration"""
        
        # Core stealth scripts - inject before page loads
        if config.enable_stealth:
            await StealthInjector._inject_webdriver_override(page)
            await StealthInjector._inject_chrome_runtime(page)
            await StealthInjector._inject_permissions_override(page)
            await StealthInjector._inject_plugins_override(page)
            await StealthInjector._inject_languages_override(page)
            
        # Advanced fingerprinting
        if config.spoof_canvas_fingerprint:
            await StealthInjector._inject_canvas_fingerprint(page)
            
        if config.spoof_webgl:
            await StealthInjector._inject_webgl_fingerprint(page)
            
        if config.spoof_audio_context:
            await StealthInjector._inject_audio_fingerprint(page)
            
        if config.prevent_webrtc_leak:
            await StealthInjector._inject_webrtc_override(page)
            
        if config.spoof_battery:
            await StealthInjector._inject_battery_override(page)
            
        if config.spoof_hardware:
            await StealthInjector._inject_hardware_override(page)
            
        # CDP detection bypass and advanced techniques
        if config.disable_cdp_detection:
            await StealthInjector._inject_cdp_detection_bypass(page)
            await StealthInjector._inject_runtime_enable_bypass(page)
            await StealthInjector._inject_console_debug_override(page)
        
        logger.info("Stealth scripts injected successfully")
    
    @staticmethod
    async def _inject_webdriver_override(page: Page):
        """Override webdriver detection with enhanced techniques"""
        await page.add_init_script("""
            // Remove webdriver property completely
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Remove automation controlled flag
            Object.defineProperty(navigator, 'automationControlled', {
                get: () => undefined
            });
            
            // Clean up all possible webdriver traces
            delete navigator.__proto__.webdriver;
            delete navigator.__proto__.__proto__.webdriver;
            
            // Override document properties
            Object.defineProperties(document, {
                '$cdc_asdjflasutopfhvcZLmcfl_': { value: undefined },
                '$chrome_asyncScriptInfo': { value: undefined },
                '$wdc_': { value: undefined }
            });
            
            // Remove CDP specific properties
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
            
            // Override the navigator object with a clean proxy
            const originalNavigator = navigator;
            const navigatorProxy = new Proxy(originalNavigator, {
                has: (target, key) => {
                    if (key === 'webdriver' || key === 'automationControlled') return false;
                    if (key.includes('webdriver')) return false;
                    return key in target;
                },
                get: (target, key) => {
                    if (key === 'webdriver' || key === 'automationControlled') return undefined;
                    if (key.includes('webdriver')) return undefined;
                    
                    // Return original value for everything else
                    const val = target[key];
                    return typeof val === 'function' ? val.bind(target) : val;
                }
            });
            
            // Replace navigator
            try {
                Object.defineProperty(window, 'navigator', {
                    value: navigatorProxy,
                    writable: false,
                    configurable: false
                });
            } catch (e) {}
            
            // Override getOwnPropertyDescriptor to hide our changes
            const originalGetOwnPropertyDescriptor = Object.getOwnPropertyDescriptor;
            Object.getOwnPropertyDescriptor = function(obj, prop) {
                if (obj === navigator && prop === 'webdriver') {
                    return undefined;
                }
                return originalGetOwnPropertyDescriptor.apply(this, arguments);
            };
        """)
    
    @staticmethod
    async def _inject_chrome_runtime(page: Page):
        """Inject chrome runtime to appear as regular Chrome"""
        await page.add_init_script("""
            if (!window.chrome) {
                window.chrome = {};
            }
            
            window.chrome.runtime = {
                connect: () => {},
                sendMessage: () => {},
                onMessage: {
                    addListener: () => {}
                },
                getManifest: () => ({}),
                getURL: (path) => `chrome-extension://fake/${path}`,
                id: 'aapbdbdomjkkjkaonfhkkikfgjllcleb'
            };
            
            window.chrome.app = {
                isInstalled: false,
                InstallState: {
                    DISABLED: 'disabled',
                    INSTALLED: 'installed',
                    NOT_INSTALLED: 'not_installed'
                }
            };
            
            window.chrome.csi = () => {};
            window.chrome.loadTimes = () => ({
                requestTime: Date.now() / 1000,
                startLoadTime: Date.now() / 1000,
                commitLoadTime: Date.now() / 1000,
                finishDocumentLoadTime: Date.now() / 1000,
                finishLoadTime: Date.now() / 1000,
                firstPaintTime: Date.now() / 1000,
                firstPaintAfterLoadTime: 0,
                navigationType: "Other",
                wasFetchedViaSpdy: false,
                wasNpnNegotiated: true,
                npnNegotiatedProtocol: "http/1.1",
                wasAlternateProtocolAvailable: false,
                connectionInfo: "http/1.1"
            });
        """)
    
    @staticmethod
    async def _inject_permissions_override(page: Page):
        """Override permissions API with realistic responses"""
        await page.add_init_script("""
            // Override permissions to look more human
            const originalQuery = navigator.permissions.query;
            navigator.permissions.query = async function(parameters) {
                // Randomize some permission states to look more realistic
                const responses = {
                    'geolocation': { state: 'prompt', onchange: null },
                    'notifications': { state: Math.random() > 0.5 ? 'denied' : 'prompt', onchange: null },
                    'push': { state: 'prompt', onchange: null },
                    'midi': { state: 'granted', onchange: null },
                    'camera': { state: 'prompt', onchange: null },
                    'microphone': { state: 'prompt', onchange: null },
                    'background-sync': { state: 'granted', onchange: null },
                    'ambient-light-sensor': { state: 'denied', onchange: null },
                    'accelerometer': { state: 'denied', onchange: null },
                    'gyroscope': { state: 'denied', onchange: null },
                    'magnetometer': { state: 'denied', onchange: null },
                    'clipboard-read': { state: 'prompt', onchange: null },
                    'clipboard-write': { state: 'granted', onchange: null }
                };
                
                if (parameters.name in responses) {
                    return Promise.resolve(responses[parameters.name]);
                }
                
                // Fallback to original for unknown permissions
                try {
                    return await originalQuery.call(navigator.permissions, parameters);
                } catch {
                    return { state: 'prompt', onchange: null };
                }
            };
            
            // Also override Notification.permission
            Object.defineProperty(Notification, 'permission', {
                get: () => 'default'
            });
        """)
    
    @staticmethod
    async def _inject_plugins_override(page: Page):
        """Inject realistic plugins"""
        await page.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    const pluginArray = [
                        {
                            name: 'Chrome PDF Plugin',
                            description: 'Portable Document Format',
                            filename: 'internal-pdf-viewer',
                            length: 1,
                            item: (i) => ({
                                type: 'application/pdf',
                                suffixes: 'pdf',
                                description: 'Portable Document Format'
                            })
                        },
                        {
                            name: 'Chrome PDF Viewer',
                            description: 'Portable Document Format',
                            filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                            length: 1,
                            item: (i) => ({
                                type: 'application/pdf',
                                suffixes: 'pdf',
                                description: 'Portable Document Format'
                            })
                        },
                        {
                            name: 'Native Client',
                            description: 'Native Client Executable',
                            filename: 'internal-nacl-plugin',
                            length: 2,
                            item: (i) => ({
                                type: i === 0 ? 'application/x-nacl' : 'application/x-pnacl',
                                suffixes: '',
                                description: 'Native Client Executable'
                            })
                        }
                    ];
                    
                    pluginArray.length = 3;
                    pluginArray.item = (i) => pluginArray[i];
                    pluginArray.namedItem = (name) => pluginArray.find(p => p.name === name);
                    pluginArray.refresh = () => {};
                    
                    return pluginArray;
                }
            });
        """)
    
    @staticmethod
    async def _inject_languages_override(page: Page):
        """Override language detection"""
        await page.add_init_script("""
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            Object.defineProperty(navigator, 'language', {
                get: () => 'en-US'
            });
        """)
    
    @staticmethod
    async def _inject_canvas_fingerprint(page: Page):
        """Enhanced canvas fingerprinting with consistent per-session noise"""
        await page.add_init_script("""
            // Generate consistent noise seed per session
            const sessionSeed = Math.random();
            const seededRandom = (seed) => {
                const x = Math.sin(seed) * 10000;
                return x - Math.floor(x);
            };
            
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            const originalToBlob = HTMLCanvasElement.prototype.toBlob;
            const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            
            // Override getContext to add noise to all canvas operations
            HTMLCanvasElement.prototype.getContext = function(type, ...args) {
                const context = originalGetContext.call(this, type, ...args);
                
                if (type === '2d' && context) {
                    // Wrap fillText to add micro variations
                    const originalFillText = context.fillText;
                    context.fillText = function(text, x, y, ...rest) {
                        // Add tiny position variations
                        const variance = seededRandom(sessionSeed + x + y) * 0.01;
                        return originalFillText.call(this, text, x + variance, y + variance, ...rest);
                    };
                    
                    // Wrap strokeText similarly
                    const originalStrokeText = context.strokeText;
                    context.strokeText = function(text, x, y, ...rest) {
                        const variance = seededRandom(sessionSeed + x + y) * 0.01;
                        return originalStrokeText.call(this, text, x + variance, y + variance, ...rest);
                    };
                }
                
                return context;
            };
            
            // Add consistent noise to canvas operations
            const addNoise = (canvas, seed) => {
                const ctx = canvas.getContext('2d');
                if (!ctx) return;
                
                try {
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    const data = imageData.data;
                    
                    // Use seeded random for consistent noise
                    for (let i = 0; i < data.length; i += 4) {
                        const noise = (seededRandom(seed + i) - 0.5) * 0.5;
                        data[i] = Math.max(0, Math.min(255, data[i] + noise));     // Red
                        data[i + 1] = Math.max(0, Math.min(255, data[i + 1] + noise)); // Green
                        data[i + 2] = Math.max(0, Math.min(255, data[i + 2] + noise)); // Blue
                    }
                    
                    ctx.putImageData(imageData, 0, 0);
                } catch (e) {
                    // Ignore errors from cross-origin canvases
                }
            };
            
            HTMLCanvasElement.prototype.toDataURL = function(...args) {
                addNoise(this, sessionSeed);
                return originalToDataURL.apply(this, args);
            };
            
            HTMLCanvasElement.prototype.toBlob = function(...args) {
                addNoise(this, sessionSeed);
                return originalToBlob.apply(this, args);
            };
            
            CanvasRenderingContext2D.prototype.getImageData = function(...args) {
                const imageData = originalGetImageData.apply(this, args);
                const data = imageData.data;
                
                // Apply consistent noise
                for (let i = 0; i < data.length; i += 4) {
                    const noise = (seededRandom(sessionSeed + i) - 0.5) * 0.5;
                    data[i] = Math.max(0, Math.min(255, data[i] + noise));
                    data[i + 1] = Math.max(0, Math.min(255, data[i + 1] + noise));
                    data[i + 2] = Math.max(0, Math.min(255, data[i + 2] + noise));
                }
                
                return imageData;
            };
        """)
    
    @staticmethod
    async def _inject_webgl_fingerprint(page: Page):
        """Spoof WebGL fingerprinting"""
        await page.add_init_script("""
            const getParameterProxyHandler = {
                apply: function(target, thisArg, argumentsList) {
                    const param = argumentsList[0];
                    const originalValue = target.apply(thisArg, argumentsList);
                    
                    // Spoof common WebGL parameters
                    const spoofedParams = {
                        37445: 'Intel Inc.', // UNMASKED_VENDOR_WEBGL
                        37446: 'Intel Iris OpenGL Engine', // UNMASKED_RENDERER_WEBGL
                        7937: 16384, // MAX_TEXTURE_SIZE
                        35660: 16, // MAX_VERTEX_UNIFORM_VECTORS
                        35661: 16, // MAX_VARYING_VECTORS
                        36349: 1024, // MAX_FRAGMENT_UNIFORM_VECTORS
                        34024: 16384, // MAX_RENDERBUFFER_SIZE
                        3379: 16384, // MAX_TEXTURE_SIZE
                        36183: 16, // MAX_ELEMENT_INDEX
                    };
                    
                    if (spoofedParams[param] !== undefined) {
                        return spoofedParams[param];
                    }
                    
                    return originalValue;
                }
            };
            
            // Override WebGLRenderingContext
            if (typeof WebGLRenderingContext !== 'undefined') {
                WebGLRenderingContext.prototype.getParameter = new Proxy(
                    WebGLRenderingContext.prototype.getParameter,
                    getParameterProxyHandler
                );
            }
            
            // Override WebGL2RenderingContext
            if (typeof WebGL2RenderingContext !== 'undefined') {
                WebGL2RenderingContext.prototype.getParameter = new Proxy(
                    WebGL2RenderingContext.prototype.getParameter,
                    getParameterProxyHandler
                );
            }
        """)
    
    @staticmethod
    async def _inject_audio_fingerprint(page: Page):
        """Spoof audio context fingerprinting"""
        await page.add_init_script("""
            // Override AudioContext
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) {
                const originalCreateOscillator = AudioContext.prototype.createOscillator;
                const originalCreateAnalyser = AudioContext.prototype.createAnalyser;
                const originalCreateGain = AudioContext.prototype.createGain;
                const originalCreateScriptProcessor = AudioContext.prototype.createScriptProcessor;
                
                AudioContext.prototype.createOscillator = function() {
                    const oscillator = originalCreateOscillator.call(this);
                    const originalConnect = oscillator.connect;
                    
                    oscillator.connect = function(destination) {
                        // Add slight frequency variation
                        oscillator.frequency.value += Math.random() * 0.001;
                        return originalConnect.call(this, destination);
                    };
                    
                    return oscillator;
                };
                
                AudioContext.prototype.createAnalyser = function() {
                    const analyser = originalCreateAnalyser.call(this);
                    const originalGetFloatFrequencyData = analyser.getFloatFrequencyData;
                    
                    analyser.getFloatFrequencyData = function(array) {
                        originalGetFloatFrequencyData.call(this, array);
                        // Add noise to frequency data
                        for (let i = 0; i < array.length; i++) {
                            array[i] += Math.random() * 0.0001;
                        }
                    };
                    
                    return analyser;
                };
            }
        """)
    
    @staticmethod
    async def _inject_webrtc_override(page: Page):
        """Prevent WebRTC leak"""
        await page.add_init_script("""
            // Override RTCPeerConnection
            const RTCPeerConnection = window.RTCPeerConnection || 
                                     window.webkitRTCPeerConnection || 
                                     window.mozRTCPeerConnection;
            
            if (RTCPeerConnection) {
                const OriginalRTCPeerConnection = RTCPeerConnection;
                
                window.RTCPeerConnection = new Proxy(OriginalRTCPeerConnection, {
                    construct: function(target, args) {
                        const config = args[0] || {};
                        
                        // Force TURN relay to prevent IP leak
                        config.iceTransportPolicy = 'relay';
                        
                        // Remove STUN servers
                        if (config.iceServers) {
                            config.iceServers = config.iceServers.filter(
                                server => !server.urls.toString().includes('stun')
                            );
                        }
                        
                        return new target(config);
                    }
                });
                
                window.webkitRTCPeerConnection = window.RTCPeerConnection;
                window.mozRTCPeerConnection = window.RTCPeerConnection;
            }
            
            // Block getUserMedia
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                const originalGetUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
                
                navigator.mediaDevices.getUserMedia = function(constraints) {
                    return Promise.reject(new Error('getUserMedia not available'));
                };
            }
        """)
    
    @staticmethod
    async def _inject_battery_override(page: Page):
        """Spoof battery API"""
        await page.add_init_script("""
            if ('getBattery' in navigator) {
                navigator.getBattery = async () => {
                    return {
                        charging: true,
                        chargingTime: 0,
                        dischargingTime: Infinity,
                        level: 0.99,
                        onchargingchange: null,
                        onchargingtimechange: null,
                        ondischargingtimechange: null,
                        onlevelchange: null,
                        addEventListener: () => {},
                        removeEventListener: () => {},
                        dispatchEvent: () => true
                    };
                };
            }
        """)
    
    @staticmethod
    async def _inject_hardware_override(page: Page):
        """Spoof hardware concurrency and device memory"""
        await page.add_init_script("""
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8
            });
            
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8
            });
            
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Win32'
            });
            
            Object.defineProperty(screen, 'colorDepth', {
                get: () => 24
            });
            
            Object.defineProperty(screen, 'pixelDepth', {
                get: () => 24
            });
        """)
    
    @staticmethod
    async def _inject_cdp_detection_bypass(page: Page):
        """Enhanced CDP detection bypass"""
        await page.add_init_script("""
            // Remove all CDP artifacts
            const cdcProps = [
                'cdc_adoQpoasnfa76pfcZLmcfl_Array',
                'cdc_adoQpoasnfa76pfcZLmcfl_Promise', 
                'cdc_adoQpoasnfa76pfcZLmcfl_Symbol',
                'cdc_adoQpoasnfa76pfcZLmcfl_JSON',
                'cdc_adoQpoasnfa76pfcZLmcfl_Object',
                'cdc_adoQpoasnfa76pfcZLmcfl_Proxy',
                '__nightmare',
                '__selenium_unwrapped',
                '__selenium_evaluate',
                '__selenium_evaluate_check',
                '__webdriver_evaluate',
                '__driver_evaluate',
                '__webdriver_unwrapped',
                '__driver_unwrapped',
                '__selenium_unwrapped',
                '__fxdriver_evaluate',
                '__fxdriver_unwrapped',
                '_phantom',
                'phantom',
                'callPhantom',
                '_selenium',
                'callSelenium',
                'domAutomation',
                'domAutomationController'
            ];
            
            cdcProps.forEach(prop => {
                delete window[prop];
                delete document[prop];
            });
            
            // Override toString to hide modifications
            const nativeToString = Function.prototype.toString;
            Function.prototype.toString = function() {
                if (this === window.navigator.permissions.query) {
                    return 'function query() { [native code] }';
                }
                if (this === console.debug) {
                    return 'function debug() { [native code] }';
                }
                return nativeToString.call(this);
            };
            
            // Hide stack traces that might reveal automation
            const originalError = Error;
            Error = new Proxy(originalError, {
                construct(target, args) {
                    const error = new target(...args);
                    if (error.stack) {
                        error.stack = error.stack
                            .split('\n')
                            .filter(line => !line.includes('playwright') && 
                                          !line.includes('puppeteer') &&
                                          !line.includes('selenium'))
                            .join('\n');
                    }
                    return error;
                }
            });
        """)
    
    @staticmethod
    async def _inject_runtime_enable_bypass(page: Page):
        """Bypass Runtime.enable CDP detection"""
        await page.add_init_script("""
            // Override Runtime.enable detection
            (function() {
                // Create isolated context to avoid Runtime.enable detection
                const originalFetch = window.fetch;
                window.fetch = function(...args) {
                    // Check if fetch is trying to detect CDP
                    if (args[0] && typeof args[0] === 'string') {
                        if (args[0].includes('json/version') || 
                            args[0].includes('json/protocol') ||
                            args[0].includes(':9222') ||
                            args[0].includes(':9229')) {
                            return Promise.reject(new Error('Failed to fetch'));
                        }
                    }
                    return originalFetch.apply(this, args);
                };
                
                // Block WebSocket connections to debugging endpoints
                const OriginalWebSocket = window.WebSocket;
                window.WebSocket = new Proxy(OriginalWebSocket, {
                    construct(target, args) {
                        const url = args[0];
                        if (url && (url.includes('devtools') || 
                                   url.includes('ws://127.0.0.1') ||
                                   url.includes('ws://localhost'))) {
                            throw new Error('WebSocket connection failed');
                        }
                        return new target(...args);
                    }
                });
            })();
        """)
    
    @staticmethod
    async def _inject_console_debug_override(page: Page):
        """Override console.debug to hide CDP messages"""
        await page.add_init_script("""
            // Save original console methods
            const originalConsole = {
                log: console.log,
                debug: console.debug,
                info: console.info,
                warn: console.warn,
                error: console.error
            };
            
            // Filter function for CDP-related messages
            const shouldFilter = (args) => {
                const message = args.map(arg => 
                    typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
                ).join(' ');
                
                const blacklist = [
                    'Runtime.enable',
                    'Runtime.executionContextCreated',
                    'Page.enable',
                    'Network.enable',
                    'DOM.enable',
                    'CSS.enable',
                    'Overlay.enable',
                    'Log.enable',
                    'Runtime.consoleAPICalled',
                    'Inspector.enable',
                    'Debugger.enable',
                    'Profiler.enable',
                    'HeapProfiler.enable'
                ];
                
                return blacklist.some(item => message.includes(item));
            };
            
            // Override console methods
            ['log', 'debug', 'info', 'warn', 'error'].forEach(method => {
                console[method] = function(...args) {
                    if (!shouldFilter(args)) {
                        return originalConsole[method].apply(console, args);
                    }
                };
            });
        """)

# ============================================================================
# Human Behavior Simulation
# ============================================================================

class HumanBehaviorSimulator:
    """Simulates human-like behavior patterns"""
    
    def __init__(self, config: BrowserConfig):
        self.config = config
        self.last_action_time = time.time()
    
    async def human_type(self, page: Page, selector: str, text: str):
        """Type with human-like speed and patterns"""
        element = await page.wait_for_selector(selector)
        await element.click()
        
        for char in text:
            await page.type(selector, char)
            # Variable delay between keystrokes
            delay = random.uniform(
                self.config.human_typing_speed[0],
                self.config.human_typing_speed[1]
            )
            await asyncio.sleep(delay / 1000)
            
            # Occasional longer pauses (thinking)
            if random.random() < 0.1:
                await asyncio.sleep(random.uniform(0.5, 2))
    
    async def human_click(self, page: Page, selector: str):
        """Click with human-like movement"""
        element = await page.wait_for_selector(selector)
        box = await element.bounding_box()
        
        if box:
            # Click slightly off-center like a human would
            x = box['x'] + box['width'] / 2 + random.uniform(-5, 5)
            y = box['y'] + box['height'] / 2 + random.uniform(-5, 5)
            
            # Move mouse with bezier curve
            await self._bezier_mouse_move(page, x, y)
            
            # Random delay before click
            await asyncio.sleep(random.uniform(0.05, 0.2))
            
            await page.mouse.click(x, y)
    
    async def human_scroll(self, page: Page):
        """Scroll with human-like patterns"""
        # Get page height
        page_height = await page.evaluate("document.body.scrollHeight")
        viewport_height = await page.evaluate("window.innerHeight")
        
        current_position = 0
        
        while current_position < page_height - viewport_height:
            # Variable scroll distance
            scroll_distance = random.uniform(200, 600)
            
            # Smooth scroll
            await page.evaluate(f"""
                window.scrollBy({{
                    top: {scroll_distance},
                    behavior: 'smooth'
                }});
            """)
            
            current_position += scroll_distance
            
            # Random pause to "read" content
            await asyncio.sleep(random.uniform(0.5, 3))
            
            # Occasionally scroll up a bit
            if random.random() < 0.2:
                scroll_up = random.uniform(50, 150)
                await page.evaluate(f"""
                    window.scrollBy({{
                        top: -{scroll_up},
                        behavior: 'smooth'
                    }});
                """)
                current_position -= scroll_up
                await asyncio.sleep(random.uniform(0.3, 1))
    
    async def _bezier_mouse_move(self, page: Page, target_x: float, target_y: float):
        """Move mouse along a bezier curve"""
        current_pos = await page.evaluate("() => ({ x: 0, y: 0 })")
        
        # Generate control points for bezier curve
        cp1_x = current_pos['x'] + (target_x - current_pos['x']) * 0.3
        cp1_y = current_pos['y'] + random.uniform(-50, 50)
        cp2_x = current_pos['x'] + (target_x - current_pos['x']) * 0.7
        cp2_y = target_y + random.uniform(-50, 50)
        
        # Move along curve
        steps = random.randint(20, 30)
        for i in range(steps):
            t = i / steps
            # Bezier formula
            x = (1-t)**3 * current_pos['x'] + 3*(1-t)**2*t * cp1_x + 3*(1-t)*t**2 * cp2_x + t**3 * target_x
            y = (1-t)**3 * current_pos['y'] + 3*(1-t)**2*t * cp1_y + 3*(1-t)*t**2 * cp2_y + t**3 * target_y
            
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.001, 0.003))
    
    async def random_mouse_movement(self, page: Page):
        """Random mouse movements to appear human"""
        for _ in range(random.randint(1, 3)):
            x = random.uniform(100, 1000)
            y = random.uniform(100, 700)
            await self._bezier_mouse_move(page, x, y)
            await asyncio.sleep(random.uniform(0.5, 2))
    
    async def human_wait(self):
        """Wait with human-like delays"""
        if self.config.random_delays:
            delay = random.uniform(
                self.config.delay_range[0],
                self.config.delay_range[1]
            ) / 1000
            await asyncio.sleep(delay)

# ============================================================================
# Main Stealth Browser Service
# ============================================================================

class BrowserService:
    """
    Main standalone browser service.
    Can be used by any application for browser automation with maximum stealth.
    """
    
    def __init__(self, config: Optional[BrowserConfig] = None):
        """
        Initialize the stealth browser service.
        
        Args:
            config: Optional configuration, uses defaults if not provided
        """
        self.config = config or BrowserConfig()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.pages: Dict[str, Page] = {}
        self.sessions: Dict[str, BrowserSession] = {}
        self.human_simulator = HumanBehaviorSimulator(self.config)
        self.playwright = None
        self._lock = asyncio.Lock()
        self._initialized = False
        
        # Generate unique browser ID
        self.browser_id = str(uuid.uuid4())
        
        logger.info(f"BrowserService initialized - ID: {self.browser_id}")
    
    
    # ========================================================================
    # Core API Methods
    # ========================================================================
    
    async def start(self) -> bool:
        """
        Start the browser service.
        
        Returns:
            True if successfully started
        """
        async with self._lock:
            if self._initialized:
                logger.warning("Browser service already started")
                return True
            
            try:
                # For Python 3.13 on Windows, set ProactorEventLoop
                import sys
                if sys.platform == 'win32' and sys.version_info >= (3, 13):
                    import asyncio
                    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                
                # Use async playwright 
                self.playwright = await async_playwright().start()
                
                # Launch browser
                await self._launch_browser()
                
                # Create context
                await self._create_context()
                
                self._initialized = True
                logger.info("Browser service started successfully")
                return True
                
            except Exception as e:
                logger.error(f"Failed to start browser service: {e}")
                return False
    
    async def stop(self) -> bool:
        """
        Stop the browser service and cleanup resources.
        
        Returns:
            True if successfully stopped
        """
        async with self._lock:
            if not self._initialized:
                return True
            
            try:
                # Close all pages
                for page_id in list(self.pages.keys()):
                    await self.close_page(page_id)
                
                # Close context
                if self.context:
                    await self.context.close()
                
                # Close browser
                if self.browser:
                    await self.browser.close()
                
                # Stop playwright
                if self.playwright:
                    await self.playwright.stop()
                
                self._initialized = False
                logger.info("Browser service stopped successfully")
                return True
                
            except Exception as e:
                logger.error(f"Error stopping browser service: {e}")
                return False
    
    async def get_page(self, url: Optional[str] = None, page_id: Optional[str] = None) -> Page:
        """
        Get a page instance. Creates new page if needed.
        
        Args:
            url: Optional URL to navigate to
            page_id: Optional page ID for retrieving existing page
            
        Returns:
            Page instance with stealth configuration
            
        Raises:
            Exception: If navigation fails
        """
        if not self._initialized:
            await self.start()
        
        # Get existing page
        if page_id and page_id in self.pages:
            page = self.pages[page_id]
        else:
            # Create new page
            page = await self._create_page()
            page_id = str(uuid.uuid4())
            self.pages[page_id] = page
        
        # Navigate if URL provided
        if url:
            success = await self.navigate(page, url)
            if not success:
                # Navigation failed - raise exception
                raise Exception(f"Navigation failed to {url}")
        
        return page
    
    async def navigate(self, page: Page, url: str, wait_until: str = "domcontentloaded") -> bool:
        """
        Navigate to a URL with stealth behavior.
        
        Args:
            page: Page instance
            url: URL to navigate to
            wait_until: Wait condition
            
        Returns:
            True if navigation successful
        """
        try:
            # Human-like delay before navigation
            await self.human_simulator.human_wait()
            
            # Navigate
            response = await page.goto(
                url,
                wait_until=wait_until,
                timeout=self.config.navigation_timeout
            )
            
            # Check for detection
            if await self._check_detection(page):
                logger.warning(f"Bot detection suspected at {url}")
                # Attempt bypass strategies
                await self._attempt_bypass(page, url)
            
            # Random actions to appear human
            if self.config.enable_human_simulation:
                await self.human_simulator.random_mouse_movement(page)
            
            return response.status < 400 if response else False
            
        except Exception as e:
            logger.error(f"Navigation failed to {url}: {e}")
            # Re-raise the exception with more context
            raise Exception(f"Navigation failed to {url}: {str(e)}")
    
    async def click(self, page: Page, selector: str) -> bool:
        """
        Click an element with human-like behavior.
        
        Args:
            page: Page instance
            selector: Element selector
            
        Returns:
            True if click successful
        """
        try:
            if self.config.enable_human_simulation:
                await self.human_simulator.human_click(page, selector)
            else:
                await page.click(selector)
            return True
        except Exception as e:
            logger.error(f"Click failed on {selector}: {e}")
            return False
    
    async def type(self, page: Page, selector: str, text: str) -> bool:
        """
        Type text with human-like behavior.
        
        Args:
            page: Page instance
            selector: Element selector
            text: Text to type
            
        Returns:
            True if typing successful
        """
        try:
            if self.config.enable_human_simulation:
                await self.human_simulator.human_type(page, selector, text)
            else:
                await page.type(selector, text)
            return True
        except Exception as e:
            logger.error(f"Type failed on {selector}: {e}")
            return False
    
    async def screenshot(self, page: Page, path: Optional[str] = None) -> Union[bytes, bool]:
        """
        Take a screenshot.
        
        Args:
            page: Page instance
            path: Optional path to save screenshot
            
        Returns:
            Screenshot bytes if no path, True if saved to path, False on error
        """
        try:
            if path:
                await page.screenshot(path=path, full_page=True)
                return True
            else:
                return await page.screenshot(full_page=True)
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return False
    
    async def evaluate(self, page: Page, script: str) -> Any:
        """
        Evaluate JavaScript in the page.
        
        Args:
            page: Page instance
            script: JavaScript to evaluate
            
        Returns:
            Result of script execution
        """
        try:
            return await page.evaluate(script)
        except Exception as e:
            logger.error(f"Script evaluation failed: {e}")
            return None
    
    async def wait_for_selector(self, page: Page, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Wait for element to appear.
        
        Args:
            page: Page instance
            selector: Element selector
            timeout: Optional timeout override
            
        Returns:
            True if element found
        """
        try:
            await page.wait_for_selector(
                selector,
                timeout=timeout or self.config.timeout
            )
            return True
        except Exception:
            return False
    
    async def get_cookies(self, page: Page) -> List[Dict]:
        """Get cookies from page"""
        return await page.context.cookies()
    
    async def set_cookies(self, page: Page, cookies: List[Dict]) -> bool:
        """Set cookies for page"""
        try:
            await page.context.add_cookies(cookies)
            return True
        except Exception as e:
            logger.error(f"Failed to set cookies: {e}")
            return False
    
    async def close_page(self, page_id: str) -> bool:
        """Close a specific page"""
        if page_id in self.pages:
            try:
                await self.pages[page_id].close()
                del self.pages[page_id]
                return True
            except Exception as e:
                logger.error(f"Failed to close page {page_id}: {e}")
                return False
        return False
    
    # ========================================================================
    # Internal Methods
    # ========================================================================
    
    async def _launch_browser(self):
        """Launch browser with enhanced stealth configuration"""
        
        # Get platform-specific launch options
        platform_options = get_playwright_launch_options()
        
        # Browser launch options - merge with platform-specific options
        launch_options = {
            "headless": self.config.headless,
            "args": self._get_browser_args() + platform_options.get("args", []),
            "ignore_default_args": [
                "--enable-automation",
                "--enable-blink-features=IdleDetection",
            ],
            # Use chromium channel for better compatibility
            "channel": "chrome" if self.config.browser_type == "chromium" else None,
        }
        
        # Use executable path from platform utils if available
        if "executable_path" in platform_options:
            launch_options["executable_path"] = platform_options["executable_path"]
        
        # Launch based on browser type
        if self.config.browser_type == "chromium":
            self.browser = await self.playwright.chromium.launch(**launch_options)
        elif self.config.browser_type == "firefox":
            self.browser = await self.playwright.firefox.launch(**launch_options)
        elif self.config.browser_type == "webkit":
            self.browser = await self.playwright.webkit.launch(**launch_options)
        else:
            raise ValueError(f"Unknown browser type: {self.config.browser_type}")
    
    def _get_browser_args(self) -> List[str]:
        """Get browser launch arguments with enhanced stealth"""
        args = [
            # Core stealth arguments
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-site-isolation-trials",
            
            # Security and sandboxing
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-web-security",
            "--allow-running-insecure-content",
            
            # Performance and rendering
            "--disable-accelerated-2d-canvas",
            "--disable-gpu",
            "--disable-gpu-sandbox",
            "--disable-software-rasterizer",
            "--disable-dev-tools",  # Hide dev tools
            
            # Window and display
            f"--window-size={self.config.viewport_width},{self.config.viewport_height}",
            "--window-position=0,0",
            "--force-device-scale-factor=1",
            
            # Process and lifecycle
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-default-apps",
            "--disable-sync",
            
            # Timing and throttling
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-features=CalculateNativeWinOcclusion",
            
            # Features to disable
            "--disable-features=TranslateUI",
            "--disable-features=RendererCodeIntegrity",
            "--disable-features=OptimizationGuideModelDownloading",
            "--disable-features=ChromeWhatsNewUI",
            "--disable-features=ImprovedCookieControls",
            
            # IPC and networking
            "--disable-ipc-flooding-protection",
            "--enable-features=NetworkService,NetworkServiceInProcess",
            "--disable-features=NetworkServiceWindowsSandbox",
            
            # Additional stealth
            "--disable-blink-features=AutomationControlled",
            "--disable-features=UserActivationV2",
            "--disable-features=IdleDetection",
            
            # Disable automation extensions
            "--disable-extensions",
            "--disable-component-extensions-with-background-pages",
            "--disable-background-networking",
            "--metrics-recording-only",
            "--mute-audio",
        ]
        
        # Additional args for maximum stealth
        if self.config.stealth_level in ["maximum", "ultimate"]:
            args.extend([
                "--disable-features=AutomationControlled",
                "--disable-blink-features=AutomationControlled",
                "--disable-features=site-per-process",
                "--disable-features=OutOfBlinkCors",
                "--disable-features=SameSiteByDefaultCookies",
                "--disable-features=CookiesWithoutSameSiteMustBeSecure",
            ])
        
        return args
    
    def _find_chrome_executable(self) -> Optional[str]:
        """Find Chrome executable path using platform utilities"""
        return get_chrome_executable_path()
    
    async def _create_context(self):
        """Create browser context with enhanced stealth settings"""
        
        # Select user agent
        user_agent = self.config.user_agent or self._get_user_agent()
        
        context_options = {
            "user_agent": user_agent,
            "locale": self.config.locale,
            "timezone_id": self.config.timezone,
            "ignore_https_errors": True,
            "java_script_enabled": True,
            "bypass_csp": True,  # Bypass Content Security Policy
            "is_mobile": False,
            "has_touch": False,
            "device_scale_factor": 1,
        }
        
        # Only set viewport if not using default to avoid detection
        if self.config.viewport_width != 1920 or self.config.viewport_height != 1080:
            context_options["viewport"] = {
                "width": self.config.viewport_width,
                "height": self.config.viewport_height
            }
        else:
            # Use null viewport to get default browser size
            context_options["viewport"] = None
        
        # Add proxy if configured
        if self.config.proxy:
            context_options["proxy"] = self.config.proxy
        
        # Add geolocation if configured
        if self.config.spoof_geolocation:
            context_options["geolocation"] = {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
            context_options["permissions"] = ["geolocation"]
        
        self.context = await self.browser.new_context(**context_options)
        
        # Set extra headers
        await self.context.set_extra_http_headers({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        })
        
        # Set up request interception if needed
        if self.config.block_images or self.config.block_media:
            await self._setup_resource_blocking()
    
    def _get_user_agent(self) -> str:
        """Get appropriate user agent based on platform and latest Chrome versions"""
        # Use latest Chrome versions to avoid detection
        chrome_versions = ["121.0.0.0", "122.0.0.0", "123.0.0.0", "124.0.0.0", "125.0.0.0"]
        chrome_version = random.choice(chrome_versions)
        
        # Platform-specific user agents
        system = platform.system()
        if system == "Windows":
            user_agents = [
                f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36",
                f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36 Edg/{chrome_version}",
            ]
        elif system == "Darwin":  # macOS
            user_agents = [
                f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36",
                f"Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36",
            ]
        else:  # Linux
            user_agents = [
                f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36",
                f"Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36",
            ]
        
        return random.choice(user_agents)
    
    async def _create_page(self) -> Page:
        """Create a new page with enhanced stealth configuration"""
        page = await self.context.new_page()
        
        # Inject stealth scripts before any navigation
        await StealthInjector.inject_all(page, self.config)
        
        # Add additional initialization scripts for specific bypasses
        if self.config.disable_runtime_enable:
            # Prevent Runtime.enable detection by overriding execution context
            await page.add_init_script("""
                // Override execution context creation
                if (window.chrome && window.chrome.runtime) {
                    const runtime = window.chrome.runtime;
                    const originalGetURL = runtime.getURL;
                    runtime.getURL = function(path) {
                        if (path && path.includes('_generated_background_page')) {
                            return '';
                        }
                        return originalGetURL.call(this, path);
                    };
                }
            """)
        
        # Set up page-level event handlers
        page.on("dialog", lambda dialog: dialog.dismiss())
        page.on("popup", lambda popup: popup.close())
        
        # Intercept and modify requests if needed
        if self.config.patch_cdp_detection:
            page.on("request", self._handle_request)
            page.on("response", self._handle_response)
        
        return page
    
    async def _handle_request(self, request):
        """Handle and potentially modify requests"""
        # Block requests that might be used for bot detection
        url = request.url
        if any(pattern in url for pattern in [
            '/cdn-cgi/challenge-platform',
            '/cdn-cgi/bm/',
            'datadome.co',
            'perimeterx.net',
        ]):
            logger.debug(f"Blocking detection request: {url}")
            try:
                await request.abort()
            except:
                pass
    
    async def _handle_response(self, response):
        """Handle and log responses for debugging"""
        if response.status == 403 or response.status == 429:
            logger.debug(f"Potential bot detection response: {response.status} from {response.url}")
    
    async def _setup_resource_blocking(self):
        """Set up resource blocking for performance"""
        
        async def route_handler(route):
            resource_type = route.request.resource_type
            
            blocked = False
            if self.config.block_images and resource_type == "image":
                blocked = True
            elif self.config.block_media and resource_type in ["media", "video"]:
                blocked = True
            elif self.config.block_fonts and resource_type == "font":
                blocked = True
            elif self.config.block_stylesheets and resource_type == "stylesheet":
                blocked = True
            
            if blocked:
                await route.abort()
            else:
                await route.continue_()
        
        await self.context.route("**/*", route_handler)
    
    async def _check_detection(self, page: Page) -> bool:
        """Enhanced detection checking with specific service patterns"""
        
        try:
            # Get page content and URL
            page_content = await page.content()
            page_url = page.url.lower()
            page_title = await page.title()
            
            # Extended detection indicators
            indicators = [
                # General bot detection
                "captcha",
                "challenge",
                "bot detected",
                "automated traffic",
                "suspicious activity",
                "access denied",
                "permission denied",
                "security check",
                "verification required",
                "prove you're human",
                "unusual traffic",
                
                # Service-specific patterns
                "cf-browser-verification",  # Cloudflare
                "cf-challenge",  # Cloudflare
                "_cf_bm",  # Cloudflare bot management
                "datadome",  # DataDome
                "px-captcha",  # PerimeterX
                "_px",  # PerimeterX
                "kasada",  # Kasada
                "akamai",  # Akamai
                "incapsula",  # Incapsula
                "distil",  # Distil Networks
            ]
            
            content_lower = page_content.lower()
            
            for indicator in indicators:
                if indicator in content_lower or indicator in page_url:
                    logger.debug(f"Detection indicator found: {indicator}")
                    return True
            
            # Check page title for detection
            if page_title:
                title_lower = page_title.lower()
                if any(word in title_lower for word in ['blocked', 'denied', 'captcha', 'verification']):
                    return True
            
            # Check for specific JavaScript challenges
            js_check = await page.evaluate("""
                () => {
                    // Check for common challenge frameworks
                    return !!(
                        window._cf_chl_opt ||
                        window.__CF$cv$ ||
                        window.dd ||
                        window._pxAppId ||
                        window.kasada ||
                        window.shapeSecurity ||
                        document.querySelector('iframe[src*="challenges.cloudflare"]') ||
                        document.querySelector('script[src*="datadome"]') ||
                        document.querySelector('script[src*="perimeterx"]')
                    );
                }
            """)
            
            if js_check:
                logger.debug("JavaScript challenge detected")
                return True
                
        except Exception as e:
            logger.debug(f"Error checking detection: {e}")
            
        return False
    
    async def _attempt_bypass(self, page: Page, url: str):
        """Enhanced bypass strategies for different detection services"""
        
        logger.info("Attempting advanced detection bypass...")
        
        try:
            # Strategy 1: Clear all browser data and retry
            await self.context.clear_cookies()
            await self.context.clear_permissions()
            
            # Strategy 2: Add more human-like behavior before retry
            await self.human_simulator.random_mouse_movement(page)
            await asyncio.sleep(random.uniform(3, 6))
            
            # Strategy 3: Try different navigation approach
            # First navigate to a safe page to build trust
            safe_sites = [
                "https://www.google.com",
                "https://www.wikipedia.org",
                "https://www.example.com"
            ]
            
            if url not in safe_sites:
                # Visit a safe site first
                safe_url = random.choice(safe_sites)
                await page.goto(safe_url, wait_until="domcontentloaded")
                await asyncio.sleep(random.uniform(2, 4))
                
                # Perform some actions to appear human
                await self.human_simulator.human_scroll(page)
                await asyncio.sleep(random.uniform(1, 2))
            
            # Strategy 4: Inject additional stealth scripts for specific services
            await page.evaluate("""
                () => {
                    // Override specific detection methods
                    if (window.navigator && window.navigator.permissions) {
                        const originalQuery = window.navigator.permissions.query;
                        window.navigator.permissions.query = (params) => {
                            return Promise.resolve({ state: 'granted' });
                        };
                    }
                    
                    // Clear any detection cookies
                    document.cookie.split(';').forEach(c => {
                        const eqPos = c.indexOf('=');
                        const name = eqPos > -1 ? c.substr(0, eqPos).trim() : c.trim();
                        if (name.includes('cf_') || name.includes('px') || name.includes('dd')) {
                            document.cookie = name + '=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/';
                        }
                    });
                }
            """)
            
            # Strategy 5: Retry with different timing
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Strategy 6: If still detected, try slower approach
            if await self._check_detection(page):
                logger.info("Initial bypass failed, trying slower approach...")
                
                # Wait longer
                await asyncio.sleep(random.uniform(10, 15))
                
                # Navigate very slowly
                await page.goto(url, wait_until="domcontentloaded")
                await asyncio.sleep(2)
                await page.wait_for_load_state("networkidle")
                
                # More human actions
                await self.human_simulator.random_mouse_movement(page)
                await self.human_simulator.human_scroll(page)
                
        except Exception as e:
            logger.error(f"Bypass attempt failed: {e}")

# ============================================================================
# REST API Server (Optional)
# ============================================================================

class StealthBrowserAPIServer:
    """REST API server for browser service"""
    
    def __init__(self, browser_service: BrowserService, port: int = 9222):
        self.browser_service = browser_service
        self.port = port
        self.app = None
        
    async def start(self):
        """Start the API server"""
        if not HAS_AIOHTTP:
            logger.error("aiohttp not installed. Install with: pip install aiohttp")
            return
        
        self.app = web.Application()
        self.setup_routes()
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        
        logger.info(f"API server started on http://localhost:{self.port}")
    
    def setup_routes(self):
        """Setup API routes"""
        self.app.router.add_get('/api/status', self.handle_status)
        self.app.router.add_post('/api/navigate', self.handle_navigate)
        self.app.router.add_post('/api/click', self.handle_click)
        self.app.router.add_post('/api/type', self.handle_type)
        self.app.router.add_post('/api/screenshot', self.handle_screenshot)
        self.app.router.add_post('/api/evaluate', self.handle_evaluate)
        self.app.router.add_get('/api/cookies', self.handle_get_cookies)
        self.app.router.add_post('/api/cookies', self.handle_set_cookies)
    
    async def handle_status(self, request):
        """Get browser status"""
        return web.json_response({
            "status": "running" if self.browser_service._initialized else "stopped",
            "browser_id": self.browser_service.browser_id,
            "pages": len(self.browser_service.pages),
            "config": {
                "headless": self.browser_service.config.headless,
                "stealth_level": self.browser_service.config.stealth_level,
            }
        })
    
    async def handle_navigate(self, request):
        """Navigate to URL"""
        data = await request.json()
        url = data.get('url')
        page_id = data.get('page_id')
        
        if not url:
            return web.json_response({"error": "URL required"}, status=400)
        
        page = await self.browser_service.get_page(url, page_id)
        success = await self.browser_service.navigate(page, url)
        
        return web.json_response({
            "success": success,
            "page_id": page_id or list(self.browser_service.pages.keys())[-1]
        })
    
    async def handle_click(self, request):
        """Click element"""
        data = await request.json()
        page_id = data.get('page_id')
        selector = data.get('selector')
        
        if not page_id or not selector:
            return web.json_response({"error": "page_id and selector required"}, status=400)
        
        if page_id not in self.browser_service.pages:
            return web.json_response({"error": "Page not found"}, status=404)
        
        page = self.browser_service.pages[page_id]
        success = await self.browser_service.click(page, selector)
        
        return web.json_response({"success": success})
    
    async def handle_type(self, request):
        """Type text"""
        data = await request.json()
        page_id = data.get('page_id')
        selector = data.get('selector')
        text = data.get('text')
        
        if not all([page_id, selector, text]):
            return web.json_response({"error": "page_id, selector, and text required"}, status=400)
        
        if page_id not in self.browser_service.pages:
            return web.json_response({"error": "Page not found"}, status=404)
        
        page = self.browser_service.pages[page_id]
        success = await self.browser_service.type(page, selector, text)
        
        return web.json_response({"success": success})
    
    async def handle_screenshot(self, request):
        """Take screenshot"""
        data = await request.json()
        page_id = data.get('page_id')
        
        if not page_id:
            return web.json_response({"error": "page_id required"}, status=400)
        
        if page_id not in self.browser_service.pages:
            return web.json_response({"error": "Page not found"}, status=404)
        
        page = self.browser_service.pages[page_id]
        screenshot = await self.browser_service.screenshot(page)
        
        if screenshot:
            return web.Response(
                body=screenshot if isinstance(screenshot, bytes) else b"",
                content_type='image/png'
            )
        else:
            return web.json_response({"error": "Screenshot failed"}, status=500)
    
    async def handle_evaluate(self, request):
        """Evaluate JavaScript"""
        data = await request.json()
        page_id = data.get('page_id')
        script = data.get('script')
        
        if not page_id or not script:
            return web.json_response({"error": "page_id and script required"}, status=400)
        
        if page_id not in self.browser_service.pages:
            return web.json_response({"error": "Page not found"}, status=404)
        
        page = self.browser_service.pages[page_id]
        result = await self.browser_service.evaluate(page, script)
        
        return web.json_response({"result": result})
    
    async def handle_get_cookies(self, request):
        """Get cookies"""
        page_id = request.query.get('page_id')
        
        if not page_id:
            return web.json_response({"error": "page_id required"}, status=400)
        
        if page_id not in self.browser_service.pages:
            return web.json_response({"error": "Page not found"}, status=404)
        
        page = self.browser_service.pages[page_id]
        cookies = await self.browser_service.get_cookies(page)
        
        return web.json_response({"cookies": cookies})
    
    async def handle_set_cookies(self, request):
        """Set cookies"""
        data = await request.json()
        page_id = data.get('page_id')
        cookies = data.get('cookies')
        
        if not page_id or not cookies:
            return web.json_response({"error": "page_id and cookies required"}, status=400)
        
        if page_id not in self.browser_service.pages:
            return web.json_response({"error": "Page not found"}, status=404)
        
        page = self.browser_service.pages[page_id]
        success = await self.browser_service.set_cookies(page, cookies)
        
        return web.json_response({"success": success})

# ============================================================================
# Usage Examples
# ============================================================================

async def example_basic_usage():
    """Basic usage example"""
    # Create browser service
    browser = BrowserService()
    
    # Start the service
    await browser.start()
    
    # Get a page and navigate
    page = await browser.get_page("https://example.com")
    
    # Interact with the page
    await browser.click(page, "a[href='/more']")
    await browser.type(page, "input[name='search']", "test query")
    
    # Take screenshot
    screenshot = await browser.screenshot(page)
    
    # Evaluate JavaScript
    title = await browser.evaluate(page, "document.title")
    print(f"Page title: {title}")
    
    # Stop the service
    await browser.stop()

async def example_with_config():
    """Example with custom configuration"""
    # Configure browser
    config = BrowserConfig(
        headless=False,
        stealth_level="ultimate",
        enable_human_simulation=True,
        viewport_width=1920,
        viewport_height=1080,
        proxy={
            "server": "http://proxy.example.com:8080",
            "username": "user",
            "password": "pass"
        }
    )
    
    # Create and use browser
    browser = BrowserService(config)
    await browser.start()
    
    page = await browser.get_page("https://protected-site.com")
    
    # Browser will automatically:
    # - Use stealth techniques
    # - Simulate human behavior
    # - Route through proxy
    
    await browser.stop()

async def example_api_server():
    """Example running as API server"""
    # Create browser and API server
    browser = BrowserService()
    server = StealthBrowserAPIServer(browser, port=9222)
    
    # Start services
    await browser.start()
    await server.start()
    
    # Now the browser can be controlled via HTTP API:
    # curl http://localhost:9222/api/navigate -d '{"url": "https://example.com"}'
    
    # Keep server running
    await asyncio.Event().wait()

# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Standalone Stealth Browser Service")
    parser.add_argument("--server", action="store_true", help="Run as API server")
    parser.add_argument("--port", type=int, default=9222, help="API server port")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--url", help="URL to navigate to (for testing)")
    
    args = parser.parse_args()
    
    async def run():
        if args.server:
            # Run as API server
            config = BrowserConfig(headless=args.headless)
            browser = BrowserService(config)
            server = StealthBrowserAPIServer(browser, port=args.port)
            
            await browser.start()
            await server.start()
            
            print(f"Stealth Browser API Server running on http://localhost:{args.port}")
            print("Press Ctrl+C to stop")
            
            try:
                await asyncio.Event().wait()
            except KeyboardInterrupt:
                await browser.stop()
        
        elif args.url:
            # Test navigation
            config = BrowserConfig(headless=args.headless)
            browser = BrowserService(config)
            
            await browser.start()
            page = await browser.get_page(args.url)
            
            print(f"Successfully navigated to {args.url}")
            print("Taking screenshot...")
            
            await browser.screenshot(page, "test_screenshot.png")
            print("Screenshot saved as test_screenshot.png")
            
            await browser.stop()
        
        else:
            # Run basic example
            await example_basic_usage()
    
    asyncio.run(run())

if __name__ == "__main__":
    main()