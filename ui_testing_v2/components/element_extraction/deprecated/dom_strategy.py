"""
DOM Analysis Strategy - Advanced DOM traversal and element extraction
"""

import asyncio
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from playwright.async_api import ElementHandle, Locator, Page

from ..advanced_extractor import (
    ElementCandidate,
    ExtractionContext,
    ExtractionStrategy,
    ExtractionStrategyBase,
)

logger = logging.getLogger(__name__)


class DOMAnalysisStrategy(ExtractionStrategyBase):
    """
    Advanced DOM analysis strategy with intelligent selector generation
    and comprehensive element extraction
    """
    
    def __init__(self, config, ai_service_factory=None):
        super().__init__(config, ai_service_factory)
        
        # Selector generation preferences
        self.selector_preferences = [
            'data-testid',
            'data-test',
            'data-cy',
            'id',
            'aria-label',
            'name',
            'class',
            'type',
            'role'
        ]
        
        # Elements to always include
        self.important_selectors = [
            'button',
            'a[href]',
            'input:not([type="hidden"])',
            'textarea',
            'select',
            '[role="button"]',
            '[role="link"]',
            '[role="tab"]',
            '[role="menuitem"]',
            '[onclick]',
            '[ng-click]',
            '[v-on\\:click]',
            '[data-action]'
        ]
        
        # Elements to exclude
        self.exclude_selectors = [
            'script',
            'style',
            'noscript',
            'svg path',
            'svg line',
            'svg rect',
            'svg circle',
            'meta',
            'link'
        ]
        
        # Cookie consent selectors
        self.cookie_selectors = [
            'button:has-text("Accept")',
            'button:has-text("Accept all")',
            'button:has-text("Accept cookies")',
            'button:has-text("I agree")',
            'button:has-text("OK")',
            'button:has-text("Got it")',
            '[id*="cookie"] button',
            '[class*="cookie"] button',
            '[class*="consent"] button',
            '[class*="gdpr"] button',
            'button[id*="accept"]',
            'button[class*="accept"]'
        ]
    
    async def extract(self, context: ExtractionContext) -> List[ElementCandidate]:
        """Extract elements using advanced DOM analysis"""
        candidates = []
        
        try:
            # Phase 0: Handle cookie consent and popups
            await self._handle_cookie_consent(context.page)
            
            # Phase 1: Wait for page stability
            await self._wait_for_page_stability(context.page)
            
            # Phase 2: Extract all potentially important elements
            elements = await self._extract_all_elements(context)
            logger.info(f"DOM Strategy: Found {len(elements)} potential elements")
            
            # Phase 3: Analyze each element with error handling
            for element in elements:
                try:
                    candidate = await self._analyze_element(element, context)
                    if candidate:
                        candidates.append(candidate)
                except Exception as e:
                    logger.debug(f"Error analyzing element: {e}")
                    continue
            
            # Phase 4: Find dynamic elements
            dynamic_elements = await self._find_dynamic_elements(context)
            for element in dynamic_elements:
                try:
                    candidate = await self._analyze_element(element, context)
                    if candidate:
                        candidate.metadata['is_dynamic'] = True
                        candidates.append(candidate)
                except Exception as e:
                    logger.debug(f"Error analyzing dynamic element: {e}")
                    continue
            
            logger.info(f"DOM Strategy: Extracted {len(candidates)} valid candidates")
            return candidates
            
        except Exception as e:
            logger.error(f"DOM analysis failed: {e}")
            return candidates
    
    def get_confidence_boost(self) -> float:
        """DOM analysis is our primary strategy"""
        return 0.3
    
    async def _handle_cookie_consent(self, page: Page):
        """Handle cookie consent popups"""
        try:
            # Wait a bit for cookie banner to appear
            await page.wait_for_timeout(2000)
            
            # Try to find and click cookie consent
            for selector in self.cookie_selectors:
                try:
                    button = page.locator(selector).first
                    if await button.is_visible():
                        await button.click()
                        logger.info(f"Clicked cookie consent: {selector}")
                        await page.wait_for_timeout(1000)
                        break
                except:
                    continue
                    
        except Exception as e:
            logger.debug(f"Cookie consent handling: {e}")
    
    async def _wait_for_page_stability(self, page: Page):
        """Wait for page to become stable"""
        try:
            # Method 1: Wait for network idle with shorter timeout
            try:
                await page.wait_for_load_state('networkidle', timeout=10000)
            except:
                logger.debug("Network idle timeout, continuing...")
            
            # Method 2: Wait for DOM stability
            await page.evaluate("""
                () => {
                    return new Promise((resolve) => {
                        let lastHeight = document.body.scrollHeight;
                        let checks = 0;
                        const maxChecks = 10;
                        
                        const checkStability = setInterval(() => {
                            const currentHeight = document.body.scrollHeight;
                            checks++;
                            
                            if (currentHeight === lastHeight || checks >= maxChecks) {
                                clearInterval(checkStability);
                                resolve();
                            }
                            
                            lastHeight = currentHeight;
                        }, 500);
                    });
                }
            """)
            
        except Exception as e:
            logger.debug(f"Page stability wait: {e}")
    
    async def _extract_all_elements(self, context: ExtractionContext) -> List[ElementHandle]:
        """Extract all potentially important elements from the page"""
        elements = []
        
        # Build combined selector
        important_selector = ', '.join(self.important_selectors)
        
        # Get all elements matching our important selectors - query individually to handle errors
        for selector in self.important_selectors:
            try:
                selector_elements = await context.page.query_selector_all(selector)
                elements.extend(selector_elements)
            except Exception as e:
                logger.debug(f"Failed to query {selector}: {e}")
                continue
        
        # Also get all elements with event listeners
        try:
            event_elements = await context.page.evaluate_handle('''() => {
                const allElements = document.querySelectorAll('*');
                const elementsWithListeners = [];
                
                for (const element of allElements) {
                    // Check for inline event handlers
                    const attributes = element.attributes;
                    let hasEventHandler = false;
                    
                    for (let i = 0; i < attributes.length; i++) {
                        if (attributes[i].name.startsWith('on')) {
                            hasEventHandler = true;
                            break;
                        }
                    }
                    
                    // Check for addEventListener (this is approximate)
                    if (hasEventHandler || element.onclick || element.onchange || element.onsubmit) {
                        elementsWithListeners.push(element);
                    }
                }
                
                return elementsWithListeners;
            }''')
            
            # Check if we got an array of elements
            try:
                # Convert JSHandle array to ElementHandles properly
                event_elements_count = await event_elements.evaluate('els => els ? els.length : 0')
                if event_elements_count > 0:
                    # Get elements one by one
                    for i in range(min(event_elements_count, 100)):  # Limit to 100 event elements
                        try:
                            element_handle = await context.page.evaluate_handle(
                                f'document.querySelectorAll("*")[{i}]'
                            )
                            if element_handle:
                                elements.append(element_handle)
                        except:
                            pass
            except:
                logger.debug("Could not process event elements")
                        
        except Exception as e:
            logger.error(f"Failed to extract event elements: {e}")
        
        # Remove duplicates and excluded elements
        unique_elements = await self._filter_unique_elements(elements, context)
        
        return unique_elements
    
    async def _filter_unique_elements(
        self,
        elements: List[ElementHandle],
        context: ExtractionContext
    ) -> List[ElementHandle]:
        """Filter out duplicate and excluded elements"""
        unique_elements = []
        seen_positions = set()
        
        for element in elements:
            try:
                # Check if element should be excluded
                tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                if any(tag_name == excluded.lower() for excluded in self.exclude_selectors if '>' not in excluded and '[' not in excluded):
                    continue
                
                # Check position for deduplication
                box = await element.bounding_box()
                if box:
                    pos_key = (
                        round(box['x']),
                        round(box['y']),
                        round(box['width']),
                        round(box['height'])
                    )
                    if pos_key in seen_positions:
                        continue
                    seen_positions.add(pos_key)
                
                # Validate element
                if await self.validate_element(element):
                    unique_elements.append(element)
                    
            except Exception:
                continue
        
        return unique_elements
    
    async def _analyze_element(
        self,
        element: ElementHandle,
        context: ExtractionContext
    ) -> Optional[ElementCandidate]:
        """Analyze a single element and create a candidate"""
        try:
            # Get basic properties
            properties = await self._get_element_properties(element)
            if not properties:
                return None
            
            # Generate multiple selectors
            selectors = await self._generate_selectors(element, properties, context.page)
            if not selectors:
                return None
            
            # Calculate confidence based on selector quality
            confidence = self._calculate_selector_confidence(selectors, properties)
            
            # Create candidate
            candidate = ElementCandidate(
                element=element,
                confidence=confidence,
                strategies_used={ExtractionStrategy.DOM_ANALYSIS},
                attributes=properties['attributes'],
                selectors=selectors,
                metadata={
                    'tag_name': properties['tag_name'],
                    'text_content': properties['text'],
                    'is_visible': properties['is_visible'],
                    'has_event_handlers': properties['has_event_handlers'],
                    'computed_role': properties.get('computed_role'),
                    'stability_score': self._calculate_stability_score(selectors)
                }
            )
            
            return candidate
            
        except Exception as e:
            logger.debug(f"Failed to analyze element: {e}")
            return None
    
    async def _get_element_properties(self, element: ElementHandle) -> Optional[Dict[str, Any]]:
        """Get comprehensive properties of an element"""
        try:
            properties = await element.evaluate(r'''(element) => {
                // Get all attributes
                const attributes = {};
                for (const attr of element.attributes) {
                    attributes[attr.name] = attr.value;
                }
                
                // Check for event handlers
                let hasEventHandlers = false;
                for (const prop in element) {
                    if (prop.startsWith('on') && element[prop]) {
                        hasEventHandlers = true;
                        break;
                    }
                }
                
                // Get computed properties
                const computedStyle = window.getComputedStyle(element);
                const rect = element.getBoundingClientRect();
                
                return {
                    tag_name: element.tagName.toLowerCase(),
                    text: element.textContent?.trim() || '',
                    attributes: attributes,
                    is_visible: !!(rect.width && rect.height && computedStyle.visibility !== 'hidden' && computedStyle.display !== 'none'),
                    has_event_handlers: hasEventHandlers,
                    computed_role: element.getAttribute('role') || element.computedRole || null,
                    classes: element.className.split(/\s+/).filter(c => c),
                    is_focusable: element.tabIndex >= 0,
                    is_contenteditable: element.contentEditable === 'true',
                    nearest_label: element.labels?.[0]?.textContent || element.getAttribute('aria-label') || null
                };
            }''')
            
            return properties
            
        except Exception as e:
            logger.debug(f"Failed to get element properties: {e}")
            return None
    
    async def _generate_selectors(
        self,
        element: ElementHandle,
        properties: Dict[str, Any],
        page: Optional[Page] = None
    ) -> List[Dict[str, Any]]:
        """Generate multiple selector strategies for an element"""
        selectors = []
        
        # Strategy 1: ID selector
        if properties['attributes'].get('id'):
            element_id = properties['attributes']['id']
            if self._is_valid_id(element_id):
                selectors.append({
                    'type': 'css',
                    'value': f'#{element_id}',
                    'score': 1.0,
                    'strategy': 'id'
                })
                selectors.append({
                    'type': 'xpath',
                    'value': f'//*[@id="{element_id}"]',
                    'score': 0.95,
                    'strategy': 'id'
                })
        
        # Strategy 2: Data attributes
        for attr in ['data-testid', 'data-test', 'data-cy', 'data-id']:
            if attr in properties['attributes']:
                value = properties['attributes'][attr]
                selectors.append({
                    'type': 'css',
                    'value': f'[{attr}="{value}"]',
                    'score': 0.9,
                    'strategy': 'data-attribute'
                })
        
        # Strategy 3: Unique class combinations
        if properties.get('classes'):
            unique_classes = await self._find_unique_class_combination(element, properties['classes'])
            if unique_classes:
                selector = '.' + '.'.join(unique_classes)
                selectors.append({
                    'type': 'css',
                    'value': selector,
                    'score': 0.7,
                    'strategy': 'class'
                })
        
        # Strategy 4: ARIA attributes
        if properties['attributes'].get('aria-label'):
            aria_label = properties['attributes']['aria-label']
            selectors.append({
                'type': 'css',
                'value': f'[aria-label="{aria_label}"]',
                'score': 0.8,
                'strategy': 'aria'
            })
        
        # Strategy 5: Text content selector (for buttons and links)
        if properties['tag_name'] in ['button', 'a'] and properties['text']:
            text = properties['text'][:50]  # Limit text length
            selectors.append({
                'type': 'xpath',
                'value': f'//{properties["tag_name"]}[contains(text(), "{text}")]',
                'score': 0.6,
                'strategy': 'text'
            })
        
        # Strategy 6: Position-based selector (last resort)
        position_selector = await self._generate_position_selector(element)
        if position_selector:
            selectors.append(position_selector)
        
        # Verify each selector
        verified_selectors = []
        if page:
            for selector in selectors:
                if await self._verify_selector(selector, element, page):
                    verified_selectors.append(selector)
        else:
            # If no page provided, return all selectors without verification
            verified_selectors = selectors
        
        return verified_selectors
    
    def _is_valid_id(self, element_id: str) -> bool:
        """Check if ID is likely to be stable"""
        # Reject IDs that look auto-generated
        if re.match(r'^[a-f0-9]{8,}$', element_id.lower()):
            return False
        if re.match(r'^ember\d+$', element_id):
            return False
        if re.match(r'^react-select-\d+', element_id):
            return False
        if element_id.startswith('__'):
            return False
        return True
    
    async def _find_unique_class_combination(
        self,
        element: ElementHandle,
        classes: List[str]
    ) -> Optional[List[str]]:
        """Find minimal unique class combination"""
        if not classes:
            return None
        
        # Filter out common framework classes
        meaningful_classes = [
            cls for cls in classes
            if not any(pattern in cls for pattern in [
                'col-', 'row-', 'btn-', 'text-', 'bg-', 'is-', 'has-',
                'justify-', 'align-', 'flex-', 'grid-', 'p-', 'm-'
            ])
        ]
        
        if not meaningful_classes:
            meaningful_classes = classes[:2]  # Fallback to first 2 classes
        
        # Try combinations starting from most specific
        for i in range(min(3, len(meaningful_classes)), 0, -1):
            for j in range(len(meaningful_classes) - i + 1):
                combination = meaningful_classes[j:j+i]
                selector = '.' + '.'.join(combination)
                
                try:
                    # Check if selector is unique
                    count = await element.evaluate(f'''
                        (el) => document.querySelectorAll('{selector}').length
                    ''')
                    if count == 1:
                        return combination
                except:
                    continue
        
        return None
    
    async def _generate_position_selector(self, element: ElementHandle) -> Optional[Dict[str, Any]]:
        """Generate position-based selector as last resort"""
        try:
            selector = await element.evaluate('''(element) => {
                // Get element's position in parent
                const parent = element.parentElement;
                if (!parent) return null;
                
                const tagName = element.tagName.toLowerCase();
                const sameTagSiblings = Array.from(parent.children).filter(
                    child => child.tagName.toLowerCase() === tagName
                );
                
                const index = sameTagSiblings.indexOf(element);
                if (index === -1) return null;
                
                // Build parent path
                let parentPath = '';
                let currentParent = parent;
                let depth = 0;
                
                while (currentParent && depth < 3) {
                    const parentTag = currentParent.tagName.toLowerCase();
                    const parentId = currentParent.id;
                    
                    if (parentId) {
                        parentPath = `#${parentId} > ` + parentPath;
                        break;
                    } else {
                        parentPath = parentTag + ' > ' + parentPath;
                    }
                    
                    currentParent = currentParent.parentElement;
                    depth++;
                }
                
                return parentPath + tagName + ':nth-of-type(' + (index + 1) + ')';
            }''')
            
            if selector:
                return {
                    'type': 'css',
                    'value': selector,
                    'score': 0.3,
                    'strategy': 'position'
                }
                
        except Exception:
            pass
        
        return None
    
    async def _verify_selector(
        self,
        selector: Dict[str, Any],
        element: ElementHandle,
        page
    ) -> bool:
        """Verify that selector uniquely identifies the element"""
        try:
            if selector['type'] == 'css':
                elements = await page.query_selector_all(selector['value'])
                if len(elements) == 1:
                    # Verify it's the same element
                    is_same = await element.evaluate(
                        f'(el) => el === document.querySelector("{selector["value"]}")'
                    )
                    return is_same
            elif selector['type'] == 'xpath':
                # XPath verification is more complex, skip for now
                return True
                
        except Exception:
            pass
        
        return False
    
    def _calculate_selector_confidence(
        self,
        selectors: List[Dict[str, Any]],
        properties: Dict[str, Any]
    ) -> float:
        """Calculate confidence based on selector quality and element properties"""
        if not selectors:
            return 0.1
        
        # Base confidence from best selector
        best_score = max(selector['score'] for selector in selectors)
        confidence = best_score * 0.7
        
        # Boost for interactive elements
        if properties['tag_name'] in ['button', 'a', 'input', 'select', 'textarea']:
            confidence += 0.1
        
        # Boost for elements with event handlers
        if properties.get('has_event_handlers'):
            confidence += 0.1
        
        # Boost for visible elements
        if properties.get('is_visible'):
            confidence += 0.05
        
        # Boost for accessible elements
        if properties.get('computed_role') or properties.get('nearest_label'):
            confidence += 0.05
        
        return min(confidence, 0.95)
    
    def _calculate_stability_score(self, selectors: List[Dict[str, Any]]) -> float:
        """Calculate how stable the selectors are likely to be"""
        if not selectors:
            return 0.0
        
        stability_weights = {
            'id': 0.9,
            'data-attribute': 0.85,
            'aria': 0.8,
            'class': 0.6,
            'text': 0.4,
            'position': 0.2
        }
        
        total_score = 0
        total_weight = 0
        
        for selector in selectors:
            strategy = selector.get('strategy', 'position')
            weight = stability_weights.get(strategy, 0.1)
            total_score += selector['score'] * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    async def _find_dynamic_elements(self, context: ExtractionContext) -> List[ElementHandle]:
        """Find elements that might be dynamically created"""
        dynamic_elements = []
        
        try:
            # Look for common dynamic element patterns
            dynamic_selectors = [
                '[data-dynamic]',
                '[ng-repeat]',
                '[v-for]',
                '[*ngFor]',
                '.lazy-load',
                '.infinite-scroll-item',
                '[data-react-component]',
                '[data-vue-component]'
            ]
            
            for selector in dynamic_selectors:
                try:
                    elements = await context.page.query_selector_all(selector)
                    dynamic_elements.extend(elements)
                except:
                    continue
            
            # Also check for elements loaded after initial render
            await context.page.wait_for_timeout(500)  # Brief wait
            
            # Check for elements that appeared after wait
            late_elements = await context.page.evaluate('''() => {
                const allElements = document.querySelectorAll('button, a, input, [role="button"], [onclick]');
                const lateElements = [];
                
                for (const element of allElements) {
                    // Check if element was likely added dynamically
                    // (This is a heuristic - elements without IDs in dynamic areas)
                    if (!element.id && element.closest('[class*="modal"], [class*="popup"], [class*="dropdown"], [role="dialog"]')) {
                        lateElements.push(element);
                    }
                }
                
                return lateElements;
            }''')
            
            # Convert to element handles (limited number)
            # Note: This is a simplified approach - in production, we'd need proper handle conversion
            
        except Exception as e:
            logger.debug(f"Dynamic element detection error: {e}")
        
        return dynamic_elements