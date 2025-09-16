#!/usr/bin/env python3
"""
Simple test for code_generation_with_llm_v3.py
Tests code generation without full test scenario generation
"""

import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from code_generation_with_llm_v3 import (
    CodeGenerationEngineV3,
    CodeGenerationContract,
    TestFramework,
    BrowserFramework,
    CodePattern
)
from test_generation_with_llm_v3 import TestScenario, GherkinStep, TestCategory, TestPriority

async def test_simple_code_generation():
    """Test code generation with manually created scenario"""
    print("="*60)
    print("SIMPLE CODE GENERATION TEST")
    print("="*60)
    
    # Create a simple test scenario manually
    scenario = TestScenario(
        name="Test Navigation to Homepage",
        description="Verify that the homepage loads correctly",
        category="functional",
        priority="high",
        steps=[
            GherkinStep(
                keyword="Given",
                text="I am on the browser"
            ),
            GherkinStep(
                keyword="When", 
                text="I navigate to https://example.com"
            ),
            GherkinStep(
                keyword="Then",
                text="the page should load successfully"
            ),
            GherkinStep(
                keyword="And",
                text="the title should contain 'Example Domain'"
            )
        ]
    )
    
    print(f"\n[TEST] Generating code for scenario: {scenario.name}")
    
    # Create contract
    contract = CodeGenerationContract(
        test_scenarios=[scenario],
        test_framework=TestFramework.PLAYWRIGHT,
        browser_framework=BrowserFramework.PLAYWRIGHT,
        code_pattern=CodePattern.DIRECT,  # Use direct pattern for simplicity
        url="https://example.com"
    )
    
    # Generate code
    engine = CodeGenerationEngineV3()
    
    try:
        generated_code = await engine.generate_code_from_scenarios(
            [scenario], contract
        )
        
        print(f"[OK] Code generated successfully")
        print(f"     Framework: {generated_code.framework}")
        print(f"     Pattern: {generated_code.pattern}")
        print(f"     Imports: {len(generated_code.imports)}")
        print(f"     Test methods: {len(generated_code.test_methods)}")
        
        # Save generated code
        output = Path("simple_test_code_v3.py")
        output.write_text(generated_code.to_file_content())
        print(f"\n[OK] Code saved to: {output}")
        
        # Show sample of generated code
        lines = generated_code.to_file_content().split('\n')[:20]
        print("\n[OK] Sample of generated code:")
        for line in lines:
            print(f"     {line}")
        
        print("\n[SUCCESS] Simple code generation test passed!")
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Code generation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(test_simple_code_generation()))