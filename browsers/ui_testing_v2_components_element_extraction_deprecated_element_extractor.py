"""
Element extractor module for browser automation with AI-powered analysis.
Provides element extraction using multiple strategies and intelligent element identification.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from urllib.parse import urljoin, urlparse
import hashlib

from playwright.async_api import Browser, BrowserContext, Page, Error as PlaywrightError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from ui_testing_v2.models.database import ExtractedElement, ElementType, ElementInteractionType
from ui_testing_v2.services.ai_services import AIService, AIServiceFactory
from ui_testing_v2.services.cache import CacheService, CacheKey
from ui_testing_v2.core.config import Config

logger = logging.getLogger(__name__)


class ElementExtractionStrategy(ABC):
    """Abstract base class for element extraction strategies"""
    
    @abstractmethod
    async def extract_elements(
        self, 
        page: Union[Page, webdriver.Remote], 
        selectors: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Extract elements from the page"""
        pass
    
    @abstractmethod
    async def get_element_attributes(
        self, 
        element: Union[Any, WebElement], 
        page: Union[Page, webdriver.Remote]
    ) -> Dict[str, Any]:
        """Get detailed attributes for an element"""
        pass


class PlaywrightExtractionStrategy(ElementExtractionStrategy):
    """Element extraction using Playwright"""
    
    def __init__(self, config: Config):
        self.config = config
        self.timeout = config.playwright.timeout * 1000  # Convert to milliseconds
    
    async def extract_elements(
        self, 
        page: Page, 
        selectors: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Extract elements using Playwright"""
        try:
            if selectors is None:
                # Default selectors for interactive elements
                selectors = [
                    'button', 'input', 'select', 'textarea', 'a[href]',
                    '[onclick]', '[role="button"]', '[type="submit"]',
                    '[type="button"]', '[data-testid]', '[aria-label]',
                    'form', '[contenteditable]'
                ]
            
            elements = []
            processed_elements = set()
            
            for selector in selectors:
                try:
                    # Find elements matching the selector
                    element_handles = await page.query_selector_all(selector)
                    
                    for handle in element_handles:
                        try:
                            # Get element hash to avoid duplicates
                            element_id = await self._get_element_id(handle)
                            if element_id in processed_elements:
                                continue
                            
                            processed_elements.add(element_id)
                            
                            # Extract element attributes
                            attributes = await self.get_element_attributes(handle, page)
                            if attributes:
                                elements.append(attributes)
                                
                        except Exception as e:
                            logger.debug(f"Error processing element in selector '{selector}': {e}")
                            continue
                            
                except Exception as e:
                    logger.debug(f"Error with selector '{selector}': {e}")
                    continue
            
            logger.info(f"Extracted {len(elements)} elements using Playwright")
            return elements
            
        except Exception as e:
            logger.error(f"Playwright element extraction failed: {e}")
            raise
    
    async def get_element_attributes(
        self, 
        element_handle, 
        page: Page
    ) -> Optional[Dict[str, Any]]:
        """Get detailed attributes for a Playwright element"""
        try:
            # Check if element is visible and interactable
            is_visible = await element_handle.is_visible()
            if not is_visible:
                return None
            
            # Get basic properties
            tag_name = await element_handle.evaluate("el => el.tagName.toLowerCase()")
            text_content = await element_handle.text_content() or ""
            inner_text = await element_handle.inner_text() or ""
            
            # Get bounding box
            bbox = await element_handle.bounding_box()
            
            # Get all attributes
            attributes = await element_handle.evaluate("""
                el => {
                    const attrs = {};
                    for (let attr of el.attributes) {
                        attrs[attr.name] = attr.value;
                    }
                    return attrs;
                }
            """)
            
            # Get computed styles for visibility and interactability
            computed_styles = await element_handle.evaluate("""
                el => {
                    const styles = window.getComputedStyle(el);
                    return {
                        display: styles.display,
                        visibility: styles.visibility,
                        opacity: styles.opacity,
                        pointerEvents: styles.pointerEvents,
                        position: styles.position,
                        zIndex: styles.zIndex
                    };
                }
            """)
            
            # Generate CSS selector
            css_selector = await element_handle.evaluate("""
                el => {
                    function getSelector(element) {
                        if (element.id) return '#' + element.id;
                        
                        let path = [];
                        let current = element;
                        
                        while (current && current.nodeType === Node.ELEMENT_NODE) {
                            let selector = current.tagName.toLowerCase();
                            
                            if (current.className) {
                                selector += '.' + current.className.split(' ').join('.');
                            }
                            
                            // Add nth-child if needed for uniqueness
                            if (current.parentNode) {
                                let siblings = Array.from(current.parentNode.children)
                                    .filter(sibling => sibling.tagName === current.tagName);
                                if (siblings.length > 1) {
                                    let index = siblings.indexOf(current) + 1;
                                    selector += `:nth-child(${index})`;
                                }
                            }
                            
                            path.unshift(selector);
                            current = current.parentElement;
                            
                            // Stop if we have enough specificity
                            if (element.id || path.length > 3) break;
                        }
                        
                        return path.join(' > ');
                    }
                    
                    return getSelector(el);
                }
            """)
            
            # Determine element type and interaction type
            element_type = self._determine_element_type(tag_name, attributes)
            interaction_type = self._determine_interaction_type(tag_name, attributes)
            
            # Calculate element stability score
            stability_score = await self._calculate_stability_score(element_handle)
            
            return {
                'tag_name': tag_name,
                'text': text_content.strip(),
                'inner_text': inner_text.strip(),
                'attributes': attributes,
                'css_selector': css_selector,
                'xpath': await self._generate_xpath(element_handle),
                'bounding_box': bbox,
                'computed_styles': computed_styles,
                'element_type': element_type,
                'interaction_type': interaction_type,
                'is_visible': is_visible,
                'is_enabled': await element_handle.is_enabled(),
                'is_editable': await element_handle.is_editable(),
                'stability_score': stability_score,
                'extraction_timestamp': datetime.now(timezone.utc).isoformat(),
                'extraction_method': 'playwright'
            }
            
        except Exception as e:
            logger.debug(f"Error getting element attributes: {e}")
            return None
    
    async def _get_element_id(self, element_handle) -> str:
        """Generate unique ID for element to avoid duplicates"""
        try:
            # Get element properties for hashing
            tag_name = await element_handle.evaluate("el => el.tagName")
            outer_html = await element_handle.evaluate("el => el.outerHTML")
            bbox = await element_handle.bounding_box()
            
            # Create hash from properties
            hash_input = f"{tag_name}:{outer_html}:{bbox}"
            return hashlib.md5(hash_input.encode()).hexdigest()
        except:
            # Fallback to timestamp-based ID
            return f"element_{datetime.now().timestamp()}"
    
    async def _generate_xpath(self, element_handle) -> str:
        """Generate XPath for element"""
        try:
            xpath = await element_handle.evaluate("""
                el => {
                    function getXPath(element) {
                        if (element.id) {
                            return `//*[@id='${element.id}']`;
                        }
                        
                        let path = '';
                        let current = element;
                        
                        while (current && current.nodeType === Node.ELEMENT_NODE) {
                            let tagName = current.tagName.toLowerCase();
                            let index = 1;
                            
                            // Count preceding siblings with same tag
                            let sibling = current.previousElementSibling;
                            while (sibling) {
                                if (sibling.tagName.toLowerCase() === tagName) {
                                    index++;
                                }
                                sibling = sibling.previousElementSibling;
                            }
                            
                            path = `/${tagName}[${index}]${path}`;
                            current = current.parentElement;
                        }
                        
                        return path;
                    }
                    
                    return getXPath(el);
                }
            """)
            return xpath
        except:
            return ""
    
    async def _calculate_stability_score(self, element_handle) -> float:
        """Calculate stability score for element (0.0 to 1.0)"""
        try:
            score = 0.0
            
            # Check for stable attributes
            attributes = await element_handle.evaluate("el => Array.from(el.attributes).map(a => a.name)")
            
            if 'id' in attributes:
                score += 0.4
            if 'data-testid' in attributes:
                score += 0.3
            if 'name' in attributes:
                score += 0.2
            if any(attr.startswith('data-') for attr in attributes):
                score += 0.1
            
            # Check for stable text content
            text_content = await element_handle.text_content()
            if text_content and len(text_content.strip()) > 0:
                score += 0.1
            
            return min(score, 1.0)
        except:
            return 0.5  # Default score
    
    def _determine_element_type(self, tag_name: str, attributes: Dict[str, str]) -> ElementType:
        """Determine the element type based on tag and attributes"""
        tag_name = tag_name.lower()
        
        if tag_name == 'button' or attributes.get('type') == 'button':
            return ElementType.BUTTON
        elif tag_name == 'input':
            input_type = attributes.get('type', 'text').lower()
            if input_type in ['text', 'email', 'password', 'search', 'url', 'tel']:
                return ElementType.INPUT
            elif input_type in ['checkbox']:
                return ElementType.CHECKBOX
            elif input_type in ['radio']:
                return ElementType.RADIO
            elif input_type in ['submit', 'button']:
                return ElementType.BUTTON
        elif tag_name == 'select':
            return ElementType.SELECT
        elif tag_name == 'textarea':
            return ElementType.TEXTAREA
        elif tag_name == 'a' and 'href' in attributes:
            return ElementType.LINK
        elif tag_name == 'form':
            return ElementType.FORM
        elif attributes.get('role') == 'button':
            return ElementType.BUTTON
        elif attributes.get('contenteditable') == 'true':
            return ElementType.INPUT
        
        return ElementType.OTHER
    
    def _determine_interaction_type(self, tag_name: str, attributes: Dict[str, str]) -> ElementInteractionType:
        """Determine the interaction type for element"""
        element_type = self._determine_element_type(tag_name, attributes)
        
        if element_type in [ElementType.BUTTON]:
            return ElementInteractionType.CLICK
        elif element_type in [ElementType.INPUT, ElementType.TEXTAREA]:
            return ElementInteractionType.TYPE
        elif element_type == ElementType.SELECT:
            return ElementInteractionType.SELECT
        elif element_type == ElementType.CHECKBOX:
            return ElementInteractionType.CHECK
        elif element_type == ElementType.RADIO:
            return ElementInteractionType.SELECT
        elif element_type == ElementType.LINK:
            return ElementInteractionType.CLICK
        elif 'onclick' in attributes:
            return ElementInteractionType.CLICK
        
        return ElementInteractionType.CLICK


class SeleniumExtractionStrategy(ElementExtractionStrategy):
    """Element extraction using Selenium"""
    
    def __init__(self, config: Config):
        self.config = config
        self.timeout = config.selenium.timeout
    
    async def extract_elements(
        self, 
        driver: webdriver.Remote, 
        selectors: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Extract elements using Selenium"""
        try:
            if selectors is None:
                # Default CSS selectors for interactive elements
                selectors = [
                    'button', 'input', 'select', 'textarea', 'a[href]',
                    '[onclick]', '[role="button"]', '[type="submit"]',
                    '[type="button"]', '[data-testid]', '[aria-label]',
                    'form', '[contenteditable]'
                ]
            
            elements = []
            processed_elements = set()
            
            for selector in selectors:
                try:
                    # Find elements matching the CSS selector
                    web_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in web_elements:
                        try:
                            # Get element hash to avoid duplicates
                            element_id = self._get_element_id(element)
                            if element_id in processed_elements:
                                continue
                            
                            processed_elements.add(element_id)
                            
                            # Extract element attributes
                            attributes = await self.get_element_attributes(element, driver)
                            if attributes:
                                elements.append(attributes)
                                
                        except Exception as e:
                            logger.debug(f"Error processing element in selector '{selector}': {e}")
                            continue
                            
                except Exception as e:
                    logger.debug(f"Error with selector '{selector}': {e}")
                    continue
            
            logger.info(f"Extracted {len(elements)} elements using Selenium")
            return elements
            
        except Exception as e:
            logger.error(f"Selenium element extraction failed: {e}")
            raise
    
    async def get_element_attributes(
        self, 
        element: WebElement, 
        driver: webdriver.Remote
    ) -> Optional[Dict[str, Any]]:
        """Get detailed attributes for a Selenium element"""
        try:
            # Check if element is visible and interactable
            if not element.is_displayed():
                return None
            
            # Get basic properties
            tag_name = element.tag_name.lower()
            text_content = element.text or ""
            
            # Get all attributes using JavaScript
            attributes = driver.execute_script("""
                var element = arguments[0];
                var attrs = {};
                for (var i = 0; i < element.attributes.length; i++) {
                    var attr = element.attributes[i];
                    attrs[attr.name] = attr.value;
                }
                return attrs;
            """, element)
            
            # Get bounding box
            location = element.location
            size = element.size
            bbox = {
                'x': location['x'],
                'y': location['y'],
                'width': size['width'],
                'height': size['height']
            }
            
            # Get computed styles
            computed_styles = driver.execute_script("""
                var element = arguments[0];
                var styles = window.getComputedStyle(element);
                return {
                    display: styles.display,
                    visibility: styles.visibility,
                    opacity: styles.opacity,
                    pointerEvents: styles.pointerEvents,
                    position: styles.position,
                    zIndex: styles.zIndex
                };
            """, element)
            
            # Generate CSS selector
            css_selector = driver.execute_script("""
                function getSelector(element) {
                    if (element.id) return '#' + element.id;
                    
                    var path = [];
                    var current = element;
                    
                    while (current && current.nodeType === Node.ELEMENT_NODE) {
                        var selector = current.tagName.toLowerCase();
                        
                        if (current.className) {
                            selector += '.' + current.className.split(' ').join('.');
                        }
                        
                        // Add nth-child if needed for uniqueness
                        if (current.parentNode) {
                            var siblings = Array.from(current.parentNode.children)
                                .filter(function(sibling) { return sibling.tagName === current.tagName; });
                            if (siblings.length > 1) {
                                var index = siblings.indexOf(current) + 1;
                                selector += ':nth-child(' + index + ')';
                            }
                        }
                        
                        path.unshift(selector);
                        current = current.parentElement;
                        
                        // Stop if we have enough specificity
                        if (element.id || path.length > 3) break;
                    }
                    
                    return path.join(' > ');
                }
                
                return getSelector(arguments[0]);
            """, element)
            
            # Generate XPath
            xpath = self._generate_xpath_selenium(driver, element)
            
            # Determine element type and interaction type
            element_type = self._determine_element_type(tag_name, attributes)
            interaction_type = self._determine_interaction_type(tag_name, attributes)
            
            # Calculate stability score
            stability_score = self._calculate_stability_score_selenium(attributes, text_content)
            
            return {
                'tag_name': tag_name,
                'text': text_content.strip(),
                'inner_text': text_content.strip(),
                'attributes': attributes,
                'css_selector': css_selector,
                'xpath': xpath,
                'bounding_box': bbox,
                'computed_styles': computed_styles,
                'element_type': element_type,
                'interaction_type': interaction_type,
                'is_visible': element.is_displayed(),
                'is_enabled': element.is_enabled(),
                'is_editable': tag_name in ['input', 'textarea'] or attributes.get('contenteditable') == 'true',
                'stability_score': stability_score,
                'extraction_timestamp': datetime.now(timezone.utc).isoformat(),
                'extraction_method': 'selenium'
            }
            
        except Exception as e:
            logger.debug(f"Error getting element attributes: {e}")
            return None
    
    def _get_element_id(self, element: WebElement) -> str:
        """Generate unique ID for element to avoid duplicates"""
        try:
            # Get element properties for hashing
            tag_name = element.tag_name
            location = element.location
            size = element.size
            text = element.text
            
            # Create hash from properties
            hash_input = f"{tag_name}:{location}:{size}:{text}"
            return hashlib.md5(hash_input.encode()).hexdigest()
        except:
            # Fallback to timestamp-based ID
            return f"element_{datetime.now().timestamp()}"
    
    def _generate_xpath_selenium(self, driver: webdriver.Remote, element: WebElement) -> str:
        """Generate XPath for Selenium element"""
        try:
            xpath = driver.execute_script("""
                function getXPath(element) {
                    if (element.id) {
                        return "//*[@id='" + element.id + "']";
                    }
                    
                    var path = '';
                    var current = element;
                    
                    while (current && current.nodeType === Node.ELEMENT_NODE) {
                        var tagName = current.tagName.toLowerCase();
                        var index = 1;
                        
                        // Count preceding siblings with same tag
                        var sibling = current.previousElementSibling;
                        while (sibling) {
                            if (sibling.tagName.toLowerCase() === tagName) {
                                index++;
                            }
                            sibling = sibling.previousElementSibling;
                        }
                        
                        path = '/' + tagName + '[' + index + ']' + path;
                        current = current.parentElement;
                    }
                    
                    return path;
                }
                
                return getXPath(arguments[0]);
            """, element)
            return xpath
        except:
            return ""
    
    def _calculate_stability_score_selenium(self, attributes: Dict[str, str], text_content: str) -> float:
        """Calculate stability score for Selenium element"""
        score = 0.0
        
        if 'id' in attributes and attributes['id']:
            score += 0.4
        if 'data-testid' in attributes:
            score += 0.3
        if 'name' in attributes and attributes['name']:
            score += 0.2
        if any(attr.startswith('data-') for attr in attributes):
            score += 0.1
        if text_content and len(text_content.strip()) > 0:
            score += 0.1
        
        return min(score, 1.0)
    
    def _determine_element_type(self, tag_name: str, attributes: Dict[str, str]) -> ElementType:
        """Determine the element type based on tag and attributes"""
        tag_name = tag_name.lower()
        
        if tag_name == 'button' or attributes.get('type') == 'button':
            return ElementType.BUTTON
        elif tag_name == 'input':
            input_type = attributes.get('type', 'text').lower()
            if input_type in ['text', 'email', 'password', 'search', 'url', 'tel']:
                return ElementType.INPUT
            elif input_type in ['checkbox']:
                return ElementType.CHECKBOX
            elif input_type in ['radio']:
                return ElementType.RADIO
            elif input_type in ['submit', 'button']:
                return ElementType.BUTTON
        elif tag_name == 'select':
            return ElementType.SELECT
        elif tag_name == 'textarea':
            return ElementType.TEXTAREA
        elif tag_name == 'a' and 'href' in attributes:
            return ElementType.LINK
        elif tag_name == 'form':
            return ElementType.FORM
        elif attributes.get('role') == 'button':
            return ElementType.BUTTON
        elif attributes.get('contenteditable') == 'true':
            return ElementType.INPUT
        
        return ElementType.OTHER
    
    def _determine_interaction_type(self, tag_name: str, attributes: Dict[str, str]) -> ElementInteractionType:
        """Determine the interaction type for element"""
        element_type = self._determine_element_type(tag_name, attributes)
        
        if element_type in [ElementType.BUTTON]:
            return ElementInteractionType.CLICK
        elif element_type in [ElementType.INPUT, ElementType.TEXTAREA]:
            return ElementInteractionType.TYPE
        elif element_type == ElementType.SELECT:
            return ElementInteractionType.SELECT
        elif element_type == ElementType.CHECKBOX:
            return ElementInteractionType.CHECK
        elif element_type == ElementType.RADIO:
            return ElementInteractionType.SELECT
        elif element_type == ElementType.LINK:
            return ElementInteractionType.CLICK
        elif 'onclick' in attributes:
            return ElementInteractionType.CLICK
        
        return ElementInteractionType.CLICK


class ElementExtractor:
    """Main element extractor class with AI-powered analysis"""
    
    def __init__(
        self,
        config: Config,
        ai_service_factory: AIServiceFactory,
        cache_service: CacheService
    ):
        self.config = config
        self.ai_service_factory = ai_service_factory
        self.cache_service = cache_service
        
        # Initialize extraction strategies
        self.playwright_strategy = PlaywrightExtractionStrategy(config)
        self.selenium_strategy = SeleniumExtractionStrategy(config)
        
        logger.info("ElementExtractor initialized with AI-powered analysis")
    
    async def extract_elements(
        self,
        page_or_driver: Union[Page, webdriver.Remote],
        url: str,
        session_id: str,
        extraction_config: Optional[Dict[str, Any]] = None
    ) -> List[ExtractedElement]:
        """
        Extract elements from a page using appropriate strategy and AI analysis
        
        Args:
            page_or_driver: Playwright Page or Selenium WebDriver instance
            url: URL of the page being analyzed
            session_id: Session ID for tracking
            extraction_config: Optional configuration for extraction
            
        Returns:
            List of ExtractedElement objects with AI analysis
        """
        try:
            # Check cache first
            cache_key = CacheKey.element_extraction(session_id, url)
            cached_elements = await self.cache_service.get(cache_key)
            
            if cached_elements and not extraction_config.get('force_refresh', False):
                logger.info(f"Using cached elements for {url}")
                return [ExtractedElement(**elem) for elem in cached_elements]
            
            # Extract elements using appropriate strategy
            if hasattr(page_or_driver, 'evaluate'):  # Playwright Page
                raw_elements = await self.playwright_strategy.extract_elements(
                    page_or_driver,
                    extraction_config.get('selectors') if extraction_config else None
                )
                extraction_method = 'playwright'
            else:  # Selenium WebDriver
                raw_elements = await self.selenium_strategy.extract_elements(
                    page_or_driver,
                    extraction_config.get('selectors') if extraction_config else None
                )
                extraction_method = 'selenium'
            
            logger.info(f"Extracted {len(raw_elements)} raw elements from {url}")
            
            # Apply AI analysis for intelligent element classification
            analyzed_elements = await self._analyze_elements_with_ai(
                raw_elements, url, session_id, extraction_config
            )
            
            # Convert to ExtractedElement objects
            extracted_elements = []
            for i, element_data in enumerate(analyzed_elements):
                try:
                    extracted_element = ExtractedElement(
                        session_id=session_id,
                        element_type=element_data['element_type'],
                        tag_name=element_data['tag_name'],
                        text=element_data.get('text', ''),
                        attributes=element_data.get('attributes', {}),
                        css_selector=element_data.get('css_selector', ''),
                        xpath=element_data.get('xpath', ''),
                        bounding_box=element_data.get('bounding_box', {}),
                        interaction_type=element_data['interaction_type'],
                        is_visible=element_data.get('is_visible', True),
                        is_interactable=element_data.get('is_enabled', True),
                        confidence_score=element_data.get('ai_confidence', 0.8),
                        extraction_method=extraction_method,
                        ai_analysis=element_data.get('ai_analysis', {}),
                        stability_score=element_data.get('stability_score', 0.5)
                    )
                    extracted_elements.append(extracted_element)
                    
                except Exception as e:
                    logger.warning(f"Error creating ExtractedElement {i}: {e}")
                    continue
            
            # Cache the results
            serializable_elements = [elem.dict() for elem in extracted_elements]
            await self.cache_service.set(
                cache_key, 
                serializable_elements, 
                ttl=self.config.cache.element_extraction_ttl
            )
            
            logger.info(f"Successfully extracted and analyzed {len(extracted_elements)} elements")
            return extracted_elements
            
        except Exception as e:
            logger.error(f"Element extraction failed for {url}: {e}")
            raise
    
    async def _analyze_elements_with_ai(
        self,
        raw_elements: List[Dict[str, Any]],
        url: str,
        session_id: str,
        extraction_config: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Analyze elements using AI for intelligent classification and scoring"""
        try:
            if not raw_elements:
                return []
            
            # Get AI service
            ai_service = await self.ai_service_factory.get_service('openai')
            if not ai_service:
                logger.warning("AI service not available, using basic analysis")
                return self._basic_element_analysis(raw_elements)
            
            # Prepare elements for AI analysis (limit to avoid token limits)
            max_elements = extraction_config.get('max_ai_analysis', 50) if extraction_config else 50
            elements_for_ai = raw_elements[:max_elements]
            
            # Create AI analysis prompt
            analysis_prompt = self._create_element_analysis_prompt(elements_for_ai, url)
            
            # Check cache for AI analysis
            prompt_hash = hashlib.md5(analysis_prompt.encode()).hexdigest()
            ai_cache_key = CacheKey.ai_analysis("openai", prompt_hash)
            cached_ai_result = await self.cache_service.get(ai_cache_key)
            
            if cached_ai_result:
                logger.info("Using cached AI analysis for elements")
                ai_analysis = cached_ai_result
            else:
                # Perform AI analysis
                logger.info(f"Analyzing {len(elements_for_ai)} elements with AI")
                ai_response = await ai_service.analyze_elements(analysis_prompt)
                
                if ai_response and ai_response.get('success'):
                    ai_analysis = ai_response.get('analysis', {})
                    # Cache AI analysis
                    await self.cache_service.set(
                        ai_cache_key, 
                        ai_analysis, 
                        ttl=self.config.cache.ai_analysis_ttl
                    )
                else:
                    logger.warning("AI analysis failed, using basic analysis")
                    return self._basic_element_analysis(raw_elements)
            
            # Merge AI analysis with raw elements
            analyzed_elements = self._merge_ai_analysis(raw_elements, ai_analysis)
            
            return analyzed_elements
            
        except Exception as e:
            logger.error(f"AI element analysis failed: {e}")
            return self._basic_element_analysis(raw_elements)
    
    def _create_element_analysis_prompt(
        self, 
        elements: List[Dict[str, Any]], 
        url: str
    ) -> str:
        """Create prompt for AI element analysis"""
        
        # Prepare element summaries for AI
        element_summaries = []
        for i, elem in enumerate(elements):
            summary = {
                'index': i,
                'tag': elem.get('tag_name', ''),
                'text': elem.get('text', '')[:100],  # Limit text length
                'type': elem.get('attributes', {}).get('type', ''),
                'id': elem.get('attributes', {}).get('id', ''),
                'class': elem.get('attributes', {}).get('class', ''),
                'role': elem.get('attributes', {}).get('role', ''),
                'aria_label': elem.get('attributes', {}).get('aria-label', ''),
                'data_testid': elem.get('attributes', {}).get('data-testid', ''),
                'is_visible': elem.get('is_visible', True),
                'bounding_box': elem.get('bounding_box', {})
            }
            element_summaries.append(summary)
        
        prompt = f"""
        Analyze the following UI elements extracted from webpage: {url}
        
        For each element, provide:
        1. Purpose classification (navigation, form_input, action_button, content, etc.)
        2. Interaction priority (1-10, where 10 is most important for testing)
        3. Business importance (1-10, where 10 is critical business functionality)
        4. Test automation suitability (1-10, where 10 is perfect for automation)
        5. Element stability prediction (1-10, where 10 is most stable across page changes)
        6. Suggested test scenarios for this element
        
        Elements to analyze:
        {json.dumps(element_summaries, indent=2)}
        
        Return analysis as JSON with this structure:
        {{
            "elements": [
                {{
                    "index": 0,
                    "purpose": "action_button",
                    "interaction_priority": 8,
                    "business_importance": 9,
                    "automation_suitability": 8,
                    "stability_prediction": 7,
                    "confidence": 0.9,
                    "suggested_scenarios": ["click_to_submit", "verify_enabled_state"],
                    "testing_notes": "Critical submit button for user registration"
                }}
            ],
            "page_insights": {{
                "page_type": "registration_form",
                "main_workflow": "user_registration",
                "critical_elements": [0, 3, 7],
                "testing_strategy": "focus_on_form_validation_and_submission"
            }}
        }}
        """
        
        return prompt
    
    def _merge_ai_analysis(
        self, 
        raw_elements: List[Dict[str, Any]], 
        ai_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Merge AI analysis results with raw element data"""
        
        analyzed_elements = []
        ai_element_data = {
            elem['index']: elem 
            for elem in ai_analysis.get('elements', [])
        }
        
        for i, raw_elem in enumerate(raw_elements):
            analyzed_elem = raw_elem.copy()
            
            # Add AI analysis if available
            if i in ai_element_data:
                ai_data = ai_element_data[i]
                analyzed_elem.update({
                    'ai_analysis': {
                        'purpose': ai_data.get('purpose', 'unknown'),
                        'interaction_priority': ai_data.get('interaction_priority', 5),
                        'business_importance': ai_data.get('business_importance', 5),
                        'automation_suitability': ai_data.get('automation_suitability', 5),
                        'stability_prediction': ai_data.get('stability_prediction', 5),
                        'suggested_scenarios': ai_data.get('suggested_scenarios', []),
                        'testing_notes': ai_data.get('testing_notes', '')
                    },
                    'ai_confidence': ai_data.get('confidence', 0.5)
                })
                
                # Update stability score with AI prediction
                ai_stability = ai_data.get('stability_prediction', 5) / 10.0
                original_stability = analyzed_elem.get('stability_score', 0.5)
                # Weighted average of AI and rule-based stability
                analyzed_elem['stability_score'] = (ai_stability * 0.7 + original_stability * 0.3)
            else:
                # Default AI analysis for elements not analyzed
                analyzed_elem.update({
                    'ai_analysis': {
                        'purpose': 'unknown',
                        'interaction_priority': 5,
                        'business_importance': 5,
                        'automation_suitability': 5,
                        'stability_prediction': 5,
                        'suggested_scenarios': [],
                        'testing_notes': 'Element not analyzed by AI'
                    },
                    'ai_confidence': 0.3
                })
            
            analyzed_elements.append(analyzed_elem)
        
        return analyzed_elements
    
    def _basic_element_analysis(self, raw_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fallback analysis without AI"""
        
        analyzed_elements = []
        
        for elem in raw_elements:
            analyzed_elem = elem.copy()
            
            # Basic rule-based analysis
            element_type = elem.get('element_type', ElementType.OTHER)
            tag_name = elem.get('tag_name', '').lower()
            attributes = elem.get('attributes', {})
            
            # Determine priority based on element type and attributes
            priority = 5  # Default
            if element_type == ElementType.BUTTON:
                priority = 8
            elif element_type in [ElementType.INPUT, ElementType.TEXTAREA]:
                priority = 7
            elif element_type == ElementType.LINK:
                priority = 6
            elif 'data-testid' in attributes:
                priority += 2
            elif attributes.get('id'):
                priority += 1
            
            analyzed_elem.update({
                'ai_analysis': {
                    'purpose': self._determine_purpose(element_type, attributes),
                    'interaction_priority': min(priority, 10),
                    'business_importance': 5,
                    'automation_suitability': 7 if 'data-testid' in attributes else 5,
                    'stability_prediction': int(elem.get('stability_score', 0.5) * 10),
                    'suggested_scenarios': self._get_basic_scenarios(element_type),
                    'testing_notes': 'Basic rule-based analysis'
                },
                'ai_confidence': 0.6
            })
            
            analyzed_elements.append(analyzed_elem)
        
        return analyzed_elements
    
    def _determine_purpose(self, element_type: ElementType, attributes: Dict[str, str]) -> str:
        """Determine element purpose using basic rules"""
        if element_type == ElementType.BUTTON:
            if 'submit' in attributes.get('type', ''):
                return 'form_submit'
            return 'action_button'
        elif element_type in [ElementType.INPUT, ElementType.TEXTAREA]:
            return 'form_input'
        elif element_type == ElementType.LINK:
            return 'navigation'
        elif element_type == ElementType.SELECT:
            return 'form_input'
        elif element_type == ElementType.CHECKBOX:
            return 'form_input'
        return 'content'
    
    def _get_basic_scenarios(self, element_type: ElementType) -> List[str]:
        """Get basic test scenarios for element type"""
        scenarios_map = {
            ElementType.BUTTON: ['click', 'verify_enabled', 'verify_visible'],
            ElementType.INPUT: ['type_text', 'clear_text', 'verify_placeholder'],
            ElementType.TEXTAREA: ['type_text', 'clear_text'],
            ElementType.SELECT: ['select_option', 'verify_options'],
            ElementType.CHECKBOX: ['check', 'uncheck', 'verify_state'],
            ElementType.RADIO: ['select', 'verify_selected'],
            ElementType.LINK: ['click', 'verify_href', 'verify_text'],
            ElementType.FORM: ['submit', 'validate_fields']
        }
        return scenarios_map.get(element_type, ['interact', 'verify_visible'])
