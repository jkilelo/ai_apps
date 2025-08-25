"""
Simple test to verify the reverse prompting engine works correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path to import reverse_prompting
sys.path.insert(0, str(Path(__file__).parent.parent))

from reverse_prompting import (
    ReversePromptingEngine,
    CodeArtifact,
    CodeLanguage,
    EngineConfig,
    PromptStrategy,
)


async def test_basic_functionality():
    """Test basic reverse prompting functionality."""
    print("🧪 Testing Reverse Prompting Engine...")

    # Create a simple code artifact
    code = CodeArtifact(
        name="hello_world",
        language=CodeLanguage.PYTHON,
        content="""def hello_world():
    \"\"\"Print a greeting message.\"\"\"
    print("Hello, World!")
    return "Hello, World!"

# Call the function
if __name__ == "__main__":
    result = hello_world()
    print(f"Function returned: {result}")""",
        description="Simple Hello World function",
    )

    # Create minimal configuration
    config = EngineConfig(
        max_iterations=2,
        enable_monitoring=False,
        enable_evolution=False,
        enable_caching=False,
        storage_backend="sqlite",
        storage_path="./test_data",
    )

    # Create engine
    engine = ReversePromptingEngine(config=config)

    try:
        # Run reverse prompting
        session = await engine.run_reverse_prompting(
            target_code=code,
            session_name="test_hello_world",
            strategies=[PromptStrategy.ZERO_SHOT],  # Use only one strategy for testing
            max_iterations=1,
        )

        # Check results
        print(f"✅ Session created: {session.name}")
        print(f"✅ Generated {len(session.generated_prompts)} prompts")
        print(f"✅ Created {len(session.generated_artifacts)} artifacts")
        print(f"✅ Completed {len(session.evaluations)} evaluations")

        if session.best_result:
            print(f"✅ Best score: {session.best_result.overall_score:.3f}")

        # Test session storage
        sessions = await engine.list_sessions(limit=5)
        print(f"✅ Found {len(sessions)} stored sessions")

        print("🎉 All tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        await engine.cleanup()


def test_imports():
    """Test that all imports work correctly."""
    print("📦 Testing imports...")

    try:
        from reverse_prompting import (
            CodeArtifact,
            CodeLanguage,
            PromptStrategy,
            ReversePromptingEngine,
            EngineConfig,
            quick_reverse_prompt,
            create_default_engine,
        )

        from reverse_prompting.strategies import (
            ZeroShotStrategy,
            ChainOfThoughtStrategy,
        )

        from reverse_prompting.evaluation import (
            ComprehensiveEvaluator,
            ExactMatchEvaluator,
        )

        from reverse_prompting.storage import SessionStorage, SQLiteStorage

        print("✅ All imports successful")
        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_quick_function():
    """Test the quick utility function."""
    print("⚡ Testing quick reverse prompt...")

    try:
        from reverse_prompting import quick_reverse_prompt, CodeLanguage

        # Simple code to test
        code = """def add_numbers(a, b):
    return a + b

result = add_numbers(5, 3)
print(f"5 + 3 = {result}")"""

        # This should work without any external dependencies
        session = quick_reverse_prompt(
            code_content=code,
            language=CodeLanguage.PYTHON,
            session_name="test_quick_add",
            max_iterations=1,
            enable_monitoring=False,
        )

        print(f"✅ Quick function generated {len(session.generated_prompts)} prompts")
        print(f"✅ Session success rate: {session.get_success_rate():.2%}")

        return True

    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("🚀 REVERSE PROMPTING ENGINE TEST SUITE")
    print("=" * 50)

    all_passed = True

    # Test imports
    if not test_imports():
        all_passed = False

    print()

    # Test quick function (synchronous)
    if not test_quick_function():
        all_passed = False

    print()

    # Test basic functionality (asynchronous)
    if not await test_basic_functionality():
        all_passed = False

    print()
    print("=" * 50)

    if all_passed:
        print("🎉 ALL TESTS PASSED! The reverse prompting engine is working correctly.")
        print("\nNext steps:")
        print("- Try: python -m reverse_prompting run your_code.py")
        print("- Run examples: python reverse_prompting/examples/usage_examples.py")
        print("- Check out the README.md for more information")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
