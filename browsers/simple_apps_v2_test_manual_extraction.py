"""
Manual test of extraction with waiting for results
"""

import asyncio
from playwright.async_api import async_playwright
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

async def manual_test():
    """Manually test and wait for extraction results"""
    
    print("\n" + "="*60)
    print("MANUAL UI TEST - STANDALONE simple_apps_v2")
    print("="*60)
    
    async with async_playwright() as p:
        # Get platform-specific launch options
        launch_options = get_playwright_launch_options()
        launch_options["headless"] = False
        # Add maximized window arg if not present
        if '--start-maximized' not in launch_options.get('args', []):
            launch_options.setdefault('args', []).append('--start-maximized')
        
        # Launch browser with dynamic configuration
        browser = await p.chromium.launch(**launch_options)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        try:
            # Navigate to the app
            print("\n1. Opening Web Automation page...")
            await page.goto("http://localhost:3000/web-automation")
            await page.wait_for_load_state("networkidle")
            
            # Enter URL
            print("2. Entering URL: https://example.com")
            await page.fill('input[type="url"]', "https://example.com")
            
            # Click extract
            print("3. Clicking Extract Elements button...")
            await page.click('button:has-text("Extract Elements")')
            
            # Wait and monitor for results
            print("4. Waiting for extraction results...")
            print("   (Monitoring for up to 60 seconds...)\n")
            
            for i in range(60):
                await asyncio.sleep(1)
                
                # Check page content
                content = await page.content()
                
                # Look for success indicators
                if "1 element" in content.lower() and "extracted" in content.lower():
                    print("\n[SUCCESS] Extraction completed!")
                    print("Found: 1 element extracted")
                    
                    # Try to find element details
                    if "more information" in content.lower():
                        print("Element: 'More information' link detected")
                    
                    # Check if next step is enabled
                    generate_button = await page.query_selector('button:has-text("Generate Tests")')
                    if generate_button:
                        is_disabled = await generate_button.get_attribute("disabled")
                        if not is_disabled:
                            print("\n[SUCCESS] Generate Tests button is now enabled!")
                            print("The workflow can proceed to the next step.")
                    
                    # Take success screenshot
                    await page.screenshot(path="manual_test_success.png", full_page=True)
                    print("\nScreenshot saved: manual_test_success.png")
                    
                    print("\n" + "="*60)
                    print("TEST RESULT: PASSED")
                    print("The standalone simple_apps_v2 UI is working correctly!")
                    print("="*60)
                    
                    # Keep browser open for observation
                    print("\nBrowser will remain open for 10 seconds for observation...")
                    await asyncio.sleep(10)
                    return True
                
                # Check for errors
                if "error" in content.lower() or "failed" in content.lower():
                    error_elem = await page.query_selector('[class*="error"]')
                    if error_elem:
                        error_text = await error_elem.text_content()
                        print(f"\n[ERROR] Extraction failed: {error_text}")
                        await page.screenshot(path="manual_test_error.png")
                        return False
                
                # Progress indicator
                if i % 5 == 0:
                    print(f"   Still waiting... ({i} seconds)")
            
            print("\n[TIMEOUT] Extraction did not complete within 60 seconds")
            await page.screenshot(path="manual_test_timeout.png", full_page=True)
            return False
            
        except Exception as e:
            print(f"\n[ERROR] Test failed with exception: {e}")
            await page.screenshot(path="manual_test_exception.png")
            return False
            
        finally:
            await browser.close()

if __name__ == "__main__":
    result = asyncio.run(manual_test())
    print(f"\nFinal result: {'PASS' if result else 'FAIL'}")