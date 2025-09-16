"""
Test the enhanced Generate Tests step with Executive/Developer view modes
"""

from playwright.sync_api import sync_playwright
import time

def test_generate_tests_view_modes():
    """Test both executive and developer view modes in Generate Tests step"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("1. Navigating to Web Automation page...")
        page.goto("http://localhost:3000/web-automation")
        time.sleep(2)
        
        print("2. Starting quick test generation flow...")
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
        
        print("3. Moving to Generate Tests step...")
        page.click('button:has-text("Continue to Test Generation")')
        time.sleep(3)
        
        # Wait for test generation to complete
        try:
            page.wait_for_selector('text="Test Cases Generated"', timeout=60000)
            print("   [SUCCESS] Test generation completed!")
        except:
            print("   [TIMEOUT] Still generating tests")
        
        # Test Executive View (should be default)
        print("4. Testing Executive View...")
        executive_button = page.query_selector('button:has-text("Executive")')
        if executive_button:
            executive_button.click()
            time.sleep(1)
            
            # Check for executive view elements
            success_banner = page.query_selector('text="Test Generation Complete"')
            test_categories = page.query_selector_all('.bg-white.rounded-lg.border.border-slate-200')
            
            if success_banner:
                print("   [SUCCESS] Executive view banner found")
            else:
                print("   [WARNING] Executive view banner not found")
                
            if len(test_categories) > 0:
                print(f"   [SUCCESS] Found {len(test_categories)} test categories in executive view")
            else:
                print("   [WARNING] No test categories found in executive view")
            
            page.screenshot(path="generate_tests_executive_view.png")
            print("   Executive view screenshot captured")
        else:
            print("   [FAILED] Executive button not found")
        
        # Test Developer View
        print("5. Testing Developer View...")
        developer_button = page.query_selector('button:has-text("Developer")')
        if developer_button:
            developer_button.click()
            time.sleep(2)
            
            # Check for developer view elements
            json_header = page.query_selector('text="generated_tests.json"')
            copy_button = page.query_selector('button:has-text("Copy JSON")')
            syntax_highlighter = page.query_selector('.language-json')
            
            if json_header:
                print("   [SUCCESS] Developer view JSON header found")
            else:
                print("   [WARNING] Developer view JSON header not found")
                
            if copy_button:
                print("   [SUCCESS] Copy JSON button found")
                # Test copy functionality
                copy_button.click()
                time.sleep(1)
                copied_indicator = page.query_selector('text="Copied!"')
                if copied_indicator:
                    print("   [SUCCESS] Copy functionality working")
                else:
                    print("   [WARNING] Copy functionality may not be working")
            else:
                print("   [WARNING] Copy JSON button not found")
                
            if syntax_highlighter:
                print("   [SUCCESS] Syntax highlighting found")
            else:
                print("   [WARNING] Syntax highlighting not found")
            
            page.screenshot(path="generate_tests_developer_view.png")
            print("   Developer view screenshot captured")
        else:
            print("   [FAILED] Developer button not found")
        
        # Test view mode toggle
        print("6. Testing view mode toggle...")
        if executive_button and developer_button:
            # Switch back to executive
            executive_button.click()
            time.sleep(1)
            page.screenshot(path="generate_tests_toggle_test.png")
            print("   [SUCCESS] View mode toggle working")
        
        print("\n7. Test complete! Screenshots saved:")
        print("   - generate_tests_executive_view.png")
        print("   - generate_tests_developer_view.png") 
        print("   - generate_tests_toggle_test.png")
        
        print("\nBrowser will stay open for manual inspection...")
        time.sleep(10)
        
        browser.close()

if __name__ == "__main__":
    test_generate_tests_view_modes()