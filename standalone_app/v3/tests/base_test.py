"""
Base test class with common functionality for all tests
"""
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json
import pytest
from playwright.async_api import Page, expect


class BaseTest:
    """Base class for all test classes"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, take_screenshot):
        """Setup for each test"""
        self.page = page
        self.take_screenshot = take_screenshot
        self.test_start_time = datetime.now()
        
    async def navigate_to(self, path: str):
        """Navigate to a specific path"""
        await self.page.goto(path)
        await self.page.wait_for_load_state("networkidle")
        
    async def wait_for_element(self, selector: str, timeout: int = 5000):
        """Wait for element to be visible"""
        await self.page.wait_for_selector(selector, state="visible", timeout=timeout)
        
    async def click_and_wait(self, selector: str, wait_for: Optional[str] = None):
        """Click element and wait for navigation or another element"""
        await self.page.click(selector)
        
        if wait_for:
            await self.wait_for_element(wait_for)
        else:
            await self.page.wait_for_load_state("networkidle")
            
    async def fill_form_field(self, selector: str, value: str, tab_out: bool = True):
        """Fill form field with value"""
        await self.page.fill(selector, value)
        
        if tab_out:
            await self.page.press(selector, "Tab")
            
    async def assert_element_visible(self, selector: str):
        """Assert element is visible"""
        await expect(self.page.locator(selector)).to_be_visible()
        
    async def assert_element_hidden(self, selector: str):
        """Assert element is hidden"""
        await expect(self.page.locator(selector)).to_be_hidden()
        
    async def assert_text_content(self, selector: str, expected_text: str):
        """Assert element contains specific text"""
        await expect(self.page.locator(selector)).to_contain_text(expected_text)
        
    async def assert_element_count(self, selector: str, expected_count: int):
        """Assert specific number of elements exist"""
        await expect(self.page.locator(selector)).to_have_count(expected_count)
        
    async def get_element_text(self, selector: str) -> str:
        """Get text content of element"""
        return await self.page.text_content(selector)
        
    async def get_element_attribute(self, selector: str, attribute: str) -> str:
        """Get attribute value of element"""
        return await self.page.get_attribute(selector, attribute)
        
    async def is_element_enabled(self, selector: str) -> bool:
        """Check if element is enabled"""
        return await self.page.is_enabled(selector)
        
    async def is_element_checked(self, selector: str) -> bool:
        """Check if checkbox/radio is checked"""
        return await self.page.is_checked(selector)
        
    async def wait_for_api_response(self, url_pattern: str, timeout: int = 10000):
        """Wait for specific API response"""
        async with self.page.expect_response(
            lambda response: url_pattern in response.url,
            timeout=timeout
        ) as response_info:
            response = await response_info.value
            return await response.json()
            
    async def mock_api_response(self, url_pattern: str, response_data: Dict[str, Any]):
        """Mock API response for testing"""
        await self.page.route(url_pattern, lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(response_data)
        ))
        
    async def check_console_errors(self):
        """Check for console errors"""
        console_errors = []
        
        def handle_console(msg):
            if msg.type == "error":
                console_errors.append(msg.text)
                
        self.page.on("console", handle_console)
        
        # Wait a bit for any errors to appear
        await self.page.wait_for_timeout(1000)
        
        assert not console_errors, f"Console errors found: {console_errors}"
        
    async def measure_load_time(self) -> float:
        """Measure page load time"""
        timing = await self.page.evaluate("""() => {
            const navigation = performance.getEntriesByType('navigation')[0];
            return navigation.loadEventEnd - navigation.fetchStart;
        }""")
        
        return timing / 1000  # Convert to seconds
        
    async def capture_test_evidence(self, step_name: str):
        """Capture evidence for test step"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Take screenshot
        screenshot_path = await self.take_screenshot(f"{self.__class__.__name__}_{step_name}")
        
        # Capture network activity
        network_log = []
        
        def log_request(request):
            network_log.append({
                "url": request.url,
                "method": request.method,
                "timestamp": datetime.now().isoformat()
            })
            
        self.page.on("request", log_request)
        
        # Wait for any pending requests
        await self.page.wait_for_load_state("networkidle")
        
        return {
            "step": step_name,
            "screenshot": screenshot_path,
            "network_log": network_log,
            "timestamp": timestamp
        }
        
    async def test_accessibility_basics(self):
        """Basic accessibility checks that all pages should pass"""
        # Check page has title
        title = await self.page.title()
        assert title, "Page must have a title"
        
        # Check page has main landmark
        main = await self.page.query_selector('main, [role="main"]')
        assert main, "Page must have a main landmark"
        
        # Check skip link exists
        skip_link = await self.page.query_selector('a[href="#main-content"]')
        assert skip_link, "Page must have skip to main content link"
        
        # Check all interactive elements are keyboard accessible
        interactive_elements = await self.page.query_selector_all(
            'button, a, input, select, textarea, [tabindex]'
        )
        
        for element in interactive_elements:
            tabindex = await element.get_attribute("tabindex")
            if tabindex and int(tabindex) < -1:
                pytest.fail(f"Element has invalid tabindex: {tabindex}")
                
    async def test_responsive_behavior(self, viewports: Optional[list] = None):
        """Test responsive behavior across different viewports"""
        if not viewports:
            viewports = [
                {"width": 320, "height": 568},   # iPhone SE
                {"width": 375, "height": 812},   # iPhone X
                {"width": 768, "height": 1024},  # iPad
                {"width": 1024, "height": 768},  # iPad landscape
                {"width": 1280, "height": 720},  # Desktop
                {"width": 1920, "height": 1080}  # Full HD
            ]
            
        for viewport in viewports:
            await self.page.set_viewport_size(viewport)
            await self.page.wait_for_timeout(500)  # Wait for any animations
            
            # Take screenshot for each viewport
            await self.take_screenshot(
                f"{self.__class__.__name__}_viewport_{viewport['width']}x{viewport['height']}"
            )