"""
Shadow DOM Traversal Strategy - Deep traversal of shadow DOM and web components
"""

import logging
from typing import Any, Dict, List, Optional, Set
from playwright.async_api import ElementHandle, JSHandle

from ..advanced_extractor import (
    ElementCandidate,
    ExtractionContext,
    ExtractionStrategy,
    ExtractionStrategyBase,
)

logger = logging.getLogger(__name__)


class ShadowDOMTraversalStrategy(ExtractionStrategyBase):
    """
    Advanced shadow DOM traversal strategy for extracting elements
    from web components and shadow roots
    """
    
    def __init__(self, config, ai_service_factory=None):
        super().__init__(config, ai_service_factory)
        
        # Common web component libraries
        self.component_libraries = {
            'polymer': ['paper-', 'iron-', 'app-'],
            'material': ['mat-', 'mdc-', 'md-'],
            'vaadin': ['vaadin-'],
            'lit': ['lit-'],
            'stencil': ['ion-'],
            'salesforce': ['lightning-'],
            'angular': ['ng-'],
            'vue': ['v-']
        }
        
        # Shadow host detection patterns
        self.shadow_host_selectors = [
            '*[shadowroot]',
            ':defined',  # Custom elements
            '[is]',  # Extended built-in elements
        ]
        
        # Add common component selectors
        for prefixes in self.component_libraries.values():
            for prefix in prefixes:
                self.shadow_host_selectors.append(f'{prefix}*')
    
    async def extract(self, context: ExtractionContext) -> List[ElementCandidate]:
        """Extract elements from shadow DOM trees"""
        candidates = []
        
        try:
            # Find all shadow hosts
            shadow_hosts = await self._find_shadow_hosts(context)
            logger.info(f"Shadow DOM Strategy: Found {len(shadow_hosts)} shadow hosts")
            
            # Process each shadow host
            processed_roots = set()
            for host in shadow_hosts:
                shadow_candidates = await self._process_shadow_host(
                    host,
                    context,
                    processed_roots
                )
                candidates.extend(shadow_candidates)
            
            # Also check for iframes
            iframe_candidates = await self._process_iframes(context)
            candidates.extend(iframe_candidates)
            
            logger.info(f"Shadow DOM Strategy: Extracted {len(candidates)} candidates")
            return candidates
            
        except Exception as e:
            logger.error(f"Shadow DOM traversal failed: {e}")
            return candidates
    
    def get_confidence_boost(self) -> float:
        """Shadow DOM elements often need special handling"""
        return 0.2
    
    async def _find_shadow_hosts(self, context: ExtractionContext) -> List[ElementHandle]:
        """Find all elements that might have shadow roots"""
        shadow_hosts = []
        
        # Method 1: Query for known patterns
        for selector in self.shadow_host_selectors:
            try:
                hosts = await context.page.query_selector_all(selector)
                shadow_hosts.extend(hosts)
            except Exception:
                continue
        
        # Method 2: JavaScript-based detection
        try:
            hosts_handle = await context.page.evaluate_handle('''() => {
                const hosts = [];
                const allElements = document.querySelectorAll('*');
                
                for (const element of allElements) {
                    // Check for shadow root
                    if (element.shadowRoot) {
                        hosts.push(element);
                        continue;
                    }
                    
                    // Check if it's a custom element
                    if (element.tagName.includes('-')) {
                        hosts.push(element);
                        continue;
                    }
                    
                    // Check for common web component attributes
                    if (element.hasAttribute('shadow') || 
                        element.hasAttribute('shadowmode') ||
                        element.hasAttribute('shadowroot')) {
                        hosts.push(element);
                    }
                }
                
                return hosts;
            }''')
            
            # Convert to element handles
            count = await hosts_handle.evaluate('hosts => hosts.length')
            for i in range(min(count, 100)):  # Limit to prevent memory issues
                try:
                    element = await hosts_handle.evaluate_handle(f'hosts => hosts[{i}]')
                    if element:
                        shadow_hosts.append(element)
                except:
                    continue
                    
        except Exception as e:
            logger.debug(f"JavaScript shadow host detection failed: {e}")
        
        # Deduplicate
        unique_hosts = []
        seen_tags = set()
        
        for host in shadow_hosts:
            try:
                tag_id = await host.evaluate('el => el.tagName + (el.id || "")')
                if tag_id not in seen_tags:
                    seen_tags.add(tag_id)
                    unique_hosts.append(host)
            except:
                continue
        
        return unique_hosts
    
    async def _process_shadow_host(
        self,
        host: ElementHandle,
        context: ExtractionContext,
        processed_roots: Set[str]
    ) -> List[ElementCandidate]:
        """Process a shadow host and extract elements from its shadow tree"""
        candidates = []
        
        try:
            # Get unique identifier
            host_id = await host.evaluate('el => el.tagName + "_" + (el.id || Math.random())')
            if host_id in processed_roots:
                return candidates
            processed_roots.add(host_id)
            
            # Check if host has shadow root
            has_shadow = await host.evaluate('el => !!el.shadowRoot')
            if not has_shadow:
                # Try to attach shadow if it's a custom element
                await self._try_attach_shadow(host)
                has_shadow = await host.evaluate('el => !!el.shadowRoot')
            
            if not has_shadow:
                return candidates
            
            # Extract elements from shadow root
            shadow_elements = await host.evaluate_handle('''host => {
                const elements = [];
                const shadowRoot = host.shadowRoot;
                
                if (!shadowRoot) return elements;
                
                // Function to recursively collect elements
                function collectElements(root) {
                    const interactiveSelectors = [
                        'button', 'a', 'input', 'select', 'textarea',
                        '[role="button"]', '[role="link"]', '[onclick]',
                        '[tabindex]:not([tabindex="-1"])'
                    ];
                    
                    for (const selector of interactiveSelectors) {
                        const found = root.querySelectorAll(selector);
                        elements.push(...found);
                    }
                    
                    // Recursively process nested shadow roots
                    const allElements = root.querySelectorAll('*');
                    for (const el of allElements) {
                        if (el.shadowRoot) {
                            collectElements(el.shadowRoot);
                        }
                    }
                }
                
                collectElements(shadowRoot);
                return elements;
            }''')
            
            # Process each shadow element
            element_count = await shadow_elements.evaluate('els => els.length')
            
            for i in range(min(element_count, 50)):  # Limit per shadow root
                try:
                    element_data = await shadow_elements.evaluate(f'''els => {{
                        const el = els[{i}];
                        if (!el) return null;
                        
                        // Get element properties
                        const rect = el.getBoundingClientRect();
                        const styles = getComputedStyle(el);
                        
                        return {{
                            tag: el.tagName.toLowerCase(),
                            text: el.textContent?.trim() || '',
                            isVisible: !!(rect.width && rect.height && styles.visibility !== 'hidden'),
                            attributes: Array.from(el.attributes).reduce((acc, attr) => {{
                                acc[attr.name] = attr.value;
                                return acc;
                            }}, {{}}),
                            position: {{
                                x: rect.x,
                                y: rect.y,
                                width: rect.width,
                                height: rect.height
                            }},
                            shadowPath: [] // Will be filled later
                        }};
                    }}''')
                    
                    if element_data and element_data['isVisible']:
                        # Create element handle in shadow DOM context
                        element_handle = await shadow_elements.evaluate_handle(
                            f'els => els[{i}]'
                        )
                        
                        if element_handle:
                            candidate = await self._create_shadow_candidate(
                                element_handle,
                                element_data,
                                host_id
                            )
                            if candidate:
                                candidates.append(candidate)
                    
                except Exception as e:
                    logger.debug(f"Failed to process shadow element {i}: {e}")
                    continue
            
        except Exception as e:
            logger.debug(f"Failed to process shadow host: {e}")
        
        return candidates
    
    async def _try_attach_shadow(self, host: ElementHandle):
        """Try to attach shadow root to custom element"""
        try:
            await host.evaluate('''host => {
                // Only for custom elements
                if (!host.tagName.includes('-')) return;
                
                // Check if element supports shadow DOM
                if (typeof host.attachShadow === 'function' && !host.shadowRoot) {
                    try {
                        host.attachShadow({ mode: 'open' });
                    } catch (e) {
                        // Element might not support shadow DOM
                    }
                }
            }''')
        except Exception:
            pass
    
    async def _create_shadow_candidate(
        self,
        element: ElementHandle,
        element_data: Dict[str, Any],
        host_id: str
    ) -> Optional[ElementCandidate]:
        """Create candidate for shadow DOM element"""
        try:
            # Generate shadow-specific selectors
            selectors = await self._generate_shadow_selectors(element, element_data, host_id)
            
            # Calculate confidence
            confidence = 0.7  # Base confidence for shadow elements
            
            # Boost for interactive elements
            if element_data['tag'] in ['button', 'a', 'input']:
                confidence += 0.1
            
            # Create candidate
            candidate = ElementCandidate(
                element=element,
                confidence=confidence,
                strategies_used={ExtractionStrategy.SHADOW_DOM_TRAVERSAL},
                attributes=element_data['attributes'],
                selectors=selectors,
                metadata={
                    'is_shadow_element': True,
                    'shadow_host': host_id,
                    'element_data': element_data,
                    'shadow_mode': 'open'  # We only handle open shadow roots
                }
            )
            
            return candidate
            
        except Exception as e:
            logger.debug(f"Failed to create shadow candidate: {e}")
            return None
    
    async def _generate_shadow_selectors(
        self,
        element: ElementHandle,
        element_data: Dict[str, Any],
        host_id: str
    ) -> List[Dict[str, Any]]:
        """Generate selectors for shadow DOM elements"""
        selectors = []
        
        try:
            # Get shadow path
            shadow_path = await element.evaluate('''el => {
                const path = [];
                let current = el;
                let root = el.getRootNode();
                
                // Build path from element to shadow root
                while (current && current !== root) {
                    const parent = current.parentElement || current.parentNode;
                    if (!parent) break;
                    
                    const siblings = Array.from(parent.children).filter(
                        child => child.tagName === current.tagName
                    );
                    const index = siblings.indexOf(current);
                    
                    if (current.id) {
                        path.unshift(`#${current.id}`);
                        break;
                    } else {
                        const selector = current.tagName.toLowerCase() + 
                            (index > 0 ? `:nth-of-type(${index + 1})` : '');
                        path.unshift(selector);
                    }
                    
                    current = parent;
                }
                
                return path.join(' > ');
            }''')
            
            # Shadow-piercing selector (for supported browsers)
            if shadow_path:
                selectors.append({
                    'type': 'shadow',
                    'value': f"{host_id} >>> {shadow_path}",
                    'score': 0.7,
                    'strategy': 'shadow-pierce'
                })
            
            # JavaScript-based selector
            js_selector = await element.evaluate('''el => {
                // Build a JavaScript path to the element
                const shadowHost = el.getRootNode().host;
                if (!shadowHost) return null;
                
                const hostSelector = shadowHost.id ? 
                    `document.getElementById('${shadowHost.id}')` :
                    `document.querySelector('${shadowHost.tagName.toLowerCase()}')`;
                
                const elementSelector = el.id ?
                    `.shadowRoot.getElementById('${el.id}')` :
                    `.shadowRoot.querySelector('${el.tagName.toLowerCase()}')`;
                
                return `${hostSelector}${elementSelector}`;
            }''')
            
            if js_selector:
                selectors.append({
                    'type': 'javascript',
                    'value': js_selector,
                    'score': 0.6,
                    'strategy': 'shadow-js'
                })
            
            # Attribute-based selector within shadow
            attrs = element_data['attributes']
            if attrs.get('data-testid'):
                selectors.append({
                    'type': 'shadow',
                    'value': f"{host_id} >>> [data-testid='{attrs['data-testid']}']",
                    'score': 0.8,
                    'strategy': 'shadow-testid'
                })
            
        except Exception as e:
            logger.debug(f"Failed to generate shadow selectors: {e}")
        
        return selectors
    
    async def _process_iframes(self, context: ExtractionContext) -> List[ElementCandidate]:
        """Process elements within iframes"""
        candidates = []
        
        try:
            # Get all iframes
            iframes = await context.page.query_selector_all('iframe')
            
            for iframe in iframes:
                try:
                    # Check if iframe is from same origin
                    is_same_origin = await iframe.evaluate('''iframe => {
                        try {
                            return !!iframe.contentDocument;
                        } catch (e) {
                            return false;
                        }
                    }''')
                    
                    if not is_same_origin:
                        continue
                    
                    # Get iframe content
                    frame = await iframe.content_frame()
                    if not frame:
                        continue
                    
                    # Extract elements from iframe
                    iframe_elements = await frame.query_selector_all(
                        'button, a, input, select, textarea, [role="button"], [onclick]'
                    )
                    
                    # Create candidates for iframe elements
                    for element in iframe_elements[:20]:  # Limit per iframe
                        candidate = await self._create_iframe_candidate(element, iframe)
                        if candidate:
                            candidates.append(candidate)
                    
                except Exception as e:
                    logger.debug(f"Failed to process iframe: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"iFrame processing failed: {e}")
        
        return candidates
    
    async def _create_iframe_candidate(
        self,
        element: ElementHandle,
        iframe: ElementHandle
    ) -> Optional[ElementCandidate]:
        """Create candidate for iframe element"""
        try:
            # Get element properties
            properties = await element.evaluate('''el => ({
                tag: el.tagName.toLowerCase(),
                text: el.textContent?.trim() || '',
                attributes: Array.from(el.attributes).reduce((acc, attr) => {
                    acc[attr.name] = attr.value;
                    return acc;
                }, {})
            })''')
            
            # Get iframe identifier
            iframe_id = await iframe.evaluate('iframe => iframe.id || iframe.src || "iframe"')
            
            # Generate selectors
            selectors = [{
                'type': 'iframe',
                'value': f"iframe#{iframe_id} >>> {properties['tag']}",
                'score': 0.5,
                'strategy': 'iframe-context'
            }]
            
            candidate = ElementCandidate(
                element=element,
                confidence=0.6,
                strategies_used={ExtractionStrategy.SHADOW_DOM_TRAVERSAL},
                attributes=properties['attributes'],
                selectors=selectors,
                metadata={
                    'is_iframe_element': True,
                    'iframe_context': iframe_id,
                    'element_tag': properties['tag']
                }
            )
            
            return candidate
            
        except Exception:
            return None