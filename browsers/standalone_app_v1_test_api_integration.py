"""
Test API Integration
"""

import requests
import json
import time

API_BASE = "http://localhost:8002/api/v1"

def test_integration():
    print("Testing API Integration...")
    
    # Step 1: Element Extraction
    print("\n1. Element Extraction")
    response = requests.post(f"{API_BASE}/element-extraction/extract", json={
        "web_page_url": "https://example.com",
        "profile": "qa_manual_tester",
        "max_depth": 1
    })
    print(f"Response status: {response.status_code}")
    data = response.json()
    job_id = data["job_id"]
    
    # Wait for completion
    while True:
        status = requests.get(f"{API_BASE}/element-extraction/extract/{job_id}")
        result = status.json()
        if result["status"] in ["completed", "failed"]:
            break
        time.sleep(1)
    
    print(f"Extraction status: {result['status']}")
    print(f"Elements found: {len(result.get('extracted_elements', []))}")
    
    # Step 2: Test Generation  
    print("\n2. Test Generation")
    extracted_elements = result.get('extracted_elements', [])
    
    # This is the exact request format
    gen_request = {
        "extracted_elements": extracted_elements,
        "test_type": "functional",
        "framework": "playwright_pytest",
        "include_negative_tests": False
    }
    
    print("Sending request:")
    print(json.dumps(gen_request, indent=2))
    
    response = requests.post(f"{API_BASE}/test-generation/generate", json=gen_request)
    print(f"Response status: {response.status_code}")
    
    if response.status_code != 200:
        print("Error response:")
        print(response.text)
        return
        
    data = response.json()
    gen_job_id = data["job_id"]
    
    # Wait for completion
    while True:
        status = requests.get(f"{API_BASE}/test-generation/generate/{gen_job_id}")
        gen_result = status.json()
        if gen_result["status"] in ["completed", "failed"]:
            break
        time.sleep(1)
    
    print(f"Generation status: {gen_result['status']}")
    print(f"Test cases generated: {len(gen_result.get('test_cases', []))}")
    
    # Step 3: Test Execution
    print("\n3. Test Execution")
    test_cases = gen_result.get('test_cases', [])
    
    exec_request = {
        "test_cases": test_cases,
        "execution_mode": "sequential",
        "browser": "chromium",
        "timeout": 300
    }
    
    response = requests.post(f"{API_BASE}/test-execution/execute", json=exec_request)
    print(f"Response status: {response.status_code}")
    
    if response.status_code != 200:
        print("Error response:")
        print(response.text)
        return
        
    data = response.json()
    exec_job_id = data["job_id"]
    
    # Wait for completion
    while True:
        status = requests.get(f"{API_BASE}/test-execution/execute/{exec_job_id}")
        exec_result = status.json()
        if exec_result["status"] in ["completed", "failed"]:
            break
        time.sleep(1)
    
    print(f"Execution status: {exec_result['status']}")
    summary = exec_result.get('summary', {})
    print(f"Tests: {summary.get('total', 0)} total, {summary.get('passed', 0)} passed, {summary.get('failed', 0)} failed")
    
    print("\n✅ Integration test complete!")

if __name__ == "__main__":
    test_integration()