"""
AI-First Browser - The main interface for intelligent web automation.

This module provides the primary interface for users to interact with
AI-powered browser automation using natural language instructions.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

# Playwright imports
try:
    from playwright.async_api import async_playwright, Browser, Playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    Browser = Any
    Playwright = Any

from .config import UnifiedConfig, ConfigFactory, ConfigProfile
from .browser.browser_context import BrowserContext
from .agents.base_agent import (
    AgentFactory, 
    WebAgentBase,
    SimpleWebAgent,
    NavigationAgent,
    InteractionAgent,
    ExtractionAgent,
    AnalysisAgent,
    run_multi_agent_task
)
from .core import BrowserState, LLMProvider


class AIBrowser:
    """
    AI-First Browser for intelligent web automation.
    
    This is the main interface that users interact with. It combines
    Playwright browser capabilities with pydantic-ai agents to provide
    intelligent, natural language-driven web automation.
    
    Example:
        browser = AIBrowser()
        async with browser:
            result = await browser.run("Go to Amazon and find laptops under $500")
            print(result.data)
    """
    
    def __init__(
        self,
        config: Optional[UnifiedConfig] = None,
        profile: Optional[ConfigProfile] = None,
        model: Optional[str] = None,
        headless: bool = True,
        debug: bool = False
    ):
        """
        Initialize AI Browser.
        
        Args:
            config: Custom configuration (overrides profile)
            profile: Configuration profile to use
            model: Specific AI model to use
            headless: Whether to run browser in headless mode
            debug: Enable debug mode
        """
        # Configuration setup
        if config:
            self.config = config
        elif profile:
            self.config = ConfigFactory.create_config(profile)
        else:
            self.config = ConfigFactory.create_config(ConfigProfile.DEFAULT)
        
        # Override headless setting if specified
        if headless is not None:
            self.config.browser.headless = headless
        
        # Override debug setting
        if debug:
            self.config.browser.debug.enabled = True
            self.config.browser.headless = False  # Show browser in debug mode
        
        # Set specific model if provided
        if model:
            self._override_model(model)
        
        # Internal state
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._browser_context: Optional[BrowserContext] = None
        self._default_agent: Optional[WebAgentBase] = None
        self._specialized_agents: Dict[str, WebAgentBase] = {}
        self._state = BrowserState.CLOSED
        
        # Session data
        self._conversation_history: List[Dict[str, Any]] = []
        self._session_data: Dict[str, Any] = {}
    
    def _override_model(self, model: str) -> None:
        """Override the AI model configuration."""
        # Parse model string (e.g., "openai:gpt-4", "anthropic:claude-3")
        if ':' in model:
            provider_str, model_name = model.split(':', 1)
            provider_map = {
                'openai': LLMProvider.OPENAI,
                'anthropic': LLMProvider.ANTHROPIC, 
                'gemini': LLMProvider.GEMINI,
                'xai': LLMProvider.XAI
            }
            if provider_str in provider_map:
                self.config.ai.primary_provider = provider_map[provider_str]
                self.config.ai.models[provider_map[provider_str]] = model_name
    
    # ============================================================================
    # LIFECYCLE MANAGEMENT
    # ============================================================================
    
    async def start(self) -> bool:
        """
        Start the AI browser.
        
        Returns:
            True if started successfully, False otherwise
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright is not installed. Install with: pip install playwright")
        
        try:
            # Initialize Playwright
            self._playwright = await async_playwright().start()
            
            # Launch browser
            browser_args = []
            if self.config.browser.debug.enabled:
                browser_args.extend([
                    '--remote-debugging-port=9222',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ])
            
            self._browser = await self._playwright.chromium.launch(
                headless=self.config.browser.headless,
                args=browser_args,
                slow_mo=100 if self.config.browser.debug.enabled else 0
            )
            
            # Initialize browser context
            self._browser_context = BrowserContext(self.config)
            await self._browser_context.initialize(self._browser)
            
            # Create default agent
            self._default_agent = AgentFactory.create_agent(
                'simple',
                self.config.ai,
                self._browser_context
            )
            
            self._state = BrowserState.READY
            return True
            
        except Exception as e:
            self._state = BrowserState.ERROR
            if self.config.browser.debug.enabled:
                print(f"Failed to start AI Browser: {e}")
            return False
    
    async def close(self) -> None:
        """Close the AI browser and cleanup resources."""
        try:
            if self._browser_context:
                await self._browser_context.close()
                
            if self._browser:
                await self._browser.close()
                
            if self._playwright:
                await self._playwright.stop()
                
        except Exception as e:
            if self.config.browser.debug.enabled:
                print(f"Error during cleanup: {e}")
        finally:
            self._state = BrowserState.CLOSED
            self._browser = None
            self._browser_context = None
            self._playwright = None
    
    @asynccontextmanager
    async def session(self):
        """Context manager for automatic lifecycle management."""
        try:
            await self.start()
            yield self
        finally:
            await self.close()
    
    # Magic methods for context manager
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    # ============================================================================
    # MAIN AI INTERFACE
    # ============================================================================
    
    async def run(self, instruction: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute an instruction using AI.
        
        This is the main interface for natural language web automation.
        
        Args:
            instruction: Natural language instruction
            context: Optional additional context
            
        Returns:
            Structured result from AI agent
            
        Example:
            result = await browser.run("Go to Amazon and search for laptops")
            result = await browser.run("Fill out the contact form with my details")
            result = await browser.run("Extract all product prices from this page")
        """
        if self._state != BrowserState.READY:
            raise RuntimeError("Browser not ready. Call start() first.")
        
        if not self._default_agent:
            raise RuntimeError("Default agent not initialized")
        
        # Add to conversation history
        self._conversation_history.append({
            'type': 'instruction',
            'content': instruction,
            'context': context,
            'timestamp': asyncio.get_event_loop().time()
        })
        
        # Enhance context with session data
        enhanced_context = self._build_enhanced_context(context)
        
        try:
            # Run the AI agent
            result = await self._default_agent.run(instruction, enhanced_context)
            
            # Record result in history
            self._conversation_history.append({
                'type': 'result', 
                'content': result,
                'timestamp': asyncio.get_event_loop().time()
            })
            
            return result
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'message': f"Failed to execute instruction: {instruction}"
            }
            
            self._conversation_history.append({
                'type': 'error',
                'content': error_result, 
                'timestamp': asyncio.get_event_loop().time()
            })
            
            return error_result
    
    # ============================================================================
    # SPECIALIZED AGENT INTERFACES
    # ============================================================================
    
    async def navigate(self, instruction: str) -> Any:
        """Use navigation specialist agent."""
        agent = await self._get_specialized_agent('navigation')
        return await agent.run(instruction)
    
    async def interact(self, instruction: str) -> Any:
        """Use interaction specialist agent."""
        agent = await self._get_specialized_agent('interaction')
        return await agent.run(instruction)
    
    async def extract(self, instruction: str) -> Any:
        """Use extraction specialist agent."""
        agent = await self._get_specialized_agent('extraction')
        return await agent.run(instruction)
    
    async def analyze(self, instruction: str) -> Any:
        """Use analysis specialist agent."""
        agent = await self._get_specialized_agent('analysis')
        return await agent.run(instruction)
    
    async def _get_specialized_agent(self, agent_type: str) -> WebAgentBase:
        """Get or create a specialized agent."""
        if agent_type not in self._specialized_agents:
            self._specialized_agents[agent_type] = AgentFactory.create_agent(
                agent_type,
                self.config.ai,
                self._browser_context
            )
        return self._specialized_agents[agent_type]
    
    # ============================================================================
    # MULTI-AGENT WORKFLOWS
    # ============================================================================
    
    async def workflow(self, steps: List[Dict[str, str]], coordination: str = "sequential") -> List[Any]:
        """
        Execute a multi-step workflow with specialized agents.
        
        Args:
            steps: List of steps with 'agent' and 'instruction' keys
            coordination: 'sequential' or 'parallel'
            
        Returns:
            List of results from each step
            
        Example:
            results = await browser.workflow([
                {'agent': 'navigation', 'instruction': 'Go to Amazon'},
                {'agent': 'interaction', 'instruction': 'Search for laptops'},
                {'agent': 'extraction', 'instruction': 'Get product details'}
            ])
        """
        agents = []
        prompts = []
        
        for step in steps:
            agent_type = step.get('agent', 'simple')
            instruction = step['instruction']
            
            agent = await self._get_specialized_agent(agent_type)
            agents.append(agent)
            prompts.append(instruction)
        
        return await run_multi_agent_task(agents, prompts, coordination)
    
    # ============================================================================
    # BROWSER STATE AND INFORMATION
    # ============================================================================
    
    async def current_page(self) -> Dict[str, Any]:
        """Get current page information."""
        if not self._browser_context:
            return {'error': 'Browser not initialized'}
            
        return await self._browser_context.get_page_info(include_screenshot=False)
    
    async def screenshot(self, file_path: Optional[str] = None) -> bytes:
        """Take a screenshot of current page."""
        if not self._browser_context:
            return b''
        
        return await self._browser_context.take_screenshot(file_path)
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history."""
        return self._conversation_history[-limit:]
    
    def get_session_data(self) -> Dict[str, Any]:
        """Get current session data."""
        return self._session_data.copy()
    
    def set_session_data(self, key: str, value: Any) -> None:
        """Set session data."""
        self._session_data[key] = value
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _build_enhanced_context(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build enhanced context with session and history data."""
        enhanced_context = context or {}
        
        # Add recent history
        if self._conversation_history:
            enhanced_context['recent_history'] = self._conversation_history[-3:]
        
        # Add session data
        if self._session_data:
            enhanced_context['session'] = self._session_data
        
        # Add browser state
        enhanced_context['browser_state'] = {
            'state': self._state.value,
            'current_url': self._browser_context.current_url if self._browser_context else None
        }
        
        return enhanced_context


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def quick_task(instruction: str, headless: bool = True, debug: bool = False) -> Any:
    """
    Execute a single task with automatic browser management.
    
    Args:
        instruction: Natural language instruction
        headless: Run in headless mode
        debug: Enable debug mode
        
    Returns:
        Task result
        
    Example:
        result = await quick_task("Go to Google and search for 'AI browser automation'")
    """
    async with AIBrowser(headless=headless, debug=debug) as browser:
        return await browser.run(instruction)


def create_browser(
    profile: ConfigProfile = ConfigProfile.DEFAULT,
    model: Optional[str] = None,
    headless: bool = True,
    debug: bool = False
) -> AIBrowser:
    """
    Create an AI browser instance.
    
    Args:
        profile: Configuration profile
        model: AI model to use
        headless: Run in headless mode
        debug: Enable debug mode
        
    Returns:
        AIBrowser instance
    """
    return AIBrowser(
        profile=profile,
        model=model,
        headless=headless,
        debug=debug
    )