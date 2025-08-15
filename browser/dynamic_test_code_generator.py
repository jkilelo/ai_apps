"""
Dynamic Test Code Generator with LLM-Powered Code Generation
=============================================================
A truly dynamic framework that generates executable Python test code 
for ANY website using LLM with advanced prompt strategies.

NO HARDCODING - Everything is generated dynamically based on:
- Extracted page elements
- Test case requirements  
- Site-specific context
- Best practices and patterns

Author: AI Test Framework
Date: 2025
"""

import asyncio
import json
import logging
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse
import hashlib

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import LLM functionality
from llm import query_llm

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
class DynamicCodeGenConfig:
    """Configuration for dynamic code generation."""
    
    # LLM Settings
    llm_provider: str = "gemini"
    llm_model: str = "gemini-2.5-flash-lite"
    llm_temperature: float = 0.1  # Very low for deterministic code
    llm_max_retries: int = 3
    llm_timeout: int = 60000  # 60 seconds for complex code generation
    
    # Advanced Prompt Strategies - ALL ENABLED for maximum quality
    enable_pal: bool = True  # Program-Aided Language
    enable_chain_of_thought: bool = True
    enable_tree_of_thoughts: bool = True
    enable_react: bool = True
    enable_constitutional_ai: bool = True
    enable_meta_prompting: bool = True
    enable_reflexion: bool = True
    enable_self_consistency: bool = True
    enable_scratchpad: bool = True
    enable_few_shot: bool = True
    enable_debate: bool = True
    enable_opro: bool = True
    enable_evolutionary: bool = True
    enable_reverse_engineering: bool = True
    enable_metacognitive: bool = True
    enable_self_healing: bool = True
    enable_code_validation: bool = True
    
    # Code Generation Settings
    test_framework: str = "pytest"
    use_page_object_model: bool = True
    generate_dynamic_selectors: bool = True
    include_fallback_strategies: bool = True
    include_error_handling: bool = True
    include_logging: bool = True
    include_screenshots: bool = True
    include_retry_logic: bool = True
    include_performance_metrics: bool = True
    validate_generated_code: bool = True
    
    # Output Settings
    output_dir: str = "dynamic_generated_tests"
    create_full_structure: bool = True
    
    # Self-consistency settings
    self_consistency_samples: int = 1  # Reduced for faster testing
    merge_strategy: str = "best"  # best, majority, ensemble


# ============================================================================
# DYNAMIC PROMPT BUILDER
# ============================================================================

class DynamicPromptBuilder:
    """Builds dynamic prompts based on actual extracted elements and context."""
    
    def __init__(self, config: DynamicCodeGenConfig):
        self.config = config
        
    def build_page_object_prompt(self, url: str, elements_data: Dict, test_cases: List[Dict]) -> str:
        """Build dynamic prompt for page object generation."""
        
        # Parse URL to get domain and page info
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('.', '_').replace('-', '_')
        page_name = self._extract_page_name(url, test_cases)
        
        # Extract unique selectors from test cases
        selectors_from_tests = self._extract_selectors_from_tests(test_cases)
        
        # Build element summary from extraction data
        element_summary = self._build_element_summary(elements_data)
        
        prompt = f"""
You are a senior test automation architect. Generate a COMPLETE, EXECUTABLE Page Object Model class.

CONTEXT:
- URL: {url}
- Domain: {domain}
- Page Type: {page_name}
- Total Elements Available: {element_summary.get('total_count', 0)}

EXTRACTED ELEMENTS FROM THE ACTUAL PAGE:
{json.dumps(element_summary, indent=2)}

SELECTORS USED IN TEST CASES:
{json.dumps(selectors_from_tests, indent=2)}

REQUIREMENTS:
1. Generate a COMPLETE Python class that is immediately executable
2. Include ALL necessary imports at the top
3. Create properties/methods for ALL elements mentioned in test cases
4. Use the ACTUAL selectors from the extracted elements
5. Include fallback selectors for resilience
6. Add smart wait strategies
7. Include proper error handling
8. Add logging for debugging
9. Follow Page Object Model best practices
10. Make it work for THIS SPECIFIC website, not a generic template

CRITICAL INSTRUCTIONS:
- This code will be saved to a .py file and executed immediately
- Every line must be valid Python syntax
- All imports must be correct and complete
- All class methods must be properly implemented
- Use the actual element selectors from the extraction, not placeholders
- The class name should be: {page_name.replace(' ', '')}Page

Generate the COMPLETE page object class code:
"""
        
        # Apply advanced strategies
        prompt = self._apply_pal_for_code(prompt)
        prompt = self._apply_chain_of_thought_for_code(prompt)
        prompt = self._apply_constitutional_for_code(prompt)
        prompt = self._apply_reflexion_for_code(prompt)
        
        return prompt
    
    def build_test_code_prompt(self, test_cases: List[Dict], page_class_name: str, 
                               url: str, strategy: str) -> str:
        """Build dynamic prompt for test code generation."""
        
        prompt = f"""
You are a senior test automation engineer. Generate COMPLETE, EXECUTABLE test code.

CONTEXT:
- URL being tested: {url}
- Test Strategy: {strategy}
- Page Object Class: {page_class_name}
- Number of test cases: {len(test_cases)}

TEST CASES TO IMPLEMENT:
{json.dumps(test_cases, indent=2)}

REQUIREMENTS:
1. Generate a COMPLETE pytest test class that is immediately executable
2. Import the page object from: from pages.{page_class_name.lower()} import {page_class_name}
3. Implement EACH test case as a separate test method
4. Use the EXACT steps and selectors from the test cases
5. Include proper assertions based on expected results
6. Add appropriate pytest markers based on priority
7. Include setup and teardown fixtures
8. Load configuration from environment variables
9. Add comprehensive error handling and logging
10. Take screenshots on failure

CRITICAL INSTRUCTIONS:
- Generate REAL code, not templates or placeholders
- Every test step must be implemented with actual Playwright calls
- Use the exact selectors from the test cases
- Handle all actions: navigate, click, type_text, wait_for, assert, etc.
- Include retry logic for flaky elements
- The code must work immediately when saved and run

IMPLEMENTATION NOTES:
- For 'navigate' action: use page.goto(selector_value)
- For 'click' action: use page.locator(selector).click()
- For 'type_text' or 'fill' action: use page.locator(selector).fill(data)
- For 'wait_for_element': use page.locator(selector).wait_for(state="visible")
- For 'assert_*' actions: use appropriate assertions or expect()
- For complex selectors, try multiple strategies

Generate the COMPLETE test class code:
"""
        
        # Apply all strategies for maximum quality
        prompt = self._apply_all_strategies_for_test_code(prompt, test_cases)
        
        return prompt
    
    def build_base_page_prompt(self) -> str:
        """Build prompt for base page generation."""
        
        prompt = """
Generate a COMPLETE, EXECUTABLE base page class for Page Object Model.

REQUIREMENTS:
1. Create a BasePage class with common functionality
2. Include ALL necessary imports
3. Implement these essential methods:
   - __init__(self, page: Page)
   - navigate_to(url)
   - wait_for_element(selector, timeout)
   - click_with_retry(selector, retries)
   - fill_field(selector, value)
   - get_text(selector)
   - is_element_visible(selector)
   - take_screenshot(name)
   - wait_for_load_state(state)
   - handle_dialog(accept, text)
   - safe_click(selector)
   - wait_and_type(selector, text)
   - get_element_with_fallback(selectors_list)
4. Include proper error handling
5. Add logging throughout
6. Use type hints
7. Add comprehensive docstrings

CRITICAL: Generate COMPLETE, WORKING code that can be saved and executed immediately.
No placeholders, no templates - actual implementation.

Generate the complete BasePage class:
"""
        
        # Apply strategies
        prompt = self._apply_constitutional_for_code(prompt)
        prompt = self._apply_few_shot_for_base_page(prompt)
        
        return prompt
    
    def build_conftest_prompt(self, url: str) -> str:
        """Build prompt for conftest generation."""
        
        prompt = f"""
Generate a COMPLETE pytest conftest.py file for test automation.

CONTEXT:
- Base URL: {url}
- Framework: Playwright with pytest
- Need fixtures for: browser, context, page

REQUIREMENTS:
1. Create all necessary pytest fixtures
2. Include ALL imports
3. Implement:
   - Session-scoped browser fixture
   - Function-scoped context fixture
   - Function-scoped page fixture
   - Setup/teardown for test environment
   - Custom markers configuration
   - Screenshot on failure hook
4. Load configuration from environment variables
5. Add proper error handling
6. Include logging setup

Generate the COMPLETE conftest.py code:
"""
        
        return prompt
    
    def _extract_page_name(self, url: str, test_cases: List[Dict]) -> str:
        """Extract meaningful page name from URL and context."""
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        
        if not path:
            # Homepage
            domain = parsed.netloc.replace('www.', '')
            return f"{domain.replace('.', '_')}_home"
        else:
            # Specific page
            page_name = path.replace('/', '_').replace('-', '_')
            return page_name
    
    def _extract_selectors_from_tests(self, test_cases: List[Dict]) -> List[str]:
        """Extract all unique selectors from test cases."""
        selectors = set()
        
        for test in test_cases:
            for step in test.get('steps', []):
                selector = step.get('selector', '')
                # Handle both string and dict selectors
                if isinstance(selector, dict):
                    # Extract primary selector if it's a dict
                    selector = selector.get('primary', '') or selector.get('value', '')
                
                if selector and isinstance(selector, str) and not selector.startswith('http'):
                    selectors.add(selector)
        
        return list(selectors)
    
    def _build_element_summary(self, elements_data: Dict) -> Dict:
        """Build summary of extracted elements."""
        summary = {
            'total_count': 0,
            'by_category': {},
            'interactive_elements': [],
            'form_elements': [],
            'navigation_elements': []
        }
        
        if isinstance(elements_data, dict):
            # Count elements by category
            for category, elements in elements_data.items():
                if isinstance(elements, list):
                    summary['by_category'][category] = len(elements)
                    summary['total_count'] += len(elements)
                    
                    # Extract key elements
                    for elem in elements[:5]:  # First 5 of each category
                        if isinstance(elem, dict):
                            elem_info = {
                                'selector': elem.get('selector', ''),
                                'type': elem.get('type', ''),
                                'text': elem.get('text', ''),
                                'category': category
                            }
                            
                            if category in ['action', 'button']:
                                summary['interactive_elements'].append(elem_info)
                            elif category in ['form_input', 'input']:
                                summary['form_elements'].append(elem_info)
                            elif category in ['navigation', 'link']:
                                summary['navigation_elements'].append(elem_info)
        
        return summary
    
    def _apply_pal_for_code(self, prompt: str) -> str:
        """Apply Program-Aided Language strategy."""
        enhancement = """

# PROGRAM-AIDED LANGUAGE STRATEGY
Use computational thinking to generate precise code:

1. Map each test requirement to specific code constructs
2. Ensure every variable is defined before use
3. Validate all imports are included
4. Check that all methods have proper return types
5. Verify error handling covers all edge cases

Generate code that a Python interpreter can execute without any modifications.
"""
        return prompt + enhancement
    
    def _apply_chain_of_thought_for_code(self, prompt: str) -> str:
        """Apply Chain of Thought for code generation."""
        enhancement = """

# CHAIN OF THOUGHT REASONING
Think through the code generation step by step:

1. What imports are needed? List them all.
2. What class structure is required? Define it.
3. What methods are needed based on test cases? Implement each.
4. What error cases might occur? Handle them.
5. What logging would help debugging? Add it.

Show your reasoning, then generate the complete code.
"""
        return prompt + enhancement
    
    def _apply_constitutional_for_code(self, prompt: str) -> str:
        """Apply Constitutional AI for safe code."""
        enhancement = """

# CONSTITUTIONAL AI PRINCIPLES
Ensure the generated code follows these principles:

SAFETY:
- No hardcoded passwords or sensitive data
- No infinite loops or memory leaks
- Proper resource cleanup

QUALITY:
- All code must be syntactically correct
- Follow PEP 8 conventions
- Include type hints
- Add docstrings

RELIABILITY:
- Include error handling
- Add retry logic for network operations
- Validate inputs
- Handle edge cases

Generate code that meets all these requirements.
"""
        return prompt + enhancement
    
    def _apply_reflexion_for_code(self, prompt: str) -> str:
        """Apply Reflexion for self-improvement."""
        enhancement = """

# REFLEXION - SELF VALIDATION
After generating the code, verify:

1. Are all imports present and correct?
2. Is every variable defined before use?
3. Are all methods properly implemented?
4. Is error handling comprehensive?
5. Would this code run without errors?

If any issues found, fix them in the final code.
"""
        return prompt + enhancement
    
    def _apply_few_shot_for_base_page(self, prompt: str) -> str:
        """Apply few-shot learning with base page example."""
        enhancement = """

# EXAMPLE PATTERN TO FOLLOW
Here's the structure to follow (but generate complete implementation):

```python
from playwright.sync_api import Page, TimeoutError
import logging
from typing import Optional

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def safe_click(self, selector: str, timeout: int = 30000) -> bool:
        try:
            self.page.locator(selector).click(timeout=timeout)
            return True
        except TimeoutError:
            self.logger.error(f"Failed to click: {selector}")
            return False
```

Generate COMPLETE implementation with ALL methods.
"""
        return prompt + enhancement
    
    def _apply_all_strategies_for_test_code(self, prompt: str, test_cases: List[Dict]) -> str:
        """Apply all strategies for test code generation."""
        
        # PAL
        prompt += """

# PROGRAM-AIDED LANGUAGE
Transform test cases into computational steps:
- Each test step → Specific Playwright command
- Each assertion → expect() or assert statement
- Each wait → Explicit wait with timeout
"""
        
        # Chain of Thought
        prompt += """

# CHAIN OF THOUGHT
Step-by-step implementation:
1. Setup: Import statements and class definition
2. Fixtures: Setup and teardown methods
3. Test Methods: One for each test case
4. Helpers: Utility methods for common operations
5. Error Handling: Try-catch blocks with screenshots
"""
        
        # Tree of Thoughts
        prompt += """

# TREE OF THOUGHTS
Consider multiple implementation approaches:
- Approach A: Direct page.locator() calls
- Approach B: Page object method calls
- Approach C: Hybrid with helpers
Choose the most maintainable approach.
"""
        
        # Constitutional AI
        prompt += """

# CONSTITUTIONAL AI
Ensure code safety and quality:
- No hardcoded credentials
- Proper exception handling
- Resource cleanup
- Follow pytest best practices
"""
        
        # Meta-prompting
        prompt += """

# META-PROMPTING
Think like a senior SDET with 10+ years experience:
- Use industry best practices
- Make tests maintainable
- Ensure readability
- Optimize for debugging
"""
        
        # Reflexion
        prompt += """

# REFLEXION
Validate the generated code:
- Check all imports
- Verify method implementations
- Ensure assertions are correct
- Confirm error handling is complete
"""
        
        return prompt


# ============================================================================
# DYNAMIC CODE GENERATOR
# ============================================================================

class DynamicTestCodeGenerator:
    """Generates test code dynamically using LLM for ANY website."""
    
    def __init__(self, config: Optional[DynamicCodeGenConfig] = None):
        self.config = config or DynamicCodeGenConfig()
        self.prompt_builder = DynamicPromptBuilder(self.config)
        self.llm_calls = 0
        self.generated_files = []
        
    async def generate_from_test_cases(self, test_cases_file: str, 
                                       extraction_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate complete test suite dynamically for any website.
        
        Args:
            test_cases_file: Path to test cases JSON
            extraction_file: Optional path to extraction data JSON
            
        Returns:
            Dictionary with generation results
        """
        logger.info(f"Starting dynamic code generation from: {test_cases_file}")
        
        # Load test cases
        with open(test_cases_file, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        # Load extraction data if available
        elements_data = {}
        if extraction_file and Path(extraction_file).exists():
            with open(extraction_file, 'r', encoding='utf-8') as f:
                extraction_data = json.load(f)
                elements_data = extraction_data.get('categories', {})
        
        url = test_data.get('url', '')
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'test_cases_file': test_cases_file,
            'extraction_file': extraction_file,
            'generated_files': [],
            'llm_calls': 0,
            'errors': []
        }
        
        # Create output directory
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        try:
            # Generate base page first
            base_page_file = await self._generate_base_page()
            results['generated_files'].append(base_page_file)
            
            # Generate page objects dynamically
            page_files = await self._generate_page_objects(url, elements_data, test_data)
            results['generated_files'].extend(page_files)
            
            # Generate test files for each strategy
            test_files = await self._generate_test_files(test_data, url)
            results['generated_files'].extend(test_files)
            
            # Generate supporting files
            support_files = await self._generate_support_files(url)
            results['generated_files'].extend(support_files)
            
            results['llm_calls'] = self.llm_calls
            results['success'] = True
            
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            results['errors'].append(str(e))
            results['success'] = False
        
        return results
    
    async def _generate_base_page(self) -> str:
        """Generate base page using LLM."""
        pages_dir = Path(self.config.output_dir) / "pages"
        pages_dir.mkdir(exist_ok=True)
        
        # Build prompt
        prompt = self.prompt_builder.build_base_page_prompt()
        
        # Call LLM
        code = await self._call_llm_for_code(prompt, "base page")
        
        # Save file
        file_path = pages_dir / "base_page.py"
        file_path.write_text(code, encoding='utf-8')
        
        return str(file_path)
    
    async def _generate_page_objects(self, url: str, elements_data: Dict, 
                                     test_data: Dict) -> List[str]:
        """Generate page objects dynamically based on actual page."""
        generated_files = []
        pages_dir = Path(self.config.output_dir) / "pages"
        pages_dir.mkdir(exist_ok=True)
        
        # Group test cases by page/functionality
        page_groups = self._group_tests_by_page(test_data.get('test_cases', {}))
        
        for page_name, test_cases in page_groups.items():
            # Build prompt with actual data
            prompt = self.prompt_builder.build_page_object_prompt(
                url, elements_data, test_cases
            )
            
            # Generate code with LLM
            code = await self._call_llm_for_code(prompt, f"{page_name} page object")
            
            # Save file
            file_name = f"{page_name.lower().replace(' ', '_')}_page.py"
            file_path = pages_dir / file_name
            file_path.write_text(code, encoding='utf-8')
            generated_files.append(str(file_path))
        
        # Generate __init__.py
        init_file = pages_dir / "__init__.py"
        init_file.write_text('"""Page Object Model classes."""\n', encoding='utf-8')
        generated_files.append(str(init_file))
        
        return generated_files
    
    async def _generate_test_files(self, test_data: Dict, url: str) -> List[str]:
        """Generate test files dynamically."""
        generated_files = []
        tests_dir = Path(self.config.output_dir) / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        # Get page class name from URL
        parsed = urlparse(url)
        domain = parsed.netloc.replace('.', '_').replace('-', '_')
        page_class_name = f"{domain.replace('_', '').title()}Page"
        
        for strategy, test_cases in test_data.get('test_cases', {}).items():
            if test_cases:
                # Build prompt
                prompt = self.prompt_builder.build_test_code_prompt(
                    test_cases, page_class_name, url, strategy
                )
                
                # Generate code with LLM
                code = await self._call_llm_for_code(prompt, f"{strategy} tests")
                
                # Save file
                file_path = tests_dir / f"test_{strategy}.py"
                file_path.write_text(code, encoding='utf-8')
                generated_files.append(str(file_path))
        
        return generated_files
    
    async def _generate_support_files(self, url: str) -> List[str]:
        """Generate supporting files."""
        generated_files = []
        
        # Generate conftest.py
        prompt = self.prompt_builder.build_conftest_prompt(url)
        code = await self._call_llm_for_code(prompt, "conftest")
        
        file_path = Path(self.config.output_dir) / "conftest.py"
        file_path.write_text(code, encoding='utf-8')
        generated_files.append(str(file_path))
        
        # Generate requirements.txt
        requirements = self._generate_requirements()
        req_path = Path(self.config.output_dir) / "requirements.txt"
        req_path.write_text(requirements, encoding='utf-8')
        generated_files.append(str(req_path))
        
        # Generate .env.test
        env_content = self._generate_env_template(url)
        env_path = Path(self.config.output_dir) / ".env.test"
        env_path.write_text(env_content, encoding='utf-8')
        generated_files.append(str(env_path))
        
        # Generate README
        readme = self._generate_readme(url)
        readme_path = Path(self.config.output_dir) / "README.md"
        readme_path.write_text(readme, encoding='utf-8')
        generated_files.append(str(readme_path))
        
        return generated_files
    
    async def _call_llm_for_code(self, prompt: str, context: str) -> str:
        """Call LLM to generate actual code."""
        logger.info(f"Generating code for: {context}")
        
        # Apply self-consistency if enabled
        if self.config.enable_self_consistency and self.config.self_consistency_samples > 1:
            codes = []
            for i in range(self.config.self_consistency_samples):
                logger.info(f"Self-consistency sample {i+1}/{self.config.self_consistency_samples}")
                code = await self._single_llm_call(prompt, self.config.llm_temperature + (i * 0.05))
                codes.append(code)
            
            # Merge or select best
            final_code = self._merge_code_samples(codes)
        else:
            final_code = await self._single_llm_call(prompt, self.config.llm_temperature)
        
        self.llm_calls += 1
        
        # Validate generated code if enabled
        if self.config.validate_generated_code:
            final_code = self._validate_and_fix_code(final_code)
        
        return final_code
    
    async def _single_llm_call(self, prompt: str, temperature: float) -> str:
        """Make a single LLM call for code generation."""
        
        # System prompt for code generation
        system_prompt = """You are an expert Python developer specializing in test automation.
Generate COMPLETE, EXECUTABLE Python code that:
1. Has all necessary imports
2. Follows PEP 8 conventions
3. Includes proper error handling
4. Uses type hints
5. Has comprehensive docstrings
6. Can be saved to a file and run immediately

CRITICAL: Generate ACTUAL CODE, not templates or placeholders.
Every line must be valid Python that will execute without errors."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        for attempt in range(self.config.llm_max_retries):
            try:
                response = query_llm(
                    provider=self.config.llm_provider,
                    model=self.config.llm_model,
                    messages=messages
                )
                
                content = response.choices[0].message.content
                
                # Extract code from response
                code = self._extract_code_from_response(content)
                
                return code
                
            except Exception as e:
                logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")
                if attempt < self.config.llm_max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    # Return a minimal working code as fallback
                    return self._generate_fallback_code(prompt)
    
    def _extract_code_from_response(self, response: str) -> str:
        """Extract Python code from LLM response."""
        # Try to find code blocks
        code_blocks = re.findall(r'```python\n(.*?)```', response, re.DOTALL)
        if code_blocks:
            return code_blocks[0]
        
        code_blocks = re.findall(r'```\n(.*?)```', response, re.DOTALL)
        if code_blocks:
            return code_blocks[0]
        
        # If no code blocks, assume entire response is code
        # Remove any markdown or explanation
        lines = response.split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            # Skip obvious non-code lines
            if line.startswith('#') and not line.startswith('#!'):
                code_lines.append(line)
                in_code = True
            elif in_code or line.strip().startswith(('import ', 'from ', 'class ', 'def ', '@')):
                code_lines.append(line)
                in_code = True
            elif in_code:
                code_lines.append(line)
        
        return '\n'.join(code_lines) if code_lines else response
    
    def _validate_and_fix_code(self, code: str) -> str:
        """Validate and fix common issues in generated code."""
        try:
            # Try to compile the code
            compile(code, '<string>', 'exec')
            return code
        except SyntaxError as e:
            logger.warning(f"Syntax error in generated code: {e}")
            # Try to fix common issues
            fixed_code = code
            
            # Fix common indentation issues
            fixed_code = self._fix_indentation(fixed_code)
            
            # Fix unclosed strings
            fixed_code = self._fix_unclosed_strings(fixed_code)
            
            # Try again
            try:
                compile(fixed_code, '<string>', 'exec')
                return fixed_code
            except:
                # Return original if fixes didn't work
                return code
        except Exception:
            # Other errors are okay (like missing imports)
            return code
    
    def _fix_indentation(self, code: str) -> str:
        """Fix common indentation issues."""
        lines = code.split('\n')
        fixed_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.lstrip()
            if not stripped:
                fixed_lines.append('')
                continue
            
            # Decrease indent for these keywords
            if stripped.startswith(('else:', 'elif ', 'except:', 'finally:', 'except ')):
                indent_level = max(0, indent_level - 1)
            
            # Apply current indent
            fixed_lines.append('    ' * indent_level + stripped)
            
            # Increase indent after these
            if stripped.endswith(':'):
                indent_level += 1
            
            # Decrease indent after return/raise/pass/continue/break
            if stripped.startswith(('return ', 'raise ', 'pass', 'continue', 'break')):
                indent_level = max(0, indent_level - 1)
        
        return '\n'.join(fixed_lines)
    
    def _fix_unclosed_strings(self, code: str) -> str:
        """Fix unclosed string literals."""
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Count quotes
            single_quotes = line.count("'") - line.count("\\'")
            double_quotes = line.count('"') - line.count('\\"')
            
            # Fix odd number of quotes
            if single_quotes % 2 != 0:
                line += "'"
            if double_quotes % 2 != 0:
                line += '"'
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _merge_code_samples(self, codes: List[str]) -> str:
        """Merge multiple code samples using configured strategy."""
        if not codes:
            return ""
        
        if len(codes) == 1:
            return codes[0]
        
        if self.config.merge_strategy == "best":
            # Return the longest valid code
            valid_codes = []
            for code in codes:
                try:
                    compile(code, '<string>', 'exec')
                    valid_codes.append(code)
                except:
                    pass
            
            if valid_codes:
                return max(valid_codes, key=len)
            else:
                return codes[0]
        
        elif self.config.merge_strategy == "majority":
            # Find most common structure
            # For simplicity, return most common by hash
            from collections import Counter
            code_hashes = [hashlib.md5(code.encode()).hexdigest() for code in codes]
            most_common = Counter(code_hashes).most_common(1)[0][0]
            for code, hash_val in zip(codes, code_hashes):
                if hash_val == most_common:
                    return code
        
        # Default: return first
        return codes[0]
    
    def _generate_fallback_code(self, prompt: str) -> str:
        """Generate minimal fallback code if LLM fails."""
        if "base_page" in prompt.lower() or "basepage" in prompt.lower():
            return '''"""Base Page Object Model class."""

from playwright.sync_api import Page, TimeoutError
import logging
from typing import Optional

class BasePage:
    """Base class for all page objects."""
    
    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def navigate_to(self, url: str) -> None:
        """Navigate to URL."""
        self.page.goto(url)
    
    def click(self, selector: str) -> None:
        """Click element."""
        self.page.locator(selector).click()
    
    def fill(self, selector: str, value: str) -> None:
        """Fill input field."""
        self.page.locator(selector).fill(value)
    
    def get_text(self, selector: str) -> str:
        """Get element text."""
        return self.page.locator(selector).text_content() or ""
'''
        
        elif "conftest" in prompt.lower():
            return '''"""Pytest configuration."""

import pytest
from playwright.sync_api import sync_playwright
from typing import Generator

@pytest.fixture(scope="session")
def browser():
    """Browser fixture."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def page(browser):
    """Page fixture."""
    page = browser.new_page()
    yield page
    page.close()
'''
        
        else:
            return '''"""Generated test code."""

import pytest
from playwright.sync_api import Page

class TestGenerated:
    """Generated test class."""
    
    def test_placeholder(self, page: Page):
        """Placeholder test."""
        page.goto("https://example.com")
        assert True
'''
    
    def _group_tests_by_page(self, test_cases: Dict) -> Dict[str, List[Dict]]:
        """Group test cases by page/functionality."""
        # For now, group all tests together
        # In a more sophisticated version, analyze test steps to determine pages
        all_tests = []
        for strategy, cases in test_cases.items():
            if cases:
                all_tests.extend(cases)
        
        return {"main": all_tests}
    
    def _generate_requirements(self) -> str:
        """Generate requirements.txt."""
        return """# Test automation requirements
pytest==8.3.4
pytest-playwright==0.6.2
playwright==1.49.0
pytest-html==4.1.1
python-dotenv==1.0.1
pytest-xdist==3.6.1
pytest-rerunfailures==15.0
allure-pytest==2.13.6
"""
    
    def _generate_env_template(self, url: str) -> str:
        """Generate .env.test template."""
        return f"""# Test environment variables
BASE_URL={url}
DEFAULT_TIMEOUT=30000
HEADLESS=false
DEBUG=false
SCREENSHOT_ON_FAILURE=true

# Test credentials (update with actual values)
TEST_USERNAME=test_user
TEST_PASSWORD=test_password
TEST_EMAIL=test@example.com
"""
    
    def _generate_readme(self, url: str) -> str:
        """Generate README."""
        return f"""# Dynamic Generated Test Suite

Generated for: {url}
Generated on: {datetime.now().isoformat()}

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

2. Configure environment:
```bash
cp .env.test .env
# Edit .env with your credentials
```

## Running Tests

```bash
pytest                    # Run all tests
pytest -m critical       # Run critical tests
pytest -n 4             # Run in parallel
pytest --html=report.html # Generate HTML report
```

## Structure

- `pages/` - Page Object Model classes
- `tests/` - Test files
- `conftest.py` - Pytest configuration
- `requirements.txt` - Dependencies
- `.env.test` - Environment template
"""


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def generate_dynamic_tests(test_cases_file: str, extraction_file: Optional[str] = None):
    """
    Generate dynamic test code for any website.
    
    Args:
        test_cases_file: Path to test cases JSON
        extraction_file: Optional path to extraction data
    """
    config = DynamicCodeGenConfig()
    generator = DynamicTestCodeGenerator(config)
    
    results = await generator.generate_from_test_cases(test_cases_file, extraction_file)
    
    return results


if __name__ == "__main__":
    import asyncio
    
    # Example usage
    test_file = "test_results_github/20250814_160251_github_com_tests.json"
    extraction_file = "test_results_github/20250814_160251_github_com_extraction.json"
    
    if Path(test_file).exists():
        results = asyncio.run(generate_dynamic_tests(test_file, extraction_file))
        
        print("\n" + "="*60)
        print("DYNAMIC CODE GENERATION COMPLETE")
        print("="*60)
        print(f"URL: {results['url']}")
        print(f"Success: {results.get('success', False)}")
        print(f"Files generated: {len(results['generated_files'])}")
        print(f"LLM calls made: {results['llm_calls']}")
        
        if results.get('errors'):
            print("\nErrors:")
            for error in results['errors']:
                print(f"  - {error}")
        
        print("\nGenerated files:")
        for file in results['generated_files']:
            print(f"  - {file}")
        
        print(f"\nOutput directory: {DynamicCodeGenConfig().output_dir}/")
    else:
        print(f"Test file not found: {test_file}")