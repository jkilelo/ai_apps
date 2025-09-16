"""Cognition Layer - LLM Integration and Reasoning"""

from .llm import ILLMProvider, LLMManager
from .providers import XAIProvider, GeminiProvider
from .actions import (
    AgentAction,
    ClickAction,
    TypeAction,
    FillAction,
    ScrollAction,
    NavigateAction,
    SelectAction,
    WaitAction,
    ReadTextAction,
    FinishedAction,
    FailedAction
)
from .prompts import PromptBuilder, BrowserPrompts
from .agents import BrowserAgent, PlannerAgent, SelfCorrectingBrowserAgent
from .orchestrator import AgentOrchestrator
from .dispatcher import ActionDispatcher

__all__ = [
    # LLM
    "ILLMProvider",
    "LLMManager",
    "XAIProvider",
    "GeminiProvider",
    
    # Actions
    "AgentAction",
    "ClickAction",
    "TypeAction",
    "FillAction",
    "ScrollAction",
    "NavigateAction",
    "SelectAction",
    "WaitAction",
    "ReadTextAction",
    "FinishedAction",
    "FailedAction",
    
    # Prompts
    "PromptBuilder",
    "BrowserPrompts",
    
    # Agents
    "BrowserAgent",
    "PlannerAgent",
    "SelfCorrectingBrowserAgent",
    "AgentOrchestrator",
    
    # Dispatcher
    "ActionDispatcher"
]