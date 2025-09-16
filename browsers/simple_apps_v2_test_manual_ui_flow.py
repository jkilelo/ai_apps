"""
Manual UI Flow Test
Senior QA Engineer Pattern: Manual UI Testing with Screenshots
"""

import time
from playwright.sync_api import sync_playwright
from pathlib import Path

def test_web_automation_flow():
    """Manually test the web automation flow with screenshots"""
    
    print("\n" + "="*60)
    print("Manual UI Flow Test - Web Automation Pipeline")
    print("="*60)
    
    # Create results directory
    Path("test-results").mkdir(exist_ok=True)
    
    with sync_playwright() as p:
        # Launch browser in headed mode
        browser = p.chromium.launch(
            headless=False,
            slow_mo=1000  # Slow down actions for visibility
        )
        
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        
        page = context.new_page()
        
        try:
            print("\n[STEP 1] Navigate to the application")
            page.goto("http://localhost:3000")
            page.wait_for_load_state("networkidle")
            page.screenshot(path="test-results/01-home-page.png")
            print("  Screenshot saved: 01-home-page.png")
            
            # Look for Web Automation link or button
            print("\n[STEP 2] Look for Web Automation feature")
            time.sleep(2)
            
            # Try to find any link or button related to web automation
            web_auto_link = page.locator('text=/web.*automation/i').first
            if web_auto_link.is_visible():
                print("  Found Web Automation link, clicking...")
                web_auto_link.click()
                page.wait_for_load_state("networkidle")
                page.screenshot(path="test-results/02-web-automation-page.png")
                print("  Screenshot saved: 02-web-automation-page.png")
            else:
                print("  Web Automation link not found, looking for alternatives...")
                
                # Try clicking on "Flows" or similar navigation
                flows_link = page.locator('text=/flows/i').first
                if flows_link.is_visible():
                    flows_link.click()
                    time.sleep(2)
                    page.screenshot(path="test-results/02-flows-page.png")
                    
                    # Now look for web automation
                    web_auto_option = page.locator('text=/web.*automation/i').first
                    if web_auto_option.is_visible():
                        web_auto_option.click()
                        time.sleep(2)
                        page.screenshot(path="test-results/03-web-automation-selected.png")
            
            # Look for URL input field
            print("\n[STEP 3] Test Element Extraction")
            time.sleep(2)
            
            # Find any input field that looks like a URL input
            url_inputs = page.locator('input[type="text"], input[type="url"]').all()
            print(f"  Found {len(url_inputs)} input fields")
            
            if url_inputs:
                # Try the first visible input
                for i, input_field in enumerate(url_inputs):
                    if input_field.is_visible():
                        print(f"  Filling input field {i+1}")
                        input_field.fill("https://example.com")
                        page.screenshot(path=f"test-results/04-url-entered-{i+1}.png")
                        
                        # Look for submit/next button
                        next_button = page.locator('button:has-text("Next"), button:has-text("Submit"), button:has-text("Start"), button:has-text("Analyze")').first
                        if next_button.is_visible():
                            print("  Found action button, clicking...")
                            next_button.click()
                            
                            # Wait for loading
                            print("  Waiting for response...")
                            time.sleep(5)
                            
                            # Check for loading spinner
                            spinner = page.locator('.animate-spin, .spinner, .loading').first
                            if spinner.is_visible():
                                print("  Loading spinner detected, waiting...")
                                spinner.wait_for(state="hidden", timeout=120000)
                            
                            page.screenshot(path="test-results/05-after-submission.png")
                            print("  Screenshot saved: 05-after-submission.png")
                            break
            
            # Continue through remaining steps if visible
            print("\n[STEP 4] Check for additional steps")
            time.sleep(3)
            
            # Look for any indication of progress
            steps_indicators = page.locator('text=/step.*2/i, text=/test.*generation/i').all()
            if steps_indicators:
                print("  Found step 2 indicators")
                page.screenshot(path="test-results/06-step-2.png")
                
                # Look for next button
                next_button = page.locator('button:has-text("Next"), button:has-text("Continue")').first
                if next_button.is_visible():
                    next_button.click()
                    time.sleep(5)
                    page.screenshot(path="test-results/07-step-3.png")
            
            print("\n[STEP 5] Final state")
            page.screenshot(path="test-results/08-final-state.png", full_page=True)
            print("  Final screenshot saved: 08-final-state.png")
            
            # Print page content for debugging
            print("\n[DEBUG] Current page URL:", page.url)
            print("[DEBUG] Page title:", page.title())
            
            # Count visible buttons
            buttons = page.locator('button:visible').all()
            print(f"[DEBUG] Found {len(buttons)} visible buttons")
            for i, button in enumerate(buttons[:5]):  # First 5 buttons
                text = button.text_content()
                if text:
                    print(f"  Button {i+1}: {text.strip()}")
            
            # Count visible inputs
            inputs = page.locator('input:visible').all()
            print(f"[DEBUG] Found {len(inputs)} visible input fields")
            
            print("\n[INFO] Manual test completed. Check test-results/ folder for screenshots.")
            
        except Exception as e:
            print(f"\n[ERROR] Test failed: {e}")
            page.screenshot(path="test-results/error-screenshot.png", full_page=True)
            print("  Error screenshot saved: error-screenshot.png")
            raise
            
        finally:
            print("\n[INFO] Press Enter to close the browser...")
            input()
            browser.close()

if __name__ == "__main__":
    print("""
    ============================================================
    Manual UI Flow Test
    This test will open a browser and navigate through the UI
    ============================================================
    """)
    
    # Check services
    import requests
    
    print("\n[CHECK] Verifying services...")
    
    try:
        requests.get("http://localhost:5175/api/ui/health", timeout=2)
        print("  [OK] Backend is running")
    except:
        print("  [ERROR] Backend is not running")
        print("  Please start: python simple_apps_v2/backend/web_automation/startup.py")
        exit(1)
        
    try:
        requests.get("http://localhost:3000", timeout=2)
        print("  [OK] Frontend is running")
    except:
        print("  [ERROR] Frontend is not running")
        print("  Please start: cd simple_apps_original/frontend && npm run dev")
        exit(1)
    
    print("\n[INFO] Starting manual UI test...")
    print("[INFO] The browser will open and navigate automatically")
    print("[INFO] Screenshots will be saved to test-results/")
    
    test_web_automation_flow()