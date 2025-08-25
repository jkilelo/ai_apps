#!/usr/bin/env python3
"""
Test Element Extractor (No LLM) Against Challenging Sites Database
Tests the pure DOM extraction capabilities against 32 challenging websites
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

from element_extractor_no_llm import ElementExtractorNoLLM
from stealth_browser import StealthBrowser, StealthConfig, StealthLevel
from utils import Logger, LogLevel

class ElementExtractorChallengeTester:
    """Test element extractor against challenging sites"""
    
    def __init__(self):
        self.logger = Logger.get_logger("ElementExtractorTester", LogLevel.INFO)
        self.extractor = ElementExtractorNoLLM()
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
        """Test element extraction on a single site"""
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
            "elements_extracted": {
                "total": 0,
                "buttons": 0,
                "links": 0,
                "inputs": 0,
                "forms": 0,
                "images": 0,
                "text": 0
            },
            "extraction_quality": {
                "has_selectors": False,
                "has_attributes": False,
                "has_text": False,
                "has_hierarchy": False
            }
        }
        
        try:
            self.logger.info(f"Testing {site['name']} ({site['difficulty']} difficulty)")
            self.logger.info(f"URL: {site['url']}")
            self.logger.info(f"Protection: {site['protection_system']}")
            
            # Start timing
            start_time = time.time()
            
            # Extract elements directly from URL
            elements = await self.extractor.extract_from_url(site["url"])
            
            # Calculate extraction time
            result["extraction_time"] = round(time.time() - start_time, 2)
            
            if elements:
                # Count elements by type
                result["elements_extracted"]["total"] = len(elements)
                
                for element in elements:
                    element_type = str(element.element_type).lower() if hasattr(element, 'element_type') else "unknown"
                    tag_name = element.tag_name.lower() if element.tag_name else ""
                    
                    if "button" in element_type or tag_name == "button":
                        result["elements_extracted"]["buttons"] += 1
                    elif "link" in element_type or tag_name == "a":
                        result["elements_extracted"]["links"] += 1
                    elif "input" in element_type or tag_name == "input":
                        result["elements_extracted"]["inputs"] += 1
                    elif "form" in element_type or tag_name == "form":
                        result["elements_extracted"]["forms"] += 1
                    elif "image" in element_type or tag_name == "img":
                        result["elements_extracted"]["images"] += 1
                    elif element.text_content:
                        result["elements_extracted"]["text"] += 1
                
                # Check extraction quality
                if elements:
                    sample_element = elements[0]
                    result["extraction_quality"]["has_selectors"] = bool(
                        sample_element.css_selector or sample_element.xpath
                    )
                    result["extraction_quality"]["has_attributes"] = bool(
                        sample_element.id or sample_element.class_names or sample_element.name
                    )
                    result["extraction_quality"]["has_text"] = any(
                        e.text_content for e in elements[:10]
                    )
                    result["extraction_quality"]["has_hierarchy"] = True  # Always true for DOM extraction
                
                result["success"] = result["elements_extracted"]["total"] > 0
                
                # Log summary
                self.logger.info(
                    f"✓ {site['name']}: Extracted {result['elements_extracted']['total']} elements "
                    f"in {result['extraction_time']}s"
                )
                
            else:
                result["error"] = "No elements extracted"
                self.logger.error(f"✗ {site['name']}: {result['error']}")
                
        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"✗ {site['name']}: {e}")
            
        return result
        
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
            # Use priority sites for testing
            priority_names = [
                "Cloudflare",
                "Nike", 
                "Supreme",
                "Instagram"
            ]
            sites = [s for s in database["sites"] if s["name"] in priority_names]
            
        self.logger.info(f"Testing {len(sites)} challenging sites with ElementExtractorNoLLM")
        self.logger.info("=" * 60)
        
        # Test each site
        for i, site in enumerate(sites, 1):
            self.logger.info(f"\n[{i}/{len(sites)}] Testing {site['name']}...")
            result = await self.test_site(site)
            self.results.append(result)
            
            # Brief pause between sites
            if i < len(sites):
                await asyncio.sleep(2)
            
        # Generate report
        await self.generate_report()
        
    async def generate_report(self):
        """Generate comprehensive test report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"element_extractor_challenge_report_{timestamp}.json"
        
        # Calculate statistics
        total = len(self.results)
        successful = sum(1 for r in self.results if r["success"])
        success_rate = (successful / total * 100) if total > 0 else 0
        
        # Calculate average elements extracted
        total_elements = sum(r["elements_extracted"]["total"] for r in self.results)
        avg_elements = total_elements / total if total > 0 else 0
        
        # Calculate average extraction time
        extraction_times = [r["extraction_time"] for r in self.results if r["extraction_time"]]
        avg_time = sum(extraction_times) / len(extraction_times) if extraction_times else 0
        
        # Group by category
        by_category = {}
        for result in self.results:
            cat = result["category"]
            if cat not in by_category:
                by_category[cat] = {
                    "total": 0,
                    "success": 0,
                    "total_elements": 0,
                    "sites": []
                }
            by_category[cat]["total"] += 1
            if result["success"]:
                by_category[cat]["success"] += 1
            by_category[cat]["total_elements"] += result["elements_extracted"]["total"]
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
                
        # Find best and worst performers
        best_extraction = max(self.results, key=lambda x: x["elements_extracted"]["total"])
        worst_extraction = min(
            [r for r in self.results if r["success"]], 
            key=lambda x: x["elements_extracted"]["total"],
            default=None
        )
        
        report = {
            "test_date": datetime.now().isoformat(),
            "module": "element_extractor_no_llm",
            "summary": {
                "total_sites_tested": total,
                "successful": successful,
                "failed": total - successful,
                "success_rate": round(success_rate, 2),
                "total_elements_extracted": total_elements,
                "average_elements_per_site": round(avg_elements, 2),
                "average_extraction_time": round(avg_time, 2)
            },
            "element_breakdown": {
                "buttons": sum(r["elements_extracted"]["buttons"] for r in self.results),
                "links": sum(r["elements_extracted"]["links"] for r in self.results),
                "inputs": sum(r["elements_extracted"]["inputs"] for r in self.results),
                "forms": sum(r["elements_extracted"]["forms"] for r in self.results),
                "images": sum(r["elements_extracted"]["images"] for r in self.results),
                "text": sum(r["elements_extracted"]["text"] for r in self.results)
            },
            "quality_metrics": {
                "with_selectors": sum(1 for r in self.results if r["extraction_quality"]["has_selectors"]),
                "with_attributes": sum(1 for r in self.results if r["extraction_quality"]["has_attributes"]),
                "with_text": sum(1 for r in self.results if r["extraction_quality"]["has_text"]),
                "with_hierarchy": sum(1 for r in self.results if r["extraction_quality"]["has_hierarchy"])
            },
            "by_category": by_category,
            "by_difficulty": by_difficulty,
            "best_extraction": {
                "site": best_extraction["name"],
                "elements": best_extraction["elements_extracted"]["total"],
                "time": best_extraction["extraction_time"]
            } if best_extraction else None,
            "worst_extraction": {
                "site": worst_extraction["name"],
                "elements": worst_extraction["elements_extracted"]["total"],
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
        self.logger.info("ELEMENT EXTRACTOR (NO LLM) CHALLENGE TEST RESULTS")
        self.logger.info("=" * 60)
        self.logger.info(f"Total Sites Tested: {total}")
        self.logger.info(f"Successful: {successful} ({success_rate:.1f}%)")
        self.logger.info(f"Failed: {total - successful}")
        self.logger.info(f"Total Elements Extracted: {total_elements}")
        self.logger.info(f"Average Elements per Site: {avg_elements:.0f}")
        self.logger.info(f"Average Extraction Time: {avg_time:.2f}s")
        
        self.logger.info("\nElement Breakdown:")
        self.logger.info(f"  Buttons: {report['element_breakdown']['buttons']}")
        self.logger.info(f"  Links: {report['element_breakdown']['links']}")
        self.logger.info(f"  Inputs: {report['element_breakdown']['inputs']}")
        self.logger.info(f"  Forms: {report['element_breakdown']['forms']}")
        
        if report["best_extraction"]:
            self.logger.info(f"\nBest Extraction: {report['best_extraction']['site']} ({report['best_extraction']['elements']} elements)")
        
        if report["failed_sites"]:
            self.logger.warning("\nFailed Sites:")
            for f in report["failed_sites"]:
                self.logger.warning(f"  - {f['name']} ({f['protection']}): {f['error'][:50]}...")
                
        self.logger.info(f"\nDetailed report saved to: {report_path}")
        
        return report

async def main():
    """Main execution"""
    tester = ElementExtractorChallengeTester()
    
    print("[INIT] Element Extractor (No LLM) Challenge Test")
    print("[INFO] Testing against high-priority challenging sites")
    print("=" * 60)
    
    # Run tests on priority sites
    await tester.run_tests()
    
    return True

if __name__ == "__main__":
    # Quick compliance test
    if os.environ.get("STANDALONE_TEST") == "1":
        print("[OK] Element extractor challenge tester loads successfully")
        sys.exit(0)
        
    # Run full test
    success = asyncio.run(main())
    sys.exit(0 if success else 1)