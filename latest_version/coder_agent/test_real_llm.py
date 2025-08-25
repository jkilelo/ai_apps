#!/usr/bin/env python3
"""
Test CODER Agent with REAL LLM code generation
Following CODER v3.1 protocol strictly
"""

import asyncio
import sys
from pathlib import Path

# Add parent path
sys.path.append(str(Path(__file__).parent.parent))

from coder_agent.contracts.base import AgentRequest
from coder_agent.core.engine import CoderEngine


async def test_real_llm_code_generation():
    """Test CODER Agent with real LLM for code generation."""
    
    print("=" * 80)
    print("TESTING CODER AGENT WITH REAL LLM CODE GENERATION")
    print("=" * 80)
    
    # Initialize CODER Engine
    config = {
        "require_tests": True,
        "follow_coder_v3": True,
        "llm": {
            "use_real_llm": True,
            "provider": "openai"
        }
    }
    
    engine = CoderEngine(config)
    
    # Test Case 1: Generate a simple function with Pydantic contracts
    print("\n[TEST 1] Generate email validator function with Pydantic v2 contracts")
    print("-" * 60)
    
    request1 = AgentRequest(
        task="Create a Python function to validate email addresses with Pydantic v2 contracts and comprehensive tests",
        project_path=str(Path.cwd()),
        platform="any",
        context={"instructions": "Generate production-ready code following CODER v3.1 protocol"}
    )
    
    response1 = await engine.execute(request1)
    
    print(f"Success: {response1.success}")
    if response1.success:
        print(f"Tokens used: {response1.tokens_used}")
        print(f"Duration: {response1.duration_seconds:.2f}s")
        if response1.changes:
            print(f"Files changed: {response1.changes}")
    else:
        print(f"Errors: {response1.errors}")
    
    # Test Case 2: Generate a more complex module
    print("\n[TEST 2] Generate password strength checker module")
    print("-" * 60)
    
    request2 = AgentRequest(
        task="Implement a password strength checker module with multiple validation rules, Pydantic v2 contracts, and pytest tests",
        project_path=str(Path.cwd()),
        platform="any",
        context={"requirements": "Must include: length check, uppercase, lowercase, digits, special chars, common patterns detection"}
    )
    
    response2 = await engine.execute(request2)
    
    print(f"Success: {response2.success}")
    if response2.success:
        print(f"Tokens used: {response2.tokens_used}")
        print(f"Duration: {response2.duration_seconds:.2f}s")
        if response2.tests_run:
            print(f"Tests run: {response2.tests_run}")
    else:
        print(f"Errors: {response2.errors}")
    
    # Test Case 3: Fix code with error
    print("\n[TEST 3] Fix broken code using real LLM")
    print("-" * 60)
    
    # First write some broken code
    broken_code = """
def calculate_average(numbers):
    # This has a bug - division by zero not handled
    total = sum(numbers)
    return total / len(numbers)

# This will crash
result = calculate_average([])
print(result)
"""
    
    broken_file = Path("broken_code.py")
    broken_file.write_text(broken_code)
    
    request3 = AgentRequest(
        task="Fix the broken_code.py file - handle the division by zero error properly with Pydantic contracts",
        project_path=str(Path.cwd()),
        platform="any",
        context={"error_info": "The code crashes with empty list. Add proper error handling and validation."}
    )
    
    response3 = await engine.execute(request3)
    
    print(f"Success: {response3.success}")
    if response3.success:
        print(f"Code fixed successfully")
        print(f"Tokens used: {response3.tokens_used}")
    else:
        print(f"Errors: {response3.errors}")
    
    # Clean up test file
    if broken_file.exists():
        broken_file.unlink()
    
    print("\n" + "=" * 80)
    print("CODER AGENT REAL LLM TESTING COMPLETE")
    print("=" * 80)
    
    # Summary
    total_tokens = response1.tokens_used + response2.tokens_used + response3.tokens_used
    total_time = response1.duration_seconds + response2.duration_seconds + response3.duration_seconds
    
    print(f"\nSUMMARY:")
    print(f"Total tokens used: {total_tokens}")
    print(f"Total time: {total_time:.2f}s")
    print(f"All tests passed: {response1.success and response2.success and response3.success}")
    
    return response1.success and response2.success and response3.success


async def test_llm_connectivity():
    """Quick test to verify LLM connectivity."""
    from coder_agent.llm import get_llm_client
    
    print("\n[CONNECTIVITY TEST] Checking LLM connections...")
    print("-" * 60)
    
    client = get_llm_client()
    results = client.verify_connectivity()
    
    for provider, connected in results.items():
        status = "✅ Connected" if connected else "❌ Not Connected"
        print(f"{provider}: {status}")
    
    return any(results.values())


async def main():
    """Main test runner."""
    # First check connectivity
    connected = await test_llm_connectivity()
    
    if not connected:
        print("\n❌ ERROR: No LLM providers connected!")
        print("Please check your API keys in .env file")
        return False
    
    # Run full tests
    success = await test_real_llm_code_generation()
    
    if success:
        print("\n✅ ALL TESTS PASSED - CODER Agent is using REAL LLM!")
    else:
        print("\n❌ SOME TESTS FAILED - Check the output above")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)