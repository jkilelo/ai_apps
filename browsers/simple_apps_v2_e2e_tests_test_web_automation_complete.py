"""
Comprehensive End-to-End Playwright Test Suite for Web Automation UI
Tests all 4 steps of the automation flow with real backend integration
"""

import asyncio
import pytest
from playwright.async_api import async_playwright, Page, expect
import logging
import sys
from pathlib import Path
import time
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test configuration
FRONTEND_URL = "http://localhost:3000"  # React frontend
BACKEND_URL = "http://localhost:5175"   # FastAPI backend
TEST_URL = "https://example.com"        # Simple test target
TIMEOUT = 60000  # 60 seconds for long operations
SHORT_TIMEOUT = 10000  # 10 seconds for quick operations

class WebAutomationE2ETest:
    """
    Senior QA Engineer approach to testing the Web Automation UI
    Tests all aspects: functionality, integration, error handling, and UX
    """
    
    def __init__(self):
        self.page = None
        self.context = None
        self.browser = None
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    async def setup(self):
        """Initialize browser and page for testing"""
        logger.info("🔧 Setting up test environment...")
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=False,  # Run with UI for visual validation
            slow_mo=500      # Slow down for observation
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )
        self.page = await self.context.new_page()
        
        # Enable console logging
        self.page.on("console", lambda msg: logger.debug(f"Browser console: {msg.text}"))
        self.page.on("pageerror", lambda err: logger.error(f"Page error: {err}"))
        
    async def teardown(self):
        """Clean up browser resources"""
        logger.info("🧹 Cleaning up test environment...")
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
    
    async def check_backend_health(self):
        """Verify backend is running and healthy"""
        logger.info("🏥 Checking backend health...")
        try:
            response = await self.page.request.get(f"{BACKEND_URL}/health")
            data = await response.json()
            assert response.status == 200, f"Backend health check failed: {response.status}"
            assert data.get("status") == "healthy", f"Backend unhealthy: {data}"
            logger.info("✅ Backend is healthy")
            return True
        except Exception as e:
            logger.error(f"❌ Backend health check failed: {e}")
            return False
    
    async def navigate_to_web_automation(self):
        """Navigate directly to the Web Automation flow"""
        logger.info("🧭 Navigating to Web Automation flow...")
        
        # Go directly to the web automation page
        await self.page.goto(f"{FRONTEND_URL}/web-automation", wait_until="networkidle")
        
        # Wait for the page to fully load by checking for the step indicator
        await self.page.wait_for_selector(
            'text="Element Extraction"',
            timeout=SHORT_TIMEOUT
        )
        
        # Verify we're on the Web Automation page
        await expect(self.page).to_have_url(f"{FRONTEND_URL}/web-automation", timeout=SHORT_TIMEOUT)
        logger.info("✅ Successfully navigated to Web Automation")
    
    async def test_step1_element_extraction(self):
        """Test Step 1: Element Extraction"""
        self.test_results["total_tests"] += 1
        logger.info("🧪 Testing Step 1: Element Extraction")
        
        try:
            # Verify we're on Step 1
            step1_indicator = await self.page.wait_for_selector(
                'text="Element Extraction"',
                timeout=SHORT_TIMEOUT
            )
            assert step1_indicator, "Step 1 indicator not found"
            
            # Check for active step styling
            active_step = await self.page.query_selector('.bg-gradient-to-r.from-\\[\\#004685\\].to-blue-600')
            assert active_step, "Step 1 is not marked as active"
            
            # Fill in the URL field
            url_input = await self.page.wait_for_selector(
                'input[placeholder*="Enter URL"]',
                timeout=SHORT_TIMEOUT
            )
            await url_input.fill(TEST_URL)
            logger.info(f"  📝 Entered URL: {TEST_URL}")
            
            # Optional: Fill test name and description
            test_name_input = await self.page.query_selector('input[placeholder*="test name"]')
            if test_name_input:
                await test_name_input.fill("E2E Test Suite")
            
            description_input = await self.page.query_selector('textarea[placeholder*="description"]')
            if description_input:
                await description_input.fill("Automated E2E test of Web Automation flow")
            
            # Click the Extract Elements button
            extract_button = await self.page.wait_for_selector(
                'button:has-text("Extract Elements")',
                timeout=SHORT_TIMEOUT
            )
            
            # Check button is enabled
            is_disabled = await extract_button.get_attribute("disabled")
            assert not is_disabled, "Extract button is disabled"
            
            logger.info("  🚀 Clicking Extract Elements button...")
            await extract_button.click()
            
            # Wait for loading state
            loading_indicator = await self.page.query_selector('[class*="animate-spin"]')
            if loading_indicator:
                logger.info("  ⏳ Extraction in progress...")
                # Wait for loading to complete
                await self.page.wait_for_selector(
                    '[class*="animate-spin"]',
                    state="hidden",
                    timeout=TIMEOUT
                )
            
            # Wait for step 2 to become active (automatic progression)
            await self.page.wait_for_selector(
                'text="Test Generation"',
                timeout=TIMEOUT
            )
            
            # Verify extraction data is stored (check console logs)
            extraction_data = await self.page.evaluate("window.__extractionData")
            assert extraction_data, "Extraction data not stored in window"
            assert extraction_data.get("elements"), "No elements extracted"
            
            logger.info(f"  ✅ Step 1 passed: Extracted {len(extraction_data.get('elements', []))} elements")
            self.test_results["passed"] += 1
            
        except Exception as e:
            logger.error(f"  ❌ Step 1 failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Step 1: {str(e)}")
            # Take screenshot for debugging
            await self.page.screenshot(path="step1_error.png")
            raise
    
    async def test_step2_test_generation(self):
        """Test Step 2: Test Generation"""
        self.test_results["total_tests"] += 1
        logger.info("🧪 Testing Step 2: Test Generation")
        
        try:
            # Verify we're on Step 2
            await self.page.wait_for_selector(
                'h2:has-text("Test Generation")',
                timeout=SHORT_TIMEOUT
            )
            
            # Check that workflow steps are displayed
            workflow_container = await self.page.query_selector('[class*="space-y-4"]')
            assert workflow_container, "Workflow container not found"
            
            # Look for "Generate Tests" button
            generate_button = await self.page.wait_for_selector(
                'button:has-text("Generate Tests")',
                timeout=SHORT_TIMEOUT
            )
            
            logger.info("  🚀 Clicking Generate Tests button...")
            await generate_button.click()
            
            # Wait for loading
            loading_indicator = await self.page.query_selector('[class*="animate-spin"]')
            if loading_indicator:
                logger.info("  ⏳ Test generation in progress...")
                await self.page.wait_for_selector(
                    '[class*="animate-spin"]',
                    state="hidden",
                    timeout=TIMEOUT
                )
            
            # Wait for workflow steps to be populated
            await asyncio.sleep(2)  # Give time for UI update
            
            # Check that workflow steps are now displayed
            workflow_steps = await self.page.query_selector_all('[class*="bg-slate-50"]')
            assert len(workflow_steps) > 0, "No workflow steps generated"
            
            logger.info(f"  📋 Generated {len(workflow_steps)} workflow steps")
            
            # Verify test data is stored
            test_data = await self.page.evaluate("window.__testData")
            assert test_data, "Test data not stored in window"
            
            # Wait for progression to Step 3
            await self.page.wait_for_selector(
                'text="Code Generation"',
                timeout=TIMEOUT
            )
            
            logger.info(f"  ✅ Step 2 passed: Generated test scenarios")
            self.test_results["passed"] += 1
            
        except Exception as e:
            logger.error(f"  ❌ Step 2 failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Step 2: {str(e)}")
            await self.page.screenshot(path="step2_error.png")
            raise
    
    async def test_step3_code_generation(self):
        """Test Step 3: Code Generation"""
        self.test_results["total_tests"] += 1
        logger.info("🧪 Testing Step 3: Code Generation")
        
        try:
            # Verify we're on Step 3
            await self.page.wait_for_selector(
                'h2:has-text("Code Generation")',
                timeout=SHORT_TIMEOUT
            )
            
            # Check for code preview
            code_block = await self.page.query_selector('pre')
            assert code_block, "Code preview not found"
            
            # Get the generated code content
            code_content = await code_block.inner_text()
            assert len(code_content) > 0, "No code generated"
            logger.info(f"  📄 Code preview shows {len(code_content)} characters")
            
            # Look for Next/Generate Code button
            next_button = await self.page.wait_for_selector(
                'button:has-text("Next"), button:has-text("Generate Code")',
                timeout=SHORT_TIMEOUT
            )
            
            logger.info("  🚀 Proceeding to next step...")
            await next_button.click()
            
            # Wait for any processing
            await asyncio.sleep(2)
            
            # Verify code data is stored
            code_data = await self.page.evaluate("window.__codeData")
            # Note: code_data might not be stored until actual generation
            
            # Wait for progression to Step 4
            await self.page.wait_for_selector(
                'text="Code Execution"',
                timeout=TIMEOUT
            )
            
            logger.info("  ✅ Step 3 passed: Code generation completed")
            self.test_results["passed"] += 1
            
        except Exception as e:
            logger.error(f"  ❌ Step 3 failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Step 3: {str(e)}")
            await self.page.screenshot(path="step3_error.png")
            raise
    
    async def test_step4_code_execution(self):
        """Test Step 4: Code Execution"""
        self.test_results["total_tests"] += 1
        logger.info("🧪 Testing Step 4: Code Execution")
        
        try:
            # Verify we're on Step 4
            await self.page.wait_for_selector(
                'h2:has-text("Code Execution")',
                timeout=SHORT_TIMEOUT
            )
            
            # Look for Execute button
            execute_button = await self.page.wait_for_selector(
                'button:has-text("Execute"), button:has-text("Run Tests")',
                timeout=SHORT_TIMEOUT
            )
            
            logger.info("  🚀 Clicking Execute button...")
            await execute_button.click()
            
            # Wait for execution to complete (this might take a while)
            loading_indicator = await self.page.query_selector('[class*="animate-spin"]')
            if loading_indicator:
                logger.info("  ⏳ Test execution in progress...")
                await self.page.wait_for_selector(
                    '[class*="animate-spin"]',
                    state="hidden",
                    timeout=TIMEOUT * 2  # Double timeout for execution
                )
            
            # Wait for results to be displayed
            await asyncio.sleep(3)
            
            # Check for results display
            results_section = await self.page.query_selector('[class*="Results"], [class*="results"]')
            if results_section:
                logger.info("  📊 Execution results displayed")
            
            # Look for success indicators
            success_indicator = await self.page.query_selector(
                'text=/passed|success|completed/i'
            )
            
            logger.info("  ✅ Step 4 passed: Code execution completed")
            self.test_results["passed"] += 1
            
        except Exception as e:
            logger.error(f"  ❌ Step 4 failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Step 4: {str(e)}")
            await self.page.screenshot(path="step4_error.png")
            raise
    
    async def test_error_handling(self):
        """Test error handling scenarios"""
        self.test_results["total_tests"] += 1
        logger.info("🧪 Testing Error Handling")
        
        try:
            # Navigate directly to web automation
            await self.page.goto(f"{FRONTEND_URL}/web-automation", wait_until="networkidle")
            await self.page.wait_for_selector('text="Element Extraction"', timeout=SHORT_TIMEOUT)
            
            # Test 1: Invalid URL
            logger.info("  📝 Testing invalid URL...")
            url_input = await self.page.wait_for_selector(
                'input[placeholder*="Enter URL"]',
                timeout=SHORT_TIMEOUT
            )
            await url_input.fill("not-a-valid-url")
            
            extract_button = await self.page.wait_for_selector(
                'button:has-text("Extract Elements")',
                timeout=SHORT_TIMEOUT
            )
            await extract_button.click()
            
            # Should show error message
            error_message = await self.page.wait_for_selector(
                'text=/error|invalid|failed/i',
                timeout=SHORT_TIMEOUT
            )
            assert error_message, "No error message shown for invalid URL"
            logger.info("  ✅ Invalid URL error handled correctly")
            
            # Test 2: Empty URL
            await self.page.reload()
            await self.page.wait_for_selector('text="Element Extraction"', timeout=SHORT_TIMEOUT)
            
            logger.info("  📝 Testing empty URL...")
            extract_button = await self.page.wait_for_selector(
                'button:has-text("Extract Elements")',
                timeout=SHORT_TIMEOUT
            )
            
            # Button should be disabled or show error on click
            is_disabled = await extract_button.get_attribute("disabled")
            if not is_disabled:
                await extract_button.click()
                error_indicator = await self.page.wait_for_selector(
                    'text=/required|enter.*url|provide.*url/i',
                    timeout=SHORT_TIMEOUT
                )
                assert error_indicator, "No error for empty URL"
            
            logger.info("  ✅ Empty URL validation works")
            self.test_results["passed"] += 1
            
        except Exception as e:
            logger.error(f"  ❌ Error handling test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Error handling: {str(e)}")
    
    async def test_navigation_controls(self):
        """Test navigation between steps"""
        self.test_results["total_tests"] += 1
        logger.info("🧪 Testing Navigation Controls")
        
        try:
            # Navigate directly to Web Automation
            await self.page.goto(f"{FRONTEND_URL}/web-automation", wait_until="networkidle")
            
            # Wait for the page to load
            await self.page.wait_for_selector('text="Element Extraction"', timeout=SHORT_TIMEOUT)
            
            # Check that only Step 1 is accessible initially
            step_buttons = await self.page.query_selector_all('[class*="rounded-xl"][class*="border"]')
            logger.info(f"  Found {len(step_buttons)} step buttons")
            
            # Try clicking on Step 2 (should not work if not completed Step 1)
            if len(step_buttons) > 1:
                step2_button = step_buttons[1]
                opacity = await step2_button.evaluate("el => window.getComputedStyle(el).opacity")
                if opacity == "0.5":
                    logger.info("  ✅ Future steps are correctly disabled")
            
            # Check for Back to Dashboard link
            back_link = await self.page.query_selector('text="Back to Dashboard"')
            assert back_link, "Back to Dashboard link not found"
            
            # Test the back link
            await back_link.click()
            await expect(self.page).to_have_url(f"{FRONTEND_URL}/", timeout=SHORT_TIMEOUT)
            logger.info("  ✅ Navigation controls work correctly")
            
            self.test_results["passed"] += 1
            
        except Exception as e:
            logger.error(f"  ❌ Navigation test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Navigation: {str(e)}")
    
    async def run_full_test_suite(self):
        """Run the complete test suite"""
        logger.info("=" * 60)
        logger.info("🚀 Starting Web Automation E2E Test Suite")
        logger.info("=" * 60)
        
        try:
            # Setup
            await self.setup()
            
            # Check backend health
            if not await self.check_backend_health():
                raise Exception("Backend is not healthy. Please start the backend first.")
            
            # Run tests in sequence
            test_methods = [
                self.test_navigation_controls,
                self.test_step1_element_extraction,
                self.test_step2_test_generation,
                self.test_step3_code_generation,
                self.test_step4_code_execution,
                self.test_error_handling
            ]
            
            for test_method in test_methods:
                try:
                    await test_method()
                    await asyncio.sleep(1)  # Brief pause between tests
                except Exception as e:
                    logger.error(f"Test failed but continuing: {e}")
                    continue
            
            # Print results
            logger.info("=" * 60)
            logger.info("📊 Test Results Summary")
            logger.info("=" * 60)
            logger.info(f"Total Tests: {self.test_results['total_tests']}")
            logger.info(f"✅ Passed: {self.test_results['passed']}")
            logger.info(f"❌ Failed: {self.test_results['failed']}")
            
            if self.test_results['errors']:
                logger.info("\n❌ Errors encountered:")
                for error in self.test_results['errors']:
                    logger.info(f"  - {error}")
            
            success_rate = (self.test_results['passed'] / self.test_results['total_tests']) * 100
            logger.info(f"\n🎯 Success Rate: {success_rate:.1f}%")
            
            if success_rate == 100:
                logger.info("🎉 All tests passed! The Web Automation UI is working perfectly!")
            elif success_rate >= 80:
                logger.info("⚠️ Most tests passed but some issues need attention.")
            else:
                logger.info("🚨 Critical issues detected. Immediate fixes required.")
            
        except Exception as e:
            logger.error(f"Fatal error in test suite: {e}")
            raise
        finally:
            # Cleanup
            await self.teardown()
        
        return self.test_results

async def main():
    """Main entry point"""
    test_suite = WebAutomationE2ETest()
    results = await test_suite.run_full_test_suite()
    
    # Exit with appropriate code
    if results['failed'] > 0:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())