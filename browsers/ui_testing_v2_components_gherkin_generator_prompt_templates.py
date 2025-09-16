"""
Prompt Template Manager

Manages prompt templates for different stages of Gherkin test generation.
Uses scientifically-proven prompt engineering techniques for optimal results.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PromptTemplateManager:
    """
    Manages prompt templates for Gherkin test generation.
    
    Features:
    - Stage-specific prompts (natural language → JSON → Gherkin)
    - Scenario type-specific templates
    - Few-shot examples for better results
    - Dynamic template selection based on context
    """
    
    def __init__(self, config):
        self.config = config
        self.templates = self._initialize_templates()
        self.examples = self._initialize_examples()
        
        logger.info("PromptTemplateManager initialized with templates")
    
    def get_natural_language_prompt(
        self,
        element_context: Dict[str, Any],
        scenario_classifications: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> str:
        """
        Get prompt for generating natural language test descriptions.
        
        This is the first step in the two-step generation process.
        """
        template = self.templates['natural_language_generation']
        
        # Prepare context summary
        context_summary = self._create_context_summary(element_context)
        
        # Prepare scenario types
        scenario_types = self._format_scenario_classifications(scenario_classifications)
        
        # Prepare element list
        element_list = self._format_test_relevant_elements(element_context)
        
        # Include few-shot examples if enabled
        examples_text = ""
        if config.get('use_few_shot', True):
            examples_text = self._format_few_shot_examples('natural_language')
        
        # Fill template
        prompt = template.format(
            url=element_context['page_info']['url'],
            page_type=element_context['page_info']['page_type'],
            total_elements=element_context['page_info']['total_elements'],
            interactive_elements=element_context['page_info']['interactive_elements'],
            context_summary=context_summary,
            scenario_types=scenario_types,
            element_list=element_list,
            examples=examples_text,
            max_scenarios=config.get('max_scenarios_per_feature', 20),
            include_negative=config.get('include_negative_scenarios', True),
            include_edge_cases=config.get('generate_edge_cases', True)
        )
        
        return prompt
    
    def get_json_conversion_prompt(
        self,
        nl_descriptions: List[Dict[str, Any]],
        element_context: Dict[str, Any],
        config: Dict[str, Any]
    ) -> str:
        """
        Get prompt for converting natural language to JSON format.
        
        This is the second step in the two-step generation process.
        """
        template = self.templates['json_conversion']
        
        # Format natural language descriptions
        nl_text = self._format_natural_language_descriptions(nl_descriptions)
        
        # Prepare element reference
        element_reference = self._create_element_reference(element_context)
        
        # JSON schema
        json_schema = self._get_json_schema()
        
        # Examples
        examples_text = ""
        if config.get('use_few_shot', True):
            examples_text = self._format_few_shot_examples('json_conversion')
        
        prompt = template.format(
            nl_descriptions=nl_text,
            element_reference=element_reference,
            json_schema=json_schema,
            examples=examples_text,
            enable_data_tables=config.get('enable_data_tables', True),
            enable_scenario_outlines=config.get('enable_scenario_outlines', True)
        )
        
        return prompt
    
    def get_enhancement_prompt(
        self,
        scenario: Dict[str, Any],
        improvements: List[Dict[str, Any]],
        element_context: Dict[str, Any]
    ) -> str:
        """Get prompt for enhancing a scenario based on improvements."""
        template = self.templates['scenario_enhancement']
        
        # Format current scenario
        scenario_text = self._format_gherkin_scenario(scenario)
        
        # Format improvements
        improvements_text = self._format_improvements(improvements)
        
        # Context
        context_summary = self._create_context_summary(element_context)
        
        prompt = template.format(
            current_scenario=scenario_text,
            improvements=improvements_text,
            context_summary=context_summary
        )
        
        return prompt
    
    def get_specialized_prompt(
        self,
        prompt_type: str,
        **kwargs
    ) -> str:
        """Get specialized prompts for specific scenarios."""
        specialized_templates = {
            'form_testing': self._get_form_testing_prompt,
            'navigation_testing': self._get_navigation_testing_prompt,
            'authentication_testing': self._get_auth_testing_prompt,
            'search_testing': self._get_search_testing_prompt,
            'e_commerce_testing': self._get_ecommerce_testing_prompt,
            'accessibility_testing': self._get_accessibility_testing_prompt,
            'negative_testing': self._get_negative_testing_prompt
        }
        
        if prompt_type in specialized_templates:
            return specialized_templates[prompt_type](**kwargs)
        else:
            logger.warning(f"Unknown prompt type: {prompt_type}")
            return self.templates['generic_test_generation']
    
    def _initialize_templates(self) -> Dict[str, str]:
        """Initialize all prompt templates."""
        templates = {}
        
        # Natural language generation template
        templates['natural_language_generation'] = """
You are an expert QA engineer creating comprehensive test scenarios for a web application.

Page Information:
- URL: {url}
- Page Type: {page_type}
- Total Elements: {total_elements}
- Interactive Elements: {interactive_elements}

Page Context:
{context_summary}

Identified Test Scenario Types:
{scenario_types}

Key Test-Relevant Elements:
{element_list}

{examples}

Generate {max_scenarios} natural language test descriptions that cover:
1. Core functionality and happy paths
2. Form validation and data entry (if applicable)
3. Navigation and user flows
4. Error handling and edge cases (if {include_edge_cases})
5. Negative test scenarios (if {include_negative})
6. Accessibility considerations
7. Cross-browser compatibility concerns

For each test, provide:
- A clear, descriptive title
- The test objective
- The user persona/role
- Prerequisites or setup needed
- The main flow of actions
- Expected outcomes
- Any special considerations

Format your response as a numbered list with clear sections for each test.
Focus on real-world user scenarios that provide business value.
"""

        # JSON conversion template
        templates['json_conversion'] = """
Convert the following natural language test descriptions into structured JSON format.

Natural Language Descriptions:
{nl_descriptions}

Element Reference (for accurate selectors):
{element_reference}

{examples}

Convert each test into the following JSON schema:
{json_schema}

Important Guidelines:
1. Map user actions to specific elements using the element reference
2. Use precise selectors from the element reference
3. Break down complex flows into atomic steps
4. Include appropriate test data for each step
5. Mark scenarios as 'scenario_outline' if they benefit from data variation (if {enable_scenario_outlines})
6. Use data tables for scenarios with multiple data sets (if {enable_data_tables})
7. Ensure each step has a clear action type and expected result
8. Add relevant tags for test organization

Return ONLY valid JSON that matches the schema.
"""

        # Scenario enhancement template
        templates['scenario_enhancement'] = """
Enhance the following Gherkin scenario based on the suggested improvements.

Current Scenario:
{current_scenario}

Suggested Improvements:
{improvements}

Page Context:
{context_summary}

Enhance the scenario by:
1. Implementing all suggested improvements
2. Improving step clarity and precision
3. Adding missing validation steps
4. Ensuring comprehensive test coverage
5. Making steps more maintainable and reusable

Return the enhanced scenario in the same format, with improvements applied.
"""

        # Generic test generation template
        templates['generic_test_generation'] = """
Generate Gherkin test scenarios for the given context.

Context:
{context}

Requirements:
{requirements}

Generate comprehensive test scenarios following Gherkin best practices.
"""

        return templates
    
    def _initialize_examples(self) -> Dict[str, List[Dict[str, str]]]:
        """Initialize few-shot examples."""
        examples = {}
        
        # Natural language examples
        examples['natural_language'] = [
            {
                'input': "Login form with email and password fields",
                'output': """
Test 1: Successful User Login
- Title: User successfully logs in with valid credentials
- Objective: Verify that users can log in with correct email and password
- User Persona: Registered user
- Prerequisites: User has an existing account with valid credentials
- Main Flow:
  1. Navigate to the login page
  2. Enter valid email address in the email field
  3. Enter correct password in the password field
  4. Click the "Login" button
- Expected Outcomes:
  - User is redirected to dashboard/home page
  - Welcome message is displayed
  - User session is established
- Special Considerations: Test with different user roles if applicable
"""
            }
        ]
        
        # JSON conversion examples
        examples['json_conversion'] = [
            {
                'input': "Test successful user login flow",
                'output': json.dumps({
                    'title': 'Successful User Login',
                    'type': 'scenario',
                    'tags': ['authentication', 'positive', 'core_flow'],
                    'priority': 'high',
                    'confidence': 0.95,
                    'steps': [
                        {
                            'action': 'navigate',
                            'description': 'Navigate to login page',
                            'element_selector': '',
                            'test_data': {'url': '/login'}
                        },
                        {
                            'action': 'fill',
                            'description': 'Enter email address',
                            'element_selector': 'input[type="email"]',
                            'test_data': {'value': 'user@example.com'}
                        },
                        {
                            'action': 'fill',
                            'description': 'Enter password',
                            'element_selector': 'input[type="password"]',
                            'test_data': {'value': 'ValidPass123!'}
                        },
                        {
                            'action': 'click',
                            'description': 'Click login button',
                            'element_selector': 'button[type="submit"]',
                            'test_data': {}
                        },
                        {
                            'action': 'verify',
                            'description': 'Verify successful login',
                            'element_selector': '',
                            'test_data': {'url_contains': '/dashboard', 'element_visible': '.welcome-message'}
                        }
                    ]
                }, indent=2)
            }
        ]
        
        return examples
    
    def _create_context_summary(self, element_context: Dict[str, Any]) -> str:
        """Create a summary of element context for prompts."""
        summary_parts = []
        
        # Page classification
        if 'page_classification' in element_context:
            classification = element_context['page_classification']
            summary_parts.append(f"Page Classification: {classification.get('type', 'Unknown')} "
                               f"(confidence: {classification.get('confidence', 0):.2f})")
        
        # Element groups
        if 'element_groups' in element_context:
            groups = element_context['element_groups']
            group_summary = []
            for group_name, elements in groups.items():
                if elements:
                    group_summary.append(f"{group_name}: {len(elements)} elements")
            summary_parts.append(f"Element Groups: {', '.join(group_summary)}")
        
        # Interaction flows
        if 'interaction_flows' in element_context:
            flows = element_context['interaction_flows']
            flow_types = [f['type'] for f in flows]
            summary_parts.append(f"Detected Flows: {', '.join(flow_types)}")
        
        # Business patterns
        if 'business_indicators' in element_context:
            patterns = element_context['business_indicators']
            detected_patterns = [k for k, v in patterns.items() if v.get('detected', False)]
            if detected_patterns:
                summary_parts.append(f"Business Patterns: {', '.join(detected_patterns)}")
        
        # Form structures
        if 'form_structures' in element_context:
            forms = element_context['form_structures']
            if forms:
                form_summary = f"{len(forms)} forms with "
                total_fields = sum(len(f['fields']) for f in forms)
                form_summary += f"{total_fields} total fields"
                summary_parts.append(form_summary)
        
        return '\n'.join(summary_parts)
    
    def _format_scenario_classifications(
        self,
        classifications: List[Dict[str, Any]]
    ) -> str:
        """Format scenario classifications for prompt."""
        if not classifications:
            return "No specific scenario types identified."
        
        formatted = []
        for classification in classifications:
            formatted.append(
                f"- {classification['type']}: {classification['description']} "
                f"(Priority: {classification['priority']}, "
                f"Elements: {classification.get('element_count', 0)})"
            )
        
        return '\n'.join(formatted)
    
    def _format_test_relevant_elements(
        self,
        element_context: Dict[str, Any]
    ) -> str:
        """Format test-relevant elements for prompt."""
        relevant_elements = element_context.get('test_relevant_elements', [])
        
        if not relevant_elements:
            return "No specific test-relevant elements identified."
        
        formatted = []
        for i, elem in enumerate(relevant_elements[:15], 1):  # Top 15
            formatted.append(
                f"{i}. {elem['type']} - {elem['text'][:50]}... "
                f"(Selector: {elem['selector']}, "
                f"Relevance: {elem['relevance_score']:.2f})"
            )
        
        return '\n'.join(formatted)
    
    def _format_few_shot_examples(self, example_type: str) -> str:
        """Format few-shot examples for prompt."""
        if example_type not in self.examples:
            return ""
        
        examples = self.examples[example_type]
        if not examples:
            return ""
        
        formatted = ["Here are some examples to guide your response:\n"]
        
        for i, example in enumerate(examples, 1):
            formatted.append(f"Example {i}:")
            formatted.append(f"Input: {example['input']}")
            formatted.append(f"Output: {example['output']}")
            formatted.append("")
        
        return '\n'.join(formatted)
    
    def _format_natural_language_descriptions(
        self,
        nl_descriptions: List[Dict[str, Any]]
    ) -> str:
        """Format natural language descriptions."""
        formatted = []
        
        for i, desc in enumerate(nl_descriptions, 1):
            formatted.append(f"Test {i}: {desc.get('title', 'Untitled')}")
            if 'description' in desc:
                formatted.append(desc['description'])
            formatted.append("")
        
        return '\n'.join(formatted)
    
    def _create_element_reference(
        self,
        element_context: Dict[str, Any]
    ) -> str:
        """Create element reference for selector mapping."""
        reference = ["Element Reference for Selector Mapping:\n"]
        
        # Group elements by type
        element_groups = element_context.get('element_groups', {})
        
        for group_name, elements in element_groups.items():
            if not elements:
                continue
                
            reference.append(f"\n{group_name.upper()}:")
            
            for elem in elements[:10]:  # Limit per group
                reference.append(
                    f"- {elem['text'][:30]}... → {elem['selector']} "
                    f"(Type: {elem['type']}, Interactive: {elem['is_interactive']})"
                )
        
        return '\n'.join(reference)
    
    def _get_json_schema(self) -> str:
        """Get JSON schema for test scenarios."""
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Clear, descriptive scenario title"},
                "description": {"type": "string", "description": "What the scenario tests"},
                "type": {"type": "string", "enum": ["scenario", "scenario_outline"]},
                "tags": {"type": "array", "items": {"type": "string"}},
                "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "enum": ["navigate", "click", "fill", "select", "verify", "wait"]},
                            "description": {"type": "string"},
                            "element_selector": {"type": "string"},
                            "test_data": {"type": "object"}
                        }
                    }
                },
                "examples": {
                    "type": "object",
                    "description": "Data table for scenario outlines"
                }
            }
        }
        
        return json.dumps(schema, indent=2)
    
    def _format_gherkin_scenario(self, scenario: Dict[str, Any]) -> str:
        """Format a Gherkin scenario for display."""
        lines = []
        
        # Tags
        if scenario.get('tags'):
            lines.append(f"@{' @'.join(scenario['tags'])}")
        
        # Title
        scenario_type = scenario.get('type', 'Scenario')
        lines.append(f"{scenario_type.title()}: {scenario.get('title', 'Untitled')}")
        
        # Steps
        for step in scenario.get('given_steps', []):
            lines.append(f"  Given {step['text']}")
        
        for step in scenario.get('when_steps', []):
            lines.append(f"  When {step['text']}")
        
        for step in scenario.get('then_steps', []):
            lines.append(f"  Then {step['text']}")
        
        # Examples (for scenario outlines)
        if scenario.get('examples'):
            lines.append("  Examples:")
            # Format examples table
            examples = scenario['examples']
            if examples:
                # Headers
                headers = list(examples.keys())
                lines.append(f"    | {' | '.join(headers)} |")
                
                # Data rows
                num_rows = len(list(examples.values())[0]) if examples else 0
                for i in range(num_rows):
                    row = []
                    for header in headers:
                        row.append(str(examples[header][i]))
                    lines.append(f"    | {' | '.join(row)} |")
        
        return '\n'.join(lines)
    
    def _format_improvements(self, improvements: List[Dict[str, Any]]) -> str:
        """Format improvement suggestions."""
        formatted = []
        
        for imp in improvements:
            formatted.append(f"- {imp['type'].upper()}: {imp['description']}")
            if 'steps' in imp:
                for step in imp['steps']:
                    formatted.append(f"  • {step}")
        
        return '\n'.join(formatted)
    
    # Specialized prompt methods
    def _get_form_testing_prompt(self, **kwargs) -> str:
        """Get specialized prompt for form testing."""
        form_structure = kwargs.get('form_structure', {})
        
        return f"""
Generate comprehensive Gherkin scenarios for form testing.

Form Structure:
- Total Fields: {len(form_structure.get('fields', []))}
- Required Fields: {len(form_structure.get('required_fields', []))}
- Field Types: {json.dumps(form_structure.get('field_types', {}))}
- Has Validation: {form_structure.get('has_validation', False)}

Generate scenarios covering:
1. Successful form submission with valid data
2. Required field validation
3. Field format validation (email, phone, etc.)
4. Boundary testing for numeric fields
5. Special character handling
6. Form reset functionality
7. Error message verification
8. Multi-step form navigation (if applicable)

Use Scenario Outlines with Examples tables for data-driven tests.
"""
    
    def _get_navigation_testing_prompt(self, **kwargs) -> str:
        """Get specialized prompt for navigation testing."""
        navigation_structure = kwargs.get('navigation_structure', {})
        
        return f"""
Generate Gherkin scenarios for navigation testing.

Navigation Structure:
{json.dumps(navigation_structure, indent=2)}

Cover:
1. Main menu navigation
2. Breadcrumb functionality
3. Footer link validation
4. Deep linking
5. Navigation state persistence
6. Mobile menu behavior
7. Keyboard navigation
8. Back/forward button behavior
"""
    
    def _get_auth_testing_prompt(self, **kwargs) -> str:
        """Get specialized prompt for authentication testing."""
        return """
Generate comprehensive authentication test scenarios in Gherkin format.

Cover:
1. Successful login with valid credentials
2. Login failure with invalid credentials
3. Password reset flow
4. Remember me functionality
5. Session timeout handling
6. Multi-factor authentication (if applicable)
7. Social login (if applicable)
8. Account lockout after failed attempts
9. Logout functionality
10. Concurrent session handling

Include both positive and negative test cases.
"""
    
    def _get_search_testing_prompt(self, **kwargs) -> str:
        """Get specialized prompt for search testing."""
        return """
Generate Gherkin scenarios for search functionality testing.

Cover:
1. Basic search with valid queries
2. Empty search handling
3. Special character searches
4. Search suggestions/autocomplete
5. Advanced search filters
6. Search result pagination
7. No results found scenario
8. Search history (if applicable)
9. Search result sorting
10. Search performance (large result sets)

Use data tables for different search queries.
"""
    
    def _get_ecommerce_testing_prompt(self, **kwargs) -> str:
        """Get specialized prompt for e-commerce testing."""
        return """
Generate e-commerce specific Gherkin test scenarios.

Cover:
1. Product browsing and filtering
2. Add to cart functionality
3. Cart management (update quantities, remove items)
4. Checkout process
5. Payment processing
6. Order confirmation
7. Inventory management (out of stock scenarios)
8. Pricing and discount calculations
9. Shipping options
10. Guest vs registered user checkout

Focus on critical business flows and edge cases.
"""
    
    def _get_accessibility_testing_prompt(self, **kwargs) -> str:
        """Get specialized prompt for accessibility testing."""
        return """
Generate Gherkin scenarios for accessibility testing.

Cover:
1. Keyboard navigation through all interactive elements
2. Screen reader compatibility
3. Focus indicators visibility
4. Color contrast verification
5. Form label associations
6. Error message accessibility
7. ARIA attributes validation
8. Skip navigation links
9. Image alt text verification
10. Video/audio transcripts

Follow WCAG 2.1 AA guidelines.
"""
    
    def _get_negative_testing_prompt(self, **kwargs) -> str:
        """Get specialized prompt for negative testing."""
        elements = kwargs.get('elements', [])
        
        return f"""
Generate negative test scenarios in Gherkin format.

Available Elements: {len(elements)}

Cover:
1. Invalid data input in forms
2. SQL injection attempts
3. XSS attempts
4. Boundary value testing
5. Concurrent action conflicts
6. Network failure scenarios
7. Session expiration during actions
8. Invalid URL parameters
9. File upload with wrong formats
10. API rate limiting

Focus on security and robustness testing.
"""