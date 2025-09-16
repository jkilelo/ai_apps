"""
Debug Executive View Data
"""

from playwright.sync_api import sync_playwright
import time

def test_executive_debug():
    """Debug the Executive view data"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"Console: {msg.text}"))
        
        print("1. Navigating to Web Automation page...")
        page.goto("http://localhost:3000/web-automation")
        time.sleep(2)
        
        print("2. Selecting GitHub...")
        page.click('button:has-text("GitHub")')
        time.sleep(0.5)
        
        print("3. Starting extraction...")
        page.click('button:has-text("Start Extraction")')
        
        # Wait for results
        page.wait_for_selector('h3:has-text("Extraction Results")', timeout=30000)
        time.sleep(3)
        
        # Add console log to check data
        print("4. Checking extracted data structure...")
        result = page.evaluate("""
            () => {
                const reactFiber = document.querySelector('[class*="space-y-4"]')?._owner || 
                                  document.querySelector('[class*="space-y-4"]')?.parentElement?._owner;
                
                // Try to find React component data
                const allElements = Array.from(document.querySelectorAll('*'));
                for (let el of allElements) {
                    for (let key in el) {
                        if (key.startsWith('__reactInternalInstance') || key.startsWith('__reactFiber')) {
                            const fiber = el[key];
                            if (fiber?.memoizedProps?.extractedElements) {
                                const data = fiber.memoizedProps.extractedElements;
                                console.log('Found extractedElements:', data);
                                return {
                                    hasLlmAnalysis: !!data.llm_analysis,
                                    hasCriticalFlows: !!data.llm_analysis?.critical_flows,
                                    criticalFlowsLength: data.llm_analysis?.critical_flows?.length || 0,
                                    hasElementsByCategory: !!data.elements_by_category,
                                    categories: Object.keys(data.elements_by_category || {}),
                                    llmAnalysisKeys: Object.keys(data.llm_analysis || {})
                                };
                            }
                        }
                    }
                }
                return { error: 'Could not find React data' };
            }
        """)
        
        print("5. Data structure found:")
        print(f"   - Has LLM Analysis: {result.get('hasLlmAnalysis', False)}")
        print(f"   - Has Critical Flows: {result.get('hasCriticalFlows', False)}")
        print(f"   - Critical Flows Length: {result.get('criticalFlowsLength', 0)}")
        print(f"   - Has Elements by Category: {result.get('hasElementsByCategory', False)}")
        print(f"   - Categories: {result.get('categories', [])}")
        print(f"   - LLM Analysis Keys: {result.get('llmAnalysisKeys', [])}")
        
        # Check if Critical Test Scenarios section exists
        critical_section = page.query_selector('h4:has-text("Critical Test Scenarios")')
        print(f"\n6. Critical Test Scenarios section visible: {critical_section is not None}")
        
        # Scroll and take screenshot
        page.evaluate('window.scrollBy(0, 500)')
        time.sleep(1)
        page.screenshot(path="executive_debug.png", full_page=True)
        print("\n7. Screenshot saved as executive_debug.png")
        
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    test_executive_debug()