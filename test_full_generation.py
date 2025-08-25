"""
Test the Complete Test Generation Flow in UI
"""

from playwright.sync_api import sync_playwright
import time

def test_full_generation():
    """Test the complete test generation flow in UI"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("1. Navigating to Web Automation page...")
        page.goto("http://localhost:3000/web-automation")
        time.sleep(2)
        
        print("2. Selecting Example.com for faster testing...")
        page.click('button:has-text("Example.com")')
        time.sleep(0.5)
        
        print("3. Starting extraction...")
        page.click('button:has-text("Start Extraction")')
        
        # Wait for extraction to complete
        print("   Waiting for extraction to complete...")
        try:
            page.wait_for_selector('h3:has-text("Extraction Results")', timeout=30000)
            print("   [SUCCESS] Extraction completed!")
            time.sleep(2)
        except:
            print("   [FAILED] Extraction failed or timed out")
            browser.close()
            return
        
        print("4. Moving to test generation...")
        # Click Continue to Test Generation button
        continue_button = page.query_selector('button:has-text("Continue to Test Generation")')
        if continue_button:
            continue_button.click()
            print("   [SUCCESS] Clicked Continue to Test Generation")
            time.sleep(2)
        else:
            print("   [FAILED] Continue button not found")
        
        # Take screenshot of test generation UI
        page.screenshot(path="test_gen_1_categories.png")
        print("5. Test categories selection captured")
        
        # Click Generate Test Cases with AI
        print("6. Starting test generation with AI...")
        generate_button = page.query_selector('button:has-text("Generate Test Cases with AI")')
        if generate_button:
            generate_button.click()
            print("   [SUCCESS] Test generation started!")
            
            # Capture progress screenshots
            for i in range(5):
                time.sleep(3)
                progress_text = page.query_selector('.text-purple-900')
                if progress_text:
                    status = progress_text.text_content()
                    print(f"   Phase {i+1}: {status}")
                page.screenshot(path=f"test_gen_2_progress_{i+1}.png")
            
            # Wait for completion
            print("7. Waiting for test generation to complete...")
            try:
                page.wait_for_selector('text="Test Cases Generated"', timeout=60000)
                print("   [SUCCESS] Test generation completed successfully!")
                time.sleep(2)
                
                # Capture the results
                page.screenshot(path="test_gen_3_results.png")
                
                # Check for generated features
                features = page.query_selector_all('.bg-white.rounded-lg.border.border-slate-200')
                print(f"   Generated {len(features)} test features")
                
                # Try to download the tests
                download_button = page.query_selector('button:has(.h-3.w-3)')
                if download_button:
                    download_button.click()
                    print("   [SUCCESS] Triggered test download")
                
            except Exception as e:
                print(f"   [FAILED] Test generation failed or timed out: {e}")
                page.screenshot(path="test_gen_error.png")
        else:
            print("   [FAILED] Generate button not found")
        
        print("\n8. Test complete! Screenshots saved:")
        print("   - test_gen_1_categories.png")
        print("   - test_gen_2_progress_*.png")
        print("   - test_gen_3_results.png")
        
        print("\nBrowser will stay open for manual inspection...")
        time.sleep(15)
        
        browser.close()

if __name__ == "__main__":
    test_full_generation()