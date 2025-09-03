#!/usr/bin/env python3
"""
NEX-057 Test Script - Advanced Production Browser Automation Features
Test the advanced authentication, link extraction, downloads, CAPTCHA, console monitoring, and network simulation
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

async def test_nex_057_methods():
    """Test the NEX-057 advanced production browser automation features"""
    print("\n" + "="*70)
    print("TESTING NEX-057 ADVANCED PRODUCTION BROWSER AUTOMATION FEATURES")
    print("="*70)
    
    # Initialize browser
    browser = NexusBrowser()
    print("SUCCESS: Browser instance created")
    
    # Check method availability
    nex_057_methods = [
        'handle_authentication',
        'extract_links',
        'handle_file_downloads',
        'detect_and_handle_captcha',
        'monitor_console_logs',
        'simulate_network_conditions'
    ]
    
    print("\n1. CHECKING METHOD AVAILABILITY:")
    for method_name in nex_057_methods:
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
            await test_without_browser(browser, nex_057_methods)
            return
        
        print("SUCCESS: Browser initialized with Playwright")
        
        # Navigate to a test page
        await browser.page.goto("https://httpbin.org/")
        
        # Test handle_authentication
        print("\n" + "-"*60)
        print("TESTING: handle_authentication()")
        print("-"*60)
        
        # Test basic auth setup
        basic_auth_result = await browser.handle_authentication(
            auth_type='basic',
            credentials={'username': 'testuser', 'password': 'testpass'}
        )
        print("BASIC AUTH RESULT:", json.dumps(basic_auth_result, indent=2))
        
        # Test form auth (will fail on httpbin but demonstrates the structure)
        form_auth_result = await browser.handle_authentication(
            auth_type='form',
            credentials={
                'username': 'testuser',
                'password': 'testpass',
                'username_selector': 'input[name="username"]',
                'password_selector': 'input[name="password"]',
                'submit_selector': 'button[type="submit"]'
            }
        )
        print("FORM AUTH RESULT:", json.dumps(form_auth_result, indent=2))
        
        if basic_auth_result.get('success'):
            print("SUCCESS: Authentication handling working")
        
        # Test extract_links
        print("\n" + "-"*60)
        print("TESTING: extract_links()")
        print("-"*60)
        
        # Navigate to a page with links
        await browser.page.goto("https://httpbin.org/html")
        
        # Extract all links
        all_links_result = await browser.extract_links(filter_type='all')
        print("ALL LINKS RESULT:", json.dumps({
            'success': all_links_result.get('success'),
            'total_links': all_links_result.get('total_links'),
            'categories': all_links_result.get('categories')
        }, indent=2))
        
        # Extract internal links only
        internal_links_result = await browser.extract_links(filter_type='internal')
        print("INTERNAL LINKS:", json.dumps({
            'success': internal_links_result.get('success'),
            'filtered_count': internal_links_result.get('filtered_count')
        }, indent=2))
        
        if all_links_result.get('success'):
            print(f"SUCCESS: Link extraction working, found {all_links_result.get('total_links')} links")
        
        # Test handle_file_downloads
        print("\n" + "-"*60)
        print("TESTING: handle_file_downloads()")
        print("-"*60)
        
        download_result = await browser.handle_file_downloads(
            auto_accept=True,
            download_path="test_downloads"
        )
        print("DOWNLOAD CONFIG RESULT:", json.dumps(download_result, indent=2))
        
        if download_result.get('success'):
            print(f"SUCCESS: Download handling configured, path: {download_result.get('download_path')}")
        
        # Test detect_and_handle_captcha
        print("\n" + "-"*60)
        print("TESTING: detect_and_handle_captcha()")
        print("-"*60)
        
        captcha_result = await browser.detect_and_handle_captcha(solver_type='manual')
        print("CAPTCHA DETECTION RESULT:", json.dumps(captcha_result, indent=2))
        
        if captcha_result.get('success'):
            if captcha_result.get('captcha_detected'):
                print(f"CAPTCHA detected: {captcha_result.get('captcha_type')}")
            else:
                print("SUCCESS: No CAPTCHA detected on current page")
        
        # Test monitor_console_logs
        print("\n" + "-"*60)
        print("TESTING: monitor_console_logs()")
        print("-"*60)
        
        console_result = await browser.monitor_console_logs(log_level='all')
        print("CONSOLE MONITORING RESULT:", json.dumps({
            'success': console_result.get('success'),
            'monitoring_active': console_result.get('monitoring_active'),
            'total_logs_captured': console_result.get('total_logs_captured'),
            'log_summary': console_result.get('log_summary')
        }, indent=2))
        
        # Execute some JavaScript to generate console logs
        await browser.page.evaluate("""
            () => {
                console.log('Test log message');
                console.error('Test error message');
                console.warn('Test warning message');
                console.info('Test info message');
            }
        """)
        
        # Check logs again
        await asyncio.sleep(0.5)  # Give time for logs to be captured
        console_result2 = await browser.monitor_console_logs(log_level='all')
        
        if console_result2.get('success'):
            logs_captured = console_result2.get('total_logs_captured', 0)
            print(f"SUCCESS: Console monitoring working, captured {logs_captured} logs")
            if console_result2.get('recent_logs'):
                print("Recent logs sample:", console_result2['recent_logs'][:3])
        
        # Test simulate_network_conditions
        print("\n" + "-"*60)
        print("TESTING: simulate_network_conditions()")
        print("-"*60)
        
        # Test different network profiles
        network_profiles = ['slow3g', 'fast3g', '4g']
        
        for profile in network_profiles:
            network_result = await browser.simulate_network_conditions(profile=profile)
            print(f"\n{profile.upper()} SIMULATION:", json.dumps({
                'success': network_result.get('success'),
                'profile': network_result.get('profile'),
                'test_duration': network_result.get('test_duration'),
                'expected_behavior': network_result.get('expected_behavior')
            }, indent=2))
            
            if network_result.get('success'):
                print(f"SUCCESS: Network simulation for {profile} applied")
        
        # Reset to normal network
        wifi_result = await browser.simulate_network_conditions(profile='wifi')
        print("\nReset to WIFI:", json.dumps({
            'success': wifi_result.get('success'),
            'profile': wifi_result.get('profile')
        }, indent=2))
        
        print("\n" + "="*70)
        print("NEX-057 ADVANCED PRODUCTION BROWSER AUTOMATION FEATURES TESTED!")
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
        ('handle_authentication', ('basic', {'username': 'test', 'password': 'test'})),
        ('extract_links', ()),
        ('handle_file_downloads', ()),
        ('detect_and_handle_captcha', ()),
        ('monitor_console_logs', ()),
        ('simulate_network_conditions', ())
    ]
    
    for method_name, args in test_calls:
        if hasattr(browser, method_name):
            method = getattr(browser, method_name)
            result = await method(*args)
            
            if 'error' in result and 'No active page available' in result['error']:
                print(f"SUCCESS: {method_name}() handles no-browser condition correctly")
            else:
                print(f"WARNING: {method_name}() unexpected response: {result}")
        else:
            print(f"SKIP: {method_name}() not available")

if __name__ == "__main__":
    print("NEX-057 Advanced Production Browser Automation Features Test")
    print("Testing 6 new production-ready browser features")
    
    asyncio.run(test_nex_057_methods())