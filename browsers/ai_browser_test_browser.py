#!/usr/bin/env python3
"""Simple test to check browser launch functionality"""

import asyncio
import sys
from pathlib import Path

# Add src to path for local imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from execution.browser_manager import BrowserManager, BrowserConfig


async def test_browser():
    """Test basic browser launch"""
    print("Testing browser launch...")
    
    # Create browser manager
    browser_manager = BrowserManager()
    
    # Create config
    config = BrowserConfig()
    config.headless = True  # Use headless for testing
    config.viewport_width = 1280
    config.viewport_height = 720
    
    try:
        # Launch browser
        print("Launching browser...")
        browser = await browser_manager.launch(config)
        print(f"Browser launched successfully: {browser}")
        
        # Create a new page
        print("Creating new page...")
        context = await browser_manager.new_context()
        page = await browser_manager.new_page(context)
        print(f"Page created: {page}")
        
        # Navigate to a simple page
        print("Navigating to httpbin.org...")
        await page.goto("https://httpbin.org/")
        print("Navigation successful!")
        
        # Get title
        title = await page.title()
        print(f"Page title: {title}")
        
        # Close everything
        await page.close()
        await context.close()
        await browser_manager.close()
        print("Browser closed successfully!")
        
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        
        # Clean up on error
        try:
            await browser_manager.close()
        except:
            pass
        
        return False


if __name__ == "__main__":
    success = asyncio.run(test_browser())
    if success:
        print("\n[SUCCESS] Browser test passed!")
    else:
        print("\n[ERROR] Browser test failed!")
        sys.exit(1)