"""Unit tests for the Cognition Layer components.

Tests LLMManager, PromptBuilder, ActionDispatcher, and AgentOrchestrator
while ensuring strict layer separation (NO direct browser manipulation).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any
import json

from src.cognition.llm import LLMManager, ILLMProvider
from src.cognition.orchestrator import AgentOrchestrator
from src.cognition.prompts import PromptBuilder
from src.cognition.dispatcher import ActionDispatcher
from src.cognition.actions import (
    AgentAction,
    ActionType as CognitionActionType,
    ActionPlan,
    ActionResult as CognitionActionResult
)
from src.perception.models import WebPageState, PageMetadata, DOMStructure
from src.execution.action_executor import ActionConfig, ActionType, ActionResult


class MockLLMProvider(ILLMProvider):
    """Mock LLM provider for testing"""
    
    def __init__(self, model="test-model"):
        self.model = model
        self.generate_calls = []
        self.structured_calls = []
    
    async def generate(self, prompt: str, temperature: float = 0.7, 
                      max_tokens: int = 2000, **kwargs) -> str:
        self.generate_calls.append(prompt)
        return "Generated response"
    
    async def generate_structured(self, prompt: str, output_model, 
                                 temperature: float = 0.7, max_tokens: int = 2000,
                                 **kwargs):
        self.structured_calls.append((prompt, output_model))
        # Return mock structured data based on output model
        if output_model.__name__ == "AgentAction":
            return AgentAction(
                action_type=CognitionActionType.CLICK,
                selector="button#test",
                confidence=0.9,
                reasoning="Test reasoning"
            )
        elif output_model.__name__ == "ActionPlan":
            return ActionPlan(
                goal="Test goal",
                steps=["Step 1", "Step 2"],
                confidence=0.85
            )
        return output_model()
    
    async def generate_with_images(self, prompt: str, images, 
                                  temperature: float = 0.7, max_tokens: int = 2000,
                                  **kwargs) -> str:
        return f"Response with {len(images)} images"
    
    def get_name(self) -> str:
        return "mock"
    
    def get_model(self) -> str:
        return self.model
    
    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4
    
    def get_max_context_window(self) -> int:
        return 4000


class TestLLMManager:
    """Test LLMManager functionality."""
    
    def test_llm_manager_initialization(self):
        """Test LLMManager initialization."""
        manager = LLMManager()
        
        assert manager.providers == {}
        assert manager.default_provider is None
        assert manager._usage_stats == {}
    
    def test_register_provider(self):
        """Test registering LLM providers."""
        manager = LLMManager()
        provider = MockLLMProvider()
        
        manager.register_provider("test", provider)
        
        assert "test" in manager.providers
        assert manager.providers["test"] == provider
        assert manager.default_provider == "test"  # First provider becomes default
        assert "test" in manager._usage_stats
    
    @pytest.mark.asyncio
    async def test_generate_text(self):
        """Test text generation."""
        manager = LLMManager()
        provider = MockLLMProvider()
        manager.register_provider("test", provider)
        
        result = await manager.generate("Test prompt")
        
        assert result == "Generated response"
        assert len(provider.generate_calls) == 1
        assert provider.generate_calls[0] == "Test prompt"
        assert manager._usage_stats["test"]["requests"] == 1
    
    @pytest.mark.asyncio
    async def test_generate_structured(self):
        """Test structured generation."""
        manager = LLMManager()
        provider = MockLLMProvider()
        manager.register_provider("test", provider)
        
        result = await manager.generate_structured(
            "Test prompt",
            AgentAction
        )
        
        assert isinstance(result, AgentAction)
        assert result.action_type == CognitionActionType.CLICK
        assert result.selector == "button#test"
        assert manager._usage_stats["test"]["requests"] == 1
    
    @pytest.mark.asyncio
    async def test_generate_with_images(self):
        """Test generation with images."""
        manager = LLMManager()
        provider = MockLLMProvider()
        manager.register_provider("test", provider)
        
        images = [b"image1", b"image2"]
        result = await manager.generate_with_images("Test prompt", images)
        
        assert result == "Response with 2 images"
        assert manager._usage_stats["test"]["requests"] == 1
    
    @pytest.mark.asyncio
    async def test_fallback_generation(self):
        """Test fallback to other providers."""
        manager = LLMManager()
        
        # Primary provider that fails
        failing_provider = MockLLMProvider("failing")
        failing_provider.generate = AsyncMock(side_effect=Exception("Failed"))
        
        # Backup provider that works
        working_provider = MockLLMProvider("working")
        
        manager.register_provider("primary", failing_provider)
        manager.register_provider("backup", working_provider)
        manager.set_default_provider("primary")
        
        result = await manager.fallback_generate("Test prompt")
        
        assert result == "Generated response"
        assert manager._usage_stats["primary"]["errors"] == 1
        assert manager._usage_stats["backup"]["requests"] == 1
    
    def test_check_prompt_fit(self):
        """Test checking if prompt fits in context window."""
        manager = LLMManager()
        provider = MockLLMProvider()
        manager.register_provider("test", provider)
        
        # Short prompt should fit
        assert manager.check_prompt_fit("Short prompt") is True
        
        # Very long prompt should not fit
        long_prompt = "x" * 15000  # Way over 4000 token limit
        assert manager.check_prompt_fit(long_prompt) is False
    
    def test_truncate_to_fit(self):
        """Test prompt truncation."""
        manager = LLMManager()
        provider = MockLLMProvider()
        manager.register_provider("test", provider)
        
        long_prompt = "x" * 20000
        truncated = manager.truncate_to_fit(long_prompt, reserve_tokens=500)
        
        # Should truncate to fit within (4000 - 500) * 4 characters
        assert len(truncated) <= 14000


class TestPromptBuilder:
    """Test PromptBuilder functionality."""
    
    def test_prompt_builder_initialization(self):
        """Test PromptBuilder initialization."""
        builder = PromptBuilder()
        assert builder is not None
    
    def test_build_action_prompt(self):
        """Test building action generation prompt."""
        builder = PromptBuilder()
        
        state = WebPageState(
            metadata=PageMetadata(url="https://example.com", title="Test Page"),
            dom_structure=DOMStructure(
                distilled_content="Page content",
                text_content="Text content"
            ),
            interactive_elements=[]
        )
        
        prompt = builder.build_action_prompt("Click the submit button", state)
        
        assert "Click the submit button" in prompt
        assert "https://example.com" in prompt
        assert "Test Page" in prompt
    
    def test_build_reasoning_prompt(self):
        """Test building reasoning prompt."""
        builder = PromptBuilder()
        
        context = {
            "task": "Find information",
            "current_state": "On homepage",
            "history": []
        }
        
        prompt = builder.build_reasoning_prompt(context)
        
        assert "Find information" in prompt
        assert "On homepage" in prompt
    
    def test_build_reflection_prompt(self):
        """Test building reflection prompt."""
        builder = PromptBuilder()
        
        result = CognitionActionResult(
            success=True,
            action_type=CognitionActionType.CLICK,
            message="Clicked button"
        )
        
        prompt = builder.build_reflection_prompt("Click button", result, "Button clicked")
        
        assert "Click button" in prompt
        assert "Button clicked" in prompt


class TestActionDispatcher:
    """Test ActionDispatcher functionality."""
    
    @pytest.mark.asyncio
    async def test_dispatcher_initialization(self):
        """Test ActionDispatcher initialization."""
        mock_executor = AsyncMock()
        mock_observer = AsyncMock()
        
        dispatcher = ActionDispatcher(mock_executor, mock_observer)
        
        assert dispatcher.action_executor == mock_executor
        assert dispatcher.state_observer == mock_observer
        assert dispatcher.last_action is None
    
    @pytest.mark.asyncio
    async def test_dispatch_action(self):
        """Test dispatching an action."""
        mock_executor = AsyncMock()
        mock_executor.execute_action = AsyncMock(return_value=ActionResult(
            success=True,
            data={"result": "test"}
        ))
        mock_observer = AsyncMock()
        mock_page = AsyncMock()
        mock_context = MagicMock()
        
        dispatcher = ActionDispatcher(mock_executor, mock_observer)
        
        action = AgentAction(
            action_type=CognitionActionType.CLICK,
            selector="button#test",
            confidence=0.9
        )
        
        result = await dispatcher.dispatch(action, mock_page, mock_context)
        
        assert result.success is True
        assert dispatcher.last_action == action
        mock_executor.execute_action.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_dispatch_with_state_capture(self):
        """Test dispatching with state capture after action."""
        mock_executor = AsyncMock()
        mock_executor.execute_action = AsyncMock(return_value=ActionResult(
            success=True
        ))
        
        mock_observer = AsyncMock()
        mock_observer.observe = AsyncMock()
        
        mock_page = AsyncMock()
        mock_context = MagicMock()
        
        dispatcher = ActionDispatcher(mock_executor, mock_observer)
        
        action = AgentAction(
            action_type=CognitionActionType.NAVIGATE,
            url="https://example.com",
            confidence=0.95
        )
        
        await dispatcher.dispatch(action, mock_page, mock_context, capture_state_after=True)
        
        # Should capture state after navigation
        mock_observer.observe.assert_called_once_with(mock_page)


class TestAgentOrchestrator:
    """Test AgentOrchestrator functionality."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self):
        """Test AgentOrchestrator initialization."""
        mock_llm = MockLLMProvider()
        orchestrator = AgentOrchestrator(mock_llm)
        
        assert orchestrator.llm == mock_llm
        assert orchestrator.planner is not None
        assert orchestrator.browser_agent is not None
        assert orchestrator.enable_self_correction is True
    
    @pytest.mark.asyncio
    async def test_execute_complex_task(self):
        """Test executing a complex task."""
        mock_llm = MockLLMProvider()
        mock_page = AsyncMock()
        
        # Mock planner response
        with patch.object(mock_llm, 'generate_structured', AsyncMock(return_value=ActionPlan(
            goal="Complete task",
            steps=["Step 1", "Step 2"],
            confidence=0.9
        ))):
            orchestrator = AgentOrchestrator(mock_llm)
            
            # Mock browser agent execution
            orchestrator.browser_agent.execute_task = AsyncMock(return_value={
                "success": True,
                "summary": "Task completed",
                "iterations": 1
            })
            
            result = await orchestrator.execute_complex_task(
                mock_page,
                "Do something complex"
            )
            
            assert result["overall_success"] is True
            assert result["completed_tasks"] == 2
            assert result["total_tasks"] == 2
            assert len(result["results"]) == 2
    
    @pytest.mark.asyncio
    async def test_execute_with_failure_handling(self):
        """Test task execution with failure handling."""
        mock_llm = MockLLMProvider()
        mock_page = AsyncMock()
        
        with patch.object(mock_llm, 'generate_structured', AsyncMock(return_value=ActionPlan(
            goal="Complete task",
            steps=["Navigate to page", "Click button"],
            confidence=0.9
        ))):
            orchestrator = AgentOrchestrator(mock_llm)
            
            # First task fails (critical), should stop execution
            orchestrator.browser_agent.execute_task = AsyncMock(return_value={
                "success": False,
                "error": "Navigation failed"
            })
            
            result = await orchestrator.execute_complex_task(
                mock_page,
                "Navigate and click"
            )
            
            assert result["overall_success"] is False
            assert result["completed_tasks"] == 0
            assert len(result["results"]) == 1  # Should stop after first failure
    
    def test_is_critical_failure(self):
        """Test critical failure detection."""
        mock_llm = MockLLMProvider()
        orchestrator = AgentOrchestrator(mock_llm)
        
        tasks = ["Navigate to login", "Enter credentials", "Click submit"]
        
        # Navigation tasks should be critical
        assert orchestrator._is_critical_failure("Navigate to login", tasks) is True
        
        # Authentication tasks should be critical
        assert orchestrator._is_critical_failure("Enter login details", tasks) is True
        
        # First task should always be critical
        assert orchestrator._is_critical_failure(tasks[0], tasks) is True
        
        # Non-critical task
        assert orchestrator._is_critical_failure("Read text", tasks) is False


class TestLayerCompliance:
    """Test layer separation compliance."""
    
    def test_no_browser_manipulation_imports(self):
        """Ensure cognition layer doesn't import browser manipulation."""
        import src.cognition.llm as llm_module
        import src.cognition.orchestrator as orch_module
        import src.cognition.prompts as prompt_module
        
        # Check module dictionaries for forbidden imports
        for module in [llm_module, orch_module, prompt_module]:
            module_dict = vars(module)
            
            # Should not directly import Playwright page manipulation
            assert 'click' not in str(module_dict).lower() or 'click' in ['CLICK', 'ClickAction']
            assert 'fill' not in str(module_dict).lower() or 'fill' in ['FillAction'] 
            assert 'goto' not in str(module_dict).lower()
    
    def test_proper_layer_imports(self):
        """Ensure cognition layer properly imports from allowed layers."""
        import src.cognition.dispatcher as dispatcher
        
        module_dict = vars(dispatcher)
        
        # Should import from execution layer (allowed)
        assert 'ActionExecutor' in str(module_dict) or 'action_executor' in str(module_dict).lower()
        
        # Should import from perception layer (allowed)
        assert 'StateObserver' in str(module_dict) or 'state_observer' in str(module_dict).lower()