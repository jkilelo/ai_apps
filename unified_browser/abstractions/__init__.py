"""
Base abstractions module for unified browser.

This module provides the abstract base classes that define contracts
for all browser implementations, establishing Layer 2 of the architecture.
"""

from __future__ import annotations

# Base browser abstraction
from .base_browser import BaseBrowser

# Navigation abstractions
from .base_navigator import (
    BaseNavigator,
    LoadNavigator,
    NetworkIdleNavigator,
    DOMContentLoadedNavigator,
    AdaptiveNavigator,
)

# Extraction abstractions
from .base_extractor import (
    BaseExtractor,
    PlaywrightExtractor,
    BeautifulSoupExtractor,
    LLMVisionExtractor,
    HybridExtractor,
)

# Stealth abstractions
from .base_stealth import (
    BaseStealth,
    BasicStealth,
    EnhancedStealth,
    MaximumStealth,
    AdaptiveStealth,
)

# Validation abstractions
from .base_validator import (
    BaseValidator,
    BasicValidator,
    EnhancedValidator,
    MLValidator,
    ComplianceValidator,
)

# LLM client abstractions
from .base_llm import (
    BaseLLMClient,
    LLMMessage,
    LLMResponse,
    VisionAnalysis,
    OpenAIClient,
    GeminiClient,
    AnthropicClient,
    XAIClient,
    HybridLLMClient,
)

__all__ = [
    # Base browser
    "BaseBrowser",
    
    # Navigation
    "BaseNavigator",
    "LoadNavigator",
    "NetworkIdleNavigator", 
    "DOMContentLoadedNavigator",
    "AdaptiveNavigator",
    
    # Extraction
    "BaseExtractor",
    "PlaywrightExtractor",
    "BeautifulSoupExtractor",
    "LLMVisionExtractor",
    "HybridExtractor",
    
    # Stealth
    "BaseStealth",
    "BasicStealth",
    "EnhancedStealth",
    "MaximumStealth",
    "AdaptiveStealth",
    
    # Validation
    "BaseValidator",
    "BasicValidator",
    "EnhancedValidator",
    "MLValidator",
    "ComplianceValidator",
    
    # LLM
    "BaseLLMClient",
    "LLMMessage",
    "LLMResponse",
    "VisionAnalysis",
    "OpenAIClient",
    "GeminiClient",
    "AnthropicClient",
    "XAIClient",
    "HybridLLMClient",
]