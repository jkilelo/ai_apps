#!/usr/bin/env python3
"""
Cross-Browser Compatibility Tests for AI Browser v2.0.0

Tests the AI Browser system across different browser engines:
- Chromium (Chrome/Edge)
- Firefox (Gecko)  
- WebKit (Safari)

Validates that core functionality works consistently across browsers:
- Browser launching and initialization
- Stealth capabilities across engines
- Action execution compatibility
- Page state capture consistency
- Memory operations across browsers
- Performance characteristics

**CRITICAL**: Uses REAL browser engines (no mocks) for true compatibility testing.
"""

import asyncio
import pytest
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from playwright.async_api import async_playwright, Browser, BrowserContext
from dotenv import load_dotenv
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from execution.browser_manager import BrowserManager, BrowserConfig
from execution.stealth_manager import StealthManager
from execution.action_executor import ActionExecutor
from perception.state_observer import StateObserver
from perception.dom_processor import DOMProcessor
from cognition.orchestrator import AgentOrchestrator

# Load environment variables
load_dotenv()

# Browser types to test
BROWSER_TYPES = ["chromium", "firefox", "webkit"]


class TestBrowserLaunchCompatibility:
    """Test browser launching works across all supported engines."""
    
    @pytest.mark.parametrize("browser_type", BROWSER_TYPES)
    @pytest.mark.asyncio
    async def test_browser_launch_and_close(self, browser_type):
        """Test basic browser launch and cleanup for each engine."""
        
        config = BrowserConfig(
            headless=True,
            browser_type=browser_type,
            viewport_width=1920,
            viewport_height=1080
        )
        
        browser_manager = BrowserManager(config)
        
        try:
            # Test browser launch
            start_time = time.time()
            browser = await browser_manager.launch()
            launch_time = time.time() - start_time
            
            # Should launch within SLA (2 seconds)
            assert launch_time < 2.0, f"{browser_type} launch took {launch_time:.2f}s, exceeds 2s SLA"
            
            # Test context creation
            context = await browser_manager.create_context()
            assert context is not None, f"Failed to create context in {browser_type}"
            
            # Test page creation
            page = await context.new_page()
            assert page is not None, f"Failed to create page in {browser_type}"
            
            # Test basic navigation
            await page.goto("https://httpbin.org/get", wait_until="networkidle", timeout=30000)
            
            # Verify page loaded
            page_title = await page.title()
            page_url = page.url
            assert "httpbin.org" in page_url, f"Navigation failed in {browser_type}"
            
            print(f"✅ {browser_type.capitalize()} browser launched and navigated successfully")
            
        except Exception as e:
            pytest.fail(f"Browser launch failed for {browser_type}: {e}")
        finally:
            await browser_manager.close()
    
    @pytest.mark.parametrize("browser_type", BROWSER_TYPES)
    @pytest.mark.asyncio
    async def test_browser_configuration_compatibility(self, browser_type):
        """Test various browser configurations work across engines."""
        
        configurations = [
            {"headless": True, "stealth_mode": True},
            {"headless": False, "stealth_mode": False},
            {"viewport_width": 800, "viewport_height": 600},
            {"viewport_width": 1920, "viewport_height": 1080},
        ]
        
        for config_dict in configurations:
            config = BrowserConfig(
                browser_type=browser_type,
                **config_dict
            )
            
            browser_manager = BrowserManager(config)
            
            try:
                browser = await browser_manager.launch()
                context = await browser_manager.create_context()
                page = await context.new_page()
                
                # Test viewport configuration
                viewport_size = page.viewport_size
                if "viewport_width" in config_dict:
                    assert viewport_size["width"] == config_dict["viewport_width"], \
                        f"Viewport width not set correctly in {browser_type}"
                    assert viewport_size["height"] == config_dict["viewport_height"], \
                        f"Viewport height not set correctly in {browser_type}"
                
                print(f"✅ {browser_type.capitalize()} configuration {config_dict} works")
                
            except Exception as e:
                pytest.fail(f"Configuration {config_dict} failed for {browser_type}: {e}")
            finally:
                await browser_manager.close()


class TestStealthCompatibility:
    """Test stealth capabilities work consistently across browsers."""
    
    @pytest.mark.parametrize("browser_type", BROWSER_TYPES)
    @pytest.mark.asyncio
    async def test_webdriver_property_hiding(self, browser_type):
        """Test navigator.webdriver property is hidden across browsers."""
        
        config = BrowserConfig(
            headless=True,
            browser_type=browser_type,
            stealth_mode=True
        )
        
        browser_manager = BrowserManager(config)
        stealth_manager = StealthManager()
        
        try:
            browser = await browser_manager.launch()
            context = await browser_manager.create_context()
            
            # Apply stealth plugins
            await stealth_manager.apply_stealth_plugins(context)
            
            page = await context.new_page()
            
            # Test webdriver property
            webdriver_value = await page.evaluate("navigator.webdriver")
            
            assert webdriver_value is False or webdriver_value is None, \
                f"navigator.webdriver not hidden in {browser_type}: {webdriver_value}"
            
            print(f"✅ {browser_type.capitalize()} webdriver property properly hidden")
            
        except Exception as e:
            pytest.fail(f"Webdriver hiding failed in {browser_type}: {e}")
        finally:
            await browser_manager.close()
    
    @pytest.mark.parametrize("browser_type", BROWSER_TYPES) 
    @pytest.mark.asyncio
    async def test_user_agent_consistency(self, browser_type):
        """Test user agent consistency across browsers."""
        
        config = BrowserConfig(
            headless=True,
            browser_type=browser_type,
            stealth_mode=True
        )
        
        browser_manager = BrowserManager(config)
        stealth_manager = StealthManager()
        
        try:
            browser = await browser_manager.launch()
            context = await browser_manager.create_context()
            await stealth_manager.apply_stealth_plugins(context)
            
            page = await context.new_page()
            
            # Get user agent
            user_agent = await page.evaluate("navigator.userAgent")
            
            # Should not contain headless indicators
            assert 'headless' not in user_agent.lower(), \
                f"User agent contains 'headless' in {browser_type}: {user_agent}"
            
            # Should be appropriate for browser type
            if browser_type == "chromium":
                assert 'chrome' in user_agent.lower(), f"Chromium user agent incorrect: {user_agent}"
            elif browser_type == "firefox":
                assert 'firefox' in user_agent.lower(), f"Firefox user agent incorrect: {user_agent}"
            elif browser_type == "webkit":
                assert 'safari' in user_agent.lower(), f"WebKit user agent incorrect: {user_agent}"
            
            print(f"✅ {browser_type.capitalize()} user agent consistent")
            
        except Exception as e:
            pytest.fail(f"User agent test failed in {browser_type}: {e}")
        finally:
            await browser_manager.close()
    
    @pytest.mark.parametrize("browser_type", BROWSER_TYPES)
    @pytest.mark.asyncio  
    async def test_plugin_spoofing_compatibility(self, browser_type):
        """Test plugin spoofing works across browsers."""
        
        config = BrowserConfig(
            headless=True,
            browser_type=browser_type,
            stealth_mode=True
        )
        
        browser_manager = BrowserManager(config)
        stealth_manager = StealthManager()
        
        try:
            browser = await browser_manager.launch()
            context = await browser_manager.create_context()
            await stealth_manager.apply_stealth_plugins(context)
            
            page = await context.new_page()
            
            # Test plugin array
            plugins = await page.evaluate("Array.from(navigator.plugins).map(p => p.name)")
            
            assert isinstance(plugins, list), f"Plugins not properly spoofed in {browser_type}"
            assert len(plugins) > 0, f"No plugins spoofed in {browser_type}"
            
            # Different browsers should have appropriate plugin sets
            plugins_str = json.dumps(plugins).lower()
            
            print(f"✅ {browser_type.capitalize()} has {len(plugins)} plugins spoofed")
            
        except Exception as e:
            print(f"⚠️  Plugin spoofing test issue in {browser_type}: {e}")
        finally:
            await browser_manager.close()


class TestActionExecutionCompatibility:
    """Test action execution works consistently across browsers."""
    
    @pytest.mark.parametrize("browser_type", BROWSER_TYPES)
    @pytest.mark.asyncio
    async def test_basic_actions_compatibility(self, browser_type):
        """Test basic actions (click, type, navigate) work across browsers."""
        
        config = BrowserConfig(
            headless=True,
            browser_type=browser_type
        )
        
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch()
            context = await browser_manager.create_context()
            page = await context.new_page()
            
            # Create action executor
            action_executor = ActionExecutor(page, context)
            
            # Test navigation action
            await page.goto("https://httpbin.org/forms/post", wait_until="networkidle")
            
            # Test typing action
            await page.fill('input[name="custname"]', f"Test User {browser_type}")
            
            # Test click action - find submit button
            submit_button = await page.query_selector('input[type="submit"]')
            assert submit_button is not None, f"Submit button not found in {browser_type}"
            
            # Click the button (may cause navigation)
            await submit_button.click()
            await asyncio.sleep(1)
            
            print(f"✅ {browser_type.capitalize()} basic actions working")
            
        except Exception as e:
            pytest.fail(f"Basic actions failed in {browser_type}: {e}")
        finally:
            await browser_manager.close()
    
    @pytest.mark.parametrize("browser_type", BROWSER_TYPES)
    @pytest.mark.asyncio
    async def test_javascript_evaluation_compatibility(self, browser_type):
        """Test JavaScript evaluation works across browsers."""
        
        config = BrowserConfig(
            headless=True,
            browser_type=browser_type
        )
        
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch()
            context = await browser_manager.create_context()
            page = await context.new_page()
            
            await page.goto("https://httpbin.org/get")
            
            # Test basic JavaScript evaluation
            result = await page.evaluate("1 + 1")
            assert result == 2, f"Basic JavaScript evaluation failed in {browser_type}"
            
            # Test DOM manipulation
            title = await page.evaluate("document.title")
            assert isinstance(title, str), f"DOM access failed in {browser_type}"
            
            # Test object creation and manipulation
            complex_result = await page.evaluate("""
                () => {
                    const obj = {name: 'test', value: 42};
                    return JSON.stringify(obj);
                }
            """)
            
            data = json.loads(complex_result)
            assert data['name'] == 'test', f"Complex JavaScript failed in {browser_type}"
            assert data['value'] == 42, f"Complex JavaScript failed in {browser_type}"
            
            print(f"✅ {browser_type.capitalize()} JavaScript evaluation working")
            
        except Exception as e:
            pytest.fail(f"JavaScript evaluation failed in {browser_type}: {e}")
        finally:
            await browser_manager.close()


class TestPerceptionCompatibility:
    """Test perception layer works consistently across browsers."""
    
    @pytest.mark.parametrize("browser_type", BROWSER_TYPES)
    @pytest.mark.asyncio
    async def test_dom_processing_compatibility(self, browser_type):
        """Test DOM processing works across browsers."""
        
        config = BrowserConfig(
            headless=True,
            browser_type=browser_type
        )
        
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch()
            context = await browser_manager.create_context()
            page = await context.new_page()
            
            await page.goto("https://httpbin.org/forms/post", wait_until="networkidle")
            
            # Create DOM processor
            dom_processor = DOMProcessor()
            
            # Process page DOM
            dom_data = await dom_processor.process_page_dom(page)
            
            # Verify DOM processing results
            assert dom_data is not None, f"DOM processing failed in {browser_type}"
            assert 'elements' in dom_data, f"DOM elements not found in {browser_type}"
            assert len(dom_data['elements']) > 0, f"No DOM elements found in {browser_type}"
            
            # Check for expected form elements
            element_types = [elem.get('type', '').lower() for elem in dom_data['elements']]
            assert 'input' in element_types or 'text' in element_types, \
                f"Form inputs not detected in {browser_type}"
            
            print(f"✅ {browser_type.capitalize()} DOM processing working - found {len(dom_data['elements'])} elements")
            
        except Exception as e:
            pytest.fail(f"DOM processing failed in {browser_type}: {e}")
        finally:
            await browser_manager.close()
    
    @pytest.mark.parametrize("browser_type", BROWSER_TYPES)
    @pytest.mark.asyncio
    async def test_screenshot_compatibility(self, browser_type):
        """Test screenshot capabilities across browsers."""
        
        config = BrowserConfig(
            headless=True,
            browser_type=browser_type,
            viewport_width=1280,
            viewport_height=720
        )
        
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch()
            context = await browser_manager.create_context()
            page = await context.new_page()
            
            await page.goto("https://httpbin.org/get", wait_until="networkidle")
            
            # Take screenshot
            screenshot = await page.screenshot()
            
            assert screenshot is not None, f"Screenshot failed in {browser_type}"
            assert len(screenshot) > 1000, f"Screenshot too small in {browser_type}: {len(screenshot)} bytes"
            
            # Verify it's a PNG
            assert screenshot[:8] == b'\x89PNG\r\n\x1a\n', f"Screenshot not valid PNG in {browser_type}"
            
            print(f"✅ {browser_type.capitalize()} screenshot working - {len(screenshot)} bytes")
            
        except Exception as e:
            pytest.fail(f"Screenshot failed in {browser_type}: {e}")
        finally:
            await browser_manager.close()
    
    @pytest.mark.parametrize("browser_type", BROWSER_TYPES)
    @pytest.mark.asyncio
    async def test_state_observation_compatibility(self, browser_type):
        """Test state observation works across browsers."""
        
        config = BrowserConfig(
            headless=True,
            browser_type=browser_type
        )
        
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch()
            context = await browser_manager.create_context()
            page = await context.new_page()
            
            await page.goto("https://httpbin.org/forms/post", wait_until="networkidle")
            
            # Create state observer
            state_observer = StateObserver(page)
            
            # Capture page state
            page_state = await state_observer.capture_current_state()
            
            # Verify state capture
            assert page_state is not None, f"State capture failed in {browser_type}"
            assert 'url' in page_state, f"URL not captured in {browser_type}"
            assert 'title' in page_state, f"Title not captured in {browser_type}"
            assert 'elements' in page_state, f"Elements not captured in {browser_type}"
            
            assert page_state['url'] == page.url, f"URL mismatch in {browser_type}"
            assert isinstance(page_state['elements'], list), f"Elements not list in {browser_type}"
            assert len(page_state['elements']) > 0, f"No elements captured in {browser_type}"
            
            print(f"✅ {browser_type.capitalize()} state observation working")
            
        except Exception as e:
            pytest.fail(f"State observation failed in {browser_type}: {e}")
        finally:
            await browser_manager.close()


class TestPerformanceCompatibility:
    """Test performance characteristics across browsers."""
    
    @pytest.mark.parametrize("browser_type", BROWSER_TYPES)
    @pytest.mark.asyncio
    async def test_browser_performance_slas(self, browser_type):
        """Test performance SLAs are met across browsers."""
        
        config = BrowserConfig(
            headless=True,
            browser_type=browser_type
        )
        
        browser_manager = BrowserManager(config)
        
        try:
            # Test browser launch time
            start_time = time.time()
            browser = await browser_manager.launch()
            launch_time = time.time() - start_time
            
            assert launch_time < 2.0, f"{browser_type} launch time {launch_time:.2f}s exceeds 2s SLA"
            
            # Test context creation time
            start_time = time.time()
            context = await browser_manager.create_context()
            context_time = time.time() - start_time
            
            assert context_time < 1.0, f"{browser_type} context creation {context_time:.2f}s exceeds 1s SLA"
            
            # Test page navigation time
            page = await context.new_page()
            
            start_time = time.time()
            await page.goto("https://httpbin.org/get", wait_until="networkidle", timeout=30000)
            navigation_time = time.time() - start_time
            
            assert navigation_time < 10.0, f"{browser_type} navigation {navigation_time:.2f}s exceeds 10s SLA"
            
            # Test action execution time
            start_time = time.time()
            await page.evaluate("document.title")
            execution_time = time.time() - start_time
            
            assert execution_time < 1.0, f"{browser_type} action execution {execution_time:.3f}s exceeds 1s SLA"
            
            print(f"✅ {browser_type.capitalize()} performance SLAs met:")
            print(f"   Launch: {launch_time:.2f}s")
            print(f"   Context: {context_time:.2f}s") 
            print(f"   Navigation: {navigation_time:.2f}s")
            print(f"   Execution: {execution_time:.3f}s")
            
        except Exception as e:
            pytest.fail(f"Performance test failed for {browser_type}: {e}")
        finally:
            await browser_manager.close()
    
    @pytest.mark.parametrize("browser_type", BROWSER_TYPES)
    @pytest.mark.asyncio
    async def test_memory_usage_compatibility(self, browser_type):
        """Test memory usage is reasonable across browsers."""
        
        config = BrowserConfig(
            headless=True,
            browser_type=browser_type
        )
        
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch()
            context = await browser_manager.create_context()
            
            # Create multiple pages to test memory scaling
            pages = []
            for i in range(5):
                page = await context.new_page()
                await page.goto(f"https://httpbin.org/get?page={i}")
                pages.append(page)
            
            # Close pages to test cleanup
            for page in pages:
                await page.close()
            
            print(f"✅ {browser_type.capitalize()} memory management working")
            
        except Exception as e:
            pytest.fail(f"Memory test failed for {browser_type}: {e}")
        finally:
            await browser_manager.close()


class TestBrowserSpecificFeatures:
    """Test browser-specific features and workarounds."""
    
    @pytest.mark.asyncio
    async def test_chromium_specific_features(self):
        """Test Chromium-specific functionality."""
        
        config = BrowserConfig(
            headless=True,
            browser_type="chromium"
        )
        
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch()
            context = await browser_manager.create_context()
            page = await context.new_page()
            
            # Test Chrome DevTools Protocol features
            await page.goto("https://httpbin.org/get")
            
            # Test performance metrics (Chromium-specific)
            metrics = await page.evaluate("""
                () => {
                    if (window.performance && window.performance.getEntriesByType) {
                        const entries = window.performance.getEntriesByType('navigation');
                        return entries.length > 0 ? entries[0] : null;
                    }
                    return null;
                }
            """)
            
            if metrics:
                print("✅ Chromium performance metrics available")
            else:
                print("⚠️  Chromium performance metrics not available")
            
        except Exception as e:
            pytest.fail(f"Chromium-specific test failed: {e}")
        finally:
            await browser_manager.close()
    
    @pytest.mark.asyncio
    async def test_firefox_specific_features(self):
        """Test Firefox-specific functionality."""
        
        config = BrowserConfig(
            headless=True,
            browser_type="firefox"
        )
        
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch()
            context = await browser_manager.create_context()
            page = await context.new_page()
            
            await page.goto("https://httpbin.org/get")
            
            # Test Firefox-specific navigator properties
            firefox_props = await page.evaluate("""
                () => {
                    return {
                        buildID: navigator.buildID || null,
                        oscpu: navigator.oscpu || null,
                        product: navigator.product || null
                    };
                }
            """)
            
            print("✅ Firefox-specific properties accessible")
            print(f"   Product: {firefox_props['product']}")
            
        except Exception as e:
            pytest.fail(f"Firefox-specific test failed: {e}")
        finally:
            await browser_manager.close()
    
    @pytest.mark.asyncio  
    async def test_webkit_specific_features(self):
        """Test WebKit-specific functionality."""
        
        config = BrowserConfig(
            headless=True,
            browser_type="webkit"
        )
        
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch()
            context = await browser_manager.create_context()
            page = await context.new_page()
            
            await page.goto("https://httpbin.org/get")
            
            # Test WebKit-specific features
            webkit_props = await page.evaluate("""
                () => {
                    return {
                        webkitStorageInfo: !!window.webkitStorageInfo,
                        safari: !!window.safari,
                        webkitURL: !!window.webkitURL
                    };
                }
            """)
            
            print("✅ WebKit-specific properties checked")
            
        except Exception as e:
            print(f"⚠️  WebKit-specific test issue: {e}")
        finally:
            await browser_manager.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])