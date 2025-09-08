"""
Enhanced DOM extraction with visual element indexing for AI-first browser.
Inspired by browser_use's approach to make web pages AI-accessible.

This module provides numbered element extraction that allows AI agents to interact
with web pages using simple commands like "Click element [5]" or "Type 'text' in element [3]".
"""

import asyncio
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from playwright.async_api import Page, ElementHandle
import logging

from ..core.js_library import JSLibrary

logger = logging.getLogger(__name__)


@dataclass
class DOMElement:
    """Represents an interactive DOM element with visual context."""
    
    index: int  # Visual index shown on screenshot
    tag_name: str
    selector: str
    xpath: str
    text: str = ""
    aria_label: Optional[str] = None
    role: Optional[str] = None
    is_clickable: bool = False
    is_input: bool = False
    is_visible: bool = True
    bounding_box: Optional[Dict[str, float]] = None
    element_hash: str = ""
    attributes: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Generate unique hash for element tracking."""
        if not self.element_hash:
            content = f"{self.tag_name}_{self.selector}_{self.text}_{self.aria_label}"
            self.element_hash = hashlib.md5(content.encode()).hexdigest()[:8]
    
    def to_ai_format(self) -> str:
        """Format element for AI understanding."""
        element_type = self._get_element_type()
        text_content = self.text[:50] if self.text else self.aria_label or ""
        
        return f"[{self.index}] {element_type}: {text_content}"
    
    def _get_element_type(self) -> str:
        """Determine element type for AI context."""
        if self.tag_name == "input":
            input_type = self.attributes.get("type", "text")
            return f"input_{input_type}"
        elif self.tag_name == "button":
            return "button"
        elif self.tag_name == "a":
            return "link"
        elif self.tag_name == "select":
            return "dropdown"
        elif self.is_clickable:
            return "clickable"
        else:
            return self.tag_name


class DOMExtractor:
    """Extract and index interactive DOM elements for AI interaction."""
    
    # Enhanced JavaScript to extract interactive elements with better detection
    EXTRACT_ELEMENTS_JS = """
    () => {
        const elements = [];
        const interactiveSelectors = [
            'a[href]', 'button', 'input', 'textarea', 'select',
            '[role="button"]', '[role="link"]', '[role="tab"]', '[role="menuitem"]',
            '[onclick]', '[ng-click]', '[data-action]', '[data-testid]',
            '.btn', '.button', '.link', '[type="submit"]', '[type="button"]'
        ];
        
        const seen = new Set();
        
        for (const selector of interactiveSelectors) {
            try {
                const nodes = document.querySelectorAll(selector);
                for (const node of nodes) {
                    if (seen.has(node)) continue;
                    seen.add(node);
                    
                    // Check visibility with advanced detection
                    const rect = node.getBoundingClientRect();
                    const style = window.getComputedStyle(node);
                    
                    if (rect.width < 1 || rect.height < 1) continue;
                    if (style.display === 'none' || style.visibility === 'hidden') continue;
                    if (parseFloat(style.opacity) < 0.1) continue;
                    
                    // Check if in viewport (with buffer for scrolling)
                    const inViewport = (
                        rect.top < window.innerHeight + 200 &&
                        rect.bottom > -200 &&
                        rect.left < window.innerWidth + 200 &&
                        rect.right > -200
                    );
                    
                    if (!inViewport) continue;
                    
                    // Check if element is truly interactive
                    const isInteractive = (
                        node.tagName === 'BUTTON' ||
                        node.tagName === 'A' ||
                        node.tagName === 'INPUT' ||
                        node.tagName === 'TEXTAREA' ||
                        node.tagName === 'SELECT' ||
                        node.onclick ||
                        node.getAttribute('role') === 'button' ||
                        node.getAttribute('role') === 'link' ||
                        node.getAttribute('tabindex') !== null ||
                        node.hasAttribute('ng-click') ||
                        node.hasAttribute('data-action')
                    );
                    
                    if (!isInteractive) continue;
                    
                    // Extract comprehensive element data
                    const elementData = {
                        tagName: node.tagName.toLowerCase(),
                        text: (node.innerText || node.textContent || node.value || '').trim(),
                        ariaLabel: node.getAttribute('aria-label'),
                        role: node.getAttribute('role'),
                        type: node.getAttribute('type'),
                        placeholder: node.getAttribute('placeholder'),
                        href: node.getAttribute('href'),
                        id: node.id,
                        className: node.className,
                        title: node.getAttribute('title'),
                        boundingBox: {
                            x: Math.round(rect.x),
                            y: Math.round(rect.y),
                            width: Math.round(rect.width),
                            height: Math.round(rect.height)
                        },
                        isClickable: (
                            node.onclick != null || 
                            node.hasAttribute('ng-click') ||
                            node.tagName === 'BUTTON' ||
                            node.tagName === 'A' ||
                            node.getAttribute('role') === 'button'
                        ),
                        isInput: (
                            node.tagName === 'INPUT' || 
                            node.tagName === 'TEXTAREA' ||
                            node.tagName === 'SELECT'
                        )
                    };
                    
                    elements.push(elementData);
                }
            } catch (e) {
                console.log('Error with selector:', selector, e);
            }
        }
        
        // Sort by visual position (reading order: top to bottom, left to right)
        elements.sort((a, b) => {
            const yDiff = a.boundingBox.y - b.boundingBox.y;
            if (Math.abs(yDiff) > 15) return yDiff; // More tolerance for same row
            return a.boundingBox.x - b.boundingBox.x;
        });
        
        return elements.slice(0, 50); // Limit to 50 elements to avoid overwhelming AI
    }
    """
    
    def __init__(self, page: Page):
        """Initialize with Playwright page."""
        self.page = page
        self.elements: Dict[int, DOMElement] = {}
        self.element_map: Dict[str, int] = {}  # hash -> index mapping
        self.last_extraction_hash: Optional[str] = None
        self.js_lib = JSLibrary()  # Use shared JS library to follow DRY
        
    async def extract_interactive_elements(self) -> List[DOMElement]:
        """Extract all interactive elements from the current page."""
        try:
            # Execute JavaScript to find elements
            raw_elements = await self.page.evaluate(self.EXTRACT_ELEMENTS_JS)
            
            # Check if page changed since last extraction
            page_hash = self._calculate_page_hash(raw_elements)
            if page_hash == self.last_extraction_hash and self.elements:
                logger.debug("Page unchanged, using cached elements")
                return list(self.elements.values())
            
            # Clear previous elements
            self.elements.clear()
            self.element_map.clear()
            self.last_extraction_hash = page_hash
            
            # Convert to DOMElement objects
            elements = []
            for idx, elem_data in enumerate(raw_elements, 1):
                # Build selector with better strategies
                selector = await self._build_smart_selector(elem_data)
                xpath = self._build_smart_xpath(elem_data)
                
                # Create DOMElement
                element = DOMElement(
                    index=idx,
                    tag_name=elem_data['tagName'],
                    selector=selector,
                    xpath=xpath,
                    text=elem_data.get('text', '').strip(),
                    aria_label=elem_data.get('ariaLabel'),
                    role=elem_data.get('role'),
                    is_clickable=elem_data.get('isClickable', False),
                    is_input=elem_data.get('isInput', False),
                    bounding_box=elem_data.get('boundingBox'),
                    attributes={
                        'type': elem_data.get('type'),
                        'placeholder': elem_data.get('placeholder'),
                        'href': elem_data.get('href'),
                        'id': elem_data.get('id'),
                        'class': elem_data.get('className'),
                        'title': elem_data.get('title')
                    }
                )
                
                elements.append(element)
                self.elements[idx] = element
                self.element_map[element.element_hash] = idx
                
            logger.info(f"Extracted {len(elements)} interactive elements")
            return elements
            
        except Exception as e:
            logger.error(f"Failed to extract DOM elements: {e}")
            return []
    
    def _calculate_page_hash(self, raw_elements: List[Dict]) -> str:
        """Calculate hash of page content for change detection."""
        content = json.dumps(raw_elements, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    async def _build_smart_selector(self, elem_data: Dict) -> str:
        """Build robust CSS selector for element using multiple strategies."""
        tag = elem_data['tagName']
        
        # Strategy 1: Use ID if available and unique
        if elem_data.get('id'):
            elem_id = elem_data['id']
            try:
                # Verify ID is unique
                count = await self.page.evaluate(f"document.querySelectorAll('#{elem_id}').length")
                if count == 1:
                    return f"#{elem_id}"
            except:
                pass
        
        # Strategy 2: Use data-testid for testing frameworks
        if 'data-testid' in str(elem_data.get('className', '')):
            try:
                test_id = await self.page.evaluate(f"""
                    Array.from(document.getElementsByTagName('{tag}')).find(el => 
                        el.getBoundingClientRect().x === {elem_data['boundingBox']['x']} &&
                        el.getBoundingClientRect().y === {elem_data['boundingBox']['y']}
                    )?.getAttribute('data-testid')
                """)
                if test_id:
                    return f"[data-testid='{test_id}']"
            except:
                pass
        
        # Strategy 3: Use meaningful class names
        if elem_data.get('className'):
            classes = elem_data['className'].split()
            meaningful_classes = [c for c in classes if len(c) > 2 and not c.startswith('css-')]
            if meaningful_classes:
                class_selector = f"{tag}.{meaningful_classes[0]}"
                return class_selector
        
        # Strategy 4: Use text content for specificity
        if elem_data.get('text'):
            text = elem_data['text'][:30].replace("'", "\\'")
            return f"{tag}:has-text('{text}')"
        
        # Strategy 5: Use aria-label
        if elem_data.get('ariaLabel'):
            aria_label = elem_data['ariaLabel'].replace("'", "\\'")
            return f"{tag}[aria-label='{aria_label}']"
        
        # Strategy 6: Use href for links
        if tag == 'a' and elem_data.get('href'):
            href = elem_data['href']
            return f"a[href='{href}']"
        
        # Strategy 7: Use type for inputs
        if tag == 'input' and elem_data.get('type'):
            input_type = elem_data['type']
            return f"input[type='{input_type}']"
        
        # Fallback: Use tag with position
        return f"{tag}:nth-of-type(1)"
    
    def _build_smart_xpath(self, elem_data: Dict) -> str:
        """Generate smart XPath for element."""
        tag = elem_data['tagName']
        
        # Use ID if available
        if elem_data.get('id'):
            return f"//{tag}[@id='{elem_data['id']}']"
        
        # Use text content
        if elem_data.get('text'):
            text = elem_data['text'][:50].replace("'", "\\'")
            return f"//{tag}[contains(text(), '{text}')]"
        
        # Use aria-label
        if elem_data.get('ariaLabel'):
            aria_label = elem_data['ariaLabel'].replace("'", "\\'")
            return f"//{tag}[@aria-label='{aria_label}']"
        
        # Fallback
        return f"//{tag}"
    
    async def get_element_by_index(self, index: int) -> Optional[ElementHandle]:
        """Get Playwright ElementHandle by index with multiple fallback strategies."""
        if index not in self.elements:
            logger.warning(f"Element index {index} not found")
            return None
            
        element = self.elements[index]
        
        try:
            # Strategy 1: Try primary selector
            handle = await self.page.query_selector(element.selector)
            
            if not handle:
                # Strategy 2: Try XPath
                handles = await self.page.query_selector_all(f"xpath={element.xpath}")
                if handles:
                    handle = handles[0]
            
            if not handle:
                # Strategy 3: Try position-based selection
                bbox = element.bounding_box
                if bbox:
                    handle = await self.page.evaluate(f"""
                        document.elementFromPoint({bbox['x'] + bbox['width']/2}, {bbox['y'] + bbox['height']/2})
                    """)
                    
            return handle
            
        except Exception as e:
            logger.error(f"Failed to get element {index}: {e}")
            return None
    
    async def click_element(self, index: int) -> bool:
        """Click element by index with intelligent retry."""
        element_info = self.elements.get(index)
        if not element_info:
            logger.error(f"Element {index} not found")
            return False
        
        try:
            # Try multiple strategies
            strategies = [
                self._click_by_handle,
                self._click_by_coordinate,
                self._click_by_js
            ]
            
            for strategy in strategies:
                if await strategy(index):
                    logger.info(f"Successfully clicked element {index} using {strategy.__name__}")
                    return True
                    
            logger.error(f"All click strategies failed for element {index}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to click element {index}: {e}")
            return False
    
    async def _click_by_handle(self, index: int) -> bool:
        """Click using element handle."""
        try:
            handle = await self.get_element_by_index(index)
            if handle:
                await handle.click(timeout=5000)
                return True
            return False
        except:
            return False
    
    async def _click_by_coordinate(self, index: int) -> bool:
        """Click using coordinates."""
        try:
            element = self.elements[index]
            bbox = element.bounding_box
            if bbox:
                x = bbox['x'] + bbox['width'] / 2
                y = bbox['y'] + bbox['height'] / 2
                await self.page.mouse.click(x, y)
                return True
            return False
        except:
            return False
    
    async def _click_by_js(self, index: int) -> bool:
        """Click using JavaScript."""
        try:
            element = self.elements[index]
            bbox = element.bounding_box
            if bbox:
                await self.page.evaluate(f"""
                    const el = document.elementFromPoint({bbox['x'] + bbox['width']/2}, {bbox['y'] + bbox['height']/2});
                    if (el) el.click();
                """)
                return True
            return False
        except:
            return False
    
    async def type_in_element(self, index: int, text: str) -> bool:
        """Type text in element by index with validation."""
        if not text:
            logger.error("No text provided for typing")
            return False
            
        handle = await self.get_element_by_index(index)
        if not handle:
            return False
            
        try:
            element = self.elements[index]
            if not element.is_input:
                logger.warning(f"Element {index} is not an input field")
                return False
            
            # Clear existing content and type new text
            await handle.click()  # Focus
            await handle.fill("")  # Clear
            await handle.type(text)  # Type with human-like speed
            
            logger.info(f"Typed '{text}' in element {index}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to type in element {index}: {e}")
            return False
    
    def get_ai_friendly_summary(self) -> str:
        """Get AI-friendly summary of all interactive elements."""
        if not self.elements:
            return "No interactive elements found on the page."
        
        lines = ["Interactive elements on the page:"]
        
        # Group by type for better organization
        buttons = []
        inputs = []
        links = []
        others = []
        
        for element in self.elements.values():
            formatted = element.to_ai_format()
            
            if element.tag_name == "button" or element.role == "button":
                buttons.append(formatted)
            elif element.is_input:
                inputs.append(formatted)
            elif element.tag_name == "a":
                links.append(formatted)
            else:
                others.append(formatted)
        
        if inputs:
            lines.append("\n🔤 Input fields:")
            lines.extend(inputs[:8])  # Limit to avoid overwhelming
            
        if buttons:
            lines.append("\n🔘 Buttons:")
            lines.extend(buttons[:8])
            
        if links:
            lines.append("\n🔗 Links:")
            lines.extend(links[:10])
            
        if others:
            lines.append("\n⚡ Other interactive elements:")
            lines.extend(others[:8])
            
        return "\n".join(lines)
    
    async def annotate_screenshot(self, screenshot_path: str) -> str:
        """Take screenshot with numbered element overlays."""
        # Take base screenshot
        await self.page.screenshot(path=screenshot_path)
        
        # Inject enhanced CSS for number overlays
        await self.page.evaluate("""
            () => {
                const style = document.createElement('style');
                style.textContent = `
                    .ai-element-index {
                        position: absolute;
                        background: linear-gradient(45deg, #ff6b6b, #ee5a52);
                        color: white;
                        font-size: 11px;
                        font-weight: bold;
                        padding: 3px 6px;
                        border-radius: 4px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                        z-index: 999999;
                        pointer-events: none;
                        border: 1px solid rgba(255,255,255,0.3);
                        font-family: 'Segoe UI', sans-serif;
                    }
                `;
                document.head.appendChild(style);
            }
        """)
        
        # Add number overlays for each element
        for idx, element in self.elements.items():
            if element.bounding_box and idx <= 20:  # Limit annotations to first 20
                bbox = element.bounding_box
                await self.page.evaluate(f"""
                    () => {{
                        const div = document.createElement('div');
                        div.className = 'ai-element-index';
                        div.textContent = '{idx}';
                        div.style.left = '{bbox["x"]}px';
                        div.style.top = '{bbox["y"] - 2}px';
                        document.body.appendChild(div);
                    }}
                """)
        
        # Take annotated screenshot
        annotated_path = screenshot_path.replace('.png', '_annotated.png')
        await self.page.screenshot(path=annotated_path, full_page=True)
        
        # Clean up overlays
        await self.page.evaluate("""
            () => {
                document.querySelectorAll('.ai-element-index').forEach(el => el.remove());
            }
        """)
        
        return annotated_path
    
    def get_element_info(self, index: int) -> Optional[DOMElement]:
        """Get detailed information about an element by index."""
        return self.elements.get(index)
    
    def find_elements_by_text(self, text: str, exact: bool = False) -> List[int]:
        """Find elements containing specific text."""
        results = []
        search_text = text.lower()
        
        for idx, element in self.elements.items():
            element_text = (element.text or "").lower()
            aria_label = (element.aria_label or "").lower()
            
            if exact:
                if search_text == element_text or search_text == aria_label:
                    results.append(idx)
            else:
                if search_text in element_text or search_text in aria_label:
                    results.append(idx)
        
        return results
    
    async def wait_for_element_change(self, timeout: int = 5000) -> bool:
        """Wait for elements on page to change."""
        old_hash = self.last_extraction_hash
        
        for _ in range(timeout // 100):
            await asyncio.sleep(0.1)
            try:
                raw_elements = await self.page.evaluate(self.EXTRACT_ELEMENTS_JS)
                new_hash = self._calculate_page_hash(raw_elements)
                if new_hash != old_hash:
                    return True
            except:
                continue
                
        return False