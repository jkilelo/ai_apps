"""
Base LLM client abstraction module.

This module defines the abstract base class for LLM integration,
handling different LLM providers and AI-powered features.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

from ..config import AIConfig
from ..core import (
    LLMProvider,
    TaskPlan,
    BrowserAction,
    ExtractionResult,
    LLMConnectionError,
    LLMResponseError,
    VisionAnalysisError,
    TaskPlanningError,
)


@dataclass
class LLMMessage:
    """Represents a message in LLM conversation."""
    role: str  # user, assistant, system
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LLMResponse:
    """Represents an LLM response."""
    content: str
    confidence: float
    tokens_used: int
    response_time: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class VisionAnalysis:
    """Represents vision analysis results."""
    description: str
    elements_detected: List[Dict[str, Any]]
    confidence_score: float
    bounding_boxes: List[Dict[str, Any]]
    text_extracted: Optional[str] = None


class BaseLLMClient(ABC):
    """
    Abstract base class for LLM client implementations.
    
    This class defines the contract for different LLM providers,
    enabling AI-powered browser automation and content understanding.
    """
    
    def __init__(self, config: AIConfig) -> None:
        """Initialize the LLM client with configuration."""
        self.config = config
        self._conversation_history: List[LLMMessage] = []
        self._usage_metrics: Dict[str, Any] = {}
        self._client = None  # Provider-specific client
    
    # ============================================================================
    # CONNECTION AND INITIALIZATION
    # ============================================================================
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize connection to the LLM provider."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check connection health and provider status."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close connection and cleanup resources."""
        pass
    
    # ============================================================================
    # BASIC TEXT GENERATION
    # ============================================================================
    
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate text completion for a prompt."""
        pass
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[LLMMessage],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate chat completion for conversation."""
        pass
    
    @abstractmethod
    async def streaming_completion(
        self,
        prompt: str,
        callback: callable,
        **kwargs
    ) -> None:
        """Generate streaming text completion."""
        pass
    
    # ============================================================================
    # VISION AND MULTIMODAL CAPABILITIES
    # ============================================================================
    
    @abstractmethod
    async def analyze_image(
        self,
        image_data: Union[bytes, str],
        prompt: Optional[str] = None,
        **kwargs
    ) -> VisionAnalysis:
        """Analyze image content using vision capabilities."""
        pass
    
    @abstractmethod
    async def analyze_screenshot(
        self,
        screenshot: bytes,
        task_description: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze screenshot for browser automation tasks."""
        pass
    
    @abstractmethod
    async def extract_text_from_image(
        self,
        image_data: bytes,
        **kwargs
    ) -> str:
        """Extract text from image using OCR capabilities."""
        pass
    
    @abstractmethod
    async def detect_elements_in_image(
        self,
        image_data: bytes,
        element_types: List[str],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Detect UI elements in screenshot."""
        pass
    
    # ============================================================================
    # BROWSER AUTOMATION PLANNING
    # ============================================================================
    
    @abstractmethod
    async def plan_browser_task(
        self,
        objective: str,
        current_context: Dict[str, Any],
        **kwargs
    ) -> TaskPlan:
        """Create a plan for browser automation task."""
        pass
    
    @abstractmethod
    async def suggest_next_action(
        self,
        current_state: Dict[str, Any],
        objective: str,
        previous_actions: List[BrowserAction],
        **kwargs
    ) -> BrowserAction:
        """Suggest the next browser action to take."""
        pass
    
    @abstractmethod
    async def evaluate_action_success(
        self,
        action: BrowserAction,
        before_screenshot: bytes,
        after_screenshot: bytes,
        **kwargs
    ) -> Dict[str, Any]:
        """Evaluate whether an action was successful."""
        pass
    
    @abstractmethod
    async def adapt_strategy(
        self,
        original_plan: TaskPlan,
        execution_results: List[Dict[str, Any]],
        **kwargs
    ) -> TaskPlan:
        """Adapt strategy based on execution results."""
        pass
    
    # ============================================================================
    # CONTENT UNDERSTANDING AND EXTRACTION
    # ============================================================================
    
    @abstractmethod
    async def understand_page_content(
        self,
        html_content: str,
        screenshot: Optional[bytes] = None,
        objective: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Understand and analyze page content."""
        pass
    
    @abstractmethod
    async def extract_structured_data(
        self,
        content: str,
        schema: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Extract structured data based on schema."""
        pass
    
    @abstractmethod
    async def classify_page_type(
        self,
        html_content: str,
        url: str,
        **kwargs
    ) -> Dict[str, str]:
        """Classify the type of web page."""
        pass
    
    @abstractmethod
    async def identify_important_elements(
        self,
        html_content: str,
        objective: str,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Identify elements important for the objective."""
        pass
    
    # ============================================================================
    # NATURAL LANGUAGE PROCESSING
    # ============================================================================
    
    @abstractmethod
    async def parse_user_intent(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Parse user intent from natural language."""
        pass
    
    @abstractmethod
    async def generate_css_selector(
        self,
        element_description: str,
        html_context: str,
        **kwargs
    ) -> List[str]:
        """Generate CSS selectors from element description."""
        pass
    
    @abstractmethod
    async def translate_to_xpath(
        self,
        natural_description: str,
        html_context: str,
        **kwargs
    ) -> List[str]:
        """Translate natural language to XPath expressions."""
        pass
    
    @abstractmethod
    async def summarize_content(
        self,
        content: str,
        max_length: Optional[int] = None,
        **kwargs
    ) -> str:
        """Summarize long content."""
        pass
    
    # ============================================================================
    # ERROR HANDLING AND DEBUGGING
    # ============================================================================
    
    @abstractmethod
    async def diagnose_automation_failure(
        self,
        error_description: str,
        screenshot: bytes,
        html_content: str,
        attempted_action: BrowserAction,
        **kwargs
    ) -> Dict[str, Any]:
        """Diagnose why automation failed."""
        pass
    
    @abstractmethod
    async def suggest_error_recovery(
        self,
        error_context: Dict[str, Any],
        **kwargs
    ) -> List[str]:
        """Suggest recovery strategies for errors."""
        pass
    
    @abstractmethod
    async def validate_automation_logic(
        self,
        plan: TaskPlan,
        **kwargs
    ) -> Dict[str, Any]:
        """Validate automation logic for potential issues."""
        pass
    
    # ============================================================================
    # CONVERSATION MANAGEMENT
    # ============================================================================
    
    def add_message(self, message: LLMMessage) -> None:
        """Add message to conversation history."""
        self._conversation_history.append(message)
        
        # Trim history if too long
        max_history = self.config.conversation.max_history_length
        if len(self._conversation_history) > max_history:
            self._conversation_history = self._conversation_history[-max_history:]
    
    def get_conversation_history(self) -> List[LLMMessage]:
        """Get conversation history."""
        return self._conversation_history.copy()
    
    def clear_conversation(self) -> None:
        """Clear conversation history."""
        self._conversation_history.clear()
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _record_usage(self, tokens_used: int, operation: str) -> None:
        """Record token usage metrics."""
        if operation not in self._usage_metrics:
            self._usage_metrics[operation] = {'total_tokens': 0, 'calls': 0}
        
        self._usage_metrics[operation]['total_tokens'] += tokens_used
        self._usage_metrics[operation]['calls'] += 1
    
    def get_usage_metrics(self) -> Dict[str, Any]:
        """Get usage metrics."""
        return self._usage_metrics.copy()
    
    def reset_metrics(self) -> None:
        """Reset usage metrics."""
        self._usage_metrics.clear()


class OpenAIClient(BaseLLMClient):
    """OpenAI client implementation."""
    
    async def initialize(self) -> bool:
        """Initialize OpenAI client."""
        # Implementation would initialize OpenAI client
        pass
    
    async def generate_text(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate text using OpenAI GPT."""
        # Implementation would call OpenAI API
        pass


class GeminiClient(BaseLLMClient):
    """Google Gemini client implementation."""
    
    async def initialize(self) -> bool:
        """Initialize Gemini client."""
        # Implementation would initialize Gemini client
        pass
    
    async def generate_text(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate text using Gemini."""
        # Implementation would call Gemini API
        pass


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude client implementation."""
    
    async def initialize(self) -> bool:
        """Initialize Claude client."""
        # Implementation would initialize Claude client
        pass
    
    async def generate_text(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate text using Claude."""
        # Implementation would call Anthropic API
        pass


class XAIClient(BaseLLMClient):
    """xAI client implementation."""
    
    async def initialize(self) -> bool:
        """Initialize xAI client."""
        # Implementation would initialize xAI client
        pass
    
    async def generate_text(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate text using xAI models."""
        # Implementation would call xAI API
        pass


class HybridLLMClient(BaseLLMClient):
    """Hybrid LLM client that routes to optimal providers."""
    
    def __init__(self, config: AIConfig) -> None:
        super().__init__(config)
        self._clients = {
            LLMProvider.OPENAI: OpenAIClient(config),
            LLMProvider.GEMINI: GeminiClient(config),
            LLMProvider.ANTHROPIC: AnthropicClient(config),
            LLMProvider.XAI: XAIClient(config),
        }
        self._routing_rules: Dict[str, LLMProvider] = {}
    
    async def initialize(self) -> bool:
        """Initialize all available clients."""
        results = {}
        for provider, client in self._clients.items():
            try:
                results[provider] = await client.initialize()
            except Exception as e:
                results[provider] = False
                print(f"Failed to initialize {provider.value}: {e}")
        
        return any(results.values())
    
    async def generate_text(self, prompt: str, **kwargs) -> LLMResponse:
        """Route text generation to optimal provider."""
        provider = await self._select_optimal_provider('text_generation', kwargs)
        client = self._clients[provider]
        return await client.generate_text(prompt, **kwargs)
    
    async def _select_optimal_provider(self, task_type: str, context: Dict[str, Any]) -> LLMProvider:
        """Select optimal provider based on task type and context."""
        # Simple routing logic - could be enhanced with ML
        if task_type == 'vision_analysis':
            return LLMProvider.GEMINI  # Excellent vision capabilities
        elif task_type == 'code_generation':
            return LLMProvider.OPENAI  # Good for coding tasks
        elif task_type == 'reasoning':
            return LLMProvider.ANTHROPIC  # Strong reasoning
        else:
            return self.config.primary_provider  # Use configured default