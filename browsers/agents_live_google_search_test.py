"""
Live Google Search Test - Real browser with advanced search techniques
"""

import asyncio
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright
from agents.langgraph_wrapper import get_langgraph_llm
from langchain_core.messages import HumanMessage, SystemMessage

print("=" * 80)
print("LIVE GOOGLE ADVANCED SEARCH TEST")
print(f"Timestamp: {datetime.now()}")
print("=" * 80)


async def perform_advanced_search():
    """Perform real advanced Google searches."""
    
    # Initialize LLM
    print("\n[LLM] Initializing AI model...")
    llm = get_langgraph_llm(temperature=0.3)
    
    # Launch browser
    print("[BROWSER] Launching browser...")
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=False,  # Show browser
        args=['--disable-blink-features=AutomationControlled']
    )
    
    context = await browser.new_context(
        viewport={'width': 1280, 'height': 720},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    page = await context.new_page()
    
    try:
        # Navigate to Google
        print("\n[STEP 1] Navigating to Google...")
        await page.goto("https://www.google.com", wait_until='domcontentloaded')
        await asyncio.sleep(2)
        
        # Example 1: Site-specific search with exact phrase
        print("\n[SEARCH 1] Site-specific search with exact phrase")
        query1 = '"machine learning" site:github.com after:2024-01-01'
        print(f"  Query: {query1}")
        
        search_box = await page.query_selector('textarea[name="q"], input[name="q"]')
        await search_box.fill(query1)
        await page.keyboard.press('Enter')
        
        # Wait for results to load
        try:
            await page.wait_for_selector('div#search', timeout=10000)
            await asyncio.sleep(2)  # Extra wait for stability
        except:
            print("  [WARNING] Search results may not have loaded fully")
        
        # Extract results
        results1 = []
        try:
            result_elements = await page.query_selector_all('div.g')
            for elem in result_elements[:3]:
                try:
                    title = await elem.query_selector('h3')
                    if title:
                        title_text = await title.text_content()
                        results1.append(title_text)
                except:
                    continue
        except Exception as e:
            print(f"  [ERROR] Could not extract results: {e}")
        
        print(f"  Found {len(results1)} results:")
        for r in results1:
            print(f"    - {r[:80]}...")
        
        # Clear search for next query
        await page.goto("https://www.google.com")
        await asyncio.sleep(2)
        
        # Example 2: Competitive analysis search
        print("\n[SEARCH 2] Competitive analysis with OR operator")
        query2 = '("ChatGPT" OR "Claude" OR "Gemini") "vs" comparison 2024'
        print(f"  Query: {query2}")
        
        search_box = await page.query_selector('textarea[name="q"], input[name="q"]')
        await search_box.fill(query2)
        await page.keyboard.press('Enter')
        
        # Wait for results
        try:
            await page.wait_for_selector('div#search', timeout=10000)
            await asyncio.sleep(2)
        except:
            print("  [WARNING] Search results may not have loaded fully")
        
        # Extract results
        results2 = []
        try:
            result_elements = await page.query_selector_all('div.g')
            for elem in result_elements[:3]:
                try:
                    title = await elem.query_selector('h3')
                    snippet = await elem.query_selector('div.VwiC3b')
                    if title:
                        title_text = await title.text_content()
                        snippet_text = await snippet.text_content() if snippet else ""
                        results2.append({"title": title_text, "snippet": snippet_text[:100]})
                except:
                    continue
        except Exception as e:
            print(f"  [ERROR] Could not extract results: {e}")
        
        print(f"  Found {len(results2)} comparison results:")
        for r in results2:
            print(f"    - {r['title'][:60]}...")
            if r['snippet']:
                print(f"      {r['snippet']}...")
        
        # Clear for next search
        await page.goto("https://www.google.com")
        await asyncio.sleep(2)
        
        # Example 3: File type search
        print("\n[SEARCH 3] PDF research papers search")
        query3 = '"artificial intelligence" "healthcare" filetype:pdf site:edu'
        print(f"  Query: {query3}")
        
        search_box = await page.query_selector('textarea[name="q"], input[name="q"]')
        await search_box.fill(query3)
        await page.keyboard.press('Enter')
        
        # Wait for results
        try:
            await page.wait_for_selector('div#search', timeout=10000)
            await asyncio.sleep(2)
        except:
            print("  [WARNING] Search results may not have loaded fully")
        
        # Count PDF results
        pdf_count = 0
        result_elements = await page.query_selector_all('div.g')
        for elem in result_elements[:5]:
            try:
                link = await elem.query_selector('a')
                if link:
                    href = await link.get_attribute('href')
                    if href and '.pdf' in href.lower():
                        pdf_count += 1
                        title = await elem.query_selector('h3')
                        if title:
                            title_text = await title.text_content()
                            print(f"    [PDF] {title_text[:70]}...")
            except:
                continue
        
        print(f"  Found {pdf_count} PDF documents")
        
        # AI Analysis
        print("\n[AI ANALYSIS] Getting insights from search results...")
        
        analysis_prompt = f"""Based on these Google searches performed:

1. Site-specific: "{query1}"
   - Found {len(results1)} GitHub repositories about machine learning

2. Competitive: "{query2}"  
   - Found {len(results2)} comparison articles

3. Academic: "{query3}"
   - Found {pdf_count} PDF research papers

What insights can you provide about:
1. The current state of machine learning projects on GitHub
2. How AI assistants are being compared in 2024
3. Academic research trends in AI healthcare

Provide a brief analysis."""
        
        response = llm.invoke([
            SystemMessage(content="You are analyzing Google search results."),
            HumanMessage(content=analysis_prompt)
        ])
        
        print("\n[AI INSIGHTS]")
        print("-" * 40)
        print(response.content[:800])
        
        # Take screenshot of last search
        print("\n[SCREENSHOT] Capturing search results...")
        filename = f"google_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        await page.screenshot(path=filename)
        print(f"  Saved: {filename}")
        
    finally:
        print("\n[CLEANUP] Closing browser...")
        await browser.close()
        await playwright.stop()
    
    print("\n" + "=" * 80)
    print("ADVANCED SEARCH TECHNIQUES DEMONSTRATED:")
    print("=" * 80)
    print("1. Site-specific search with date filter (site: after:)")
    print("2. OR operator for competitive analysis")  
    print("3. File type search for academic papers (filetype: site:)")
    print("4. Exact phrase matching with quotes")
    print("5. AI analysis of search results")
    print("\nAll searches performed on LIVE Google with REAL browser!")


if __name__ == "__main__":
    print("\nStarting live Google advanced search test...")
    print("This will open a real browser and perform actual searches.")
    asyncio.run(perform_advanced_search())