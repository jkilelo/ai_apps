"""
LLM Module - Configuration-Driven Multi-Provider Support
Uses llm_models.json for all model configurations
Supports OpenAI, Gemini, and Anthropic with 2025 latest APIs
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Iterator
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# Provider imports
try:
    from openai import OpenAI, AsyncOpenAI

    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    OpenAI = None
    AsyncOpenAI = None

try:
    from google import genai
    from google.genai import types as genai_types

    HAS_GEMINI = True
except ImportError:
    try:
        import google.generativeai as genai

        HAS_GEMINI = True
    except ImportError:
        HAS_GEMINI = False
        genai = None

try:
    from anthropic import Anthropic, AsyncAnthropic

    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    Anthropic = None
    AsyncAnthropic = None

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
    
    # Load .env from the correct path (parent of ui_testing_automation)
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)
    logger.info(f"Loaded environment from {env_path}")
except ImportError:
    logger.warning("dotenv not available")
except Exception as e:
    logger.warning(f"Could not load .env file: {e}")


# ==============================================================================
# PYDANTIC V2 CONTRACTS
# ==============================================================================


class LLMMessage(BaseModel):
    """Single message in conversation"""

    model_config = ConfigDict(str_strip_whitespace=True)

    role: str = Field(..., description="Message role (system/user/assistant)")
    content: str = Field(..., description="Message content")


class LLMResponse(BaseModel):
    """Standard LLM response contract"""

    model_config = ConfigDict(str_strip_whitespace=True)

    # Core response
    content: str = Field(..., description="Response content text")
    provider: str = Field(..., description="LLM provider used")
    model: str = Field(..., description="Model name used")

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.now)
    temperature: float = Field(0.0, description="Temperature used")
    max_tokens: int = Field(8192, description="Max tokens allowed")

    # Usage stats (optional)
    prompt_tokens: Optional[int] = Field(default=None, description="Tokens in prompt")
    completion_tokens: Optional[int] = Field(default=None, description="Tokens in completion")
    total_tokens: Optional[int] = Field(default=None, description="Total tokens used")

    # Streaming flag
    is_streaming: bool = Field(default=False, description="Whether response was streamed")


class LLMStreamChunk(BaseModel):
    """Single chunk in streaming response"""

    model_config = ConfigDict(str_strip_whitespace=True)

    content: str = Field(..., description="Chunk content")
    index: int = Field(..., description="Chunk index")
    finish_reason: Optional[str] = Field(default=None)


class LLMConfig(BaseModel):
    """LLM configuration from JSON"""

    model_config = ConfigDict(str_strip_whitespace=True)

    provider: str
    model: str
    supports_streaming: bool = Field(default=True)
    max_tokens: Optional[int] = Field(default=None)
    max_input_tokens: Optional[int] = Field(default=None)
    max_output_tokens: Optional[int] = Field(default=None)
    context_window: Optional[int] = Field(default=None)
    api_version: Optional[str] = Field(default=None)


# ==============================================================================
# CONFIGURATION LOADER
# ==============================================================================


class ConfigurationManager:
    """Manages LLM configurations from JSON file"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(__file__).parent / "llm_models.json"
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config from {self.config_path}: {e}")
            # Return minimal default config
            return {"default": {"provider": "gemini", "model": "gemini-2.5-flash"}, "providers": {}}

    def get_default_config(self) -> LLMConfig:
        """Get default LLM configuration"""
        default = self.config.get("default", {})
        return LLMConfig(**default)

    def get_model_config(self, provider: str, model: str) -> Optional[Dict[str, Any]]:
        """Get configuration for specific model"""
        providers = self.config.get("providers", {})
        if provider in providers:
            models = providers[provider].get("models", [])
            for model_config in models:
                if model_config.get("model") == model:
                    return model_config
        return None

    def get_fallback_models(self) -> List[LLMConfig]:
        """Get fallback model configurations"""
        fallback_order = self.config.get("fallback_order", [])
        return [LLMConfig(**f) for f in fallback_order]


# ==============================================================================
# PROVIDER IMPLEMENTATIONS
# ==============================================================================


class OpenAIProvider:
    """OpenAI provider implementation (GPT-5, GPT-4o, O-series)"""

    def __init__(self, api_key: Optional[str] = None):
        if OpenAI is None:
            raise ImportError("openai package not installed. Run: pip install openai")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found")

        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)

    def generate(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> LLMResponse:
        """Generate response using OpenAI"""

        # Handle max_tokens based on model
        kwargs = {"model": model, "messages": messages, "temperature": temperature}

        # GPT-5 and newer models use max_completion_tokens
        if "gpt-5" in model or "o3" in model or "o4" in model:
            if max_tokens:
                kwargs["max_completion_tokens"] = max_tokens
        else:
            if max_tokens:
                kwargs["max_tokens"] = max_tokens

        if stream:
            kwargs["stream"] = True
            return self._handle_stream(kwargs)

        response = self.client.chat.completions.create(**kwargs)

        content = response.choices[0].message.content or ""

        return LLMResponse(
            content=content,
            provider="openai",
            model=model,
            temperature=temperature,
            max_tokens=max_tokens or 128000,
            prompt_tokens=response.usage.prompt_tokens if response.usage else None,
            completion_tokens=response.usage.completion_tokens if response.usage else None,
            total_tokens=response.usage.total_tokens if response.usage else None,
            is_streaming=False,
        )

    def _handle_stream(self, kwargs: Dict[str, Any]) -> LLMResponse:
        """Handle streaming response"""
        stream = self.client.chat.completions.create(**kwargs)

        full_content = []
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_content.append(chunk.choices[0].delta.content)

        return LLMResponse(
            content="".join(full_content),
            provider="openai",
            model=kwargs["model"],
            temperature=kwargs["temperature"],
            max_tokens=kwargs.get("max_tokens") or kwargs.get("max_completion_tokens") or 128000,
            is_streaming=True,
        )

    def stream(
        self, model: str, messages: List[Dict[str, Any]], temperature: float = 0.0, max_tokens: Optional[int] = None
    ) -> Iterator[LLMStreamChunk]:
        """Stream response chunks"""
        kwargs = {"model": model, "messages": messages, "temperature": temperature, "stream": True}

        if "gpt-5" in model or "o3" in model or "o4" in model:
            if max_tokens:
                kwargs["max_completion_tokens"] = max_tokens
        else:
            if max_tokens:
                kwargs["max_tokens"] = max_tokens

        stream = self.client.chat.completions.create(**kwargs)

        index = 0
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield LLMStreamChunk(
                    content=chunk.choices[0].delta.content, index=index, finish_reason=chunk.choices[0].finish_reason
                )
                index += 1


class GeminiProvider:
    """Google Gemini provider implementation (2.0, 2.5 models)"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not found")

        # Check which Gemini SDK is available
        self.use_new_sdk = False

        if genai is not None:
            if hasattr(genai, "Client"):
                # New google-genai SDK (2025)
                self.use_new_sdk = True
                self.client = genai.Client(api_key=self.api_key)
            else:
                # Legacy google-generativeai SDK
                genai.configure(api_key=self.api_key)
        else:
            raise ImportError("No Gemini SDK found. Install: pip install google-genai or google-generativeai")

    def generate(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> LLMResponse:
        """Generate response using Gemini"""

        if self.use_new_sdk:
            return self._generate_new_sdk(model, messages, temperature, max_tokens, stream)
        else:
            return self._generate_legacy_sdk(model, messages, temperature, max_tokens, stream)

    def _generate_new_sdk(
        self, model: str, messages: List[Dict[str, Any]], temperature: float, max_tokens: Optional[int], stream: bool
    ) -> LLMResponse:
        """Generate using new google-genai SDK"""

        # Prepare messages for Gemini format
        system_instruction = None
        contents = []

        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                contents.append(msg["content"])
            elif msg["role"] == "assistant":
                # For multi-turn, need to handle differently
                pass

        # Combine all user messages for now
        combined_content = "\n".join(contents) if contents else "Hello"

        config = {"temperature": temperature, "max_output_tokens": min(max_tokens or 8192, 8192)}

        if system_instruction:
            config["system_instruction"] = system_instruction

        if stream:
            response_stream = self.client.models.generate_content_stream(
                model=model,
                contents=combined_content,
                config=genai_types.GenerateContentConfig(**config) if hasattr(genai, "types") else config,
            )

            full_content = []
            for chunk in response_stream:
                if hasattr(chunk, "text"):
                    full_content.append(chunk.text)

            return LLMResponse(
                content="".join(full_content),
                provider="gemini",
                model=model,
                temperature=temperature,
                max_tokens=max_tokens or 8192,
                is_streaming=True,
            )
        else:
            response = self.client.models.generate_content(
                model=model,
                contents=combined_content,
                config=genai_types.GenerateContentConfig(**config) if hasattr(genai, "types") else config,
            )

            content = response.text if hasattr(response, "text") else str(response)

            return LLMResponse(
                content=content,
                provider="gemini",
                model=model,
                temperature=temperature,
                max_tokens=max_tokens or 8192,
                is_streaming=False,
            )

    def _generate_legacy_sdk(
        self, model: str, messages: List[Dict[str, Any]], temperature: float, max_tokens: Optional[int], stream: bool
    ) -> LLMResponse:
        """Generate using legacy google-generativeai SDK"""

        # Convert messages to Gemini format
        gemini_messages = []
        system_message = None

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            elif msg["role"] == "user":
                gemini_messages.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                gemini_messages.append({"role": "model", "parts": [msg["content"]]})

        generation_config = {
            "temperature": temperature,
            "max_output_tokens": min(max_tokens or 8192, 8192),
        }

        # Create model
        if system_message:
            gemini_model = genai.GenerativeModel(
                model_name=model, generation_config=generation_config, system_instruction=system_message
            )
        else:
            gemini_model = genai.GenerativeModel(model_name=model, generation_config=generation_config)

        # Generate response
        if len(gemini_messages) > 1:
            chat = gemini_model.start_chat(history=gemini_messages[:-1])
            response = chat.send_message(gemini_messages[-1]["parts"][0], stream=stream)
        else:
            content_to_send = gemini_messages[0]["parts"][0] if gemini_messages else "Hello"
            response = gemini_model.generate_content(content_to_send, stream=stream)

        if stream:
            full_content = []
            for chunk in response:
                if hasattr(chunk, "text"):
                    full_content.append(chunk.text)

            return LLMResponse(
                content="".join(full_content),
                provider="gemini",
                model=model,
                temperature=temperature,
                max_tokens=max_tokens or 8192,
                is_streaming=True,
            )
        else:
            # Extract text content
            content = ""
            if hasattr(response, "text"):
                content = response.text
            elif hasattr(response, "candidates") and response.candidates:
                content = response.candidates[0].content.parts[0].text

            return LLMResponse(
                content=content,
                provider="gemini",
                model=model,
                temperature=temperature,
                max_tokens=max_tokens or 8192,
                is_streaming=False,
            )


class AnthropicProvider:
    """Anthropic provider implementation (Claude 3.5, Sonnet 4)"""

    def __init__(self, api_key: Optional[str] = None):
        if Anthropic is None:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not found")

        self.client = Anthropic(api_key=self.api_key)
        self.async_client = AsyncAnthropic(api_key=self.api_key)

    def generate(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> LLMResponse:
        """Generate response using Anthropic"""

        # Separate system message
        system_message = None
        claude_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                claude_messages.append({"role": msg["role"], "content": msg["content"]})

        kwargs = {
            "model": model,
            "messages": claude_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 8192,
        }

        if system_message:
            kwargs["system"] = system_message

        if stream:
            # Use streaming helper for better experience
            with self.client.messages.stream(**kwargs) as stream:
                full_content = []
                for text in stream.text_stream:
                    full_content.append(text)

                # Get final message for usage stats
                message = stream.get_final_message()

                return LLMResponse(
                    content="".join(full_content),
                    provider="anthropic",
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens or 8192,
                    prompt_tokens=message.usage.input_tokens if hasattr(message, "usage") else None,
                    completion_tokens=message.usage.output_tokens if hasattr(message, "usage") else None,
                    is_streaming=True,
                )
        else:
            response = self.client.messages.create(**kwargs)

            # Extract content from response
            content = ""
            if hasattr(response, "content"):
                if isinstance(response.content, list):
                    content = response.content[0].text if response.content else ""
                else:
                    content = response.content

            return LLMResponse(
                content=content,
                provider="anthropic",
                model=model,
                temperature=temperature,
                max_tokens=max_tokens or 8192,
                prompt_tokens=response.usage.input_tokens if hasattr(response, "usage") else None,
                completion_tokens=response.usage.output_tokens if hasattr(response, "usage") else None,
                is_streaming=False,
            )

    def stream(
        self, model: str, messages: List[Dict[str, Any]], temperature: float = 0.0, max_tokens: Optional[int] = None
    ) -> Iterator[LLMStreamChunk]:
        """Stream response chunks"""

        # Separate system message
        system_message = None
        claude_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                claude_messages.append({"role": msg["role"], "content": msg["content"]})

        kwargs = {
            "model": model,
            "messages": claude_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 8192,
        }

        if system_message:
            kwargs["system"] = system_message

        with self.client.messages.stream(**kwargs) as stream:
            index = 0
            for text in stream.text_stream:
                yield LLMStreamChunk(content=text, index=index, finish_reason=None)
                index += 1


# ==============================================================================
# MAIN API FUNCTIONS
# ==============================================================================

# Global configuration manager
_config_manager = ConfigurationManager()

# Provider instances cache
_providers: Dict[str, Any] = {}


def _get_provider(provider_name: str) -> Any:
    """Get or create provider instance"""
    if provider_name not in _providers:
        if provider_name.lower() == "openai":
            _providers[provider_name] = OpenAIProvider()
        elif provider_name.lower() == "gemini":
            _providers[provider_name] = GeminiProvider()
        elif provider_name.lower() == "anthropic":
            _providers[provider_name] = AnthropicProvider()
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")

    return _providers[provider_name]


def query_llm(
    model: str,
    messages: List[Dict[str, Any]],
    llm_provider: str = "gemini",
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
    stream: bool = False,
) -> LLMResponse:
    """
    Query LLM with specified model and provider.
    All configuration comes from llm_models.json.

    Args:
        model: Model name from configuration
        messages: List of message dicts with 'role' and 'content'
        llm_provider: Provider name (openai, gemini, anthropic)
        temperature: Sampling temperature (0.0 to 1.0)
        max_tokens: Maximum tokens in response
        stream: Whether to stream the response

    Returns:
        LLMResponse with the generated content and metadata
    """

    # Get model configuration
    model_config = _config_manager.get_model_config(llm_provider, model)

    # Use configured max tokens if not specified
    if max_tokens is None and model_config:
        max_tokens = model_config.get("max_output_tokens") or model_config.get("max_tokens")

    # Get provider and generate
    provider = _get_provider(llm_provider)

    try:
        return provider.generate(
            model=model, messages=messages, temperature=temperature, max_tokens=max_tokens, stream=stream
        )
    except Exception as e:
        logger.error(f"Failed with {llm_provider}/{model}: {e}")

        # Try fallback models
        for fallback in _config_manager.get_fallback_models():
            try:
                logger.info(f"Trying fallback: {fallback.provider}/{fallback.model}")
                provider = _get_provider(fallback.provider)
                return provider.generate(
                    model=fallback.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream,
                )
            except Exception as fallback_error:
                logger.error(f"Fallback failed: {fallback_error}")
                continue

        # All attempts failed
        raise RuntimeError(f"All LLM providers failed. Last error: {e}")


def call_default_llm(messages: List[Dict[str, Any]]) -> LLMResponse:
    """
    Call the default LLM from configuration.

    Args:
        messages: List of message dicts with 'role' and 'content'

    Returns:
        LLMResponse with the generated content and metadata
    """

    default_config = _config_manager.get_default_config()

    return query_llm(
        model=default_config.model,
        messages=messages,
        llm_provider=default_config.provider,
        temperature=0.0,
        max_tokens=default_config.max_tokens,
        stream=False,
    )


def stream_llm(
    model: str,
    messages: List[Dict[str, Any]],
    llm_provider: str = "gemini",
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
) -> Iterator[LLMStreamChunk]:
    """
    Stream response from LLM.

    Args:
        model: Model name from configuration
        messages: List of message dicts with 'role' and 'content'
        llm_provider: Provider name (openai, gemini, anthropic)
        temperature: Sampling temperature (0.0 to 1.0)
        max_tokens: Maximum tokens in response

    Yields:
        LLMStreamChunk objects with content chunks
    """

    # Get model configuration
    model_config = _config_manager.get_model_config(llm_provider, model)

    # Check if streaming is supported
    if model_config and not model_config.get("supports_streaming", True):
        raise ValueError(f"Model {model} does not support streaming")

    # Use configured max tokens if not specified
    if max_tokens is None and model_config:
        max_tokens = model_config.get("max_output_tokens") or model_config.get("max_tokens")

    # Get provider and stream
    provider = _get_provider(llm_provider)

    if hasattr(provider, "stream"):
        yield from provider.stream(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
    else:
        # Fallback to non-streaming if provider doesn't support it
        response = provider.generate(
            model=model, messages=messages, temperature=temperature, max_tokens=max_tokens, stream=False
        )
        yield LLMStreamChunk(content=response.content, index=0, finish_reason="stop")


def get_available_models(provider: Optional[str] = None) -> List[str]:
    """Get list of available models for a provider or all providers"""

    if provider:
        providers = {provider: _config_manager.config.get("providers", {}).get(provider, {})}
    else:
        providers = _config_manager.config.get("providers", {})

    models = []
    for provider_name, provider_config in providers.items():
        for model_config in provider_config.get("models", []):
            models.append(f"{provider_name}/{model_config['model']}")

    return models


if __name__ == "__main__":
    # Test the module
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "What's the capital city of Kenya? Reply with only one word"},
    ]

    try:
        # Test default LLM
        response = call_default_llm(messages)
        print(f"Default LLM Response: {response.content}")
        print(f"Provider: {response.provider}, Model: {response.model}")

        # Test streaming
        print("\nStreaming test:")
        for chunk in stream_llm(model=response.model, messages=messages, llm_provider=response.provider):
            print(chunk.content, end="", flush=True)
        print()

    except Exception as e:
        print(f"Error: {e}")
