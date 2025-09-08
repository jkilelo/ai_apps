"""Stealth system with plugin architecture for bot evasion"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from playwright.async_api import BrowserContext, Page
from loguru import logger
import json


class IStealthPlugin(ABC):
    """Abstract interface for stealth plugins"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Return plugin name for identification"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return plugin description"""
        pass
    
    @abstractmethod
    async def apply_to_context(self, context: BrowserContext) -> None:
        """Apply stealth modifications to browser context"""
        pass
    
    @abstractmethod
    async def apply_to_page(self, page: Page) -> None:
        """Apply stealth modifications to specific page"""
        pass
    
    @abstractmethod
    def get_priority(self) -> int:
        """Return priority for plugin execution order (lower = earlier)"""
        pass


class WebDriverPlugin(IStealthPlugin):
    """Hide webdriver detection flag"""
    
    def get_name(self) -> str:
        return "webdriver_flag"
    
    def get_description(self) -> str:
        return "Removes navigator.webdriver flag and WebDriver traces"
    
    def get_priority(self) -> int:
        return 1
    
    async def apply_to_context(self, context: BrowserContext) -> None:
        await context.add_init_script("""
            // Completely remove webdriver property from navigator
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
                set: () => {},
                enumerable: false,
                configurable: true
            });
            
            // Remove webdriver from prototype chain
            if ('webdriver' in Navigator.prototype) {
                delete Navigator.prototype.webdriver;
            }
            
            // Remove automation flags that WebDriver sets
            const automationFlags = [
                'cdc_adoQpoasnfa76pfcZLmcfl_Array',
                'cdc_adoQpoasnfa76pfcZLmcfl_Promise', 
                'cdc_adoQpoasnfa76pfcZLmcfl_Symbol',
                'cdc_adoQpoasnfa76pfcZLmcfl_JSON',
                'cdc_adoQpoasnfa76pfcZLmcfl_Object',
                'cdc_adoQpoasnfa76pfcZLmcfl_Proxy',
                'cdc_adoQpoasnfa76pfcZLmcfl_Reflect'
            ];
            
            automationFlags.forEach(flag => {
                if (window[flag]) {
                    delete window[flag];
                }
            });
            
            // Override document.documentElement.getAttribute to hide automation
            const originalGetAttribute = document.documentElement.getAttribute;
            document.documentElement.getAttribute = function(name) {
                if (name === 'webdriver') {
                    return null;
                }
                return originalGetAttribute.call(this, name);
            };
            
            // Remove selenium indicators
            const seleniumVars = ['$cdc_asdjflasutopfhvcZLmcfl_', '$chrome_asyncScriptInfo'];
            seleniumVars.forEach(name => {
                if (window[name]) {
                    delete window[name];
                }
            });
            
            // Override toString to hide traces
            if (navigator.webdriver !== undefined) {
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                    enumerable: false,
                    configurable: false
                });
            }
        """)
    
    async def apply_to_page(self, page: Page) -> None:
        await page.evaluate("""
            // Ensure webdriver is completely undefined
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
                set: () => {},
                enumerable: false,
                configurable: true
            });
            
            // Double-check webdriver removal
            if ('webdriver' in navigator) {
                try {
                    delete navigator.webdriver;
                } catch(e) {
                    // Redefine if delete fails
                    Object.defineProperty(navigator, 'webdriver', {
                        value: undefined,
                        writable: false,
                        enumerable: false,
                        configurable: false
                    });
                }
            }
        """)


class ChromeRuntimePlugin(IStealthPlugin):
    """Add Chrome runtime objects"""
    
    def get_name(self) -> str:
        return "chrome_runtime"
    
    def get_description(self) -> str:
        return "Adds Chrome-specific runtime objects"
    
    def get_priority(self) -> int:
        return 2
    
    async def apply_to_context(self, context: BrowserContext) -> None:
        await context.add_init_script("""
            // Add chrome object
            if (!window.chrome) {
                window.chrome = {
                    runtime: {
                        connect: () => {},
                        sendMessage: () => {},
                        onMessage: {
                            addListener: () => {}
                        }
                    },
                    loadTimes: () => ({
                        requestTime: Date.now() / 1000,
                        startLoadTime: Date.now() / 1000,
                        commitLoadTime: Date.now() / 1000,
                        finishDocumentLoadTime: Date.now() / 1000,
                        finishLoadTime: Date.now() / 1000,
                        firstPaintTime: Date.now() / 1000,
                        firstPaintAfterLoadTime: 0,
                        navigationType: "Other",
                        wasFetchedViaSpdy: false,
                        wasNpnNegotiated: false,
                        npnNegotiatedProtocol: "",
                        wasAlternateProtocolAvailable: false,
                        connectionInfo: "http/1.1"
                    }),
                    csi: () => ({
                        onloadT: Date.now(),
                        pageT: Date.now(),
                        startE: Date.now() - 100,
                        tran: 1
                    })
                };
            }
        """)
    
    async def apply_to_page(self, page: Page) -> None:
        pass


class PluginsArrayPlugin(IStealthPlugin):
    """Emulate browser plugins"""
    
    def get_name(self) -> str:
        return "plugins_array"
    
    def get_description(self) -> str:
        return "Adds realistic browser plugins array"
    
    def get_priority(self) -> int:
        return 3
    
    async def apply_to_context(self, context: BrowserContext) -> None:
        await context.add_init_script("""
            // Create fake plugins array
            const fakePlugins = [
                {
                    name: 'Chrome PDF Plugin',
                    description: 'Portable Document Format',
                    filename: 'internal-pdf-viewer',
                    mimeTypes: [{
                        type: 'application/pdf',
                        suffixes: 'pdf',
                        description: 'Portable Document Format'
                    }]
                },
                {
                    name: 'Chrome PDF Viewer',
                    description: 'Portable Document Format',
                    filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                    mimeTypes: [{
                        type: 'application/pdf',
                        suffixes: 'pdf',
                        description: 'Portable Document Format'
                    }]
                },
                {
                    name: 'Native Client',
                    description: 'Native Client Executable',
                    filename: 'internal-nacl-plugin',
                    mimeTypes: [
                        {
                            type: 'application/x-nacl',
                            suffixes: '',
                            description: 'Native Client Executable'
                        },
                        {
                            type: 'application/x-pnacl',
                            suffixes: '',
                            description: 'Portable Native Client Executable'
                        }
                    ]
                }
            ];
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => fakePlugins
            });
            
            // Override mimeTypes
            const mimeTypes = [];
            fakePlugins.forEach(plugin => {
                plugin.mimeTypes.forEach(mimeType => {
                    mimeTypes.push(mimeType);
                });
            });
            
            Object.defineProperty(navigator, 'mimeTypes', {
                get: () => mimeTypes
            });
        """)
    
    async def apply_to_page(self, page: Page) -> None:
        pass


class WebGLPlugin(IStealthPlugin):
    """Spoof WebGL vendor and renderer"""
    
    def get_name(self) -> str:
        return "webgl_vendor"
    
    def get_description(self) -> str:
        return "Spoofs WebGL vendor and renderer info"
    
    def get_priority(self) -> int:
        return 4
    
    async def apply_to_context(self, context: BrowserContext) -> None:
        await context.add_init_script("""
            // Override WebGL vendor and renderer
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter.apply(this, arguments);
            };
            
            const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
            WebGL2RenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter2.apply(this, arguments);
            };
        """)
    
    async def apply_to_page(self, page: Page) -> None:
        pass


class LanguagesPlugin(IStealthPlugin):
    """Set consistent browser languages"""
    
    def get_name(self) -> str:
        return "languages"
    
    def get_description(self) -> str:
        return "Sets consistent browser language properties"
    
    def get_priority(self) -> int:
        return 5
    
    async def apply_to_context(self, context: BrowserContext) -> None:
        await context.add_init_script("""
            // Override language properties
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            Object.defineProperty(navigator, 'language', {
                get: () => 'en-US'
            });
        """)
    
    async def apply_to_page(self, page: Page) -> None:
        pass


class PermissionsPlugin(IStealthPlugin):
    """Handle permissions API"""
    
    def get_name(self) -> str:
        return "permissions"
    
    def get_description(self) -> str:
        return "Implements permissions API"
    
    def get_priority(self) -> int:
        return 6
    
    async def apply_to_context(self, context: BrowserContext) -> None:
        await context.add_init_script("""
            // Override permissions
            if (!navigator.permissions) {
                navigator.permissions = {
                    query: async (permissionDesc) => {
                        return {
                            state: 'granted',
                            onchange: null
                        };
                    }
                };
            }
            
            const originalQuery = navigator.permissions.query;
            navigator.permissions.query = async (parameters) => {
                if (parameters.name === 'notifications') {
                    return Promise.resolve({ state: Notification.permission });
                }
                return originalQuery(parameters);
            };
        """)
    
    async def apply_to_page(self, page: Page) -> None:
        pass


class UserAgentPlugin(IStealthPlugin):
    """Override user agent data"""
    
    def get_name(self) -> str:
        return "user_agent"
    
    def get_description(self) -> str:
        return "Overrides navigator.userAgentData"
    
    def get_priority(self) -> int:
        return 7
    
    async def apply_to_context(self, context: BrowserContext) -> None:
        # Set a realistic non-headless user agent for the context
        realistic_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        await context.set_extra_http_headers({
            "User-Agent": realistic_ua
        })
        
        await context.add_init_script("""
            // Override userAgent string to remove HeadlessChrome
            const realisticUA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';
            
            Object.defineProperty(navigator, 'userAgent', {
                get: () => realisticUA,
                configurable: true
            });
            
            // Also override appVersion to be consistent
            Object.defineProperty(navigator, 'appVersion', {
                get: () => '5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                configurable: true
            });
            
            // Override userAgentData
            Object.defineProperty(navigator, 'userAgentData', {
                get: () => ({
                    brands: [
                        { brand: "Not_A Brand", version: "8" },
                        { brand: "Chromium", version: "120" },
                        { brand: "Google Chrome", version: "120" }
                    ],
                    mobile: false,
                    platform: "Windows",
                    getHighEntropyValues: async (hints) => {
                        return {
                            brands: [
                                { brand: "Not_A Brand", version: "8" },
                                { brand: "Chromium", version: "120" },
                                { brand: "Google Chrome", version: "120" }
                            ],
                            mobile: false,
                            platform: "Windows",
                            platformVersion: "10.0.0",
                            architecture: "x86",
                            bitness: "64",
                            model: "",
                            uaFullVersion: "120.0.0.0"
                        };
                    }
                })
            });
        """)
    
    async def apply_to_page(self, page: Page) -> None:
        pass


class CanvasPlugin(IStealthPlugin):
    """Add noise to canvas fingerprinting"""
    
    def get_name(self) -> str:
        return "canvas_noise"
    
    def get_description(self) -> str:
        return "Adds noise to canvas fingerprinting"
    
    def get_priority(self) -> int:
        return 8
    
    async def apply_to_context(self, context: BrowserContext) -> None:
        await context.add_init_script("""
            // Add canvas noise
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function() {
                const context = this.getContext('2d');
                if (context) {
                    // Add random noise
                    const imageData = context.getImageData(0, 0, this.width, this.height);
                    for (let i = 0; i < imageData.data.length; i += 4) {
                        imageData.data[i] += Math.random() * 0.1 - 0.05;     // R
                        imageData.data[i+1] += Math.random() * 0.1 - 0.05;   // G
                        imageData.data[i+2] += Math.random() * 0.1 - 0.05;   // B
                    }
                    context.putImageData(imageData, 0, 0);
                }
                return originalToDataURL.apply(this, arguments);
            };
        """)
    
    async def apply_to_page(self, page: Page) -> None:
        pass


class AdvancedTimingPlugin(IStealthPlugin):
    """Advanced timing attack countermeasures"""
    
    def get_name(self) -> str:
        return "advanced_timing"
    
    def get_description(self) -> str:
        return "Counters timing-based bot detection"
    
    def get_priority(self) -> int:
        return 9
    
    async def apply_to_context(self, context: BrowserContext) -> None:
        await context.add_init_script("""
            // Advanced timing attack countermeasures
            
            // Add realistic performance timing jitter
            const originalNow = performance.now.bind(performance);
            const startTime = Date.now();
            let callCount = 0;
            let lastCall = 0;
            
            performance.now = function() {
                callCount++;
                const realTime = originalNow();
                const currentCall = realTime;
                
                // Add realistic jitter based on system load simulation
                let jitter = 0;
                if (currentCall - lastCall < 16) { // < 60fps
                    jitter = Math.random() * 0.5; // Small jitter for rapid calls
                } else {
                    jitter = Math.random() * 2.0; // Larger jitter for spaced calls
                }
                
                lastCall = currentCall;
                return realTime + jitter;
            };
            
            // Override Date.now() with realistic drift
            const originalDateNow = Date.now.bind(Date);
            let timeOffset = Math.random() * 10 - 5; // ±5ms offset
            
            Date.now = function() {
                // Simulate clock drift
                timeOffset += (Math.random() - 0.5) * 0.1;
                return originalDateNow() + timeOffset;
            };
            
            // Add realistic memory usage patterns
            if ('memory' in performance) {
                const originalMemory = performance.memory;
                Object.defineProperty(performance, 'memory', {
                    get: () => ({
                        get usedJSHeapSize() {
                            return originalMemory.usedJSHeapSize + Math.floor(Math.random() * 100000);
                        },
                        get totalJSHeapSize() {
                            return originalMemory.totalJSHeapSize + Math.floor(Math.random() * 200000);
                        },
                        get jsHeapSizeLimit() {
                            return originalMemory.jsHeapSizeLimit;
                        }
                    })
                });
            }
            
            // Simulate realistic resource loading timing
            const originalFetch = window.fetch.bind(window);
            window.fetch = async function(...args) {
                const startTime = performance.now();
                const result = await originalFetch(...args);
                const endTime = performance.now();
                
                // Add artificial delay if request was too fast
                const duration = endTime - startTime;
                if (duration < 10) { // Less than 10ms is suspicious
                    await new Promise(resolve => setTimeout(resolve, 10 + Math.random() * 20));
                }
                
                return result;
            };
        """)
    
    async def apply_to_page(self, page: Page) -> None:
        # Apply timing countermeasures to all pages
        await page.add_init_script("""
            // Additional page-level timing protections
            
            // Randomize setTimeout/setInterval timing
            const originalSetTimeout = window.setTimeout.bind(window);
            const originalSetInterval = window.setInterval.bind(window);
            
            window.setTimeout = function(callback, delay, ...args) {
                // Add ±10% jitter to timeouts
                const jitteredDelay = delay + (Math.random() - 0.5) * delay * 0.1;
                return originalSetTimeout(callback, Math.max(0, jitteredDelay), ...args);
            };
            
            window.setInterval = function(callback, delay, ...args) {
                // Add ±5% jitter to intervals
                const jitteredDelay = delay + (Math.random() - 0.5) * delay * 0.05;
                return originalSetInterval(callback, Math.max(1, jitteredDelay), ...args);
            };
            
            // Override requestAnimationFrame with realistic timing
            const originalRAF = window.requestAnimationFrame.bind(window);
            let rafCallCount = 0;
            
            window.requestAnimationFrame = function(callback) {
                rafCallCount++;
                return originalRAF(function(timestamp) {
                    // Add small jitter to frame timing
                    const jitteredTimestamp = timestamp + (Math.random() - 0.5) * 0.5;
                    return callback(jitteredTimestamp);
                });
            };
        """);


class EnhancedFingerprintPlugin(IStealthPlugin):
    """Enhanced fingerprinting countermeasures for Google Scholar"""
    
    def get_name(self) -> str:
        return "enhanced_fingerprint"
    
    def get_description(self) -> str:
        return "Advanced fingerprinting countermeasures for Google Scholar detection"
    
    def get_priority(self) -> int:
        return 10
    
    async def apply_to_context(self, context: BrowserContext) -> None:
        await context.add_init_script("""
            // Enhanced fingerprinting countermeasures
            
            // Override font detection with consistent results
            const originalOffsetWidth = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'offsetWidth');
            const originalOffsetHeight = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'offsetHeight');
            
            Object.defineProperty(HTMLElement.prototype, 'offsetWidth', {
                get: function() {
                    const value = originalOffsetWidth.get.call(this);
                    // Add small random variation to prevent fingerprinting
                    if (this.style && this.style.font) {
                        return value + (Math.random() - 0.5) * 0.1;
                    }
                    return value;
                },
                configurable: true
            });
            
            Object.defineProperty(HTMLElement.prototype, 'offsetHeight', {
                get: function() {
                    const value = originalOffsetHeight.get.call(this);
                    // Add small random variation to prevent fingerprinting
                    if (this.style && this.style.font) {
                        return value + (Math.random() - 0.5) * 0.1;
                    }
                    return value;
                },
                configurable: true
            });
            
            // Override AudioContext for audio fingerprinting defense
            if (window.AudioContext || window.webkitAudioContext) {
                const OriginalAudioContext = window.AudioContext || window.webkitAudioContext;
                window.AudioContext = function(...args) {
                    const context = new OriginalAudioContext(...args);
                    const originalGetByteFrequencyData = context.constructor.prototype.getByteFrequencyData;
                    
                    context.constructor.prototype.getByteFrequencyData = function(array) {
                        const result = originalGetByteFrequencyData.apply(this, arguments);
                        // Add noise to audio fingerprint
                        for (let i = 0; i < array.length; i++) {
                            array[i] = array[i] + Math.floor(Math.random() * 3) - 1;
                        }
                        return result;
                    };
                    
                    return context;
                };
                
                if (window.webkitAudioContext) {
                    window.webkitAudioContext = window.AudioContext;
                }
            }
            
            // Override navigator.hardwareConcurrency with variation
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => {
                    // Vary between 4, 8, and 16 cores randomly
                    const cores = [4, 8, 16];
                    return cores[Math.floor(Math.random() * cores.length)];
                },
                enumerable: true,
                configurable: true
            });
            
            // Add realistic timezone handling
            const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
            Date.prototype.getTimezoneOffset = function() {
                // Add small random variation to timezone offset
                const baseOffset = originalGetTimezoneOffset.call(this);
                return baseOffset + Math.floor(Math.random() * 3) - 1;
            };
            
            // Override Intl.DateTimeFormat for locale consistency
            const originalDateTimeFormat = Intl.DateTimeFormat;
            Intl.DateTimeFormat = function(locales, options) {
                // Always report US locale to match headers
                return new originalDateTimeFormat('en-US', options);
            };
        """)
    
    async def apply_to_page(self, page: Page) -> None:
        await page.add_init_script("""
            // Page-level fingerprint countermeasures
            
            // Override getComputedStyle for CSS fingerprinting defense
            const originalGetComputedStyle = window.getComputedStyle;
            window.getComputedStyle = function(element, pseudoElement) {
                const styles = originalGetComputedStyle.call(this, element, pseudoElement);
                
                // Create proxy to modify font-related properties
                return new Proxy(styles, {
                    get: function(target, prop) {
                        const value = target[prop];
                        if (typeof value === 'string' && prop.includes('font')) {
                            // Add small variations to font measurements
                            const numValue = parseFloat(value);
                            if (!isNaN(numValue) && numValue > 0) {
                                const variation = numValue + (Math.random() - 0.5) * 0.02;
                                return value.replace(numValue.toString(), variation.toString());
                            }
                        }
                        return value;
                    }
                });
            };
        """);


class BehavioralSimulationPlugin(IStealthPlugin):
    """Simulate realistic human behavioral patterns"""
    
    def get_name(self) -> str:
        return "behavioral_simulation"
    
    def get_description(self) -> str:
        return "Simulates realistic human behavioral patterns"
    
    def get_priority(self) -> int:
        return 11
    
    async def apply_to_context(self, context: BrowserContext) -> None:
        await context.add_init_script("""
            // Behavioral simulation for human-like interaction patterns
            
            // Track interaction patterns
            window.humanBehaviorTracker = {
                mouseMovements: 0,
                keystrokes: 0,
                clicks: 0,
                scrolls: 0,
                startTime: Date.now(),
                lastActivity: Date.now(),
                
                // Simulate realistic activity
                simulateActivity: function() {
                    // Simulate occasional mouse movements
                    setInterval(() => {
                        this.mouseMovements += Math.floor(Math.random() * 5);
                        this.lastActivity = Date.now();
                    }, 100 + Math.random() * 200);
                    
                    // Simulate periodic scrolling
                    setInterval(() => {
                        this.scrolls += Math.floor(Math.random() * 2);
                        this.lastActivity = Date.now();
                    }, 1000 + Math.random() * 3000);
                },
                
                // Get activity metrics that look human
                getMetrics: function() {
                    const sessionDuration = Date.now() - this.startTime;
                    return {
                        sessionDuration,
                        mouseMovements: this.mouseMovements,
                        keystrokes: this.keystrokes,
                        clicks: this.clicks,
                        scrolls: this.scrolls,
                        activityRate: (this.mouseMovements + this.keystrokes + this.clicks) / (sessionDuration / 1000)
                    };
                }
            };
            
            // Start simulating activity
            window.humanBehaviorTracker.simulateActivity();
            
            // Override event handlers to track real interactions
            const originalAddEventListener = EventTarget.prototype.addEventListener;
            EventTarget.prototype.addEventListener = function(type, listener, options) {
                const wrappedListener = function(event) {
                    // Track different types of interactions
                    switch(event.type) {
                        case 'mousemove':
                            window.humanBehaviorTracker.mouseMovements++;
                            break;
                        case 'keydown':
                        case 'keyup':
                            window.humanBehaviorTracker.keystrokes++;
                            break;
                        case 'click':
                            window.humanBehaviorTracker.clicks++;
                            break;
                        case 'scroll':
                            window.humanBehaviorTracker.scrolls++;
                            break;
                    }
                    window.humanBehaviorTracker.lastActivity = Date.now();
                    
                    return listener.apply(this, arguments);
                };
                
                return originalAddEventListener.call(this, type, wrappedListener, options);
            };
            
            // Add realistic viewport interaction patterns
            Object.defineProperty(document, 'visibilityState', {
                get: () => 'visible',
                enumerable: true,
                configurable: true
            });
            
            Object.defineProperty(document, 'hidden', {
                get: () => false,
                enumerable: true,
                configurable: true
            });
        """)
    
    async def apply_to_page(self, page: Page) -> None:
        # Simulate human-like page interactions
        await page.add_init_script("""
            // Page-specific behavioral simulation
            
            // Simulate realistic focus/blur patterns
            let focusEventCount = 0;
            const originalFocus = HTMLElement.prototype.focus;
            HTMLElement.prototype.focus = function() {
                focusEventCount++;
                window.humanBehaviorTracker.lastActivity = Date.now();
                return originalFocus.apply(this, arguments);
            };
            
            // Add realistic idle detection evasion
            let userIsActive = true;
            let lastActivityTime = Date.now();
            
            // Reset activity timer on various events
            ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
                document.addEventListener(event, () => {
                    userIsActive = true;
                    lastActivityTime = Date.now();
                }, true);
            });
            
            // Simulate periodic activity to prevent idle detection
            setInterval(() => {
                const timeSinceActivity = Date.now() - lastActivityTime;
                if (timeSinceActivity > 30000) { // 30 seconds
                    // Simulate small mouse movement
                    const event = new MouseEvent('mousemove', {
                        clientX: Math.random() * 10,
                        clientY: Math.random() * 10,
                        bubbles: true
                    });
                    document.dispatchEvent(event);
                    lastActivityTime = Date.now();
                }
            }, 15000); // Check every 15 seconds
        """);


class GoogleScholarStealthPlugin(IStealthPlugin):
    """Google Scholar specific stealth enhancements"""
    
    def get_name(self) -> str:
        return "google_scholar_stealth"
    
    def get_description(self) -> str:
        return "Specific stealth measures for Google Scholar bot detection"
    
    def get_priority(self) -> int:
        return 12
    
    async def apply_to_context(self, context: BrowserContext) -> None:
        await context.add_init_script("""
            // Google Scholar specific evasion techniques
            
            // Add realistic referrer patterns
            Object.defineProperty(document, 'referrer', {
                get: () => {
                    const referrers = [
                        'https://www.google.com/',
                        'https://www.google.com/search?q=research+papers',
                        'https://scholar.google.com/',
                        ''  // Direct navigation
                    ];
                    return referrers[Math.floor(Math.random() * referrers.length)];
                },
                configurable: true
            });
            
            // Override screen properties to match typical academic users
            Object.defineProperties(screen, {
                availWidth: { value: 1920, enumerable: true, configurable: true },
                availHeight: { value: 1040, enumerable: true, configurable: true },
                width: { value: 1920, enumerable: true, configurable: true },
                height: { value: 1080, enumerable: true, configurable: true },
                colorDepth: { value: 24, enumerable: true, configurable: true },
                pixelDepth: { value: 24, enumerable: true, configurable: true }
            });
            
            // Add realistic network connection for academic setting
            Object.defineProperty(navigator, 'connection', {
                value: {
                    effectiveType: '4g',
                    downlink: 25, // Typical university connection
                    rtt: 30,
                    saveData: false
                },
                enumerable: true,
                configurable: true
            });
            
            // Simulate realistic battery status (laptop user)
            if ('getBattery' in navigator) {
                Object.defineProperty(navigator, 'getBattery', {
                    value: () => Promise.resolve({
                        charging: Math.random() > 0.3, // 70% chance charging
                        chargingTime: Math.random() > 0.5 ? 0 : Math.random() * 7200,
                        dischargingTime: Math.random() * 28800, // 0-8 hours
                        level: 0.3 + Math.random() * 0.6 // 30-90% battery
                    }),
                    enumerable: true,
                    configurable: true
                });
            }
            
            // Override performance timing to look like academic browsing
            if (performance && performance.timing) {
                const timing = performance.timing;
                const now = Date.now();
                const realistic = {
                    navigationStart: now - Math.random() * 3000,
                    domContentLoadedEventEnd: now - Math.random() * 1000,
                    loadEventEnd: now - Math.random() * 500
                };
                
                Object.defineProperties(performance.timing, {
                    navigationStart: { value: realistic.navigationStart, enumerable: true },
                    domContentLoadedEventEnd: { value: realistic.domContentLoadedEventEnd, enumerable: true },
                    loadEventEnd: { value: realistic.loadEventEnd, enumerable: true }
                });
            }
        """)
    
    async def apply_to_page(self, page: Page) -> None:
        # Apply Scholar-specific page enhancements
        if 'scholar.google' in page.url:
            await page.add_init_script("""
                // Scholar-specific page behavior simulation
                
                // Simulate realistic reading patterns
                let scholarSession = {
                    pageLoadTime: Date.now(),
                    searchAttempts: 0,
                    papersViewed: 0,
                    scrollDepth: 0,
                    timeOnPage: 0
                };
                
                // Track Scholar-specific interactions
                document.addEventListener('click', (e) => {
                    if (e.target.closest('.gs_rt a')) {
                        scholarSession.papersViewed++;
                    }
                });
                
                document.addEventListener('scroll', () => {
                    const scrollPercent = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
                    scholarSession.scrollDepth = Math.max(scholarSession.scrollDepth, scrollPercent);
                });
                
                // Simulate realistic search timing
                document.addEventListener('focus', (e) => {
                    if (e.target.id === 'gs_hdr_tsb' || e.target.name === 'q') {
                        scholarSession.searchAttempts++;
                        
                        // Add realistic delay before typing
                        setTimeout(() => {
                            if (e.target.value === '') {
                                // Simulate thinking time
                                const thinkingTime = 500 + Math.random() * 2000;
                                setTimeout(() => {
                                    // Trigger some background activity
                                    window.humanBehaviorTracker.mouseMovements += 5;
                                }, thinkingTime);
                            }
                        }, 100);
                    }
                });
                
                // Expose Scholar session data
                window.getScholarSession = () => {
                    scholarSession.timeOnPage = Date.now() - scholarSession.pageLoadTime;
                    return scholarSession;
                };
                
                // Simulate periodic checks (like human reading)
                setInterval(() => {
                    if (document.hasFocus()) {
                        window.humanBehaviorTracker.scrolls += Math.floor(Math.random() * 2);
                    }
                }, 3000 + Math.random() * 5000);
            """)


class StealthManager:
    """Manages stealth plugins for bot evasion"""
    
    def __init__(self, auto_load_defaults: bool = True):
        self.plugins: List[IStealthPlugin] = []
        self.enabled_plugins: List[str] = []
        self._default_plugins = [
            WebDriverPlugin(),
            ChromeRuntimePlugin(),
            PluginsArrayPlugin(),
            WebGLPlugin(),
            LanguagesPlugin(),
            PermissionsPlugin(),
            UserAgentPlugin(),
            CanvasPlugin(),
            AdvancedTimingPlugin(),
            EnhancedFingerprintPlugin(),
            BehavioralSimulationPlugin(),
            GoogleScholarStealthPlugin()
        ]
        self.adaptive_mode = False
        self.detection_results: Dict[str, Any] = {}
        
        if auto_load_defaults:
            self.use_default_plugins()
    
    def register_plugin(self, plugin: IStealthPlugin) -> None:
        """Register a stealth plugin"""
        self.plugins.append(plugin)
        logger.info(f"Registered stealth plugin: {plugin.get_name()}")
    
    def enable_plugin(self, plugin_name: str) -> None:
        """Enable specific plugin by name"""
        self.enabled_plugins.append(plugin_name)
    
    def disable_plugin(self, plugin_name: str) -> None:
        """Disable specific plugin by name"""
        if plugin_name in self.enabled_plugins:
            self.enabled_plugins.remove(plugin_name)
    
    def use_default_plugins(self) -> None:
        """Register all default plugins"""
        for plugin in self._default_plugins:
            self.register_plugin(plugin)
        logger.info(f"Registered {len(self._default_plugins)} default stealth plugins")
    
    async def apply_to_context(self, context: BrowserContext, plugins: Optional[List[str]] = None) -> None:
        """Apply stealth modifications to browser context"""
        # Use specified plugins or all registered ones
        if plugins:
            active_plugins = [p for p in self.plugins if p.get_name() in plugins]
        elif self.enabled_plugins:
            active_plugins = [p for p in self.plugins if p.get_name() in self.enabled_plugins]
        else:
            active_plugins = self.plugins
        
        # Sort by priority
        active_plugins.sort(key=lambda p: p.get_priority())
        
        # Apply each plugin
        for plugin in active_plugins:
            try:
                await plugin.apply_to_context(context)
                logger.debug(f"Applied stealth plugin to context: {plugin.get_name()}")
            except Exception as e:
                logger.error(f"Failed to apply plugin {plugin.get_name()}: {e}")
    
    async def apply_to_page(self, page: Page, plugins: Optional[List[str]] = None) -> None:
        """Apply stealth modifications to specific page"""
        # Use specified plugins or all registered ones
        if plugins:
            active_plugins = [p for p in self.plugins if p.get_name() in plugins]
        elif self.enabled_plugins:
            active_plugins = [p for p in self.plugins if p.get_name() in self.enabled_plugins]
        else:
            active_plugins = self.plugins
        
        # Sort by priority
        active_plugins.sort(key=lambda p: p.get_priority())
        
        # Apply each plugin
        for plugin in active_plugins:
            try:
                await plugin.apply_to_page(page)
                logger.debug(f"Applied stealth plugin to page: {plugin.get_name()}")
            except Exception as e:
                logger.error(f"Failed to apply plugin {plugin.get_name()}: {e}")
    
    async def test_detection(self, page: Page) -> Dict[str, Any]:
        """Test if browser is detected as bot"""
        results = {}
        
        # Test webdriver flag
        results["webdriver"] = await page.evaluate("navigator.webdriver")
        
        # Test Chrome runtime
        results["chrome"] = await page.evaluate("typeof window.chrome !== 'undefined'")
        
        # Test plugins
        results["plugins_length"] = await page.evaluate("navigator.plugins.length")
        
        # Test user agent
        results["user_agent"] = await page.evaluate("navigator.userAgent")
        
        # Test languages
        results["languages"] = await page.evaluate("navigator.languages")
        
        # Store results
        self.detection_results = results
        
        # Determine if bot-like
        is_bot = results.get("webdriver", False) or results.get("plugins_length", 0) == 0
        
        logger.info(f"Detection test results: Bot detected = {is_bot}")
        return {
            "is_bot": is_bot,
            "details": results
        }
    
    def get_optimal_plugin_combination(self, target_domain: str) -> List[str]:
        """Get optimal plugin combination for specific domain"""
        # This could be enhanced with ML-based optimization
        # For now, return all plugins
        return [p.get_name() for p in self.plugins]
    
    def enable_adaptive_mode(self) -> None:
        """Enable adaptive evasion based on detection results"""
        self.adaptive_mode = True
        logger.info("Adaptive stealth mode enabled")