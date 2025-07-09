"""
LLM Query page object
"""
from playwright.async_api import Page, Locator
from .base_page import BasePage


class LLMPage(BasePage):
    """Page object for LLM Query feature"""
    
    def __init__(self, page: Page):
        super().__init__(page)
        self.path = "#llm"
        
    # Page elements
    @property
    def query_form(self) -> Locator:
        return self.page.locator("#queryForm")
        
    @property
    def prompt_textarea(self) -> Locator:
        return self.page.locator("#prompt")
        
    @property
    def char_count(self) -> Locator:
        return self.page.locator("#charCount")
        
    @property
    def clear_button(self) -> Locator:
        return self.page.locator("#clearBtn")
        
    @property
    def submit_button(self) -> Locator:
        return self.page.locator("#submitBtn")
        
    @property
    def submit_text(self) -> Locator:
        return self.page.locator("#submitText")
        
    @property
    def response_section(self) -> Locator:
        return self.page.locator("#responseSection")
        
    @property
    def response_content(self) -> Locator:
        return self.page.locator("#responseContent")
        
    @property
    def loading_indicator(self) -> Locator:
        return self.page.locator("#loadingIndicator")
        
    @property
    def copy_button(self) -> Locator:
        return self.page.locator("#copyBtn")
        
    @property
    def history_section(self) -> Locator:
        return self.page.locator("#historySection")
        
    @property
    def history_list(self) -> Locator:
        return self.page.locator("#historyList")
        
    @property
    def history_items(self) -> Locator:
        return self.page.locator(".history-item")
        
    # Page actions
    async def navigate(self):
        """Navigate to LLM Query page"""
        await self.navigate_to(self.path)
        await self.wait_for_query_form()
        
    async def wait_for_query_form(self):
        """Wait for query form to be visible"""
        await self.query_form.wait_for(state="visible", timeout=self.timeout)
        
    async def type_prompt(self, text: str):
        """Type text into prompt textarea"""
        await self.clear_and_type("#prompt", text)
        
    async def get_char_count_text(self) -> str:
        """Get character count text"""
        return await self.char_count.text_content()
        
    async def clear_prompt(self):
        """Click clear button"""
        await self.clear_button.click()
        
    async def submit_query(self):
        """Submit the query"""
        await self.submit_button.click()
        
    async def wait_for_response(self, timeout: int = 30000):
        """Wait for response to load"""
        # Wait for loading to disappear
        await self.loading_indicator.wait_for(state="hidden", timeout=timeout)
        
    async def get_response_text(self) -> str:
        """Get response content text"""
        return await self.response_content.text_content()
        
    async def is_response_visible(self) -> bool:
        """Check if response section is visible"""
        return await self.response_section.is_visible()
        
    async def copy_response(self):
        """Click copy response button"""
        await self.copy_button.click()
        
    async def get_history_count(self) -> int:
        """Get number of history items"""
        return await self.history_items.count()
        
    async def click_history_item(self, index: int):
        """Click specific history item"""
        await self.history_items.nth(index).click()
        
    async def get_history_prompt(self, index: int) -> str:
        """Get prompt text from history item"""
        item = self.history_items.nth(index)
        return await item.locator(".history-prompt").text_content()
        
    async def is_history_visible(self) -> bool:
        """Check if history section is visible"""
        return await self.history_section.is_visible()
        
    async def get_submit_button_text(self) -> str:
        """Get submit button text"""
        return await self.submit_text.text_content()
        
    async def is_submit_button_enabled(self) -> bool:
        """Check if submit button is enabled"""
        return await self.submit_button.is_enabled()
        
    async def press_ctrl_enter(self):
        """Press Ctrl+Enter keyboard shortcut"""
        await self.prompt_textarea.focus()
        await self.page.keyboard.down("Control")
        await self.page.keyboard.press("Enter")
        await self.page.keyboard.up("Control")