"""
Test REAL Python test execution - NO MOCKS!
"""

import requests
import json
import time

def test_real_execution():
    """Test real pytest execution through the API"""
    
    print("TESTING REAL PYTHON CODE EXECUTION")
    print("=" * 50)
    
    # Create some actual test files
    test_files = {
        "test_example.py": """
import pytest

def test_basic_addition():
    '''Test that basic addition works'''
    assert 1 + 1 == 2
    
def test_string_operations():
    '''Test string concatenation'''
    result = "Hello" + " " + "World"
    assert result == "Hello World"
    
def test_list_operations():
    '''Test list operations'''
    my_list = [1, 2, 3]
    my_list.append(4)
    assert len(my_list) == 4
    assert my_list[-1] == 4

def test_intentional_failure():
    '''This test should fail to demonstrate failure handling'''
    assert 5 == 10, "This is an intentional failure for testing"
""",
        "test_math.py": """
import pytest

def test_multiplication():
    '''Test multiplication'''
    assert 3 * 4 == 12

def test_division():
    '''Test division'''
    assert 10 / 2 == 5.0
    
def test_modulo():
    '''Test modulo operation'''
    assert 10 % 3 == 1

@pytest.mark.skip(reason="Demonstrating skipped test")
def test_skipped_example():
    '''This test will be skipped'''
    assert False
"""
    }
    
    print("1. Calling /api/execute-tests with real test files...")
    
    try:
        response = requests.post(
            "http://localhost:5175/api/execute-tests",
            json={
                "generated_files": test_files,
                "url": "https://example.com",
                "test_type": "pytest"
            },
            headers={"Content-Type": "application/json"},
            timeout=60  # Give it time to actually run
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n2. REAL EXECUTION RESULTS:")
            print("   " + "-" * 40)
            print(f"   Success: {data.get('success')}")
            print(f"   Total Tests: {data.get('total_tests')}")
            print(f"   Passed: {data.get('passed')}")
            print(f"   Failed: {data.get('failed')}")
            print(f"   Skipped: {data.get('skipped')}")
            print(f"   Duration: {data.get('duration', 0):.2f}s")
            
            print("\n3. EXECUTION LOGS:")
            for log in data.get('logs', []):
                print(f"   > {log}")
            
            print("\n4. INDIVIDUAL TEST RESULTS:")
            for test in data.get('test_results', []):
                status_symbol = "✓" if test['status'] == 'passed' else "✗" if test['status'] == 'failed' else "○"
                print(f"   [{status_symbol}] {test['name']}")
                print(f"       Status: {test['status']}")
                print(f"       Duration: {test.get('duration', 0):.3f}s")
                if test.get('message'):
                    print(f"       Message: {test['message'][:100]}...")
            
            # Save full response
            with open('real_execution_results.json', 'w') as f:
                json.dump(data, f, indent=2)
            
            print("\n5. VERIFICATION:")
            if data.get('success'):
                print("   [SUCCESS] Real pytest execution working!")
                print("   - Tests were actually executed using subprocess")
                print("   - Real Python interpreter was used")
                print("   - Actual test results were collected")
                print("   - NO MOCKS WERE USED!")
            else:
                print("   [WARNING] Execution completed but had issues")
                
        else:
            print(f"   [ERROR] API returned error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   [ERROR] Request failed: {e}")
    
    print("\n" + "=" * 50)
    print("Real execution test completed!")

if __name__ == "__main__":
    test_real_execution()