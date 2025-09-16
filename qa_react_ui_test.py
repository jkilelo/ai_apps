"""
Comprehensive QA Testing for React Web Automation UI
Testing the React app at http://localhost:3002 with detailed screenshots and verification
"""

import asyncio
import os
import time
from datetime import datetime
from playwright.async_api import async_playwright, expect
import json

class ReactUIQATester:
    def __init__(self):
        self.base_url = "http://localhost:3002"
        self.screenshot_dir = "C:\\Users\\kleiy\\OneDrive\\Desktop\\python-ai-apps\\ai_apps\\qa_screenshots"
        self.test_results = []

    async def setup(self):
        """Initialize Playwright and create screenshot directory"""
        # Create screenshots directory
        os.makedirs(self.screenshot_dir, exist_ok=True)

        # Launch browser with slow motion for better visibility
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Run in headed mode to see what's happening
            slow_mo=1000     # Slow down actions for better observation
        )

        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            record_video_dir=self.screenshot_dir
        )

        self.page = await self.context.new_page()

        # Set up console logging
        self.page.on("console", lambda msg: print(f"Console: {msg.text}"))
        self.page.on("pageerror", lambda exc: print(f"Page Error: {exc}"))

    async def cleanup(self):
        """Clean up browser resources"""
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()

    async def take_screenshot(self, name, description=""):
        """Take a screenshot with timestamp and description"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(self.screenshot_dir, filename)

        await self.page.screenshot(path=filepath, full_page=True)

        result = {
            "step": name,
            "description": description,
            "screenshot": filepath,
            "timestamp": timestamp,
            "url": self.page.url,
            "status": "success"
        }

        self.test_results.append(result)
        print(f"[SUCCESS] Screenshot saved: {filename} - {description}")
        return filepath

    async def log_error(self, step, error, description=""):
        """Log test errors"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result = {
            "step": step,
            "description": description,
            "error": str(error),
            "timestamp": timestamp,
            "url": self.page.url if hasattr(self, 'page') else "N/A",
            "status": "error"
        }
        self.test_results.append(result)
        print(f"[ERROR] Error in {step}: {error}")

    async def wait_for_stability(self, timeout=10000):
        """Wait for page to be stable (no network activity)"""
        try:
            await self.page.wait_for_load_state('networkidle', timeout=timeout)
            await self.page.wait_for_load_state('domcontentloaded')
            # Additional wait for any dynamic content
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Warning: Page stability wait failed: {e}")

    async def test_step1_homepage(self):
        """Step 1: Navigate to homepage and take screenshot"""
        try:
            print("\\n[STEP 1] Testing React homepage...")

            # Navigate to the React app
            await self.page.goto(self.base_url, wait_until='networkidle')
            await self.wait_for_stability()

            # Take screenshot of homepage
            await self.take_screenshot("step1_homepage", "React app homepage loaded")

            # Verify page title and basic elements
            title = await self.page.title()
            print(f"Page title: {title}")

            # Check if React app loaded successfully
            react_root = self.page.locator("#root")
            await expect(react_root).to_be_visible()

            print("[SUCCESS] Step 1: Homepage test completed successfully")
            return True

        except Exception as e:
            await self.log_error("step1_homepage", e, "Failed to load homepage")
            return False

    async def test_step2_navigation(self):
        """Step 2: Navigate to Web Automation flow"""
        try:
            print("\\n🔍 Step 2: Testing navigation to Web Automation flow...")

            # Look for navigation elements - try multiple possible selectors
            nav_selectors = [
                "text=Web Automation",
                "[data-testid='web-automation']",
                "a[href*='web-automation']",
                "button:has-text('Web Automation')",
                ".nav-item:has-text('Web Automation')",
                "[role='menuitem']:has-text('Web Automation')"
            ]

            nav_element = None
            for selector in nav_selectors:
                try:
                    nav_element = self.page.locator(selector).first
                    if await nav_element.is_visible(timeout=2000):
                        print(f"Found navigation element with selector: {selector}")
                        break
                except:
                    continue

            if not nav_element or not await nav_element.is_visible():
                # If no specific navigation found, look for any clickable elements
                print("No specific Web Automation nav found, looking for general navigation...")

                # Check for any buttons or links that might lead to web automation
                possible_elements = await self.page.locator("button, a, [role='button']").all()

                for element in possible_elements:
                    text = await element.text_content()
                    if text and any(keyword in text.lower() for keyword in ['web', 'automation', 'test', 'extract']):
                        nav_element = element
                        print(f"Found potential navigation element: {text}")
                        break

            if nav_element and await nav_element.is_visible():
                await nav_element.click()
                await self.wait_for_stability()
                await self.take_screenshot("step2_navigation", "Navigated to Web Automation flow")
                print("✅ Step 2: Navigation test completed successfully")
                return True
            else:
                # Take screenshot of current state for debugging
                await self.take_screenshot("step2_navigation_failed", "Could not find Web Automation navigation")
                print("⚠️ Could not find Web Automation navigation, continuing with current page")
                return False

        except Exception as e:
            await self.log_error("step2_navigation", e, "Failed to navigate to Web Automation flow")
            await self.take_screenshot("step2_navigation_error", f"Navigation error: {str(e)}")
            return False

    async def test_step3_url_entry(self):
        """Step 3: Test URL entry and element extraction"""
        try:
            print("\\n🔍 Step 3: Testing URL entry and element extraction...")

            # Look for URL input field
            url_selectors = [
                "input[type='url']",
                "input[placeholder*='url']",
                "input[placeholder*='URL']",
                "input[name='url']",
                "input[id*='url']",
                "[data-testid*='url']",
                "input[type='text']"  # Fallback to any text input
            ]

            url_input = None
            for selector in url_selectors:
                try:
                    url_input = self.page.locator(selector).first
                    if await url_input.is_visible(timeout=2000):
                        print(f"Found URL input with selector: {selector}")
                        break
                except:
                    continue

            if url_input and await url_input.is_visible():
                # Clear and enter the test URL
                await url_input.clear()
                await url_input.fill("https://httpbin.org/forms/post")
                await asyncio.sleep(1)

                await self.take_screenshot("step3_url_entered", "URL entered in input field")

                # Look for extract/submit button
                button_selectors = [
                    "button:has-text('Extract')",
                    "button:has-text('extract')",
                    "button:has-text('Analyze')",
                    "button:has-text('Submit')",
                    "[data-testid*='extract']",
                    "input[type='submit']",
                    "button[type='submit']"
                ]

                extract_button = None
                for selector in button_selectors:
                    try:
                        extract_button = self.page.locator(selector).first
                        if await extract_button.is_visible(timeout=2000) and await extract_button.is_enabled():
                            print(f"Found extract button with selector: {selector}")
                            break
                    except:
                        continue

                if extract_button:
                    await extract_button.click()
                    print("Clicked extract button, waiting for results...")

                    # Wait longer for element extraction to complete
                    await asyncio.sleep(5)
                    await self.wait_for_stability(timeout=15000)

                    await self.take_screenshot("step3_extraction_results", "Element extraction completed")
                    print("✅ Step 3: URL entry and extraction test completed")
                    return True
                else:
                    await self.take_screenshot("step3_no_extract_button", "Could not find extract button")
                    print("⚠️ Could not find extract button")
                    return False
            else:
                await self.take_screenshot("step3_no_url_input", "Could not find URL input field")
                print("⚠️ Could not find URL input field")
                return False

        except Exception as e:
            await self.log_error("step3_url_entry", e, "Failed to test URL entry and extraction")
            await self.take_screenshot("step3_error", f"URL entry error: {str(e)}")
            return False

    async def test_step4_extracted_elements(self):
        """Step 4: Verify extracted elements are displayed"""
        try:
            print("\\n🔍 Step 4: Verifying extracted elements display...")

            # Look for extracted elements display
            element_indicators = [
                ".element-list",
                ".extracted-elements",
                "[data-testid*='element']",
                ".element-item",
                "ul li",  # Generic list items
                ".results",
                ".element-results"
            ]

            elements_found = False
            for selector in element_indicators:
                try:
                    elements = self.page.locator(selector)
                    count = await elements.count()
                    if count > 0:
                        print(f"Found {count} elements with selector: {selector}")
                        elements_found = True
                        break
                except:
                    continue

            await self.take_screenshot("step4_extracted_elements", "Extracted elements display")

            if elements_found:
                print("✅ Step 4: Extracted elements verification completed")
                return True
            else:
                print("⚠️ No extracted elements found in display")
                return False

        except Exception as e:
            await self.log_error("step4_extracted_elements", e, "Failed to verify extracted elements")
            return False

    async def test_step5_generate_tests(self):
        """Step 5: Test Generate Tests functionality"""
        try:
            print("\\n🔍 Step 5: Testing Generate Tests functionality...")

            # Look for Generate Tests button
            test_button_selectors = [
                "button:has-text('Generate Tests')",
                "button:has-text('Generate Test')",
                "button:has-text('Create Tests')",
                "[data-testid*='generate-test']",
                "button:has-text('Test')"
            ]

            test_button = None
            for selector in test_button_selectors:
                try:
                    test_button = self.page.locator(selector).first
                    if await test_button.is_visible(timeout=2000) and await test_button.is_enabled():
                        print(f"Found Generate Tests button with selector: {selector}")
                        break
                except:
                    continue

            if test_button:
                await test_button.click()
                print("Clicked Generate Tests button, waiting for results...")

                # Wait for test generation to complete
                await asyncio.sleep(8)
                await self.wait_for_stability(timeout=20000)

                await self.take_screenshot("step5_generated_tests", "Generated tests display")
                print("✅ Step 5: Generate Tests completed")
                return True
            else:
                await self.take_screenshot("step5_no_test_button", "Could not find Generate Tests button")
                print("⚠️ Could not find Generate Tests button")
                return False

        except Exception as e:
            await self.log_error("step5_generate_tests", e, "Failed to test Generate Tests")
            return False

    async def test_step6_generate_code(self):
        """Step 6: Test Generate Code functionality"""
        try:
            print("\\n🔍 Step 6: Testing Generate Code functionality...")

            # Look for Generate Code button
            code_button_selectors = [
                "button:has-text('Generate Code')",
                "button:has-text('Create Code')",
                "button:has-text('Export Code')",
                "[data-testid*='generate-code']",
                "button:has-text('Code')"
            ]

            code_button = None
            for selector in code_button_selectors:
                try:
                    code_button = self.page.locator(selector).first
                    if await code_button.is_visible(timeout=2000) and await code_button.is_enabled():
                        print(f"Found Generate Code button with selector: {selector}")
                        break
                except:
                    continue

            if code_button:
                await code_button.click()
                print("Clicked Generate Code button, waiting for results...")

                # Wait for code generation to complete
                await asyncio.sleep(8)
                await self.wait_for_stability(timeout=20000)

                await self.take_screenshot("step6_generated_code", "Generated code display")
                print("✅ Step 6: Generate Code completed")
                return True
            else:
                await self.take_screenshot("step6_no_code_button", "Could not find Generate Code button")
                print("⚠️ Could not find Generate Code button")
                return False

        except Exception as e:
            await self.log_error("step6_generate_code", e, "Failed to test Generate Code")
            return False

    async def test_step7_error_scenarios(self):
        """Step 7: Test error scenarios"""
        try:
            print("\\n🔍 Step 7: Testing error scenarios...")

            # Test invalid URL
            url_input = self.page.locator("input[type='url'], input[placeholder*='url'], input[name='url']").first
            if await url_input.is_visible():
                await url_input.clear()
                await url_input.fill("invalid-url")

                extract_button = self.page.locator("button:has-text('Extract'), button:has-text('extract')").first
                if await extract_button.is_visible():
                    await extract_button.click()
                    await asyncio.sleep(3)

                    await self.take_screenshot("step7_invalid_url_error", "Testing invalid URL error handling")

            # Test network error scenario (non-existent domain)
            if await url_input.is_visible():
                await url_input.clear()
                await url_input.fill("https://this-domain-does-not-exist-12345.com")

                if await extract_button.is_visible():
                    await extract_button.click()
                    await asyncio.sleep(5)

                    await self.take_screenshot("step7_network_error", "Testing network error handling")

            print("✅ Step 7: Error scenarios testing completed")
            return True

        except Exception as e:
            await self.log_error("step7_error_scenarios", e, "Failed to test error scenarios")
            return False

    async def generate_report(self):
        """Generate comprehensive test report"""
        report_path = os.path.join(self.screenshot_dir, "qa_test_report.json")

        with open(report_path, 'w') as f:
            json.dump({
                "test_session": {
                    "timestamp": datetime.now().isoformat(),
                    "base_url": self.base_url,
                    "total_steps": len(self.test_results),
                    "successful_steps": len([r for r in self.test_results if r['status'] == 'success']),
                    "failed_steps": len([r for r in self.test_results if r['status'] == 'error'])
                },
                "results": self.test_results
            }, indent=2)

        print(f"\\n📊 Test report generated: {report_path}")
        return report_path

    async def run_full_qa_test(self):
        """Run the complete QA test suite"""
        print("🚀 Starting comprehensive React UI QA testing...")
        print(f"Testing application at: {self.base_url}")

        try:
            await self.setup()

            # Execute test steps in sequence
            await self.test_step1_homepage()
            await self.test_step2_navigation()
            await self.test_step3_url_entry()
            await self.test_step4_extracted_elements()
            await self.test_step5_generate_tests()
            await self.test_step6_generate_code()
            await self.test_step7_error_scenarios()

            # Generate final report
            report_path = await self.generate_report()

            print("\\n🎉 QA testing completed successfully!")
            print(f"Screenshots saved in: {self.screenshot_dir}")
            print(f"Test report: {report_path}")

            return True

        except Exception as e:
            print(f"\\n❌ QA testing failed: {e}")
            await self.log_error("full_test", e, "Complete test suite failed")
            return False

        finally:
            await self.cleanup()

async def main():
    """Main execution function"""
    tester = ReactUIQATester()
    await tester.run_full_qa_test()

if __name__ == "__main__":
    asyncio.run(main())