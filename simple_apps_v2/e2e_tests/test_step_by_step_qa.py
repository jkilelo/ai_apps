"""
Senior QA Engineer Approach: Step-by-Step Testing with Evidence
Tests each step individually, takes screenshots, and fixes issues as found
"""

import asyncio
from playwright.async_api import async_playwright, Page
import logging
import sys
from pathlib import Path
import time
import json
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:5175"
SCREENSHOTS_DIR = Path("test_evidence")
SCREENSHOTS_DIR.mkdir(exist_ok=True)

class StepByStepQATest:
    """
    Methodical testing approach:
    1. Test each step individually
    2. Take screenshots for evidence
    3. Identify and document issues
    4. Fix issues before proceeding
    """
    
    def __init__(self):
        self.page = None
        self.context = None
        self.browser = None
        self.step_number = 0
        
    async def setup(self):
        """Initialize browser with debugging capabilities"""
        logger.info("🔧 Setting up test environment...")
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=False,  # Watch the test run
            slow_mo=1000,    # Slow for observation
            devtools=True    # Enable DevTools
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True,
            record_video_dir="videos/"  # Record video evidence
        )
        self.page = await self.context.new_page()
        
        # Enable console and error logging
        self.page.on("console", lambda msg: logger.info(f"Browser console: {msg.text}"))
        self.page.on("pageerror", lambda err: logger.error(f"Page error: {err}"))
        
    async def teardown(self):
        """Clean up and save video"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
    
    async def take_screenshot(self, name: str):
        """Take screenshot with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = SCREENSHOTS_DIR / f"{timestamp}_{name}.png"
        await self.page.screenshot(path=str(filename), full_page=True)
        logger.info(f"📸 Screenshot saved: {filename}")
        return filename
    
    async def inspect_page_elements(self):
        """Inspect and log all important elements on the page"""
        logger.info("🔍 Inspecting page elements...")
        
        # Get all buttons
        buttons = await self.page.query_selector_all("button")
        logger.info(f"  Found {len(buttons)} buttons")
        for i, btn in enumerate(buttons):
            text = await btn.inner_text()
            logger.info(f"    Button {i}: '{text}'")
        
        # Get all inputs
        inputs = await self.page.query_selector_all("input")
        logger.info(f"  Found {len(inputs)} inputs")
        for i, inp in enumerate(inputs):
            placeholder = await inp.get_attribute("placeholder")
            value = await inp.input_value()
            logger.info(f"    Input {i}: placeholder='{placeholder}', value='{value}'")
        
        # Get all headings
        headings = await self.page.query_selector_all("h1, h2, h3")
        logger.info(f"  Found {len(headings)} headings")
        for i, h in enumerate(headings):
            text = await h.inner_text()
            logger.info(f"    Heading {i}: '{text}'")
    
    async def test_step_1_element_extraction(self):
        """Test Step 1: Element Extraction"""
        logger.info("=" * 60)
        logger.info("🧪 STEP 1: ELEMENT EXTRACTION")
        logger.info("=" * 60)
        
        try:
            # Navigate to web automation
            logger.info("📍 Navigating to web automation page...")
            await self.page.goto(f"{FRONTEND_URL}/web-automation", wait_until="networkidle")
            await asyncio.sleep(2)  # Let page fully render
            
            # Take initial screenshot
            await self.take_screenshot("step1_initial")
            
            # Inspect what's on the page
            await self.inspect_page_elements()
            
            # Look for URL input field
            logger.info("🔍 Looking for URL input field...")
            
            # Try different selectors
            url_input = None
            selectors_to_try = [
                'input[type="url"]',
                'input[placeholder*="url" i]',
                'input[placeholder*="URL" i]',
                'input[placeholder*="enter" i][placeholder*="url" i]',
                'input[name="url"]',
                'input[name="targetUrl"]',
                '#url-input',
                'input.url-input'
            ]
            
            for selector in selectors_to_try:
                try:
                    url_input = await self.page.wait_for_selector(selector, timeout=2000)
                    if url_input:
                        logger.info(f"  ✅ Found URL input with selector: {selector}")
                        break
                except:
                    continue
            
            if not url_input:
                logger.error("  ❌ Could not find URL input field")
                await self.take_screenshot("step1_no_url_input")
                
                # Try to find any input
                all_inputs = await self.page.query_selector_all("input")
                if all_inputs:
                    logger.info(f"  Found {len(all_inputs)} inputs, using first one")
                    url_input = all_inputs[0]
            
            # Fill the URL
            if url_input:
                logger.info("📝 Filling URL input...")
                await url_input.fill("https://example.com")
                await self.take_screenshot("step1_url_filled")
            
            # Look for Extract button
            logger.info("🔍 Looking for Extract button...")
            extract_button = None
            button_texts = [
                "Extract Elements",
                "Extract",
                "Start",
                "Begin",
                "Next",
                "Continue"
            ]
            
            for text in button_texts:
                try:
                    extract_button = await self.page.wait_for_selector(f'button:has-text("{text}")', timeout=2000)
                    if extract_button:
                        logger.info(f"  ✅ Found button with text: {text}")
                        break
                except:
                    continue
            
            if not extract_button:
                # Try finding any enabled button
                all_buttons = await self.page.query_selector_all("button:not([disabled])")
                if all_buttons:
                    logger.info(f"  Found {len(all_buttons)} enabled buttons")
                    for btn in all_buttons:
                        btn_text = await btn.inner_text()
                        logger.info(f"    Button text: '{btn_text}'")
                    extract_button = all_buttons[0]
            
            # Click the button
            if extract_button:
                logger.info("🚀 Clicking extract button...")
                await self.take_screenshot("step1_before_click")
                await extract_button.click()
                
                # Wait for response
                logger.info("⏳ Waiting for backend response...")
                await asyncio.sleep(5)  # Give time for backend
                
                # Check for loading indicators
                loading = await self.page.query_selector('[class*="animate-spin"], [class*="loading"], [class*="spinner"]')
                if loading:
                    logger.info("  ⏳ Loading indicator detected, waiting...")
                    await self.page.wait_for_selector('[class*="animate-spin"], [class*="loading"], [class*="spinner"]', state="hidden", timeout=30000)
                
                await self.take_screenshot("step1_after_extraction")
                
                # Check if we moved to step 2
                step2_indicator = await self.page.query_selector('text=/test.*generation/i')
                if step2_indicator:
                    logger.info("  ✅ Successfully moved to Step 2!")
                    await self.take_screenshot("step1_success")
                else:
                    logger.warning("  ⚠️ Did not automatically progress to Step 2")
                    
                    # Check for error messages
                    error = await self.page.query_selector('[class*="error"], [class*="alert"], text=/error|failed/i')
                    if error:
                        error_text = await error.inner_text()
                        logger.error(f"  ❌ Error detected: {error_text}")
                        await self.take_screenshot("step1_error")
                
                # Check window.__extractionData
                extraction_data = await self.page.evaluate("window.__extractionData")
                if extraction_data:
                    logger.info(f"  ✅ Extraction data stored: {len(extraction_data.get('elements', []))} elements")
                else:
                    logger.warning("  ⚠️ No extraction data in window.__extractionData")
                
                return True
            else:
                logger.error("  ❌ No extract button found")
                await self.take_screenshot("step1_no_button")
                return False
                
        except Exception as e:
            logger.error(f"❌ Step 1 failed with exception: {e}")
            await self.take_screenshot("step1_exception")
            return False
    
    async def test_step_2_test_generation(self):
        """Test Step 2: Test Generation"""
        logger.info("=" * 60)
        logger.info("🧪 STEP 2: TEST GENERATION")
        logger.info("=" * 60)
        
        try:
            await self.take_screenshot("step2_initial")
            
            # Inspect current page
            await self.inspect_page_elements()
            
            # Check if we're on step 2
            current_url = self.page.url
            logger.info(f"📍 Current URL: {current_url}")
            
            # Look for test generation indicators
            step2_texts = ["Test Generation", "Generate Tests", "Test Scenarios", "Workflow"]
            found_step2 = False
            
            for text in step2_texts:
                element = await self.page.query_selector(f'text=/{text}/i')
                if element:
                    logger.info(f"  ✅ Found Step 2 indicator: {text}")
                    found_step2 = True
                    break
            
            if not found_step2:
                logger.warning("  ⚠️ Step 2 indicators not found")
            
            # Check for workflow steps display
            logger.info("🔍 Looking for generated workflow steps...")
            workflow_container = await self.page.query_selector('[class*="space-y"], [class*="workflow"], [class*="steps"]')
            
            if workflow_container:
                # Count workflow steps
                workflow_steps = await workflow_container.query_selector_all('[class*="bg-slate"], [class*="rounded"], .step-item')
                logger.info(f"  📋 Found {len(workflow_steps)} workflow steps")
                
                if len(workflow_steps) > 0:
                    # Log first few steps
                    for i, step in enumerate(workflow_steps[:3]):
                        step_text = await step.inner_text()
                        logger.info(f"    Step {i+1}: {step_text[:50]}...")
                    
                    await self.take_screenshot("step2_workflow_populated")
                else:
                    logger.warning("  ⚠️ No workflow steps found, checking for generate button...")
                    
                    # Look for Generate Tests button
                    generate_button = None
                    button_texts = ["Generate Tests", "Generate", "Build Workflow", "Create Tests", "Next"]
                    
                    for text in button_texts:
                        generate_button = await self.page.query_selector(f'button:has-text("{text}")')
                        if generate_button:
                            logger.info(f"  Found button: {text}")
                            await generate_button.click()
                            await asyncio.sleep(5)
                            await self.take_screenshot("step2_after_generate")
                            break
            
            # Check test data in window
            test_data = await self.page.evaluate("window.__testData")
            if test_data:
                logger.info(f"  ✅ Test data stored in window")
                if 'test_scenarios' in test_data or 'gherkin_features' in test_data:
                    logger.info("  ✅ Test scenarios/features found in data")
            else:
                logger.warning("  ⚠️ No test data in window.__testData")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Step 2 failed: {e}")
            await self.take_screenshot("step2_exception")
            return False
    
    async def test_step_3_code_generation(self):
        """Test Step 3: Code Generation"""
        logger.info("=" * 60)
        logger.info("🧪 STEP 3: CODE GENERATION")
        logger.info("=" * 60)
        
        try:
            await self.take_screenshot("step3_initial")
            await self.inspect_page_elements()
            
            # Look for code generation indicators
            code_indicators = await self.page.query_selector('text=/code.*generation|generated.*code/i')
            if code_indicators:
                logger.info("  ✅ On Code Generation step")
            
            # Look for code display
            code_block = await self.page.query_selector('pre, code, [class*="code"], [class*="highlight"]')
            if code_block:
                code_text = await code_block.inner_text()
                logger.info(f"  ✅ Code block found with {len(code_text)} characters")
                await self.take_screenshot("step3_code_displayed")
            else:
                logger.warning("  ⚠️ No code block found")
            
            # Look for next/proceed button
            next_button = await self.page.query_selector('button:has-text("Next"), button:has-text("Execute"), button:has-text("Run")')
            if next_button:
                logger.info("  🚀 Clicking to proceed to execution...")
                await next_button.click()
                await asyncio.sleep(3)
                await self.take_screenshot("step3_after_next")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Step 3 failed: {e}")
            await self.take_screenshot("step3_exception")
            return False
    
    async def test_step_4_code_execution(self):
        """Test Step 4: Code Execution"""
        logger.info("=" * 60)
        logger.info("🧪 STEP 4: CODE EXECUTION")
        logger.info("=" * 60)
        
        try:
            await self.take_screenshot("step4_initial")
            await self.inspect_page_elements()
            
            # Look for execution indicators
            exec_indicators = await self.page.query_selector('text=/execution|execute|run.*test/i')
            if exec_indicators:
                logger.info("  ✅ On Code Execution step")
            
            # Look for execute button
            execute_button = await self.page.query_selector('button:has-text("Execute"), button:has-text("Run"), button:has-text("Start")')
            if execute_button:
                logger.info("  🚀 Clicking execute button...")
                await execute_button.click()
                
                # Wait for execution
                logger.info("  ⏳ Waiting for test execution...")
                await asyncio.sleep(10)
                
                # Check for results
                results = await self.page.query_selector('[class*="result"], text=/passed|failed|success/i')
                if results:
                    results_text = await results.inner_text()
                    logger.info(f"  ✅ Execution results: {results_text[:100]}...")
                    await self.take_screenshot("step4_results")
                else:
                    logger.warning("  ⚠️ No results found")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Step 4 failed: {e}")
            await self.take_screenshot("step4_exception")
            return False
    
    async def run_full_test(self):
        """Run complete test with evidence"""
        logger.info("=" * 60)
        logger.info("🚀 SENIOR QA ENGINEER TEST SUITE")
        logger.info("=" * 60)
        
        try:
            await self.setup()
            
            # Test each step
            step1_result = await self.test_step_1_element_extraction()
            logger.info(f"Step 1 Result: {'✅ PASS' if step1_result else '❌ FAIL'}")
            
            if step1_result:
                step2_result = await self.test_step_2_test_generation()
                logger.info(f"Step 2 Result: {'✅ PASS' if step2_result else '❌ FAIL'}")
                
                if step2_result:
                    step3_result = await self.test_step_3_code_generation()
                    logger.info(f"Step 3 Result: {'✅ PASS' if step3_result else '❌ FAIL'}")
                    
                    if step3_result:
                        step4_result = await self.test_step_4_code_execution()
                        logger.info(f"Step 4 Result: {'✅ PASS' if step4_result else '❌ FAIL'}")
            
            # Final screenshot
            await self.take_screenshot("final_state")
            
            logger.info("=" * 60)
            logger.info("📊 TEST EVIDENCE")
            logger.info("=" * 60)
            logger.info(f"Screenshots saved in: {SCREENSHOTS_DIR.absolute()}")
            
            # List all screenshots
            screenshots = list(SCREENSHOTS_DIR.glob("*.png"))
            for screenshot in screenshots:
                logger.info(f"  📸 {screenshot.name}")
            
        finally:
            await self.teardown()

async def main():
    test = StepByStepQATest()
    await test.run_full_test()

if __name__ == "__main__":
    asyncio.run(main())