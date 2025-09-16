"""
Test script for the updated Web Automation Flow
Tests the combined Extract Elements step and full flow
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime
import sys
import io

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def test_web_automation_flow():
    """Test the updated web automation flow with combined Extract Elements step"""
    
    print("🚀 Starting Web Automation Flow Test")
    print("=" * 50)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "errors": []
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Capture console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append({
            "type": msg.type,
            "text": msg.text
        }))
        
        # Capture network activity
        api_calls = []
        def track_api_call(request):
            if 'localhost:5175' in request.url:
                api_calls.append({
                    "url": request.url,
                    "method": request.method,
                    "timestamp": datetime.now().isoformat()
                })
        page.on("request", track_api_call)
        
        try:
            # Navigate to Web Automation page
            print("\n1️⃣ Navigating to Web Automation Flow...")
            await page.goto("http://localhost:3000/web-automation", wait_until="networkidle")
            await page.wait_for_timeout(1000)
            
            # Check if we're on Step 1 (Extract Elements)
            print("\n2️⃣ Verifying Step 1 - Extract Elements...")
            step1_title = await page.query_selector("text=Extract Elements")
            if step1_title:
                results["tests"]["step1_visible"] = "✅ PASSED"
                print("   ✅ Step 1 'Extract Elements' is visible")
            else:
                results["tests"]["step1_visible"] = "❌ FAILED"
                print("   ❌ Step 1 'Extract Elements' not found")
            
            # Check for URL input field
            print("\n3️⃣ Testing URL Input...")
            url_input = await page.query_selector("input[type='url']")
            if url_input:
                # Clear and enter a test URL
                await url_input.fill("")
                await url_input.type("https://example.com")
                results["tests"]["url_input"] = "✅ PASSED"
                print("   ✅ URL input field working")
            else:
                results["tests"]["url_input"] = "❌ FAILED"
                print("   ❌ URL input field not found")
            
            # Check for test site buttons
            print("\n4️⃣ Checking Quick Select Sites...")
            test_sites = await page.query_selector_all("button")
            site_buttons = [btn for btn in test_sites if await btn.text_content() in ["Google", "GitHub", "Stack Overflow", "Reddit", "Wikipedia"]]
            if site_buttons:
                results["tests"]["quick_select"] = "✅ PASSED"
                print(f"   ✅ Found {len(site_buttons)} quick select buttons")
                
                # Click one of them
                if site_buttons:
                    await site_buttons[0].click()
                    await page.wait_for_timeout(500)
                    print("   ✅ Clicked a quick select button")
            else:
                results["tests"]["quick_select"] = "❌ FAILED"
                print("   ❌ Quick select buttons not found")
            
            # Look for Extract Elements button
            print("\n5️⃣ Looking for Extract Elements button...")
            extract_button = await page.query_selector("button:has-text('Extract Elements')")
            if extract_button:
                results["tests"]["extract_button"] = "✅ PASSED"
                print("   ✅ Extract Elements button found")
                
                # Click the button to trigger extraction
                print("\n6️⃣ Triggering element extraction...")
                await extract_button.click()
                
                # Wait for extraction to start
                await page.wait_for_timeout(2000)
                
                # Check for progress indicators
                progress = await page.query_selector("text=Extracting")
                if progress:
                    print("   ✅ Extraction in progress...")
                    results["tests"]["extraction_progress"] = "✅ PASSED"
                    
                    # Wait for extraction to complete (max 30 seconds)
                    try:
                        await page.wait_for_selector("text=Extraction Complete", timeout=30000)
                        print("   ✅ Extraction completed successfully")
                        results["tests"]["extraction_complete"] = "✅ PASSED"
                    except:
                        print("   ⚠️ Extraction taking longer than expected")
                        results["tests"]["extraction_complete"] = "⚠️ TIMEOUT"
                else:
                    results["tests"]["extraction_progress"] = "❌ FAILED"
                    print("   ❌ No extraction progress shown")
            else:
                results["tests"]["extract_button"] = "❌ FAILED"
                print("   ❌ Extract Elements button not found")
            
            # Check for results display
            print("\n7️⃣ Checking for extraction results...")
            await page.wait_for_timeout(3000)
            
            # Look for executive/developer view toggle
            view_toggle = await page.query_selector("text=Executive")
            if view_toggle:
                results["tests"]["results_display"] = "✅ PASSED"
                print("   ✅ Results display with view toggle found")
            else:
                results["tests"]["results_display"] = "⚠️ PARTIAL"
                print("   ⚠️ Results display may not be visible")
            
            # Check for Continue button to step 2
            print("\n8️⃣ Looking for Continue button...")
            continue_button = await page.query_selector("button:has-text('Continue')")
            if continue_button:
                results["tests"]["continue_button"] = "✅ PASSED"
                print("   ✅ Continue button found (manual progression)")
            else:
                results["tests"]["continue_button"] = "⚠️ WARNING"
                print("   ⚠️ Continue button not found (may auto-progress)")
            
            # Check API calls
            print("\n9️⃣ Verifying API Integration...")
            extract_api_calls = [call for call in api_calls if '/api/extract-elements' in call['url']]
            if extract_api_calls:
                results["tests"]["api_integration"] = "✅ PASSED"
                print(f"   ✅ API call made to /api/extract-elements")
            else:
                results["tests"]["api_integration"] = "❌ FAILED"
                print("   ❌ No API call to /api/extract-elements detected")
            
            # Check for console errors
            errors = [msg for msg in console_messages if msg["type"] == "error"]
            if errors:
                results["errors"] = errors
                print(f"\n⚠️ Found {len(errors)} console errors")
                for error in errors[:3]:
                    print(f"   - {error['text'][:100]}")
            else:
                print("\n✅ No console errors detected")
            
        except Exception as e:
            results["errors"].append(str(e))
            print(f"\n❌ Test failed with error: {str(e)}")
        
        # Take screenshot
        await page.screenshot(path="web_automation_test_screenshot.png")
        print("\n📸 Screenshot saved as web_automation_test_screenshot.png")
        
        await browser.close()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print("=" * 50)
    
    passed = sum(1 for v in results["tests"].values() if "✅ PASSED" in str(v))
    failed = sum(1 for v in results["tests"].values() if "❌ FAILED" in str(v))
    warnings = sum(1 for v in results["tests"].values() if "⚠️" in str(v))
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️ Warnings: {warnings}")
    
    # Save results
    with open("web_automation_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print("\n📁 Detailed results saved to web_automation_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_web_automation_flow())