import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Literal

from openai import OpenAI
from openai.types.chat import ChatCompletion
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Add project root to path
sys.path.append(str(Path(__file__).parent))
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


# Message Pydantic model
class Message(BaseModel):
    """Message model for LLM interactions"""

    role: Literal["system", "user", "assistant"]
    content: str


# Unified LLM Response class for provider-agnostic handling
class LLMResponse(BaseModel):
    """Unified response model for all LLM providers"""

    content: str
    raw_response: Any = None  # Store original response if needed
    provider: str = ""
    model: str = ""
    usage: dict[str, Any] = {}

    @classmethod
    def from_provider_response(cls, response: Any, provider: str, model: str = "") -> "LLMResponse":
        """
        Create LLMResponse from provider-specific response format

        Args:
            response: Raw response from the provider
            provider: Name of the provider (openai, gemini, claude)
            model: Model name used

        Returns:
            Unified LLMResponse object
        """
        content = ""
        usage = {}
        if provider in ["openai", "claude"]:
            # OpenAI and Claude use similar format: response.choices[0].message.content
            if hasattr(response, "choices") and len(response.choices) > 0:
                content = response.choices[0].message.content
            elif hasattr(response, "content"):
                # Some Claude responses might have direct content
                content = response.content

            # Extract usage if available
            if hasattr(response, "usage"):
                usage = {
                    "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(response.usage, "completion_tokens", 0),
                    "total_tokens": getattr(response.usage, "total_tokens", 0),
                }
        elif provider == "gemini":
            # Gemini might have different response structure
            if hasattr(response, "choices") and len(response.choices) > 0:
                # Gemini via OpenAI compatibility endpoint
                content = response.choices[0].message.content
            elif hasattr(response, "text"):
                # Native Gemini response
                content = response.text
            elif hasattr(response, "content"):
                content = response.content

            # Extract usage if available
            if hasattr(response, "usage"):
                usage = {
                    "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(response.usage, "completion_tokens", 0),
                    "total_tokens": getattr(response.usage, "total_tokens", 0),
                }
        # Fallback for unknown providers
        elif hasattr(response, "choices") and len(response.choices) > 0:
            content = response.choices[0].message.content
        elif hasattr(response, "content"):
            content = response.content
        elif hasattr(response, "text"):
            content = response.text
        else:
            # Last resort: convert to string
            content = str(response)

        return cls(
            content=content,
            raw_response=response,
            provider=provider,
            model=model,
            usage=usage,
        )


# clients
gemini_client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),  # Your Google API key
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
openai_client = OpenAI()

claude_client = OpenAI(
    api_key=os.getenv("ANTHROPIC_API_KEY"),  # Your Anthropic API key
    base_url="https://api.anthropic.com/v1/",  # Anthropic's API endpoint
)


class UnsupportedProviderError(Exception):
    """Raised when an unsupported provider is requested."""

    def __init__(self, provider: str) -> None:
        super().__init__(f"Unsupported provider: {provider}")


def query_llm(provider: str, model: str, messages: list[dict[str, str]], return_raw: bool = False):
    """
    Query the LLM with the given provider, model, and messages.

    Args:
        provider: LLM provider name
        model: Model to use
        messages: List of messages
        return_raw: If True, return raw provider response. If False, return LLMResponse

    Returns:
        LLMResponse or raw response based on return_raw flag
    """
    if provider == "gemini":
        response = gemini_client.chat.completions.create(model=model, messages=messages)
    elif provider == "openai":
        response = openai_client.chat.completions.create(model=model, messages=messages)
    elif provider == "claude":
        response = claude_client.chat.completions.create(model=model, messages=messages)
    else:
        raise UnsupportedProviderError(provider)

    if return_raw:
        return response

    return LLMResponse.from_provider_response(response, provider, model)


def call_default_llm(
    messages: list[Message],
    _strategy: str | None = None,
    provider: str | None = None,
    model: str | None = None,
) -> LLMResponse:
    """
    Call the default LLM with Message objects.

    Args:
        messages: List of Message objects
        _strategy: Optional strategy parameter (for future use)
        provider: Optional provider override (defaults to "openai")
        model: Optional model override (defaults to "gpt-4.1" for openai)

    Returns:
        LLMResponse with unified interface
    """
    timeout: int = 30

    # Use provided or default provider/model
    if provider is None:
        provider = "gemini"

    if model is None:
        # Default models per provider
        default_models = {
            "openai": "gpt-4.1",
            "gemini": "gemini-2.5-pro",
            "claude": "claude-sonnet-4-20250514",
        }
        model = default_models.get(provider, "gemini-2.5-pro")

    # Convert Message objects to dicts for API call
    message_dicts = [{"role": msg.role, "content": msg.content} for msg in messages]

    start_time = time.time()
    response = query_llm(provider, model, message_dicts, return_raw=False)

    elapsed_time = time.time() - start_time
    if elapsed_time > timeout:
        logging.warning(
            f"Response from {provider}/{model} took too long: {elapsed_time:.2f} seconds"
        )

    logging.info(f"LLM Response from {provider}/{model}: {len(response.content)} chars")

    return response


def default_llm(messages: list | None = None) -> ChatCompletion:
    timeout: int = 30
    provider: str = "openai"
    model: str = "gpt-4.1"
    """Default LLM query function."""
    if messages is None:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that genuinely helps users.",
            },
            {
                "role": "user",
                "content": "What is the meaning of life? Reply with 10 words or less.",
            },
        ]

    start_time = time.time()
    response = query_llm(provider, model, messages)

    elapsed_time = time.time() - start_time
    if elapsed_time > timeout:
        logging.warning(f"Response took too long: {elapsed_time:.2f} seconds")

    return response


if __name__ == "__main__":
    # test all llm
    provider_and_models = [
        ("gemini", "gemini-2.5-pro"),
        ("openai", "gpt-4.1"),
        ("claude", "claude-sonnet-4-20250514"),
    ]
    messages = [
        {"role": "system", "content": "You are a helpful assistant that genuinely helps users."},
        {"role": "user", "content": "What is the meaning of life? Reply with 10 words or less."},
    ]
    for provider, model in provider_and_models:
        response = query_llm(provider, model, messages)
        res = response.model_dump()
        logging.info(f"Response from {provider}: {res}")
