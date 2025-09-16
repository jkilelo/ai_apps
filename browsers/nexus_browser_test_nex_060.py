#!/usr/bin/env python3
"""
NEX-060 Test Script - Final Set of Practical Web Automation Features
Test proxy management, rate limiting, caching, cookies, fingerprinting, and CAPTCHA solving
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

async def test_nex_060_methods():
    """Test the NEX-060 final set of practical web automation features"""
    print("\n" + "="*70)
    print("TESTING NEX-060 FINAL SET OF PRACTICAL WEB AUTOMATION FEATURES")
    print("="*70)
    
    # Initialize browser
    browser = NexusBrowser()
    print("SUCCESS: Browser instance created")
    
    # Check method availability
    nex_060_methods = [
        'manage_proxy_settings',
        'implement_rate_limiting',
        'setup_request_caching',
        'manage_advanced_cookies',
        'control_browser_fingerprint',
        'integrate_captcha_solver'
    ]
    
    print("\n1. CHECKING METHOD AVAILABILITY:")
    for method_name in nex_060_methods:
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
            await test_without_browser(browser, nex_060_methods)
            return
        
        print("SUCCESS: Browser initialized with Playwright")
        
        # Navigate to a test page
        await browser.page.goto("https://httpbin.org/")
        
        # Test manage_proxy_settings
        print("\n" + "-"*60)
        print("TESTING: manage_proxy_settings()")
        print("-"*60)
        
        # Test different proxy actions
        for action in ['get', 'test', 'rotate']:
            proxy_result = await browser.manage_proxy_settings(action=action)
            print(f"{action.upper()} ACTION:", json.dumps({
                'success': proxy_result.get('success'),
                'action': proxy_result.get('action')
            }, indent=2))
            
            if action == 'get':
                print(f"  Current proxy: {proxy_result.get('current_proxy', {})}")
            elif action == 'test' and proxy_result.get('proxy_test'):
                print(f"  IP Address: {proxy_result['proxy_test'].get('ip_address')}")
            elif action == 'rotate':
                print(f"  Rotated to: {proxy_result.get('rotated_proxy')}")
        
        # Test implement_rate_limiting
        print("\n" + "-"*60)
        print("TESTING: implement_rate_limiting()")
        print("-"*60)
        
        rate_limit_result = await browser.implement_rate_limiting(
            requests_per_second=2.0,
            burst_size=5
        )
        print("RATE LIMITING RESULT:", json.dumps({
            'success': rate_limit_result.get('success'),
            'config': rate_limit_result.get('rate_limit_config'),
            'effective_rate': rate_limit_result.get('test_results', {}).get('effective_rate')
        }, indent=2))
        
        if rate_limit_result.get('success'):
            test_results = rate_limit_result.get('test_results', {})
            print(f"SUCCESS: Rate limiting implemented - {test_results.get('effective_rate', 0):.2f} req/sec")
        
        # Test setup_request_caching
        print("\n" + "-"*60)
        print("TESTING: setup_request_caching()")
        print("-"*60)
        
        cache_result = await browser.setup_request_caching({
            'ttl_seconds': 60,
            'max_size_mb': 10,
            'cache_patterns': ['*.js', '*.css', '*.png']
        })
        print("CACHING RESULT:", json.dumps({
            'success': cache_result.get('success'),
            'cache_patterns': cache_result.get('cached_patterns'),
            'statistics': cache_result.get('cache_statistics')
        }, indent=2))
        
        if cache_result.get('success'):
            stats = cache_result.get('cache_statistics', {})
            print(f"SUCCESS: Caching setup - Hit rate: {stats.get('hit_rate', '0%')}")
        
        # Test manage_advanced_cookies
        print("\n" + "-"*60)
        print("TESTING: manage_advanced_cookies()")
        print("-"*60)
        
        # Test different cookie actions
        cookie_actions = ['get', 'export', 'clear']
        for action in cookie_actions:
            cookie_result = await browser.manage_advanced_cookies(action=action)
            print(f"{action.upper()} ACTION:", json.dumps({
                'success': cookie_result.get('success'),
                'action': cookie_result.get('action'),
                'statistics': cookie_result.get('statistics')
            }, indent=2))
            
            if cookie_result.get('success'):
                stats = cookie_result.get('statistics', {})
                print(f"  Total cookies: {stats.get('total_cookies', 0)}")
        
        # Test control_browser_fingerprint
        print("\n" + "-"*60)
        print("TESTING: control_browser_fingerprint()")
        print("-"*60)
        
        fingerprint_result = await browser.control_browser_fingerprint({
            'randomize_canvas': True,
            'randomize_webgl': True,
            'timezone': 'Europe/London',
            'language': 'en-GB'
        })
        print("FINGERPRINT CONTROL RESULT:", json.dumps({
            'success': fingerprint_result.get('success'),
            'stealth_features': fingerprint_result.get('stealth_features'),
            'fingerprint_tests': fingerprint_result.get('fingerprint_tests')
        }, indent=2))
        
        if fingerprint_result.get('success'):
            current_fp = fingerprint_result.get('current_fingerprint', {})
            print(f"SUCCESS: Fingerprint controlled - Platform: {current_fp.get('platform')}, Timezone: {current_fp.get('timezone')}")
        
        # Test integrate_captcha_solver
        print("\n" + "-"*60)
        print("TESTING: integrate_captcha_solver()")
        print("-"*60)
        
        # Test different solver types
        solver_types = ['manual', '2captcha', 'anti-captcha']
        for solver_type in solver_types:
            solver_result = await browser.integrate_captcha_solver(
                solver_type=solver_type,
                api_key='test_api_key_12345' if solver_type != 'manual' else None
            )
            print(f"{solver_type.upper()} SOLVER:", json.dumps({
                'success': solver_result.get('success'),
                'solver_type': solver_result.get('solver_type'),
                'captcha_detection': solver_result.get('captcha_detection', {}).get('count'),
                'solver_ready': solver_result.get('statistics', {}).get('solver_ready')
            }, indent=2))
            
            if solver_result.get('success'):
                detection = solver_result.get('captcha_detection', {})
                config = solver_result.get('solver_config', {})
                print(f"  CAPTCHAs detected: {detection.get('count', 0)}")
                if solver_type != 'manual':
                    print(f"  Supported types: {config.get('supported_types', [])}")
                    print(f"  Success rate: {config.get('success_rate', 'N/A')}")
        
        print("\n" + "="*70)
        print("NEX-060 FINAL SET OF PRACTICAL WEB AUTOMATION FEATURES TESTED!")
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
        ('manage_proxy_settings', ()),
        ('implement_rate_limiting', ()),
        ('setup_request_caching', ()),
        ('manage_advanced_cookies', ()),
        ('control_browser_fingerprint', ()),
        ('integrate_captcha_solver', ())
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
    print("NEX-060 Final Set of Practical Web Automation Features Test")
    print("Testing 6 advanced automation features: proxy, rate limiting, caching, cookies, fingerprinting, CAPTCHA")
    
    asyncio.run(test_nex_060_methods())