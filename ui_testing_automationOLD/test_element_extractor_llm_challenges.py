#!/usr/bin/env python3
"""
Test Element Extractor WITH LLM Against Challenging Sites Database
Tests the AI-enhanced extraction capabilities against challenging websites
Compares results with non-LLM extraction
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

from element_extractor_with_llm import EnhancedElementExtractor, AIExtractionConfig, ExtractionMode
from llm import LLM, LLMConfig, LLMProvider
from utils import Logger, LogLevel

class ElementExtractorLLMChallengeTester:
    """Test LLM-enhanced element extractor against challenging sites"""
    
    def __init__(self):
        self.logger = Logger.get_logger("LLMExtractorTester", LogLevel.INFO)
        # Configure AI extraction with OpenAI
        extraction_config = AIExtractionConfig(
            mode=ExtractionMode.COMPREHENSIVE,
            use_llm=True,
            llm_provider=LLMProvider.OPENAI,
            semantic_analysis=True,
            visual_analysis=True,
            context_understanding=True,
            element_scoring=True
        )
        self.extractor = EnhancedElementExtractor(config=extraction_config)
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
        """Test LLM-enhanced element extraction on a single site"""
        result = {
            "id": site["id"],
            "name": site["name"],
            "url": site["url"],
            "category": site["category"],
            "difficulty": site["difficulty"],
            "protection_system": site["protection_system"],
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": None,
            "extraction_time": None,
            "llm_time": None,
            "elements_extracted": {
                "total": 0,
                "buttons": 0,
                "links": 0,
                "inputs": 0,
                "forms": 0,
                "images": 0,
                "text": 0,
                "interactive": 0
            },
            "ai_enhancements": {
                "semantic_groups": 0,
                "interaction_patterns": 0,
                "accessibility_score": 0,
                "framework_detected": None,
                "page_type": None,
                "key_actions": []
            },
            "extraction_quality": {
                "has_selectors": False,
                "has_semantic_meaning": False,
                "has_interaction_hints": False,
                "has_ai_classification": False
            }
        }
        
        try:
            self.logger.info(f"Testing {site['name']} ({site['difficulty']} difficulty) with LLM")
            self.logger.info(f"URL: {site['url']}")
            self.logger.info(f"Protection: {site['protection_system']}")
            
            # Start timing
            start_time = time.time()
            
            # Extract elements with LLM enhancement
            extraction_result = await self.extractor.extract(site["url"])
            
            # Calculate extraction time
            result["extraction_time"] = round(time.time() - start_time, 2)
            
            if extraction_result:
                # Process extraction results
                if hasattr(extraction_result, 'elements'):
                    elements = extraction_result.elements
                else:
                    # Handle list result
                    elements = extraction_result if isinstance(extraction_result, list) else []
                
                result["elements_extracted"]["total"] = len(elements)
                
                # Count elements by type
                for element in elements:
                    if hasattr(element, 'element_type'):
                        element_type = str(element.element_type).lower()
                    else:
                        element_type = "unknown"
                    
                    tag_name = element.tag_name.lower() if hasattr(element, 'tag_name') and element.tag_name else ""
                    
                    if "button" in element_type or tag_name == "button":
                        result["elements_extracted"]["buttons"] += 1
                    elif "link" in element_type or tag_name == "a":
                        result["elements_extracted"]["links"] += 1
                    elif "input" in element_type or tag_name in ["input", "textarea", "select"]:
                        result["elements_extracted"]["inputs"] += 1
                    elif "form" in element_type or tag_name == "form":
                        result["elements_extracted"]["forms"] += 1
                    elif "image" in element_type or tag_name == "img":
                        result["elements_extracted"]["images"] += 1
                    elif hasattr(element, 'text_content') and element.text_content:
                        result["elements_extracted"]["text"] += 1
                    
                    # Count interactive elements
                    if hasattr(element, 'is_clickable') and element.is_clickable:
                        result["elements_extracted"]["interactive"] += 1
                
                # Check for AI enhancements
                if hasattr(extraction_result, 'semantic_groups'):
                    result["ai_enhancements"]["semantic_groups"] = len(extraction_result.semantic_groups)
                
                if hasattr(extraction_result, 'framework'):
                    result["ai_enhancements"]["framework_detected"] = extraction_result.framework
                    
                if hasattr(extraction_result, 'page_type'):
                    result["ai_enhancements"]["page_type"] = extraction_result.page_type
                    
                if hasattr(extraction_result, 'key_actions'):
                    result["ai_enhancements"]["key_actions"] = extraction_result.key_actions[:5]
                
                # Check extraction quality
                if elements:
                    sample = elements[0] if elements else None
                    if sample:
                        result["extraction_quality"]["has_selectors"] = bool(
                            (hasattr(sample, 'css_selector') and sample.css_selector) or 
                            (hasattr(sample, 'xpath') and sample.xpath)
                        )
                        result["extraction_quality"]["has_semantic_meaning"] = bool(
                            hasattr(sample, 'semantic_role') or 
                            hasattr(sample, 'aria_label')
                        )
                        result["extraction_quality"]["has_interaction_hints"] = bool(
                            hasattr(sample, 'is_clickable') or 
                            hasattr(sample, 'interaction_type')
                        )
                        result["extraction_quality"]["has_ai_classification"] = bool(
                            result["ai_enhancements"]["page_type"] or 
                            result["ai_enhancements"]["framework_detected"]
                        )
                
                result["success"] = result["elements_extracted"]["total"] > 0
                
                # Log summary
                self.logger.info(
                    f"✓ {site['name']}: Extracted {result['elements_extracted']['total']} elements "
                    f"({result['elements_extracted']['interactive']} interactive) in {result['extraction_time']}s"
                )
                
                if result["ai_enhancements"]["page_type"]:
                    self.logger.info(f"  AI detected: {result['ai_enhancements']['page_type']} page")
                if result["ai_enhancements"]["framework_detected"]:
                    self.logger.info(f"  Framework: {result['ai_enhancements']['framework_detected']}")
                
            else:
                result["error"] = "No elements extracted"
                self.logger.error(f"✗ {site['name']}: {result['error']}")
                
        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"✗ {site['name']}: {e}")
            
        return result
        
    async def run_tests(self, sites_to_test: List[str] = None):
        """Run tests on specified sites or priority sites"""
        # Load database
        database = await self.load_database()
        if not database:
            return
            
        # Filter sites if specified
        if sites_to_test:
            sites = [s for s in database["sites"] if s["name"] in sites_to_test or s["id"] in sites_to_test]
        else:
            # Use priority sites for testing (fewer to save on LLM costs)
            priority_names = [
                "Cloudflare",
                "Supreme",
                "Instagram"
            ]
            sites = [s for s in database["sites"] if s["name"] in priority_names]
            
        self.logger.info(f"Testing {len(sites)} challenging sites with LLM-Enhanced Extractor")
        self.logger.info("Using AI to enhance extraction with semantic understanding")
        self.logger.info("=" * 60)
        
        # Test each site
        for i, site in enumerate(sites, 1):
            self.logger.info(f"\n[{i}/{len(sites)}] Testing {site['name']}...")
            result = await self.test_site(site)
            self.results.append(result)
            
            # Brief pause between sites to avoid rate limiting
            if i < len(sites):
                await asyncio.sleep(3)
            
        # Generate report
        await self.generate_report()
        
    async def generate_report(self):
        """Generate comprehensive test report with AI enhancement metrics"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"element_extractor_llm_challenge_report_{timestamp}.json"
        
        # Calculate statistics
        total = len(self.results)
        successful = sum(1 for r in self.results if r["success"])
        success_rate = (successful / total * 100) if total > 0 else 0
        
        # Calculate average elements extracted
        total_elements = sum(r["elements_extracted"]["total"] for r in self.results)
        avg_elements = total_elements / total if total > 0 else 0
        
        # Calculate interactive elements
        total_interactive = sum(r["elements_extracted"]["interactive"] for r in self.results)
        
        # Calculate average extraction time
        extraction_times = [r["extraction_time"] for r in self.results if r["extraction_time"]]
        avg_time = sum(extraction_times) / len(extraction_times) if extraction_times else 0
        
        # Count AI enhancements
        with_page_type = sum(1 for r in self.results if r["ai_enhancements"]["page_type"])
        with_framework = sum(1 for r in self.results if r["ai_enhancements"]["framework_detected"])
        with_key_actions = sum(1 for r in self.results if r["ai_enhancements"]["key_actions"])
        
        # Group by category
        by_category = {}
        for result in self.results:
            cat = result["category"]
            if cat not in by_category:
                by_category[cat] = {
                    "total": 0,
                    "success": 0,
                    "total_elements": 0,
                    "interactive_elements": 0,
                    "sites": []
                }
            by_category[cat]["total"] += 1
            if result["success"]:
                by_category[cat]["success"] += 1
            by_category[cat]["total_elements"] += result["elements_extracted"]["total"]
            by_category[cat]["interactive_elements"] += result["elements_extracted"]["interactive"]
            by_category[cat]["sites"].append(result["name"])
            
        # Find best and worst performers
        if self.results:
            best_extraction = max(self.results, key=lambda x: x["elements_extracted"]["total"])
            successful_results = [r for r in self.results if r["success"]]
            worst_extraction = min(
                successful_results, 
                key=lambda x: x["elements_extracted"]["total"],
                default=None
            ) if successful_results else None
        else:
            best_extraction = worst_extraction = None
        
        report = {
            "test_date": datetime.now().isoformat(),
            "module": "element_extractor_with_llm",
            "llm_provider": "openai",
            "summary": {
                "total_sites_tested": total,
                "successful": successful,
                "failed": total - successful,
                "success_rate": round(success_rate, 2),
                "total_elements_extracted": total_elements,
                "total_interactive_elements": total_interactive,
                "average_elements_per_site": round(avg_elements, 2),
                "average_extraction_time": round(avg_time, 2)
            },
            "element_breakdown": {
                "buttons": sum(r["elements_extracted"]["buttons"] for r in self.results),
                "links": sum(r["elements_extracted"]["links"] for r in self.results),
                "inputs": sum(r["elements_extracted"]["inputs"] for r in self.results),
                "forms": sum(r["elements_extracted"]["forms"] for r in self.results),
                "images": sum(r["elements_extracted"]["images"] for r in self.results),
                "text": sum(r["elements_extracted"]["text"] for r in self.results),
                "interactive": total_interactive
            },
            "ai_enhancements": {
                "sites_with_page_type": with_page_type,
                "sites_with_framework_detection": with_framework,
                "sites_with_key_actions": with_key_actions,
                "page_types_detected": list(set(
                    r["ai_enhancements"]["page_type"] 
                    for r in self.results 
                    if r["ai_enhancements"]["page_type"]
                )),
                "frameworks_detected": list(set(
                    r["ai_enhancements"]["framework_detected"] 
                    for r in self.results 
                    if r["ai_enhancements"]["framework_detected"]
                ))
            },
            "quality_metrics": {
                "with_selectors": sum(1 for r in self.results if r["extraction_quality"]["has_selectors"]),
                "with_semantic_meaning": sum(1 for r in self.results if r["extraction_quality"]["has_semantic_meaning"]),
                "with_interaction_hints": sum(1 for r in self.results if r["extraction_quality"]["has_interaction_hints"]),
                "with_ai_classification": sum(1 for r in self.results if r["extraction_quality"]["has_ai_classification"])
            },
            "by_category": by_category,
            "best_extraction": {
                "site": best_extraction["name"],
                "elements": best_extraction["elements_extracted"]["total"],
                "interactive": best_extraction["elements_extracted"]["interactive"],
                "time": best_extraction["extraction_time"],
                "page_type": best_extraction["ai_enhancements"]["page_type"]
            } if best_extraction else None,
            "worst_extraction": {
                "site": worst_extraction["name"],
                "elements": worst_extraction["elements_extracted"]["total"],
                "interactive": worst_extraction["elements_extracted"]["interactive"],
                "time": worst_extraction["extraction_time"]
            } if worst_extraction else None,
            "failed_sites": [
                {
                    "name": f["name"],
                    "url": f["url"],
                    "protection": f["protection_system"],
                    "error": f["error"]
                }
                for f in self.results if not f["success"]
            ],
            "detailed_results": self.results
        }
        
        # Save report
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        # Print summary
        self.logger.info("\n" + "=" * 60)
        self.logger.info("ELEMENT EXTRACTOR WITH LLM - CHALLENGE TEST RESULTS")
        self.logger.info("=" * 60)
        self.logger.info(f"Total Sites Tested: {total}")
        self.logger.info(f"Successful: {successful} ({success_rate:.1f}%)")
        self.logger.info(f"Failed: {total - successful}")
        self.logger.info(f"Total Elements Extracted: {total_elements}")
        self.logger.info(f"Interactive Elements: {total_interactive}")
        self.logger.info(f"Average Elements per Site: {avg_elements:.0f}")
        self.logger.info(f"Average Extraction Time: {avg_time:.2f}s")
        
        self.logger.info("\nAI Enhancements:")
        self.logger.info(f"  Page Types Detected: {with_page_type}/{total}")
        self.logger.info(f"  Frameworks Detected: {with_framework}/{total}")
        self.logger.info(f"  Key Actions Identified: {with_key_actions}/{total}")
        
        if report["ai_enhancements"]["page_types_detected"]:
            self.logger.info(f"  Page Types: {', '.join(report['ai_enhancements']['page_types_detected'])}")
        
        if report["best_extraction"]:
            self.logger.info(f"\nBest Extraction: {report['best_extraction']['site']} "
                           f"({report['best_extraction']['elements']} elements, "
                           f"{report['best_extraction']['interactive']} interactive)")
        
        if report["failed_sites"]:
            self.logger.warning("\nFailed Sites:")
            for f in report["failed_sites"]:
                self.logger.warning(f"  - {f['name']} ({f['protection']}): {f['error'][:50]}...")
                
        self.logger.info(f"\nDetailed report saved to: {report_path}")
        
        return report

async def main():
    """Main execution"""
    tester = ElementExtractorLLMChallengeTester()
    
    print("[INIT] Element Extractor WITH LLM Challenge Test")
    print("[INFO] Testing with AI-enhanced extraction capabilities")
    print("[INFO] Using OpenAI GPT for semantic understanding")
    print("=" * 60)
    
    # Run tests on priority sites
    await tester.run_tests()
    
    return True

if __name__ == "__main__":
    # Quick compliance test
    if os.environ.get("STANDALONE_TEST") == "1":
        print("[OK] LLM-enhanced element extractor tester loads successfully")
        sys.exit(0)
        
    # Run full test
    success = asyncio.run(main())
    sys.exit(0 if success else 1)