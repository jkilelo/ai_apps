"""
Element Extractor with LLM Enhancement
Focuses ONLY on element extraction and enrichment
Test generation handled by test_generation_with_llm.py
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import base extractor
from elements_extractor_no_llm import (
    ElementsExtractorNoLLM,
    ExtractedElement,
    ExtractionResult,
)

# Import types
from data_types import (
    ElementType,
    BrowserExtractionConfig as ExtractionConfig,
)

# Import LLM functionality
from llm import call_default_llm

# Import shared utilities and models
from llm_utils import (
    LLMResponseParser,
    StrategySelector,
    LLMPromptBuilder,
    prepare_llm_messages
)

from data_types import (
    TestCategory,
    TestPriority,
    ElementContext,
    EnrichedElement,
    PageAnalysis
)


class ElementLLMAnalyzer:
    """
    Analyzes elements using LLM for semantic enrichment
    ONLY focuses on element analysis - NO test generation
    """
    
    def __init__(self, batch_size: int = 10):
        """
        Initialize the LLM analyzer
        
        Args:
            batch_size: Number of elements to process in each LLM call
        """
        self.batch_size = batch_size
        self.parser = LLMResponseParser()
        self.strategy_selector = StrategySelector()
        self.prompt_builder = LLMPromptBuilder()
    
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
                "aria_label": elem.attributes.get("aria-label") if elem.attributes else None,
                "role": elem.attributes.get("role") if elem.attributes else None,
            }
            batch_data.append(elem_dict)
        
        return json.dumps(batch_data, indent=2)
    
    async def analyze_elements(
        self, elements: List[ExtractedElement]
    ) -> List[EnrichedElement]:
        """
        Analyze elements with LLM enrichment
        Focus on semantic understanding and categorization
        
        Args:
            elements: List of extracted elements
            
        Returns:
            List of enriched elements with LLM analysis
        """
        enriched_elements = []
        
        # Process in batches
        for i in range(0, len(elements), self.batch_size):
            batch = elements[i : i + self.batch_size]
            batch_json = self._prepare_element_batch(batch)
            
            # Build analysis prompt using shared utility
            expected_structure = {
                "semantic_role": "string describing the element's semantic role",
                "interaction_likelihood": "0.0 to 1.0",
                "accessibility_score": "0.0 to 1.0",
                "potential_issues": ["list", "of", "potential", "issues"],
                "suggested_improvements": ["list", "of", "improvements"],
                "element_purpose": "detailed purpose description",
                "user_impact": "how this element impacts user experience",
                "confidence": "0.0 to 1.0"
            }
            
            analysis_prompt = self.prompt_builder.build_json_prompt(
                task_description="Analyze these web elements for semantic understanding and quality assessment:",
                context={"elements": json.loads(batch_json)},
                expected_structure=[expected_structure]  # Array of structures
            )
            
            # Prepare messages with strategy
            strategy = self.strategy_selector.get_strategy("element_analysis")
            messages = prepare_llm_messages(analysis_prompt, strategy=strategy)
            
            # Call LLM
            response = call_default_llm(messages)
            
            # Parse response using shared parser
            analysis_results = self.parser.parse_json_array(response.content)
            
            # Validate result count
            if len(analysis_results) != len(batch):
                raise ValueError(
                    f"LLM returned {len(analysis_results)} results for {len(batch)} elements"
                )
            
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
                    test_categories=[],  # Empty - test generation handles this
                    test_scenarios=[],   # Empty - test generation handles this
                    confidence_score=analysis.get("confidence", 0.8),
                )
                
                enriched_elements.append(enriched)
        
        return enriched_elements
    
    def _element_to_dict(self, element: ExtractedElement) -> Dict[str, Any]:
        """Convert ExtractedElement to dictionary"""
        return {
            "tag_name": element.tag_name,
            "element_type": (
                element.element_type.value if element.element_type else None
            ),
            "text": element.text,
            "selector": element.selector,
            "xpath": element.xpath,
            "attributes": element.attributes,
            "is_interactive": element.is_clickable or element.is_editable,
            "is_visible": element.is_visible,
        }


class PageCharacteristicsAnalyzer:
    """
    Analyzes overall page characteristics
    Separate from element analysis for single responsibility
    """
    
    def __init__(self):
        self.parser = LLMResponseParser()
        self.strategy_selector = StrategySelector()
        self.prompt_builder = LLMPromptBuilder()
    
    async def analyze_page(
        self, extraction_result: ExtractionResult, url: str
    ) -> Dict[str, Any]:
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
            "total_elements": len(extraction_result.elements),
            "sample_elements": [
                self._element_summary(elem) for elem in extraction_result.elements[:20]
            ],
        }
        
        expected_structure = {
            "page_type": "login, dashboard, e-commerce, blog, etc.",
            "framework": "React, Vue, Angular, etc. or null",
            "functionality": ["list", "of", "key", "functionalities"],
            "ui_patterns": ["list", "of", "UI", "patterns"],
            "accessibility_level": "high, medium, or low",
            "mobile_friendly": "true or false",
            "recommendations": ["list", "of", "recommendations"]
        }
        
        analysis_prompt = self.prompt_builder.build_json_prompt(
            task_description="Analyze this web page to determine its characteristics:",
            context=page_summary,
            expected_structure=expected_structure
        )
        
        # Use appropriate strategy
        strategy = self.strategy_selector.get_strategy("page_classification")
        messages = prepare_llm_messages(analysis_prompt, strategy=strategy)
        
        response = call_default_llm(messages)
        insights = self.parser.parse_json_object(response.content)
        
        # Ensure required keys
        if "page_type" not in insights:
            insights["page_type"] = "unknown"
        
        return insights
    
    def _element_summary(self, element: ExtractedElement) -> Dict[str, Any]:
        """Create summary of element for analysis"""
        return {
            "tag": element.tag_name,
            "type": element.element_type.value if element.element_type else None,
            "text": element.text[:50] if element.text else None,
            "interactive": element.is_clickable or element.is_editable,
        }


class ElementsExtractorWithLLM:
    """
    Main class for extracting and enriching web elements with LLM
    Focuses ONLY on extraction and enrichment - NO test generation
    """
    
    def __init__(self, extraction_config: Optional[ExtractionConfig] = None):
        """
        Initialize the extractor
        
        Args:
            extraction_config: Configuration for element extraction
        """
        self.extraction_config = extraction_config or ExtractionConfig()
        self.base_extractor = ElementsExtractorNoLLM(self.extraction_config)
        self.element_analyzer = ElementLLMAnalyzer()
        self.page_analyzer = PageCharacteristicsAnalyzer()
        
        # Define interactive element criteria inspired by v2
        self.interactive_tags = {'button', 'a', 'input', 'select', 'textarea', 'label', 'option'}
        self.interactive_roles = {'button', 'link', 'checkbox', 'radio', 'textbox', 'combobox', 'listbox'}
        self.interactive_types = {ElementType.BUTTON, ElementType.LINK, ElementType.INPUT, 
                                 ElementType.SELECT, ElementType.TEXTAREA, ElementType.CHECKBOX,
                                 ElementType.RADIO}
    
    async def extract_and_analyze(
        self, url: str, analyze_with_llm: bool = True, max_elements: int = 10
    ) -> PageAnalysis:
        """
        Extract elements from URL and analyze with LLM
        
        Args:
            url: URL to extract elements from
            analyze_with_llm: Whether to enrich with LLM analysis
            max_elements: Maximum number of interactive elements to enrich with LLM (default: 10)
            
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
            if hasattr(self.base_extractor, "browser") and self.base_extractor.browser:
                await self.base_extractor.browser.cleanup()
        
        extraction_time = (datetime.now() - start_time).total_seconds()
        
        if not extraction_result.success:
            return PageAnalysis(
                url=url,
                extraction_time=extraction_time,
                llm_insights={"error": "Base extraction failed"},
            )
        
        # Filter for interactive elements only and remove nulls
        interactive_elements = self._filter_interactive_elements(extraction_result.elements)
        
        # Limit to max_elements if there are too many
        original_count = len(interactive_elements)
        if len(interactive_elements) > max_elements:
            print(f"[INFO] Limiting interactive elements from {len(interactive_elements)} to {max_elements} for LLM processing")
            # Take the first max_elements most important elements (prioritize forms, buttons, links)
            interactive_elements = self._prioritize_elements(interactive_elements, max_elements)
        
        # Start page analysis
        page_analysis = PageAnalysis(
            url=url,
            total_elements=original_count,  # Keep track of original count
            extraction_time=extraction_time,
        )
        
        # Count element types (from all interactive elements, not just limited)
        page_analysis.interactive_elements = original_count
        for elem in interactive_elements[:max_elements]:  # Only count the ones we'll process
            if elem.element_type == ElementType.INPUT:
                page_analysis.form_elements += 1
            if elem.tag_name.lower() == "nav":
                page_analysis.navigation_elements += 1
        
        if analyze_with_llm and interactive_elements:
            llm_start = datetime.now()
            
            # Skip LLM enrichment for simple pages (< 5 interactive elements)
            if len(interactive_elements) < 5:
                print(f"[INFO] Skipping LLM enrichment for simple page ({len(interactive_elements)} interactive elements)")
                # Convert to enriched format without LLM
                enriched = [self._create_basic_enriched_element(elem) for elem in interactive_elements]
            else:
                # Enrich elements with LLM (already limited to max_elements)
                print(f"[INFO] Enriching {len(interactive_elements)} interactive elements with LLM...")
                enriched = await self.element_analyzer.analyze_elements(
                    interactive_elements
                )
            page_analysis.enriched_elements = enriched
            
            # Analyze page characteristics
            print("[INFO] Analyzing page characteristics...")
            page_insights = await self.page_analyzer.analyze_page(
                extraction_result, url
            )
            page_analysis.page_type = page_insights.get("page_type", "unknown")
            page_analysis.framework_detected = page_insights.get("framework")
            page_analysis.llm_insights = page_insights
            
            page_analysis.llm_processing_time = (
                datetime.now() - llm_start
            ).total_seconds()
        
        return page_analysis
    
    def _filter_interactive_elements(self, elements: List[Any]) -> List[Any]:
        """
        Filter for interactive elements only and remove nulls
        Inspired by v2 interactive profile
        """
        interactive_elements = []
        
        for elem in elements:
            # Skip null or invalid elements
            if not elem or not hasattr(elem, 'tag_name'):
                continue
            
            # Check if element is interactive
            is_interactive = False
            
            # Check by tag name
            if elem.tag_name.lower() in self.interactive_tags:
                is_interactive = True
            
            # Check by element type
            elif hasattr(elem, 'element_type') and elem.element_type in self.interactive_types:
                is_interactive = True
            
            # Check by attributes (role, onclick, href, etc.)
            elif hasattr(elem, 'attributes'):
                attrs = elem.attributes or {}
                if attrs.get('role') in self.interactive_roles:
                    is_interactive = True
                elif any(attrs.get(attr) for attr in ['onclick', 'href', 'ng-click', '@click']):
                    is_interactive = True
                elif attrs.get('tabindex', '-1') != '-1':
                    is_interactive = True
            
            # Check by clickable/editable flags
            elif hasattr(elem, 'is_clickable') and elem.is_clickable:
                is_interactive = True
            elif hasattr(elem, 'is_editable') and elem.is_editable:
                is_interactive = True
            
            if is_interactive:
                interactive_elements.append(elem)
        
        return interactive_elements
    
    def _prioritize_elements(self, elements: List[Any], max_count: int) -> List[Any]:
        """
        Prioritize elements for LLM processing when there are too many
        Priority: forms/inputs > buttons > links > others
        
        Args:
            elements: List of interactive elements
            max_count: Maximum number to return
            
        Returns:
            Prioritized list of elements limited to max_count
        """
        if len(elements) <= max_count:
            return elements
        
        # Categorize elements by priority
        forms_inputs = []
        buttons = []
        links = []
        others = []
        
        for elem in elements:
            tag = elem.tag_name.lower() if hasattr(elem, 'tag_name') else ''
            elem_type = getattr(elem, 'element_type', None)
            
            if tag in ['input', 'textarea', 'select'] or elem_type == ElementType.INPUT:
                forms_inputs.append(elem)
            elif tag == 'button' or elem_type == ElementType.BUTTON:
                buttons.append(elem)
            elif tag == 'a' or elem_type == ElementType.LINK:
                links.append(elem)
            else:
                others.append(elem)
        
        # Build prioritized list
        prioritized = []
        
        # Add forms/inputs first (most important for testing)
        prioritized.extend(forms_inputs[:max_count])
        
        # Add buttons if we have room
        remaining = max_count - len(prioritized)
        if remaining > 0:
            prioritized.extend(buttons[:remaining])
        
        # Add links if we still have room
        remaining = max_count - len(prioritized)
        if remaining > 0:
            prioritized.extend(links[:remaining])
        
        # Add others if we still have room
        remaining = max_count - len(prioritized)
        if remaining > 0:
            prioritized.extend(others[:remaining])
        
        return prioritized[:max_count]  # Ensure we don't exceed max_count
    
    def _create_basic_enriched_element(self, elem: Any) -> EnrichedElement:
        """
        Create a basic enriched element without LLM analysis
        For simple pages with < 5 interactive elements
        """
        # Determine functional purpose based on element type
        functional_purpose = "unknown"
        if elem.tag_name.lower() == 'button':
            functional_purpose = "trigger_action"
        elif elem.tag_name.lower() == 'a':
            functional_purpose = "navigate"
        elif elem.tag_name.lower() in ['input', 'textarea']:
            functional_purpose = "input_data"
        elif elem.tag_name.lower() == 'select':
            functional_purpose = "select_option"
        
        # Create basic context
        context = ElementContext(
            semantic_role=functional_purpose,
            parent_hierarchy=[],
            siblings_count=0,
            position_in_parent=0
        )
        
        # Convert element to dict format for base_element
        base_element_dict = {}
        if hasattr(elem, '__dict__'):
            base_element_dict = elem.__dict__.copy()
        elif hasattr(elem, 'to_dict'):
            base_element_dict = elem.to_dict()
        else:
            # Create minimal dict representation
            base_element_dict = {
                'tag_name': getattr(elem, 'tag_name', 'unknown'),
                'attributes': getattr(elem, 'attributes', {}),
                'text': getattr(elem, 'text', ''),
                'xpath': getattr(elem, 'xpath', '')
            }
        
        return EnrichedElement(
            base_element=base_element_dict,
            context=context,
            llm_analysis={
                "purpose": functional_purpose,
                "confidence": 1.0,
                "is_basic_analysis": True
            },
            test_categories=[TestCategory.FUNCTIONAL],
            test_scenarios=["Basic interaction test"],
            test_priority=TestPriority.MEDIUM,
            functional_purpose=functional_purpose,
            confidence_score=1.0
        )


# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

async def extract_and_analyze(
    url: str, config: Optional[ExtractionConfig] = None, max_elements: int = 10
) -> PageAnalysis:
    """
    Extract and analyze web elements from a URL
    
    Args:
        url: URL to analyze
        config: Optional extraction configuration
        max_elements: Maximum number of interactive elements to enrich with LLM (default: 10)
        
    Returns:
        Complete page analysis with LLM enrichment
    """
    extractor = ElementsExtractorWithLLM(config)
    return await extractor.extract_and_analyze(url, analyze_with_llm=True, max_elements=max_elements)


async def extract_without_llm(
    url: str, config: Optional[ExtractionConfig] = None
) -> PageAnalysis:
    """
    Extract elements without LLM analysis
    
    Args:
        url: URL to analyze
        config: Optional extraction configuration
        
    Returns:
        Page analysis without LLM enrichment
    """
    extractor = ElementsExtractorWithLLM(config)
    return await extractor.extract_and_analyze(url, analyze_with_llm=False)


# ==============================================================================
# MAIN EXECUTION FOR TESTING
# ==============================================================================

async def main():
    """Test the implementation"""
    print("=" * 60)
    print("ELEMENTS EXTRACTOR WITH LLM")
    print("=" * 60)
    print()
    
    test_url = "https://example.com"
    
    # Configure extraction
    config = ExtractionConfig(
        max_elements=10,
        enable_stealth=True,
        enable_shadow_dom=True,
    )
    
    try:
        # Extract and analyze
        print(f"[TEST] Analyzing: {test_url}")
        analysis = await extract_and_analyze(test_url, config)
        
        print(f"[OK] Extraction completed")
        print(f"     Total elements: {analysis.total_elements}")
        print(f"     Enriched: {len(analysis.enriched_elements)}")
        print(f"     Page type: {analysis.page_type}")
        print(f"     Framework: {analysis.framework_detected}")
        print(f"     Extraction time: {analysis.extraction_time:.1f}s")
        print(f"     LLM time: {analysis.llm_processing_time:.1f}s")
        
        # Save results
        output_file = Path("element_extraction_results.json")
        with open(output_file, 'w') as f:
            # Convert to dict for JSON serialization
            result_dict = {
                "url": analysis.url,
                "page_type": analysis.page_type,
                "framework": analysis.framework_detected,
                "total_elements": analysis.total_elements,
                "interactive_elements": analysis.interactive_elements,
                "form_elements": analysis.form_elements,
                "navigation_elements": analysis.navigation_elements,
                "insights": analysis.llm_insights,
                "timing": {
                    "extraction": analysis.extraction_time,
                    "llm": analysis.llm_processing_time
                }
            }
            json.dump(result_dict, f, indent=2)
        
        print(f"[OK] Results saved to: {output_file}")
        print()
        print("[SUCCESS] Extraction working correctly!")
        
        await asyncio.sleep(0.1)
        return 0
        
    except Exception as e:
        print(f"[ERROR] Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))