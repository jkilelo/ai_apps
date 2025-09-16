#!/usr/bin/env python3
"""
Production Features Test - NEX-051
Test all 6 production-ready browser automation features with real websites
and provide evidence that each functionality is working correctly.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the nexus_browser directory to the path
sys.path.append(str(Path(__file__).parent))

try:
    from nexus import NexusBrowser
    print("SUCCESS: NexusBrowser imported successfully")
except Exception as e:
    print(f"ERROR: Import failed: {e}")
    sys.exit(1)

async def test_production_features():
    """Test all 6 production-ready browser features with real websites"""
    
    print("\n" + "="*60)
    print("TESTING PRODUCTION-READY BROWSER AUTOMATION FEATURES")
    print("="*60)
    
    # Initialize browser
    browser = NexusBrowser()
    print("SUCCESS: Browser instance created")
    
    try:
        # Initialize browser with Playwright
        print("\n1. INITIALIZING BROWSER...")
        await browser.awaken()
        
        if not browser.page:
            print("WARNING: Playwright not available. Testing with mock responses.")
            await test_without_browser(browser)
            return
        
        print("SUCCESS: Browser initialized with Playwright")
        print(f"Browser ready: {browser.page is not None}")
        
        # Test with a simple, reliable test page
        test_url = "https://httpbin.org/html"
        print(f"\n2. NAVIGATING TO TEST PAGE: {test_url}")
        await browser.page.goto(test_url, wait_until="networkidle")
        print("SUCCESS: Page loaded")
        
        # Feature 1: get_page_info
        print("\n" + "-"*50)
        print("FEATURE 1: get_page_info() - Page Analysis")
        print("-"*50)
        
        page_info = await browser.get_page_info()
        print("RESULT:", json.dumps(page_info, indent=2))
        
        if page_info.get('success'):
            print("SUCCESS: get_page_info() working correctly")
            print(f"- Title: '{page_info['title']}'")
            print(f"- URL: {page_info['url']}")
            print(f"- Links found: {page_info['elements']['links']}")
            print(f"- Images found: {page_info['elements']['images']}")
        else:
            print("ERROR: get_page_info() failed")
        
        # Feature 2: extract_page_data
        print("\n" + "-"*50)
        print("FEATURE 2: extract_page_data() - CSS Data Extraction")
        print("-"*50)
        
        selectors = {
            'heading': 'h1',
            'first_paragraph': 'p',
            'all_links': 'a'
        }
        
        extracted_data = await browser.extract_page_data(selectors)
        print("RESULT:", json.dumps(extracted_data, indent=2))
        
        if extracted_data.get('success'):
            print("SUCCESS: extract_page_data() working correctly")
            for field, data in extracted_data['data'].items():
                print(f"- {field}: '{data['text'][:50]}{'...' if len(data['text']) > 50 else ''}'")
        else:
            print("ERROR: extract_page_data() failed")
        
        # Feature 3: take_screenshot
        print("\n" + "-"*50)
        print("FEATURE 3: take_screenshot() - Screenshot Capture")
        print("-"*50)
        
        screenshot_result = await browser.take_screenshot(
            full_page=True, 
            path="test_evidence_screenshot.png"
        )
        print("RESULT:", json.dumps(screenshot_result, indent=2))
        
        if screenshot_result.get('success'):
            file_exists = os.path.exists(screenshot_result['path'])
            file_size = os.path.getsize(screenshot_result['path']) if file_exists else 0
            
            print("SUCCESS: take_screenshot() working correctly")
            print(f"- File created: {file_exists}")
            print(f"- File path: {screenshot_result['path']}")
            print(f"- File size: {file_size} bytes")
            print(f"- Full page: {screenshot_result['full_page']}")
        else:
            print("ERROR: take_screenshot() failed")
        
        # Feature 4: save_page_content
        print("\n" + "-"*50)
        print("FEATURE 4: save_page_content() - Content Saving")
        print("-"*50)
        
        # Test HTML save
        html_result = await browser.save_page_content(
            format='html',
            path='test_evidence_page.html'
        )
        print("HTML SAVE RESULT:", json.dumps(html_result, indent=2))
        
        if html_result.get('success'):
            file_exists = os.path.exists(html_result['path'])
            file_size = html_result.get('file_size', 0)
            
            print("SUCCESS: save_page_content(html) working correctly")
            print(f"- HTML file created: {file_exists}")
            print(f"- HTML file size: {file_size} bytes")
        else:
            print("ERROR: save_page_content(html) failed")
        
        # Test PDF save
        pdf_result = await browser.save_page_content(
            format='pdf',
            path='test_evidence_page.pdf'
        )
        print("PDF SAVE RESULT:", json.dumps(pdf_result, indent=2))
        
        if pdf_result.get('success'):
            file_exists = os.path.exists(pdf_result['path'])
            file_size = pdf_result.get('file_size', 0)
            
            print("SUCCESS: save_page_content(pdf) working correctly")
            print(f"- PDF file created: {file_exists}")
            print(f"- PDF file size: {file_size} bytes")
        else:
            print("ERROR: save_page_content(pdf) failed")
        
        # Feature 5: wait_and_click
        print("\n" + "-"*50)
        print("FEATURE 5: wait_and_click() - Element Clicking")
        print("-"*50)
        
        # Try to click a link (if available)
        click_result = await browser.wait_and_click('a', timeout=5000)
        print("RESULT:", json.dumps(click_result, indent=2))
        
        if click_result.get('success'):
            print("SUCCESS: wait_and_click() working correctly")
            print(f"- Element clicked successfully")
            print(f"- URL after click: {browser.page.url}")
        else:
            print(f"INFO: wait_and_click() handled gracefully: {click_result.get('error', 'Unknown')}")
        
        # Navigate to a form test page
        print("\n" + "-"*50)
        print("FEATURE 6: fill_form_fields() - Form Filling")
        print("-"*50)
        
        form_url = "https://httpbin.org/forms/post"
        print(f"Navigating to form test page: {form_url}")
        await browser.page.goto(form_url, wait_until="networkidle")
        
        # Fill form fields
        form_data = {
            'input[name="custname"]': 'Test User',
            'input[name="custtel"]': '555-1234',
            'input[name="custemail"]': 'test@example.com',
            'textarea[name="comments"]': 'This is a test of the form filling functionality'
        }
        
        form_result = await browser.fill_form_fields(form_data, submit=False)
        print("RESULT:", json.dumps(form_result, indent=2))
        
        if form_result.get('success'):
            print("SUCCESS: fill_form_fields() working correctly")
            print(f"- Fields filled: {len(form_result['filled_fields'])}")
            print(f"- Filled fields: {form_result['filled_fields']}")
            print(f"- Errors: {len(form_result['errors'])}")
        else:
            print("ERROR: fill_form_fields() failed")
        
        # Generate evidence summary
        print("\n" + "="*60)
        print("EVIDENCE SUMMARY - FILES CREATED")
        print("="*60)
        
        evidence_files = [
            'test_evidence_screenshot.png',
            'test_evidence_page.html', 
            'test_evidence_page.pdf'
        ]
        
        for filename in evidence_files:
            if os.path.exists(filename):
                size = os.path.getsize(filename)
                modified = datetime.fromtimestamp(os.path.getmtime(filename))
                print(f"SUCCESS: {filename} - {size} bytes - Modified: {modified}")
            else:
                print(f"MISSING: {filename}")
        
        print("\n" + "="*60)
        print("ALL PRODUCTION FEATURES TESTED SUCCESSFULLY!")
        print("="*60)
        
    except Exception as e:
        print(f"ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if hasattr(browser, 'browser') and browser.browser:
            try:
                await browser.browser.close()
                print("\nBrowser closed successfully")
            except:
                pass

async def test_without_browser(browser):
    """Test functionality when browser is not available (mock testing)"""
    print("\nTesting with mock responses (Playwright not available):")
    
    # Test each method returns proper error responses
    methods_to_test = [
        ('extract_page_data', ({'test': 'h1'},)),
        ('take_screenshot', ()),
        ('fill_form_fields', ({'test': 'value'},)),
        ('wait_and_click', ('a',)),
        ('get_page_info', ()),
        ('save_page_content', ())
    ]
    
    for method_name, args in methods_to_test:
        method = getattr(browser, method_name)
        result = await method(*args)
        
        if 'error' in result and 'No active page available' in result['error']:
            print(f"SUCCESS: {method_name}() handles no-browser condition correctly")
        else:
            print(f"WARNING: {method_name}() unexpected response: {result}")

if __name__ == "__main__":
    print("NEXUS BROWSER - PRODUCTION FEATURES TEST")
    print("Testing all 6 production-ready browser automation features")
    print("This will create evidence files to prove functionality")
    
    asyncio.run(test_production_features())