"""
Manual check of the Generate Tests view modes implementation
"""

from playwright.sync_api import sync_playwright
import time

def manual_check_view_modes():
    """Open browser and wait for manual inspection of view modes"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("1. Opening Web Automation page...")
        page.goto("http://localhost:3000/web-automation")
        time.sleep(2)
        
        print("\nMANUAL TEST INSTRUCTIONS:")
        print("1. Click 'Example.com' button")
        print("2. Click 'Start Extraction' and wait for completion")
        print("3. Click 'Continue to Test Generation'")
        print("4. Wait for test generation to complete")
        print("5. Look for Executive/Developer toggle buttons")
        print("6. Test both view modes")
        print("\nThe browser will stay open for 60 seconds for manual testing...")
        
        # Keep browser open for manual testing
        time.sleep(60)
        
        print("Closing browser...")
        browser.close()

if __name__ == "__main__":
    manual_check_view_modes()