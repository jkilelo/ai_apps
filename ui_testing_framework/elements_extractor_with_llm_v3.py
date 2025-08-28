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
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import base extractor - from same directory
from elements_extractor_no_llm import (
    ElementsExtractorNoLLM,
    ExtractionConfig,
    ExtractedElement,
    ExtractionResult,
    ElementType,
)

# Import our new LLM V3
from llm_v3 import call_default_llm, Message


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

For each element, provide:
1. Semantic understanding and purpose
2. QA test categories (functional, validation, accessibility, security, etc.)
3. Potential test scenarios
4. Interaction likelihood score (0-1)
5. Accessibility assessment
6. Any security concerns
7. Validation rules if applicable

Return analysis as JSON array matching the input order."""

            # Call LLM with appropriate strategy
            messages: List[Union[Message, Dict[str, str]]] = [{"role": "user", "content": analysis_prompt}]
            strategy = self._select_strategy_for_task("element_analysis")

            try:
                response = call_default_llm(messages, strategy=strategy)

                # Parse LLM response
                analysis_results = self._parse_llm_response(response.content)
                
                # Ensure we have enough analysis results for the batch
                while len(analysis_results) < len(batch):
                    analysis_results.append({
                        "analysis": "default",
                        "confidence": 0.5,
                        "semantic_role": "unknown"
                    })

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

            except Exception as e:
                print(f"[ERROR] LLM analysis failed for batch: {e}")
                # Create basic enrichment without LLM
                for elem in batch:
                    enriched = self._create_basic_enrichment(elem)
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

        qa_prompt = f"""Generate a comprehensive QA test plan for this web page:

URL: {url}
ELEMENTS SUMMARY:
{element_summary}

Create test scenarios for these categories:
1. Functional Testing - Core functionality tests
2. Validation Testing - Input validation and data integrity
3. Accessibility Testing - WCAG compliance and usability
4. Security Testing - XSS, injection, authentication
5. Performance Testing - Load times, responsiveness
6. Error Handling - Edge cases and error recovery
7. Cross-browser Testing - Compatibility checks
8. Localization Testing - Multi-language support

For each category, provide specific, executable test cases.
Return as JSON object with categories as keys and test case arrays as values."""

        messages: List[Union[Message, Dict[str, str]]] = [{"role": "user", "content": qa_prompt}]
        strategy = self._select_strategy_for_task("qa_generation")

        try:
            response = call_default_llm(messages, strategy=strategy)
            test_plan = self._parse_qa_response(response.content)
            return test_plan
        except Exception as e:
            print(f"[ERROR] QA test plan generation failed: {e}")
            return self._generate_basic_test_plan(elements)

    def _parse_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response into structured data"""
        try:
            # Clean the response first
            response = response.strip()
            
            # Try direct JSON parse first
            if response.startswith('['):
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    pass
            
            # Try to extract JSON array from response
            import re
            json_match = re.search(r'\[.*?\]', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            # Fallback to basic parsing - create one analysis per element
            return [{"analysis": "basic", "confidence": 0.5, "semantic_role": "unknown"}]
        except Exception as e:
            print(f"[WARN] Failed to parse LLM response: {e}")
            return [{"analysis": "error", "confidence": 0.3, "semantic_role": "unknown"}]

    def _parse_qa_response(self, response: str) -> Dict[str, List[str]]:
        """Parse QA test plan from LLM response"""
        try:
            # Clean the response
            response = response.strip()
            
            # Try direct JSON parse first
            if response.startswith('{'):
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    pass
            
            # Try to extract JSON object from response
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
                    
            # Return basic test plan if parsing fails
            return self._generate_basic_test_plan([])
        except Exception as e:
            print(f"[WARN] Failed to parse QA response: {e}")
            return self._generate_basic_test_plan([])

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
            try:
                mapped.append(QACategory(cat_lower))
            except Exception:
                # Default to functional if unknown
                if not mapped:
                    mapped.append(QACategory.FUNCTIONAL)
        return mapped

    def _create_basic_enrichment(self, element: ExtractedElement) -> EnrichedElement:
        """Create basic enrichment without LLM"""
        context = ElementContext(interaction_likelihood=1.0 if (element.is_clickable or element.is_editable) else 0.2)

        # Determine basic QA categories
        categories = [QACategory.FUNCTIONAL]
        if element.element_type == ElementType.INPUT:
            categories.append(QACategory.VALIDATION)
        if element.attributes.get("aria-label") or element.attributes.get("role"):
            categories.append(QACategory.ACCESSIBILITY)

        return EnrichedElement(
            base_element=self._element_to_dict(element), context=context, qa_categories=categories, confidence_score=0.5
        )

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

    def _generate_basic_test_plan(self, elements: List[EnrichedElement]) -> Dict[str, List[str]]:
        """Generate basic test plan without LLM"""
        plan = {
            "functional": [
                "Verify all buttons are clickable",
                "Test all form submissions",
                "Validate navigation links",
            ],
            "validation": ["Test required field validation", "Verify input format requirements"],
            "accessibility": ["Check ARIA labels presence", "Verify keyboard navigation"],
        }
        return plan


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
                try:
                    await self.base_extractor.browser.cleanup()
                except Exception:
                    pass

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

        messages: List[Union[Message, Dict[str, str]]] = [{"role": "user", "content": analysis_prompt}]
        strategy = self.llm_analyzer._select_strategy_for_task("page_classification")

        try:
            response = call_default_llm(messages, strategy=strategy)
            return self._parse_page_insights(response.content)
        except Exception as e:
            print(f"[ERROR] Page analysis failed: {e}")
            return {"page_type": "unknown", "error": str(e)}

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
        try:
            # Clean the response
            response = response.strip()
            
            # Try direct JSON parse first
            if response.startswith('{'):
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    pass
            
            # Try to extract JSON object
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    # Ensure required keys exist
                    if "page_type" not in result:
                        result["page_type"] = "unknown"
                    return result
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"[WARN] Failed to parse page insights: {e}")

        # Return default insights
        return {
            "page_type": "unknown",
            "framework": None,
            "functionality": [],
            "patterns": [],
            "challenges": [],
            "strategies": []
        }

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

        messages: List[Union[Message, Dict[str, str]]] = [{"role": "user", "content": code_prompt}]
        strategy = self.llm_analyzer._select_strategy_for_task("test_scenario")

        try:
            response = call_default_llm(messages, strategy=strategy)
            return self._extract_code(response.content)
        except Exception as e:
            print(f"[ERROR] Code generation failed: {e}")
            return None

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
    """Test the implementation with a real URL"""
    print("=" * 60)
    print("ELEMENTS EXTRACTOR WITH LLM V3")
    print("=" * 60)
    print()

    # Test URL
    test_url = "https://example.com"

    print(f"[TEST] Analyzing: {test_url}")
    print()

    try:
        # Extract and analyze
        analysis = await extract_and_analyze(test_url)

        print("[OK] Extraction completed")
        print(f"     Total elements: {analysis.total_elements}")
        print(f"     Interactive elements: {analysis.interactive_elements}")
        print(f"     Enriched elements: {len(analysis.enriched_elements)}")
        print(f"     Page type: {analysis.page_type}")
        print(f"     Framework: {analysis.framework_detected or 'Not detected'}")
        print(f"     Extraction time: {analysis.extraction_time:.2f}s")
        print(f"     LLM processing time: {analysis.llm_processing_time:.2f}s")

        if analysis.qa_test_plan:
            print()
            print("[OK] QA Test Plan Generated:")
            for category, tests in list(analysis.qa_test_plan.items())[:3]:
                print(f"     {category}: {len(tests)} test scenarios")

        # Save results
        output_file = Path(__file__).parent / "test_results_v3.json"
        with open(output_file, "w") as f:
            # Convert to dict for JSON serialization
            result_dict = {
                "url": analysis.url,
                "title": analysis.title,
                "page_type": analysis.page_type,
                "framework": analysis.framework_detected,
                "stats": {
                    "total_elements": analysis.total_elements,
                    "interactive": analysis.interactive_elements,
                    "enriched": len(analysis.enriched_elements),
                },
                "qa_test_categories": list(analysis.qa_test_plan.keys()) if analysis.qa_test_plan else [],
                "timing": {"extraction": analysis.extraction_time, "llm_processing": analysis.llm_processing_time},
            }
            json.dump(result_dict, f, indent=2)

        print()
        print(f"[OK] Results saved to: {output_file}")
        print()
        print("[SUCCESS] Elements Extractor with LLM V3 working!")

        return 0

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

