"""
Unified DOM Extractor - Consolidated DOM element extraction with stealth capabilities

This module provides a single, high-quality DOM extraction implementation that combines
all the best features from the various DOM strategy implementations.
"""

import asyncio
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime
from playwright.async_api import ElementHandle, Page, BrowserContext

from ...core.stealth_browser import create_stealth_browser
from ...core.browser_profiles import ProfileType
from .advanced_extractor import (
    ElementCandidate,
    ExtractionContext,
    ExtractionStrategy,
    ExtractionStrategyBase,
)

logger = logging.getLogger(__name__)


class DOMExtractor(ExtractionStrategyBase):
    """
    Unified DOM extractor with configurable stealth levels and extraction modes.
    
    This consolidates all DOM extraction strategies into a single, high-quality implementation.
    """
    
    def __init__(self, config, ai_service_factory=None, stealth_level: str = "enhanced", 
                 use_ultra_stealth_profile: bool = False):
        """
        Initialize the DOM extractor.
        
        Args:
            config: Configuration object
            ai_service_factory: Optional AI service factory
            stealth_level: Stealth level - "none", "basic", "enhanced", or "maximum"
            use_ultra_stealth_profile: Use exact ultra-stealth timing profile for 100% parity
        """
        super().__init__(config, ai_service_factory)
        
        self.stealth_level = stealth_level
        
        # Create stealth browser with appropriate profile
        if use_ultra_stealth_profile:
            self.stealth = create_stealth_browser(ProfileType.ULTRA_STEALTH)
            # Override stealth level to maximum for ultra-stealth profile
            self.stealth_level = "maximum"
        else:
            # Map stealth levels to profiles
            profile_map = {
                "none": ProfileType.BOT,
                "basic": ProfileType.HUMAN,
                "enhanced": ProfileType.STEALTH,
                "maximum": ProfileType.STEALTH
            }
            profile = profile_map.get(stealth_level, ProfileType.STEALTH)
            self.stealth = create_stealth_browser(profile)
        
        # Configurable selector preferences
        self.selector_preferences = [
            'data-testid',
            'data-test',
            'data-cy',
            'data-qa',
            'data-automation',
            'id',
            'aria-label',
            'aria-labelledby',
            'name',
            'class',
            'type',
            'role'
        ]
        
        # Elements to prioritize for extraction
        self.important_selectors = [
            # Basic interactive elements
            'button',
            'a[href]',
            'input:not([type="hidden"])',
            'textarea',
            'select',
            
            # ARIA roles
            '[role="button"]',
            '[role="link"]',
            '[role="tab"]',
            '[role="menuitem"]',
            '[role="combobox"]',
            '[role="textbox"]',
            '[role="checkbox"]',
            '[role="radio"]',
            
            # Event handlers
            '[onclick]',
            '[ng-click]',
            '[v-on\\:click]',
            '[data-action]',
            '[data-click]',
            '[data-href]',
            
            # Framework-specific
            '[data-react-component]',
            '[data-reactid]',
            '[data-ng-click]',
            '[data-vue]',
            '[data-ember-action]'
        ]
        
        # Elements to exclude - match ultra-stealth
        self.exclude_selectors = [
            'script',
            'style',
            'noscript',
            'meta',
            'link'
        ]
        
        # Extraction statistics
        self.stats = {
            'total_extracted': 0,
            'extraction_time': 0,
            'stealth_actions': 0
        }
    
    async def extract(self, context: ExtractionContext) -> List[ElementCandidate]:
        """
        Extract elements from the page with configured stealth level.
        
        Args:
            context: The extraction context
            
        Returns:
            List of element candidates
        """
        start_time = datetime.now()
        candidates = []
        
        try:
            # Apply stealth if configured
            if self.stealth_level != "none":
                # Profile-based stealth application
                await self.stealth.apply_stealth(context.page)
                self.stats['stealth_actions'] += 1
            
            # Handle anti-bot challenges if maximum stealth or ultra-stealth profile
            if self.stealth_level == "maximum" or self.stealth.profile.stealth.handle_cloudflare:
                await self._handle_challenges(context.page)
            
            # Handle cookie consent based on profile
            if self.stealth.profile.stealth.auto_handle_cookies:
                if await self.stealth.handle_cookie_consent(context.page):
                    self.stats['stealth_actions'] += 1
            
            # Build trust if profile requires it
            if self.stealth.profile.stealth.build_trust:
                domain = self._extract_domain(context.url)
                await self.stealth.build_trust(context.page, domain)
            
            # Wait for page stability
            await self._wait_for_page_stability(context.page)
            
            # Extract elements using multiple methods
            all_elements = await self._extract_all_elements(context)
            # Match ultra-stealth logging - log AFTER filtering in _extract_all_elements
            # logger.info(f"DOM Extractor: Found {len(all_elements)} potential elements")
            
            # Analyze each element
            for element in all_elements:
                try:
                    # Add micro-delays between element analysis based on profile
                    if self.stealth_level != "none":
                        await self.stealth.human_like_delay(delay_type="element_analysis")
                    
                    candidate = await self._analyze_element(element, context)
                    if candidate:
                        candidates.append(candidate)
                except Exception as e:
                    logger.debug(f"Error analyzing element: {e}")
                    continue
            
            # Extract dynamic elements if configured
            if self.config.browser.timeout > 20000:  # Only for longer timeouts
                dynamic_elements = await self._extract_dynamic_elements(context)
                for element in dynamic_elements:
                    try:
                        candidate = await self._analyze_element(element, context)
                        if candidate:
                            candidate.metadata['is_dynamic'] = True
                            candidates.append(candidate)
                    except Exception as e:
                        logger.debug(f"Error analyzing dynamic element: {e}")
                        continue
            
            # Update statistics
            self.stats['total_extracted'] += len(candidates)
            self.stats['extraction_time'] = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"DOM Extractor: Extracted {len(candidates)} valid candidates in {self.stats['extraction_time']:.2f}s")
            return candidates
            
        except Exception as e:
            logger.error(f"DOM extraction failed: {e}")
            return candidates
    
    def get_confidence_boost(self) -> float:
        """Get confidence boost based on stealth level"""
        boost_map = {
            "none": 0.2,
            "basic": 0.3,
            "enhanced": 0.4,
            "maximum": 0.5
        }
        return boost_map.get(self.stealth_level, 0.3)
    
    async def _handle_challenges(self, page: Page) -> None:
        """Handle anti-bot challenges"""
        if await self.stealth.handle_cloudflare_challenge(page):
            self.stats['stealth_actions'] += 1
            logger.info("Successfully handled anti-bot challenge")
    
    async def _wait_for_page_stability(self, page: Page) -> None:
        """Wait for page to become stable"""
        try:
            # Use different waiting strategies based on profile
            if self.stealth.profile.profile_type == ProfileType.ULTRA_STEALTH:
                # Use exact ultra-stealth timing
                await self.stealth.human_like_delay(delay_type="stability")
            elif self.stealth_level == "maximum":
                # More human-like waiting
                await self.stealth.human_like_delay(1000, 2000)
            
            # Wait for network idle
            try:
                timeout = self.stealth.profile.timing.network_idle_timeout
                await page.wait_for_load_state('networkidle', timeout=timeout)
            except:
                logger.debug("Network idle timeout, continuing...")
            
            # Wait for DOM stability
            await page.evaluate("""
                () => {
                    return new Promise((resolve) => {
                        let lastHeight = document.body.scrollHeight;
                        let checks = 0;
                        const maxChecks = 10;
                        const interval = 400 + Math.floor(Math.random() * 200);
                        
                        const checkStability = setInterval(() => {
                            const currentHeight = document.body.scrollHeight;
                            checks++;
                            
                            if (currentHeight === lastHeight || checks >= maxChecks) {
                                clearInterval(checkStability);
                                resolve();
                            }
                            
                            lastHeight = currentHeight;
                        }, interval);
                    });
                }
            """)
            
        except Exception as e:
            logger.debug(f"Page stability wait error: {e}")
    
    async def _extract_all_elements(self, context: ExtractionContext) -> List[ElementHandle]:
        """Extract all potential elements from the page"""
        elements = []
        
        # Method 1: Query important selectors (match ultra-stealth approach)
        # Only use first 15 selectors like ultra-stealth
        selectors_to_use = self.important_selectors[:15]
        
        # Use batching for ultra-stealth profile
        if self.stealth.profile.profile_type == ProfileType.ULTRA_STEALTH:
            # Build selectors in batches like ultra-stealth
            selector_batches = [
                selectors_to_use[i:i+5] 
                for i in range(0, len(selectors_to_use), 5)
            ]
            
            for batch in selector_batches:
                # Random delay between batches
                await self.stealth.human_like_delay(delay_type="selector_batch")
                
                for selector in batch:
                    try:
                        selector_elements = await context.page.query_selector_all(selector)
                        elements.extend(selector_elements)
                    except Exception as e:
                        logger.debug(f"Failed to query {selector}: {e}")
                        continue
        else:
            # Standard extraction
            for selector in selectors_to_use:
                try:
                    selector_elements = await context.page.query_selector_all(selector)
                    elements.extend(selector_elements)
                    
                    # Add delay in maximum stealth mode
                    if self.stealth_level == "maximum":
                        await self.stealth.human_like_delay(50, 150)
                except Exception as e:
                    logger.debug(f"Failed to query {selector}: {e}")
                    continue
        
        # Method 2: Find elements with event listeners
        # Add delay before event extraction based on profile
        if self.stealth.profile.profile_type == ProfileType.ULTRA_STEALTH:
            await self.stealth.human_like_delay(delay_type="event_extraction")
        elif self.stealth_level == "maximum":
            await self.stealth.human_like_delay(100, 300)
        
        try:
            event_elements = await self._extract_event_elements(context.page)
            elements.extend(event_elements)
        except Exception as e:
            logger.debug(f"Failed to extract event elements: {e}")
        
        # Don't do shadow DOM, iframe, or dynamic extraction in the main flow
        # Ultra-stealth doesn't do these in _extract_all_elements_stealth
        
        # Remove duplicates and filter
        unique_elements = await self._filter_unique_elements(elements, context)
        
        # Log after filtering to match ultra-stealth
        logger.info(f"DOM Extractor: Found {len(unique_elements)} potential elements")
        
        return unique_elements
    
    async def _extract_event_elements(self, page: Page) -> List[ElementHandle]:
        """Extract elements with event listeners"""
        event_elements = []
        
        try:
            event_elements_handle = await page.evaluate_handle("""
                () => {
                    const allElements = document.querySelectorAll('*');
                    const elementsWithListeners = [];
                    
                    for (const element of allElements) {
                        // Skip invisible elements
                        const style = window.getComputedStyle(element);
                        if (style.display === 'none' || 
                            style.visibility === 'hidden' ||
                            style.opacity === '0') {
                            continue;
                        }
                        
                        // Check for event attributes
                        const hasEventAttr = Array.from(element.attributes).some(
                            attr => attr.name.startsWith('on')
                        );
                        
                        // Check for data attributes suggesting interactivity
                        const hasDataAction = Array.from(element.attributes).some(
                            attr => attr.name.includes('action') || 
                                   attr.name.includes('click') ||
                                   attr.name.includes('href')
                        );
                        
                        // Check for interactive properties
                        if (hasEventAttr || hasDataAction || 
                            element.onclick || element.onchange || 
                            element.onsubmit || element.style.cursor === 'pointer') {
                            elementsWithListeners.push(element);
                        }
                    }
                    
                    return elementsWithListeners;
                }
            """)
            
            # Convert to element handles
            count = await event_elements_handle.evaluate('els => els.length')
            # Limit to 100 like ultra-stealth
            for i in range(min(count, 100)):
                try:
                    element = await event_elements_handle.evaluate_handle(f'els => els[{i}]')
                    event_elements.append(element)
                except:
                    pass
                    
        except Exception as e:
            logger.debug(f"Event elements extraction error: {e}")
        
        return event_elements
    
    async def _extract_shadow_dom_elements(self, page: Page) -> List[ElementHandle]:
        """Extract elements from shadow DOM"""
        shadow_elements = []
        
        try:
            shadow_hosts = await page.evaluate_handle("""
                () => {
                    const hosts = [];
                    const allElements = document.querySelectorAll('*');
                    
                    for (const element of allElements) {
                        if (element.shadowRoot) {
                            hosts.push(element);
                        }
                    }
                    
                    return hosts;
                }
            """)
            
            count = await shadow_hosts.evaluate('hosts => hosts.length')
            logger.debug(f"Found {count} shadow DOM hosts")
            
            for i in range(count):
                try:
                    shadow_root_elements = await page.evaluate_handle(f"""
                        () => {{
                            const hosts = Array.from(document.querySelectorAll('*')).filter(el => el.shadowRoot);
                            const host = hosts[{i}];
                            if (!host || !host.shadowRoot) return [];
                            
                            const elements = [];
                            const shadowElements = host.shadowRoot.querySelectorAll('*');
                            
                            for (const element of shadowElements) {{
                                const tagName = element.tagName.toLowerCase();
                                if (['a', 'button', 'input', 'select', 'textarea'].includes(tagName) ||
                                    element.hasAttribute('onclick') ||
                                    element.hasAttribute('role')) {{
                                    elements.push(element);
                                }}
                            }}
                            
                            return elements;
                        }}
                    """)
                    
                    shadow_count = await shadow_root_elements.evaluate('els => els.length')
                    for j in range(min(shadow_count, 50)):
                        try:
                            element = await shadow_root_elements.evaluate_handle(f'els => els[{j}]')
                            shadow_elements.append(element)
                        except:
                            pass
                            
                except Exception as e:
                    logger.debug(f"Shadow root {i} extraction error: {e}")
                    
        except Exception as e:
            logger.debug(f"Shadow DOM extraction error: {e}")
        
        return shadow_elements
    
    async def _extract_iframe_elements(self, page: Page) -> List[ElementHandle]:
        """Extract elements from iframes"""
        iframe_elements = []
        
        try:
            frames = page.frames
            logger.debug(f"Found {len(frames)} frames")
            
            for frame in frames[1:]:  # Skip main frame
                try:
                    await frame.wait_for_load_state('domcontentloaded', timeout=5000)
                    
                    for selector in self.important_selectors[:10]:  # Limit selectors
                        try:
                            elements = await frame.query_selector_all(selector)
                            iframe_elements.extend(elements)
                        except:
                            continue
                            
                except Exception as e:
                    logger.debug(f"Iframe extraction error: {e}")
                    
        except Exception as e:
            logger.debug(f"Iframe processing error: {e}")
        
        return iframe_elements
    
    async def _extract_dynamic_elements(self, context: ExtractionContext) -> List[ElementHandle]:
        """Extract dynamically loaded elements"""
        dynamic_elements = []
        
        try:
            # Set up mutation observer
            await context.page.evaluate("""
                () => {
                    window.__mutationElements = [];
                    
                    const observer = new MutationObserver((mutations) => {
                        mutations.forEach((mutation) => {
                            mutation.addedNodes.forEach((node) => {
                                if (node.nodeType === 1) { // Element node
                                    const tagName = node.tagName?.toLowerCase();
                                    if (['a', 'button', 'input', 'select', 'textarea'].includes(tagName) ||
                                        node.hasAttribute?.('onclick') ||
                                        node.hasAttribute?.('role')) {
                                        window.__mutationElements.push(node);
                                    }
                                }
                            });
                        });
                    });
                    
                    observer.observe(document.body, {
                        childList: true,
                        subtree: true
                    });
                    
                    // Trigger some events
                    document.dispatchEvent(new Event('scroll'));
                    window.dispatchEvent(new Event('resize'));
                }
            """)
            
            # Wait for mutations based on profile
            if self.stealth.profile.profile_type == ProfileType.ULTRA_STEALTH:
                await self.stealth.human_like_delay(delay_type="dynamic_wait")
            elif self.stealth_level == "maximum":
                await self.stealth.human_like_delay(2000, 3000)
            else:
                await context.page.wait_for_timeout(2000)
            
            # Collect mutated elements
            mutation_count = await context.page.evaluate('() => window.__mutationElements?.length || 0')
            for i in range(min(mutation_count, 50)):
                try:
                    element = await context.page.evaluate_handle(f'() => window.__mutationElements[{i}]')
                    dynamic_elements.append(element)
                except:
                    pass
                    
        except Exception as e:
            logger.debug(f"Dynamic element extraction error: {e}")
        
        return dynamic_elements
    
    async def _filter_unique_elements(self, elements: List[ElementHandle], context: ExtractionContext) -> List[ElementHandle]:
        """Filter out duplicate and excluded elements"""
        unique_elements = []
        seen_positions = set()
        
        for element in elements:
            try:
                # Check if element should be excluded
                tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                if tag_name in self.exclude_selectors:
                    continue
                
                # Check position for deduplication (matching ultra-stealth logic)
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
    
    async def _get_element_hash(self, element: ElementHandle) -> str:
        """Generate unique hash for element"""
        try:
            props = await element.evaluate("""
                el => ({
                    tag: el.tagName,
                    id: el.id,
                    className: el.className,
                    text: el.textContent?.substring(0, 50),
                    href: el.href,
                    type: el.type,
                    name: el.name,
                    role: el.getAttribute('role'),
                    dataTestId: el.getAttribute('data-testid')
                })
            """)
            
            # Create hash from significant properties
            hash_str = f"{props['tag']}:{props['id']}:{props['className']}:{props.get('dataTestId', '')}:{props.get('text', '')}"
            return hash_str
        except:
            return str(id(element))
    
    async def _analyze_element(self, element: ElementHandle, context: ExtractionContext) -> Optional[ElementCandidate]:
        """Analyze element and create candidate"""
        try:
            # Get element properties
            properties = await self._get_element_properties(element)
            if not properties:
                return None
            
            # Generate selectors
            selectors = await self._generate_selectors(element, properties, context.page)
            if not selectors:
                return None
            
            # Calculate confidence
            confidence = self._calculate_confidence(selectors, properties)
            
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
                    'framework': properties.get('framework'),
                    'is_shadow_dom': properties.get('is_shadow_dom', False),
                    'is_iframe': properties.get('is_iframe', False),
                    'stability_score': self._calculate_stability_score(selectors),
                    'stealth_level': self.stealth_level
                }
            )
            
            return candidate
            
        except Exception as e:
            logger.debug(f"Element analysis error: {e}")
            return None
    
    async def _get_element_properties(self, element: ElementHandle) -> Optional[Dict[str, Any]]:
        """Get comprehensive element properties"""
        try:
            properties = await element.evaluate(r"""
                (element) => {
                    // Get all attributes
                    const attributes = {};
                    for (const attr of element.attributes || []) {
                        attributes[attr.name] = attr.value;
                    }
                    
                    // Detect framework
                    let framework = null;
                    if (element.hasAttribute('data-reactid') || 
                        element._reactInternalFiber || 
                        element.__reactInternalInstance) {
                        framework = 'react';
                    } else if (element.__vue__ || element._isVue) {
                        framework = 'vue';
                    } else if (element.hasAttribute('ng-') || 
                             attributes['_ngcontent'] !== undefined) {
                        framework = 'angular';
                    }
                    
                    // Check if in shadow DOM
                    const isInShadowDOM = element.getRootNode() instanceof ShadowRoot;
                    
                    // Check if in iframe
                    const isInIframe = window !== window.top;
                    
                    // Get computed properties
                    const style = window.getComputedStyle(element);
                    const rect = element.getBoundingClientRect();
                    
                    // Check for event handlers
                    const hasEventHandlers = 
                        element.onclick || 
                        element.onchange || 
                        element.onsubmit ||
                        Array.from(element.attributes || []).some(attr => 
                            attr.name.startsWith('on') || 
                            attr.name.includes('click') ||
                            attr.name.includes('action')
                        );
                    
                    // Get computed role
                    const computedRole = element.getAttribute('role') || 
                                       element.getAttribute('aria-role') ||
                                       (element.tagName === 'A' && element.href ? 'link' : null) ||
                                       (element.tagName === 'BUTTON' ? 'button' : null);
                    
                    return {
                        tag_name: element.tagName.toLowerCase(),
                        text: element.textContent?.trim() || '',
                        attributes: attributes,
                        classes: element.className ? element.className.split(/\s+/).filter(c => c) : [],
                        computed_role: computedRole,
                        has_event_handlers: hasEventHandlers,
                        is_visible: !!(rect.width && rect.height && 
                                     style.visibility !== 'hidden' && 
                                     style.display !== 'none' &&
                                     style.opacity !== '0'),
                        is_shadow_dom: isInShadowDOM,
                        is_iframe: isInIframe,
                        framework: framework,
                        cursor_style: style.cursor,
                        is_focusable: element.tabIndex >= 0,
                        is_contenteditable: element.contentEditable === 'true',
                        nearest_label: element.labels?.[0]?.textContent || 
                                     element.getAttribute('aria-label') || null
                    };
                }
            """)
            
            return properties
            
        except Exception as e:
            logger.debug(f"Property extraction error: {e}")
            return None
    
    async def _generate_selectors(self, element: ElementHandle, properties: Dict[str, Any], page: Page) -> List[Dict[str, Any]]:
        """Generate multiple selector strategies"""
        selectors = []
        
        # Strategy 1: ID selector (highest priority)
        if properties['attributes'].get('id'):
            element_id = properties['attributes']['id']
            if self._is_valid_id(element_id):
                selectors.append({
                    'type': 'css',
                    'value': f'#{element_id}',
                    'score': 1.0,
                    'strategy': 'id'
                })
        
        # Strategy 2: Data attributes (very reliable)
        for attr in self.selector_preferences[:6]:  # data-* attributes
            if attr in properties['attributes']:
                value = properties['attributes'][attr]
                selectors.append({
                    'type': 'css',
                    'value': f'[{attr}="{value}"]',
                    'score': 0.95,
                    'strategy': 'data-attribute'
                })
        
        # Strategy 3: ARIA attributes
        aria_attrs = ['aria-label', 'aria-labelledby', 'role']
        for attr in aria_attrs:
            if attr in properties['attributes']:
                value = properties['attributes'][attr]
                selectors.append({
                    'type': 'css',
                    'value': f'[{attr}="{value}"]',
                    'score': 0.85,
                    'strategy': 'aria'
                })
        
        # Strategy 4: Unique class combinations
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
        
        # Strategy 5: Text-based selectors
        if properties['tag_name'] in ['button', 'a'] and properties['text']:
            text = properties['text'][:50].replace('"', '\\"')
            selectors.append({
                'type': 'xpath',
                'value': f'//{properties["tag_name"]}[normalize-space(.)="{text}"]',
                'score': 0.6,
                'strategy': 'text'
            })
        
        # Strategy 6: Position-based selector (last resort)
        position_selector = await self._generate_position_selector(element)
        if position_selector:
            selectors.append(position_selector)
        
        # Verify selectors if page is available
        verified_selectors = []
        for selector in selectors:
            if await self._verify_selector(selector, element, page):
                verified_selectors.append(selector)
        
        return verified_selectors if verified_selectors else selectors[:3]  # Return top 3 if none verified
    
    def _is_valid_id(self, element_id: str) -> bool:
        """Check if ID is likely to be stable"""
        # Reject auto-generated IDs
        invalid_patterns = [
            r'^[a-f0-9]{8,}$',  # Hash-like
            r'^ember\d+$',      # Ember.js
            r'^react-select-\d+',  # React
            r'^\d+$',           # Pure numbers
            r'^__',             # Private/internal
            r'^ng-',            # Angular generated
            r'^vue-'            # Vue generated
        ]
        
        for pattern in invalid_patterns:
            if re.match(pattern, element_id.lower()):
                return False
        
        return True
    
    async def _find_unique_class_combination(self, element: ElementHandle, classes: List[str]) -> Optional[List[str]]:
        """Find minimal unique class combination"""
        if not classes:
            return None
        
        # Filter out framework/utility classes
        meaningful_classes = []
        exclude_patterns = [
            r'^[a-f0-9]{8,}$',  # Hash-like
            r'^_',              # Private
            r'^css-\w+$',       # CSS modules
            r'^sc-\w+$',        # Styled components
            r'^v-',             # Vue
            r'^ng-',            # Angular
            r'^col-',           # Bootstrap grid
            r'^row-',           # Bootstrap grid
            r'^btn-\w+$',       # Bootstrap buttons
            r'^text-\w+$',      # Text utilities
            r'^bg-\w+$',        # Background utilities
            r'^is-',            # State classes
            r'^has-'            # State classes
        ]
        
        for cls in classes:
            skip = False
            for pattern in exclude_patterns:
                if re.match(pattern, cls):
                    skip = True
                    break
            
            if not skip and len(cls) > 2:
                meaningful_classes.append(cls)
        
        if not meaningful_classes:
            meaningful_classes = classes[:2]
        
        # Try to find unique combination
        for i in range(min(3, len(meaningful_classes)), 0, -1):
            combination = meaningful_classes[:i]
            selector = '.' + '.'.join(combination)
            
            try:
                count = await element.evaluate(f'el => document.querySelectorAll("{selector}").length')
                if count == 1:
                    return combination
            except:
                continue
        
        return meaningful_classes[:2] if len(meaningful_classes) >= 2 else meaningful_classes
    
    async def _generate_position_selector(self, element: ElementHandle) -> Optional[Dict[str, Any]]:
        """Generate position-based selector as fallback"""
        try:
            result = await element.evaluate("""
                (element) => {
                    const parent = element.parentElement;
                    if (!parent) return null;
                    
                    const siblings = Array.from(parent.children);
                    const index = siblings.indexOf(element) + 1;
                    const tag = element.tagName.toLowerCase();
                    
                    // Build parent path
                    let parentPath = '';
                    let current = parent;
                    let depth = 0;
                    
                    while (current && depth < 3) {
                        if (current.id) {
                            parentPath = `#${current.id} > ` + parentPath;
                            break;
                        } else if (current.className) {
                            const classes = current.className.split(/\\s+/).filter(c => c && c.length > 2);
                            if (classes.length > 0) {
                                parentPath = `.${classes[0]} > ` + parentPath;
                                break;
                            }
                        }
                        
                        parentPath = current.tagName.toLowerCase() + ' > ' + parentPath;
                        current = current.parentElement;
                        depth++;
                    }
                    
                    return {
                        selector: parentPath + tag + ':nth-child(' + index + ')',
                        index: index
                    };
                }
            """)
            
            if result and result['selector']:
                return {
                    'type': 'css',
                    'value': result['selector'],
                    'score': 0.3,
                    'strategy': 'position'
                }
                
        except:
            pass
        
        return None
    
    async def _verify_selector(self, selector: Dict[str, Any], original_element: ElementHandle, page: Page) -> bool:
        """Verify that selector uniquely identifies the element"""
        try:
            if selector['type'] == 'css':
                found = await page.query_selector(selector['value'])
            elif selector['type'] == 'xpath':
                found = await page.query_selector(f'xpath={selector["value"]}')
            else:
                return False
            
            if not found:
                return False
            
            # Verify it's the same element
            is_same = await page.evaluate(
                '(el1, el2) => el1 === el2',
                original_element,
                found
            )
            
            return is_same
            
        except:
            return False
    
    def _calculate_confidence(self, selectors: List[Dict[str, Any]], properties: Dict[str, Any]) -> float:
        """Calculate element confidence score"""
        if not selectors:
            return 0.1
        
        # Base confidence from best selector
        best_score = max(selector['score'] for selector in selectors)
        confidence = best_score * 0.7
        
        # Boost for interactive elements
        if properties['tag_name'] in ['button', 'a', 'input', 'select', 'textarea']:
            confidence += 0.1
        
        # Boost for event handlers
        if properties.get('has_event_handlers'):
            confidence += 0.1
        
        # Boost for visible elements
        if properties.get('is_visible'):
            confidence += 0.05
        
        # Boost for accessible elements
        if properties.get('computed_role') or properties.get('nearest_label'):
            confidence += 0.05
        
        # Apply stealth level boost
        confidence += self.get_confidence_boost() * 0.1
        
        return min(confidence, 0.95)
    
    def _calculate_stability_score(self, selectors: List[Dict[str, Any]]) -> float:
        """Calculate selector stability score"""
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
            score = selector.get('score', 0.5) * weight
            total_score += score
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    async def _find_more_dynamic_elements(self, context: ExtractionContext) -> List[ElementHandle]:
        """Find additional dynamic elements using ultra-stealth approach"""
        dynamic_elements = []
        
        try:
            # Trigger events to reveal dynamic content
            await context.page.evaluate("""
                () => {
                    // Trigger scroll event
                    window.dispatchEvent(new Event('scroll'));
                    
                    // Trigger resize event
                    window.dispatchEvent(new Event('resize'));
                    
                    // Mouse over common areas
                    const nav = document.querySelector('nav, header');
                    if (nav) {
                        nav.dispatchEvent(new MouseEvent('mouseenter', {
                            bubbles: true,
                            cancelable: true
                        }));
                    }
                }
            """)
            
            # Wait for potential changes
            await self.stealth.human_like_delay(delay_type="dynamic_wait")
            
            # Look for common dynamic element patterns
            dynamic_selectors = [
                '[data-dynamic]',
                '[ng-repeat]',
                '[v-for]',
                '[*ngFor]',
                '.lazy-load',
                '[data-react-component]'
            ]
            
            for selector in dynamic_selectors:
                try:
                    elements = await context.page.query_selector_all(selector)
                    dynamic_elements.extend(elements)
                except:
                    continue
        
        except Exception as e:
            logger.debug(f"More dynamic elements extraction: {e}")
        
        return dynamic_elements
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    
    def get_stats(self) -> Dict[str, Any]:
        """Get extraction statistics"""
        return self.stats.copy()