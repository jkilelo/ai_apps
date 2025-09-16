"""
Test Executive and Developer View Modes
"""

from playwright.sync_api import sync_playwright
import time

def test_view_modes():
    """Test both Executive and Developer view modes"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("1. Navigating to Web Automation page...")
        page.goto("http://localhost:3000/web-automation")
        time.sleep(2)
        
        # Select GitHub from quick select
        print("2. Selecting GitHub from quick select...")
        github_button = page.query_selector('button:has-text("GitHub")')
        if github_button:
            github_button.click()
            time.sleep(0.5)
        
        # Start extraction
        print("3. Starting extraction...")
        start_button = page.query_selector('button:has-text("Start Extraction")')
        if start_button:
            start_button.click()
            
            # Wait for extraction to complete
            print("   Waiting for extraction to complete...")
            page.wait_for_selector('h3:has-text("Extraction Results")', timeout=30000)
            time.sleep(2)
            
            # Take screenshot of Executive view (default)
            print("4. Taking screenshot of Executive view...")
            page.screenshot(path="executive_view.png")
            
            # Switch to Developer view
            print("5. Switching to Developer view...")
            dev_button = page.query_selector('button:has-text("Developer")')
            if dev_button:
                dev_button.click()
                time.sleep(1)
                
                # Take screenshot of Developer view
                print("6. Taking screenshot of Developer view...")
                page.screenshot(path="developer_view.png")
                
                # Test copy button
                print("7. Testing copy JSON button...")
                copy_button = page.query_selector('button:has(.text-slate-400)')
                if copy_button:
                    copy_button.click()
                    print("   JSON copied to clipboard!")
                    time.sleep(1)
                
                # Switch back to Executive view
                print("8. Switching back to Executive view...")
                exec_button = page.query_selector('button:has-text("Executive")')
                if exec_button:
                    exec_button.click()
                    time.sleep(1)
        
        print("\nTest complete! Screenshots saved:")
        print("  - executive_view.png")
        print("  - developer_view.png")
        
        # Keep browser open briefly
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    test_view_modes()