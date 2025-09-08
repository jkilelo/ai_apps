"""
Browser context for AI agents.

This module provides the bridge between pydantic-ai agents and Playwright browser,
enabling agents to interact with web pages through a structured, type-safe interface.
"""

from __future__ import annotations

import asyncio
import base64
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path

from playwright.async_api import Page, Browser, BrowserContext as PlaywrightContext

from ..core import (
    NavigationResult,
    ElementData,
    BoundingBox,
    Point,
    BrowserState,
    DEFAULT_TIMEOUT,
)
from ..config import UnifiedConfig
from .dom_extractor import DOMExtractor, DOMElement
from .stealth import StealthManager, StealthConfig


@dataclass
class PageInfo:
    """Current page information."""
    url: str
    title: str
    html_length: int
    screenshot_b64: Optional[str] = None
    viewport: Dict[str, int] = field(default_factory=dict)
    load_state: str = "unknown"
    
    
@dataclass
class ElementInfo:
    """Information about a web element."""
    selector: str
    tag_name: str
    text: str
    attributes: Dict[str, str]
    bounding_box: Optional[BoundingBox]
    is_visible: bool
    is_enabled: bool


class BrowserContext:
    """
    Browser context for AI agents.
    
    This class provides a high-level interface for AI agents to interact
    with Playwright browser instances. It maintains state and provides
    structured access to browser capabilities.
    """
    
    def __init__(self, config: UnifiedConfig) -> None:
        """Initialize browser context."""
        self.config = config
        self._browser: Optional[Browser] = None
        self._context: Optional[PlaywrightContext] = None  
        self._page: Optional[Page] = None
        self._state = BrowserState.CLOSED
        self._current_url: Optional[str] = None
        self._action_history: List[Dict[str, Any]] = []
        self._dom_extractor: Optional[DOMExtractor] = None
        
        # Initialize stealth manager with configuration
        stealth_config = StealthConfig(
            override_webdriver=True,
            randomize_user_agent=getattr(config.browser, 'randomize_user_agent', False),
            override_navigator=True,
            override_permissions=True,
            randomize_viewport=getattr(config.browser, 'randomize_viewport', False),
            inject_canvas_noise=True,
            spoof_timezone=True,
            block_webrtc=True
        )
        self._stealth_manager = StealthManager(stealth_config)
        
    @property
    def browser(self) -> Optional[Browser]:
        """Get browser instance."""
        return self._browser
        
    @property
    def page(self) -> Optional[Page]:
        """Get current page."""
        return self._page
        
    @property 
    def state(self) -> BrowserState:
        """Get browser state."""
        return self._state
        
    @property
    def current_url(self) -> Optional[str]:
        """Get current URL."""
        return self._current_url
    
    # ============================================================================
    # LIFECYCLE MANAGEMENT
    # ============================================================================
    
    async def initialize(self, browser: Browser) -> bool:
        """Initialize browser context."""
        try:
            self._browser = browser
            # Get viewport (with optional randomization)
            viewport = self._stealth_manager.get_random_viewport()
            
            # Create context with stealth configuration
            self._context = await browser.new_context(
                viewport=viewport,
                user_agent=self.config.browser.user_agent or self._stealth_manager._get_random_user_agent(),
                ignore_https_errors=not self.config.security.strict_ssl,
            )
            
            # Apply stealth measures to context
            await self._stealth_manager.apply_stealth_to_context(self._context)
            
            self._page = await self._context.new_page()
            
            # Apply stealth measures to page
            await self._stealth_manager.apply_stealth_to_page(self._page)
            
            self._state = BrowserState.READY
            
            # Set up page event listeners
            self._page.on('load', self._on_page_load)
            self._page.on('domcontentloaded', self._on_dom_ready)
            
            # Initialize DOM extractor
            self._dom_extractor = DOMExtractor(self._page)
            
            return True
            
        except Exception as e:
            self._state = BrowserState.ERROR
            return False
    
    async def close(self) -> None:
        """Close browser context."""
        if self._context:
            await self._context.close()
            self._context = None
            self._page = None
            self._state = BrowserState.CLOSED
    
    # ============================================================================
    # PAGE INFORMATION
    # ============================================================================
    
    async def get_page_info(self, include_screenshot: bool = True) -> PageInfo:
        """Get current page information."""
        if not self._page:
            raise RuntimeError("Browser not initialized")
            
        screenshot_b64 = None
        if include_screenshot:
            screenshot_bytes = await self._page.screenshot()
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
        
        viewport = await self._page.evaluate("() => ({width: window.innerWidth, height: window.innerHeight})")
        
        return PageInfo(
            url=self._page.url,
            title=await self._page.title(),
            html_length=len(await self._page.content()),
            screenshot_b64=screenshot_b64,
            viewport=viewport,
            load_state=self._page.url != 'about:blank' and 'loaded' or 'empty'
        )
    
    async def get_visible_text(self, max_length: int = 5000) -> str:
        """Get visible text content of the page."""
        if not self._page:
            return ""
            
        text = await self._page.evaluate("""
            () => {
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    {
                        acceptNode: (node) => {
                            const parent = node.parentElement;
                            if (!parent) return NodeFilter.FILTER_REJECT;
                            
                            const style = window.getComputedStyle(parent);
                            if (style.display === 'none' || style.visibility === 'hidden') {
                                return NodeFilter.FILTER_REJECT;
                            }
                            
                            return NodeFilter.FILTER_ACCEPT;
                        }
                    }
                );
                
                let text = '';
                let node;
                while (node = walker.nextNode()) {
                    text += node.textContent.trim() + ' ';
                }
                
                return text.trim();
            }
        """)
        
        return text[:max_length] if text else ""
    
    # ============================================================================
    # NAVIGATION METHODS  
    # ============================================================================
    
    async def navigate_to(self, url: str, timeout: Optional[int] = None) -> NavigationResult:
        """Navigate to URL."""
        if not self._page:
            return NavigationResult(
                success=False,
                url=url,
                final_url="",
                title="",
                load_time=0,
                error="Browser not initialized"
            )
        
        start_time = asyncio.get_event_loop().time()
        timeout_ms = timeout or self.config.navigation.timeouts.navigation
        
        try:
            response = await self._page.goto(url, timeout=timeout_ms, wait_until='load')
            end_time = asyncio.get_event_loop().time()
            
            self._current_url = self._page.url
            self._record_action('navigate', {'url': url, 'final_url': self._current_url})
            
            return NavigationResult(
                success=True,
                url=url,
                final_url=self._page.url,
                title=await self._page.title(),
                load_time=end_time - start_time,
                status_code=response.status if response else 200
            )
            
        except Exception as e:
            end_time = asyncio.get_event_loop().time()
            return NavigationResult(
                success=False,
                url=url,
                final_url=self._current_url or "",
                title="",
                load_time=end_time - start_time,
                error=str(e)
            )
    
    # ============================================================================
    # ELEMENT INTERACTION
    # ============================================================================
    
    async def find_element(self, selector: str) -> Optional[ElementInfo]:
        """Find element by selector."""
        if not self._page:
            return None
            
        try:
            element = await self._page.wait_for_selector(selector, timeout=5000)
            if not element:
                return None
                
            # Get element information
            bounding_box = await element.bounding_box()
            bbox = BoundingBox(
                x=bounding_box['x'],
                y=bounding_box['y'], 
                width=bounding_box['width'],
                height=bounding_box['height']
            ) if bounding_box else None
            
            return ElementInfo(
                selector=selector,
                tag_name=await element.get_attribute('tagName') or 'unknown',
                text=await element.text_content() or '',
                attributes=await element.evaluate('el => Object.fromEntries([...el.attributes].map(a => [a.name, a.value]))'),
                bounding_box=bbox,
                is_visible=await element.is_visible(),
                is_enabled=await element.is_enabled()
            )
            
        except Exception:
            return None
    
    async def click_element(self, selector: str) -> bool:
        """Click element by selector."""
        if not self._page:
            return False
            
        try:
            await self._page.click(selector, timeout=10000)
            self._record_action('click', {'selector': selector})
            return True
        except Exception:
            return False
    
    async def type_text(self, selector: str, text: str, clear: bool = True) -> bool:
        """Type text into element."""
        if not self._page:
            return False
            
        try:
            if clear:
                await self._page.fill(selector, text)
            else:
                await self._page.type(selector, text)
                
            self._record_action('type', {'selector': selector, 'text': text[:50]})
            return True
        except Exception:
            return False
    
    # ============================================================================
    # ADVANCED OPERATIONS
    # ============================================================================
    
    async def take_screenshot(self, file_path: Optional[str] = None) -> bytes:
        """Take screenshot of current page."""
        if not self._page:
            return b''
            
        screenshot = await self._page.screenshot(
            path=file_path,
            full_page=True
        )
        self._record_action('screenshot', {'file_path': file_path})
        return screenshot
    
    async def execute_script(self, script: str) -> Any:
        """Execute JavaScript in page context."""
        if not self._page:
            return None
            
        try:
            result = await self._page.evaluate(script)
            self._record_action('execute_script', {'script': script[:100]})
            return result
        except Exception as e:
            return {'error': str(e)}
    
    async def wait_for_condition(self, condition: str, timeout: int = 10000) -> bool:
        """Wait for JavaScript condition to be true."""
        if not self._page:
            return False
            
        try:
            await self._page.wait_for_function(condition, timeout=timeout)
            return True
        except Exception:
            return False
    
    # ============================================================================
    # ACTION HISTORY
    # ============================================================================
    
    def _record_action(self, action_type: str, details: Dict[str, Any]) -> None:
        """Record action in history."""
        self._action_history.append({
            'type': action_type,
            'details': details,
            'timestamp': asyncio.get_event_loop().time(),
            'url': self._current_url
        })
        
        # Keep only last 50 actions
        if len(self._action_history) > 50:
            self._action_history = self._action_history[-50:]
    
    def get_action_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent action history."""
        return self._action_history[-limit:]
    
    # ============================================================================
    # AI-FIRST DOM INTERACTION (Browser-use Inspired)
    # ============================================================================
    
    async def extract_interactive_elements(self) -> List[DOMElement]:
        """Extract all interactive elements with numbered indices for AI interaction."""
        if not self._dom_extractor:
            return []
        return await self._dom_extractor.extract_interactive_elements()
    
    async def get_page_summary_for_ai(self) -> str:
        """Get AI-friendly summary of current page with numbered elements."""
        if not self._page:
            return "No page loaded"
        
        if not self._dom_extractor:
            return "DOM extractor not available"
        
        # Extract elements first
        await self._dom_extractor.extract_interactive_elements()
        
        # Get page info
        page_info = await self.get_page_info(include_screenshot=False)
        
        # Build comprehensive summary
        summary = f"📄 Current page: {page_info.title}\n🔗 URL: {page_info.url}\n\n"
        
        # Add AI-friendly element summary
        element_summary = self._dom_extractor.get_ai_friendly_summary()
        summary += element_summary
        
        # Add page text preview
        visible_text = await self.get_visible_text(500)
        if visible_text:
            summary += f"\n\n📝 Page text preview:\n{visible_text[:300]}..."
        
        return summary
    
    async def click_element_by_index(self, index: int) -> bool:
        """Click element by its numbered index (AI-friendly interaction)."""
        if not self._dom_extractor:
            return False
        
        success = await self._dom_extractor.click_element(index)
        if success:
            self._record_action('click_by_index', {'index': index})
        return success
    
    async def type_in_element_by_index(self, index: int, text: str) -> bool:
        """Type text in element by its numbered index (AI-friendly interaction)."""
        if not self._dom_extractor:
            return False
        
        success = await self._dom_extractor.type_in_element(index, text)
        if success:
            self._record_action('type_by_index', {'index': index, 'text': text[:50]})
        return success
    
    async def get_element_info_by_index(self, index: int) -> Optional[DOMElement]:
        """Get detailed information about an element by its index."""
        if not self._dom_extractor:
            return None
        return self._dom_extractor.get_element_info(index)
    
    async def find_elements_by_text(self, text: str, exact: bool = False) -> List[int]:
        """Find elements containing specific text, returns their indices."""
        if not self._dom_extractor:
            return []
        return self._dom_extractor.find_elements_by_text(text, exact)
    
    async def take_annotated_screenshot(self, file_path: Optional[str] = None) -> str:
        """Take screenshot with numbered element overlays for AI visualization."""
        if not self._dom_extractor:
            if file_path:
                await self.take_screenshot(file_path)
                return file_path
            return ""
        
        # Ensure elements are extracted first
        await self._dom_extractor.extract_interactive_elements()
        
        # Generate filename if not provided
        if not file_path:
            import time
            file_path = f"page_annotated_{int(time.time())}.png"
        
        annotated_path = await self._dom_extractor.annotate_screenshot(file_path)
        self._record_action('annotated_screenshot', {'file_path': annotated_path})
        return annotated_path
    
    async def wait_for_page_change(self, timeout: int = 5000) -> bool:
        """Wait for interactive elements on page to change (useful after actions)."""
        if not self._dom_extractor:
            return False
        return await self._dom_extractor.wait_for_element_change(timeout)
    
    # ============================================================================
    # EVENT HANDLERS
    # ============================================================================
    
    async def _on_page_load(self) -> None:
        """Handle page load event."""
        self._current_url = self._page.url if self._page else None
        
    async def _on_dom_ready(self) -> None:
        """Handle DOM content loaded event."""
        # Re-extract elements when DOM is ready
        if self._dom_extractor:
            await self._dom_extractor.extract_interactive_elements()