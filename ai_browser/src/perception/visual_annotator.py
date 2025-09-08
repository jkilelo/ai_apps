"""Visual annotation system using Set-of-Marks (SoM)"""

from typing import List, Dict, Tuple, Optional, Any
from playwright.async_api import Page
from loguru import logger
import base64
import json
from .models import InteractiveElement, AnnotatedElement


class VisualAnnotator:
    """Implements Set-of-Marks visual annotation for web pages"""
    
    # Color coding based on CLAUDE.md specifications
    COLOR_MAP = {
        'button': '#FF6B6B',  # Red
        'link': '#4ECDC4',    # Cyan  
        'input': '#95E77E',   # Green
        'select': '#FFE66D',  # Yellow
        'textarea': '#95E77E', # Green (same as input)
        'checkbox': '#95E77E', # Green
        'radio': '#95E77E',   # Green
        'default': '#FF6B6B'  # Red as default
    }
    
    # JavaScript for Set-of-Marks annotation
    SOM_INJECTION_SCRIPT = """
    (async function annotateInteractiveElements() {
        // Configuration with color mapping
        const colorMap = {
            'BUTTON': '#FF6B6B',  // Red
            'A': '#4ECDC4',       // Cyan
            'INPUT': '#95E77E',   // Green
            'SELECT': '#FFE66D',  // Yellow
            'TEXTAREA': '#95E77E', // Green
            'default': '#FF6B6B'  // Red default
        };
        
        // Base label style
        const baseLabelStyle = {
            position: 'absolute',
            color: 'white',
            fontSize: '14px',
            fontWeight: 'bold',
            padding: '2px 6px',
            borderRadius: '2px',
            zIndex: 10000,
            pointerEvents: 'none',
            fontFamily: 'Arial, sans-serif',
            lineHeight: '1.2',
            boxShadow: '0 2px 4px rgba(0,0,0,0.3)',
            backgroundColor: 'rgba(0,0,0,0.7)'  // Semi-transparent black background
        };
        
        // Remove any existing annotations
        document.querySelectorAll('.som-annotation-label').forEach(el => el.remove());
        
        // Define interactive selectors (exclude hidden and carousel elements)
        const interactiveSelectors = [
            'button:not([style*="display: none"]):not([style*="visibility: hidden"])',
            'a[href]:not([style*="display: none"]):not([style*="visibility: hidden"])',
            'input:not([type="hidden"]):not(.a-carousel-firstvisibleitem):not([style*="display: none"]):not([style*="visibility: hidden"])',
            'select:not([style*="display: none"]):not([style*="visibility: hidden"])',
            'textarea:not([style*="display: none"]):not([style*="visibility: hidden"])',
            '[onclick]:not([style*="display: none"]):not([style*="visibility: hidden"])',
            '[role="button"]:not([style*="display: none"]):not([style*="visibility: hidden"])',
            '[role="link"]:not([style*="display: none"]):not([style*="visibility: hidden"])',
            '[role="checkbox"]:not([style*="display: none"]):not([style*="visibility: hidden"])',
            '[role="radio"]:not([style*="display: none"]):not([style*="visibility: hidden"])',
            '[role="combobox"]:not([style*="display: none"]):not([style*="visibility: hidden"])',
            '[role="textbox"]:not([style*="display: none"]):not([style*="visibility: hidden"])',
            '[role="searchbox"]:not([style*="display: none"]):not([style*="visibility: hidden"])',
            '[role="tab"]:not([style*="display: none"]):not([style*="visibility: hidden"])',
            '[role="menuitem"]:not([style*="display: none"]):not([style*="visibility: hidden"])',
            '[contenteditable="true"]:not([style*="display: none"]):not([style*="visibility: hidden"])',
            'video:not([style*="display: none"]):not([style*="visibility: hidden"])',
            'audio:not([style*="display: none"]):not([style*="visibility: hidden"])',
            'iframe:not([style*="display: none"]):not([style*="visibility: hidden"])'
        ];
        
        // Find all interactive elements
        const elements = document.querySelectorAll(interactiveSelectors.join(', '));
        const annotatedElements = [];
        let labelIndex = 1;
        
        // Helper function to check if element is visible
        function isVisible(element) {
            if (!element) return false;
            
            // Check for hidden input type
            if (element.type === 'hidden') {
                return false;
            }
            
            // Check for Amazon carousel elements specifically
            if (element.classList.contains('a-carousel-firstvisibleitem') || 
                element.classList.contains('a-carousel-lastvisibleitem') ||
                element.className.includes('carousel')) {
                return false;
            }
            
            const style = window.getComputedStyle(element);
            if (style.display === 'none' || 
                style.visibility === 'hidden' || 
                style.opacity === '0') {
                return false;
            }
            
            const rect = element.getBoundingClientRect();
            if (rect.width === 0 || rect.height === 0) {
                return false;
            }
            
            // For search inputs, be more lenient with viewport requirements
            const isSearchInput = element.id === 'twotabsearchtextbox' || 
                                element.name === 'field-keywords' ||
                                element.getAttribute('aria-label')?.includes('Search') ||
                                element.placeholder?.includes('Search') ||
                                element.type === 'search';
            
            if (isSearchInput) {
                // Search inputs just need to be present and have size
                return rect.width > 0 && rect.height > 0;
            }
            
            // Check if element is in viewport (with some tolerance)
            const inViewport = (
                rect.bottom >= -100 &&
                rect.right >= -100 &&
                rect.top <= (window.innerHeight || document.documentElement.clientHeight) + 100 &&
                rect.left <= (window.innerWidth || document.documentElement.clientWidth) + 100
            );
            
            return inViewport;
        }
        
        // Helper to generate unique selector for element
        function generateSelector(element) {
            if (element.id) {
                return '#' + CSS.escape(element.id);
            }
            
            if (element.className && typeof element.className === 'string') {
                const classes = element.className.trim().split(/\\s+/);
                if (classes.length > 0 && classes[0]) {
                    return '.' + classes.map(c => CSS.escape(c)).join('.');
                }
            }
            
            // Generate path selector
            let path = [];
            let current = element;
            while (current && current.tagName) {
                let selector = current.tagName.toLowerCase();
                
                // Add nth-child if needed
                if (current.parentElement) {
                    const siblings = Array.from(current.parentElement.children)
                        .filter(child => child.tagName === current.tagName);
                    if (siblings.length > 1) {
                        const index = siblings.indexOf(current) + 1;
                        selector += ':nth-of-type(' + index + ')';
                    }
                }
                
                path.unshift(selector);
                if (current.tagName === 'BODY') break;
                current = current.parentElement;
            }
            
            return path.join(' > ');
        }
        
        // Annotate each visible element
        for (const element of elements) {
            if (!isVisible(element)) continue;
            
            const rect = element.getBoundingClientRect();
            const scrollX = window.pageXOffset || document.documentElement.scrollLeft;
            const scrollY = window.pageYOffset || document.documentElement.scrollTop;
            
            // Create label element
            const label = document.createElement('div');
            label.className = 'som-annotation-label';
            label.textContent = labelIndex.toString();
            
            // Determine color based on element type
            let bgColor = colorMap.default;
            const tagName = element.tagName.toUpperCase();
            if (colorMap[tagName]) {
                bgColor = colorMap[tagName];
            } else if (element.type === 'submit' || element.type === 'button') {
                bgColor = colorMap['BUTTON'];
            }
            
            // Apply styles with appropriate color
            Object.assign(label.style, baseLabelStyle);
            label.style.border = `2px solid ${bgColor}`;
            
            // Position label at top-left corner of element
            label.style.left = (rect.left + scrollX) + 'px';
            label.style.top = (rect.top + scrollY - 2) + 'px';
            
            // Adjust position if label would be off-screen
            if (rect.top < 20) {
                label.style.top = (rect.bottom + scrollY + 2) + 'px';
            }
            
            // Add to document
            document.body.appendChild(label);
            
            // Store element info
            const elementInfo = {
                id: labelIndex,
                selector: generateSelector(element),
                tagName: element.tagName.toLowerCase(),
                text: element.textContent?.substring(0, 100)?.trim() || '',
                type: element.type || element.tagName.toLowerCase(),
                href: element.href || '',
                value: element.value || '',
                placeholder: element.placeholder || '',
                ariaLabel: element.getAttribute('aria-label') || '',
                role: element.getAttribute('role') || '',
                rect: {
                    x: rect.left,
                    y: rect.top,
                    width: rect.width,
                    height: rect.height
                }
            };
            
            annotatedElements.push(elementInfo);
            labelIndex++;
        }
        
        return annotatedElements;
    })();
    """
    
    REMOVE_ANNOTATIONS_SCRIPT = """
    document.querySelectorAll('.som-annotation-label').forEach(el => el.remove());
    """
    
    def __init__(self):
        self.last_annotations: List[Dict[str, Any]] = []
        self.element_map: Dict[int, str] = {}
    
    async def annotate_page(self, page: Page) -> Tuple[List[Dict[str, Any]], Dict[int, str]]:
        """
        Inject Set-of-Marks annotations and return element information
        
        Returns:
            Tuple of (annotated_elements, element_map)
        """
        try:
            # Inject and execute annotation script
            annotated_elements = await page.evaluate(self.SOM_INJECTION_SCRIPT)
            
            # Create element map
            element_map = {}
            for elem in annotated_elements:
                element_map[elem['id']] = elem['selector']
            
            self.last_annotations = annotated_elements
            self.element_map = element_map
            
            logger.info(f"Annotated {len(annotated_elements)} interactive elements")
            return annotated_elements, element_map
            
        except Exception as e:
            logger.error(f"Failed to annotate page: {e}")
            return [], {}
    
    async def capture_annotated_screenshot(self, page: Page, 
                                          full_page: bool = False) -> Tuple[bytes, List[Dict[str, Any]]]:
        """
        Capture screenshot with annotations
        
        Returns:
            Tuple of (screenshot_bytes, annotated_elements)
        """
        try:
            # Annotate the page
            annotated_elements, element_map = await self.annotate_page(page)
            
            # Wait a moment for annotations to render
            await page.wait_for_timeout(100)
            
            # Capture screenshot
            screenshot = await page.screenshot(full_page=full_page)
            
            logger.debug(f"Captured annotated screenshot with {len(annotated_elements)} elements")
            return screenshot, annotated_elements
            
        except Exception as e:
            logger.error(f"Failed to capture annotated screenshot: {e}")
            # Try to capture without annotations
            screenshot = await page.screenshot(full_page=full_page)
            return screenshot, []
    
    async def remove_annotations(self, page: Page) -> None:
        """Remove all visual annotations from the page"""
        try:
            await page.evaluate(self.REMOVE_ANNOTATIONS_SCRIPT)
            logger.debug("Removed all annotations from page")
        except Exception as e:
            logger.error(f"Failed to remove annotations: {e}")
    
    async def capture_clean_and_annotated(self, page: Page, 
                                         full_page: bool = False) -> Dict[str, Any]:
        """
        Capture both clean and annotated screenshots
        
        Returns:
            Dictionary with clean_screenshot, annotated_screenshot, and element data
        """
        result = {
            'clean_screenshot': None,
            'clean_screenshot_base64': None,
            'annotated_screenshot': None,
            'annotated_screenshot_base64': None,
            'annotated_elements': [],
            'element_map': {}
        }
        
        try:
            # First capture clean screenshot
            clean_screenshot = await page.screenshot(full_page=full_page)
            result['clean_screenshot'] = clean_screenshot
            result['clean_screenshot_base64'] = base64.b64encode(clean_screenshot).decode('utf-8')
            
            # Then annotate and capture
            annotated_screenshot, annotated_elements = await self.capture_annotated_screenshot(
                page, full_page=full_page
            )
            result['annotated_screenshot'] = annotated_screenshot
            result['annotated_screenshot_base64'] = base64.b64encode(annotated_screenshot).decode('utf-8')
            result['annotated_elements'] = annotated_elements
            result['element_map'] = self.element_map
            
            # Clean up annotations
            await self.remove_annotations(page)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to capture screenshots: {e}")
            return result
    
    def create_annotated_elements(self, interactive_elements: List[InteractiveElement],
                                 annotations: List[Dict[str, Any]]) -> List[AnnotatedElement]:
        """
        Match interactive elements with visual annotations
        
        Args:
            interactive_elements: List of InteractiveElement from DOM
            annotations: List of annotation data from JavaScript
            
        Returns:
            List of AnnotatedElement with matched annotations
        """
        annotated = []
        
        # Create selector map from interactive elements
        selector_to_element = {}
        for elem in interactive_elements:
            selector_to_element[elem.selector] = elem
        
        # Match annotations with elements
        for annotation in annotations:
            selector = annotation.get('selector')
            if selector in selector_to_element:
                element = selector_to_element[selector]
                annotated_elem = AnnotatedElement(
                    element=element,
                    annotation_id=annotation['id'],
                    color='red',
                    confidence=1.0
                )
                annotated.append(annotated_elem)
            else:
                # Create new element from annotation
                elem = InteractiveElement(
                    id=annotation['id'],
                    selector=selector,
                    type='other',
                    tag_name=annotation.get('tagName', ''),
                    text=annotation.get('text', ''),
                    href=annotation.get('href', ''),
                    value=annotation.get('value', ''),
                    placeholder=annotation.get('placeholder', ''),
                    attributes={},
                    aria_label=annotation.get('ariaLabel', ''),
                    aria_role=annotation.get('role', ''),
                    bounding_box=annotation.get('rect')
                )
                annotated_elem = AnnotatedElement(
                    element=elem,
                    annotation_id=annotation['id'],
                    color='red',
                    confidence=0.8
                )
                annotated.append(annotated_elem)
        
        return annotated
    
    async def highlight_element(self, page: Page, selector: str, 
                               color: str = 'yellow', duration: int = 2000) -> None:
        """
        Temporarily highlight a specific element
        
        Args:
            page: Playwright page
            selector: CSS selector of element to highlight
            color: Highlight color
            duration: Duration in milliseconds
        """
        try:
            highlight_script = f"""
            const element = document.querySelector('{selector}');
            if (element) {{
                const originalStyle = element.style.cssText;
                element.style.outline = '3px solid {color}';
                element.style.outlineOffset = '2px';
                element.style.transition = 'outline 0.3s';
                
                setTimeout(() => {{
                    element.style.cssText = originalStyle;
                }}, {duration});
            }}
            """
            await page.evaluate(highlight_script)
            logger.debug(f"Highlighted element: {selector}")
        except Exception as e:
            logger.error(f"Failed to highlight element {selector}: {e}")
    
    async def scroll_to_element(self, page: Page, selector: str) -> bool:
        """
        Scroll element into view
        
        Args:
            page: Playwright page
            selector: CSS selector of element
            
        Returns:
            True if successful, False otherwise
        """
        try:
            scroll_script = f"""
            const element = document.querySelector('{selector}');
            if (element) {{
                element.scrollIntoView({{
                    behavior: 'smooth',
                    block: 'center',
                    inline: 'center'
                }});
                return true;
            }}
            return false;
            """
            result = await page.evaluate(scroll_script)
            if result:
                await page.wait_for_timeout(500)  # Wait for smooth scroll
            return result
        except Exception as e:
            logger.error(f"Failed to scroll to element {selector}: {e}")
            return False