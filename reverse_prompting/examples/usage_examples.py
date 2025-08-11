"""
Reverse Prompting Engine Examples

This module demonstrates various ways to use the reverse prompting engine
to generate high-quality prompts from existing code.
"""

import asyncio
from pathlib import Path
import json

from reverse_prompting import (
    ReversePromptingEngine,
    CodeArtifact,
    CodeLanguage,
    PromptStrategy,
    EngineConfig,
    quick_reverse_prompt,
    create_default_engine,
)


# Example 1: Basic Python Function
async def example_1_basic_python():
    """Example 1: Basic reverse prompting with a simple Python function."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Python Function")
    print("=" * 60)

    # Define the target code
    code = CodeArtifact(
        name="fibonacci",
        language=CodeLanguage.PYTHON,
        content="""def fibonacci(n):
    \"\"\"Calculate the nth Fibonacci number using recursion.\"\"\"
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
for i in range(10):
    print(f"fibonacci({i}) = {fibonacci(i)}")""",
        description="Recursive Fibonacci implementation with test",
    )

    # Create engine with basic configuration
    config = EngineConfig(
        max_iterations=3, enable_monitoring=True, success_threshold=0.7
    )
    engine = ReversePromptingEngine(config=config)

    # Run reverse prompting
    session = await engine.run_reverse_prompting(
        target_code=code,
        session_name="fibonacci_example",
        strategies=[PromptStrategy.ZERO_SHOT, PromptStrategy.CHAIN_OF_THOUGHT],
    )

    # Display results
    print(f"✅ Generated {len(session.generated_prompts)} prompts")
    print(f"✅ Success rate: {session.get_success_rate():.2%}")
    print(f"✅ Best score: {session.best_result.overall_score:.3f}")

    # Show the best prompt
    if session.best_result:
        best_prompt_id = session.best_result.prompt_id
        best_prompt = next(
            (p for p in session.generated_prompts if p.id == best_prompt_id), None
        )
        if best_prompt:
            print(f"\n🏆 Best Prompt ({best_prompt.strategy.value}):")
            print("-" * 40)
            print(
                best_prompt.content[:200] + "..."
                if len(best_prompt.content) > 200
                else best_prompt.content
            )

    await engine.cleanup()
    print()


# Example 2: JavaScript with Multiple Strategies
async def example_2_javascript_multi_strategy():
    """Example 2: JavaScript code with multiple prompting strategies."""
    print("=" * 60)
    print("EXAMPLE 2: JavaScript with Multiple Strategies")
    print("=" * 60)

    # Define a more complex JavaScript function
    code = CodeArtifact(
        name="data_processor",
        language=CodeLanguage.JAVASCRIPT,
        content="""function processUserData(users) {
    // Filter active users and transform data
    return users
        .filter(user => user.active && user.age >= 18)
        .map(user => ({
            id: user.id,
            name: user.name.toUpperCase(),
            email: user.email.toLowerCase(),
            category: user.age < 30 ? 'young' : 'adult'
        }))
        .sort((a, b) => a.name.localeCompare(b.name));
}

// Example usage
const sampleUsers = [
    { id: 1, name: 'John Doe', email: 'JOHN@EXAMPLE.COM', age: 25, active: true },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com', age: 17, active: true },
    { id: 3, name: 'Bob Wilson', email: 'BOB@TEST.COM', age: 35, active: false }
];

console.log(processUserData(sampleUsers));""",
        description="User data processing with filtering, mapping, and sorting",
    )

    # Use all available strategies
    strategies = [
        PromptStrategy.ZERO_SHOT,
        PromptStrategy.FEW_SHOT,
        PromptStrategy.CHAIN_OF_THOUGHT,
        PromptStrategy.SELF_CONSISTENCY,
    ]

    config = EngineConfig(
        max_iterations=2,
        parallel_strategies=2,  # Run strategies in parallel
        enable_evolution=True,
        enable_monitoring=True,
    )

    engine = ReversePromptingEngine(config=config)

    session = await engine.run_reverse_prompting(
        target_code=code,
        session_name="javascript_data_processor",
        strategies=strategies,
    )

    # Analyze results by strategy
    print(f"✅ Total prompts: {len(session.generated_prompts)}")
    print(f"✅ Total evaluations: {len(session.evaluations)}")
    print(f"✅ Success rate: {session.get_success_rate():.2%}")

    # Show strategy performance
    strategy_scores = {}
    for evaluation in session.evaluations:
        prompt = next(
            (p for p in session.generated_prompts if p.id == evaluation.prompt_id), None
        )
        if prompt:
            strategy = prompt.strategy.value
            if strategy not in strategy_scores:
                strategy_scores[strategy] = []
            strategy_scores[strategy].append(evaluation.overall_score)

    print("\n📊 Strategy Performance:")
    for strategy, scores in strategy_scores.items():
        avg_score = sum(scores) / len(scores) if scores else 0
        print(f"  {strategy}: {avg_score:.3f} avg ({len(scores)} attempts)")

    await engine.cleanup()
    print()


# Example 3: Quick Utility Function
def example_3_quick_reverse_prompt():
    """Example 3: Using the quick utility function."""
    print("=" * 60)
    print("EXAMPLE 3: Quick Reverse Prompting")
    print("=" * 60)

    # Simple sorting algorithm
    code = """def bubble_sort(arr):
    \"\"\"Sort an array using the bubble sort algorithm.\"\"\"
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr

# Test with sample data
test_array = [64, 34, 25, 12, 22, 11, 90]
print(f"Original: {test_array}")
sorted_array = bubble_sort(test_array.copy())
print(f"Sorted: {sorted_array}")"""

    # Use the quick utility - this runs synchronously
    session = quick_reverse_prompt(
        code_content=code,
        language=CodeLanguage.PYTHON,
        session_name="bubble_sort_quick",
        max_iterations=2,
        enable_monitoring=False,  # Disable for quick run
    )

    print(f"✅ Quick run completed!")
    print(f"✅ Generated {len(session.generated_prompts)} prompts")
    print(f"✅ Best score: {session.best_result.overall_score:.3f}")
    print()


# Example 4: Advanced Configuration with Evolution
async def example_4_advanced_evolution():
    """Example 4: Advanced configuration with evolutionary prompt improvement."""
    print("=" * 60)
    print("EXAMPLE 4: Advanced Evolution Example")
    print("=" * 60)

    # More complex algorithm - binary search
    code = CodeArtifact(
        name="binary_search",
        language=CodeLanguage.PYTHON,
        content="""def binary_search(arr, target):
    \"\"\"
    Perform binary search on a sorted array.
    
    Args:
        arr: Sorted array to search in
        target: Value to find
        
    Returns:
        Index of target if found, -1 otherwise
    \"\"\"
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        mid_val = arr[mid]
        
        if mid_val == target:
            return mid
        elif mid_val < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

# Comprehensive test
def test_binary_search():
    test_cases = [
        ([1, 3, 5, 7, 9, 11], 7, 3),
        ([1, 3, 5, 7, 9, 11], 1, 0),
        ([1, 3, 5, 7, 9, 11], 11, 5),
        ([1, 3, 5, 7, 9, 11], 4, -1),
        ([], 5, -1),
        ([5], 5, 0)
    ]
    
    for arr, target, expected in test_cases:
        result = binary_search(arr, target)
        status = "✓" if result == expected else "✗"
        print(f"{status} Search {target} in {arr}: {result} (expected {expected})")

test_binary_search()""",
        description="Binary search algorithm with comprehensive test suite",
    )

    # Advanced configuration with evolution enabled
    config = EngineConfig(
        max_iterations=5,
        parallel_strategies=3,
        success_threshold=0.85,
        enable_evolution=True,
        evolution_generations=3,
        population_size=10,
        mutation_rate=0.3,
        crossover_rate=0.7,
        enable_monitoring=True,
        enable_caching=True,
    )

    engine = ReversePromptingEngine(config=config)

    session = await engine.run_reverse_prompting(
        target_code=code,
        session_name="binary_search_evolution",
        strategies=[
            PromptStrategy.CHAIN_OF_THOUGHT,
            PromptStrategy.TREE_OF_THOUGHTS,
            PromptStrategy.META_PROMPTING,
        ],
    )

    print(f"✅ Evolution completed!")
    print(f"✅ Generated {len(session.generated_prompts)} prompts")
    print(f"✅ Conducted {len(session.evaluations)} evaluations")
    print(f"✅ Success rate: {session.get_success_rate():.2%}")
    print(f"✅ Best score: {session.best_result.overall_score:.3f}")

    # Show evolution progress
    if len(session.evaluations) > 5:
        scores = [e.overall_score for e in session.evaluations]
        initial_avg = sum(scores[:3]) / 3
        final_avg = sum(scores[-3:]) / 3
        improvement = (
            ((final_avg - initial_avg) / initial_avg) * 100 if initial_avg > 0 else 0
        )
        print(f"📈 Evolution improvement: {improvement:+.1f}%")

    await engine.cleanup()
    print()


# Example 5: Multi-Language Comparison
async def example_5_multi_language():
    """Example 5: Compare reverse prompting across different languages."""
    print("=" * 60)
    print("EXAMPLE 5: Multi-Language Comparison")
    print("=" * 60)

    # Same algorithm in different languages
    algorithms = [
        CodeArtifact(
            name="factorial_python",
            language=CodeLanguage.PYTHON,
            content="""def factorial(n):
    \"\"\"Calculate factorial recursively.\"\"\"
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print([factorial(i) for i in range(6)])""",
            description="Recursive factorial in Python",
        ),
        CodeArtifact(
            name="factorial_javascript",
            language=CodeLanguage.JAVASCRIPT,
            content="""function factorial(n) {
    // Calculate factorial recursively
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

// Test the function
for (let i = 0; i < 6; i++) {
    console.log(`${i}! = ${factorial(i)}`);
}""",
            description="Recursive factorial in JavaScript",
        ),
    ]

    config = EngineConfig(
        max_iterations=2, enable_monitoring=True, success_threshold=0.7
    )

    results = {}

    for code in algorithms:
        engine = ReversePromptingEngine(config=config)

        session = await engine.run_reverse_prompting(
            target_code=code,
            session_name=f"factorial_{code.language.value}",
            strategies=[PromptStrategy.ZERO_SHOT, PromptStrategy.CHAIN_OF_THOUGHT],
        )

        results[code.language.value] = {
            "prompts": len(session.generated_prompts),
            "success_rate": session.get_success_rate(),
            "best_score": (
                session.best_result.overall_score if session.best_result else 0.0
            ),
        }

        await engine.cleanup()

    # Compare results
    print("🔍 Language Comparison Results:")
    for language, stats in results.items():
        print(f"  {language.upper()}:")
        print(f"    Prompts: {stats['prompts']}")
        print(f"    Success Rate: {stats['success_rate']:.2%}")
        print(f"    Best Score: {stats['best_score']:.3f}")
    print()


# Example 6: Save and Load Session
async def example_6_session_persistence():
    """Example 6: Demonstrate session saving and loading."""
    print("=" * 60)
    print("EXAMPLE 6: Session Persistence")
    print("=" * 60)

    # Create a simple function
    code = CodeArtifact(
        name="string_reverser",
        language=CodeLanguage.PYTHON,
        content="""def reverse_string(s):
    \"\"\"Reverse a string using slicing.\"\"\"
    return s[::-1]

def reverse_words(s):
    \"\"\"Reverse the order of words in a string.\"\"\"
    return ' '.join(s.split()[::-1])

# Test both functions
test_string = "Hello World Python"
print(f"Original: {test_string}")
print(f"Reversed: {reverse_string(test_string)}")
print(f"Words reversed: {reverse_words(test_string)}")""",
        description="String manipulation functions",
    )

    # Configure with SQLite storage
    config = EngineConfig(
        max_iterations=2,
        storage_backend="sqlite",
        storage_path="./examples_data",
        enable_caching=True,
    )

    engine = ReversePromptingEngine(config=config)

    # Run reverse prompting
    session = await engine.run_reverse_prompting(
        target_code=code, session_name="string_reverser_persistent"
    )

    session_id = str(session.id)
    print(f"✅ Session created with ID: {session_id[:8]}...")
    print(f"✅ Generated {len(session.generated_prompts)} prompts")

    # List sessions
    sessions = await engine.list_sessions(limit=5)
    print(f"\n📋 Recent sessions ({len(sessions)} found):")
    for s in sessions:
        print(f"  - {s['name']} (Score: {s['best_score']:.3f})")

    # Load the session back
    loaded_session = await engine.storage.load_session(session_id)
    if loaded_session:
        print(f"\n✅ Successfully loaded session: {loaded_session.name}")
        print(f"✅ Loaded {len(loaded_session.generated_prompts)} prompts")

    await engine.cleanup()
    print()


async def main():
    """Run all examples."""
    print("🚀 REVERSE PROMPTING ENGINE EXAMPLES")
    print("=" * 60)
    print("This demo showcases the capabilities of the reverse prompting system.")
    print("Each example demonstrates different features and use cases.\n")

    try:
        # Run examples
        await example_1_basic_python()
        await example_2_javascript_multi_strategy()
        example_3_quick_reverse_prompt()  # Synchronous
        await example_4_advanced_evolution()
        await example_5_multi_language()
        await example_6_session_persistence()

        print("🎉 All examples completed successfully!")
        print("\nNext steps:")
        print("- Try the CLI: python -m reverse_prompting run your_code.py")
        print("- Explore the API documentation")
        print("- Experiment with different strategies and configurations")

    except Exception as e:
        print(f"❌ Error running examples: {e}")
        raise


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())
