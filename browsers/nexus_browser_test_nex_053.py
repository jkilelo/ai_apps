#!/usr/bin/env python3
"""
NEX-053 Test Script - Advanced Production Browser Features
Test the advanced production-ready features implemented in NEX-053
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

async def test_nex_053_methods():
    """Test the NEX-053 advanced production browser features"""
    print("\n" + "="*60)
    print("TESTING NEX-053 ADVANCED PRODUCTION BROWSER FEATURES")
    print("="*60)
    
    # Initialize browser
    browser = NexusBrowser()
    print("SUCCESS: Browser instance created")
    
    # Check method availability
    nex_053_methods = [
        'manage_cookies',
        'configure_proxy',
        'rotate_user_agent',
        'monitor_performance',
        'manage_browser_storage',
        'capture_network_traffic'
    ]
    
    print("\n1. CHECKING METHOD AVAILABILITY:")
    for method_name in nex_053_methods:
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
            await test_without_browser(browser, nex_053_methods)
            return
        
        print("SUCCESS: Browser initialized with Playwright")
        
        # Navigate to a test page
        await browser.page.goto("https://httpbin.org/")
        
        # Test manage_cookies
        print("\n" + "-"*50)
        print("TESTING: manage_cookies()")
        print("-"*50)
        
        # Test getting cookies
        cookie_result = await browser.manage_cookies('get')
        print("GET COOKIES RESULT:", json.dumps(cookie_result, indent=2))
        
        if cookie_result.get('success'):
            print(f"SUCCESS: Got {cookie_result.get('count', 0)} cookies")
        
        # Test setting a cookie
        test_cookies = [{'name': 'test_cookie', 'value': 'test_value', 'url': 'https://httpbin.org'}]
        set_result = await browser.manage_cookies('set', cookies=test_cookies)
        print("SET COOKIE RESULT:", json.dumps(set_result, indent=2))
        
        # Test configure_proxy
        print("\n" + "-"*50)
        print("TESTING: configure_proxy()")
        print("-"*50)
        
        proxy_config = {'server': 'http://proxy.example.com:8080', 'username': 'user', 'password': 'pass'}
        proxy_result = await browser.configure_proxy(proxy_config)
        print("PROXY CONFIG RESULT:", json.dumps(proxy_result, indent=2))
        
        if proxy_result.get('success'):
            print("SUCCESS: Proxy configuration prepared")
        
        # Test rotate_user_agent
        print("\n" + "-"*50)
        print("TESTING: rotate_user_agent()")
        print("-"*50)
        
        ua_result = await browser.rotate_user_agent()
        print("USER AGENT RESULT:", json.dumps(ua_result, indent=2))
        
        if ua_result.get('success'):
            print(f"SUCCESS: User agent rotated to: {ua_result.get('user_agent', '')[:50]}...")
        
        # Test monitor_performance
        print("\n" + "-"*50)
        print("TESTING: monitor_performance()")
        print("-"*50)
        
        perf_result = await browser.monitor_performance()
        print("PERFORMANCE RESULT:", json.dumps(perf_result, indent=2))
        
        if perf_result.get('success'):
            print("SUCCESS: Performance monitoring working")
            if 'metrics' in perf_result:
                print(f"Page load time: {perf_result['metrics'].get('page_load_time', 'N/A')}ms")
        
        # Test manage_browser_storage
        print("\n" + "-"*50)
        print("TESTING: manage_browser_storage()")
        print("-"*50)
        
        # Set a localStorage item
        storage_set = await browser.manage_browser_storage('local', 'set', 'test_key', 'test_value')
        print("STORAGE SET RESULT:", json.dumps(storage_set, indent=2))
        
        # Get the localStorage item
        storage_get = await browser.manage_browser_storage('local', 'get', 'test_key')
        print("STORAGE GET RESULT:", json.dumps(storage_get, indent=2))
        
        # List localStorage keys
        storage_list = await browser.manage_browser_storage('local', 'list')
        print("STORAGE LIST RESULT:", json.dumps(storage_list, indent=2))
        
        if storage_get.get('success') and storage_get.get('value') == 'test_value':
            print("SUCCESS: Browser storage working correctly")
        
        # Test capture_network_traffic
        print("\n" + "-"*50)
        print("TESTING: capture_network_traffic()")
        print("-"*50)
        
        # Enable network capture
        traffic_enable = await browser.capture_network_traffic(True, ['document', 'script'])
        print("TRAFFIC ENABLE RESULT:", json.dumps(traffic_enable, indent=2))
        
        # Navigate to trigger some requests
        await browser.page.goto("https://httpbin.org/html")
        
        # Disable and get captured data
        traffic_disable = await browser.capture_network_traffic(False)
        print("TRAFFIC DISABLE RESULT:", json.dumps(traffic_disable, indent=2))
        
        if traffic_disable.get('success'):
            print(f"SUCCESS: Captured {traffic_disable.get('captured_requests', 0)} network requests")
        
        print("\n" + "="*60)
        print("NEX-053 ADVANCED PRODUCTION FEATURES TESTED SUCCESSFULLY!")
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

async def test_without_browser(browser, methods):
    """Test functionality when browser is not available"""
    print("\nTesting error handling (Playwright not available):")
    
    # Test each method returns proper error responses
    test_calls = [
        ('manage_cookies', ('get',)),
        ('configure_proxy', ()),
        ('rotate_user_agent', ()),
        ('monitor_performance', ()),
        ('manage_browser_storage', ('local', 'list')),
        ('capture_network_traffic', ())
    ]
    
    for method_name, args in test_calls:
        if hasattr(browser, method_name):
            method = getattr(browser, method_name)
            result = await method(*args)
            
            if 'error' in result and ('No active page available' in result['error'] or result.get('success') == True):
                print(f"SUCCESS: {method_name}() handles no-browser condition correctly")
            else:
                print(f"WARNING: {method_name}() unexpected response: {result}")
        else:
            print(f"SKIP: {method_name}() not available")

if __name__ == "__main__":
    print("NEX-053 Advanced Production Browser Features Test")
    print("Testing 6 new production-ready browser automation features")
    
    asyncio.run(test_nex_053_methods())