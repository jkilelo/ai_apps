#!/usr/bin/env python3
"""
NEX-061 Test Script - Additional Practical Web Automation Features
Test infinite scroll, social media extraction, SEO audit, ad detection, contact extraction, AJAX monitoring
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

async def test_nex_061_methods():
    """Test the NEX-061 additional practical web automation features"""
    print("\n" + "="*70)
    print("TESTING NEX-061 ADDITIONAL PRACTICAL WEB AUTOMATION FEATURES")
    print("="*70)
    
    # Initialize browser
    browser = NexusBrowser()
    print("SUCCESS: Browser instance created")
    
    # Check method availability
    nex_061_methods = [
        'handle_infinite_scroll',
        'extract_social_media_data',
        'perform_seo_audit',
        'detect_and_block_ads',
        'extract_contact_information',
        'monitor_ajax_requests'
    ]
    
    print("\n1. CHECKING METHOD AVAILABILITY:")
    for method_name in nex_061_methods:
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
            await test_without_browser(browser, nex_061_methods)
            return
        
        print("SUCCESS: Browser initialized with Playwright")
        
        # Navigate to a test page
        await browser.page.goto("https://httpbin.org/html")
        
        # Test handle_infinite_scroll
        print("\n" + "-"*60)
        print("TESTING: handle_infinite_scroll()")
        print("-"*60)
        
        scroll_result = await browser.handle_infinite_scroll(
            max_scrolls=3,
            wait_time=500,
            content_selector='p'
        )
        print("INFINITE SCROLL RESULT:", json.dumps({
            'success': scroll_result.get('success'),
            'total_scrolls': scroll_result.get('scroll_statistics', {}).get('total_scrolls'),
            'reached_end': scroll_result.get('scroll_statistics', {}).get('reached_end'),
            'content_loaded': scroll_result.get('content_loaded', {})
        }, indent=2))
        
        if scroll_result.get('success'):
            stats = scroll_result.get('scroll_statistics', {})
            content = scroll_result.get('content_loaded', {})
            print(f"SUCCESS: Scrolled {stats.get('total_scrolls')} times, loaded {content.get('images')} images")
        
        # Test extract_social_media_data
        print("\n" + "-"*60)
        print("TESTING: extract_social_media_data()")
        print("-"*60)
        
        social_result = await browser.extract_social_media_data()
        print("SOCIAL MEDIA EXTRACTION RESULT:", json.dumps({
            'success': social_result.get('success'),
            'platform': social_result.get('platform'),
            'statistics': social_result.get('statistics')
        }, indent=2))
        
        if social_result.get('success'):
            stats = social_result.get('statistics', {})
            print(f"SUCCESS: Found {stats.get('total_share_buttons')} share buttons, {stats.get('total_profile_links')} profile links")
        
        # Test perform_seo_audit
        print("\n" + "-"*60)
        print("TESTING: perform_seo_audit()")
        print("-"*60)
        
        seo_result = await browser.perform_seo_audit()
        print("SEO AUDIT RESULT:", json.dumps({
            'success': seo_result.get('success'),
            'seo_score': seo_result.get('seo_score'),
            'grade': seo_result.get('grade'),
            'issues_found': len(seo_result.get('issues_found', []))
        }, indent=2))
        
        if seo_result.get('success'):
            print(f"SUCCESS: SEO Score: {seo_result.get('seo_score')}/100 (Grade: {seo_result.get('grade')})")
            issues = seo_result.get('issues_found', [])
            if issues:
                print(f"  Issues found: {', '.join(issues[:3])}")
            recommendations = seo_result.get('recommendations', [])
            if recommendations:
                print(f"  Top recommendation: {recommendations[0]}")
        
        # Test detect_and_block_ads
        print("\n" + "-"*60)
        print("TESTING: detect_and_block_ads()")
        print("-"*60)
        
        # First detect ads
        ad_detect_result = await browser.detect_and_block_ads(action='detect')
        print("AD DETECTION RESULT:", json.dumps({
            'success': ad_detect_result.get('success'),
            'action': ad_detect_result.get('action'),
            'ads_detected': ad_detect_result.get('ads_detected'),
            'ad_networks': ad_detect_result.get('ad_networks')
        }, indent=2))
        
        # Then try blocking
        ad_block_result = await browser.detect_and_block_ads(action='block')
        print("AD BLOCKING RESULT:", json.dumps({
            'success': ad_block_result.get('success'),
            'action': ad_block_result.get('action'),
            'ads_blocked': ad_block_result.get('ads_blocked')
        }, indent=2))
        
        if ad_detect_result.get('success'):
            stats = ad_detect_result.get('statistics', {})
            print(f"SUCCESS: Found {stats.get('total_ads_found', 0)} ads, {stats.get('visible_ads', 0)} visible")
        
        # Test extract_contact_information
        print("\n" + "-"*60)
        print("TESTING: extract_contact_information()")
        print("-"*60)
        
        contact_result = await browser.extract_contact_information()
        print("CONTACT EXTRACTION RESULT:", json.dumps({
            'success': contact_result.get('success'),
            'statistics': contact_result.get('statistics'),
            'confidence': contact_result.get('confidence')
        }, indent=2))
        
        if contact_result.get('success'):
            stats = contact_result.get('statistics', {})
            contact_info = contact_result.get('contact_information', {})
            print(f"SUCCESS: Found {stats.get('emails_found')} emails, {stats.get('phones_found')} phones")
            if contact_info.get('emails'):
                print(f"  Sample email: {contact_info['emails'][0][:20]}...")
        
        # Test monitor_ajax_requests
        print("\n" + "-"*60)
        print("TESTING: monitor_ajax_requests()")
        print("-"*60)
        
        # Navigate to a page with AJAX requests
        await browser.page.goto("https://httpbin.org/")
        
        ajax_result = await browser.monitor_ajax_requests(
            duration=2000,
            filter_pattern=None
        )
        print("AJAX MONITORING RESULT:", json.dumps({
            'success': ajax_result.get('success'),
            'monitoring_duration_ms': ajax_result.get('monitoring_duration_ms'),
            'statistics': ajax_result.get('statistics')
        }, indent=2))
        
        if ajax_result.get('success'):
            stats = ajax_result.get('statistics', {})
            print(f"SUCCESS: Captured {stats.get('total_requests')} AJAX requests in 2 seconds")
            print(f"  Unique endpoints: {stats.get('unique_endpoints')}")
            print(f"  Requests per second: {stats.get('requests_per_second', 0):.2f}")
        
        print("\n" + "="*70)
        print("NEX-061 ADDITIONAL PRACTICAL WEB AUTOMATION FEATURES TESTED!")
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
        ('handle_infinite_scroll', ()),
        ('extract_social_media_data', ()),
        ('perform_seo_audit', ()),
        ('detect_and_block_ads', ()),
        ('extract_contact_information', ()),
        ('monitor_ajax_requests', ())
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
    print("NEX-061 Additional Practical Web Automation Features Test")
    print("Testing 6 advanced features: infinite scroll, social media, SEO, ads, contacts, AJAX")
    
    asyncio.run(test_nex_061_methods())