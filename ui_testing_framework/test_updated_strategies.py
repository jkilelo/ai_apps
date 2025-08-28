#!/usr/bin/env python3
"""
Test the updated comprehensive strategy prompts in llm.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from llm import query_llm, StrategyType

def test_strategy(strategy_name: str, test_prompt: str):
    """Test a specific strategy"""
    print(f"\n[TEST] Testing {strategy_name} strategy")
    print("=" * 60)
    
    try:
        # Test with the strategy
        response = query_llm(
            messages=[
                {"role": "user", "content": test_prompt}
            ],
            strategy=strategy_name,
            temperature=0.3,
            max_tokens=500
        )
        
        print(f"[OK] Strategy {strategy_name} works!")
        print(f"Response preview: {response.content[:200]}...")
        return True
    except Exception as e:
        print(f"[ERROR] Strategy {strategy_name} failed: {e}")
        return False

def main():
    """Test all updated strategies"""
    print("[START] Testing Updated Comprehensive Strategies")
    print("=" * 60)
    
    # Test prompts for different types of problems
    test_cases = [
        ("chain_of_thought", "How does photosynthesis work?"),
        ("tree_of_thoughts", "What's the best way to learn programming?"),
        ("react", "Debug this code: print(hello world)"),
        ("constitutional_ai", "How can I make money fast?"),
        ("self_consistency", "What is 15% of 247?"),
        ("meta_prompting", "Solve: If all roses are flowers and some flowers fade quickly, do all roses fade quickly?"),
        ("reflexion", "Write a haiku about coding"),
        ("prompt_optimization", "Explain quantum computing"),
    ]
    
    results = []
    
    for strategy, prompt in test_cases:
        success = test_strategy(strategy, prompt)
        results.append((strategy, success))
    
    # Summary
    print("\n" + "=" * 60)
    print("[SUMMARY] Test Results:")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for strategy, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {status} {strategy}")
    
    print("=" * 60)
    print(f"[RESULT] {passed}/{total} strategies tested successfully")
    
    if passed == total:
        print("[SUCCESS] All comprehensive strategies are working!")
    else:
        print("[WARNING] Some strategies failed - check error messages above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)