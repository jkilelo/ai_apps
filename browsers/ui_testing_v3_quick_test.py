#!/usr/bin/env python3
"""
Quick test of Ultimate Stealth Browser with a few challenging sites
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ultimate_stealth_browser import (
    UltimateStealthBrowser,
    StealthConfig,
    StealthLevel
)

async def test_site(url: str, name: str):
    """Test a single site"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print('='*60)
    
    config = StealthConfig(
        level=StealthLevel.MAXIMUM,
        headless=False,
        enable_human_typing=True,
        enable_human_mouse=True,
        detect_frameworks=True,
        detect_captcha=True,
        handle_cookies=True,
        bypass_cloudflare=True,
        bypass_f5_networks=True
    )
    
    try:
        async with UltimateStealthBrowser(config) as browser:
            print("Browser initialized successfully")
            
            result = await browser.extract_elements(url)
            
            if result.success:
                print(f"[SUCCESS] Extracted {len(result.elements)} elements")
                print(f"  - Page title: {result.page_title}")
                print(f"  - Framework: {result.framework_detected or 'None'}")
                print(f"  - CAPTCHA: {'Yes - ' + result.captcha_type if result.captcha_detected else 'No'}")
                print(f"  - Time: {result.extraction_time:.2f}s")
                
                # Show first 3 elements
                if result.elements:
                    print("\nFirst 3 elements:")
                    for i, elem in enumerate(result.elements[:3], 1):
                        print(f"  {i}. {elem.tag_name} - {elem.element_type.value}")
                        if elem.text_content:
                            print(f"     Text: {elem.text_content[:50]}...")
            else:
                print(f"[FAILED] Extraction failed")
                if result.errors:
                    for error in result.errors:
                        print(f"  Error: {error}")
    
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run quick tests"""
    print("ULTIMATE STEALTH BROWSER - QUICK TEST")
    print("="*60)
    
    # Test sites (easier ones first)
    test_sites = [
        ("https://example.com", "Example.com (Simple site)"),
        ("https://www.google.com", "Google (Medium difficulty)"),
        ("https://bot.sannysoft.com", "Bot Detection Test"),
        ("https://www.cloudflare.com", "Cloudflare (High protection)"),
    ]
    
    for url, name in test_sites:
        await test_site(url, name)
        await asyncio.sleep(2)  # Delay between sites
    
    print("\n" + "="*60)
    print("All tests completed!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted")
    except Exception as e:
        print(f"Test failed: {e}")