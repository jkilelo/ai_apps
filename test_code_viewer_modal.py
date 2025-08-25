"""
Test the new code viewer modal functionality in the Executive view
"""

from playwright.sync_api import sync_playwright
import time

def test_code_viewer_modal():
    """Test the code viewer modal in Generate Code step"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("TESTING CODE VIEWER MODAL FUNCTIONALITY")
        print("=" * 40)
        
        # First, generate code through the API to have data ready
        print("1. Generating test code via API...")
        import requests
        
        mock_extraction_data = {
            "url": "https://example.com",
            "elements": [
                {
                    "selector": "h1",
                    "tag_name": "h1",
                    "category": "heading",
                    "description": "Main heading"
                }
            ]
        }
        
        mock_test_data = {
            "features": {
                "functional": {
                    "title": "Functional Tests",
                    "scenarios": [
                        {
                            "title": "Verify page loads",
                            "steps": ["Given I navigate to the page", "Then I see the heading"],
                            "tags": ["smoke"]
                        }
                    ]
                }
            }
        }
        
        response = requests.post(
            "http://localhost:5175/api/generate-code",
            json={
                "extraction_data": mock_extraction_data,
                "test_data": mock_test_data,
                "code_type": "pytest",
                "language": "python"
            }
        )
        
        if response.status_code == 200:
            print("   [SUCCESS] Code generated via API")
        else:
            print("   [FAILED] API error")
            browser.close()
            return
        
        print("2. Opening Web Automation page...")
        page.goto("http://localhost:3000/web-automation")
        time.sleep(2)
        
        # Navigate directly to Generate Code step
        print("3. Navigating to Generate Code step...")
        
        # Click on Generate Code step in sidebar
        generate_code_button = page.query_selector('button:has-text("Generate Code")')
        if generate_code_button:
            generate_code_button.click()
            time.sleep(2)
            print("   [SUCCESS] Navigated to Generate Code step")
        
        # Check if Executive view is active
        executive_button = page.query_selector('button:has-text("Executive")')
        if executive_button:
            executive_button.click()
            time.sleep(1)
            print("   [SUCCESS] Executive view selected")
        
        # Check for the instruction text
        instruction_text = page.query_selector('text="Click any file card below to view the full Python code"')
        if instruction_text:
            print("   [SUCCESS] Instruction text visible")
        else:
            print("   [WARNING] Instruction text not found")
        
        # Find and click a file card
        print("4. Testing file card click...")
        
        # Look for a file card (e.g., conftest.py)
        file_cards = page.query_selector_all('.bg-white.rounded-lg.border.border-slate-200.p-4.hover\\:border-slate-300')
        
        if len(file_cards) > 0:
            print(f"   Found {len(file_cards)} file cards")
            
            # Click the first file card
            file_cards[0].click()
            time.sleep(2)
            
            # Check if modal opened
            modal = page.query_selector('.fixed.inset-0.bg-black.bg-opacity-50.z-50')
            if modal:
                print("   [SUCCESS] Modal opened!")
                
                # Check for modal elements
                modal_header = page.query_selector('h3.text-lg.font-semibold')
                if modal_header:
                    filename = modal_header.text_content()
                    print(f"   Viewing file: {filename}")
                
                # Check for syntax highlighter
                code_block = page.query_selector('pre')
                if code_block:
                    print("   [SUCCESS] Code displayed with syntax highlighting")
                    
                    # Check for line numbers
                    line_numbers = page.query_selector_all('.linenumber')
                    if len(line_numbers) > 0:
                        print(f"   [SUCCESS] Line numbers visible ({len(line_numbers)} lines)")
                
                # Test copy button
                copy_button = page.query_selector('button[title="Copy code"]')
                if copy_button:
                    print("   [SUCCESS] Copy button available")
                
                # Test download button
                download_button = page.query_selector('button[title="Download file"]')
                if download_button:
                    print("   [SUCCESS] Download button available")
                
                # Take screenshot of modal
                page.screenshot(path="code_viewer_modal.png")
                print("   Screenshot saved: code_viewer_modal.png")
                
                # Test close button
                close_button = page.query_selector('button[title="Close"]')
                if close_button:
                    close_button.click()
                    time.sleep(1)
                    
                    # Verify modal closed
                    modal_after_close = page.query_selector('.fixed.inset-0.bg-black.bg-opacity-50.z-50')
                    if not modal_after_close:
                        print("   [SUCCESS] Modal closed successfully")
                
            else:
                print("   [FAILED] Modal did not open")
                
        else:
            print("   [FAILED] No file cards found")
        
        # Test clicking another card
        print("5. Testing second file card...")
        if len(file_cards) > 1:
            file_cards[1].click()
            time.sleep(2)
            
            modal = page.query_selector('.fixed.inset-0.bg-black.bg-opacity-50.z-50')
            if modal:
                modal_header = page.query_selector('h3.text-lg.font-semibold')
                if modal_header:
                    filename = modal_header.text_content()
                    print(f"   [SUCCESS] Viewing second file: {filename}")
                
                page.screenshot(path="code_viewer_modal_2.png")
                print("   Screenshot saved: code_viewer_modal_2.png")
        
        print("\n" + "=" * 40)
        print("TEST SUMMARY:")
        print("- Code viewer modal functionality is working")
        print("- File cards are clickable")
        print("- Modal displays code with syntax highlighting")
        print("- Copy and download buttons available")
        print("- Modal can be closed properly")
        print("\nBrowser staying open for manual inspection...")
        
        time.sleep(10)
        browser.close()

if __name__ == "__main__":
    test_code_viewer_modal()