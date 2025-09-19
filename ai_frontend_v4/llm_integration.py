"""
Shared LLM Integration Utilities
Centralizes LLM imports and utility setup for DRY compliance.
"""

# Import LLM functionality
import sys
from pathlib import Path
# Add parent directory to path for LLM import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


from llm import call_default_llm
from llm_utils import (
    LLMResponseParser,
    StrategySelector,
    LLMPromptBuilder,
    prepare_llm_messages,
)


class LLMIntegration:
    @staticmethod
    def get_llm_components():
        return {
            "call_llm": call_default_llm,
            "parser": LLMResponseParser(),
            "strategy_selector": StrategySelector(),
            "prompt_builder": LLMPromptBuilder(),
            "message_prep": prepare_llm_messages,
        }
