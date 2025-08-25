"""
Test Full Web Automation Integration
"""

from playwright.sync_api import sync_playwright
import time

def test_integration():
    """Test the full integration of Web Automation"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("1. Navigating to Web Automation page...")
        page.goto("http://localhost:3000/web-automation")
        
        # Wait for page to load
        time.sleep(2)
        
        print("2. Checking if URL input has default value...")
        url_input = page.query_selector('input[type="url"]')
        if url_input:
            value = url_input.get_attribute('value')
            print(f"   URL input value: {value}")
            
            # Clear and enter a new URL
            url_input.fill("https://example.com")
            print("   Set URL to: https://example.com")
        
        print("3. Clicking Continue button...")
        continue_button = page.query_selector('button:has-text("Continue")')
        if continue_button:
            continue_button.click()
            print("   Clicked Continue - waiting for extraction...")
            
            # Wait for extraction to complete (look for loading state to disappear)
            time.sleep(15)  # Give it time to extract
            
            # Check if we're on step 2
            step2_header = page.query_selector('h3:has-text("Extracted Elements")')
            if step2_header:
                print("4. SUCCESS! Moved to Extract Elements step")
                
                # Check for success message
                success_msg = page.query_selector('.bg-green-50')
                if success_msg:
                    text = success_msg.text_content()
                    print(f"   Extraction result: {text}")
            else:
                print("4. Still on step 1 or extraction failed")
        
        # Take screenshot
        page.screenshot(path="web_automation_test.png")
        print("\n5. Screenshot saved as web_automation_test.png")
        
        # Keep browser open for manual inspection
        print("\nTest complete! Browser will stay open for 10 seconds...")
        time.sleep(10)
        
        browser.close()

if __name__ == "__main__":
    test_integration()