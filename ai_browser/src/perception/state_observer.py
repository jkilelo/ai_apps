"""State observer for comprehensive page state capture"""

from typing import Optional, Dict, Any, List
from playwright.async_api import Page
from loguru import logger
import time
import base64

from .dom_processor import DOMProcessor
from .visual_annotator import VisualAnnotator
from .models import (
    WebPageState, 
    PageMetadata,
    DOMStructure,
    AccessibilityTree,
    PerceptionResult,
    InteractiveElement,
    AnnotatedElement
)


class StateObserver:
    """Orchestrates perception components to capture complete page state"""
    
    def __init__(self):
        self.dom_processor = DOMProcessor()
        self.visual_annotator = VisualAnnotator()
        self.last_state: Optional[WebPageState] = None
        
    async def observe(self, page: Page, 
                     capture_screenshot: bool = True,
                     annotate_visuals: bool = True,
                     extract_accessibility: bool = False,
                     full_page: bool = False) -> PerceptionResult:
        """
        Capture comprehensive page state
        
        Args:
            page: Playwright page to observe
            capture_screenshot: Whether to capture screenshots
            annotate_visuals: Whether to add visual annotations
            extract_accessibility: Whether to extract accessibility tree
            full_page: Whether to capture full page screenshot
            
        Returns:
            PerceptionResult with captured state or error
        """
        start_time = time.perf_counter()
        warnings = []
        metrics = {}
        
        try:
            # 1. Extract page metadata
            metadata = await self._extract_metadata(page)
            metrics['metadata_ms'] = (time.perf_counter() - start_time) * 1000
            
            # 2. Get and process DOM
            dom_start = time.perf_counter()
            html = await page.content()
            dom_structure = self.dom_processor.process_html(html)
            interactive_elements = self.dom_processor.get_interactive_elements()
            element_map = self.dom_processor.get_element_map()
            metrics['dom_processing_ms'] = (time.perf_counter() - dom_start) * 1000
            
            # 3. Capture visual state
            visual_data = {
                'screenshot': None,
                'screenshot_base64': None,
                'annotated_screenshot': None,
                'annotated_screenshot_base64': None,
                'annotated_elements': []
            }
            
            if capture_screenshot:
                visual_start = time.perf_counter()
                
                if annotate_visuals:
                    # Capture both clean and annotated screenshots
                    visual_result = await self.visual_annotator.capture_clean_and_annotated(
                        page, full_page=full_page
                    )
                    visual_data.update(visual_result)
                    
                    # Match DOM elements with visual annotations
                    if visual_result['annotated_elements']:
                        annotated_elements = self.visual_annotator.create_annotated_elements(
                            interactive_elements,
                            visual_result['annotated_elements']
                        )
                        visual_data['annotated_elements'] = annotated_elements
                else:
                    # Just capture clean screenshot
                    screenshot = await page.screenshot(full_page=full_page)
                    visual_data['screenshot'] = screenshot
                    visual_data['screenshot_base64'] = base64.b64encode(screenshot).decode('utf-8')
                
                metrics['visual_capture_ms'] = (time.perf_counter() - visual_start) * 1000
            
            # 4. Extract accessibility tree (optional)
            accessibility = None
            if extract_accessibility:
                acc_start = time.perf_counter()
                accessibility = await self._extract_accessibility(page)
                metrics['accessibility_ms'] = (time.perf_counter() - acc_start) * 1000
            
            # 5. Detect page characteristics
            characteristics = await self._detect_page_characteristics(page, dom_structure)
            
            # 6. Create complete page state
            total_duration = (time.perf_counter() - start_time) * 1000
            
            state = WebPageState(
                metadata=metadata,
                dom_structure=dom_structure,
                interactive_elements=interactive_elements,
                screenshot=visual_data.get('screenshot'),
                screenshot_base64=visual_data.get('screenshot_base64'),
                annotated_screenshot=visual_data.get('annotated_screenshot'),
                annotated_screenshot_base64=visual_data.get('annotated_screenshot_base64'),
                element_map=visual_data.get('element_map', element_map),
                annotated_elements=visual_data.get('annotated_elements', []),
                accessibility=accessibility,
                capture_duration_ms=total_duration,
                is_error_page=characteristics.get('is_error_page', False),
                requires_authentication=characteristics.get('requires_authentication', False),
                has_captcha=characteristics.get('has_captcha', False),
                detected_frameworks=characteristics.get('frameworks', [])
            )
            
            self.last_state = state
            
            logger.info(f"Page state captured in {total_duration:.2f}ms")
            logger.debug(f"Metrics: {metrics}")
            
            return PerceptionResult(
                success=True,
                state=state,
                warnings=warnings,
                metrics=metrics
            )
            
        except Exception as e:
            logger.error(f"Failed to observe page state: {e}")
            return PerceptionResult(
                success=False,
                error=str(e),
                warnings=warnings,
                metrics=metrics
            )
    
    async def _extract_metadata(self, page: Page) -> PageMetadata:
        """Extract page metadata"""
        try:
            # Basic metadata
            url = page.url
            title = await page.title()
            
            # Try to get meta description
            description = await page.evaluate("""
                () => {
                    const meta = document.querySelector('meta[name="description"]');
                    return meta ? meta.content : null;
                }
            """)
            
            # Get keywords
            keywords = await page.evaluate("""
                () => {
                    const meta = document.querySelector('meta[name="keywords"]');
                    return meta ? meta.content.split(',').map(k => k.trim()) : [];
                }
            """)
            
            # Get language
            language = await page.evaluate("""
                () => document.documentElement.lang || 'en'
            """)
            
            # Get viewport and scroll info
            viewport_info = await page.evaluate("""
                () => ({
                    viewportWidth: window.innerWidth,
                    viewportHeight: window.innerHeight,
                    scrollX: window.pageXOffset || document.documentElement.scrollLeft,
                    scrollY: window.pageYOffset || document.documentElement.scrollTop,
                    pageWidth: document.documentElement.scrollWidth,
                    pageHeight: document.documentElement.scrollHeight
                })
            """)
            
            return PageMetadata(
                url=url,
                title=title,
                description=description,
                keywords=keywords if keywords else None,
                language=language,
                viewport_width=viewport_info['viewportWidth'],
                viewport_height=viewport_info['viewportHeight'],
                scroll_position={
                    'x': viewport_info['scrollX'],
                    'y': viewport_info['scrollY']
                },
                page_width=viewport_info['pageWidth'],
                page_height=viewport_info['pageHeight']
            )
            
        except Exception as e:
            logger.error(f"Failed to extract metadata: {e}")
            # Return minimal metadata
            return PageMetadata(
                url=page.url,
                title="Unknown"
            )
    
    async def _extract_accessibility(self, page: Page) -> AccessibilityTree:
        """Extract accessibility tree information"""
        try:
            # Get accessibility snapshot
            snapshot = await page.accessibility.snapshot()
            
            # Extract focusable elements
            focusable = await page.evaluate("""
                () => {
                    const elements = document.querySelectorAll(
                        'a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
                    );
                    return Array.from(elements).map(el => ({
                        tag: el.tagName.toLowerCase(),
                        text: el.textContent?.substring(0, 50) || '',
                        ariaLabel: el.getAttribute('aria-label') || '',
                        role: el.getAttribute('role') || '',
                        tabIndex: el.tabIndex
                    }));
                }
            """)
            
            # Extract ARIA landmarks
            landmarks = await page.evaluate("""
                () => {
                    const landmarkRoles = [
                        'banner', 'navigation', 'main', 'complementary',
                        'contentinfo', 'search', 'form', 'region'
                    ];
                    const elements = [];
                    
                    landmarkRoles.forEach(role => {
                        const found = document.querySelectorAll(`[role="${role}"]`);
                        found.forEach(el => {
                            elements.push({
                                role: role,
                                label: el.getAttribute('aria-label') || '',
                                text: el.textContent?.substring(0, 50) || ''
                            });
                        });
                    });
                    
                    return elements;
                }
            """)
            
            # Extract heading hierarchy
            headings = await page.evaluate("""
                () => {
                    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                    return Array.from(headings).map(h => ({
                        level: parseInt(h.tagName[1]),
                        text: h.textContent?.trim() || '',
                        id: h.id || ''
                    }));
                }
            """)
            
            return AccessibilityTree(
                tree=snapshot,
                focusable_elements=focusable,
                landmarks=landmarks,
                headings_hierarchy=headings
            )
            
        except Exception as e:
            logger.error(f"Failed to extract accessibility tree: {e}")
            return AccessibilityTree()
    
    async def _detect_page_characteristics(self, page: Page, 
                                          dom_structure: DOMStructure) -> Dict[str, Any]:
        """Detect special page characteristics"""
        characteristics = {
            'is_error_page': False,
            'requires_authentication': False,
            'has_captcha': False,
            'frameworks': []
        }
        
        try:
            # Check for error page indicators
            error_indicators = ['404', '403', '500', 'error', 'not found', 'forbidden']
            page_text = dom_structure.text_content.lower()
            title = await page.title()
            
            for indicator in error_indicators:
                if indicator in title.lower() or indicator in page_text[:500]:
                    characteristics['is_error_page'] = True
                    break
            
            # Check for authentication requirements
            auth_indicators = ['login', 'sign in', 'password', 'authenticate']
            form_fields = [f for form in dom_structure.forms for f in form.get('fields', [])]
            has_password_field = any(f.get('type') == 'password' for f in form_fields)
            
            if has_password_field:
                characteristics['requires_authentication'] = True
            else:
                for indicator in auth_indicators:
                    if indicator in page_text[:1000]:
                        characteristics['requires_authentication'] = True
                        break
            
            # Check for CAPTCHA
            captcha_indicators = ['captcha', 'recaptcha', 'hcaptcha', 'verify you are human']
            for indicator in captcha_indicators:
                if indicator in page_text.lower():
                    characteristics['has_captcha'] = True
                    break
            
            # Detect frameworks
            frameworks = await page.evaluate("""
                () => {
                    const detected = [];
                    
                    // React
                    if (window.React || document.querySelector('[data-reactroot]')) {
                        detected.push('React');
                    }
                    
                    // Vue
                    if (window.Vue || document.querySelector('#app[data-v-]')) {
                        detected.push('Vue');
                    }
                    
                    // Angular
                    if (window.ng || document.querySelector('[ng-app], [data-ng-app]')) {
                        detected.push('Angular');
                    }
                    
                    // jQuery
                    if (window.jQuery || window.$) {
                        detected.push('jQuery');
                    }
                    
                    // Bootstrap
                    if (document.querySelector('.container, .container-fluid, .btn-primary')) {
                        detected.push('Bootstrap');
                    }
                    
                    // Tailwind
                    if (document.querySelector('[class*="flex"], [class*="grid"], [class*="px-"], [class*="py-"]')) {
                        const classes = Array.from(document.querySelectorAll('*'))
                            .flatMap(el => Array.from(el.classList));
                        if (classes.some(c => /^(flex|grid|px-|py-|mx-|my-|text-)/.test(c))) {
                            detected.push('Tailwind');
                        }
                    }
                    
                    return detected;
                }
            """)
            
            characteristics['frameworks'] = frameworks
            
        except Exception as e:
            logger.error(f"Failed to detect page characteristics: {e}")
        
        return characteristics
    
    async def observe_changes(self, page: Page, 
                            previous_state: Optional[WebPageState] = None) -> Dict[str, Any]:
        """
        Observe changes between current and previous state
        
        Args:
            page: Current page
            previous_state: Previous page state to compare against
            
        Returns:
            Dictionary describing changes
        """
        if not previous_state:
            previous_state = self.last_state
        
        if not previous_state:
            return {'error': 'No previous state to compare'}
        
        # Capture current state
        current_result = await self.observe(page, capture_screenshot=False)
        
        if not current_result.success or not current_result.state:
            return {'error': 'Failed to capture current state'}
        
        current_state = current_result.state
        changes = {
            'url_changed': current_state.metadata.url != previous_state.metadata.url,
            'title_changed': current_state.metadata.title != previous_state.metadata.title,
            'elements_added': [],
            'elements_removed': [],
            'content_changes': False
        }
        
        # Compare interactive elements
        prev_selectors = {elem.selector for elem in previous_state.interactive_elements}
        curr_selectors = {elem.selector for elem in current_state.interactive_elements}
        
        changes['elements_added'] = list(curr_selectors - prev_selectors)
        changes['elements_removed'] = list(prev_selectors - curr_selectors)
        
        # Check content changes
        if current_state.dom_structure.text_content != previous_state.dom_structure.text_content:
            changes['content_changes'] = True
        
        return changes
    
    def get_last_state(self) -> Optional[WebPageState]:
        """Get the last captured state"""
        return self.last_state