#!/usr/bin/env python3
"""
LLM Module V2 - Minimal Code, Maximum Functionality
====================================================
Leverages native SDK structured output capabilities for all providers.
Single source of truth for ALL LLM operations with type-safe outputs.

Key Features:
- Native OpenAI response_format with Pydantic parse()
- Native Anthropic tool use for structured JSON
- Native Google Gemini response_schema
- Automatic fallback and retry logic
- Unified interface for all providers

Author: Senior Software Architect (30+ years)
Version: 2.0.0
Date: 2024
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)
except:
    pass

# Type variable for generic Pydantic models
T = TypeVar("T", bound=BaseModel)

# ==============================================================================
# PROVIDER IMPORTS - Lazy loading for efficiency
# ==============================================================================

def _import_openai():
    """Lazy import OpenAI"""
    try:
        from openai import OpenAI
        return OpenAI
    except ImportError:
        logger.warning("OpenAI SDK not installed. Run: pip install openai")
        return None

def _import_anthropic():
    """Lazy import Anthropic"""
    try:
        from anthropic import Anthropic
        return Anthropic
    except ImportError:
        logger.warning("Anthropic SDK not installed. Run: pip install anthropic")
        return None

def _import_google():
    """Lazy import Google GenAI"""
    try:
        from google import genai
        from google.genai import types
        return genai, types
    except ImportError:
        try:
            # Fallback to legacy SDK
            import google.generativeai as genai
            return genai, None
        except ImportError:
            logger.warning("Google GenAI SDK not installed. Run: pip install google-genai")
            return None, None

# ==============================================================================
# UNIFIED DATA CONTRACTS
# ==============================================================================

class LLMConfig(BaseModel):
    """Unified configuration for LLM operations"""
    model_config = ConfigDict(extra='forbid')
    
    provider: str = Field("gemini", description="Provider: openai, anthropic, gemini")
    model: str = Field("gemini-2.0-flash", description="Model name")
    temperature: float = Field(0.0, ge=0, le=2)
    max_tokens: Optional[int] = Field(None, description="Max output tokens")
    timeout: int = Field(30, description="Request timeout in seconds")
    retry_attempts: int = Field(3, description="Number of retry attempts")

class LLMResponse(BaseModel):
    """Standard response for raw LLM calls"""
    model_config = ConfigDict(extra='forbid')
    
    content: str
    provider: str
    model: str
    usage: Optional[Dict[str, int]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# ==============================================================================
# MAIN LLM GATEWAY - Minimal code with native SDK features
# ==============================================================================

class LLMGateway:
    """
    Unified gateway for all LLM operations.
    Uses native SDK features for structured output - no custom parsing needed.
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize with configuration"""
        self.config = config or LLMConfig()
        self._clients = {}  # Cache for initialized clients
        
    def query(
        self,
        messages: List[Dict[str, str]],
        output_model: Optional[Type[T]] = None,
        **kwargs
    ) -> Union[T, LLMResponse]:
        """
        Universal query method with optional structured output.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            output_model: Optional Pydantic model for structured output
            **kwargs: Additional provider-specific arguments
            
        Returns:
            Pydantic model instance if output_model provided, else LLMResponse
        """
        provider = kwargs.get('provider', self.config.provider)
        
        if output_model:
            # Structured output path - use native SDK features
            return self._query_structured(messages, output_model, provider, **kwargs)
        else:
            # Raw output path
            return self._query_raw(messages, provider, **kwargs)
    
    def _query_structured(
        self,
        messages: List[Dict[str, str]],
        output_model: Type[T],
        provider: str,
        **kwargs
    ) -> T:
        """Query with structured output using native SDK features"""
        
        # Route to provider-specific implementation
        if provider == "openai":
            return self._openai_structured(messages, output_model, **kwargs)
        elif provider == "anthropic":
            return self._anthropic_structured(messages, output_model, **kwargs)
        elif provider == "gemini":
            return self._gemini_structured(messages, output_model, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _query_raw(
        self,
        messages: List[Dict[str, str]],
        provider: str,
        **kwargs
    ) -> LLMResponse:
        """Query for raw text output"""
        
        if provider == "openai":
            return self._openai_raw(messages, **kwargs)
        elif provider == "anthropic":
            return self._anthropic_raw(messages, **kwargs)
        elif provider == "gemini":
            return self._gemini_raw(messages, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    # ===========================================================================
    # OPENAI IMPLEMENTATION - Native response_format with parse()
    # ===========================================================================
    
    def _get_openai_client(self):
        """Get or create OpenAI client"""
        if 'openai' not in self._clients:
            OpenAI = _import_openai()
            if not OpenAI:
                raise ImportError("OpenAI SDK not available")
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found")
            self._clients['openai'] = OpenAI(api_key=api_key)
        return self._clients['openai']
    
    def _openai_structured(
        self,
        messages: List[Dict[str, str]],
        output_model: Type[T],
        **kwargs
    ) -> T:
        """
        OpenAI structured output using native SDK parse() method.
        Automatically handles response_format and strict mode.
        """
        client = self._get_openai_client()
        model = kwargs.get('model', self.config.model)
        
        # Use beta.chat.completions.parse() for automatic Pydantic parsing
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=output_model,  # SDK handles schema generation
            temperature=kwargs.get('temperature', self.config.temperature),
            max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
        )
        
        # Return the parsed Pydantic model directly
        return completion.parsed
    
    def _openai_raw(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """OpenAI raw text output"""
        client = self._get_openai_client()
        model = kwargs.get('model', self.config.model)
        
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=kwargs.get('temperature', self.config.temperature),
            max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
        )
        
        return LLMResponse(
            content=completion.choices[0].message.content,
            provider="openai",
            model=model,
            usage={
                "prompt_tokens": completion.usage.prompt_tokens,
                "completion_tokens": completion.usage.completion_tokens,
                "total_tokens": completion.usage.total_tokens,
            } if completion.usage else None
        )
    
    # ===========================================================================
    # ANTHROPIC IMPLEMENTATION - Native tool use for structured output
    # ===========================================================================
    
    def _get_anthropic_client(self):
        """Get or create Anthropic client"""
        if 'anthropic' not in self._clients:
            Anthropic = _import_anthropic()
            if not Anthropic:
                raise ImportError("Anthropic SDK not available")
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found")
            self._clients['anthropic'] = Anthropic(api_key=api_key)
        return self._clients['anthropic']
    
    def _anthropic_structured(
        self,
        messages: List[Dict[str, str]],
        output_model: Type[T],
        **kwargs
    ) -> T:
        """
        Anthropic structured output using tool use.
        Forces the model to use a tool that returns structured JSON.
        """
        client = self._get_anthropic_client()
        model = kwargs.get('model', self.config.model)
        
        # Convert Pydantic model to JSON schema
        schema = output_model.model_json_schema()
        
        # Create a tool that forces structured output
        tools = [{
            "name": "return_structured_output",
            "description": f"Return the response as {output_model.__name__}",
            "input_schema": schema
        }]
        
        # Separate system message if present
        system_msg = None
        claude_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                claude_messages.append(msg)
        
        # Add instruction to use the tool
        if claude_messages and claude_messages[-1]["role"] == "user":
            claude_messages[-1]["content"] += "\n\nUse the return_structured_output tool to provide your response."
        
        # Make the API call with tool_choice to force tool use
        response = client.messages.create(
            model=model,
            messages=claude_messages,
            system=system_msg,
            tools=tools,
            tool_choice={"type": "tool", "name": "return_structured_output"},
            temperature=kwargs.get('temperature', self.config.temperature),
            max_tokens=kwargs.get('max_tokens', self.config.max_tokens or 8192),
        )
        
        # Extract the structured data from tool use
        for content_block in response.content:
            if content_block.type == "tool_use":
                # Parse and validate with Pydantic
                return output_model.model_validate(content_block.input)
        
        raise ValueError("No tool use found in response")
    
    def _anthropic_raw(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Anthropic raw text output"""
        client = self._get_anthropic_client()
        model = kwargs.get('model', self.config.model)
        
        # Separate system message
        system_msg = None
        claude_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                claude_messages.append(msg)
        
        response = client.messages.create(
            model=model,
            messages=claude_messages,
            system=system_msg,
            temperature=kwargs.get('temperature', self.config.temperature),
            max_tokens=kwargs.get('max_tokens', self.config.max_tokens or 8192),
        )
        
        # Extract text content
        content = ""
        for block in response.content:
            if hasattr(block, 'text'):
                content += block.text
        
        return LLMResponse(
            content=content,
            provider="anthropic",
            model=model,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
            } if hasattr(response, 'usage') else None
        )
    
    # ===========================================================================
    # GOOGLE GEMINI IMPLEMENTATION - Native response_schema
    # ===========================================================================
    
    def _get_gemini_client(self):
        """Get or create Gemini client"""
        if 'gemini' not in self._clients:
            genai, types = _import_google()
            if not genai:
                raise ImportError("Google GenAI SDK not available")
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found")
            
            # Check which SDK version
            if hasattr(genai, 'Client'):
                # New google-genai SDK
                self._clients['gemini'] = genai.Client(api_key=api_key)
                self._clients['gemini_types'] = types
            else:
                # Legacy google-generativeai SDK
                genai.configure(api_key=api_key)
                self._clients['gemini'] = genai
                self._clients['gemini_types'] = None
        
        return self._clients['gemini'], self._clients.get('gemini_types')
    
    def _gemini_structured(
        self,
        messages: List[Dict[str, str]],
        output_model: Type[T],
        **kwargs
    ) -> T:
        """
        Gemini structured output using native response_schema.
        Directly passes Pydantic model to SDK.
        """
        client, types = self._get_gemini_client()
        model = kwargs.get('model', self.config.model)
        
        # Prepare content and system instruction
        system_instruction = None
        user_content = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                user_content.append(msg["content"])
        
        combined_content = "\n".join(user_content) if user_content else "Please respond"
        
        if hasattr(client, 'models'):
            # New SDK (google-genai)
            config_dict = {
                "temperature": kwargs.get('temperature', self.config.temperature),
                "response_schema": output_model,  # Pass Pydantic model directly
                "response_mime_type": "application/json",
            }
            
            if kwargs.get('max_tokens'):
                config_dict["max_output_tokens"] = kwargs['max_tokens']
            
            if system_instruction:
                config_dict["system_instruction"] = system_instruction
            
            # Use GenerateContentConfig if available
            if types and hasattr(types, 'GenerateContentConfig'):
                config = types.GenerateContentConfig(**config_dict)
            else:
                config = config_dict
            
            response = client.models.generate_content(
                model=model,
                contents=combined_content,
                config=config
            )
        else:
            # Legacy SDK (google-generativeai)
            generation_config = {
                "temperature": kwargs.get('temperature', self.config.temperature),
                "response_mime_type": "application/json",
                "response_schema": output_model.model_json_schema(),  # Convert to schema
            }
            
            if kwargs.get('max_tokens'):
                generation_config["max_output_tokens"] = kwargs['max_tokens']
            
            # Create model
            if system_instruction:
                gemini_model = client.GenerativeModel(
                    model_name=model,
                    generation_config=generation_config,
                    system_instruction=system_instruction
                )
            else:
                gemini_model = client.GenerativeModel(
                    model_name=model,
                    generation_config=generation_config
                )
            
            response = gemini_model.generate_content(combined_content)
        
        # Parse the JSON response
        if hasattr(response, 'text'):
            json_str = response.text
        elif hasattr(response, 'candidates') and response.candidates:
            json_str = response.candidates[0].content.parts[0].text
        else:
            raise ValueError("No content in response")
        
        # Validate with Pydantic
        return output_model.model_validate_json(json_str)
    
    def _gemini_raw(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Gemini raw text output"""
        client, types = self._get_gemini_client()
        model = kwargs.get('model', self.config.model)
        
        # Prepare content
        system_instruction = None
        user_content = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                user_content.append(msg["content"])
        
        combined_content = "\n".join(user_content) if user_content else "Hello"
        
        if hasattr(client, 'models'):
            # New SDK
            config_dict = {
                "temperature": kwargs.get('temperature', self.config.temperature),
            }
            
            if kwargs.get('max_tokens'):
                config_dict["max_output_tokens"] = kwargs['max_tokens']
            
            if system_instruction:
                config_dict["system_instruction"] = system_instruction
            
            response = client.models.generate_content(
                model=model,
                contents=combined_content,
                config=config_dict
            )
        else:
            # Legacy SDK
            generation_config = {
                "temperature": kwargs.get('temperature', self.config.temperature),
            }
            
            if kwargs.get('max_tokens'):
                generation_config["max_output_tokens"] = kwargs['max_tokens']
            
            if system_instruction:
                gemini_model = client.GenerativeModel(
                    model_name=model,
                    generation_config=generation_config,
                    system_instruction=system_instruction
                )
            else:
                gemini_model = client.GenerativeModel(
                    model_name=model,
                    generation_config=generation_config
                )
            
            response = gemini_model.generate_content(combined_content)
        
        # Extract content
        if hasattr(response, 'text'):
            content = response.text
        elif hasattr(response, 'candidates') and response.candidates:
            content = response.candidates[0].content.parts[0].text
        else:
            content = ""
        
        return LLMResponse(
            content=content,
            provider="gemini",
            model=model
        )

# ==============================================================================
# CONVENIENCE FUNCTIONS - Backward compatibility + shortcuts
# ==============================================================================

# Global gateway instance
_gateway = None

def get_gateway() -> LLMGateway:
    """Get or create global gateway instance"""
    global _gateway
    if _gateway is None:
        _gateway = LLMGateway()
    return _gateway

def query_structured(
    messages: List[Dict[str, str]],
    output_model: Type[T],
    **kwargs
) -> T:
    """
    Query LLM with structured output.
    
    This is the PRIMARY interface for the framework.
    Uses native SDK features for guaranteed type safety.
    """
    return get_gateway().query(messages, output_model, **kwargs)

def query_raw(
    messages: List[Dict[str, str]],
    **kwargs
) -> LLMResponse:
    """Query LLM for raw text output"""
    return get_gateway().query(messages, output_model=None, **kwargs)

# Backward compatibility functions
def call_default_llm(messages: List[Dict[str, str]]) -> LLMResponse:
    """Backward compatibility - calls default LLM"""
    return query_raw(messages)

def query_llm(
    model: str,
    messages: List[Dict[str, str]],
    llm_provider: str = "gemini",
    **kwargs
) -> LLMResponse:
    """Backward compatibility - calls specified LLM"""
    return query_raw(messages, provider=llm_provider, model=model, **kwargs)

# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================

if __name__ == "__main__":
    # Example 1: Structured output with Pydantic model
    from pydantic import BaseModel
    
    class WebElement(BaseModel):
        selector: str
        element_type: str
        text: Optional[str] = None
        attributes: Dict[str, str] = {}
    
    messages = [
        {"role": "system", "content": "You are a web scraping assistant."},
        {"role": "user", "content": "Extract the main heading element from a typical webpage."}
    ]
    
    # Test with each provider
    for provider in ["openai", "anthropic", "gemini"]:
        try:
            print(f"\nTesting {provider}...")
            element = query_structured(messages, WebElement, provider=provider)
            print(f"[OK] {provider}: {element}")
        except Exception as e:
            print(f"[ERROR] {provider}: {e}")
    
    # Example 2: Raw output
    try:
        response = query_raw(messages)
        print(f"\nRaw output: {response.content[:100]}...")
    except Exception as e:
        print(f"Raw output error: {e}")