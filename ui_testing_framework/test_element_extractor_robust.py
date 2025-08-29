#!/usr/bin/env python3
"""
Comprehensive Test Suite for Ultimate Element Extractor
Tests extraction capabilities across diverse website types
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from element_extractor_no_llm_robust import (
    UltimateElementExtractor,
    ExtractionStrategy,
    ExtractionConfig,
    ElementData,
    ExtractionResult
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExtractorTestSuite:
    """Comprehensive test suite for element extractor"""
    
    def __init__(self):
        self.extractor = UltimateElementExtractor()
        self.test_results = []
        
    async def test_static_site(self) -> Dict[str, Any]:
        """Test extraction from a static HTML site"""
        logger.info("Testing static site extraction...")
        
        url = "https://example.com"
        try:
            result = await self.extractor.extract(
                url=url,
                strategies=[ExtractionStrategy.DOM_REGULAR]
            )
            
            return {
                "test": "static_site",
                "url": url,
                "success": result.success,
                "elements_found": len(result.elements),
                "extraction_time": result.extraction_time,
                "errors": result.errors
            }
        except Exception as e:
            return {
                "test": "static_site",
                "url": url,
                "success": False,
                "error": str(e)
            }
    
    async def test_react_spa(self) -> Dict[str, Any]:
        """Test extraction from React SPA"""
        logger.info("Testing React SPA extraction...")
        
        url = "https://react.dev"
        try:
            result = await self.extractor.extract(
                url=url,
                strategies=[
                    ExtractionStrategy.DOM_REGULAR,
                    ExtractionStrategy.DYNAMIC_CONTENT,
                    ExtractionStrategy.MUTATION_OBSERVER
                ]
            )
            
            return {
                "test": "react_spa",
                "url": url,
                "success": result.success,
                "elements_found": len(result.elements),
                "framework_detected": result.framework_detected,
                "extraction_time": result.extraction_time
            }
        except Exception as e:
            return {
                "test": "react_spa",
                "url": url,
                "success": False,
                "error": str(e)
            }
    
    async def test_shadow_dom_site(self) -> Dict[str, Any]:
        """Test extraction from site with shadow DOM"""
        logger.info("Testing shadow DOM extraction...")
        
        url = "https://www.youtube.com"
        try:
            result = await self.extractor.extract(
                url=url,
                strategies=[
                    ExtractionStrategy.DOM_REGULAR,
                    ExtractionStrategy.SHADOW_DOM,
                    ExtractionStrategy.WEB_COMPONENTS
                ]
            )
            
            shadow_elements = [e for e in result.elements if e.is_shadow_element]
            
            return {
                "test": "shadow_dom",
                "url": url,
                "success": result.success,
                "total_elements": len(result.elements),
                "shadow_elements": len(shadow_elements),
                "extraction_time": result.extraction_time
            }
        except Exception as e:
            return {
                "test": "shadow_dom",
                "url": url,
                "success": False,
                "error": str(e)
            }
    
    async def test_infinite_scroll(self) -> Dict[str, Any]:
        """Test extraction from infinite scroll site"""
        logger.info("Testing infinite scroll extraction...")
        
        url = "https://www.reddit.com"
        try:
            config = ExtractionConfig(
                scroll_count=3,
                scroll_pause=2.0,
                wait_for_network_idle=True
            )
            
            result = await self.extractor.extract(
                url=url,
                strategies=[
                    ExtractionStrategy.INFINITE_SCROLL,
                    ExtractionStrategy.INTERSECTION_OBSERVER
                ],
                config=config
            )
            
            return {
                "test": "infinite_scroll",
                "url": url,
                "success": result.success,
                "elements_found": len(result.elements),
                "extraction_time": result.extraction_time
            }
        except Exception as e:
            return {
                "test": "infinite_scroll",
                "url": url,
                "success": False,
                "error": str(e)
            }
    
    async def test_form_heavy_site(self) -> Dict[str, Any]:
        """Test extraction from form-heavy site"""
        logger.info("Testing form extraction...")
        
        url = "https://www.google.com/forms/about/"
        try:
            result = await self.extractor.extract(
                url=url,
                strategies=[
                    ExtractionStrategy.DOM_REGULAR,
                    ExtractionStrategy.FORM_ELEMENTS
                ]
            )
            
            form_elements = [e for e in result.elements if e.element_type in ["form", "input", "select", "textarea"]]
            
            return {
                "test": "forms",
                "url": url,
                "success": result.success,
                "total_elements": len(result.elements),
                "form_elements": len(form_elements),
                "extraction_time": result.extraction_time
            }
        except Exception as e:
            return {
                "test": "forms",
                "url": url,
                "success": False,
                "error": str(e)
            }
    
    async def test_iframe_site(self) -> Dict[str, Any]:
        """Test extraction from site with iframes"""
        logger.info("Testing iframe extraction...")
        
        url = "https://www.w3schools.com/html/html_iframe.asp"
        try:
            result = await self.extractor.extract(
                url=url,
                strategies=[
                    ExtractionStrategy.DOM_REGULAR,
                    ExtractionStrategy.IFRAME
                ]
            )
            
            iframe_elements = [e for e in result.elements if e.is_iframe_element]
            
            return {
                "test": "iframes",
                "url": url,
                "success": result.success,
                "total_elements": len(result.elements),
                "iframe_elements": len(iframe_elements),
                "extraction_time": result.extraction_time
            }
        except Exception as e:
            return {
                "test": "iframes",
                "url": url,
                "success": False,
                "error": str(e)
            }
    
    async def test_accessibility(self) -> Dict[str, Any]:
        """Test accessibility tree extraction"""
        logger.info("Testing accessibility extraction...")
        
        url = "https://www.w3.org/WAI/"
        try:
            result = await self.extractor.extract(
                url=url,
                strategies=[
                    ExtractionStrategy.ACCESSIBILITY_TREE
                ]
            )
            
            accessible_elements = [e for e in result.elements if e.aria_label or e.aria_role]
            
            return {
                "test": "accessibility",
                "url": url,
                "success": result.success,
                "total_elements": len(result.elements),
                "accessible_elements": len(accessible_elements),
                "extraction_time": result.extraction_time
            }
        except Exception as e:
            return {
                "test": "accessibility",
                "url": url,
                "success": False,
                "error": str(e)
            }
    
    async def test_enrichment_validation(self) -> Dict[str, Any]:
        """Test element enrichment and validation"""
        logger.info("Testing enrichment and validation...")
        
        url = "https://github.com"
        try:
            result = await self.extractor.extract_with_enrichment(
                url=url,
                enrich=True,
                validate=True
            )
            
            enriched_elements = [e for e in result.elements if e.semantic_type]
            valid_elements = [e for e in result.elements if e.validation_score and e.validation_score > 0.7]
            
            return {
                "test": "enrichment_validation",
                "url": url,
                "success": result.success,
                "total_elements": len(result.elements),
                "enriched_elements": len(enriched_elements),
                "valid_elements": len(valid_elements),
                "extraction_time": result.extraction_time
            }
        except Exception as e:
            return {
                "test": "enrichment_validation",
                "url": url,
                "success": False,
                "error": str(e)
            }
    
    async def test_batch_extraction(self) -> Dict[str, Any]:
        """Test batch URL extraction"""
        logger.info("Testing batch extraction...")
        
        urls = [
            "https://example.com",
            "https://www.wikipedia.org",
            "https://www.github.com"
        ]
        
        try:
            results = await self.extractor.extract_batch(
                urls=urls,
                max_concurrent=2
            )
            
            successful = sum(1 for r in results if r.success)
            total_elements = sum(len(r.elements) for r in results)
            
            return {
                "test": "batch_extraction",
                "urls": urls,
                "success": True,
                "successful_extractions": successful,
                "total_urls": len(urls),
                "total_elements": total_elements
            }
        except Exception as e:
            return {
                "test": "batch_extraction",
                "urls": urls,
                "success": False,
                "error": str(e)
            }
    
    async def test_mobile_responsive(self) -> Dict[str, Any]:
        """Test mobile viewport extraction"""
        logger.info("Testing mobile responsive extraction...")
        
        url = "https://www.amazon.com"
        try:
            config = ExtractionConfig(
                viewport_width=375,
                viewport_height=812,
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
            )
            
            result = await self.extractor.extract(
                url=url,
                config=config
            )
            
            return {
                "test": "mobile_responsive",
                "url": url,
                "success": result.success,
                "elements_found": len(result.elements),
                "viewport": f"{config.viewport_width}x{config.viewport_height}",
                "extraction_time": result.extraction_time
            }
        except Exception as e:
            return {
                "test": "mobile_responsive",
                "url": url,
                "success": False,
                "error": str(e)
            }
    
    async def run_all_tests(self) -> List[Dict[str, Any]]:
        """Run all test cases"""
        logger.info("Starting comprehensive test suite...")
        
        test_methods = [
            self.test_static_site,
            self.test_react_spa,
            self.test_shadow_dom_site,
            self.test_infinite_scroll,
            self.test_form_heavy_site,
            self.test_iframe_site,
            self.test_accessibility,
            self.test_enrichment_validation,
            self.test_batch_extraction,
            self.test_mobile_responsive
        ]
        
        results = []
        for test_method in test_methods:
            try:
                result = await test_method()
                results.append(result)
                
                # Log result
                if result.get("success"):
                    logger.info(f"✓ {result['test']} test passed")
                else:
                    logger.error(f"✗ {result['test']} test failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"Test {test_method.__name__} failed with exception: {e}")
                results.append({
                    "test": test_method.__name__,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate test report"""
        successful = sum(1 for r in results if r.get("success"))
        total = len(results)
        
        report = f"""
═══════════════════════════════════════════════════════════════════
                    ELEMENT EXTRACTOR TEST REPORT
═══════════════════════════════════════════════════════════════════

Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Tests: {total}
Successful: {successful}
Failed: {total - successful}
Success Rate: {(successful/total)*100:.1f}%

═══════════════════════════════════════════════════════════════════
                         TEST RESULTS
═══════════════════════════════════════════════════════════════════

"""
        
        for result in results:
            status = "✓ PASS" if result.get("success") else "✗ FAIL"
            report += f"\n{status} - {result['test'].upper()}\n"
            report += "-" * 50 + "\n"
            
            for key, value in result.items():
                if key not in ["test", "success"]:
                    report += f"  {key}: {value}\n"
            
            report += "\n"
        
        report += """
═══════════════════════════════════════════════════════════════════
                         SUMMARY
═══════════════════════════════════════════════════════════════════

"""
        
        if successful == total:
            report += "🎉 ALL TESTS PASSED! The extractor is working perfectly.\n"
        elif successful >= total * 0.8:
            report += "✓ Most tests passed. The extractor is working well.\n"
        elif successful >= total * 0.5:
            report += "⚠ Some tests failed. The extractor needs improvement.\n"
        else:
            report += "✗ Many tests failed. The extractor needs significant work.\n"
        
        report += "\n═══════════════════════════════════════════════════════════════════\n"
        
        return report


async def main():
    """Run test suite"""
    suite = ExtractorTestSuite()
    
    # Run all tests
    results = await suite.run_all_tests()
    
    # Generate report
    report = suite.generate_report(results)
    print(report)
    
    # Save results to file
    output_dir = Path("test_results")
    output_dir.mkdir(exist_ok=True)
    
    # Save JSON results
    json_file = output_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Save text report
    report_file = output_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    logger.info(f"Test results saved to {json_file}")
    logger.info(f"Test report saved to {report_file}")
    
    # Return success code
    successful = sum(1 for r in results if r.get("success"))
    return 0 if successful == len(results) else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)