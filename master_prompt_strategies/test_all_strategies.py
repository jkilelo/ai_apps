"""
Comprehensive Test Suite for All 21 Master Prompt Strategies
Tests loading, applying, and combining all strategies
"""

import unittest
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from strategy_orchestrator import (
    StrategyOrchestrator,
    StrategyType,
    PromptContext,
    StrategyResult
)


class TestAllStrategies(unittest.TestCase):
    """Test suite for all 21 prompt strategies."""
    
    def setUp(self):
        """Initialize orchestrator with all strategies."""
        self.orchestrator = StrategyOrchestrator()
        self.base_prompt = "Explain quantum computing"
        
        # Test context with rich metadata
        self.context = PromptContext(
            domain="science",
            task_type="explanation",
            complexity="high",
            metadata={
                'samples': 5,
                'temperature': 0.7,
                'max_depth': 3,
                'urgency': 'high',
                'audience': 'technical',
                'enable_ethics': True
            }
        )
    
    def test_all_strategies_load(self):
        """Test that all 21 strategies can be loaded."""
        all_strategies = [
            StrategyType.CHAIN_OF_THOUGHT,
            StrategyType.TREE_OF_THOUGHTS,
            StrategyType.REACT,
            StrategyType.CONSTITUTIONAL_AI,
            StrategyType.SELF_CONSISTENCY,
            StrategyType.META_PROMPTING,
            StrategyType.DEBATE,
            StrategyType.REFLEXION,
            StrategyType.SCRATCHPAD,
            StrategyType.FEW_SHOT,
            StrategyType.ZERO_SHOT,
            StrategyType.OPRO,
            StrategyType.MIXTURE_OF_EXPERTS,
            StrategyType.QUANTUM_PROMPTING,
            StrategyType.REVERSE_PROMPTING,
            StrategyType.EVOLUTIONARY_OPTIMIZATION,
            StrategyType.PSYCHOLOGICAL_TRIGGERS,
            StrategyType.UNIVERSAL_SELF_CONSISTENCY,
            StrategyType.PROGRAM_AIDED_LANGUAGE,
            StrategyType.CHAIN_OF_TABLE,
            StrategyType.META_COGNITIVE_FRAMEWORK
        ]
        
        for strategy_type in all_strategies:
            with self.subTest(strategy=strategy_type.value):
                self.orchestrator.add_strategy(strategy_type)
                self.assertIn(strategy_type.value, 
                             [s.type.value for s in self.orchestrator.strategies])
    
    def test_individual_strategy_application(self):
        """Test each strategy can be applied individually."""
        strategies_to_test = [
            (StrategyType.CHAIN_OF_THOUGHT, "step-by-step reasoning"),
            (StrategyType.TREE_OF_THOUGHTS, "exploring multiple paths"),
            (StrategyType.REACT, "reasoning and acting"),
            (StrategyType.CONSTITUTIONAL_AI, "ethical constraints"),
            (StrategyType.SELF_CONSISTENCY, "multiple samples"),
            (StrategyType.META_PROMPTING, "recursive self-improvement"),
            (StrategyType.DEBATE, "adversarial refinement"),
            (StrategyType.REFLEXION, "iterative reflection"),
            (StrategyType.SCRATCHPAD, "working memory"),
            (StrategyType.FEW_SHOT, "learning from examples"),
            (StrategyType.ZERO_SHOT, "first principles"),
            (StrategyType.OPRO, "optimization without gradients"),
            (StrategyType.MIXTURE_OF_EXPERTS, "specialized experts"),
            (StrategyType.QUANTUM_PROMPTING, "superposition of possibilities"),
            (StrategyType.REVERSE_PROMPTING, "backward from solution"),
            (StrategyType.EVOLUTIONARY_OPTIMIZATION, "genetic evolution"),
            (StrategyType.PSYCHOLOGICAL_TRIGGERS, "cognitive influence"),
            (StrategyType.UNIVERSAL_SELF_CONSISTENCY, "multiverse reasoning"),
            (StrategyType.PROGRAM_AIDED_LANGUAGE, "code generation"),
            (StrategyType.CHAIN_OF_TABLE, "tabular transformations"),
            (StrategyType.META_COGNITIVE_FRAMEWORK, "thinking about thinking")
        ]
        
        for strategy_type, expected_pattern in strategies_to_test:
            with self.subTest(strategy=strategy_type.value):
                # Clear and add single strategy
                self.orchestrator.strategies.clear()
                self.orchestrator.add_strategy(strategy_type)
                
                # Apply strategy
                result = self.orchestrator.apply(self.base_prompt, self.context)
                
                # Verify result contains strategy application
                self.assertIsNotNone(result)
                self.assertIsInstance(result, StrategyResult)
                self.assertTrue(len(result.enhanced_prompt) > len(self.base_prompt))
    
    def test_strategy_combinations(self):
        """Test combining multiple strategies."""
        test_combinations = [
            # Classic combinations
            ([StrategyType.CHAIN_OF_THOUGHT, StrategyType.SELF_CONSISTENCY],
             "Chain + Consistency"),
            
            # Advanced combinations
            ([StrategyType.TREE_OF_THOUGHTS, StrategyType.DEBATE, StrategyType.REFLEXION],
             "Tree + Debate + Reflection"),
            
            # Quantum combinations
            ([StrategyType.QUANTUM_PROMPTING, StrategyType.UNIVERSAL_SELF_CONSISTENCY],
             "Quantum + Universal"),
            
            # Optimization combinations
            ([StrategyType.EVOLUTIONARY_OPTIMIZATION, StrategyType.OPRO],
             "Evolution + OPRO"),
            
            # Meta combinations
            ([StrategyType.META_PROMPTING, StrategyType.META_COGNITIVE_FRAMEWORK],
             "Meta + Meta-Cognitive"),
            
            # Full stack
            ([StrategyType.CHAIN_OF_THOUGHT, StrategyType.TREE_OF_THOUGHTS,
              StrategyType.CONSTITUTIONAL_AI, StrategyType.QUANTUM_PROMPTING,
              StrategyType.META_COGNITIVE_FRAMEWORK],
             "Full cognitive stack")
        ]
        
        for strategies, description in test_combinations:
            with self.subTest(combination=description):
                self.orchestrator.strategies.clear()
                for strategy in strategies:
                    self.orchestrator.add_strategy(strategy)
                
                result = self.orchestrator.apply(self.base_prompt, self.context)
                
                # Verify multiple strategies were applied
                self.assertIsNotNone(result)
                self.assertEqual(len(result.strategies_applied), len(strategies))
    
    def test_complexity_based_selection(self):
        """Test automatic strategy selection based on complexity."""
        test_cases = [
            ("simple", [StrategyType.ZERO_SHOT]),
            ("medium", [StrategyType.CHAIN_OF_THOUGHT]),
            ("complex", [StrategyType.TREE_OF_THOUGHTS, StrategyType.DEBATE]),
            ("paradoxical", [StrategyType.QUANTUM_PROMPTING, StrategyType.META_COGNITIVE_FRAMEWORK])
        ]
        
        for complexity, expected_strategies in test_cases:
            with self.subTest(complexity=complexity):
                context = PromptContext(
                    domain="test",
                    task_type="analysis",
                    complexity=complexity
                )
                
                # Add all strategies
                self.orchestrator.strategies.clear()
                for strategy in StrategyType:
                    self.orchestrator.add_strategy(strategy)
                
                # Apply with smart selection
                result = self.orchestrator.apply_smart(
                    self.base_prompt, 
                    context
                )
                
                self.assertIsNotNone(result)
    
    def test_performance_metrics(self):
        """Test strategy performance measurement."""
        # Add multiple strategies
        self.orchestrator.strategies.clear()
        strategies = [
            StrategyType.CHAIN_OF_THOUGHT,
            StrategyType.QUANTUM_PROMPTING,
            StrategyType.EVOLUTIONARY_OPTIMIZATION,
            StrategyType.META_COGNITIVE_FRAMEWORK
        ]
        
        for strategy in strategies:
            self.orchestrator.add_strategy(strategy)
        
        # Apply strategies
        result = self.orchestrator.apply(self.base_prompt, self.context)
        
        # Check metrics
        self.assertIn('enhancement_factor', result.metrics)
        self.assertIn('processing_time', result.metrics)
        self.assertIn('strategy_count', result.metrics)
        self.assertEqual(result.metrics['strategy_count'], len(strategies))
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Empty prompt
        result = self.orchestrator.apply("", self.context)
        self.assertIsNotNone(result)
        
        # Very long prompt
        long_prompt = "Explain " * 1000
        result = self.orchestrator.apply(long_prompt, self.context)
        self.assertIsNotNone(result)
        
        # No strategies
        self.orchestrator.strategies.clear()
        result = self.orchestrator.apply(self.base_prompt, self.context)
        self.assertEqual(result.enhanced_prompt, self.base_prompt)
    
    def test_strategy_file_existence(self):
        """Test that all strategy markdown files exist."""
        strategy_files = [
            "01_chain_of_thought.md",
            "02_tree_of_thoughts.md",
            "03_react.md",
            "04_constitutional_ai.md",
            "05_self_consistency.md",
            "06_meta_prompting.md",
            "07_debate.md",
            "08_reflexion.md",
            "09_scratchpad.md",
            "10_few_shot.md",
            "11_zero_shot.md",
            "12_opro.md",
            "13_mixture_of_experts.md",
            "14_quantum_prompting.md",
            "15_reverse_prompting.md",
            "16_evolutionary_optimization.md",
            "17_psychological_triggers.md",
            "18_universal_self_consistency.md",
            "19_program_aided_language.md",
            "20_chain_of_table.md",
            "21_meta_cognitive_framework.md"
        ]
        
        base_path = Path(__file__).parent
        for filename in strategy_files:
            with self.subTest(file=filename):
                file_path = base_path / filename
                self.assertTrue(file_path.exists(), 
                               f"Strategy file {filename} not found")
    
    def test_enhancement_factor_calculation(self):
        """Test that enhancement factors are calculated correctly."""
        # Single strategy
        self.orchestrator.strategies.clear()
        self.orchestrator.add_strategy(StrategyType.CHAIN_OF_THOUGHT)
        result = self.orchestrator.apply(self.base_prompt, self.context)
        
        single_factor = result.metrics.get('enhancement_factor', 1)
        self.assertGreater(single_factor, 1)
        
        # Multiple strategies should have higher factor
        self.orchestrator.add_strategy(StrategyType.QUANTUM_PROMPTING)
        self.orchestrator.add_strategy(StrategyType.META_COGNITIVE_FRAMEWORK)
        result = self.orchestrator.apply(self.base_prompt, self.context)
        
        multi_factor = result.metrics.get('enhancement_factor', 1)
        self.assertGreater(multi_factor, single_factor)
    
    def test_strategy_synergy(self):
        """Test that certain strategy combinations have synergistic effects."""
        synergistic_pairs = [
            (StrategyType.CHAIN_OF_THOUGHT, StrategyType.SELF_CONSISTENCY),
            (StrategyType.TREE_OF_THOUGHTS, StrategyType.DEBATE),
            (StrategyType.QUANTUM_PROMPTING, StrategyType.UNIVERSAL_SELF_CONSISTENCY),
            (StrategyType.EVOLUTIONARY_OPTIMIZATION, StrategyType.REFLEXION)
        ]
        
        for strategy1, strategy2 in synergistic_pairs:
            with self.subTest(pair=f"{strategy1.value}+{strategy2.value}"):
                # Test individual strategies
                self.orchestrator.strategies.clear()
                self.orchestrator.add_strategy(strategy1)
                result1 = self.orchestrator.apply(self.base_prompt, self.context)
                factor1 = result1.metrics.get('enhancement_factor', 1)
                
                self.orchestrator.strategies.clear()
                self.orchestrator.add_strategy(strategy2)
                result2 = self.orchestrator.apply(self.base_prompt, self.context)
                factor2 = result2.metrics.get('enhancement_factor', 1)
                
                # Test combination
                self.orchestrator.strategies.clear()
                self.orchestrator.add_strategy(strategy1)
                self.orchestrator.add_strategy(strategy2)
                result_combined = self.orchestrator.apply(self.base_prompt, self.context)
                factor_combined = result_combined.metrics.get('enhancement_factor', 1)
                
                # Combined should be more than sum of parts (synergy)
                self.assertGreater(factor_combined, factor1 + factor2 - 1)


def run_comprehensive_tests():
    """Run all tests and generate report."""
    print("Running Comprehensive Strategy Tests...")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestAllStrategies)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate report
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.wasSuccessful():
        print("\n[SUCCESS] All 21 strategies tested successfully!")
        print("The Master Prompt Strategies Repository is fully operational!")
    else:
        print("\n[FAILURE] Some tests failed. Please review the errors above.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)