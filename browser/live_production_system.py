"""
LIVE Production UI Testing System with Real Browser Automation
==============================================================
This system uses REAL browser automation to extract elements from LIVE websites.
No mocks, no fake data - everything is extracted from actual web pages.

Pipeline:
1. Real browser navigation using UltimateStealthBrowserLLMEnhanced
2. Live element extraction with LLM optimization
3. Test case generation based on actual page structure
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import sys
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import LLM functionality
from llm import query_llm

# Import browser automation
from browser.main import UltimateStealthBrowserLLMEnhanced
from browser.base import StealthConfig, StealthLevel
from browser.element_structure import PageStructure, LLMOptimizedElement

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class LiveProductionConfig:
    """Configuration for live production testing."""
    
    # Browser Settings
    headless: bool = False  # Set to False to see browser in action
    stealth_level: StealthLevel = StealthLevel.MAXIMUM
    timeout: int = 30000  # 30 seconds
    wait_for_load: bool = True
    
    # LLM Settings
    llm_provider: str = "gemini"
    llm_model: str = "gemini-2.0-flash-exp"
    llm_temperature: float = 0.3
    llm_max_retries: int = 3
    
    # Extraction Settings
    max_elements_per_page: int = 50
    extract_timeout: int = 60
    
    # Test Generation Settings
    test_strategies: List[str] = field(default_factory=lambda: [
        "critical_path",
        "validation",
        "error_handling",
        "security"
    ])
    scenarios_per_strategy: int = 3
    
    # Storage Settings
    results_dir: str = "live_test_results"
    save_screenshots: bool = True
    save_intermediate: bool = True


# ============================================================================
# LIVE BROWSER EXTRACTOR
# ============================================================================

class LiveBrowserExtractor:
    """Extract elements from live websites using real browser automation."""
    
    def __init__(self, config: LiveProductionConfig):
        self.config = config
        self.browser = None
        self.extraction_count = 0
    
    async def initialize(self):
        """Initialize the browser with stealth configuration."""
        browser_config = StealthConfig(
            level=self.config.stealth_level,
            headless=self.config.headless,
            detect_frameworks=True,
            detect_captcha=True
        )
        
        self.browser = UltimateStealthBrowserLLMEnhanced(browser_config)
        await self.browser.initialize()
        logger.info("Browser initialized with stealth capabilities")
    
    async def extract_from_url(self, url: str) -> PageStructure:
        """Extract elements from a live URL."""
        if not self.browser:
            await self.initialize()
        
        try:
            logger.info(f"Navigating to {url}...")
            
            # Extract elements using LLM-optimized method
            page_structure = await self.browser.extract_elements_for_llm(url)
            
            self.extraction_count += 1
            
            # Count total elements
            total_elements = sum(
                len(elements) for elements in page_structure.elements_by_category.values()
            )
            
            logger.info(f"Extracted {total_elements} elements from {url}")
            logger.info(f"Categories found: {list(page_structure.elements_by_category.keys())}")
            
            # Take screenshot if enabled
            if self.config.save_screenshots:
                screenshot_path = await self._take_screenshot(url)
                logger.info(f"Screenshot saved: {screenshot_path}")
            
            return page_structure
            
        except Exception as e:
            logger.error(f"Error extracting from {url}: {e}")
            raise
    
    async def _take_screenshot(self, url: str) -> str:
        """Take a screenshot of the current page."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        site_name = url.split('/')[2].replace('.', '_')
        
        results_dir = Path(self.config.results_dir)
        results_dir.mkdir(exist_ok=True)
        
        screenshot_path = results_dir / f"{timestamp}_{site_name}_screenshot.png"
        
        if self.browser and self.browser.page:
            await self.browser.page.screenshot(path=str(screenshot_path))
        
        return str(screenshot_path)
    
    async def cleanup(self):
        """Clean up browser resources."""
        if self.browser:
            await self.browser.cleanup()
            logger.info("Browser cleanup completed")


# ============================================================================
# LLM TEST GENERATOR
# ============================================================================

class LiveTestGenerator:
    """Generate test cases from live extracted elements using LLM."""
    
    def __init__(self, config: LiveProductionConfig):
        self.config = config
        self.llm_calls = 0
    
    async def generate_tests(
        self, 
        page_structure: PageStructure,
        strategy: str
    ) -> List[Dict[str, Any]]:
        """Generate test cases for a specific strategy based on live data."""
        
        # Prepare element summary from live extraction
        element_summary = self._create_element_summary(page_structure)
        
        strategy_prompts = {
            "critical_path": """Generate test cases for the MOST CRITICAL user journeys on this page.
Focus on paths that users MUST be able to complete successfully.
Consider the actual page structure and business purpose.""",
            
            "validation": """Generate test cases for INPUT VALIDATION based on the actual form fields found.
Test required fields, format validation, boundary values, and field interdependencies.
Use the actual validation rules detected on the page.""",
            
            "error_handling": """Generate test cases for ERROR SCENARIOS based on the actual page elements.
Test how the application handles invalid inputs, missing data, and edge cases.
Consider the specific error-prone areas identified.""",
            
            "security": """Generate SECURITY test cases based on the actual vulnerabilities present.
Test for XSS, injection attacks, authentication bypass, and data exposure.
Focus on the specific security risks identified in the elements."""
        }
        
        prompt = f"""{strategy_prompts.get(strategy, strategy_prompts['critical_path'])}

PAGE INFORMATION:
URL: {page_structure.url}
Type: {page_structure.page_type}
Purpose: {page_structure.business_purpose}

ACTUAL ELEMENTS EXTRACTED:
{element_summary}

CRITICAL PATHS IDENTIFIED:
{json.dumps(page_structure.critical_paths[:3], indent=2) if page_structure.critical_paths else "None identified"}

USER JOURNEYS:
{json.dumps(page_structure.user_journeys[:3], indent=2) if page_structure.user_journeys else "None identified"}

VALIDATIONS REQUIRED:
{json.dumps(page_structure.page_validations[:5], indent=2) if page_structure.page_validations else "None identified"}

Generate exactly {self.config.scenarios_per_strategy} test cases based on the ACTUAL page structure above.

Return as JSON:
{{
  "test_cases": [
    {{
      "title": "Specific test case title",
      "description": "What this tests on the actual page",
      "priority": "critical|high|medium|low",
      "steps": [
        {{"action": "Specific action on actual element", "selector": "actual selector", "expected": "Expected result"}}
      ],
      "assertions": ["Specific assertion"],
      "test_data": {{"field": "value for actual field"}}
    }}
  ]
}}"""

        try:
            response = await self._call_llm(prompt)
            self.llm_calls += 1
            
            if response and 'test_cases' in response:
                return response['test_cases']
            else:
                logger.warning(f"No test cases generated for {strategy}")
                return []
                
        except Exception as e:
            logger.error(f"Error generating tests: {e}")
            return []
    
    def _create_element_summary(self, page_structure: PageStructure) -> str:
        """Create a concise summary of live extracted elements."""
        summary = []
        
        for category, elements in page_structure.elements_by_category.items():
            if elements:
                summary.append(f"\n{category.value.upper()} ({len(elements)} elements):")
                
                for elem in elements[:3]:  # Show first 3 of each category
                    elem_info = {
                        'id': elem.element_id,
                        'tag': elem.tag_name,
                        'type': elem.element_category.value,
                        'selectors': elem.selectors,
                        'purpose': elem.semantic.primary_purpose if elem.semantic else None,
                        'priority': elem.test_priority.value if elem.test_priority else None
                    }
                    
                    # Add interaction info
                    if elem.interaction:
                        elem_info['interaction'] = elem.interaction.primary_interaction.value
                    
                    # Add validation info
                    if elem.validation and elem.validation.rules:
                        elem_info['validation_rules'] = [r.value for r in elem.validation.rules]
                    
                    summary.append(f"  - {json.dumps(elem_info, indent=4)}")
        
        return '\n'.join(summary)
    
    async def _call_llm(self, prompt: str) -> Dict:
        """Call LLM with retry logic."""
        for attempt in range(self.config.llm_max_retries):
            try:
                messages = [
                    {"role": "system", "content": "You are a QA expert. Generate practical test cases based on actual page elements."},
                    {"role": "user", "content": prompt}
                ]
                
                response = query_llm(
                    provider=self.config.llm_provider,
                    model=self.config.llm_model,
                    messages=messages
                )
                
                content = response.choices[0].message.content
                
                # Extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                
                return {}
                
            except Exception as e:
                logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")
                if attempt < self.config.llm_max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise


# ============================================================================
# RESULT MANAGER
# ============================================================================

class LiveResultManager:
    """Manage results from live testing."""
    
    def __init__(self, config: LiveProductionConfig):
        self.config = config
        self.results_dir = Path(config.results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def save_extraction(self, url: str, page_structure: PageStructure) -> Path:
        """Save live extraction results."""
        site_name = url.split('/')[2].replace('.', '_')
        file_path = self.results_dir / f"{self.session_id}_{site_name}_extraction.json"
        
        # Convert to serializable format
        data = {
            "url": page_structure.url,
            "timestamp": datetime.now().isoformat(),
            "page_type": page_structure.page_type,
            "business_purpose": page_structure.business_purpose,
            "total_elements": sum(len(elems) for elems in page_structure.elements_by_category.values()),
            "categories": {
                category.value: len(elements) 
                for category, elements in page_structure.elements_by_category.items()
            },
            "user_journeys": page_structure.user_journeys,
            "critical_paths": page_structure.critical_paths,
            "page_validations": page_structure.page_validations,
            "security_considerations": page_structure.security_considerations
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Saved extraction to {file_path}")
        return file_path
    
    def save_test_cases(self, url: str, test_cases: Dict[str, List]) -> Path:
        """Save generated test cases."""
        site_name = url.split('/')[2].replace('.', '_')
        file_path = self.results_dir / f"{self.session_id}_{site_name}_tests.json"
        
        data = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "total_cases": sum(len(cases) for cases in test_cases.values()),
            "test_cases": test_cases
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved test cases to {file_path}")
        return file_path
    
    def save_summary(self, results: List[Dict]) -> Path:
        """Save overall summary."""
        file_path = self.results_dir / f"{self.session_id}_summary.json"
        
        with open(file_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Saved summary to {file_path}")
        return file_path


# ============================================================================
# MAIN LIVE PRODUCTION SYSTEM
# ============================================================================

class LiveProductionUITestSystem:
    """Production system using REAL browser automation on LIVE sites."""
    
    def __init__(self, config: Optional[LiveProductionConfig] = None):
        self.config = config or LiveProductionConfig()
        self.extractor = LiveBrowserExtractor(self.config)
        self.generator = LiveTestGenerator(self.config)
        self.result_manager = LiveResultManager(self.config)
        self.stats = {
            "start_time": datetime.now(),
            "sites_processed": 0,
            "elements_extracted": 0,
            "test_cases_generated": 0,
            "llm_calls": 0
        }
    
    async def process_site(self, url: str) -> Dict[str, Any]:
        """Process a live site with real browser automation."""
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing LIVE site: {url}")
        logger.info('='*60)
        
        result = {
            "url": url,
            "success": False,
            "extraction": None,
            "test_cases": None,
            "errors": []
        }
        
        try:
            # Step 1: Extract elements from LIVE site
            logger.info("Step 1: Extracting elements from LIVE page...")
            page_structure = await self.extractor.extract_from_url(url)
            
            # Save extraction results
            extraction_file = self.result_manager.save_extraction(url, page_structure)
            
            total_elements = sum(
                len(elements) for elements in page_structure.elements_by_category.values()
            )
            
            result["extraction"] = {
                "total_elements": total_elements,
                "categories": list(page_structure.elements_by_category.keys()),
                "page_type": page_structure.page_type,
                "file": str(extraction_file)
            }
            
            self.stats["elements_extracted"] += total_elements
            
            # Display extraction summary
            print(f"\n[LIVE EXTRACTION COMPLETE]")
            print(f"  URL: {url}")
            print(f"  Page Type: {page_structure.page_type}")
            print(f"  Total Elements: {total_elements}")
            print(f"  Categories: {', '.join(cat.value for cat in page_structure.elements_by_category.keys())}")
            
            if page_structure.user_journeys:
                print(f"\n  User Journeys Detected:")
                for journey in page_structure.user_journeys[:3]:
                    print(f"    - {journey.get('name', 'Unknown')}")
            
            if page_structure.critical_paths:
                print(f"\n  Critical Paths:")
                for path in page_structure.critical_paths[:3]:
                    print(f"    - {path.get('element', 'Unknown')}: {path.get('action', 'Unknown')}")
            
            # Step 2: Generate test cases based on LIVE data
            logger.info("Step 2: Generating test cases from LIVE elements...")
            test_cases = {}
            
            for strategy in self.config.test_strategies:
                logger.info(f"  Generating {strategy} tests...")
                cases = await self.generator.generate_tests(page_structure, strategy)
                test_cases[strategy] = cases
                self.stats["test_cases_generated"] += len(cases)
                
                # Rate limiting
                await asyncio.sleep(1)
            
            # Save test cases
            test_file = self.result_manager.save_test_cases(url, test_cases)
            
            result["test_cases"] = {
                "total": sum(len(cases) for cases in test_cases.values()),
                "by_strategy": {s: len(c) for s, c in test_cases.items()},
                "file": str(test_file)
            }
            
            self.stats["llm_calls"] = self.generator.llm_calls
            
            # Display test summary
            print(f"\n[TEST GENERATION COMPLETE]")
            print(f"  Total Test Cases: {result['test_cases']['total']}")
            for strategy, count in result['test_cases']['by_strategy'].items():
                print(f"    {strategy}: {count} cases")
            
            # Show sample test case
            for strategy, cases in test_cases.items():
                if cases and len(cases) > 0:
                    print(f"\n  Sample {strategy} test:")
                    case = cases[0]
                    print(f"    Title: {case.get('title', 'N/A')}")
                    print(f"    Priority: {case.get('priority', 'N/A')}")
                    if case.get('steps'):
                        print(f"    First Step: {case['steps'][0].get('action', 'N/A')}")
                    break
            
            result["success"] = True
            self.stats["sites_processed"] += 1
            
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            result["errors"].append(str(e))
            import traceback
            traceback.print_exc()
        
        return result
    
    async def run_tests(self, urls: List[str]) -> List[Dict]:
        """Run tests on multiple live sites."""
        results = []
        
        try:
            # Initialize browser once
            await self.extractor.initialize()
            
            for url in urls:
                result = await self.process_site(url)
                results.append(result)
                
                # Save intermediate results
                self.result_manager.save_summary(results)
                
                # Rate limiting between sites
                await asyncio.sleep(2)
            
        finally:
            # Always cleanup browser
            await self.extractor.cleanup()
        
        return results
    
    def get_stats(self) -> Dict:
        """Get system statistics."""
        runtime = (datetime.now() - self.stats["start_time"]).total_seconds()
        return {
            "runtime_seconds": runtime,
            "sites_processed": self.stats["sites_processed"],
            "elements_extracted": self.stats["elements_extracted"],
            "test_cases_generated": self.stats["test_cases_generated"],
            "llm_calls": self.stats["llm_calls"],
            "avg_elements_per_site": self.stats["elements_extracted"] / max(self.stats["sites_processed"], 1),
            "avg_cases_per_site": self.stats["test_cases_generated"] / max(self.stats["sites_processed"], 1)
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def run_live_production_tests():
    """Run production tests on LIVE websites."""
    
    # Configuration
    config = LiveProductionConfig(
        headless=False,  # Set to False to see browser in action
        stealth_level=StealthLevel.MAXIMUM,
        test_strategies=["critical_path", "validation", "security"],
        scenarios_per_strategy=2,
        save_screenshots=True
    )
    
    # Test sites
    test_sites = [
        "https://example.com",
        "https://quotes.toscrape.com",
        "https://github.com/login"
    ]
    
    print("\n" + "="*60)
    print("LIVE PRODUCTION UI TESTING SYSTEM")
    print("="*60)
    print("Testing REAL websites with LIVE browser automation")
    print(f"Sites to test: {', '.join(test_sites)}")
    print(f"Browser mode: {'Headless' if config.headless else 'Visible'}")
    print(f"Strategies: {', '.join(config.test_strategies)}")
    print(f"Results directory: {config.results_dir}/")
    print("="*60)
    
    # Initialize system
    system = LiveProductionUITestSystem(config)
    
    # Run tests on live sites
    results = await system.run_tests(test_sites)
    
    # Final summary
    print("\n" + "="*60)
    print("LIVE TESTING SUMMARY")
    print("="*60)
    
    stats = system.get_stats()
    print(f"Runtime: {stats['runtime_seconds']:.1f} seconds")
    print(f"Sites processed: {stats['sites_processed']}")
    print(f"Elements extracted (LIVE): {stats['elements_extracted']}")
    print(f"Test cases generated: {stats['test_cases_generated']}")
    print(f"LLM calls: {stats['llm_calls']}")
    print(f"Avg elements/site: {stats['avg_elements_per_site']:.1f}")
    print(f"Avg test cases/site: {stats['avg_cases_per_site']:.1f}")
    
    # Success/failure summary
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    print(f"\nSuccess rate: {successful}/{len(results)} sites")
    
    if failed > 0:
        print(f"Failed sites:")
        for r in results:
            if not r['success']:
                print(f"  - {r['url']}: {r['errors']}")
    
    # Save final summary
    summary_path = system.result_manager.save_summary({
        "stats": stats,
        "results": results,
        "config": {
            "headless": config.headless,
            "stealth_level": config.stealth_level.value,
            "strategies": config.test_strategies
        }
    })
    
    print(f"\nAll results saved to: {summary_path.parent}/")
    
    return results


if __name__ == "__main__":
    print("Starting LIVE Production UI Testing System")
    print("This will use REAL browser automation on LIVE websites")
    print("")
    
    try:
        # Check for required packages
        try:
            import playwright
            print("[OK] Playwright is installed")
        except ImportError:
            print("[WARNING] Playwright not installed. Installing...")
            os.system("pip install playwright")
            os.system("playwright install chromium")
        
        # Run the live tests
        results = asyncio.run(run_live_production_tests())
        print("\n[SUCCESS] Live testing completed!")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()