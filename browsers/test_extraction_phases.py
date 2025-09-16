"""
Test Extraction Progress Phases
"""

from playwright.sync_api import sync_playwright
import time

def test_extraction_phases():
    """Test the extraction progress phases display"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("1. Navigating to Web Automation page...")
        page.goto("http://localhost:3000/web-automation")
        time.sleep(2)
        
        print("2. Selecting Wikipedia for slower extraction...")
        page.click('button:has-text("Wikipedia")')
        time.sleep(0.5)
        
        print("3. Starting extraction to see phases...")
        page.click('button:has-text("Start Extraction")')
        
        # Capture screenshots of different phases
        phases = []
        for i in range(8):
            time.sleep(2)
            phase_text = page.query_selector('.text-blue-900')
            if phase_text:
                phase = phase_text.text_content()
                if phase and phase not in phases:
                    phases.append(phase)
                    print(f"   Phase {i+1}: {phase}")
                    page.screenshot(path=f"phase_{i+1}.png")
        
        # Wait for completion
        try:
            page.wait_for_selector('h3:has-text("Extraction Results")', timeout=30000)
            print("\n4. Extraction completed successfully!")
        except:
            print("\n4. Extraction still in progress or failed")
        
        # Final screenshot
        page.screenshot(path="extraction_phases_complete.png")
        print("\n5. Screenshots saved:")
        print("   - phase_*.png (individual phases)")
        print("   - extraction_phases_complete.png (final result)")
        
        print("\nBrowser will stay open for inspection...")
        time.sleep(5)
        
        browser.close()

if __name__ == "__main__":
    test_extraction_phases()