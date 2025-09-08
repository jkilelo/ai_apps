/**
 * Hide webdriver presence to avoid bot detection
 */
(function() {
    'use strict';
    
    // Override navigator.webdriver
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
        configurable: true
    });
    
    // Remove webdriver traces from prototype
    try {
        delete navigator.__proto__.webdriver;
    } catch (e) {}
    
    // Hide automation indicators
    Object.defineProperty(document, 'hidden', { 
        get: () => false,
        configurable: true 
    });
    
    Object.defineProperty(document, 'visibilityState', { 
        get: () => 'visible',
        configurable: true
    });
    
    // Override chrome runtime check
    if (!window.chrome) {
        window.chrome = {};
    }
    
    if (!window.chrome.runtime) {
        window.chrome.runtime = {};
    }
})();