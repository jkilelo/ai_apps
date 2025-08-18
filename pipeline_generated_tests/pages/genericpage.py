"""
Generic Page Object Model
Works with any website without specific customization
"""

from typing import Optional, List
from playwright.sync_api import Page, Locator
import logging

logger = logging.getLogger(__name__)


class GenericPage:
    """Generic page object that adapts to any website."""
    
    def __init__(self, page: Page, url: str = None):
        self.page = page
        self.url = url
        
    def navigate_to(self, url: str = None) -> None:
        """Navigate to URL."""
        target = url or self.url
        if target:
            self.page.goto(target)
            
    def smart_click(self, text: str = None, selector: str = None) -> bool:
        """Click element by text or selector."""
        try:
            if text:
                self.page.locator(f"text={text}").first.click()
            elif selector:
                self.page.locator(selector).first.click()
            return True
        except:
            return False
            
    def smart_fill(self, value: str, placeholder: str = None, label: str = None, selector: str = None) -> bool:
        """Fill input by placeholder, label, or selector."""
        try:
            if placeholder:
                self.page.locator(f"[placeholder*='{placeholder}']").first.fill(value)
            elif label:
                self.page.locator(f"label:has-text('{label}') + input").first.fill(value)
            elif selector:
                self.page.locator(selector).first.fill(value)
            return True
        except:
            return False
            
    def extract_all_text(self) -> str:
        """Extract all visible text from page."""
        return self.page.locator("body").text_content() or ""
