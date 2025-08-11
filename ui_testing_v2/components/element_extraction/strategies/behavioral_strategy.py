"""
Behavioral Analysis Strategy - Advanced analysis of element behavior and user interactions
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


class BehavioralAnalysisStrategy(ExtractionStrategyBase):
    """
    Analyze element behavior patterns, user interactions, and UI feedback
    to identify truly interactive elements
    """
    
    def __init__(self, config, ai_service_factory=None):
        super().__init__(config, ai_service_factory)
        
        # Behavioral patterns to analyze
        self.behavior_patterns = {
            'hover_effects': {
                'cursor_change': ['pointer', 'hand', 'grab', 'text'],
                'style_changes': ['background', 'color', 'transform', 'opacity'],
                'tooltip_display': True,
                'underline_text': True
            },
            'click_feedback': {
                'visual_feedback': ['ripple', 'flash', 'scale', 'color'],
                'state_change': ['disabled', 'loading', 'success', 'error'],
                'navigation': True,
                'modal_trigger': True
            },
            'focus_behavior': {
                'keyboard_accessible': True,
                'focus_ring': True,
                'tab_order': True,
                'aria_states': True
            },
            'interaction_patterns': {
                'double_click': False,
                'right_click': False,
                'drag_drop': False,
                'long_press': False
            }
        }
        
        # Scoring weights for different behaviors
        self.behavior_weights = {
            'cursor_pointer': 0.3,
            'hover_effect': 0.2,
            'click_handler': 0.25,
            'keyboard_accessible': 0.15,
            'aria_interactive': 0.1
        }
    
    async def extract(self, context: ExtractionContext) -> List[ElementCandidate]:
        """Extract elements based on behavioral analysis"""
        candidates = []
        
        try:
            # Get all potentially interactive elements
            potential_elements = await self._get_potential_elements(context.page)
            logger.info(f"Behavioral Strategy: Analyzing {len(potential_elements)} potential elements")
            
            # Analyze each element's behavior
            for element in potential_elements:
                try:
                    behavior_score = await self._analyze_element_behavior(element, context.page)
                    
                    if behavior_score['total_score'] > 0.5:
                        candidate = await self._create_behavioral_candidate(
                            element,
                            behavior_score,
                            context
                        )
                        if candidate:
                            candidates.append(candidate)
                            
                except Exception as e:
                    logger.debug(f"Failed to analyze element behavior: {e}")
                    continue
            
            # Skip interaction testing in batch mode to improve performance
            # Only test top 3 candidates if there are many elements
            if len(candidates) > 20:
                top_candidates = sorted(candidates, key=lambda c: c.confidence, reverse=True)[:3]
            else:
                top_candidates = sorted(candidates, key=lambda c: c.confidence, reverse=True)[:5]
            
            for candidate in top_candidates:
                try:
                    interaction_score = await self._test_interaction(candidate.element, context.page)
                    if interaction_score > 0:
                        candidate.confidence = min(candidate.confidence + interaction_score * 0.1, 0.95)
                        candidate.metadata['interaction_tested'] = True
                except Exception:
                    continue
            
            logger.info(f"Behavioral Strategy: Found {len(candidates)} behaviorally interactive elements")
            return candidates
            
        except Exception as e:
            logger.error(f"Behavioral analysis failed: {e}")
            return candidates
    
    def get_confidence_boost(self) -> float:
        """Behavioral analysis provides good confidence boost"""
        return 0.15
    
    async def _get_potential_elements(self, page: Page) -> List[ElementHandle]:
        """Get all potentially interactive elements for analysis"""
        try:
            # Query for common interactive elements and those with event attributes
            elements = await page.query_selector_all('''
                button, a, input, select, textarea,
                [role="button"], [role="link"], [role="tab"], [role="menuitem"],
                [onclick], [onmouseover], [onmousedown], [onkeydown],
                [tabindex]:not([tabindex="-1"]),
                [contenteditable="true"],
                label[for], summary,
                .btn, .button, .link, .clickable,
                [class*="click"], [class*="button"], [class*="link"]
            ''')
            
            # Filter out hidden elements
            visible_elements = []
            for element in elements:
                is_visible = await element.evaluate('''el => {
                    const rect = el.getBoundingClientRect();
                    const style = getComputedStyle(el);
                    return rect.width > 0 && rect.height > 0 && 
                           style.visibility !== 'hidden' &&
                           style.display !== 'none' &&
                           style.opacity !== '0';
                }''')
                
                if is_visible:
                    visible_elements.append(element)
            
            return visible_elements[:50]  # Limit for performance
            
        except Exception as e:
            logger.error(f"Failed to get potential elements: {e}")
            return []
    
    async def _analyze_element_behavior(self, element: ElementHandle, page: Page) -> Dict[str, Any]:
        """Analyze various behavioral aspects of an element"""
        behavior_score = {
            'cursor_pointer': 0,
            'hover_effect': 0,
            'click_handler': 0,
            'keyboard_accessible': 0,
            'aria_interactive': 0,
            'total_score': 0,
            'behaviors_detected': []
        }
        
        try:
            # 1. Check cursor style
            cursor_check = await element.evaluate('''el => {
                const computed = getComputedStyle(el);
                const cursor = computed.cursor;
                
                // Check element and parent cursor styles
                let hasCursorPointer = cursor === 'pointer';
                let parent = el.parentElement;
                while (!hasCursorPointer && parent && parent !== document.body) {
                    if (getComputedStyle(parent).cursor === 'pointer') {
                        hasCursorPointer = true;
                    }
                    parent = parent.parentElement;
                }
                
                return {
                    cursor: cursor,
                    isPointer: hasCursorPointer,
                    isText: cursor === 'text',
                    isCustom: cursor.includes('url(')
                };
            }''')
            
            if cursor_check['isPointer']:
                behavior_score['cursor_pointer'] = 1.0
                behavior_score['behaviors_detected'].append('cursor_pointer')
            
            # 2. Check for hover effects
            hover_check = await self._check_hover_effects(element, page)
            if hover_check['has_hover_effect']:
                behavior_score['hover_effect'] = hover_check['score']
                behavior_score['behaviors_detected'].extend(hover_check['effects'])
            
            # 3. Check for event handlers
            event_check = await element.evaluate('''el => {
                const hasOnclick = !!(el.onclick || el.getAttribute('onclick'));
                const hasEventListeners = el.getEventListeners ? 
                    Object.keys(el.getEventListeners()).length > 0 : false;
                
                // Check for framework-specific handlers
                const hasNgClick = el.hasAttribute('ng-click');
                const hasVueClick = el.hasAttribute('v-on:click') || el.hasAttribute('@click');
                const hasReactClick = Object.keys(el).some(key => key.startsWith('__reactEventHandlers'));
                
                // Check parent elements for delegated handlers
                let hasParentHandler = false;
                let parent = el.parentElement;
                while (!hasParentHandler && parent && parent !== document.body) {
                    if (parent.onclick || parent.getAttribute('onclick')) {
                        hasParentHandler = true;
                    }
                    parent = parent.parentElement;
                }
                
                return {
                    hasDirectHandler: hasOnclick || hasEventListeners,
                    hasFrameworkHandler: hasNgClick || hasVueClick || hasReactClick,
                    hasParentHandler: hasParentHandler,
                    handlerTypes: []
                };
            }''')
            
            if (event_check['hasDirectHandler'] or event_check['hasFrameworkHandler'] or 
                event_check['hasParentHandler']):
                behavior_score['click_handler'] = 1.0
                behavior_score['behaviors_detected'].append('click_handler')
            
            # 4. Check keyboard accessibility
            keyboard_check = await element.evaluate('''el => {
                const tabindex = el.getAttribute('tabindex');
                const isNaturallyFocusable = ['A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA'].includes(el.tagName);
                const hasTabindex = tabindex !== null && tabindex !== '-1';
                const hasKeyHandler = !!(el.onkeydown || el.onkeyup || el.onkeypress ||
                                       el.getAttribute('onkeydown') || el.getAttribute('onkeyup'));
                
                return {
                    isFocusable: isNaturallyFocusable || hasTabindex,
                    tabindex: tabindex,
                    hasKeyHandler: hasKeyHandler
                };
            }''')
            
            if keyboard_check['isFocusable']:
                behavior_score['keyboard_accessible'] = 1.0
                behavior_score['behaviors_detected'].append('keyboard_accessible')
            
            # 5. Check ARIA attributes
            aria_check = await element.evaluate('''el => {
                const role = el.getAttribute('role');
                const ariaLabel = el.getAttribute('aria-label');
                const ariaPressed = el.getAttribute('aria-pressed');
                const ariaExpanded = el.getAttribute('aria-expanded');
                const ariaControls = el.getAttribute('aria-controls');
                
                const interactiveRoles = ['button', 'link', 'tab', 'menuitem', 'checkbox', 
                                        'radio', 'switch', 'slider', 'option'];
                
                return {
                    role: role,
                    isInteractiveRole: interactiveRoles.includes(role),
                    hasAriaLabel: !!ariaLabel,
                    hasAriaStates: !!(ariaPressed || ariaExpanded),
                    hasAriaControls: !!ariaControls
                };
            }''')
            
            if (aria_check['isInteractiveRole'] or aria_check['hasAriaStates'] or 
                aria_check['hasAriaControls']):
                behavior_score['aria_interactive'] = 1.0
                behavior_score['behaviors_detected'].append('aria_interactive')
            
            # Calculate total score
            total_score = 0
            for behavior, weight in self.behavior_weights.items():
                total_score += behavior_score.get(behavior, 0) * weight
            
            behavior_score['total_score'] = total_score
            
        except Exception as e:
            logger.debug(f"Failed to analyze element behavior: {e}")
        
        return behavior_score
    
    async def _check_hover_effects(self, element: ElementHandle, page: Page) -> Dict[str, Any]:
        """Check if element has hover effects using CSS analysis (faster)"""
        hover_result = {
            'has_hover_effect': False,
            'score': 0,
            'effects': []
        }
        
        try:
            # Use CSS analysis instead of actual hovering for speed
            hover_check = await element.evaluate('''el => {
                // Check if element or ancestors have :hover pseudo-class styles
                const hasHoverStyles = (elem) => {
                    try {
                        const sheets = document.styleSheets;
                        for (let sheet of sheets) {
                            try {
                                const rules = sheet.cssRules || sheet.rules;
                                for (let rule of rules) {
                                    if (rule.selectorText && rule.selectorText.includes(':hover')) {
                                        // Simple check if this hover rule might apply to element
                                        try {
                                            if (elem.matches(rule.selectorText.replace(':hover', ''))) {
                                                return true;
                                            }
                                        } catch (e) {}
                                    }
                                }
                            } catch (e) {}
                        }
                    } catch (e) {}
                    return false;
                };
                
                // Check element and parents
                let current = el;
                while (current && current !== document.body) {
                    if (hasHoverStyles(current)) return true;
                    current = current.parentElement;
                }
                
                // Check common hover indicators
                const classes = el.className.split(' ');
                const hasHoverClass = classes.some(c => 
                    c.includes('hover') || c.includes('over')
                );
                
                return hasHoverStyles(el) || hasHoverClass;
            }''')
            
            if hover_check:
                hover_result['has_hover_effect'] = True
                hover_result['score'] = 0.7
                hover_result['effects'] = ['css_hover_rule']
                
        except Exception as e:
            logger.debug(f"Failed to check hover effects: {e}")
        
        return hover_result
    
    async def _test_interaction(self, element: ElementHandle, page: Page) -> float:
        """Test actual interaction with the element"""
        interaction_score = 0
        
        try:
            # Store current URL and page state
            initial_url = page.url
            initial_dom_count = await page.evaluate('document.querySelectorAll("*").length')
            
            # Set up listeners for various events
            await page.evaluate('''() => {
                window.__interactionEvents = [];
                const events = ['click', 'focus', 'blur', 'change', 'submit'];
                events.forEach(eventType => {
                    document.addEventListener(eventType, (e) => {
                        window.__interactionEvents.push({
                            type: eventType,
                            target: e.target.tagName,
                            timestamp: Date.now()
                        });
                    }, true);
                });
            }''')
            
            # Try clicking the element
            try:
                await element.click(timeout=1000)
                await page.wait_for_timeout(500)
                
                # Check for interaction effects
                events_triggered = await page.evaluate('window.__interactionEvents || []')
                current_url = page.url
                current_dom_count = await page.evaluate('document.querySelectorAll("*").length')
                
                # Score based on effects
                if len(events_triggered) > 0:
                    interaction_score += 0.3
                
                if current_url != initial_url:
                    interaction_score += 0.4  # Navigation occurred
                
                if abs(current_dom_count - initial_dom_count) > 10:
                    interaction_score += 0.3  # Significant DOM change
                    
            except Exception:
                # Element might not be clickable, but that's okay
                pass
            
            # Clean up
            await page.evaluate('delete window.__interactionEvents')
            
        except Exception as e:
            logger.debug(f"Failed to test interaction: {e}")
        
        return interaction_score
    
    async def _create_behavioral_candidate(
        self,
        element: ElementHandle,
        behavior_score: Dict[str, Any],
        context: ExtractionContext
    ) -> Optional[ElementCandidate]:
        """Create candidate from behavioral analysis"""
        try:
            # Get element properties
            properties = await element.evaluate('''el => ({
                tag: el.tagName.toLowerCase(),
                text: el.textContent?.trim() || '',
                attributes: Array.from(el.attributes).reduce((acc, attr) => {
                    acc[attr.name] = attr.value;
                    return acc;
                }, {}),
                isLink: el.tagName === 'A' && !!el.href,
                isButton: el.tagName === 'BUTTON' || el.getAttribute('role') === 'button',
                isInput: ['INPUT', 'SELECT', 'TEXTAREA'].includes(el.tagName)
            })''')
            
            # Generate selectors based on behavioral context
            selectors = await self._generate_behavioral_selectors(element, properties, behavior_score)
            
            # Calculate confidence based on behavior score and element type
            base_confidence = behavior_score['total_score']
            
            # Boost for certain element types
            if properties['isButton'] or properties['isLink']:
                base_confidence = min(base_confidence + 0.1, 0.95)
            
            # Boost for multiple behaviors
            if len(behavior_score['behaviors_detected']) >= 3:
                base_confidence = min(base_confidence + 0.05, 0.95)
            
            candidate = ElementCandidate(
                element=element,
                confidence=base_confidence,
                strategies_used={ExtractionStrategy.BEHAVIORAL_ANALYSIS},
                attributes=properties['attributes'],
                selectors=selectors,
                metadata={
                    'behavior_score': behavior_score['total_score'],
                    'behaviors_detected': behavior_score['behaviors_detected'],
                    'element_type': self._determine_element_type(properties, behavior_score),
                    'interaction_tested': False
                }
            )
            
            return candidate
            
        except Exception as e:
            logger.debug(f"Failed to create behavioral candidate: {e}")
            return None
    
    async def _generate_behavioral_selectors(
        self,
        element: ElementHandle,
        properties: Dict[str, Any],
        behavior_score: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate selectors emphasizing behavioral attributes"""
        selectors = []
        attrs = properties['attributes']
        
        try:
            # ID selector (always preferred)
            if attrs.get('id'):
                selectors.append({
                    'type': 'css',
                    'value': f"#{attrs['id']}",
                    'score': 0.95,
                    'strategy': 'behavioral-id'
                })
            
            # Behavioral attribute selectors
            if 'click_handler' in behavior_score['behaviors_detected']:
                if attrs.get('onclick'):
                    selectors.append({
                        'type': 'css',
                        'value': f"{properties['tag']}[onclick]",
                        'score': 0.7,
                        'strategy': 'behavioral-onclick'
                    })
            
            # ARIA-based selectors
            if 'aria_interactive' in behavior_score['behaviors_detected']:
                if attrs.get('role'):
                    selectors.append({
                        'type': 'css',
                        'value': f"[role='{attrs['role']}']",
                        'score': 0.8,
                        'strategy': 'behavioral-role'
                    })
                if attrs.get('aria-label'):
                    selectors.append({
                        'type': 'css',
                        'value': f"[aria-label='{attrs['aria-label']}']",
                        'score': 0.85,
                        'strategy': 'behavioral-aria'
                    })
            
            # Text-based selector for buttons/links with good behavior
            if properties['text'] and behavior_score['total_score'] > 0.7:
                if properties['isButton'] or properties['isLink']:
                    selectors.append({
                        'type': 'xpath',
                        'value': f"//{properties['tag']}[contains(text(), '{properties['text'][:30]}')]",
                        'score': 0.6,
                        'strategy': 'behavioral-text'
                    })
            
            # Class-based selector emphasizing interactive classes
            if attrs.get('class'):
                classes = attrs['class'].split()
                interactive_classes = [c for c in classes if any(
                    keyword in c.lower() for keyword in ['btn', 'button', 'link', 'click']
                )]
                if interactive_classes:
                    selectors.append({
                        'type': 'css',
                        'value': f".{interactive_classes[0]}",
                        'score': 0.5,
                        'strategy': 'behavioral-class'
                    })
                    
        except Exception as e:
            logger.debug(f"Failed to generate behavioral selectors: {e}")
        
        return selectors
    
    def _determine_element_type(self, properties: Dict[str, Any], behavior_score: Dict[str, Any]) -> str:
        """Determine element type based on properties and behavior"""
        behaviors = behavior_score['behaviors_detected']
        
        if properties['isButton']:
            return 'button'
        elif properties['isLink']:
            return 'link'
        elif properties['isInput']:
            return 'input'
        elif 'aria_interactive' in behaviors:
            role = properties['attributes'].get('role', '')
            if role:
                return f"aria_{role}"
        elif 'click_handler' in behaviors and 'cursor_pointer' in behaviors:
            return 'clickable'
        elif 'keyboard_accessible' in behaviors:
            return 'focusable'
        else:
            return 'interactive'