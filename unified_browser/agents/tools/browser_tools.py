"""
Browser tools for pydantic-ai agents.

This module provides tools that allow pydantic-ai agents to interact with
web browsers through a structured, type-safe interface.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel

# Import will be available when pydantic-ai is installed
try:
    from pydantic_ai import RunContext
    from pydantic_ai.tools import Tool
    PYDANTIC_AI_AVAILABLE = True
except ImportError:
    # Fallback for development without pydantic-ai
    PYDANTIC_AI_AVAILABLE = False
    
    # Mock classes for development
    class RunContext:
        def __init__(self, deps):
            self.deps = deps
    
    def Tool(func):
        return func

from ...browser.browser_context import BrowserContext, PageInfo, ElementInfo
from ...browser.dom_extractor import DOMElement
from ...core import NavigationResult
from ...core.security import get_input_validator, get_rate_limiter, validate_and_sanitize_input


class NavigationCommand(BaseModel):
    """Command for navigation operations."""
    url: str
    wait_for: Optional[str] = None
    timeout: Optional[int] = None


class ElementSelector(BaseModel):
    """Element selection criteria."""
    selector: str
    description: Optional[str] = None
    wait_timeout: Optional[int] = 5000


class TextInput(BaseModel):
    """Text input command."""
    selector: str
    text: str
    clear_first: bool = True


class ClickTarget(BaseModel):
    """Click target specification."""
    selector: str
    button: str = "left"  # left, right, middle
    modifiers: List[str] = []  # shift, ctrl, alt, meta


class ElementIndexCommand(BaseModel):
    """Command for interacting with elements by their AI-friendly index."""
    index: int
    action: str  # 'click', 'type', 'info'
    text: Optional[str] = None  # For type action
    description: Optional[str] = None


class ElementSearchCommand(BaseModel):
    """Command for finding elements by text content."""
    search_text: str
    exact_match: bool = False
    max_results: int = 10


class ScreenshotCommand(BaseModel):
    """Enhanced screenshot command."""
    annotated: bool = False  # Whether to show element indices
    file_path: Optional[str] = None


# ============================================================================
# NAVIGATION TOOLS
# ============================================================================

@Tool
async def navigate_to_page(ctx: RunContext[BrowserContext], command: NavigationCommand) -> Dict[str, Any]:
    """
    Navigate to a web page with security validation and rate limiting.
    
    Args:
        command: Navigation command with URL and options
        
    Returns:
        Navigation result with success status, timing, and page info
    """
    browser_ctx = ctx.deps
    
    # Security validation
    is_valid, sanitized_url, error = validate_and_sanitize_input('url', command.url)
    if not is_valid:
        return {
            "success": False,
            "error": f"Invalid URL: {error}",
            "final_url": "",
            "title": "",
            "load_time": 0
        }
    
    # Rate limiting
    rate_limiter = get_rate_limiter()
    if not rate_limiter.check_rate_limit("navigation", 30, 60):  # 30 navigations per minute
        return {
            "success": False,
            "error": "Rate limit exceeded for navigation",
            "final_url": "",
            "title": "",
            "load_time": 0
        }
    
    result = await browser_ctx.navigate_to(
        sanitized_url,
        timeout=command.timeout
    )
    
    return {
        "success": result.success,
        "final_url": result.final_url,
        "title": result.title,
        "load_time": result.load_time,
        "error": result.error
    }


@Tool
async def get_current_page_info(ctx: RunContext[BrowserContext], include_screenshot: bool = False) -> Dict[str, Any]:
    """
    Get information about the current page.
    
    Args:
        include_screenshot: Whether to include a base64 screenshot
        
    Returns:
        Current page information including URL, title, and optionally screenshot
    """
    browser_ctx = ctx.deps
    page_info = await browser_ctx.get_page_info(include_screenshot=include_screenshot)
    
    return {
        "url": page_info.url,
        "title": page_info.title,
        "html_length": page_info.html_length,
        "viewport": page_info.viewport,
        "load_state": page_info.load_state,
        "screenshot_b64": page_info.screenshot_b64 if include_screenshot else None
    }


@Tool
async def get_page_text(ctx: RunContext[BrowserContext], max_length: int = 3000) -> str:
    """
    Get the visible text content of the current page.
    
    Args:
        max_length: Maximum length of text to return
        
    Returns:
        Visible text content of the page
    """
    browser_ctx = ctx.deps
    return await browser_ctx.get_visible_text(max_length=max_length)


# ============================================================================
# ELEMENT INTERACTION TOOLS
# ============================================================================

@Tool
async def find_element_info(ctx: RunContext[BrowserContext], selector: ElementSelector) -> Optional[Dict[str, Any]]:
    """
    Find an element and get its information.
    
    Args:
        selector: Element selector with CSS selector string
        
    Returns:
        Element information if found, None otherwise
    """
    browser_ctx = ctx.deps
    element_info = await browser_ctx.find_element(selector.selector)
    
    if not element_info:
        return None
        
    return {
        "selector": element_info.selector,
        "tag_name": element_info.tag_name,
        "text": element_info.text,
        "attributes": element_info.attributes,
        "is_visible": element_info.is_visible,
        "is_enabled": element_info.is_enabled,
        "bounding_box": {
            "x": element_info.bounding_box.x,
            "y": element_info.bounding_box.y,
            "width": element_info.bounding_box.width,
            "height": element_info.bounding_box.height
        } if element_info.bounding_box else None
    }


@Tool
async def click_element(ctx: RunContext[BrowserContext], target: ClickTarget) -> bool:
    """
    Click on an element.
    
    Args:
        target: Click target with selector and options
        
    Returns:
        True if click was successful, False otherwise
    """
    browser_ctx = ctx.deps
    return await browser_ctx.click_element(target.selector)


@Tool
async def type_text(ctx: RunContext[BrowserContext], input_cmd: TextInput) -> bool:
    """
    Type text into an element.
    
    Args:
        input_cmd: Text input command with selector and text
        
    Returns:
        True if typing was successful, False otherwise
    """
    browser_ctx = ctx.deps
    return await browser_ctx.type_text(
        input_cmd.selector,
        input_cmd.text,
        clear=input_cmd.clear_first
    )


# ============================================================================
# ANALYSIS TOOLS
# ============================================================================

@Tool
async def take_screenshot(ctx: RunContext[BrowserContext], file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Take a screenshot of the current page.
    
    Args:
        file_path: Optional path to save screenshot file
        
    Returns:
        Screenshot information with base64 data
    """
    browser_ctx = ctx.deps
    screenshot_bytes = await browser_ctx.take_screenshot(file_path)
    
    import base64
    return {
        "success": len(screenshot_bytes) > 0,
        "size_bytes": len(screenshot_bytes),
        "base64_data": base64.b64encode(screenshot_bytes).decode() if screenshot_bytes else None,
        "file_path": file_path
    }


@Tool
async def execute_javascript(ctx: RunContext[BrowserContext], script: str) -> Any:
    """
    Execute JavaScript in the page context.
    
    Args:
        script: JavaScript code to execute
        
    Returns:
        Result of JavaScript execution
    """
    browser_ctx = ctx.deps
    return await browser_ctx.execute_script(script)


@Tool
async def wait_for_condition(ctx: RunContext[BrowserContext], condition: str, timeout_ms: int = 10000) -> bool:
    """
    Wait for a JavaScript condition to become true.
    
    Args:
        condition: JavaScript condition to wait for
        timeout_ms: Timeout in milliseconds
        
    Returns:
        True if condition became true, False if timeout
    """
    browser_ctx = ctx.deps
    return await browser_ctx.wait_for_condition(condition, timeout=timeout_ms)


# ============================================================================
# ADVANCED TOOLS
# ============================================================================

@Tool
async def extract_links(ctx: RunContext[BrowserContext]) -> List[Dict[str, str]]:
    """
    Extract all links from the current page.
    
    Returns:
        List of links with href, text, and title
    """
    browser_ctx = ctx.deps
    
    links = await browser_ctx.execute_script("""
        () => {
            const links = Array.from(document.querySelectorAll('a[href]'));
            return links.map(link => ({
                href: link.href,
                text: link.textContent.trim(),
                title: link.title || ''
            })).filter(link => link.text.length > 0);
        }
    """)
    
    return links if isinstance(links, list) else []


@Tool
async def extract_form_fields(ctx: RunContext[BrowserContext], form_selector: str = "form") -> List[Dict[str, Any]]:
    """
    Extract form fields from a form.
    
    Args:
        form_selector: CSS selector for the form
        
    Returns:
        List of form fields with their properties
    """
    browser_ctx = ctx.deps
    
    fields = await browser_ctx.execute_script(f"""
        () => {{
            const form = document.querySelector('{form_selector}');
            if (!form) return [];
            
            const inputs = Array.from(form.querySelectorAll('input, select, textarea'));
            return inputs.map(input => {{
                return {{
                    tag: input.tagName.toLowerCase(),
                    type: input.type || 'text',
                    name: input.name || '',
                    id: input.id || '',
                    placeholder: input.placeholder || '',
                    value: input.value || '',
                    required: input.required || false,
                    disabled: input.disabled || false
                }};
            }});
        }}
    """)
    
    return fields if isinstance(fields, list) else []


@Tool
async def get_action_history(ctx: RunContext[BrowserContext], limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get recent browser action history.
    
    Args:
        limit: Maximum number of actions to return
        
    Returns:
        List of recent actions taken by the browser
    """
    browser_ctx = ctx.deps
    return browser_ctx.get_action_history(limit=limit)


# ============================================================================
# AI-FRIENDLY ELEMENT INTERACTION TOOLS (Browser-use Inspired)
# ============================================================================

@Tool
async def get_page_summary_for_ai(ctx: RunContext[BrowserContext]) -> str:
    """
    Get AI-friendly summary of current page with numbered interactive elements.
    
    This tool provides a comprehensive overview of the page that helps AI agents
    understand what actions they can take. Elements are numbered for easy reference.
    
    Returns:
        Formatted string with page info and numbered interactive elements
    """
    browser_ctx = ctx.deps
    return await browser_ctx.get_page_summary_for_ai()


@Tool
async def interact_with_element_by_index(ctx: RunContext[BrowserContext], command: ElementIndexCommand) -> Dict[str, Any]:
    """
    Interact with an element using its numbered index from the page summary.
    
    This is the key AI-friendly interaction tool. Instead of complex selectors,
    agents can simply say "click element [5]" or "type 'hello' in element [3]".
    
    Args:
        command: Element interaction command with index and action
        
    Returns:
        Result of the interaction with success status
    """
    browser_ctx = ctx.deps
    
    if command.action == "click":
        success = await browser_ctx.click_element_by_index(command.index)
        return {
            "success": success,
            "action": "click",
            "index": command.index,
            "message": f"{'Successfully clicked' if success else 'Failed to click'} element [{command.index}]"
        }
    
    elif command.action == "type" and command.text:
        # Validate text input
        is_valid, sanitized_text, error = validate_and_sanitize_input('text', command.text)
        if not is_valid:
            return {
                "success": False,
                "action": "type",
                "index": command.index,
                "error": f"Invalid text input: {error}"
            }
        
        success = await browser_ctx.type_in_element_by_index(command.index, sanitized_text)
        return {
            "success": success,
            "action": "type",
            "index": command.index,
            "text": sanitized_text[:50] + "..." if len(sanitized_text) > 50 else sanitized_text,
            "message": f"{'Successfully typed' if success else 'Failed to type'} in element [{command.index}]"
        }
    
    elif command.action == "info":
        element_info = await browser_ctx.get_element_info_by_index(command.index)
        if element_info:
            return {
                "success": True,
                "action": "info",
                "index": command.index,
                "element": {
                    "tag": element_info.tag_name,
                    "text": element_info.text,
                    "aria_label": element_info.aria_label,
                    "is_clickable": element_info.is_clickable,
                    "is_input": element_info.is_input,
                    "attributes": element_info.attributes
                }
            }
        else:
            return {
                "success": False,
                "action": "info",
                "index": command.index,
                "error": f"Element [{command.index}] not found"
            }
    
    else:
        return {
            "success": False,
            "error": f"Unknown action '{command.action}' or missing text for type action"
        }


@Tool
async def find_elements_by_text_content(ctx: RunContext[BrowserContext], search: ElementSearchCommand) -> Dict[str, Any]:
    """
    Find interactive elements by their text content.
    
    This helps AI agents locate elements when they know what text to look for
    but don't have the exact index.
    
    Args:
        search: Search command with text and options
        
    Returns:
        List of matching element indices and their information
    """
    browser_ctx = ctx.deps
    
    matching_indices = await browser_ctx.find_elements_by_text(
        search.search_text, 
        exact=search.exact_match
    )
    
    results = []
    for index in matching_indices[:search.max_results]:
        element_info = await browser_ctx.get_element_info_by_index(index)
        if element_info:
            results.append({
                "index": index,
                "text": element_info.text,
                "tag": element_info.tag_name,
                "is_clickable": element_info.is_clickable,
                "is_input": element_info.is_input
            })
    
    return {
        "success": True,
        "search_text": search.search_text,
        "exact_match": search.exact_match,
        "found_count": len(results),
        "elements": results
    }


@Tool
async def take_annotated_screenshot(ctx: RunContext[BrowserContext], command: ScreenshotCommand) -> Dict[str, Any]:
    """
    Take a screenshot with optional element numbering annotations.
    
    When annotated=True, this creates a visual reference showing numbered
    elements that correspond to the page summary indices.
    
    Args:
        command: Screenshot command with options
        
    Returns:
        Screenshot information with file path
    """
    browser_ctx = ctx.deps
    
    if command.annotated:
        # Take screenshot with numbered element overlays
        screenshot_path = await browser_ctx.take_annotated_screenshot(command.file_path)
        return {
            "success": True,
            "annotated": True,
            "file_path": screenshot_path,
            "message": "Annotated screenshot taken with numbered elements"
        }
    else:
        # Regular screenshot
        screenshot_bytes = await browser_ctx.take_screenshot(command.file_path)
        return {
            "success": len(screenshot_bytes) > 0,
            "annotated": False,
            "file_path": command.file_path,
            "size_bytes": len(screenshot_bytes)
        }


@Tool
async def wait_for_page_elements_to_change(ctx: RunContext[BrowserContext], timeout_ms: int = 5000) -> bool:
    """
    Wait for interactive elements on the page to change.
    
    This is useful after performing actions that might cause page updates,
    dynamic content loading, or navigation changes.
    
    Args:
        timeout_ms: Maximum time to wait in milliseconds
        
    Returns:
        True if elements changed, False if timeout
    """
    browser_ctx = ctx.deps
    return await browser_ctx.wait_for_page_change(timeout_ms)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_all_browser_tools() -> List[Any]:
    """
    Get all browser tools for agent registration.
    
    Returns:
        List of all available browser tools
    """
    if not PYDANTIC_AI_AVAILABLE:
        return []
        
    return [
        # Core navigation and page tools
        navigate_to_page,
        get_current_page_info,
        get_page_text,
        
        # Traditional element interaction
        find_element_info,
        click_element,
        type_text,
        
        # AI-friendly element interaction (Browser-use inspired)
        get_page_summary_for_ai,
        interact_with_element_by_index,
        find_elements_by_text_content,
        take_annotated_screenshot,
        wait_for_page_elements_to_change,
        
        # Analysis and extraction
        take_screenshot,
        execute_javascript,
        wait_for_condition,
        extract_links,
        extract_form_fields,
        get_action_history,
    ]


def register_browser_tools(agent: Any) -> None:
    """
    Register all browser tools with an agent.
    
    Args:
        agent: pydantic-ai agent to register tools with
    """
    if not PYDANTIC_AI_AVAILABLE:
        return
        
    tools = get_all_browser_tools()
    for tool in tools:
        agent.tool(tool)