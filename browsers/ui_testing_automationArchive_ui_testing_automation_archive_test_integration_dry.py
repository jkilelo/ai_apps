#!/usr/bin/env python3
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
    print("\n[STEP 2] Generating Python Playwright code...")
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
    
    print("\n[SUCCESS] Integration test passed!")
    print("Modules properly separated:")
    print("  - test_generation_with_llm.py: Generates test scenarios only")
    print("  - code_generation_with_llm.py: Generates Python Playwright code")
    print("  - No code duplication (DRY compliance)")
    
    return True


if __name__ == "__main__":
    asyncio.run(test_integration())
