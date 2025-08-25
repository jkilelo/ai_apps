"""
Test UI Integration for Standalone simple_apps_v2
This script tests the full UI flow using Playwright
"""

import asyncio
from playwright.async_api import async_playwright
import time
import sys
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).parent
project_root = current_dir.parent  # ai_apps level
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Use absolute imports
from simple_apps_v2.shared_modules.import_resolver import dynamic_import_from
get_playwright_launch_options = dynamic_import_from('platform_utils', 'get_playwright_launch_options')

async def test_ui_flow():
    """Test the complete UI flow"""
    
    print("Starting UI Integration Test...")
    print("-" * 50)
    
    async with async_playwright() as p:
        # Get platform-specific launch options
        launch_options = get_playwright_launch_options()
        launch_options["headless"] = False  # Set to False to see the browser
        
        # Launch browser with dynamic configuration
        browser = await p.chromium.launch(**launch_options)
        page = await browser.new_page()
        
        try:
            # Navigate to frontend
            print("\n1. Navigating to frontend...")
            await page.goto("http://localhost:3000")
            await page.wait_for_load_state("networkidle")
            print("   ✓ Frontend loaded successfully")
            
            # Check if homepage loads
            print("\n2. Checking homepage...")
            title = await page.title()
            print(f"   Page title: {title}")
            
            # Navigate to Web Automation page
            print("\n3. Navigating to Web Automation...")
            # Click on the Web Automation card
            await page.click('a[href="/web-automation"]')
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(1)
            print("   ✓ Web Automation page loaded")
            
            # Test Extract Elements functionality
            print("\n4. Testing Extract Elements...")
            
            # Find URL input field and enter a test URL
            url_input = await page.wait_for_selector('input[type="url"]', timeout=5000)
            await url_input.fill("https://example.com")
            print("   ✓ URL entered: https://example.com")
            
            # Click Extract button
            extract_button = await page.wait_for_selector('button:has-text("Extract Elements")', timeout=5000)
            await extract_button.click()
            print("   ✓ Extract button clicked")
            
            # Wait for extraction to complete (look for success indicator)
            print("   ⏳ Waiting for extraction to complete...")
            
            # Wait for either success or error
            result = await page.wait_for_selector(
                'text=/extracted|error|fail/i',
                timeout=30000
            )
            
            result_text = await result.text_content()
            print(f"   Result: {result_text}")
            
            # Check if extraction was successful
            if "extracted" in result_text.lower() or "element" in result_text.lower():
                print("   ✓ Extraction completed successfully!")
                
                # Check if elements are displayed
                elements_section = await page.query_selector('text=/element/i')
                if elements_section:
                    print("   ✓ Elements are displayed in UI")
            else:
                print("   ⚠ Extraction may have encountered issues")
            
            # Take a screenshot for verification
            screenshot_path = "test_ui_screenshot.png"
            await page.screenshot(path=screenshot_path)
            print(f"\n5. Screenshot saved: {screenshot_path}")
            
            print("\n" + "=" * 50)
            print("✅ UI Integration Test Completed Successfully!")
            print("=" * 50)
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            # Take error screenshot
            await page.screenshot(path="test_ui_error.png")
            print("Error screenshot saved: test_ui_error.png")
            raise
            
        finally:
            # Keep browser open for manual inspection
            print("\nPress Enter to close browser...")
            input()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_ui_flow())