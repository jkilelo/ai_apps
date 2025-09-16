#!/usr/bin/env python3
"""
Stealth Browser Usage Examples
===============================
Comprehensive examples showing how different applications can use the
standalone stealth browser service.

Examples include:
1. LLM/AI Agent usage
2. Web scraping automation
3. Testing automation
4. Manual scripting
5. Data extraction
6. Form automation
7. Screenshot service
8. Multi-page workflows
"""

import asyncio
import json
import aiohttp
from pathlib import Path
from typing import List, Dict, Any
import sys

# Add browser directory to path
sys.path.insert(0, str(Path(__file__).parent))

from browser import StealthBrowserService, BrowserConfig

# ============================================================================
# Example 1: LLM/AI Agent Usage
# ============================================================================

async def llm_agent_example():
    """
    Example of how an LLM or AI agent would use the browser.
    The agent can browse websites, extract information, and interact with pages.
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: LLM/AI Agent Usage")
    print("="*60)
    
    # Configure browser for AI agent use
    config = BrowserConfig(
        headless=False,  # Show browser for demo
        stealth_level="maximum",
        enable_human_simulation=True,  # Simulate human behavior
        random_delays=True,
        human_typing_speed=(100, 300),  # Natural typing speed
    )
    
    browser = StealthBrowserService(config)
    await browser.start()
    
    # AI agent task: Research a topic on Wikipedia
    print("\n[AI Agent] Task: Research 'Artificial Intelligence' on Wikipedia")
    
    # Navigate to Wikipedia
    page = await browser.get_page("https://en.wikipedia.org")
    print("[AI Agent] Navigated to Wikipedia")
    
    # Search for the topic
    await browser.type(page, "input[name='search']", "Artificial Intelligence")
    # press enter
    await browser.press(page, "input[name='search']", "Enter")
    # await browser.click(page, "button[type='submit']")
    print("[AI Agent] Searched for 'Artificial Intelligence'")
    
    # Wait for results
    await browser.wait_for_selector(page, "#firstHeading")
    
    # Extract information
    article_title = await browser.evaluate(page, """
        document.querySelector('#firstHeading').textContent
    """)
    
    first_paragraph = await browser.evaluate(page, """
        document.querySelector('#mw-content-text p').textContent
    """)
    
    print(f"\n[AI Agent] Found article: {article_title}")
    print(f"[AI Agent] Summary: {first_paragraph[:200]}...")
    
    # Extract links for further research
    related_links = await browser.evaluate(page, """
        Array.from(document.querySelectorAll('#mw-content-text a'))
            .slice(0, 5)
            .map(a => ({ text: a.textContent, href: a.href }))
    """)
    
    print("\n[AI Agent] Related topics found:")
    for link in related_links:
        print(f"  - {link['text']}")
    
    await browser.stop()
    print("\n[AI Agent] Research completed")

# ============================================================================
# Example 2: Web Scraping Automation
# ============================================================================

async def web_scraping_example():
    """
    Example of using the browser for web scraping with stealth.
    Bypasses detection while extracting data from e-commerce sites.
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Web Scraping with Stealth")
    print("="*60)
    
    # Configure for scraping
    config = BrowserConfig(
        headless=True,  # Run headless for efficiency
        stealth_level="ultimate",  # Maximum stealth for protected sites
        enable_human_simulation=True,
        block_images=True,  # Faster loading
        block_media=True,
        viewport_width=1920,
        viewport_height=1080,
    )
    
    browser = StealthBrowserService(config)
    await browser.start()
    
    # Example: Scrape product information
    print("\n[Scraper] Starting product data extraction...")
    
    page = await browser.get_page("https://example.com/products")
    
    # Wait for products to load
    await browser.wait_for_selector(page, ".product-item", timeout=10000)
    
    # Extract product data
    products = await browser.evaluate(page, """
        Array.from(document.querySelectorAll('.product-item')).map(item => ({
            name: item.querySelector('.product-name')?.textContent?.trim(),
            price: item.querySelector('.product-price')?.textContent?.trim(),
            image: item.querySelector('img')?.src,
            link: item.querySelector('a')?.href
        }))
    """)
    
    print(f"[Scraper] Extracted {len(products)} products")
    
    # Save data
    output_file = Path("scraped_products.json")
    output_file.write_text(json.dumps(products, indent=2))
    print(f"[Scraper] Data saved to {output_file}")
    
    await browser.stop()
    print("[Scraper] Scraping completed successfully")

# ============================================================================
# Example 3: Automated Testing
# ============================================================================

async def automated_testing_example():
    """
    Example of using the browser for automated testing.
    Performs end-to-end tests with human-like interactions.
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Automated Testing")
    print("="*60)
    
    # Configure for testing
    config = BrowserConfig(
        headless=False,  # Show browser for test visibility
        stealth_level="enhanced",
        enable_human_simulation=True,
        slow_mo=500,  # Slow down for visibility
    )
    
    browser = StealthBrowserService(config)
    await browser.start()
    
    # Test scenario: User registration flow
    print("\n[Test] Starting user registration test...")
    
    page = await browser.get_page("https://example.com/register")
    
    # Fill registration form
    test_data = {
        "username": "testuser123",
        "email": "test@example.com",
        "password": "SecurePass123!",
    }
    
    print("[Test] Filling registration form...")
    await browser.type(page, "#username", test_data["username"])
    await browser.type(page, "#email", test_data["email"])
    await browser.type(page, "#password", test_data["password"])
    
    # Accept terms
    await browser.click(page, "#terms-checkbox")
    
    # Submit form
    await browser.click(page, "#submit-button")
    
    # Wait for success message
    success = await browser.wait_for_selector(page, ".success-message", timeout=5000)
    
    if success:
        message = await browser.evaluate(page, "document.querySelector('.success-message').textContent")
        print(f"[Test] ✓ Registration successful: {message}")
    else:
        print("[Test] ✗ Registration failed")
    
    # Take screenshot for test report
    await browser.screenshot(page, "test_registration_result.png")
    print("[Test] Screenshot saved for test report")
    
    await browser.stop()
    print("[Test] Test completed")

# ============================================================================
# Example 4: Form Automation
# ============================================================================

async def form_automation_example():
    """
    Example of automating complex form filling with file uploads.
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Form Automation")
    print("="*60)
    
    config = BrowserConfig(
        headless=False,
        stealth_level="maximum",
        enable_human_simulation=True,
        human_typing_speed=(80, 150),  # Natural typing
    )
    
    browser = StealthBrowserService(config)
    await browser.start()
    
    print("\n[Form] Starting job application automation...")
    
    page = await browser.get_page("https://example.com/apply")
    
    # Personal information
    print("[Form] Filling personal information...")
    await browser.type(page, "#first-name", "John")
    await browser.type(page, "#last-name", "Doe")
    await browser.type(page, "#email", "john.doe@example.com")
    await browser.type(page, "#phone", "+1-555-0123")
    
    # Address
    print("[Form] Filling address...")
    await browser.type(page, "#street", "123 Main St")
    await browser.type(page, "#city", "New York")
    
    # Select dropdown
    await browser.evaluate(page, """
        document.querySelector('#state').value = 'NY';
        document.querySelector('#state').dispatchEvent(new Event('change'));
    """)
    
    await browser.type(page, "#zip", "10001")
    
    # Work experience
    print("[Form] Adding work experience...")
    await browser.type(page, "#company", "Tech Corp")
    await browser.type(page, "#position", "Senior Developer")
    await browser.type(page, "#years", "5")
    
    # Skills checkboxes
    skills = ["Python", "JavaScript", "React", "Node.js"]
    for skill in skills:
        await browser.click(page, f"input[value='{skill}']")
    
    # Cover letter
    print("[Form] Writing cover letter...")
    cover_letter = """
    I am excited to apply for this position. With my extensive experience
    in web development and automation, I believe I would be a valuable
    addition to your team.
    """
    await browser.type(page, "#cover-letter", cover_letter)
    
    # File upload (if needed)
    # await page.set_input_files("#resume-upload", "resume.pdf")
    
    print("[Form] Form completed successfully")
    
    # Preview before submission
    await browser.screenshot(page, "form_preview.png")
    print("[Form] Preview saved")
    
    await browser.stop()

# ============================================================================
# Example 5: Data Extraction Pipeline
# ============================================================================

async def data_extraction_pipeline():
    """
    Example of a complete data extraction pipeline.
    Extracts data from multiple pages with pagination.
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: Data Extraction Pipeline")
    print("="*60)
    
    config = BrowserConfig(
        headless=True,
        stealth_level="maximum",
        enable_human_simulation=True,
        block_images=True,  # Optimize for speed
    )
    
    browser = StealthBrowserService(config)
    await browser.start()
    
    all_data = []
    page_num = 1
    max_pages = 5
    
    print("\n[Pipeline] Starting multi-page extraction...")
    
    while page_num <= max_pages:
        print(f"[Pipeline] Processing page {page_num}...")
        
        # Navigate to page
        url = f"https://example.com/listings?page={page_num}"
        page = await browser.get_page(url)
        
        # Wait for content
        await browser.wait_for_selector(page, ".listing-item")
        
        # Extract data from current page
        page_data = await browser.evaluate(page, """
            Array.from(document.querySelectorAll('.listing-item')).map(item => ({
                title: item.querySelector('.title')?.textContent?.trim(),
                description: item.querySelector('.description')?.textContent?.trim(),
                price: item.querySelector('.price')?.textContent?.trim(),
                location: item.querySelector('.location')?.textContent?.trim(),
                date: item.querySelector('.date')?.textContent?.trim(),
                url: item.querySelector('a')?.href
            }))
        """)
        
        all_data.extend(page_data)
        print(f"[Pipeline] Extracted {len(page_data)} items from page {page_num}")
        
        # Check for next page
        has_next = await browser.evaluate(page, """
            !!document.querySelector('.pagination .next:not(.disabled)')
        """)
        
        if not has_next or page_num >= max_pages:
            break
        
        page_num += 1
        
        # Human-like delay between pages
        await asyncio.sleep(2)
    
    print(f"\n[Pipeline] Extraction complete. Total items: {len(all_data)}")
    
    # Save results
    output_file = Path("extracted_data.json")
    output_file.write_text(json.dumps(all_data, indent=2))
    print(f"[Pipeline] Data saved to {output_file}")
    
    await browser.stop()

# ============================================================================
# Example 6: Screenshot Service
# ============================================================================

async def screenshot_service_example():
    """
    Example of using the browser as a screenshot service.
    Takes screenshots of multiple URLs with different viewports.
    """
    print("\n" + "="*60)
    print("EXAMPLE 6: Screenshot Service")
    print("="*60)
    
    # URLs to screenshot
    urls = [
        "https://github.com",
        "https://news.ycombinator.com",
        "https://example.com",
    ]
    
    # Different viewport sizes
    viewports = [
        {"name": "desktop", "width": 1920, "height": 1080},
        {"name": "tablet", "width": 768, "height": 1024},
        {"name": "mobile", "width": 375, "height": 667},
    ]
    
    for viewport in viewports:
        print(f"\n[Screenshot] Taking {viewport['name']} screenshots...")
        
        config = BrowserConfig(
            headless=True,
            stealth_level="basic",  # Basic stealth is enough for screenshots
            viewport_width=viewport["width"],
            viewport_height=viewport["height"],
        )
        
        browser = StealthBrowserService(config)
        await browser.start()
        
        for url in urls:
            # Get domain name for filename
            domain = url.replace("https://", "").replace("/", "_")
            filename = f"screenshot_{domain}_{viewport['name']}.png"
            
            page = await browser.get_page(url)
            
            # Wait for page to load
            await asyncio.sleep(2)
            
            # Take screenshot
            await browser.screenshot(page, filename)
            print(f"  ✓ {filename}")
        
        await browser.stop()
    
    print("\n[Screenshot] All screenshots completed")

# ============================================================================
# Example 7: API Client Usage
# ============================================================================

async def api_client_example():
    """
    Example of using the browser through its REST API.
    Shows how external applications can control the browser via HTTP.
    """
    print("\n" + "="*60)
    print("EXAMPLE 7: REST API Client")
    print("="*60)
    
    # Note: This requires the browser to be running as an API server:
    # python standalone_stealth_browser.py --server --port 9222
    
    api_url = "http://localhost:9222/api"
    
    print("\n[API Client] Connecting to browser API...")
    
    async with aiohttp.ClientSession() as session:
        # Check status
        async with session.get(f"{api_url}/status") as resp:
            status = await resp.json()
            print(f"[API Client] Browser status: {status['status']}")
            print(f"[API Client] Browser ID: {status['browser_id']}")
        
        # Navigate to a URL
        print("\n[API Client] Navigating to example.com...")
        async with session.post(
            f"{api_url}/navigate",
            json={"url": "https://example.com"}
        ) as resp:
            result = await resp.json()
            page_id = result['page_id']
            print(f"[API Client] Navigation successful. Page ID: {page_id}")
        
        # Type in search box
        print("[API Client] Typing in search box...")
        async with session.post(
            f"{api_url}/type",
            json={
                "page_id": page_id,
                "selector": "input[type='search']",
                "text": "test query"
            }
        ) as resp:
            result = await resp.json()
            print(f"[API Client] Typing: {result['success']}")
        
        # Click search button
        print("[API Client] Clicking search button...")
        async with session.post(
            f"{api_url}/click",
            json={
                "page_id": page_id,
                "selector": "button[type='submit']"
            }
        ) as resp:
            result = await resp.json()
            print(f"[API Client] Click: {result['success']}")
        
        # Take screenshot
        print("[API Client] Taking screenshot...")
        async with session.post(
            f"{api_url}/screenshot",
            json={"page_id": page_id}
        ) as resp:
            if resp.status == 200:
                screenshot = await resp.read()
                Path("api_screenshot.png").write_bytes(screenshot)
                print("[API Client] Screenshot saved")
        
        # Evaluate JavaScript
        print("[API Client] Evaluating JavaScript...")
        async with session.post(
            f"{api_url}/evaluate",
            json={
                "page_id": page_id,
                "script": "document.title"
            }
        ) as resp:
            result = await resp.json()
            print(f"[API Client] Page title: {result['result']}")
        
        # Get cookies
        print("[API Client] Getting cookies...")
        async with session.get(
            f"{api_url}/cookies",
            params={"page_id": page_id}
        ) as resp:
            result = await resp.json()
            print(f"[API Client] Cookies: {len(result['cookies'])} cookies found")
    
    print("\n[API Client] API operations completed")

# ============================================================================
# Example 8: Multi-Browser Coordination
# ============================================================================

async def multi_browser_example():
    """
    Example of coordinating multiple browser instances.
    Useful for parallel processing or comparison testing.
    """
    print("\n" + "="*60)
    print("EXAMPLE 8: Multi-Browser Coordination")
    print("="*60)
    
    # Create multiple browser instances with different configs
    browsers = []
    
    configs = [
        BrowserConfig(
            headless=True,
            stealth_level="basic",
            viewport_width=1920,
            viewport_height=1080,
        ),
        BrowserConfig(
            headless=True,
            stealth_level="maximum",
            viewport_width=1366,
            viewport_height=768,
        ),
        BrowserConfig(
            headless=True,
            stealth_level="ultimate",
            viewport_width=1280,
            viewport_height=720,
        ),
    ]
    
    print("\n[Multi] Starting 3 browser instances...")
    
    for i, config in enumerate(configs):
        browser = StealthBrowserService(config)
        await browser.start()
        browsers.append(browser)
        print(f"[Multi] Browser {i+1} started (stealth: {config.stealth_level})")
    
    # Test the same site with different configurations
    test_url = "https://example.com"
    
    print(f"\n[Multi] Testing {test_url} with all browsers...")
    
    tasks = []
    for i, browser in enumerate(browsers):
        async def test_browser(browser_instance, browser_num):
            page = await browser_instance.get_page(test_url)
            
            # Measure load time
            load_time = await browser_instance.evaluate(page, """
                performance.timing.loadEventEnd - performance.timing.navigationStart
            """)
            
            # Check if detected as bot
            page_source = await browser_instance.evaluate(page, "document.body.innerHTML")
            is_detected = "captcha" in page_source.lower() or "bot" in page_source.lower()
            
            return {
                "browser": browser_num,
                "load_time": load_time,
                "detected": is_detected,
                "stealth_level": browser_instance.config.stealth_level
            }
        
        task = test_browser(browser, i+1)
        tasks.append(task)
    
    # Run all tests in parallel
    results = await asyncio.gather(*tasks)
    
    print("\n[Multi] Test Results:")
    print("-" * 40)
    for result in results:
        print(f"Browser {result['browser']} ({result['stealth_level']}):")
        print(f"  Load time: {result['load_time']}ms")
        print(f"  Bot detected: {'Yes' if result['detected'] else 'No'}")
    
    # Cleanup all browsers
    print("\n[Multi] Stopping all browsers...")
    for browser in browsers:
        await browser.stop()
    
    print("[Multi] All browsers stopped")

# ============================================================================
# Example 9: Session Persistence
# ============================================================================

async def session_persistence_example():
    """
    Example of maintaining session across browser restarts.
    Useful for long-running automation that needs to preserve state.
    """
    print("\n" + "="*60)
    print("EXAMPLE 9: Session Persistence")
    print("="*60)
    
    cookies_file = Path("session_cookies.json")
    
    # First session - login and save cookies
    print("\n[Session] Starting first session - Login...")
    
    config = BrowserConfig(
        headless=False,
        stealth_level="maximum",
        persist_session=True,
        cookies_file=str(cookies_file),
    )
    
    browser = StealthBrowserService(config)
    await browser.start()
    
    # Navigate and login
    page = await browser.get_page("https://example.com/login")
    
    print("[Session] Logging in...")
    await browser.type(page, "#username", "demo_user")
    await browser.type(page, "#password", "demo_pass")
    await browser.click(page, "#login-button")
    
    # Wait for login to complete
    await asyncio.sleep(2)
    
    # Save cookies
    cookies = await browser.get_cookies(page)
    cookies_file.write_text(json.dumps(cookies, indent=2))
    print(f"[Session] Cookies saved ({len(cookies)} cookies)")
    
    await browser.stop()
    
    # Second session - restore cookies
    print("\n[Session] Starting second session - Restore...")
    
    browser2 = StealthBrowserService(config)
    await browser2.start()
    
    # Load saved cookies
    saved_cookies = json.loads(cookies_file.read_text())
    
    page2 = await browser2.get_page("https://example.com")
    await browser2.set_cookies(page2, saved_cookies)
    print(f"[Session] Cookies restored ({len(saved_cookies)} cookies)")
    
    # Navigate to protected area
    await browser2.navigate(page2, "https://example.com/dashboard")
    
    # Check if still logged in
    is_logged_in = await browser2.evaluate(page2, """
        !!document.querySelector('.user-menu')
    """)
    
    if is_logged_in:
        print("[Session] ✓ Successfully restored session - still logged in!")
    else:
        print("[Session] ✗ Session restoration failed")
    
    await browser2.stop()
    
    # Cleanup
    if cookies_file.exists():
        cookies_file.unlink()

# ============================================================================
# Main Runner
# ============================================================================

async def main():
    """Run all examples"""
    
    examples = [
        ("LLM/AI Agent", llm_agent_example),
        ("Web Scraping", web_scraping_example),
        ("Automated Testing", automated_testing_example),
        ("Form Automation", form_automation_example),
        ("Data Extraction Pipeline", data_extraction_pipeline),
        ("Screenshot Service", screenshot_service_example),
        # ("API Client", api_client_example),  # Requires server running
        ("Multi-Browser", multi_browser_example),
        ("Session Persistence", session_persistence_example),
    ]
    
    print("\n" + "="*60)
    print("STEALTH BROWSER USAGE EXAMPLES")
    print("="*60)
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    
    # Run examples
    for name, example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"\n[ERROR] Example '{name}' failed: {e}")
        
        # Pause between examples
        await asyncio.sleep(2)
    
    print("\n" + "="*60)
    print("ALL EXAMPLES COMPLETED")
    print("="*60)

if __name__ == "__main__":
    # Run all examples
    asyncio.run(main())
    
    # Or run specific example:
    # asyncio.run(llm_agent_example())
    # asyncio.run(web_scraping_example())
    # asyncio.run(automated_testing_example())
    # etc.