"""
End-to-End Integration Test for Web Automation Pipeline
Tests the complete 4-step flow with actual API calls
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path
import time

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# API Configuration
API_BASE_URL = "http://localhost:5175/api/ui"
TEST_URL = "https://example.com"

async def test_element_extraction():
    """Test Step 1: Element Extraction"""
    print("\n[STEP 1] Element Extraction")
    print("-" * 50)
    print("[INFO] This step may take 30-60 seconds due to LLM processing...")
    
    start_time = time.time()
    
    # Increase timeout for LLM operations
    timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes timeout
    async with aiohttp.ClientSession(timeout=timeout) as session:
        payload = {
            "url": TEST_URL,
            "headless": True
        }
        
        async with session.post(f"{API_BASE_URL}/element_extraction", json=payload) as response:
            result = await response.json()
            
            elapsed = time.time() - start_time
            
            if result.get("success"):
                print(f"[SUCCESS] Element extraction successful (took {elapsed:.1f}s)")
                print(f"   - URL: {result['data'].get('url')}")
                print(f"   - Title: {result['data'].get('title')}")
                print(f"   - Elements found: {len(result['data'].get('elements', []))}")
                return result['data']
            else:
                print(f"[ERROR] Element extraction failed after {elapsed:.1f}s: {result.get('error')}")
                return None

async def test_test_generation(extraction_data):
    """Test Step 2: Test Generation"""
    print("\n[STEP 2] Test Generation")
    print("-" * 50)
    print("[INFO] This step may take 60-120 seconds due to multiple LLM calls...")
    
    start_time = time.time()
    
    # Increase timeout for LLM operations
    timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes timeout
    async with aiohttp.ClientSession(timeout=timeout) as session:
        payload = {
            "extraction_data": extraction_data,
            "test_categories": ["functional", "validation", "navigation", "interaction"]
        }
        
        async with session.post(f"{API_BASE_URL}/test_generation", json=payload) as response:
            result = await response.json()
            
            elapsed = time.time() - start_time
            
            if result.get("success"):
                print(f"[SUCCESS] Test generation successful (took {elapsed:.1f}s)")
                test_data = result['data']
                scenarios = test_data.get('test_scenarios', {})
                total_tests = sum(len(cat.get('scenarios', [])) for cat in scenarios.values())
                print(f"   - Categories: {len(scenarios)}")
                print(f"   - Total test scenarios: {total_tests}")
                return test_data
            else:
                print(f"[ERROR] Test generation failed after {elapsed:.1f}s: {result.get('error')}")
                return None

async def test_code_generation(test_data):
    """Test Step 3: Code Generation"""
    print("\n[STEP 3] Code Generation")
    print("-" * 50)
    print("[INFO] This step may take 60-90 seconds due to code generation...")
    
    start_time = time.time()
    
    # Increase timeout for LLM operations
    timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes timeout
    async with aiohttp.ClientSession(timeout=timeout) as session:
        payload = {
            "test_data": test_data,
            "language": "python",
            "framework": "playwright"
        }
        
        async with session.post(f"{API_BASE_URL}/code_generation", json=payload) as response:
            result = await response.json()
            
            elapsed = time.time() - start_time
            
            if result.get("success"):
                print(f"[SUCCESS] Code generation successful (took {elapsed:.1f}s)")
                code_data = result['data']
                print(f"   - Language: {code_data.get('language')}")
                print(f"   - Framework: {code_data.get('framework')}")
                print(f"   - Code length: {len(code_data.get('code', ''))} characters")
                print(f"   - Test files: {len(code_data.get('test_files', []))}")
                return code_data
            else:
                print(f"[ERROR] Code generation failed after {elapsed:.1f}s: {result.get('error')}")
                return None

async def test_code_execution(code_data):
    """Test Step 4: Code Execution"""
    print("\n[STEP 4] Code Execution")
    print("-" * 50)
    print("[INFO] This step may take 30-60 seconds to execute tests...")
    
    start_time = time.time()
    
    # Increase timeout for test execution
    timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes timeout
    async with aiohttp.ClientSession(timeout=timeout) as session:
        payload = {
            "code_data": code_data,
            "run_tests": True,
            "capture_screenshots": True,
            "timeout": 60000
        }
        
        async with session.post(f"{API_BASE_URL}/code_execution", json=payload) as response:
            result = await response.json()
            
            elapsed = time.time() - start_time
            
            if result.get("success"):
                print(f"[SUCCESS] Code execution successful (took {elapsed:.1f}s)")
                exec_data = result['data']
                test_exec = exec_data.get('test_execution', {})
                print(f"   - Tests executed: {test_exec.get('total_tests', 0)}")
                print(f"   - Tests passed: {test_exec.get('passed_tests', 0)}")
                print(f"   - Tests failed: {test_exec.get('failed_tests', 0)}")
                print(f"   - Execution time: {test_exec.get('execution_time', 0):.2f}s")
                return exec_data
            else:
                print(f"[ERROR] Code execution failed after {elapsed:.1f}s: {result.get('error')}")
                return None

async def run_full_pipeline():
    """Run the complete 4-step pipeline"""
    print("\n" + "="*60)
    print("Web Automation Pipeline - End-to-End Integration Test")
    print("="*60)
    print("\n[WARNING] This test may take 3-5 minutes to complete due to LLM processing.")
    print("[INFO] Please be patient while the pipeline runs through all 4 steps...")
    
    try:
        # Step 1: Element Extraction
        extraction_data = await test_element_extraction()
        if not extraction_data:
            print("\n[FAILED] Pipeline failed at Step 1")
            return False
        
        # Step 2: Test Generation
        test_data = await test_test_generation(extraction_data)
        if not test_data:
            print("\n[FAILED] Pipeline failed at Step 2")
            return False
        
        # Step 3: Code Generation
        code_data = await test_code_generation(test_data)
        if not code_data:
            print("\n[FAILED] Pipeline failed at Step 3")
            return False
        
        # Step 4: Code Execution
        execution_data = await test_code_execution(code_data)
        if not execution_data:
            print("\n[FAILED] Pipeline failed at Step 4")
            return False
        
        print("\n" + "="*60)
        print("[SUCCESS] PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        # Summary
        print("\n[SUMMARY] Pipeline Summary:")
        print(f"   - Target URL: {TEST_URL}")
        print(f"   - Elements extracted: {len(extraction_data.get('elements', []))}")
        test_scenarios = test_data.get('test_scenarios', {})
        total_scenarios = sum(len(cat.get('scenarios', [])) for cat in test_scenarios.values())
        print(f"   - Test scenarios generated: {total_scenarios}")
        print(f"   - Code files generated: {len(code_data.get('test_files', []))}")
        test_exec = execution_data.get('test_execution', {})
        print(f"   - Tests executed: {test_exec.get('total_tests', 0)}")
        print(f"   - Success rate: {(test_exec.get('passed_tests', 0) / max(test_exec.get('total_tests', 1), 1) * 100):.1f}%")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_backend_health():
    """Test if backend is running"""
    print("\n[HEALTH] Testing Backend Health...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"[SUCCESS] Backend is healthy: {data}")
                    return True
                else:
                    print(f"[ERROR] Backend returned status {response.status}")
                    return False
    except Exception as e:
        print(f"[ERROR] Cannot connect to backend: {e}")
        print(f"   Make sure the backend is running on port 5175")
        print(f"   Run: python simple_apps_v2/backend/web_automation/startup.py")
        return False

async def main():
    """Main test runner"""
    # Check backend health first
    if not await test_backend_health():
        print("\n[WARNING] Please start the backend server first!")
        return
    
    # Run full pipeline test
    success = await run_full_pipeline()
    
    if success:
        print("\n[SUCCESS] All integration tests passed!")
    else:
        print("\n[WARNING] Some tests failed. Check the output above.")

if __name__ == "__main__":
    print("\n[INFO] Starting Integration Tests...")
    print("   Backend URL: " + API_BASE_URL)
    print("   Test URL: " + TEST_URL)
    
    asyncio.run(main())