"""Action dispatcher to map structured actions to browser execution"""

from typing import Dict, Any, Optional
from playwright.async_api import Page
from loguru import logger
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from cognition.actions import (
    AgentAction, ClickAction, TypeAction, FillAction, ScrollAction,
    NavigateAction, SelectAction, WaitAction, ReadTextAction,
    PressKeyAction, HoverAction, DragAction, ScreenshotAction,
    FinishedAction, FailedAction
)
from execution.actions import (
    ActionResult, ClickAction as BrowserClickAction,
    TypeAction as BrowserTypeAction, FillAction as BrowserFillAction,
    ScrollAction as BrowserScrollAction, NavigateAction as BrowserNavigateAction,
    SelectOptionAction, PressAction, WaitAction as BrowserWaitAction,
    GetHTMLAction, GetScreenshotAction
)


class ActionDispatcher:
    """Dispatches structured agent actions to browser execution layer"""
    
    def __init__(self):
        # Initialize browser action executors
        self.browser_actions = {
            'click': BrowserClickAction(),
            'type': BrowserTypeAction(),
            'fill': BrowserFillAction(),
            'scroll': BrowserScrollAction(),
            'navigate': BrowserNavigateAction(),
            'select': SelectOptionAction(),
            'press': PressAction(),
            'wait': BrowserWaitAction(),
            'get_html': GetHTMLAction(),
            'screenshot': GetScreenshotAction()
        }
        
        # Track execution statistics
        self.stats = {
            'total_actions': 0,
            'successful_actions': 0,
            'failed_actions': 0,
            'action_types': {}
        }
    
    async def dispatch(self, action: AgentAction, page: Page,
                      element_map: Dict[int, str]) -> ActionResult:
        """
        Dispatch a structured action to browser execution
        
        Args:
            action: Structured agent action
            page: Playwright page
            element_map: Mapping from element IDs to CSS selectors
            
        Returns:
            ActionResult from execution
        """
        self.stats['total_actions'] += 1
        action_type = action.action
        
        # Track action type
        if action_type not in self.stats['action_types']:
            self.stats['action_types'][action_type] = 0
        self.stats['action_types'][action_type] += 1
        
        try:
            # Route to appropriate handler
            if isinstance(action, ClickAction):
                result = await self._dispatch_click(action, page, element_map)
            elif isinstance(action, TypeAction):
                result = await self._dispatch_type(action, page, element_map)
            elif isinstance(action, FillAction):
                result = await self._dispatch_fill(action, page, element_map)
            elif isinstance(action, ScrollAction):
                result = await self._dispatch_scroll(action, page, element_map)
            elif isinstance(action, NavigateAction):
                result = await self._dispatch_navigate(action, page)
            elif isinstance(action, SelectAction):
                result = await self._dispatch_select(action, page, element_map)
            elif isinstance(action, WaitAction):
                result = await self._dispatch_wait(action, page, element_map)
            elif isinstance(action, ReadTextAction):
                result = await self._dispatch_read_text(action, page, element_map)
            elif isinstance(action, PressKeyAction):
                result = await self._dispatch_press_key(action, page, element_map)
            elif isinstance(action, HoverAction):
                result = await self._dispatch_hover(action, page, element_map)
            elif isinstance(action, DragAction):
                result = await self._dispatch_drag(action, page, element_map)
            elif isinstance(action, ScreenshotAction):
                result = await self._dispatch_screenshot(action, page, element_map)
            elif isinstance(action, FinishedAction):
                result = await self._dispatch_finished(action)
            elif isinstance(action, FailedAction):
                result = await self._dispatch_failed(action)
            else:
                result = ActionResult(
                    success=False,
                    error=f"Unknown action type: {action_type}"
                )
            
            # Update statistics
            if result.success:
                self.stats['successful_actions'] += 1
            else:
                self.stats['failed_actions'] += 1
            
            # Log result
            logger.debug(f"Action {action_type} {'succeeded' if result.success else 'failed'}")
            
            return result
            
        except Exception as e:
            logger.error(f"Unexpected error dispatching {action_type}: {e}")
            self.stats['failed_actions'] += 1
            return ActionResult(
                success=False,
                error=str(e)
            )
    
    async def _dispatch_click(self, action: ClickAction, page: Page,
                            element_map: Dict[int, str]) -> ActionResult:
        """Dispatch click action"""
        selector = element_map.get(action.element_id)
        if not selector:
            return ActionResult(
                success=False,
                error=f"Element ID {action.element_id} not found in element map"
            )
        
        # Validate element before attempting to click
        validation_result = await self._validate_element_before_action(page, selector, "click")
        if not validation_result.success:
            return validation_result
        
        # Prepare click options
        options = {}
        if action.click_type == "double":
            options["click_count"] = 2
        elif action.click_type == "right":
            options["button"] = "right"
        elif action.click_type == "middle":
            options["button"] = "middle"
        
        if action.modifiers:
            options["modifiers"] = action.modifiers
        
        return await self.browser_actions['click'].execute(
            page, selector=selector, **options
        )
    
    async def _dispatch_type(self, action: TypeAction, page: Page,
                            element_map: Dict[int, str]) -> ActionResult:
        """Dispatch type action"""
        selector = element_map.get(action.element_id)
        if not selector:
            return ActionResult(
                success=False,
                error=f"Element ID {action.element_id} not found in element map"
            )
        
        # Validate element before attempting to type
        validation_result = await self._validate_element_before_action(page, selector, "type")
        if not validation_result.success:
            return validation_result
        
        # Clear field if requested
        if action.clear_first:
            clear_result = await page.locator(selector).clear()
        
        return await self.browser_actions['type'].execute(
            page, 
            selector=selector,
            text=action.text_to_type,
            delay=action.delay_ms
        )
    
    async def _dispatch_fill(self, action: FillAction, page: Page,
                            element_map: Dict[int, str]) -> ActionResult:
        """Dispatch fill action"""
        selector = element_map.get(action.element_id)
        if not selector:
            return ActionResult(
                success=False,
                error=f"Element ID {action.element_id} not found in element map"
            )
        
        # Validate element before attempting to fill
        validation_result = await self._validate_element_before_action(page, selector, "fill")
        if not validation_result.success:
            return validation_result
        
        return await self.browser_actions['fill'].execute(
            page,
            selector=selector,
            text=action.text,
            clear_first=action.clear_first
        )
    
    async def _dispatch_scroll(self, action: ScrollAction, page: Page,
                              element_map: Dict[int, str]) -> ActionResult:
        """Dispatch scroll action"""
        # If element_id provided, scroll to element
        if action.element_id:
            selector = element_map.get(action.element_id)
            if selector:
                try:
                    await page.locator(selector).scroll_into_view_if_needed()
                    return ActionResult(success=True)
                except Exception as e:
                    return ActionResult(success=False, error=str(e))
        
        # Otherwise, do page scroll
        return await self.browser_actions['scroll'].execute(
            page,
            direction=action.direction,
            amount=action.amount,
            smooth=action.smooth
        )
    
    async def _dispatch_navigate(self, action: NavigateAction, page: Page) -> ActionResult:
        """Dispatch navigate action"""
        return await self.browser_actions['navigate'].execute(
            page,
            url=action.url,
            wait_until=action.wait_until
        )
    
    async def _dispatch_select(self, action: SelectAction, page: Page,
                              element_map: Dict[int, str]) -> ActionResult:
        """Dispatch select action"""
        selector = element_map.get(action.element_id)
        if not selector:
            return ActionResult(
                success=False,
                error=f"Element ID {action.element_id} not found in element map"
            )
        
        # Determine selection method
        if action.option_text:
            return await self.browser_actions['select'].execute(
                page, selector=selector, label=action.option_text
            )
        elif action.option_value:
            return await self.browser_actions['select'].execute(
                page, selector=selector, value=action.option_value
            )
        elif action.option_index is not None:
            return await self.browser_actions['select'].execute(
                page, selector=selector, index=action.option_index
            )
        else:
            return ActionResult(
                success=False,
                error="No selection criteria provided"
            )
    
    async def _dispatch_wait(self, action: WaitAction, page: Page,
                            element_map: Dict[int, str]) -> ActionResult:
        """Dispatch wait action"""
        if action.wait_type == "time":
            return await self.browser_actions['wait'].execute(
                page, timeout=action.duration_ms or 1000
            )
        elif action.wait_type == "element" and action.element_id:
            selector = element_map.get(action.element_id)
            if not selector:
                return ActionResult(
                    success=False,
                    error=f"Element ID {action.element_id} not found"
                )
            
            return await self.browser_actions['wait'].execute(
                page,
                selector=selector,
                state=action.element_state or "visible",
                timeout=action.duration_ms or 5000
            )
        elif action.wait_type == "condition" and action.condition:
            try:
                await page.wait_for_function(
                    action.condition,
                    timeout=action.duration_ms or 5000
                )
                return ActionResult(success=True)
            except Exception as e:
                return ActionResult(success=False, error=str(e))
        else:
            return ActionResult(
                success=False,
                error="Invalid wait configuration"
            )
    
    async def _dispatch_read_text(self, action: ReadTextAction, page: Page,
                                 element_map: Dict[int, str]) -> ActionResult:
        """Dispatch read text action"""
        selector = element_map.get(action.element_id)
        if not selector:
            return ActionResult(
                success=False,
                error=f"Element ID {action.element_id} not found"
            )
        
        try:
            text = await page.locator(selector).text_content()
            return ActionResult(
                success=True,
                data={"text": text, "purpose": action.purpose}
            )
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    async def _dispatch_press_key(self, action: PressKeyAction, page: Page,
                                 element_map: Dict[int, str]) -> ActionResult:
        """Dispatch key press action"""
        selector = None
        if action.element_id:
            selector = element_map.get(action.element_id)
            if not selector:
                return ActionResult(
                    success=False,
                    error=f"Element ID {action.element_id} not found"
                )
        
        return await self.browser_actions['press'].execute(
            page,
            key=action.key,
            selector=selector
        )
    
    async def _dispatch_hover(self, action: HoverAction, page: Page,
                             element_map: Dict[int, str]) -> ActionResult:
        """Dispatch hover action"""
        selector = element_map.get(action.element_id)
        if not selector:
            return ActionResult(
                success=False,
                error=f"Element ID {action.element_id} not found"
            )
        
        try:
            await page.locator(selector).hover()
            if action.duration_ms > 0:
                await page.wait_for_timeout(action.duration_ms)
            return ActionResult(success=True)
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    async def _dispatch_drag(self, action: DragAction, page: Page,
                           element_map: Dict[int, str]) -> ActionResult:
        """Dispatch drag action"""
        source_selector = element_map.get(action.source_element_id)
        if not source_selector:
            return ActionResult(
                success=False,
                error=f"Source element ID {action.source_element_id} not found"
            )
        
        try:
            source = page.locator(source_selector)
            
            if action.target_element_id:
                target_selector = element_map.get(action.target_element_id)
                if not target_selector:
                    return ActionResult(
                        success=False,
                        error=f"Target element ID {action.target_element_id} not found"
                    )
                
                await source.drag_to(page.locator(target_selector))
            else:
                # Drag by offset
                await source.drag_to(
                    source,
                    source_position={"x": 0, "y": 0},
                    target_position={"x": action.offset_x or 0, "y": action.offset_y or 0}
                )
            
            return ActionResult(success=True)
        except Exception as e:
            return ActionResult(success=False, error=str(e))
    
    async def _dispatch_screenshot(self, action: ScreenshotAction, page: Page,
                                  element_map: Dict[int, str]) -> ActionResult:
        """Dispatch screenshot action"""
        selector = None
        if action.element_id:
            selector = element_map.get(action.element_id)
            if not selector:
                return ActionResult(
                    success=False,
                    error=f"Element ID {action.element_id} not found"
                )
        
        return await self.browser_actions['screenshot'].execute(
            page,
            selector=selector,
            full_page=action.full_page
        )
    
    async def _dispatch_finished(self, action: FinishedAction) -> ActionResult:
        """Handle finished action"""
        return ActionResult(
            success=True,
            data={
                "status": "finished",
                "summary": action.summary,
                "extracted_data": action.extracted_data,
                "next_steps": action.next_steps
            }
        )
    
    async def _dispatch_failed(self, action: FailedAction) -> ActionResult:
        """Handle failed action"""
        return ActionResult(
            success=False,
            error=action.reason,
            data={
                "status": "failed",
                "error_type": action.error_type,
                "attempted_actions": action.attempted_actions,
                "suggestions": action.suggestions
            }
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return {
            **self.stats,
            "success_rate": (
                self.stats['successful_actions'] / self.stats['total_actions']
                if self.stats['total_actions'] > 0 else 0
            )
        }
    
    def reset_stats(self) -> None:
        """Reset execution statistics"""
        self.stats = {
            'total_actions': 0,
            'successful_actions': 0,
            'failed_actions': 0,
            'action_types': {}
        }
    
    async def _validate_element_before_action(self, page: Page, selector: str, action_type: str) -> ActionResult:
        """
        Validate element visibility and interactability before executing action
        
        Args:
            page: Playwright page instance
            selector: CSS selector of the element
            action_type: Type of action being performed
            
        Returns:
            ActionResult indicating validation success/failure
        """
        try:
            # Check if element exists
            element_count = await page.locator(selector).count()
            if element_count == 0:
                return ActionResult(
                    success=False,
                    error=f"Element not found: {selector}"
                )
            
            # Wait briefly for element to stabilize (especially for dynamic content)
            await page.wait_for_timeout(100)
            
            # Validate element properties using JavaScript
            validation_script = f"""
            (() => {{
                const element = document.querySelector('{selector}');
                if (!element) {{
                    return {{ valid: false, reason: 'Element not found' }};
                }}
                
                // Check for hidden input types
                if (element.type === 'hidden') {{
                    return {{ valid: false, reason: 'Element is hidden input type' }};
                }}
                
                // Check for Amazon carousel elements
                if (element.classList.contains('a-carousel-firstvisibleitem') || 
                    element.classList.contains('a-carousel-lastvisibleitem')) {{
                    return {{ valid: false, reason: 'Element is Amazon carousel component (hidden)' }};
                }}
                
                // Check computed styles
                const style = window.getComputedStyle(element);
                if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {{
                    return {{ valid: false, reason: 'Element is not visible (CSS)' }};
                }}
                
                // Check element size
                const rect = element.getBoundingClientRect();
                if (rect.width === 0 || rect.height === 0) {{
                    return {{ valid: false, reason: 'Element has zero dimensions' }};
                }}
                
                // Check if element is within viewport
                const viewport = {{
                    width: window.innerWidth || document.documentElement.clientWidth,
                    height: window.innerHeight || document.documentElement.clientHeight
                }};
                
                if (rect.bottom < 0 || rect.right < 0 || 
                    rect.top > viewport.height || rect.left > viewport.width) {{
                    return {{ valid: false, reason: 'Element is outside viewport' }};
                }}
                
                // For fill/type actions, ensure element is interactable
                if (['fill', 'type'].includes('{action_type}')) {{
                    if (element.disabled || element.readOnly) {{
                        return {{ valid: false, reason: 'Element is disabled or readonly' }};
                    }}
                    
                    // Enhanced interactability check for Google Scholar and other sites
                    const interactableTypes = ['input', 'textarea', 'select'];
                    const isInput = interactableTypes.includes(element.tagName.toLowerCase());
                    const isContentEditable = element.contentEditable === 'true';
                    
                    // Special case for Google Scholar search boxes
                    const isScholarSearch = element.id === 'gs_hdr_tsb' || 
                                          element.name === 'q' ||
                                          element.classList.contains('gs_in_txt');
                    
                    if (!isInput && !isContentEditable && !isScholarSearch) {{
                        // Additional check - see if element can receive focus
                        try {{
                            element.focus();
                            const canFocus = document.activeElement === element;
                            if (!canFocus) {{
                                return {{ valid: false, reason: 'Element is not interactable for text input' }};
                            }}
                        }} catch (e) {{
                            return {{ valid: false, reason: 'Element cannot receive focus' }};
                        }}
                    }}
                }}
                
                // For click actions, check if element is clickable
                if (action_type === 'click') {{
                    // Check if element or parent has click handlers
                    const hasClickHandler = element.onclick !== null ||
                                          element.addEventListener !== undefined ||
                                          element.tagName.toLowerCase() === 'a' ||
                                          element.tagName.toLowerCase() === 'button' ||
                                          element.role === 'button' ||
                                          style.cursor === 'pointer';
                    
                    if (!hasClickHandler) {{
                        // Check if any parent has click handling
                        let parent = element.parentElement;
                        let foundClickable = false;
                        while (parent && parent !== document.body) {{
                            const parentStyle = window.getComputedStyle(parent);
                            if (parent.onclick || parentStyle.cursor === 'pointer' ||
                                parent.tagName.toLowerCase() === 'a') {{
                                foundClickable = true;
                                break;
                            }}
                            parent = parent.parentElement;
                        }}
                        
                        if (!foundClickable) {{
                            logger.debug('Element may not be clickable but allowing click attempt');
                        }}
                    }}
                }}
                
                return {{ 
                    valid: true, 
                    elementInfo: {{
                        tagName: element.tagName,
                        type: element.type,
                        id: element.id,
                        className: element.className,
                        rect: {{ width: rect.width, height: rect.height }},
                        isVisible: true,
                        isInViewport: rect.top >= 0 && rect.left >= 0 && 
                                    rect.bottom <= viewport.height && rect.right <= viewport.width
                    }}
                }};
            }})()
            """
            
            result = await page.evaluate(validation_script)
            
            if not result.get('valid', False):
                reason = result.get('reason', 'Unknown validation failure')
                logger.warning(f"Element validation failed for {selector}: {reason}")
                
                # For Amazon searches, suggest alternative
                if 'carousel' in reason.lower() and action_type == 'fill':
                    return ActionResult(
                        success=False,
                        error=f"Cannot fill carousel element '{selector}'. "
                               f"Use Amazon's main search box with id='twotabsearchtextbox' instead. "
                               f"Reason: {reason}"
                    )
                
                # For Google Scholar, provide more specific guidance
                if 'gs_hdr_tsb' in selector or 'scholar' in page.url:
                    if 'not interactable' in reason.lower() or 'cannot receive focus' in reason.lower():
                        return ActionResult(
                            success=False,
                            error=f"Google Scholar search box validation failed. "
                                   f"This may indicate bot detection or page loading issues. "
                                   f"Consider refreshing the page or using alternative selectors. "
                                   f"Reason: {reason}"
                        )
                
                return ActionResult(
                    success=False,
                    error=f"Element validation failed: {reason}"
                )
            
            # Log successful validation
            element_info = result.get('elementInfo', {})
            logger.debug(f"Element validation passed for {selector}: {element_info}")
            
            return ActionResult(success=True)
            
        except Exception as e:
            logger.error(f"Element validation error for {selector}: {e}")
            return ActionResult(
                success=False,
                error=f"Validation error: {str(e)}"
            )