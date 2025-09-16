import asyncio
from playwright.async_api import async_playwright

async def test_element_extraction_ui():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to the UI
        await page.goto("http://localhost:8002/")
        
        # Wait for the page to load
        await page.wait_for_load_state("networkidle")
        
        # Click on UI Web Auto Testing app
        await page.click("text=UI Web Auto Testing")
        await page.wait_for_timeout(1000)
        
        # Fill in the form
        await page.fill('input[name="web_page_url"]', "https://example.com/")
        
        # Submit the form
        await page.click('button[type="submit"]')
        
        # Wait for the extraction to complete
        await page.wait_for_selector("text=Element Extraction Complete", timeout=30000)
        
        # Get console logs
        page.on("console", lambda msg: print(f"Console: {msg.text}"))
        
        # Take a screenshot
        await page.screenshot(path="/tmp/element_extraction_result.png")
        
        # Wait a bit to see console logs
        await page.wait_for_timeout(2000)
        
        await browser.close()
        print("Test completed - check /tmp/element_extraction_result.png")

if __name__ == "__main__":
    asyncio.run(test_element_extraction_ui())