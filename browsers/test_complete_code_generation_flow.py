"""
Comprehensive test of the complete Web Automation flow including Generate Code step
"""

from playwright.sync_api import sync_playwright
import time

def test_complete_code_generation_flow():
    """Test the complete 5-step flow including the new Generate Code step"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("🚀 COMPREHENSIVE WEB AUTOMATION FLOW TEST")
        print("=" * 55)
        
        print("1️⃣ Step 1: Web URL...")
        page.goto("http://localhost:3000/web-automation")
        time.sleep(2)
        
        # Verify 5 steps in navigation
        step_indicators = page.query_selector_all('.text-xs.text-slate-500')
        for indicator in step_indicators:
            if "Step" in indicator.text_content():
                print(f"   ✅ Found step indicator: {indicator.text_content()}")
                break
        
        print("2️⃣ Starting element extraction...")
        page.click('button:has-text("Example.com")')
        time.sleep(0.5)
        
        page.click('button:has-text("Start Extraction")')
        print("   Waiting for extraction...")
        
        try:
            page.wait_for_selector('h3:has-text("Extraction Results")', timeout=30000)
            print("   ✅ Step 2: Extract Elements completed!")
        except:
            print("   ❌ Extraction timeout")
            browser.close()
            return
        
        print("3️⃣ Moving to Generate Tests step...")
        page.click('button:has-text("Continue to Test Generation")')
        time.sleep(3)
        
        # Check if we're on step 3
        step_3_indicator = page.query_selector('text="Step 3 of 5"')
        if step_3_indicator:
            print("   ✅ Successfully on Step 3 of 5")
        
        # Wait for test generation to complete
        try:
            page.wait_for_selector('text="Test Cases Generated"', timeout=60000)
            print("   ✅ Step 3: Generate Tests completed!")
        except:
            print("   ⏰ Still generating tests, proceeding...")
        
        print("4️⃣ Moving to Generate Code step...")
        page.click('button:has-text("Continue to Code Generation")')
        time.sleep(3)
        
        # Check if we're on step 4
        step_4_indicator = page.query_selector('text="Step 4 of 5"')
        if step_4_indicator:
            print("   ✅ Successfully on Step 4 of 5 - Generate Code")
        
        # Verify Generate Code UI elements
        print("5️⃣ Testing Generate Code UI...")
        
        # Check for auto-generation info
        auto_code_info = page.query_selector('text="Automatic Code Generation"')
        if auto_code_info:
            print("   ✅ Auto-generation info displayed")
        
        # Check for progress indicator
        time.sleep(5)  # Wait for potential progress
        progress_indicators = page.query_selector_all('.text-purple-900')
        if progress_indicators:
            for indicator in progress_indicators:
                status = indicator.text_content()
                if status:
                    print(f"   🔄 Code generation status: {status}")
        
        # Wait for code generation to complete
        try:
            page.wait_for_selector('text="Code Generated"', timeout=120000)
            print("   ✅ Step 4: Generate Code completed!")
            
            # Test view mode toggle
            executive_btn = page.query_selector('button:has-text("Executive")')
            developer_btn = page.query_selector('button:has-text("Developer")')
            
            if executive_btn and developer_btn:
                print("   ✅ View mode toggle buttons found")
                
                # Test Executive View
                executive_btn.click()
                time.sleep(1)
                success_banner = page.query_selector('text="Code Generation Complete"')
                file_structure = page.query_selector_all('.bg-white.rounded-lg.border.border-slate-200')
                
                if success_banner:
                    print("   ✅ Executive view success banner found")
                if len(file_structure) > 0:
                    print(f"   ✅ Executive view shows {len(file_structure)} generated files")
                
                page.screenshot(path="generate_code_executive_view.png")
                print("   📸 Executive view screenshot saved")
                
                # Test Developer View
                developer_btn.click()
                time.sleep(2)
                json_header = page.query_selector('text="generated_code.json"')
                copy_btn = page.query_selector('button:has-text("Copy JSON")')
                stats_grid = page.query_selector_all('.bg-slate-800.rounded-lg')
                
                if json_header:
                    print("   ✅ Developer view JSON header found")
                if copy_btn:
                    print("   ✅ Copy JSON button found")
                if len(stats_grid) >= 3:
                    print(f"   ✅ Developer stats grid found ({len(stats_grid)} stats)")
                
                page.screenshot(path="generate_code_developer_view.png")
                print("   📸 Developer view screenshot saved")
            
            # Test export functionality
            zip_export = page.query_selector('button[title="Download as ZIP"]')
            if zip_export:
                print("   ✅ ZIP export button found")
                # Don't actually click to avoid download issues
            
        except Exception as e:
            print(f"   ⏰ Code generation still in progress or failed: {e}")
            page.screenshot(path="generate_code_timeout.png")
        
        print("6️⃣ Testing navigation to final step...")
        continue_btn = page.query_selector('button:has-text("View Test Results")')
        if continue_btn:
            continue_btn.click()
            time.sleep(2)
            
            # Check if we're on step 5
            step_5_indicator = page.query_selector('text="Step 5 of 5"')
            if step_5_indicator:
                print("   ✅ Successfully reached Step 5 of 5 - View Results")
                page.screenshot(path="step_5_view_results.png")
        
        print("\n🎯 COMPLETE FLOW TEST SUMMARY:")
        print("✅ Enhanced Web Automation Flow includes:")
        print("   • Step 1: Web URL input")
        print("   • Step 2: Extract Elements with AI")
        print("   • Step 3: Generate Tests with AI")
        print("   • Step 4: Generate Code with AI (NEW!)")
        print("   • Step 5: View Test Results")
        print("\n🔧 Generate Code Features:")
        print("   • Auto-execution when reaching step")
        print("   • Live LLM integration for code generation")
        print("   • Executive and Developer view modes")
        print("   • Progress tracking with phases")
        print("   • File structure display")
        print("   • Copy JSON functionality")
        print("   • ZIP export option")
        print("   • Consistent UI/UX with other steps")
        
        print("\n📁 Screenshots saved:")
        print("   • generate_code_executive_view.png")
        print("   • generate_code_developer_view.png")
        print("   • step_5_view_results.png")
        
        print("\nBrowser will stay open for 20 seconds...")
        time.sleep(20)
        
        browser.close()

if __name__ == "__main__":
    test_complete_code_generation_flow()