#!/usr/bin/env python3
"""
Test Runner for Element Extraction V2 - Tests 20 websites
Comprehensive testing with metrics, reporting, and analysis
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src" / "ui_testing_v2" / "components" / "element_extraction"))

from optimized_extractor_v2 import (
    extract_elements_for_test_generation,
    ExtractionConfig
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TestResult:
    """Container for test results."""
    def __init__(self, url: str):
        self.url = url
        self.domain = urlparse(url).netloc
        self.success = False
        self.error = None
        self.element_count = 0
        self.elements_by_type = {}
        self.extraction_time = 0
        self.metadata_completeness = 0
        self.test_scenarios_count = 0
        self.semantic_purposes_found = []
        self.validation_rules_count = 0
        self.relationships_mapped = 0
        self.raw_elements = []
        self.timestamp = datetime.now().isoformat()


class ElementExtractionTester:
    """Test runner for element extraction across multiple websites."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.test_sites = self._load_test_sites()
        
    def _load_test_sites(self) -> List[Dict[str, str]]:
        """Load test sites from configuration."""
        return [
            {"url": "https://example.com", "category": "Simple Static", "name": "Example.com"},
            {"url": "https://httpbin.org", "category": "Simple Static", "name": "HTTPBin.org"},
            {"url": "https://www.bbc.com/news", "category": "News/Content", "name": "BBC News"},
            {"url": "https://en.wikipedia.org/wiki/Main_Page", "category": "News/Content", "name": "Wikipedia"},
            {"url": "https://www.amazon.com", "category": "E-commerce", "name": "Amazon"},
            {"url": "https://www.etsy.com", "category": "E-commerce", "name": "Etsy"},
            {"url": "https://www.reddit.com", "category": "Social Media", "name": "Reddit"},
            {"url": "https://stackoverflow.com", "category": "Social Media", "name": "Stack Overflow"},
            {"url": "https://github.com", "category": "Web Applications", "name": "GitHub"},
            {"url": "https://www.google.com", "category": "Web Applications", "name": "Google Search"},
            {"url": "https://twitter.com", "category": "SPA/PWA", "name": "Twitter/X"},
            {"url": "https://www.youtube.com", "category": "SPA/PWA", "name": "YouTube"},
            {"url": "https://docs.google.com/forms", "category": "Forms", "name": "Google Forms"},
            {"url": "https://www.typeform.com/templates/", "category": "Forms", "name": "Typeform"},
            {"url": "https://mui.com/material-ui/getting-started/", "category": "Component Libraries", "name": "Material UI"},
            {"url": "https://getbootstrap.com/docs/5.3/examples/", "category": "Component Libraries", "name": "Bootstrap"},
            {"url": "https://www.usa.gov", "category": "Government/Accessibility", "name": "USA.gov"},
            {"url": "https://www.w3.org", "category": "Government/Accessibility", "name": "W3C"},
            {"url": "https://developer.mozilla.org", "category": "Interactive", "name": "MDN Web Docs"},
            {"url": "https://codepen.io", "category": "Interactive", "name": "CodePen"}
        ]
    
    async def test_single_site(self, site_info: Dict[str, str]) -> TestResult:
        """Test a single website and collect metrics."""
        url = site_info["url"]
        logger.info(f"Testing {site_info['name']} ({site_info['category']}): {url}")
        
        result = TestResult(url)
        result.site_name = site_info["name"]
        result.category = site_info["category"]
        
        try:
            # Configure extraction for comprehensive testing
            config = ExtractionConfig(
                max_elements=100,
                enable_ai_analysis=False,  # Disable for speed  
                parallel_strategies=True,
                extract_validation_rules=True,
                extract_relationships=True,
                generate_test_hints=True,
                timeout=30,
                min_confidence=0.3,
                enable_accessibility_extraction=True,
                stealth_mode=True
            )
            
            # Measure extraction time
            start_time = time.time()
            elements = await extract_elements_for_test_generation(
                url=url,
                config=config
            )
            result.extraction_time = time.time() - start_time
            
            # Analyze results
            result.success = True
            result.element_count = len(elements)
            result.raw_elements = elements
            
            # Categorize elements by type
            for element in elements:
                elem_type = element.get('element_type', 'unknown')
                result.elements_by_type[elem_type] = result.elements_by_type.get(elem_type, 0) + 1
                
                # Count semantic purposes
                if element.get('semantic_purpose'):
                    result.semantic_purposes_found.append(element['semantic_purpose'])
                
                # Count test scenarios
                if element.get('suggested_test_scenarios'):
                    result.test_scenarios_count += len(element['suggested_test_scenarios'])
                
                # Count validation rules
                if element.get('validation_pattern'):
                    result.validation_rules_count += 1
                
                # Count relationships
                if element.get('relationships'):
                    result.relationships_mapped += len(element['relationships'])
            
            # Calculate metadata completeness
            if elements:
                total_fields = 0
                filled_fields = 0
                important_fields = [
                    'element_id', 'selectors', 'element_type', 'semantic_purpose',
                    'business_context', 'test_priority', 'suggested_test_scenarios',
                    'expected_behaviors', 'validation_pattern', 'is_required'
                ]
                
                for element in elements[:10]:  # Sample first 10 elements
                    for field in important_fields:
                        total_fields += 1
                        if element.get(field):
                            filled_fields += 1
                
                result.metadata_completeness = (filled_fields / total_fields * 100) if total_fields > 0 else 0
            
            logger.info(f"✓ Success: {result.element_count} elements extracted in {result.extraction_time:.2f}s")
            
        except Exception as e:
            result.success = False
            result.error = str(e)
            logger.error(f"✗ Failed: {e}")
        
        return result
    
    async def run_all_tests(self) -> None:
        """Run tests on all configured websites."""
        logger.info(f"Starting tests on {len(self.test_sites)} websites...")
        
        # Test sites one by one to avoid overwhelming resources
        for site_info in self.test_sites:
            result = await self.test_single_site(site_info)
            self.results.append(result)
            
            # Small delay between tests
            await asyncio.sleep(2)
        
        logger.info("All tests completed!")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        successful_tests = [r for r in self.results if r.success]
        failed_tests = [r for r in self.results if not r.success]
        
        # Calculate aggregate metrics
        total_elements = sum(r.element_count for r in successful_tests)
        avg_extraction_time = sum(r.extraction_time for r in successful_tests) / len(successful_tests) if successful_tests else 0
        avg_metadata_completeness = sum(r.metadata_completeness for r in successful_tests) / len(successful_tests) if successful_tests else 0
        
        # Element type distribution
        all_element_types = {}
        for result in successful_tests:
            for elem_type, count in result.elements_by_type.items():
                all_element_types[elem_type] = all_element_types.get(elem_type, 0) + count
        
        # Category performance
        category_metrics = {}
        for result in self.results:
            category = getattr(result, 'category', 'Unknown')
            if category not in category_metrics:
                category_metrics[category] = {
                    'total': 0,
                    'successful': 0,
                    'avg_elements': 0,
                    'avg_time': 0,
                    'sites': []
                }
            
            category_metrics[category]['total'] += 1
            category_metrics[category]['sites'].append(getattr(result, 'site_name', result.domain))
            
            if result.success:
                category_metrics[category]['successful'] += 1
                category_metrics[category]['avg_elements'] += result.element_count
                category_metrics[category]['avg_time'] += result.extraction_time
        
        # Calculate category averages
        for category, metrics in category_metrics.items():
            if metrics['successful'] > 0:
                metrics['avg_elements'] /= metrics['successful']
                metrics['avg_time'] /= metrics['successful']
                metrics['success_rate'] = (metrics['successful'] / metrics['total']) * 100
            else:
                metrics['success_rate'] = 0
        
        report = {
            "summary": {
                "total_sites_tested": len(self.results),
                "successful_tests": len(successful_tests),
                "failed_tests": len(failed_tests),
                "success_rate": (len(successful_tests) / len(self.results) * 100) if self.results else 0,
                "total_elements_extracted": total_elements,
                "avg_extraction_time": round(avg_extraction_time, 2),
                "avg_metadata_completeness": round(avg_metadata_completeness, 2)
            },
            "element_distribution": all_element_types,
            "category_performance": category_metrics,
            "llm_readiness_metrics": {
                "total_test_scenarios": sum(r.test_scenarios_count for r in successful_tests),
                "total_semantic_purposes": sum(len(r.semantic_purposes_found) for r in successful_tests),
                "total_validation_rules": sum(r.validation_rules_count for r in successful_tests),
                "total_relationships": sum(r.relationships_mapped for r in successful_tests),
                "avg_scenarios_per_site": sum(r.test_scenarios_count for r in successful_tests) / len(successful_tests) if successful_tests else 0
            },
            "site_details": [],
            "failures": []
        }
        
        # Add detailed site results
        for result in self.results:
            site_detail = {
                "url": result.url,
                "name": getattr(result, 'site_name', result.domain),
                "category": getattr(result, 'category', 'Unknown'),
                "success": result.success,
                "element_count": result.element_count,
                "extraction_time": round(result.extraction_time, 2),
                "metadata_completeness": round(result.metadata_completeness, 2),
                "elements_by_type": result.elements_by_type,
                "test_scenarios_count": result.test_scenarios_count,
                "validation_rules_count": result.validation_rules_count,
                "timestamp": result.timestamp
            }
            
            if result.success:
                report["site_details"].append(site_detail)
            else:
                site_detail["error"] = result.error
                report["failures"].append(site_detail)
        
        return report
    
    def save_results(self, report: Dict[str, Any]) -> None:
        """Save test results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON report
        report_file = f"test_report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Report saved to {report_file}")
        
        # Save detailed elements for analysis
        elements_file = f"extracted_elements_{timestamp}.json"
        all_elements = []
        for result in self.results:
            if result.success and result.raw_elements:
                all_elements.append({
                    "site": getattr(result, 'site_name', result.domain),
                    "url": result.url,
                    "elements": result.raw_elements[:10]  # Save first 10 elements per site
                })
        
        with open(elements_file, 'w') as f:
            json.dump(all_elements, f, indent=2)
        logger.info(f"Sample elements saved to {elements_file}")
        
        # Generate markdown report
        self._generate_markdown_report(report, f"test_report_{timestamp}.md")
    
    def _generate_markdown_report(self, report: Dict[str, Any], filename: str) -> None:
        """Generate a human-readable markdown report."""
        md_content = ["# Element Extraction V2 Test Report\n"]
        md_content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Summary
        md_content.append("## Executive Summary\n")
        summary = report["summary"]
        md_content.append(f"- **Sites Tested**: {summary['total_sites_tested']}\n")
        md_content.append(f"- **Success Rate**: {summary['success_rate']:.1f}%\n")
        md_content.append(f"- **Total Elements Extracted**: {summary['total_elements_extracted']:,}\n")
        md_content.append(f"- **Average Extraction Time**: {summary['avg_extraction_time']:.2f}s\n")
        md_content.append(f"- **Metadata Completeness**: {summary['avg_metadata_completeness']:.1f}%\n\n")
        
        # LLM Readiness
        md_content.append("## LLM Readiness Metrics\n")
        llm_metrics = report["llm_readiness_metrics"]
        md_content.append(f"- **Test Scenarios Generated**: {llm_metrics['total_test_scenarios']:,}\n")
        md_content.append(f"- **Semantic Purposes Identified**: {llm_metrics['total_semantic_purposes']:,}\n")
        md_content.append(f"- **Validation Rules Extracted**: {llm_metrics['total_validation_rules']:,}\n")
        md_content.append(f"- **Element Relationships Mapped**: {llm_metrics['total_relationships']:,}\n")
        md_content.append(f"- **Avg Scenarios per Site**: {llm_metrics['avg_scenarios_per_site']:.1f}\n\n")
        
        # Category Performance
        md_content.append("## Performance by Category\n")
        md_content.append("| Category | Success Rate | Avg Elements | Avg Time |\n")
        md_content.append("|----------|-------------|--------------|----------|\n")
        for category, metrics in report["category_performance"].items():
            md_content.append(f"| {category} | {metrics.get('success_rate', 0):.1f}% | "
                            f"{metrics['avg_elements']:.0f} | {metrics['avg_time']:.2f}s |\n")
        md_content.append("\n")
        
        # Element Distribution
        md_content.append("## Element Type Distribution\n")
        md_content.append("| Element Type | Count |\n")
        md_content.append("|-------------|-------|\n")
        for elem_type, count in sorted(report["element_distribution"].items(), key=lambda x: x[1], reverse=True):
            md_content.append(f"| {elem_type} | {count:,} |\n")
        md_content.append("\n")
        
        # Site Details
        md_content.append("## Site-by-Site Results\n")
        md_content.append("| Site | Category | Elements | Time | Completeness | Status |\n")
        md_content.append("|------|----------|----------|------|--------------|--------|\n")
        for site in report["site_details"]:
            status = "✅" if site["success"] else "❌"
            md_content.append(f"| {site['name']} | {site['category']} | {site['element_count']} | "
                            f"{site['extraction_time']:.2f}s | {site['metadata_completeness']:.1f}% | {status} |\n")
        md_content.append("\n")
        
        # Failures
        if report["failures"]:
            md_content.append("## Failed Tests\n")
            for failure in report["failures"]:
                md_content.append(f"### {failure['name']}\n")
                md_content.append(f"- **URL**: {failure['url']}\n")
                md_content.append(f"- **Error**: {failure['error']}\n\n")
        
        # Recommendations
        md_content.append("## Recommendations\n")
        if summary['success_rate'] < 80:
            md_content.append("- ⚠️ Success rate below 80% - investigate timeout and error handling\n")
        if summary['avg_metadata_completeness'] < 70:
            md_content.append("- ⚠️ Metadata completeness below 70% - enhance extraction strategies\n")
        if summary['avg_extraction_time'] > 10:
            md_content.append("- ⚠️ Average extraction time high - consider performance optimization\n")
        if llm_metrics['avg_scenarios_per_site'] < 5:
            md_content.append("- ⚠️ Low test scenario generation - improve semantic analysis\n")
        
        md_content.append("\n## Conclusion\n")
        md_content.append(f"The optimized element extraction system V2 successfully processed {summary['successful_tests']} "
                         f"out of {summary['total_sites_tested']} websites, extracting a total of "
                         f"{summary['total_elements_extracted']:,} elements with comprehensive metadata for LLM test generation.\n")
        
        with open(filename, 'w') as f:
            f.write(''.join(md_content))
        logger.info(f"Markdown report saved to {filename}")


async def main():
    """Main test execution function."""
    print("=" * 80)
    print("ELEMENT EXTRACTION V2 - COMPREHENSIVE TESTING")
    print("=" * 80)
    
    tester = ElementExtractionTester()
    
    try:
        # Run all tests
        await tester.run_all_tests()
        
        # Generate report
        report = tester.generate_report()
        
        # Save results
        tester.save_results(report)
        
        # Print summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        summary = report["summary"]
        print(f"✓ Sites Tested: {summary['total_sites_tested']}")
        print(f"✓ Success Rate: {summary['success_rate']:.1f}%")
        print(f"✓ Total Elements: {summary['total_elements_extracted']:,}")
        print(f"✓ Avg Time: {summary['avg_extraction_time']:.2f}s")
        print(f"✓ Metadata Completeness: {summary['avg_metadata_completeness']:.1f}%")
        
        llm_metrics = report["llm_readiness_metrics"]
        print("\nLLM READINESS:")
        print(f"✓ Test Scenarios: {llm_metrics['total_test_scenarios']:,}")
        print(f"✓ Semantic Purposes: {llm_metrics['total_semantic_purposes']:,}")
        print(f"✓ Validation Rules: {llm_metrics['total_validation_rules']:,}")
        
        if report["failures"]:
            print(f"\n⚠️ Failed Tests: {len(report['failures'])}")
            for failure in report["failures"]:
                print(f"  - {failure['name']}: {failure['error'][:50]}...")
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())