"""Google Scholar specific handler with enhanced bot detection evasion"""

import asyncio
import random
from typing import Dict, List, Optional, Any
from playwright.async_api import Page, BrowserContext, TimeoutError as PlaywrightTimeoutError
from loguru import logger
from .actions import ActionResult
from .human_behavior import ScholarSpecificBehavior


class GoogleScholarHandler:
    """Specialized handler for Google Scholar with anti-detection measures"""
    
    def __init__(self):
        self.behavior_simulator = ScholarSpecificBehavior()
        self.search_selectors = [
            'input[name="q"]',  # Primary search input (main search box)
            '#gs_hdr_tsi',  # Header search input by ID
            '.gs_in_txt:visible',  # Scholar visible input text only
            'input[type="text"][aria-label*="Search"]',  # Search input by aria-label
            'input[type="text"]:visible'  # Generic visible text input fallback
        ]
        
        self.paper_selectors = {
            'title': [
                '.gs_rt a',  # Primary title link
                '.gs_rt h3 a',  # Alternative title
                'h3.gs_rt a',  # Header variant
                '.gs_ri h3 a'  # Result item title
            ],
            'authors': [
                '.gs_a',  # Author information
                '.gs_gray',  # Gray text (often authors)
                '.gs_authors'  # Direct author class
            ],
            'citation_count': [
                '.gs_fl a:contains("Cited by")',  # Cited by link
                'a[href*="cites"]',  # Citation link
                '.gs_fl a:nth-child(3)'  # Third link often citations
            ],
            'abstract': [
                '.gs_rs',  # Result snippet
                '.gs_ri .gs_rs',  # Result item snippet
                '.gs_ab'  # Abstract class
            ]
        }
    
    async def setup_scholar_context(self, context: BrowserContext) -> None:
        """Apply Google Scholar specific stealth measures"""
        await context.add_init_script("""
            // Google Scholar specific evasion
            
            // Override navigator properties commonly checked by Google
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Win32'
            });
            
            // Add realistic screen properties
            Object.defineProperty(screen, 'availWidth', {
                get: () => 1920
            });
            Object.defineProperty(screen, 'availHeight', {
                get: () => 1040
            });
            
            // Override performance timing to look realistic
            const originalTiming = performance.timing;
            Object.defineProperty(performance, 'timing', {
                get: () => {
                    const now = Date.now();
                    return {
                        ...originalTiming,
                        navigationStart: now - Math.random() * 1000,
                        domContentLoadedEventEnd: now - Math.random() * 500,
                        loadEventEnd: now - Math.random() * 200
                    };
                }
            });
            
            // Remove automation indicators specific to Scholar detection
            const scholarIndicators = [
                '__nightmare',
                '__phantomas',
                'callPhantom',
                '_phantom',
                'phantom'
            ];
            
            scholarIndicators.forEach(indicator => {
                if (window[indicator]) {
                    delete window[indicator];
                }
            });
            
            // Add realistic mouse movement tracking
            let mouseMovements = 0;
            document.addEventListener('mousemove', () => {
                mouseMovements++;
            });
            
            // Expose mouse activity for later verification
            window.getMouseActivity = () => mouseMovements;
        """)
    
    async def navigate_to_scholar(self, page: Page, search_query: str) -> ActionResult:
        """Navigate to Google Scholar with proper timing and error handling"""
        try:
            logger.info(f"Navigating to Google Scholar for query: {search_query}")
            
            # First go to Scholar homepage to establish session
            await page.goto('https://scholar.google.com', 
                          wait_until='domcontentloaded', 
                          timeout=30000)
            
            # Wait for initial load with multiple strategies
            await self._wait_for_scholar_load(page)
            
            # Simulate human behavior - random delay
            await asyncio.sleep(random.uniform(1.0, 2.5))
            
            # Check if we can search directly or need to use search form
            search_url = f"https://scholar.google.com/scholar?q={search_query.replace(' ', '+')}"
            
            # Try direct search URL first
            await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait for search results or search form
            await self._wait_for_scholar_content(page)
            
            return ActionResult(success=True, data={'url': search_url})
            
        except Exception as e:
            logger.error(f"Failed to navigate to Google Scholar: {e}")
            return ActionResult(success=False, error=str(e))
    
    async def perform_search(self, page: Page, search_query: str) -> ActionResult:
        """Perform search with enhanced human-like behavior"""
        try:
            # Check if we're already on results page
            if 'scholar?q=' in page.url:
                logger.info("Already on search results page")
                return ActionResult(success=True)
            
            # Use human-like search session simulation
            await self.behavior_simulator.simulate_search_session(page, search_query)
            
            # Wait for results with enhanced detection
            await self._wait_for_search_results(page)
            
            # Simulate brief results browsing to establish behavioral pattern
            await asyncio.sleep(random.uniform(1.0, 2.0))
            await self.behavior_simulator.simulate_results_browsing(page, duration=random.uniform(3.0, 6.0))
            
            return ActionResult(success=True)
            
        except Exception as e:
            logger.error(f"Enhanced search failed: {e}")
            
            # Fallback to basic search
            return await self._fallback_basic_search(page, search_query)
    
    async def extract_papers(self, page: Page, max_papers: int = 5) -> List[Dict[str, Any]]:
        """Extract paper information with enhanced human-like behavior"""
        papers = []
        
        try:
            # Wait for paper results to load with multiple strategies
            await page.wait_for_selector('.gs_r', timeout=15000)
            
            # Simulate human browsing behavior while extracting
            await self.behavior_simulator.simulate_results_browsing(page, duration=random.uniform(2.0, 4.0))
            
            # Get all paper result containers
            paper_elements = await page.locator('.gs_r').count()
            logger.info(f"Found {paper_elements} paper elements")
            
            for i in range(min(paper_elements, max_papers)):
                # Simulate human reading pattern
                if i > 0:  # Not for first paper
                    await asyncio.sleep(random.uniform(1.0, 2.5))  # Reading time
                    
                    # Sometimes scroll to next paper
                    if random.random() < 0.6:
                        next_paper = page.locator('.gs_r').nth(i)
                        await next_paper.scroll_into_view_if_needed()
                        await asyncio.sleep(random.uniform(0.3, 0.8))
                
                paper_data = await self._extract_single_paper(page, i)
                if paper_data:
                    papers.append(paper_data)
                    
                    # Simulate reading abstract if present
                    if paper_data.get('abstract'):
                        reading_time = min(3.0, len(paper_data['abstract']) / 200)  # 200 chars/sec
                        await asyncio.sleep(reading_time * random.uniform(0.7, 1.3))
                
                # Human-like delay between paper processing
                await asyncio.sleep(random.uniform(0.5, 1.2))
            
            # Final browsing simulation
            await self.behavior_simulator.simulate_results_browsing(page, duration=random.uniform(1.0, 3.0))
            
        except Exception as e:
            logger.error(f"Enhanced paper extraction failed: {e}")
        
        return papers
    
    async def _extract_single_paper(self, page: Page, index: int) -> Optional[Dict[str, Any]]:
        """Extract data from a single paper result"""
        try:
            paper_container = page.locator('.gs_r').nth(index)
            paper_data = {}
            
            # Extract title
            for title_selector in self.paper_selectors['title']:
                try:
                    title_element = paper_container.locator(title_selector).first
                    if await title_element.count() > 0:
                        title = await title_element.text_content()
                        paper_data['title'] = title.strip() if title else ''
                        
                        # Get paper URL
                        href = await title_element.get_attribute('href')
                        paper_data['url'] = href if href else ''
                        break
                except:
                    continue
            
            # Extract authors and publication info
            for author_selector in self.paper_selectors['authors']:
                try:
                    author_element = paper_container.locator(author_selector).first
                    if await author_element.count() > 0:
                        author_text = await author_element.text_content()
                        if author_text:
                            paper_data['authors_raw'] = author_text.strip()
                            break
                except:
                    continue
            
            # Extract citation count
            try:
                cite_links = paper_container.locator('a').all()
                for link in await cite_links:
                    text = await link.text_content()
                    if text and 'Cited by' in text:
                        # Extract number from "Cited by X"
                        import re
                        match = re.search(r'Cited by (\d+)', text)
                        if match:
                            paper_data['citation_count'] = int(match.group(1))
                        break
            except:
                paper_data['citation_count'] = 0
            
            # Extract abstract/snippet
            for abstract_selector in self.paper_selectors['abstract']:
                try:
                    abstract_element = paper_container.locator(abstract_selector).first
                    if await abstract_element.count() > 0:
                        abstract = await abstract_element.text_content()
                        paper_data['abstract'] = abstract.strip() if abstract else ''
                        break
                except:
                    continue
            
            return paper_data if paper_data.get('title') else None
            
        except Exception as e:
            logger.error(f"Failed to extract paper {index}: {e}")
            return None
    
    async def _wait_for_scholar_load(self, page: Page) -> None:
        """Wait for Google Scholar to fully load"""
        # Wait for multiple indicators that Scholar has loaded
        try:
            await page.wait_for_selector('#gs_hdr_tsb, input[name="q"]', timeout=15000)
        except PlaywrightTimeoutError:
            # Try alternative loading check
            await page.wait_for_function(
                "document.readyState === 'complete' && !document.body.innerText.includes('Loading')",
                timeout=10000
            )
    
    async def _wait_for_scholar_content(self, page: Page) -> None:
        """Wait for Scholar content to be ready"""
        await page.wait_for_function("""
            () => {
                const body = document.body;
                return body && 
                       !body.innerText.includes('Loading...') && 
                       !body.innerText.includes('The system') &&
                       (body.querySelector('#gs_hdr_tsb') || 
                        body.querySelector('.gs_r') ||
                        body.querySelector('input[name="q"]'));
            }
        """, timeout=20000)
    
    async def _wait_for_search_results(self, page: Page) -> None:
        """Wait for search results to load"""
        try:
            await page.wait_for_selector('.gs_r', timeout=15000)
        except PlaywrightTimeoutError:
            # Check if we have any results or error messages
            await page.wait_for_function(
                "document.querySelector('.gs_r') || document.body.innerText.includes('did not match')",
                timeout=10000
            )
    
    async def _is_element_interactable(self, page: Page, selector: str, for_typing: bool = False) -> bool:
        """Check if element is actually interactable and suitable for the intended action"""
        try:
            result = await page.evaluate(f"""
                (for_typing) => {{
                    const element = document.querySelector('{selector}');
                    if (!element) return {{valid: false, reason: 'Element not found'}};
                    
                    const style = window.getComputedStyle(element);
                    const rect = element.getBoundingClientRect();
                    const tagName = element.tagName.toLowerCase();
                    const elementType = element.type;
                    
                    // Basic visibility checks
                    const isVisible = style.display !== 'none' &&
                                    style.visibility !== 'hidden' &&
                                    style.opacity !== '0' &&
                                    rect.width > 0 &&
                                    rect.height > 0;
                    
                    if (!isVisible) {{
                        return {{valid: false, reason: 'Element not visible'}};
                    }}
                    
                    // If this is for typing, validate element can accept text
                    if (for_typing) {{
                        const canAcceptText = (
                            (tagName === 'input' && ['text', 'search', 'email', 'password', 'url', 'tel'].includes(elementType)) ||
                            tagName === 'textarea' ||
                            element.contentEditable === 'true' ||
                            element.contentEditable === ''
                        );
                        
                        if (!canAcceptText) {{
                            return {{
                                valid: false, 
                                reason: `Element cannot accept text input: ${{tagName}} type=${{elementType}}`
                            }};
                        }}
                        
                        // Check if element is disabled or readonly
                        if (element.disabled || element.readOnly) {{
                            return {{valid: false, reason: 'Element is disabled or readonly'}};
                        }}
                    }}
                    
                    return {{
                        valid: true,
                        tagName: tagName,
                        type: elementType,
                        contentEditable: element.contentEditable
                    }};
                }}
            """, for_typing)
            
            if isinstance(result, dict):
                if result.get('valid'):
                    logger.debug(f"Element {selector} is valid: {result.get('tagName')} type={result.get('type')}")
                    return True
                else:
                    logger.warning(f"Element {selector} is not interactable: {result.get('reason')}")
                    return False
            
            return bool(result)
        except Exception as e:
            logger.error(f"Error checking element interactability for {selector}: {e}")
            return False
    
    async def _fallback_basic_search(self, page: Page, search_query: str) -> ActionResult:
        """Fallback basic search if enhanced search fails"""
        try:
            logger.info("Using fallback basic search method")
            
            # Try each search selector with proper validation
            search_box = None
            working_selector = None
            for selector in self.search_selectors:
                try:
                    elements = await page.locator(selector).count()
                    if elements > 0:
                        element = page.locator(selector).first
                        # Check if element is suitable for typing
                        if await self._is_element_interactable(page, selector, for_typing=True):
                            search_box = element
                            working_selector = selector
                            logger.info(f"Found working search input: {selector}")
                            break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not search_box or not working_selector:
                return ActionResult(
                    success=False, 
                    error="No accessible search input found on Google Scholar"
                )
            
            # Use human-like interaction even in fallback
            await self.behavior_simulator.human_like_click(page, working_selector)
            await asyncio.sleep(random.uniform(0.2, 0.5))
            
            await search_box.fill('')  # Clear first
            await self.behavior_simulator.human_like_type(page, working_selector, search_query)
            
            # Submit search with human timing
            await asyncio.sleep(random.uniform(0.3, 0.8))
            await page.keyboard.press('Enter')
            
            # Wait for results
            await self._wait_for_search_results(page)
            
            return ActionResult(success=True)
            
        except Exception as e:
            logger.error(f"Fallback search failed: {e}")
            return ActionResult(success=False, error=str(e))