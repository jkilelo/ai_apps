"""
Test Generation with LLM
Focuses on test generation using enriched elements from elements_extractor
Uses shared utilities and types for DRY compliance
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import LLM functionality
from llm import call_default_llm

# Import shared utilities
from llm_utils import (
    LLMResponseParser,
    StrategySelector,
    LLMPromptBuilder,
    prepare_llm_messages
)

# Import shared models
from data_types import (
    TestCategory,
    TestPriority,
    TestFramework,
    GherkinStep,
    TestScenario,
    TestSuite,
    PageAnalysis,
    EnrichedElement,
    TestGenerationContract,
    TestGenerationResult,
    BrowserExtractionConfig as ExtractionConfig
)

# Import element extraction
from elements_extractor_with_llm import extract_and_analyze


class TestGenerationEngine:
    """
    Main test generation engine
    Generates tests from enriched elements - follows single responsibility
    """
    
    def __init__(self):
        """Initialize the test generation engine"""
        self.parser = LLMResponseParser()
        self.strategy_selector = StrategySelector()
        self.prompt_builder = LLMPromptBuilder()
        logger.info("Initialized TestGenerationEngine with shared utilities")
    
    async def generate_test_scenarios(
        self,
        page_analysis: PageAnalysis,
        categories: List[TestCategory],
        max_per_category: int = 5
    ) -> List[TestScenario]:
        """
        Generate test scenarios for given categories
        
        Args:
            page_analysis: Page analysis with enriched elements
            categories: Test categories to generate
            max_per_category: Maximum scenarios per category
            
        Returns:
            List of test scenarios
        """
        # Optimization: For simple pages, generate basic scenarios without LLM
        if page_analysis.interactive_elements < 5:
            return self._generate_basic_scenarios(page_analysis, categories)
        
        # For functional tests only, batch all in one LLM call
        if len(categories) == 1 and categories[0] == TestCategory.FUNCTIONAL:
            return await self._generate_all_functional_scenarios(
                page_analysis, max_per_category
            )
        
        # Original behavior for multiple categories
        all_scenarios = []
        for category in categories:
            scenarios = await self._generate_category_scenarios(
                page_analysis, category, max_per_category
            )
            all_scenarios.extend(scenarios)
        
        return all_scenarios
    
    async def _generate_category_scenarios(
        self,
        page_analysis: PageAnalysis,
        category: TestCategory,
        max_scenarios: int
    ) -> List[TestScenario]:
        """
        Generate scenarios for a specific category
        
        Args:
            page_analysis: Page analysis data
            category: Test category
            max_scenarios: Maximum number of scenarios
            
        Returns:
            List of test scenarios for the category
        """
        # Prepare context
        elements_summary = self._summarize_page_elements(page_analysis)
        
        # Build prompt using shared utility
        expected_structure = {
            "name": "scenario name",
            "description": "detailed description",
            "priority": "critical|high|medium|low",
            "steps": [
                {"keyword": "Given", "text": "step text"},
                {"keyword": "When", "text": "step text"},
                {"keyword": "Then", "text": "step text"}
            ],
            "test_data": {"key": "value"},
            "expected_results": ["result 1", "result 2"],
            "tags": ["tag1", "tag2"],
            "confidence_score": 0.95
        }
        
        prompt = self.prompt_builder.build_json_prompt(
            task_description=f"Generate {max_scenarios} detailed test scenarios for {category.value if isinstance(category, TestCategory) else str(category)} testing.",
            context={
                "url": page_analysis.url,
                "page_type": page_analysis.page_type,
                "framework": page_analysis.framework_detected or "Unknown",
                "elements_summary": elements_summary,
                "focus": f"Focus specifically on {category.value if isinstance(category, TestCategory) else str(category)} testing aspects"
            },
            expected_structure=[expected_structure]  # Array of structures
        )
        
        # Get strategy and prepare messages
        strategy = self.strategy_selector.get_strategy("scenario_generation")
        messages = prepare_llm_messages(prompt, strategy=strategy)
        
        # Call LLM
        response = call_default_llm(messages)
        
        # Parse response using shared parser
        scenario_data = self.parser.parse_json_array(response.content, strict=False)
        
        # Convert to TestScenario objects
        scenarios = []
        for data in scenario_data:
            try:
                steps = [
                    GherkinStep(keyword=step["keyword"], text=step["text"])
                    for step in data.get("steps", [])
                ]
                
                scenario = TestScenario(
                    name=data["name"],
                    description=data.get("description", ""),
                    category=category,
                    priority=TestPriority(data.get("priority", "medium")),
                    steps=steps,
                    test_data=data.get("test_data", {}),
                    expected_results=data.get("expected_results", []),
                    tags=data.get("tags", []),
                    confidence_score=data.get("confidence_score", 0.95)
                )
                scenarios.append(scenario)
            except (KeyError, ValueError) as e:
                logger.warning(f"Skipping invalid scenario: {e}")
                continue
        
        return scenarios
    
    def _summarize_page_elements(self, page_analysis: PageAnalysis) -> Dict[str, Any]:
        """
        Summarize page elements for LLM context
        
        Args:
            page_analysis: Page analysis data
            
        Returns:
            Summary dictionary
        """
        summary = {
            "total_elements": page_analysis.total_elements,
            "interactive_elements": page_analysis.interactive_elements,
            "form_elements": page_analysis.form_elements,
            "navigation_elements": page_analysis.navigation_elements,
            "element_types": [],
            "key_features": []
        }
        
        # Analyze enriched elements if available
        if page_analysis.enriched_elements:
            element_types = set()
            high_interaction = []
            
            for element in page_analysis.enriched_elements[:20]:  # Limit for context
                elem_data = element.base_element
                element_types.add(elem_data.get("tag_name", "unknown"))
                
                if element.context.interaction_likelihood > 0.7:
                    high_interaction.append(elem_data.get("tag_name"))
            
            summary["element_types"] = list(element_types)
            summary["high_interaction_elements"] = high_interaction
        
        return summary
    
    async def generate_qa_test_plan(
        self,
        page_analysis: PageAnalysis,
        categories: Optional[List[TestCategory]] = None
    ) -> Dict[str, List[str]]:
        """
        Generate comprehensive QA test plan
        
        Args:
            page_analysis: Page analysis with enriched elements
            categories: Optional specific categories to focus on
            
        Returns:
            QA test plan organized by category
        """
        # Use provided categories or default set
        if not categories:
            categories = [
                TestCategory.FUNCTIONAL,
                TestCategory.VALIDATION,
                TestCategory.ACCESSIBILITY,
                TestCategory.SECURITY,
                TestCategory.ERROR_HANDLING
            ]
        
        # Build prompt (handle both enum and string types)
        expected_structure = {}
        for category in categories:
            if isinstance(category, TestCategory):
                expected_structure[category.value] = ["test case 1", "test case 2", "..."]
            else:
                expected_structure[str(category)] = ["test case 1", "test case 2", "..."]
        
        context = {
            "url": page_analysis.url,
            "page_type": page_analysis.page_type,
            "total_elements": page_analysis.total_elements,
            "interactive_elements": page_analysis.interactive_elements,
            "form_elements": page_analysis.form_elements
        }
        
        prompt = self.prompt_builder.build_json_prompt(
            task_description="Generate a comprehensive QA test plan for this web page.",
            context=context,
            expected_structure=expected_structure
        )
        
        # Get strategy and call LLM
        strategy = self.strategy_selector.get_strategy("qa_generation")
        messages = prepare_llm_messages(prompt, strategy=strategy)
        response = call_default_llm(messages)
        
        # Parse and return
        test_plan = self.parser.parse_json_object(response.content, strict=False)
        
        # Ensure all categories have at least empty list
        for category in categories:
            cat_value = category.value if isinstance(category, TestCategory) else str(category)
            if cat_value not in test_plan:
                test_plan[cat_value] = []
        
        return test_plan
    
    async def generate_gherkin_feature(
        self,
        page_analysis: PageAnalysis,
        scenarios: List[TestScenario]
    ) -> TestSuite:
        """
        Generate complete Gherkin feature file
        
        Args:
            page_analysis: Page analysis data
            scenarios: Test scenarios to include
            
        Returns:
            Complete test suite
        """
        # Build prompt for feature generation
        expected_structure = {
            "feature_name": "concise feature name",
            "feature_description": "detailed feature description"
        }
        
        context = {
            "url": page_analysis.url,
            "page_type": page_analysis.page_type,
            "total_scenarios": len(scenarios),
            "categories": list(set(s.category.value if isinstance(s.category, TestCategory) else str(s.category) for s in scenarios))
        }
        
        prompt = self.prompt_builder.build_json_prompt(
            task_description="Generate a feature name and description for testing this page.",
            context=context,
            expected_structure=expected_structure
        )
        
        # Get strategy and call LLM
        strategy = self.strategy_selector.get_strategy("gherkin_creation")
        messages = prepare_llm_messages(prompt, strategy=strategy)
        response = call_default_llm(messages)
        
        # Parse response
        feature_data = self.parser.parse_json_object(response.content)
        
        return TestSuite(
            feature_name=feature_data.get("feature_name", "Web Page Testing"),
            feature_description=feature_data.get("feature_description", "Automated test suite"),
            url=page_analysis.url,
            scenarios=scenarios,
            total_scenarios=len(scenarios),
            generation_time=0.0  # Will be set by caller
        )
    
    async def generate_test_code(
        self,
        scenario: TestScenario,
        page_analysis: PageAnalysis,
        framework: TestFramework = TestFramework.PLAYWRIGHT
    ) -> str:
        """
        Generate executable test code for a scenario
        
        Args:
            scenario: Test scenario
            page_analysis: Page analysis data
            framework: Target test framework
            
        Returns:
            Executable test code
        """
        # Get relevant elements for the scenario
        relevant_elements = self._get_relevant_elements(
            scenario, page_analysis.enriched_elements
        )
        
        # Build prompt
        context = {
            "scenario_name": scenario.name,
            "scenario_description": scenario.description,
            "category": scenario.category.value if isinstance(scenario.category, TestCategory) else str(scenario.category),
            "url": page_analysis.url,
            "framework": framework.value,
            "steps": [{"keyword": s.keyword, "text": s.text} for s in scenario.steps],
            "relevant_elements": [
                {
                    "tag": e.base_element.get("tag_name"),
                    "selector": e.base_element.get("selector"),
                    "text": e.base_element.get("text", "")[:50]
                }
                for e in relevant_elements[:5]
            ]
        }
        
        prompt = f"""Generate executable {framework.value} test code for this scenario:

{json.dumps(context, indent=2)}

Generate complete, executable code that:
1. Navigates to the URL
2. Performs all test steps
3. Includes assertions
4. Handles errors gracefully

Return ONLY the code, no explanations."""
        
        # Get strategy and call LLM
        strategy = self.strategy_selector.get_strategy("test_scenario")
        messages = prepare_llm_messages(prompt, strategy=strategy)
        response = call_default_llm(messages)
        
        # Extract code from response
        return self._extract_code(response.content)
    
    def _get_relevant_elements(
        self,
        scenario: TestScenario,
        elements: List[EnrichedElement]
    ) -> List[EnrichedElement]:
        """
        Get elements relevant to a test scenario
        
        Args:
            scenario: Test scenario
            elements: All enriched elements
            
        Returns:
            Relevant elements for the scenario
        """
        if not elements:
            return []
        
        scenario_text = f"{scenario.name} {scenario.description}".lower()
        relevant = []
        
        for element in elements:
            elem_text = str(element.base_element.get("text", "")).lower()
            elem_type = str(element.base_element.get("element_type", "")).lower()
            
            # Simple relevance check
            if any(keyword in scenario_text for keyword in [elem_text[:20], elem_type]):
                relevant.append(element)
            elif element.context.interaction_likelihood > 0.7:
                relevant.append(element)
        
        return relevant[:10]  # Return top 10 most relevant
    
    def _extract_code(self, response: str) -> str:
        """Extract code from LLM response"""
        import re
        
        # Try to find code block
        code_match = re.search(r'```(?:python|javascript|typescript)?\n(.*?)```', response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # Try to find function definition
        func_match = re.search(r'((?:async\s+)?(?:def|function|test).*?(?=\n\n|\Z))', response, re.DOTALL)
        if func_match:
            return func_match.group(1).strip()
        
        # Return as is if it looks like code
        if any(keyword in response for keyword in ['async', 'def', 'function', 'test', 'describe']):
            return response.strip()
        
        return ""
    
    def _generate_basic_scenarios(self, page_analysis: PageAnalysis, categories: List[TestCategory]) -> List[TestScenario]:
        """
        Generate basic test scenarios for simple pages without LLM
        
        Args:
            page_analysis: Page analysis data
            categories: Test categories (will focus on functional only)
            
        Returns:
            List of basic test scenarios
        """
        scenarios = []
        
        if not page_analysis.enriched_elements:
            return scenarios
        
        # For each interactive element, create a basic functional test
        for i, element in enumerate(page_analysis.enriched_elements[:3]):  # Limit to 3 scenarios
            if hasattr(element, 'original_element'):
                elem = element.original_element
                
                # Create basic scenario based on element type
                if elem.tag_name.lower() == 'button':
                    scenario = TestScenario(
                        name=f"Test Button Click {i+1}",
                        description=f"Verify button functionality",
                        category=TestCategory.FUNCTIONAL,
                        priority=TestPriority.HIGH,
                        steps=[
                            GherkinStep(keyword="Given", text=f"the user is on {page_analysis.url}"),
                            GherkinStep(keyword="When", text=f"the user clicks the button"),
                            GherkinStep(keyword="Then", text=f"the expected action should occur")
                        ]
                    )
                elif elem.tag_name.lower() == 'a':
                    scenario = TestScenario(
                        name=f"Test Link Navigation {i+1}",
                        description=f"Verify link navigation",
                        category=TestCategory.FUNCTIONAL,
                        priority=TestPriority.HIGH,
                        steps=[
                            GherkinStep(keyword="Given", text=f"the user is on {page_analysis.url}"),
                            GherkinStep(keyword="When", text=f"the user clicks the link"),
                            GherkinStep(keyword="Then", text=f"the browser should navigate to the correct page")
                        ]
                    )
                elif elem.tag_name.lower() in ['input', 'textarea']:
                    scenario = TestScenario(
                        name=f"Test Input Field {i+1}",
                        description=f"Verify input field functionality",
                        category=TestCategory.FUNCTIONAL,
                        priority=TestPriority.MEDIUM,
                        steps=[
                            GherkinStep(keyword="Given", text=f"the user is on {page_analysis.url}"),
                            GherkinStep(keyword="When", text=f"the user enters text in the input field"),
                            GherkinStep(keyword="Then", text=f"the text should be accepted and displayed")
                        ]
                    )
                else:
                    continue
                
                scenarios.append(scenario)
        
        return scenarios
    
    async def _generate_all_functional_scenarios(
        self, 
        page_analysis: PageAnalysis, 
        max_scenarios: int
    ) -> List[TestScenario]:
        """
        Generate all functional test scenarios in one LLM call (optimization)
        
        Args:
            page_analysis: Page analysis data
            max_scenarios: Maximum number of scenarios
            
        Returns:
            List of functional test scenarios
        """
        # Prepare minimal context
        elements_summary = {
            "url": page_analysis.url,
            "interactive_elements": page_analysis.interactive_elements,
            "element_types": []
        }
        
        # Add only essential element info
        if page_analysis.enriched_elements:
            for elem in page_analysis.enriched_elements[:10]:  # Limit context
                if hasattr(elem, 'original_element'):
                    elements_summary["element_types"].append(elem.original_element.tag_name)
        
        # Single prompt for all functional scenarios
        prompt = f"""Generate {max_scenarios} functional test scenarios for a page with {page_analysis.interactive_elements} interactive elements.
Focus ONLY on testing interactive functionality - clicks, inputs, navigation.
Return as JSON array with: name, description, steps (keyword, text).
Be concise and practical."""
        
        messages = prepare_llm_messages(
            f"Generate functional test scenarios: {json.dumps(elements_summary)}",
            prompt
        )
        
        response = call_default_llm(messages)
        scenarios_data = self.parser.parse_json_array(response.content)
        
        # Convert to TestScenario objects
        scenarios = []
        for data in scenarios_data[:max_scenarios]:
            steps = [
                GherkinStep(keyword=s.get("keyword", "When"), text=s.get("text", ""))
                for s in data.get("steps", [])
            ]
            
            scenario = TestScenario(
                name=data.get("name", "Test Scenario"),
                description=data.get("description", ""),
                category=TestCategory.FUNCTIONAL,
                priority=TestPriority.MEDIUM,
                steps=steps
            )
            scenarios.append(scenario)
        
        return scenarios


# ==============================================================================
# MAIN TEST GENERATION FUNCTION
# ==============================================================================

async def generate_tests_for_url(contract: TestGenerationContract) -> TestGenerationResult:
    """
    Generate comprehensive test suite for a URL
    
    Args:
        contract: Test generation configuration
        
    Returns:
        Complete test generation result
    """
    start_time = datetime.now()
    
    # Step 1: Analyze the page using element extractor
    print(f"[INFO] Analyzing page: {contract.url}")
    page_analysis = await extract_and_analyze(contract.url)
    
    # Save Step 1 results
    step1_file = Path("step1_page_analysis.json")
    with open(step1_file, 'w') as f:
        step1_data = {
            "url": page_analysis.url,
            "page_type": page_analysis.page_type,
            "total_elements": page_analysis.total_elements,
            "interactive_elements": page_analysis.interactive_elements,
            "form_elements": page_analysis.form_elements,
            "navigation_elements": page_analysis.navigation_elements,
            "framework_detected": page_analysis.framework_detected,
            "llm_insights": page_analysis.llm_insights,
            "enriched_elements_count": len(page_analysis.enriched_elements) if page_analysis.enriched_elements else 0,
            "extraction_time": page_analysis.extraction_time,
            "llm_processing_time": page_analysis.llm_processing_time
        }
        json.dump(step1_data, f, indent=2)
    print(f"[DEBUG] Saved Step 1 results to {step1_file}")
    
    analysis_time = (datetime.now() - start_time).total_seconds()
    
    # Step 2: Focus on FUNCTIONAL tests only (optimization)
    if contract.test_categories:
        # Filter to only functional tests
        categories = [c for c in contract.test_categories 
                     if (isinstance(c, TestCategory) and c == TestCategory.FUNCTIONAL) or 
                        (isinstance(c, str) and c.lower() == 'functional')]
        if not categories:
            categories = [TestCategory.FUNCTIONAL]
    else:
        # Default to functional only
        categories = [TestCategory.FUNCTIONAL]
    
    # Convert to values for display (handle both enum and string types)
    category_values = []
    for c in categories:
        if isinstance(c, TestCategory):
            category_values.append(c.value)
        else:
            category_values.append(str(c))
    
    print(f"[INFO] Generating FUNCTIONAL tests only for: {category_values}")
    
    # Optimization: Skip test generation for pages with no interactive elements
    if page_analysis.interactive_elements == 0:
        print("[INFO] No interactive elements found, skipping test generation")
        return TestGenerationResult(
            url=contract.url,
            test_suite=TestSuite(
                feature_name="Empty Page",
                feature_description="No interactive elements to test",
                scenarios=[],
                total_scenarios=0,
                generation_time=(datetime.now() - start_time).total_seconds()
            ),
            total_scenarios=0,
            categories_covered=category_values,
            generation_time=(datetime.now() - start_time).total_seconds()
        )
    
    # Step 3: Generate test scenarios (optimized for functional only)
    generator = TestGenerationEngine()
    
    # Optimization: Skip QA test plan for simple pages
    if page_analysis.interactive_elements < 5:
        print(f"[INFO] Simple page detected ({page_analysis.interactive_elements} interactive elements), using simplified generation")
        qa_test_plan = {"functional": ["Test all interactive elements"]}
    else:
        # Generate QA test plan for complex pages
        qa_test_plan = await generator.generate_qa_test_plan(page_analysis, categories)
    
    # Save Step 2 results (QA Test Plan)
    step2_file = Path("step2_qa_test_plan.json")
    with open(step2_file, 'w') as f:
        json.dump(qa_test_plan, f, indent=2)
    print(f"[DEBUG] Saved Step 2 QA test plan to {step2_file}")
    
    # Generate detailed scenarios
    scenarios = await generator.generate_test_scenarios(
        page_analysis,
        categories,
        contract.max_scenarios_per_category
    )
    
    # Save Step 3 results (Test Scenarios)
    step3_file = Path("step3_test_scenarios.json")
    with open(step3_file, 'w') as f:
        scenarios_data = []
        for scenario in scenarios:
            scenarios_data.append({
                "name": scenario.name,
                "description": scenario.description,
                "category": scenario.category.value if isinstance(scenario.category, TestCategory) else str(scenario.category),
                "priority": scenario.priority.value if hasattr(scenario, 'priority') and hasattr(scenario.priority, 'value') else "medium",
                "steps": [{"keyword": step.keyword, "text": step.text} for step in scenario.steps] if hasattr(scenario, 'steps') else []
            })
        json.dump(scenarios_data, f, indent=2)
    print(f"[DEBUG] Saved Step 3 test scenarios to {step3_file}")
    
    print(f"[INFO] Generated {len(scenarios)} test scenarios")
    
    # Step 4: Create test suite
    test_suite = await generator.generate_gherkin_feature(page_analysis, scenarios)
    
    # Save Step 4 results (Test Suite)
    step4_file = Path("step4_test_suite.json")
    with open(step4_file, 'w') as f:
        suite_data = {
            "feature_name": test_suite.feature_name if hasattr(test_suite, 'feature_name') else "Test Suite",
            "feature_description": test_suite.feature_description if hasattr(test_suite, 'feature_description') else "",
            "scenarios_count": len(test_suite.scenarios) if hasattr(test_suite, 'scenarios') else 0,
            "gherkin_content": test_suite.gherkin_content if hasattr(test_suite, 'gherkin_content') else "",
            "test_code": test_suite.test_code if hasattr(test_suite, 'test_code') else ""
        }
        json.dump(suite_data, f, indent=2)
    print(f"[DEBUG] Saved Step 4 test suite to {step4_file}")
    
    generation_time = (datetime.now() - start_time).total_seconds()
    test_suite.generation_time = generation_time
    
    # Step 5: Build result
    result = TestGenerationResult(
        url=contract.url,
        test_suite=test_suite,
        page_analysis=page_analysis,
        total_scenarios=len(scenarios),
        categories_covered=[c.value if isinstance(c, TestCategory) else str(c) for c in categories],
        generation_time=generation_time,
        llm_processing_time=generation_time - analysis_time,
        strategies_used=generator.strategy_selector.list_tasks()[:10]  # Sample of strategies
    )
    
    return result


# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

async def generate_tests(
    url: str,
    frameworks: Optional[List[str]] = None,
    categories: Optional[List[str]] = None,
    max_scenarios: int = 5
) -> TestGenerationResult:
    """
    Convenience function to generate tests for a URL
    
    Args:
        url: URL to test
        frameworks: Test frameworks to target
        categories: Test categories to include
        max_scenarios: Max scenarios per category
        
    Returns:
        Test generation result
    """
    # Convert strings to enums
    test_frameworks = []
    if frameworks:
        for fw in frameworks:
            try:
                test_frameworks.append(TestFramework(fw))
            except ValueError:
                logger.warning(f"Invalid framework: {fw}")
    
    test_categories = []
    if categories:
        for cat in categories:
            try:
                test_categories.append(TestCategory(cat))
            except ValueError:
                logger.warning(f"Invalid category: {cat}")
    
    contract = TestGenerationContract(
        url=url,
        test_frameworks=test_frameworks or [TestFramework.PLAYWRIGHT],
        test_categories=test_categories,
        max_scenarios_per_category=max_scenarios
    )
    
    return await generate_tests_for_url(contract)


async def generate_test_code_for_url(
    url: str,
    framework: str = "playwright",
    max_scenarios: int = 3
) -> Tuple[TestGenerationResult, List[str]]:
    """
    Generate test scenarios and executable code
    
    Args:
        url: URL to test
        framework: Test framework
        max_scenarios: Maximum scenarios to generate code for
        
    Returns:
        Tuple of test result and code snippets
    """
    # Generate test scenarios
    result = await generate_tests(url, frameworks=[framework], max_scenarios=1)
    
    # Generate code for scenarios
    generator = TestGenerationEngine()
    code_snippets = []
    
    for scenario in result.test_suite.scenarios[:max_scenarios]:
        code = await generator.generate_test_code(
            scenario,
            result.page_analysis,
            TestFramework(framework)
        )
        if code:
            code_snippets.append(code)
    
    return result, code_snippets


# ==============================================================================
# MAIN EXECUTION FOR TESTING
# ==============================================================================

async def main():
    """Test the implementation"""
    print("=" * 60)
    print("TEST GENERATION WITH LLM")
    print("=" * 60)
    print()
    
    test_url = "https://www.wikipedia.org"  # Simple homepage with forms and links
    
    print(f"[TEST] Generating tests for: {test_url}")
    print()
    
    try:
        # Generate comprehensive test suite - FOCUSED ON FUNCTIONAL ONLY
        result = await generate_tests(
            url=test_url,
            frameworks=["playwright"],
            categories=["functional"],  # Only functional tests as optimized
            max_scenarios=5
        )
        
        print("[OK] Test generation completed")
        print(f"     URL: {result.url}")
        print(f"     Total scenarios: {result.total_scenarios}")
        print(f"     Categories covered: {result.categories_covered}")
        print(f"     Generation time: {result.generation_time:.2f}s")
        print(f"     LLM processing: {result.llm_processing_time:.2f}s")
        print()
        
        # Display sample scenarios
        print("[OK] Sample Test Scenarios:")
        for i, scenario in enumerate(result.test_suite.scenarios[:3], 1):
            print(f"     {i}. {scenario.name} ({scenario.category})")
            print(f"        Priority: {scenario.priority}")
            print(f"        Steps: {len(scenario.steps)}")
        
        # Save Gherkin feature file
        output_file = Path("test_generation.feature")
        with open(output_file, 'w') as f:
            f.write(result.test_suite.to_gherkin())
        
        print()
        print(f"[OK] Gherkin feature saved to: {output_file}")
        
        # Save JSON results
        json_file = Path("test_generation_results.json")
        with open(json_file, 'w') as f:
            result_dict = {
                "url": result.url,
                "total_scenarios": result.total_scenarios,
                "categories_covered": result.categories_covered,
                "generation_time": result.generation_time,
                "llm_processing_time": result.llm_processing_time,
                "feature_name": result.test_suite.feature_name,
                "scenarios": [
                    {
                        "name": s.name,
                        "category": s.category,
                        "priority": s.priority,
                        "steps_count": len(s.steps),
                        "confidence": s.confidence_score
                    }
                    for s in result.test_suite.scenarios
                ]
            }
            json.dump(result_dict, f, indent=2)
        
        print(f"[OK] Results saved to: {json_file}")
        print()
        print("[SUCCESS] Test generation working correctly!")
        
        await asyncio.sleep(0.1)
        return 0
        
    except Exception as e:
        print(f"[ERROR] Test generation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))