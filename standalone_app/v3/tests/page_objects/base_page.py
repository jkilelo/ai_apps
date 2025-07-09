"""
Base page object with common functionality
"""
from typing import Optional, List, Dict, Any
from playwright.async_api import Page, Locator, expect
import asyncio


class BasePage:
    """Base class for all page objects"""
    
    def __init__(self, page: Page):
        self.page = page
        self.timeout = 30000  # 30 seconds default timeout
        
    # Navigation elements
    @property
    def header(self) -> Locator:
        return self.page.locator("header.app-header")
        
    @property
    def main_nav(self) -> Locator:
        return self.page.locator("nav.main-nav")
        
    @property
    def nav_links(self) -> Locator:
        return self.page.locator("nav.main-nav a.nav-link")
        
    @property
    def theme_toggle(self) -> Locator:
        return self.page.locator("button.theme-toggle")
        
    @property
    def mobile_menu_toggle(self) -> Locator:
        return self.page.locator("button.menu-toggle")
        
    @property
    def footer(self) -> Locator:
        return self.page.locator("footer.app-footer")
        
    @property
    def loading_overlay(self) -> Locator:
        return self.page.locator("div.loading-overlay")
        
    @property
    def toast_container(self) -> Locator:
        return self.page.locator("div.toast-container")
        
    async def navigate_to(self, path: str = ""):
        """Navigate to page"""
        await self.page.goto(f"/{path}")
        await self.wait_for_load()
        
    async def wait_for_load(self):
        """Wait for page to fully load"""
        await self.page.wait_for_load_state("networkidle")
        await self.loading_overlay.wait_for(state="hidden", timeout=self.timeout)
        
    async def click_nav_link(self, link_text: str):
        """Click navigation link by text"""
        await self.nav_links.filter(has_text=link_text).click()
        await self.wait_for_load()
        
    async def toggle_theme(self):
        """Toggle theme between light and dark"""
        await self.theme_toggle.click()
        await self.page.wait_for_timeout(300)  # Wait for transition
        
    async def get_current_theme(self) -> str:
        """Get current theme"""
        return await self.page.evaluate("document.documentElement.getAttribute('data-theme')")
        
    async def toggle_mobile_menu(self):
        """Toggle mobile menu"""
        await self.mobile_menu_toggle.click()
        await self.page.wait_for_timeout(300)  # Wait for animation
        
    async def is_mobile_menu_open(self) -> bool:
        """Check if mobile menu is open"""
        aria_expanded = await self.mobile_menu_toggle.get_attribute("aria-expanded")
        return aria_expanded == "true"
        
    async def wait_for_toast(self, timeout: int = 5000) -> Locator:
        """Wait for toast notification to appear"""
        toast = self.page.locator(".toast-message").first
        await toast.wait_for(state="visible", timeout=timeout)
        return toast
        
    async def get_toast_message(self) -> str:
        """Get current toast message text"""
        toast = await self.wait_for_toast()
        return await toast.text_content()
        
    async def close_toast(self):
        """Close toast notification"""
        close_button = self.page.locator(".toast-close").first
        if await close_button.is_visible():
            await close_button.click()
            
    async def wait_for_element(self, selector: str, state: str = "visible", timeout: Optional[int] = None):
        """Wait for element with specific state"""
        timeout = timeout or self.timeout
        await self.page.wait_for_selector(selector, state=state, timeout=timeout)
        
    async def is_element_visible(self, selector: str) -> bool:
        """Check if element is visible"""
        return await self.page.is_visible(selector)
        
    async def get_element_text(self, selector: str) -> str:
        """Get text content of element"""
        return await self.page.text_content(selector)
        
    async def click_element(self, selector: str):
        """Click element and wait for any navigation"""
        await self.page.click(selector)
        await self.page.wait_for_load_state("networkidle")
        
    async def type_text(self, selector: str, text: str, delay: int = 50):
        """Type text with realistic delay"""
        await self.page.type(selector, text, delay=delay)
        
    async def clear_and_type(self, selector: str, text: str):
        """Clear field and type new text"""
        await self.page.click(selector, click_count=3)  # Triple click to select all
        await self.page.keyboard.press("Backspace")
        await self.type_text(selector, text)
        
    async def press_key(self, key: str):
        """Press keyboard key"""
        await self.page.keyboard.press(key)
        
    async def scroll_to_element(self, selector: str):
        """Scroll element into view"""
        await self.page.evaluate(f"""
            document.querySelector('{selector}').scrollIntoView({{
                behavior: 'smooth',
                block: 'center'
            }});
        """)
        await self.page.wait_for_timeout(500)  # Wait for scroll animation
        
    async def get_viewport_size(self) -> Dict[str, int]:
        """Get current viewport size"""
        return await self.page.evaluate("""() => ({
            width: window.innerWidth,
            height: window.innerHeight
        })""")
        
    async def is_mobile_viewport(self) -> bool:
        """Check if current viewport is mobile size"""
        size = await self.get_viewport_size()
        return size["width"] < 768
        
    async def take_screenshot(self, name: str, full_page: bool = True):
        """Take screenshot with specific name"""
        await self.page.screenshot(
            path=f"test_reports/screenshots/{name}.png",
            full_page=full_page
        )
        
    async def get_network_activity(self) -> List[Dict[str, Any]]:
        """Get network activity for debugging"""
        return await self.page.evaluate("""() => {
            return performance.getEntriesByType('resource').map(entry => ({
                name: entry.name,
                duration: entry.duration,
                size: entry.transferSize,
                type: entry.initiatorType
            }));
        }""")
        
    async def wait_for_api_call(self, url_pattern: str, timeout: int = 10000):
        """Wait for specific API call to complete"""
        async with self.page.expect_response(
            lambda response: url_pattern in response.url,
            timeout=timeout
        ) as response_info:
            response = await response_info.value
            return response
            
    async def check_accessibility(self):
        """Basic accessibility checks"""
        # Check for page title
        title = await self.page.title()
        assert title, "Page must have a title"
        
        # Check for focus indication
        await self.page.keyboard.press("Tab")
        focused_element = await self.page.evaluate("document.activeElement.tagName")
        assert focused_element != "BODY", "Page must have focusable elements"
        
        # Check for alt text on images
        images_without_alt = await self.page.query_selector_all("img:not([alt])")
        assert not images_without_alt, f"Found {len(images_without_alt)} images without alt text"
        
    async def measure_performance(self) -> Dict[str, float]:
        """Measure page performance metrics"""
        metrics = await self.page.evaluate("""() => {
            const navigation = performance.getEntriesByType('navigation')[0];
            const paint = performance.getEntriesByType('paint');
            
            return {
                domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
                firstPaint: paint.find(p => p.name === 'first-paint')?.startTime || 0,
                firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0
            };
        }""")
        
        return metrics