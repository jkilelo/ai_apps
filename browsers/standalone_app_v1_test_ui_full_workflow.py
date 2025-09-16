"""
Full UI Workflow Test with Playwright
Tests the complete workflow from element extraction through test execution
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def test_full_ui_workflow():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"Browser console: {msg.text}"))
        page.on("pageerror", lambda err: print(f"Page error: {err}"))
        
        print("=== UI Web Auto Testing - Full Workflow Test ===\n")
        
        # 1. Navigate to the app
        print("1. Navigating to http://localhost:3000/")
        await page.goto("http://localhost:3000/")
        await page.wait_for_timeout(2000)
        
        # 2. Click on UI Web Auto Testing
        print("2. Selecting UI Web Auto Testing app...")
        ui_app = await page.query_selector("text=ui_web_auto_testing")
        if not ui_app:
            ui_app = await page.query_selector("text=UI Web Auto Testing")
        
        if ui_app:
            await ui_app.click()
            await page.wait_for_timeout(1000)
            print("   ✓ App selected")
        else:
            print("   ✗ Could not find app!")
            await browser.close()
            return
        
        # 3. Element Extraction
        print("\n3. Testing Element Extraction...")
        
        # Click on Element Extraction step
        elem_extraction = await page.query_selector("text=Element Extraction")
        if elem_extraction:
            await elem_extraction.click()
            await page.wait_for_timeout(500)
        
        # Fill the form
        url_input = await page.query_selector('input[name="web_page_url"]')
        if not url_input:
            url_input = await page.query_selector('input[type="text"]')
        
        if url_input:
            await url_input.fill("https://example.com")
            print("   ✓ Filled URL: https://example.com")
        
        # Submit
        submit_btn = await page.query_selector('button[type="submit"]')
        if submit_btn:
            await submit_btn.click()
            print("   ✓ Submitted form")
            
            # Wait for completion
            print("   ⏳ Waiting for extraction to complete...")
            success_found = False
            for i in range(15):  # Wait up to 15 seconds
                await page.wait_for_timeout(1000)
                
                # Check for success indicator
                success = await page.query_selector('text=Extraction Complete')
                if not success:
                    success = await page.query_selector('text=Success')
                    
                if success:
                    success_found = True
                    print("   ✓ Extraction completed successfully!")
                    await page.screenshot(path="/tmp/ui_workflow_1_extraction_complete.png")
                    break
                    
                # Check for error
                error = await page.query_selector('text=Failed')
                if error:
                    print("   ✗ Extraction failed!")
                    error_details = await page.query_selector('.font-mono')
                    if error_details:
                        error_text = await error_details.text_content()
                        print(f"   Error: {error_text}")
                    await page.screenshot(path="/tmp/ui_workflow_1_extraction_error.png")
                    break
            
            if not success_found and not error:
                print("   ⚠️  Extraction may still be running")
                await page.screenshot(path="/tmp/ui_workflow_1_extraction_timeout.png")
        
        # 4. Test Generation
        print("\n4. Testing Test Generation...")
        
        # Click on Generate Test Cases step
        test_gen = await page.query_selector("text=Generate Test Cases")
        if test_gen:
            await test_gen.click()
            await page.wait_for_timeout(1000)
            print("   ✓ Selected Test Generation step")
            
            # The form should auto-populate with extracted elements
            # Just click submit
            submit_btn = await page.query_selector('button[type="submit"]')
            if submit_btn:
                await submit_btn.click()
                print("   ✓ Submitted test generation")
                
                # Wait for completion
                print("   ⏳ Waiting for test generation...")
                await page.wait_for_timeout(3000)
                await page.screenshot(path="/tmp/ui_workflow_2_test_generation.png")
        
        # 5. Test Execution
        print("\n5. Testing Test Execution...")
        
        # Click on Execute Test Cases step
        test_exec = await page.query_selector("text=Execute Test Cases")
        if test_exec:
            await test_exec.click()
            await page.wait_for_timeout(1000)
            print("   ✓ Selected Test Execution step")
            
            # Submit to execute tests
            submit_btn = await page.query_selector('button[type="submit"]')
            if submit_btn:
                await submit_btn.click()
                print("   ✓ Started test execution")
                
                # Wait for completion
                print("   ⏳ Waiting for test execution...")
                await page.wait_for_timeout(5000)
                await page.screenshot(path="/tmp/ui_workflow_3_test_execution.png")
                
                # Look for results
                pass_rate = await page.query_selector('text=Pass rate')
                if pass_rate:
                    print("   ✓ Test execution completed!")
                    
                    # Try to get pass rate
                    rate_elem = await page.query_selector('text=%')
                    if rate_elem:
                        rate_text = await rate_elem.text_content()
                        print(f"   Pass rate: {rate_text}")
        
        print("\n=== Workflow Test Complete ===")
        print("Screenshots saved:")
        print("  - /tmp/ui_workflow_1_extraction_complete.png")
        print("  - /tmp/ui_workflow_2_test_generation.png")
        print("  - /tmp/ui_workflow_3_test_execution.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_full_ui_workflow())