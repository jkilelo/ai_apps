#!/usr/bin/env python3
"""
Test Enhanced Stealth Browser
==============================
Tests the updated stealth browser against detection sites.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from browser import StealthBrowserService, BrowserConfig

async def test_github():
    """Test against GitHub which was detecting us before"""
    print("\n" + "="*60)
    print("TESTING ENHANCED STEALTH ON GITHUB")
    print("="*60)
    
    config = BrowserConfig(
        headless=False,
        stealth_level="ultimate",
        enable_human_simulation=True,
        disable_runtime_enable=True,
        patch_cdp_detection=True,
        randomize_fingerprints=True,
    )
    
    browser = StealthBrowserService(config)
    
    try:
        await browser.start()
        print("[INFO] Browser started with enhanced stealth")
        
        # Test GitHub
        print("\n[TEST] Navigating to GitHub...")
        page = await browser.get_page("https://github.com")
        
        # Wait a bit for any detection to trigger
        await asyncio.sleep(3)
        
        # Check if we're detected
        is_detected = await browser._check_detection(page)
        
        if is_detected:
            print("[WARN] Still detected by GitHub, but attempting bypass...")
            await browser._attempt_bypass(page, "https://github.com")
            
            # Check again
            await asyncio.sleep(2)
            is_detected = await browser._check_detection(page)
            
            if is_detected:
                print("[FAIL] GitHub still detecting the browser")
            else:
                print("[PASS] Bypass successful!")
        else:
            print("[PASS] Not detected by GitHub!")
        
        # Check page title to verify we're on the right page
        title = await browser.evaluate(page, "document.title")
        print(f"[INFO] Page title: {title}")
        
        # Check for specific GitHub elements
        has_github_elements = await browser.evaluate(page, """
            !!document.querySelector('.Header') || 
            !!document.querySelector('[aria-label="Homepage"]')
        """)
        
        if has_github_elements:
            print("[PASS] GitHub page loaded successfully")
        else:
            print("[WARN] GitHub page may not have loaded correctly")
        
        # Take screenshot
        await browser.screenshot(page, "github_test.png")
        print("[INFO] Screenshot saved as github_test.png")
        
        await browser.stop()
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        await browser.stop()

async def test_detection_sites():
    """Test against known detection test sites"""
    print("\n" + "="*60)
    print("TESTING DETECTION SITES")
    print("="*60)
    
    config = BrowserConfig(
        headless=False,
        stealth_level="ultimate",
        enable_human_simulation=True,
        disable_runtime_enable=True,
        patch_cdp_detection=True,
    )
    
    browser = StealthBrowserService(config)
    
    test_sites = [
        {
            "name": "Sannysoft Bot Test",
            "url": "https://bot.sannysoft.com/",
            "check_selector": "td.success",
            "description": "Comprehensive bot detection tests"
        },
        {
            "name": "Intoli Headless Test",
            "url": "https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html",
            "check_selector": ".result-box.success",
            "description": "Chrome headless detection"
        },
    ]
    
    try:
        await browser.start()
        
        for site in test_sites:
            print(f"\n[TEST] {site['name']}")
            print(f"  URL: {site['url']}")
            print(f"  {site['description']}")
            
            page = await browser.get_page(site['url'])
            await asyncio.sleep(3)
            
            # Check for success indicators
            if site['check_selector']:
                success = await browser.evaluate(page, f"""
                    !!document.querySelector('{site['check_selector']}')
                """)
                
                if success:
                    print(f"  [PASS] Not detected!")
                else:
                    print(f"  [FAIL] Detected as bot")
            
            # Check specific properties
            webdriver = await browser.evaluate(page, "navigator.webdriver")
            chrome = await browser.evaluate(page, "!!window.chrome")
            plugins = await browser.evaluate(page, "navigator.plugins.length")
            
            print(f"  navigator.webdriver: {webdriver}")
            print(f"  window.chrome exists: {chrome}")
            print(f"  plugins count: {plugins}")
            
            # Take screenshot
            filename = f"detection_{site['name'].replace(' ', '_').lower()}.png"
            await browser.screenshot(page, filename)
            print(f"  Screenshot: {filename}")
        
        await browser.stop()
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        await browser.stop()

async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("ENHANCED STEALTH BROWSER TEST")
    print("="*60)
    print("\nThis test checks if the enhanced stealth features")
    print("successfully bypass detection on problematic sites.")
    
    # Test GitHub first
    await test_github()
    
    # Small delay
    await asyncio.sleep(2)
    
    # Test detection sites
    await test_detection_sites()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("\nCheck the screenshots to verify results.")
    print("Green/success indicators mean the browser is undetected.")

if __name__ == "__main__":
    asyncio.run(main())