"""Action primitives for browser interaction"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List
from dataclasses import dataclass
from playwright.async_api import Page, Locator
from loguru import logger
import asyncio
import base64


@dataclass
class ActionResult:
    """Result of an action execution"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: Optional[float] = None
    retry_count: int = 0


class IAction(ABC):
    """Abstract interface for browser actions"""
    
    @abstractmethod
    async def execute(self, page: Page, **kwargs) -> ActionResult:
        """Execute the action on the page"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get action name"""
        pass
    
    async def execute_with_retry(self, page: Page, max_retries: int = 3, **kwargs) -> ActionResult:
        """Execute action with retry logic"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = await self.execute(page, **kwargs)
                if result.success:
                    result.retry_count = attempt
                    return result
                last_error = result.error
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
            
            if attempt < max_retries - 1:
                await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
        
        return ActionResult(
            success=False,
            error=f"Failed after {max_retries} attempts. Last error: {last_error}",
            retry_count=max_retries
        )


class ClickAction(IAction):
    """Click on an element"""
    
    def get_name(self) -> str:
        return "click"
    
    async def execute(self, page: Page, selector: str = None, element_id: int = None, 
                      element_map: Dict[int, str] = None, **kwargs) -> ActionResult:
        """Execute click action"""
        import time
        start_time = time.perf_counter()
        
        try:
            # Determine selector
            if element_id is not None and element_map:
                selector = element_map.get(element_id)
                if not selector:
                    return ActionResult(
                        success=False,
                        error=f"Element ID {element_id} not found in element map"
                    )
            
            if not selector:
                return ActionResult(
                    success=False,
                    error="No selector provided for click action"
                )
            
            # Find and click element
            locator = page.locator(selector)
            
            # Wait for element to be visible and enabled
            await locator.wait_for(state="visible", timeout=10000)
            await locator.wait_for(state="enabled", timeout=5000)
            
            # Scroll into view if needed
            await locator.scroll_into_view_if_needed()
            
            # Click the element
            await locator.click(**kwargs)
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Clicked element: {selector} (took {duration:.2f}ms)")
            
            return ActionResult(
                success=True,
                data={"selector": selector},
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"Failed to click element {selector}: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                duration_ms=duration
            )


class FillAction(IAction):
    """Fill text into an input field"""
    
    def get_name(self) -> str:
        return "fill"
    
    async def execute(self, page: Page, selector: str = None, text: str = "", 
                      element_id: int = None, element_map: Dict[int, str] = None, 
                      clear_first: bool = True, **kwargs) -> ActionResult:
        """Execute fill action"""
        import time
        start_time = time.perf_counter()
        
        try:
            # Determine selector
            if element_id is not None and element_map:
                selector = element_map.get(element_id)
                if not selector:
                    return ActionResult(
                        success=False,
                        error=f"Element ID {element_id} not found in element map"
                    )
            
            if not selector:
                return ActionResult(
                    success=False,
                    error="No selector provided for fill action"
                )
            
            # Find and fill element
            locator = page.locator(selector)
            
            # Wait for element
            await locator.wait_for(state="visible", timeout=10000)
            await locator.wait_for(state="enabled", timeout=5000)
            
            # Clear field if requested
            if clear_first:
                await locator.clear()
            
            # Fill the text
            await locator.fill(text, **kwargs)
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Filled element {selector} with text (took {duration:.2f}ms)")
            
            return ActionResult(
                success=True,
                data={"selector": selector, "text_length": len(text)},
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"Failed to fill element {selector}: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                duration_ms=duration
            )


class TypeAction(IAction):
    """Type text with human-like delay"""
    
    def get_name(self) -> str:
        return "type"
    
    async def execute(self, page: Page, selector: str = None, text: str = "",
                      element_id: int = None, element_map: Dict[int, str] = None,
                      delay: int = 50, **kwargs) -> ActionResult:
        """Execute type action with human-like delay"""
        import time
        start_time = time.perf_counter()
        
        try:
            # Determine selector
            if element_id is not None and element_map:
                selector = element_map.get(element_id)
                if not selector:
                    return ActionResult(
                        success=False,
                        error=f"Element ID {element_id} not found in element map"
                    )
            
            if not selector:
                return ActionResult(
                    success=False,
                    error="No selector provided for type action"
                )
            
            # Find and type into element
            locator = page.locator(selector)
            
            # Wait and focus
            await locator.wait_for(state="visible", timeout=10000)
            await locator.focus()
            
            # Type with delay
            await locator.type(text, delay=delay, **kwargs)
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Typed into element {selector} (took {duration:.2f}ms)")
            
            return ActionResult(
                success=True,
                data={"selector": selector, "text_length": len(text)},
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"Failed to type into element {selector}: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                duration_ms=duration
            )


class ScrollAction(IAction):
    """Scroll the page"""
    
    def get_name(self) -> str:
        return "scroll"
    
    async def execute(self, page: Page, direction: str = "down", amount: int = 500,
                      smooth: bool = True, **kwargs) -> ActionResult:
        """Execute scroll action"""
        import time
        start_time = time.perf_counter()
        
        try:
            # Determine scroll parameters
            x = 0
            y = 0
            
            if direction.lower() == "down":
                y = amount
            elif direction.lower() == "up":
                y = -amount
            elif direction.lower() == "right":
                x = amount
            elif direction.lower() == "left":
                x = -amount
            else:
                return ActionResult(
                    success=False,
                    error=f"Invalid scroll direction: {direction}"
                )
            
            # Execute scroll
            if smooth:
                await page.evaluate(f"""
                    window.scrollBy({{
                        left: {x},
                        top: {y},
                        behavior: 'smooth'
                    }});
                """)
                await page.wait_for_timeout(500)  # Wait for smooth scroll
            else:
                await page.evaluate(f"window.scrollBy({x}, {y});")
            
            # Get new scroll position
            scroll_pos = await page.evaluate("({x: window.scrollX, y: window.scrollY})")
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Scrolled {direction} by {amount}px (took {duration:.2f}ms)")
            
            return ActionResult(
                success=True,
                data={"direction": direction, "amount": amount, "position": scroll_pos},
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"Failed to scroll: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                duration_ms=duration
            )


class NavigateAction(IAction):
    """Navigate to a URL"""
    
    def get_name(self) -> str:
        return "navigate"
    
    async def execute(self, page: Page, url: str, wait_until: str = "networkidle",
                      timeout: int = 30000, **kwargs) -> ActionResult:
        """Execute navigate action"""
        import time
        start_time = time.perf_counter()
        
        try:
            # Validate URL
            if not url.startswith(("http://", "https://")):
                url = f"https://{url}"
            
            # Navigate to URL
            response = await page.goto(url, wait_until=wait_until, timeout=timeout, **kwargs)
            
            # Check response status
            status = response.status if response else None
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.info(f"Navigated to {url} (status: {status}, took {duration:.2f}ms)")
            
            return ActionResult(
                success=True,
                data={"url": url, "status": status, "title": await page.title()},
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"Failed to navigate to {url}: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                duration_ms=duration
            )


class PressAction(IAction):
    """Press a key or key combination"""
    
    def get_name(self) -> str:
        return "press"
    
    async def execute(self, page: Page, key: str, selector: str = None,
                      element_id: int = None, element_map: Dict[int, str] = None,
                      **kwargs) -> ActionResult:
        """Execute key press action"""
        import time
        start_time = time.perf_counter()
        
        try:
            # If selector provided, press key on specific element
            if selector or (element_id is not None and element_map):
                if element_id is not None and element_map:
                    selector = element_map.get(element_id)
                    if not selector:
                        return ActionResult(
                            success=False,
                            error=f"Element ID {element_id} not found in element map"
                        )
                
                locator = page.locator(selector)
                await locator.wait_for(state="visible", timeout=10000)
                await locator.press(key, **kwargs)
            else:
                # Press key on page
                await page.keyboard.press(key, **kwargs)
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Pressed key: {key} (took {duration:.2f}ms)")
            
            return ActionResult(
                success=True,
                data={"key": key, "selector": selector},
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"Failed to press key {key}: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                duration_ms=duration
            )


class SelectOptionAction(IAction):
    """Select option from dropdown"""
    
    def get_name(self) -> str:
        return "select_option"
    
    async def execute(self, page: Page, selector: str = None, value: str = None,
                      label: str = None, index: int = None,
                      element_id: int = None, element_map: Dict[int, str] = None,
                      **kwargs) -> ActionResult:
        """Execute select option action"""
        import time
        start_time = time.perf_counter()
        
        try:
            # Determine selector
            if element_id is not None and element_map:
                selector = element_map.get(element_id)
                if not selector:
                    return ActionResult(
                        success=False,
                        error=f"Element ID {element_id} not found in element map"
                    )
            
            if not selector:
                return ActionResult(
                    success=False,
                    error="No selector provided for select action"
                )
            
            # Find select element
            locator = page.locator(selector)
            await locator.wait_for(state="visible", timeout=10000)
            
            # Select option
            if value:
                await locator.select_option(value=value, **kwargs)
                selected = value
            elif label:
                await locator.select_option(label=label, **kwargs)
                selected = label
            elif index is not None:
                await locator.select_option(index=index, **kwargs)
                selected = f"index:{index}"
            else:
                return ActionResult(
                    success=False,
                    error="No selection criteria provided (value, label, or index)"
                )
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Selected option in {selector}: {selected} (took {duration:.2f}ms)")
            
            return ActionResult(
                success=True,
                data={"selector": selector, "selected": selected},
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"Failed to select option in {selector}: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                duration_ms=duration
            )


class CheckAction(IAction):
    """Check or uncheck checkbox/radio button"""
    
    def get_name(self) -> str:
        return "check"
    
    async def execute(self, page: Page, selector: str = None, checked: bool = True,
                      element_id: int = None, element_map: Dict[int, str] = None,
                      **kwargs) -> ActionResult:
        """Execute check/uncheck action"""
        import time
        start_time = time.perf_counter()
        
        try:
            # Determine selector
            if element_id is not None and element_map:
                selector = element_map.get(element_id)
                if not selector:
                    return ActionResult(
                        success=False,
                        error=f"Element ID {element_id} not found in element map"
                    )
            
            if not selector:
                return ActionResult(
                    success=False,
                    error="No selector provided for check action"
                )
            
            # Find checkbox/radio element
            locator = page.locator(selector)
            await locator.wait_for(state="visible", timeout=10000)
            
            # Check or uncheck
            if checked:
                await locator.check(**kwargs)
            else:
                await locator.uncheck(**kwargs)
            
            # Verify state
            is_checked = await locator.is_checked()
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.debug(f"{'Checked' if checked else 'Unchecked'} {selector} (took {duration:.2f}ms)")
            
            return ActionResult(
                success=True,
                data={"selector": selector, "checked": is_checked},
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"Failed to check/uncheck {selector}: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                duration_ms=duration
            )


class GetHTMLAction(IAction):
    """Get HTML content of page or element"""
    
    def get_name(self) -> str:
        return "get_html"
    
    async def execute(self, page: Page, selector: str = None,
                      element_id: int = None, element_map: Dict[int, str] = None,
                      **kwargs) -> ActionResult:
        """Execute get HTML action"""
        import time
        start_time = time.perf_counter()
        
        try:
            # Get HTML of specific element or entire page
            if selector or (element_id is not None and element_map):
                if element_id is not None and element_map:
                    selector = element_map.get(element_id)
                    if not selector:
                        return ActionResult(
                            success=False,
                            error=f"Element ID {element_id} not found in element map"
                        )
                
                locator = page.locator(selector)
                await locator.wait_for(state="visible", timeout=10000)
                html = await locator.inner_html()
            else:
                html = await page.content()
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Retrieved HTML (length: {len(html)}, took {duration:.2f}ms)")
            
            return ActionResult(
                success=True,
                data=html,
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"Failed to get HTML: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                duration_ms=duration
            )


class GetScreenshotAction(IAction):
    """Take screenshot of page or element"""
    
    def get_name(self) -> str:
        return "get_screenshot"
    
    async def execute(self, page: Page, selector: str = None,
                      element_id: int = None, element_map: Dict[int, str] = None,
                      full_page: bool = False, path: str = None,
                      **kwargs) -> ActionResult:
        """Execute screenshot action"""
        import time
        start_time = time.perf_counter()
        
        try:
            # Take screenshot of specific element or entire page
            if selector or (element_id is not None and element_map):
                if element_id is not None and element_map:
                    selector = element_map.get(element_id)
                    if not selector:
                        return ActionResult(
                            success=False,
                            error=f"Element ID {element_id} not found in element map"
                        )
                
                locator = page.locator(selector)
                await locator.wait_for(state="visible", timeout=10000)
                screenshot = await locator.screenshot(path=path, **kwargs)
            else:
                screenshot = await page.screenshot(path=path, full_page=full_page, **kwargs)
            
            # Convert to base64 if not saving to file
            if not path and screenshot:
                screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
            else:
                screenshot_b64 = None
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Took screenshot (took {duration:.2f}ms)")
            
            return ActionResult(
                success=True,
                data={
                    "screenshot": screenshot_b64,
                    "path": path,
                    "size": len(screenshot) if screenshot else 0
                },
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"Failed to take screenshot: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                duration_ms=duration
            )


class WaitAction(IAction):
    """Wait for a condition or timeout"""
    
    def get_name(self) -> str:
        return "wait"
    
    async def execute(self, page: Page, selector: str = None, state: str = "visible",
                      timeout: int = 5000, element_id: int = None,
                      element_map: Dict[int, str] = None, **kwargs) -> ActionResult:
        """Execute wait action"""
        import time
        start_time = time.perf_counter()
        
        try:
            if selector or (element_id is not None and element_map):
                # Wait for element
                if element_id is not None and element_map:
                    selector = element_map.get(element_id)
                    if not selector:
                        return ActionResult(
                            success=False,
                            error=f"Element ID {element_id} not found in element map"
                        )
                
                locator = page.locator(selector)
                await locator.wait_for(state=state, timeout=timeout)
                message = f"Element {selector} reached state: {state}"
            else:
                # Simple timeout wait
                await page.wait_for_timeout(timeout)
                message = f"Waited for {timeout}ms"
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.debug(f"{message} (took {duration:.2f}ms)")
            
            return ActionResult(
                success=True,
                data={"message": message},
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"Wait failed: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                duration_ms=duration
            )


class ScreenshotAction(IAction):
    """Take a screenshot of the page"""
    
    def get_name(self) -> str:
        return "screenshot"
    
    async def execute(self, page: Page, filename: Optional[str] = None,
                      full_page: bool = False, **kwargs) -> ActionResult:
        """Execute screenshot action"""
        import time
        import os
        from datetime import datetime
        
        start_time = time.perf_counter()
        
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            # Ensure screenshots directory exists
            screenshots_dir = "screenshots"
            os.makedirs(screenshots_dir, exist_ok=True)
            
            # Full path for screenshot
            filepath = os.path.join(screenshots_dir, filename)
            
            # Take screenshot
            screenshot_bytes = await page.screenshot(
                path=filepath,
                full_page=full_page,
                **kwargs
            )
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Screenshot saved to {filepath} (took {duration:.2f}ms)")
            
            return ActionResult(
                success=True,
                data=filepath,
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"Failed to take screenshot: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                duration_ms=duration
            )


class ExtractTextAction(IAction):
    """Extract text content from an element"""
    
    def get_name(self) -> str:
        return "extract_text"
    
    async def execute(self, page: Page, selector: str = None,
                      element_id: int = None, element_map: Dict[int, str] = None,
                      **kwargs) -> ActionResult:
        """Execute text extraction"""
        import time
        start_time = time.perf_counter()
        
        try:
            # Determine selector
            if element_id is not None and element_map:
                selector = element_map.get(element_id)
                if not selector:
                    return ActionResult(
                        success=False,
                        error=f"Element ID {element_id} not found in element map"
                    )
            
            if not selector:
                # Extract text from entire page
                text = await page.text_content("body")
            else:
                # Extract text from specific element
                locator = page.locator(selector)
                await locator.wait_for(state="visible", timeout=10000)
                text = await locator.text_content()
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Extracted text from {selector or 'page'} (took {duration:.2f}ms)")
            
            return ActionResult(
                success=True,
                data=text,
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"Failed to extract text: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                duration_ms=duration
            )


class ExtractAttributeAction(IAction):
    """Extract attribute value from an element"""
    
    def get_name(self) -> str:
        return "extract_attribute"
    
    async def execute(self, page: Page, selector: str, attribute: str,
                      element_id: int = None, element_map: Dict[int, str] = None,
                      **kwargs) -> ActionResult:
        """Execute attribute extraction"""
        import time
        start_time = time.perf_counter()
        
        try:
            # Determine selector
            if element_id is not None and element_map:
                selector = element_map.get(element_id)
                if not selector:
                    return ActionResult(
                        success=False,
                        error=f"Element ID {element_id} not found in element map"
                    )
            
            if not selector:
                return ActionResult(
                    success=False,
                    error="No selector provided for attribute extraction"
                )
            
            # Extract attribute
            locator = page.locator(selector)
            await locator.wait_for(state="visible", timeout=10000)
            value = await locator.get_attribute(attribute)
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Extracted {attribute} from {selector} (took {duration:.2f}ms)")
            
            return ActionResult(
                success=True,
                data={attribute: value},
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"Failed to extract attribute: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                duration_ms=duration
            )


class HoverAction(IAction):
    """Hover over an element"""
    
    def get_name(self) -> str:
        return "hover"
    
    async def execute(self, page: Page, selector: str = None,
                      element_id: int = None, element_map: Dict[int, str] = None,
                      **kwargs) -> ActionResult:
        """Execute hover action"""
        import time
        start_time = time.perf_counter()
        
        try:
            # Determine selector
            if element_id is not None and element_map:
                selector = element_map.get(element_id)
                if not selector:
                    return ActionResult(
                        success=False,
                        error=f"Element ID {element_id} not found in element map"
                    )
            
            if not selector:
                return ActionResult(
                    success=False,
                    error="No selector provided for hover action"
                )
            
            # Hover over element
            locator = page.locator(selector)
            await locator.wait_for(state="visible", timeout=10000)
            await locator.hover(**kwargs)
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Hovered over {selector} (took {duration:.2f}ms)")
            
            return ActionResult(
                success=True,
                data={"selector": selector},
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"Failed to hover: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                duration_ms=duration
            )


class SelectAction(IAction):
    """Select option from dropdown"""
    
    def get_name(self) -> str:
        return "select"
    
    async def execute(self, page: Page, selector: str, value: str = None,
                      element_id: int = None, element_map: Dict[int, str] = None,
                      **kwargs) -> ActionResult:
        """Execute select action"""
        import time
        start_time = time.perf_counter()
        
        try:
            # Determine selector
            if element_id is not None and element_map:
                selector = element_map.get(element_id)
                if not selector:
                    return ActionResult(
                        success=False,
                        error=f"Element ID {element_id} not found in element map"
                    )
            
            if not selector:
                return ActionResult(
                    success=False,
                    error="No selector provided for select action"
                )
            
            # Select option
            locator = page.locator(selector)
            await locator.wait_for(state="visible", timeout=10000)
            
            if value:
                await locator.select_option(value=value, **kwargs)
            else:
                return ActionResult(
                    success=False,
                    error="No value provided for select action"
                )
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Selected {value} from {selector} (took {duration:.2f}ms)")
            
            return ActionResult(
                success=True,
                data={"selector": selector, "value": value},
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"Failed to select option: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                duration_ms=duration
            )


class KeyPressAction(IAction):
    """Press keyboard keys"""
    
    def get_name(self) -> str:
        return "key_press"
    
    async def execute(self, page: Page, key: str, **kwargs) -> ActionResult:
        """Execute key press action"""
        import time
        start_time = time.perf_counter()
        
        try:
            # Press the key
            await page.keyboard.press(key, **kwargs)
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Pressed key: {key} (took {duration:.2f}ms)")
            
            return ActionResult(
                success=True,
                data={"key": key},
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"Failed to press key {key}: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                duration_ms=duration
            )


class EvaluateAction(IAction):
    """Evaluate JavaScript in the page context"""
    
    def get_name(self) -> str:
        return "evaluate"
    
    async def execute(self, page: Page, script: str, **kwargs) -> ActionResult:
        """Execute JavaScript evaluation"""
        import time
        start_time = time.perf_counter()
        
        try:
            # Evaluate script
            result = await page.evaluate(script, **kwargs)
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Evaluated JavaScript (took {duration:.2f}ms)")
            
            return ActionResult(
                success=True,
                data=result,
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"Failed to evaluate script: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                duration_ms=duration
            )


class FileUploadAction(IAction):
    """Upload files to file input"""
    
    def get_name(self) -> str:
        return "file_upload"
    
    async def execute(self, page: Page, selector: str, files: List[str],
                      element_id: int = None, element_map: Dict[int, str] = None,
                      **kwargs) -> ActionResult:
        """Execute file upload action"""
        import time
        import os
        start_time = time.perf_counter()
        
        try:
            # Determine selector
            if element_id is not None and element_map:
                selector = element_map.get(element_id)
                if not selector:
                    return ActionResult(
                        success=False,
                        error=f"Element ID {element_id} not found in element map"
                    )
            
            if not selector:
                return ActionResult(
                    success=False,
                    error="No selector provided for file upload"
                )
            
            # Validate files exist
            for filepath in files:
                if not os.path.exists(filepath):
                    return ActionResult(
                        success=False,
                        error=f"File not found: {filepath}"
                    )
            
            # Upload files
            locator = page.locator(selector)
            await locator.set_input_files(files, **kwargs)
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Uploaded {len(files)} file(s) (took {duration:.2f}ms)")
            
            return ActionResult(
                success=True,
                data={"files": files, "count": len(files)},
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"Failed to upload files: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                duration_ms=duration
            )