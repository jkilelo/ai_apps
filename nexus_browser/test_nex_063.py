#!/usr/bin/env python3
"""
NEX-063 Test Script - Advanced Automation and Integration Features
Test automated test generation, CI/CD integration, blueprints, data export, webhooks, and dashboard
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

async def test_nex_063_methods():
    """Test the NEX-063 advanced automation and integration features"""
    print("\n" + "="*70)
    print("TESTING NEX-063 ADVANCED AUTOMATION AND INTEGRATION FEATURES")
    print("="*70)
    
    # Initialize browser
    browser = NexusBrowser()
    print("SUCCESS: Browser instance created")
    
    # Check method availability
    nex_063_methods = [
        'generate_automated_tests',
        'integrate_with_ci_cd',
        'create_page_blueprint',
        'generate_data_export_report',
        'setup_webhook_notifications',
        'create_automation_dashboard'
    ]
    
    print("\n1. CHECKING METHOD AVAILABILITY:")
    for method_name in nex_063_methods:
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
            await test_without_browser(browser, nex_063_methods)
            return
        
        print("SUCCESS: Browser initialized with Playwright")
        
        # Navigate to a test page
        await browser.page.goto("https://httpbin.org/forms/post")
        
        # Test generate_automated_tests
        print("\n" + "-"*60)
        print("TESTING: generate_automated_tests()")
        print("-"*60)
        
        # Test UI test generation
        ui_test_result = await browser.generate_automated_tests(
            test_type='ui',
            selector_strategy='smart'
        )
        print("UI TEST GENERATION RESULT:", json.dumps({
            'success': ui_test_result.get('success'),
            'test_type': ui_test_result.get('test_type'),
            'page_analysis': ui_test_result.get('page_analysis'),
            'test_framework': ui_test_result.get('test_framework')
        }, indent=2))
        
        # Test accessibility test generation
        a11y_test_result = await browser.generate_automated_tests(test_type='accessibility')
        print("ACCESSIBILITY TEST GENERATION:", json.dumps({
            'success': a11y_test_result.get('success'),
            'test_type': a11y_test_result.get('test_type'),
            'total_tests': a11y_test_result.get('generated_tests', {}).get('total_tests', 0)
        }, indent=2))
        
        if ui_test_result.get('success'):
            analysis = ui_test_result.get('page_analysis', {})
            tests = ui_test_result.get('generated_tests', {})
            print(f"SUCCESS: Generated {tests.get('total_tests')} tests for {analysis.get('forms_found')} forms, {analysis.get('buttons_found')} buttons")
        
        # Test integrate_with_ci_cd
        print("\n" + "-"*60)
        print("TESTING: integrate_with_ci_cd()")
        print("-"*60)
        
        # Test different CI/CD platforms
        for platform in ['github', 'gitlab', 'jenkins']:
            ci_cd_result = await browser.integrate_with_ci_cd(
                platform=platform,
                test_command='pytest --headless'
            )
            print(f"{platform.upper()} CI/CD INTEGRATION:", json.dumps({
                'success': ci_cd_result.get('success'),
                'platform': ci_cd_result.get('platform'),
                'estimated_setup_time': ci_cd_result.get('estimated_setup_time')
            }, indent=2))
            
            if ci_cd_result.get('success'):
                configs = ci_cd_result.get('ci_cd_configs', {})
                test_config = ci_cd_result.get('test_configuration', {})
                print(f"  Generated {len(configs)} config files, {len(test_config)} test files")
        
        # Test create_page_blueprint
        print("\n" + "-"*60)
        print("TESTING: create_page_blueprint()")
        print("-"*60)
        
        blueprint_result = await browser.create_page_blueprint()
        print("PAGE BLUEPRINT RESULT:", json.dumps({
            'success': blueprint_result.get('success'),
            'analysis': blueprint_result.get('analysis'),
            'recommendations_count': len(blueprint_result.get('recommendations', []))
        }, indent=2))
        
        if blueprint_result.get('success'):
            analysis = blueprint_result.get('analysis', {})
            print(f"SUCCESS: Blueprint created - Complexity: {analysis.get('complexity_score')}")
            print(f"  Assets: {analysis.get('asset_summary', {}).get('total_assets')} total")
            print(f"  SEO Score: {analysis.get('seo_score')}/100")
            print(f"  A11y Score: {analysis.get('accessibility_score'):.1f}/100")
        
        # Test generate_data_export_report
        print("\n" + "-"*60)
        print("TESTING: generate_data_export_report()")
        print("-"*60)
        
        # Test different export formats
        for format_type in ['json', 'csv', 'html']:
            export_result = await browser.generate_data_export_report(
                format_type=format_type,
                include_screenshots=False
            )
            print(f"{format_type.upper()} EXPORT RESULT:", json.dumps({
                'success': export_result.get('success'),
                'export_format': export_result.get('export_format'),
                'data_summary': export_result.get('data_summary'),
                'full_data_size': export_result.get('full_data_size')
            }, indent=2))
            
            if export_result.get('success'):
                summary = export_result.get('data_summary', {})
                print(f"  Exported: {summary.get('word_count')} words, {summary.get('image_count')} images, {summary.get('link_count')} links")
        
        # Test setup_webhook_notifications
        print("\n" + "-"*60)
        print("TESTING: setup_webhook_notifications()")
        print("-"*60)
        
        webhook_result = await browser.setup_webhook_notifications(
            webhook_url='https://webhook.example.com/nexus',
            events=['page_load', 'form_submit', 'error'],
            test_mode=True
        )
        print("WEBHOOK SETUP RESULT:", json.dumps({
            'success': webhook_result.get('success'),
            'webhook_config': webhook_result.get('webhook_config'),
            'test_results': webhook_result.get('test_results')
        }, indent=2))
        
        if webhook_result.get('success'):
            config = webhook_result.get('webhook_config', {})
            handlers = webhook_result.get('event_handlers', {})
            print(f"SUCCESS: Webhook configured for {len(config.get('events', []))} events")
            print(f"  Handlers: {', '.join(handlers.keys())}")
        
        # Test create_automation_dashboard
        print("\n" + "-"*60)
        print("TESTING: create_automation_dashboard()")
        print("-"*60)
        
        dashboard_result = await browser.create_automation_dashboard()
        print("DASHBOARD CREATION RESULT:", json.dumps({
            'success': dashboard_result.get('success'),
            'features': dashboard_result.get('features'),
            'file_size_kb': dashboard_result.get('file_size_kb')
        }, indent=2))
        
        if dashboard_result.get('success'):
            features = dashboard_result.get('features', [])
            size_kb = dashboard_result.get('file_size_kb', 0)
            customization = dashboard_result.get('customization_options', {})
            print(f"SUCCESS: Dashboard created with {len(features)} features ({size_kb:.1f}KB)")
            print(f"  Themes: {', '.join(customization.get('themes', [])[:3])}")
            print(f"  Widgets: {', '.join(customization.get('widgets', [])[:3])}")
        
        print("\n" + "="*70)
        print("NEX-063 ADVANCED AUTOMATION AND INTEGRATION FEATURES TESTED!")
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
        ('generate_automated_tests', ()),
        ('integrate_with_ci_cd', ()),
        ('create_page_blueprint', ()),
        ('generate_data_export_report', ()),
        ('setup_webhook_notifications', ('https://example.com/webhook',)),
        ('create_automation_dashboard', ())
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
    print("NEX-063 Advanced Automation and Integration Features Test")
    print("Testing 6 features: test generation, CI/CD, blueprints, export, webhooks, dashboard")
    
    asyncio.run(test_nex_063_methods())