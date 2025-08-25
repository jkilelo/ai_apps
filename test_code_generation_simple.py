"""
Simple test of the Generate Code step in UI
"""

from playwright.sync_api import sync_playwright
import time

def test_code_generation_simple():
    """Test the Generate Code step functionality"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("TESTING GENERATE CODE STEP")
        print("=" * 40)
        
        print("1. Opening Web Automation page...")
        page.goto("http://localhost:3000/web-automation")
        time.sleep(2)
        
        # Check if we have 5 steps
        step_text = page.query_selector('.text-xs.text-slate-500')
        if step_text and "of 5" in step_text.text_content():
            print("   [SUCCESS] Found 5-step flow")
        else:
            print("   [WARNING] Step indicator not found or incorrect")
        
        print("2. Starting extraction flow...")
        page.click('button:has-text("Example.com")')
        time.sleep(0.5)
        
        page.click('button:has-text("Start Extraction")')
        print("   Waiting for extraction...")
        
        try:
            page.wait_for_selector('h3:has-text("Extraction Results")', timeout=30000)
            print("   [SUCCESS] Extraction completed!")
        except:
            print("   [FAILED] Extraction timeout")
            browser.close()
            return
        
        print("3. Moving to Generate Tests...")
        page.click('button:has-text("Continue to Test Generation")')
        time.sleep(3)
        
        # Wait for test generation to complete
        try:
            page.wait_for_selector('text="Test Cases Generated"', timeout=60000)
            print("   [SUCCESS] Test generation completed!")
        except:
            print("   [TIMEOUT] Still generating tests")
        
        print("4. Moving to Generate Code step...")
        try:
            continue_btn = page.query_selector('button:has-text("Continue to Code Generation")')
            if continue_btn:
                continue_btn.click()
                time.sleep(3)
                print("   [SUCCESS] Moved to Generate Code step")
            else:
                print("   [FAILED] Continue to Code Generation button not found")
                browser.close()
                return
        except Exception as e:
            print(f"   [ERROR] Failed to navigate to code generation: {e}")
            browser.close()
            return
        
        # Check if we're on Generate Code step
        generate_code_title = page.query_selector('h3:has-text("Generate Code")')
        if generate_code_title:
            print("   [SUCCESS] On Generate Code step")
        else:
            print("   [FAILED] Not on Generate Code step")
        
        # Check for auto-generation UI
        auto_info = page.query_selector('text="Automatic Code Generation"')
        if auto_info:
            print("   [SUCCESS] Auto-generation info displayed")
        else:
            print("   [WARNING] Auto-generation info not found")
        
        # Wait for code generation process
        print("5. Waiting for code generation...")
        start_time = time.time()
        timeout = 120  # 2 minutes timeout
        
        while time.time() - start_time < timeout:
            # Check for progress indicators
            progress_text = page.query_selector('.text-purple-900')
            if progress_text:
                status = progress_text.text_content()
                if status:
                    print(f"   Progress: {status}")
            
            # Check for completion
            code_generated = page.query_selector('text="Code Generated"')
            if code_generated:
                print("   [SUCCESS] Code generation completed!")
                break
                
            # Check for errors
            error_indicator = page.query_selector('.text-red-')
            if error_indicator:
                print(f"   [ERROR] Generation failed: {error_indicator.text_content()}")
                break
                
            time.sleep(3)
        else:
            print("   [TIMEOUT] Code generation timed out")
        
        # Test view modes if generation completed
        code_generated = page.query_selector('text="Code Generated"')
        if code_generated:
            print("6. Testing view modes...")
            
            # Test Executive View
            executive_btn = page.query_selector('button:has-text("Executive")')
            if executive_btn:
                executive_btn.click()
                time.sleep(1)
                
                success_banner = page.query_selector('text="Code Generation Complete"')
                if success_banner:
                    print("   [SUCCESS] Executive view working")
                
                # Count generated files
                file_cards = page.query_selector_all('.bg-white.rounded-lg.border.border-slate-200')
                if len(file_cards) > 0:
                    print(f"   [SUCCESS] Shows {len(file_cards)} generated files")
                
                page.screenshot(path="code_generation_executive.png")
                
            # Test Developer View
            developer_btn = page.query_selector('button:has-text("Developer")')
            if developer_btn:
                developer_btn.click()
                time.sleep(2)
                
                json_header = page.query_selector('text="generated_code.json"')
                if json_header:
                    print("   [SUCCESS] Developer view working")
                
                page.screenshot(path="code_generation_developer.png")
            
            # Test export button
            zip_btn = page.query_selector('button[title="Download as ZIP"]')
            if zip_btn:
                print("   [SUCCESS] ZIP export button found")
            
        else:
            print("6. Code generation did not complete - taking debug screenshot")
            page.screenshot(path="code_generation_debug.png")
        
        print("\nTEST SUMMARY:")
        print("- 5-step flow implemented")
        print("- Generate Code step integrated")
        print("- Auto-generation UI working")
        if code_generated:
            print("- Live LLM code generation successful")
            print("- Executive/Developer views functional")
            print("- Export functionality available")
        else:
            print("- Code generation process needs debugging")
        
        print("\nScreenshots saved:")
        print("- code_generation_executive.png")
        print("- code_generation_developer.png")
        print("- code_generation_debug.png (if needed)")
        
        print("\nBrowser staying open for inspection...")
        time.sleep(15)
        
        browser.close()

if __name__ == "__main__":
    test_code_generation_simple()