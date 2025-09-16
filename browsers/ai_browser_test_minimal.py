#!/usr/bin/env python3
"""Minimal test with proper error handling"""

import asyncio
import sys
from pathlib import Path

# Add src to path for local imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from execution.browser_manager import BrowserManager, BrowserConfig


async def test_minimal():
    """Test minimal browser operation"""
    browser_manager = None
    context = None
    
    try:
        print("1. Creating BrowserManager...")
        browser_manager = BrowserManager()
        
        print("2. Creating BrowserConfig...")
        config = BrowserConfig()
        config.headless = True  # Headless for testing
        
        print("3. Launching browser...")
        browser = await browser_manager.launch(config)
        print(f"   Browser: {browser}")
        
        print("4. Creating context...")
        context = await browser_manager.new_context()
        print(f"   Context: {context}")
        
        print("5. Creating page...")
        page = await browser_manager.new_page(context)
        print(f"   Page: {page}")
        
        print("6. Navigating to example.com...")
        await page.goto("https://example.com")
        
        print("7. Getting title...")
        title = await page.title()
        print(f"   Title: {title}")
        
        print("8. Closing page...")
        await page.close()
        
        print("9. Success!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed at step: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        print("\n10. Cleanup...")
        try:
            if context and browser_manager:
                await browser_manager.close_context(context)
            if browser_manager:
                await browser_manager.close()
            print("    Cleanup complete")
        except Exception as cleanup_error:
            print(f"    Cleanup error: {cleanup_error}")


if __name__ == "__main__":
    success = asyncio.run(test_minimal())
    sys.exit(0 if success else 1)