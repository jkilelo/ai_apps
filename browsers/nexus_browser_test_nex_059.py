#!/usr/bin/env python3
"""
NEX-059 Test Script - Advanced Web Scraping and Data Processing Features
Test table extraction, page monitoring, popup handling, media extraction, visual regression, and JS execution
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

async def test_nex_059_methods():
    """Test the NEX-059 advanced web scraping and data processing features"""
    print("\n" + "="*70)
    print("TESTING NEX-059 ADVANCED WEB SCRAPING AND DATA PROCESSING")
    print("="*70)
    
    # Initialize browser
    browser = NexusBrowser()
    print("SUCCESS: Browser instance created")
    
    # Check method availability
    nex_059_methods = [
        'extract_tables',
        'monitor_page_changes',
        'handle_popup_windows',
        'extract_media_content',
        'perform_visual_regression',
        'execute_javascript_code'
    ]
    
    print("\n1. CHECKING METHOD AVAILABILITY:")
    for method_name in nex_059_methods:
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
            await test_without_browser(browser, nex_059_methods)
            return
        
        print("SUCCESS: Browser initialized with Playwright")
        
        # Navigate to a test page
        await browser.page.goto("https://httpbin.org/html")
        
        # Test extract_tables
        print("\n" + "-"*60)
        print("TESTING: extract_tables()")
        print("-"*60)
        
        # Test different formats
        for format_type in ['json', 'csv', 'markdown']:
            table_result = await browser.extract_tables(format=format_type)
            print(f"{format_type.upper()} FORMAT:", json.dumps({
                'success': table_result.get('success'),
                'format': table_result.get('format'),
                'tables_found': table_result.get('tables_found')
            }, indent=2))
            
            if table_result.get('success') and table_result.get('tables_found', 0) > 0:
                print(f"  Found {table_result.get('tables_found')} tables")
        
        # Test monitor_page_changes
        print("\n" + "-"*60)
        print("TESTING: monitor_page_changes()")
        print("-"*60)
        
        # Monitor for a short duration
        monitor_result = await browser.monitor_page_changes(duration=2000, check_interval=500)
        print("MONITORING RESULT:", json.dumps({
            'success': monitor_result.get('success'),
            'checks_performed': monitor_result.get('checks_performed'),
            'total_changes': monitor_result.get('total_changes'),
            'duration_ms': monitor_result.get('duration_ms')
        }, indent=2))
        
        if monitor_result.get('success'):
            print(f"SUCCESS: Performed {monitor_result.get('checks_performed')} checks, detected {monitor_result.get('total_changes')} changes")
        
        # Test handle_popup_windows
        print("\n" + "-"*60)
        print("TESTING: handle_popup_windows()")
        print("-"*60)
        
        popup_result = await browser.handle_popup_windows()
        print("POPUP HANDLING RESULT:", json.dumps({
            'success': popup_result.get('success'),
            'potential_popup_triggers': popup_result.get('potential_popup_triggers'),
            'popups_handled': popup_result.get('popups_handled'),
            'modal_dialogs': popup_result.get('modal_dialogs')
        }, indent=2))
        
        if popup_result.get('success'):
            print(f"SUCCESS: Found {popup_result.get('potential_popup_triggers', 0)} potential popup triggers")
        
        # Test extract_media_content
        print("\n" + "-"*60)
        print("TESTING: extract_media_content()")
        print("-"*60)
        
        media_result = await browser.extract_media_content()
        print("MEDIA EXTRACTION RESULT:", json.dumps({
            'success': media_result.get('success'),
            'media_summary': media_result.get('media_summary'),
            'media_statistics': media_result.get('media_statistics')
        }, indent=2))
        
        if media_result.get('success'):
            summary = media_result.get('media_summary', {})
            print(f"SUCCESS: Found {summary.get('total_images', 0)} images, {summary.get('total_videos', 0)} videos, {summary.get('total_audio', 0)} audio")
        
        # Test perform_visual_regression
        print("\n" + "-"*60)
        print("TESTING: perform_visual_regression()")
        print("-"*60)
        
        visual_result = await browser.perform_visual_regression()
        print("VISUAL REGRESSION RESULT:", json.dumps({
            'success': visual_result.get('success'),
            'screenshot_size': visual_result.get('screenshot_size'),
            'page_dimensions': visual_result.get('page_dimensions'),
            'comparison': visual_result.get('comparison'),
            'critical_elements': len(visual_result.get('critical_elements', []))
        }, indent=2))
        
        if visual_result.get('success'):
            print(f"SUCCESS: Screenshot captured ({visual_result.get('screenshot_size', 0)} bytes)")
            print(f"  Critical elements found: {len(visual_result.get('critical_elements', []))}")
        
        # Test execute_javascript_code
        print("\n" + "-"*60)
        print("TESTING: execute_javascript_code()")
        print("-"*60)
        
        # Test safe JavaScript execution
        safe_code = "return document.title + ' - ' + window.location.hostname;"
        js_result = await browser.execute_javascript_code(safe_code, safe_mode=True)
        print("SAFE JS EXECUTION:", json.dumps({
            'success': js_result.get('success'),
            'result': js_result.get('result'),
            'type': js_result.get('type'),
            'safe_mode': js_result.get('safe_mode')
        }, indent=2))
        
        # Test dangerous code detection
        dangerous_code = "localStorage.setItem('test', 'value');"
        danger_result = await browser.execute_javascript_code(dangerous_code, safe_mode=True)
        print("DANGEROUS CODE TEST:", json.dumps({
            'success': danger_result.get('success'),
            'error': danger_result.get('error'),
            'violations': danger_result.get('violations', [])
        }, indent=2))
        
        if js_result.get('success'):
            print(f"SUCCESS: Safe JavaScript executed, result: {js_result.get('result')}")
        if not danger_result.get('success') and 'violations' in danger_result:
            print(f"SUCCESS: Dangerous code blocked, violations: {danger_result.get('violations')}")
        
        print("\n" + "="*70)
        print("NEX-059 ADVANCED WEB SCRAPING AND DATA PROCESSING TESTED!")
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
        ('extract_tables', ()),
        ('monitor_page_changes', ()),
        ('handle_popup_windows', ()),
        ('extract_media_content', ()),
        ('perform_visual_regression', ()),
        ('execute_javascript_code', ('test code',))
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
    print("NEX-059 Advanced Web Scraping and Data Processing Features Test")
    print("Testing 6 advanced data extraction and processing features")
    
    asyncio.run(test_nex_059_methods())