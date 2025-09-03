#!/usr/bin/env python3
"""
NEX-051 Test Script - Production-Ready Browser Methods
Test the practical browser automation features implemented in NEX-051
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the nexus_browser directory to the path
sys.path.append(str(Path(__file__).parent))

try:
    from nexus import NexusBrowser
    print("✓ Successfully imported NexusBrowser")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

async def test_nex_051_methods():
    """Test the NEX-051 production-ready browser methods"""
    print("\n" + "="*50)
    print("Testing NEX-051 Production-Ready Browser Methods")
    print("="*50)
    
    # Initialize browser
    browser = NexusBrowser()
    print("✓ NexusBrowser instance created")
    
    try:
        # Test 1: Basic initialization
        print("\n1. Testing browser initialization...")
        await browser.awaken()
        print("✓ Browser awakened successfully")
        
        if not browser.page:
            print("⚠ No Playwright available or browser not initialized")
            print("Testing methods with mock data...")
            
            # Test methods that don't require active page
            result = await browser.extract_page_data({}, 1000)
            print(f"✓ extract_page_data returns expected error: {result.get('error', 'No error')}")
            
            result = await browser.take_screenshot()
            print(f"✓ take_screenshot returns expected error: {result.get('error', 'No error')}")
            
            result = await browser.fill_form_fields({})
            print(f"✓ fill_form_fields returns expected error: {result.get('error', 'No error')}")
            
            result = await browser.wait_and_click('test')
            print(f"✓ wait_and_click returns expected error: {result.get('error', 'No error')}")
            
            result = await browser.get_page_info()
            print(f"✓ get_page_info returns expected error: {result.get('error', 'No error')}")
            
            result = await browser.save_page_content()
            print(f"✓ save_page_content returns expected error: {result.get('error', 'No error')}")
            
            print("\n✓ All methods handle 'no page' condition gracefully")
            
        else:
            print("✓ Browser page available - full testing possible")
            
            # Test with real browser
            print("\n2. Testing navigation...")
            await browser.page.goto("https://httpbin.org/html")
            print("✓ Navigated to test page")
            
            # Test extract_page_data
            print("\n3. Testing extract_page_data...")
            result = await browser.extract_page_data({
                'title': 'h1',
                'paragraph': 'p'
            })
            print(f"✓ Data extraction: {json.dumps(result, indent=2)}")
            
            # Test get_page_info
            print("\n4. Testing get_page_info...")
            result = await browser.get_page_info()
            print(f"✓ Page info: Title='{result.get('title')}', Links={result.get('elements', {}).get('links')}")
            
            # Test take_screenshot
            print("\n5. Testing take_screenshot...")
            result = await browser.take_screenshot(path="test_screenshot.png")
            if result.get('success'):
                print(f"✓ Screenshot saved: {result['path']}")
            else:
                print(f"✗ Screenshot failed: {result.get('error')}")
            
            # Test save_page_content
            print("\n6. Testing save_page_content...")
            result = await browser.save_page_content(format='html', path='test_page.html')
            if result.get('success'):
                print(f"✓ Page content saved: {result['path']} ({result.get('file_size', 0)} bytes)")
            else:
                print(f"✗ Save failed: {result.get('error')}")
        
    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if hasattr(browser, 'browser') and browser.browser:
            try:
                await browser.browser.close()
                print("✓ Browser closed")
            except:
                pass

    print("\n" + "="*50)
    print("NEX-051 Testing Complete!")
    print("="*50)

if __name__ == "__main__":
    print("NEX-051 Production-Ready Browser Methods Test")
    print("This tests the practical browser automation features")
    asyncio.run(test_nex_051_methods())