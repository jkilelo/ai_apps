"""
Complete QA Test for Web Automation Flow with Screenshots
Tests all 4 steps of the flow and captures evidence
"""

import asyncio
import time
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
import os

# Create screenshots directory
SCREENSHOT_DIR = Path("qa_screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)

def get_timestamp():
    """Get formatted timestamp for filenames"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

async def test_complete_flow():
    """Test the complete web automation flow with screenshots"""

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        print("\n" + "="*80)
        print("WEB AUTOMATION FLOW - COMPLETE QA TEST")
        print("="*80)

        try:
            # Navigate to the app
            print("\n[STEP 0] Navigating to frontend...")
            await page.goto("http://localhost:3002")
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(2000)

            # Take initial screenshot
            await page.screenshot(path=f"qa_screenshots/{get_timestamp()}_00_initial_page.png")
            print("[OK] Screenshot captured: Initial page")

            # Find and click Web Automation link
            print("\n[STEP 1] Finding Web Automation flow...")
            web_automation_link = await page.get_by_text("Web Automation").first.is_visible()

            if not web_automation_link:
                # Try to find it another way
                await page.get_by_role("link", name="Web Automation").click()
            else:
                await page.get_by_text("Web Automation").first.click()

            await page.wait_for_timeout(1000)
            await page.screenshot(path=f"qa_screenshots/{get_timestamp()}_01_web_automation_page.png")
            print("[OK] Screenshot captured: Web Automation page")

            # Check for URL input field
            print("\n[STEP 2] Looking for URL input field...")
            url_input = page.locator('input[placeholder*="URL"], input[placeholder*="url"], input[type="url"], input#url')

            if not await url_input.count():
                print("[WARNING] URL input not found with standard selectors, trying broader search...")
                url_input = page.locator('input').first

            await url_input.fill("https://example.com")
            await page.wait_for_timeout(500)
            await page.screenshot(path=f"qa_screenshots/{get_timestamp()}_02_url_entered.png")
            print("[OK] Screenshot captured: URL entered")

            # Click Extract Elements button (Step 1)
            print("\n[STEP 3] Clicking Extract Elements button...")
            extract_button = page.locator('button:has-text("Extract"), button:has-text("extract")').first

            if not await extract_button.count():
                extract_button = page.locator('button').filter(has_text="Extract").first

            await extract_button.click()
            print("[WAITING] Waiting for element extraction...")

            # Wait for extraction to complete (up to 30 seconds)
            try:
                await page.wait_for_selector('text=/\\d+ elements?/i', timeout=30000)
                await page.wait_for_timeout(2000)
                await page.screenshot(path=f"qa_screenshots/{get_timestamp()}_03_elements_extracted.png")
                print("[OK] Screenshot captured: Elements extracted")

                # Get element count
                element_text = await page.locator('text=/\\d+ elements?/i').first.text_content()
                print(f"[OK] Elements found: {element_text}")

            except:
                await page.screenshot(path=f"qa_screenshots/{get_timestamp()}_03_extraction_timeout.png")
                print("[WARNING] Element extraction may have timed out")

            # Click Generate Tests button (Step 2)
            print("\n[STEP 4] Clicking Generate Tests button...")
            generate_button = page.locator('button:has-text("Generate"), button:has-text("generate")').first

            if not await generate_button.count():
                generate_button = page.locator('button').filter(has_text="Generate").first

            await generate_button.click()
            print("[WAITING] Waiting for test generation...")

            # Wait for tests to appear
            await page.wait_for_timeout(5000)
            await page.screenshot(path=f"qa_screenshots/{get_timestamp()}_04_tests_generated.png")
            print("[OK] Screenshot captured: Tests generated")

            # Check if tests were generated
            test_items = await page.locator('[class*="test"], [data-test*="test"], li').count()
            print(f"[OK] Test scenarios found: {test_items}")

            # Click Generate Code button (Step 3)
            print("\n[STEP 5] Looking for Generate Code button...")
            code_button = page.locator('button:has-text("Code"), button:has-text("code")').first

            if not await code_button.count():
                # Scroll down to find it
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1000)
                code_button = page.locator('button').filter(has_text="Code").first

            if await code_button.count():
                await code_button.click()
                print("[WAITING] Waiting for code generation...")
                await page.wait_for_timeout(3000)
                await page.screenshot(path=f"qa_screenshots/{get_timestamp()}_05_code_generated.png")
                print("[OK] Screenshot captured: Code generated")
            else:
                print("[WARNING] Generate Code button not found")

            # Look for Execute button (Step 4)
            print("\n[STEP 6] Looking for Execute button...")
            execute_button = page.locator('button:has-text("Execute"), button:has-text("execute"), button:has-text("Run")').first

            if await execute_button.count():
                await execute_button.click()
                print("[WAITING] Waiting for code execution...")
                await page.wait_for_timeout(3000)
                await page.screenshot(path=f"qa_screenshots/{get_timestamp()}_06_code_executed.png")
                print("[OK] Screenshot captured: Code executed")
            else:
                print("[WARNING] Execute button not found")

            # Final screenshot showing complete flow
            await page.evaluate("window.scrollTo(0, 0)")
            await page.wait_for_timeout(1000)
            await page.screenshot(path=f"qa_screenshots/{get_timestamp()}_07_final_state.png", full_page=True)
            print("[OK] Screenshot captured: Final state (full page)")

            print("\n" + "="*80)
            print("QA TEST COMPLETE")
            print(f"Screenshots saved in: {SCREENSHOT_DIR.absolute()}")
            print("="*80)

        except Exception as e:
            print(f"\n[ERROR] Error during test: {e}")
            await page.screenshot(path=f"qa_screenshots/{get_timestamp()}_error.png", full_page=True)
            print("[OK] Error screenshot captured")
            raise

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_complete_flow())