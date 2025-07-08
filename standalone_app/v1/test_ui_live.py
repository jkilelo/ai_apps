"""
Live UI Testing with Playwright
Tests the actual UI Web Auto Testing app in the browser
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def test_ui_web_testing():
    async with async_playwright() as p:
        # Launch browser in headless mode (no display available)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # Enable console logging
        page = await context.new_page()
        page.on("console", lambda msg: print(f"Browser console: {msg.text}"))
        page.on("pageerror", lambda err: print(f"Page error: {err}"))
        
        print("1. Navigating to http://localhost:3000/")
        await page.goto("http://localhost:3000/")
        await page.wait_for_load_state("networkidle")
        
        # Take screenshot of landing page
        await page.screenshot(path="/tmp/ui_test_1_landing.png")
        print("   Screenshot saved: /tmp/ui_test_1_landing.png")
        
        # Look for UI Web Auto Testing app
        print("\n2. Looking for UI Web Auto Testing app...")
        
        # Wait for page to fully load
        await page.wait_for_timeout(2000)
        
        # Get page content for debugging
        page_content = await page.content()
        if len(page_content) < 1000:
            print("   WARNING: Page seems empty or not fully loaded")
            print(f"   Page content length: {len(page_content)}")
        
        # Try different selectors for sidebar
        sidebar = await page.query_selector(".sidebar")
        if not sidebar:
            sidebar = await page.query_selector('[class*="sidebar"]')
            if not sidebar:
                sidebar = await page.query_selector('aside')
        
        if not sidebar:
            print("   WARNING: Could not find sidebar")
            # Let's see what's on the page
            all_text = await page.text_content('body')
            print(f"   Page text preview: {all_text[:200]}...")
        
        # Find and click on UI Web Auto Testing
        ui_web_testing = await page.query_selector("text=ui_web_auto_testing")
        if not ui_web_testing:
            ui_web_testing = await page.query_selector("text=UI Web Auto Testing")
        
        if ui_web_testing:
            print("   Found UI Web Auto Testing app")
            await ui_web_testing.click()
            await page.wait_for_load_state("networkidle")
            await page.screenshot(path="/tmp/ui_test_2_app_selected.png")
            print("   Screenshot saved: /tmp/ui_test_2_app_selected.png")
        else:
            print("   ERROR: Could not find UI Web Auto Testing app!")
            await browser.close()
            return
        
        # Wait for the workflow steps to appear
        print("\n3. Waiting for workflow steps...")
        await page.wait_for_selector("text=Element Extraction", timeout=5000)
        
        # Click on Element Extraction step
        element_extraction = await page.query_selector("text=Element Extraction")
        if element_extraction:
            await element_extraction.click()
            await page.wait_for_timeout(1000)
            print("   Clicked on Element Extraction step")
        
        # Look for the form
        print("\n4. Looking for the form...")
        await page.screenshot(path="/tmp/ui_test_3_form_view.png")
        print("   Screenshot saved: /tmp/ui_test_3_form_view.png")
        
        # Find the URL input field
        url_input = await page.query_selector('input[name="web_page_url"]')
        if not url_input:
            # Try other selectors
            url_input = await page.query_selector('input[type="text"]')
            if not url_input:
                url_input = await page.query_selector('input[type="url"]')
        
        if url_input:
            print("   Found URL input field")
            await url_input.fill("https://example.com")
            print("   Filled URL: https://example.com")
        else:
            print("   ERROR: Could not find URL input field!")
            # Try to find any input fields
            inputs = await page.query_selector_all('input')
            print(f"   Found {len(inputs)} input fields total")
            for i, inp in enumerate(inputs):
                input_type = await inp.get_attribute('type')
                input_name = await inp.get_attribute('name')
                input_placeholder = await inp.get_attribute('placeholder')
                print(f"     Input {i}: type={input_type}, name={input_name}, placeholder={input_placeholder}")
        
        # Find and click submit button
        print("\n5. Looking for submit button...")
        submit_button = await page.query_selector('button[type="submit"]')
        if not submit_button:
            submit_button = await page.query_selector('button:has-text("Execute")')
            if not submit_button:
                submit_button = await page.query_selector('button:has-text("Submit")')
                if not submit_button:
                    submit_button = await page.query_selector('button:has-text("Run")')
        
        if submit_button:
            print("   Found submit button")
            await page.screenshot(path="/tmp/ui_test_4_before_submit.png")
            print("   Screenshot saved: /tmp/ui_test_4_before_submit.png")
            
            # Click submit
            await submit_button.click()
            print("   Clicked submit button")
            
            # Wait for response
            await page.wait_for_timeout(3000)
            
            # Take screenshot of result
            await page.screenshot(path="/tmp/ui_test_5_after_submit.png")
            print("   Screenshot saved: /tmp/ui_test_5_after_submit.png")
            
            # Look for error messages
            error_element = await page.query_selector('text=Error')
            if not error_element:
                error_element = await page.query_selector('text=Failed')
                
            if error_element:
                print("\n   ERROR FOUND!")
                error_text = await error_element.text_content()
                print(f"   Error text: {error_text}")
                
                # Try to get more error details
                error_container = await error_element.evaluate_handle('el => el.parentElement')
                full_error = await error_container.text_content()
                print(f"   Full error container: {full_error}")
        else:
            print("   ERROR: Could not find submit button!")
            # List all buttons
            buttons = await page.query_selector_all('button')
            print(f"   Found {len(buttons)} buttons total")
            for i, btn in enumerate(buttons):
                btn_text = await btn.text_content()
                btn_type = await btn.get_attribute('type')
                print(f"     Button {i}: text='{btn_text}', type={btn_type}")
        
        # Wait a bit before closing
        print("\n6. Test complete. Browser will close in 5 seconds...")
        await page.wait_for_timeout(5000)
        
        await browser.close()

if __name__ == "__main__":
    print("Starting live UI test...")
    asyncio.run(test_ui_web_testing())
    print("\nTest complete! Check screenshots in /tmp/ui_test_*.png")