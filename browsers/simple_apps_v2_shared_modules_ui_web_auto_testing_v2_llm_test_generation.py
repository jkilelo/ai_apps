"""
LLM-Powered Gherkin Test Generation System
Generates high-quality BDD test scenarios using live LLM (Gemini-2.5-flash)
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path
import sys
from datetime import datetime
import re

# Add simple_apps_v2 root to path for imports
simple_apps_v2_root = Path(__file__).parent.parent.parent
if str(simple_apps_v2_root) not in sys.path:
    sys.path.insert(0, str(simple_apps_v2_root))

# Import LLM functionality
from backend.shared.llm import query_llm

# Import element extraction
from shared_modules.ui_web_auto_testing_v2.element_extractor import extract_elements_from_url

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GherkinTestGenerator:
    """Generates high-quality Gherkin test scenarios using LLM"""
    
    def __init__(self, model: str = "gemini-2.5-flash"):
        """Initialize the Gherkin test generator
        
        Args:
            model: The LLM model to use for generation
        """
        self.model = model
        self.provider = "gemini"
        
    async def generate_gherkin_tests(
        self, 
        extraction_data: Dict[str, Any],
        test_categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive Gherkin test scenarios from extracted elements
        
        Args:
            extraction_data: The extracted elements and LLM analysis
            test_categories: Specific test categories to focus on
            
        Returns:
            Dictionary containing generated Gherkin features and scenarios
        """
        
        if not test_categories:
            test_categories = [
                "functional",
                "validation", 
                "edge_cases",
                "security",
                "accessibility",
                "performance"
            ]
        
        # Prepare context from extraction data
        context = self._prepare_context(extraction_data)
        
        # Generate tests for each category
        all_features = {}
        
        for category in test_categories:
            logger.info(f"Generating {category} tests...")
            feature = await self._generate_feature_for_category(
                context, 
                category,
                extraction_data.get('llm_analysis', {})
            )
            if feature:
                all_features[category] = feature
        
        # Generate comprehensive test suite
        test_suite = await self._generate_comprehensive_suite(all_features, context)
        
        return {
            "url": extraction_data.get("url"),
            "timestamp": str(datetime.now()),
            "features": all_features,
            "test_suite": test_suite,
            "statistics": self._calculate_statistics(all_features)
        }
    
    def _prepare_context(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for LLM from extraction data"""
        
        elements = extraction_data.get("elements", [])
        
        # Group elements by category
        elements_by_category = extraction_data.get("elements_by_category", {})
        
        # Extract key elements for testing
        form_inputs = []
        buttons = []
        links = []
        auth_elements = []
        
        for element in elements:
            category = element.get("category")
            tag = element.get("tag_name")
            
            if category == "form_input":
                form_inputs.append({
                    "id": element.get("id"),
                    "name": element.get("name"),
                    "type": element.get("type"),
                    "required": element.get("isRequired"),
                    "selector": element.get("cssSelector") or element.get("xpath"),
                    "description": element.get("description")
                })
            elif tag == "button" or element.get("type") == "submit":
                buttons.append({
                    "text": element.get("text") or element.get("value"),
                    "selector": element.get("cssSelector") or element.get("xpath"),
                    "description": element.get("description")
                })
            elif tag == "a":
                links.append({
                    "text": element.get("text"),
                    "href": element.get("href"),
                    "selector": element.get("cssSelector") or element.get("xpath"),
                    "description": element.get("description")
                })
            elif category == "authentication":
                auth_elements.append({
                    "type": element.get("type"),
                    "selector": element.get("cssSelector") or element.get("xpath"),
                    "description": element.get("description")
                })
        
        return {
            "url": extraction_data.get("url"),
            "total_elements": len(elements),
            "form_inputs": form_inputs,
            "buttons": buttons,
            "links": links,
            "auth_elements": auth_elements,
            "categories": list(elements_by_category.keys())
        }
    
    async def _generate_feature_for_category(
        self, 
        context: Dict[str, Any],
        category: str,
        llm_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate Gherkin feature for a specific test category"""
        
        # Build category-specific prompt
        prompt = self._build_category_prompt(context, category, llm_analysis)
        
        # Create messages for LLM
        messages = [
            {
                "role": "system", 
                "content": """You are an expert QA automation engineer specializing in BDD/Gherkin test creation.
                Generate high-quality, comprehensive Gherkin scenarios following these principles:
                1. Use clear, business-readable language
                2. Follow Given-When-Then format strictly
                3. Include both positive and negative test cases
                4. Add appropriate tags for test organization
                5. Include data tables for parameterized tests where applicable
                6. Ensure scenarios are atomic and independent
                7. Use Background for common setup steps
                8. Follow the single responsibility principle - one scenario tests one thing
                9. Make assertions specific and measurable
                10. Include scenario outlines for data-driven tests"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            # Call LLM
            response = await asyncio.to_thread(
                query_llm,
                self.provider,
                self.model,
                messages
            )
            
            if response and response.choices and response.choices[0].message.content:
                content = response.choices[0].message.content
                
                # Parse the Gherkin content
                return self._parse_gherkin_response(content, category)
            
        except Exception as e:
            logger.error(f"Failed to generate {category} tests: {e}")
            
        return None
    
    def _build_category_prompt(
        self, 
        context: Dict[str, Any], 
        category: str,
        llm_analysis: Dict[str, Any]
    ) -> str:
        """Build category-specific prompt for LLM"""
        
        base_info = f"""
Page URL: {context.get('url')}
Total Elements: {context.get('total_elements')}

Form Inputs:
{json.dumps(context.get('form_inputs', []), indent=2)}

Buttons:
{json.dumps(context.get('buttons', []), indent=2)}

Links:
{json.dumps(context.get('links', []), indent=2)}
"""
        
        category_prompts = {
            "functional": f"""
{base_info}

Critical Flows from Analysis:
{json.dumps(llm_analysis.get('critical_flows', []), indent=2)}

Generate a comprehensive Gherkin feature file for FUNCTIONAL testing.
Include scenarios for:
1. Happy path user flows
2. All critical user journeys
3. Form submissions
4. Navigation flows
5. Data entry and submission

Format as a complete .feature file with Feature description, Background (if needed), and multiple Scenarios.
Use appropriate tags like @smoke, @regression, @critical.
""",
            
            "validation": f"""
{base_info}

Validation Scenarios from Analysis:
{json.dumps(llm_analysis.get('validation_scenarios', []), indent=2)}

Generate a Gherkin feature file for VALIDATION testing.
Include scenarios for:
1. Required field validation
2. Field format validation (email, phone, etc.)
3. Length constraints
4. Pattern matching
5. Error message verification
6. Boundary value testing

Use Scenario Outlines with Examples tables for different test data.
Include tags like @validation, @boundary, @negative.
""",
            
            "edge_cases": f"""
{base_info}

Edge Cases from Analysis:
{json.dumps(llm_analysis.get('edge_cases', []), indent=2)}

Generate a Gherkin feature file for EDGE CASE testing.
Include scenarios for:
1. Special characters in inputs
2. Very long input strings
3. Empty/null values
4. Unicode characters
5. Concurrent operations
6. Browser back/forward navigation
7. Session timeout handling

Focus on unusual but valid user behaviors.
Use tags like @edge_case, @exploratory, @resilience.
""",
            
            "security": f"""
{base_info}

Security Tests from Analysis:
{json.dumps(llm_analysis.get('security_tests', []), indent=2)}

Generate a Gherkin feature file for SECURITY testing.
Include scenarios for:
1. SQL injection attempts
2. XSS (Cross-site scripting) prevention
3. CSRF protection verification
4. Authentication bypass attempts
5. Authorization checks
6. Session management
7. Input sanitization

Use tags like @security, @penetration, @vulnerability.
Note: These are defensive security tests only.
""",
            
            "accessibility": f"""
{base_info}

Accessibility Concerns from Analysis:
{json.dumps(llm_analysis.get('accessibility_concerns', []), indent=2)}

Generate a Gherkin feature file for ACCESSIBILITY testing.
Include scenarios for:
1. Keyboard navigation (Tab order)
2. Screen reader compatibility
3. ARIA labels and roles
4. Focus management
5. Color contrast verification
6. Error announcement
7. Form field associations

Follow WCAG 2.1 AA guidelines.
Use tags like @accessibility, @wcag, @a11y.
""",
            
            "performance": f"""
{base_info}

Generate a Gherkin feature file for PERFORMANCE testing.
Include scenarios for:
1. Page load time verification
2. Form submission response time
3. Search/filter response time
4. Concurrent user operations
5. Large data handling
6. Network latency simulation
7. Resource usage monitoring

Include specific performance thresholds.
Use tags like @performance, @load, @stress.
"""
        }
        
        prompt = category_prompts.get(category, category_prompts["functional"])
        prompt += """

IMPORTANT: 
- Generate ONLY the .feature file content, no explanations
- Use realistic test data
- Make selectors specific using the provided CSS selectors or element IDs
- Each scenario should be complete and executable
- Include at least 5-10 scenarios per feature
"""
        
        return prompt
    
    def _parse_gherkin_response(self, content: str, category: str) -> Dict[str, Any]:
        """Parse Gherkin content from LLM response"""
        
        # Extract feature content
        feature_match = re.search(r'Feature:.*?(?=Feature:|$)', content, re.DOTALL)
        if not feature_match:
            # Try to use the entire content if no explicit Feature found
            feature_content = content
        else:
            feature_content = feature_match.group(0)
        
        # Parse scenarios
        scenarios = []
        scenario_matches = re.findall(
            r'(Scenario(?: Outline)?:.*?)(?=Scenario|Feature:|$)', 
            feature_content, 
            re.DOTALL
        )
        
        for match in scenario_matches:
            scenario_text = match[0] if isinstance(match, tuple) else match
            
            # Extract scenario title
            title_match = re.search(r'Scenario(?: Outline)?:\s*(.+)', scenario_text)
            title = title_match.group(1).strip() if title_match else "Untitled Scenario"
            
            # Extract tags
            tags = re.findall(r'@(\w+)', scenario_text)
            
            # Extract steps
            steps = []
            for step_match in re.finditer(r'(Given|When|Then|And|But)\s+(.+)', scenario_text):
                steps.append({
                    "keyword": step_match.group(1),
                    "text": step_match.group(2).strip()
                })
            
            # Extract examples if it's a Scenario Outline
            examples = None
            examples_match = re.search(r'Examples?:\s*\n(.*?)(?=Scenario|$)', scenario_text, re.DOTALL)
            if examples_match:
                examples = examples_match.group(1).strip()
            
            scenarios.append({
                "title": title,
                "tags": tags,
                "steps": steps,
                "examples": examples,
                "is_outline": "Scenario Outline" in scenario_text
            })
        
        # Extract feature title and description
        feature_title_match = re.search(r'Feature:\s*(.+)', feature_content)
        feature_title = feature_title_match.group(1).strip() if feature_title_match else f"{category.title()} Tests"
        
        # Extract feature description (lines after Feature: before first tag or scenario)
        desc_match = re.search(r'Feature:.*?\n\s*(.+?)(?=@|Scenario|Background)', feature_content, re.DOTALL)
        feature_description = desc_match.group(1).strip() if desc_match else ""
        
        # Extract background if present
        background = None
        background_match = re.search(r'Background:(.*?)(?=Scenario|$)', feature_content, re.DOTALL)
        if background_match:
            background_steps = []
            for step_match in re.finditer(r'(Given|When|Then|And|But)\s+(.+)', background_match.group(1)):
                background_steps.append({
                    "keyword": step_match.group(1),
                    "text": step_match.group(2).strip()
                })
            background = background_steps
        
        return {
            "category": category,
            "feature_title": feature_title,
            "feature_description": feature_description,
            "background": background,
            "scenarios": scenarios,
            "raw_content": feature_content
        }
    
    async def _generate_comprehensive_suite(
        self, 
        all_features: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a comprehensive test suite summary"""
        
        # Create suite summary prompt
        features_summary = {
            category: {
                "title": feature.get("feature_title"),
                "scenarios_count": len(feature.get("scenarios", [])),
                "has_background": feature.get("background") is not None
            }
            for category, feature in all_features.items()
        }
        
        prompt = f"""
Based on these generated test features:
{json.dumps(features_summary, indent=2)}

For the page: {context.get('url')}

Create a comprehensive test suite summary including:
1. Test execution strategy (order of execution, dependencies)
2. Test data requirements
3. Environment setup requirements
4. Risk coverage assessment
5. Recommended CI/CD integration approach
6. Estimated execution time
7. Maintenance considerations

Format as JSON with these keys: 
execution_strategy, data_requirements, setup_requirements, risk_coverage, 
ci_cd_integration, estimated_time, maintenance_tips
"""
        
        messages = [
            {
                "role": "system",
                "content": "You are a QA architect designing comprehensive test strategies."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            response = await asyncio.to_thread(
                query_llm,
                self.provider,
                self.model,
                messages
            )
            
            if response and response.choices and response.choices[0].message.content:
                content = response.choices[0].message.content
                
                # Try to parse JSON from response
                try:
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                except:
                    pass
                
                return {"summary": content}
                
        except Exception as e:
            logger.error(f"Failed to generate suite summary: {e}")
            
        return {}
    
    def _calculate_statistics(self, all_features: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate test suite statistics"""
        
        total_scenarios = 0
        total_steps = 0
        scenario_outlines = 0
        tags_used = set()
        
        for category, feature in all_features.items():
            scenarios = feature.get("scenarios", [])
            total_scenarios += len(scenarios)
            
            for scenario in scenarios:
                total_steps += len(scenario.get("steps", []))
                tags_used.update(scenario.get("tags", []))
                if scenario.get("is_outline"):
                    scenario_outlines += 1
        
        return {
            "total_features": len(all_features),
            "total_scenarios": total_scenarios,
            "total_steps": total_steps,
            "scenario_outlines": scenario_outlines,
            "unique_tags": list(tags_used),
            "categories_covered": list(all_features.keys())
        }
    
    def save_feature_files(self, test_results: Dict[str, Any], output_dir: str = "."):
        """Save generated features as .feature files
        
        Args:
            test_results: The generated test results
            output_dir: Directory to save feature files
        """
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        features = test_results.get("features", {})
        
        for category, feature in features.items():
            filename = f"{category}_tests.feature"
            filepath = output_path / filename
            
            # Write the raw Gherkin content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(feature.get("raw_content", ""))
            
            logger.info(f"Saved {category} tests to {filepath}")
        
        # Save the complete test results as JSON
        results_file = output_path / "test_generation_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2)
        
        logger.info(f"Saved complete results to {results_file}")


async def generate_tests_from_url(
    url: str,
    categories: Optional[List[str]] = None,
    save_files: bool = True
) -> Dict[str, Any]:
    """Generate Gherkin tests from a URL
    
    Args:
        url: The URL to test
        categories: Test categories to generate
        save_files: Whether to save .feature files
        
    Returns:
        Generated test results
    """
    
    logger.info(f"Starting test generation for {url}")
    
    # Extract elements with LLM analysis
    logger.info("Extracting elements from page...")
    extraction_data = await extract_elements_from_url(url, analyze=True)
    
    # Generate Gherkin tests
    logger.info("Generating Gherkin tests...")
    generator = GherkinTestGenerator()
    test_results = await generator.generate_gherkin_tests(extraction_data, categories)
    
    # Save feature files if requested
    if save_files:
        generator.save_feature_files(test_results)
    
    # Print summary
    stats = test_results.get("statistics", {})
    print(f"\n[TEST GENERATION COMPLETE]")
    print(f"  Features Generated: {stats.get('total_features')}")
    print(f"  Total Scenarios: {stats.get('total_scenarios')}")
    print(f"  Total Steps: {stats.get('total_steps')}")
    print(f"  Categories: {', '.join(stats.get('categories_covered', []))}")
    
    return test_results


async def generate_from_extraction_file(
    extraction_file: str,
    categories: Optional[List[str]] = None,
    save_files: bool = True
) -> Dict[str, Any]:
    """Generate Gherkin tests from saved extraction data
    
    Args:
        extraction_file: Path to extraction JSON file
        categories: Test categories to generate
        save_files: Whether to save .feature files
        
    Returns:
        Generated test results
    """
    
    # Load extraction data
    with open(extraction_file, 'r', encoding='utf-8') as f:
        extraction_data = json.load(f)
    
    logger.info(f"Loaded extraction data from {extraction_file}")
    
    # Generate tests
    generator = GherkinTestGenerator()
    test_results = await generator.generate_gherkin_tests(extraction_data, categories)
    
    # Save feature files if requested
    if save_files:
        generator.save_feature_files(test_results)
    
    return test_results


# Example usage
if __name__ == "__main__":
    async def main():
        # Option 1: Generate from URL
        # url = "https://quotes.toscrape.com/login"
        # test_results = await generate_tests_from_url(url)
        
        # Option 2: Generate from saved extraction file
        extraction_file = "llm_extraction_output.json"
        
        # Generate specific categories or all
        categories = ["functional", "validation", "security", "accessibility"]
        
        print("[GHERKIN TEST GENERATION]")
        print("=" * 50)
        print(f"Using extraction: {extraction_file}")
        print(f"Categories: {', '.join(categories)}")
        print()
        
        test_results = await generate_from_extraction_file(
            extraction_file,
            categories=categories,
            save_files=True
        )
        
        # Display sample scenario
        if test_results.get("features"):
            first_category = list(test_results["features"].keys())[0]
            first_feature = test_results["features"][first_category]
            
            print(f"\n[SAMPLE FEATURE - {first_category.upper()}]")
            print("-" * 50)
            print(first_feature.get("raw_content", "")[:1000])
            print("...")
        
        print("\n[Files saved in current directory]")
    
    asyncio.run(main())