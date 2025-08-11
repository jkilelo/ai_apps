"""
Dynamic Content Tracking Strategy - Advanced tracking for SPAs and dynamic content
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


class DynamicContentTrackingStrategy(ExtractionStrategyBase):
    """
    Advanced strategy for tracking and extracting dynamically loaded elements
    in Single Page Applications (SPAs) and dynamic websites
    """
    
    def __init__(self, config, ai_service_factory=None):
        super().__init__(config, ai_service_factory)
        
        # Configuration for dynamic tracking
        self.mutation_observer_timeout = 5000  # 5 seconds
        self.scroll_increment = 500  # pixels
        self.max_scroll_attempts = 10
        self.ajax_wait_time = 2000  # milliseconds
        self.route_change_wait = 3000  # milliseconds
        
        # Common SPA frameworks and their patterns
        self.spa_patterns = {
            'react': {
                'root_selectors': ['#root', '#app', '.app', '[data-reactroot]'],
                'route_indicators': ['react-router', 'data-react-router'],
                'dynamic_markers': ['__reactInternalInstance', '_reactRootContainer']
            },
            'angular': {
                'root_selectors': ['app-root', '[ng-app]', '[data-ng-app]'],
                'route_indicators': ['router-outlet', 'ng-view'],
                'dynamic_markers': ['ng-version', '__ngContext__']
            },
            'vue': {
                'root_selectors': ['#app', '[data-app]', '.vue-app'],
                'route_indicators': ['router-view', 'nuxt'],
                'dynamic_markers': ['__vue__', '__vue_app__']
            },
            'ember': {
                'root_selectors': ['.ember-application', '[data-ember-application]'],
                'route_indicators': ['outlet'],
                'dynamic_markers': ['__ember']
            }
        }
        
        # Dynamic content patterns
        self.dynamic_patterns = {
            'infinite_scroll': ['infinite-scroll', 'load-more', 'show-more'],
            'lazy_load': ['lazy', 'lazyload', 'lazy-load'],
            'ajax_content': ['ajax-content', 'dynamic-content', 'async-content'],
            'modal_triggers': ['modal-trigger', 'popup-trigger', 'dialog-trigger'],
            'tab_content': ['tab-pane', 'tab-content', 'tabs-panel'],
            'accordion': ['accordion', 'collapse', 'expandable']
        }
    
    async def extract(self, context: ExtractionContext) -> List[ElementCandidate]:
        """Extract elements with dynamic content tracking"""
        candidates = []
        
        try:
            # Detect SPA framework
            spa_info = await self._detect_spa_framework(context.page)
            logger.info(f"Dynamic Strategy: Detected SPA - {spa_info}")
            
            # Initial element capture
            initial_elements = await self._capture_visible_elements(context)
            candidates.extend(initial_elements)
            
            # Set up mutation observer
            mutations_detected = await self._setup_mutation_observer(context.page)
            
            # Track dynamic content loading strategies
            strategies_used = []
            
            # 1. Scroll-based loading (infinite scroll, lazy load)
            if await self._has_scroll_loading(context.page):
                scroll_elements = await self._track_scroll_loading(context)
                candidates.extend(scroll_elements)
                strategies_used.append('scroll_loading')
            
            # 2. User interaction triggers (tabs, accordions, modals)
            interaction_elements = await self._track_interaction_triggers(context)
            candidates.extend(interaction_elements)
            if interaction_elements:
                strategies_used.append('interaction_triggers')
            
            # 3. Route changes (SPA navigation)
            if spa_info['is_spa']:
                route_elements = await self._track_route_changes(context, spa_info)
                candidates.extend(route_elements)
                strategies_used.append('route_navigation')
            
            # 4. AJAX/Fetch monitoring
            ajax_elements = await self._track_ajax_content(context)
            candidates.extend(ajax_elements)
            if ajax_elements:
                strategies_used.append('ajax_monitoring')
            
            # 5. Time-based content (animations, delays)
            delayed_elements = await self._track_delayed_content(context)
            candidates.extend(delayed_elements)
            if delayed_elements:
                strategies_used.append('time_delayed')
            
            # Remove duplicates while preserving order
            unique_candidates = self._deduplicate_candidates(candidates)
            
            logger.info(f"Dynamic Strategy: Found {len(unique_candidates)} unique elements")
            logger.info(f"Strategies used: {strategies_used}")
            
            return unique_candidates
            
        except Exception as e:
            logger.error(f"Dynamic content tracking failed: {e}")
            return candidates
    
    def get_confidence_boost(self) -> float:
        """Dynamic elements often need special handling"""
        return 0.2
    
    async def _detect_spa_framework(self, page: Page) -> Dict[str, Any]:
        """Detect if page is an SPA and which framework"""
        spa_info = {
            'is_spa': False,
            'framework': None,
            'version': None,
            'root_element': None
        }
        
        try:
            # Check for SPA frameworks
            framework_check = await page.evaluate('''() => {
                const checks = {
                    react: {
                        check: () => !!(window.React || document.querySelector('[data-reactroot]') || 
                                     window.__REACT_DEVTOOLS_GLOBAL_HOOK__),
                        version: () => window.React?.version || 'unknown'
                    },
                    angular: {
                        check: () => !!(window.ng || window.getAllAngularRootElements || 
                                     document.querySelector('[ng-version]')),
                        version: () => window.ng?.VERSION?.full || 
                                     document.querySelector('[ng-version]')?.getAttribute('ng-version') || 'unknown'
                    },
                    vue: {
                        check: () => !!(window.Vue || window.__VUE__ || 
                                     document.querySelector('#app')?.__vue__),
                        version: () => window.Vue?.version || 'unknown'
                    },
                    ember: {
                        check: () => !!(window.Ember || window.Em),
                        version: () => window.Ember?.VERSION || 'unknown'
                    }
                };
                
                for (const [framework, methods] of Object.entries(checks)) {
                    if (methods.check()) {
                        return {
                            framework: framework,
                            version: methods.version(),
                            hasRouter: !!(window.location.pathname !== '/' || 
                                       window.history.length > 1)
                        };
                    }
                }
                
                // Check for generic SPA indicators
                const genericSPA = !!(
                    window.history.pushState ||
                    document.querySelector('[data-spa]') ||
                    document.querySelector('#app') ||
                    document.querySelector('#root')
                );
                
                return {
                    framework: genericSPA ? 'generic' : null,
                    version: null,
                    hasRouter: genericSPA
                };
            }''')
            
            if framework_check['framework']:
                spa_info['is_spa'] = True
                spa_info['framework'] = framework_check['framework']
                spa_info['version'] = framework_check['version']
                
                # Find root element
                framework_config = self.spa_patterns.get(framework_check['framework'], {})
                for selector in framework_config.get('root_selectors', []):
                    root = await page.query_selector(selector)
                    if root:
                        spa_info['root_element'] = selector
                        break
            
        except Exception as e:
            logger.debug(f"SPA detection failed: {e}")
        
        return spa_info
    
    async def _setup_mutation_observer(self, page: Page) -> bool:
        """Set up mutation observer to track DOM changes"""
        try:
            await page.evaluate('''() => {
                window.__dynamicMutations = [];
                window.__mutationObserver = new MutationObserver((mutations) => {
                    mutations.forEach(mutation => {
                        if (mutation.type === 'childList') {
                            mutation.addedNodes.forEach(node => {
                                if (node.nodeType === 1) { // Element node
                                    window.__dynamicMutations.push({
                                        type: 'added',
                                        tag: node.tagName,
                                        id: node.id,
                                        classes: Array.from(node.classList || []),
                                        timestamp: Date.now()
                                    });
                                }
                            });
                        }
                    });
                });
                
                window.__mutationObserver.observe(document.body, {
                    childList: true,
                    subtree: true,
                    attributes: true,
                    attributeFilter: ['style', 'class', 'hidden', 'disabled']
                });
                
                return true;
            }''')
            return True
        except Exception:
            return False
    
    async def _capture_visible_elements(self, context: ExtractionContext) -> List[ElementCandidate]:
        """Capture currently visible interactive elements"""
        candidates = []
        
        try:
            # Query for interactive elements
            elements = await context.page.query_selector_all(
                'button:visible, a:visible, input:visible, [role="button"]:visible, ' +
                '[onclick]:visible, [ng-click]:visible, [v-on\\:click]:visible'
            )
            
            for element in elements[:50]:  # Limit initial capture
                try:
                    candidate = await self._create_dynamic_candidate(element, 'initial_load')
                    if candidate:
                        candidates.append(candidate)
                except Exception:
                    continue
                    
        except Exception as e:
            logger.debug(f"Failed to capture visible elements: {e}")
        
        return candidates
    
    async def _has_scroll_loading(self, page: Page) -> bool:
        """Check if page has scroll-based loading"""
        try:
            indicators = await page.evaluate('''() => {
                // Check for infinite scroll indicators
                const hasInfiniteScroll = !!(
                    document.querySelector('[class*="infinite"]') ||
                    document.querySelector('[class*="load-more"]') ||
                    document.querySelector('[data-infinite-scroll]')
                );
                
                // Check if content height exceeds viewport
                const hasScrollableContent = 
                    document.documentElement.scrollHeight > window.innerHeight;
                
                // Check for lazy load attributes
                const hasLazyLoad = !!(
                    document.querySelector('[loading="lazy"]') ||
                    document.querySelector('[data-lazy]') ||
                    document.querySelector('.lazy')
                );
                
                return hasInfiniteScroll || (hasScrollableContent && hasLazyLoad);
            }''')
            
            return indicators
            
        except Exception:
            return False
    
    async def _track_scroll_loading(self, context: ExtractionContext) -> List[ElementCandidate]:
        """Track elements loaded during scrolling"""
        candidates = []
        
        try:
            initial_height = await context.page.evaluate('document.documentElement.scrollHeight')
            
            for i in range(self.max_scroll_attempts):
                # Scroll down
                await context.page.evaluate(f'window.scrollBy(0, {self.scroll_increment})')
                await context.page.wait_for_timeout(1000)
                
                # Check for new content
                current_height = await context.page.evaluate('document.documentElement.scrollHeight')
                
                if current_height > initial_height:
                    # New content loaded
                    new_elements = await context.page.evaluate('''() => {
                        const mutations = window.__dynamicMutations || [];
                        const recentMutations = mutations.filter(
                            m => Date.now() - m.timestamp < 2000
                        );
                        return recentMutations.length;
                    }''')
                    
                    if new_elements > 0:
                        # Capture new elements
                        elements = await context.page.query_selector_all(
                            'button:visible, a:visible, [role="button"]:visible'
                        )
                        
                        for element in elements[-20:]:  # Get last 20 elements
                            candidate = await self._create_dynamic_candidate(element, 'scroll_load')
                            if candidate:
                                candidates.append(candidate)
                    
                    initial_height = current_height
                else:
                    # No new content, check if we're at bottom
                    at_bottom = await context.page.evaluate('''() => {
                        return window.innerHeight + window.scrollY >= 
                               document.documentElement.scrollHeight - 100;
                    }''')
                    
                    if at_bottom:
                        break
            
            # Scroll back to top
            await context.page.evaluate('window.scrollTo(0, 0)')
            
        except Exception as e:
            logger.debug(f"Scroll tracking failed: {e}")
        
        return candidates
    
    async def _track_interaction_triggers(self, context: ExtractionContext) -> List[ElementCandidate]:
        """Track elements that appear after user interactions"""
        candidates = []
        
        try:
            # Find interaction triggers
            triggers = await context.page.evaluate('''() => {
                const triggers = [];
                
                // Tab triggers
                const tabs = document.querySelectorAll(
                    '[role="tab"], .nav-tab, .tab-link, [data-toggle="tab"]'
                );
                tabs.forEach(tab => triggers.push({
                    element: tab,
                    type: 'tab',
                    selector: tab.id ? `#${tab.id}` : null
                }));
                
                // Accordion/Collapse triggers
                const accordions = document.querySelectorAll(
                    '[data-toggle="collapse"], .accordion-toggle, .collapse-trigger'
                );
                accordions.forEach(acc => triggers.push({
                    element: acc,
                    type: 'accordion',
                    target: acc.getAttribute('data-target') || acc.getAttribute('href')
                }));
                
                // Modal triggers
                const modals = document.querySelectorAll(
                    '[data-toggle="modal"], [data-modal], .modal-trigger'
                );
                modals.forEach(modal => triggers.push({
                    element: modal,
                    type: 'modal',
                    target: modal.getAttribute('data-target') || modal.getAttribute('href')
                }));
                
                return triggers.length;
            }''')
            
            if triggers > 0:
                # Test a few triggers
                for i in range(min(triggers, 3)):
                    try:
                        # Click trigger
                        trigger = await context.page.evaluate(f'document.querySelectorAll("[role=tab], .nav-tab")[{i}]')
                        if trigger:
                            await trigger.click()
                            await context.page.wait_for_timeout(1000)
                            
                            # Capture revealed content
                            new_elements = await context.page.query_selector_all(
                                '.tab-pane.active button, .tab-pane.active a'
                            )
                            
                            for element in new_elements[:5]:
                                candidate = await self._create_dynamic_candidate(element, 'interaction_reveal')
                                if candidate:
                                    candidates.append(candidate)
                    except Exception:
                        continue
                        
        except Exception as e:
            logger.debug(f"Interaction tracking failed: {e}")
        
        return candidates
    
    async def _track_route_changes(self, context: ExtractionContext, spa_info: Dict[str, Any]) -> List[ElementCandidate]:
        """Track elements that appear on route changes"""
        candidates = []
        
        try:
            # Get current URL
            initial_url = context.page.url
            
            # Find navigation links
            nav_links = await context.page.query_selector_all(
                'nav a, [role="navigation"] a, .nav-link, .router-link'
            )
            
            # Test a few route changes
            for i, link in enumerate(nav_links[:3]):
                try:
                    # Click navigation link
                    await link.click()
                    
                    # Wait for route change
                    await context.page.wait_for_timeout(self.route_change_wait)
                    
                    # Check if URL changed
                    current_url = context.page.url
                    if current_url != initial_url:
                        # Capture elements on new route
                        elements = await context.page.query_selector_all(
                            'button:visible, a:visible, [role="button"]:visible'
                        )
                        
                        for element in elements[:10]:
                            candidate = await self._create_dynamic_candidate(element, 'route_change')
                            if candidate:
                                candidates.append(candidate)
                        
                        # Navigate back
                        await context.page.go_back()
                        await context.page.wait_for_timeout(1000)
                        
                except Exception:
                    continue
                    
        except Exception as e:
            logger.debug(f"Route tracking failed: {e}")
        
        return candidates
    
    async def _track_ajax_content(self, context: ExtractionContext) -> List[ElementCandidate]:
        """Track content loaded via AJAX/Fetch"""
        candidates = []
        
        try:
            # Set up network monitoring
            ajax_detected = await context.page.evaluate('''() => {
                window.__ajaxRequests = [];
                
                // Intercept XMLHttpRequest
                const originalXHR = window.XMLHttpRequest;
                window.XMLHttpRequest = function() {
                    const xhr = new originalXHR();
                    const originalOpen = xhr.open;
                    
                    xhr.open = function(method, url) {
                        window.__ajaxRequests.push({
                            method: method,
                            url: url,
                            timestamp: Date.now()
                        });
                        return originalOpen.apply(xhr, arguments);
                    };
                    
                    return xhr;
                };
                
                // Intercept Fetch
                const originalFetch = window.fetch;
                window.fetch = function(url, options) {
                    window.__ajaxRequests.push({
                        method: options?.method || 'GET',
                        url: url.toString(),
                        timestamp: Date.now()
                    });
                    return originalFetch.apply(window, arguments);
                };
                
                return true;
            }''')
            
            # Trigger some actions that might load AJAX content
            buttons = await context.page.query_selector_all('button:visible')
            
            for button in buttons[:3]:
                try:
                    text = await button.text_content()
                    if any(keyword in text.lower() for keyword in ['load', 'show', 'more', 'refresh']):
                        await button.click()
                        await context.page.wait_for_timeout(self.ajax_wait_time)
                        
                        # Check for AJAX requests
                        ajax_count = await context.page.evaluate('window.__ajaxRequests.length')
                        if ajax_count > 0:
                            # Capture new elements
                            elements = await context.page.query_selector_all(
                                '[data-ajax], .ajax-content, .dynamic-content'
                            )
                            
                            for element in elements[:5]:
                                candidate = await self._create_dynamic_candidate(element, 'ajax_load')
                                if candidate:
                                    candidates.append(candidate)
                                    
                except Exception:
                    continue
                    
        except Exception as e:
            logger.debug(f"AJAX tracking failed: {e}")
        
        return candidates
    
    async def _track_delayed_content(self, context: ExtractionContext) -> List[ElementCandidate]:
        """Track content that appears after delays"""
        candidates = []
        
        try:
            # Wait for animations and delayed content
            await context.page.wait_for_timeout(3000)
            
            # Check for newly visible elements
            delayed_elements = await context.page.evaluate('''() => {
                const elements = [];
                
                // Find elements with animation classes
                const animated = document.querySelectorAll(
                    '[class*="animate"], [class*="fade"], [class*="slide"]'
                );
                
                animated.forEach(el => {
                    const isInteractive = el.matches(
                        'button, a, input, [role="button"], [onclick]'
                    );
                    if (isInteractive && el.offsetParent !== null) {
                        elements.push(el);
                    }
                });
                
                return elements.length;
            }''')
            
            if delayed_elements > 0:
                elements = await context.page.query_selector_all(
                    '[class*="animate"] button, [class*="fade"] a'
                )
                
                for element in elements[:10]:
                    candidate = await self._create_dynamic_candidate(element, 'delayed_appear')
                    if candidate:
                        candidates.append(candidate)
                        
        except Exception as e:
            logger.debug(f"Delayed content tracking failed: {e}")
        
        return candidates
    
    async def _create_dynamic_candidate(
        self,
        element: ElementHandle,
        load_type: str
    ) -> Optional[ElementCandidate]:
        """Create candidate for dynamically loaded element"""
        try:
            # Get element properties
            properties = await element.evaluate('''el => ({
                tag: el.tagName.toLowerCase(),
                text: el.textContent?.trim() || '',
                isVisible: !!(el.offsetWidth || el.offsetHeight),
                attributes: Array.from(el.attributes).reduce((acc, attr) => {
                    acc[attr.name] = attr.value;
                    return acc;
                }, {}),
                hasEvent: !!(el.onclick || el.getAttribute('onclick') || 
                           el.getAttribute('ng-click') || el.getAttribute('v-on:click'))
            })''')
            
            if not properties['isVisible']:
                return None
            
            # Generate selectors for dynamic element
            selectors = await self._generate_dynamic_selectors(element, properties)
            
            # Calculate confidence based on load type
            confidence_map = {
                'initial_load': 0.6,
                'scroll_load': 0.7,
                'interaction_reveal': 0.75,
                'route_change': 0.8,
                'ajax_load': 0.75,
                'delayed_appear': 0.65
            }
            
            confidence = confidence_map.get(load_type, 0.6)
            
            # Boost confidence for certain indicators
            if properties['hasEvent']:
                confidence += 0.1
            if properties['tag'] in ['button', 'a', 'input']:
                confidence += 0.05
            
            candidate = ElementCandidate(
                element=element,
                confidence=min(confidence, 0.95),
                strategies_used={ExtractionStrategy.DYNAMIC_CONTENT_TRACKING},
                attributes=properties['attributes'],
                selectors=selectors,
                metadata={
                    'is_dynamic': True,
                    'load_type': load_type,
                    'element_tag': properties['tag'],
                    'has_event_handler': properties['hasEvent']
                }
            )
            
            return candidate
            
        except Exception as e:
            logger.debug(f"Failed to create dynamic candidate: {e}")
            return None
    
    async def _generate_dynamic_selectors(
        self,
        element: ElementHandle,
        properties: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate selectors for dynamic elements"""
        selectors = []
        
        try:
            attrs = properties['attributes']
            
            # ID selector (most stable for dynamic content)
            if attrs.get('id'):
                selectors.append({
                    'type': 'css',
                    'value': f"#{attrs['id']}",
                    'score': 0.9,
                    'strategy': 'dynamic-id'
                })
            
            # Data attribute selectors (common in SPAs)
            for attr_name, attr_value in attrs.items():
                if attr_name.startswith('data-') and attr_value:
                    selectors.append({
                        'type': 'css',
                        'value': f"[{attr_name}='{attr_value}']",
                        'score': 0.8,
                        'strategy': 'dynamic-data-attr'
                    })
                    break  # Use first data attribute
            
            # Framework-specific selectors
            if attrs.get('ng-click'):
                selectors.append({
                    'type': 'css',
                    'value': f"[ng-click='{attrs['ng-click']}']",
                    'score': 0.75,
                    'strategy': 'angular-dynamic'
                })
            elif attrs.get('v-on:click'):
                selectors.append({
                    'type': 'css',
                    'value': f"[v-on\\:click='{attrs['v-on:click']}']",
                    'score': 0.75,
                    'strategy': 'vue-dynamic'
                })
            
            # Text-based selector for buttons/links
            if properties['text'] and properties['tag'] in ['button', 'a']:
                selectors.append({
                    'type': 'xpath',
                    'value': f"//{properties['tag']}[contains(text(), '{properties['text'][:30]}')]",
                    'score': 0.6,
                    'strategy': 'dynamic-text'
                })
            
            # Class-based selector (less reliable for dynamic content)
            if attrs.get('class'):
                classes = attrs['class'].split()
                if classes:
                    selectors.append({
                        'type': 'css',
                        'value': f".{classes[0]}",
                        'score': 0.5,
                        'strategy': 'dynamic-class'
                    })
                    
        except Exception as e:
            logger.debug(f"Failed to generate dynamic selectors: {e}")
        
        return selectors
    
    def _deduplicate_candidates(self, candidates: List[ElementCandidate]) -> List[ElementCandidate]:
        """Remove duplicate candidates while preserving the best ones"""
        seen_selectors = set()
        unique_candidates = []
        
        # Sort by confidence (highest first)
        sorted_candidates = sorted(candidates, key=lambda c: c.confidence, reverse=True)
        
        for candidate in sorted_candidates:
            # Create a unique key from selectors
            selector_key = None
            for selector in candidate.selectors:
                if selector['score'] > 0.7:  # Use high-scoring selectors for dedup
                    selector_key = f"{selector['type']}:{selector['value']}"
                    break
            
            if selector_key and selector_key not in seen_selectors:
                seen_selectors.add(selector_key)
                unique_candidates.append(candidate)
            elif not selector_key:
                # Include elements without good selectors (might be truly dynamic)
                unique_candidates.append(candidate)
        
        return unique_candidates