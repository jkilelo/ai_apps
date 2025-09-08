"""Human-like behavioral simulation for stealth automation"""

import asyncio
import random
import math
from typing import List, Tuple, Optional
from playwright.async_api import Page, Locator
from loguru import logger


class HumanBehaviorSimulator:
    """Simulates realistic human interaction patterns"""
    
    def __init__(self):
        self.typing_speeds = {
            'slow': (80, 150),      # 80-150ms between keystrokes
            'medium': (50, 120),    # 50-120ms between keystrokes  
            'fast': (30, 80)        # 30-80ms between keystrokes
        }
        
        # Realistic error rates for typing
        self.error_rates = {
            'careful': 0.01,    # 1% error rate
            'normal': 0.02,     # 2% error rate
            'hurried': 0.05     # 5% error rate
        }
    
    async def human_like_click(self, page: Page, selector: str, 
                              move_to_first: bool = True) -> None:
        """Perform human-like click with mouse movement"""
        try:
            element = page.locator(selector).first
            
            # Wait for element to be visible and stable
            await element.wait_for(state='visible', timeout=10000)
            
            # Get element bounding box
            box = await element.bounding_box()
            if not box:
                logger.warning(f"Could not get bounding box for {selector}")
                await element.click()
                return
            
            # Calculate target position with some randomness
            target_x = box['x'] + box['width'] * random.uniform(0.3, 0.7)
            target_y = box['y'] + box['height'] * random.uniform(0.3, 0.7)
            
            if move_to_first:
                # Get current mouse position (approximate)
                viewport = await page.viewport_size()
                current_x = random.randint(0, viewport['width'])
                current_y = random.randint(0, viewport['height'])
                
                # Generate human-like movement path
                path = self._generate_mouse_path(
                    (current_x, current_y), 
                    (target_x, target_y)
                )
                
                # Move mouse along path
                for point in path:
                    await page.mouse.move(point[0], point[1])
                    await asyncio.sleep(random.uniform(0.01, 0.02))
            
            # Human-like click timing
            await page.mouse.move(target_x, target_y)
            await asyncio.sleep(random.uniform(0.05, 0.15))  # Pre-click pause
            await page.mouse.down()
            await asyncio.sleep(random.uniform(0.05, 0.12))  # Click duration
            await page.mouse.up()
            await asyncio.sleep(random.uniform(0.1, 0.3))    # Post-click pause
            
            logger.debug(f"Human-like click completed on {selector}")
            
        except Exception as e:
            logger.error(f"Human-like click failed for {selector}: {e}")
            # Fallback to regular click
            await element.click()
    
    async def human_like_type(self, page: Page, selector: str, text: str,
                             speed: str = 'medium', style: str = 'normal') -> None:
        """Type text with human-like patterns including errors and corrections"""
        try:
            element = page.locator(selector).first
            await element.wait_for(state='visible', timeout=10000)
            
            # Validate that element can accept text input
            tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
            element_type = await element.get_attribute('type')
            is_contenteditable = await element.get_attribute('contenteditable')
            
            # Check if element can accept text input
            can_type = (
                tag_name == 'input' and element_type in ['text', 'search', 'email', 'password', 'url', 'tel'] or
                tag_name == 'textarea' or
                is_contenteditable == 'true' or
                is_contenteditable == ''
            )
            
            if not can_type:
                error_msg = f"Cannot type into element {selector}: {tag_name} type={element_type}, contenteditable={is_contenteditable}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.debug(f"Validated typing target: {selector} ({tag_name}, type={element_type})")
            
            # Focus the element first
            await self.human_like_click(page, selector, move_to_first=False)
            await element.focus()
            
            # Clear existing content
            await element.fill('')  # Clear first
            await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # Get typing parameters
            min_delay, max_delay = self.typing_speeds[speed]
            error_rate = self.error_rates[style]
            
            i = 0
            while i < len(text):
                char = text[i]
                
                # Simulate thinking pauses at word boundaries
                if char == ' ' and random.random() < 0.1:
                    await asyncio.sleep(random.uniform(0.2, 0.8))
                
                # Simulate typing errors
                if random.random() < error_rate:
                    # Type wrong character
                    wrong_char = self._get_adjacent_key(char)
                    await page.keyboard.type(wrong_char)
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                    
                    # Realize mistake and correct it
                    await page.keyboard.press('Backspace')
                    await asyncio.sleep(random.uniform(0.1, 0.2))
                    
                    # Sometimes hesitate after correction
                    if random.random() < 0.3:
                        await asyncio.sleep(random.uniform(0.2, 0.5))
                
                # Type the correct character
                await page.keyboard.type(char)
                
                # Variable delay between keystrokes
                delay = random.uniform(min_delay, max_delay) / 1000
                
                # Longer pauses for punctuation
                if char in '.,;:!?':
                    delay *= random.uniform(1.5, 2.5)
                
                await asyncio.sleep(delay)
                i += 1
            
            logger.debug(f"Human-like typing completed for {selector}")
            
        except ValueError as e:
            # Re-raise validation errors - don't fallback for these
            logger.error(f"Human-like typing failed for {selector}: {e}")
            raise
        except Exception as e:
            logger.error(f"Human-like typing failed for {selector}: {e}")
            # Only fallback for non-validation errors
            try:
                await element.fill(text)
            except Exception as fallback_error:
                logger.error(f"Fallback typing also failed for {selector}: {fallback_error}")
                raise e  # Raise the original error
    
    async def simulate_reading_time(self, text_length: int) -> None:
        """Simulate realistic reading time based on text length"""
        # Average reading speed: 200-300 words per minute
        # Assume 5 characters per word
        words = max(1, text_length // 5)
        reading_speed = random.uniform(200, 300)  # words per minute
        
        # Calculate reading time in seconds
        reading_time = (words / reading_speed) * 60
        
        # Add some randomness and minimum time
        actual_time = max(1.0, reading_time * random.uniform(0.7, 1.3))
        
        # Cap at reasonable maximum
        actual_time = min(actual_time, 10.0)
        
        logger.debug(f"Simulating reading time: {actual_time:.2f}s for {words} words")
        await asyncio.sleep(actual_time)
    
    async def simulate_scroll_behavior(self, page: Page, target_element: Optional[str] = None) -> None:
        """Simulate realistic scrolling behavior"""
        try:
            # Get page height
            page_height = await page.evaluate("document.body.scrollHeight")
            viewport_height = (await page.viewport_size())['height']
            
            if page_height <= viewport_height:
                return  # No need to scroll
            
            current_scroll = 0
            scroll_sessions = random.randint(2, 5)  # Multiple scroll sessions
            
            for session in range(scroll_sessions):
                # Random scroll distance
                scroll_distance = random.randint(100, 500)
                scroll_direction = 1 if random.random() > 0.1 else -1  # 90% down, 10% up
                
                # Scroll in small increments for realism
                increments = random.randint(3, 8)
                increment_size = scroll_distance // increments
                
                for _ in range(increments):
                    await page.mouse.wheel(0, increment_size * scroll_direction)
                    await asyncio.sleep(random.uniform(0.05, 0.15))
                
                # Pause between scroll sessions (reading)
                pause_time = random.uniform(1.0, 3.0)
                await asyncio.sleep(pause_time)
            
            # If target element specified, scroll it into view
            if target_element:
                element = page.locator(target_element).first
                if await element.count() > 0:
                    await element.scroll_into_view_if_needed()
                    await asyncio.sleep(random.uniform(0.3, 0.8))
            
            logger.debug("Realistic scrolling behavior completed")
            
        except Exception as e:
            logger.error(f"Scroll simulation failed: {e}")
    
    def _generate_mouse_path(self, start: Tuple[float, float], 
                           end: Tuple[float, float], 
                           steps: int = 20) -> List[Tuple[float, float]]:
        """Generate human-like Bezier curve path for mouse movement"""
        
        # Add control points for natural curve
        distance = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        control_distance = distance * 0.25
        
        # Control points with some randomness
        control1 = (
            start[0] + (end[0] - start[0]) * 0.25 + random.uniform(-control_distance, control_distance),
            start[1] + (end[1] - start[1]) * 0.25 + random.uniform(-control_distance, control_distance)
        )
        
        control2 = (
            start[0] + (end[0] - start[0]) * 0.75 + random.uniform(-control_distance, control_distance),
            start[1] + (end[1] - start[1]) * 0.75 + random.uniform(-control_distance, control_distance)
        )
        
        points = []
        for i in range(steps):
            t = i / (steps - 1)
            
            # Cubic Bezier curve formula
            x = ((1-t)**3 * start[0] + 
                 3*(1-t)**2*t * control1[0] + 
                 3*(1-t)*t**2 * control2[0] + 
                 t**3 * end[0])
            
            y = ((1-t)**3 * start[1] + 
                 3*(1-t)**2*t * control1[1] + 
                 3*(1-t)*t**2 * control2[1] + 
                 t**3 * end[1])
            
            points.append((x, y))
        
        return points
    
    def _get_adjacent_key(self, char: str) -> str:
        """Get an adjacent key on QWERTY keyboard for realistic typos"""
        qwerty_map = {
            'q': ['w', 'a'], 'w': ['q', 'e', 'a', 's'], 'e': ['w', 'r', 's', 'd'],
            'r': ['e', 't', 'd', 'f'], 't': ['r', 'y', 'f', 'g'], 'y': ['t', 'u', 'g', 'h'],
            'u': ['y', 'i', 'h', 'j'], 'i': ['u', 'o', 'j', 'k'], 'o': ['i', 'p', 'k', 'l'],
            'p': ['o', 'l'], 'a': ['q', 'w', 's', 'z'], 's': ['a', 'w', 'e', 'd', 'z', 'x'],
            'd': ['s', 'e', 'r', 'f', 'x', 'c'], 'f': ['d', 'r', 't', 'g', 'c', 'v'],
            'g': ['f', 't', 'y', 'h', 'v', 'b'], 'h': ['g', 'y', 'u', 'j', 'b', 'n'],
            'j': ['h', 'u', 'i', 'k', 'n', 'm'], 'k': ['j', 'i', 'o', 'l', 'm'],
            'l': ['k', 'o', 'p'], 'z': ['a', 's', 'x'], 'x': ['z', 's', 'd', 'c'],
            'c': ['x', 'd', 'f', 'v'], 'v': ['c', 'f', 'g', 'b'], 'b': ['v', 'g', 'h', 'n'],
            'n': ['b', 'h', 'j', 'm'], 'm': ['n', 'j', 'k']
        }
        
        char_lower = char.lower()
        if char_lower in qwerty_map and qwerty_map[char_lower]:
            adjacent = random.choice(qwerty_map[char_lower])
            return adjacent.upper() if char.isupper() else adjacent
        
        return char  # Return original if no adjacent key found


class ScholarSpecificBehavior(HumanBehaviorSimulator):
    """Google Scholar specific human behavior patterns"""
    
    async def simulate_search_session(self, page: Page, search_query: str) -> None:
        """Simulate a realistic Google Scholar search session"""
        try:
            logger.info("Starting realistic Scholar search session")
            
            # Initial page load - wait and "read" the page
            await asyncio.sleep(random.uniform(1.0, 2.5))
            
            # Sometimes scroll a bit to see the page layout
            if random.random() < 0.3:
                await page.mouse.wheel(0, random.randint(50, 150))
                await asyncio.sleep(random.uniform(0.5, 1.0))
            
            # Move towards search box with realistic timing - prioritize input elements
            search_selectors = ['input[name="q"]', '#gs_hdr_tsi', '.gs_in_txt:visible']
            search_selector = None
            
            for selector in search_selectors:
                try:
                    elements = await page.locator(selector).count()
                    if elements > 0:
                        # Verify it's actually an input element and visible
                        element = page.locator(selector).first
                        is_input = await element.evaluate('el => el.tagName.toLowerCase() === "input"')
                        is_visible = await element.is_visible()
                        if is_input and is_visible:
                            search_selector = selector
                            break
                except:
                    continue
            
            if not search_selector:
                logger.warning("No search box found for realistic interaction")
                return
            
            # Click on search box with human behavior
            await self.human_like_click(page, search_selector)
            
            # Small pause as user thinks about what to type
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Type the search query with realistic patterns
            await self.human_like_type(page, search_selector, search_query, 
                                     speed='medium', style='normal')
            
            # Brief pause before pressing Enter (like double-checking query)
            await asyncio.sleep(random.uniform(0.3, 0.8))
            
            # Press Enter to search
            await page.keyboard.press('Enter')
            
            logger.info("Realistic search session completed")
            
        except Exception as e:
            logger.error(f"Scholar search session simulation failed: {e}")
    
    async def simulate_results_browsing(self, page: Page, duration: float = 10.0) -> None:
        """Simulate realistic browsing of search results"""
        try:
            logger.info(f"Simulating {duration}s of results browsing")
            
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < duration:
                # Random action selection
                action_weights = [
                    ('scroll', 0.4),
                    ('hover_title', 0.3),
                    ('read_abstract', 0.2),
                    ('pause', 0.1)
                ]
                
                action = random.choices(
                    [a[0] for a in action_weights],
                    weights=[a[1] for a in action_weights]
                )[0]
                
                if action == 'scroll':
                    await self._simulate_research_scroll(page)
                elif action == 'hover_title':
                    await self._simulate_title_hover(page)
                elif action == 'read_abstract':
                    await self._simulate_abstract_reading(page)
                elif action == 'pause':
                    await asyncio.sleep(random.uniform(2.0, 4.0))
                
                # Small delay between actions
                await asyncio.sleep(random.uniform(0.5, 1.5))
            
            logger.info("Results browsing simulation completed")
            
        except Exception as e:
            logger.error(f"Results browsing simulation failed: {e}")
    
    async def _simulate_research_scroll(self, page: Page) -> None:
        """Simulate scrolling behavior typical of academic research"""
        scroll_amount = random.randint(200, 600)
        direction = 1 if random.random() > 0.15 else -1  # 85% down, 15% up
        
        # Scroll in smooth increments
        increments = random.randint(4, 8)
        for _ in range(increments):
            await page.mouse.wheel(0, (scroll_amount // increments) * direction)
            await asyncio.sleep(random.uniform(0.1, 0.2))
        
        # Pause after scrolling (reading time)
        await asyncio.sleep(random.uniform(1.5, 3.0))
    
    async def _simulate_title_hover(self, page: Page) -> None:
        """Simulate hovering over paper titles"""
        try:
            titles = await page.locator('.gs_rt a').all()
            if titles:
                title = random.choice(titles[:5])  # Only first 5 results
                if await title.is_visible():
                    await title.hover()
                    await asyncio.sleep(random.uniform(0.5, 1.5))
        except:
            pass
    
    async def _simulate_abstract_reading(self, page: Page) -> None:
        """Simulate reading paper abstracts"""
        try:
            abstracts = await page.locator('.gs_rs').all()
            if abstracts:
                abstract = random.choice(abstracts[:3])  # Only first 3 abstracts
                if await abstract.is_visible():
                    # Scroll to abstract
                    await abstract.scroll_into_view_if_needed()
                    await asyncio.sleep(random.uniform(0.3, 0.7))
                    
                    # Simulate reading time based on text length
                    text = await abstract.text_content()
                    if text:
                        await self.simulate_reading_time(len(text))
        except:
            pass