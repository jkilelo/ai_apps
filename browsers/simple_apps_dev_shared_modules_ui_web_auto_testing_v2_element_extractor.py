"""
Element Extractor for UI Testing
Extracts all testable elements from a webpage using browser automation
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path
import sys
import re
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import browser functionality
from shared_modules.ui_web_auto_testing_v2.browser import BrowserService, BrowserConfig
from shared_modules.ui_web_auto_testing_v2.element_structure import (
    ElementCategory,
    InteractionPattern,
    TestPriority,
    ValidationRule
)

# Import LLM functionality  
from backend.shared.llm import query_llm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ElementExtractor:
    """Extracts testable elements from web pages"""
    
    def __init__(self, headless: bool = False):
        """Initialize the element extractor
        
        Args:
            headless: Whether to run browser in headless mode
        """
        self.config = BrowserConfig(
            headless=headless,
            stealth_level="maximum",
            enable_stealth=True,
            enable_human_simulation=True
        )
        self.browser_service = BrowserService(self.config)
        self.extracted_elements = []
        
    async def extract_elements(self, url: str) -> List[Dict[str, Any]]:
        """Extract all testable elements from a URL
        
        Args:
            url: The URL to extract elements from
            
        Returns:
            List of extracted elements with their properties
        """
        try:
            # Start browser service
            await self.browser_service.start()
            
            # Get page and navigate
            logger.info(f"Navigating to {url}")
            self.page = await self.browser_service.get_page(url)
            
            if not self.page:
                raise Exception(f"Failed to navigate to {url}")
            
            # Extract elements
            logger.info("Extracting elements from page")
            elements = await self._extract_page_elements()
            
            # Process and categorize elements
            processed_elements = self._process_elements(elements)
            
            self.extracted_elements = processed_elements
            return processed_elements
            
        except Exception as e:
            logger.error(f"Error extracting elements: {e}")
            raise
        finally:
            # Cleanup
            await self.browser_service.stop()
    
    async def _extract_page_elements(self) -> List[Dict[str, Any]]:
        """Extract elements using browser's extraction capabilities"""
        
        extraction_script = """
        () => {
            const elements = [];
            
            // Helper to get element properties
            const getElementInfo = (element) => {
                const rect = element.getBoundingClientRect();
                const styles = window.getComputedStyle(element);
                
                return {
                    tag_name: element.tagName.toLowerCase(),
                    id: element.id || null,
                    className: element.className || '',
                    name: element.name || null,
                    type: element.type || null,
                    href: element.href || null,
                    text: element.textContent?.trim().substring(0, 200) || '',
                    value: element.value || null,
                    placeholder: element.placeholder || null,
                    
                    // State
                    isEnabled: !element.disabled,
                    isVisible: rect.width > 0 && rect.height > 0 && styles.visibility !== 'hidden',
                    isRequired: element.required || false,
                    isReadonly: element.readOnly || false,
                    
                    // Position
                    position: {
                        x: Math.round(rect.x),
                        y: Math.round(rect.y),
                        width: Math.round(rect.width),
                        height: Math.round(rect.height)
                    },
                    
                    // Accessibility
                    ariaLabel: element.getAttribute('aria-label'),
                    ariaRole: element.getAttribute('role'),
                    tabIndex: element.tabIndex,
                    
                    // Validation
                    pattern: element.pattern || null,
                    minLength: element.minLength || null,
                    maxLength: element.maxLength || null,
                    min: element.min || null,
                    max: element.max || null,
                    
                    // Selectors
                    xpath: (() => {
                        let path = '';
                        let current = element;
                        while (current && current.nodeType === Node.ELEMENT_NODE) {
                            let index = 0;
                            let sibling = current.previousSibling;
                            while (sibling) {
                                if (sibling.nodeType === Node.ELEMENT_NODE && 
                                    sibling.nodeName === current.nodeName) {
                                    index++;
                                }
                                sibling = sibling.previousSibling;
                            }
                            const tagName = current.nodeName.toLowerCase();
                            const xpathIndex = index > 0 ? `[${index + 1}]` : '';
                            path = `/${tagName}${xpathIndex}${path}`;
                            current = current.parentNode;
                        }
                        return path;
                    })(),
                    
                    cssSelector: (() => {
                        if (element.id) return `#${element.id}`;
                        let selector = element.tagName.toLowerCase();
                        if (element.className) {
                            const classes = element.className.split(' ').filter(c => c);
                            if (classes.length > 0) {
                                selector += `.${classes.join('.')}`;
                            }
                        }
                        return selector;
                    })()
                };
            };
            
            // Interactive element selectors
            const selectors = [
                'input:not([type="hidden"])',
                'textarea',
                'select',
                'button',
                'a[href]',
                '[role="button"]',
                '[role="link"]',
                '[onclick]',
                '[role="checkbox"]',
                '[role="radio"]',
                '[contenteditable="true"]',
                'label[for]'
            ];
            
            // Extract all interactive elements
            document.querySelectorAll(selectors.join(', ')).forEach(element => {
                try {
                    const info = getElementInfo(element);
                    // Only include visible elements
                    if (info.isVisible) {
                        elements.push(info);
                    }
                } catch (e) {
                    console.error('Error extracting element:', e);
                }
            });
            
            // Also extract forms for context
            document.querySelectorAll('form').forEach(form => {
                elements.push({
                    tag_name: 'form',
                    id: form.id || null,
                    name: form.name || null,
                    action: form.action || null,
                    method: form.method || null,
                    isForm: true
                });
            });
            
            return elements;
        }
        """
        
        # Execute extraction script on the page
        try:
            result = await self.page.evaluate(extraction_script)
            return result if result else []
        except Exception as e:
            logger.error(f"Failed to extract elements: {e}")
            return []
    
    def _process_elements(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and categorize extracted elements"""
        
        processed = []
        
        for element in elements:
            # Skip form containers (keep only for context)
            if element.get('isForm'):
                continue
                
            # Categorize element
            category = self._categorize_element(element)
            
            # Determine interaction pattern
            interaction = self._get_interaction_pattern(element)
            
            # Determine test priority
            priority = self._get_test_priority(element)
            
            # Add processing metadata
            element['category'] = category
            element['interaction_pattern'] = interaction
            element['test_priority'] = priority
            
            # Add human-readable description
            element['description'] = self._generate_description(element)
            
            processed.append(element)
        
        return processed
    
    def _categorize_element(self, element: Dict[str, Any]) -> str:
        """Categorize element based on its properties"""
        
        tag = element.get('tag_name', '')
        type_attr = element.get('type', '')
        role = element.get('ariaRole', '')
        text = (element.get('text', '') or '').lower()
        
        # Authentication elements
        if type_attr == 'password' or 'login' in text or 'sign in' in text:
            return ElementCategory.AUTHENTICATION.value
            
        # Search elements  
        if type_attr == 'search' or 'search' in text:
            return ElementCategory.SEARCH.value
            
        # Navigation elements
        if tag == 'a' or role == 'navigation':
            return ElementCategory.NAVIGATION.value
            
        # Form inputs
        if tag in ['input', 'textarea', 'select']:
            return ElementCategory.FORM_INPUT.value
            
        # Action elements
        if tag == 'button' or role == 'button':
            return ElementCategory.ACTION.value
            
        # Default to interactive
        return ElementCategory.INTERACTIVE.value
    
    def _get_interaction_pattern(self, element: Dict[str, Any]) -> str:
        """Determine primary interaction pattern for element"""
        
        tag = element.get('tag_name', '')
        type_attr = element.get('type', '')
        
        if tag in ['input', 'textarea']:
            if type_attr == 'file':
                return InteractionPattern.UPLOAD_FILE.value
            return InteractionPattern.TYPE_TEXT.value
            
        if tag == 'select':
            return InteractionPattern.SELECT_OPTION.value
            
        if tag in ['button', 'a'] or element.get('ariaRole') == 'button':
            return InteractionPattern.CLICK.value
            
        return InteractionPattern.CLICK.value
    
    def _get_test_priority(self, element: Dict[str, Any]) -> str:
        """Determine test priority for element"""
        
        text = (element.get('text', '') or '').lower()
        type_attr = element.get('type', '')
        
        # Critical elements
        if type_attr == 'submit' or 'submit' in text or 'login' in text:
            return TestPriority.CRITICAL.value
            
        # High priority
        if element.get('isRequired') or type_attr == 'password':
            return TestPriority.HIGH.value
            
        # Medium priority
        if element.get('tag_name') in ['input', 'select', 'textarea']:
            return TestPriority.MEDIUM.value
            
        return TestPriority.LOW.value
    
    def _generate_description(self, element: Dict[str, Any]) -> str:
        """Generate human-readable description of element"""
        
        tag = element.get('tag_name', 'element')
        text = element.get('text', '')
        placeholder = element.get('placeholder', '')
        aria_label = element.get('ariaLabel', '')
        element_id = element.get('id', '')
        
        # Build description
        desc_parts = [f"{tag}"]
        
        if element_id:
            desc_parts.append(f"with id '{element_id}'")
        
        if aria_label:
            desc_parts.append(f"labeled '{aria_label}'")
        elif placeholder:
            desc_parts.append(f"with placeholder '{placeholder}'")
        elif text and len(text) < 50:
            desc_parts.append(f"containing '{text}'")
        
        return " ".join(desc_parts)
    
    async def analyze_with_llm(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Use LLM to analyze extracted elements and suggest test scenarios
        
        Args:
            elements: List of extracted elements
            
        Returns:
            LLM analysis with test suggestions
        """
        
        # Prepare context for LLM
        element_summary = []
        for elem in elements[:20]:  # Limit to first 20 for token efficiency
            element_summary.append({
                'type': elem.get('tag_name'),
                'category': elem.get('category'),
                'description': elem.get('description'),
                'priority': elem.get('test_priority'),
                'interaction': elem.get('interaction_pattern')
            })
        
        prompt = f"""Analyze these UI elements and suggest test scenarios:

Elements:
{json.dumps(element_summary, indent=2)}

Please provide:
1. Critical user flows to test
2. Key validation scenarios
3. Edge cases to consider
4. Accessibility concerns
5. Security test recommendations

Format as JSON with these keys: critical_flows, validation_scenarios, edge_cases, accessibility_concerns, security_tests"""

        try:
            # Create messages format for LLM
            messages = [
                {"role": "system", "content": "You are a UI testing expert. Analyze the provided UI elements and suggest comprehensive test scenarios."},
                {"role": "user", "content": prompt}
            ]
            
            # Call LLM with correct parameters
            response = await asyncio.to_thread(
                query_llm,
                "gemini",  # provider
                "gemini-2.0-flash-exp",  # model
                messages  # messages
            )
            
            # Extract content from response
            if response and response.choices and response.choices[0].message.content:
                content = response.choices[0].message.content
                # Try to extract JSON from response
                try:
                    # Look for JSON in response
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                except:
                    pass
                    
                return {'raw_analysis': content}
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            
        return {}


async def extract_elements_from_url(url: str, headless: bool = False, analyze: bool = False) -> Dict[str, Any]:
    """Main function to extract elements from a URL
    
    Args:
        url: The URL to extract from
        headless: Whether to run browser in headless mode
        analyze: Whether to analyze with LLM
        
    Returns:
        Dictionary containing extracted elements and optional analysis
    """
    
    extractor = ElementExtractor(headless=headless)
    
    # Extract elements
    elements = await extractor.extract_elements(url)
    
    result = {
        'url': url,
        'timestamp': str(datetime.now()),
        'total_elements': len(elements),
        'elements': elements
    }
    
    # Categorize by type
    by_category = {}
    for elem in elements:
        cat = elem.get('category', 'unknown')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(elem)
    
    result['elements_by_category'] = by_category
    
    # Add LLM analysis if requested
    if analyze:
        logger.info("Analyzing with LLM...")
        analysis = await extractor.analyze_with_llm(elements)
        result['llm_analysis'] = analysis
    
    return result


# Example usage
if __name__ == "__main__":
    async def main():
        # Test with a simple website
        url = "https://example.com"
        
        print(f"Extracting elements from {url}...")
        result = await extract_elements_from_url(url, headless=False, analyze=True)
        
        print(f"\n✅ Extracted {result['total_elements']} elements")
        
        # Show category breakdown
        print("\nElements by category:")
        for category, elems in result.get('elements_by_category', {}).items():
            print(f"  {category}: {len(elems)} elements")
        
        # Show first few elements
        print("\nFirst 5 elements:")
        for i, elem in enumerate(result['elements'][:5], 1):
            print(f"\n{i}. {elem['description']}")
            print(f"   Category: {elem.get('category')}")
            print(f"   Priority: {elem.get('test_priority')}")
            print(f"   Interaction: {elem.get('interaction_pattern')}")
        
        # Show LLM analysis if available
        if 'llm_analysis' in result:
            print("\n📊 LLM Analysis:")
            print(json.dumps(result['llm_analysis'], indent=2))
        
        # Save to file
        output_file = "extracted_elements.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Results saved to {output_file}")
    
    asyncio.run(main())