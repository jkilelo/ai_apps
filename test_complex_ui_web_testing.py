"""
Test UI Web Testing API with a more complex website
"""

import asyncio
import aiohttp
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8002/api/v1"

async def test_complex_workflow():
    async with aiohttp.ClientSession() as session:
        print("=" * 50)
        print("UI Web Testing API - Complex Website Test")
        print("=" * 50)
        
        # Test with a more feature-rich website
        test_url = "https://www.wikipedia.org"
        
        # Step 1: Element Extraction
        print("\n=== Testing Element Extraction ===")
        print(f"Starting element extraction for {test_url}...")
        
        extract_payload = {
            "web_page_url": test_url,
            "profile_type": "qa_manual_tester",
            "max_depth": 1,
            "max_pages": 1
        }
        
        async with session.post(f"{API_BASE_URL}/element-extraction/extract", json=extract_payload) as resp:
            result = await resp.json()
            job_id = result["job_id"]
            print(f"Job started: {job_id}")
        
        # Poll for completion
        extraction_result = await poll_job_status(
            session, 
            f"{API_BASE_URL}/element-extraction/extract/{job_id}",
            timeout=60
        )
        
        if extraction_result["status"] == "completed":
            print("✓ Extraction completed!")
            elements = extraction_result["extracted_elements"]
            print(f"  - Elements found: {len(elements)}")
            print(f"  - Element types: {set(e['type'] for e in elements)}")
            
            # Show first 5 elements
            print("\n  First 5 elements extracted:")
            for i, elem in enumerate(elements[:5]):
                print(f"    {i+1}. {elem['type']}: {elem.get('text', 'No text')[:50]}")
        else:
            print(f"✗ Extraction failed: {extraction_result.get('error', 'Unknown error')}")
            return
        
        # Step 2: Test Generation
        print("\n=== Testing Test Generation ===")
        print(f"Generating tests for {len(elements)} elements...")
        
        gen_payload = {
            "extracted_elements": elements[:10],  # Limit to first 10 elements
            "test_type": "functional",
            "framework": "playwright",
            "include_negative_tests": True
        }
        
        async with session.post(f"{API_BASE_URL}/test-generation/generate", json=gen_payload) as resp:
            result = await resp.json()
            gen_job_id = result["job_id"]
            print(f"Job started: {gen_job_id}")
        
        generation_result = await poll_job_status(
            session,
            f"{API_BASE_URL}/test-generation/generate/{gen_job_id}",
            timeout=30
        )
        
        if generation_result["status"] == "completed":
            print("✓ Test generation completed!")
            test_cases = generation_result["test_cases"]
            print(f"  - Test cases generated: {len(test_cases)}")
            
            # Show test case summary
            print("\n  Test cases summary:")
            for i, test in enumerate(test_cases[:5]):
                print(f"    {i+1}. {test['name']}")
        else:
            print(f"✗ Generation failed: {generation_result.get('error', 'Unknown error')}")
            return
        
        # Step 3: Test Execution
        print("\n=== Testing Test Execution ===")
        print(f"Executing {len(test_cases[:5])} test cases...")
        
        exec_payload = {
            "test_cases": test_cases[:5],  # Execute first 5 tests
            "execution_mode": "sequential",
            "browser": "chromium",
            "timeout": 30
        }
        
        async with session.post(f"{API_BASE_URL}/test-execution/execute", json=exec_payload) as resp:
            result = await resp.json()
            exec_job_id = result["job_id"]
            print(f"Job started: {exec_job_id}")
        
        execution_result = await poll_job_status(
            session,
            f"{API_BASE_URL}/test-execution/execute/{exec_job_id}",
            timeout=120
        )
        
        if execution_result["status"] == "completed":
            print("✓ Test execution completed!")
            summary = execution_result["summary"]
            print(f"  - Total tests: {summary['total']}")
            print(f"  - Passed: {summary['passed']}")
            print(f"  - Failed: {summary['failed']}")
            print(f"  - Pass rate: {summary['pass_rate']:.1f}%")
            
            # Show individual test results
            print("\n  Individual test results:")
            for result in execution_result["test_results"]:
                status_icon = "✓" if result["status"] == "passed" else "✗"
                print(f"    {status_icon} {result['test_name']} ({result['duration']:.2f}s)")
                if result["status"] == "failed" and result.get("error"):
                    print(f"      Error: {result['error']}")
        else:
            print(f"✗ Execution failed: {execution_result.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 50)
        print("✓ Complex workflow test completed!")
        print("=" * 50)


async def poll_job_status(session, url, timeout=60, interval=1):
    """Poll job status until completion or timeout"""
    start_time = asyncio.get_event_loop().time()
    
    while asyncio.get_event_loop().time() - start_time < timeout:
        async with session.get(url) as resp:
            result = await resp.json()
            status = result.get("status")
            print(f"Status: {status}")
            
            if status in ["completed", "failed"]:
                return result
        
        await asyncio.sleep(interval)
    
    raise TimeoutError(f"Job timed out after {timeout} seconds")


if __name__ == "__main__":
    asyncio.run(test_complex_workflow())