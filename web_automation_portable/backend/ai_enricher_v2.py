"""
AI Enricher v2 - LLM Enrichment with Caching
Receives elements from Element Extractor
Contract: EnrichContract -> EnrichedResult
"""

import asyncio
import json
import time
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import ALL types from centralized data_types_v2
from data_types_v2 import (
    EnrichContract,
    EnrichedResult,
    Element,
    EnrichedElement,
    ElementContext,
    PageInsights,
    PageType,
    LLMConfig,
    validate_ascii,
    SystemConstants
)

# Import LLM components - REAL LLM, NO MOCKS!
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Import REAL LLM integration
from llm_integration import LLMIntegration

# Get REAL LLM components
llm_components = LLMIntegration.get_llm_components()
parser = llm_components["parser"]
strategy_selector = llm_components["strategy_selector"]
prompt_builder = llm_components["prompt_builder"]
call_llm = llm_components["call_llm"]
prepare_llm_messages = llm_components["message_prep"]


class LLMCache:
    """Simple in-memory cache for LLM responses"""

    def __init__(self, ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl

    def _get_key(self, data: Any) -> str:
        """Generate cache key from data"""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(json_str.encode()).hexdigest()

    def get(self, data: Any) -> Optional[Any]:
        """Get cached response if available"""
        key = self._get_key(data)
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['response']
            else:
                del self.cache[key]
        return None

    def set(self, data: Any, response: Any) -> None:
        """Store response in cache"""
        key = self._get_key(data)
        self.cache[key] = {
            'response': response,
            'timestamp': time.time()
        }


class AIEnricherV2:
    """
    AI Enricher with intelligent caching and batch processing
    Takes elements and enriches them with LLM insights
    """

    def __init__(self):
        self.cache = LLMCache()
        self.cache_hits = 0
        self.llm_calls = 0

    async def execute(self, contract: EnrichContract) -> EnrichedResult:
        """
        Main execution function - implements the contract
        Args:
            contract: EnrichContract with elements to enrich
        Returns:
            EnrichedResult with enriched elements and insights
        """
        start_time = time.time()

        # Skip enrichment for simple pages
        if len(contract.elements) < SystemConstants.SIMPLE_PAGE_THRESHOLD:
            return self._create_basic_result(contract, start_time)

        # Process elements in batches
        enriched_elements = await self._enrich_elements_batch(
            contract.elements,
            contract.config
        )

        # Generate page insights
        page_insights = await self._generate_page_insights(
            contract.elements,
            contract.page_context,
            contract.config
        )

        # Calculate confidence scores
        confidence_scores = self._calculate_confidence_scores(enriched_elements)

        return EnrichedResult(
            elements=enriched_elements,
            page_insights=page_insights,
            enrichment_time=time.time() - start_time,
            llm_tokens_used=self._estimate_tokens(enriched_elements),
            cache_hits=self.cache_hits,
            confidence_scores=confidence_scores
        )

    async def _enrich_elements_batch(
        self,
        elements: List[Element],
        config: LLMConfig
    ) -> List[EnrichedElement]:
        """Process elements in batches for efficiency"""
        enriched = []
        batch_size = config.batch_size

        # Filter to interactive elements only
        interactive_elements = [
            e for e in elements
            if e.is_clickable or e.is_editable or e.is_focusable
        ]

        for i in range(0, len(interactive_elements), batch_size):
            batch = interactive_elements[i:i + batch_size]

            # Check cache first
            cache_key = self._create_batch_key(batch)
            cached_response = self.cache.get(cache_key)

            if cached_response:
                self.cache_hits += 1
                enriched_batch = cached_response
            else:
                # Call LLM for batch
                enriched_batch = await self._call_llm_for_batch(batch, config)
                self.cache.set(cache_key, enriched_batch)
                self.llm_calls += 1

            enriched.extend(enriched_batch)

        return enriched

    def _create_batch_key(self, batch: List[Element]) -> Dict[str, Any]:
        """Create a cache key for a batch of elements"""
        return {
            'elements': [
                {
                    'tag': e.tag_name,
                    'type': e.element_type.value,
                    'text': e.text_content[:50] if e.text_content else '',
                    'clickable': e.is_clickable,
                    'editable': e.is_editable
                }
                for e in batch
            ]
        }

    async def _call_llm_for_batch(
        self,
        batch: List[Element],
        config: LLMConfig
    ) -> List[EnrichedElement]:
        """Call LLM to enrich a batch of elements"""

        # Prepare prompt
        prompt = self._build_enrichment_prompt(batch)

        # Call REAL LLM with proper strategy
        strategy = strategy_selector.get_strategy("element_analysis")
        messages = prepare_llm_messages(prompt, strategy=strategy)
        response = call_llm(messages)

        # Parse response
        try:
            result = json.loads(response.content)
            elements_data = result.get('elements', [])
        except:
            # Fallback to basic enrichment
            elements_data = [self._create_basic_enrichment(e) for e in batch]

        # Convert to EnrichedElement objects
        enriched = []
        for element, data in zip(batch, elements_data):
            context = ElementContext(
                semantic_role=validate_ascii(data.get('semantic_role', 'unknown')),
                page_section='main',
                interaction_probability=data.get('interaction_probability', 0.5),
                accessibility_score=data.get('accessibility_score', 0.5),
                parent_chain=[],
                related_elements=[]
            )

            enriched_element = EnrichedElement(
                base_element=element,
                context=context,
                ai_insights=data,
                test_relevance=data.get('test_relevance', 0.5),
                suggested_tests=data.get('suggested_tests', []),
                potential_issues=data.get('potential_issues', []),
                best_selector=element.selectors.css or element.selectors.id or '',
                confidence_score=data.get('confidence', 0.8)
            )

            enriched.append(enriched_element)

        return enriched

    def _build_enrichment_prompt(self, batch: List[Element]) -> str:
        """Build prompt for element enrichment"""
        elements_data = []
        for element in batch:
            elem_dict = {
                'tag': element.tag_name,
                'type': element.element_type.value,
                'text': element.text_content[:100] if element.text_content else '',
                'attributes': dict(list(element.attributes.items())[:5]),  # Limit attributes
                'clickable': element.is_clickable,
                'editable': element.is_editable,
                'selector': element.selectors.css or element.selectors.id or ''
            }
            elements_data.append(elem_dict)

        prompt = f"""
Analyze these web elements and provide enrichment data.

Elements:
{json.dumps(elements_data, indent=2)}

Return JSON with this structure:
{{
    "elements": [
        {{
            "semantic_role": "navigation|form|content|etc",
            "interaction_probability": 0.0-1.0,
            "accessibility_score": 0.0-1.0,
            "purpose": "element purpose",
            "test_relevance": 0.0-1.0,
            "suggested_tests": ["test1", "test2"],
            "potential_issues": ["issue1"],
            "confidence": 0.0-1.0
        }}
    ]
}}
"""
        return validate_ascii(prompt)

    async def _generate_page_insights(
        self,
        elements: List[Element],
        page_context: Optional[Dict[str, Any]],
        config: LLMConfig
    ) -> PageInsights:
        """Generate overall page insights"""

        # Check cache
        cache_key = {'page_analysis': len(elements), 'types': list(set(e.element_type.value for e in elements[:20]))}
        cached = self.cache.get(cache_key)

        if cached:
            self.cache_hits += 1
            return cached

        # Prepare page summary
        page_summary = {
            'total_elements': len(elements),
            'interactive_elements': sum(1 for e in elements if e.is_clickable or e.is_editable),
            'form_elements': sum(1 for e in elements if e.element_type.value in ['input', 'select', 'textarea']),
            'navigation_elements': sum(1 for e in elements if e.element_type.value == 'navigation'),
            'element_types': list(set(e.element_type.value for e in elements))
        }

        prompt = f"""
Analyze this web page structure and provide insights.

Page Summary:
{json.dumps(page_summary, indent=2)}

Return JSON with:
{{
    "page_type": "login|dashboard|form|ecommerce|etc",
    "detected_framework": "react|vue|angular|none",
    "functionality": ["list", "of", "functions"],
    "ui_patterns": ["list", "of", "patterns"],
    "accessibility_level": "low|medium|high",
    "mobile_friendly": true/false,
    "performance_score": 0.0-1.0,
    "security_concerns": ["list"],
    "recommendations": ["list"]
}}
"""

        # Use REAL LLM with proper strategy
        strategy = strategy_selector.get_strategy("page_classification")
        messages = prepare_llm_messages(validate_ascii(prompt), strategy=strategy)
        response = call_llm(messages)
        self.llm_calls += 1

        try:
            insights_data = json.loads(response.content)
        except:
            # Fallback to defaults
            insights_data = {
                'page_type': 'unknown',
                'functionality': ['general'],
                'ui_patterns': ['standard'],
                'accessibility_level': 'medium',
                'mobile_friendly': False
            }

        insights = PageInsights(
            page_type=PageType(insights_data.get('page_type', 'unknown')),
            detected_framework=insights_data.get('detected_framework'),
            functionality=insights_data.get('functionality', []),
            ui_patterns=insights_data.get('ui_patterns', []),
            accessibility_level=insights_data.get('accessibility_level', 'medium'),
            mobile_friendly=insights_data.get('mobile_friendly', False),
            performance_score=insights_data.get('performance_score', 0.5),
            security_concerns=insights_data.get('security_concerns', []),
            recommendations=insights_data.get('recommendations', [])
        )

        self.cache.set(cache_key, insights)
        return insights

    def _create_basic_enrichment(self, element: Element) -> Dict[str, Any]:
        """Create basic enrichment without LLM"""
        return {
            'semantic_role': element.element_type.value,
            'interaction_probability': 0.8 if element.is_clickable else 0.3,
            'accessibility_score': 0.7 if element.attributes.get('aria-label') else 0.4,
            'purpose': f"{element.element_type.value} element",
            'test_relevance': 0.6,
            'suggested_tests': ['click_test'] if element.is_clickable else [],
            'potential_issues': [],
            'confidence': 0.6
        }

    def _create_basic_result(self, contract: EnrichContract, start_time: float) -> EnrichedResult:
        """Create basic result for simple pages"""
        enriched = []

        for element in contract.elements[:SystemConstants.SIMPLE_PAGE_THRESHOLD]:
            context = ElementContext(
                semantic_role=element.element_type.value,
                page_section='main',
                interaction_probability=0.5,
                accessibility_score=0.5
            )

            enriched_element = EnrichedElement(
                base_element=element,
                context=context,
                ai_insights={},
                test_relevance=0.5,
                suggested_tests=[],
                potential_issues=[],
                best_selector=element.selectors.css or '',
                confidence_score=0.7
            )
            enriched.append(enriched_element)

        page_insights = PageInsights(
            page_type=PageType.UNKNOWN,
            detected_framework=None,
            functionality=['basic'],
            ui_patterns=['simple'],
            accessibility_level='medium',
            mobile_friendly=False
        )

        return EnrichedResult(
            elements=enriched,
            page_insights=page_insights,
            enrichment_time=time.time() - start_time,
            llm_tokens_used=0,
            cache_hits=0,
            confidence_scores={'overall': 0.7}
        )

    def _calculate_confidence_scores(self, elements: List[EnrichedElement]) -> Dict[str, float]:
        """Calculate confidence scores for enrichment"""
        if not elements:
            return {'overall': 0.0}

        scores = [e.confidence_score for e in elements]
        return {
            'overall': sum(scores) / len(scores),
            'min': min(scores),
            'max': max(scores)
        }

    def _estimate_tokens(self, elements: List[EnrichedElement]) -> int:
        """Estimate tokens used for LLM calls"""
        # Rough estimation: 4 chars = 1 token
        total_chars = sum(
            len(json.dumps(e.ai_insights)) for e in elements
        )
        return total_chars // 4


# ==============================================================================
# MAIN EXECUTION FUNCTION - Contract Implementation
# ==============================================================================

async def execute(contract: EnrichContract) -> EnrichedResult:
    """
    Main module execution function
    Args:
        contract: Input contract with elements to enrich
    Returns:
        EnrichedResult according to output contract
    """
    enricher = AIEnricherV2()
    return await enricher.execute(contract)


# ==============================================================================
# TEST
# ==============================================================================

async def test():
    """Test the AI enricher"""
    print("Testing AI Enricher v2...")

    # Create test elements
    from data_types_v2 import ElementSelector

    test_elements = [
        Element(
            tag_name="button",
            element_type=ElementType.BUTTON,
            selectors=ElementSelector(css="#submit-btn", id="submit-btn"),
            text_content="Submit",
            attributes={"type": "submit"},
            is_visible=True,
            is_clickable=True,
            is_editable=False,
            is_focusable=True
        ),
        Element(
            tag_name="input",
            element_type=ElementType.INPUT,
            selectors=ElementSelector(css="#email", id="email"),
            text_content="",
            attributes={"type": "email", "placeholder": "Enter email"},
            is_visible=True,
            is_clickable=False,
            is_editable=True,
            is_focusable=True
        )
    ]

    contract = EnrichContract(
        elements=test_elements,
        config=LLMConfig(
            batch_size=10,
            cache_enabled=True
        )
    )

    result = await execute(contract)

    print(f"Enriched {len(result.elements)} elements")
    print(f"Page type: {result.page_insights.page_type}")
    print(f"Cache hits: {result.cache_hits}")
    print(f"Enrichment time: {result.enrichment_time:.2f}s")
    print("Test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test())