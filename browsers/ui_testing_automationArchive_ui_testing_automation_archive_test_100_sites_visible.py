"""
Test 100+ Challenging Sites with Visible Browser (headless=False)
Tests the expanded database of challenging websites with visible browser for debugging
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import traceback

# Add parent directory to path
sys.path.insert(0, r'C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\ui_testing_automation')

from ui_testing_automation.base.browser import UltimateStealthBrowser
from browser_contracts import StealthConfig, StealthLevel
from dataclasses import dataclass, field

@dataclass
class TestResult:
    """Result of testing a single site"""
    site_id: str
    url: str
    name: str
    category: str
    difficulty: str
    success: bool
    error: Optional[str] = None
    elements_extracted: int = 0
    screenshots_captured: int = 0
    load_time: float = 0.0
    extraction_time: float = 0.0
    challenges_encountered: List[str] = field(default_factory=list)
    bypass_methods_used: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'site_id': self.site_id,
            'url': self.url,
            'name': self.name,
            'category': self.category,
            'difficulty': self.difficulty,
            'success': self.success,
            'error': self.error,
            'elements_extracted': self.elements_extracted,
            'screenshots_captured': self.screenshots_captured,
            'load_time': self.load_time,
            'extraction_time': self.extraction_time,
            'challenges_encountered': self.challenges_encountered,
            'bypass_methods_used': self.bypass_methods_used
        }

class ChallengingSitesTester:
    """Test harness for challenging websites"""
    
    def __init__(self, database_path: str, headless: bool = False):
        self.database_path = Path(database_path)
        self.headless = headless
        self.results: List[TestResult] = []
        self.sites = []
        self.load_database()
        
    def load_database(self):
        """Load the sites database"""
        with open(self.database_path, 'r') as f:
            data = json.load(f)
            self.sites = data['sites']
        print(f"[INFO] Loaded {len(self.sites)} sites from database")
        
    async def test_site(self, site: Dict[str, Any]) -> TestResult:
        """Test a single site"""
        print(f"\n[TESTING] {site['name']} ({site['url']})")
        print(f"  Category: {site['category']}")
        print(f"  Difficulty: {site['difficulty']}")
        print(f"  Challenges: {', '.join(site['challenges'][:3])}...")
        
        result = TestResult(
            site_id=site['id'],
            url=site['url'],
            name=site['name'],
            category=site['category'],
            difficulty=site['difficulty'],
            success=False
        )
        
        # Configure browser based on site difficulty
        config = StealthConfig()
        config.headless = self.headless
        
        if site['difficulty'] == 'extreme':
            config.level = StealthLevel.MAXIMUM
            result.bypass_methods_used.append('stealth_maximum')
        elif site['difficulty'] == 'high':
            config.level = StealthLevel.ADVANCED
            result.bypass_methods_used.append('stealth_advanced')
        elif site['difficulty'] == 'medium':
            config.level = StealthLevel.MODERATE
            result.bypass_methods_used.append('stealth_moderate')
        else:
            config.level = StealthLevel.BASIC
            result.bypass_methods_used.append('stealth_basic')
            
        # Add bypass methods based on challenges
        if 'cloudflare' in site['challenges']:
            config.level = StealthLevel.MAXIMUM
            config.bypass_cloudflare = True
            result.bypass_methods_used.append('cloudflare_bypass')
        if 'captcha' in site['challenges']:
            result.bypass_methods_used.append('captcha_handling')
        if 'fingerprinting' in site['challenges']:
            config.randomize_fingerprint = True
            result.bypass_methods_used.append('fingerprint_spoofing')
            
        # Set viewport
        config.viewport_width = 1920
        config.viewport_height = 1080
            
        # Create browser instance
        browser = UltimateStealthBrowser(config)
        
        try:
            # Initialize browser
            start_time = time.time()
            await browser.initialize()
            
            # Navigate and extract
            extraction_start = time.time()
            extraction_result = await browser.extract_elements(site['url'])
            extraction_end = time.time()
            
            result.load_time = extraction_start - start_time
            result.extraction_time = extraction_end - extraction_start
            
            if extraction_result:
                if hasattr(extraction_result, 'success'):
                    result.success = extraction_result.success
                elif hasattr(extraction_result, 'elements'):
                    result.success = len(extraction_result.elements) > 0
                else:
                    result.success = True
                    
                result.elements_extracted = len(extraction_result.elements) if hasattr(extraction_result, 'elements') else 0
                result.screenshots_captured = len(extraction_result.screenshots) if hasattr(extraction_result, 'screenshots') else 0
                
                print(f"  [OK] Success! Extracted {result.elements_extracted} elements")
                print(f"  Load time: {result.load_time:.2f}s")
                print(f"  Extraction time: {result.extraction_time:.2f}s")
                
                # Analyze extraction details
                print(f"\n  [LOG ANALYSIS]")
                print(f"  - Elements found: {result.elements_extracted}")
                if result.elements_extracted > 0 and hasattr(extraction_result, 'elements'):
                    # Count element types
                    element_types = {}
                    for elem in extraction_result.elements[:10]:  # Sample first 10
                        tag = elem.get('tag', 'unknown') if isinstance(elem, dict) else getattr(elem, 'tag', 'unknown')
                        element_types[tag] = element_types.get(tag, 0) + 1
                    print(f"  - Element types: {element_types}")
                
                # Check for specific issues
                if result.elements_extracted == 0:
                    print(f"  [WARNING] No elements extracted - possible bot detection or auth wall")
                    result.challenges_encountered.append('no_elements')
                elif result.elements_extracted < 10:
                    print(f"  [WARNING] Very few elements - possible partial block")
                    result.challenges_encountered.append('partial_block')
                    
                # Identify challenges that were encountered
                if hasattr(extraction_result, 'metadata'):
                    meta = extraction_result.metadata
                    if meta.get('cloudflare_detected'):
                        result.challenges_encountered.append('cloudflare')
                        print(f"  [DETECTED] Cloudflare protection")
                    if meta.get('captcha_detected'):
                        result.challenges_encountered.append('captcha')
                        print(f"  [DETECTED] CAPTCHA")
                    if meta.get('auth_wall_detected'):
                        result.challenges_encountered.append('auth_wall')
                        print(f"  [DETECTED] Authentication wall")
            else:
                result.success = False
                result.error = "Extraction returned None"
                print(f"  [FAIL] Extraction failed - no result returned")
                
        except Exception as e:
            result.success = False
            result.error = str(e)
            print(f"\n  [ERROR ANALYSIS]")
            print(f"  Error type: {type(e).__name__}")
            print(f"  Error message: {str(e)}")
            
            # Analyze specific error types
            error_str = str(e).lower()
            if 'timeout' in error_str:
                result.challenges_encountered.append('timeout')
                print(f"  [ISSUE] Timeout - site may be slow or blocking")
            elif 'navigation' in error_str:
                result.challenges_encountered.append('navigation_error')
                print(f"  [ISSUE] Navigation failed - possible redirect or block")
            elif 'closed' in error_str or 'target' in error_str:
                result.challenges_encountered.append('browser_crash')
                print(f"  [ISSUE] Browser/page closed unexpectedly")
            elif 'captcha' in error_str:
                result.challenges_encountered.append('captcha_block')
                print(f"  [ISSUE] CAPTCHA blocking access")
            elif 'cloudflare' in error_str:
                result.challenges_encountered.append('cloudflare_block')
                print(f"  [ISSUE] Cloudflare protection active")
            
            print(f"\n  Full traceback:")
            traceback.print_exc()
            
        finally:
            try:
                await browser.cleanup()
            except:
                pass
                
        return result
        
    async def test_batch(self, sites: List[Dict[str, Any]], batch_size: int = 5):
        """Test a batch of sites"""
        results = []
        for i in range(0, len(sites), batch_size):
            batch = sites[i:i+batch_size]
            print(f"\n[BATCH] Testing sites {i+1} to {min(i+batch_size, len(sites))} of {len(sites)}")
            
            # Test sites in batch sequentially to avoid resource issues
            for site in batch:
                result = await self.test_site(site)
                results.append(result)
                self.results.append(result)
                
                # Small delay between sites to avoid rate limiting
                await asyncio.sleep(2)
                
        return results
        
    async def run_tests(self, limit: Optional[int] = None, categories: Optional[List[str]] = None,
                       difficulties: Optional[List[str]] = None):
        """Run the test suite"""
        print(f"\n{'='*80}")
        print(f"TESTING 100+ CHALLENGING SITES")
        print(f"Headless: {self.headless}")
        print(f"Database: {self.database_path}")
        print(f"{'='*80}")
        
        # Filter sites based on criteria
        test_sites = self.sites
        
        if categories:
            test_sites = [s for s in test_sites if s['category'] in categories]
            print(f"Filtering by categories: {categories}")
            
        if difficulties:
            test_sites = [s for s in test_sites if s['difficulty'] in difficulties]
            print(f"Filtering by difficulties: {difficulties}")
            
        if limit:
            test_sites = test_sites[:limit]
            print(f"Limiting to {limit} sites")
            
        print(f"\nTotal sites to test: {len(test_sites)}")
        
        # Test sites in batches
        start_time = time.time()
        await self.test_batch(test_sites, batch_size=1)  # One at a time for visible browser
        end_time = time.time()
        
        # Generate report
        self.generate_report(end_time - start_time)
        
    def generate_report(self, total_time: float):
        """Generate test report"""
        print(f"\n{'='*80}")
        print(f"TEST RESULTS SUMMARY")
        print(f"{'='*80}")
        
        # Calculate statistics
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        failed = total - successful
        success_rate = (successful / total * 100) if total > 0 else 0
        
        print(f"\nOverall Statistics:")
        print(f"  Total sites tested: {total}")
        print(f"  Successful: {successful} ({success_rate:.1f}%)")
        print(f"  Failed: {failed}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Average time per site: {total_time/total:.2f}s" if total > 0 else "N/A")
        
        # Group by difficulty
        print(f"\nResults by Difficulty:")
        for difficulty in ['extreme', 'high', 'medium', 'low']:
            diff_results = [r for r in self.results if r.difficulty == difficulty]
            if diff_results:
                diff_success = sum(1 for r in diff_results if r.success)
                diff_rate = (diff_success / len(diff_results) * 100)
                print(f"  {difficulty.capitalize():8} - {diff_success}/{len(diff_results)} ({diff_rate:.1f}%)")
                
        # Group by category
        print(f"\nResults by Category (top 10):")
        categories = {}
        for r in self.results:
            if r.category not in categories:
                categories[r.category] = {'total': 0, 'success': 0}
            categories[r.category]['total'] += 1
            if r.success:
                categories[r.category]['success'] += 1
                
        sorted_cats = sorted(categories.items(), key=lambda x: x[1]['total'], reverse=True)[:10]
        for cat, stats in sorted_cats:
            rate = (stats['success'] / stats['total'] * 100)
            print(f"  {cat:15} - {stats['success']}/{stats['total']} ({rate:.1f}%)")
            
        # Failed sites
        print(f"\nFailed Sites (top 10):")
        failed_sites = [r for r in self.results if not r.success][:10]
        for r in failed_sites:
            print(f"  - {r.name} ({r.difficulty}): {r.error}")
            
        # Most challenging sites that succeeded
        print(f"\nSuccessful Extreme Difficulty Sites:")
        extreme_success = [r for r in self.results if r.success and r.difficulty == 'extreme'][:5]
        for r in extreme_success:
            print(f"  - {r.name}: {r.elements_extracted} elements in {r.extraction_time:.2f}s")
            
        # Save detailed results to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = Path(f"test_results_100_sites_{timestamp}.json")
        
        report_data = {
            'summary': {
                'total_sites': total,
                'successful': successful,
                'failed': failed,
                'success_rate': success_rate,
                'total_time': total_time,
                'timestamp': datetime.now().isoformat(),
                'headless': self.headless
            },
            'results': [r.to_dict() for r in self.results]
        }
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        print(f"\n[INFO] Detailed report saved to: {report_path}")

async def main():
    """Main test function"""
    # Test configuration
    DATABASE_PATH = "challenging_sites_database_100.json"
    HEADLESS = False  # Visible browser for debugging
    
    # Test options
    LIMIT = 30  # Test first 30 sites for broader coverage
    CATEGORIES = None  # Or specify: ['e-commerce', 'social_media', 'news']
    DIFFICULTIES = ['extreme', 'high', 'medium', 'low']  # Test all difficulties
    
    # Create tester
    tester = ChallengingSitesTester(DATABASE_PATH, headless=HEADLESS)
    
    # Run tests
    await tester.run_tests(
        limit=LIMIT,
        categories=CATEGORIES,
        difficulties=DIFFICULTIES
    )

if __name__ == "__main__":
    print("[START] Testing 100+ Challenging Sites with Visible Browser")
    print("[INFO] Press Ctrl+C to stop testing")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[STOP] Testing interrupted by user")
    except Exception as e:
        print(f"[ERROR] Test suite failed: {e}")
        traceback.print_exc()
    
    print("[END] Testing complete")