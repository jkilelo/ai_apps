/**
 * Spoof navigator properties to appear more human-like
 */
(function() {
    'use strict';
    
    // Override navigator.plugins with realistic values
    Object.defineProperty(navigator, 'plugins', {
        get: function() {
            return Object.create(PluginArray.prototype, {
                length: { value: 3 },
                0: {
                    value: Object.create(Plugin.prototype, {
                        name: { value: "Chrome PDF Plugin" },
                        filename: { value: "internal-pdf-viewer" },
                        description: { value: "Portable Document Format" },
                        length: { value: 1 }
                    })
                },
                1: {
                    value: Object.create(Plugin.prototype, {
                        name: { value: "Chrome PDF Viewer" },
                        filename: { value: "mhjfbmdgcfjbbpaeojofohoefgiehjai" },
                        description: { value: "Portable Document Format" },
                        length: { value: 1 }
                    })
                },
                2: {
                    value: Object.create(Plugin.prototype, {
                        name: { value: "Native Client" },
                        filename: { value: "native-client" },
                        description: { value: "Native Client Executable" },
                        length: { value: 2 }
                    })
                }
            });
        },
        configurable: true
    });
    
    // Override navigator.languages
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en'],
        configurable: true
    });
    
    // Override navigator.platform
    Object.defineProperty(navigator, 'platform', {
        get: () => 'Win32',
        configurable: true
    });
    
    // Override hardware concurrency with realistic value
    Object.defineProperty(navigator, 'hardwareConcurrency', {
        get: () => 4 + Math.floor(Math.random() * 4),
        configurable: true
    });
    
    // Override device memory
    Object.defineProperty(navigator, 'deviceMemory', {
        get: () => 8,
        configurable: true
    });
    
    // Override maxTouchPoints
    Object.defineProperty(navigator, 'maxTouchPoints', {
        get: () => 0,
        configurable: true
    });
})();