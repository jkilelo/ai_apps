#!/usr/bin/env python3
"""
NEX-054 Test Script - Production Web Scraping & Accessibility Features
Test the advanced web scraping and accessibility features implemented in NEX-054
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the nexus_browser directory to the path
sys.path.append(str(Path(__file__).parent))

try:
    from nexus import NexusBrowser
    print("SUCCESS: NexusBrowser imported successfully")
except Exception as e:
    print(f"ERROR: Import failed: {e}")
    sys.exit(1)

async def test_nex_054_methods():
    """Test the NEX-054 production web scraping and accessibility features"""
    print("\n" + "="*70)
    print("TESTING NEX-054 PRODUCTION WEB SCRAPING & ACCESSIBILITY FEATURES")
    print("="*70)
    
    # Initialize browser
    browser = NexusBrowser()
    print("SUCCESS: Browser instance created")
    
    # Check method availability
    nex_054_methods = [
        'extract_structured_data',
        'simulate_mobile_device',
        'check_accessibility',
        'debug_page_issues',
        'batch_url_processor',
        'generate_page_report'
    ]
    
    print("\n1. CHECKING METHOD AVAILABILITY:")
    for method_name in nex_054_methods:
        if hasattr(browser, method_name):
            method = getattr(browser, method_name)
            if callable(method):
                print(f"SUCCESS: {method_name} - Available and callable")
            else:
                print(f"ERROR: {method_name} - Not callable")
        else:
            print(f"ERROR: {method_name} - Not found")
    
    try:
        # Initialize browser with Playwright
        print("\n2. INITIALIZING BROWSER...")
        await browser.awaken()
        
        if not browser.page:
            print("WARNING: Playwright not available. Testing error handling only.")
            await test_without_browser(browser, nex_054_methods)
            return
        
        print("SUCCESS: Browser initialized with Playwright")
        
        # Navigate to a test page with various elements
        await browser.page.goto("https://httpbin.org/forms/post")
        
        # Test extract_structured_data
        print("\n" + "-"*60)
        print("TESTING: extract_structured_data()")
        print("-"*60)
        
        # Define extraction schema
        schema = {
            'title': {
                'selector': 'h1',
                'attribute': 'textContent',
                'transform': 'strip'
            },
            'form_inputs': {
                'selector': 'input[type="text"]',
                'attribute': 'name',
                'multiple': True
            },
            'textarea': {
                'selector': 'textarea',
                'attribute': 'name'
            }
        }
        
        extraction_result = await browser.extract_structured_data(schema)
        print("EXTRACTION RESULT:", json.dumps(extraction_result, indent=2))
        
        if extraction_result.get('success'):
            print("SUCCESS: Structured data extraction working")
        
        # Test simulate_mobile_device
        print("\n" + "-"*60)
        print("TESTING: simulate_mobile_device()")
        print("-"*60)
        
        mobile_result = await browser.simulate_mobile_device('iPhone 12')
        print("MOBILE SIMULATION RESULT:", json.dumps(mobile_result, indent=2))
        
        if mobile_result.get('success'):
            print(f"SUCCESS: Mobile device simulation for {mobile_result.get('device')}")
        
        # Test with different device
        ipad_result = await browser.simulate_mobile_device('iPad')
        print("IPAD SIMULATION RESULT:", json.dumps(ipad_result, indent=2))
        
        # Test check_accessibility
        print("\n" + "-"*60)
        print("TESTING: check_accessibility()")
        print("-"*60)
        
        accessibility_result = await browser.check_accessibility()
        print("ACCESSIBILITY RESULT:", json.dumps(accessibility_result, indent=2))
        
        if accessibility_result.get('success'):
            score = accessibility_result.get('accessibility_score', 0)
            print(f"SUCCESS: Accessibility check completed, score: {score}%")
        
        # Test debug_page_issues
        print("\n" + "-"*60)
        print("TESTING: debug_page_issues()")
        print("-"*60)
        
        debug_result = await browser.debug_page_issues()
        print("DEBUG RESULT:", json.dumps(debug_result, indent=2))
        
        if debug_result.get('success'):
            print("SUCCESS: Page debugging completed")
            perf = debug_result.get('performance', {})
            if 'loadTime' in perf:
                print(f"Page load time: {perf['loadTime']}ms")
        
        # Test batch_url_processor (with a small batch)
        print("\n" + "-"*60)
        print("TESTING: batch_url_processor()")
        print("-"*60)
        
        test_urls = [
            'https://httpbin.org/',
            'https://httpbin.org/html',
            'https://httpbin.org/json'
        ]
        
        # Define a simple callback function
        async def simple_callback(page):
            return {
                'title': await page.title(),
                'url': page.url
            }
        
        batch_result = await browser.batch_url_processor(test_urls, simple_callback, 2)
        print("BATCH PROCESSING RESULT:", json.dumps(batch_result, indent=2))
        
        if batch_result.get('success'):
            processed = batch_result.get('processed', 0)
            failed = batch_result.get('failed', 0)
            print(f"SUCCESS: Processed {processed} URLs, {failed} failed")
        
        # Test generate_page_report
        print("\n" + "-"*60)
        print("TESTING: generate_page_report()")
        print("-"*60)
        
        # Navigate back to a page for report generation
        await browser.page.goto("https://httpbin.org/html")
        
        report_result = await browser.generate_page_report(include_screenshots=True)
        print("PAGE REPORT RESULT:", json.dumps(report_result, indent=2))
        
        if report_result.get('success'):
            health_score = report_result.get('overall_health_score', 0)
            print(f"SUCCESS: Page report generated, health score: {health_score}%")
        
        print("\n" + "="*70)
        print("NEX-054 PRODUCTION WEB SCRAPING & ACCESSIBILITY FEATURES TESTED!")
        print("="*70)
        
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

async def test_without_browser(browser, methods):
    """Test functionality when browser is not available"""
    print("\nTesting error handling (Playwright not available):")
    
    # Test each method returns proper error responses
    test_calls = [
        ('extract_structured_data', ({'test': {'selector': 'h1'}},)),
        ('simulate_mobile_device', ()),
        ('check_accessibility', ()),
        ('debug_page_issues', ()),
        ('generate_page_report', ())
    ]
    
    for method_name, args in test_calls:
        if hasattr(browser, method_name):
            method = getattr(browser, method_name)
            result = await method(*args)
            
            if 'error' in result and ('No active page available' in result['error'] or 'No browser instance available' in result['error']):
                print(f"SUCCESS: {method_name}() handles no-browser condition correctly")
            else:
                print(f"WARNING: {method_name}() unexpected response: {result}")
        else:
            print(f"SKIP: {method_name}() not available")

if __name__ == "__main__":
    print("NEX-054 Production Web Scraping & Accessibility Features Test")
    print("Testing 6 new production-ready web automation features")
    
    asyncio.run(test_nex_054_methods())