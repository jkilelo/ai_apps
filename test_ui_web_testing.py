#!/usr/bin/env python3
"""
Test script for UI Web Testing API
This script tests the real API endpoints to ensure everything works correctly
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

API_BASE_URL = "http://localhost:8002/api/v1"

async def test_element_extraction():
    """Test the element extraction endpoint"""
    print("\n=== Testing Element Extraction ===")
    
    async with httpx.AsyncClient() as client:
        # Start extraction
        request_data = {
            "web_page_url": "https://example.com",
            "profile": "qa_manual_tester",
            "include_screenshots": False,
            "max_depth": 1
        }
        
        print(f"Starting element extraction for {request_data['web_page_url']}...")
        response = await client.post(
            f"{API_BASE_URL}/element-extraction/extract",
            json=request_data
        )
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return None
        
        job_data = response.json()
        job_id = job_data["job_id"]
        print(f"Job started: {job_id}")
        
        # Poll for results
        max_attempts = 30
        for attempt in range(max_attempts):
            await asyncio.sleep(2)
            
            status_response = await client.get(
                f"{API_BASE_URL}/element-extraction/extract/{job_id}"
            )
            
            if status_response.status_code != 200:
                print(f"Error checking status: {status_response.text}")
                return None
            
            result = status_response.json()
            print(f"Status: {result['status']}")
            
            if result["status"] == "completed":
                print(f"✓ Extraction completed!")
                print(f"  - Elements found: {len(result.get('extracted_elements', []))}")
                if result.get('metadata'):
                    print(f"  - Pages crawled: {result['metadata'].get('pages_crawled', 0)}")
                return result.get('extracted_elements', [])
            
            elif result["status"] == "failed":
                print(f"✗ Extraction failed: {result.get('error', 'Unknown error')}")
                return None
        
        print("✗ Extraction timed out")
        return None


async def test_test_generation(extracted_elements: list):
    """Test the test generation endpoint"""
    print("\n=== Testing Test Generation ===")
    
    if not extracted_elements:
        print("No elements to generate tests for")
        return None
    
    async with httpx.AsyncClient() as client:
        # Start test generation
        request_data = {
            "extracted_elements": extracted_elements,
            "test_type": "functional",
            "framework": "playwright_pytest",
            "include_negative_tests": True
        }
        
        print(f"Generating tests for {len(extracted_elements)} elements...")
        response = await client.post(
            f"{API_BASE_URL}/test-generation/generate",
            json=request_data
        )
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return None
        
        job_data = response.json()
        job_id = job_data["job_id"]
        print(f"Job started: {job_id}")
        
        # Poll for results
        max_attempts = 20
        for attempt in range(max_attempts):
            await asyncio.sleep(2)
            
            status_response = await client.get(
                f"{API_BASE_URL}/test-generation/generate/{job_id}"
            )
            
            if status_response.status_code != 200:
                print(f"Error checking status: {status_response.text}")
                return None
            
            result = status_response.json()
            print(f"Status: {result['status']}")
            
            if result["status"] == "completed":
                print(f"✓ Test generation completed!")
                print(f"  - Test cases generated: {len(result.get('test_cases', []))}")
                return result.get('test_cases', [])
            
            elif result["status"] == "failed":
                print(f"✗ Test generation failed: {result.get('error', 'Unknown error')}")
                return None
        
        print("✗ Test generation timed out")
        return None


async def test_test_execution(test_cases: list):
    """Test the test execution endpoint"""
    print("\n=== Testing Test Execution ===")
    
    if not test_cases:
        print("No test cases to execute")
        return None
    
    async with httpx.AsyncClient() as client:
        # Start test execution
        request_data = {
            "test_cases": test_cases,
            "execution_mode": "sequential",
            "timeout": 300,
            "browser": "chromium"
        }
        
        print(f"Executing {len(test_cases)} test cases...")
        response = await client.post(
            f"{API_BASE_URL}/test-execution/execute",
            json=request_data
        )
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return None
        
        job_data = response.json()
        job_id = job_data["job_id"]
        print(f"Job started: {job_id}")
        
        # Poll for results
        max_attempts = 30
        for attempt in range(max_attempts):
            await asyncio.sleep(2)
            
            status_response = await client.get(
                f"{API_BASE_URL}/test-execution/execute/{job_id}"
            )
            
            if status_response.status_code != 200:
                print(f"Error checking status: {status_response.text}")
                return None
            
            result = status_response.json()
            print(f"Status: {result['status']}")
            
            if result["status"] == "completed":
                print(f"✓ Test execution completed!")
                summary = result.get('summary', {})
                print(f"  - Total tests: {summary.get('total', 0)}")
                print(f"  - Passed: {summary.get('passed', 0)}")
                print(f"  - Failed: {summary.get('failed', 0)}")
                print(f"  - Pass rate: {summary.get('pass_rate', 0):.1f}%")
                return result
            
            elif result["status"] == "failed":
                print(f"✗ Test execution failed: {result.get('error', 'Unknown error')}")
                return None
        
        print("✗ Test execution timed out")
        return None


async def test_full_workflow():
    """Test the complete workflow"""
    print("\n" + "="*50)
    print("UI Web Testing API - Full Workflow Test")
    print("="*50)
    
    # Check if API is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL.replace('/v1', '')}/health")
            if response.status_code == 200:
                print("✓ API is healthy")
            else:
                print("✗ API health check failed")
                return
    except Exception as e:
        print(f"✗ Cannot connect to API at {API_BASE_URL}")
        print(f"  Error: {e}")
        print("\nMake sure the API server is running:")
        print("  cd /var/www/ai_apps/apps/ui_web_auto_testing")
        print("  python run_api.py")
        return
    
    # Test element extraction
    extracted_elements = await test_element_extraction()
    if not extracted_elements:
        print("\n✗ Workflow failed at element extraction step")
        return
    
    # Test test generation
    test_cases = await test_test_generation(extracted_elements)
    if not test_cases:
        print("\n✗ Workflow failed at test generation step")
        return
    
    # Test test execution
    execution_result = await test_test_execution(test_cases)
    if not execution_result:
        print("\n✗ Workflow failed at test execution step")
        return
    
    print("\n" + "="*50)
    print("✓ Full workflow completed successfully!")
    print("="*50)


if __name__ == "__main__":
    asyncio.run(test_full_workflow())