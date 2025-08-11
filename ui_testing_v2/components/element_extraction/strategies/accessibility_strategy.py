"""
Accessibility Mapping Strategy - Advanced ARIA and accessibility-focused extraction
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime
from playwright.async_api import ElementHandle, Page

from ..advanced_extractor import (
    ElementCandidate,
    ExtractionContext,
    ExtractionStrategy,
    ExtractionStrategyBase,
)

logger = logging.getLogger(__name__)


class AccessibilityMappingStrategy(ExtractionStrategyBase):
    """
    Extract elements with focus on accessibility features, ARIA attributes,
    and semantic HTML patterns that indicate interactive functionality
    """
    
    def __init__(self, config, ai_service_factory=None):
        super().__init__(config, ai_service_factory)
        
        # ARIA roles that indicate interactive elements
        self.interactive_roles = [
            'button', 'link', 'menuitem', 'menuitemcheckbox', 'menuitemradio',
            'option', 'radio', 'switch', 'tab', 'treeitem', 'checkbox',
            'gridcell', 'spinbutton', 'searchbox', 'slider', 'textbox',
            'combobox', 'listbox', 'navigation', 'toolbar', 'menu',
            'progressbar', 'scrollbar'
        ]
        
        # ARIA attributes that suggest interactivity
        self.interactive_aria_attrs = [
            'aria-controls', 'aria-expanded', 'aria-pressed', 'aria-checked',
            'aria-selected', 'aria-haspopup', 'aria-owns', 'aria-activedescendant',
            'aria-valuemin', 'aria-valuemax', 'aria-valuenow', 'aria-autocomplete',
            'aria-multiline', 'aria-multiselectable', 'aria-orientation'
        ]
        
        # Landmark roles for navigation
        self.landmark_roles = [
            'banner', 'complementary', 'contentinfo', 'form', 'main',
            'navigation', 'region', 'search'
        ]
        
        # Focus management attributes
        self.focus_attrs = [
            'tabindex', 'accesskey', 'contenteditable', 'draggable'
        ]
    
    async def extract(self, context: ExtractionContext) -> List[ElementCandidate]:
        """Extract elements based on accessibility features"""
        candidates = []
        
        try:
            # 1. Extract ARIA-labeled interactive elements
            aria_elements = await self._extract_aria_elements(context.page)
            logger.info(f"Accessibility Strategy: Found {len(aria_elements)} ARIA elements")
            
            # 2. Extract semantic HTML5 elements
            semantic_elements = await self._extract_semantic_elements(context.page)
            logger.info(f"Accessibility Strategy: Found {len(semantic_elements)} semantic elements")
            
            # 3. Extract form elements with labels
            form_elements = await self._extract_form_elements(context.page)
            logger.info(f"Accessibility Strategy: Found {len(form_elements)} form elements")
            
            # 4. Extract keyboard-navigable elements
            keyboard_elements = await self._extract_keyboard_navigable(context.page)
            logger.info(f"Accessibility Strategy: Found {len(keyboard_elements)} keyboard-navigable elements")
            
            # 5. Extract elements with focus indicators
            focus_elements = await self._extract_focus_managed(context.page)
            logger.info(f"Accessibility Strategy: Found {len(focus_elements)} focus-managed elements")
            
            # Combine all elements and remove duplicates
            all_elements = []
            seen_elements = set()
            
            for element_list in [aria_elements, semantic_elements, form_elements, 
                               keyboard_elements, focus_elements]:
                for element, metadata in element_list:
                    try:
                        # Use element handle as unique identifier
                        element_id = await element.evaluate('el => el.outerHTML.substring(0, 100)')
                        if element_id not in seen_elements:
                            seen_elements.add(element_id)
                            all_elements.append((element, metadata))
                    except:
                        all_elements.append((element, metadata))
            
            logger.info(f"Accessibility Strategy: Analyzing {len(all_elements)} unique elements")
            
            # Create candidates with accessibility scoring
            for element, metadata in all_elements:
                try:
                    candidate = await self._create_accessibility_candidate(
                        element, metadata, context
                    )
                    if candidate:
                        candidates.append(candidate)
                except Exception as e:
                    logger.debug(f"Failed to create candidate: {e}")
                    continue
            
            # Sort by accessibility score
            candidates.sort(key=lambda c: c.confidence, reverse=True)
            
            logger.info(f"Accessibility Strategy: Created {len(candidates)} candidates")
            return candidates
            
        except Exception as e:
            logger.error(f"Accessibility extraction failed: {e}")
            return candidates
    
    def get_confidence_boost(self) -> float:
        """Accessibility provides strong confidence boost"""
        return 0.20
    
    async def _extract_aria_elements(self, page: Page) -> List[Tuple[ElementHandle, Dict]]:
        """Extract elements with ARIA attributes"""
        elements = []
        
        try:
            # Query for elements with interactive ARIA roles
            role_selector = ', '.join([f'[role="{role}"]' for role in self.interactive_roles])
            aria_elements = await page.query_selector_all(role_selector)
            
            for element in aria_elements:
                try:
                    aria_data = await element.evaluate('''el => {
                        const attrs = {};
                        for (let attr of el.attributes) {
                            if (attr.name.startsWith('aria-')) {
                                attrs[attr.name] = attr.value;
                            }
                        }
                        return {
                            role: el.getAttribute('role'),
                            label: el.getAttribute('aria-label') || el.getAttribute('aria-labelledby'),
                            description: el.getAttribute('aria-description') || el.getAttribute('aria-describedby'),
                            attributes: attrs,
                            hasName: !!el.getAttribute('name'),
                            hasId: !!el.getAttribute('id')
                        };
                    }''')
                    
                    metadata = {
                        'source': 'aria_role',
                        'aria_data': aria_data,
                        'has_label': bool(aria_data.get('label')),
                        'accessibility_score': self._calculate_aria_score(aria_data)
                    }
                    
                    elements.append((element, metadata))
                    
                except Exception as e:
                    logger.debug(f"Failed to analyze ARIA element: {e}")
                    continue
            
            # Also get elements with any interactive ARIA attributes
            for attr in self.interactive_aria_attrs:
                attr_elements = await page.query_selector_all(f'[{attr}]')
                for element in attr_elements[:20]:  # Limit per attribute
                    try:
                        aria_data = await self._get_element_aria_data(element)
                        metadata = {
                            'source': 'aria_attribute',
                            'trigger_attribute': attr,
                            'aria_data': aria_data,
                            'accessibility_score': self._calculate_aria_score(aria_data)
                        }
                        elements.append((element, metadata))
                    except:
                        continue
                        
        except Exception as e:
            logger.error(f"Failed to extract ARIA elements: {e}")
        
        return elements
    
    async def _extract_semantic_elements(self, page: Page) -> List[Tuple[ElementHandle, Dict]]:
        """Extract semantic HTML5 elements"""
        elements = []
        
        semantic_selectors = [
            'nav a', 'nav button',           # Navigation links
            'header a', 'header button',      # Header actions
            'main button', 'main a',          # Main content actions
            'article a', 'article button',    # Article actions
            'section[role] a', 'section[role] button',  # Section with roles
            'aside a', 'aside button',        # Sidebar actions
            'footer a', 'footer button',      # Footer links
            'details summary',                # Expandable content
            'dialog button', 'dialog a',      # Dialog actions
            'menu li', 'menu button'          # Menu items
        ]
        
        try:
            for selector in semantic_selectors:
                semantic_elements = await page.query_selector_all(selector)
                
                for element in semantic_elements[:10]:  # Limit per type
                    try:
                        semantic_data = await element.evaluate('''el => {
                            const parent = el.closest('nav, header, main, article, section, aside, footer, dialog, menu');
                            return {
                                tag: el.tagName.toLowerCase(),
                                parentLandmark: parent ? parent.tagName.toLowerCase() : null,
                                parentRole: parent ? parent.getAttribute('role') : null,
                                text: el.textContent.trim().substring(0, 100),
                                hasHeading: !!el.closest('h1, h2, h3, h4, h5, h6')
                            };
                        }''')
                        
                        metadata = {
                            'source': 'semantic_html',
                            'semantic_context': semantic_data,
                            'accessibility_score': 0.7 if semantic_data['parentLandmark'] else 0.5
                        }
                        
                        elements.append((element, metadata))
                        
                    except Exception as e:
                        logger.debug(f"Failed to analyze semantic element: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Failed to extract semantic elements: {e}")
        
        return elements
    
    async def _extract_form_elements(self, page: Page) -> List[Tuple[ElementHandle, Dict]]:
        """Extract form elements with proper labels"""
        elements = []
        
        try:
            # Get all form controls
            form_elements = await page.query_selector_all('''
                input:not([type="hidden"]), 
                select, 
                textarea, 
                button[type="submit"], 
                button[type="button"],
                [role="textbox"],
                [role="combobox"],
                [role="spinbutton"]
            ''')
            
            for element in form_elements:
                try:
                    form_data = await element.evaluate('''el => {
                        // Find associated label
                        let label = null;
                        const id = el.id;
                        
                        if (id) {
                            const labelEl = document.querySelector(`label[for="${id}"]`);
                            if (labelEl) label = labelEl.textContent.trim();
                        }
                        
                        if (!label) {
                            const parentLabel = el.closest('label');
                            if (parentLabel) label = parentLabel.textContent.trim();
                        }
                        
                        // Check fieldset legend
                        const fieldset = el.closest('fieldset');
                        const legend = fieldset ? fieldset.querySelector('legend') : null;
                        
                        return {
                            type: el.type || el.tagName.toLowerCase(),
                            name: el.name,
                            id: el.id,
                            label: label,
                            placeholder: el.placeholder,
                            ariaLabel: el.getAttribute('aria-label'),
                            required: el.required || el.getAttribute('aria-required') === 'true',
                            disabled: el.disabled || el.getAttribute('aria-disabled') === 'true',
                            legend: legend ? legend.textContent.trim() : null,
                            form: el.form ? el.form.id || 'unnamed-form' : null
                        };
                    }''')
                    
                    # Skip if disabled
                    if form_data['disabled']:
                        continue
                    
                    has_label = bool(form_data['label'] or form_data['ariaLabel'] or 
                                   form_data['placeholder'])
                    
                    metadata = {
                        'source': 'form_element',
                        'form_data': form_data,
                        'has_label': has_label,
                        'accessibility_score': 0.9 if has_label else 0.4
                    }
                    
                    elements.append((element, metadata))
                    
                except Exception as e:
                    logger.debug(f"Failed to analyze form element: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to extract form elements: {e}")
        
        return elements
    
    async def _extract_keyboard_navigable(self, page: Page) -> List[Tuple[ElementHandle, Dict]]:
        """Extract keyboard-navigable elements"""
        elements = []
        
        try:
            # Get elements with explicit tabindex
            tabindex_elements = await page.query_selector_all('[tabindex]:not([tabindex="-1"])')
            
            for element in tabindex_elements:
                try:
                    keyboard_data = await element.evaluate('''el => {
                        const tabindex = el.getAttribute('tabindex');
                        const accesskey = el.getAttribute('accesskey');
                        
                        return {
                            tabindex: tabindex,
                            accesskey: accesskey,
                            tag: el.tagName.toLowerCase(),
                            isNaturallyFocusable: ['A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA'].includes(el.tagName),
                            hasKeyHandler: !!(el.onkeydown || el.onkeyup || el.onkeypress)
                        };
                    }''')
                    
                    metadata = {
                        'source': 'keyboard_navigable',
                        'keyboard_data': keyboard_data,
                        'accessibility_score': 0.8
                    }
                    
                    elements.append((element, metadata))
                    
                except Exception as e:
                    logger.debug(f"Failed to analyze keyboard element: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to extract keyboard elements: {e}")
        
        return elements
    
    async def _extract_focus_managed(self, page: Page) -> List[Tuple[ElementHandle, Dict]]:
        """Extract elements with focus management"""
        elements = []
        
        try:
            # Get elements that manage focus for other elements
            focus_managers = await page.query_selector_all('''
                [aria-controls],
                [aria-owns],
                [aria-activedescendant],
                [aria-flowto]
            ''')
            
            for element in focus_managers[:30]:  # Limit
                try:
                    focus_data = await element.evaluate('''el => {
                        return {
                            controls: el.getAttribute('aria-controls'),
                            owns: el.getAttribute('aria-owns'),
                            activeDescendant: el.getAttribute('aria-activedescendant'),
                            flowTo: el.getAttribute('aria-flowto'),
                            expanded: el.getAttribute('aria-expanded'),
                            popup: el.getAttribute('aria-haspopup')
                        };
                    }''')
                    
                    metadata = {
                        'source': 'focus_management',
                        'focus_data': focus_data,
                        'manages_focus': True,
                        'accessibility_score': 0.85
                    }
                    
                    elements.append((element, metadata))
                    
                except Exception as e:
                    logger.debug(f"Failed to analyze focus element: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to extract focus elements: {e}")
        
        return elements
    
    async def _get_element_aria_data(self, element: ElementHandle) -> Dict[str, Any]:
        """Get comprehensive ARIA data for an element"""
        return await element.evaluate('''el => {
            const aria = {};
            const attrs = el.attributes;
            
            for (let i = 0; i < attrs.length; i++) {
                if (attrs[i].name.startsWith('aria-')) {
                    aria[attrs[i].name] = attrs[i].value;
                }
            }
            
            return {
                role: el.getAttribute('role'),
                label: el.getAttribute('aria-label'),
                describedby: el.getAttribute('aria-describedby'),
                labelledby: el.getAttribute('aria-labelledby'),
                attributes: aria
            };
        }''')
    
    def _calculate_aria_score(self, aria_data: Dict[str, Any]) -> float:
        """Calculate accessibility score based on ARIA data"""
        score = 0.5  # Base score
        
        # Boost for role
        if aria_data.get('role') in self.interactive_roles:
            score += 0.2
        
        # Boost for labeling
        if aria_data.get('label') or aria_data.get('labelledby'):
            score += 0.15
        
        # Boost for description
        if aria_data.get('description') or aria_data.get('describedby'):
            score += 0.1
        
        # Boost for interactive attributes
        attrs = aria_data.get('attributes', {})
        interactive_count = sum(1 for attr in self.interactive_aria_attrs if attr in attrs)
        score += min(interactive_count * 0.05, 0.15)
        
        return min(score, 0.95)
    
    async def _create_accessibility_candidate(
        self,
        element: ElementHandle,
        metadata: Dict[str, Any],
        context: ExtractionContext
    ) -> Optional[ElementCandidate]:
        """Create candidate from accessibility analysis"""
        try:
            # Get element properties
            properties = await element.evaluate('''el => ({
                tag: el.tagName.toLowerCase(),
                text: el.textContent?.trim().substring(0, 200) || '',
                value: el.value || '',
                attributes: Array.from(el.attributes).reduce((acc, attr) => {
                    acc[attr.name] = attr.value;
                    return acc;
                }, {}),
                isVisible: el.offsetWidth > 0 && el.offsetHeight > 0,
                rect: el.getBoundingClientRect()
            })''')
            
            # Skip if not visible
            if not properties['isVisible']:
                return None
            
            # Generate selectors optimized for accessibility
            selectors = await self._generate_accessibility_selectors(element, properties, metadata)
            
            # Calculate final confidence
            base_confidence = metadata.get('accessibility_score', 0.5)
            
            # Boost for multiple accessibility indicators
            indicator_count = 0
            if metadata.get('has_label'):
                indicator_count += 1
            if metadata.get('manages_focus'):
                indicator_count += 1
            if 'aria_data' in metadata and metadata['aria_data'].get('role'):
                indicator_count += 1
            
            confidence = min(base_confidence + (indicator_count * 0.05), 0.95)
            
            candidate = ElementCandidate(
                element=element,
                confidence=confidence,
                strategies_used={ExtractionStrategy.ACCESSIBILITY_MAPPING},
                attributes=properties['attributes'],
                selectors=selectors,
                metadata={
                    'accessibility_source': metadata['source'],
                    'has_aria': 'aria_data' in metadata,
                    'has_label': metadata.get('has_label', False),
                    'manages_focus': metadata.get('manages_focus', False),
                    'accessibility_score': base_confidence,
                    'element_text': properties['text'][:50] if properties['text'] else None
                }
            )
            
            return candidate
            
        except Exception as e:
            logger.debug(f"Failed to create accessibility candidate: {e}")
            return None
    
    async def _generate_accessibility_selectors(
        self,
        element: ElementHandle,
        properties: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate selectors emphasizing accessibility attributes"""
        selectors = []
        attrs = properties['attributes']
        
        try:
            # ID selector (always preferred)
            if attrs.get('id'):
                selectors.append({
                    'type': 'css',
                    'value': f"#{attrs['id']}",
                    'score': 0.95,
                    'strategy': 'accessibility-id'
                })
            
            # ARIA label selector
            if attrs.get('aria-label'):
                selectors.append({
                    'type': 'css',
                    'value': f'[aria-label="{attrs["aria-label"]}"]',
                    'score': 0.9,
                    'strategy': 'accessibility-label'
                })
            
            # Role-based selector
            if attrs.get('role'):
                role_selector = f'[role="{attrs["role"]}"]'
                if properties['text']:
                    selectors.append({
                        'type': 'xpath',
                        'value': f'//*[@role="{attrs["role"]}"][contains(text(), "{properties["text"][:30]}")]',
                        'score': 0.8,
                        'strategy': 'accessibility-role-text'
                    })
                else:
                    selectors.append({
                        'type': 'css',
                        'value': role_selector,
                        'score': 0.7,
                        'strategy': 'accessibility-role'
                    })
            
            # Form element with name
            if attrs.get('name') and properties['tag'] in ['input', 'select', 'textarea']:
                selectors.append({
                    'type': 'css',
                    'value': f'{properties["tag"]}[name="{attrs["name"]}"]',
                    'score': 0.85,
                    'strategy': 'accessibility-form-name'
                })
            
            # Accessible name from text
            if properties['text'] and properties['tag'] in ['button', 'a']:
                selectors.append({
                    'type': 'xpath',
                    'value': f'//{properties["tag"]}[normalize-space(text())="{properties["text"][:50]}"]',
                    'score': 0.6,
                    'strategy': 'accessibility-text'
                })
                    
        except Exception as e:
            logger.debug(f"Failed to generate accessibility selectors: {e}")
        
        return selectors