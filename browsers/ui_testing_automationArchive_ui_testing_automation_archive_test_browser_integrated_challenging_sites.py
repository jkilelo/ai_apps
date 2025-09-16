#!/usr/bin/env python3
"""
Test browser_integrated.py with challenging sites database
Tests the integrated browser module against various protected websites
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Import the integrated browser module
from ui_testing_automation.base.browser import (
    UltimateStealthBrowser,
    StealthConfig,
    StealthLevel,
    ExtractionResult
)

# ============================================================================
# TEST CONFIGURATION
# ============================================================================

TEST_CONFIG = {
    "headless": True,
    "timeout": 30,
    "max_concurrent": 3,
    "save_results": True,
    "results_file": "test_results_integrated.json"
}

# ============================================================================
# TEST RUNNER CLASS
# ============================================================================

class ChallengingSitesTestRunner:
    """Test runner for challenging sites with the integrated browser"""
    
    def __init__(self, database_path: str):
        """Initialize test runner"""
        self.database_path = Path(database_path)
        self.results = []
        self.start_time = None
        self.end_time = None
        
    def load_database(self) -> Dict[str, Any]:
        """Load the challenging sites database"""
        with open(self.database_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def test_site(self, site: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single site"""
        
        print(f"\n[TEST] Site #{site['id']}: {site['name']}")
        print(f"  URL: {site['url']}")
        print(f"  Category: {site['category']}")
        print(f"  Difficulty: {site['difficulty']}")
        print(f"  Protection: {site['protection_system']}")
        
        # Configure browser based on difficulty
        stealth_level = self._get_stealth_level(site['difficulty'])
        config = StealthConfig(
            level=stealth_level,
            headless=TEST_CONFIG['headless'],
            enable_human_delays=True,
            enable_human_mouse=True,
            enable_human_typing=True,
            enable_micro_behaviors=True,
            timeout=TEST_CONFIG['timeout'],
            bypass_cloudflare=site['protection_system'] == 'Cloudflare',
            bypass_datadome=site['protection_system'] == 'DataDome',
            bypass_shape_security='Shape' in site['protection_system'],
            bypass_f5_networks='F5' in site['protection_system'],
            bypass_kasada='Kasada' in site['protection_system']
        )
        
        start_time = time.time()
        result = {
            'id': site['id'],
            'name': site['name'],
            'url': site['url'],
            'category': site['category'],
            'difficulty': site['difficulty'],
            'protection_system': site['protection_system'],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Create browser instance
            async with UltimateStealthBrowser(config) as browser:
                # Extract elements
                extraction_result = await browser.extract_elements(site['url'])
                
                # Record results
                result['success'] = extraction_result.success
                result['elements_extracted'] = extraction_result.element_count
                result['extraction_time'] = round(time.time() - start_time, 2)
                result['framework_detected'] = extraction_result.framework_detected
                result['captcha_detected'] = extraction_result.captcha_detected
                result['captcha_type'] = extraction_result.captcha_type
                result['errors'] = extraction_result.errors
                result['warnings'] = extraction_result.warnings
                
                # Get metrics
                metrics = await browser.get_metrics()
                result['metrics'] = {
                    'requests_total': metrics['requests_total'],
                    'requests_success': metrics['requests_success'],
                    'requests_failed': metrics['requests_failed'],
                    'avg_response_time': round(metrics['avg_response_time'], 2)
                }
                
                # Success/failure message
                if extraction_result.success:
                    print(f"  [OK] SUCCESS - Extracted {extraction_result.element_count} elements in {result['extraction_time']}s")
                    if extraction_result.framework_detected:
                        print(f"      Framework: {extraction_result.framework_detected}")
                    if extraction_result.captcha_detected:
                        print(f"      CAPTCHA detected: {extraction_result.captcha_type}")
                else:
                    print(f"  [FAIL] FAILED - {extraction_result.errors}")
                
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            result['extraction_time'] = round(time.time() - start_time, 2)
            print(f"  [ERROR] Exception: {e}")
        
        return result
    
    def _get_stealth_level(self, difficulty: str) -> StealthLevel:
        """Map difficulty to stealth level"""
        mapping = {
            'low': StealthLevel.BASIC,
            'medium': StealthLevel.MODERATE,
            'high': StealthLevel.ADVANCED,
            'very_high': StealthLevel.MAXIMUM,
            'extreme': StealthLevel.MAXIMUM
        }
        return mapping.get(difficulty, StealthLevel.MAXIMUM)
    
    async def run_tests(self, sites_to_test: List[Dict[str, Any]] = None) -> None:
        """Run tests on specified sites or all sites"""
        
        print("[BROWSER INTEGRATED MODULE TEST]")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # Load database
        database = self.load_database()
        
        # Determine sites to test
        if sites_to_test is None:
            sites_to_test = database['sites']
        
        print(f"Testing {len(sites_to_test)} sites")
        print(f"Concurrency: {TEST_CONFIG['max_concurrent']}")
        print(f"Headless: {TEST_CONFIG['headless']}")
        print(f"Timeout: {TEST_CONFIG['timeout']}s")
        print("=" * 60)
        
        # Run tests with concurrency limit
        semaphore = asyncio.Semaphore(TEST_CONFIG['max_concurrent'])
        
        async def test_with_semaphore(site):
            async with semaphore:
                return await self.test_site(site)
        
        # Execute tests
        tasks = [test_with_semaphore(site) for site in sites_to_test]
        self.results = await asyncio.gather(*tasks)
        
        self.end_time = time.time()
        
        # Generate report
        self.generate_report()
        
        # Save results if configured
        if TEST_CONFIG['save_results']:
            self.save_results()
    
    def generate_report(self) -> None:
        """Generate test report"""
        
        print("\n" + "=" * 60)
        print("[TEST REPORT]")
        print("=" * 60)
        
        # Calculate statistics
        total = len(self.results)
        successful = sum(1 for r in self.results if r.get('success', False))
        failed = total - successful
        success_rate = (successful / total * 100) if total > 0 else 0
        total_time = self.end_time - self.start_time
        
        print(f"\nOverall Statistics:")
        print(f"  Total Sites Tested: {total}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Total Test Time: {total_time:.1f}s")
        print(f"  Average Time per Site: {total_time/total:.1f}s")
        
        # Group by category
        print(f"\nResults by Category:")
        categories = {}
        for result in self.results:
            category = result['category']
            if category not in categories:
                categories[category] = {'total': 0, 'success': 0}
            categories[category]['total'] += 1
            if result.get('success', False):
                categories[category]['success'] += 1
        
        for category, stats in sorted(categories.items()):
            rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {category}: {stats['success']}/{stats['total']} ({rate:.0f}%)")
        
        # Group by difficulty
        print(f"\nResults by Difficulty:")
        difficulties = {}
        for result in self.results:
            difficulty = result['difficulty']
            if difficulty not in difficulties:
                difficulties[difficulty] = {'total': 0, 'success': 0}
            difficulties[difficulty]['total'] += 1
            if result.get('success', False):
                difficulties[difficulty]['success'] += 1
        
        difficulty_order = ['low', 'medium', 'high', 'very_high', 'extreme']
        for difficulty in difficulty_order:
            if difficulty in difficulties:
                stats = difficulties[difficulty]
                rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
                print(f"  {difficulty}: {stats['success']}/{stats['total']} ({rate:.0f}%)")
        
        # Group by protection system
        print(f"\nResults by Protection System:")
        protection_systems = {}
        for result in self.results:
            system = result['protection_system'].split(' + ')[0]  # Get primary system
            if system not in protection_systems:
                protection_systems[system] = {'total': 0, 'success': 0}
            protection_systems[system]['total'] += 1
            if result.get('success', False):
                protection_systems[system]['success'] += 1
        
        for system, stats in sorted(protection_systems.items()):
            rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {system}: {stats['success']}/{stats['total']} ({rate:.0f}%)")
        
        # Failed sites
        failed_sites = [r for r in self.results if not r.get('success', False)]
        if failed_sites:
            print(f"\nFailed Sites ({len(failed_sites)}):")
            for site in failed_sites:
                error = site.get('error', 'Unknown error')
                print(f"  - {site['name']} ({site['protection_system']}): {error}")
        
        # Sites with CAPTCHAs detected
        captcha_sites = [r for r in self.results if r.get('captcha_detected', False)]
        if captcha_sites:
            print(f"\nSites with CAPTCHA Detected ({len(captcha_sites)}):")
            for site in captcha_sites:
                print(f"  - {site['name']}: {site.get('captcha_type', 'Unknown')}")
        
        # Performance statistics
        extraction_times = [r['extraction_time'] for r in self.results if 'extraction_time' in r]
        if extraction_times:
            print(f"\nPerformance Statistics:")
            print(f"  Fastest extraction: {min(extraction_times):.2f}s")
            print(f"  Slowest extraction: {max(extraction_times):.2f}s")
            print(f"  Average extraction: {sum(extraction_times)/len(extraction_times):.2f}s")
        
        print("\n" + "=" * 60)
    
    def save_results(self) -> None:
        """Save test results to JSON file"""
        
        output = {
            'metadata': {
                'test_date': datetime.now().isoformat(),
                'total_sites': len(self.results),
                'successful': sum(1 for r in self.results if r.get('success', False)),
                'failed': sum(1 for r in self.results if not r.get('success', False)),
                'total_time': round(self.end_time - self.start_time, 2),
                'module': 'browser_integrated.py',
                'config': TEST_CONFIG
            },
            'results': self.results
        }
        
        with open(TEST_CONFIG['results_file'], 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)
        
        print(f"Results saved to: {TEST_CONFIG['results_file']}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main test execution"""
    
    # Database path
    database_path = r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ui_testing_automation\challenging_sites_database.json"
    
    # Create test runner
    runner = ChallengingSitesTestRunner(database_path)
    
    # Select sites to test
    # Option 1: Test all sites
    # await runner.run_tests()
    
    # Option 2: Test specific categories
    database = runner.load_database()
    test_sites = []
    
    # Test a sample from each category for quick validation
    categories_to_test = [
        'Bot Protection',    # 3 sites
        'E-commerce',       # 5 sites
        'Financial',        # 3 sites
        'Social Media',     # 5 sites
        'Testing'          # 4 sites
    ]
    
    for site in database['sites']:
        if site['category'] in categories_to_test:
            test_sites.append(site)
            # Limit to 2 sites per category for quick test
            category_count = sum(1 for s in test_sites if s['category'] == site['category'])
            if category_count >= 2:
                categories_to_test = [c for c in categories_to_test if c != site['category']]
    
    # Run tests
    await runner.run_tests(test_sites[:10])  # Test first 10 sites for quick validation

if __name__ == "__main__":
    print("[STARTING BROWSER INTEGRATED MODULE TEST]")
    print("Testing against challenging sites database...")
    
    try:
        asyncio.run(main())
        print("\n[TEST COMPLETE]")
    except KeyboardInterrupt:
        print("\n[TEST INTERRUPTED]")
    except Exception as e:
        print(f"\n[TEST ERROR]: {e}")
        import traceback
        traceback.print_exc()