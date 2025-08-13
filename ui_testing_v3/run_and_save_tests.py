#!/usr/bin/env python3
"""
Run tests on challenging sites and save results to JSON
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ultimate_stealth_browser import (
    UltimateStealthBrowser,
    StealthConfig,
    StealthLevel
)

async def test_sites_and_save():
    """Test sites and save results"""
    
    # Load challenging sites
    db_path = Path("latest_version/challenging_sites_database.json")
    with open(db_path, 'r') as f:
        database = json.load(f)
    
    # Select a variety of sites to test
    test_sites = [
        {"name": "Example.com", "url": "https://example.com", "category": "Testing", "difficulty": "low"},
        {"name": "Google", "url": "https://www.google.com", "category": "Search", "difficulty": "medium"},
        {"name": "Bot Test", "url": "https://bot.sannysoft.com", "category": "Testing", "difficulty": "medium"},
        {"name": "Cloudflare", "url": "https://www.cloudflare.com", "category": "Bot Protection", "difficulty": "high"},
        {"name": "Nike", "url": "https://www.nike.com", "category": "E-commerce", "difficulty": "very_high"},
        {"name": "Instagram", "url": "https://www.instagram.com", "category": "Social Media", "difficulty": "very_high"},
    ]
    
    # Configuration
    config = StealthConfig(
        level=StealthLevel.MAXIMUM,
        headless=False,
        detect_frameworks=True,
        detect_captcha=True,
        handle_cookies=True,
        bypass_cloudflare=True,
        bypass_f5_networks=True
    )
    
    results = {
        "test_info": {
            "timestamp": datetime.now().isoformat(),
            "stealth_level": config.level.value,
            "total_sites": len(test_sites),
            "browser": "Chrome (via platform_utils)",
            "platform": os.name
        },
        "sites_tested": [],
        "summary": {
            "successful": 0,
            "failed": 0,
            "total_elements": 0,
            "total_time": 0
        }
    }
    
    print(f"Starting tests on {len(test_sites)} sites...")
    print("="*60)
    
    async with UltimateStealthBrowser(config) as browser:
        for site in test_sites:
            print(f"\nTesting: {site['name']} ({site['difficulty']})")
            print(f"URL: {site['url']}")
            
            start_time = time.time()
            
            try:
                result = await browser.extract_elements(site['url'])
                
                site_result = {
                    "name": site['name'],
                    "url": site['url'],
                    "category": site['category'],
                    "difficulty": site['difficulty'],
                    "success": result.success,
                    "elements_extracted": len(result.elements),
                    "page_title": result.page_title,
                    "framework_detected": result.framework_detected,
                    "captcha_detected": result.captcha_detected,
                    "captcha_type": result.captcha_type,
                    "extraction_time": round(time.time() - start_time, 2),
                    "errors": result.errors,
                    "timestamp": datetime.now().isoformat()
                }
                
                if result.success:
                    print(f"  [SUCCESS] {len(result.elements)} elements in {site_result['extraction_time']}s")
                    results["summary"]["successful"] += 1
                    results["summary"]["total_elements"] += len(result.elements)
                else:
                    print(f"  [FAILED] {result.errors}")
                    results["summary"]["failed"] += 1
                
                results["summary"]["total_time"] += site_result['extraction_time']
                
            except Exception as e:
                print(f"  [ERROR] {e}")
                site_result = {
                    "name": site['name'],
                    "url": site['url'],
                    "category": site['category'],
                    "difficulty": site['difficulty'],
                    "success": False,
                    "elements_extracted": 0,
                    "extraction_time": round(time.time() - start_time, 2),
                    "errors": [str(e)],
                    "timestamp": datetime.now().isoformat()
                }
                results["summary"]["failed"] += 1
            
            results["sites_tested"].append(site_result)
            
            # Small delay between sites
            await asyncio.sleep(2)
    
    # Calculate success rate
    total = results["summary"]["successful"] + results["summary"]["failed"]
    results["summary"]["success_rate"] = round(
        (results["summary"]["successful"] / total * 100) if total > 0 else 0, 
        2
    )
    
    # Save results
    output_file = f"ultimate_stealth_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*60)
    print("TEST SUMMARY:")
    print(f"  Total sites: {total}")
    print(f"  Successful: {results['summary']['successful']}")
    print(f"  Failed: {results['summary']['failed']}")
    print(f"  Success rate: {results['summary']['success_rate']}%")
    print(f"  Total elements: {results['summary']['total_elements']}")
    print(f"  Total time: {results['summary']['total_time']:.2f}s")
    print(f"\nResults saved to: {output_file}")
    
    return output_file

if __name__ == "__main__":
    try:
        output_file = asyncio.run(test_sites_and_save())
        print(f"\n[COMPLETE] Test results saved to: {output_file}")
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Test cancelled by user")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()