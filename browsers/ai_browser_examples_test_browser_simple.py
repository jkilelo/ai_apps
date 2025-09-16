#!/usr/bin/env python3
"""Simple test to verify browser functionality works"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from execution.browser_manager import BrowserManager, BrowserConfig
from perception.state_observer import StateObserver

async def test_browser():
    """Test basic browser functionality"""
    browser_manager = None
    
    try:
        print("Testing Browser Functionality")
        print("=" * 50)
        
        # Initialize browser manager
        browser_manager = BrowserManager()
        
        # Create browser config
        config = BrowserConfig()
        config.headless = True
        config.viewport_width = 1280
        config.viewport_height = 720
        
        print("Launching browser...")
        browser = await browser_manager.launch(config)
        print("[SUCCESS] Browser launched")
        
        # Create a new context
        print("Creating browser context...")
        context = await browser_manager.new_context()
        print("[SUCCESS] Context created")
        
        # Create a new page
        print("Creating new page...")
        page = await browser_manager.new_page(context)
        print("[SUCCESS] Page created")
        
        # Navigate to a test URL
        print("Navigating to example.com...")
        await page.goto("https://example.com")
        print(f"[SUCCESS] Navigated to {page.url}")
        
        # Get page title
        title = await page.title()
        print(f"Page title: {title}")
        
        # Process DOM
        print("Observing page state...")
        state_observer = StateObserver()
        perception_result = await state_observer.observe(page)
        if perception_result.success and perception_result.state:
            element_count = len(perception_result.state.interactive_elements)
            print(f"[SUCCESS] Page state observed. Found {element_count} interactive elements")
        else:
            print(f"[WARNING] Could not observe page state: {perception_result.error}")
        
        # Take screenshot
        print("Taking screenshot...")
        screenshot_path = Path("example_screenshot.png")
        await page.screenshot(path=str(screenshot_path))
        print(f"[SUCCESS] Screenshot saved to {screenshot_path}")
        
        print("\n" + "=" * 50)
        print("All tests passed successfully!")
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up
        if browser_manager:
            print("Closing browser...")
            await browser_manager.close()
            print("[SUCCESS] Browser closed")

if __name__ == "__main__":
    asyncio.run(test_browser())