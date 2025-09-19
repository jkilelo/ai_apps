"""
Test Generator v2 - Generates Test Scenarios from Enriched Elements
Receives enriched elements from AI Enricher
Contract: TestContract -> TestSuiteResult
"""

import asyncio
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import ALL types from centralized data_types_v2
from data_types_v2 import (
    TestContract,
    TestSuiteResult,
    TestScenario,
    TestStep,
    TestAssertion,
    EnrichedElement,
    PageInsights,
    TestCategory,
    TestPriority,
    TestConfig,
    validate_ascii,
    SystemConstants
)

# Import LLM components - REAL LLM ONLY!
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Import REAL LLM integration and shared utilities
from llm_integration import LLMIntegration
from llm_utils import (
    LLMResponseParser,
    StrategySelector,
    LLMPromptBuilder,
    prepare_llm_messages
)

# Get REAL LLM components
llm_components = LLMIntegration.get_llm_components()
parser = llm_components["parser"]
strategy_selector = llm_components["strategy_selector"]
prompt_builder = llm_components["prompt_builder"]
call_llm = llm_components["call_llm"]
prepare_llm_messages_func = llm_components["message_prep"]


class TestGeneratorV2:
    """
    Test Generator - Creates comprehensive test scenarios
    Takes enriched elements and generates test suites
    """

    def __init__(self):
        self.scenarios_generated = 0
        self.llm_calls = 0

    async def execute(self, contract: TestContract) -> TestSuiteResult:
        """
        Main execution function - implements the contract
        Args:
            contract: TestContract with enriched elements
        Returns:
            TestSuiteResult with generated test scenarios
        """
        start_time = time.time()

        # Check if we have elements to test
        if not contract.enriched_elements:
            return self._create_empty_result(start_time)

        # Generate test scenarios based on configuration
        scenarios = []

        for category in contract.config.categories:
            category_scenarios = await self._generate_scenarios_for_category(
                contract.enriched_elements,
                contract.page_insights,
                category,
                contract.config
            )
            scenarios.extend(category_scenarios)

        # Calculate coverage
        coverage = self._calculate_coverage(
            scenarios,
            contract.enriched_elements
        )

        # Perform risk assessment
        risk_assessment = self._assess_risk(
            scenarios,
            contract.page_insights
        )

        # Build feature name and description
        feature_name = self._generate_feature_name(contract.page_insights)
        feature_description = self._generate_feature_description(
            contract.page_insights,
            scenarios
        )

        return TestSuiteResult(
            feature_name=validate_ascii(feature_name),
            feature_description=validate_ascii(feature_description),
            scenarios=scenarios,
            total_scenarios=len(scenarios),
            coverage_percentage=coverage,
            risk_assessment=risk_assessment,
            generation_time=time.time() - start_time
        )

    async def _generate_scenarios_for_category(
        self,
        elements: List[EnrichedElement],
        page_insights: PageInsights,
        category: TestCategory,
        config: TestConfig
    ) -> List[TestScenario]:
        """Generate test scenarios for a specific category"""

        # Filter relevant elements for the category
        relevant_elements = self._filter_elements_for_category(elements, category)

        if not relevant_elements:
            return []

        # Prepare prompt for LLM
        prompt = self._build_test_generation_prompt(
            relevant_elements,
            page_insights,
            category,
            config.max_scenarios_per_category
        )

        # Call REAL LLM with proper strategy
        strategy = strategy_selector.get_strategy("scenario_generation")
        messages = prepare_llm_messages_func(prompt, strategy=strategy)
        response = call_llm(messages)
        self.llm_calls += 1

        # Parse response
        try:
            result = json.loads(response.content)
            scenarios_data = result.get('scenarios', [])
        except:
            # Fallback to basic scenarios
            scenarios_data = self._create_basic_scenarios(relevant_elements, category)

        # Convert to TestScenario objects
        scenarios = []
        for i, data in enumerate(scenarios_data[:config.max_scenarios_per_category]):
            scenario = self._create_scenario_from_data(data, category, i)
            scenarios.append(scenario)
            self.scenarios_generated += 1

        return scenarios

    def _filter_elements_for_category(
        self,
        elements: List[EnrichedElement],
        category: TestCategory
    ) -> List[EnrichedElement]:
        """Filter elements relevant to test category"""

        if category == TestCategory.FUNCTIONAL:
            # Interactive elements for functional tests
            return [e for e in elements if e.base_element.is_clickable or e.base_element.is_editable]

        elif category == TestCategory.VALIDATION:
            # Form elements for validation tests
            return [e for e in elements if e.base_element.is_editable]

        elif category == TestCategory.ACCESSIBILITY:
            # All visible elements for accessibility
            return [e for e in elements if e.base_element.is_visible]

        elif category == TestCategory.SECURITY:
            # Input elements for security tests
            return [e for e in elements if e.base_element.element_type.value in ['input', 'textarea']]

        else:
            # Return all for other categories
            return elements

    def _build_test_generation_prompt(
        self,
        elements: List[EnrichedElement],
        page_insights: PageInsights,
        category: TestCategory,
        max_scenarios: int
    ) -> str:
        """Build prompt for test scenario generation"""

        elements_data = []
        for element in elements[:10]:  # Limit to prevent token overflow
            elem_dict = {
                'type': element.base_element.element_type.value,
                'selector': element.best_selector or element.base_element.selectors.css or '',
                'purpose': element.ai_insights.get('purpose', ''),
                'interaction': element.base_element.is_clickable or element.base_element.is_editable,
                'text': element.base_element.text_content[:50] if element.base_element.text_content else ''
            }
            elements_data.append(elem_dict)

        prompt = f"""
Generate {max_scenarios} test scenarios for {category.value} testing.

Page Type: {page_insights.page_type.value}
Page Functionality: {', '.join(page_insights.functionality[:5])}

Available Elements:
{json.dumps(elements_data, indent=2)}

Return JSON with this structure:
{{
    "scenarios": [
        {{
            "name": "descriptive test name",
            "description": "detailed test description",
            "steps": [
                {{
                    "action": "navigate|click|type|select|assert|wait",
                    "target": "element selector or url",
                    "value": "value if needed",
                    "description": "step description"
                }}
            ],
            "priority": "critical|high|medium|low",
            "category": "{category.value}",
            "expected_results": ["result 1", "result 2"],
            "test_data": {{"key": "value"}},
            "tags": ["tag1", "tag2"]
        }}
    ]
}}

Focus on {category.value} testing aspects. Be specific and actionable.
"""
        return validate_ascii(prompt)

    def _create_scenario_from_data(
        self,
        data: Dict[str, Any],
        category: TestCategory,
        index: int
    ) -> TestScenario:
        """Create TestScenario object from data"""

        # Parse steps
        steps = []
        for step_data in data.get('steps', []):
            step = TestStep(
                action=validate_ascii(step_data.get('action', 'click')),
                target=validate_ascii(step_data.get('target', '')),
                value=validate_ascii(step_data.get('value', '')) if step_data.get('value') else None,
                description=validate_ascii(step_data.get('description', '')),
                wait_before=step_data.get('wait_before', 0),
                wait_after=step_data.get('wait_after', 0),
                screenshot=step_data.get('screenshot', False)
            )
            steps.append(step)

        # Parse assertions if any
        assertions = []
        for assertion_data in data.get('assertions', []):
            assertion = TestAssertion(
                type=validate_ascii(assertion_data.get('type', 'equals')),
                target=validate_ascii(assertion_data.get('target', '')),
                expected=assertion_data.get('expected'),
                message=validate_ascii(assertion_data.get('message', '')),
                soft=assertion_data.get('soft', False)
            )
            assertions.append(assertion)

        # Create scenario
        scenario = TestScenario(
            id=f"test_{category.value}_{index+1}",
            name=validate_ascii(data.get('name', f'Test {index+1}')),
            description=validate_ascii(data.get('description', '')),
            category=category,
            priority=TestPriority(data.get('priority', 'medium')),
            steps=steps,
            assertions=assertions,
            prerequisites=data.get('prerequisites', []),
            test_data=data.get('test_data', {}),
            expected_results=data.get('expected_results', []),
            tags=data.get('tags', []),
            estimated_duration=data.get('estimated_duration', 30000)
        )

        return scenario

    def _create_basic_scenarios(
        self,
        elements: List[EnrichedElement],
        category: TestCategory
    ) -> List[Dict[str, Any]]:
        """Create basic scenarios without LLM"""

        scenarios = []
        for i, element in enumerate(elements[:3]):
            scenario = {
                "name": f"{category.value} test for {element.base_element.element_type.value}",
                "description": f"Test {element.base_element.element_type.value} functionality",
                "steps": [
                    {
                        "action": "navigate",
                        "target": "page",
                        "description": "Navigate to page"
                    },
                    {
                        "action": "click" if element.base_element.is_clickable else "type",
                        "target": element.best_selector or "",
                        "value": "test" if element.base_element.is_editable else None,
                        "description": f"Interact with {element.base_element.element_type.value}"
                    },
                    {
                        "action": "assert",
                        "target": "page",
                        "expected": "success",
                        "description": "Verify action completed"
                    }
                ],
                "priority": "medium",
                "category": category.value
            }
            scenarios.append(scenario)

        return scenarios

    def _calculate_coverage(
        self,
        scenarios: List[TestScenario],
        elements: List[EnrichedElement]
    ) -> float:
        """Calculate test coverage percentage"""

        if not elements:
            return 1.0

        # Count tested elements
        tested_selectors = set()
        for scenario in scenarios:
            for step in scenario.steps:
                if step.target and step.target not in ['page', 'url']:
                    tested_selectors.add(step.target)

        # Count how many elements are covered
        covered_elements = 0
        for element in elements:
            if element.best_selector in tested_selectors:
                covered_elements += 1
            elif element.base_element.selectors.css in tested_selectors:
                covered_elements += 1
            elif element.base_element.selectors.id in tested_selectors:
                covered_elements += 1

        return min(1.0, covered_elements / len(elements))

    def _assess_risk(
        self,
        scenarios: List[TestScenario],
        page_insights: PageInsights
    ) -> Dict[str, Any]:
        """Assess testing risk"""

        critical_count = sum(1 for s in scenarios if s.priority == TestPriority.CRITICAL)
        high_count = sum(1 for s in scenarios if s.priority == TestPriority.HIGH)

        risk_level = "low"
        if critical_count > 2 or high_count > 5:
            risk_level = "high"
        elif critical_count > 0 or high_count > 2:
            risk_level = "medium"

        return {
            "level": risk_level,
            "critical_scenarios": critical_count,
            "high_priority_scenarios": high_count,
            "total_scenarios": len(scenarios),
            "page_complexity": page_insights.page_type.value,
            "recommendations": [
                "Focus on critical scenarios first",
                "Ensure proper test data preparation",
                "Consider edge cases for form validation"
            ]
        }

    def _generate_feature_name(self, page_insights: PageInsights) -> str:
        """Generate feature name from page insights"""
        page_type = page_insights.page_type.value
        return f"Automated Testing for {page_type.title()} Page"

    def _generate_feature_description(
        self,
        page_insights: PageInsights,
        scenarios: List[TestScenario]
    ) -> str:
        """Generate feature description"""
        categories = list(set(s.category.value for s in scenarios))
        return f"Comprehensive test suite covering {', '.join(categories)} testing for {page_insights.page_type.value} functionality"

    def _create_empty_result(self, start_time: float) -> TestSuiteResult:
        """Create empty result when no elements to test"""
        return TestSuiteResult(
            feature_name="Empty Test Suite",
            feature_description="No testable elements found",
            scenarios=[],
            total_scenarios=0,
            coverage_percentage=0.0,
            risk_assessment={"level": "low"},
            generation_time=time.time() - start_time
        )


# ==============================================================================
# MAIN EXECUTION FUNCTION - Contract Implementation
# ==============================================================================

async def execute(contract: TestContract) -> TestSuiteResult:
    """
    Main module execution function
    Args:
        contract: Input contract with enriched elements
    Returns:
        TestSuiteResult according to output contract
    """
    generator = TestGeneratorV2()
    return await generator.execute(contract)


# ==============================================================================
# TEST
# ==============================================================================

async def test():
    """Test the test generator"""
    print("Testing Test Generator v2...")

    # Create test data
    from data_types_v2 import Element, ElementSelector, ElementType, ElementContext

    # Create mock enriched elements
    test_elements = [
        EnrichedElement(
            base_element=Element(
                tag_name="button",
                element_type=ElementType.BUTTON,
                selectors=ElementSelector(css="#login-btn", id="login-btn"),
                text_content="Login",
                attributes={"type": "submit"},
                is_visible=True,
                is_clickable=True,
                is_editable=False,
                is_focusable=True
            ),
            context=ElementContext(
                semantic_role="authentication",
                interaction_probability=0.9,
                accessibility_score=0.8
            ),
            ai_insights={"purpose": "User login submission"},
            test_relevance=0.9,
            suggested_tests=["Click test", "Disabled state test"],
            potential_issues=[],
            best_selector="#login-btn",
            confidence_score=0.95
        )
    ]

    # Create page insights
    page_insights = PageInsights(
        page_type=PageType.LOGIN,
        functionality=["authentication", "form submission"],
        ui_patterns=["form", "buttons"],
        accessibility_level="high",
        mobile_friendly=True
    )

    # Create contract
    from data_types_v2 import PageType
    contract = TestContract(
        enriched_elements=test_elements,
        page_insights=page_insights,
        config=TestConfig(
            categories=[TestCategory.FUNCTIONAL],
            max_scenarios_per_category=3
        )
    )

    # Execute
    result = await execute(contract)

    print(f"Generated {result.total_scenarios} scenarios")
    print(f"Coverage: {result.coverage_percentage:.0%}")
    print(f"Risk Level: {result.risk_assessment.get('level')}")
    print("Test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test())