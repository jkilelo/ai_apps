"""
Simple Live LLM Test for the AI Prompt Generator

This script tests the _llm.py interface with real API calls and demonstrates
how it can be used for reverse prompting tasks.
"""

import os
import sys
import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add parent directory to path to import _llm.py
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

try:
    # Import from the actual location
    llm_path = parent_dir / "_llm.py"
    if llm_path.exists():
        import importlib.util

        spec = importlib.util.spec_from_file_location("_llm", llm_path)
        _llm_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_llm_module)
        query_llm = _llm_module.query_llm
        print(f"✅ Successfully imported _llm.py from {llm_path}")
    else:
        raise ImportError(f"_llm.py not found at {llm_path}")
except Exception as e:
    print(f"❌ Error importing _llm.py: {e}")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_llm_connection():
    """Test basic LLM connectivity."""
    print("🔌 Testing LLM Connections...")
    print("=" * 50)

    # Check API keys
    api_keys = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Google": os.getenv("GOOGLE_API_KEY"),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
    }

    print("🔑 API Key Status:")
    available_providers = []
    for provider, key in api_keys.items():
        if key:
            status = "✅ Available"
            if provider == "OpenAI":
                available_providers.append(("openai", "gpt-4"))
            elif provider == "Google":
                available_providers.append(("gemini", "gemini-2.0-flash-exp"))
            elif provider == "Anthropic":
                available_providers.append(("claude", "claude-3-5-sonnet-20241022"))
        else:
            status = "❌ Missing"
        print(f"  {provider}: {status}")

    return available_providers


def test_simple_query(provider: str, model: str):
    """Test a simple query to verify the LLM works."""
    print(f"\n🧪 Testing {provider.upper()} ({model})...")

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Always respond concisely.",
        },
        {"role": "user", "content": "Say 'Hello from AI!' and nothing else."},
    ]

    try:
        start_time = time.time()
        response = query_llm(provider, model, messages)
        end_time = time.time()

        content = response.choices[0].message.content

        print(f"✅ Success!")
        print(f"   Response: {content}")
        print(f"   Time: {end_time - start_time:.2f}s")
        if response.usage:
            print(f"   Tokens: {response.usage.total_tokens}")

        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_code_generation(provider: str, model: str):
    """Test code generation capability."""
    print(f"\n💻 Testing Code Generation with {provider.upper()}...")

    messages = [
        {
            "role": "system",
            "content": """You are an expert Python programmer. Generate clean, working code.
Always wrap your code in triple backticks with 'python' specified.""",
        },
        {
            "role": "user",
            "content": """Create a Python function that calculates the factorial of a number using recursion.
The function should:
1. Take an integer parameter n
2. Return the factorial of n  
3. Handle the base case when n is 0 or 1
4. Include a docstring

Generate only the function code with proper formatting.""",
        },
    ]

    try:
        start_time = time.time()
        response = query_llm(provider, model, messages)
        end_time = time.time()

        content = response.choices[0].message.content

        # Extract code from response
        if "```python" in content:
            code_start = content.find("```python") + 9
            code_end = content.find("```", code_start)
            if code_end != -1:
                code = content[code_start:code_end].strip()
            else:
                code = content[code_start:].strip()
        elif "```" in content:
            code_start = content.find("```") + 3
            code_end = content.find("```", code_start)
            if code_end != -1:
                code = content[code_start:code_end].strip()
            else:
                code = content[code_start:].strip()
        else:
            code = content.strip()

        print(f"✅ Generated Code:")
        print("=" * 40)
        print(code)
        print("=" * 40)
        print(f"   Generation time: {end_time - start_time:.2f}s")
        if response.usage:
            print(f"   Tokens used: {response.usage.total_tokens}")

        # Test if the code is valid Python
        try:
            compile(code, "<string>", "exec")
            print("✅ Code compiles successfully!")

            # Try to execute it
            local_vars = {}
            exec(code, {}, local_vars)

            # Test the factorial function if it exists
            if "factorial" in local_vars:
                factorial_func = local_vars["factorial"]
                test_result = factorial_func(5)
                expected = 120  # 5! = 120
                if test_result == expected:
                    print(f"✅ Function test passed! factorial(5) = {test_result}")
                else:
                    print(f"⚠️  Function test failed. Expected 120, got {test_result}")

        except Exception as e:
            print(f"❌ Code execution failed: {e}")

        return True

    except Exception as e:
        print(f"❌ Code generation failed: {e}")
        return False


def test_reverse_prompting_simulation(provider: str, model: str):
    """Simulate reverse prompting by generating a prompt for existing code."""
    print(f"\n🔄 Testing Reverse Prompting Simulation with {provider.upper()}...")

    # Target code we want to generate a prompt for
    target_code = '''def fibonacci(n):
    """Calculate the nth Fibonacci number using recursion."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)'''

    print("🎯 Target Code:")
    print("-" * 30)
    print(target_code)
    print("-" * 30)

    messages = [
        {
            "role": "system",
            "content": """You are an expert at creating programming prompts. Given a piece of code, 
generate a clear, detailed prompt that would lead someone to write similar code.

The prompt should:
1. Describe what the function should do
2. Specify the algorithm or approach to use
3. Include any requirements or constraints
4. Be clear enough that another programmer could implement it

Do not include the actual code in your response, only the prompt.""",
        },
        {
            "role": "user",
            "content": f"""Analyze this Python code and generate a prompt that would lead someone to write similar code:

```python
{target_code}
```

Generate a programming prompt that would result in code like this.""",
        },
    ]

    try:
        start_time = time.time()
        response = query_llm(provider, model, messages)
        end_time = time.time()

        generated_prompt = response.choices[0].message.content

        print(f"✅ Generated Reverse Prompt:")
        print("=" * 50)
        print(generated_prompt)
        print("=" * 50)
        print(f"   Generation time: {end_time - start_time:.2f}s")

        # Now test if this prompt can regenerate similar code
        print(f"\n🔄 Testing the generated prompt...")

        test_messages = [
            {
                "role": "system",
                "content": "You are an expert Python programmer. Generate clean, working code based on the requirements.",
            },
            {
                "role": "user",
                "content": generated_prompt
                + "\n\nGenerate the Python code with proper formatting.",
            },
        ]

        test_response = query_llm(provider, model, test_messages)
        regenerated_content = test_response.choices[0].message.content

        # Extract code
        if "```python" in regenerated_content:
            code_start = regenerated_content.find("```python") + 9
            code_end = regenerated_content.find("```", code_start)
            if code_end != -1:
                regenerated_code = regenerated_content[code_start:code_end].strip()
            else:
                regenerated_code = regenerated_content[code_start:].strip()
        else:
            regenerated_code = regenerated_content.strip()

        print(f"🔄 Regenerated Code:")
        print("-" * 40)
        print(regenerated_code)
        print("-" * 40)

        # Simple similarity check
        similarity_score = 0
        if "fibonacci" in regenerated_code.lower():
            similarity_score += 0.3
        if (
            "recursion" in regenerated_code.lower()
            or "fibonacci(n - 1)" in regenerated_code
        ):
            similarity_score += 0.4
        if "n <= 1" in regenerated_code or "n < 2" in regenerated_code:
            similarity_score += 0.3

        print(f"📊 Similarity Score: {similarity_score:.1f}/1.0")

        if similarity_score >= 0.7:
            print("✅ Reverse prompting successful! High similarity achieved.")
        elif similarity_score >= 0.4:
            print("⚠️  Reverse prompting partially successful. Moderate similarity.")
        else:
            print("❌ Reverse prompting needs improvement. Low similarity.")

        return True

    except Exception as e:
        print(f"❌ Reverse prompting test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 LIVE LLM TEST FOR AI PROMPT GENERATOR")
    print("=" * 80)

    # Test connections
    available_providers = test_llm_connection()

    if not available_providers:
        print("\n⚠️  No API keys found. Please set at least one of:")
        print("   - OPENAI_API_KEY")
        print("   - GOOGLE_API_KEY")
        print("   - ANTHROPIC_API_KEY")
        print("\nExample: export OPENAI_API_KEY='your-key-here'")
        return

    print(f"\n🎯 Found {len(available_providers)} available provider(s)")

    # Test each available provider
    successful_tests = 0
    total_tests = 0

    for provider, model in available_providers:
        print(f"\n" + "=" * 60)
        print(f"🧪 TESTING {provider.upper()} - {model}")
        print("=" * 60)

        tests = [
            ("Simple Query", lambda p, m: test_simple_query(p, m)),
            ("Code Generation", lambda p, m: test_code_generation(p, m)),
            ("Reverse Prompting", lambda p, m: test_reverse_prompting_simulation(p, m)),
        ]

        provider_success = 0
        for test_name, test_func in tests:
            print(f"\n📋 Running: {test_name}")
            try:
                if test_func(provider, model):
                    provider_success += 1
                    successful_tests += 1
                total_tests += 1
            except Exception as e:
                print(f"❌ Test '{test_name}' failed with error: {e}")
                total_tests += 1

        print(
            f"\n📊 {provider.upper()} Results: {provider_success}/{len(tests)} tests passed"
        )

    # Final summary
    print(f"\n" + "=" * 80)
    print("🏁 FINAL RESULTS")
    print("=" * 80)
    print(f"✅ Successful tests: {successful_tests}/{total_tests}")
    print(
        f"📈 Success rate: {successful_tests/total_tests*100:.1f}%"
        if total_tests > 0
        else "No tests run"
    )

    if successful_tests > 0:
        print(f"\n🎉 Live LLM integration is working!")
        print("💡 You can now use these LLM providers for:")
        print("   • Code generation")
        print("   • Reverse prompting")
        print("   • Prompt optimization")
        print("   • Multi-strategy prompt testing")
    else:
        print(f"\n⚠️  All tests failed. Please check:")
        print("   • API key validity")
        print("   • Internet connection")
        print("   • Rate limits")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback

        traceback.print_exc()
