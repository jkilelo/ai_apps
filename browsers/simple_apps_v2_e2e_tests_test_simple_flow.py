"""
Quick test to check API response
"""

import asyncio
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_simple():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False, slow_mo=500)
    page = await browser.new_page()
    
    # Log console messages
    page.on("console", lambda msg: logger.info(f"Console: {msg.text}"))
    
    # Navigate to web automation
    await page.goto("http://localhost:3000/web-automation")
    await asyncio.sleep(2)
    
    # Fill URL
    url_input = await page.wait_for_selector('input[type="url"]')
    await url_input.fill("https://example.com")
    
    # Click button - new UI has "Extract Elements" button
    button = await page.wait_for_selector('button:has-text("Extract Elements")')
    await button.click()
    
    # Wait for backend response (can take 20+ seconds with LLM)
    await asyncio.sleep(30)
    
    # Check window.__extractionData
    data = await page.evaluate("window.__extractionData")
    logger.info(f"Extraction data: {data}")
    
    await browser.close()

asyncio.run(test_simple())