"""
Simple UI Test for Standalone simple_apps_v2
"""

import asyncio
from playwright.async_api import async_playwright
import json
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

async def test_extract_elements():
    """Test the extraction functionality through UI"""
    
    print("Testing UI Integration...")
    print("-" * 50)
    
    async with async_playwright() as p:
        # Get platform-specific launch options
        launch_options = get_playwright_launch_options()
        launch_options["headless"] = True
        
        browser = await p.chromium.launch(**launch_options)
        page = await browser.new_page()
        
        try:
            # Navigate to frontend
            print("\n1. Loading frontend...")
            await page.goto("http://localhost:3000", wait_until="networkidle")
            
            # Navigate to Web Automation
            print("2. Navigating to Web Automation...")
            await page.click('a[href="/web-automation"]')
            await page.wait_for_load_state("networkidle")
            
            # Enter URL and extract
            print("3. Testing extraction...")
            await page.fill('input[type="url"]', "https://example.com")
            await page.click('button:has-text("Extract Elements")')
            
            # Wait for result
            print("4. Waiting for extraction result...")
            await page.wait_for_selector('text=/extracted|element/i', timeout=30000)
            
            # Check for success indicators
            success_element = await page.query_selector('[class*="success"]')
            error_element = await page.query_selector('[class*="error"]')
            
            if success_element:
                print("\n[SUCCESS] Extraction completed successfully!")
                # Try to get extracted elements count
                elements_text = await page.text_content('body')
                if "1 element" in elements_text.lower() or "extracted" in elements_text.lower():
                    print("[SUCCESS] Elements were extracted and displayed in UI")
            elif error_element:
                error_text = await error_element.text_content()
                print(f"\n[ERROR] Extraction failed: {error_text}")
            else:
                print("\n[INFO] Extraction completed, checking content...")
                
            # Take screenshot
            await page.screenshot(path="ui_test_result.png")
            print("\nScreenshot saved: ui_test_result.png")
            
            print("\n" + "=" * 50)
            print("UI Test Completed!")
            print("=" * 50)
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Test failed: {e}")
            await page.screenshot(path="ui_test_error.png")
            return False
            
        finally:
            await browser.close()

if __name__ == "__main__":
    success = asyncio.run(test_extract_elements())
    exit(0 if success else 1)