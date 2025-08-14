#!/usr/bin/env python3
"""
Enhanced Strategy Orchestrator v2.0
Integrates CODER Agent patterns with Master Prompt Strategies

This implementation demonstrates the practical integration of:
- CODER's metacognition and quality gates
- Contract-driven prompt engineering
- Progressive enhancement patterns
- Test-driven prompt development
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
import hashlib
from datetime import datetime
from abc import ABC, abstractmethod

# Pydantic for contracts (following CODER pattern)
from pydantic import BaseModel, Field, field_validator, ConfigDict


# ============================================================================
# CONTRACTS (CODER Pattern: Boundary validation)
# ============================================================================

class ConfidenceLevel(Enum):
    """From CODER's metacognition - confidence levels"""
    CERTAIN = 1.0
    VERY_CONFIDENT = 0.9
    CONFIDENT = 0.7
    SOMEWHAT_CONFIDENT = 0.5
    UNCERTAIN = 0.3
    SPECULATION = 0.1


class SafetyLevel(Enum):
    """From CODER's safety contract"""
    SAFE = 1
    CAUTION = 2
    RESTRICTED = 3
    REFUSED = 4


class ComplexityLevel(str, Enum):
    """Prompt complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    PARADOXICAL = "paradoxical"


class PromptContract(BaseModel):
    """Contract for prompt generation - CODER pattern applied to prompts"""
    model_config = ConfigDict(extra="forbid")  # Strict validation
    
    # Quality requirements
    min_clarity: float = Field(0.8, ge=0.0, le=1.0)
    max_complexity: int = Field(18, gt=0)
    min_confidence: float = Field(0.6, ge=0.0, le=1.0)
    
    # Safety requirements
    safety_level: SafetyLevel = Field(SafetyLevel.SAFE)
    forbidden_patterns: List[str] = Field(default_factory=list)
    
    # Strategy requirements
    required_strategies: List[str] = Field(default_factory=list)
    excluded_strategies: List[str] = Field(default_factory=list)
    
    # Performance requirements
    max_tokens: int = Field(4000, gt=0)
    max_processing_time: float = Field(5.0, gt=0)  # seconds
    
    @field_validator('forbidden_patterns')
    def validate_patterns(cls, v):
        """Ensure patterns are non-empty strings"""
        return [p for p in v if p and isinstance(p, str)]


class PromptResult(BaseModel):
    """Result of prompt enhancement - structured output"""
    original_prompt: str
    enhanced_prompt: str
    strategies_applied: List[str]
    confidence: float
    safety_assessment: SafetyLevel
    complexity_score: int
    quality_metrics: Dict[str, float]
    processing_time: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# QUALITY GATES (CODER Pattern: Stop points)
# ============================================================================

class QualityGate(ABC):
    """Abstract base for quality gates"""
    
    @abstractmethod
    def check(self, prompt: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if prompt passes gate. Returns (passed, message)"""
        pass


class ClarityGate(QualityGate):
    """Ensures prompt clarity meets minimum threshold"""
    
    def __init__(self, min_score: float = 0.8):
        self.min_score = min_score
    
    def check(self, prompt: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        # Simplified clarity check
        ambiguous_terms = ["something", "stuff", "it", "thing", "whatever"]
        clarity_score = 1.0
        
        for term in ambiguous_terms:
            if term in prompt.lower():
                clarity_score -= 0.15
        
        passed = clarity_score >= self.min_score
        message = f"Clarity: {clarity_score:.2f} (min: {self.min_score})"
        return passed, message


class ComplexityGate(QualityGate):
    """Ensures prompt complexity is within bounds"""
    
    def __init__(self, max_score: int = 18):
        self.max_score = max_score
    
    def check(self, prompt: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        # CODER's complexity formula adapted
        strategies_used = len(context.get("strategies", []))
        depth = context.get("reasoning_depth", 1)
        tokens = len(prompt.split())
        
        complexity = (strategies_used * 6) + (depth * 4) + (tokens // 200)
        
        passed = complexity <= self.max_score
        message = f"Complexity: {complexity} (max: {self.max_score})"
        return passed, message


class SafetyGate(QualityGate):
    """Ensures prompt is safe - from CODER's safety contract"""
    
    UNSAFE_PATTERNS = [
        "hack", "exploit", "malicious", "attack", "bypass security",
        "steal", "phishing", "malware", "virus", "trojan"
    ]
    
    def check(self, prompt: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        prompt_lower = prompt.lower()
        
        for pattern in self.UNSAFE_PATTERNS:
            if pattern in prompt_lower:
                return False, f"Unsafe pattern detected: {pattern}"
        
        return True, "Safety check passed"


# ============================================================================
# METACOGNITION (Direct integration with CODER's approach)
# ============================================================================

class MetaCognitiveMonitor:
    """
    Monitors prompt enhancement process - inspired by CODER's MetacognitionEngine
    Thinks about thinking during prompt generation
    """
    
    def __init__(self):
        self.monitoring_history = []
        self.quality_metrics = {
            "coherence": 0.0,
            "relevance": 0.0,
            "effectiveness": 0.0,
            "safety": 1.0
        }
        self.cognitive_load = 0.0
        self.loop_detector = []
    
    async def assess_understanding(self, prompt: str) -> Dict[str, Any]:
        """Layer 1: Assess understanding of the prompt request"""
        assessment = {
            "clarity": self._assess_clarity(prompt),
            "intent_confidence": self._assess_intent_confidence(prompt),
            "capability_match": 1.0,  # We can enhance any prompt
            "concerns": []
        }
        
        # Meta-assessment: Am I understanding correctly?
        if assessment["clarity"] < 0.6:
            assessment["concerns"].append("Low clarity - may need clarification")
        
        if assessment["intent_confidence"] < 0.5:
            assessment["concerns"].append("Uncertain about true intent")
        
        overall_confidence = (assessment["clarity"] + assessment["intent_confidence"]) / 2
        assessment["confidence"] = overall_confidence
        
        self.monitoring_history.append({
            "type": "understanding",
            "assessment": assessment,
            "timestamp": time.time()
        })
        
        return assessment
    
    async def monitor_enhancement(self, strategies_applied: List[str]) -> Dict[str, Any]:
        """Layer 2: Monitor enhancement quality in real-time"""
        monitoring = {
            "needs_adjustment": False,
            "adjustments": [],
            "warnings": []
        }
        
        # Check for loops
        if self._detect_loop(strategies_applied):
            monitoring["needs_adjustment"] = True
            monitoring["adjustments"].append("break_loop")
            monitoring["warnings"].append("Strategy loop detected")
        
        # Check cognitive load
        self.cognitive_load = len(strategies_applied) / 10.0
        if self.cognitive_load > 0.8:
            monitoring["needs_adjustment"] = True
            monitoring["adjustments"].append("simplify")
            monitoring["warnings"].append("High cognitive load")
        
        return monitoring
    
    async def final_review(self, result: PromptResult) -> Dict[str, Any]:
        """Layer 3: Final review before returning enhanced prompt"""
        review = {
            "approved": True,
            "concerns": [],
            "confidence": result.confidence
        }
        
        # Quality checks
        if result.confidence < 0.6:
            review["concerns"].append("Low confidence in enhancement")
        
        if result.complexity_score > 18:
            review["concerns"].append("Complexity too high")
        
        if result.safety_assessment != SafetyLevel.SAFE:
            review["approved"] = False
            review["concerns"].append("Safety concerns detected")
        
        return review
    
    def _assess_clarity(self, prompt: str) -> float:
        """Assess prompt clarity"""
        # Simplified - in production would use NLP
        score = 1.0
        if len(prompt.split()) < 3:
            score -= 0.3
        if "?" not in prompt and "." not in prompt:
            score -= 0.2
        return max(0.0, score)
    
    def _assess_intent_confidence(self, prompt: str) -> float:
        """Assess confidence in understanding intent"""
        # Check for clear action words
        action_words = ["explain", "create", "analyze", "compare", "summarize"]
        has_action = any(word in prompt.lower() for word in action_words)
        return 0.9 if has_action else 0.5
    
    def _detect_loop(self, strategies: List[str]) -> bool:
        """Detect if we're in a strategy loop"""
        if len(strategies) < 3:
            return False
        
        # Check last 3 strategies for repetition
        recent = strategies[-3:]
        return len(set(recent)) == 1


# ============================================================================
# PROGRESSIVE ENHANCEMENT (CODER's fallback pattern)
# ============================================================================

class EnhancementLevel(Enum):
    """Progressive enhancement levels"""
    MINIMAL = 1      # Fast, basic enhancement
    STANDARD = 2     # Balanced enhancement
    DEEP = 3        # Comprehensive enhancement
    QUANTUM = 4     # Maximum power (all strategies)


class ProgressiveEnhancer:
    """
    Implements progressive enhancement pattern from CODER
    Start simple, add complexity as needed
    """
    
    def __init__(self):
        self.levels = {
            EnhancementLevel.MINIMAL: ["zero_shot"],
            EnhancementLevel.STANDARD: ["chain_of_thought", "self_consistency"],
            EnhancementLevel.DEEP: ["tree_of_thoughts", "debate", "reflexion"],
            EnhancementLevel.QUANTUM: ["quantum_prompting", "meta_cognitive_framework", "universal_self_consistency"]
        }
    
    def select_level(self, complexity: ComplexityLevel, time_budget: float) -> EnhancementLevel:
        """Select appropriate enhancement level based on constraints"""
        if complexity == ComplexityLevel.SIMPLE or time_budget < 1.0:
            return EnhancementLevel.MINIMAL
        elif complexity == ComplexityLevel.MODERATE or time_budget < 3.0:
            return EnhancementLevel.STANDARD
        elif complexity == ComplexityLevel.COMPLEX or time_budget < 5.0:
            return EnhancementLevel.DEEP
        else:
            return EnhancementLevel.QUANTUM
    
    def get_strategies(self, level: EnhancementLevel) -> List[str]:
        """Get strategies for enhancement level"""
        strategies = []
        for l in EnhancementLevel:
            strategies.extend(self.levels[l])
            if l == level:
                break
        return strategies


# ============================================================================
# ENHANCED ORCHESTRATOR V2
# ============================================================================

class EnhancedOrchestratorV2:
    """
    Master orchestrator integrating CODER patterns with prompt strategies
    
    Features:
    - Contract-driven validation
    - Quality gates with stop points
    - Metacognitive monitoring
    - Progressive enhancement
    - Feedback loops
    """
    
    def __init__(self, strategies_dir: Optional[Path] = None):
        self.strategies_dir = strategies_dir or Path(__file__).parent
        self.metacognition = MetaCognitiveMonitor()
        self.progressive_enhancer = ProgressiveEnhancer()
        self.quality_gates = [
            ClarityGate(),
            ComplexityGate(),
            SafetyGate()
        ]
        self.performance_history = []
    
    async def enhance_prompt(
        self,
        prompt: str,
        contract: Optional[PromptContract] = None,
        complexity: ComplexityLevel = ComplexityLevel.MODERATE
    ) -> PromptResult:
        """
        Main entry point - enhance prompt with full CODER integration
        
        Implements:
        1. Contract validation
        2. Metacognitive assessment
        3. Progressive enhancement
        4. Quality gates
        5. Performance monitoring
        """
        start_time = time.time()
        
        # Default contract if none provided
        if contract is None:
            contract = PromptContract()
        
        # STOP 0: Pre-flight checks (CODER pattern)
        if not self._preflight_check():
            raise RuntimeError("Pre-flight checks failed")
        
        # Layer 1: Assess understanding (Metacognition)
        understanding = await self.metacognition.assess_understanding(prompt)
        
        # STOP 1: Low understanding
        if understanding["confidence"] < contract.min_confidence:
            # Try to clarify
            prompt = self._clarify_prompt(prompt)
            understanding = await self.metacognition.assess_understanding(prompt)
            
            if understanding["confidence"] < contract.min_confidence:
                return PromptResult(
                    original_prompt=prompt,
                    enhanced_prompt=prompt,
                    strategies_applied=[],
                    confidence=understanding["confidence"],
                    safety_assessment=SafetyLevel.SAFE,
                    complexity_score=0,
                    quality_metrics={"understanding": understanding["confidence"]},
                    processing_time=time.time() - start_time,
                    metadata={"stopped_at": "understanding"}
                )
        
        # Select enhancement level (Progressive Enhancement)
        time_budget = contract.max_processing_time
        level = self.progressive_enhancer.select_level(complexity, time_budget)
        strategies = self.progressive_enhancer.get_strategies(level)
        
        # Filter strategies based on contract
        strategies = self._filter_strategies(strategies, contract)
        
        # Apply strategies with monitoring
        enhanced_prompt = prompt
        applied_strategies = []
        
        for strategy in strategies:
            # Check time budget
            if time.time() - start_time > time_budget:
                break
            
            # Apply strategy
            enhanced_prompt = self._apply_strategy(enhanced_prompt, strategy)
            applied_strategies.append(strategy)
            
            # Layer 2: Monitor enhancement
            monitoring = await self.metacognition.monitor_enhancement(applied_strategies)
            
            if monitoring["needs_adjustment"]:
                if "break_loop" in monitoring["adjustments"]:
                    break
                if "simplify" in monitoring["adjustments"]:
                    strategies = strategies[:2]  # Keep only first 2
        
        # Calculate metrics
        complexity_score = self._calculate_complexity(applied_strategies, enhanced_prompt)
        confidence = await self._calculate_confidence(enhanced_prompt, applied_strategies)
        safety = self._assess_safety(enhanced_prompt)
        
        # Create result
        result = PromptResult(
            original_prompt=prompt,
            enhanced_prompt=enhanced_prompt,
            strategies_applied=applied_strategies,
            confidence=confidence,
            safety_assessment=safety,
            complexity_score=complexity_score,
            quality_metrics=self.metacognition.quality_metrics,
            processing_time=time.time() - start_time,
            metadata={
                "enhancement_level": level.name,
                "understanding": understanding
            }
        )
        
        # STOP 2: Quality gates
        context = {
            "strategies": applied_strategies,
            "reasoning_depth": len(applied_strategies)
        }
        
        for gate in self.quality_gates:
            passed, message = gate.check(enhanced_prompt, context)
            if not passed:
                # Log gate failure
                result.metadata["failed_gate"] = message
                
                # Attempt recovery
                enhanced_prompt = self._recover_from_gate_failure(
                    enhanced_prompt, gate, message
                )
                result.enhanced_prompt = enhanced_prompt
        
        # Layer 3: Final review
        review = await self.metacognition.final_review(result)
        
        if not review["approved"]:
            # Revert to original with warning
            result.enhanced_prompt = prompt
            result.metadata["reverted"] = True
            result.metadata["revert_reason"] = review["concerns"]
        
        # Store for learning
        self._record_performance(result)
        
        return result
    
    def _preflight_check(self) -> bool:
        """CODER pattern: Pre-flight validation"""
        # Check strategies directory exists
        if not self.strategies_dir.exists():
            return False
        
        # Check required files
        required_files = ["strategy_orchestrator.py"]
        for file in required_files:
            if not (self.strategies_dir / file).exists():
                return False
        
        return True
    
    def _clarify_prompt(self, prompt: str) -> str:
        """Attempt to clarify ambiguous prompt"""
        # Add structure to unclear prompts
        if not any(word in prompt.lower() for word in ["explain", "create", "analyze"]):
            prompt = f"Analyze and explain: {prompt}"
        
        return prompt
    
    def _filter_strategies(self, strategies: List[str], contract: PromptContract) -> List[str]:
        """Filter strategies based on contract requirements"""
        # Add required strategies
        for required in contract.required_strategies:
            if required not in strategies:
                strategies.append(required)
        
        # Remove excluded strategies
        strategies = [s for s in strategies if s not in contract.excluded_strategies]
        
        return strategies
    
    def _apply_strategy(self, prompt: str, strategy: str) -> str:
        """Apply a single strategy to prompt"""
        # Simplified - in production would load actual strategy
        strategy_templates = {
            "chain_of_thought": "Let's think step by step. {prompt}",
            "tree_of_thoughts": "Exploring multiple paths: {prompt}",
            "quantum_prompting": "In superposition of possibilities: {prompt}",
            "meta_cognitive_framework": "Thinking about thinking: {prompt}"
        }
        
        template = strategy_templates.get(strategy, "{prompt}")
        return template.format(prompt=prompt)
    
    def _calculate_complexity(self, strategies: List[str], prompt: str) -> int:
        """Calculate complexity score using CODER formula"""
        strategies_count = len(strategies)
        depth = min(strategies_count, 5)  # Cap depth at 5
        tokens = len(prompt.split())
        
        return (strategies_count * 6) + (depth * 4) + (tokens // 200)
    
    async def _calculate_confidence(self, prompt: str, strategies: List[str]) -> float:
        """Calculate overall confidence in enhancement"""
        base_confidence = 0.7
        
        # Boost for each quality strategy
        quality_strategies = ["chain_of_thought", "self_consistency", "meta_cognitive_framework"]
        quality_boost = sum(0.05 for s in strategies if s in quality_strategies)
        
        # Penalty for too many strategies (overengineering)
        if len(strategies) > 5:
            quality_boost -= 0.1
        
        return min(1.0, base_confidence + quality_boost)
    
    def _assess_safety(self, prompt: str) -> SafetyLevel:
        """Assess prompt safety"""
        unsafe_patterns = ["hack", "exploit", "attack", "malicious"]
        
        prompt_lower = prompt.lower()
        for pattern in unsafe_patterns:
            if pattern in prompt_lower:
                return SafetyLevel.REFUSED
        
        return SafetyLevel.SAFE
    
    def _recover_from_gate_failure(self, prompt: str, gate: QualityGate, message: str) -> str:
        """Attempt to recover from quality gate failure"""
        if isinstance(gate, ClarityGate):
            # Add clarifying structure
            return f"To be clear: {prompt}"
        elif isinstance(gate, ComplexityGate):
            # Simplify by removing nested structures
            return prompt.replace("(", "").replace(")", "")
        elif isinstance(gate, SafetyGate):
            # Remove problematic terms
            for pattern in SafetyGate.UNSAFE_PATTERNS:
                prompt = prompt.replace(pattern, "[REDACTED]")
            return prompt
        
        return prompt
    
    def _record_performance(self, result: PromptResult):
        """Record performance for learning"""
        self.performance_history.append({
            "timestamp": datetime.now().isoformat(),
            "strategies": result.strategies_applied,
            "confidence": result.confidence,
            "complexity": result.complexity_score,
            "processing_time": result.processing_time
        })
        
        # Keep only last 100 entries
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of orchestrator performance"""
        if not self.performance_history:
            return {"message": "No performance data yet"}
        
        avg_confidence = sum(h["confidence"] for h in self.performance_history) / len(self.performance_history)
        avg_complexity = sum(h["complexity"] for h in self.performance_history) / len(self.performance_history)
        avg_time = sum(h["processing_time"] for h in self.performance_history) / len(self.performance_history)
        
        # Find most effective strategies
        strategy_counts = {}
        for history in self.performance_history:
            for strategy in history["strategies"]:
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        return {
            "total_enhancements": len(self.performance_history),
            "average_confidence": avg_confidence,
            "average_complexity": avg_complexity,
            "average_processing_time": avg_time,
            "most_used_strategies": sorted(strategy_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "metacognitive_metrics": self.metacognition.quality_metrics
        }


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

async def example_usage():
    """Demonstrate the enhanced orchestrator with CODER integration"""
    
    # Initialize orchestrator
    orchestrator = EnhancedOrchestratorV2()
    
    # Example 1: Simple enhancement with default contract
    print("Example 1: Simple Enhancement")
    result = await orchestrator.enhance_prompt(
        "Explain quantum computing",
        complexity=ComplexityLevel.SIMPLE
    )
    print(f"Enhanced: {result.enhanced_prompt}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Strategies: {result.strategies_applied}\n")
    
    # Example 2: Complex enhancement with custom contract
    print("Example 2: Complex Enhancement with Contract")
    contract = PromptContract(
        min_clarity=0.9,
        max_complexity=25,
        required_strategies=["meta_cognitive_framework"],
        max_processing_time=10.0
    )
    
    result = await orchestrator.enhance_prompt(
        "How does consciousness emerge from neural activity?",
        contract=contract,
        complexity=ComplexityLevel.PARADOXICAL
    )
    print(f"Enhanced: {result.enhanced_prompt}")
    print(f"Complexity Score: {result.complexity_score}")
    print(f"Applied: {result.strategies_applied}\n")
    
    # Example 3: Get performance summary
    print("Performance Summary:")
    summary = orchestrator.get_performance_summary()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    # Run examples
    asyncio.run(example_usage())