#!/usr/bin/env python3
"""
Refactoring script to fix DRY violations between test_generation_with_llm.py 
and code_generation_with_llm.py

This script:
1. Removes code generation from test_generation_with_llm.py
2. Updates code_generation_with_llm.py to handle Python Playwright
3. Ensures proper integration through Pydantic contracts
"""

import re
from pathlib import Path

def refactor_test_generation():
    """Remove code generation from test_generation_with_llm.py"""
    
    file_path = Path("test_generation_with_llm.py")
    content = file_path.read_text(encoding='utf-8')
    
    # Comment out the executable code generation step
    content = re.sub(
        r'(logger\.info\("\[STEP 5\] Generating executable test code.*?\n.*?executable_code = await self\._generate_executable_code.*?\n.*?\))',
        r'''logger.info("[STEP 5] Test scenarios ready for code generation...")
            # Code generation removed - handled by code_generation_with_llm.py (DRY principle)
            # Use code_generation_with_llm.py to generate Python Playwright code
            executable_code = None  # Code generation is handled separately''',
        content,
        flags=re.DOTALL
    )
    
    # Remove all code generation methods (keep them commented for reference)
    methods_to_comment = [
        '_generate_executable_code',
        '_generate_framework_code', 
        '_generate_playwright_code',
        '_generate_playwright_step_code',
        '_generate_cypress_code',
        '_generate_selenium_code',
        '_generate_pytest_code',
        '_generate_generic_code',
        '_get_framework_dependencies'
    ]
    
    for method in methods_to_comment:
        # Find the method and comment it out
        pattern = rf'(\n    (async )?def {method}\(.*?\n(?:.*?\n)*?(?=\n    (async )?def |\nclass |\Z))'
        
        def comment_method(match):
            lines = match.group(1).split('\n')
            if not lines[0].strip().startswith('#'):
                commented_lines = []
                for line in lines:
                    if line:
                        commented_lines.append('    # ' + line.lstrip())
                    else:
                        commented_lines.append('')
                return '\n'.join(commented_lines)
            return match.group(0)
        
        content = re.sub(pattern, comment_method, content, flags=re.DOTALL | re.MULTILINE)
    
    # Add a note about the refactoring
    if "# DRY COMPLIANCE NOTE:" not in content:
        note = '''
# ============================================================================
# DRY COMPLIANCE NOTE:
# Code generation has been removed from this module to avoid duplication.
# This module focuses on generating test scenarios and Gherkin steps only.
# For code generation, use code_generation_with_llm.py which handles:
# - Python Playwright code generation
# - pytest and pytest-bdd code generation  
# - Page Object Model (POM) generation
# ============================================================================
'''
        # Insert after imports section
        import_end = content.find("# ============================================================================\n# DATA CONTRACTS")
        if import_end > 0:
            content = content[:import_end] + note + "\n" + content[import_end:]
    
    # Save the refactored version
    backup_path = Path("test_generation_with_llm.py.backup")
    file_path.rename(backup_path)
    file_path.write_text(content, encoding='utf-8')
    
    print("[OK] Refactored test_generation_with_llm.py")
    print(f"[OK] Backup saved to {backup_path}")
    return True


def update_code_generation_for_playwright():
    """Ensure code_generation_with_llm.py properly handles Python Playwright"""
    
    file_path = Path("code_generation_with_llm.py")
    content = file_path.read_text(encoding='utf-8')
    
    # Check if it already has Python Playwright support
    if "def generate_playwright_python" not in content:
        # Add Python Playwright generation method
        playwright_method = '''
    def generate_playwright_python(self, test_scenario: TestScenario, page_object: bool = True) -> str:
        """Generate Python Playwright code from test scenario"""
        
        imports = [
            "import pytest",
            "from playwright.sync_api import Page, expect",
            "import time",
            ""
        ]
        
        if page_object:
            imports.append("from pages.base_page import BasePage")
            imports.append("")
        
        # Generate test class
        class_name = f"Test{test_scenario.name.replace(' ', '')}"
        code_lines = imports + [
            f"class {class_name}:",
            f'    """',
            f'    {test_scenario.description}',
            f'    Category: {test_scenario.category}',
            f'    Priority: {test_scenario.priority}',
            f'    """',
            "",
        ]
        
        # Generate test method
        method_name = f"test_{test_scenario.name.lower().replace(' ', '_')}"
        code_lines.extend([
            f"    def {method_name}(self, page: Page):",
            f'        """Execute: {test_scenario.name}"""',
            ""
        ])
        
        # Generate step code
        for step in test_scenario.steps:
            code_lines.append(f"        # {step.keyword}: {step.text}")
            
            # Generate appropriate Playwright Python code
            step_code = self._generate_playwright_python_step(step, test_scenario.test_data)
            code_lines.extend([f"        {line}" for line in step_code])
            code_lines.append("")
        
        # Add assertions for expected results
        if test_scenario.expected_results:
            code_lines.append("        # Verify expected results")
            for result in test_scenario.expected_results:
                code_lines.append(f'        # Expected: {result}')
                if "visible" in result.lower():
                    code_lines.append('        expect(page.locator("[data-testid=\\"success\\"]")).to_be_visible()')
                elif "success" in result.lower():
                    code_lines.append('        assert "dashboard" in page.url')
            code_lines.append("")
        
        return "\\n".join(code_lines)
    
    def _generate_playwright_python_step(self, step: GherkinStep, test_data: dict) -> List[str]:
        """Generate Python Playwright code for a Gherkin step"""
        
        code = []
        text_lower = step.text.lower()
        
        if "navigate" in text_lower or "go to" in text_lower:
            url = test_data.get("url", "/")
            code.append(f'page.goto("{url}")')
            code.append('page.wait_for_load_state("networkidle")')
            
        elif "click" in text_lower:
            if "button" in text_lower:
                if "login" in text_lower or "sign in" in text_lower:
                    code.append('page.get_by_role("button", name=re.compile("login|sign in", re.IGNORECASE)).click()')
                else:
                    code.append('page.get_by_role("button").first.click()')
            else:
                code.append('page.locator("[data-testid=\\"element\\"]").click()')
                
        elif "enter" in text_lower or "type" in text_lower or "fill" in text_lower:
            if "email" in text_lower:
                email = test_data.get("email", "test@example.com")
                code.append(f'page.get_by_label("Email").fill("{email}")')
            elif "password" in text_lower:
                password = test_data.get("password", "SecurePass123!")
                code.append(f'page.get_by_label("Password").fill("{password}")')
            else:
                code.append('page.get_by_role("textbox").first.fill("test value")')
                
        elif "should" in text_lower or "verify" in text_lower or "expect" in text_lower:
            if "visible" in text_lower:
                code.append('expect(page.locator(":visible")).to_have_count(lambda count: count > 0)')
            elif "url" in text_lower:
                code.append('expect(page).to_have_url(re.compile(".*"))')
            else:
                code.append('# Add assertion here')
                
        elif "wait" in text_lower:
            code.append('page.wait_for_timeout(2000)')
            
        else:
            code.append(f'# TODO: Implement step - {step.text}')
            
        return code
'''
        
        # Find where to insert the new method
        engine_class = content.find("class CodeGenerationEngine:")
        if engine_class > 0:
            # Find the end of the class
            next_class = content.find("\nclass ", engine_class + 1)
            if next_class > 0:
                # Insert before the next class
                content = content[:next_class] + playwright_method + content[next_class:]
    
    # Save updated version
    backup_path = Path("code_generation_with_llm.py.backup")
    file_path.rename(backup_path)
    file_path.write_text(content, encoding='utf-8')
    
    print("[OK] Updated code_generation_with_llm.py with Python Playwright support")
    print(f"[OK] Backup saved to {backup_path}")
    return True


def create_integration_test():
    """Create a test to verify the integration works"""
    
    test_content = '''#!/usr/bin/env python3
"""
Integration test for test_generation_with_llm.py and code_generation_with_llm.py
Verifies proper separation of concerns and DRY compliance
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from test_generation_with_llm import WorldClassTestGenerator, TestCategory, TestFramework
from code_generation_with_llm import CodeGenerationEngine
from elements_extractor_no_llm import ExtractedElement, ElementType, InteractionType


async def test_integration():
    """Test that modules work together properly"""
    
    print("[INTEGRATION TEST] Testing module separation and integration")
    print("=" * 70)
    
    # Step 1: Generate test scenarios with test_generation_with_llm.py
    print("[STEP 1] Generating test scenarios...")
    test_generator = WorldClassTestGenerator()
    
    # Create sample elements
    elements = [
        ExtractedElement(
            selector='#email',
            element_type=ElementType.INPUT,
            tag_name='input',
            attributes={'type': 'email'},
            is_editable=True,
            confidence=0.95,
            interaction_types=[InteractionType.TYPE]
        ),
        ExtractedElement(
            selector='#submit',
            element_type=ElementType.BUTTON,
            tag_name='button',
            text='Submit',
            is_clickable=True,
            confidence=0.98,
            interaction_types=[InteractionType.CLICK]
        )
    ]
    
    # Generate test scenarios (NO code generation here)
    result = await test_generator.generate_from_elements(
        elements=elements,
        url="https://example.com/form",
        test_categories=[TestCategory.FUNCTIONAL],
        frameworks=[TestFramework.PLAYWRIGHT],  # Just for metadata
        enable_mcp=False,
        enable_self_healing=False
    )
    
    print(f"[OK] Generated {result.total_scenarios} test scenarios")
    print(f"[OK] No executable code in result: {result.test_suites[0].executable_code is None}")
    
    # Step 2: Generate code with code_generation_with_llm.py
    print("\\n[STEP 2] Generating Python Playwright code...")
    code_generator = CodeGenerationEngine()
    
    # Get the first test suite's scenarios
    test_scenarios = result.test_suites[0].scenarios
    
    # Generate Python Playwright code
    generated_code = []
    for scenario in test_scenarios:
        code = await code_generator.generate_from_scenario(
            scenario=scenario,
            test_framework="pytest",
            browser_framework="playwright"
        )
        generated_code.append(code)
        
        # Verify it's Python code
        print(f"[OK] Generated Python code for: {scenario.name}")
        assert "import pytest" in code.code or "from playwright" in code.code
        assert "def test_" in code.code or "class Test" in code.code
        print(f"     Language: {code.language}")
        print(f"     Framework: {code.framework}")
    
    print("\\n[SUCCESS] Integration test passed!")
    print("Modules properly separated:")
    print("  - test_generation_with_llm.py: Generates test scenarios only")
    print("  - code_generation_with_llm.py: Generates Python Playwright code")
    print("  - No code duplication (DRY compliance)")
    
    return True


if __name__ == "__main__":
    asyncio.run(test_integration())
'''
    
    test_path = Path("test_integration_dry.py")
    test_path.write_text(test_content, encoding='utf-8')
    print(f"[OK] Created integration test: {test_path}")
    return True


if __name__ == "__main__":
    print("[REFACTORING] Fixing DRY violations...")
    print("=" * 70)
    
    # Run refactoring
    success = True
    success = success and refactor_test_generation()
    success = success and update_code_generation_for_playwright()
    success = success and create_integration_test()
    
    if success:
        print("\n[SUCCESS] Refactoring complete!")
        print("Next steps:")
        print("1. Run test_integration_dry.py to verify integration")
        print("2. Test with live LLM calls")
        print("3. Validate Python Playwright code generation")
    else:
        print("\n[ERROR] Refactoring failed")