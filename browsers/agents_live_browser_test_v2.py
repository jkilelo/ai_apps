"""
LIVE TEST V2 - Enhanced browser automation with better action execution
Real browser, real LLM, real websites - NO MOCKS
"""

import asyncio
import sys
import os
import re
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright
from agents.langgraph_wrapper import get_langgraph_llm
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from typing import Dict, Any

print("=" * 80)
print("LIVE BROWSER TEST V2 - REAL BROWSER + REAL LLM")
print(f"Timestamp: {datetime.now()}")
print("=" * 80)

# Global browser instance
BROWSER = None
PAGE = None

# Browser tools
@tool
async def navigate_to_url(url: str) -> Dict[str, Any]:
    """Navigate to a URL."""
    global PAGE
    try:
        await PAGE.goto(url, wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(2)  # Let page settle
        title = await PAGE.title()
        current_url = PAGE.url
        print(f"  [NAV] Successfully navigated to: {current_url}")
        print(f"  [NAV] Page title: {title}")
        return {"success": True, "url": current_url, "title": title}
    except Exception as e:
        print(f"  [ERROR] Navigation failed: {e}")
        return {"success": False, "error": str(e)}

@tool
async def search_wikipedia(query: str) -> Dict[str, Any]:
    """Search on Wikipedia."""
    global PAGE
    try:
        # Navigate to Wikipedia search directly
        search_url = f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
        await PAGE.goto(search_url, wait_until='domcontentloaded')
        await asyncio.sleep(2)
        
        title = await PAGE.title()
        current_url = PAGE.url
        
        print(f"  [SEARCH] Searched for: {query}")
        print(f"  [SEARCH] Result page: {title}")
        
        return {"success": True, "query": query, "url": current_url, "title": title}
    except Exception as e:
        print(f"  [ERROR] Search failed: {e}")
        return {"success": False, "error": str(e)}

@tool
async def extract_main_content() -> Dict[str, Any]:
    """Extract main heading and first paragraph."""
    global PAGE
    try:
        # Get main heading
        heading = None
        try:
            h1 = await PAGE.query_selector('h1')
            if h1:
                heading = await h1.text_content()
        except:
            pass
        
        # Get first paragraph
        first_para = None
        try:
            # Wikipedia specific: get first paragraph after lead section
            para = await PAGE.query_selector('div.mw-parser-output > p:not(.mw-empty-elt)')
            if para:
                first_para = await para.text_content()
                first_para = first_para.strip()
        except:
            pass
        
        print(f"  [EXTRACT] Heading: {heading[:50] if heading else 'None'}...")
        print(f"  [EXTRACT] First paragraph: {first_para[:100] if first_para else 'None'}...")
        
        return {
            "success": True,
            "heading": heading,
            "first_paragraph": first_para
        }
    except Exception as e:
        print(f"  [ERROR] Extraction failed: {e}")
        return {"success": False, "error": str(e)}

@tool
async def take_screenshot() -> Dict[str, Any]:
    """Take a screenshot."""
    global PAGE
    try:
        filename = f"wikipedia_ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        await PAGE.screenshot(path=filename, full_page=False)
        print(f"  [SCREENSHOT] Saved as: {filename}")
        return {"success": True, "filename": filename}
    except Exception as e:
        print(f"  [ERROR] Screenshot failed: {e}")
        return {"success": False, "error": str(e)}

async def run_automated_task():
    """Run the complete automated task."""
    global BROWSER, PAGE
    
    print("\n[TASK] Starting automated browser task...")
    
    # Initialize browser
    print("[SETUP] Launching Playwright browser...")
    playwright = await async_playwright().start()
    BROWSER = await playwright.chromium.launch(
        headless=False,  # Show browser window
        args=['--disable-blink-features=AutomationControlled']
    )
    
    context = await BROWSER.new_context(
        viewport={'width': 1280, 'height': 720},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    PAGE = await context.new_page()
    print("[SETUP] Browser ready")
    
    # Initialize LLM
    print("\n[LLM] Initializing language model...")
    llm = get_langgraph_llm(temperature=0.3)
    
    # Task definition
    task = """
    I need to:
    1. Search Wikipedia for 'Artificial Intelligence'
    2. Extract the main heading and first paragraph
    3. Take a screenshot of the page
    """
    
    print(f"\n[TASK DESCRIPTION]{task}")
    
    results = {}
    
    try:
        # Step 1: Navigate to Wikipedia
        print("\n[STEP 1] Navigating to Wikipedia...")
        nav_result = await navigate_to_url.ainvoke({"url": "https://www.wikipedia.org"})
        results['navigation'] = nav_result
        
        # Step 2: Search for AI
        print("\n[STEP 2] Searching for Artificial Intelligence...")
        search_result = await search_wikipedia.ainvoke({"query": "Artificial Intelligence"})
        results['search'] = search_result
        
        # Step 3: Extract content
        print("\n[STEP 3] Extracting main content...")
        extract_result = await extract_main_content.ainvoke({})
        results['extraction'] = extract_result
        
        # Step 4: Take screenshot
        print("\n[STEP 4] Taking screenshot...")
        screenshot_result = await take_screenshot.ainvoke({})
        results['screenshot'] = screenshot_result
        
        # Step 5: Get LLM summary
        print("\n[STEP 5] Getting AI summary of findings...")
        
        summary_prompt = f"""
        I've automated a browser to search Wikipedia for Artificial Intelligence.
        Here's what I found:
        
        Page Title: {search_result.get('title', 'Unknown')}
        Main Heading: {extract_result.get('heading', 'Not found')}
        First Paragraph: {extract_result.get('first_paragraph', 'Not found')[:200]}...
        
        Please provide a brief summary of what we learned about AI from Wikipedia.
        """
        
        summary = llm.invoke([
            SystemMessage(content="You are summarizing information extracted from Wikipedia."),
            HumanMessage(content=summary_prompt)
        ])
        
        results['ai_summary'] = summary.content
        
    finally:
        # Always close browser
        print("\n[CLEANUP] Closing browser...")
        await BROWSER.close()
        await playwright.stop()
        print("[CLEANUP] Complete")
    
    return results

async def main():
    """Main execution."""
    print("\n" + "=" * 80)
    print("EXECUTING LIVE BROWSER AUTOMATION")
    print("=" * 80)
    
    # Run the task
    results = await run_automated_task()
    
    # Display results
    print("\n" + "=" * 80)
    print("LIVE TEST RESULTS")
    print("=" * 80)
    
    print("\n[RESULTS] Task Execution Summary:")
    print("-" * 40)
    
    # Check each step
    steps = ['navigation', 'search', 'extraction', 'screenshot']
    for step in steps:
        if step in results:
            success = results[step].get('success', False)
            status = "[OK]" if success else "[FAILED]"
            print(f"  {status} {step.capitalize()}")
    
    # Show extracted content
    if results.get('extraction', {}).get('success'):
        print("\n[EXTRACTED DATA]")
        print("-" * 40)
        heading = results['extraction'].get('heading', 'None')
        para = results['extraction'].get('first_paragraph', 'None')
        
        print(f"Heading: {heading}")
        print(f"\nFirst Paragraph (truncated):")
        if para and len(para) > 200:
            print(f"{para[:200]}...")
        else:
            print(para)
    
    # Show AI summary
    if 'ai_summary' in results:
        print("\n[AI SUMMARY]")
        print("-" * 40)
        print(results['ai_summary'])
    
    # Screenshot info
    if results.get('screenshot', {}).get('success'):
        print(f"\n[SCREENSHOT] Saved to: {results['screenshot']['filename']}")
    
    print("\n" + "=" * 80)
    print("LIVE TEST COMPLETED")
    print("This was a REAL test with:")
    print("  - Real browser automation (Playwright)")
    print("  - Real LLM reasoning (via langgraph_wrapper)")
    print("  - Real website interaction (Wikipedia)")
    print("  - Real data extraction and screenshot")
    print("=" * 80)

if __name__ == "__main__":
    print("\nInitializing live browser test...")
    asyncio.run(main())