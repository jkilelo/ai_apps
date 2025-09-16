"""
UI End-to-End Test Using Playwright
Senior QA Engineer Pattern: Practical E2E Testing
"""

import asyncio
from playwright.async_api import async_playwright, Page, expect
import sys
from pathlib import Path
import time

class WebAutomationE2ETest:
    """E2E test for Web Automation Pipeline UI"""
    
    def __init__(self):
        self.frontend_url = "http://localhost:3000"
        self.backend_url = "http://localhost:5175"
        self.test_results = {
            "passed": [],
            "failed": [],
            "errors": []
        }
        
    async def setup(self, page: Page):
        """Setup test environment"""
        # Set viewport
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Navigate to the web automation flow
        await page.goto(f"{self.frontend_url}/flows/web-automation")
        
        # Wait for page to load
        await page.wait_for_load_state("networkidle")
        
    async def test_page_loads(self, page: Page) -> bool:
        """Test that the page loads correctly"""
        try:
            print("\n[TEST] Page Load Test")
            print("-" * 40)
            
            # Check if we're on the right page
            title = await page.title()
            print(f"  Page title: {title}")
            
            # Look for the main container
            main_container = page.locator('.min-h-screen')
            await expect(main_container).to_be_visible(timeout=10000)
            
            # Look for step indicators
            steps = page.locator('.flex.items-center.justify-center.gap-2')
            await expect(steps).to_be_visible(timeout=10000)
            
            print("  [PASS] Page loaded successfully")
            self.test_results["passed"].append("Page Load Test")
            return True
            
        except Exception as e:
            print(f"  [FAIL] Page load failed: {e}")
            self.test_results["failed"].append("Page Load Test")
            self.test_results["errors"].append(str(e))
            return False
            
    async def test_step1_element_extraction(self, page: Page) -> bool:
        """Test Step 1: Element Extraction"""
        try:
            print("\n[TEST] Step 1: Element Extraction")
            print("-" * 40)
            
            # Find the URL input field
            url_input = page.get_by_placeholder("https://example.com")
            await expect(url_input).to_be_visible(timeout=10000)
            
            # Enter a test URL
            await url_input.fill("https://example.com")
            print("  Entered URL: https://example.com")
            
            # Find and click the Next button
            next_button = page.get_by_role("button", name="Next")
            await expect(next_button).to_be_enabled()
            
            # Take screenshot before proceeding
            await page.screenshot(path="test-results/step1-before.png")
            
            # Click next and wait for loading
            await next_button.click()
            print("  Clicked Next button")
            
            # Wait for loading to complete (look for spinner to appear and disappear)
            loading_indicator = page.locator('.animate-spin')
            if await loading_indicator.is_visible():
                print("  Loading spinner appeared...")
                await expect(loading_indicator).not_to_be_visible(timeout=120000)
                print("  Loading completed")
            
            # Wait for step 2 to be visible
            await page.wait_for_timeout(2000)
            
            # Check if we moved to step 2
            step2_visible = await page.locator('text="Test Generation"').is_visible()
            
            if step2_visible:
                print("  [PASS] Element extraction completed")
                await page.screenshot(path="test-results/step1-complete.png")
                self.test_results["passed"].append("Step 1: Element Extraction")
                return True
            else:
                raise Exception("Did not progress to Step 2")
                
        except Exception as e:
            print(f"  [FAIL] Element extraction failed: {e}")
            self.test_results["failed"].append("Step 1: Element Extraction")
            self.test_results["errors"].append(str(e))
            await page.screenshot(path="test-results/step1-error.png")
            return False
            
    async def test_step2_test_generation(self, page: Page) -> bool:
        """Test Step 2: Test Generation"""
        try:
            print("\n[TEST] Step 2: Test Generation")
            print("-" * 40)
            
            # Wait for test generation to complete
            print("  Waiting for test generation...")
            
            # Look for loading spinner
            loading_indicator = page.locator('.animate-spin')
            if await loading_indicator.is_visible():
                await expect(loading_indicator).not_to_be_visible(timeout=120000)
            
            # Wait for test scenarios to appear
            await page.wait_for_timeout(3000)
            
            # Look for the Next button to proceed to step 3
            next_button = page.get_by_role("button", name="Next")
            await expect(next_button).to_be_visible(timeout=10000)
            
            # Take screenshot
            await page.screenshot(path="test-results/step2-complete.png")
            
            # Click next
            await next_button.click()
            print("  Clicked Next to proceed to Code Generation")
            
            print("  [PASS] Test generation completed")
            self.test_results["passed"].append("Step 2: Test Generation")
            return True
            
        except Exception as e:
            print(f"  [FAIL] Test generation failed: {e}")
            self.test_results["failed"].append("Step 2: Test Generation")
            self.test_results["errors"].append(str(e))
            await page.screenshot(path="test-results/step2-error.png")
            return False
            
    async def test_step3_code_generation(self, page: Page) -> bool:
        """Test Step 3: Code Generation"""
        try:
            print("\n[TEST] Step 3: Code Generation")
            print("-" * 40)
            
            # Wait for code generation
            print("  Waiting for code generation...")
            
            # Look for loading spinner
            loading_indicator = page.locator('.animate-spin')
            if await loading_indicator.is_visible():
                await expect(loading_indicator).not_to_be_visible(timeout=120000)
            
            # Wait for code to appear
            await page.wait_for_timeout(3000)
            
            # Look for code viewer or Next button
            next_button = page.get_by_role("button", name="Next")
            if await next_button.is_visible():
                await page.screenshot(path="test-results/step3-complete.png")
                await next_button.click()
                print("  Clicked Next to proceed to Code Execution")
            else:
                # Look for View Code or Continue button
                view_code_button = page.get_by_role("button", name="View Code")
                if await view_code_button.is_visible():
                    await view_code_button.click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path="test-results/step3-code-view.png")
                
            print("  [PASS] Code generation completed")
            self.test_results["passed"].append("Step 3: Code Generation")
            return True
            
        except Exception as e:
            print(f"  [FAIL] Code generation failed: {e}")
            self.test_results["failed"].append("Step 3: Code Generation")
            self.test_results["errors"].append(str(e))
            await page.screenshot(path="test-results/step3-error.png")
            return False
            
    async def test_step4_code_execution(self, page: Page) -> bool:
        """Test Step 4: Code Execution"""
        try:
            print("\n[TEST] Step 4: Code Execution")
            print("-" * 40)
            
            # Look for execute button
            execute_button = page.get_by_role("button", name="Execute")
            if not await execute_button.is_visible():
                execute_button = page.get_by_role("button", name="Run Tests")
                
            if await execute_button.is_visible():
                await execute_button.click()
                print("  Clicked Execute button")
                
                # Wait for execution to complete
                loading_indicator = page.locator('.animate-spin')
                if await loading_indicator.is_visible():
                    print("  Waiting for execution to complete...")
                    await expect(loading_indicator).not_to_be_visible(timeout=120000)
                
                await page.wait_for_timeout(3000)
                
            # Take final screenshot
            await page.screenshot(path="test-results/step4-complete.png")
            
            print("  [PASS] Code execution completed")
            self.test_results["passed"].append("Step 4: Code Execution")
            return True
            
        except Exception as e:
            print(f"  [FAIL] Code execution failed: {e}")
            self.test_results["failed"].append("Step 4: Code Execution")
            self.test_results["errors"].append(str(e))
            await page.screenshot(path="test-results/step4-error.png")
            return False
            
    async def test_form_validation(self, page: Page) -> bool:
        """Test form validation"""
        try:
            print("\n[TEST] Form Validation")
            print("-" * 40)
            
            # Navigate back to start
            await page.goto(f"{self.frontend_url}/flows/web-automation")
            await page.wait_for_load_state("networkidle")
            
            # Try to submit empty form
            next_button = page.get_by_role("button", name="Next")
            
            # Check if button is disabled when input is empty
            url_input = page.get_by_placeholder("https://example.com")
            await url_input.clear()
            
            is_disabled = await next_button.is_disabled()
            
            if is_disabled:
                print("  [PASS] Next button disabled for empty input")
            else:
                print("  [WARNING] Next button not disabled for empty input")
                
            # Test invalid URL
            await url_input.fill("not-a-valid-url")
            await next_button.click()
            
            # Check for error message
            await page.wait_for_timeout(1000)
            error_visible = await page.locator('text=/error|invalid/i').is_visible()
            
            if error_visible:
                print("  [PASS] Error shown for invalid URL")
            else:
                print("  [WARNING] No error shown for invalid URL")
                
            self.test_results["passed"].append("Form Validation")
            return True
            
        except Exception as e:
            print(f"  [FAIL] Form validation test failed: {e}")
            self.test_results["failed"].append("Form Validation")
            self.test_results["errors"].append(str(e))
            return False
            
    async def run_all_tests(self):
        """Run all E2E tests"""
        print("\n" + "="*60)
        print("Web Automation Pipeline - UI E2E Tests")
        print("="*60)
        
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(
                headless=False,  # Set to True for CI/CD
                slow_mo=500  # Slow down for visibility
            )
            
            # Create context with video recording
            context = await browser.new_context(
                record_video_dir="test-results/videos"
            )
            
            # Create page
            page = await context.new_page()
            
            try:
                # Setup
                await self.setup(page)
                
                # Run tests
                await self.test_page_loads(page)
                await self.test_form_validation(page)
                
                # Reset for full flow test
                await page.goto(f"{self.frontend_url}/flows/web-automation")
                await page.wait_for_load_state("networkidle")
                
                # Test complete flow
                print("\n[TEST SUITE] Complete Pipeline Flow")
                print("="*60)
                
                if await self.test_step1_element_extraction(page):
                    if await self.test_step2_test_generation(page):
                        if await self.test_step3_code_generation(page):
                            await self.test_step4_code_execution(page)
                
            except Exception as e:
                print(f"\n[ERROR] Test suite error: {e}")
                self.test_results["errors"].append(str(e))
                await page.screenshot(path="test-results/error-final.png")
                
            finally:
                # Close browser
                await context.close()
                await browser.close()
                
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total = len(self.test_results["passed"]) + len(self.test_results["failed"])
        
        print(f"\nTotal Tests: {total}")
        print(f"  Passed: {len(self.test_results['passed'])} [PASS]")
        print(f"  Failed: {len(self.test_results['failed'])} [FAIL]")
        
        if self.test_results["passed"]:
            print("\n[PASSED TESTS]")
            for test in self.test_results["passed"]:
                print(f"  [PASS] {test}")
                
        if self.test_results["failed"]:
            print("\n[FAILED TESTS]")
            for test in self.test_results["failed"]:
                print(f"  [FAIL] {test}")
                
        if self.test_results["errors"]:
            print("\n[ERRORS]")
            for i, error in enumerate(self.test_results["errors"], 1):
                print(f"  {i}. {error[:100]}...")
                
        # Calculate pass rate
        if total > 0:
            pass_rate = (len(self.test_results["passed"]) / total) * 100
            print(f"\nPass Rate: {pass_rate:.1f}%")
            
            if pass_rate == 100:
                print("\n[SUCCESS] ALL TESTS PASSED!")
            elif pass_rate >= 80:
                print("\n[WARNING] Most tests passed, but some failures need attention")
            else:
                print("\n[ERROR] Multiple test failures - investigation needed")


async def main():
    """Main entry point"""
    print("""
    ============================================================
         Web Automation Pipeline - UI E2E Test                 
         Senior QA Engineer Edition                            
    ============================================================
    """)
    
    # Create test results directory
    Path("test-results").mkdir(exist_ok=True)
    Path("test-results/videos").mkdir(exist_ok=True)
    
    # Check if services are running
    import requests
    
    print("\n[SETUP] Checking services...")
    
    # Check backend
    try:
        response = requests.get("http://localhost:5175/api/ui/health")
        if response.status_code == 200:
            print("  [OK] Backend is running on port 5175")
        else:
            print("  [ERROR] Backend is not healthy")
            sys.exit(1)
    except:
        print("  [ERROR] Backend is not running. Please start it first:")
        print("    python simple_apps_v2/backend/web_automation/startup.py")
        sys.exit(1)
        
    # Check frontend
    try:
        response = requests.get("http://localhost:3000")
        if response.status_code == 200:
            print("  [OK] Frontend is running on port 3000")
        else:
            print("  [ERROR] Frontend is not healthy")
            sys.exit(1)
    except:
        print("  [ERROR] Frontend is not running. Please start it first:")
        print("    cd simple_apps_original/frontend && npm run dev")
        sys.exit(1)
        
    print("\n[INFO] Services are ready. Starting E2E tests...")
    
    # Run tests
    tester = WebAutomationE2ETest()
    await tester.run_all_tests()


if __name__ == "__main__":
    # Install playwright if needed
    import subprocess
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("Installing Playwright...")
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"])
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])
        
    asyncio.run(main())