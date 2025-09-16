"""
Test frontend with console logging to find JavaScript errors
"""
import asyncio
from playwright.async_api import async_playwright

async def test_with_console():
    """Test frontend and capture console logs"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Listen for console messages
        def handle_console_msg(msg):
            print(f"CONSOLE: {msg.type}: {msg.text}")

        def handle_page_error(error):
            print(f"PAGE ERROR: {error}")

        page.on("console", handle_console_msg)
        page.on("pageerror", handle_page_error)

        try:
            print("=== Testing Frontend with Console Monitoring ===")

            # Navigate to React app
            await page.goto('http://localhost:3001/web-automation')
            await page.wait_for_load_state('networkidle')
            print("SUCCESS: Navigated to Web Automation flow")

            # Monitor network requests
            def handle_request(request):
                if 'api/web-automation' in request.url:
                    print(f"REQUEST: {request.method} {request.url}")

            def handle_response(response):
                if 'api/web-automation' in response.url:
                    print(f"RESPONSE: {response.status} {response.url}")

            page.on("request", handle_request)
            page.on("response", handle_response)

            # Fill URL and click extract
            url_input = page.locator('input').first
            await url_input.clear()
            await url_input.fill('https://httpbin.org/forms/post')
            print("SUCCESS: Entered test URL")

            extract_button = page.locator('button:has-text("Extract Elements")').first
            await extract_button.click()
            print("SUCCESS: Clicked Extract Elements button")

            # Wait and monitor for 20 seconds
            print("MONITORING: Waiting 20 seconds for completion...")
            await page.wait_for_timeout(20000)

            # Take final screenshot
            await page.screenshot(path='qa_screenshots/console_test_final.png')
            print("SUCCESS: Final screenshot saved")

        except Exception as e:
            print(f"ERROR: Test failed: {e}")
            await page.screenshot(path='qa_screenshots/console_test_error.png')

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_with_console())