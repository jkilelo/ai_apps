"""
QA Testing Script for React Web Automation UI
Tests the WebAutomationFlowSimplified.tsx component thoroughly
"""
import asyncio
from playwright.async_api import async_playwright
import time

async def test_react_ui():
    async with async_playwright() as p:
        # Launch browser with visible UI
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context(viewport={'width': 1200, 'height': 800})
        page = await context.new_page()

        try:
            print("=== QA Test 1: Home Page ===")
            # Navigate to React app
            await page.goto('http://localhost:3001')
            await page.wait_for_load_state('networkidle')
            await page.screenshot(path='qa_screenshots/01_home_page.png')
            print("SUCCESS: Screenshot saved: 01_home_page.png")

            print("\n=== QA Test 2: Navigate to Web Automation ===")
            # Look for Web Automation link/button
            web_automation_selector = 'a[href*="web-automation"], button:has-text("Web Automation"), [data-testid*="web-automation"]'

            try:
                await page.wait_for_selector('text=Web Automation', timeout=5000)
                await page.click('text=Web Automation')
                print("SUCCESS: Clicked Web Automation link")
            except:
                # Try alternative selectors
                try:
                    await page.click('a[href="/flows/web-automation"]')
                    print("SUCCESS: Clicked Web Automation flow link")
                except:
                    print("ERROR: Could not find Web Automation navigation")
                    # Take screenshot of current state
                    await page.screenshot(path='qa_screenshots/02_navigation_issue.png')
                    return

            await page.wait_for_load_state('networkidle')
            await page.screenshot(path='qa_screenshots/02_web_automation_flow.png')
            print("SUCCESS: Screenshot saved: 02_web_automation_flow.png")

            print("\n=== QA Test 3: URL Input and Element Extraction ===")
            # Find URL input field - based on the UI screenshot, it shows "https://example.com"
            url_input = page.locator('input[placeholder*="example.com"], input[value*="example.com"], input').first
            await url_input.clear()
            await url_input.fill('https://httpbin.org/forms/post')
            print("SUCCESS: Entered test URL")

            # Find and click extract button - based on UI, it's "Extract Elements"
            extract_button = page.locator('button:has-text("Extract Elements"), button:has-text("Extract")').first
            await extract_button.click()
            print("SUCCESS: Clicked extract button")

            # Wait for extraction to complete
            await page.wait_for_timeout(3000)
            await page.screenshot(path='qa_screenshots/03_element_extraction.png')
            print("SUCCESS: Screenshot saved: 03_element_extraction.png")

            print("\n=== QA Test 4: Test Generation ===")
            # Look for next step or generate tests button
            try:
                next_button = page.locator('button:has-text("Generate Tests"), button:has-text("Next"), button:has-text("Continue")').first
                await next_button.click()
                print("SUCCESS: Clicked generate tests button")

                await page.wait_for_timeout(2000)
                await page.screenshot(path='qa_screenshots/04_test_generation.png')
                print("SUCCESS: Screenshot saved: 04_test_generation.png")
            except:
                print("WARNING: Test generation step not found or not ready")
                await page.screenshot(path='qa_screenshots/04_test_generation_issue.png')

            print("\n=== QA Test 5: Code Generation ===")
            try:
                code_button = page.locator('button:has-text("Generate Code"), button:has-text("Code"), button:has-text("Next")').first
                await code_button.click()
                print("SUCCESS: Clicked generate code button")

                await page.wait_for_timeout(2000)
                await page.screenshot(path='qa_screenshots/05_code_generation.png')
                print("SUCCESS: Screenshot saved: 05_code_generation.png")
            except:
                print("WARNING: Code generation step not found or not ready")
                await page.screenshot(path='qa_screenshots/05_code_generation_issue.png')

            print("\n=== QA Test 6: Error Handling ===")
            # Test with invalid URL
            try:
                # Go back to start or refresh
                await page.reload()
                await page.wait_for_load_state('networkidle')

                url_input = page.locator('input[type="text"], input[placeholder*="URL"]').first
                await url_input.fill('invalid-url-test')

                extract_button = page.locator('button:has-text("Extract"), button:has-text("Analyze")').first
                await extract_button.click()

                await page.wait_for_timeout(2000)
                await page.screenshot(path='qa_screenshots/06_error_handling.png')
                print("SUCCESS: Screenshot saved: 06_error_handling.png")
            except:
                print("WARNING: Error handling test could not be completed")

            print("\n=== QA Test Results Summary ===")
            print("All screenshots saved to qa_screenshots/ directory")
            print("Check screenshots for visual verification of UI functionality")

        except Exception as e:
            print(f"ERROR: QA Test failed: {e}")
            await page.screenshot(path='qa_screenshots/error_state.png')

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_react_ui())