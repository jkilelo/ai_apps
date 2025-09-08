"""
Base agent for AI-powered browser automation.

This module provides the foundation for all pydantic-ai agents that interact
with web browsers, establishing common patterns and capabilities.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from abc import ABC, abstractmethod
from pydantic import BaseModel

# Import will be available when pydantic-ai is installed
try:
    from pydantic_ai import Agent, RunContext
    PYDANTIC_AI_AVAILABLE = True
except ImportError:
    # Fallback for development without pydantic-ai
    PYDANTIC_AI_AVAILABLE = False
    
    class Agent:
        def __init__(self, *args, **kwargs):
            pass
            
        def tool(self, func):
            return func
    
    class RunContext:
        def __init__(self, deps):
            self.deps = deps

from ..browser.browser_context import BrowserContext
from ..config import UnifiedConfig, AIConfig
from ..core import LLMProvider
from .tools.browser_tools import register_browser_tools


T = TypeVar('T', bound=BaseModel)
R = TypeVar('R')


class AgentResult(BaseModel):
    """Base result type for agent operations."""
    success: bool
    message: str
    confidence: float = 0.0
    data: Dict[str, Any] = {}
    actions_taken: List[str] = []
    errors: List[str] = []


class WebAgentBase(ABC, Generic[T, R]):
    """
    Base class for all web automation agents.
    
    This class provides the foundation for creating specialized pydantic-ai agents
    that can interact with web browsers through a unified interface.
    """
    
    def __init__(
        self,
        config: AIConfig,
        browser_context: BrowserContext,
        model: Optional[str] = None,
        instructions: Optional[str] = None,
    ):
        """Initialize the base web agent."""
        self.config = config
        self.browser_context = browser_context
        self.model = model or self._get_default_model()
        self.instructions = instructions or self._get_default_instructions()
        
        # Initialize pydantic-ai agent if available
        self.agent: Optional[Agent] = None
        if PYDANTIC_AI_AVAILABLE:
            self._initialize_agent()
    
    def _get_default_model(self) -> str:
        """Get default model for this agent type."""
        provider = self.config.primary_provider
        
        model_map = {
            LLMProvider.OPENAI: "openai:gpt-4-turbo-preview",
            LLMProvider.ANTHROPIC: "anthropic:claude-3-sonnet-20240229", 
            LLMProvider.GEMINI: "gemini:gemini-1.5-pro",
            LLMProvider.XAI: "xai:grok-beta"
        }
        
        return model_map.get(provider, "openai:gpt-4-turbo-preview")
    
    @abstractmethod
    def _get_default_instructions(self) -> str:
        """Get default instructions for this agent type."""
        pass
    
    @abstractmethod 
    def _get_result_type(self) -> Type[R]:
        """Get the result type for this agent."""
        pass
    
    def _initialize_agent(self) -> None:
        """Initialize the pydantic-ai agent."""
        if not PYDANTIC_AI_AVAILABLE:
            return
            
        self.agent = Agent(
            model=self.model,
            deps_type=BrowserContext,
            result_type=self._get_result_type(),
            instructions=self.instructions,
        )
        
        # Register browser tools
        register_browser_tools(self.agent)
        
        # Register agent-specific tools
        self._register_custom_tools()
    
    def _register_custom_tools(self) -> None:
        """Register custom tools specific to this agent type."""
        pass
    
    async def run(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> R:
        """
        Run the agent with a given prompt.
        
        Args:
            prompt: The user's request or instruction
            context: Optional additional context
            
        Returns:
            Structured result from the agent
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized - pydantic-ai not available")
        
        # Add context to prompt if provided
        enhanced_prompt = self._enhance_prompt(prompt, context)
        
        # Run the agent
        try:
            result = await self.agent.run(
                enhanced_prompt,
                deps=self.browser_context
            )
            return result
        except Exception as e:
            # Return error result
            return self._create_error_result(str(e))
    
    def _enhance_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Enhance prompt with additional context."""
        if not context:
            return prompt
            
        context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
        return f"Context:\n{context_str}\n\nTask: {prompt}"
    
    def _create_error_result(self, error: str) -> R:
        """Create an error result."""
        # This is a simplified error result - subclasses should override
        result_type = self._get_result_type()
        if hasattr(result_type, '__call__'):
            try:
                return result_type(
                    success=False,
                    message=f"Agent error: {error}",
                    confidence=0.0,
                    errors=[error]
                )
            except Exception:
                pass
        
        # Fallback - create a basic dict result
        return {
            'success': False,
            'message': f"Agent error: {error}",
            'errors': [error]
        }


class NavigationResult(AgentResult):
    """Result from navigation operations."""
    current_url: str = ""
    page_title: str = ""
    load_time: float = 0.0
    navigation_success: bool = False


class InteractionResult(AgentResult):
    """Result from interaction operations."""
    elements_found: int = 0
    interactions_completed: int = 0
    form_data_submitted: Dict[str, Any] = {}


class ExtractionResult(AgentResult):
    """Result from extraction operations."""
    extracted_data: Dict[str, Any] = {}
    data_quality: float = 0.0
    extraction_method: str = ""
    

class AnalysisResult(AgentResult):
    """Result from analysis operations."""
    page_analysis: Dict[str, Any] = {}
    recommendations: List[str] = []
    risk_factors: List[str] = []


# Example specialized agent implementations

class SimpleWebAgent(WebAgentBase[str, AgentResult]):
    """Simple web agent for general tasks."""
    
    def _get_default_instructions(self) -> str:
        return """
        You are a helpful web automation assistant. You can:
        - Navigate to web pages
        - Find and interact with elements
        - Extract information from pages
        - Take screenshots and analyze content
        
        Always be precise and explain what you're doing.
        When interacting with elements, verify they exist first.
        If something fails, try alternative approaches.
        """
    
    def _get_result_type(self) -> Type[AgentResult]:
        return AgentResult


class NavigationAgent(WebAgentBase[str, NavigationResult]):
    """Specialized agent for navigation tasks."""
    
    def _get_default_instructions(self) -> str:
        return """
        You are a web navigation specialist. Your role is to:
        - Navigate to requested URLs efficiently
        - Handle redirects and page loading issues
        - Verify successful navigation
        - Deal with popups and overlays
        - Wait for content to load properly
        
        Always confirm navigation success and report page details.
        Handle errors gracefully with alternative strategies.
        """
    
    def _get_result_type(self) -> Type[NavigationResult]:
        return NavigationResult


class InteractionAgent(WebAgentBase[str, InteractionResult]):
    """Specialized agent for element interaction."""
    
    def _get_default_instructions(self) -> str:
        return """
        You are a web interaction expert. You excel at:
        - Finding elements using various strategies
        - Clicking buttons and links
        - Filling out forms
        - Handling dynamic content
        - Working with dropdowns and complex widgets
        
        Always verify elements exist and are interactable before acting.
        Use descriptive selectors and fall back to alternatives if needed.
        """
    
    def _get_result_type(self) -> Type[InteractionResult]:
        return InteractionResult


class ExtractionAgent(WebAgentBase[str, ExtractionResult]):
    """Specialized agent for data extraction."""
    
    def _get_default_instructions(self) -> str:
        return """
        You are a data extraction specialist. You can:
        - Extract structured data from web pages
        - Parse tables, lists, and forms
        - Clean and validate extracted data
        - Handle dynamic and Ajax-loaded content
        - Export data in various formats
        
        Focus on data accuracy and completeness.
        Validate extracted information and handle edge cases.
        """
    
    def _get_result_type(self) -> Type[ExtractionResult]:
        return ExtractionResult


class AnalysisAgent(WebAgentBase[str, AnalysisResult]):
    """Specialized agent for page analysis."""
    
    def _get_default_instructions(self) -> str:
        return """
        You are a web analysis expert. You specialize in:
        - Analyzing page structure and content
        - Identifying automation opportunities  
        - Detecting security and bot protection
        - Recommending optimal strategies
        - Assessing page complexity and risks
        
        Provide detailed analysis with actionable recommendations.
        Consider both technical and strategic aspects.
        """
    
    def _get_result_type(self) -> Type[AnalysisResult]:
        return AnalysisResult


# Agent Factory

class AgentFactory:
    """Factory for creating specialized agents."""
    
    @staticmethod
    def create_agent(
        agent_type: str,
        config: AIConfig,
        browser_context: BrowserContext,
        model: Optional[str] = None,
        instructions: Optional[str] = None,
    ) -> WebAgentBase:
        """
        Create a specialized agent.
        
        Args:
            agent_type: Type of agent to create
            config: AI configuration
            browser_context: Browser context for the agent
            model: Optional specific model to use
            instructions: Optional custom instructions
            
        Returns:
            Specialized agent instance
        """
        agents = {
            'simple': SimpleWebAgent,
            'navigation': NavigationAgent,
            'interaction': InteractionAgent,
            'extraction': ExtractionAgent,
            'analysis': AnalysisAgent,
        }
        
        agent_class = agents.get(agent_type, SimpleWebAgent)
        return agent_class(config, browser_context, model, instructions)


# Utility functions for agent coordination

async def run_multi_agent_task(
    agents: List[WebAgentBase],
    prompts: List[str],
    coordination_strategy: str = "sequential"
) -> List[Any]:
    """
    Run multiple agents with coordination.
    
    Args:
        agents: List of agents to run
        prompts: List of prompts for each agent
        coordination_strategy: How to coordinate agents
        
    Returns:
        List of results from all agents
    """
    if coordination_strategy == "parallel":
        tasks = [agent.run(prompt) for agent, prompt in zip(agents, prompts)]
        return await asyncio.gather(*tasks)
    else:  # sequential
        results = []
        for agent, prompt in zip(agents, prompts):
            result = await agent.run(prompt)
            results.append(result)
        return results