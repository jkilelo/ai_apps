#!/usr/bin/env python3
"""
Simple test of real LLM code generation
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from coder_agent.llm import get_llm_client, CodeGenerationInput


async def test_simple_code_generation():
    """Test simple code generation with real LLM."""
    
    print("=" * 80)
    print("TESTING REAL LLM CODE GENERATION")
    print("=" * 80)
    
    # Get LLM client
    client = get_llm_client()
    
    # Test 1: Generate email validator
    print("\n[TEST 1] Generate email validator with Pydantic v2")
    print("-" * 60)
    
    request = CodeGenerationInput(
        task_description="Create a Python function to validate email addresses using regex, with Pydantic v2 input/output contracts",
        language="python",
        requirements=[
            "Use Pydantic v2 for input/output contracts",
            "Include comprehensive tests using pytest",
            "Handle edge cases",
            "Add proper documentation"
        ],
        follow_coder_v3=True
    )
    
    result = client.generate_code(request)
    
    if result.success:
        print("✅ Code generation successful!")
        print(f"Tokens used: {result.tokens_used}")
        print(f"CODER v3.1 compliant: {result.coder_v3_compliant}")
        
        # Save generated code
        if result.code:
            code_file = Path("generated_email_validator.py")
            code_file.write_text(result.code)
            print(f"Code saved to: {code_file}")
        
        if result.tests:
            test_file = Path("test_generated_email_validator.py")
            test_file.write_text(result.tests)
            print(f"Tests saved to: {test_file}")
        
        # Show a snippet of the code
        if result.code:
            lines = result.code.split('\n')[:20]
            print("\nGenerated code (first 20 lines):")
            print("-" * 40)
            for i, line in enumerate(lines, 1):
                print(f"{i:3}: {line}")
    else:
        print(f"❌ Code generation failed: {result.error_message}")
    
    # Test 2: Generate with different provider
    print("\n[TEST 2] Generate password validator using Anthropic")
    print("-" * 60)
    
    from coder_agent.llm import LLMRequestInput, LLMMessage, LLMProvider
    
    llm_request = LLMRequestInput(
        provider=LLMProvider.ANTHROPIC,
        messages=[
            LLMMessage(
                role="system",
                content="You are a Python expert. Generate clean, production-ready code with Pydantic v2 contracts."
            ),
            LLMMessage(
                role="user",
                content="Create a password strength checker function with Pydantic v2 contracts. Include checks for length, uppercase, lowercase, digits, and special characters."
            )
        ],
        temperature=0.3,
        max_tokens=2000
    )
    
    response = client.query_llm(llm_request)
    
    if response.success:
        print("✅ Anthropic generation successful!")
        print(f"Tokens used: {response.tokens_used}")
        print(f"Model: {response.model}")
        
        # Show snippet
        if response.content:
            lines = response.content.split('\n')[:15]
            print("\nGenerated content (first 15 lines):")
            print("-" * 40)
            for line in lines:
                print(line)
    else:
        print(f"❌ Generation failed: {response.error_message}")
    
    print("\n" + "=" * 80)
    print("REAL LLM TESTING COMPLETE")
    print("=" * 80)
    
    return result.success


if __name__ == "__main__":
    success = asyncio.run(test_simple_code_generation())
    sys.exit(0 if success else 1)