#!/usr/bin/env python3
"""
Test Stealth Browser Against Challenging Sites Database
Tests the stealth browser's anti-detection capabilities against 32 challenging websites
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stealth_browser import StealthBrowser, StealthConfig
from utils import Logger, LogLevel

class StealthBrowserChallengeTester:
    """Test stealth browser against challenging sites"""
    
    def __init__(self):
        self.logger = Logger.get_logger("StealthChallengeTester", LogLevel.INFO)
        self.browser = None
        self.results = []
        self.database_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "challenging_sites_database.json"
        )
        
    async def load_database(self) -> Dict:
        """Load the challenging sites database"""
        try:
            with open(self.database_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load database: {e}")
            return None
            
    async def test_site(self, site: Dict) -> Dict:
        """Test a single site"""
        result = {
            "id": site["id"],
            "name": site["name"],
            "url": site["url"],
            "category": site["category"],
            "difficulty": site["difficulty"],
            "protection_system": site["protection_system"],
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "detection_status": "unknown",
            "error": None,
            "load_time": None,
            "elements_found": 0,
            "stealth_score": 0
        }
        
        try:
            self.logger.info(f"Testing {site['name']} ({site['difficulty']} difficulty)")
            self.logger.info(f"Protection: {site['protection_system']}")
            
            # Create a new page and navigate to the site
            start_time = time.time()
            async with self.browser.new_page(site["url"]) as page:
                # Wait for page to stabilize
                await asyncio.sleep(3)
                
                # Calculate load time
                result["load_time"] = round(time.time() - start_time, 2)
                
                # Check for common bot detection indicators
                detection_checks = await self.check_bot_detection_on_page(page)
                result["detection_checks"] = detection_checks
                
                # Try to extract some elements as proof of access
                elements = await page.evaluate("""
                    () => {
                        const elements = document.querySelectorAll('a, button, input, form');
                        return elements.length;
                    }
                """)
                result["elements_found"] = elements
                
                # Check page title to ensure we're on the right page
                title = await page.title()
                result["page_title"] = title[:100] if title else "No title"
                
                # Special checks for testing sites
                if site["category"] == "Testing":
                    test_results = await self.run_detection_tests_on_page(page, site["url"])
                    result["test_results"] = test_results
            
            # Calculate stealth score based on various factors
            stealth_score = 100
            title = result.get("page_title", "")
            elements = result.get("elements_found", 0)
            
            if "captcha" in title.lower() or "verify" in title.lower():
                stealth_score -= 30
                result["detection_status"] = "captcha_triggered"
            elif "access denied" in title.lower() or "blocked" in title.lower():
                stealth_score -= 50
                result["detection_status"] = "blocked"
            elif elements < 5:
                stealth_score -= 20
                result["detection_status"] = "limited_access"
            else:
                result["detection_status"] = "undetected"
                
            result["stealth_score"] = stealth_score
            result["success"] = stealth_score >= 50
                
            self.logger.info(f"✓ {site['name']}: Score {stealth_score}/100")
            
        except Exception as e:
            result["error"] = str(e)
            result["detection_status"] = "error"
            self.logger.error(f"✗ {site['name']}: {e}")
            
        return result
        
    async def check_bot_detection_on_page(self, page) -> Dict:
        """Check for common bot detection indicators on a specific page"""
        checks = {}
        
        try:
            # Check for WebDriver property
            checks["webdriver"] = await page.evaluate(
                "() => navigator.webdriver"
            )
            
            # Check for Chrome property
            checks["chrome"] = await page.evaluate(
                "() => !!window.chrome"
            )
            
            # Check for automation indicators
            checks["automation"] = await page.evaluate("""
                () => {
                    return {
                        webdriver: navigator.webdriver,
                        phantom: !!window._phantom,
                        nightmare: !!window.__nightmare,
                        selenium: !!window.selenium || !!document.selenium,
                        domAutomation: !!window.domAutomation,
                        webdriverEvaluate: !!document.__webdriver_evaluate,
                        driverEvaluate: !!document.__driver_evaluate
                    };
                }
            """)
            
            # Check user agent
            checks["user_agent"] = await page.evaluate(
                "() => navigator.userAgent"
            )
            
            # Check for headless indicators
            checks["headless_check"] = await page.evaluate("""
                () => {
                    const width = window.outerWidth;
                    const height = window.outerHeight;
                    return {
                        dimensions: `${width}x${height}`,
                        isHeadless: width === 0 || height === 0
                    };
                }
            """)
            
        except Exception as e:
            checks["error"] = str(e)
            
        return checks
        
    async def run_detection_tests_on_page(self, page, url: str) -> Dict:
        """Run specific tests for detection testing sites on a specific page"""
        tests = {}
        
        try:
            if "bot.sannysoft.com" in url:
                # Check the bot detection results
                tests["bot_detection"] = await page.evaluate("""
                    () => {
                        const results = {};
                        const rows = document.querySelectorAll('tr');
                        rows.forEach(row => {
                            const cells = row.querySelectorAll('td');
                            if (cells.length >= 2) {
                                const test = cells[0].textContent.trim();
                                const result = cells[1].textContent.trim();
                                if (test) results[test] = result;
                            }
                        });
                        return results;
                    }
                """)
                
            elif "areyouheadless" in url:
                # Check headless detection result
                tests["headless_result"] = await page.evaluate("""
                    () => {
                        const result = document.querySelector('h1');
                        return result ? result.textContent : 'Unknown';
                    }
                """)
                
            elif "pixelscan.net" in url:
                # Wait for analysis to complete
                await asyncio.sleep(5)
                tests["pixelscan_score"] = await page.evaluate("""
                    () => {
                        const scoreElement = document.querySelector('.score');
                        return scoreElement ? scoreElement.textContent : 'Not found';
                    }
                """)
                
        except Exception as e:
            tests["error"] = str(e)
            
        return tests
        
    async def run_tests(self, sites_to_test: List[str] = None):
        """Run tests on specified sites or all sites"""
        # Load database
        database = await self.load_database()
        if not database:
            return
            
        # Filter sites if specified
        if sites_to_test:
            sites = [s for s in database["sites"] if s["name"] in sites_to_test or s["id"] in sites_to_test]
        else:
            sites = database["sites"]
            
        self.logger.info(f"Testing {len(sites)} challenging sites")
        self.logger.info("=" * 60)
        
        # Initialize browser with maximum stealth
        from stealth_browser import StealthLevel
        config = StealthConfig()
        config.level = StealthLevel.MAXIMUM
        config.headless = False
        config.hide_webdriver = True
        config.hide_automation_indicators = True
        config.prevent_webrtc_leak = True
        config.spoof_canvas_fingerprint = True
        config.enable_human_typing = True
        config.enable_human_mouse = True
        config.enable_human_scrolling = True
        config.enable_human_delays = True
        
        self.browser = StealthBrowser(config)
        await self.browser.start()
        
        try:
            # Test each site
            for i, site in enumerate(sites, 1):
                self.logger.info(f"\n[{i}/{len(sites)}] Testing {site['name']}...")
                result = await self.test_site(site)
                self.results.append(result)
                
                # Brief pause between sites to avoid rate limiting
                if i < len(sites):
                    await asyncio.sleep(2)
                    
        finally:
            await self.browser.stop()
            
        # Generate report
        await self.generate_report()
        
    async def generate_report(self):
        """Generate comprehensive test report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"stealth_browser_challenge_report_{timestamp}.json"
        
        # Calculate statistics
        total = len(self.results)
        successful = sum(1 for r in self.results if r["success"])
        success_rate = (successful / total * 100) if total > 0 else 0
        
        # Group by category
        by_category = {}
        for result in self.results:
            cat = result["category"]
            if cat not in by_category:
                by_category[cat] = {"total": 0, "success": 0, "sites": []}
            by_category[cat]["total"] += 1
            if result["success"]:
                by_category[cat]["success"] += 1
            by_category[cat]["sites"].append(result["name"])
            
        # Group by difficulty
        by_difficulty = {}
        for result in self.results:
            diff = result["difficulty"]
            if diff not in by_difficulty:
                by_difficulty[diff] = {"total": 0, "success": 0}
            by_difficulty[diff]["total"] += 1
            if result["success"]:
                by_difficulty[diff]["success"] += 1
                
        # Find failed sites
        failed_sites = [r for r in self.results if not r["success"]]
        
        report = {
            "test_date": datetime.now().isoformat(),
            "summary": {
                "total_sites_tested": total,
                "successful": successful,
                "failed": total - successful,
                "success_rate": round(success_rate, 2),
                "average_stealth_score": round(
                    sum(r["stealth_score"] for r in self.results) / total, 2
                ) if total > 0 else 0,
                "average_load_time": round(
                    sum(r["load_time"] for r in self.results if r["load_time"]) / 
                    sum(1 for r in self.results if r["load_time"]), 2
                ) if any(r["load_time"] for r in self.results) else 0
            },
            "by_category": by_category,
            "by_difficulty": by_difficulty,
            "failed_sites": [
                {
                    "name": f["name"],
                    "url": f["url"],
                    "protection": f["protection_system"],
                    "error": f["error"],
                    "detection_status": f["detection_status"]
                }
                for f in failed_sites
            ],
            "detailed_results": self.results
        }
        
        # Save report
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        # Print summary
        self.logger.info("\n" + "=" * 60)
        self.logger.info("STEALTH BROWSER CHALLENGE TEST RESULTS")
        self.logger.info("=" * 60)
        self.logger.info(f"Total Sites Tested: {total}")
        self.logger.info(f"Successful: {successful} ({success_rate:.1f}%)")
        self.logger.info(f"Failed: {total - successful}")
        self.logger.info(f"Average Stealth Score: {report['summary']['average_stealth_score']}/100")
        self.logger.info(f"Average Load Time: {report['summary']['average_load_time']}s")
        
        if failed_sites:
            self.logger.warning("\nFailed Sites:")
            for f in failed_sites:
                self.logger.warning(f"  - {f['name']} ({f['protection_system']}): {f['detection_status']}")
                
        self.logger.info(f"\nDetailed report saved to: {report_path}")
        
        return report

async def main():
    """Main execution"""
    tester = StealthBrowserChallengeTester()
    
    # Test specific high-value sites first
    priority_sites = [
        "Cloudflare",      # Bot protection leader
        "Nike",            # E-commerce with strong anti-bot
        "Supreme",         # Extreme difficulty
        "Chase Bank",      # Failed in original test
        "Instagram",       # Social media giant
        "Bot Test",        # Detection test site
        "FingerprintJS",   # Fingerprinting test
        "PixelScan"        # Comprehensive analysis
    ]
    
    print("[INIT] Stealth Browser Challenge Test")
    print(f"[INFO] Testing {len(priority_sites)} priority sites")
    print("=" * 60)
    
    # Run tests
    await tester.run_tests(priority_sites)
    
    return True

if __name__ == "__main__":
    # Quick compliance test
    if os.environ.get("STANDALONE_TEST") == "1":
        print("[OK] Stealth browser challenge tester loads successfully")
        sys.exit(0)
        
    # Run full test
    success = asyncio.run(main())
    sys.exit(0 if success else 1)