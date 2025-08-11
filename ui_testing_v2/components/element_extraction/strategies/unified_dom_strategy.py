"""
Unified DOM Strategy - Consolidates DOM extraction logic from multiple sources.
Combines features from dom_strategy.py, dom_extractor.py, and stealth capabilities.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from playwright.async_api import Page, Browser, BrowserContext
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

from ..extraction_utils import (
    ElementType, InteractionType, SelectorGenerator,
    ElementTypeDetector, ConfidenceCalculator, ElementValidator,
    StealthUtilities, ExtractionMetrics
)

logger = logging.getLogger(__name__)


@dataclass
class DOMExtractionConfig:
    """Configuration for DOM extraction with stealth options"""
    enable_stealth: bool = False
    enable_shadow_dom: bool = True
    enable_iframe_traversal: bool = True
    enable_dynamic_wait: bool = True
    enable_mutation_observer: bool = True
    max_depth: int = 10
    max_elements: int = 1000
    extraction_timeout: int = 30000
    viewport_size: Optional[Dict[str, int]] = None
    user_agent: Optional[str] = None
    handle_cookie_consent: bool = True
    extract_computed_styles: bool = True
    extract_accessibility_tree: bool = True
    filter_invisible: bool = True
    filter_duplicates: bool = True


class UnifiedDOMStrategy:
    """
    Unified DOM extraction strategy combining best practices from multiple implementations.
    Supports both Playwright and Selenium with configurable stealth features.
    """
    
    def __init__(self, config: Optional[DOMExtractionConfig] = None):
        self.config = config or DOMExtractionConfig()
        self.selector_generator = SelectorGenerator()
        self.type_detector = ElementTypeDetector()
        self.confidence_calculator = ConfidenceCalculator()
        self.validator = ElementValidator()
        self._extraction_stats = {}
        
    async def extract_playwright(self, page: Page) -> List[Dict[str, Any]]:
        """Extract elements using Playwright with advanced features"""
        try:
            # Apply stealth configuration if enabled
            if self.config.enable_stealth:
                await self._apply_stealth_playwright(page)
            
            # Handle cookie consent if configured
            if self.config.handle_cookie_consent:
                await self._handle_cookie_consent_playwright(page)
            
            # Wait for dynamic content if configured
            if self.config.enable_dynamic_wait:
                await self._wait_for_stability_playwright(page)
            
            # Extract DOM elements
            elements = await self._extract_dom_elements_playwright(page)
            
            # Extract shadow DOM if enabled
            if self.config.enable_shadow_dom:
                shadow_elements = await self._extract_shadow_dom_playwright(page)
                elements.extend(shadow_elements)
            
            # Extract iframe content if enabled
            if self.config.enable_iframe_traversal:
                iframe_elements = await self._extract_iframe_content_playwright(page)
                elements.extend(iframe_elements)
            
            # Process and enrich elements
            processed_elements = await self._process_elements(elements, page)
            
            # Filter based on configuration
            if self.config.filter_invisible:
                processed_elements = [e for e in processed_elements if self.validator.is_visible_element(e)]
            
            if self.config.filter_duplicates:
                processed_elements = self.validator.filter_duplicate_elements(processed_elements)
            
            # Calculate extraction statistics
            self._extraction_stats = ExtractionMetrics.calculate_extraction_stats(processed_elements)
            
            return processed_elements[:self.config.max_elements]
            
        except Exception as e:
            logger.error(f"Error in Playwright DOM extraction: {e}")
            return []
    
    def extract_selenium(self, driver: WebDriver) -> List[Dict[str, Any]]:
        """Extract elements using Selenium with advanced features"""
        try:
            # Apply stealth configuration if enabled
            if self.config.enable_stealth:
                self._apply_stealth_selenium(driver)
            
            # Handle cookie consent if configured
            if self.config.handle_cookie_consent:
                self._handle_cookie_consent_selenium(driver)
            
            # Wait for dynamic content if configured
            if self.config.enable_dynamic_wait:
                self._wait_for_stability_selenium(driver)
            
            # Extract DOM elements
            elements = self._extract_dom_elements_selenium(driver)
            
            # Extract shadow DOM if enabled
            if self.config.enable_shadow_dom:
                shadow_elements = self._extract_shadow_dom_selenium(driver)
                elements.extend(shadow_elements)
            
            # Process and enrich elements
            processed_elements = self._process_elements_selenium(elements, driver)
            
            # Filter based on configuration
            if self.config.filter_invisible:
                processed_elements = [e for e in processed_elements if self.validator.is_visible_element(e)]
            
            if self.config.filter_duplicates:
                processed_elements = self.validator.filter_duplicate_elements(processed_elements)
            
            # Calculate extraction statistics
            self._extraction_stats = ExtractionMetrics.calculate_extraction_stats(processed_elements)
            
            return processed_elements[:self.config.max_elements]
            
        except Exception as e:
            logger.error(f"Error in Selenium DOM extraction: {e}")
            return []
    
    async def _apply_stealth_playwright(self, page: Page):
        """Apply stealth techniques for Playwright"""
        # Set random user agent if not specified
        if not self.config.user_agent:
            self.config.user_agent = StealthUtilities.get_random_user_agent()
        
        # Set random viewport if not specified
        if not self.config.viewport_size:
            self.config.viewport_size = StealthUtilities.get_random_viewport()
        
        await page.set_viewport_size(self.config.viewport_size)
        
        # Override navigator properties
        await page.add_init_script("""
            // Override navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override navigator.plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override navigator.languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Override chrome runtime
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {}
            };
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
    
    def _apply_stealth_selenium(self, driver: WebDriver):
        """Apply stealth techniques for Selenium"""
        # Execute stealth JavaScript
        driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
    
    async def _handle_cookie_consent_playwright(self, page: Page):
        """Handle cookie consent banners in Playwright"""
        for selector in StealthUtilities.COOKIE_SELECTORS:
            try:
                element = await page.wait_for_selector(selector, timeout=2000)
                if element:
                    await element.click()
                    await asyncio.sleep(StealthUtilities.calculate_human_delay())
                    break
            except:
                continue
    
    def _handle_cookie_consent_selenium(self, driver: WebDriver):
        """Handle cookie consent banners in Selenium"""
        import time
        for selector in StealthUtilities.COOKIE_SELECTORS:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].is_displayed():
                    elements[0].click()
                    time.sleep(StealthUtilities.calculate_human_delay())
                    break
            except:
                continue
    
    async def _wait_for_stability_playwright(self, page: Page):
        """Wait for page to stabilize in Playwright"""
        # Wait for network idle
        await page.wait_for_load_state('networkidle', timeout=self.config.extraction_timeout)
        
        # Wait for any animations to complete
        await page.evaluate("""
            () => new Promise((resolve) => {
                if (document.readyState === 'complete') {
                    // Check for ongoing animations
                    const checkAnimations = () => {
                        const animations = document.getAnimations();
                        if (animations.length === 0) {
                            resolve();
                        } else {
                            setTimeout(checkAnimations, 100);
                        }
                    };
                    setTimeout(checkAnimations, 100);
                } else {
                    window.addEventListener('load', () => setTimeout(resolve, 100));
                }
            })
        """)
    
    def _wait_for_stability_selenium(self, driver: WebDriver):
        """Wait for page to stabilize in Selenium"""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        wait = WebDriverWait(driver, self.config.extraction_timeout / 1000)
        
        # Wait for document ready
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        
        # Wait for jQuery if present
        driver.execute_script("""
            if (typeof jQuery !== 'undefined') {
                return jQuery.active == 0;
            }
            return true;
        """)
    
    async def _extract_dom_elements_playwright(self, page: Page) -> List[Dict[str, Any]]:
        """Extract DOM elements using Playwright"""
        elements_data = await page.evaluate("""
            () => {
                const elements = [];
                const visited = new Set();
                
                function extractElement(element, depth = 0) {
                    if (depth > 10 || visited.has(element)) return null;
                    visited.add(element);
                    
                    const rect = element.getBoundingClientRect();
                    const styles = window.getComputedStyle(element);
                    
                    // Extract attributes
                    const attributes = {};
                    for (const attr of element.attributes) {
                        attributes[attr.name] = attr.value;
                    }
                    
                    // Extract event listeners
                    const eventTypes = ['click', 'change', 'input', 'submit', 'focus', 'blur'];
                    const hasListeners = {};
                    for (const eventType of eventTypes) {
                        const listeners = getEventListeners ? getEventListeners(element)[eventType] : null;
                        hasListeners[eventType] = listeners && listeners.length > 0;
                    }
                    
                    return {
                        tag_name: element.tagName.toLowerCase(),
                        text: element.textContent?.trim().substring(0, 200),
                        attributes: attributes,
                        bounding_box: {
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height,
                            top: rect.top,
                            bottom: rect.bottom,
                            left: rect.left,
                            right: rect.right
                        },
                        computed_style: {
                            display: styles.display,
                            visibility: styles.visibility,
                            opacity: styles.opacity,
                            position: styles.position,
                            zIndex: styles.zIndex,
                            backgroundColor: styles.backgroundColor,
                            color: styles.color,
                            fontSize: styles.fontSize,
                            fontWeight: styles.fontWeight
                        },
                        is_visible: rect.width > 0 && rect.height > 0 && 
                                   styles.display !== 'none' && 
                                   styles.visibility !== 'hidden',
                        is_enabled: !element.disabled,
                        is_clickable: element.onclick !== null || hasListeners.click,
                        has_listeners: hasListeners,
                        xpath: getXPath(element),
                        css_path: getCSSPath(element)
                    };
                }
                
                function getXPath(element) {
                    if (element.id) return `//*[@id="${element.id}"]`;
                    if (element === document.body) return '/html/body';
                    
                    let ix = 0;
                    const siblings = element.parentNode?.childNodes;
                    if (siblings) {
                        for (let i = 0; i < siblings.length; i++) {
                            const sibling = siblings[i];
                            if (sibling === element) {
                                return getXPath(element.parentNode) + '/' + 
                                       element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                            }
                            if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                                ix++;
                            }
                        }
                    }
                    return '';
                }
                
                function getCSSPath(element) {
                    const path = [];
                    while (element && element.nodeType === Node.ELEMENT_NODE) {
                        let selector = element.tagName.toLowerCase();
                        if (element.id) {
                            selector += '#' + element.id;
                            path.unshift(selector);
                            break;
                        } else if (element.className) {
                            selector += '.' + element.className.trim().split(/\s+/).join('.');
                        }
                        path.unshift(selector);
                        element = element.parentNode;
                    }
                    return path.join(' > ');
                }
                
                // Get all interactive and potentially important elements
                const selectors = [
                    'a', 'button', 'input', 'select', 'textarea',
                    '[role="button"]', '[role="link"]', '[role="textbox"]',
                    '[onclick]', '[ng-click]', '[data-click]', '[data-action]',
                    'label', 'form', 'iframe', 'video', 'audio', 'canvas',
                    '[contenteditable="true"]', '[tabindex]'
                ];
                
                const allElements = document.querySelectorAll(selectors.join(', '));
                
                for (const element of allElements) {
                    const data = extractElement(element);
                    if (data) {
                        elements.push(data);
                    }
                }
                
                return elements;
            }
        """)
        
        return elements_data
    
    def _extract_dom_elements_selenium(self, driver: WebDriver) -> List[Dict[str, Any]]:
        """Extract DOM elements using Selenium"""
        script = """
            const elements = [];
            const selectors = [
                'a', 'button', 'input', 'select', 'textarea',
                '[role="button"]', '[role="link"]', '[role="textbox"]',
                '[onclick]', 'label', 'form'
            ];
            
            const allElements = document.querySelectorAll(selectors.join(', '));
            
            for (const element of allElements) {
                const rect = element.getBoundingClientRect();
                const styles = window.getComputedStyle(element);
                const attributes = {};
                
                for (const attr of element.attributes) {
                    attributes[attr.name] = attr.value;
                }
                
                elements.push({
                    tag_name: element.tagName.toLowerCase(),
                    text: element.textContent?.trim().substring(0, 200),
                    attributes: attributes,
                    bounding_box: {
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height
                    },
                    computed_style: {
                        display: styles.display,
                        visibility: styles.visibility,
                        opacity: styles.opacity
                    },
                    is_visible: rect.width > 0 && rect.height > 0,
                    is_enabled: !element.disabled
                });
            }
            
            return elements;
        """
        
        return driver.execute_script(script)
    
    async def _extract_shadow_dom_playwright(self, page: Page) -> List[Dict[str, Any]]:
        """Extract elements from shadow DOM using Playwright"""
        shadow_elements = await page.evaluate("""
            () => {
                const elements = [];
                
                function extractFromShadowRoot(root, depth = 0) {
                    if (depth > 5) return;
                    
                    const shadowHosts = root.querySelectorAll('*');
                    for (const host of shadowHosts) {
                        if (host.shadowRoot) {
                            // Extract elements from shadow root
                            const shadowElements = host.shadowRoot.querySelectorAll('*');
                            for (const element of shadowElements) {
                                const rect = element.getBoundingClientRect();
                                if (rect.width > 0 && rect.height > 0) {
                                    elements.push({
                                        tag_name: element.tagName.toLowerCase(),
                                        text: element.textContent?.trim().substring(0, 200),
                                        is_shadow_element: true,
                                        shadow_host: host.tagName.toLowerCase(),
                                        bounding_box: {
                                            x: rect.x,
                                            y: rect.y,
                                            width: rect.width,
                                            height: rect.height
                                        }
                                    });
                                }
                            }
                            // Recursively check for nested shadow roots
                            extractFromShadowRoot(host.shadowRoot, depth + 1);
                        }
                    }
                }
                
                extractFromShadowRoot(document, 0);
                return elements;
            }
        """)
        
        return shadow_elements
    
    def _extract_shadow_dom_selenium(self, driver: WebDriver) -> List[Dict[str, Any]]:
        """Extract elements from shadow DOM using Selenium"""
        script = """
            const elements = [];
            const shadowHosts = document.querySelectorAll('*');
            
            for (const host of shadowHosts) {
                if (host.shadowRoot) {
                    const shadowElements = host.shadowRoot.querySelectorAll('*');
                    for (const element of shadowElements) {
                        const rect = element.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            elements.push({
                                tag_name: element.tagName.toLowerCase(),
                                text: element.textContent?.trim().substring(0, 200),
                                is_shadow_element: true,
                                shadow_host: host.tagName.toLowerCase()
                            });
                        }
                    }
                }
            }
            
            return elements;
        """
        
        return driver.execute_script(script)
    
    async def _extract_iframe_content_playwright(self, page: Page) -> List[Dict[str, Any]]:
        """Extract content from iframes using Playwright"""
        iframe_elements = []
        
        frames = page.frames
        for frame in frames[1:]:  # Skip main frame
            try:
                frame_elements = await frame.evaluate("""
                    () => {
                        const elements = [];
                        const allElements = document.querySelectorAll('a, button, input, select, textarea');
                        
                        for (const element of allElements) {
                            const rect = element.getBoundingClientRect();
                            elements.push({
                                tag_name: element.tagName.toLowerCase(),
                                text: element.textContent?.trim().substring(0, 200),
                                is_iframe_element: true,
                                frame_url: window.location.href,
                                bounding_box: {
                                    x: rect.x,
                                    y: rect.y,
                                    width: rect.width,
                                    height: rect.height
                                }
                            });
                        }
                        
                        return elements;
                    }
                """)
                iframe_elements.extend(frame_elements)
            except Exception as e:
                logger.debug(f"Could not extract from iframe: {e}")
        
        return iframe_elements
    
    async def _process_elements(self, elements: List[Dict[str, Any]], page: Page) -> List[Dict[str, Any]]:
        """Process and enrich extracted elements with Playwright"""
        processed = []
        
        for element in elements:
            try:
                # Generate selectors
                css_selectors = self.selector_generator.generate_css_selector(element)
                xpath_selectors = self.selector_generator.generate_xpath_selector(element)
                element['selectors'] = css_selectors + xpath_selectors
                
                # Determine element type
                element_type = self.type_detector.determine_element_type(
                    element.get('tag_name', ''),
                    element.get('attributes', {})
                )
                element['element_type'] = element_type.value
                
                # Determine interaction types
                interaction_types = self.type_detector.determine_interaction_type(
                    element_type,
                    element.get('attributes', {})
                )
                element['interaction_types'] = [it.value for it in interaction_types]
                
                # Calculate confidence score
                confidence = self.confidence_calculator.calculate_element_confidence(
                    element.get('selectors', []),
                    element,
                    element_type
                )
                element['confidence'] = confidence
                
                # Calculate stability score
                stability = self.confidence_calculator.calculate_stability_score(element)
                element['stability_score'] = stability
                
                # Validate element
                is_valid, issues = self.validator.validate_element_data(element)
                element['is_valid'] = is_valid
                if not is_valid:
                    element['validation_issues'] = issues
                
                # Add extraction metadata
                element['extraction_method'] = 'unified_dom'
                element['extraction_timestamp'] = asyncio.get_event_loop().time()
                
                processed.append(element)
                
            except Exception as e:
                logger.debug(f"Error processing element: {e}")
                continue
        
        return processed
    
    def _process_elements_selenium(self, elements: List[Dict[str, Any]], driver: WebDriver) -> List[Dict[str, Any]]:
        """Process and enrich extracted elements with Selenium"""
        processed = []
        
        for element in elements:
            try:
                # Generate selectors
                css_selectors = self.selector_generator.generate_css_selector(element)
                xpath_selectors = self.selector_generator.generate_xpath_selector(element)
                element['selectors'] = css_selectors + xpath_selectors
                
                # Determine element type
                element_type = self.type_detector.determine_element_type(
                    element.get('tag_name', ''),
                    element.get('attributes', {})
                )
                element['element_type'] = element_type.value
                
                # Determine interaction types
                interaction_types = self.type_detector.determine_interaction_type(
                    element_type,
                    element.get('attributes', {})
                )
                element['interaction_types'] = [it.value for it in interaction_types]
                
                # Calculate confidence score
                confidence = self.confidence_calculator.calculate_element_confidence(
                    element.get('selectors', []),
                    element,
                    element_type
                )
                element['confidence'] = confidence
                
                # Calculate stability score
                stability = self.confidence_calculator.calculate_stability_score(element)
                element['stability_score'] = stability
                
                # Add extraction metadata
                element['extraction_method'] = 'unified_dom'
                
                processed.append(element)
                
            except Exception as e:
                logger.debug(f"Error processing element: {e}")
                continue
        
        return processed
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get statistics from the last extraction"""
        return self._extraction_stats