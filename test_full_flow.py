"""
Test the complete web automation flow
"""
import asyncio
from playwright.async_api import async_playwright

async def test_full_flow():
    """Test all 4 steps of the web automation flow"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Listen for console messages
        def handle_console(msg):
            if 'API Response' in msg.text or 'Elements' in msg.text:
                print(f"CONSOLE: {msg.text}")

        page.on("console", handle_console)

        try:
            print("=== STEP 1: Element Extraction ===")

            # Navigate to Web Automation flow
            await page.goto('http://localhost:3001/web-automation')
            await page.wait_for_load_state('networkidle')
            print("SUCCESS: Navigated to Web Automation flow")
            await page.screenshot(path='qa_screenshots/flow_01_initial.png')

            # Fill URL and extract elements
            url_input = page.locator('input').first
            await url_input.clear()
            await url_input.fill('https://httpbin.org/forms/post')
            print("SUCCESS: Entered URL")

            extract_button = page.locator('button:has-text("Extract Elements")').first
            await extract_button.click()
            print("WAITING: Extracting elements...")

            # Wait for extraction to complete (up to 20 seconds)
            await page.wait_for_selector('text=Extracted Elements (', timeout=20000)
            await page.wait_for_timeout(1000)
            await page.screenshot(path='qa_screenshots/flow_02_elements_extracted.png')
            print("SUCCESS: Elements extracted and displayed")

            # Check element count
            element_header = page.locator('text=/Extracted Elements \\(\\d+\\)/')
            header_text = await element_header.text_content()
            print(f"RESULT: {header_text}")

            print("\n=== STEP 2: Test Generation ===")

            # Click Generate Tests
            generate_tests_button = page.locator('button:has-text("Generate Tests")').first
            await generate_tests_button.click()
            print("WAITING: Generating tests...")

            # Wait for test generation (this might use LLM and take time)
            try:
                await page.wait_for_selector('text=Step 3 of 4', timeout=60000)
                await page.wait_for_timeout(1000)
                await page.screenshot(path='qa_screenshots/flow_03_tests_generated.png')
                print("SUCCESS: Tests generated, moved to Step 3")
            except:
                await page.screenshot(path='qa_screenshots/flow_03_test_generation_timeout.png')
                print("WARNING: Test generation took too long or failed")
                return

            print("\n=== STEP 3: Code Generation ===")

            # Check if we're on code generation step
            if await page.locator('text=Code Generation').count() > 0:
                print("SUCCESS: On Code Generation step")

                # Generate code (usually there's a language selector)
                generate_code_button = page.locator('button:has-text("Generate Code")').first
                if await generate_code_button.count() > 0:
                    await generate_code_button.click()
                    print("WAITING: Generating code...")

                    # Wait for code generation
                    try:
                        await page.wait_for_selector('text=Step 4 of 4', timeout=30000)
                        await page.wait_for_timeout(1000)
                        await page.screenshot(path='qa_screenshots/flow_04_code_generated.png')
                        print("SUCCESS: Code generated, moved to Step 4")
                    except:
                        await page.screenshot(path='qa_screenshots/flow_04_code_generation_issue.png')
                        print("WARNING: Code generation issue")

            print("\n=== STEP 4: Code Execution ===")

            # Check if we're on execution step
            if await page.locator('text=Code Execution').count() > 0:
                print("SUCCESS: On Code Execution step")
                await page.screenshot(path='qa_screenshots/flow_05_execution_ready.png')

                # Usually there's an execute button
                execute_button = page.locator('button:has-text("Execute")').first
                if await execute_button.count() > 0:
                    print("INFO: Execute button available")

            print("\n=== FLOW SUMMARY ===")
            print("Step 1 - Element Extraction: COMPLETED")
            print("Step 2 - Test Generation: Check screenshot")
            print("Step 3 - Code Generation: Check screenshot")
            print("Step 4 - Code Execution: Check screenshot")

        except Exception as e:
            print(f"ERROR: Test failed: {e}")
            await page.screenshot(path='qa_screenshots/flow_error.png')

        finally:
            await page.wait_for_timeout(2000)  # Let user see final state
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_full_flow())