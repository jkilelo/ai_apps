"""
DEPRECATED MODULE
=================
This legacy navigation agent module is retained temporarily for historical context.
New development uses typed pydantic-ai agents defined in `agents/registry.py` and
the `AgentFacade` orchestration/command layers. Do not add new logic here.

Original description:
NavigationAgent - AI Agent for intelligent browsing and interaction patterns.
This agent handles smart navigation, form filling, and human-like interaction
patterns to ensure natural browsing behavior.
"""

from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
import asyncio
import random
from datetime import datetime, timedelta


class NavigationPattern(BaseModel):
    """Model for navigation patterns."""

    pattern_type: str  # scroll, click, hover, type, wait
    timing: float = Field(gt=0.0)  # Duration in seconds
    coordinates: Optional[Tuple[int, int]] = None
    element_selector: Optional[str] = None
    human_variance: float = Field(default=0.1, ge=0.0, le=1.0)


class InteractionSequence(BaseModel):
    """Model for sequences of interactions."""

    name: str
    patterns: List[NavigationPattern]
    success_rate: float = Field(ge=0.0, le=1.0)
    last_used: datetime = Field(default_factory=datetime.now)


class NavigationAgent:
    """
    AI Agent responsible for intelligent and human-like browser navigation.

    Key responsibilities:
    - Generate natural scrolling and clicking patterns
    - Simulate human-like delays and movements
    - Adapt interaction patterns based on page context
    - Coordinate with stealth requirements
    """

    def __init__(self):
        self.interaction_history: List[InteractionSequence] = []
        self.learned_patterns: Dict[str, List[NavigationPattern]] = {}
        self.human_simulation_enabled = True
        self.stealth_mode = False

    async def navigate_naturally(self, page: Any, target_url: str) -> bool:
        """
        Navigate to a URL using natural human-like patterns.

        Args:
            page: Playwright page object
            target_url: URL to navigate to

        Returns:
            True if navigation successful, False otherwise
        """
        try:
            # Add natural delay before navigation
            await self._human_delay(0.5, 2.0)

            # Navigate with realistic timeout
            await page.goto(target_url, wait_until="domcontentloaded", timeout=30000)

            # Simulate natural post-navigation behavior
            await self._post_navigation_simulation(page)

            return True
        except Exception as e:
            print(f"Navigation failed: {e}")
            return False

    async def scroll_naturally(
        self, page: Any, direction: str = "down", distance: Optional[int] = None
    ) -> None:
        """
        Perform natural scrolling with human-like patterns.

        Args:
            page: Playwright page object
            direction: "up", "down", "left", "right"
            distance: Pixels to scroll, auto-calculated if None
        """
        if distance is None:
            # Calculate natural scroll distance (viewport based)
            viewport_size = page.viewport_size
            distance = random.randint(
                int(viewport_size["height"] * 0.3), int(viewport_size["height"] * 0.8)
            )

        # Add human variance to scrolling
        scroll_steps = random.randint(3, 8)
        step_distance = distance // scroll_steps

        for _ in range(scroll_steps):
            scroll_delta = step_distance + random.randint(-20, 20)

            if direction == "down":
                await page.mouse.wheel(0, scroll_delta)
            elif direction == "up":
                await page.mouse.wheel(0, -scroll_delta)
            elif direction == "right":
                await page.mouse.wheel(scroll_delta, 0)
            elif direction == "left":
                await page.mouse.wheel(-scroll_delta, 0)

            # Random delay between scroll steps
            await self._human_delay(0.1, 0.5)

    async def click_naturally(self, page: Any, selector: str) -> bool:
        """
        Click an element with human-like behavior patterns.

        Args:
            page: Playwright page object
            selector: CSS selector for the element to click

        Returns:
            True if click successful, False otherwise
        """
        try:
            # Wait for element to be visible
            await page.wait_for_selector(selector, state="visible", timeout=10000)

            # Get element bounding box for natural clicking
            element = page.locator(selector)
            box = await element.bounding_box()

            if not box:
                return False

            # Calculate click position with human variance
            click_x = box["x"] + box["width"] * random.uniform(0.3, 0.7)
            click_y = box["y"] + box["height"] * random.uniform(0.3, 0.7)

            # Move mouse naturally to the element
            await self._move_mouse_naturally(page, click_x, click_y)

            # Add pre-click delay
            await self._human_delay(0.1, 0.3)

            # Perform the click
            await page.mouse.click(click_x, click_y)

            # Post-click delay
            await self._human_delay(0.2, 0.6)

            return True
        except Exception as e:
            print(f"Click failed: {e}")
            return False

    async def type_naturally(self, page: Any, selector: str, text: str) -> bool:
        """
        Type text with human-like typing patterns.

        Args:
            page: Playwright page object
            selector: CSS selector for the input element
            text: Text to type

        Returns:
            True if typing successful, False otherwise
        """
        try:
            # Click on the input field first
            if not await self.click_naturally(page, selector):
                return False

            # Clear existing text
            await page.locator(selector).clear()

            # Type with human-like delays
            for char in text:
                await page.keyboard.type(char)

                # Varying delays between keystrokes
                if char == " ":
                    delay = random.uniform(0.1, 0.3)  # Longer pause for spaces
                elif char in ".,!?":
                    delay = random.uniform(0.2, 0.4)  # Pause for punctuation
                else:
                    delay = random.uniform(0.05, 0.15)  # Normal typing speed

                await asyncio.sleep(delay)

            return True
        except Exception as e:
            print(f"Typing failed: {e}")
            return False

    async def _human_delay(self, min_seconds: float, max_seconds: float) -> None:
        """Add human-like delay with random variance."""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)

    async def _move_mouse_naturally(
        self, page: Any, target_x: float, target_y: float
    ) -> None:
        """Move mouse to target position with natural curved movement."""
        current_position = await page.evaluate("() => ({ x: 0, y: 0 })")  # Simplified

        # Calculate movement in steps for natural curve
        steps = random.randint(5, 12)
        for i in range(steps):
            progress = (i + 1) / steps

            # Add slight curve to movement
            curve_offset = random.uniform(-10, 10) * (1 - abs(progress - 0.5) * 2)

            intermediate_x = (
                current_position["x"] + (target_x - current_position["x"]) * progress
            )
            intermediate_y = (
                current_position["y"]
                + (target_y - current_position["y"]) * progress
                + curve_offset
            )

            await page.mouse.move(intermediate_x, intermediate_y)
            await asyncio.sleep(random.uniform(0.01, 0.03))

    async def _post_navigation_simulation(self, page: Any) -> None:
        """Simulate natural behavior after page navigation."""
        # Wait for page to settle
        await self._human_delay(1.0, 3.0)

        # Random scroll to simulate reading
        if random.random() < 0.7:  # 70% chance to scroll
            await self.scroll_naturally(page, "down")

        # Pause as if reading content
        await self._human_delay(2.0, 5.0)

    async def adapt_to_stealth_mode(self, stealth_level: float) -> None:
        """
        Adapt navigation patterns based on required stealth level.

        Args:
            stealth_level: Float 0.0-1.0 indicating required stealth intensity
        """
        self.stealth_mode = stealth_level > 0.7

        if self.stealth_mode:
            # Slower, more careful movements in high stealth mode
            self.human_simulation_enabled = True
        else:
            # Can be more efficient in low stealth scenarios
            pass
