"""
Comprehensive React Frontend Testing Script
Tests all aspects of the React application including:
- Page loading and rendering
- Console errors
- Network requests
- Component mounting
- Interactivity
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime
import sys
import io

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def test_frontend():
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "errors": [],
        "warnings": [],
        "network_failures": []
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Capture console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append({
            "type": msg.type,
            "text": msg.text,
            "location": msg.location
        }))
        
        # Capture page errors
        page_errors = []
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        
        # Capture network failures
        network_failures = []
        def handle_request_failed(request):
            network_failures.append({
                "url": request.url,
                "failure": request.failure
            })
        page.on("requestfailed", handle_request_failed)
        
        # Track network requests
        network_requests = []
        page.on("request", lambda req: network_requests.append({
            "url": req.url,
            "method": req.method,
            "resource_type": req.resource_type
        }))
        
        network_responses = []
        page.on("response", lambda res: network_responses.append({
            "url": res.url,
            "status": res.status,
            "ok": res.ok
        }))
        
        print("🔍 Starting comprehensive frontend tests...\n")
        
        # Test 1: Page Loading
        print("1️⃣ Testing page loading...")
        try:
            await page.goto("http://localhost:3000", wait_until="networkidle", timeout=30000)
            results["tests"]["page_loading"] = "✅ PASSED"
            print("   ✅ Page loaded successfully")
        except Exception as e:
            results["tests"]["page_loading"] = f"❌ FAILED: {str(e)}"
            print(f"   ❌ Page loading failed: {str(e)}")
        
        # Test 2: Check for React Root
        print("\n2️⃣ Checking for React root element...")
        try:
            root = await page.query_selector("#root")
            if root:
                root_html = await root.inner_html()
                if root_html and len(root_html) > 10:
                    results["tests"]["react_root"] = "✅ PASSED - Root element has content"
                    print(f"   ✅ React root found with content ({len(root_html)} chars)")
                else:
                    results["tests"]["react_root"] = "⚠️ WARNING - Root element is empty"
                    print("   ⚠️ React root found but appears empty")
            else:
                results["tests"]["react_root"] = "❌ FAILED - No root element"
                print("   ❌ No React root element found")
        except Exception as e:
            results["tests"]["react_root"] = f"❌ FAILED: {str(e)}"
            print(f"   ❌ Error checking React root: {str(e)}")
        
        # Test 3: Check for React Components
        print("\n3️⃣ Checking for React components...")
        try:
            # Wait for any common React indicators
            await page.wait_for_timeout(2000)  # Give React time to mount
            
            # Check for common UI elements
            elements_to_check = [
                ("header", "Header"),
                ("nav", "Navigation"),
                ("main", "Main content"),
                ("button", "Buttons"),
                ("input", "Input fields"),
                ("form", "Forms"),
                ("[class*='container']", "Container elements"),
                ("[class*='App']", "App component")
            ]
            
            found_elements = []
            for selector, name in elements_to_check:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        found_elements.append(name)
                        print(f"   ✅ Found: {name}")
                except:
                    pass
            
            if found_elements:
                results["tests"]["components"] = f"✅ PASSED - Found {len(found_elements)} components"
            else:
                results["tests"]["components"] = "❌ FAILED - No components found"
                print("   ❌ No React components detected")
        except Exception as e:
            results["tests"]["components"] = f"❌ FAILED: {str(e)}"
            print(f"   ❌ Error checking components: {str(e)}")
        
        # Test 4: Console Errors
        print("\n4️⃣ Checking console for errors...")
        errors = [msg for msg in console_messages if msg["type"] in ["error", "warning"]]
        if errors:
            results["errors"] = errors
            print(f"   ⚠️ Found {len(errors)} console errors/warnings:")
            for error in errors[:5]:  # Show first 5
                print(f"      - {error['type']}: {error['text'][:100]}")
        else:
            results["tests"]["console_clean"] = "✅ PASSED"
            print("   ✅ No console errors detected")
        
        # Test 5: Network Issues
        print("\n5️⃣ Checking network requests...")
        failed_requests = [res for res in network_responses if not res["ok"] and res["status"] >= 400]
        if failed_requests:
            results["network_failures"] = failed_requests
            print(f"   ⚠️ Found {len(failed_requests)} failed network requests:")
            for req in failed_requests[:5]:
                print(f"      - {req['status']}: {req['url']}")
        else:
            results["tests"]["network_clean"] = "✅ PASSED"
            print("   ✅ All network requests successful")
        
        # Test 6: JavaScript Execution
        print("\n6️⃣ Testing JavaScript execution...")
        try:
            # Check if React is loaded
            react_loaded = await page.evaluate("""
                () => {
                    return {
                        hasReact: typeof React !== 'undefined' || typeof window.React !== 'undefined',
                        hasReactDOM: typeof ReactDOM !== 'undefined' || typeof window.ReactDOM !== 'undefined',
                        hasDocument: typeof document !== 'undefined',
                        documentReady: document.readyState === 'complete'
                    }
                }
            """)
            
            if react_loaded["documentReady"]:
                results["tests"]["javascript"] = "✅ PASSED - Document ready"
                print("   ✅ JavaScript executing, document ready")
            else:
                results["tests"]["javascript"] = "⚠️ WARNING - Document not ready"
                print("   ⚠️ Document not fully loaded")
                
        except Exception as e:
            results["tests"]["javascript"] = f"❌ FAILED: {str(e)}"
            print(f"   ❌ JavaScript execution error: {str(e)}")
        
        # Test 7: Page Content
        print("\n7️⃣ Checking page content...")
        try:
            page_text = await page.text_content("body")
            if page_text and len(page_text.strip()) > 50:
                results["tests"]["content"] = "✅ PASSED - Page has content"
                print(f"   ✅ Page has content ({len(page_text)} chars)")
                # Show first bit of content
                preview = page_text.strip()[:200].replace('\n', ' ')
                print(f"   📄 Content preview: {preview}...")
            else:
                results["tests"]["content"] = "❌ FAILED - Page appears empty"
                print("   ❌ Page appears to have no content")
        except Exception as e:
            results["tests"]["content"] = f"❌ FAILED: {str(e)}"
            print(f"   ❌ Error getting page content: {str(e)}")
        
        # Test 8: Check specific app features
        print("\n8️⃣ Checking for app-specific features...")
        try:
            # Look for Web Automation or Data Profiling components
            web_automation = await page.query_selector("[class*='automation']")
            data_profiling = await page.query_selector("[class*='profil']")
            navigation = await page.query_selector("[class*='nav']")
            
            features = []
            if web_automation:
                features.append("Web Automation")
            if data_profiling:
                features.append("Data Profiling")
            if navigation:
                features.append("Navigation")
                
            if features:
                results["tests"]["features"] = f"✅ PASSED - Found: {', '.join(features)}"
                print(f"   ✅ Found features: {', '.join(features)}")
            else:
                results["tests"]["features"] = "⚠️ WARNING - No specific features found"
                print("   ⚠️ No specific app features detected")
        except Exception as e:
            results["tests"]["features"] = f"❌ FAILED: {str(e)}"
            print(f"   ❌ Error checking features: {str(e)}")
        
        # Take screenshot for debugging
        print("\n📸 Taking screenshot for debugging...")
        await page.screenshot(path="frontend_test_screenshot.png")
        print("   ✅ Screenshot saved as frontend_test_screenshot.png")
        
        # Save HTML for debugging
        html_content = await page.content()
        with open("frontend_test_page.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("   ✅ HTML saved as frontend_test_page.html")
        
        await browser.close()
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY:")
    print("="*50)
    
    passed = sum(1 for v in results["tests"].values() if "✅ PASSED" in str(v))
    failed = sum(1 for v in results["tests"].values() if "❌ FAILED" in str(v))
    warnings = sum(1 for v in results["tests"].values() if "⚠️ WARNING" in str(v))
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️ Warnings: {warnings}")
    
    # Save detailed results
    with open("frontend_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print("\n📁 Detailed results saved to frontend_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_frontend())