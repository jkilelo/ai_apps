"""
Comprehensive Test Suite for API Server with Database Integration
Tests all endpoints and database persistence functionality
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8005"

class APITester:
    def __init__(self):
        self.session = None
        self.test_url = "https://example.com"
        self.results = {
            "passed": 0,
            "failed": 0,
            "tests": []
        }

    async def setup(self):
        """Setup aiohttp session"""
        self.session = aiohttp.ClientSession()

    async def cleanup(self):
        """Cleanup session"""
        if self.session:
            await self.session.close()

    def print_header(self, title):
        """Print test section header"""
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")

    async def test_endpoint(self, name: str, method: str, endpoint: str, data: Dict[str, Any] = None, expected_status: int = 200):
        """Test a single endpoint"""
        try:
            url = f"{BASE_URL}{endpoint}"

            if method == "GET":
                async with self.session.get(url) as response:
                    status = response.status
                    result = await response.json()
            elif method == "POST":
                async with self.session.post(url, json=data) as response:
                    status = response.status
                    result = await response.json()
            elif method == "DELETE":
                async with self.session.delete(url) as response:
                    status = response.status
                    result = await response.json()
            else:
                raise ValueError(f"Unsupported method: {method}")

            if status == expected_status:
                print(f"[OK] {name}: Status {status}")
                self.results["passed"] += 1
                self.results["tests"].append({
                    "name": name,
                    "status": "passed",
                    "response": result
                })
                return result
            else:
                print(f"[FAIL] {name}: Expected {expected_status}, got {status}")
                print(f"       Response: {result}")
                self.results["failed"] += 1
                self.results["tests"].append({
                    "name": name,
                    "status": "failed",
                    "response": result
                })
                return None

        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            self.results["failed"] += 1
            self.results["tests"].append({
                "name": name,
                "status": "error",
                "error": str(e)
            })
            return None

    async def test_root_endpoint(self):
        """Test 1: Root endpoint"""
        self.print_header("TEST 1: Root Endpoint")

        result = await self.test_endpoint(
            "Get API info",
            "GET",
            "/"
        )

        if result:
            print(f"  Database stats: {result.get('database_stats', {})}")

    async def test_extraction_with_cache(self):
        """Test 2: Element extraction with caching"""
        self.print_header("TEST 2: Element Extraction with Caching")

        # First extraction (should save to DB)
        result1 = await self.test_endpoint(
            "Extract elements (fresh)",
            "POST",
            "/api/web-automation/extract",
            {
                "url": self.test_url,
                "max_elements": 5,
                "use_cache": False
            }
        )

        if result1:
            print(f"  Elements found: {result1.get('total_found', 0)}")
            print(f"  From cache: {result1.get('from_cache', False)}")
            session_id = result1.get('session_id')

        # Second extraction (should load from cache)
        result2 = await self.test_endpoint(
            "Extract elements (cached)",
            "POST",
            "/api/web-automation/extract",
            {
                "url": self.test_url,
                "max_elements": 5,
                "use_cache": True,
                "cache_strategy": "cached"
            }
        )

        if result2:
            print(f"  From cache: {result2.get('from_cache', False)}")
            assert result2.get('from_cache') == True, "Should have loaded from cache"

    async def test_ai_analysis(self):
        """Test 3: AI element analysis"""
        self.print_header("TEST 3: AI Element Analysis")

        # Analyze elements (will use cached extraction)
        result = await self.test_endpoint(
            "Analyze elements with AI",
            "POST",
            "/api/web-automation/analyze-elements",
            {
                "url": self.test_url,
                "use_cache": True
            }
        )

        if result:
            print(f"  Page type: {result.get('page_type', 'unknown')}")
            print(f"  Elements analyzed: {result.get('element_count', 0)}")

    async def test_test_generation(self):
        """Test 4: Test scenario generation"""
        self.print_header("TEST 4: Test Scenario Generation")

        # Generate tests
        result = await self.test_endpoint(
            "Generate test scenarios",
            "POST",
            "/api/web-automation/generate-tests",
            {
                "url": self.test_url,
                "use_cache": True
            }
        )

        if result:
            print(f"  Tests generated: {len(result.get('tests', []))}")
            print(f"  From cache: {result.get('from_cache', False)}")

            # Test with cache
            result2 = await self.test_endpoint(
                "Generate tests (cached)",
                "POST",
                "/api/web-automation/generate-tests",
                {
                    "url": self.test_url,
                    "use_cache": True
                }
            )

            if result2:
                print(f"  From cache (2nd call): {result2.get('from_cache', False)}")

    async def test_code_generation(self):
        """Test 5: Code generation"""
        self.print_header("TEST 5: Code Generation")

        # Generate code
        result = await self.test_endpoint(
            "Generate Playwright code",
            "POST",
            "/api/web-automation/generate-code",
            {
                "url": self.test_url,
                "framework": "playwright",
                "language": "python",
                "use_cache": True
            }
        )

        if result:
            print(f"  Framework: {result.get('framework', 'unknown')}")
            print(f"  Language: {result.get('language', 'unknown')}")
            print(f"  Code length: {len(result.get('code', ''))} chars")
            print(f"  From cache: {result.get('from_cache', False)}")

    async def test_session_management(self):
        """Test 6: Session management endpoints"""
        self.print_header("TEST 6: Session Management")

        # Get session summary
        result = await self.test_endpoint(
            "Get session summary",
            "GET",
            f"/api/web-automation/session/{self.test_url}"
        )

        if result:
            print(f"  URL: {result.get('url', '')}")
            print(f"  Complete: {result.get('is_complete', False)}")
            print(f"  Completion: {result.get('completion_percentage', 0)}%")
            print(f"  Elements: {result.get('total_elements', 0)}")

        # List sessions
        result = await self.test_endpoint(
            "List all sessions",
            "GET",
            "/api/web-automation/sessions?limit=5"
        )

        if result:
            print(f"  Total sessions: {result.get('total_count', 0)}")
            sessions = result.get('sessions', [])
            for session in sessions[:3]:
                print(f"    - {session.get('netloc', 'unknown')}: {session.get('page_title', 'N/A')}")

    async def test_resume_functionality(self):
        """Test 7: Resume functionality"""
        self.print_header("TEST 7: Resume Functionality")

        # Create partial session
        partial_url = "https://partial-test.com"

        # Extract only
        await self.test_endpoint(
            "Extract for partial session",
            "POST",
            "/api/web-automation/extract",
            {
                "url": partial_url,
                "use_cache": False
            }
        )

        # Check resume point
        result = await self.test_endpoint(
            "Get resume point",
            "GET",
            f"/api/web-automation/resume/{partial_url}"
        )

        if result:
            print(f"  Next step: {result.get('next_step', 'None')}")
            print(f"  Steps remaining: {result.get('steps_remaining', [])}")

    async def test_cache_management(self):
        """Test 8: Cache management"""
        self.print_header("TEST 8: Cache Management")

        # Clear specific cache
        result = await self.test_endpoint(
            "Clear extraction cache",
            "POST",
            f"/api/web-automation/clear-cache/{self.test_url}",
            ["element_extraction"]
        )

        if result:
            print(f"  Message: {result.get('message', '')}")
            print(f"  Steps cleared: {result.get('steps_cleared', 'unknown')}")

        # Get stats
        result = await self.test_endpoint(
            "Get database statistics",
            "GET",
            "/api/web-automation/stats"
        )

        if result:
            print(f"  Total sessions: {result.get('total_sessions', 0)}")
            print(f"  Complete sessions: {result.get('complete_sessions', 0)}")
            print(f"  Completion rate: {result.get('completion_rate', 0):.1f}%")

    async def test_full_pipeline(self):
        """Test 9: Full pipeline execution"""
        self.print_header("TEST 9: Full Pipeline Execution")

        test_url = "https://pipeline-test.com"

        # Step 1: Extract
        result = await self.test_endpoint(
            "Pipeline - Extract",
            "POST",
            "/api/web-automation/extract",
            {"url": test_url, "use_cache": False}
        )
        print(f"  Step 1 complete: {result is not None}")

        # Step 2: Analyze
        result = await self.test_endpoint(
            "Pipeline - Analyze",
            "POST",
            "/api/web-automation/analyze-elements",
            {"url": test_url}
        )
        print(f"  Step 2 complete: {result is not None}")

        # Step 3: Generate tests
        result = await self.test_endpoint(
            "Pipeline - Generate tests",
            "POST",
            "/api/web-automation/generate-tests",
            {"url": test_url}
        )
        print(f"  Step 3 complete: {result is not None}")

        # Step 4: Generate code
        result = await self.test_endpoint(
            "Pipeline - Generate code",
            "POST",
            "/api/web-automation/generate-code",
            {"url": test_url}
        )
        print(f"  Step 4 complete: {result is not None}")

        # Check session completeness
        result = await self.test_endpoint(
            "Pipeline - Check completion",
            "GET",
            f"/api/web-automation/session/{test_url}"
        )

        if result:
            print(f"  Pipeline complete: {result.get('is_complete', False)}")
            print(f"  Completion percentage: {result.get('completion_percentage', 0)}%")

    async def test_error_handling(self):
        """Test 10: Error handling"""
        self.print_header("TEST 10: Error Handling")

        # Test with invalid URL
        result = await self.test_endpoint(
            "Extract with invalid URL",
            "POST",
            "/api/web-automation/extract",
            {"url": "invalid-url", "use_cache": False},
            expected_status=500
        )

        # Test non-existent session
        result = await self.test_endpoint(
            "Get non-existent session",
            "GET",
            "/api/web-automation/session/https://does-not-exist.com",
            expected_status=404
        )

        # Delete non-existent session
        result = await self.test_endpoint(
            "Delete non-existent session",
            "DELETE",
            "/api/web-automation/session/https://does-not-exist.com",
            expected_status=404
        )

    async def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print(" API SERVER WITH DATABASE - COMPREHENSIVE TEST SUITE")
        print("="*60)

        await self.setup()

        try:
            # Run tests
            await self.test_root_endpoint()
            await self.test_extraction_with_cache()
            await self.test_ai_analysis()
            await self.test_test_generation()
            await self.test_code_generation()
            await self.test_session_management()
            await self.test_resume_functionality()
            await self.test_cache_management()
            await self.test_full_pipeline()
            await self.test_error_handling()

            # Print summary
            self.print_header("TEST SUMMARY")
            print(f"Total tests: {self.results['passed'] + self.results['failed']}")
            print(f"Passed: {self.results['passed']}")
            print(f"Failed: {self.results['failed']}")

            if self.results['failed'] == 0:
                print("\n[OK] ALL TESTS PASSED!")
            else:
                print(f"\n[WARNING] {self.results['failed']} tests failed")
                print("Failed tests:")
                for test in self.results['tests']:
                    if test['status'] == 'failed' or test['status'] == 'error':
                        print(f"  - {test['name']}")

        finally:
            await self.cleanup()

async def main():
    """Main test runner"""
    tester = APITester()
    await tester.run_all_tests()

if __name__ == "__main__":
    print("Starting API tests...")
    print(f"Testing against: {BASE_URL}")
    print("Make sure the API server is running on port 8003")
    print("Run: python api_server_with_db.py")
    print("\nStarting tests in 2 seconds...")
    time.sleep(2)

    asyncio.run(main())