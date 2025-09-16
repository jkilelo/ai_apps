"""
LLM Test Generator - Integration layer between formatters and prompts
Combines extracted elements with prompt strategies to generate comprehensive tests
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from llm import Message, call_default_llm
from ..prompts_optimized import STRATEGIES, StrategyName
from ..formatters import format_output
from ..core.models import Element


class LLMTestGenerator:
    """
    Orchestrates test generation using LLM with optimized prompts
    """
    
    def __init__(self, strategy: Optional[str] = None):
        """
        Initialize with a specific strategy
        
        Args:
            strategy: Name of the prompt strategy to use 
                     (default: QA_ENGINEER_AGENT)
        """
        self.strategy_name = strategy or StrategyName.QA_ENGINEER_AGENT
        self.strategy = STRATEGIES.get(self.strategy_name.upper())
        
        if not self.strategy:
            # Fallback to QA strategy
            self.strategy = STRATEGIES["QA_ENGINEER_AGENT"]
    
    def generate_tests(self, 
                      elements: List[Element], 
                      url: str,
                      test_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Generate tests from extracted elements
        
        Args:
            elements: List of extracted UI elements
            url: URL of the page
            test_type: Type of tests to generate 
                      ('comprehensive', 'functional', 'accessibility', 'edge_cases')
        
        Returns:
            Dictionary containing generated tests and metadata
        """
        
        # Step 1: Format elements for LLM consumption
        metadata = {"url": url, "test_type": test_type}
        llm_format = format_output(elements, "llm_test", metadata)
        
        # Step 2: Build context-rich prompt
        prompt = self._build_test_generation_prompt(llm_format, test_type)
        
        # Step 3: Apply chosen strategy
        strategized_prompt = self.strategy.render(task=prompt)
        
        # Step 4: Create messages for LLM
        messages = self._create_messages(strategized_prompt, llm_format)
        
        # Step 5: Call LLM
        response = call_default_llm(messages)
        
        # Step 6: Parse and structure response
        tests = self._parse_test_response(response.content)
        
        return {
            "url": url,
            "test_type": test_type,
            "strategy_used": self.strategy_name,
            "element_count": len(elements),
            "tests": tests,
            "raw_response": response.content,
            "token_usage": response.usage
        }
    
    def _build_test_generation_prompt(self, 
                                     llm_format: Dict[str, Any], 
                                     test_type: str) -> str:
        """
        Build detailed prompt from formatted elements
        """
        
        # Extract key information
        page_type = llm_format["page_context"]["page_type"]
        total_elements = llm_format["page_context"]["total_interactive_elements"]
        
        # Build element summary
        element_summary = []
        for element_type, data in llm_format["testable_elements"].items():
            if data["count"] > 0:
                element_details = []
                for elem in data["elements"][:3]:  # First 3 examples
                    element_details.append(f"  - {elem['description']} [{elem['selector']}]")
                
                element_summary.append(
                    f"\n{element_type.upper()} ({data['count']} total):\n" + 
                    "\n".join(element_details)
                )
        
        # Test type specific instructions
        test_instructions = self._get_test_instructions(test_type)
        
        # Build complete prompt
        prompt = f"""Generate {test_type} test cases for the following web application:

URL: {llm_format['page_context']['url']}
Page Type: {page_type}
Total Interactive Elements: {total_elements}

ELEMENTS TO TEST:
{''.join(element_summary)}

TEST SCENARIOS TO COVER:
{chr(10).join(['- ' + s for s in llm_format['suggested_test_scenarios']])}

SPECIFIC REQUIREMENTS:
{test_instructions}

For each test case, provide:
1. Test Name (descriptive)
2. Test Category (functional/ui/integration/edge_case)
3. Priority (high/medium/low)
4. Preconditions
5. Test Steps (numbered)
6. Expected Results
7. Test Data (if applicable)
8. Selectors to use

Format as structured JSON for easy parsing."""
        
        return prompt
    
    def _get_test_instructions(self, test_type: str) -> str:
        """Get specific instructions based on test type"""
        
        instructions = {
            "comprehensive": """
- Cover all interactive elements
- Include positive and negative scenarios
- Test validation and error handling
- Verify accessibility requirements
- Include edge cases and boundary conditions
- Test different user flows""",
            
            "functional": """
- Focus on core functionality
- Test happy path scenarios
- Verify form submissions
- Check navigation flows
- Validate data processing""",
            
            "accessibility": """
- Verify ARIA labels and roles
- Test keyboard navigation
- Check screen reader compatibility
- Validate focus management
- Test color contrast requirements""",
            
            "edge_cases": """
- Test boundary values
- Invalid input handling
- Concurrent operations
- Network failures
- Session timeouts
- Browser compatibility"""
        }
        
        return instructions.get(test_type, instructions["comprehensive"])
    
    def _create_messages(self, 
                        strategized_prompt: str, 
                        llm_format: Dict[str, Any]) -> List[Message]:
        """
        Create message list for LLM with system context
        """
        
        # System message with QA expertise
        system_message = Message(
            role="system",
            content="""You are a Senior QA Engineer with 30+ years of experience in test automation.
You specialize in creating comprehensive, maintainable test cases that ensure software quality.
Your tests follow industry best practices and cover functional, non-functional, and edge cases.
You always provide structured, actionable test cases with clear steps and expected results."""
        )
        
        # Add context about the page
        context_message = Message(
            role="user",
            content=f"""Page Analysis Context:
{json.dumps(llm_format['page_context'], indent=2)}

Element Statistics:
- Inputs: {llm_format['testable_elements']['inputs']['count']}
- Buttons: {llm_format['testable_elements']['buttons']['count']}
- Links: {llm_format['testable_elements']['links']['count']}
- Forms: {llm_format['testable_elements']['forms']['count']}"""
        )
        
        # Main prompt with strategy
        user_message = Message(
            role="user",
            content=strategized_prompt
        )
        
        return [system_message, context_message, user_message]
    
    def _parse_test_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse LLM response into structured test cases
        """
        
        # Try to extract JSON if present
        try:
            # Look for JSON blocks in response
            import re
            json_pattern = r'```json\s*(.*?)\s*```'
            json_match = re.search(json_pattern, response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)
            
            # Try direct JSON parse
            return json.loads(response)
            
        except (json.JSONDecodeError, Exception):
            # Fallback: Parse as text and structure manually
            return self._parse_text_response(response)
    
    def _parse_text_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Fallback parser for non-JSON responses
        """
        
        tests = []
        current_test = None
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            
            # Detect new test case
            if line.startswith(('Test:', 'Test Case:', '1.', '##')):
                if current_test:
                    tests.append(current_test)
                current_test = {
                    "name": line.replace('Test:', '').replace('Test Case:', '').strip(),
                    "steps": [],
                    "expected": []
                }
            
            # Parse test components
            elif current_test:
                if 'step' in line.lower() or line[0:1].isdigit():
                    current_test["steps"].append(line)
                elif 'expect' in line.lower() or 'result' in line.lower():
                    current_test["expected"].append(line)
                elif 'priority' in line.lower():
                    current_test["priority"] = line.split(':')[-1].strip()
                elif 'category' in line.lower():
                    current_test["category"] = line.split(':')[-1].strip()
        
        # Add last test
        if current_test:
            tests.append(current_test)
        
        return tests


class TestGenerationPipeline:
    """
    Complete pipeline from extraction to test generation
    """
    
    def __init__(self):
        """Initialize pipeline components"""
        self.generators = {
            "qa": LLMTestGenerator(StrategyName.QA_ENGINEER_AGENT),
            "cot": LLMTestGenerator(StrategyName.CHAIN_OF_THOUGHT),
            "tot": LLMTestGenerator(StrategyName.TREE_OF_THOUGHTS),
            "debate": LLMTestGenerator(StrategyName.DEBATE)
        }
    
    def generate_comprehensive_tests(self, 
                                    elements: List[Element],
                                    url: str,
                                    strategies: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate tests using multiple strategies for comprehensive coverage
        
        Args:
            elements: Extracted UI elements
            url: Page URL
            strategies: List of strategies to use (default: ['qa'])
        
        Returns:
            Combined test results from all strategies
        """
        
        strategies = strategies or ["qa"]
        all_tests = {}
        
        for strategy_name in strategies:
            if strategy_name in self.generators:
                generator = self.generators[strategy_name]
                
                # Generate different test types
                for test_type in ["functional", "edge_cases", "accessibility"]:
                    key = f"{strategy_name}_{test_type}"
                    all_tests[key] = generator.generate_tests(
                        elements, url, test_type
                    )
        
        return {
            "url": url,
            "total_strategies": len(strategies),
            "test_suites": all_tests,
            "summary": self._generate_summary(all_tests)
        }
    
    def _generate_summary(self, all_tests: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics"""
        
        total_tests = 0
        test_categories = {}
        
        for suite_name, suite_data in all_tests.items():
            if "tests" in suite_data:
                total_tests += len(suite_data["tests"])
                
                for test in suite_data["tests"]:
                    category = test.get("category", "unknown")
                    test_categories[category] = test_categories.get(category, 0) + 1
        
        return {
            "total_test_cases": total_tests,
            "test_suites": len(all_tests),
            "categories": test_categories
        }


# Convenience function for simple test generation
def generate_tests_from_elements(elements: List[Element], 
                                url: str,
                                strategy: str = "qa",
                                test_type: str = "comprehensive") -> Dict[str, Any]:
    """
    Simple function to generate tests from elements
    
    Args:
        elements: List of extracted elements
        url: Page URL
        strategy: Prompt strategy to use
        test_type: Type of tests to generate
    
    Returns:
        Generated test cases
    """
    
    generator = LLMTestGenerator(strategy)
    return generator.generate_tests(elements, url, test_type)