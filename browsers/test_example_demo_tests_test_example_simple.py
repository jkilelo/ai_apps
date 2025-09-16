
import pytest
from playwright.sync_api import Page
from pages.examplepage import ExamplePage

def test_example_com_loads():
    """Test that example.com loads successfully."""
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Use the dynamically generated page object
        example_page = ExamplePage(page)
        example_page.navigate_to()
        
        # Verify the page loaded
        assert "Example Domain" in page.title()
        print("[OK] Example.com loaded successfully")
        
        browser.close()

if __name__ == "__main__":
    test_example_com_loads()
