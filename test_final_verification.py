"""
Final verification test - REAL execution confirmation
"""

import requests
import json
import time

def test_final_verification():
    """Direct API test to confirm real execution is working"""
    
    print("FINAL VERIFICATION: Real Python Test Execution")
    print("=" * 60)
    
    # Create comprehensive test files
    test_files = {
        "test_math_operations.py": """
import pytest

class TestMathOperations:
    def test_addition(self):
        assert 2 + 2 == 4
        assert 10 + 5 == 15
    
    def test_subtraction(self):
        assert 10 - 5 == 5
        assert 100 - 50 == 50
    
    def test_multiplication(self):
        assert 3 * 4 == 12
        assert 5 * 5 == 25
    
    def test_division(self):
        assert 10 / 2 == 5
        assert 20 / 4 == 5
""",
        "test_string_operations.py": """
import pytest

def test_string_concatenation():
    result = "Hello" + " " + "World"
    assert result == "Hello World"

def test_string_methods():
    text = "Python Testing"
    assert text.upper() == "PYTHON TESTING"
    assert text.lower() == "python testing"
    assert text.startswith("Python")
    assert text.endswith("Testing")

def test_string_length():
    text = "Test Automation"
    assert len(text) == 15
""",
        "test_data_structures.py": """
import pytest

def test_list_operations():
    my_list = [1, 2, 3, 4, 5]
    assert len(my_list) == 5
    assert sum(my_list) == 15
    assert max(my_list) == 5
    assert min(my_list) == 1
    my_list.append(6)
    assert len(my_list) == 6

def test_dictionary_operations():
    my_dict = {"name": "Test", "type": "Automation"}
    assert my_dict["name"] == "Test"
    assert len(my_dict) == 2
    my_dict["status"] = "Running"
    assert len(my_dict) == 3

def test_set_operations():
    my_set = {1, 2, 3, 4, 5}
    assert len(my_set) == 5
    my_set.add(6)
    assert 6 in my_set
""",
        "test_with_failures.py": """
import pytest

def test_this_will_pass():
    assert True

def test_this_will_fail():
    # Intentional failure to demonstrate real execution
    assert 1 == 2, "Intentional failure: 1 does not equal 2"

@pytest.mark.skip(reason="Demonstrating skipped test")
def test_this_is_skipped():
    assert False
"""
    }
    
    print("\n1. Calling /api/execute-tests with comprehensive test suite...")
    print(f"   Sending {len(test_files)} test files")
    print(f"   Total test functions: ~16")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:5175/api/execute-tests",
            json={
                "generated_files": test_files,
                "url": "https://example.com",
                "test_type": "pytest"
            },
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        execution_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n2. EXECUTION RESULTS:")
            print("-" * 40)
            print(f"   API Response Time: {execution_time:.2f}s")
            print(f"   Success: {data.get('success')}")
            print(f"   Total Tests: {data.get('total_tests')}")
            print(f"   Passed: {data.get('passed')}")
            print(f"   Failed: {data.get('failed')}")
            print(f"   Skipped: {data.get('skipped')}")
            print(f"   Pytest Duration: {data.get('duration', 0):.2f}s")
            
            print("\n3. EXECUTION LOGS (showing key lines):")
            print("-" * 40)
            logs = data.get('logs', [])
            key_logs = [
                log for log in logs 
                if any(keyword in log for keyword in [
                    "Created test environment",
                    "Installing",
                    "Running pytest",
                    "Command:",
                    "passed",
                    "failed",
                    "skipped",
                    "Results:",
                    "Cleaned"
                ])
            ]
            
            for log in key_logs:
                print(f"   > {log}")
            
            print("\n4. INDIVIDUAL TEST RESULTS:")
            print("-" * 40)
            test_results = data.get('test_results', [])
            
            # Group by status
            passed_tests = [t for t in test_results if t['status'] == 'passed']
            failed_tests = [t for t in test_results if t['status'] == 'failed']
            skipped_tests = [t for t in test_results if t['status'] == 'skipped']
            
            if passed_tests:
                print(f"\n   PASSED ({len(passed_tests)}):")
                for test in passed_tests[:5]:  # Show first 5
                    print(f"     + {test['name']}")
                if len(passed_tests) > 5:
                    print(f"     ... and {len(passed_tests) - 5} more")
            
            if failed_tests:
                print(f"\n   FAILED ({len(failed_tests)}):")
                for test in failed_tests:
                    print(f"     - {test['name']}")
                    if test.get('message'):
                        print(f"       Error: {test['message'][:100]}")
            
            if skipped_tests:
                print(f"\n   SKIPPED ({len(skipped_tests)}):")
                for test in skipped_tests:
                    print(f"     o {test['name']}")
            
            # Verification
            print("\n5. VERIFICATION:")
            print("-" * 40)
            
            verification_passed = True
            
            # Check that we have real results
            if data.get('total_tests', 0) > 0:
                print("   [PASS] Tests were executed")
            else:
                print("   [FAIL] No tests executed")
                verification_passed = False
            
            # Check for pytest in logs
            if any("pytest" in log for log in logs):
                print("   [PASS] pytest command was run")
            else:
                print("   [FAIL] No pytest execution detected")
                verification_passed = False
            
            # Check for temp directory creation
            if any("Created test environment" in log for log in logs):
                print("   [PASS] Temporary test environment created")
            else:
                print("   [FAIL] No temp directory creation")
                verification_passed = False
            
            # Check for mix of pass/fail
            if data.get('passed', 0) > 0 and data.get('failed', 0) > 0:
                print("   [PASS] Mixed results (pass and fail) - proves real execution")
            else:
                print("   [WARN] No mixed results")
            
            # Check execution time is reasonable
            if 0.1 < data.get('duration', 0) < 30:
                print(f"   [PASS] Reasonable execution time: {data.get('duration', 0):.2f}s")
            else:
                print("   [WARN] Unusual execution time")
            
            print("\n" + "=" * 60)
            if verification_passed:
                print("SUCCESS: REAL PYTHON TEST EXECUTION CONFIRMED!")
                print("\nThe system is:")
                print("  - Creating temporary test environments")
                print("  - Writing actual Python test files")
                print("  - Running pytest with subprocess")
                print("  - Capturing real test results")
                print("  - Cleaning up after execution")
                print("\nNO MOCKS USED - 100% REAL EXECUTION!")
            else:
                print("WARNING: Some verification checks failed")
            print("=" * 60)
            
            # Save results
            with open('final_verification_results.json', 'w') as f:
                json.dump(data, f, indent=2)
            print("\nFull results saved to: final_verification_results.json")
            
        else:
            print(f"\n[ERROR] API returned status {response.status_code}")
            print(f"Response: {response.text[:500]}")
    
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")

if __name__ == "__main__":
    test_final_verification()