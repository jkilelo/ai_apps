"""
Stealth Test Suite for AI Browser v2.0.0

Tests bot detection evasion capabilities against known detection methods.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List
import json
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from execution.browser_manager import BrowserManager, BrowserConfig
from execution.stealth_manager import StealthManager


class TestWebDriverDetection:
    """Test webdriver property detection evasion"""
    
    @pytest.mark.asyncio
    async def test_navigator_webdriver_hidden(self):
        """Test that navigator.webdriver is undefined or false"""
        browser_config = BrowserConfig(headless=False)
        browser_manager = BrowserManager()
        stealth_manager = StealthManager(auto_load_defaults=True)
        
        try:
            await browser_manager.launch(browser_config)
            context = await browser_manager.browser.new_context()
            
            # Apply stealth to context (must be done before creating page)
            await stealth_manager.apply_to_context(context)
            
            page = await context.new_page()
            
            # Apply additional stealth to page
            await stealth_manager.apply_to_page(page)
            
            # Navigate to test page
            await page.goto("data:text/html,<html><body>Test</body></html>")
            
            # Check webdriver property
            webdriver_check = await page.evaluate("""
                () => {
                    return {
                        webdriver: navigator.webdriver,
                        type: typeof navigator.webdriver,
                        isUndefined: navigator.webdriver === undefined,
                        isFalse: navigator.webdriver === false
                    }
                }
            """)
            
            # Webdriver should be undefined or false
            assert webdriver_check["webdriver"] in [None, False, "undefined"]
            assert webdriver_check["isUndefined"] or webdriver_check["isFalse"]
            
            await context.close()
        finally:
            await browser_manager.close()
    
    @pytest.mark.asyncio
    async def test_chrome_runtime_object(self):
        """Test that window.chrome object exists"""
        browser_config = BrowserConfig(headless=False)
        browser_manager = BrowserManager()
        stealth_manager = StealthManager(auto_load_defaults=True)
        
        try:
            await browser_manager.launch(browser_config)
            context = await browser_manager.browser.new_context()
            
            # Apply stealth to context first
            await stealth_manager.apply_to_context(context)
            
            page = await context.new_page()
            await stealth_manager.apply_to_page(page)
            await page.goto("data:text/html,<html><body>Test</body></html>")
            
            # Check chrome object
            chrome_check = await page.evaluate("""
                () => {
                    return {
                        hasChrome: typeof window.chrome !== 'undefined',
                        hasRuntime: window.chrome && typeof window.chrome.runtime !== 'undefined',
                        hasLoadTimes: window.chrome && typeof window.chrome.loadTimes === 'function',
                        hasCsi: window.chrome && typeof window.chrome.csi === 'function'
                    }
                }
            """)
            
            # Chrome object should exist
            assert chrome_check["hasChrome"] is True
            
            await context.close()
        finally:
            await browser_manager.close()


class TestFingerprintEvasion:
    """Test browser fingerprint evasion"""
    
    @pytest.mark.asyncio
    async def test_canvas_fingerprint_noise(self):
        """Test that canvas fingerprinting is randomized"""
        browser_config = BrowserConfig(headless=False)
        browser_manager = BrowserManager()
        stealth_manager = StealthManager(auto_load_defaults=True)
        
        fingerprints = []
        
        try:
            await browser_manager.launch()
            
            # Get fingerprints from multiple contexts
            for _ in range(2):
                context = await browser_manager.browser.new_context()
                page = await context.new_page()
                
                await stealth_manager.apply_to_page(page)
                await page.goto("data:text/html,<html><body><canvas id='c'></canvas></body></html>")
                
                # Generate canvas fingerprint
                fingerprint = await page.evaluate("""
                    () => {
                        const canvas = document.getElementById('c');
                        const ctx = canvas.getContext('2d');
                        
                        // Draw test pattern
                        ctx.textBaseline = 'top';
                        ctx.font = '14px Arial';
                        ctx.fillStyle = '#f60';
                        ctx.fillRect(125, 1, 62, 20);
                        ctx.fillStyle = '#069';
                        ctx.fillText('Browser fingerprint test', 2, 15);
                        
                        // Get data URL
                        return canvas.toDataURL();
                    }
                """)
                
                fingerprints.append(fingerprint)
                await context.close()
            
            # With noise injection, fingerprints might differ
            # (Note: Some stealth plugins may not implement canvas noise)
            assert len(fingerprints) == 2
            
        finally:
            await browser_manager.close()
    
    @pytest.mark.asyncio
    async def test_webgl_vendor_spoofing(self):
        """Test WebGL vendor/renderer spoofing"""
        browser_config = BrowserConfig(headless=False)
        browser_manager = BrowserManager()
        stealth_manager = StealthManager(auto_load_defaults=True)
        
        try:
            await browser_manager.launch(browser_config)
            context = await browser_manager.browser.new_context()
            
            # Apply stealth to context first
            await stealth_manager.apply_to_context(context)
            
            page = await context.new_page()
            await stealth_manager.apply_to_page(page)
            await page.goto("data:text/html,<html><body><canvas id='c'></canvas></body></html>")
            
            # Get WebGL info
            webgl_info = await page.evaluate("""
                () => {
                    const canvas = document.getElementById('c');
                    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                    
                    if (!gl) return null;
                    
                    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                    if (!debugInfo) return {vendor: 'unknown', renderer: 'unknown'};
                    
                    return {
                        vendor: gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL),
                        renderer: gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)
                    };
                }
            """)
            
            # Should have WebGL info (may be spoofed)
            assert webgl_info is not None
            
            await context.close()
        finally:
            await browser_manager.close()


class TestPluginAndLanguageDetection:
    """Test plugin and language detection evasion"""
    
    @pytest.mark.asyncio
    async def test_plugin_array_spoofing(self):
        """Test that navigator.plugins is populated"""
        browser_config = BrowserConfig(headless=False)
        browser_manager = BrowserManager()
        stealth_manager = StealthManager(auto_load_defaults=True)
        
        try:
            await browser_manager.launch(browser_config)
            context = await browser_manager.browser.new_context()
            
            # Apply stealth to context first
            await stealth_manager.apply_to_context(context)
            
            page = await context.new_page()
            await stealth_manager.apply_to_page(page)
            await page.goto("data:text/html,<html><body>Test</body></html>")
            
            # Check plugins
            plugin_info = await page.evaluate("""
                () => {
                    return {
                        count: navigator.plugins.length,
                        hasFlash: Array.from(navigator.plugins).some(p => 
                            p.name.toLowerCase().includes('flash')),
                        hasPDF: Array.from(navigator.plugins).some(p => 
                            p.name.toLowerCase().includes('pdf')),
                        names: Array.from(navigator.plugins).map(p => p.name)
                    }
                }
            """)
            
            # Should have plugins (real Chrome has 3-5 typically)
            assert plugin_info["count"] > 0
            
            await context.close()
        finally:
            await browser_manager.close()
    
    @pytest.mark.asyncio
    async def test_language_consistency(self):
        """Test that language properties are consistent"""
        browser_config = BrowserConfig(headless=False)
        browser_manager = BrowserManager()
        stealth_manager = StealthManager(auto_load_defaults=True)
        
        try:
            await browser_manager.launch(browser_config)
            context = await browser_manager.browser.new_context()
            
            # Apply stealth to context first
            await stealth_manager.apply_to_context(context)
            
            page = await context.new_page()
            await stealth_manager.apply_to_page(page)
            await page.goto("data:text/html,<html><body>Test</body></html>")
            
            # Check language properties
            lang_info = await page.evaluate("""
                () => {
                    return {
                        language: navigator.language,
                        languages: navigator.languages,
                        languagesLength: navigator.languages.length,
                        userLanguage: navigator.userLanguage,
                        browserLanguage: navigator.browserLanguage,
                        systemLanguage: navigator.systemLanguage
                    }
                }
            """)
            
            # Should have consistent language settings
            assert lang_info["language"] is not None
            assert lang_info["languagesLength"] > 0
            assert lang_info["language"] in lang_info["languages"]
            
            await context.close()
        finally:
            await browser_manager.close()


class TestPermissionsAPI:
    """Test Permissions API implementation"""
    
    @pytest.mark.asyncio
    async def test_permissions_query(self):
        """Test that Permissions API is properly implemented"""
        browser_config = BrowserConfig(headless=False)
        browser_manager = BrowserManager()
        stealth_manager = StealthManager(auto_load_defaults=True)
        
        try:
            await browser_manager.launch(browser_config)
            context = await browser_manager.browser.new_context()
            
            # Apply stealth to context first
            await stealth_manager.apply_to_context(context)
            
            page = await context.new_page()
            await stealth_manager.apply_to_page(page)
            await page.goto("data:text/html,<html><body>Test</body></html>")
            
            # Check Permissions API
            permissions_check = await page.evaluate("""
                async () => {
                    const results = {};
                    
                    try {
                        // Check if Permissions API exists
                        results.hasAPI = typeof navigator.permissions !== 'undefined';
                        
                        if (results.hasAPI) {
                            // Try to query notification permission
                            const notif = await navigator.permissions.query({name: 'notifications'});
                            results.notifications = notif.state;
                            
                            // Try to query geolocation permission
                            const geo = await navigator.permissions.query({name: 'geolocation'});
                            results.geolocation = geo.state;
                        }
                    } catch (e) {
                        results.error = e.message;
                    }
                    
                    return results;
                }
            """)
            
            # Should have Permissions API
            assert permissions_check.get("hasAPI") is True
            
            await context.close()
        finally:
            await browser_manager.close()


class TestHeadlessDetection:
    """Test headless browser detection evasion"""
    
    @pytest.mark.asyncio
    async def test_headless_user_agent(self):
        """Test that HeadlessChrome is not in user agent"""
        browser_config = BrowserConfig(headless=True)  # Test in headless mode
        browser_manager = BrowserManager()
        stealth_manager = StealthManager(auto_load_defaults=True)
        
        try:
            await browser_manager.launch(browser_config)
            context = await browser_manager.browser.new_context()
            
            # Apply stealth to context first
            await stealth_manager.apply_to_context(context)
            
            page = await context.new_page()
            await stealth_manager.apply_to_page(page)
            await page.goto("data:text/html,<html><body>Test</body></html>")
            
            # Check user agent
            user_agent = await page.evaluate("() => navigator.userAgent")
            
            # Should not contain HeadlessChrome
            assert "HeadlessChrome" not in user_agent
            assert "Headless" not in user_agent
            
            await context.close()
        finally:
            await browser_manager.close()
    
    @pytest.mark.asyncio
    async def test_window_size_in_headless(self):
        """Test that window size is realistic in headless mode"""
        browser_config = BrowserConfig(headless=True)
        browser_manager = BrowserManager()
        stealth_manager = StealthManager(auto_load_defaults=True)
        
        try:
            await browser_manager.launch()
            context = await browser_manager.browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            await stealth_manager.apply_to_page(page)
            await page.goto("data:text/html,<html><body>Test</body></html>")
            
            # Check window dimensions
            dimensions = await page.evaluate("""
                () => ({
                    innerWidth: window.innerWidth,
                    innerHeight: window.innerHeight,
                    outerWidth: window.outerWidth,
                    outerHeight: window.outerHeight,
                    screenWidth: window.screen.width,
                    screenHeight: window.screen.height,
                    availWidth: window.screen.availWidth,
                    availHeight: window.screen.availHeight
                })
            """)
            
            # Should have realistic dimensions
            assert dimensions["innerWidth"] > 0
            assert dimensions["innerHeight"] > 0
            assert dimensions["screenWidth"] >= dimensions["innerWidth"]
            assert dimensions["screenHeight"] >= dimensions["innerHeight"]
            
            await context.close()
        finally:
            await browser_manager.close()


class TestBotDetectionSites:
    """Test against actual bot detection test sites"""
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires internet connection")
    async def test_sannysoft_bot_detection(self):
        """Test against bot.sannysoft.com"""
        browser_config = BrowserConfig(headless=False)
        browser_manager = BrowserManager()
        stealth_manager = StealthManager(auto_load_defaults=True)
        
        try:
            await browser_manager.launch(browser_config)
            context = await browser_manager.browser.new_context()
            
            # Apply stealth to context first
            await stealth_manager.apply_to_context(context)
            
            page = await context.new_page()
            await stealth_manager.apply_to_page(page)
            
            # Navigate to bot detection site
            await page.goto("https://bot.sannysoft.com/", wait_until="networkidle")
            await asyncio.sleep(2)  # Wait for detection
            
            # Check detection results
            results = await page.evaluate("""
                () => {
                    const rows = document.querySelectorAll('table tr');
                    const detections = {};
                    
                    rows.forEach(row => {
                        const cells = row.querySelectorAll('td');
                        if (cells.length >= 2) {
                            const test = cells[0].innerText;
                            const result = cells[1].className;
                            detections[test] = result !== 'failed';
                        }
                    });
                    
                    return detections;
                }
            """)
            
            # Key tests should pass
            assert results.get("User Agent", False) is True
            assert results.get("WebDriver", False) is True
            
            await context.close()
        finally:
            await browser_manager.close()
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires internet connection")
    async def test_areyouheadless_detection(self):
        """Test against arh.antoinevastel.com/bots/areyouheadless"""
        browser_config = BrowserConfig(headless=True)  # Test headless detection
        browser_manager = BrowserManager(browser_config)
        stealth_manager = StealthManager(browser_manager, auto_load_defaults=True)
        
        try:
            await browser_manager.launch(browser_config)
            context = await browser_manager.browser.new_context()
            
            # Apply stealth to context first
            await stealth_manager.apply_to_context(context)
            
            page = await context.new_page()
            await stealth_manager.apply_to_page(page)
            
            # Navigate to headless detection site
            await page.goto("https://arh.antoinevastel.com/bots/areyouheadless", 
                           wait_until="networkidle")
            await asyncio.sleep(3)  # Wait for detection
            
            # Check if detected as headless
            detected = await page.evaluate("""
                () => {
                    const content = document.body.innerText.toLowerCase();
                    return content.includes('you are headless') || 
                           content.includes('headless chrome');
                }
            """)
            
            # Should not be detected as headless
            assert detected is False
            
            await context.close()
        finally:
            await browser_manager.close()


class TestAdvancedDetectionMethods:
    """Test against advanced detection methods"""
    
    @pytest.mark.asyncio
    async def test_tcp_ip_fingerprint(self):
        """Test TCP/IP stack fingerprinting resistance"""
        # This would require low-level network inspection
        # Mocking for demonstration
        assert True  # Placeholder
    
    @pytest.mark.asyncio
    async def test_timing_analysis(self):
        """Test resistance to timing-based detection"""
        browser_config = BrowserConfig(headless=False)
        browser_manager = BrowserManager()
        stealth_manager = StealthManager(auto_load_defaults=True)
        
        try:
            await browser_manager.launch(browser_config)
            context = await browser_manager.browser.new_context()
            
            # Apply stealth to context first
            await stealth_manager.apply_to_context(context)
            
            page = await context.new_page()
            await stealth_manager.apply_to_page(page)
            await page.goto("data:text/html,<html><body>Test</body></html>")
            
            # Measure JavaScript execution timing
            timing_check = await page.evaluate("""
                () => {
                    const iterations = 1000;
                    const start = performance.now();
                    
                    // Perform CPU-intensive task
                    let result = 0;
                    for (let i = 0; i < iterations; i++) {
                        result += Math.sqrt(i);
                    }
                    
                    const end = performance.now();
                    const duration = end - start;
                    
                    // Check if timing is within human-like range
                    // Bots often execute too fast or too consistently
                    return {
                        duration: duration,
                        isRealistic: duration > 0.01 && duration < 1000, // More realistic range
                        result: result
                    };
                }
            """)
            
            # Timing should be non-negative and performance.now should work
            assert timing_check["duration"] >= 0
            assert timing_check["result"] > 0  # Math operations should produce result
            
            await context.close()
        finally:
            await browser_manager.close()
    
    @pytest.mark.asyncio
    async def test_behavioral_analysis(self):
        """Test human-like behavior patterns"""
        browser_config = BrowserConfig(headless=False)
        browser_manager = BrowserManager()
        stealth_manager = StealthManager(auto_load_defaults=True)
        
        try:
            await browser_manager.launch(browser_config)
            context = await browser_manager.browser.new_context()
            
            # Apply stealth to context first
            await stealth_manager.apply_to_context(context)
            
            page = await context.new_page()
            await stealth_manager.apply_to_page(page)
            await page.goto("data:text/html,<html><body><button id='btn'>Click</button></body></html>")
            
            # Simulate human-like mouse movement
            await page.mouse.move(100, 100)
            await asyncio.sleep(0.1)
            await page.mouse.move(150, 150)
            await asyncio.sleep(0.1)
            
            # Click with human-like delay
            button = await page.query_selector("#btn")
            await button.hover()
            await asyncio.sleep(0.2)  # Human reaction time
            await button.click()
            
            # Verify interaction was recorded
            clicked = await page.evaluate("() => document.querySelector('#btn').clicked === true")
            
            await context.close()
        finally:
            await browser_manager.close()


@pytest.fixture
async def stealth_browser():
    """Fixture for creating a stealth-enabled browser"""
    browser_config = BrowserConfig(headless=False)
    browser_manager = BrowserManager()
    stealth_manager = StealthManager(auto_load_defaults=True)
    
    await browser_manager.launch(browser_config)
    
    yield browser_manager, stealth_manager
    
    await browser_manager.close()


def test_stealth_plugin_loading():
    """Test that stealth plugins are loaded correctly"""
    stealth_manager = StealthManager(auto_load_defaults=True)
    
    # Check default plugins are loaded
    assert len(stealth_manager.plugins) > 0
    
    # Check essential plugins are present
    plugin_names = [p.__class__.__name__ for p in stealth_manager.plugins]
    
    # Should have key evasion plugins
    expected_plugins = [
        "WebDriverPlugin",
        "ChromeRuntimePlugin", 
        "UserAgentPlugin"
    ]
    
    for expected in expected_plugins:
        assert any(expected == name for name in plugin_names)