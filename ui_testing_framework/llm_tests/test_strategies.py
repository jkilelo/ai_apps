#!/usr/bin/env python3
"""
Strategy Tests - All 21 Master Prompt Strategies
QA Focus: Validate each strategy implementation, verify output differences
Senior QA: Strategy effectiveness, prompt augmentation validation
"""

import sys
from pathlib import Path
from typing import Dict, List
import hashlib

sys.path.insert(0, str(Path(__file__).parent.parent))

from llm import query_llm, StrategyType
from test_config import TestRunner, assert_response_valid


class StrategyTests:
    """Test all 21 master prompt strategies"""
    
    def __init__(self):
        self.runner = TestRunner()
        self.test_prompt = "Explain how a computer works"
        self.simple_messages = [{"role": "user", "content": self.test_prompt}]
    
    def _test_strategy(self, strategy: StrategyType, expected_patterns: List[str] = None):
        """Generic strategy test"""
        response = query_llm(
            self.simple_messages,
            strategy=strategy.value,
            max_tokens=500  # Limit for faster testing
        )
        
        assert_response_valid(response, min_length=50)
        assert response.strategy_used == strategy, \
            f"Strategy mismatch: expected {strategy}, got {response.strategy_used}"
        
        # Check for expected patterns in response
        if expected_patterns:
            content_lower = response.content.lower()
            for pattern in expected_patterns:
                if pattern.lower() not in content_lower:
                    print(f"    Warning: Expected pattern '{pattern}' not found")
        
        return response
    
    # ==================== CORE REASONING STRATEGIES ====================
    
    def test_chain_of_thought(self):
        """Test Chain of Thought strategy"""
        response = self._test_strategy(
            StrategyType.CHAIN_OF_THOUGHT,
            ["step", "first", "then", "finally"]
        )
        # CoT should have step-by-step reasoning
        assert len(response.content) > 100, "CoT response too short"
    
    def test_tree_of_thoughts(self):
        """Test Tree of Thoughts strategy"""
        response = self._test_strategy(
            StrategyType.TREE_OF_THOUGHTS,
            ["path", "approach", "alternative"]
        )
        # ToT should explore multiple paths
        assert len(response.content) > 150, "ToT response too short"
    
    def test_graph_of_thoughts(self):
        """Test Graph of Thoughts strategy"""
        response = self._test_strategy(
            StrategyType.GRAPH_OF_THOUGHTS,
            ["node", "relationship", "connection", "graph"]
        )
        assert len(response.content) > 100, "GoT response too short"
    
    # ==================== PROBLEM DECOMPOSITION ====================
    
    def test_least_to_most(self):
        """Test Least to Most strategy"""
        response = self._test_strategy(
            StrategyType.LEAST_TO_MOST,
            ["simple", "basic", "complex", "build"]
        )
        assert len(response.content) > 100, "Least-to-Most response too short"
    
    def test_step_back(self):
        """Test Step Back strategy"""
        response = self._test_strategy(
            StrategyType.STEP_BACK,
            ["principle", "category", "general"]
        )
        assert len(response.content) > 80, "Step Back response too short"
    
    def test_decomposed(self):
        """Test Decomposed strategy"""
        response = self._test_strategy(
            StrategyType.DECOMPOSED,
            ["sub-problem", "component", "solve", "combine"]
        )
        assert len(response.content) > 100, "Decomposed response too short"
    
    # ==================== KNOWLEDGE ENHANCEMENT ====================
    
    def test_retrieval_augmented(self):
        """Test Retrieval Augmented Generation"""
        # Provide context for RAG
        messages = [{"role": "user", "content": "What is quantum computing?"}]
        
        response = query_llm(
            messages,
            strategy=StrategyType.RETRIEVAL_AUGMENTED.value,
            knowledge="Quantum computers use qubits instead of bits.",
            max_tokens=500
        )
        
        assert_response_valid(response)
        assert response.strategy_used == StrategyType.RETRIEVAL_AUGMENTED
    
    def test_generated_knowledge(self):
        """Test Generated Knowledge strategy"""
        response = self._test_strategy(
            StrategyType.GENERATED_KNOWLEDGE,
            ["knowledge", "information", "relevant"]
        )
        assert len(response.content) > 100, "Generated Knowledge response too short"
    
    def test_knowledge_graph(self):
        """Test Knowledge Graph strategy"""
        response = self._test_strategy(
            StrategyType.KNOWLEDGE_GRAPH,
            ["entity", "relation", "structure"]
        )
        assert len(response.content) > 100, "Knowledge Graph response too short"
    
    # ==================== SELF-IMPROVEMENT ====================
    
    def test_self_consistency(self):
        """Test Self-Consistency strategy"""
        response = self._test_strategy(
            StrategyType.SELF_CONSISTENCY,
            ["solution", "approach", "vote", "best"]
        )
        # Should generate multiple solutions
        assert len(response.content) > 150, "Self-Consistency response too short"
    
    def test_self_refine(self):
        """Test Self-Refine strategy"""
        response = self._test_strategy(
            StrategyType.SELF_REFINE,
            ["initial", "critique", "refine", "improve"]
        )
        assert len(response.content) > 100, "Self-Refine response too short"
    
    def test_self_verification(self):
        """Test Self-Verification strategy"""
        response = self._test_strategy(
            StrategyType.SELF_VERIFICATION,
            ["verify", "check", "validate", "correct"]
        )
        assert len(response.content) > 100, "Self-Verification response too short"
    
    # ==================== REASONING FRAMEWORKS ====================
    
    def test_react(self):
        """Test ReAct framework"""
        response = self._test_strategy(
            StrategyType.REACT,
            ["thought", "action", "observation"]
        )
        assert len(response.content) > 100, "ReAct response too short"
    
    def test_reflexion(self):
        """Test Reflexion strategy"""
        response = self._test_strategy(
            StrategyType.REFLEXION,
            ["attempt", "reflect", "learn", "improve"]
        )
        assert len(response.content) > 100, "Reflexion response too short"
    
    def test_chain_of_verification(self):
        """Test Chain of Verification"""
        response = self._test_strategy(
            StrategyType.CHAIN_OF_VERIFICATION,
            ["step", "verify", "evidence", "proceed"]
        )
        assert len(response.content) > 100, "Chain of Verification response too short"
    
    # ==================== ADVANCED REASONING ====================
    
    def test_hypothetical_document(self):
        """Test Hypothetical Document Embeddings"""
        response = self._test_strategy(
            StrategyType.HYPOTHETICAL_DOCUMENT,
            ["document", "contain", "perfect", "resource"]
        )
        assert len(response.content) > 100, "Hypothetical Document response too short"
    
    def test_analogical_reasoning(self):
        """Test Analogical Reasoning"""
        response = self._test_strategy(
            StrategyType.ANALOGICAL_REASONING,
            ["similar", "analogy", "adapt", "compare"]
        )
        assert len(response.content) > 100, "Analogical Reasoning response too short"
    
    def test_socratic_method(self):
        """Test Socratic Method"""
        response = self._test_strategy(
            StrategyType.SOCRATIC_METHOD,
            ["question", "answer", "why", "what"]
        )
        assert len(response.content) > 100, "Socratic Method response too short"
    
    # ==================== META STRATEGIES ====================
    
    def test_meta_prompting(self):
        """Test Meta-Prompting"""
        response = self._test_strategy(
            StrategyType.META_PROMPTING,
            ["task", "problem", "strategy", "apply"]
        )
        assert len(response.content) > 100, "Meta-Prompting response too short"
    
    def test_prompt_optimization(self):
        """Test Prompt Optimization"""
        response = self._test_strategy(
            StrategyType.PROMPT_OPTIMIZATION,
            ["optimize", "clarify", "structure", "improve"]
        )
        assert len(response.content) > 100, "Prompt Optimization response too short"
    
    def test_constitutional_ai(self):
        """Test Constitutional AI"""
        response = query_llm(
            self.simple_messages,
            strategy=StrategyType.CONSTITUTIONAL_AI.value,
            principles=["Be helpful", "Be accurate", "Be concise"],
            max_tokens=500
        )
        
        assert_response_valid(response)
        assert response.strategy_used == StrategyType.CONSTITUTIONAL_AI
        assert len(response.content) > 50, "Constitutional AI response too short"
    
    # ==================== STRATEGY COMPARISON TESTS ====================
    
    def test_strategy_output_differences(self):
        """Test that different strategies produce different outputs"""
        strategies_to_compare = [
            StrategyType.CHAIN_OF_THOUGHT,
            StrategyType.TREE_OF_THOUGHTS,
            StrategyType.SELF_CONSISTENCY,
            StrategyType.META_PROMPTING,
        ]
        
        responses = {}
        hashes = set()
        
        for strategy in strategies_to_compare:
            response = query_llm(
                self.simple_messages,
                strategy=strategy.value,
                temperature=0.0,  # Deterministic
                max_tokens=300
            )
            
            # Hash the response to check uniqueness
            response_hash = hashlib.md5(response.content.encode()).hexdigest()
            hashes.add(response_hash)
            responses[strategy] = response
        
        # At least some strategies should produce different outputs
        assert len(hashes) >= 2, \
            f"Strategies produced too similar outputs: {len(hashes)} unique out of {len(strategies_to_compare)}"
    
    def test_strategy_with_complex_prompt(self):
        """Test strategies with complex, multi-part prompt"""
        complex_messages = [{
            "role": "user",
            "content": """Analyze the following scenario:
            1. A company needs to reduce costs by 20%
            2. They have 100 employees
            3. Their main expense is office rent
            4. Remote work is possible for 60% of roles
            
            Provide recommendations."""
        }]
        
        strategies = [
            StrategyType.CHAIN_OF_THOUGHT,
            StrategyType.DECOMPOSED,
            StrategyType.SELF_CONSISTENCY,
        ]
        
        for strategy in strategies:
            response = query_llm(
                complex_messages,
                strategy=strategy.value,
                max_tokens=500
            )
            
            assert_response_valid(response, min_length=100)
            assert response.strategy_used == strategy
            
            # Complex prompts should generate substantial responses
            assert len(response.content) > 200, \
                f"Strategy {strategy} produced short response for complex prompt"
    
    def test_strategy_null_effect(self):
        """Test that None strategy works (baseline)"""
        response_with = query_llm(
            self.simple_messages,
            strategy=StrategyType.CHAIN_OF_THOUGHT.value,
            max_tokens=300
        )
        
        response_without = query_llm(
            self.simple_messages,
            strategy=None,
            max_tokens=300
        )
        
        assert_response_valid(response_with)
        assert_response_valid(response_without)
        
        # Response with strategy should generally be longer/more structured
        # But both should work
        assert response_with.strategy_used == StrategyType.CHAIN_OF_THOUGHT
        assert response_without.strategy_used is None
    
    def run_all_tests(self) -> TestRunner:
        """Run all strategy tests"""
        print("\n" + "=" * 60)
        print("STRATEGY TESTS (21 Master Strategies)")
        print("=" * 60)
        
        # Test each strategy
        strategies = [
            (self.test_chain_of_thought, "chain_of_thought"),
            (self.test_tree_of_thoughts, "tree_of_thoughts"),
            (self.test_graph_of_thoughts, "graph_of_thoughts"),
            (self.test_least_to_most, "least_to_most"),
            (self.test_step_back, "step_back"),
            (self.test_decomposed, "decomposed"),
            (self.test_retrieval_augmented, "retrieval_augmented"),
            (self.test_generated_knowledge, "generated_knowledge"),
            (self.test_knowledge_graph, "knowledge_graph"),
            (self.test_self_consistency, "self_consistency"),
            (self.test_self_refine, "self_refine"),
            (self.test_self_verification, "self_verification"),
            (self.test_react, "react"),
            (self.test_reflexion, "reflexion"),
            (self.test_chain_of_verification, "chain_of_verification"),
            (self.test_hypothetical_document, "hypothetical_document"),
            (self.test_analogical_reasoning, "analogical_reasoning"),
            (self.test_socratic_method, "socratic_method"),
            (self.test_meta_prompting, "meta_prompting"),
            (self.test_prompt_optimization, "prompt_optimization"),
            (self.test_constitutional_ai, "constitutional_ai"),
        ]
        
        for test_func, name in strategies:
            self.runner.add_result(
                self.runner.run_test(test_func, name, "strategies")
            )
        
        # Comparison tests
        self.runner.add_result(
            self.runner.run_test(self.test_strategy_output_differences, "output_differences", "strategy_comparison")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_strategy_with_complex_prompt, "complex_prompt", "strategy_comparison")
        )
        self.runner.add_result(
            self.runner.run_test(self.test_strategy_null_effect, "null_strategy", "strategy_comparison")
        )
        
        return self.runner


if __name__ == "__main__":
    tests = StrategyTests()
    runner = tests.run_all_tests()
    
    # Generate and save report
    report = runner.generate_report()
    print("\n" + "=" * 60)
    print("STRATEGY TEST SUMMARY")
    print("=" * 60)
    print(f"Total Strategies Tested: 21")
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Pass Rate: {report['summary']['pass_rate']:.1f}%")
    
    runner.save_report("strategy_test_report.json")