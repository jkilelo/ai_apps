#!/usr/bin/env python3
"""
Test browser.py against the challenging sites database
Senior Software Engineer approach - comprehensive testing
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from browser import StealthConfig, UltimateStealthBrowser, StealthLevel

class ChallengingSitesTest:
    """Test browser against challenging sites with detailed reporting"""
    
    def __init__(self):
        self.database_file = Path("challenging_sites_database.json")
        self.results = {
            "test_run": {
                "timestamp": datetime.now().isoformat(),
                "browser_version": "v2.0",
                "total_sites_tested": 0,
                "successful_extractions": 0,
                "failed_extractions": 0,
                "success_rate": 0.0
            },
            "site_results": []
        }
        
    def load_database(self):
        """Load challenging sites database"""
        if not self.database_file.exists():
            print(f"[ERROR] Database file not found: {self.database_file}")
            return []
        
        with open(self.database_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        sites = data.get('sites', [])
        print(f"[OK] Loaded {len(sites)} challenging sites from database")
        return sites
    
    async def test_site(self, site_data, stealth_level=StealthLevel.MAXIMUM):
        """Test a single site with detailed results"""
        site_name = site_data.get('name', 'Unknown')
        site_url = site_data.get('url', '')
        difficulty = site_data.get('difficulty', 'unknown')
        protection = site_data.get('protection_system', 'Unknown')
        
        print(f"\n[TESTING] {site_name}")
        print(f"  URL: {site_url}")
        print(f"  Difficulty: {difficulty}")
        print(f"  Protection: {protection}")
        
        result = {
            "site_name": site_name,
            "url": site_url,
            "difficulty": difficulty,
            "protection_system": protection,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "elements_extracted": 0,
            "load_time": 0.0,
            "error_message": None,
            "stealth_level_used": stealth_level.value
        }
        
        try:
            # Configure browser for maximum stealth
            config = StealthConfig()
            config.headless = True
            config.stealth_level = stealth_level
            config.human_behavior = True
            config.randomize_fingerprint = True
            
            browser = UltimateStealthBrowser(config)
            
            print(f"  [1/4] Initializing browser with {stealth_level.value} stealth...")
            start_time = time.time()
            await browser.initialize()
            
            print(f"  [2/4] Navigating to site...")
            extraction_result = await browser.extract_elements(site_url)
            
            end_time = time.time()
            load_time = end_time - start_time
            
            print(f"  [3/4] Processing results...")
            if extraction_result.success:
                result["success"] = True
                result["elements_extracted"] = len(extraction_result.elements)
                result["load_time"] = load_time
                
                print(f"  [SUCCESS] [OK] Extracted {len(extraction_result.elements)} elements")
                print(f"  [TIMING] Load time: {load_time:.2f}s")
                
                # Show sample elements
                if extraction_result.elements:
                    print(f"  [SAMPLE] First 3 elements:")
                    for i, elem in enumerate(extraction_result.elements[:3], 1):
                        elem_type = getattr(elem, 'element_type', 'unknown')
                        elem_tag = getattr(elem, 'tag_name', 'unknown')
                        print(f"    {i}. <{elem_tag}> - Type: {elem_type}")
            else:
                result["success"] = False
                result["error_message"] = str(extraction_result.errors)
                result["load_time"] = load_time
                
                print(f"  [FAILED] [X] Extraction failed")
                print(f"  [ERROR] {extraction_result.errors}")
            
            print(f"  [4/4] Cleaning up...")
            await browser.cleanup()
            
        except asyncio.TimeoutError:
            result["error_message"] = "Timeout after 30 seconds"
            print(f"  [TIMEOUT] Site took too long to respond")
        except Exception as e:
            result["error_message"] = str(e)
            print(f"  [ERROR] Exception: {e}")
        
        return result
    
    async def test_sample_sites(self, max_sites=5):
        """Test a sample of challenging sites"""
        sites = self.load_database()
        
        if not sites:
            print("[ERROR] No sites to test")
            return
        
        # Select a diverse sample
        sample_sites = []
        
        # Get sites by difficulty
        difficulties = ['low', 'medium', 'high', 'very_high', 'extreme']
        sites_by_difficulty = {diff: [] for diff in difficulties}
        
        for site in sites:
            diff = site.get('difficulty', 'unknown')
            if diff in sites_by_difficulty:
                sites_by_difficulty[diff].append(site)
        
        # Select at least one from each difficulty level
        for difficulty in difficulties:
            if sites_by_difficulty[difficulty] and len(sample_sites) < max_sites:
                sample_sites.append(sites_by_difficulty[difficulty][0])
        
        # Add more if needed
        remaining_slots = max_sites - len(sample_sites)
        if remaining_slots > 0:
            remaining_sites = [site for site in sites if site not in sample_sites]
            sample_sites.extend(remaining_sites[:remaining_slots])
        
        print(f"\n[SELECTED] Testing {len(sample_sites)} challenging sites:")
        for i, site in enumerate(sample_sites, 1):
            print(f"  {i}. {site['name']} ({site['difficulty']}) - {site['protection_system']}")
        
        # Test each site
        successful = 0
        total = len(sample_sites)
        
        for i, site in enumerate(sample_sites, 1):
            print(f"\n{'='*60}")
            print(f"SITE {i}/{total}")
            print(f"{'='*60}")
            
            result = await self.test_site(site)
            self.results["site_results"].append(result)
            
            if result["success"]:
                successful += 1
        
        # Calculate final results
        self.results["test_run"]["total_sites_tested"] = total
        self.results["test_run"]["successful_extractions"] = successful
        self.results["test_run"]["failed_extractions"] = total - successful
        self.results["test_run"]["success_rate"] = (successful / total) * 100 if total > 0 else 0
        
        self.print_final_report()
    
    def print_final_report(self):
        """Print comprehensive final report"""
        print(f"\n{'='*80}")
        print("CHALLENGING SITES TEST - FINAL REPORT")
        print(f"{'='*80}")
        
        run_data = self.results["test_run"]
        print(f"Test Run: {run_data['timestamp']}")
        print(f"Browser Version: {run_data['browser_version']}")
        print(f"Total Sites Tested: {run_data['total_sites_tested']}")
        print(f"Successful Extractions: {run_data['successful_extractions']}")
        print(f"Failed Extractions: {run_data['failed_extractions']}")
        print(f"Success Rate: {run_data['success_rate']:.1f}%")
        
        print(f"\n[DETAILED RESULTS]")
        print("-" * 80)
        
        for result in self.results["site_results"]:
            status = "[PASS]" if result["success"] else "[FAIL]"
            elements = result["elements_extracted"]
            load_time = result["load_time"]
            
            print(f"{status} {result['site_name']} ({result['difficulty']})")
            print(f"     {result['protection_system']} | {elements} elements | {load_time:.2f}s")
            if not result["success"] and result["error_message"]:
                error_preview = result["error_message"][:60] + "..." if len(result["error_message"]) > 60 else result["error_message"]
                print(f"     Error: {error_preview}")
            print()
        
        # Performance assessment
        success_rate = run_data['success_rate']
        print(f"[PERFORMANCE ASSESSMENT]")
        if success_rate >= 80:
            grade = "EXCELLENT"
        elif success_rate >= 60:
            grade = "GOOD"
        elif success_rate >= 40:
            grade = "ACCEPTABLE"
        else:
            grade = "NEEDS IMPROVEMENT"
        
        print(f"Overall Grade: {grade} ({success_rate:.1f}%)")
        
        # Save detailed report
        report_file = f"challenging_sites_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n[REPORT SAVED] Detailed report: {report_file}")
        
        print(f"\n{'='*80}")
        print("BROWSER.PY CHALLENGING SITES TEST COMPLETE")
        print(f"{'='*80}")

async def main():
    """Run the challenging sites test"""
    print("BROWSER.PY CHALLENGING SITES DATABASE TEST")
    print("Senior Software Engineer - 30+ Years Experience")
    print("Testing against real-world difficult websites")
    print()
    
    tester = ChallengingSitesTest()
    
    # Test 5 diverse challenging sites
    await tester.test_sample_sites(max_sites=5)

if __name__ == "__main__":
    asyncio.run(main())