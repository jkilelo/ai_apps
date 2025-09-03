#!/usr/bin/env python3
"""
NEX-058 Test Script - More Production Browser Automation Features
Test multi-tab operations, metadata extraction, iframe handling, PDF generation, form automation, and security analysis
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

async def test_nex_058_methods():
    """Test the NEX-058 production browser automation features"""
    print("\n" + "="*70)
    print("TESTING NEX-058 MORE PRODUCTION BROWSER AUTOMATION FEATURES")
    print("="*70)
    
    # Initialize browser
    browser = NexusBrowser()
    print("SUCCESS: Browser instance created")
    
    # Check method availability
    nex_058_methods = [
        'handle_multi_tab_operations',
        'extract_metadata',
        'handle_iframe_content',
        'generate_page_pdf',
        'automate_form_filling',
        'analyze_page_security'
    ]
    
    print("\n1. CHECKING METHOD AVAILABILITY:")
    for method_name in nex_058_methods:
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
            await test_without_browser(browser, nex_058_methods)
            return
        
        print("SUCCESS: Browser initialized with Playwright")
        
        # Navigate to a test page
        await browser.page.goto("https://httpbin.org/html")
        
        # Test handle_multi_tab_operations
        print("\n" + "-"*60)
        print("TESTING: handle_multi_tab_operations()")
        print("-"*60)
        
        multi_tab_result = await browser.handle_multi_tab_operations(max_tabs=3)
        print("MULTI-TAB RESULT:", json.dumps({
            'success': multi_tab_result.get('success'),
            'total_tabs': multi_tab_result.get('total_tabs'),
            'new_tab_created': multi_tab_result.get('new_tab_created'),
            'tabs': len(multi_tab_result.get('tabs', []))
        }, indent=2))
        
        if multi_tab_result.get('success'):
            print(f"SUCCESS: Multi-tab operations working, {multi_tab_result.get('total_tabs')} tabs managed")
        
        # Test extract_metadata
        print("\n" + "-"*60)
        print("TESTING: extract_metadata()")
        print("-"*60)
        
        metadata_result = await browser.extract_metadata()
        print("METADATA RESULT:", json.dumps({
            'success': metadata_result.get('success'),
            'title': metadata_result.get('metadata', {}).get('title'),
            'charset': metadata_result.get('metadata', {}).get('charset'),
            'stats': metadata_result.get('metadata', {}).get('stats')
        }, indent=2))
        
        if metadata_result.get('success'):
            stats = metadata_result.get('metadata', {}).get('stats', {})
            print(f"SUCCESS: Metadata extracted - {stats.get('links', 0)} links, {stats.get('images', 0)} images")
        
        # Test handle_iframe_content
        print("\n" + "-"*60)
        print("TESTING: handle_iframe_content()")
        print("-"*60)
        
        # Navigate to a page that might have iframes
        await browser.page.goto("https://httpbin.org/")
        
        iframe_result = await browser.handle_iframe_content()
        print("IFRAME RESULT:", json.dumps({
            'success': iframe_result.get('success'),
            'total_iframes': iframe_result.get('total_iframes'),
            'iframes_analyzed': len(iframe_result.get('iframes', []))
        }, indent=2))
        
        if iframe_result.get('success'):
            print(f"SUCCESS: Iframe handling working, found {iframe_result.get('total_iframes')} iframes")
        
        # Test generate_page_pdf
        print("\n" + "-"*60)
        print("TESTING: generate_page_pdf()")
        print("-"*60)
        
        pdf_result = await browser.generate_page_pdf(
            output_path="test_page_nex058.pdf",
            options={'format': 'A4'}
        )
        print("PDF GENERATION RESULT:", json.dumps({
            'success': pdf_result.get('success'),
            'pdf_path': pdf_result.get('pdf_path'),
            'pdf_size_mb': pdf_result.get('pdf_size_mb'),
            'page_title': pdf_result.get('page_title')
        }, indent=2))
        
        if pdf_result.get('success'):
            print(f"SUCCESS: PDF generated - {pdf_result.get('pdf_size_mb')} MB")
        
        # Test automate_form_filling
        print("\n" + "-"*60)
        print("TESTING: automate_form_filling()")
        print("-"*60)
        
        # Navigate to a form page
        await browser.page.goto("https://httpbin.org/forms/post")
        
        form_data = {
            'custname': 'Test User',
            'custtel': '555-1234',
            'custemail': 'test@example.com',
            'size': 'medium',
            'topping': 'cheese',
            'comments': 'Automated test comment'
        }
        
        form_result = await browser.automate_form_filling(form_data, submit=False)
        print("FORM FILLING RESULT:", json.dumps({
            'success': form_result.get('success'),
            'forms_found': form_result.get('forms_found'),
            'fields_filled': len(form_result.get('fields_filled', [])),
            'fields_not_found': form_result.get('fields_not_found', [])
        }, indent=2))
        
        if form_result.get('success'):
            filled = len(form_result.get('fields_filled', []))
            not_found = len(form_result.get('fields_not_found', []))
            print(f"SUCCESS: Form automation working - {filled} fields filled, {not_found} not found")
        
        # Test analyze_page_security
        print("\n" + "-"*60)
        print("TESTING: analyze_page_security()")
        print("-"*60)
        
        # Navigate to a page for security analysis
        await browser.page.goto("https://httpbin.org/")
        
        security_result = await browser.analyze_page_security()
        print("SECURITY ANALYSIS RESULT:", json.dumps({
            'success': security_result.get('success'),
            'url': security_result.get('url'),
            'security_score': security_result.get('security_score'),
            'https': security_result.get('security_analysis', {}).get('https'),
            'recommendations': len(security_result.get('security_recommendations', []))
        }, indent=2))
        
        if security_result.get('success'):
            score = security_result.get('security_score', 0)
            recommendations = security_result.get('security_recommendations', [])
            print(f"SUCCESS: Security analysis complete - Score: {score}/100")
            if recommendations:
                print("Security recommendations:")
                for rec in recommendations[:3]:
                    print(f"  - {rec}")
        
        print("\n" + "="*70)
        print("NEX-058 MORE PRODUCTION BROWSER AUTOMATION FEATURES TESTED!")
        print("="*70)
        
    except Exception as e:
        print(f"ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        # Clean up PDF file if it exists
        try:
            pdf_file = Path("test_page_nex058.pdf")
            if pdf_file.exists():
                pdf_file.unlink()
                print("Cleaned up test PDF file")
        except:
            pass
            
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
        ('handle_multi_tab_operations', ()),
        ('extract_metadata', ()),
        ('handle_iframe_content', ()),
        ('generate_page_pdf', ()),
        ('automate_form_filling', ({'test': 'data'},)),
        ('analyze_page_security', ())
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
    print("NEX-058 More Production Browser Automation Features Test")
    print("Testing 6 advanced browser automation features")
    
    asyncio.run(test_nex_058_methods())