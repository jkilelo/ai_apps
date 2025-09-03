#!/usr/bin/env python3
"""
NEX-056 Test Script - Enterprise Browser Automation Features
Test the advanced enterprise automation features implemented in NEX-056
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

async def test_nex_056_methods():
    """Test the NEX-056 enterprise browser automation features"""
    print("\n" + "="*70)
    print("TESTING NEX-056 ENTERPRISE BROWSER AUTOMATION FEATURES")
    print("="*70)
    
    # Initialize browser
    browser = NexusBrowser()
    print("SUCCESS: Browser instance created")
    
    # Check method availability
    nex_056_methods = [
        'test_api_endpoints',
        'export_data_to_formats',
        'manage_browser_sessions',
        'schedule_recurring_tasks',
        'generate_automation_report',
        'validate_web_standards'
    ]
    
    print("\n1. CHECKING METHOD AVAILABILITY:")
    for method_name in nex_056_methods:
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
            await test_without_browser(browser, nex_056_methods)
            return
        
        print("SUCCESS: Browser initialized with Playwright")
        
        # Navigate to a test page
        await browser.page.goto("https://httpbin.org/")
        
        # Test test_api_endpoints
        print("\n" + "-"*60)
        print("TESTING: test_api_endpoints()")
        print("-"*60)
        
        # Define API endpoints to test
        endpoints = [
            {
                'name': 'Basic GET request',
                'method': 'GET',
                'url': 'https://httpbin.org/get',
                'expected_status': 200,
                'timeout': 10000
            },
            {
                'name': 'JSON response test',
                'method': 'GET',
                'url': 'https://httpbin.org/json',
                'expected_status': 200,
                'timeout': 5000
            },
            {
                'name': 'User agent test',
                'method': 'GET',
                'url': 'https://httpbin.org/user-agent',
                'expected_status': 200,
                'timeout': 5000
            }
        ]
        
        api_test_result = await browser.test_api_endpoints(endpoints)
        print("API TEST RESULT:", json.dumps(api_test_result, indent=2))
        
        if api_test_result.get('success'):
            passed = api_test_result.get('passed', 0)
            total = api_test_result.get('total', 0)
            print(f"SUCCESS: API endpoint testing completed {passed}/{total}")
        
        # Test export_data_to_formats
        print("\n" + "-"*60)
        print("TESTING: export_data_to_formats()")
        print("-"*60)
        
        # Test data to export
        test_data = [
            {'name': 'John Doe', 'age': 30, 'city': 'New York'},
            {'name': 'Jane Smith', 'age': 25, 'city': 'Los Angeles'},
            {'name': 'Mike Johnson', 'age': 35, 'city': 'Chicago'}
        ]
        
        # Test JSON export
        json_export = await browser.export_data_to_formats(test_data, 'json', 'test_export_json')
        print("JSON EXPORT RESULT:", json.dumps(json_export, indent=2))
        
        # Test CSV export
        csv_export = await browser.export_data_to_formats(test_data, 'csv', 'test_export_csv')
        print("CSV EXPORT RESULT:", json.dumps(csv_export, indent=2))
        
        # Test XML export
        xml_export = await browser.export_data_to_formats(test_data, 'xml', 'test_export_xml')
        print("XML EXPORT RESULT:", json.dumps(xml_export, indent=2))
        
        if json_export.get('success') and csv_export.get('success') and xml_export.get('success'):
            print("SUCCESS: Data export to multiple formats working")
        
        # Test manage_browser_sessions
        print("\n" + "-"*60)
        print("TESTING: manage_browser_sessions()")
        print("-"*60)
        
        # Save current session
        save_session = await browser.manage_browser_sessions('save', 'test_session_nex056')
        print("SAVE SESSION RESULT:", json.dumps(save_session, indent=2))
        
        # List sessions
        list_sessions = await browser.manage_browser_sessions('list')
        print("LIST SESSIONS RESULT:", json.dumps(list_sessions, indent=2))
        
        # Navigate to a different page
        await browser.page.goto("https://httpbin.org/html")
        
        # Restore session (this will try to restore to original page)
        restore_session = await browser.manage_browser_sessions('restore', 'test_session_nex056')
        print("RESTORE SESSION RESULT:", json.dumps(restore_session, indent=2))
        
        if save_session.get('success') and list_sessions.get('success'):
            print("SUCCESS: Browser session management working")
        
        # Test schedule_recurring_tasks
        print("\n" + "-"*60)
        print("TESTING: schedule_recurring_tasks()")
        print("-"*60)
        
        # Define a simple recurring task
        task_config = {
            'name': 'Check page title',
            'action': 'navigate_and_check',
            'interval': 30,  # seconds
            'url': 'https://httpbin.org/',
            'check_element': 'title'
        }
        
        schedule_result = await browser.schedule_recurring_tasks('create', task_config)
        print("SCHEDULE TASK RESULT:", json.dumps(schedule_result, indent=2))
        
        # List scheduled tasks
        list_tasks = await browser.schedule_recurring_tasks('list')
        print("LIST TASKS RESULT:", json.dumps(list_tasks, indent=2))
        
        # Cancel the task we just created
        if schedule_result.get('success') and schedule_result.get('task_id'):
            cancel_result = await browser.schedule_recurring_tasks('cancel', {'task_id': schedule_result['task_id']})
            print("CANCEL TASK RESULT:", json.dumps(cancel_result, indent=2))
        
        if schedule_result.get('success'):
            print("SUCCESS: Task scheduling working")
        
        # Test generate_automation_report
        print("\n" + "-"*60)
        print("TESTING: generate_automation_report()")
        print("-"*60)
        
        # Collect test results for report
        test_results = [
            api_test_result,
            json_export,
            save_session,
            schedule_result
        ]
        
        report_result = await browser.generate_automation_report(
            test_results, 
            "nex_056_enterprise_report",
            include_performance=True,
            include_screenshots=True
        )
        print("AUTOMATION REPORT RESULT:", json.dumps(report_result, indent=2))
        
        if report_result.get('success'):
            report_file = report_result.get('report_file', 'Unknown')
            overall_score = report_result.get('overall_score', 0)
            print(f"SUCCESS: Automation report generated: {report_file} (Score: {overall_score}%)")
        
        # Test validate_web_standards
        print("\n" + "-"*60)
        print("TESTING: validate_web_standards()")
        print("-"*60)
        
        # Navigate to a page for validation
        await browser.page.goto("https://httpbin.org/html")
        
        standards_result = await browser.validate_web_standards(
            check_html5=True,
            check_accessibility=True,
            check_performance=True
        )
        print("WEB STANDARDS RESULT:", json.dumps(standards_result, indent=2))
        
        if standards_result.get('success'):
            overall_compliance = standards_result.get('overall_compliance_score', 0)
            print(f"SUCCESS: Web standards validation completed (Compliance: {overall_compliance}%)")
        
        print("\n" + "="*70)
        print("NEX-056 ENTERPRISE BROWSER AUTOMATION FEATURES TESTED!")
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
        ('test_api_endpoints', ([],)),
        ('export_data_to_formats', ([], 'json', 'test')),
        ('manage_browser_sessions', ('list',)),
        ('schedule_recurring_tasks', ('list',)),
        ('generate_automation_report', ([],)),
        ('validate_web_standards', ())
    ]
    
    for method_name, args in test_calls:
        if hasattr(browser, method_name):
            method = getattr(browser, method_name)
            result = await method(*args)
            
            if 'error' in result and ('No active page available' in result['error'] or 'No browser instance available' in result['error'] or result.get('success') == True):
                print(f"SUCCESS: {method_name}() handles no-browser condition correctly")
            else:
                print(f"WARNING: {method_name}() unexpected response: {result}")
        else:
            print(f"SKIP: {method_name}() not available")

if __name__ == "__main__":
    print("NEX-056 Enterprise Browser Automation Features Test")
    print("Testing 6 new enterprise-grade automation features")
    
    asyncio.run(test_nex_056_methods())