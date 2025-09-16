"""
QA Test with Console Error Logging
"""

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
from pathlib import Path

# Create screenshots directory
SCREENSHOT_DIR = Path("qa_screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)

async def test_with_console():
    """Test the flow and capture console errors"""

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        # Enable console message listening
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))

        # Listen for page errors
        page_errors = []
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        print("\n" + "="*80)
        print("TESTING WEB AUTOMATION FLOW WITH CONSOLE LOGGING")
        print("="*80)

        try:
            # Navigate to the app
            print("\n[1] Navigating to frontend...")
            await page.goto("http://localhost:3002")
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(2000)

            # Click Web Automation
            print("[2] Going to Web Automation...")
            await page.get_by_text("Web Automation").first.click()
            await page.wait_for_timeout(1000)

            # Enter URL
            print("[3] Entering URL...")
            await page.fill('input[type="url"], input[placeholder*="URL"], input[placeholder*="url"]', "https://example.com")
            await page.wait_for_timeout(500)

            # Click Extract Elements
            print("[4] Clicking Extract Elements...")

            # First, let's see what buttons are visible
            buttons = await page.locator('button').all_text_contents()
            print(f"    Available buttons: {buttons}")

            # Try to click the Extract button
            extract_btn = page.locator('button:has-text("Extract Elements")')
            if await extract_btn.count() > 0:
                await extract_btn.first.click()
            else:
                # Try alternative selector
                await page.locator('button').filter(has_text="Extract").first.click()

            print("[5] Waiting for response...")

            # Wait for either success or error
            await page.wait_for_timeout(10000)  # 10 seconds

            # Take screenshot
            await page.screenshot(path=f"qa_screenshots/console_test_final.png", full_page=True)

            # Check for any error messages on page
            error_elements = await page.locator('[class*="error"], [class*="Error"], [role="alert"]').all_text_contents()
            if error_elements:
                print(f"\n[ERROR] Error messages found on page: {error_elements}")

            # Print console messages
            if console_messages:
                print("\n[CONSOLE MESSAGES]:")
                for msg in console_messages:
                    print(f"  {msg}")

            # Print page errors
            if page_errors:
                print("\n[PAGE ERRORS]:")
                for err in page_errors:
                    print(f"  {err}")

            # Check for elements found
            elements_text = await page.locator('text=/\\d+ element/i').all_text_contents()
            if elements_text:
                print(f"\n[SUCCESS] Found elements: {elements_text}")

        except Exception as e:
            print(f"\n[ERROR] Test failed: {e}")
            await page.screenshot(path=f"qa_screenshots/console_error.png", full_page=True)

        finally:
            print("\n" + "="*80)
            print("Console messages captured:", len(console_messages))
            print("Page errors captured:", len(page_errors))
            print("="*80)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_with_console())