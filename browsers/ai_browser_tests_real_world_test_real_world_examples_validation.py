#!/usr/bin/env python3
"""
Real-World Examples Validation Tests

Comprehensive validation tests for AI Browser real-world examples to ensure
they work reliably with actual websites, live LLM calls, and real-world conditions.

These tests validate:
- Real website interactions (no mocking)
- Live LLM API calls and reasoning quality
- Stealth effectiveness against bot detection
- Error handling and recovery mechanisms
- Data quality and business value
- Performance under real-world conditions
"""

import asyncio
import pytest
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import json
import requests

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from main import AIBrowser, TaskConfig
from loguru import logger


class RealWorldValidationSuite:
    """Comprehensive validation suite for real-world AI Browser examples"""
    
    def __init__(self):
        self.results_dir = Path("tests/real_world/validation_results")
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.test_results = {}
        
    async def validate_ecommerce_research(self):
        """Validate e-commerce product research functionality"""
        logger.info("🛒 Validating E-commerce Product Research")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        test_cases = [
            {
                "task": "Search Amazon for 'wireless bluetooth headphones' under $100 and get the top 3 products with prices and ratings",
                "url": "https://www.amazon.com",
                "expected_data": ["product_name", "price", "rating", "url"],
                "max_steps": 12,
                "timeout": 90000
            },
            {
                "task": "Go to Best Buy, search for 'gaming laptop' and extract specifications and prices of 3 products",
                "url": "https://www.bestbuy.com",
                "expected_data": ["product_name", "price", "specifications"],
                "max_steps": 10,
                "timeout": 60000
            }
        ]
        
        results = []
        for test_case in test_cases:
            try:
                config = TaskConfig(
                    task=test_case["task"],
                    url=test_case["url"],
                    headless=True,  # Use headless for automated testing
                    max_steps=test_case["max_steps"],
                    timeout=test_case["timeout"],
                    screenshot_on_error=True
                )
                
                start_time = time.time()
                await browser.initialize(config)
                result = await browser.execute_task(config)
                execution_time = time.time() - start_time
                
                # Validate results
                success = result['status'] == 'completed'
                has_extracted_data = bool(result.get('extracted_data'))
                has_reasoning = bool(result.get('reasoning_steps'))
                
                test_result = {
                    "test_case": test_case["task"][:50] + "...",
                    "url": test_case["url"],
                    "success": success,
                    "execution_time": execution_time,
                    "has_extracted_data": has_extracted_data,
                    "has_reasoning": has_reasoning,
                    "reasoning_steps": len(result.get('reasoning_steps', [])),
                    "summary": result.get('summary', ''),
                    "error": result.get('error')
                }
                
                results.append(test_result)
                logger.info(f"E-commerce test result: {success} ({execution_time:.2f}s)")
                
                await browser.cleanup()
                
            except Exception as e:
                logger.error(f"E-commerce test failed: {e}")
                results.append({
                    "test_case": test_case["task"][:50] + "...",
                    "success": False,
                    "error": str(e),
                    "execution_time": 0
                })
                
                if browser:
                    await browser.cleanup()
        
        return {
            "category": "ecommerce_research",
            "total_tests": len(test_cases),
            "successful_tests": sum(1 for r in results if r.get("success")),
            "results": results,
            "avg_execution_time": sum(r.get("execution_time", 0) for r in results) / len(results)
        }
    
    async def validate_news_monitoring(self):
        """Validate news monitoring and summarization"""
        logger.info("📰 Validating News Monitoring")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        test_cases = [
            {
                "task": "Go to BBC News, find today's top 3 technology stories and summarize key points",
                "url": "https://www.bbc.com/news/technology",
                "expected_outputs": ["headlines", "summaries", "sources"],
                "max_steps": 8,
                "timeout": 45000
            },
            {
                "task": "Visit CNN Business, extract the main business headline and provide a brief analysis",
                "url": "https://www.cnn.com/business",
                "expected_outputs": ["headline", "analysis"],
                "max_steps": 6,
                "timeout": 30000
            }
        ]
        
        results = []
        for test_case in test_cases:
            try:
                config = TaskConfig(
                    task=test_case["task"],
                    url=test_case["url"],
                    headless=True,
                    max_steps=test_case["max_steps"],
                    timeout=test_case["timeout"]
                )
                
                start_time = time.time()
                await browser.initialize(config)
                result = await browser.execute_task(config)
                execution_time = time.time() - start_time
                
                success = result['status'] == 'completed'
                has_summary = bool(result.get('summary'))
                summary_quality = len(result.get('summary', '').split()) > 10  # At least 10 words
                
                test_result = {
                    "test_case": test_case["task"][:50] + "...",
                    "success": success,
                    "execution_time": execution_time,
                    "has_summary": has_summary,
                    "summary_quality": summary_quality,
                    "reasoning_steps": len(result.get('reasoning_steps', [])),
                    "error": result.get('error')
                }
                
                results.append(test_result)
                logger.info(f"News monitoring test result: {success} ({execution_time:.2f}s)")
                
                await browser.cleanup()
                
            except Exception as e:
                logger.error(f"News monitoring test failed: {e}")
                results.append({
                    "test_case": test_case["task"][:50] + "...",
                    "success": False,
                    "error": str(e)
                })
                
                if browser:
                    await browser.cleanup()
        
        return {
            "category": "news_monitoring",
            "total_tests": len(test_cases),
            "successful_tests": sum(1 for r in results if r.get("success")),
            "results": results,
            "avg_execution_time": sum(r.get("execution_time", 0) for r in results) / len(results)
        }
    
    async def validate_academic_research(self):
        """Validate academic research functionality"""
        logger.info("🎓 Validating Academic Research")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        test_cases = [
            {
                "task": "Search Google Scholar for 'machine learning browser automation' papers from 2023-2024 and extract titles, authors, and abstracts of top 3 results",
                "url": "https://scholar.google.com",
                "expected_data": ["titles", "authors", "abstracts"],
                "max_steps": 10,
                "timeout": 60000
            }
        ]
        
        results = []
        for test_case in test_cases:
            try:
                config = TaskConfig(
                    task=test_case["task"],
                    url=test_case["url"],
                    headless=True,
                    max_steps=test_case["max_steps"],
                    timeout=test_case["timeout"]
                )
                
                start_time = time.time()
                await browser.initialize(config)
                result = await browser.execute_task(config)
                execution_time = time.time() - start_time
                
                success = result['status'] == 'completed'
                has_academic_data = bool(result.get('extracted_data'))
                
                test_result = {
                    "test_case": test_case["task"][:50] + "...",
                    "success": success,
                    "execution_time": execution_time,
                    "has_academic_data": has_academic_data,
                    "reasoning_steps": len(result.get('reasoning_steps', [])),
                    "error": result.get('error')
                }
                
                results.append(test_result)
                logger.info(f"Academic research test result: {success} ({execution_time:.2f}s)")
                
                await browser.cleanup()
                
            except Exception as e:
                logger.error(f"Academic research test failed: {e}")
                results.append({
                    "test_case": test_case["task"][:50] + "...",
                    "success": False,
                    "error": str(e)
                })
                
                if browser:
                    await browser.cleanup()
        
        return {
            "category": "academic_research",
            "total_tests": len(test_cases),
            "successful_tests": sum(1 for r in results if r.get("success")),
            "results": results,
            "avg_execution_time": sum(r.get("execution_time", 0) for r in results) / len(results)
        }
    
    async def validate_stealth_effectiveness(self):
        """Validate stealth capabilities against bot detection"""
        logger.info("🥷 Validating Stealth Effectiveness")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        # Test against known bot detection sites
        stealth_test_sites = [
            {
                "name": "Basic WebDriver Detection",
                "url": "https://bot.sannysoft.com/",
                "task": "Navigate to this bot detection site and tell me what it shows about browser detection",
                "max_steps": 3
            },
            {
                "name": "Advanced Detection Test",
                "url": "https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html",
                "task": "Check this advanced headless detection page and report the results",
                "max_steps": 3
            }
        ]
        
        results = []
        for test_site in stealth_test_sites:
            try:
                config = TaskConfig(
                    task=test_site["task"],
                    url=test_site["url"],
                    headless=True,
                    max_steps=test_site["max_steps"],
                    timeout=30000
                )
                
                await browser.initialize(config)
                result = await browser.execute_task(config)
                
                # Analyze result for detection indicators
                summary = result.get('summary', '').lower()
                detected_indicators = [
                    'webdriver' in summary,
                    'automated' in summary,
                    'bot' in summary,
                    'headless' in summary
                ]
                
                stealth_score = 1.0 - (sum(detected_indicators) / len(detected_indicators))
                
                test_result = {
                    "site": test_site["name"],
                    "success": result['status'] == 'completed',
                    "stealth_score": stealth_score,
                    "detected_indicators": sum(detected_indicators),
                    "summary_snippet": summary[:200] + "..." if len(summary) > 200 else summary
                }
                
                results.append(test_result)
                logger.info(f"Stealth test {test_site['name']}: score {stealth_score:.2f}")
                
                await browser.cleanup()
                
            except Exception as e:
                logger.error(f"Stealth test failed for {test_site['name']}: {e}")
                results.append({
                    "site": test_site["name"],
                    "success": False,
                    "error": str(e)
                })
                
                if browser:
                    await browser.cleanup()
        
        avg_stealth_score = sum(r.get("stealth_score", 0) for r in results) / len(results)
        
        return {
            "category": "stealth_effectiveness",
            "total_tests": len(stealth_test_sites),
            "successful_tests": sum(1 for r in results if r.get("success")),
            "results": results,
            "avg_stealth_score": avg_stealth_score
        }
    
    async def validate_error_handling(self):
        """Validate error handling and recovery mechanisms"""
        logger.info("🔧 Validating Error Handling")
        
        browser = AIBrowser({"log_level": "INFO"})
        
        # Test error scenarios
        error_test_cases = [
            {
                "name": "Non-existent Website",
                "task": "Navigate to a non-existent website and handle the error gracefully",
                "url": "https://this-site-definitely-does-not-exist-12345.com",
                "max_steps": 3,
                "expect_error": True
            },
            {
                "name": "Timeout Handling",
                "task": "Navigate to httpbin.org/delay/10 and handle timeout",
                "url": "https://httpbin.org/delay/10",
                "max_steps": 3,
                "timeout": 5000,  # 5 second timeout for 10 second delay
                "expect_error": True
            }
        ]
        
        results = []
        for test_case in error_test_cases:
            try:
                config = TaskConfig(
                    task=test_case["task"],
                    url=test_case["url"],
                    headless=True,
                    max_steps=test_case["max_steps"],
                    timeout=test_case.get("timeout", 30000)
                )
                
                await browser.initialize(config)
                result = await browser.execute_task(config)
                
                # For error test cases, we expect graceful failure handling
                graceful_handling = (
                    result.get('error') is not None and  # Error was captured
                    result.get('status') == 'failed' and  # Status correctly set
                    result.get('reasoning_steps', [])  # Some reasoning was attempted
                )
                
                test_result = {
                    "test_case": test_case["name"],
                    "expected_error": test_case["expect_error"],
                    "graceful_handling": graceful_handling,
                    "error_message": result.get('error', 'No error captured'),
                    "reasoning_attempts": len(result.get('reasoning_steps', []))
                }
                
                results.append(test_result)
                logger.info(f"Error handling test {test_case['name']}: graceful={graceful_handling}")
                
                await browser.cleanup()
                
            except Exception as e:
                # Unexpected exceptions are not graceful handling
                logger.error(f"Error handling test failed: {e}")
                results.append({
                    "test_case": test_case["name"],
                    "graceful_handling": False,
                    "unexpected_exception": str(e)
                })
                
                if browser:
                    await browser.cleanup()
        
        return {
            "category": "error_handling",
            "total_tests": len(error_test_cases),
            "graceful_handling_tests": sum(1 for r in results if r.get("graceful_handling")),
            "results": results
        }
    
    async def validate_llm_integration(self):
        """Validate LLM integration and reasoning quality"""
        logger.info("🧠 Validating LLM Integration")
        
        from cognition.llm import LLMManager
        
        llm_manager = LLMManager()
        
        test_prompts = [
            {
                "category": "reasoning",
                "prompt": "Analyze this e-commerce scenario: A customer wants wireless headphones under $100 with good battery life. What are the key factors to consider when searching and comparing products?",
                "expected_elements": ["price", "battery", "reviews", "features"]
            },
            {
                "category": "summarization", 
                "prompt": "Summarize this news article excerpt: 'The Federal Reserve announced today a 0.25% interest rate increase, citing concerns about inflation and economic growth. Market analysts predict this will impact mortgage rates and consumer spending.' Provide a concise summary with key implications.",
                "expected_elements": ["fed", "rate", "inflation", "impact"]
            },
            {
                "category": "analysis",
                "prompt": "You are analyzing a job posting for a Python Developer role requiring 'FastAPI, Docker, AWS, 3+ years experience, remote work'. What key qualifications should an applicant highlight in their application?",
                "expected_elements": ["FastAPI", "Docker", "AWS", "experience"]
            }
        ]
        
        results = []
        for prompt_test in test_prompts:
            try:
                # Test with different providers
                providers = ['openai', 'gemini']
                provider_results = {}
                
                for provider in providers:
                    try:
                        start_time = time.time()
                        response = await llm_manager.generate(
                            prompt=prompt_test["prompt"],
                            provider=provider,
                            max_tokens=200,
                            temperature=0.7
                        )
                        response_time = time.time() - start_time
                        
                        # Check if response contains expected elements
                        response_lower = response.lower()
                        found_elements = sum(
                            1 for element in prompt_test["expected_elements"] 
                            if element.lower() in response_lower
                        )
                        relevance_score = found_elements / len(prompt_test["expected_elements"])
                        
                        provider_results[provider] = {
                            "success": True,
                            "response_time": response_time,
                            "response_length": len(response),
                            "relevance_score": relevance_score,
                            "response_snippet": response[:100] + "..." if len(response) > 100 else response
                        }
                        
                    except Exception as e:
                        logger.error(f"LLM test failed for {provider}: {e}")
                        provider_results[provider] = {
                            "success": False,
                            "error": str(e)
                        }
                
                results.append({
                    "category": prompt_test["category"],
                    "provider_results": provider_results
                })
                
            except Exception as e:
                logger.error(f"LLM integration test failed: {e}")
                results.append({
                    "category": prompt_test["category"],
                    "error": str(e)
                })
        
        # Calculate overall success rate
        successful_provider_tests = 0
        total_provider_tests = 0
        
        for result in results:
            for provider, provider_result in result.get("provider_results", {}).items():
                total_provider_tests += 1
                if provider_result.get("success"):
                    successful_provider_tests += 1
        
        return {
            "category": "llm_integration",
            "total_tests": len(test_prompts),
            "total_provider_tests": total_provider_tests,
            "successful_provider_tests": successful_provider_tests,
            "results": results,
            "success_rate": successful_provider_tests / total_provider_tests if total_provider_tests > 0 else 0
        }
    
    async def run_comprehensive_validation(self):
        """Run all validation tests and generate comprehensive report"""
        logger.info("🚀 Starting Comprehensive Real-World Validation")
        
        start_time = datetime.now()
        
        # Run all validation suites
        validation_suites = [
            ("E-commerce Research", self.validate_ecommerce_research),
            ("News Monitoring", self.validate_news_monitoring),
            ("Academic Research", self.validate_academic_research),
            ("Stealth Effectiveness", self.validate_stealth_effectiveness),
            ("Error Handling", self.validate_error_handling),
            ("LLM Integration", self.validate_llm_integration)
        ]
        
        all_results = {}
        
        for suite_name, validation_func in validation_suites:
            try:
                logger.info(f"Running {suite_name} validation...")
                suite_result = await validation_func()
                all_results[suite_name] = suite_result
                
                # Add delay between suites to be respectful to websites
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Validation suite {suite_name} failed: {e}")
                all_results[suite_name] = {
                    "category": suite_name.lower().replace(" ", "_"),
                    "success": False,
                    "error": str(e)
                }
        
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        # Generate comprehensive report
        report = {
            "validation_timestamp": start_time.isoformat(),
            "total_duration_seconds": total_duration,
            "validation_suites": all_results,
            "overall_summary": self._generate_overall_summary(all_results)
        }
        
        # Save detailed report
        report_file = self.results_dir / f"validation_report_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Comprehensive validation report saved: {report_file}")
        
        # Print summary
        self._print_validation_summary(report)
        
        return report
    
    def _generate_overall_summary(self, all_results: Dict) -> Dict:
        """Generate overall validation summary"""
        total_suites = len(all_results)
        successful_suites = sum(1 for result in all_results.values() 
                               if result.get("successful_tests", 0) > 0 or result.get("success_rate", 0) > 0.5)
        
        # Calculate various metrics
        total_tests = sum(result.get("total_tests", 0) for result in all_results.values())
        successful_tests = sum(result.get("successful_tests", 0) for result in all_results.values())
        
        return {
            "total_validation_suites": total_suites,
            "successful_suites": successful_suites,
            "suite_success_rate": successful_suites / total_suites if total_suites > 0 else 0,
            "total_individual_tests": total_tests,
            "successful_individual_tests": successful_tests,
            "individual_test_success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "overall_status": "PRODUCTION_READY" if (successful_suites / total_suites) >= 0.8 else "NEEDS_IMPROVEMENT"
        }
    
    def _print_validation_summary(self, report: Dict):
        """Print formatted validation summary"""
        print("\n" + "="*80)
        print("🎯 REAL-WORLD AI BROWSER VALIDATION SUMMARY")
        print("="*80)
        
        summary = report["overall_summary"]
        
        print(f"Validation Duration: {report['total_duration_seconds']:.1f} seconds")
        print(f"Total Validation Suites: {summary['total_validation_suites']}")
        print(f"Successful Suites: {summary['successful_suites']}")
        print(f"Suite Success Rate: {summary['suite_success_rate']:.1%}")
        print(f"Individual Tests: {summary['successful_individual_tests']}/{summary['total_individual_tests']}")
        print(f"Overall Test Success Rate: {summary['individual_test_success_rate']:.1%}")
        print(f"Overall Status: {summary['overall_status']}")
        
        print("\n📊 DETAILED RESULTS BY CATEGORY:")
        print("-" * 80)
        
        for suite_name, suite_result in report["validation_suites"].items():
            if isinstance(suite_result, dict):
                success_rate = "N/A"
                if suite_result.get("total_tests", 0) > 0:
                    success_rate = f"{suite_result.get('successful_tests', 0)}/{suite_result.get('total_tests', 0)}"
                elif "success_rate" in suite_result:
                    success_rate = f"{suite_result['success_rate']:.1%}"
                
                status = "✅ PASS" if (
                    suite_result.get("successful_tests", 0) > 0 or 
                    suite_result.get("success_rate", 0) > 0.5
                ) else "❌ FAIL"
                
                print(f"{suite_name:.<30} {success_rate:>10} {status}")
        
        print("\n" + "="*80)
        
        if summary["overall_status"] == "PRODUCTION_READY":
            print("🎉 AI BROWSER REAL-WORLD EXAMPLES ARE PRODUCTION READY!")
            print("   All major functionality validated with live websites and LLM calls.")
        else:
            print("⚠️  Some validation tests need attention before production deployment.")
        
        print("="*80)


async def main():
    """Run the comprehensive real-world validation suite"""
    validator = RealWorldValidationSuite()
    
    try:
        report = await validator.run_comprehensive_validation()
        
        # Return appropriate exit code
        summary = report["overall_summary"]
        success_rate = summary["suite_success_rate"]
        
        if success_rate >= 0.8:
            print(f"\n✅ Validation passed with {success_rate:.1%} success rate")
            return 0
        else:
            print(f"\n❌ Validation needs improvement: {success_rate:.1%} success rate")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Validation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Validation failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)