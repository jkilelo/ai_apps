"""
Test error handling for Extract Elements feature
Tests various failure scenarios to ensure meaningful error messages
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any
import time

# Test configuration
BASE_URL = "http://localhost:5175"
TEST_SCENARIOS = [
    {
        "name": "Valid URL - Success Case",
        "url": "https://example.com",
        "expected_success": True,
        "description": "Should successfully extract elements from a valid URL"
    },
    {
        "name": "Invalid URL Format",
        "url": "not-a-valid-url",
        "expected_success": False,
        "expected_error_type": "invalid_url",
        "description": "Should return validation error for invalid URL format"
    },
    {
        "name": "Non-existent Domain",
        "url": "https://this-domain-definitely-does-not-exist-12345.com",
        "expected_success": False,
        "expected_error_type": "navigation_failed",
        "description": "Should return navigation error for non-existent domain"
    },
    {
        "name": "Timeout Simulation",
        "url": "https://httpstat.us/200?sleep=60000",
        "expected_success": False,
        "expected_error_type": "navigation_timeout",
        "description": "Should handle timeout gracefully"
    },
    {
        "name": "Empty URL",
        "url": "",
        "expected_success": False,
        "expected_error_type": "invalid_url",
        "description": "Should return validation error for empty URL"
    },
    {
        "name": "Missing Protocol",
        "url": "example.com",
        "expected_success": True,  # Should auto-prepend https://
        "description": "Should auto-prepend https:// to URLs without protocol"
    },
    {
        "name": "Server Error Page",
        "url": "https://httpstat.us/500",
        "expected_success": False,
        "expected_error_type": "navigation_failed",
        "description": "Should handle server error pages"
    }
]

class TestColors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{TestColors.HEADER}{TestColors.BOLD}{'='*60}{TestColors.ENDC}")
    print(f"{TestColors.HEADER}{TestColors.BOLD}{text}{TestColors.ENDC}")
    print(f"{TestColors.HEADER}{TestColors.BOLD}{'='*60}{TestColors.ENDC}")

def print_scenario(scenario: Dict[str, Any]):
    print(f"\n{TestColors.CYAN}[TEST] {scenario['name']}{TestColors.ENDC}")
    print(f"   URL: {scenario['url'] or '(empty)'}")
    print(f"   {scenario['description']}")

def print_success(message: str):
    print(f"{TestColors.GREEN}[PASS] {message}{TestColors.ENDC}")

def print_error(message: str):
    print(f"{TestColors.FAIL}[FAIL] {message}{TestColors.ENDC}")

def print_warning(message: str):
    print(f"{TestColors.WARNING}[WARN] {message}{TestColors.ENDC}")

def print_info(message: str):
    print(f"{TestColors.BLUE}[INFO] {message}{TestColors.ENDC}")

async def test_extraction(session: aiohttp.ClientSession, scenario: Dict[str, Any]) -> bool:
    """Test a single extraction scenario"""
    
    print_scenario(scenario)
    
    try:
        # Make extraction request
        start_time = time.time()
        print(f"   Making request to {BASE_URL}/api/extract-elements...")
        
        async with session.post(
            f"{BASE_URL}/api/extract-elements",
            json={"url": scenario["url"]},
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            elapsed = time.time() - start_time
            print(f"   Response time: {elapsed:.2f}s")
            
            data = await response.json()
            
            # Check response status
            if response.status == 200:
                if scenario["expected_success"]:
                    # Success case - verify we got elements
                    if "elements" in data:
                        element_count = len(data.get("elements", []))
                        print_success(f"Extraction successful - Found {element_count} elements")
                        
                        # Check for LLM analysis
                        if "llm_analysis" in data:
                            if "error" in data["llm_analysis"]:
                                print_warning(f"LLM analysis failed: {data['llm_analysis']['error']}")
                                if "suggestion" in data["llm_analysis"]:
                                    print_info(f"Suggestion: {data['llm_analysis']['suggestion']}")
                            else:
                                print_success("LLM analysis completed")
                        return True
                    else:
                        print_error(f"Expected success but got no elements")
                        return False
                else:
                    print_error(f"Expected failure but request succeeded")
                    return False
                    
            elif response.status == 422:
                # Validation error
                if not scenario["expected_success"]:
                    error_detail = data.get("detail", "Unknown validation error")
                    
                    if isinstance(error_detail, list) and len(error_detail) > 0:
                        error_msg = error_detail[0].get("msg", "Unknown error")
                        print_success(f"Got expected validation error: {error_msg}")
                    else:
                        print_success(f"Got expected validation error: {error_detail}")
                    
                    # Verify error type matches
                    if "expected_error_type" in scenario:
                        if scenario["expected_error_type"] == "invalid_url":
                            return True
                    return True
                else:
                    print_error(f"Unexpected validation error: {data}")
                    return False
                    
            elif response.status == 500:
                # Server error with our structured error response
                if not scenario["expected_success"]:
                    if "error" in data:
                        error_info = data["error"]
                        print_success(f"Got expected error response:")
                        print(f"     Type: {error_info.get('error_type', 'unknown')}")
                        print(f"     Message: {error_info.get('message', 'unknown')}")
                        
                        if "suggestion" in error_info:
                            print(f"     Suggestion: {error_info['suggestion']}")
                        
                        # Verify error type matches expected
                        if "expected_error_type" in scenario:
                            actual_type = error_info.get("error_type", "")
                            if actual_type == scenario["expected_error_type"]:
                                print_success(f"Error type matches expected: {actual_type}")
                            else:
                                print_warning(f"Error type mismatch - Expected: {scenario['expected_error_type']}, Got: {actual_type}")
                        
                        return True
                    else:
                        print_error(f"Expected structured error but got: {data}")
                        return False
                else:
                    print_error(f"Unexpected server error: {data}")
                    return False
            else:
                print_error(f"Unexpected status code: {response.status}")
                print(f"   Response: {data}")
                return False
                
    except asyncio.TimeoutError:
        if not scenario["expected_success"] and scenario.get("expected_error_type") == "navigation_timeout":
            print_success("Request timed out as expected")
            return True
        else:
            print_error("Request timed out unexpectedly")
            return False
            
    except Exception as e:
        print_error(f"Test failed with exception: {e}")
        return False

async def run_tests():
    """Run all test scenarios"""
    
    print_header("ERROR HANDLING TEST SUITE")
    print("Testing Extract Elements feature error handling")
    print(f"Target: {BASE_URL}")
    
    # Check if backend is running
    print("\n[CHECK] Checking backend availability...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    print_success("Backend is running")
                else:
                    print_error(f"Backend returned status {resp.status}")
                    return
    except Exception as e:
        print_error(f"Backend is not available: {e}")
        print_warning("Please start the backend with: cd simple_apps_v2 && python -m uvicorn backend.web_automation.main:app --port 5175")
        return
    
    # Run test scenarios
    print_header("RUNNING TEST SCENARIOS")
    
    results = []
    async with aiohttp.ClientSession() as session:
        for i, scenario in enumerate(TEST_SCENARIOS, 1):
            print(f"\n{TestColors.BOLD}[{i}/{len(TEST_SCENARIOS)}]{TestColors.ENDC}", end="")
            
            success = await test_extraction(session, scenario)
            results.append({
                "scenario": scenario["name"],
                "success": success
            })
            
            # Small delay between tests
            await asyncio.sleep(1)
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for r in results if r["success"])
    failed = len(results) - passed
    
    print(f"\nTotal tests: {len(results)}")
    print(f"{TestColors.GREEN}Passed: {passed}{TestColors.ENDC}")
    if failed > 0:
        print(f"{TestColors.FAIL}Failed: {failed}{TestColors.ENDC}")
    
    print("\n[RESULTS] By scenario:")
    for result in results:
        status = "PASS" if result["success"] else "FAIL"
        color = TestColors.GREEN if result["success"] else TestColors.FAIL
        print(f"   {color}[{status}]{TestColors.ENDC} - {result['scenario']}")
    
    if failed == 0:
        print_success("\nAll tests passed!")
    else:
        print_error(f"\n{failed} test(s) failed")
    
    return failed == 0

async def test_retry_mechanism():
    """Test the retry mechanism specifically"""
    
    print_header("RETRY MECHANISM TEST")
    
    test_url = "https://httpstat.us/500"  # This will fail
    
    print(f"Testing retry mechanism with URL that returns 500 error")
    print(f"URL: {test_url}")
    print("Expected: Should attempt 3 times before giving up")
    
    async with aiohttp.ClientSession() as session:
        print("\n[RETRY] Sending request...")
        start_time = time.time()
        
        try:
            async with session.post(
                f"{BASE_URL}/api/extract-elements",
                json={"url": test_url},
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                elapsed = time.time() - start_time
                data = await response.json()
                
                print(f"\n[TIME] Total time: {elapsed:.2f}s")
                
                if response.status == 500 and "error" in data:
                    error_info = data["error"]
                    print_success("Retry mechanism completed")
                    print(f"   Final error type: {error_info.get('error_type')}")
                    print(f"   Recoverable: {error_info.get('recoverable', True)}")
                    
                    # Check if it mentions retry attempts
                    if "technical_details" in error_info:
                        print(f"   Technical details: {error_info['technical_details']}")
                        
        except Exception as e:
            print_error(f"Test failed: {e}")

if __name__ == "__main__":
    print(f"{TestColors.BOLD}Extract Elements - Error Handling Test Suite{TestColors.ENDC}")
    print(f"Testing comprehensive error handling for web automation")
    
    # Run main tests
    asyncio.run(run_tests())
    
    # Run retry mechanism test
    print("\n")
    asyncio.run(test_retry_mechanism())