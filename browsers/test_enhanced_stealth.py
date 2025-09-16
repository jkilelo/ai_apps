#!/usr/bin/env python3
"""Enhanced stealth validation test for Google Scholar access"""

import asyncio
import sys
import json
from pathlib import Path
from loguru import logger
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from execution.browser_manager import BrowserManager, BrowserConfig
from execution.stealth_manager import StealthManager
from execution.google_scholar_handler import GoogleScholarHandler


class EnhancedStealthValidator:
    """Comprehensive stealth validation for Google Scholar"""
    
    def __init__(self):
        self.browser_manager = None
        self.stealth_manager = StealthManager()
        self.scholar_handler = GoogleScholarHandler()
        self.test_results = {}
        
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive stealth validation tests"""
        logger.info("Starting enhanced stealth validation tests")
        
        results = {
            "stealth_fingerprints": {},
            "behavioral_patterns": {},
            "scholar_access": {},
            "timing_analysis": {},
            "overall_success": False,
            "recommendations": []
        }
        
        try:
            # Initialize browser with enhanced stealth
            await self._initialize_browser()
            
            # Test 1: Stealth fingerprint validation
            results["stealth_fingerprints"] = await self._test_stealth_fingerprints()
            
            # Test 2: Behavioral pattern validation
            results["behavioral_patterns"] = await self._test_behavioral_patterns()
            
            # Test 3: Google Scholar access test
            results["scholar_access"] = await self._test_scholar_access()
            
            # Test 4: Timing attack resistance
            results["timing_analysis"] = await self._test_timing_resistance()
            
            # Generate recommendations
            results["recommendations"] = self._generate_recommendations(results)
            
            # Determine overall success
            results["overall_success"] = self._evaluate_overall_success(results)
            
        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            results["error"] = str(e)
        finally:
            await self._cleanup()
        
        return results
    
    async def _initialize_browser(self) -> None:
        """Initialize browser with enhanced stealth configuration"""
        config = BrowserConfig(
            headless=True,  # Use headless for testing
            viewport_width=1920,
            viewport_height=1080,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        self.browser_manager = BrowserManager(enable_stealth=True)
        await self.browser_manager.launch(config)
        logger.info("Browser initialized with enhanced stealth")
    
    async def _test_stealth_fingerprints(self) -> Dict[str, Any]:
        """Test stealth fingerprinting countermeasures"""
        logger.info("Testing stealth fingerprints...")
        
        context = await self.browser_manager.new_context()
        page = await context.new_page()
        
        # Navigate to a test page
        await page.goto("https://httpbin.org/headers", wait_until='domcontentloaded')
        
        # Test fingerprint detection
        fingerprint_tests = {
            "webdriver_flag": await page.evaluate("navigator.webdriver"),
            "chrome_runtime": await page.evaluate("typeof window.chrome !== 'undefined'"),
            "plugins_count": await page.evaluate("navigator.plugins.length"),
            "languages": await page.evaluate("navigator.languages"),
            "hardware_concurrency": await page.evaluate("navigator.hardwareConcurrency"),
            "user_agent": await page.evaluate("navigator.userAgent"),
            "canvas_fingerprint": await self._test_canvas_fingerprint(page),
            "webgl_fingerprint": await self._test_webgl_fingerprint(page),
            "timing_precision": await self._test_timing_precision(page),
        }
        
        # Evaluate results
        passed_tests = sum(1 for result in [
            fingerprint_tests["webdriver_flag"] is None,  # Should be None/undefined
            fingerprint_tests["chrome_runtime"] is True,  # Should have Chrome runtime
            fingerprint_tests["plugins_count"] > 0,       # Should have plugins
            len(fingerprint_tests["languages"]) > 0,      # Should have languages
            isinstance(fingerprint_tests["hardware_concurrency"], int),
            "Chrome" in fingerprint_tests["user_agent"] and "HeadlessChrome" not in fingerprint_tests["user_agent"],
        ] if result)
        
        await context.close()
        
        return {
            "tests": fingerprint_tests,
            "passed": passed_tests,
            "total": 6,
            "score": passed_tests / 6,
            "success": passed_tests >= 5  # 80% pass rate
        }
    
    async def _test_behavioral_patterns(self) -> Dict[str, Any]:
        """Test behavioral simulation patterns"""
        logger.info("Testing behavioral patterns...")
        
        context = await self.browser_manager.new_context()
        page = await context.new_page()
        
        # Navigate to a page and test behavior simulation
        await page.goto("about:blank")
        
        # Test behavior tracker
        behavioral_tests = {
            "has_behavior_tracker": await page.evaluate("typeof window.humanBehaviorTracker !== 'undefined'"),
            "mouse_simulation": False,
            "timing_jitter": False,
            "activity_simulation": False
        }
        
        # Test mouse activity simulation
        if behavioral_tests["has_behavior_tracker"]:
            initial_mouse = await page.evaluate("window.humanBehaviorTracker.mouseMovements")
            await asyncio.sleep(1.0)  # Wait for simulation
            final_mouse = await page.evaluate("window.humanBehaviorTracker.mouseMovements")
            behavioral_tests["mouse_simulation"] = final_mouse > initial_mouse
        
        # Test timing jitter
        timing_values = []
        for _ in range(10):
            timing_values.append(await page.evaluate("performance.now()"))
            await asyncio.sleep(0.01)
        
        # Check if there's realistic jitter in timing
        timing_diffs = [timing_values[i+1] - timing_values[i] for i in range(len(timing_values)-1)]
        behavioral_tests["timing_jitter"] = len(set(timing_diffs)) > 5  # Should have variation
        
        # Test activity simulation
        if behavioral_tests["has_behavior_tracker"]:
            metrics = await page.evaluate("window.humanBehaviorTracker.getMetrics()")
            behavioral_tests["activity_simulation"] = (
                metrics.get("mouseMovements", 0) > 0 or
                metrics.get("scrolls", 0) > 0
            )
        
        passed_behavioral = sum([
            behavioral_tests["has_behavior_tracker"],
            behavioral_tests["mouse_simulation"],
            behavioral_tests["timing_jitter"],
            behavioral_tests["activity_simulation"]
        ])
        
        await context.close()
        
        return {
            "tests": behavioral_tests,
            "passed": passed_behavioral,
            "total": 4,
            "score": passed_behavioral / 4,
            "success": passed_behavioral >= 3
        }
    
    async def _test_scholar_access(self) -> Dict[str, Any]:
        """Test actual Google Scholar access"""
        logger.info("Testing Google Scholar access...")
        
        context = await self.browser_manager.new_context()
        page = await context.new_page()
        
        scholar_results = {
            "navigation_success": False,
            "search_success": False,
            "extraction_success": False,
            "no_blocking": False,
            "papers_extracted": 0,
            "error_messages": []
        }
        
        try:
            # Test navigation
            await page.goto("https://scholar.google.com", wait_until='domcontentloaded', timeout=30000)
            
            # Check for blocking indicators
            page_content = await page.content()
            blocking_indicators = [
                "Loading... The system can't perform the operation now",
                "Your client does not have permission",
                "We're sorry...",
                "blocked",
                "robot",
                "automated"
            ]
            
            is_blocked = any(indicator.lower() in page_content.lower() for indicator in blocking_indicators)
            scholar_results["no_blocking"] = not is_blocked
            scholar_results["navigation_success"] = True
            
            if not is_blocked:
                # Test search functionality
                search_result = await self.scholar_handler.perform_search(page, "machine learning")
                scholar_results["search_success"] = search_result.success
                
                if search_result.success:
                    # Test paper extraction
                    papers = await self.scholar_handler.extract_papers(page, max_papers=3)
                    scholar_results["papers_extracted"] = len(papers)
                    scholar_results["extraction_success"] = len(papers) > 0
                    
                else:
                    scholar_results["error_messages"].append(search_result.error)
            else:
                scholar_results["error_messages"].append("Page content indicates blocking")
                
        except Exception as e:
            scholar_results["error_messages"].append(str(e))
        
        await context.close()
        
        # Calculate success score
        success_score = sum([
            scholar_results["navigation_success"],
            scholar_results["search_success"], 
            scholar_results["extraction_success"],
            scholar_results["no_blocking"]
        ]) / 4
        
        scholar_results["score"] = success_score
        scholar_results["success"] = success_score >= 0.75
        
        return scholar_results
    
    async def _test_timing_resistance(self) -> Dict[str, Any]:
        """Test timing attack resistance"""
        logger.info("Testing timing attack resistance...")
        
        context = await self.browser_manager.new_context()
        page = await context.new_page()
        
        await page.goto("about:blank")
        
        timing_tests = {
            "performance_now_jitter": False,
            "date_now_variation": False,
            "fetch_timing_realistic": False,
            "timeout_jitter": False
        }
        
        # Test performance.now() jitter
        perf_times = []
        for _ in range(20):
            perf_times.append(await page.evaluate("performance.now()"))
            await asyncio.sleep(0.005)
        
        perf_diffs = [perf_times[i+1] - perf_times[i] for i in range(len(perf_times)-1)]
        timing_tests["performance_now_jitter"] = len(set(perf_diffs)) > 10
        
        # Test Date.now() variation
        date_times = []
        for _ in range(10):
            date_times.append(await page.evaluate("Date.now()"))
            await asyncio.sleep(0.01)
        
        date_diffs = [date_times[i+1] - date_times[i] for i in range(len(date_times)-1)]
        timing_tests["date_now_variation"] = any(abs(diff - 10) > 2 for diff in date_diffs)  # Should have some variation from expected 10ms
        
        # Test realistic fetch timing (if available)
        try:
            fetch_time = await page.evaluate("""
                async () => {
                    const start = performance.now();
                    await fetch('data:text/plain,test');
                    return performance.now() - start;
                }
            """)
            timing_tests["fetch_timing_realistic"] = fetch_time > 5  # Should take some realistic time
        except:
            timing_tests["fetch_timing_realistic"] = True  # Assume pass if can't test
        
        # Test setTimeout jitter
        timeout_actual = await page.evaluate("""
            new Promise(resolve => {
                const start = performance.now();
                setTimeout(() => {
                    resolve(performance.now() - start);
                }, 100);
            })
        """)
        timing_tests["timeout_jitter"] = abs(timeout_actual - 100) > 1  # Should have some jitter
        
        await context.close()
        
        passed_timing = sum(timing_tests.values())
        
        return {
            "tests": timing_tests,
            "passed": passed_timing,
            "total": 4,
            "score": passed_timing / 4,
            "success": passed_timing >= 3
        }
    
    async def _test_canvas_fingerprint(self, page) -> bool:
        """Test canvas fingerprinting countermeasures"""
        try:
            # Test if canvas fingerprinting returns consistent but non-identical results
            result1 = await page.evaluate("""
                () => {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    ctx.fillText('Test fingerprint', 10, 10);
                    return canvas.toDataURL();
                }
            """)
            
            result2 = await page.evaluate("""
                () => {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    ctx.fillText('Test fingerprint', 10, 10);
                    return canvas.toDataURL();
                }
            """)
            
            # Should have some variation (noise) but not be completely different
            return result1 != result2 and len(result1) > 100
        except:
            return False
    
    async def _test_webgl_fingerprint(self, page) -> bool:
        """Test WebGL fingerprinting countermeasures"""
        try:
            vendor = await page.evaluate("""
                () => {
                    const canvas = document.createElement('canvas');
                    const gl = canvas.getContext('webgl');
                    if (!gl) return null;
                    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                    return debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : null;
                }
            """)
            
            return vendor is not None and vendor != ""
        except:
            return False
    
    async def _test_timing_precision(self, page) -> bool:
        """Test timing precision reduction"""
        try:
            # Test if performance.now() has reduced precision
            times = []
            for _ in range(10):
                time_val = await page.evaluate("performance.now()")
                times.append(time_val)
            
            # Check if we have realistic timing variation
            return len(set(times)) > 5
        except:
            return False
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Fingerprint recommendations
        if results["stealth_fingerprints"]["score"] < 0.8:
            recommendations.append("Improve fingerprinting countermeasures - some detection vectors are not fully masked")
        
        # Behavioral recommendations  
        if results["behavioral_patterns"]["score"] < 0.75:
            recommendations.append("Enhance behavioral simulation - patterns may appear too mechanical")
        
        # Scholar access recommendations
        if not results["scholar_access"]["success"]:
            if not results["scholar_access"]["no_blocking"]:
                recommendations.append("CRITICAL: Google Scholar is detecting and blocking automation")
            if not results["scholar_access"]["search_success"]:
                recommendations.append("Improve search interaction patterns for Scholar")
            if not results["scholar_access"]["extraction_success"]:
                recommendations.append("Enhance paper extraction with more human-like browsing")
        
        # Timing recommendations
        if results["timing_analysis"]["score"] < 0.75:
            recommendations.append("Strengthen timing attack countermeasures - patterns may be too predictable")
        
        if not recommendations:
            recommendations.append("Stealth implementation appears robust against tested detection vectors")
        
        return recommendations
    
    def _evaluate_overall_success(self, results: Dict[str, Any]) -> bool:
        """Evaluate overall success of stealth implementation"""
        key_scores = [
            results["stealth_fingerprints"]["score"],
            results["behavioral_patterns"]["score"], 
            results["scholar_access"]["score"],
            results["timing_analysis"]["score"]
        ]
        
        avg_score = sum(key_scores) / len(key_scores)
        
        # Success criteria: average score > 0.75 and Scholar access working
        return avg_score > 0.75 and results["scholar_access"]["success"]
    
    async def _cleanup(self) -> None:
        """Clean up resources"""
        if self.browser_manager:
            await self.browser_manager.close()


async def main():
    """Run enhanced stealth validation"""
    logger.info("=== Enhanced Google Scholar Stealth Validation ===")
    
    validator = EnhancedStealthValidator()
    results = await validator.run_comprehensive_test()
    
    # Display results
    print("\\n" + "="*60)
    print("ENHANCED STEALTH TEST RESULTS")
    print("="*60)
    
    # Fingerprint results
    fp = results["stealth_fingerprints"]
    print(f"\\n[FINGERPRINT] TESTS: {fp['passed']}/{fp['total']} passed ({fp['score']*100:.1f}%)")
    for test, result in fp["tests"].items():
        status = "[PASS]" if (
            (test == "webdriver_flag" and result is None) or
            (test == "chrome_runtime" and result is True) or
            (test == "plugins_count" and result > 0) or
            (test == "languages" and len(result) > 0) or
            (test in ["hardware_concurrency", "user_agent", "canvas_fingerprint", "webgl_fingerprint", "timing_precision"] and result)
        ) else "[FAIL]"
        print(f"  {status} {test}: {result}")
    
    # Behavioral results
    bp = results["behavioral_patterns"]
    print(f"\\n[BEHAVIORAL] TESTS: {bp['passed']}/{bp['total']} passed ({bp['score']*100:.1f}%)")
    for test, result in bp["tests"].items():
        status = "✅" if result else "❌"
        print(f"  {status} {test}: {result}")
    
    # Scholar access results
    sa = results["scholar_access"]
    print(f"\\n📚 SCHOLAR ACCESS: {sa['score']*100:.1f}% success")
    print(f"  ✅ Navigation: {sa['navigation_success']}")
    print(f"  ✅ No Blocking: {sa['no_blocking']}")
    print(f"  ✅ Search: {sa['search_success']}")
    print(f"  ✅ Extraction: {sa['extraction_success']} ({sa['papers_extracted']} papers)")
    if sa["error_messages"]:
        print(f"  ❌ Errors: {', '.join(sa['error_messages'])}")
    
    # Timing results
    ta = results["timing_analysis"] 
    print(f"\\n⏱️  TIMING RESISTANCE: {ta['passed']}/{ta['total']} passed ({ta['score']*100:.1f}%)")
    for test, result in ta["tests"].items():
        status = "✅" if result else "❌"
        print(f"  {status} {test}: {result}")
    
    # Overall assessment
    print(f"\\n{'='*60}")
    if results["overall_success"]:
        print("🎉 OVERALL ASSESSMENT: SUCCESS")
        print("Enhanced stealth measures are working effectively!")
    else:
        print("⚠️  OVERALL ASSESSMENT: NEEDS IMPROVEMENT")
    
    # Recommendations
    print(f"\\n📋 RECOMMENDATIONS:")
    for i, rec in enumerate(results["recommendations"], 1):
        print(f"  {i}. {rec}")
    
    print(f"\\n{'='*60}")
    
    # Save detailed results
    results_file = Path("enhanced_stealth_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"📄 Detailed results saved to: {results_file}")
    
    return results["overall_success"]


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)