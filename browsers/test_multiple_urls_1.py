"""
Test Multiple URLs in Web Automation
"""

from playwright.sync_api import sync_playwright
import time
import json

def test_multiple_urls():
    """Test Web Automation with multiple real URLs"""
    
    # URLs to test
    test_urls = [
        ("GitHub", "https://github.com"),
        ("Google", "https://www.google.com"),
        ("Stack Overflow", "https://stackoverflow.com")
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("Navigating to Web Automation page...")
        page.goto("http://localhost:3000/web-automation")
        time.sleep(2)
        
        for name, url in test_urls:
            print(f"\n{'='*50}")
            print(f"Testing: {name} ({url})")
            print('='*50)
            
            # Click on the quick select button for this site
            quick_button = page.query_selector(f'button:has-text("{name}")')
            if quick_button:
                print(f"1. Clicking quick select for {name}")
                quick_button.click()
                time.sleep(0.5)
            else:
                # Manually enter the URL
                print(f"1. Entering URL: {url}")
                url_input = page.query_selector('input[type="url"]')
                if url_input:
                    url_input.fill(url)
            
            # Click Start Extraction
            print("2. Starting extraction...")
            extract_button = page.query_selector('button:has-text("Start Extraction")')
            if extract_button:
                extract_button.click()
                
                # Wait for extraction to complete
                print("   Waiting for extraction to complete...")
                page.wait_for_selector('h3:has-text("Extracted Elements")', timeout=30000)
                
                # Check results
                print("3. Checking extraction results...")
                
                # Look for success message
                success_elem = page.query_selector('.bg-gradient-to-r.from-green-50')
                if success_elem:
                    success_text = success_elem.text_content()
                    print(f"   [SUCCESS] {success_text}")
                
                # Check elements by category
                category_section = page.query_selector('.bg-white.rounded-lg:has-text("Elements by Category")')
                if category_section:
                    categories = category_section.query_selector_all('.flex.items-center.justify-between')
                    print("   Elements found by category:")
                    for cat in categories[:3]:  # Show first 3 categories
                        cat_text = cat.text_content()
                        print(f"     - {cat_text}")
                
                # Check AI Analysis
                ai_section = page.query_selector('.bg-gradient-to-r.from-blue-50')
                if ai_section:
                    print("   [AI] Analysis available")
                
                # Take screenshot
                screenshot_name = f"test_{name.lower().replace(' ', '_')}.png"
                page.screenshot(path=screenshot_name)
                print(f"   Screenshot saved: {screenshot_name}")
                
                # Go back to step 1 for next test
                print("4. Going back to URL selection...")
                step1_button = page.query_selector('button:has-text("Web URL")')
                if step1_button:
                    step1_button.click()
                    time.sleep(1)
            
            time.sleep(2)  # Brief pause between tests
        
        print("\n" + "="*50)
        print("All tests complete!")
        print("="*50)
        
        # Keep browser open briefly
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    test_multiple_urls()