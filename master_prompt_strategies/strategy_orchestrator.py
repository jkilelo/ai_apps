"""
Universal Prompt Strategy Orchestrator
A master system for loading, combining, and applying prompt strategies dynamically.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import hashlib
from datetime import datetime


class StrategyType(Enum):
    """All available prompt strategies."""
    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    REACT = "react"
    CONSTITUTIONAL_AI = "constitutional_ai"
    SELF_CONSISTENCY = "self_consistency"
    META_PROMPTING = "meta_prompting"
    DEBATE = "debate"
    REFLEXION = "reflexion"
    SCRATCHPAD = "scratchpad"
    FEW_SHOT = "few_shot"
    ZERO_SHOT = "zero_shot"
    OPRO = "opro"
    MIXTURE_OF_EXPERTS = "mixture_of_experts"
    QUANTUM_PROMPTING = "quantum_prompting"
    REVERSE_PROMPTING = "reverse_prompting"
    EVOLUTIONARY_OPTIMIZATION = "evolutionary_optimization"
    PSYCHOLOGICAL_TRIGGERS = "psychological_triggers"
    UNIVERSAL_SELF_CONSISTENCY = "universal_self_consistency"
    PROGRAM_AIDED_LANGUAGE = "program_aided_language"
    CHAIN_OF_TABLE = "chain_of_table"
    META_COGNITIVE_FRAMEWORK = "meta_cognitive_framework"


@dataclass
class StrategyConfig:
    """Configuration for a prompt strategy."""
    name: str
    type: StrategyType
    enabled: bool = True
    priority: int = 1  # Higher priority strategies are applied first
    parameters: Dict[str, Any] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)  # When to apply
    
    
@dataclass
class PromptContext:
    """Context for prompt generation."""
    domain: str
    task_type: str
    complexity: str  # simple, moderate, complex, paradoxical
    constraints: Dict[str, Any] = field(default_factory=dict)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategyResult:
    """Result of applying strategies to a prompt."""
    original_prompt: str
    enhanced_prompt: str
    strategies_applied: List[str]
    metrics: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


class StrategyLoader:
    """Loads and manages prompt strategies."""
    
    def __init__(self, strategies_dir: Optional[Path] = None):
        self.strategies_dir = strategies_dir or Path(__file__).parent
        self.strategies: Dict[StrategyType, str] = {}
        self.templates: Dict[str, str] = {}
        self._load_all_strategies()
    
    def _load_all_strategies(self):
        """Load all strategy templates from markdown files."""
        strategy_files = {
            StrategyType.CHAIN_OF_THOUGHT: "01_chain_of_thought.md",
            StrategyType.TREE_OF_THOUGHTS: "02_tree_of_thoughts.md",
            StrategyType.REACT: "03_react.md",
            StrategyType.CONSTITUTIONAL_AI: "04_constitutional_ai.md",
            StrategyType.SELF_CONSISTENCY: "05_self_consistency.md",
            StrategyType.META_PROMPTING: "06_meta_prompting.md",
            StrategyType.DEBATE: "07_debate.md",
            StrategyType.REFLEXION: "08_reflexion.md",
            StrategyType.SCRATCHPAD: "09_scratchpad.md",
            StrategyType.FEW_SHOT: "10_few_shot.md",
            StrategyType.ZERO_SHOT: "11_zero_shot.md",
            StrategyType.OPRO: "12_opro.md",
            StrategyType.MIXTURE_OF_EXPERTS: "13_mixture_of_experts.md",
            # Note: Quantum Prompting loaded separately as it's strategy 14
        }
        
        for strategy_type, filename in strategy_files.items():
            filepath = self.strategies_dir / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.strategies[strategy_type] = content
                    self.templates[strategy_type.value] = self._extract_template(content)
    
    def _extract_template(self, content: str) -> str:
        """Extract the universal prompt template from strategy content."""
        # Find the universal prompt section
        pattern = r'\*\*THE UNIVERSAL .+ PROMPT\*\*\n```\n(.+?)\n```'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1)
        # Fallback: extract any code block
        pattern = r'```\n(.+?)\n```'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1) if match else content[:1000]
    
    def get_strategy(self, strategy_type: StrategyType) -> str:
        """Get a specific strategy template."""
        return self.strategies.get(strategy_type, "")
    
    def get_template(self, strategy_type: StrategyType) -> str:
        """Get the extracted template for a strategy."""
        return self.templates.get(strategy_type.value, "")


class StrategyOrchestrator:
    """
    Orchestrates the application of multiple prompt strategies.
    Combines strategies intelligently based on context and requirements.
    """
    
    def __init__(self, strategies_dir: Optional[Path] = None):
        self.loader = StrategyLoader(strategies_dir)
        self.active_strategies: List[StrategyConfig] = []
        self.execution_history: List[Dict] = []
        self.performance_metrics: Dict[str, float] = {}
        
    def add_strategy(self, config: StrategyConfig):
        """Add a strategy to the orchestrator."""
        self.active_strategies.append(config)
        self.active_strategies.sort(key=lambda x: x.priority, reverse=True)
    
    def remove_strategy(self, strategy_type: StrategyType):
        """Remove a strategy from the orchestrator."""
        self.active_strategies = [
            s for s in self.active_strategies 
            if s.type != strategy_type
        ]
    
    def apply_strategies(
        self, 
        base_prompt: str, 
        context: PromptContext
    ) -> str:
        """
        Apply all active strategies to enhance a prompt.
        
        Args:
            base_prompt: The original prompt
            context: Context for strategy application
            
        Returns:
            Enhanced prompt with all strategies applied
        """
        enhanced_prompt = base_prompt
        applied_strategies = []
        
        for strategy in self.active_strategies:
            if not strategy.enabled:
                continue
                
            if self._should_apply_strategy(strategy, context):
                enhanced_prompt = self._apply_single_strategy(
                    enhanced_prompt, 
                    strategy, 
                    context
                )
                applied_strategies.append(strategy.type.value)
        
        # Record execution
        self._record_execution(base_prompt, enhanced_prompt, applied_strategies, context)
        
        return enhanced_prompt
    
    def _should_apply_strategy(
        self, 
        strategy: StrategyConfig, 
        context: PromptContext
    ) -> bool:
        """Determine if a strategy should be applied based on context."""
        if not strategy.conditions:
            return True
        
        for condition, value in strategy.conditions.items():
            if condition == "min_complexity":
                complexity_levels = ["simple", "moderate", "complex", "paradoxical"]
                if complexity_levels.index(context.complexity) < complexity_levels.index(value):
                    return False
            elif condition == "domains":
                if context.domain not in value:
                    return False
            elif condition == "task_types":
                if context.task_type not in value:
                    return False
        
        return True
    
    def _apply_single_strategy(
        self, 
        prompt: str, 
        strategy: StrategyConfig,
        context: PromptContext
    ) -> str:
        """Apply a single strategy to enhance a prompt."""
        template = self.loader.get_template(strategy.type)
        
        if strategy.type == StrategyType.CHAIN_OF_THOUGHT:
            return self._apply_chain_of_thought(prompt, template, context)
        elif strategy.type == StrategyType.TREE_OF_THOUGHTS:
            return self._apply_tree_of_thoughts(prompt, template, context)
        elif strategy.type == StrategyType.REACT:
            return self._apply_react(prompt, template, context)
        elif strategy.type == StrategyType.CONSTITUTIONAL_AI:
            return self._apply_constitutional_ai(prompt, template, context)
        elif strategy.type == StrategyType.SELF_CONSISTENCY:
            return self._apply_self_consistency(prompt, template, context)
        elif strategy.type == StrategyType.META_PROMPTING:
            return self._apply_meta_prompting(prompt, template, context)
        else:
            return prompt + "\n\n" + template
    
    def _apply_chain_of_thought(self, prompt: str, template: str, context: PromptContext) -> str:
        """Apply Chain of Thought reasoning."""
        cot_enhancement = """
Let us think through this step-by-step:

STEP 1: DECOMPOSITION
Break down the problem into atomic components.

STEP 2: SEQUENTIAL ANALYSIS
Analyze each component in logical order.

STEP 3: SYNTHESIS
Combine the analyzed components.

STEP 4: VALIDATION
Test the reasoning chain.

Now, applying this structured thinking:
"""
        return prompt + "\n\n" + cot_enhancement
    
    def _apply_tree_of_thoughts(self, prompt: str, template: str, context: PromptContext) -> str:
        """Apply Tree of Thoughts exploration."""
        tot_enhancement = f"""
Explore multiple reasoning branches for this {context.complexity} problem:

Branch 1 - Optimistic Path: Assume ideal conditions
Branch 2 - Pessimistic Path: Consider worst cases  
Branch 3 - Creative Path: Think unconventionally
Branch 4 - Pragmatic Path: Focus on immediate feasibility

Synthesize insights from all branches:
"""
        return prompt + "\n\n" + tot_enhancement
    
    def _apply_react(self, prompt: str, template: str, context: PromptContext) -> str:
        """Apply ReAct reasoning and action cycles."""
        react_enhancement = """
Apply iterative Reasoning and Acting:

THOUGHT: Analyze the current situation
ACTION: Choose and execute an intervention
OBSERVATION: Observe the results
REFLECTION: Update understanding

Continue this cycle until the goal is achieved:
"""
        return prompt + "\n\n" + react_enhancement
    
    def _apply_constitutional_ai(self, prompt: str, template: str, context: PromptContext) -> str:
        """Apply Constitutional AI principles."""
        constitutional_enhancement = """
Ensure all responses adhere to these principles:
- Do no harm (non-maleficence)
- Promote wellbeing (beneficence)
- Respect truth and accuracy
- Ensure fairness and justice
- Protect privacy and dignity
- Consider long-term sustainability

Applying these ethical constraints:
"""
        return prompt + "\n\n" + constitutional_enhancement
    
    def _apply_self_consistency(self, prompt: str, template: str, context: PromptContext) -> str:
        """Apply Self-Consistency through multiple sampling."""
        consistency_enhancement = f"""
Generate {context.metadata.get('samples', 3)} independent reasoning paths:

Path 1 (Analytical): Systematic, logical approach
Path 2 (Creative): Intuitive, associative approach
Path 3 (Balanced): Pragmatic, evidence-based approach

Synthesize convergent insights:
"""
        return prompt + "\n\n" + consistency_enhancement
    
    def _apply_meta_prompting(self, prompt: str, template: str, context: PromptContext) -> str:
        """Apply Meta-Prompting self-reflection."""
        meta_enhancement = f"""
Before solving, examine the problem at a meta-level:
- What type of problem is this?
- What cognitive approach is optimal?
- What biases might affect the solution?
- What would an expert in {context.domain} consider?

With this awareness, proceed:
"""
        return prompt + "\n\n" + meta_enhancement
    
    def _record_execution(
        self, 
        base_prompt: str, 
        enhanced_prompt: str,
        applied_strategies: List[str],
        context: PromptContext
    ):
        """Record execution for analysis and improvement."""
        execution = {
            "timestamp": datetime.now().isoformat(),
            "base_prompt_hash": hashlib.md5(base_prompt.encode()).hexdigest(),
            "enhanced_prompt_hash": hashlib.md5(enhanced_prompt.encode()).hexdigest(),
            "applied_strategies": applied_strategies,
            "context": {
                "domain": context.domain,
                "task_type": context.task_type,
                "complexity": context.complexity
            },
            "enhancement_ratio": len(enhanced_prompt) / len(base_prompt)
        }
        self.execution_history.append(execution)
    
    def optimize_strategy_selection(
        self, 
        context: PromptContext,
        performance_data: Optional[Dict] = None
    ) -> List[StrategyConfig]:
        """
        Use historical performance to optimize strategy selection.
        
        This is where OPRO-style optimization would occur.
        """
        optimal_strategies = []
        
        # Analyze historical performance
        if performance_data:
            for strategy_type, performance in performance_data.items():
                if performance > 0.7:  # Threshold for good performance
                    config = StrategyConfig(
                        name=strategy_type,
                        type=StrategyType[strategy_type.upper()],
                        priority=int(performance * 10)
                    )
                    optimal_strategies.append(config)
        
        # Default strategies based on complexity
        if context.complexity == "simple":
            optimal_strategies.append(
                StrategyConfig("chain_of_thought", StrategyType.CHAIN_OF_THOUGHT, priority=10)
            )
        elif context.complexity == "complex":
            optimal_strategies.extend([
                StrategyConfig("tree_of_thoughts", StrategyType.TREE_OF_THOUGHTS, priority=10),
                StrategyConfig("self_consistency", StrategyType.SELF_CONSISTENCY, priority=9),
                StrategyConfig("meta_prompting", StrategyType.META_PROMPTING, priority=8)
            ])
        
        return optimal_strategies
    
    def create_hybrid_strategy(
        self,
        strategies: List[StrategyType],
        weights: Optional[List[float]] = None
    ) -> Callable:
        """
        Create a custom hybrid strategy combining multiple strategies.
        
        Args:
            strategies: List of strategies to combine
            weights: Optional weights for each strategy
            
        Returns:
            A callable that applies the hybrid strategy
        """
        if weights is None:
            weights = [1.0] * len(strategies)
        
        def hybrid_apply(prompt: str, context: PromptContext) -> str:
            enhanced = prompt
            for strategy, weight in zip(strategies, weights):
                if weight > 0:
                    config = StrategyConfig(
                        name=f"hybrid_{strategy.value}",
                        type=strategy,
                        priority=int(weight * 10)
                    )
                    enhanced = self._apply_single_strategy(enhanced, config, context)
            return enhanced
        
        return hybrid_apply
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze the performance of applied strategies."""
        if not self.execution_history:
            return {}
        
        analysis = {
            "total_executions": len(self.execution_history),
            "strategy_frequency": {},
            "average_enhancement_ratio": 0,
            "complexity_distribution": {},
            "domain_distribution": {}
        }
        
        total_ratio = 0
        for execution in self.execution_history:
            # Strategy frequency
            for strategy in execution["applied_strategies"]:
                analysis["strategy_frequency"][strategy] = \
                    analysis["strategy_frequency"].get(strategy, 0) + 1
            
            # Enhancement ratio
            total_ratio += execution["enhancement_ratio"]
            
            # Complexity distribution
            complexity = execution["context"]["complexity"]
            analysis["complexity_distribution"][complexity] = \
                analysis["complexity_distribution"].get(complexity, 0) + 1
            
            # Domain distribution
            domain = execution["context"]["domain"]
            analysis["domain_distribution"][domain] = \
                analysis["domain_distribution"].get(domain, 0) + 1
        
        analysis["average_enhancement_ratio"] = total_ratio / len(self.execution_history)
        
        return analysis


# Convenience functions for easy usage

def create_orchestrator(
    strategies: Optional[List[StrategyType]] = None,
    auto_optimize: bool = True
) -> StrategyOrchestrator:
    """
    Create a pre-configured orchestrator.
    
    Args:
        strategies: List of strategies to enable (None = all)
        auto_optimize: Whether to automatically optimize strategy selection
        
    Returns:
        Configured StrategyOrchestrator
    """
    orchestrator = StrategyOrchestrator()
    
    if strategies is None:
        # Add all available strategies
        strategies = list(StrategyType)
    
    for i, strategy_type in enumerate(strategies):
        config = StrategyConfig(
            name=strategy_type.value,
            type=strategy_type,
            priority=len(strategies) - i  # Descending priority
        )
        orchestrator.add_strategy(config)
    
    return orchestrator


def enhance_prompt(
    prompt: str,
    domain: str = "general",
    complexity: str = "moderate",
    strategies: Optional[List[str]] = None
) -> str:
    """
    Quick function to enhance any prompt with selected strategies.
    
    Args:
        prompt: The base prompt to enhance
        domain: Problem domain
        complexity: Problem complexity (simple/moderate/complex/paradoxical)
        strategies: List of strategy names to apply
        
    Returns:
        Enhanced prompt
    """
    context = PromptContext(
        domain=domain,
        task_type="general",
        complexity=complexity
    )
    
    orchestrator = create_orchestrator()
    
    if strategies:
        # Filter to only requested strategies
        orchestrator.active_strategies = [
            s for s in orchestrator.active_strategies
            if s.name in strategies
        ]
    
    return orchestrator.apply_strategies(prompt, context)


if __name__ == "__main__":
    # Example usage
    base_prompt = "How can I improve the performance of my web application?"
    
    # Create context
    context = PromptContext(
        domain="software_engineering",
        task_type="optimization",
        complexity="complex"
    )
    
    # Create and configure orchestrator
    orchestrator = create_orchestrator()
    
    # Apply strategies
    enhanced = orchestrator.apply_strategies(base_prompt, context)
    
    print("Original Prompt:")
    print(base_prompt)
    print("\n" + "="*50 + "\n")
    print("Enhanced Prompt:")
    print(enhanced)
    
    # Analyze performance
    print("\n" + "="*50 + "\n")
    print("Performance Analysis:")
    print(json.dumps(orchestrator.analyze_performance(), indent=2))