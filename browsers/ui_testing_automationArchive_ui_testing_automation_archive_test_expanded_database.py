#!/usr/bin/env python3
"""
Test browser_integrated.py with expanded challenging sites database (120 sites)
Tests with headless=False for visual monitoring
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import random

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
    "headless": False,  # Visual browser for monitoring
    "timeout": 30,
    "max_concurrent": 2,  # Lower concurrency for visual monitoring
    "save_results": True,
    "results_file": "test_results_expanded.json",
    "sample_size": 30,  # Test 30 sites from different categories
    "test_all": False   # Set to True to test all 120 sites
}

# ============================================================================
# EXPANDED TEST RUNNER
# ============================================================================

class ExpandedTestRunner:
    """Test runner for expanded database with 120 sites"""
    
    def __init__(self, database_path: str):
        """Initialize test runner"""
        self.database_path = Path(database_path)
        self.results = []
        self.start_time = None
        self.end_time = None
        
    def load_database(self) -> Dict[str, Any]:
        """Load the expanded challenging sites database"""
        with open(self.database_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def test_site(self, site: Dict[str, Any], site_number: int, total_sites: int) -> Dict[str, Any]:
        """Test a single site with visual browser"""
        
        print(f"\n[TEST {site_number}/{total_sites}] Site #{site['id']}: {site['name']}")
        print(f"  URL: {site['url']}")
        print(f"  Category: {site['category']}")
        print(f"  Difficulty: {site['difficulty']}")
        print(f"  Protection: {site['protection_system']}")
        
        # Configure browser based on difficulty
        stealth_level = self._get_stealth_level(site['difficulty'])
        config = StealthConfig(
            level=stealth_level,
            headless=TEST_CONFIG['headless'],  # Visual mode
            enable_human_delays=True,
            enable_human_mouse=True,
            enable_human_typing=True,
            enable_micro_behaviors=True,
            timeout=TEST_CONFIG['timeout'],
            viewport_width=1920,
            viewport_height=1080,
            bypass_cloudflare=site['protection_system'] == 'Cloudflare',
            bypass_datadome=site['protection_system'] == 'DataDome',
            bypass_shape_security='Shape' in site['protection_system'],
            bypass_f5_networks='F5' in site['protection_system'],
            bypass_kasada='Kasada' in site['protection_system'],
            bypass_perimeter_x='PerimeterX' in site['protection_system']
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
                print(f"  [INFO] Browser launched (visual mode)")
                
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
    
    def select_test_sites(self, database: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Select sites to test based on configuration"""
        
        if TEST_CONFIG['test_all']:
            return database['sites']
        
        # Select sample from each category
        categories = {}
        for site in database['sites']:
            category = site['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(site)
        
        selected_sites = []
        sites_per_category = max(1, TEST_CONFIG['sample_size'] // len(categories))
        
        for category, sites in categories.items():
            # Shuffle and select from each category
            random.shuffle(sites)
            selected = sites[:sites_per_category]
            selected_sites.extend(selected)
            print(f"  Selected {len(selected)} sites from {category}")
        
        # Add more if needed to reach sample size
        remaining = TEST_CONFIG['sample_size'] - len(selected_sites)
        if remaining > 0:
            all_sites = database['sites'].copy()
            random.shuffle(all_sites)
            for site in all_sites:
                if site not in selected_sites:
                    selected_sites.append(site)
                    remaining -= 1
                    if remaining == 0:
                        break
        
        return selected_sites[:TEST_CONFIG['sample_size']]
    
    async def run_tests(self) -> None:
        """Run tests on selected sites with visual browser"""
        
        print("[EXPANDED DATABASE TEST - VISUAL MODE]")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # Load database
        database = self.load_database()
        print(f"Database loaded: {database['metadata']['total_sites']} sites")
        print(f"Categories: {', '.join(database['metadata']['categories'])}")
        
        # Select sites to test
        sites_to_test = self.select_test_sites(database)
        
        print(f"\nTesting {len(sites_to_test)} sites")
        print(f"Concurrency: {TEST_CONFIG['max_concurrent']}")
        print(f"Headless: {TEST_CONFIG['headless']} (Visual Mode)")
        print(f"Timeout: {TEST_CONFIG['timeout']}s")
        print("=" * 60)
        
        # Run tests with limited concurrency for visual monitoring
        semaphore = asyncio.Semaphore(TEST_CONFIG['max_concurrent'])
        
        async def test_with_semaphore(site, idx, total):
            async with semaphore:
                return await self.test_site(site, idx, total)
        
        # Execute tests
        tasks = [
            test_with_semaphore(site, idx + 1, len(sites_to_test)) 
            for idx, site in enumerate(sites_to_test)
        ]
        self.results = await asyncio.gather(*tasks)
        
        self.end_time = time.time()
        
        # Generate report
        self.generate_report()
        
        # Save results
        if TEST_CONFIG['save_results']:
            self.save_results()
    
    def generate_report(self) -> None:
        """Generate comprehensive test report"""
        
        print("\n" + "=" * 60)
        print("[TEST REPORT - EXPANDED DATABASE]")
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
        
        # Sort by total count
        for system, stats in sorted(protection_systems.items(), key=lambda x: x[1]['total'], reverse=True)[:10]:
            rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {system}: {stats['success']}/{stats['total']} ({rate:.0f}%)")
        
        # Top performing sites
        successful_sites = [r for r in self.results if r.get('success', False)]
        if successful_sites:
            print(f"\nTop 5 Fastest Extractions:")
            for site in sorted(successful_sites, key=lambda x: x['extraction_time'])[:5]:
                print(f"  - {site['name']}: {site['extraction_time']}s ({site['elements_extracted']} elements)")
        
        # Failed sites
        failed_sites = [r for r in self.results if not r.get('success', False)]
        if failed_sites:
            print(f"\nFailed Sites ({len(failed_sites)}):")
            for site in failed_sites[:10]:  # Show first 10 failures
                error = site.get('error', 'Unknown error')
                print(f"  - {site['name']} ({site['protection_system']}): {error[:50]}...")
        
        # Sites with CAPTCHAs detected
        captcha_sites = [r for r in self.results if r.get('captcha_detected', False)]
        if captcha_sites:
            print(f"\nSites with CAPTCHA Detected ({len(captcha_sites)}):")
            for site in captcha_sites[:5]:
                print(f"  - {site['name']}: {site.get('captcha_type', 'Unknown')}")
        
        # Performance statistics
        extraction_times = [r['extraction_time'] for r in self.results if 'extraction_time' in r]
        if extraction_times:
            print(f"\nPerformance Statistics:")
            print(f"  Fastest extraction: {min(extraction_times):.2f}s")
            print(f"  Slowest extraction: {max(extraction_times):.2f}s")
            print(f"  Average extraction: {sum(extraction_times)/len(extraction_times):.2f}s")
            print(f"  Median extraction: {sorted(extraction_times)[len(extraction_times)//2]:.2f}s")
        
        # Elements statistics
        elements_counts = [r['elements_extracted'] for r in self.results if r.get('success', False)]
        if elements_counts:
            print(f"\nElement Extraction Statistics:")
            print(f"  Maximum elements: {max(elements_counts)}")
            print(f"  Minimum elements: {min(elements_counts)}")
            print(f"  Average elements: {sum(elements_counts)/len(elements_counts):.0f}")
        
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
                'database': 'challenging_sites_database_expanded.json',
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
    database_path = r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ui_testing_automation\challenging_sites_database_expanded.json"
    
    # Create test runner
    runner = ExpandedTestRunner(database_path)
    
    # Run tests
    await runner.run_tests()

if __name__ == "__main__":
    print("[STARTING EXPANDED DATABASE TEST WITH VISUAL BROWSER]")
    print("Testing 120 sites with headless=False for monitoring...")
    print("You will see browser windows opening and closing during the test.")
    print("")
    
    try:
        asyncio.run(main())
        print("\n[TEST COMPLETE]")
    except KeyboardInterrupt:
        print("\n[TEST INTERRUPTED BY USER]")
    except Exception as e:
        print(f"\n[TEST ERROR]: {e}")
        import traceback
        traceback.print_exc()