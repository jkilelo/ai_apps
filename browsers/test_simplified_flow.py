"""
Test the Simplified Auto-Generation Flow in UI
"""

from playwright.sync_api import sync_playwright
import time

def test_simplified_flow():
    """Test the simplified auto-generation flow with no user inputs"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("1. Navigating to Web Automation page...")
        page.goto("http://localhost:3000/web-automation")
        time.sleep(2)
        
        print("2. Selecting Example.com for testing...")
        page.click('button:has-text("Example.com")')
        time.sleep(0.5)
        
        print("3. Starting extraction...")
        page.click('button:has-text("Start Extraction")')
        
        # Wait for extraction to complete
        print("   Waiting for extraction to complete...")
        try:
            page.wait_for_selector('h3:has-text("Extraction Results")', timeout=30000)
            print("   [SUCCESS] Extraction completed!")
            time.sleep(2)
        except:
            print("   [FAILED] Extraction failed or timed out")
            browser.close()
            return
        
        print("4. Testing auto-navigation to Generate Tests...")
        # Click Continue to Test Generation button
        continue_button = page.query_selector('button:has-text("Continue to Test Generation")')
        if continue_button:
            continue_button.click()
            print("   [SUCCESS] Clicked Continue to Test Generation")
            time.sleep(2)
        else:
            print("   [FAILED] Continue button not found")
            browser.close()
            return
        
        # Check if we're on step 3 (Generate Tests)
        step_indicator = page.query_selector('text="Step 3 of 4"')
        if step_indicator:
            print("   [SUCCESS] Now on Step 3 - Generate Tests")
        else:
            print("   [FAILED] Not on step 3")
        
        # Take screenshot of simplified UI
        page.screenshot(path="simplified_generate_tests.png")
        print("5. Screenshot captured - simplified UI")
        
        # Verify no test category selection UI exists
        category_selection = page.query_selector('text="Select Test Categories"')
        if not category_selection:
            print("   [SUCCESS] Test category selection UI removed")
        else:
            print("   [FAILED] Test category selection UI still exists")
        
        # Verify auto-generation info is shown
        auto_info = page.query_selector('text="Automatic Test Generation"')
        if auto_info:
            print("   [SUCCESS] Auto-generation info displayed")
        else:
            print("   [FAILED] Auto-generation info not found")
        
        # Check if generation started automatically
        print("6. Checking if test generation started automatically...")
        generation_progress = page.query_selector('.text-purple-900')
        if generation_progress:
            print("   [SUCCESS] Test generation started automatically!")
            
            # Monitor progress
            for i in range(10):
                time.sleep(3)
                progress_text = page.query_selector('.text-purple-900')
                if progress_text:
                    status = progress_text.text_content()
                    print(f"   Progress: {status}")
                
                # Check if we auto-advanced to step 4
                step_4 = page.query_selector('text="Step 4 of 4"')
                if step_4:
                    print("   [SUCCESS] Auto-advanced to Step 4 - View Results!")
                    break
                    
                page.screenshot(path=f"auto_generation_progress_{i+1}.png")
            
            # Final check for results
            test_results = page.query_selector('text="Test Cases Generated"')
            if test_results:
                print("   [SUCCESS] Test generation completed successfully!")
                page.screenshot(path="auto_generation_complete.png")
            else:
                print("   [TIMEOUT] Test generation still in progress")
                
        else:
            print("   [FAILED] Test generation did not start automatically")
        
        print("\n7. Test complete! Screenshots saved:")
        print("   - simplified_generate_tests.png")
        print("   - auto_generation_progress_*.png")
        print("   - auto_generation_complete.png")
        
        print("\nBrowser will stay open for manual inspection...")
        time.sleep(10)
        
        browser.close()

if __name__ == "__main__":
    test_simplified_flow()