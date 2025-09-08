"""
Base browser abstraction module.

This module defines the abstract base class for all browser implementations,
establishing the core contract that all browser engines must implement.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

from ..config import UnifiedConfig
from ..core import (
    BrowserState,
    BrowserAction,
    ExtractionResult,
    NavigationResult,
    PerformanceMetrics,
    Point,
    BoundingBox,
    ElementData,
    ContentType,
    Selector,
    JSFunction,
    JSResult,
    HeadersDict,
    CookiesDict,
    Coordinates,
)


class BaseBrowser(ABC):
    """
    Abstract base class for all browser implementations.
    
    This class defines the core contract that all browser engines (Playwright,
    Selenium, undetected-chromedriver, etc.) must implement to be part of the
    unified browser system.
    """
    
    def __init__(self, config: UnifiedConfig) -> None:
        """Initialize the browser with configuration."""
        self.config = config
        self._state = BrowserState.CLOSED
        self._performance_metrics = PerformanceMetrics()
        self._current_url: Optional[str] = None
        self._page_title: Optional[str] = None
        self._context_data: Dict[str, Any] = {}
    
    @property
    def state(self) -> BrowserState:
        """Get current browser state."""
        return self._state
    
    @property
    def current_url(self) -> Optional[str]:
        """Get current page URL."""
        return self._current_url
    
    @property
    def page_title(self) -> Optional[str]:
        """Get current page title."""
        return self._page_title
    
    @property
    def performance_metrics(self) -> PerformanceMetrics:
        """Get performance metrics."""
        return self._performance_metrics
    
    # ============================================================================
    # LIFECYCLE MANAGEMENT
    # ============================================================================
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the browser instance."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the browser and cleanup resources."""
        pass
    
    @asynccontextmanager
    async def managed_session(self) -> AsyncGenerator[BaseBrowser, None]:
        """Context manager for automatic browser lifecycle management."""
        try:
            await self.initialize()
            yield self
        finally:
            await self.close()
    
    # ============================================================================
    # NAVIGATION METHODS
    # ============================================================================
    
    @abstractmethod
    async def navigate(self, url: str, **kwargs) -> NavigationResult:
        """Navigate to a URL."""
        pass
    
    @abstractmethod
    async def go_back(self) -> NavigationResult:
        """Navigate back in history."""
        pass
    
    @abstractmethod
    async def go_forward(self) -> NavigationResult:
        """Navigate forward in history."""
        pass
    
    @abstractmethod
    async def refresh(self) -> NavigationResult:
        """Refresh the current page."""
        pass
    
    @abstractmethod
    async def wait_for_navigation(self, timeout: Optional[int] = None) -> NavigationResult:
        """Wait for navigation to complete."""
        pass
    
    # ============================================================================
    # ELEMENT INTERACTION METHODS
    # ============================================================================
    
    @abstractmethod
    async def find_element(self, selector: Selector, timeout: Optional[int] = None) -> Optional[ElementData]:
        """Find a single element by selector."""
        pass
    
    @abstractmethod
    async def find_elements(self, selector: Selector, timeout: Optional[int] = None) -> List[ElementData]:
        """Find multiple elements by selector."""
        pass
    
    @abstractmethod
    async def click(self, selector: Selector, **kwargs) -> bool:
        """Click an element."""
        pass
    
    @abstractmethod
    async def double_click(self, selector: Selector, **kwargs) -> bool:
        """Double-click an element."""
        pass
    
    @abstractmethod
    async def right_click(self, selector: Selector, **kwargs) -> bool:
        """Right-click an element."""
        pass
    
    @abstractmethod
    async def hover(self, selector: Selector, **kwargs) -> bool:
        """Hover over an element."""
        pass
    
    @abstractmethod
    async def scroll_to(self, selector: Selector, **kwargs) -> bool:
        """Scroll to an element."""
        pass
    
    @abstractmethod
    async def scroll_by(self, x: int, y: int) -> bool:
        """Scroll by specified pixels."""
        pass
    
    # ============================================================================
    # INPUT METHODS
    # ============================================================================
    
    @abstractmethod
    async def type_text(self, selector: Selector, text: str, **kwargs) -> bool:
        """Type text into an element."""
        pass
    
    @abstractmethod
    async def clear_text(self, selector: Selector) -> bool:
        """Clear text from an element."""
        pass
    
    @abstractmethod
    async def upload_file(self, selector: Selector, file_path: str) -> bool:
        """Upload a file to a file input element."""
        pass
    
    @abstractmethod
    async def select_option(self, selector: Selector, value: Union[str, int], **kwargs) -> bool:
        """Select an option from a dropdown."""
        pass
    
    @abstractmethod
    async def check_checkbox(self, selector: Selector, checked: bool = True) -> bool:
        """Check or uncheck a checkbox."""
        pass
    
    # ============================================================================
    # EXTRACTION METHODS
    # ============================================================================
    
    @abstractmethod
    async def extract_content(
        self, 
        content_types: List[ContentType],
        selectors: Optional[List[Selector]] = None,
        **kwargs
    ) -> ExtractionResult:
        """Extract content from the page."""
        pass
    
    @abstractmethod
    async def get_text(self, selector: Selector) -> Optional[str]:
        """Get text content of an element."""
        pass
    
    @abstractmethod
    async def get_attribute(self, selector: Selector, attribute: str) -> Optional[str]:
        """Get an attribute value of an element."""
        pass
    
    @abstractmethod
    async def get_property(self, selector: Selector, property_name: str) -> Optional[Any]:
        """Get a property value of an element."""
        pass
    
    @abstractmethod
    async def get_bounding_box(self, selector: Selector) -> Optional[BoundingBox]:
        """Get the bounding box of an element."""
        pass
    
    @abstractmethod
    async def is_visible(self, selector: Selector) -> bool:
        """Check if an element is visible."""
        pass
    
    @abstractmethod
    async def is_enabled(self, selector: Selector) -> bool:
        """Check if an element is enabled."""
        pass
    
    # ============================================================================
    # JAVASCRIPT EXECUTION
    # ============================================================================
    
    @abstractmethod
    async def execute_script(self, script: JSFunction, *args) -> JSResult:
        """Execute JavaScript in the browser context."""
        pass
    
    @abstractmethod
    async def execute_async_script(self, script: JSFunction, *args) -> JSResult:
        """Execute async JavaScript in the browser context."""
        pass
    
    # ============================================================================
    # SCREENSHOT AND PAGE SOURCE
    # ============================================================================
    
    @abstractmethod
    async def take_screenshot(self, file_path: Optional[str] = None, **kwargs) -> bytes:
        """Take a screenshot of the current page."""
        pass
    
    @abstractmethod
    async def take_element_screenshot(self, selector: Selector, file_path: Optional[str] = None) -> bytes:
        """Take a screenshot of a specific element."""
        pass
    
    @abstractmethod
    async def get_page_source(self) -> str:
        """Get the HTML source of the current page."""
        pass
    
    # ============================================================================
    # COOKIE AND SESSION MANAGEMENT
    # ============================================================================
    
    @abstractmethod
    async def get_cookies(self) -> CookiesDict:
        """Get all cookies."""
        pass
    
    @abstractmethod
    async def set_cookie(self, name: str, value: str, **kwargs) -> bool:
        """Set a cookie."""
        pass
    
    @abstractmethod
    async def delete_cookie(self, name: str) -> bool:
        """Delete a cookie."""
        pass
    
    @abstractmethod
    async def clear_cookies(self) -> bool:
        """Clear all cookies."""
        pass
    
    # ============================================================================
    # HEADERS AND NETWORK
    # ============================================================================
    
    @abstractmethod
    async def set_headers(self, headers: HeadersDict) -> bool:
        """Set custom headers."""
        pass
    
    @abstractmethod
    async def set_user_agent(self, user_agent: str) -> bool:
        """Set user agent."""
        pass
    
    @abstractmethod
    async def set_viewport(self, width: int, height: int) -> bool:
        """Set viewport size."""
        pass
    
    # ============================================================================
    # WAIT METHODS
    # ============================================================================
    
    @abstractmethod
    async def wait_for_element(self, selector: Selector, timeout: Optional[int] = None) -> Optional[ElementData]:
        """Wait for an element to appear."""
        pass
    
    @abstractmethod
    async def wait_for_element_hidden(self, selector: Selector, timeout: Optional[int] = None) -> bool:
        """Wait for an element to be hidden."""
        pass
    
    @abstractmethod
    async def wait_for_text(self, text: str, timeout: Optional[int] = None) -> bool:
        """Wait for specific text to appear on the page."""
        pass
    
    @abstractmethod
    async def wait_for_url(self, url_pattern: str, timeout: Optional[int] = None) -> bool:
        """Wait for URL to match a pattern."""
        pass
    
    @abstractmethod
    async def wait_for_condition(self, condition: JSFunction, timeout: Optional[int] = None) -> bool:
        """Wait for a custom JavaScript condition."""
        pass
    
    # ============================================================================
    # FRAME HANDLING
    # ============================================================================
    
    @abstractmethod
    async def switch_to_frame(self, frame_selector: Selector) -> bool:
        """Switch to a frame or iframe."""
        pass
    
    @abstractmethod
    async def switch_to_default_frame(self) -> bool:
        """Switch back to the main frame."""
        pass
    
    # ============================================================================
    # WINDOW AND TAB MANAGEMENT
    # ============================================================================
    
    @abstractmethod
    async def open_new_tab(self, url: Optional[str] = None) -> str:
        """Open a new tab and return its handle."""
        pass
    
    @abstractmethod
    async def close_tab(self, tab_handle: Optional[str] = None) -> bool:
        """Close a tab."""
        pass
    
    @abstractmethod
    async def switch_to_tab(self, tab_handle: str) -> bool:
        """Switch to a specific tab."""
        pass
    
    @abstractmethod
    async def get_tab_handles(self) -> List[str]:
        """Get all tab handles."""
        pass
    
    # ============================================================================
    # ALERT HANDLING
    # ============================================================================
    
    @abstractmethod
    async def handle_alert(self, accept: bool = True, prompt_text: Optional[str] = None) -> Optional[str]:
        """Handle JavaScript alerts, confirms, and prompts."""
        pass
    
    # ============================================================================
    # ADVANCED FEATURES
    # ============================================================================
    
    @abstractmethod
    async def intercept_network(self, url_pattern: str, response_handler: callable) -> bool:
        """Intercept network requests/responses."""
        pass
    
    @abstractmethod
    async def bypass_cloudflare(self) -> bool:
        """Attempt to bypass Cloudflare protection."""
        pass
    
    @abstractmethod
    async def solve_captcha(self, captcha_type: str, **kwargs) -> bool:
        """Attempt to solve CAPTCHA challenges."""
        pass
    
    @abstractmethod
    async def get_performance_timing(self) -> Dict[str, Any]:
        """Get page performance timing information."""
        pass
    
    @abstractmethod
    async def emulate_device(self, device_name: str) -> bool:
        """Emulate a specific device."""
        pass
    
    @abstractmethod
    async def set_geolocation(self, latitude: float, longitude: float) -> bool:
        """Set geolocation coordinates."""
        pass
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _update_state(self, new_state: BrowserState) -> None:
        """Update browser state."""
        self._state = new_state
    
    def _update_current_url(self, url: str) -> None:
        """Update current URL."""
        self._current_url = url
    
    def _update_page_title(self, title: str) -> None:
        """Update page title."""
        self._page_title = title
    
    def _record_action(self, action: BrowserAction) -> None:
        """Record a browser action for metrics."""
        # This could be extended to maintain action history
        pass
    
    def _log_performance_metric(self, metric_name: str, value: float) -> None:
        """Log a performance metric."""
        # Implementation would update self._performance_metrics
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the browser instance."""
        return {
            "state": self.state.value,
            "current_url": self.current_url,
            "responsive": self.state != BrowserState.CRASHED,
            "memory_usage": "unknown",  # To be implemented by subclasses
            "cpu_usage": "unknown",     # To be implemented by subclasses
        }