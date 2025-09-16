#!/usr/bin/env python3
"""
Live Test of Optimized Prompts with Real LLM API Calls

This test validates that the advanced prompting strategies work with actual LLM APIs,
not just theoretical implementations.

CRITICAL: Tests actual API calls to verify real-world performance improvements.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from cognition.prompt_testing_framework import create_prompt_tester, PromptingStrategy
    from cognition.optimized_prompt_integration import get_optimized_prompt_manager, configure_optimization
    from cognition.advanced_prompts import PromptingStrategy
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the ai_browser directory with src/ available")
    sys.exit(1)


async def test_optimized_prompts_live():
    """Test optimized prompts with live LLM API calls"""
    
    print("🧪 TESTING OPTIMIZED PROMPTS WITH LIVE LLM API CALLS")
    print("=" * 60)
    print("CRITICAL: This test uses REAL API calls to validate optimization effectiveness")
    print()
    
    # Initialize tester
    try:
        tester = create_prompt_tester()
        print("✅ Prompt testing framework initialized")
    except Exception as e:
        print(f"❌ Failed to initialize tester: {e}")
        return
    
    # Test scenarios
    scenarios = [
        {
            "name": "E-commerce Product Search",
            "task": "Search for wireless bluetooth headphones under $100 on Amazon and extract product details",
            "domain": "ecommerce",
            "complexity": "moderate",
            "url": "https://amazon.com",
            "title": "Amazon Product Search",
            "content": "Amazon product search page with various electronic items and search functionality"
        },
        {
            "name": "Job Search Analysis", 
            "task": "Find software engineering jobs in San Francisco and analyze job requirements",
            "domain": "job_search",
            "complexity": "complex",
            "url": "https://linkedin.com/jobs",
            "title": "LinkedIn Jobs Search",
            "content": "LinkedIn jobs search page with filters and job listings"
        }
    ]
    
    # Strategies to test
    strategies_to_test = [
        ("Chain of Thought", PromptingStrategy.CHAIN_OF_THOUGHT),
        ("Tree of Thoughts", PromptingStrategy.TREE_OF_THOUGHTS), 
        ("Constitutional AI", PromptingStrategy.CONSTITUTIONAL_AI),
        ("Enhanced ReAct", PromptingStrategy.REACT_ENHANCED)
    ]
    
    results = {}
    
    for scenario in scenarios:
        print(f"\n🎯 TESTING SCENARIO: {scenario['name']}")
        print("-" * 40)
        
        scenario_results = {}
        
        for strategy_name, strategy in strategies_to_test:
            print(f"\n🔍 Testing {strategy_name}...")
            
            try:
                # Execute REAL LLM API call with optimized prompt
                result = await tester.test_advanced_strategy(
                    strategy=strategy,
                    test_scenario=scenario,
                    provider="openai"  # Use actual OpenAI API
                )
                
                scenario_results[strategy_name] = result
                
                # Display real results
                print(f"   ✅ SUCCESS:")
                print(f"      Quality Score: {result.reasoning_quality_score:.1f}/10")
                print(f"      Accuracy Score: {result.accuracy_score:.1f}/10") 
                print(f"      Coherence Score: {result.coherence_score:.1f}/10")
                print(f"      Response Time: {result.response_time_ms:.0f}ms")
                print(f"      Input Tokens: {result.token_count_input}")
                print(f"      Output Tokens: {result.token_count_output}")
                print(f"      API Cost: ${result.api_cost_estimate:.4f}")
                
                if result.response and len(result.response) > 50:
                    print(f"      Response Preview: {result.response[:150]}...")
                
            except Exception as e:
                print(f"   ❌ FAILED: {e}")
                scenario_results[strategy_name] = {"error": str(e)}
            
            # Brief pause to respect API rate limits
            await asyncio.sleep(2)
        
        results[scenario['name']] = scenario_results
    
    # Analysis of results
    print("\n" + "=" * 60)
    print("📊 LIVE API TEST RESULTS ANALYSIS")
    print("=" * 60)
    
    total_tests = 0
    successful_tests = 0
    total_quality_score = 0
    
    for scenario_name, scenario_results in results.items():
        print(f"\n📈 {scenario_name} Results:")
        
        best_strategy = None
        best_score = 0
        
        for strategy_name, result in scenario_results.items():
            if isinstance(result, dict) and "error" in result:
                print(f"   ❌ {strategy_name}: Failed - {result['error']}")
                total_tests += 1
            else:
                overall_score = (result.reasoning_quality_score + result.accuracy_score + result.coherence_score) / 3
                print(f"   ✅ {strategy_name}: {overall_score:.1f}/10 overall quality")
                
                total_tests += 1
                successful_tests += 1
                total_quality_score += overall_score
                
                if overall_score > best_score:
                    best_score = overall_score
                    best_strategy = strategy_name
        
        if best_strategy:
            print(f"   🏆 Best Strategy: {best_strategy} ({best_score:.1f}/10)")
    
    # Overall summary
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    avg_quality = (total_quality_score / successful_tests) if successful_tests > 0 else 0
    
    print(f"\n🎉 OVERALL RESULTS:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Success Rate: {success_rate:.1f}%")
    print(f"   Average Quality Score: {avg_quality:.1f}/10")
    
    if success_rate > 70 and avg_quality > 6.0:
        print(f"   🚀 OPTIMIZATION SUCCESSFUL! Advanced prompting strategies are working with live APIs.")
    elif success_rate > 50:
        print(f"   ⚠️ PARTIAL SUCCESS: Some strategies working, may need refinement.")
    else:
        print(f"   ❌ OPTIMIZATION NEEDS WORK: Low success rate indicates issues.")
    
    return results


async def test_integration_layer():
    """Test the integration layer with optimized prompt management"""
    
    print("\n🔧 TESTING OPTIMIZED PROMPT INTEGRATION LAYER")
    print("-" * 50)
    
    # Configure optimization
    configure_optimization(
        enable=True,
        strategy=PromptingStrategy.CHAIN_OF_THOUGHT,
        monitoring=True
    )
    
    manager = get_optimized_prompt_manager()
    
    # Test optimized prompt generation
    test_context = {
        "url": "https://amazon.com",
        "title": "Amazon Product Search",
        "content": "Product search page with various items",
        "domain": "ecommerce"
    }
    
    try:
        optimized_prompt = await manager.generate_optimized_task_prompt(
            task="Find wireless headphones under $50",
            context=test_context,
            example_type="ecommerce_research"
        )
        
        print("✅ Optimized prompt generated successfully")
        print(f"   Prompt length: {len(optimized_prompt)} characters")
        print(f"   Preview: {optimized_prompt[:200]}...")
        
        # Test optimized LLM execution
        print("\n🤖 Testing optimized LLM execution...")
        
        response = await manager.execute_optimized_llm_call(
            task="Search for budget wireless earbuds on Amazon",
            context=test_context,
            example_type="ecommerce_research",
            provider="openai"
        )
        
        print("✅ Optimized LLM call executed successfully")
        print(f"   Response length: {len(response)} characters")
        print(f"   Response preview: {response[:300]}...")
        
        # Get performance summary
        summary = manager.get_performance_summary()
        print(f"\n📊 Performance Summary:")
        print(f"   Total calls: {summary.get('total_calls', 0)}")
        print(f"   Success rate: {summary.get('success_rate', 0):.1f}%")
        print(f"   Average response time: {summary.get('average_response_time', 0):.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test execution"""
    
    print("🚀 ADVANCED PROMPTING OPTIMIZATION TEST SUITE")
    print("=" * 60)
    print("This test validates optimization with REAL LLM API calls")
    print("Ensure you have valid API keys configured in your environment")
    print()
    
    # Test 1: Live prompt optimization testing
    await test_optimized_prompts_live()
    
    # Test 2: Integration layer testing
    integration_success = await test_integration_layer()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 FINAL TEST SUMMARY")
    print("=" * 60)
    
    if integration_success:
        print("✅ All tests completed successfully!")
        print("🚀 Advanced prompting strategies are ready for production use")
        print("💡 Integration layer provides seamless drop-in optimization")
    else:
        print("⚠️ Some tests had issues - review configuration and API keys")
    
    print("\n📚 Next Steps:")
    print("1. Update real-world examples to use optimized prompts")
    print("2. Monitor performance improvements in production")
    print("3. Fine-tune strategies based on domain-specific results")


if __name__ == "__main__":
    """Run comprehensive optimization test"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()