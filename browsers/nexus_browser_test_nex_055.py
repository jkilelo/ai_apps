#!/usr/bin/env python3
"""
NEX-055 Test Script - Advanced Testing & API Integration Features
Test the advanced testing and API integration features implemented in NEX-055
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

async def test_nex_055_methods():
    """Test the NEX-055 advanced testing and API integration features"""
    print("\n" + "="*70)
    print("TESTING NEX-055 ADVANCED TESTING & API INTEGRATION FEATURES")
    print("="*70)
    
    # Initialize browser
    browser = NexusBrowser()
    print("SUCCESS: Browser instance created")
    
    # Check method availability
    nex_055_methods = [
        'wait_for_condition',
        'intercept_network_requests',
        'simulate_user_interactions',
        'test_form_validation',
        'compare_page_states',
        'generate_test_report'
    ]
    
    print("\n1. CHECKING METHOD AVAILABILITY:")
    for method_name in nex_055_methods:
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
            await test_without_browser(browser, nex_055_methods)
            return
        
        print("SUCCESS: Browser initialized with Playwright")
        
        # Navigate to a test page
        await browser.page.goto("https://httpbin.org/forms/post")
        
        # Test wait_for_condition
        print("\n" + "-"*60)
        print("TESTING: wait_for_condition()")
        print("-"*60)
        
        # Define a simple condition function
        async def page_loaded_condition(page):
            return await page.evaluate("document.readyState === 'complete'")
        
        condition_result = await browser.wait_for_condition(page_loaded_condition, timeout=5000)
        print("CONDITION RESULT:", json.dumps(condition_result, indent=2))
        
        if condition_result.get('success'):
            print("SUCCESS: Wait for condition working")
        
        # Test intercept_network_requests
        print("\n" + "-"*60)
        print("TESTING: intercept_network_requests()")
        print("-"*60)
        
        # Enable interception
        intercept_enable = await browser.intercept_network_requests(True, ["*.css", "*.js"])
        print("INTERCEPTION ENABLE:", json.dumps(intercept_enable, indent=2))
        
        # Navigate to trigger requests
        await browser.page.goto("https://httpbin.org/")
        await browser.page.wait_for_timeout(2000)
        
        # Disable interception
        intercept_disable = await browser.intercept_network_requests(False)
        print("INTERCEPTION DISABLE:", json.dumps(intercept_disable, indent=2))
        
        if intercept_enable.get('success') and intercept_disable.get('success'):
            print("SUCCESS: Network request interception working")
        
        # Test simulate_user_interactions
        print("\n" + "-"*60)
        print("TESTING: simulate_user_interactions()")
        print("-"*60)
        
        # Navigate to form page
        await browser.page.goto("https://httpbin.org/forms/post")
        
        # Define user interactions
        interactions = [
            {
                'type': 'type',
                'target': 'input[name="custname"]',
                'options': {'text': 'Test User', 'delay': 500}
            },
            {
                'type': 'type',
                'target': 'input[name="custtel"]',
                'options': {'text': '555-1234', 'delay': 600}
            },
            {
                'type': 'scroll',
                'target': 'body',
                'options': {'y': 200, 'delay': 300}
            },
            {
                'type': 'wait',
                'target': None,
                'options': {'time': 1000}
            }
        ]
        
        interaction_result = await browser.simulate_user_interactions(interactions)
        print("INTERACTION RESULT:", json.dumps(interaction_result, indent=2))
        
        if interaction_result.get('success'):
            completed = interaction_result.get('completed_actions', 0)
            total = interaction_result.get('total_actions', 0)
            print(f"SUCCESS: User interactions completed {completed}/{total}")
        
        # Test test_form_validation
        print("\n" + "-"*60)
        print("TESTING: test_form_validation()")
        print("-"*60)
        
        # Define test cases for form validation
        test_cases = [
            {
                'name': 'Valid form submission',
                'inputs': {
                    'input[name="custname"]': 'John Doe',
                    'input[name="custtel"]': '555-0123',
                    'input[name="custemail"]': 'john@example.com',
                    'textarea[name="comments"]': 'Test comment'
                },
                'expected': {}  # No validation errors expected
            },
            {
                'name': 'Empty required fields',
                'inputs': {
                    'input[name="custname"]': '',
                    'input[name="custtel"]': '',
                    'input[name="custemail"]': '',
                    'textarea[name="comments"]': ''
                },
                'expected': {
                    'custname': 'This field is required',
                    'custemail': 'This field is required'
                }
            }
        ]
        
        form_validation_result = await browser.test_form_validation('form', test_cases)
        print("FORM VALIDATION RESULT:", json.dumps(form_validation_result, indent=2))
        
        if form_validation_result.get('success'):
            print("SUCCESS: Form validation testing completed")
        
        # Test compare_page_states
        print("\n" + "-"*60)
        print("TESTING: compare_page_states()")
        print("-"*60)
        
        # Define actions for different states
        state1_actions = [
            {'type': 'type', 'target': 'input[name="custname"]', 'options': {'text': 'State 1 User'}}
        ]
        
        state2_actions = [
            {'type': 'type', 'target': 'input[name="custname"]', 'options': {'text': 'State 2 User'}},
            {'type': 'scroll', 'target': 'body', 'options': {'y': 100}}
        ]
        
        comparison_result = await browser.compare_page_states(state1_actions, state2_actions)
        print("COMPARISON RESULT:", json.dumps(comparison_result, indent=2))
        
        if comparison_result.get('success'):
            print("SUCCESS: Page state comparison completed")
        
        # Test generate_test_report
        print("\n" + "-"*60)
        print("TESTING: generate_test_report()")
        print("-"*60)
        
        # Collect all test results
        test_results = [
            condition_result,
            intercept_enable,
            interaction_result,
            form_validation_result,
            comparison_result
        ]
        
        report_result = await browser.generate_test_report(test_results, "nex_055_test_report")
        print("REPORT RESULT:", json.dumps(report_result, indent=2))
        
        if report_result.get('success'):
            report_file = report_result.get('report_file', 'Unknown')
            success_rate = report_result.get('summary', {}).get('success_rate', 0)
            print(f"SUCCESS: Test report generated: {report_file} (Success rate: {success_rate}%)")
        
        print("\n" + "="*70)
        print("NEX-055 ADVANCED TESTING & API INTEGRATION FEATURES TESTED!")
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
        ('wait_for_condition', (lambda x: True,)),
        ('intercept_network_requests', ()),
        ('simulate_user_interactions', ([],)),
        ('test_form_validation', ('form', [])),
        ('compare_page_states', ([], [])),
        ('generate_test_report', ([],))
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
    print("NEX-055 Advanced Testing & API Integration Features Test")
    print("Testing 6 new production-ready testing automation features")
    
    asyncio.run(test_nex_055_methods())