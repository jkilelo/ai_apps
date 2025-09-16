#!/usr/bin/env python3
"""
Elements Extractor with LLM V3 - Clean implementation using llm_v3.py

This module extracts web elements and enriches them with LLM analysis
using appropriate prompt strategies from prompts_v3.py via llm_v3.py

Author: Senior Software Engineer
Date: 2025-08-28
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import base extractor - from same directory
from elements_extractor_no_llm import (
    ElementsExtractorNoLLM,
    ExtractionConfig,
    ExtractedElement,
    ExtractionResult,
    ElementType,
)

# Import our new LLM V3
from llm import call_default_llm, Message


# QA Test Categories
class QACategory(str, Enum):
    """Categories for QA testing scenarios"""

    FUNCTIONAL = "functional"
    VALIDATION = "validation"
    ACCESSIBILITY = "accessibility"
    SECURITY = "security"
    PERFORMANCE = "performance"
    USABILITY = "usability"
    COMPATIBILITY = "compatibility"
    ERROR_HANDLING = "error_handling"
    LOCALIZATION = "localization"
    DATA_INTEGRITY = "data_integrity"


# Pydantic Models for Type Safety
class ElementContext(BaseModel):
    """Context information for an element"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    parent_hierarchy: List[str] = Field(default_factory=list)
    siblings_count: int = 0
    position_in_parent: int = 0
    visual_prominence: float = 0.0
    interaction_likelihood: float = 0.0
    semantic_role: Optional[str] = None
    accessibility_score: float = 0.0


class EnrichedElement(BaseModel):
    """Element enriched with LLM analysis"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    base_element: Dict[str, Any]
    llm_analysis: Dict[str, Any] = Field(default_factory=dict)
    context: ElementContext
    qa_categories: List[QACategory] = Field(default_factory=list)
    test_scenarios: List[str] = Field(default_factory=list)
    confidence_score: float = 0.0
    extraction_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class PageAnalysis(BaseModel):
    """Complete page analysis with LLM insights"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    url: str
    title: str = ""
    page_type: str = "unknown"
    framework_detected: Optional[str] = None
    total_elements: int = 0
    interactive_elements: int = 0
    form_elements: int = 0
    navigation_elements: int = 0
    enriched_elements: List[EnrichedElement] = Field(default_factory=list)
    qa_test_plan: Dict[str, List[str]] = Field(default_factory=dict)
    llm_insights: Dict[str, Any] = Field(default_factory=dict)
    extraction_time: float = 0.0
    llm_processing_time: float = 0.0


class ElementLLMAnalyzerV3:
    """Analyzes elements using LLM V3 with appropriate strategies"""

    def __init__(self, batch_size: int = 10):
        """
        Initialize the LLM analyzer

        Args:
            batch_size: Number of elements to process in each LLM call
        """
        self.batch_size = batch_size
        self.analysis_cache: Dict[str, Any] = {}

    def _select_strategy_for_task(self, task_type: str) -> str:
        """
        Select appropriate prompt strategy based on task type

        Args:
            task_type: Type of analysis task

        Returns:
            Strategy name from prompts_v3
        """
        strategy_map = {
            "element_analysis": "chain_of_thought",
            "qa_generation": "tree_of_thoughts",
            "semantic_understanding": "meta_cognitive_framework",
            "test_scenario": "program_aided_language",
            "accessibility": "constitutional_ai",
            "security": "debate",
            "validation": "self_consistency",
            "page_classification": "few_shot",
            "framework_detection": "chain_of_table",
            "interaction_prediction": "reflexion",
        }
        return strategy_map.get(task_type, "chain_of_thought")

    def _prepare_element_batch(self, elements: List[ExtractedElement]) -> str:
        """
        Prepare a batch of elements for LLM analysis

        Args:
            elements: List of extracted elements

        Returns:
            JSON string representation of elements
        """
        batch_data = []
        for elem in elements:
            elem_dict = {
                "tag": elem.tag_name,
                "type": elem.element_type.value if elem.element_type else "unknown",
                "text": elem.text[:100] if elem.text else "",
                "attributes": elem.attributes or {},
                "selector": elem.selector,
                "xpath": elem.xpath,
                "is_interactive": elem.is_clickable or elem.is_editable,
                "is_visible": elem.is_visible,
                "aria_label": elem.attributes.get("aria-label"),
                "role": elem.attributes.get("role"),
            }
            batch_data.append(elem_dict)

        return json.dumps(batch_data, indent=2)

    async def analyze_elements(self, elements: List[ExtractedElement]) -> List[EnrichedElement]:
        """
        Analyze elements with LLM enrichment

        Args:
            elements: List of extracted elements

        Returns:
            List of enriched elements with LLM analysis
        """
        enriched_elements = []

        # Process in batches
        for i in range(0, len(elements), self.batch_size):
            batch = elements[i:i + self.batch_size]
            batch_json = self._prepare_element_batch(batch)

            # Prepare analysis prompt
            analysis_prompt = f"""Analyze these web elements and provide enrichment:

ELEMENTS:
{batch_json}

Return a JSON array with exactly one object per element in the same order.
Each object MUST have these exact keys:
{{
  "semantic_role": "string describing the element's semantic role",
  "qa_categories": ["list of categories - MUST be from: functional, validation, accessibility, security, performance, usability, compatibility, error_handling, localization, data_integrity"],
  "test_scenarios": ["list", "of", "test", "scenarios"],
  "interaction_likelihood": 0.0 to 1.0,
  "accessibility_score": 0.0 to 1.0,
  "security_concerns": ["list", "of", "concerns"],
  "validation_rules": ["list", "of", "rules"],
  "analysis": "detailed analysis text",
  "confidence": 0.0 to 1.0
}}

IMPORTANT: Return ONLY valid JSON array starting with [ and ending with ].
No markdown, no explanations, just the JSON array."""

            # Call LLM with appropriate strategy
            messages = [Message(role="user", content=analysis_prompt)]
            strategy = self._select_strategy_for_task("element_analysis")

            response = call_default_llm(messages, strategy=strategy)

            # Parse LLM response - now response.content is directly accessible
            analysis_results = self._parse_llm_response(response.content)
            
            # Must have exact match for batch size - NO FALLBACKS
            if len(analysis_results) != len(batch):
                raise ValueError(f"LLM returned {len(analysis_results)} results for {len(batch)} elements")

            # Create enriched elements
            for elem, analysis in zip(batch, analysis_results):
                context = ElementContext(
                    semantic_role=analysis.get("semantic_role", "unknown"),
                    interaction_likelihood=analysis.get("interaction_likelihood", 0.0),
                    accessibility_score=analysis.get("accessibility_score", 0.0),
                )

                enriched = EnrichedElement(
                    base_element=self._element_to_dict(elem),
                    llm_analysis=analysis,
                    context=context,
                    qa_categories=self._map_qa_categories(analysis.get("qa_categories", [])),
                    test_scenarios=analysis.get("test_scenarios", []),
                    confidence_score=analysis.get("confidence", 0.8),
                )

                enriched_elements.append(enriched)

        return enriched_elements

    async def generate_qa_test_plan(self, elements: List[EnrichedElement], url: str) -> Dict[str, List[str]]:
        """
        Generate comprehensive QA test plan using LLM

        Args:
            elements: List of enriched elements
            url: Page URL

        Returns:
            QA test plan organized by category
        """
        # Prepare context for test generation
        element_summary = self._summarize_elements_for_qa(elements)

        qa_prompt = f"""Generate a QA test plan for this web page. Return ONLY a valid JSON object.

URL: {url}
ELEMENTS SUMMARY:
{element_summary}

Return a JSON object with these exact keys:
{{
  "functional": ["test case 1", "test case 2"],
  "validation": ["test case 1"],
  "accessibility": ["test case 1"],
  "security": ["test case 1"],
  "performance": ["test case 1"],
  "error_handling": ["test case 1"],
  "cross_browser": ["test case 1"],
  "localization": ["test case 1"]
}}

Each key should have an array of specific test cases. 
If a category doesn't apply, use empty array [].
Start your response with {{ and end with }}"""

        messages = [Message(role="user", content=qa_prompt)]
        strategy = self._select_strategy_for_task("qa_generation")

        response = call_default_llm(messages, strategy=strategy)
        test_plan = self._parse_qa_response(response.content)
        return test_plan

    def _parse_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response into structured data"""
        # Clean the response first
        response = response.strip()
        
        # Remove markdown code blocks if present
        if '```json' in response:
            response = response.replace('```json', '').replace('```', '')
            response = response.strip()
        
        # Try direct JSON parse first
        if response.startswith('['):
            return json.loads(response)
        
        # Try to extract JSON array from response
        import re
        json_match = re.search(r'\[.*?\]', response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # NO FALLBACKS - must succeed or fail completely
        raise ValueError(f"Could not parse JSON array from LLM response")

    def _parse_qa_response(self, response: str) -> Dict[str, List[str]]:
        """Parse QA test plan from LLM response"""
        # Clean the response
        response = response.strip()
        
        # Remove markdown code blocks if present
        if '```json' in response:
            response = response.replace('```json', '').replace('```', '')
            response = response.strip()
        elif response.startswith('```'):
            lines = response.split('\n')
            if len(lines) > 2:
                response = '\n'.join(lines[1:-1]).strip()
        
        # Try direct JSON parse first
        if response.startswith('{'):
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                pass
        
        # Try to find complete JSON object with balanced braces
        import re
        
        brace_count = 0
        json_start = -1
        
        for i, char in enumerate(response):
            if char == '{':
                if brace_count == 0:
                    json_start = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and json_start != -1:
                    # Found complete JSON object
                    json_str = response[json_start:i+1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        continue
        
        # NO FALLBACKS - must succeed or fail completely
        raise ValueError(f"Could not parse JSON object from QA response: {response[:200]}...")

    def _element_to_dict(self, element: ExtractedElement) -> Dict[str, Any]:
        """Convert ExtractedElement to dictionary"""
        return {
            "tag_name": element.tag_name,
            "element_type": element.element_type.value if element.element_type else None,
            "text": element.text,
            "selector": element.selector,
            "xpath": element.xpath,
            "attributes": element.attributes,
            "is_interactive": element.is_clickable or element.is_editable,
            "is_visible": element.is_visible,
        }

    def _map_qa_categories(self, categories: List[str]) -> List[QACategory]:
        """Map string categories to QACategory enum"""
        mapped = []
        for cat in categories:
            cat_lower = cat.lower().replace(" ", "_")
            # Will raise ValueError if invalid category - NO FALLBACKS
            mapped.append(QACategory(cat_lower))
        return mapped

    def _summarize_elements_for_qa(self, elements: List[EnrichedElement]) -> str:
        """Summarize elements for QA test planning"""
        summary = {
            "total_elements": len(elements),
            "interactive": sum(1 for e in elements if e.context.interaction_likelihood > 0.5),
            "forms": sum(1 for e in elements if "form" in str(e.base_element.get("tag_name", "")).lower()),
            "buttons": sum(1 for e in elements if e.base_element.get("element_type") == "button"),
            "links": sum(1 for e in elements if e.base_element.get("element_type") == "link"),
            "inputs": sum(1 for e in elements if e.base_element.get("element_type") == "input"),
        }
        return json.dumps(summary, indent=2)



class ElementsExtractorWithLLMV3:
    """Main class for extracting and enriching web elements with LLM V3"""

    def __init__(self, extraction_config: Optional[ExtractionConfig] = None):
        """
        Initialize the extractor

        Args:
            extraction_config: Configuration for element extraction
        """
        self.extraction_config = extraction_config or ExtractionConfig()
        self.base_extractor = ElementsExtractorNoLLM(self.extraction_config)
        self.llm_analyzer = ElementLLMAnalyzerV3()
        self.browser = None

    async def extract_and_analyze(self, url: str, analyze_with_llm: bool = True) -> PageAnalysis:
        """
        Extract elements from URL and analyze with LLM

        Args:
            url: URL to extract elements from
            analyze_with_llm: Whether to enrich with LLM analysis

        Returns:
            Complete page analysis with enriched elements
        """
        start_time = datetime.now()

        # Extract base elements
        print(f"[INFO] Extracting elements from: {url}")
        try:
            extraction_result = await self.base_extractor.extract_from_url(url)
        finally:
            # Ensure proper cleanup
            if hasattr(self.base_extractor, 'browser') and self.base_extractor.browser:
                await self.base_extractor.browser.cleanup()

        extraction_time = (datetime.now() - start_time).total_seconds()

        if not extraction_result.success:
            return PageAnalysis(
                url=url, extraction_time=extraction_time, llm_insights={"error": "Base extraction failed"}
            )

        # Start page analysis
        page_analysis = PageAnalysis(
            url=url,
            title="",  # title can be extracted from elements if needed
            total_elements=len(extraction_result.elements),
            extraction_time=extraction_time,
        )

        # Count element types
        for elem in extraction_result.elements:
            if elem.is_clickable or elem.is_editable:
                page_analysis.interactive_elements += 1
            if elem.element_type == ElementType.INPUT:
                page_analysis.form_elements += 1
            # NAV might not be in ElementType, check if tag is nav instead
            if elem.tag_name.lower() == "nav":
                page_analysis.navigation_elements += 1

        if analyze_with_llm and extraction_result.elements:
            llm_start = datetime.now()

            # Enrich elements with LLM
            print(f"[INFO] Enriching {len(extraction_result.elements)} elements with LLM...")
            enriched = await self.llm_analyzer.analyze_elements(extraction_result.elements)
            page_analysis.enriched_elements = enriched

            # Generate QA test plan
            print("[INFO] Generating QA test plan...")
            test_plan = await self.llm_analyzer.generate_qa_test_plan(enriched, url)
            page_analysis.qa_test_plan = test_plan

            # Detect framework and page type
            page_insights = await self._analyze_page_characteristics(extraction_result, url)
            page_analysis.page_type = page_insights.get("page_type", "unknown")
            page_analysis.framework_detected = page_insights.get("framework")
            page_analysis.llm_insights = page_insights

            page_analysis.llm_processing_time = (datetime.now() - llm_start).total_seconds()

        return page_analysis

    async def _analyze_page_characteristics(self, extraction_result: ExtractionResult, url: str) -> Dict[str, Any]:
        """
        Analyze overall page characteristics using LLM

        Args:
            extraction_result: Base extraction results
            url: Page URL

        Returns:
            Page insights including type and framework
        """
        # Prepare page summary
        page_summary = {
            "url": url,
            "title": "",  # Could extract from page title element if present
            "total_elements": len(extraction_result.elements),
            "sample_elements": [self._element_summary(elem) for elem in extraction_result.elements[:20]],
        }

        analysis_prompt = f"""Analyze this web page and determine:

PAGE DATA:
{json.dumps(page_summary, indent=2)}

Please identify:
1. Page type (login, dashboard, e-commerce, blog, etc.)
2. Frontend framework if detectable (React, Vue, Angular, etc.)
3. Key functionality areas
4. User interaction patterns
5. Potential testing challenges
6. Recommended testing strategies

Return as JSON with keys: page_type, framework, functionality, patterns, challenges, strategies"""

        messages = [Message(role="user", content=analysis_prompt)]
        strategy = self.llm_analyzer._select_strategy_for_task("page_classification")

        response = call_default_llm(messages, strategy=strategy)
        return self._parse_page_insights(response.content)

    def _element_summary(self, element: ExtractedElement) -> Dict[str, Any]:
        """Create summary of element for analysis"""
        return {
            "tag": element.tag_name,
            "type": element.element_type.value if element.element_type else None,
            "text": element.text[:50] if element.text else None,
            "interactive": element.is_clickable or element.is_editable,
        }

    def _parse_page_insights(self, response: str) -> Dict[str, Any]:
        """Parse page insights from LLM response"""
        # Clean the response
        response = response.strip()
        
        # Remove markdown code blocks if present
        if '```json' in response:
            response = response.replace('```json', '').replace('```', '')
            response = response.strip()
        
        # Try direct JSON parse first
        if response.startswith('{'):
            result = json.loads(response)
            # Ensure required keys exist
            if "page_type" not in result:
                result["page_type"] = "unknown"
            return result
        
        # Try to extract JSON object
        import re
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            # Ensure required keys exist
            if "page_type" not in result:
                result["page_type"] = "unknown"
            return result

        # NO FALLBACKS - must succeed or fail completely
        raise ValueError(f"Could not parse JSON from page insights response")

    async def extract_for_qa(self, url: str) -> Tuple[PageAnalysis, List[str]]:
        """
        Extract elements and generate executable QA test code

        Args:
            url: URL to analyze

        Returns:
            Tuple of page analysis and list of test code snippets
        """
        # Get page analysis
        analysis = await self.extract_and_analyze(url, analyze_with_llm=True)

        # Generate test code for top scenarios
        test_code_snippets = []

        if analysis.qa_test_plan:
            print("[INFO] Generating Playwright test code...")

            for category, scenarios in list(analysis.qa_test_plan.items())[:3]:  # Top 3 categories
                for scenario in scenarios[:2]:  # Top 2 scenarios per category
                    code = await self._generate_test_code(scenario, analysis, category)
                    if code:
                        test_code_snippets.append(code)

        return analysis, test_code_snippets

    async def _generate_test_code(self, scenario: str, analysis: PageAnalysis, category: str) -> Optional[str]:
        """
        Generate executable Playwright test code for a scenario

        Args:
            scenario: Test scenario description
            analysis: Page analysis data
            category: Test category

        Returns:
            Executable Playwright code or None
        """
        # Get relevant elements for the scenario
        relevant_elements = self._get_relevant_elements(scenario, analysis.enriched_elements)

        code_prompt = f"""Generate executable Playwright test code for this scenario:

SCENARIO: {scenario}
CATEGORY: {category}
URL: {analysis.url}

RELEVANT ELEMENTS:
{json.dumps([e.base_element for e in relevant_elements[:5]], indent=2)}

Generate complete, executable Playwright code that:
1. Navigates to the URL
2. Performs the test scenario
3. Includes assertions
4. Handles errors gracefully

Return ONLY the Python code, no explanations."""

        messages = [Message(role="user", content=code_prompt)]
        strategy = self.llm_analyzer._select_strategy_for_task("test_scenario")

        response = call_default_llm(messages, strategy=strategy)
        return self._extract_code(response.content)

    def _get_relevant_elements(self, scenario: str, elements: List[EnrichedElement]) -> List[EnrichedElement]:
        """Get elements relevant to a test scenario"""
        scenario_lower = scenario.lower()
        relevant = []

        for elem in elements:
            elem_text = str(elem.base_element.get("text", "")).lower()
            elem_type = str(elem.base_element.get("element_type", "")).lower()

            # Simple relevance matching
            if any(keyword in scenario_lower for keyword in [elem_text[:20], elem_type]):
                relevant.append(elem)
            elif elem.context.interaction_likelihood > 0.7:
                relevant.append(elem)

        return relevant[:10]  # Return top 10 most relevant

    def _extract_code(self, response: str) -> str:
        """Extract Python code from LLM response"""
        import re

        # Try to find code block
        code_match = re.search(r"```python\n(.*?)```", response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()

        # Try to find async def
        code_match = re.search(r"(async def test.*?(?=\n\nasync def|\n\n#|\Z))", response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()

        # Return as is if it looks like code
        if "async def" in response or "page.goto" in response:
            return response.strip()

        return ""


# Convenience functions
async def extract_and_analyze(url: str, config: Optional[ExtractionConfig] = None) -> PageAnalysis:
    """
    Extract and analyze web elements from a URL

    Args:
        url: URL to analyze
        config: Optional extraction configuration

    Returns:
        Complete page analysis with LLM enrichment
    """
    extractor = ElementsExtractorWithLLMV3(config)
    return await extractor.extract_and_analyze(url, analyze_with_llm=True)


async def generate_qa_tests(url: str) -> Tuple[PageAnalysis, List[str]]:
    """
    Generate QA test code for a URL

    Args:
        url: URL to test

    Returns:
        Page analysis and test code snippets
    """
    extractor = ElementsExtractorWithLLMV3()
    return await extractor.extract_for_qa(url)


# Main execution for testing
async def main():
    """Test the implementation with random URLs from database"""
    print("=" * 60)
    print("ELEMENTS EXTRACTOR WITH LLM V3 - MULTI-SITE TEST")
    print("=" * 60)
    print()

    # Load the challenging sites database
    import random
    database_file = Path(__file__).parent / "challenging_sites_database_expanded.json"
    
    try:
        with open(database_file, "r") as f:
            database = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Database file not found: {database_file}")
        print("[INFO] Falling back to example.com")
        database = {"sites": [{"url": "https://example.com", "name": "Example", "category": "Testing"}]}
    
    # Select 5 random sites
    sites = database.get("sites", [])
    if len(sites) > 5:
        selected_sites = random.sample(sites, 5)
    else:
        selected_sites = sites[:5]
    
    print(f"[INFO] Testing {len(selected_sites)} random sites from database")
    print("-" * 60)
    
    # Configure extraction with 5-element limit
    config = ExtractionConfig(
        max_elements=5,  # Cap at 5 elements
        enable_stealth=True,
        enable_shadow_dom=True,
        include_invisible=False,
        include_iframes=False
    )
    
    results = []
    
    for i, site in enumerate(selected_sites, 1):
        test_url = site.get("url", "https://example.com")
        site_name = site.get("name", "Unknown")
        category = site.get("category", "Unknown")
        
        print()
        print(f"[{i}/{len(selected_sites)}] Testing: {site_name}")
        print(f"     URL: {test_url}")
        print(f"     Category: {category}")
        
        try:
            # Create extractor with config
            extractor = ElementsExtractorWithLLMV3(config)
            
            # Extract and analyze (with timeout)
            analysis = await asyncio.wait_for(
                extractor.extract_and_analyze(test_url, analyze_with_llm=True),
                timeout=120  # 2 minute timeout per site
            )
            
            print(f"     [OK] Extraction completed")
            print(f"       Total elements: {analysis.total_elements}")
            print(f"       Enriched: {len(analysis.enriched_elements)}")
            print(f"       Page type: {analysis.page_type}")
            print(f"       Time: {analysis.extraction_time:.1f}s + {analysis.llm_processing_time:.1f}s LLM")
            
            results.append({
                "site": site_name,
                "url": test_url,
                "success": True,
                "elements": analysis.total_elements,
                "enriched": len(analysis.enriched_elements),
                "page_type": analysis.page_type,
                "timing": {
                    "extraction": analysis.extraction_time,
                    "llm": analysis.llm_processing_time
                }
            })
            
        except asyncio.TimeoutError:
            print(f"     [TIMEOUT] After 120 seconds")
            results.append({
                "site": site_name,
                "url": test_url,
                "success": False,
                "error": "Timeout"
            })
        except Exception as e:
            print(f"     [ERROR] {str(e)[:100]}")
            results.append({
                "site": site_name,
                "url": test_url,
                "success": False,
                "error": str(e)[:200]
            })
    
    # Save all results
    output_file = Path(__file__).parent / "multi_site_test_results.json"
    with open(output_file, "w") as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "config": {
                "max_elements": config.max_elements,
                "sites_tested": len(selected_sites)
            },
            "results": results
        }, f, indent=2)
    
    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    successful = sum(1 for r in results if r.get("success"))
    print(f"Sites tested: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    print(f"Results saved to: {output_file}")
    print()
    
    # Add delay for proper asyncio cleanup
    await asyncio.sleep(0.1)
    
    return 0 if successful > 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

