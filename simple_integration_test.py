"""
Simple Test: Browser Integration Working Example
This demonstrates a minimal working example of using the existing browser.
"""

import asyncio
import sys
from pathlib import Path

# Add browser directory to path
sys.path.insert(0, str(Path(__file__).parent))

from browser.browser_integration_adapter import BrowserIntegrationAdapter


async def simple_test():
    """Simple test showing browser integration works."""
    
    print("\n" + "="*60)
    print("SIMPLE BROWSER INTEGRATION TEST")
    print("="*60)
    
    # Create adapter (uses existing browser infrastructure)
    adapter = BrowserIntegrationAdapter()
    print("[OK] Browser adapter created")
    
    # Test with example.com
    print("\nTesting with example.com:")
    try:
        async with adapter.test_context("https://example.com") as (browser, page):
            print(f"  [OK] Navigated to: {page.url}")
            
            # Get page title
            title = await page.title()
            print(f"  [OK] Page title: {title}")
            
            # Verify it's the right page
            assert "Example" in title
            print(f"  [OK] Title verification passed")
            
            # Extract elements (AI-powered)
            results = await browser.extract_elements()
            print(f"  [OK] Found {len(results.elements)} elements")
            
            # Take screenshot
            await page.screenshot(path="simple_test.png")
            print(f"  [OK] Screenshot saved")
            
    except Exception as e:
        print(f"  [ERROR] Test failed: {e}")
        return False
    
    # Test with another site (Wikipedia)
    print("\nTesting with Wikipedia:")
    try:
        async with adapter.test_context("https://en.wikipedia.org") as (browser, page):
            print(f"  [OK] Navigated to: {page.url}")
            
            title = await page.title()
            print(f"  [OK] Page title: {title}")
            
            assert "Wikipedia" in title
            print(f"  [OK] Title verification passed")
            
    except Exception as e:
        print(f"  [ERROR] Test failed: {e}")
        return False
    
    # Cleanup
    await adapter.cleanup()
    print("\n[OK] Browser cleaned up")
    
    print("\n" + "="*60)
    print("SUCCESS: Browser integration works!")
    print("="*60)
    print("\nKey Points Demonstrated:")
    print("1. Single browser instance used for multiple tests")
    print("2. Works with different websites (example.com, wikipedia.org)")
    print("3. Standard Playwright API works (page.title(), page.screenshot())")
    print("4. AI element extraction available (browser.extract_elements())")
    print("5. Clean resource management with context managers")
    
    return True


def main():
    """Run the simple test."""
    success = asyncio.run(simple_test())
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)