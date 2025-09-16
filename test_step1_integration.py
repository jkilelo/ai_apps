"""
Test Step 1: Element Extraction Integration
Tests frontend-backend sync for element extraction step
"""
import asyncio
from playwright.async_api import async_playwright

async def test_step1_integration():
    """Test the element extraction step integration"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            print("=== Testing Step 1: Element Extraction Integration ===")

            # Navigate to React app
            await page.goto('http://localhost:3001/web-automation')
            await page.wait_for_load_state('networkidle')
            print("SUCCESS: Navigated to Web Automation flow")

            # Take initial screenshot
            await page.screenshot(path='qa_screenshots/step1_initial.png')
            print("SUCCESS: Initial screenshot saved")

            # Find and fill URL input
            url_input = page.locator('input').first
            await url_input.clear()
            await url_input.fill('https://httpbin.org/forms/post')
            print("SUCCESS: Entered test URL: https://httpbin.org/forms/post")

            # Take screenshot before clicking
            await page.screenshot(path='qa_screenshots/step1_url_entered.png')
            print("SUCCESS: URL entered screenshot saved")

            # Click Extract Elements button
            extract_button = page.locator('button:has-text("Extract Elements")').first
            await extract_button.click()
            print("SUCCESS: Clicked Extract Elements button")

            # Wait and monitor for response (up to 90 seconds)
            print("WAITING: Element extraction may take up to 90 seconds...")

            # Take screenshot showing loading state
            await page.wait_for_timeout(2000)
            await page.screenshot(path='qa_screenshots/step1_loading.png')
            print("SUCCESS: Loading state screenshot saved")

            # Wait for either success or failure
            try:
                # Wait for the loading to complete - either button text changes or step advances
                await page.wait_for_function(
                    """() => {
                        const button = document.querySelector('button:has-text("Extracting Elements")');
                        return !button || !button.textContent.includes('Extracting Elements');
                    }""",
                    timeout=90000  # 90 seconds
                )

                # Take screenshot after extraction completes
                await page.screenshot(path='qa_screenshots/step1_completed.png')
                print("SUCCESS: Element extraction completed!")

                # Check if we advanced to step 2
                step2_indicator = page.locator('text=Step 2 of 4')
                if await step2_indicator.count() > 0:
                    print("SUCCESS: Advanced to Step 2 - Element extraction worked!")

                    # Check if elements are displayed
                    elements_found = page.locator('[data-testid="extracted-elements"], .element-item, .element-list')
                    element_count = await elements_found.count()
                    if element_count > 0:
                        print(f"SUCCESS: Found {element_count} extracted elements in UI")
                    else:
                        print("WARNING: No elements displayed in UI")

                else:
                    print("ERROR: Did not advance to Step 2")

                    # Check for error messages
                    error_msg = page.locator('.error, [role="alert"], .text-red')
                    if await error_msg.count() > 0:
                        error_text = await error_msg.first.text_content()
                        print(f"ERROR: {error_text}")

            except Exception as wait_error:
                print("ERROR: Element extraction took longer than 90 seconds or failed")
                await page.screenshot(path='qa_screenshots/step1_timeout.png')
                print("SUCCESS: Timeout screenshot saved")

        except Exception as e:
            print(f"ERROR: Test failed: {e}")
            await page.screenshot(path='qa_screenshots/step1_error.png')

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_step1_integration())