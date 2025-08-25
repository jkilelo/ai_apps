"""
Test Script for Web Automation Pipeline
Tests each endpoint with live LLM connections
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import logging
from typing import Dict, Any
import sys
from pathlib import Path

# Add paths for imports
simple_apps_v2_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(simple_apps_v2_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/ui"

# Test URLs
TEST_URLS = [
    "https://www.example.com",
    "https://www.wikipedia.org",
    "https://www.python.org"
]

class PipelineTestClient:
    """Client for testing the web automation pipeline"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health(self) -> bool:
        """Test the health endpoint"""
        try:
            async with self.session.get(f"{self.base_url}{API_PREFIX}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Health Check: {data['status']}")
                    return True
                else:
                    logger.error(f"❌ Health Check Failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Health Check Error: {str(e)}")
            return False
    
    async def test_step1_element_extraction(self, url: str) -> Dict[str, Any]:
        """Test Step 1: Element Extraction"""
        logger.info(f"\n🔍 Testing Step 1: Element Extraction for {url}")
        
        try:
            payload = {
                "url": url,
                "headless": True
            }
            
            async with self.session.post(
                f"{self.base_url}{API_PREFIX}/element_extraction",
                json=payload
            ) as response:
                data = await response.json()
                
                if data['success']:
                    elements_count = data['data']['statistics']['total_elements']
                    logger.info(f"✅ Step 1 Success: Extracted {elements_count} elements")
                    self.test_results.append({
                        "step": "element_extraction",
                        "url": url,
                        "success": True,
                        "elements": elements_count
                    })
                    return data['data']
                else:
                    logger.error(f"❌ Step 1 Failed: {data['error']}")
                    self.test_results.append({
                        "step": "element_extraction",
                        "url": url,
                        "success": False,
                        "error": data['error']
                    })
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Step 1 Error: {str(e)}")
            self.test_results.append({
                "step": "element_extraction",
                "url": url,
                "success": False,
                "error": str(e)
            })
            return None
    
    async def test_step2_test_generation(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test Step 2: Test Generation"""
        logger.info(f"\n🧪 Testing Step 2: Test Generation")
        
        if not extraction_data:
            logger.warning("⚠️ Skipping Step 2: No extraction data")
            return None
        
        try:
            payload = {
                "extraction_data": extraction_data,
                "test_categories": ["functional", "validation", "navigation"]
            }
            
            async with self.session.post(
                f"{self.base_url}{API_PREFIX}/test_generation",
                json=payload
            ) as response:
                data = await response.json()
                
                if data['success']:
                    scenarios = data['data']['statistics']['scenarios_count']
                    logger.info(f"✅ Step 2 Success: Generated {scenarios} test scenarios")
                    self.test_results.append({
                        "step": "test_generation",
                        "success": True,
                        "scenarios": scenarios
                    })
                    return data['data']
                else:
                    logger.error(f"❌ Step 2 Failed: {data['error']}")
                    self.test_results.append({
                        "step": "test_generation",
                        "success": False,
                        "error": data['error']
                    })
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Step 2 Error: {str(e)}")
            self.test_results.append({
                "step": "test_generation",
                "success": False,
                "error": str(e)
            })
            return None
    
    async def test_step3_code_generation(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test Step 3: Code Generation"""
        logger.info(f"\n💻 Testing Step 3: Code Generation")
        
        if not test_data:
            logger.warning("⚠️ Skipping Step 3: No test data")
            return None
        
        try:
            payload = {
                "test_data": test_data,
                "language": "python",
                "framework": "playwright"
            }
            
            async with self.session.post(
                f"{self.base_url}{API_PREFIX}/code_generation",
                json=payload
            ) as response:
                data = await response.json()
                
                if data['success']:
                    files = data['data']['statistics']['total_files']
                    lines = data['data']['statistics']['total_lines']
                    logger.info(f"✅ Step 3 Success: Generated {files} files with {lines} lines of code")
                    self.test_results.append({
                        "step": "code_generation",
                        "success": True,
                        "files": files,
                        "lines": lines
                    })
                    return data['data']
                else:
                    logger.error(f"❌ Step 3 Failed: {data['error']}")
                    self.test_results.append({
                        "step": "code_generation",
                        "success": False,
                        "error": data['error']
                    })
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Step 3 Error: {str(e)}")
            self.test_results.append({
                "step": "code_generation",
                "success": False,
                "error": str(e)
            })
            return None
    
    async def test_step4_code_execution(self, code_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test Step 4: Code Execution"""
        logger.info(f"\n🚀 Testing Step 4: Code Execution")
        
        if not code_data:
            logger.warning("⚠️ Skipping Step 4: No code data")
            return None
        
        try:
            payload = {
                "code_data": code_data,
                "run_tests": False  # Dry run for testing
            }
            
            async with self.session.post(
                f"{self.base_url}{API_PREFIX}/code_execution",
                json=payload
            ) as response:
                data = await response.json()
                
                if data['success']:
                    status = data['data']['execution_results']['status']
                    logger.info(f"✅ Step 4 Success: Execution status = {status}")
                    self.test_results.append({
                        "step": "code_execution",
                        "success": True,
                        "status": status
                    })
                    return data['data']
                else:
                    logger.error(f"❌ Step 4 Failed: {data['error']}")
                    self.test_results.append({
                        "step": "code_execution",
                        "success": False,
                        "error": data['error']
                    })
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Step 4 Error: {str(e)}")
            self.test_results.append({
                "step": "code_execution",
                "success": False,
                "error": str(e)
            })
            return None
    
    async def test_full_pipeline(self, url: str) -> Dict[str, Any]:
        """Test the full pipeline endpoint"""
        logger.info(f"\n🎯 Testing Full Pipeline for {url}")
        
        try:
            payload = {
                "url": url,
                "headless": True,
                "language": "python",
                "framework": "playwright",
                "execute": False  # Dry run
            }
            
            async with self.session.post(
                f"{self.base_url}{API_PREFIX}/full_pipeline",
                json=payload
            ) as response:
                data = await response.json()
                
                if data['success']:
                    summary = data['data']['summary']
                    logger.info(f"✅ Full Pipeline Success:")
                    logger.info(f"   - Elements: {summary['elements_found']}")
                    logger.info(f"   - Tests: {summary['tests_generated']}")
                    logger.info(f"   - Files: {summary['code_files_created']}")
                    return data['data']
                else:
                    logger.error(f"❌ Full Pipeline Failed: {data['error']}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Full Pipeline Error: {str(e)}")
            return None
    
    async def run_sequential_test(self, url: str):
        """Run sequential test of all 4 steps"""
        logger.info(f"\n{'='*60}")
        logger.info(f"📋 Running Sequential Test for {url}")
        logger.info(f"{'='*60}")
        
        # Step 1: Element Extraction
        extraction_data = await self.test_step1_element_extraction(url)
        if not extraction_data:
            logger.warning("⚠️ Stopping test: Step 1 failed")
            return
        
        # Step 2: Test Generation
        test_data = await self.test_step2_test_generation(extraction_data)
        if not test_data:
            logger.warning("⚠️ Stopping test: Step 2 failed")
            return
        
        # Step 3: Code Generation
        code_data = await self.test_step3_code_generation(test_data)
        if not code_data:
            logger.warning("⚠️ Stopping test: Step 3 failed")
            return
        
        # Step 4: Code Execution
        execution_data = await self.test_step4_code_execution(code_data)
        if not execution_data:
            logger.warning("⚠️ Stopping test: Step 4 failed")
            return
        
        logger.info(f"\n✅ Sequential Test Completed Successfully!")
    
    def print_summary(self):
        """Print test summary"""
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 Test Summary")
        logger.info(f"{'='*60}")
        
        success_count = sum(1 for r in self.test_results if r.get('success'))
        total_count = len(self.test_results)
        
        logger.info(f"Total Tests: {total_count}")
        logger.info(f"Successful: {success_count}")
        logger.info(f"Failed: {total_count - success_count}")
        logger.info(f"Success Rate: {(success_count/total_count*100):.1f}%")
        
        # Print detailed results
        logger.info(f"\n📋 Detailed Results:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            step = result['step']
            if result['success']:
                details = json.dumps({k: v for k, v in result.items() if k not in ['step', 'success']})
                logger.info(f"  {status} {step}: {details}")
            else:
                logger.info(f"  {status} {step}: {result.get('error', 'Unknown error')}")

async def run_tests():
    """Main test runner"""
    logger.info(f"\n{'='*60}")
    logger.info(f"🚀 Starting Web Automation Pipeline Tests")
    logger.info(f"{'='*60}")
    logger.info(f"Time: {datetime.now().isoformat()}")
    logger.info(f"Base URL: {BASE_URL}")
    
    async with PipelineTestClient(BASE_URL) as client:
        # Test health endpoint
        if not await client.test_health():
            logger.error("❌ API is not healthy. Please start the backend server.")
            return
        
        # Test with example.com (simple site)
        await client.run_sequential_test(TEST_URLS[0])
        
        # Test full pipeline endpoint
        await client.test_full_pipeline(TEST_URLS[0])
        
        # Print summary
        client.print_summary()
    
    logger.info(f"\n🎉 Tests Completed at {datetime.now().isoformat()}")

async def test_standalone_functions():
    """Test the standalone functions directly without API"""
    logger.info(f"\n{'='*60}")
    logger.info(f"🧪 Testing Standalone Functions")
    logger.info(f"{'='*60}")
    
    from automation_pipeline import (
        element_extraction,
        test_generation,
        code_generation,
        code_execution
    )
    
    try:
        # Test Step 1
        logger.info("\n📍 Testing element_extraction function...")
        extraction = await element_extraction("https://www.example.com")
        logger.info(f"   Result: {extraction['statistics']}")
        
        # Test Step 2
        logger.info("\n📍 Testing test_generation function...")
        tests = await test_generation(extraction)
        logger.info(f"   Result: {tests['statistics']}")
        
        # Test Step 3
        logger.info("\n📍 Testing code_generation function...")
        code = code_generation(tests)
        logger.info(f"   Result: {code['statistics']}")
        
        # Test Step 4
        logger.info("\n📍 Testing code_execution function...")
        execution = await code_execution(code, run_tests=False)
        logger.info(f"   Result: {execution['test_report']}")
        
        logger.info("\n✅ All standalone functions tested successfully!")
        
    except Exception as e:
        logger.error(f"\n❌ Standalone function test failed: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Web Automation Pipeline")
    parser.add_argument("--api", action="store_true", help="Test via API endpoints")
    parser.add_argument("--standalone", action="store_true", help="Test standalone functions")
    parser.add_argument("--url", type=str, help="Custom URL to test", default="https://www.example.com")
    
    args = parser.parse_args()
    
    if args.standalone:
        asyncio.run(test_standalone_functions())
    else:
        # Default to API testing
        if args.url not in TEST_URLS:
            TEST_URLS.insert(0, args.url)
        asyncio.run(run_tests())