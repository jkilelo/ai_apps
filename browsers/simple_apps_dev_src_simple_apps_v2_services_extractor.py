"""
Modern element extractor service with type safety and comprehensive extraction.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from playwright.async_api import Page

from simple_apps_v2.core.logging import get_logger
from simple_apps_v2.core.models import (
    BrowserConfig, ElementCategory, ExtractedElement, 
    InteractionPattern, TestPriority, ValidationRule
)
from simple_apps_v2.services.browser import BrowserService
from simple_apps_v2.services.llm import LLMService, LLMMessage

logger = get_logger(__name__)


class ElementExtractor:
    """Modern element extractor with comprehensive analysis."""
    
    def __init__(self, config: Optional[BrowserConfig] = None):
        """Initialize element extractor."""
        self.config = config or BrowserConfig()
        self.browser_service = BrowserService(self.config)
        self.llm_service = LLMService()
        
    async def extract_elements_from_url(
        self,
        url: str,
        analyze_with_llm: bool = True,
        categories: Optional[List[ElementCategory]] = None
    ) -> Dict[str, Any]:
        """
        Extract elements from a URL with optional LLM analysis.
        
        Args:
            url: Target URL
            analyze_with_llm: Whether to use LLM for analysis
            categories: Optional filter by element categories
            
        Returns:
            Extraction results dictionary
        """
        start_time = time.time()
        
        try:
            # Start browser service
            await self.browser_service.start()
            
            # Get page and navigate
            page = await self.browser_service.get_page(url)
            if not page:
                raise Exception(f"Failed to navigate to {url}")
            
            # Extract elements
            logger.info("Extracting elements from page")
            raw_elements = await self._extract_page_elements(page)
            
            # Process and categorize elements
            elements = self._process_elements(raw_elements, url)
            
            # Filter by categories if specified
            if categories:
                elements = [e for e in elements if e.category in categories]
            
            # Group by category
            elements_by_category = self._group_by_category(elements)
            
            # Optional LLM analysis
            llm_analysis = None
            if analyze_with_llm:
                logger.info("Performing LLM analysis")
                llm_analysis = await self._perform_llm_analysis(elements, url)
            
            extraction_time = time.time() - start_time
            
            result = {
                "success": True,
                "url": url,
                "total_elements": len(elements),
                "elements": [e.dict() for e in elements],
                "elements_by_category": {
                    category.value: [e.dict() for e in elem_list] 
                    for category, elem_list in elements_by_category.items()
                },
                "extraction_time": extraction_time,
                "llm_analysis": llm_analysis,
                "metadata": {
                    "page_title": await page.title(),
                    "page_url": page.url,
                    "extracted_at": datetime.now().isoformat(),
                    "extractor_version": "2.0.0"
                }
            }
            
            logger.info(f"Extraction completed: {len(elements)} elements in {extraction_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Element extraction failed: {e}")
            return {
                "success": False,
                "url": url,
                "total_elements": 0,
                "elements": [],
                "elements_by_category": {},
                "extraction_time": time.time() - start_time,
                "error": str(e)
            }
        finally:
            await self.browser_service.stop()
    
    async def _extract_page_elements(self, page: Page) -> List[Dict[str, Any]]:
        """Extract raw elements from page using JavaScript execution."""
        
        extraction_script = """
        () => {
            const elements = [];
            
            // Helper to get element properties
            const getElementInfo = (element) => {
                const rect = element.getBoundingClientRect();
                const styles = window.getComputedStyle(element);
                
                return {
                    tag_name: element.tagName.toLowerCase(),
                    selector: generateSelector(element),
                    element_type: getElementType(element),
                    text: getElementText(element),
                    placeholder: element.placeholder || null,
                    value: element.value || null,
                    href: element.href || null,
                    src: element.src || null,
                    id: element.id || null,
                    className: element.className || null,
                    
                    // Position and size
                    x: Math.round(rect.x),
                    y: Math.round(rect.y),
                    width: Math.round(rect.width),
                    height: Math.round(rect.height),
                    
                    // Visibility and state
                    visible: isVisible(element),
                    enabled: !element.disabled,
                    clickable: isClickable(element),
                    
                    // Attributes
                    attributes: getRelevantAttributes(element),
                    
                    // Computed styles (selected properties)
                    styles: {
                        display: styles.display,
                        visibility: styles.visibility,
                        opacity: styles.opacity,
                        position: styles.position,
                        zIndex: styles.zIndex
                    }
                };
            };
            
            // Generate unique CSS selector
            const generateSelector = (element) => {
                if (element.id) {
                    return `#${element.id}`;
                }
                
                let selector = element.tagName.toLowerCase();
                
                if (element.className) {
                    const classes = element.className.trim().split(/\\s+/);
                    if (classes.length > 0 && classes[0]) {
                        selector += '.' + classes.slice(0, 2).join('.');
                    }
                }
                
                // Add nth-child if needed for uniqueness
                const siblings = Array.from(element.parentNode?.children || [])
                    .filter(el => el.tagName === element.tagName);
                if (siblings.length > 1) {
                    const index = siblings.indexOf(element) + 1;
                    selector += `:nth-child(${index})`;
                }
                
                return selector;
            };
            
            // Determine element type
            const getElementType = (element) => {
                const tag = element.tagName.toLowerCase();
                const type = element.type;
                const role = element.getAttribute('role');
                
                if (tag === 'input') return type || 'text';
                if (tag === 'button' || role === 'button') return 'button';
                if (tag === 'a') return 'link';
                if (tag === 'select') return 'select';
                if (tag === 'textarea') return 'textarea';
                if (['img', 'video', 'audio'].includes(tag)) return 'media';
                if (['div', 'span', 'section', 'article'].includes(tag)) return 'container';
                
                return tag;
            };
            
            // Get meaningful text content
            const getElementText = (element) => {
                // For form elements, check labels
                if (['input', 'select', 'textarea'].includes(element.tagName.toLowerCase())) {
                    const label = element.labels?.[0] || 
                        document.querySelector(`label[for="${element.id}"]`);
                    if (label) return label.textContent.trim();
                }
                
                // Get direct text content
                let text = element.textContent?.trim() || '';
                
                // Limit text length
                if (text.length > 200) {
                    text = text.substring(0, 200) + '...';
                }
                
                return text || null;
            };
            
            // Check if element is visible
            const isVisible = (element) => {
                const rect = element.getBoundingClientRect();
                const styles = window.getComputedStyle(element);
                
                return rect.width > 0 && 
                       rect.height > 0 && 
                       styles.display !== 'none' && 
                       styles.visibility !== 'hidden' && 
                       styles.opacity !== '0';
            };
            
            // Check if element is clickable
            const isClickable = (element) => {
                const clickableTags = ['a', 'button', 'input', 'select', 'textarea'];
                const clickableTypes = ['button', 'submit', 'reset', 'checkbox', 'radio'];
                const tag = element.tagName.toLowerCase();
                const type = element.type;
                const role = element.getAttribute('role');
                
                return clickableTags.includes(tag) || 
                       clickableTypes.includes(type) ||
                       role === 'button' ||
                       element.onclick !== null ||
                       element.hasAttribute('onclick') ||
                       window.getComputedStyle(element).cursor === 'pointer';
            };
            
            // Get relevant attributes
            const getRelevantAttributes = (element) => {
                const relevantAttrs = [
                    'name', 'type', 'role', 'aria-label', 'title', 'alt', 
                    'data-testid', 'data-test', 'for', 'form'
                ];
                
                const attributes = {};
                relevantAttrs.forEach(attr => {
                    const value = element.getAttribute(attr);
                    if (value !== null) {
                        attributes[attr] = value;
                    }
                });
                
                return attributes;
            };
            
            // Extract all relevant elements
            const selectors = [
                'input', 'button', 'a', 'select', 'textarea', 'form',
                '[role="button"]', '[role="link"]', '[role="textbox"]',
                '[onclick]', '[data-testid]', '[data-test]',
                'h1, h2, h3, h4, h5, h6', 'img', 'video', 'audio',
                '.btn', '.button', '.link', '.nav', '.menu'
            ];
            
            const allElements = new Set();
            
            selectors.forEach(selector => {
                try {
                    document.querySelectorAll(selector).forEach(el => {
                        if (!allElements.has(el)) {
                            allElements.add(el);
                            const info = getElementInfo(el);
                            // Only include visible or potentially important elements
                            if (info.visible || info.clickable || 
                                ['input', 'button', 'a', 'select'].includes(info.tag_name)) {
                                elements.push(info);
                            }
                        }
                    });
                } catch (e) {
                    console.warn(`Error with selector ${selector}:`, e);
                }
            });
            
            return elements;
        }
        """
        
        try:
            elements = await page.evaluate(extraction_script)
            logger.info(f"Extracted {len(elements)} raw elements from page")
            return elements
        except Exception as e:
            logger.error(f"Error executing extraction script: {e}")
            return []
    
    def _process_elements(self, raw_elements: List[Dict[str, Any]], url: str) -> List[ExtractedElement]:
        """Process raw elements into structured ExtractedElement models."""
        processed_elements = []
        
        for raw_elem in raw_elements:
            try:
                # Determine category
                category = self._categorize_element(raw_elem)
                
                # Determine priority
                priority = self._determine_priority(raw_elem, category)
                
                # Determine interaction patterns
                patterns = self._get_interaction_patterns(raw_elem)
                
                # Determine validation rules
                validation_rules = self._get_validation_rules(raw_elem)
                
                # Generate description
                description = self._generate_description(raw_elem)
                
                # Create ExtractedElement
                element = ExtractedElement(
                    selector=raw_elem.get("selector", ""),
                    tag_name=raw_elem.get("tag_name", ""),
                    element_type=raw_elem.get("element_type", ""),
                    category=category,
                    priority=priority,
                    text=raw_elem.get("text"),
                    placeholder=raw_elem.get("placeholder"),
                    value=raw_elem.get("value"),
                    href=raw_elem.get("href"),
                    src=raw_elem.get("src"),
                    visible=raw_elem.get("visible", True),
                    enabled=raw_elem.get("enabled", True),
                    x=raw_elem.get("x", 0),
                    y=raw_elem.get("y", 0),
                    width=raw_elem.get("width", 0),
                    height=raw_elem.get("height", 0),
                    clickable=raw_elem.get("clickable", False),
                    interaction_patterns=patterns,
                    description=description,
                    validation_rules=validation_rules,
                )
                
                processed_elements.append(element)
                
            except Exception as e:
                logger.warning(f"Error processing element: {e}")
                continue
        
        logger.info(f"Processed {len(processed_elements)} elements")
        return processed_elements
    
    def _categorize_element(self, element: Dict[str, Any]) -> ElementCategory:
        """Categorize element based on its properties."""
        tag = element.get("tag_name", "").lower()
        elem_type = element.get("element_type", "").lower()
        text = (element.get("text") or "").lower()
        attributes = element.get("attributes", {})
        
        # Navigation elements
        if (tag == "a" or "nav" in text or "menu" in text or 
            any(nav_term in text for nav_term in ["home", "about", "contact", "login", "logout"])):
            return ElementCategory.NAVIGATION
        
        # Form inputs
        if tag in ["input", "textarea", "select"] or elem_type in ["text", "email", "password", "number"]:
            return ElementCategory.FORM_INPUT
        
        # Buttons
        if tag == "button" or elem_type == "button" or attributes.get("role") == "button":
            return ElementCategory.BUTTON
        
        # Links
        if tag == "a" and element.get("href"):
            return ElementCategory.LINK
        
        # Media
        if tag in ["img", "video", "audio"] or elem_type == "media":
            return ElementCategory.MEDIA
        
        # Interactive elements
        if element.get("clickable") and tag not in ["a", "button"]:
            return ElementCategory.INTERACTIVE
        
        # Text display
        if tag in ["h1", "h2", "h3", "h4", "h5", "h6", "p", "span", "div"] and element.get("text"):
            return ElementCategory.TEXT_DISPLAY
        
        # Containers
        if tag in ["div", "section", "article", "main", "header", "footer"]:
            return ElementCategory.CONTAINER
        
        return ElementCategory.OTHER
    
    def _determine_priority(self, element: Dict[str, Any], category: ElementCategory) -> TestPriority:
        """Determine test priority based on element characteristics."""
        tag = element.get("tag_name", "").lower()
        elem_type = element.get("element_type", "").lower()
        text = (element.get("text") or "").lower()
        
        # Critical elements
        critical_keywords = ["login", "signup", "submit", "buy", "purchase", "checkout", "pay"]
        if any(keyword in text for keyword in critical_keywords):
            return TestPriority.CRITICAL
        
        if elem_type in ["submit", "button"] and category == ElementCategory.BUTTON:
            return TestPriority.HIGH
        
        if tag == "form" or category == ElementCategory.FORM_INPUT:
            return TestPriority.HIGH
        
        if category == ElementCategory.NAVIGATION:
            return TestPriority.HIGH
        
        if category in [ElementCategory.LINK, ElementCategory.INTERACTIVE]:
            return TestPriority.MEDIUM
        
        return TestPriority.LOW
    
    def _get_interaction_patterns(self, element: Dict[str, Any]) -> List[InteractionPattern]:
        """Determine possible interaction patterns for element."""
        patterns = []
        tag = element.get("tag_name", "").lower()
        elem_type = element.get("element_type", "").lower()
        
        # Click patterns
        if element.get("clickable") or tag in ["button", "a"]:
            patterns.append(InteractionPattern.CLICK)
        
        # Type patterns
        if tag in ["input", "textarea"] and elem_type not in ["checkbox", "radio", "button", "submit"]:
            patterns.append(InteractionPattern.TYPE)
        
        # Select patterns
        if tag == "select":
            patterns.append(InteractionPattern.SELECT)
        
        # Hover patterns (for interactive elements)
        if element.get("clickable"):
            patterns.append(InteractionPattern.HOVER)
        
        # Upload patterns
        if elem_type == "file":
            patterns.append(InteractionPattern.UPLOAD)
        
        return patterns
    
    def _get_validation_rules(self, element: Dict[str, Any]) -> List[ValidationRule]:
        """Determine validation rules for element."""
        rules = []
        
        if element.get("visible"):
            rules.append(ValidationRule.VISIBLE)
        
        if element.get("enabled"):
            rules.append(ValidationRule.ENABLED)
        
        if element.get("text"):
            rules.append(ValidationRule.CONTAINS_TEXT)
        
        if element.get("attributes"):
            rules.append(ValidationRule.HAS_ATTRIBUTE)
        
        return rules
    
    def _generate_description(self, element: Dict[str, Any]) -> str:
        """Generate human-readable description for element."""
        tag = element.get("tag_name", "")
        elem_type = element.get("element_type", "")
        text = element.get("text", "")
        
        if text:
            return f"{tag} element with text '{text[:50]}'"
        elif elem_type:
            return f"{tag} element of type '{elem_type}'"
        else:
            return f"{tag} element"
    
    def _group_by_category(self, elements: List[ExtractedElement]) -> Dict[ElementCategory, List[ExtractedElement]]:
        """Group elements by category."""
        grouped = {}
        for element in elements:
            if element.category not in grouped:
                grouped[element.category] = []
            grouped[element.category].append(element)
        
        return grouped
    
    async def _perform_llm_analysis(self, elements: List[ExtractedElement], url: str) -> Dict[str, Any]:
        """Perform LLM analysis of extracted elements."""
        try:
            # Convert elements to dict for LLM analysis
            elements_data = [element.dict() for element in elements]
            
            analysis = await self.llm_service.analyze_elements(
                elements=elements_data,
                url=url,
                analysis_type="comprehensive"
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {"error": str(e), "success": False}


# Backward compatibility function
async def extract_elements_from_url(
    url: str,
    headless: bool = True,
    analyze: bool = True
) -> Dict[str, Any]:
    """Backward compatibility function for element extraction."""
    config = BrowserConfig(headless=headless)
    extractor = ElementExtractor(config)
    
    return await extractor.extract_elements_from_url(
        url=url,
        analyze_with_llm=analyze
    )