"""
Element Extractor v2 - Pure Element Extraction
Receives browser session from Browser Manager
Contract: ExtractContract -> ElementResult
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from playwright.async_api import Page

# Import ALL types from centralized data_types_v2
from data_types_v2 import (
    ExtractContract,
    ElementResult,
    Element,
    ElementType,
    ElementSelector,
    ExtractionConfig,
    validate_ascii,
    SystemConstants
)


class ElementExtractorV2:
    """
    Pure element extraction - no browser management
    Takes browser session and extracts elements
    """

    def __init__(self):
        self.extracted_elements: List[Element] = []
        self.element_tree: Dict[str, Any] = {}

    async def execute(self, contract: ExtractContract, page: Page) -> ElementResult:
        """
        Main execution function - implements the contract
        Args:
            contract: ExtractContract with browser session
            page: Playwright page object from browser manager
        Returns:
            ElementResult with extracted elements
        """
        start_time = time.time()

        # Wait for page stability (skip for sites with continuous network activity)
        if contract.config.wait_for_network:
            try:
                await page.wait_for_load_state('domcontentloaded', timeout=5000)
            except:
                pass  # Continue even if timeout

        # Extract elements based on configuration
        elements = await self._extract_all_elements(page, contract.config)

        # Filter based on contract specifications
        if contract.target_elements:
            elements = self._filter_target_elements(elements, contract.target_elements)

        if contract.exclude_selectors:
            elements = self._exclude_elements(elements, contract.exclude_selectors)

        # Build element tree
        element_tree = self._build_element_tree(elements)

        # Calculate metrics
        interactive_count = sum(
            1 for e in elements
            if e.is_clickable or e.is_editable or e.is_focusable
        )

        return ElementResult(
            url=validate_ascii(page.url),
            total_elements=len(elements),
            interactive_elements=interactive_count,
            elements=elements[:contract.config.max_elements],
            element_tree=element_tree,
            extraction_time=time.time() - start_time,
            metadata={
                'viewport': page.viewport_size,
                'title': validate_ascii(await page.title()),
                'extraction_strategy': contract.config.selectors_strategy
            }
        )

    async def _extract_all_elements(self, page: Page, config: ExtractionConfig) -> List[Element]:
        """Extract all elements from the page"""
        elements = []

        # JavaScript to extract element information
        extraction_script = """
        () => {
            const elements = [];
            const allElements = document.querySelectorAll('*');

            for (const elem of allElements) {
                const rect = elem.getBoundingClientRect();
                const styles = window.getComputedStyle(elem);

                // Skip invisible elements unless configured
                if (!%s && (rect.width === 0 || rect.height === 0 ||
                    styles.display === 'none' || styles.visibility === 'hidden')) {
                    continue;
                }

                // Build element data
                const elemData = {
                    tagName: elem.tagName.toLowerCase(),
                    id: elem.id || null,
                    className: elem.className || null,
                    textContent: elem.textContent?.substring(0, 200) || null,
                    attributes: {},
                    isVisible: rect.width > 0 && rect.height > 0,
                    isClickable: elem.onclick || elem.tagName === 'BUTTON' ||
                                 elem.tagName === 'A' || elem.role === 'button',
                    isEditable: elem.contentEditable === 'true' ||
                               elem.tagName === 'INPUT' || elem.tagName === 'TEXTAREA',
                    isFocusable: elem.tabIndex >= 0,
                    boundingBox: {
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height
                    }
                };

                // Add key attributes
                ['href', 'src', 'type', 'name', 'value', 'placeholder', 'aria-label', 'role', 'data-testid'].forEach(attr => {
                    if (elem.hasAttribute(attr)) {
                        elemData.attributes[attr] = elem.getAttribute(attr);
                    }
                });

                elements.push(elemData);
            }

            return elements;
        }
        """ % str(config.include_invisible).lower()

        # Execute extraction
        raw_elements = await page.evaluate(extraction_script)

        # Convert to Element objects
        for raw_elem in raw_elements:
            element = Element(
                tag_name=validate_ascii(raw_elem['tagName']),
                element_type=self._determine_element_type(raw_elem),
                selectors=self._build_selectors(raw_elem),
                text_content=validate_ascii(raw_elem.get('textContent', '')),
                attributes={k: validate_ascii(str(v)) for k, v in raw_elem.get('attributes', {}).items()},
                is_visible=raw_elem['isVisible'],
                is_clickable=raw_elem['isClickable'],
                is_editable=raw_elem['isEditable'],
                is_focusable=raw_elem['isFocusable'],
                bounding_box=raw_elem['boundingBox'],
                parent_selector=None,
                children_count=0
            )
            elements.append(element)

        # Handle iframes if configured
        if config.include_iframes:
            iframe_elements = await self._extract_iframe_elements(page)
            elements.extend(iframe_elements)

        # Handle shadow DOM if configured
        if config.include_shadow_dom:
            shadow_elements = await self._extract_shadow_dom_elements(page)
            elements.extend(shadow_elements)

        return elements

    def _determine_element_type(self, raw_elem: Dict[str, Any]) -> ElementType:
        """Determine the type of element"""
        tag = raw_elem['tagName'].lower()
        elem_type = raw_elem.get('attributes', {}).get('type', '')

        if tag == 'button':
            return ElementType.BUTTON
        elif tag == 'a':
            return ElementType.LINK
        elif tag == 'input':
            if elem_type == 'checkbox':
                return ElementType.CHECKBOX
            elif elem_type == 'radio':
                return ElementType.RADIO
            else:
                return ElementType.INPUT
        elif tag == 'select':
            return ElementType.SELECT
        elif tag == 'textarea':
            return ElementType.TEXTAREA
        elif tag == 'img':
            return ElementType.IMAGE
        elif tag == 'video':
            return ElementType.VIDEO
        elif tag == 'form':
            return ElementType.FORM
        elif tag == 'nav':
            return ElementType.NAVIGATION
        elif tag == 'header':
            return ElementType.HEADER
        elif tag == 'footer':
            return ElementType.FOOTER
        elif tag == 'div':
            return ElementType.DIV
        elif tag == 'span':
            return ElementType.SPAN
        else:
            return ElementType.UNKNOWN

    def _build_selectors(self, raw_elem: Dict[str, Any]) -> ElementSelector:
        """Build multiple selector strategies for an element"""
        selectors = ElementSelector()

        # ID selector
        if raw_elem.get('id'):
            selectors.id = raw_elem['id']
            selectors.css = f"#{raw_elem['id']}"

        # Class selector
        elif raw_elem.get('className'):
            classes = raw_elem['className'].split()
            if classes:
                selectors.css = f".{'.'.join(classes)}"

        # Data-testid selector
        if raw_elem.get('attributes', {}).get('data-testid'):
            selectors.data_testid = raw_elem['attributes']['data-testid']
            selectors.css = f"[data-testid='{raw_elem['attributes']['data-testid']}']"

        # Accessibility selector
        if raw_elem.get('attributes', {}).get('aria-label'):
            selectors.accessibility = raw_elem['attributes']['aria-label']

        # Text selector for links and buttons
        if raw_elem.get('textContent') and raw_elem['tagName'] in ['a', 'button']:
            selectors.text = raw_elem['textContent'][:50]

        # XPath as fallback
        selectors.xpath = f"//{raw_elem['tagName']}"

        return selectors

    async def _extract_iframe_elements(self, page: Page) -> List[Element]:
        """Extract elements from iframes"""
        elements = []
        frames = page.frames

        for frame in frames[1:]:  # Skip main frame
            try:
                # Extract from each iframe
                iframe_elements = await self._extract_all_elements(
                    frame,
                    ExtractionConfig(include_iframes=False)
                )
                elements.extend(iframe_elements)
            except:
                pass  # Skip inaccessible iframes

        return elements

    async def _extract_shadow_dom_elements(self, page: Page) -> List[Element]:
        """Extract elements from shadow DOM"""
        shadow_script = """
        () => {
            const elements = [];
            const shadows = document.querySelectorAll('*');

            for (const elem of shadows) {
                if (elem.shadowRoot) {
                    const shadowElements = elem.shadowRoot.querySelectorAll('*');
                    shadowElements.forEach(shadowElem => {
                        elements.push({
                            tagName: shadowElem.tagName.toLowerCase(),
                            textContent: shadowElem.textContent?.substring(0, 200) || null,
                            attributes: {},
                            isVisible: true,
                            isClickable: false,
                            isEditable: false,
                            isFocusable: false,
                            boundingBox: {x: 0, y: 0, width: 0, height: 0}
                        });
                    });
                }
            }

            return elements;
        }
        """

        try:
            raw_shadow_elements = await page.evaluate(shadow_script)
            shadow_elements = []

            for raw_elem in raw_shadow_elements:
                element = Element(
                    tag_name=validate_ascii(raw_elem['tagName']),
                    element_type=ElementType.UNKNOWN,
                    selectors=ElementSelector(),
                    text_content=validate_ascii(raw_elem.get('textContent', '')),
                    attributes={},
                    is_visible=True,
                    is_clickable=False,
                    is_editable=False,
                    is_focusable=False,
                    bounding_box=None,
                    parent_selector="shadow-root",
                    children_count=0
                )
                shadow_elements.append(element)

            return shadow_elements
        except:
            return []

    def _filter_target_elements(self, elements: List[Element], targets: List[str]) -> List[Element]:
        """Filter elements to only include targets"""
        filtered = []
        for element in elements:
            for target in targets:
                if (element.selectors.css == target or
                    element.selectors.id == target or
                    element.selectors.data_testid == target):
                    filtered.append(element)
                    break
        return filtered

    def _exclude_elements(self, elements: List[Element], excludes: List[str]) -> List[Element]:
        """Exclude elements matching selectors"""
        filtered = []
        for element in elements:
            exclude = False
            for exclude_selector in excludes:
                if (element.selectors.css == exclude_selector or
                    element.selectors.id == exclude_selector):
                    exclude = True
                    break
            if not exclude:
                filtered.append(element)
        return filtered

    def _build_element_tree(self, elements: List[Element]) -> Dict[str, Any]:
        """Build hierarchical tree of elements"""
        tree = {
            'root': {
                'tag': 'document',
                'children': [],
                'element_count': len(elements)
            }
        }

        # Group by tag name for summary
        tag_counts = {}
        for element in elements:
            tag = element.tag_name
            if tag not in tag_counts:
                tag_counts[tag] = 0
            tag_counts[tag] += 1

        tree['tag_distribution'] = tag_counts
        tree['interactive_elements'] = sum(
            1 for e in elements if e.is_clickable or e.is_editable
        )

        return tree


# ==============================================================================
# MAIN EXECUTION FUNCTION - Contract Implementation
# ==============================================================================

async def execute(contract: ExtractContract, page: Page) -> ElementResult:
    """
    Main module execution function
    Args:
        contract: Input contract
        page: Page object from browser manager
    Returns:
        ElementResult according to output contract
    """
    extractor = ElementExtractorV2()
    return await extractor.execute(contract, page)


# ==============================================================================
# TEST
# ==============================================================================

async def test():
    """Test the element extractor"""
    print("Testing Element Extractor v2...")

    # This would normally receive a page from browser manager
    # For testing, we'll create a mock

    from data_types_v2 import ExtractionConfig

    contract = ExtractContract(
        browser_session="mock_session_123",
        config=ExtractionConfig(
            max_elements=100,
            include_invisible=False,
            include_iframes=True
        )
    )

    print("Element Extractor ready for integration with Browser Manager")
    print("Contract created successfully!")


if __name__ == "__main__":
    asyncio.run(test())