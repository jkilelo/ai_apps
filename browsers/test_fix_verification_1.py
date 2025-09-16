"""
Test to verify the React error fix
"""

from playwright.sync_api import sync_playwright
import time

def test_react_error_fix():
    """Test that the React error is fixed when displaying test results"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Enable console logging to catch React errors
        console_messages = []
        def handle_console(msg):
            console_messages.append(msg.text)
            if "error" in msg.type.lower():
                print(f"[CONSOLE ERROR] {msg.text}")
        
        page.on("console", handle_console)
        
        print("1. Navigating to Web Automation page...")
        page.goto("http://localhost:3000/web-automation")
        time.sleep(2)
        
        print("2. Starting quick flow to test generation...")
        page.click('button:has-text("Example.com")')
        time.sleep(0.5)
        
        page.click('button:has-text("Start Extraction")')
        print("   Waiting for extraction...")
        
        try:
            page.wait_for_selector('h3:has-text("Extraction Results")', timeout=30000)
            print("   [SUCCESS] Extraction completed!")
        except:
            print("   [FAILED] Extraction timeout")
            browser.close()
            return
        
        # Continue to test generation
        page.click('button:has-text("Continue to Test Generation")')
        print("3. Moved to test generation, waiting for completion...")
        time.sleep(3)
        
        # Wait for test generation to complete and advance to step 4
        try:
            page.wait_for_selector('text="Step 4 of 4"', timeout=60000)
            print("   [SUCCESS] Auto-advanced to View Results!")
        except:
            print("   [TIMEOUT] Still generating tests...")
        
        # Check for React errors in console
        react_errors = [msg for msg in console_messages if "react" in msg.lower() and "error" in msg.lower()]
        object_errors = [msg for msg in console_messages if "objects are not valid as a react child" in msg.lower()]
        
        if react_errors:
            print(f"   [FAILED] Found React errors: {len(react_errors)}")
            for error in react_errors[:3]:  # Show first 3 errors
                print(f"     - {error}")
        else:
            print("   [SUCCESS] No React errors found!")
        
        if object_errors:
            print(f"   [FAILED] Found object rendering errors: {len(object_errors)}")
        else:
            print("   [SUCCESS] No object rendering errors!")
        
        # Take final screenshot
        page.screenshot(path="error_fix_verification.png")
        print("4. Screenshot captured for verification")
        
        print(f"\n5. Total console messages: {len(console_messages)}")
        print("   Browser will stay open for manual inspection...")
        time.sleep(5)
        
        browser.close()

if __name__ == "__main__":
    test_react_error_fix()