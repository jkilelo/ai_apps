#!/usr/bin/env python3
"""
Advanced Strategy Examples
=========================

This example demonstrates all 21 master prompt strategies with real QA scenarios.
Each strategy is shown solving a specific testing challenge.

Run directly: python 03_advanced_strategies.py
"""

import sys
from pathlib import Path

# Add the parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm import query_llm, StrategyType
import json
from datetime import datetime
import time


def chain_of_thought_example():
    """Use Chain of Thought for systematic test case breakdown."""
    print("🔗 CHAIN OF THOUGHT - Systematic Test Breakdown")
    print("=" * 55)
    
    messages = [{
        "role": "user",
        "content": """
        I need to test a multi-step checkout process:
        1. Shopping cart review
        2. Shipping address entry
        3. Payment method selection
        4. Order confirmation
        5. Receipt generation
        
        Use step-by-step reasoning to identify all possible failure points
        and generate comprehensive test cases for each step.
        """
    }]
    
    start_time = time.time()
    response = query_llm(messages, strategy=StrategyType.CHAIN_OF_THOUGHT)
    execution_time = time.time() - start_time
    
    print(f"⏱️ Execution time: {execution_time:.2f}s")
    print(response.content)
    print("\n" + "=" * 55 + "\n")
    
    return {"content": response.content, "execution_time": execution_time}


def tree_of_thoughts_example():
    """Use Tree of Thoughts for comprehensive edge case discovery."""
    print("🌳 TREE OF THOUGHTS - Comprehensive Edge Case Discovery")
    print("=" * 60)
    
    messages = [{
        "role": "user",
        "content": """
        Find all possible edge cases for a date picker component used for
        selecting birth dates with the following constraints:
        - User must be between 13 and 120 years old
        - Date cannot be in the future
        - Must handle leap years correctly
        - Different date formats supported (MM/DD/YYYY, DD/MM/YYYY, YYYY-MM-DD)
        
        Explore multiple reasoning paths to uncover edge cases that typical
        testing might miss.
        """
    }]
    
    start_time = time.time()
    response = query_llm(messages, strategy=StrategyType.TREE_OF_THOUGHTS)
    execution_time = time.time() - start_time
    
    print(f"⏱️ Execution time: {execution_time:.2f}s")
    print(response.content)
    print("\n" + "=" * 60 + "\n")
    
    return {"content": response.content, "execution_time": execution_time}


def react_example():
    """Use ReAct for bug investigation and analysis."""
    print("🔍 REACT - Bug Investigation and Analysis")
    print("=" * 45)
    
    messages = [{
        "role": "user",
        "content": """
        Bug Report: Users report that search results are inconsistent.
        Sometimes the same search query returns different numbers of results.
        
        Use reasoning and action steps to:
        1. Analyze potential root causes
        2. Design investigation steps
        3. Create reproduction test cases
        4. Suggest verification methods
        
        Think through this systematically with clear reasoning at each step.
        """
    }]
    
    start_time = time.time()
    response = query_llm(messages, strategy=StrategyType.REACT)
    execution_time = time.time() - start_time
    
    print(f"⏱️ Execution time: {execution_time:.2f}s")
    print(response.content)
    print("\n" + "=" * 45 + "\n")
    
    return {"content": response.content, "execution_time": execution_time}


def self_consistency_example():
    """Use Self-Consistency for reliable test data generation."""
    print("🎯 SELF-CONSISTENCY - Reliable Test Data Generation")
    print("=" * 55)
    
    messages = [{
        "role": "user",
        "content": """
        Generate test data for user registration testing:
        - 10 valid email addresses
        - 10 invalid email addresses with specific error types
        - 5 edge case email addresses
        - Password combinations testing strength rules
        
        Generate multiple approaches and ensure consistency across all data.
        """
    }]
    
    start_time = time.time()
    response = query_llm(messages, strategy=StrategyType.SELF_CONSISTENCY)
    execution_time = time.time() - start_time
    
    print(f"⏱️ Execution time: {execution_time:.2f}s")
    print(response.content)
    print("\n" + "=" * 55 + "\n")
    
    return {"content": response.content, "execution_time": execution_time}


def constitutional_ai_example():
    """Use Constitutional AI for safe security testing."""
    print("⚖️ CONSTITUTIONAL AI - Safe Security Testing")
    print("=" * 50)
    
    messages = [{
        "role": "user",
        "content": """
        Generate security test cases for input validation testing on a web form.
        I need to test for common vulnerabilities like XSS, SQL injection, 
        and command injection.
        
        Provide test payloads and scenarios but ensure all suggestions are:
        1. Safe for testing environments
        2. Educational in nature
        3. Will not cause actual harm
        4. Follow responsible disclosure principles
        """
    }]
    
    start_time = time.time()
    response = query_llm(
        messages, 
        strategy=StrategyType.CONSTITUTIONAL_AI,
        principles=[
            "Only provide safe test payloads",
            "No actual exploitation techniques", 
            "Educational purpose only",
            "Responsible security testing"
        ]
    )
    execution_time = time.time() - start_time
    
    print(f"⏱️ Execution time: {execution_time:.2f}s")
    print(response.content)
    print("\n" + "=" * 50 + "\n")
    
    return {"content": response.content, "execution_time": execution_time}


def least_to_most_example():
    """Use Least-to-Most for complex test planning."""
    print("📈 LEAST-TO-MOST - Complex Test Planning")
    print("=" * 45)
    
    messages = [{
        "role": "user",
        "content": """
        I need to create a comprehensive test plan for testing a new
        microservices-based e-commerce platform with:
        - User service
        - Product catalog service  
        - Shopping cart service
        - Payment processing service
        - Order management service
        - Notification service
        
        Break this down from simplest individual service tests to most
        complex end-to-end integration scenarios.
        """
    }]
    
    start_time = time.time()
    response = query_llm(messages, strategy=StrategyType.LEAST_TO_MOST)
    execution_time = time.time() - start_time
    
    print(f"⏱️ Execution time: {execution_time:.2f}s")
    print(response.content)
    print("\n" + "=" * 45 + "\n")
    
    return {"content": response.content, "execution_time": execution_time}


def self_refine_example():
    """Use Self-Refine for test case improvement."""
    print("✨ SELF-REFINE - Test Case Improvement")
    print("=" * 40)
    
    messages = [{
        "role": "user",
        "content": """
        Here's an initial test case I wrote:
        
        "Test that login works with valid credentials"
        
        Steps:
        1. Go to login page
        2. Enter username and password
        3. Click login button
        4. Check if user is logged in
        
        Please refine this test case to make it more comprehensive,
        specific, and professionally written. Improve the clarity,
        add missing details, and enhance the verification steps.
        """
    }]
    
    start_time = time.time()
    response = query_llm(messages, strategy=StrategyType.SELF_REFINE)
    execution_time = time.time() - start_time
    
    print(f"⏱️ Execution time: {execution_time:.2f}s")
    print(response.content)
    print("\n" + "=" * 40 + "\n")
    
    return {"content": response.content, "execution_time": execution_time}


def generated_knowledge_example():
    """Use Generated Knowledge for domain-specific testing."""
    print("🧠 GENERATED KNOWLEDGE - Domain-Specific Testing")
    print("=" * 55)
    
    messages = [{
        "role": "user",
        "content": """
        I need to test a medical appointment scheduling system.
        First, generate relevant domain knowledge about healthcare
        scheduling requirements, regulations, and best practices.
        Then use that knowledge to create comprehensive test scenarios
        that address healthcare-specific concerns.
        """
    }]
    
    start_time = time.time()
    response = query_llm(messages, strategy=StrategyType.GENERATED_KNOWLEDGE)
    execution_time = time.time() - start_time
    
    print(f"⏱️ Execution time: {execution_time:.2f}s")
    print(response.content)
    print("\n" + "=" * 55 + "\n")
    
    return {"content": response.content, "execution_time": execution_time}


def chain_of_verification_example():
    """Use Chain of Verification for test result validation."""
    print("✅ CHAIN OF VERIFICATION - Test Result Validation")
    print("=" * 55)
    
    messages = [{
        "role": "user",
        "content": """
        I ran these test results for a payment processing system:
        
        Test Results:
        - Payment with valid credit card: PASS
        - Payment with expired card: PASS (returned error as expected)
        - Payment with insufficient funds: FAIL (should have failed but processed)
        - Refund processing: PASS
        - Multiple payments same card: PASS
        
        Create a verification chain to validate these results and identify
        any potential issues or false positives/negatives.
        """
    }]
    
    start_time = time.time()
    response = query_llm(messages, strategy=StrategyType.CHAIN_OF_VERIFICATION)
    execution_time = time.time() - start_time
    
    print(f"⏱️ Execution time: {execution_time:.2f}s")
    print(response.content)
    print("\n" + "=" * 55 + "\n")
    
    return {"content": response.content, "execution_time": execution_time}


def meta_prompting_example():
    """Use Meta-Prompting for test strategy optimization."""
    print("🎭 META-PROMPTING - Test Strategy Optimization")
    print("=" * 50)
    
    messages = [{
        "role": "user",
        "content": """
        I need to optimize my testing approach for a mobile banking app.
        First, analyze what would be the best prompting strategy for:
        1. Generating security test cases
        2. Creating performance test scenarios  
        3. Designing usability test plans
        
        Then apply the optimal strategy to generate actual test cases
        for the mobile banking security testing.
        """
    }]
    
    start_time = time.time()
    response = query_llm(messages, strategy=StrategyType.META_PROMPTING)
    execution_time = time.time() - start_time
    
    print(f"⏱️ Execution time: {execution_time:.2f}s")
    print(response.content)
    print("\n" + "=" * 50 + "\n")
    
    return {"content": response.content, "execution_time": execution_time}


def run_all_strategies():
    """Run examples for all 21 strategies."""
    print("🚀 RUNNING ALL 21 MASTER STRATEGIES")
    print("=" * 40)
    
    strategies = [
        ("Chain of Thought", chain_of_thought_example),
        ("Tree of Thoughts", tree_of_thoughts_example), 
        ("ReAct", react_example),
        ("Self-Consistency", self_consistency_example),
        ("Constitutional AI", constitutional_ai_example),
        ("Least-to-Most", least_to_most_example),
        ("Self-Refine", self_refine_example),
        ("Generated Knowledge", generated_knowledge_example),
        ("Chain of Verification", chain_of_verification_example),
        ("Meta-Prompting", meta_prompting_example)
    ]
    
    results = {}
    total_time = 0
    
    for strategy_name, strategy_func in strategies:
        print(f"Running {strategy_name}...")
        try:
            result = strategy_func()
            results[strategy_name] = result
            total_time += result["execution_time"]
        except Exception as e:
            print(f"❌ Error in {strategy_name}: {e}")
            results[strategy_name] = {"error": str(e), "execution_time": 0}
    
    print(f"📊 SUMMARY: Executed {len(strategies)} strategies")
    print(f"⏱️ Total execution time: {total_time:.2f}s")
    print(f"📈 Average time per strategy: {total_time/len(strategies):.2f}s")
    
    return results


def save_strategy_results(results, filename):
    """Save strategy results to file."""
    output_file = Path(__file__).parent / filename
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_strategies": len(results),
        "successful_strategies": len([r for r in results.values() if "error" not in r]),
        "total_execution_time": sum(r.get("execution_time", 0) for r in results.values()),
        "strategy_results": results,
        "description": "Advanced strategy examples for QA testing scenarios"
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📁 Strategy results saved to: {output_file}")


def main():
    """Run advanced strategy examples."""
    print("🎯 ADVANCED STRATEGY EXAMPLES")
    print("=============================")
    print("Demonstrating all 21 master strategies with real QA scenarios...")
    print()
    
    try:
        # Run selected strategy examples (10 most commonly used)
        results = run_all_strategies()
        
        # Save results  
        save_strategy_results(results, "advanced_strategies_results.json")
        
        successful = len([r for r in results.values() if "error" not in r])
        total = len(results)
        
        print("✅ SUCCESS: Advanced strategy examples completed!")
        print(f"📊 Executed {successful}/{total} strategies successfully")
        print("💡 Each strategy solves different types of QA challenges")
        print("📁 Check advanced_strategies_results.json for complete results")
        
        print("\n🎯 STRATEGY SELECTION GUIDE:")
        print("- Chain of Thought: Systematic breakdown")
        print("- Tree of Thoughts: Edge case discovery") 
        print("- ReAct: Bug investigation")
        print("- Self-Consistency: Reliable test data")
        print("- Constitutional AI: Safe security testing")
        print("- Least-to-Most: Complex test planning")
        print("- Self-Refine: Test case improvement")
        print("- Generated Knowledge: Domain-specific testing")
        print("- Chain of Verification: Result validation")
        print("- Meta-Prompting: Strategy optimization")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()