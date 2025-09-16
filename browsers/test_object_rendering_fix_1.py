"""
Quick test to verify the React object rendering fix
"""

from playwright.sync_api import sync_playwright
import time

def test_object_rendering_fix():
    """Test the object rendering fix by navigating to a completed test result"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Capture console errors
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if "error" in msg.type.lower() else None)
        
        print("1. Navigating to Web Automation page...")
        page.goto("http://localhost:3000/web-automation")
        time.sleep(2)
        
        # Check for any immediate React errors
        time.sleep(3)
        
        # Look for React object rendering errors specifically
        object_errors = [error for error in console_errors if "objects are not valid as a react child" in error.lower()]
        react_errors = [error for error in console_errors if "react" in error.lower() and "error" in error.lower()]
        
        print(f"2. Console errors found: {len(console_errors)}")
        print(f"   Object rendering errors: {len(object_errors)}")
        print(f"   React errors: {len(react_errors)}")
        
        if object_errors:
            print("   [FAILED] Still finding object rendering errors:")
            for error in object_errors:
                print(f"     - {error}")
        else:
            print("   [SUCCESS] No object rendering errors found!")
        
        if react_errors:
            print("   React errors detected:")
            for error in react_errors[:2]:  # Show first 2
                print(f"     - {error}")
        else:
            print("   [SUCCESS] No React errors found!")
        
        # Take screenshot
        page.screenshot(path="react_fix_verification.png")
        print("3. Screenshot captured")
        
        print("\nBrowser will stay open for 5 seconds for manual inspection...")
        time.sleep(5)
        
        browser.close()
        
        return len(object_errors) == 0 and len(react_errors) == 0

if __name__ == "__main__":
    success = test_object_rendering_fix()
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")