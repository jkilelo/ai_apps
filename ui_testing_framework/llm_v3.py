#!/usr/bin/env python3
"""
LLM V3 - Clean integration with prompts_v3.py

This module provides a clean LLM interface that uses prompts_v3.py as the
single source of truth for all prompt strategies.

Author: Senior Integration Engineer
Date: 2025-08-28
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union, TypeVar
from pathlib import Path
from datetime import datetime
from enum import Enum

# Pydantic v2 imports
from pydantic import BaseModel, Field, ConfigDict, field_validator

# Import prompts_v3 as the single source of truth
from prompts_v3 import PromptLibrary

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv

    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded environment from {env_path}")
except ImportError:
    logger.warning("dotenv not available, using system environment variables")

# Type variable for Pydantic models
T = TypeVar("T", bound=BaseModel)

# ==============================================================================
# PYDANTIC V2 MODELS WITH STRICT TYPE ENFORCEMENT
# ==============================================================================


class Provider(str, Enum):
    """Supported LLM providers"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    GOOGLE = "google"  # Alias for Gemini


class Role(str, Enum):
    """Message roles"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    """Message with Pydantic v2 validation"""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    role: Role = Field(..., description="Message role")
    content: str = Field(..., min_length=1, description="Message content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Ensure content is not empty"""
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        return v.strip()


class LLMConfig(BaseModel):
    """LLM configuration with Pydantic v2"""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    provider: Provider = Field(..., description="LLM provider")
    model: str = Field(..., min_length=1, description="Model name")
    api_key: Optional[str] = Field(None, description="API key")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature")
    max_tokens: Optional[int] = Field(None, gt=0, description="Max tokens")
    timeout: int = Field(120, gt=0, description="Timeout in seconds")
    retry_attempts: int = Field(3, ge=1, le=10, description="Retry attempts")


class LLMResponse(BaseModel):
    """LLM response with Pydantic v2"""

    model_config = ConfigDict(str_strip_whitespace=True)

    content: str = Field(..., min_length=1, description="Response content")
    provider: Provider = Field(..., description="Provider used")
    model: str = Field(..., description="Model used")
    strategy_used: Optional[str] = Field(None, description="Strategy applied")
    tokens_used: Optional[int] = Field(None, ge=0, description="Tokens consumed")
    latency_ms: Optional[int] = Field(None, ge=0, description="Response latency")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response time")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ProviderResponse(BaseModel):
    """Raw provider response wrapper"""

    model_config = ConfigDict(str_strip_whitespace=True)

    raw_response: Any = Field(..., description="Raw API response")
    parsed_content: str = Field(..., description="Parsed content")
    provider: Provider = Field(..., description="Provider")
    model: str = Field(..., description="Model")


# ==============================================================================
# STRATEGY ENGINE - USES PROMPTS_V3 EXCLUSIVELY
# ==============================================================================


class StrategyEngine:
    """
    Strategy engine that uses prompts_v3.py as the single source of truth.
    NO embedded prompts, NO mappings, ONLY delegation to prompts_v3.
    """

    def __init__(self) -> None:
        """Initialize with prompts_v3 library"""
        self.prompt_library = PromptLibrary()
        self._strategies = self.prompt_library.list_strategies()
        logger.info(f"StrategyEngine initialized with {len(self._strategies)} strategies from prompts_v3")

    def apply_strategy(
        self, messages: List[Message], strategy: str, context: Optional[Dict[str, Any]] = None
    ) -> List[Message]:
        """
        Apply a strategy from prompts_v3 to messages.

        Args:
            messages: Input messages
            strategy: Strategy name from prompts_v3
            context: Optional context for rendering

        Returns:
            Enhanced messages with strategy applied
        """
        if not messages:
            return messages

        # Get user's original content
        user_message = next((m for m in messages if m.role == Role.USER), None)
        if not user_message:
            return messages

        # Get strategy from prompts_v3
        try:
            prompt_strategy = self.prompt_library.get(strategy)
            if not prompt_strategy:
                logger.warning(f"Strategy '{strategy}' not found, using original")
                return messages

            # Render the strategic prompt
            enhanced_prompt = prompt_strategy.render(task=user_message.content, context=context or {})

            # Create new message with enhanced prompt
            enhanced_message = Message(
                role=Role.USER,
                content=enhanced_prompt,
                metadata={
                    "original_content": user_message.content,
                    "strategy_applied": strategy,
                    "strategy_title": prompt_strategy.title,
                    "timestamp": datetime.now().isoformat(),
                },
            )

            # Return enhanced messages
            result = [m for m in messages if m.role != Role.USER]
            result.append(enhanced_message)
            return result

        except Exception as e:
            logger.error(f"Error applying strategy '{strategy}': {e}")
            return messages

    def get_available_strategies(self) -> List[str]:
        """Get all available strategies from prompts_v3"""
        return self._strategies

    def get_strategy_info(self, strategy: str) -> Optional[Dict[str, Any]]:
        """Get detailed info about a strategy from prompts_v3"""
        try:
            prompt_strategy = self.prompt_library.get(strategy)
            if prompt_strategy:
                return {
                    "name": prompt_strategy.name,
                    "title": prompt_strategy.title,
                    "core_principle": prompt_strategy.core_principle,
                    "short_description": prompt_strategy.short_description,
                    "usage_example": prompt_strategy.usage_example,
                    "philosophical_grounding": prompt_strategy.philosophical_grounding,
                }
        except Exception as e:
            logger.error(f"Error getting strategy info: {e}")
        return None


# ==============================================================================
# PROVIDER IMPLEMENTATIONS
# ==============================================================================


class OpenAIProvider:
    """OpenAI provider implementation"""

    def __init__(self, config: LLMConfig):
        """Initialize OpenAI provider"""
        self.config = config
        self._client: Optional[Any] = None

    def _get_client(self) -> Any:
        """Get or create OpenAI client"""
        if self._client is None:
            try:
                from openai import OpenAI

                api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OpenAI API key not found")
                self._client = OpenAI(api_key=api_key)
            except ImportError:
                raise ImportError("openai package not installed")
        return self._client

    def query(self, messages: List[Message]) -> ProviderResponse:
        """Query OpenAI API"""
        client = self._get_client()

        # Convert messages to OpenAI format
        api_messages = [{"role": msg.role.value, "content": msg.content} for msg in messages]

        # Make API call
        response = client.chat.completions.create(
            model=self.config.model,
            messages=api_messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            timeout=self.config.timeout,
        )

        # Parse response
        content = response.choices[0].message.content

        return ProviderResponse(
            raw_response=response, parsed_content=content, provider=Provider.OPENAI, model=self.config.model
        )


class GeminiProvider:
    """Google Gemini provider implementation"""

    def __init__(self, config: LLMConfig):
        """Initialize Gemini provider"""
        self.config = config
        self._model: Optional[Any] = None

    def _get_model(self) -> Any:
        """Get or create Gemini model"""
        if self._model is None:
            try:
                import google.generativeai as genai

                api_key = self.config.api_key or os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    raise ValueError("Google API key not found")
                genai.configure(api_key=api_key)
                self._model = genai.GenerativeModel(self.config.model)
            except ImportError:
                raise ImportError("google-generativeai package not installed")
        return self._model

    def query(self, messages: List[Message]) -> ProviderResponse:
        """Query Gemini API"""
        model = self._get_model()

        # Combine messages into single prompt for Gemini
        prompt = "\n\n".join([f"{msg.role.value.upper()}: {msg.content}" for msg in messages])

        # Generate response
        response = model.generate_content(
            prompt,
            generation_config={"temperature": self.config.temperature, "max_output_tokens": self.config.max_tokens},
        )

        return ProviderResponse(
            raw_response=response, parsed_content=response.text, provider=Provider.GEMINI, model=self.config.model
        )


class AnthropicProvider:
    """Anthropic Claude provider implementation"""

    def __init__(self, config: LLMConfig):
        """Initialize Anthropic provider"""
        self.config = config
        self._client: Optional[Any] = None

    def _get_client(self) -> Any:
        """Get or create Anthropic client"""
        if self._client is None:
            try:
                from anthropic import Anthropic

                api_key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("Anthropic API key not found")
                self._client = Anthropic(api_key=api_key)
            except ImportError:
                raise ImportError("anthropic package not installed")
        return self._client

    def query(self, messages: List[Message]) -> ProviderResponse:
        """Query Anthropic API"""
        client = self._get_client()

        # Separate system message
        system_msg = next((m.content for m in messages if m.role == Role.SYSTEM), None)
        other_messages = [m for m in messages if m.role != Role.SYSTEM]

        # Convert to Anthropic format
        api_messages = [{"role": msg.role.value, "content": msg.content} for msg in other_messages]

        # Make API call
        kwargs = {
            "model": self.config.model,
            "messages": api_messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens or 4096,
        }
        if system_msg:
            kwargs["system"] = system_msg

        response = client.messages.create(**kwargs)

        # Parse response
        content = response.content[0].text if response.content else ""

        return ProviderResponse(
            raw_response=response, parsed_content=content, provider=Provider.ANTHROPIC, model=self.config.model
        )


# ==============================================================================
# UNIFIED LLM GATEWAY
# ==============================================================================


class UnifiedLLMGateway:
    """
    Unified gateway for all LLM providers.
    Uses prompts_v3 for strategies, providers for API calls.
    """

    def __init__(self) -> None:
        """Initialize gateway"""
        self.strategy_engine = StrategyEngine()
        self._providers: Dict[str, Union[OpenAIProvider, GeminiProvider, AnthropicProvider]] = {}
        self._default_config = self._load_default_config()

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration from llm_models.json"""
        config_path = Path(__file__).parent / "llm_models.json"
        if config_path.exists():
            with open(config_path) as f:
                data = json.load(f)
                # Handle both formats for backward compatibility
                if "default" in data:
                    return {
                        "default_provider": data["default"]["provider"],
                        "default_model": data["default"]["model"]
                    }
                return data
        return {"default_provider": "gemini", "default_model": "gemini-2.0-flash"}

    def _get_provider(self, config: LLMConfig) -> Union[OpenAIProvider, GeminiProvider, AnthropicProvider]:
        """Get or create provider instance"""
        key = f"{config.provider.value}:{config.model}"

        if key not in self._providers:
            if config.provider in [Provider.OPENAI]:
                self._providers[key] = OpenAIProvider(config)
            elif config.provider in [Provider.GEMINI, Provider.GOOGLE]:
                self._providers[key] = GeminiProvider(config)
            elif config.provider in [Provider.ANTHROPIC]:
                self._providers[key] = AnthropicProvider(config)
            else:
                raise ValueError(f"Unsupported provider: {config.provider}")

        return self._providers[key]  # type: ignore[return-value]

    def query(
        self, messages: List[Message], config: Optional[LLMConfig] = None, strategy: Optional[str] = None
    ) -> LLMResponse:
        """
        Query LLM with optional strategy from prompts_v3.

        Args:
            messages: Input messages
            config: LLM configuration
            strategy: Optional strategy name from prompts_v3

        Returns:
            LLM response with Pydantic v2 validation
        """
        # Use default config if not provided
        if config is None:
            config = LLMConfig(
                provider=Provider(self._default_config["default_provider"]), model=self._default_config["default_model"]
            )

        # Apply strategy if specified
        enhanced_messages = messages
        if strategy:
            enhanced_messages = self.strategy_engine.apply_strategy(messages, strategy)

        # Query provider
        start_time = datetime.now()
        provider = self._get_provider(config)
        provider_response = provider.query(enhanced_messages)
        latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        # Create response
        return LLMResponse(
            content=provider_response.parsed_content,
            provider=provider_response.provider,
            model=provider_response.model,
            strategy_used=strategy,
            latency_ms=latency_ms,
            metadata={
                "messages_count": len(enhanced_messages),
                "original_messages_count": len(messages),
                "strategy_applied": strategy is not None,
            },
        )

    def get_available_strategies(self) -> List[str]:
        """Get all available strategies from prompts_v3"""
        return self.strategy_engine.get_available_strategies()


# ==============================================================================
# PUBLIC API FUNCTIONS
# ==============================================================================

# Global gateway instance
_gateway = UnifiedLLMGateway()


def query_llm(
    provider: str,
    model: str,
    messages: List[Union[Message, Dict[str, str]]],
    strategy: Optional[str] = None,
    **kwargs: Any,
) -> LLMResponse:
    """
    Query LLM with specified provider and model.

    Args:
        provider: Provider name (openai, gemini, anthropic)
        model: Model name
        messages: List of messages
        strategy: Optional strategy from prompts_v3
        **kwargs: Additional configuration

    Returns:
        LLM response with full metadata
    """
    # Convert dict messages to Message objects
    typed_messages = []
    for msg in messages:
        if isinstance(msg, dict):
            typed_messages.append(Message(role=Role(msg["role"]), content=msg["content"]))
        else:
            typed_messages.append(msg)

    # Create config
    config = LLMConfig(
        provider=Provider(provider.lower()),
        model=model,
        temperature=kwargs.get("temperature", 0.7),
        max_tokens=kwargs.get("max_tokens"),
        timeout=kwargs.get("timeout", 120),
    )

    # Query through gateway
    return _gateway.query(typed_messages, config, strategy)


def call_default_llm(
    messages: List[Union[Message, Dict[str, str]]], strategy: Optional[str] = None, **kwargs: Any
) -> LLMResponse:
    """
    Query default LLM (configured in llm_models.json).

    Args:
        messages: List of messages
        strategy: Optional strategy from prompts_v3
        **kwargs: Additional configuration

    Returns:
        LLM response
    """
    config = _gateway._default_config
    return query_llm(
        provider=config["default_provider"],
        model=config["default_model"],
        messages=messages,
        strategy=strategy,
        **kwargs,
    )


def list_available_strategies() -> List[str]:
    """Get all available strategies from prompts_v3"""
    return _gateway.get_available_strategies()


def get_strategy_info(strategy: str) -> Optional[Dict[str, Any]]:
    """Get detailed information about a strategy"""
    return _gateway.strategy_engine.get_strategy_info(strategy)


# ==============================================================================
# SELF TEST
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("LLM V3 - Clean Integration with prompts_v3.py")
    print("=" * 60)
    print()

    # Test imports
    print("[TEST] Testing core imports...")
    assert Provider.GEMINI.value == "gemini"
    assert Role.USER.value == "user"
    print("[OK] Enums working")

    # Test Pydantic models
    msg = Message(role=Role.USER, content="Test message")
    assert msg.content == "Test message"
    print("[OK] Message model with Pydantic v2")

    response = LLMResponse(
        content="Test response", provider=Provider.GEMINI, model="gemini-2.0-flash", strategy_used="chain_of_thought"
    )
    assert response.provider == Provider.GEMINI
    print("[OK] LLMResponse model with Pydantic v2")

    # Test strategy engine
    print()
    print("[TEST] Testing StrategyEngine with prompts_v3...")
    engine = StrategyEngine()
    strategies = engine.get_available_strategies()
    print(f"[OK] Found {len(strategies)} strategies from prompts_v3")

    # Test strategy application
    messages = [Message(role=Role.USER, content="Explain quantum computing")]
    enhanced = engine.apply_strategy(messages, "chain_of_thought")
    assert len(enhanced[0].content) > len(messages[0].content)
    print(f"[OK] Strategy application: {len(messages[0].content)} -> {len(enhanced[0].content)} chars")

    # Test public API
    print()
    print("[TEST] Testing public API functions...")
    strategies = list_available_strategies()
    print(f"[OK] list_available_strategies: {len(strategies)} strategies")

    info = get_strategy_info("chain_of_thought")
    if info:
        print(f"[OK] get_strategy_info: {info['name']}")

    print()
    print("=" * 60)
    print("[SUCCESS] LLM V3 ready with clean prompts_v3 integration!")
    print()
    print("Key Features:")
    print("- All strategies from prompts_v3.py ONLY")
    print("- Full Pydantic v2 type enforcement")
    print("- Clean provider implementations")
    print("- No backward compatibility cruft")
    print("- Ready for production use")
