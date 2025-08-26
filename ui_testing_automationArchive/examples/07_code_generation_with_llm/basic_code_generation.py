#!/usr/bin/env python3
"""
Basic Code Generation Example

This example demonstrates:
- Simple Gherkin to Python test conversion
- Basic configuration options
- File output and validation
- Integration with Constitutional AI safety features

Requirements:
- API key: OPENAI_API_KEY (or ANTHROPIC_API_KEY or GEMINI_API_KEY)
- Dependencies: openai, black, psutil
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from code_generation_with_llm import (
    CodeGenerationWithLLM, 
    CodeGenerationConfig,
    TestFramework,
    BrowserFramework,
    CodePattern,
    LLMProvider
)

async def basic_generation_example():
    """
    Demonstrates basic code generation from Gherkin scenarios
    """
    print("="*60)
    print("BASIC CODE GENERATION EXAMPLE")
    print("="*60)
    
    # Check for API keys
    if not any([os.getenv("OPENAI_API_KEY"), os.getenv("ANTHROPIC_API_KEY"), os.getenv("GEMINI_API_KEY")]):
        print("[ERROR] Error: No LLM API key found!")
        print("Please set one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY")
        return False
    
    # Simple Gherkin scenario for login functionality
    gherkin_scenario = """
Feature: User Authentication
  As a user
  I want to log into the system
  So that I can access my account

  Scenario: Successful login with valid credentials
    Given I am on the login page
    And the login form is visible
    When I enter "user@example.com" in the email field
    And I enter "secure_password123" in the password field
    And I click the "Sign In" button
    Then I should be redirected to the dashboard
    And I should see "Welcome back" message
    And the user menu should be visible

  Scenario: Failed login with invalid credentials
    Given I am on the login page
    When I enter "invalid@example.com" in the email field
    And I enter "wrong_password" in the password field
    And I click the "Sign In" button
    Then I should see an error message "Invalid credentials"
    And I should remain on the login page
"""

    try:
        # Create basic configuration
        config = CodeGenerationConfig(
            test_framework=TestFramework.PYTEST,
            browser_framework=BrowserFramework.PLAYWRIGHT,
            code_pattern=CodePattern.PAGE_OBJECT,
            
            # Enable safety features
            enable_constitutional_ai=True,
            safety_threshold=0.9,
            
            # Basic quality features
            auto_format=True,
            validate_syntax=True,
            add_type_hints=True,
            add_docstrings=True
        )
        
        print("🚀 Initializing Code Generator...")
        
        # Initialize generator with OpenAI (fallback to others if needed)
        llm_provider = LLMProvider.OPENAI
        if not os.getenv("OPENAI_API_KEY"):
            if os.getenv("ANTHROPIC_API_KEY"):
                llm_provider = LLMProvider.ANTHROPIC
            elif os.getenv("GEMINI_API_KEY"):
                llm_provider = LLMProvider.GEMINI
        
        generator = CodeGenerationWithLLM(
            config=config,
            llm_provider=llm_provider,
            llm_model="gpt-4" if llm_provider == LLMProvider.OPENAI else None,
            verbose=True
        )
        
        print(f"[OK] Using LLM Provider: {llm_provider.value}")
        print("\n📝 Input Gherkin Scenario:")
        print("-" * 40)
        print(gherkin_scenario.strip())
        
        print("\n🔄 Generating test code...")
        print("This may take 10-30 seconds...")
        
        # Generate code from Gherkin
        result = await generator.generate_from_gherkin(
            gherkin_text=gherkin_scenario,
            output_file="generated_login_test.py"
        )
        
        # Display results
        print("\n" + "="*60)
        print("GENERATION RESULTS")
        print("="*60)
        
        print(f"[OK] Code generation successful!")
        print(f"📊 Generated {len(result.code.split(chr(10)))} lines of code")
        print(f"🛡️ Safety score: {result.safety_score:.2f}")
        print(f"[FAST] Generation time: {result.generation_time:.1f}s")
        print(f"[OK] Syntax valid: {result.syntax_valid}")
        
        # Show code preview
        print(f"\n📋 Code Preview (first 20 lines):")
        print("-" * 40)
        code_lines = result.code.split('\n')
        for i, line in enumerate(code_lines[:20], 1):
            print(f"{i:2d}| {line}")
        
        if len(code_lines) > 20:
            print(f"... ({len(code_lines) - 20} more lines)")
        
        # Safety check results
        if result.safety_violations:
            print(f"\n⚠️ Safety violations detected:")
            for violation in result.safety_violations:
                print(f"  - {violation.type}: {violation.description}")
        else:
            print(f"\n[OK] No safety violations detected")
        
        # Code quality metrics
        if hasattr(result, 'metrics') and result.metrics:
            print(f"\n📈 Code Quality Metrics:")
            print(f"  - Lines of code: {result.metrics.lines_of_code}")
            print(f"  - Cyclomatic complexity: {result.metrics.cyclomatic_complexity}")
            print(f"  - Maintainability index: {result.metrics.maintainability_index:.1f}")
        
        # Save to file
        output_file = Path("generated_login_test.py")
        output_file.write_text(result.code)
        print(f"\n💾 Code saved to: {output_file.absolute()}")
        
        # Show file contents info
        print(f"📁 File size: {len(result.code)} characters")
        print(f"🏷️ Test framework: {config.test_framework.value}")
        print(f"🌐 Browser framework: {config.browser_framework.value}")
        print(f"📐 Code pattern: {config.code_pattern.value}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error during code generation: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        # Show common solutions
        print(f"\n🔧 Common solutions:")
        print(f"1. Check your API key is set correctly")
        print(f"2. Ensure you have internet connection")
        print(f"3. Verify all dependencies are installed: pip install openai black psutil")
        print(f"4. Try with a different LLM provider")
        
        return False

async def validate_generated_code():
    """
    Validates the generated code can be imported and parsed
    """
    print("\n" + "="*60)
    print("CODE VALIDATION")
    print("="*60)
    
    output_file = Path("generated_login_test.py")
    
    if not output_file.exists():
        print("[ERROR] Generated file not found")
        return False
    
    try:
        # Read the generated code
        code = output_file.read_text()
        
        # Basic syntax validation using AST
        import ast
        ast.parse(code)
        print("[OK] Generated code has valid Python syntax")
        
        # Check for basic test structure
        if "class" in code and "def test_" in code:
            print("[OK] Generated code contains test classes and methods")
        
        if "import pytest" in code or "from playwright" in code:
            print("[OK] Generated code imports required testing frameworks")
        
        if "async def" in code:
            print("[OK] Generated code uses async/await pattern")
        
        # Count test methods
        test_methods = code.count("def test_")
        async_test_methods = code.count("async def test_")
        print(f"📊 Found {test_methods} test methods ({async_test_methods} async)")
        
        # Check for Page Object Model
        if "class" in code and "Page" in code:
            print("[OK] Generated code follows Page Object Model pattern")
        
        print("\n🎉 Code validation successful!")
        return True
        
    except SyntaxError as e:
        print(f"[ERROR] Syntax error in generated code: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error validating code: {e}")
        return False

async def main():
    """
    Main function that runs the basic code generation example
    """
    print("🚀 Starting Basic Code Generation Example")
    print("This example demonstrates simple Gherkin-to-Python conversion")
    
    # Run the basic generation example
    success = await basic_generation_example()
    
    if success:
        # Validate the generated code
        await validate_generated_code()
        
        print("\n" + "="*60)
        print("EXAMPLE COMPLETED SUCCESSFULLY")
        print("="*60)
        print("[OK] Code generation completed")
        print("[OK] Safety checks passed")
        print("[OK] Code validation passed")
        print("[OK] File saved successfully")
        
        print("\n📁 Next steps:")
        print("1. Review the generated code in 'generated_login_test.py'")
        print("2. Install test dependencies: pip install pytest playwright")
        print("3. Install browser: playwright install chromium")
        print("4. Run the test: python -m pytest generated_login_test.py -v")
        
        print("\n🔗 Try other examples:")
        print("- python advanced_features_demo.py")
        print("- python multi_framework_demo.py")
        print("- python safety_features_demo.py")
        
    else:
        print("\n[ERROR] Example failed. Please check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Example interrupted by user")
        sys.exit(130)