#!/usr/bin/env python3
"""
Debug script to test form submission and see validation errors
"""

import requests
import json
import re
from datetime import date, timedelta

# Start a new session
base_url = "http://localhost:8117"  # Update with your actual port

# Test basic info submission
def test_basic_info_submission():
    # First, start a new onboarding session
    response = requests.get(f"{base_url}/onboarding/start")
    if response.status_code != 200:
        print(f"Failed to start onboarding: {response.status_code}")
        return
    
    # Extract session ID from the form
    import re
    html = response.text
    match = re.search(r'action="/api/onboarding/([^/]+)/process/', html)
    if not match:
        print("Could not find session ID in form")
        return
    
    session_id = match.group(1)
    print(f"Session ID: {session_id}")
    
    # Test data - all fields that should be valid
    test_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+15551234567",  # Valid US phone format
        "date_of_birth": "1990-01-15",  # Valid date, person is 34 years old
        "csrf_token": "test_token",  # This might be the issue
        "chain_state": ""
    }
    
    print("\nSubmitting test data:")
    for key, value in test_data.items():
        if key != "csrf_token" and key != "chain_state":
            print(f"  {key}: {value}")
    
    # Submit the form
    response = requests.post(
        f"{base_url}/api/onboarding/{session_id}/process/basic_info",
        data=test_data
    )
    
    print(f"\nResponse status: {response.status_code}")
    
    if response.status_code == 400:
        print("\nValidation errors:")
        result = response.json()
        if "errors" in result:
            for error in result["errors"]:
                print(f"  - Field: {error.get('field', 'unknown')}")
                print(f"    Message: {error.get('message', 'unknown')}")
                print(f"    Type: {error.get('type', 'unknown')}")
        else:
            print(f"  {result}")
    elif response.status_code == 200:
        print("\nSuccess! Moving to next step...")
        result = response.json()
        print(f"Next step: {result.get('next_step_id')}")
        if "chain_state" in result:
            print(f"Employee ID: {result['chain_state']['step_basic_info_response']['employee_id']}")
    else:
        print(f"\nUnexpected response: {response.text[:500]}")

def check_csrf_requirement():
    """Check if CSRF token is actually validated"""
    print("\n" + "="*50)
    print("Checking CSRF token requirement...")
    
    # Get the form to see the actual CSRF token
    response = requests.get(f"{base_url}/onboarding/start")
    if response.status_code == 200:
        html = response.text
        # Extract CSRF token
        match = re.search(r'name="csrf_token" value="([^"]+)"', html)
        if match:
            csrf_token = match.group(1)
            print(f"Found CSRF token: {csrf_token[:20]}...")
            return csrf_token
        else:
            print("No CSRF token found in form")
    return None

if __name__ == "__main__":
    import sys
    
    # Allow port to be passed as argument
    if len(sys.argv) > 1:
        port = sys.argv[1]
        base_url = f"http://localhost:{port}"
    
    print(f"Testing form submission on {base_url}")
    print("="*50)
    
    # First check CSRF
    csrf_token = check_csrf_requirement()
    
    # Then test submission
    test_basic_info_submission()
    
    # Test with actual CSRF token if found
    if csrf_token:
        print("\n" + "="*50)
        print("Testing with actual CSRF token...")
        
        response = requests.get(f"{base_url}/onboarding/start")
        html = response.text
        match = re.search(r'action="/api/onboarding/([^/]+)/process/', html)
        session_id = match.group(1)
        
        test_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "phone": "+15559876543",
            "date_of_birth": "1985-05-20",
            "csrf_token": csrf_token,  # Use actual CSRF token
            "chain_state": ""
        }
        
        response = requests.post(
            f"{base_url}/api/onboarding/{session_id}/process/basic_info",
            data=test_data
        )
        
        print(f"Response with real CSRF: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.json()}")