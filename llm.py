import os
from pathlib import Path
import sys
from openai import OpenAI
import json
import logging
import time
from openai.types.chat import ChatCompletion
from pydantic import BaseModel
from typing import List, Dict, Any, Literal


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

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
    usage: Dict[str, Any] = {}
    
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
            if hasattr(response, 'choices') and len(response.choices) > 0:
                content = response.choices[0].message.content
            elif hasattr(response, 'content'):
                # Some Claude responses might have direct content
                content = response.content
            
            # Extract usage if available
            if hasattr(response, 'usage'):
                usage = {
                    "prompt_tokens": getattr(response.usage, 'prompt_tokens', 0),
                    "completion_tokens": getattr(response.usage, 'completion_tokens', 0),
                    "total_tokens": getattr(response.usage, 'total_tokens', 0)
                }
                
        elif provider == "gemini":
            # Gemini might have different response structure
            if hasattr(response, 'choices') and len(response.choices) > 0:
                # Gemini via OpenAI compatibility endpoint
                content = response.choices[0].message.content
            elif hasattr(response, 'text'):
                # Native Gemini response
                content = response.text
            elif hasattr(response, 'content'):
                content = response.content
            
            # Extract usage if available
            if hasattr(response, 'usage'):
                usage = {
                    "prompt_tokens": getattr(response.usage, 'prompt_tokens', 0),
                    "completion_tokens": getattr(response.usage, 'completion_tokens', 0),
                    "total_tokens": getattr(response.usage, 'total_tokens', 0)
                }
        else:
            # Fallback for unknown providers
            if hasattr(response, 'choices') and len(response.choices) > 0:
                content = response.choices[0].message.content
            elif hasattr(response, 'content'):
                content = response.content
            elif hasattr(response, 'text'):
                content = response.text
            else:
                # Last resort: convert to string
                content = str(response)
        
        return cls(
            content=content,
            raw_response=response,
            provider=provider,
            model=model,
            usage=usage
        )

# clients
gemini_client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),  # Your Google API key
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
openai_client = OpenAI()

claude_client = OpenAI(
    api_key=os.getenv("ANTHROPIC_API_KEY"),  # Your Anthropic API key
    base_url="https://api.anthropic.com/v1/"  # Anthropic's API endpoint
)



def query_llm(provider, model, messages, return_raw=False):
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
        response = gemini_client.chat.completions.create(
            model=model,
            messages=messages
        )
    elif provider == "openai":
        response = openai_client.chat.completions.create(
            model=model,
            messages=messages
        )
    elif provider == "claude":
        response = claude_client.chat.completions.create(
            model=model,
            messages=messages
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    
    if return_raw:
        return response
    
    return LLMResponse.from_provider_response(response, provider, model)

def call_default_llm(messages) -> LLMResponse:
    """
    Call the default LLM with Message objects.
    
    Args:
        messages: List of Message objects
        strategy: Optional strategy parameter (for future use)
        provider: Optional provider override (defaults to "openai")
        model: Optional model override (defaults to "gpt-4.1" for openai)
        
    Returns:
        LLMResponse with unified interface
    """
    timeout: int = 30

    model = "gemini-2.5-pro"
    provider = "gemini"
    start_time = time.time()
    response = query_llm(provider, model, messages, return_raw=False)

    elapsed_time = time.time() - start_time
    if elapsed_time > timeout:
        logging.warning(f"Response from {provider}/{model} took too long: {elapsed_time:.2f} seconds")
    
    logging.info(f"LLM Response from {provider}/{model}: {len(response.content)} chars")
    
    return response

def default_llm(messages: list = None) -> ChatCompletion:   
    timeout: int = 30 
    provider: str = "openai"
    model: str = "gpt-4.1"
    """Default LLM query function."""
    if messages is None:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that genuinely helps users."
            },
            {
                "role": "user",
                "content": "What is the meaning of life? Reply with 10 words or less."
            }
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
        ("claude", "claude-sonnet-4-20250514")
    ]
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that genuinely helps users."
        },
        {
            "role": "user",
            "content": "What is the meaning of life? Reply with 10 words or less."
        }
    ]
    for provider, model in provider_and_models:
        response = query_llm(provider, model, messages)
        res = response.model_dump()
        logging.info(f"Response from {provider}: {res}")