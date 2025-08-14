"""
Master Prompt Strategies Package
A comprehensive collection of advanced prompt engineering strategies.
"""

from .strategy_orchestrator import (
    StrategyOrchestrator,
    StrategyLoader,
    StrategyConfig,
    StrategyType,
    PromptContext,
    create_orchestrator,
    enhance_prompt
)

__version__ = "1.0.0"
__author__ = "Master Prompt Engineering Collective"

__all__ = [
    "StrategyOrchestrator",
    "StrategyLoader", 
    "StrategyConfig",
    "StrategyType",
    "PromptContext",
    "create_orchestrator",
    "enhance_prompt"
]

# Quick access to common strategy combinations
STRATEGY_PRESETS = {
    "simple": ["chain_of_thought"],
    "balanced": ["chain_of_thought", "self_consistency"],
    "thorough": ["chain_of_thought", "tree_of_thoughts", "self_consistency"],
    "maximum": ["chain_of_thought", "tree_of_thoughts", "react", "self_consistency", "meta_prompting"],
    "ethical": ["constitutional_ai", "chain_of_thought", "self_consistency"],
    "creative": ["tree_of_thoughts", "few_shot", "mixture_of_experts"],
    "analytical": ["chain_of_thought", "scratchpad", "meta_prompting"],
    "debug": ["meta_prompting", "reflexion", "self_consistency"]
}

def quick_enhance(prompt: str, preset: str = "balanced") -> str:
    """
    Quickly enhance a prompt using a preset strategy combination.
    
    Args:
        prompt: The prompt to enhance
        preset: One of the preset combinations (simple/balanced/thorough/maximum/ethical/creative/analytical/debug)
        
    Returns:
        Enhanced prompt
    """
    strategies = STRATEGY_PRESETS.get(preset, STRATEGY_PRESETS["balanced"])
    return enhance_prompt(prompt, strategies=strategies)