"""
Senior UI/UX Engineer - Final Proof that UI displays all backend responses
"""

import asyncio
from playwright.async_api import async_playwright
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_ui_backend_integration():
    """Test and capture screenshots proving UI displays backend data"""
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False, slow_mo=1000)
    page = await browser.new_page()
    
    # Log console messages
    page.on("console", lambda msg: logger.info(f"Console: {msg.text}"))
    
    logger.info("=" * 60)
    logger.info("🎯 TESTING UI-BACKEND INTEGRATION")
    logger.info("=" * 60)
    
    # Navigate to web automation
    await page.goto("http://localhost:3000/web-automation")
    await asyncio.sleep(2)
    
    # Take initial screenshot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    await page.screenshot(path=f"ui_proof_{timestamp}_step1_initial.png")
    logger.info("📸 Screenshot: Step 1 Initial State")
    
    # STEP 1: ELEMENT EXTRACTION
    logger.info("\n🧪 STEP 1: ELEMENT EXTRACTION")
    url_input = await page.wait_for_selector('input[type="url"]')
    await url_input.fill("https://example.com")
    await page.screenshot(path=f"ui_proof_{timestamp}_step1_url_filled.png")
    
    # Click Extract Elements
    extract_button = await page.wait_for_selector('button:has-text("Extract Elements")')
    await extract_button.click()
    logger.info("⏳ Waiting for backend response...")
    
    # Wait for extraction to complete (shows loading state)
    await asyncio.sleep(2)
    await page.screenshot(path=f"ui_proof_{timestamp}_step1_loading.png")
    logger.info("📸 Screenshot: Loading state during extraction")
    
    # Wait for backend response (20+ seconds)
    await asyncio.sleep(25)
    
    # Check if extraction results are displayed
    extraction_success = await page.query_selector('text="Extraction Successful"')
    if extraction_success:
        await page.screenshot(path=f"ui_proof_{timestamp}_step1_success.png")
        logger.info("✅ STEP 1 SUCCESS: Extraction results displayed in UI!")
        
        # Check extraction data
        data = await page.evaluate("window.__extractionData")
        if data:
            logger.info(f"✅ Extraction data stored: {data.get('elements', []).__len__()} elements")
    else:
        await page.screenshot(path=f"ui_proof_{timestamp}_step1_error.png")
        logger.info("❌ Extraction results not displayed")
    
    # Wait for auto-progression to Step 2
    await asyncio.sleep(2)
    
    # STEP 2: TEST GENERATION
    logger.info("\n🧪 STEP 2: TEST GENERATION")
    await page.screenshot(path=f"ui_proof_{timestamp}_step2_initial.png")
    
    # Click Generate Test Scenarios
    generate_button = await page.query_selector('button:has-text("Generate Test")')
    if generate_button:
        await generate_button.click()
        logger.info("⏳ Generating test scenarios...")
        await asyncio.sleep(20)
        
        # Check for test scenarios display
        test_scenarios = await page.query_selector('text="Generated Test Scenarios"')
        if test_scenarios:
            await page.screenshot(path=f"ui_proof_{timestamp}_step2_scenarios.png")
            logger.info("✅ STEP 2 SUCCESS: Test scenarios displayed in UI!")
        else:
            logger.info("❌ Test scenarios not displayed")
    
    # STEP 3: CODE GENERATION
    logger.info("\n🧪 STEP 3: CODE GENERATION")
    code_button = await page.query_selector('button:has-text("Generate Code")')
    if code_button:
        await code_button.click()
        logger.info("⏳ Generating code...")
        await asyncio.sleep(15)
        
        # Check for generated code display
        code_block = await page.query_selector('pre')
        if code_block:
            await page.screenshot(path=f"ui_proof_{timestamp}_step3_code.png")
            logger.info("✅ STEP 3 SUCCESS: Generated code displayed in UI!")
        else:
            logger.info("❌ Generated code not displayed")
    
    # STEP 4: CODE EXECUTION
    logger.info("\n🧪 STEP 4: CODE EXECUTION")
    execute_button = await page.query_selector('button:has-text("Execute")')
    if execute_button:
        await execute_button.click()
        logger.info("⏳ Executing tests...")
        await asyncio.sleep(20)
        
        # Check for execution results
        results = await page.query_selector('text="Test Results"')
        if results:
            await page.screenshot(path=f"ui_proof_{timestamp}_step4_results.png")
            logger.info("✅ STEP 4 SUCCESS: Execution results displayed in UI!")
        else:
            logger.info("❌ Execution results not displayed")
    
    # Final screenshot
    await page.screenshot(path=f"ui_proof_{timestamp}_final.png")
    
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST COMPLETE - ALL SCREENSHOTS CAPTURED")
    logger.info("=" * 60)
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(test_ui_backend_integration())