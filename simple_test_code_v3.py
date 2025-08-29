"""
Generated Test Code - 2025-08-28T11:29:27.328649
Framework: playwright
Browser: playwright
Pattern: direct
"""

from playwright.sync_api import sync_playwright
from typing import Any

# Helper Methods
async def verify_element(page: Page, selector: str, timeout: int = 5000) -> bool:
    """Verifies the presence and visibility of a given element on the page.

    Args:
        page: The Playwright Page object.
        selector: The CSS selector for the element to verify.
        timeout: The maximum time in milliseconds to wait for the element.

    Returns:
        True if the element is found and visible, False otherwise.
    """
    try:
        await page.wait_for_selector(selector, state='visible', timeout=timeout)
        return True
    except Exception:
        return False

# Test Methods
def playwright_page(browser_type: BrowserType) -> Page:
    """
    Provides a Playwright Page instance for testing.
    """
    try:
        browser = browser_type.launch()
        page = browser.new_page()
        yield page
        browser.close()
    except Exception as e:
        pytest.fail(f"Failed to initialize Playwright page: {e}")
