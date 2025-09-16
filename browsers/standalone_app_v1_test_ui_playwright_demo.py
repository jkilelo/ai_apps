"""
Demo: Test Real Playwright Execution with UI Web Testing API
"""

import requests
import time
import json

API_BASE_URL = "http://localhost:8002/api/v1"

def test_playwright_execution():
    print("=" * 60)
    print("UI Web Testing API - Real Playwright Test Execution Demo")
    print("=" * 60)
    
    # Create a test case that navigates to a form and fills it
    test_cases = [
        {
            "id": "test_form_submission",
            "name": "Test form submission on httpbin.org",
            "type": "functional",
            "element": {
                "type": "form",
                "page_url": "https://httpbin.org/forms/post",
                "selector": "form"
            },
            "steps": [
                {
                    "type": "action",
                    "action": "navigate",
                    "target": "https://httpbin.org/forms/post",
                    "value": ""
                },
                {
                    "type": "action",
                    "action": "screenshot",
                    "target": "",
                    "value": "form_initial.png"
                },
                {
                    "type": "action",
                    "action": "fill",
                    "target": "input[name='custname']",
                    "value": "Test User"
                },
                {
                    "type": "action",
                    "action": "fill",
                    "target": "input[name='custtel']",
                    "value": "555-1234"
                },
                {
                    "type": "action",
                    "action": "fill",
                    "target": "input[name='custemail']",
                    "value": "test@example.com"
                },
                {
                    "type": "action",
                    "action": "select",
                    "target": "select[name='size']",
                    "value": "medium"
                },
                {
                    "type": "action",
                    "action": "check",
                    "target": "input[value='bacon']",
                    "value": ""
                },
                {
                    "type": "action",
                    "action": "fill",
                    "target": "textarea[name='comments']",
                    "value": "This is a test comment from Playwright automation"
                },
                {
                    "type": "action",
                    "action": "screenshot",
                    "target": "",
                    "value": "form_filled.png"
                },
                {
                    "type": "action",
                    "action": "click",
                    "target": "button[type='submit']",
                    "value": ""
                },
                {
                    "type": "action",
                    "action": "wait",
                    "target": "",
                    "value": "2000"
                },
                {
                    "type": "action",
                    "action": "screenshot",
                    "target": "",
                    "value": "form_result.png"
                }
            ]
        }
    ]
    
    # Execute the test
    print("\n=== Executing Playwright Test ===")
    exec_payload = {
        "test_cases": test_cases,
        "execution_mode": "sequential",
        "browser": "chromium",
        "timeout": 30
    }
    
    response = requests.post(f"{API_BASE_URL}/test-execution/execute", json=exec_payload)
    result = response.json()
    job_id = result["job_id"]
    print(f"Test execution started: {job_id}")
    
    # Poll for completion
    max_attempts = 30
    for i in range(max_attempts):
        response = requests.get(f"{API_BASE_URL}/test-execution/execute/{job_id}")
        status_data = response.json()
        status = status_data["status"]
        
        print(f"Status: {status}", end="")
        
        if status == "completed":
            print("\n✓ Test execution completed!")
            
            # Show summary
            summary = status_data["summary"]
            print(f"\nExecution Summary:")
            print(f"  - Total tests: {summary['total']}")
            print(f"  - Passed: {summary['passed']}")
            print(f"  - Failed: {summary['failed']}")
            print(f"  - Duration: {summary['duration']:.2f}s")
            
            # Show detailed test steps
            test_result = status_data["test_results"][0]
            print(f"\nTest: {test_result['test_name']}")
            print(f"Status: {test_result['status']}")
            print(f"Duration: {test_result['duration']:.2f}s")
            
            print("\nTest Steps:")
            for log in test_result["logs"]:
                status_icon = "✓" if log["status"] == "passed" else "✗"
                print(f"  {status_icon} Step {log['step_index']}: {log['message']}")
                if log.get("screenshot"):
                    print(f"    Screenshot: {log['screenshot']}")
            
            print(f"\nScreenshots created:")
            for screenshot in test_result.get("screenshots", []):
                print(f"  - {screenshot}")
            
            break
        elif status == "failed":
            print(f"\n✗ Test execution failed: {status_data.get('error', 'Unknown error')}")
            break
        else:
            print(" (waiting...)", end="\r")
            time.sleep(1)
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_playwright_execution()