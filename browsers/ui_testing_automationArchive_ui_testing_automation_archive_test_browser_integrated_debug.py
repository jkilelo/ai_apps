#!/usr/bin/env python3
"""
Debug test for browser_integrated.py with enhanced logging
Identifies and monitors issues during testing
"""

import asyncio
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_debug.log', mode='w')
    ]
)
logger = logging.getLogger(__name__)

# Import the integrated browser module
from ui_testing_automation.base.browser import (
    UltimateStealthBrowser,
    StealthConfig,
    StealthLevel,
    ExtractionResult
)

# ============================================================================
# DEBUG TEST CONFIGURATION
# ============================================================================

TEST_CONFIG = {
    "headless": True,
    "timeout": 30,
    "max_concurrent": 1,  # Run sequentially for better debugging
    "save_results": True,
    "results_file": "test_debug_results.json"
}

# ============================================================================
# DEBUG TEST RUNNER
# ============================================================================

class DebugTestRunner:
    """Debug test runner with enhanced monitoring"""
    
    def __init__(self):
        """Initialize debug test runner"""
        self.results = []
        self.issues_found = []
        
    async def test_single_site(self, url: str, name: str, protection: str) -> Dict[str, Any]:
        """Test a single site with detailed monitoring"""
        
        print(f"\n{'='*60}")
        print(f"[DEBUG TEST] {name}")
        print(f"URL: {url}")
        print(f"Protection: {protection}")
        print(f"{'='*60}")
        
        # Configure browser
        config = StealthConfig(
            level=StealthLevel.MAXIMUM,
            headless=TEST_CONFIG['headless'],
            enable_human_delays=True,
            enable_human_mouse=True,
            enable_human_typing=True,
            enable_micro_behaviors=True,
            timeout=TEST_CONFIG['timeout']
        )
        
        start_time = time.time()
        result = {
            'name': name,
            'url': url,
            'protection': protection,
            'timestamp': datetime.now().isoformat(),
            'issues': []
        }
        
        try:
            print("[1] Creating browser instance...")
            browser = UltimateStealthBrowser(config)
            
            print("[2] Initializing browser...")
            await browser.initialize()
            print("    [OK] Browser initialized")
            
            print("[3] Navigating to URL...")
            nav_success = await browser.navigate(url)
            if nav_success:
                print("    [OK] Navigation successful")
            else:
                print("    [ISSUE] Navigation failed")
                result['issues'].append("Navigation failed")
            
            print("[4] Getting page title...")
            try:
                if browser.page:
                    title = await browser.page.title()
                    print(f"    [OK] Page title: {title[:50]}...")
                    result['page_title'] = title
                else:
                    print("    [ISSUE] browser.page is None")
                    result['issues'].append("browser.page is None")
            except Exception as e:
                print(f"    [ERROR] Failed to get title: {e}")
                result['issues'].append(f"Title error: {str(e)}")
            
            print("[5] Detecting framework...")
            try:
                if browser.page:
                    from ui_testing_automation.base.browser import DetectionSystem
                    framework = await DetectionSystem.detect_framework(browser.page)
                    if framework:
                        print(f"    [OK] Framework detected: {framework}")
                        result['framework'] = framework
                    else:
                        print("    [INFO] No framework detected")
                else:
                    print("    [ISSUE] Cannot detect framework - page is None")
                    result['issues'].append("Cannot detect framework - page is None")
            except Exception as e:
                print(f"    [ERROR] Framework detection failed: {e}")
                result['issues'].append(f"Framework detection error: {str(e)}")
            
            print("[6] Detecting CAPTCHA...")
            try:
                if browser.page:
                    from ui_testing_automation.base.browser import DetectionSystem
                    captcha_info = await DetectionSystem.detect_captcha(browser.page)
                    if captcha_info['detected']:
                        print(f"    [WARNING] CAPTCHA detected: {captcha_info['type']}")
                        result['captcha'] = captcha_info['type']
                    else:
                        print("    [OK] No CAPTCHA detected")
                else:
                    print("    [ISSUE] Cannot detect CAPTCHA - page is None")
                    result['issues'].append("Cannot detect CAPTCHA - page is None")
            except Exception as e:
                print(f"    [ERROR] CAPTCHA detection failed: {e}")
                result['issues'].append(f"CAPTCHA detection error: {str(e)}")
            
            print("[7] Extracting elements...")
            try:
                # Use the extraction method directly
                from ui_testing_automation.base.browser import DOMExtractionStrategy
                strategy = DOMExtractionStrategy()
                
                if browser.page:
                    elements = await strategy.extract(browser.page)
                    print(f"    [OK] Extracted {len(elements)} elements")
                    result['elements_count'] = len(elements)
                    
                    # Check for specific issues
                    if len(elements) == 0:
                        print("    [WARNING] No elements extracted")
                        result['issues'].append("No elements extracted")
                        
                        # Try to get page content for debugging
                        try:
                            content = await browser.page.content()
                            print(f"    [DEBUG] Page content length: {len(content)}")
                            if len(content) < 1000:
                                print("    [WARNING] Page content is very small")
                                result['issues'].append("Page content is very small")
                        except:
                            pass
                else:
                    print("    [ISSUE] Cannot extract elements - page is None")
                    result['issues'].append("Cannot extract elements - page is None")
                    
            except Exception as e:
                print(f"    [ERROR] Element extraction failed: {e}")
                result['issues'].append(f"Extraction error: {str(e)}")
                import traceback
                print(f"    [TRACEBACK] {traceback.format_exc()}")
            
            print("[8] Getting browser metrics...")
            try:
                metrics = await browser.get_metrics()
                print(f"    [OK] Requests: {metrics['requests_total']}, Success: {metrics['requests_success']}")
                result['metrics'] = metrics
            except Exception as e:
                print(f"    [ERROR] Failed to get metrics: {e}")
                result['issues'].append(f"Metrics error: {str(e)}")
            
            print("[9] Checking browser health...")
            try:
                if browser.monitor:
                    health = await browser.monitor.check_health()
                    print(f"    [OK] Health: {'Healthy' if health['healthy'] else 'Unhealthy'}")
                    if not health['healthy']:
                        result['issues'].append(f"Browser unhealthy: {health}")
                else:
                    print("    [INFO] No monitor available")
            except Exception as e:
                print(f"    [ERROR] Health check failed: {e}")
            
            print("[10] Cleaning up...")
            await browser.cleanup()
            print("    [OK] Cleanup complete")
            
            result['success'] = len(result['issues']) == 0
            result['extraction_time'] = round(time.time() - start_time, 2)
            
        except Exception as e:
            print(f"\n[CRITICAL ERROR] {e}")
            import traceback
            traceback.print_exc()
            result['success'] = False
            result['error'] = str(e)
            result['extraction_time'] = round(time.time() - start_time, 2)
            result['issues'].append(f"Critical error: {str(e)}")
        
        # Summary
        print(f"\n[SUMMARY]")
        print(f"  Success: {result.get('success', False)}")
        print(f"  Time: {result.get('extraction_time', 0)}s")
        print(f"  Issues found: {len(result['issues'])}")
        if result['issues']:
            for issue in result['issues']:
                print(f"    - {issue}")
        
        return result
    
    async def run_debug_tests(self) -> None:
        """Run debug tests on selected sites"""
        
        print("[DEBUG TEST SUITE]")
        print("=" * 60)
        print("Testing browser_integrated.py with detailed monitoring")
        print("=" * 60)
        
        # Test sites - one from each category with different protection levels
        test_sites = [
            # Simple test first
            {
                'url': 'https://example.com',
                'name': 'Example.com',
                'protection': 'None'
            },
            # Medium difficulty
            {
                'url': 'https://bot.sannysoft.com',
                'name': 'Bot Test',
                'protection': 'Detection Tests'
            },
            # High difficulty - Cloudflare
            {
                'url': 'https://www.cloudflare.com',
                'name': 'Cloudflare',
                'protection': 'Cloudflare'
            },
            # Very high difficulty - Meta
            {
                'url': 'https://www.instagram.com',
                'name': 'Instagram',
                'protection': 'Meta Custom'
            },
            # Extreme difficulty - PerimeterX
            {
                'url': 'https://www.supreme.com',
                'name': 'Supreme',
                'protection': 'PerimeterX'
            }
        ]
        
        for site in test_sites:
            result = await self.test_single_site(
                site['url'],
                site['name'],
                site['protection']
            )
            self.results.append(result)
            
            # Collect issues
            if result['issues']:
                self.issues_found.extend([
                    f"{site['name']}: {issue}" for issue in result['issues']
                ])
            
            # Small delay between tests
            await asyncio.sleep(2)
        
        # Generate report
        self.generate_report()
    
    def generate_report(self) -> None:
        """Generate debug report"""
        
        print("\n" + "=" * 60)
        print("[DEBUG REPORT]")
        print("=" * 60)
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r.get('success', False))
        
        print(f"\nOverall Results:")
        print(f"  Total sites tested: {total}")
        print(f"  Successful: {successful}/{total}")
        print(f"  Success rate: {(successful/total*100):.1f}%")
        
        print(f"\nIssues Found ({len(self.issues_found)}):")
        if self.issues_found:
            for issue in self.issues_found:
                print(f"  - {issue}")
        else:
            print("  No issues found!")
        
        print(f"\nPer-Site Results:")
        for result in self.results:
            status = "OK" if result.get('success') else "FAILED"
            print(f"\n  {result['name']} [{status}]")
            print(f"    URL: {result['url']}")
            print(f"    Time: {result.get('extraction_time', 0)}s")
            if 'page_title' in result:
                print(f"    Title: {result['page_title'][:50]}...")
            if 'framework' in result:
                print(f"    Framework: {result['framework']}")
            if 'captcha' in result:
                print(f"    CAPTCHA: {result['captcha']}")
            if 'elements_count' in result:
                print(f"    Elements: {result['elements_count']}")
            if result['issues']:
                print(f"    Issues:")
                for issue in result['issues']:
                    print(f"      - {issue}")
        
        # Common issues analysis
        print(f"\n[ISSUE ANALYSIS]")
        issue_patterns = {}
        for issue in self.issues_found:
            # Categorize issues
            if "browser.page is None" in issue:
                category = "Page initialization"
            elif "No elements extracted" in issue:
                category = "Element extraction"
            elif "Navigation failed" in issue:
                category = "Navigation"
            elif "'NoneType' object" in issue:
                category = "NoneType errors"
            elif "validation error" in issue:
                category = "Pydantic validation"
            else:
                category = "Other"
            
            if category not in issue_patterns:
                issue_patterns[category] = 0
            issue_patterns[category] += 1
        
        if issue_patterns:
            print("\nIssue Categories:")
            for category, count in sorted(issue_patterns.items(), key=lambda x: x[1], reverse=True):
                print(f"  {category}: {count}")
        
        # Save results
        with open(TEST_CONFIG['results_file'], 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': self.results,
                'issues': self.issues_found,
                'issue_patterns': issue_patterns
            }, f, indent=2)
        
        print(f"\nResults saved to: {TEST_CONFIG['results_file']}")
        print("=" * 60)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main debug execution"""
    
    runner = DebugTestRunner()
    await runner.run_debug_tests()

if __name__ == "__main__":
    print("[STARTING DEBUG TEST]")
    print("Monitoring browser_integrated.py for issues...")
    
    try:
        asyncio.run(main())
        print("\n[DEBUG TEST COMPLETE]")
    except KeyboardInterrupt:
        print("\n[TEST INTERRUPTED]")
    except Exception as e:
        print(f"\n[TEST ERROR]: {e}")
        import traceback
        traceback.print_exc()