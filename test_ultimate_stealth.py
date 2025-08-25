#!/usr/bin/env python3
"""
Test script for Ultimate Stealth Browser with challenging sites.
Tests against sites from challenging_sites_database.json
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ultimate_stealth_browser import (
    UltimateStealthBrowser,
    StealthConfig,
    StealthLevel,
    ExtractionResult
)

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text: str, color: str = Colors.RESET, bold: bool = False):
    """Print colored text to terminal"""
    # Replace unicode characters with ASCII equivalents for Windows compatibility
    text = text.replace('✓', '[OK]').replace('✗', '[FAIL]').replace('⚠', '[WARN]')
    
    if bold:
        print(f"{Colors.BOLD}{color}{text}{Colors.RESET}")
    else:
        print(f"{color}{text}{Colors.RESET}")

def print_header(text: str):
    """Print a formatted header"""
    print()
    print_colored("=" * 80, Colors.CYAN)
    print_colored(text.center(80), Colors.CYAN, bold=True)
    print_colored("=" * 80, Colors.CYAN)
    print()

def print_site_header(site_name: str, url: str, difficulty: str):
    """Print site test header"""
    print()
    print_colored("-" * 60, Colors.BLUE)
    print_colored(f"Testing: {site_name}", Colors.BLUE, bold=True)
    print_colored(f"URL: {url}", Colors.BLUE)
    print_colored(f"Difficulty: {difficulty.upper()}", 
                 Colors.RED if difficulty in ['very_high', 'extreme'] else Colors.YELLOW)
    print_colored("-" * 60, Colors.BLUE)

async def test_single_site(browser: UltimateStealthBrowser, site: dict) -> dict:
    """Test a single site and return results"""
    start_time = time.time()
    result = {
        'id': site['id'],
        'name': site['name'],
        'url': site['url'],
        'category': site['category'],
        'difficulty': site['difficulty'],
        'protection_system': site['protection_system'],
        'success': False,
        'elements_extracted': 0,
        'extraction_time': 0,
        'error': None,
        'framework_detected': None,
        'captcha_detected': False,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        # Extract elements
        extraction_result = await browser.extract_elements(site['url'])
        
        # Update result
        result['success'] = extraction_result.success
        result['elements_extracted'] = len(extraction_result.elements)
        result['extraction_time'] = round(time.time() - start_time, 2)
        result['framework_detected'] = extraction_result.framework_detected
        result['captcha_detected'] = extraction_result.captcha_detected
        
        if extraction_result.errors:
            result['error'] = '; '.join(extraction_result.errors)
        
        # Print results
        if result['success']:
            print_colored(f"✓ SUCCESS", Colors.GREEN, bold=True)
            print(f"  Elements: {result['elements_extracted']}")
            print(f"  Time: {result['extraction_time']}s")
            if result['framework_detected']:
                print(f"  Framework: {result['framework_detected']}")
            if result['captcha_detected']:
                print_colored(f"  ⚠ CAPTCHA detected: {extraction_result.captcha_type}", Colors.YELLOW)
        else:
            print_colored(f"✗ FAILED", Colors.RED, bold=True)
            if result['error']:
                print(f"  Error: {result['error']}")
        
    except Exception as e:
        result['error'] = str(e)
        result['extraction_time'] = round(time.time() - start_time, 2)
        print_colored(f"✗ EXCEPTION", Colors.RED, bold=True)
        print(f"  Error: {e}")
    
    return result

async def test_sites(sites_to_test: list, stealth_level: StealthLevel = StealthLevel.MAXIMUM):
    """Test multiple sites with the ultimate stealth browser"""
    
    print_header("ULTIMATE STEALTH BROWSER TEST")
    print(f"Testing {len(sites_to_test)} sites")
    print(f"Stealth Level: {stealth_level.value}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create configuration
    config = StealthConfig(
        level=stealth_level,
        headless=False,  # Run with GUI for testing
        enable_human_typing=True,
        enable_human_mouse=True,
        enable_human_scrolling=True,
        enable_micro_behaviors=True,
        detect_frameworks=True,
        detect_captcha=True,
        handle_cookies=True,
        parallel_extraction=True,
        bypass_cloudflare=True,
        bypass_f5_networks=True,
        bypass_shape_security=True,
        bypass_datadome=True,
        bypass_kasada=True,
        bypass_perimeter_x=True
    )
    
    # Test results
    all_results = []
    successful = 0
    failed = 0
    
    # Initialize browser
    print()
    print_colored("Initializing Ultimate Stealth Browser...", Colors.CYAN)
    
    async with UltimateStealthBrowser(config) as browser:
        print_colored("Browser initialized successfully!", Colors.GREEN)
        
        # Test each site
        for i, site in enumerate(sites_to_test, 1):
            print_site_header(
                f"[{i}/{len(sites_to_test)}] {site['name']}",
                site['url'],
                site['difficulty']
            )
            
            # Add delay between sites to avoid rate limiting
            if i > 1:
                await asyncio.sleep(2)
            
            # Test the site
            result = await test_single_site(browser, site)
            all_results.append(result)
            
            if result['success']:
                successful += 1
            else:
                failed += 1
    
    return all_results, successful, failed

def print_summary(results: list, successful: int, failed: int):
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    total = len(results)
    success_rate = (successful / total * 100) if total > 0 else 0
    
    print(f"Total Sites Tested: {total}")
    print_colored(f"Successful: {successful}", Colors.GREEN)
    print_colored(f"Failed: {failed}", Colors.RED)
    print_colored(f"Success Rate: {success_rate:.1f}%", 
                 Colors.GREEN if success_rate >= 80 else Colors.YELLOW)
    
    # Group by category
    print()
    print_colored("Results by Category:", Colors.CYAN, bold=True)
    categories = {}
    for result in results:
        cat = result['category']
        if cat not in categories:
            categories[cat] = {'success': 0, 'total': 0}
        categories[cat]['total'] += 1
        if result['success']:
            categories[cat]['success'] += 1
    
    for cat, stats in sorted(categories.items()):
        rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"  {cat}: {stats['success']}/{stats['total']} ({rate:.0f}%)")
    
    # Group by difficulty
    print()
    print_colored("Results by Difficulty:", Colors.CYAN, bold=True)
    difficulties = {}
    for result in results:
        diff = result['difficulty']
        if diff not in difficulties:
            difficulties[diff] = {'success': 0, 'total': 0}
        difficulties[diff]['total'] += 1
        if result['success']:
            difficulties[diff]['success'] += 1
    
    difficulty_order = ['low', 'medium', 'high', 'very_high', 'extreme']
    for diff in difficulty_order:
        if diff in difficulties:
            stats = difficulties[diff]
            rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            color = Colors.GREEN if rate >= 80 else (Colors.YELLOW if rate >= 50 else Colors.RED)
            print_colored(f"  {diff.upper()}: {stats['success']}/{stats['total']} ({rate:.0f}%)", color)
    
    # Failed sites
    if failed > 0:
        print()
        print_colored("Failed Sites:", Colors.RED, bold=True)
        for result in results:
            if not result['success']:
                print(f"  - {result['name']} ({result['difficulty']}): {result.get('error', 'Unknown error')}")

async def main():
    """Main test function"""
    # Load challenging sites database
    db_path = Path("latest_version/challenging_sites_database.json")
    if not db_path.exists():
        print_colored(f"Error: Database not found at {db_path}", Colors.RED)
        return
    
    with open(db_path, 'r') as f:
        database = json.load(f)
    
    # Select sites to test
    sites = database['sites']
    
    # Test different categories
    test_categories = [
        'Bot Protection',  # Test anti-bot systems
        'E-commerce',      # Test e-commerce protection
        'Financial',       # Test financial sites
        'Social Media',    # Test social platforms
        'Testing'          # Test detection sites
    ]
    
    # Filter sites by category and difficulty
    sites_to_test = []
    for category in test_categories:
        category_sites = [s for s in sites if s['category'] == category]
        # Take up to 2 sites per category
        sites_to_test.extend(category_sites[:2])
    
    # Also add some extreme difficulty sites
    extreme_sites = [s for s in sites if s['difficulty'] in ['very_high', 'extreme']]
    for site in extreme_sites[:3]:
        if site not in sites_to_test:
            sites_to_test.append(site)
    
    # Limit total sites for testing
    sites_to_test = sites_to_test[:15]
    
    print_colored("Selected Sites for Testing:", Colors.MAGENTA, bold=True)
    for site in sites_to_test:
        print(f"  - {site['name']} ({site['category']}, {site['difficulty']})")
    
    # Test with different stealth levels
    stealth_levels_to_test = [
        StealthLevel.MAXIMUM,  # Test with maximum stealth
        # StealthLevel.PARANOID  # Uncomment to test paranoid mode
    ]
    
    for level in stealth_levels_to_test:
        print()
        print_colored(f"Testing with Stealth Level: {level.value}", Colors.MAGENTA, bold=True)
        
        # Run tests
        results, successful, failed = await test_sites(sites_to_test, level)
        
        # Print summary
        print_summary(results, successful, failed)
        
        # Save results
        output_file = f"test_results_{level.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump({
                'test_info': {
                    'timestamp': datetime.now().isoformat(),
                    'stealth_level': level.value,
                    'total_sites': len(sites_to_test),
                    'successful': successful,
                    'failed': failed,
                    'success_rate': (successful / len(sites_to_test) * 100) if sites_to_test else 0
                },
                'results': results
            }, f, indent=2)
        
        print()
        print_colored(f"Results saved to: {output_file}", Colors.GREEN)
    
    print()
    print_colored("All tests completed!", Colors.GREEN, bold=True)

if __name__ == "__main__":
    # Check if playwright is installed
    try:
        import playwright
    except ImportError:
        print_colored("Error: Playwright is not installed.", Colors.RED)
        print("Install it with: pip install playwright")
        print("Then install browsers with: playwright install chromium")
        sys.exit(1)
    
    # Run tests
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print()
        print_colored("Tests interrupted by user", Colors.YELLOW)
    except Exception as e:
        print_colored(f"Test failed with error: {e}", Colors.RED)
        import traceback
        traceback.print_exc()