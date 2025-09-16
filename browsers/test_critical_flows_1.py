"""
Test Critical Flows Display
"""

from playwright.sync_api import sync_playwright
import time

def test_critical_flows():
    """Test the Critical Flows display"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("1. Navigating to Web Automation page...")
        page.goto("http://localhost:3000/web-automation")
        time.sleep(2)
        
        print("2. Selecting GitHub...")
        page.click('button:has-text("GitHub")')
        time.sleep(0.5)
        
        print("3. Starting extraction...")
        page.click('button:has-text("Start Extraction")')
        
        # Wait for results
        page.wait_for_selector('h3:has-text("Extraction Results")', timeout=30000)
        time.sleep(3)
        
        # Try to scroll the content area
        print("4. Looking for scrollable content area...")
        content_area = page.query_selector('.overflow-auto')
        if content_area:
            print("   Found scrollable area, scrolling down...")
            content_area.evaluate('el => el.scrollTop = el.scrollHeight')
            time.sleep(1)
        
        # Look for Critical Test Scenarios section
        print("5. Looking for Critical Test Scenarios...")
        critical_section = page.query_selector('text="Critical Test Scenarios"')
        if critical_section:
            print("   [FOUND] Critical Test Scenarios section!")
            # Scroll it into view
            critical_section.scroll_into_view_if_needed()
            time.sleep(1)
        else:
            print("   [NOT FOUND] Critical Test Scenarios section not found")
        
        # Look for test flow cards
        flow_cards = page.query_selector_all('[class*="bg-gradient-to-r"][class*="border"][class*="rounded-xl"]')
        print(f"6. Found {len(flow_cards)} flow cards")
        
        # Take screenshot
        page.screenshot(path="critical_flows_test.png", full_page=True)
        print("\n7. Screenshot saved as critical_flows_test.png")
        
        # Keep browser open to inspect
        print("\nBrowser will stay open for inspection...")
        time.sleep(10)
        
        browser.close()

if __name__ == "__main__":
    test_critical_flows()