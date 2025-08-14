"""
Example usage of the Master Prompt Strategies system.
Demonstrates various ways to enhance prompts for maximum intelligence.
"""

from strategy_orchestrator import (
    StrategyOrchestrator, 
    PromptContext, 
    StrategyConfig,
    StrategyType,
    enhance_prompt,
    create_orchestrator
)

def example_simple_enhancement():
    """Simple enhancement with default settings."""
    print("=" * 60)
    print("EXAMPLE 1: Simple Enhancement")
    print("=" * 60)
    
    prompt = "How do I improve code performance?"
    enhanced = enhance_prompt(prompt)
    
    print("Original:", prompt)
    print("\nEnhanced:", enhanced[:500] + "...")
    
def example_complex_problem():
    """Complex problem requiring multiple strategies."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Complex Problem Solving")
    print("=" * 60)
    
    prompt = "Design a distributed system that handles millions of requests per second with zero downtime"
    
    context = PromptContext(
        domain="distributed_systems",
        task_type="architecture_design",
        complexity="complex",
        constraints={
            "scale": "millions_rps",
            "availability": "99.999%",
            "budget": "moderate"
        }
    )
    
    orchestrator = create_orchestrator([
        StrategyType.TREE_OF_THOUGHTS,
        StrategyType.REACT,
        StrategyType.META_PROMPTING,
        StrategyType.SELF_CONSISTENCY
    ])
    
    enhanced = orchestrator.apply_strategies(prompt, context)
    
    print("Original:", prompt)
    print("\nStrategies Applied:", [s.type.value for s in orchestrator.active_strategies])
    print("\nEnhanced Preview:", enhanced[:600] + "...")
    
def example_ethical_ai():
    """Ensuring ethical AI responses."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Ethical AI Enhancement")
    print("=" * 60)
    
    prompt = "How can I extract maximum value from user data?"
    
    context = PromptContext(
        domain="data_science",
        task_type="optimization",
        complexity="moderate",
        constraints={"ethical": True, "legal": "GDPR_compliant"}
    )
    
    orchestrator = StrategyOrchestrator()
    
    # Prioritize Constitutional AI
    orchestrator.add_strategy(StrategyConfig(
        name="constitutional_ai",
        type=StrategyType.CONSTITUTIONAL_AI,
        priority=100  # Highest priority
    ))
    
    orchestrator.add_strategy(StrategyConfig(
        name="chain_of_thought",
        type=StrategyType.CHAIN_OF_THOUGHT,
        priority=50
    ))
    
    enhanced = orchestrator.apply_strategies(prompt, context)
    
    print("Potentially Problematic Prompt:", prompt)
    print("\nEthically Enhanced:", enhanced[:500] + "...")
    
def example_creative_solution():
    """Creative problem solving with Tree of Thoughts."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Creative Problem Solving")
    print("=" * 60)
    
    prompt = "Invent a new programming paradigm that solves the problems of both functional and object-oriented programming"
    
    context = PromptContext(
        domain="computer_science",
        task_type="innovation",
        complexity="paradoxical"
    )
    
    orchestrator = create_orchestrator([
        StrategyType.TREE_OF_THOUGHTS,
        StrategyType.META_PROMPTING
    ])
    
    enhanced = orchestrator.apply_strategies(prompt, context)
    
    print("Creative Challenge:", prompt)
    print("\nEnhanced for Innovation:", enhanced[:600] + "...")
    
def example_self_improving():
    """Self-improving prompt through meta-prompting."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Self-Improving Prompt")
    print("=" * 60)
    
    prompt = "What is the best way to ask this question?"
    
    # Apply meta-prompting recursively
    enhanced = prompt
    for i in range(3):
        context = PromptContext(
            domain="meta_cognition",
            task_type="optimization",
            complexity="complex"
        )
        enhanced = enhance_prompt(
            enhanced,
            domain="meta_cognition",
            complexity="complex",
            strategies=["meta_prompting"]
        )
        print(f"\nRecursion {i+1}:", enhanced[:200] + "...")
    
def example_hybrid_strategy():
    """Custom hybrid strategy for specific use case."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Custom Hybrid Strategy")
    print("=" * 60)
    
    prompt = "Solve P vs NP"
    
    orchestrator = StrategyOrchestrator()
    
    # Create a custom hybrid for extremely hard problems
    hybrid = orchestrator.create_hybrid_strategy(
        strategies=[
            StrategyType.CHAIN_OF_THOUGHT,
            StrategyType.TREE_OF_THOUGHTS,
            StrategyType.SELF_CONSISTENCY,
            StrategyType.META_PROMPTING
        ],
        weights=[0.8, 1.0, 0.9, 0.7]  # ToT gets highest weight
    )
    
    context = PromptContext(
        domain="theoretical_computer_science",
        task_type="proof",
        complexity="paradoxical"
    )
    
    enhanced = hybrid(prompt, context)
    
    print("Millennium Problem:", prompt)
    print("\nHybrid Strategy Applied:", enhanced[:600] + "...")
    
def example_performance_analysis():
    """Analyze strategy performance."""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Performance Analysis")
    print("=" * 60)
    
    orchestrator = create_orchestrator()
    
    # Run multiple enhancements
    test_prompts = [
        ("Simple math problem", "mathematics", "simple"),
        ("Complex algorithm design", "algorithms", "complex"),
        ("Ethical dilemma", "philosophy", "complex"),
        ("Creative writing", "literature", "moderate")
    ]
    
    for prompt, domain, complexity in test_prompts:
        context = PromptContext(
            domain=domain,
            task_type="general",
            complexity=complexity
        )
        orchestrator.apply_strategies(prompt, context)
    
    # Analyze performance
    analysis = orchestrator.analyze_performance()
    
    print("Performance Analysis:")
    print(f"Total Executions: {analysis['total_executions']}")
    print(f"Average Enhancement Ratio: {analysis['average_enhancement_ratio']:.2f}x")
    print(f"Complexity Distribution: {analysis['complexity_distribution']}")
    print(f"Domain Distribution: {analysis['domain_distribution']}")

def main():
    """Run all examples."""
    print("\n" + "🚀 MASTER PROMPT STRATEGIES DEMONSTRATION 🚀" + "\n")
    
    example_simple_enhancement()
    example_complex_problem()
    example_ethical_ai()
    example_creative_solution()
    example_self_improving()
    example_hybrid_strategy()
    example_performance_analysis()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()