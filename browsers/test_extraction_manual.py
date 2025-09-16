"""
Manual test to verify extraction button works
"""

import asyncio
from playwright.async_api import async_playwright
import sys
import io

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def test_extraction():
    print("Testing Web Automation Extraction...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to the page
        await page.goto("http://localhost:3000/web-automation")
        await page.wait_for_timeout(2000)
        
        # Enter a URL
        print("Entering URL...")
        url_input = await page.query_selector("input[type='url']")
        await url_input.fill("https://example.com")
        
        # Click the Extract Elements button
        print("Clicking Extract Elements button...")
        extract_button = await page.query_selector("button:has-text('Extract Elements')")
        await extract_button.click()
        
        # Wait for extraction to start
        print("Waiting for extraction...")
        await page.wait_for_timeout(5000)
        
        # Check if extraction started
        try:
            # Look for any extraction indicators
            extracting = await page.query_selector("text=Extracting")
            analyzing = await page.query_selector("text=Analyzing")
            complete = await page.query_selector("text=Complete")
            error = await page.query_selector("text=Error")
            
            if extracting or analyzing:
                print("✅ Extraction is in progress!")
            elif complete:
                print("✅ Extraction completed!")
            elif error:
                print("❌ Extraction failed with error")
            else:
                print("⚠️ No extraction status detected")
                
            # Take screenshot
            await page.screenshot(path="extraction_test.png")
            print("Screenshot saved as extraction_test.png")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print("\nKeeping browser open for manual inspection...")
        print("Press Ctrl+C to close")
        
        try:
            await asyncio.sleep(300)  # Keep open for 5 minutes
        except KeyboardInterrupt:
            print("\nClosing browser...")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_extraction())