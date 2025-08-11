"""
LLM Interface for Reverse Prompting

This module provides a unified interface for interacting with different
Large Language Models (OpenAI, Anthropic, Google, etc.) for code generation.
"""

import asyncio
import time
import json
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import random

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai

    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

from ..core.models import CodeLanguage, EngineConfig


class LLMProvider(Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


@dataclass
class LLMResponse:
    """Response from an LLM."""

    code: str
    model: str
    provider: str
    generation_time: float
    tokens_used: Optional[int] = None
    success: bool = True
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseLLMProvider:
    """Base class for LLM providers."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)

    async def generate_code(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        language: CodeLanguage = CodeLanguage.PYTHON,
        max_tokens: int = 4000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate code using the LLM."""
        raise NotImplementedError

    def _get_language_instructions(self, language: CodeLanguage) -> str:
        """Get language-specific instructions."""
        instructions = {
            CodeLanguage.PYTHON: "Generate clean, well-documented Python code. Use type hints and follow PEP 8.",
            CodeLanguage.JAVASCRIPT: "Generate modern JavaScript (ES6+) code with clear comments.",
            CodeLanguage.TYPESCRIPT: "Generate TypeScript code with proper type annotations.",
            CodeLanguage.JAVA: "Generate clean Java code following best practices.",
            CodeLanguage.CSHARP: "Generate C# code following Microsoft coding conventions.",
            CodeLanguage.CPP: "Generate modern C++ code (C++17 or later) with clear structure.",
            CodeLanguage.RUST: "Generate idiomatic Rust code with proper error handling.",
            CodeLanguage.GO: "Generate Go code following Go conventions and best practices.",
        }
        return instructions.get(language, "Generate clean, well-documented code.")


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI not available. Install with: pip install openai")

        self.client = openai.AsyncOpenAI(
            api_key=config.get("api_key"),
            base_url=config.get("base_url"),
            timeout=config.get("timeout", 60),
        )
        self.model = config.get("model", "gpt-4")

    async def generate_code(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        language: CodeLanguage = CodeLanguage.PYTHON,
        max_tokens: int = 4000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate code using OpenAI GPT."""
        start_time = time.time()

        try:
            # Prepare messages
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                default_system = f"""You are an expert programmer. {self._get_language_instructions(language)}
                
Generate only the code requested. Do not include explanations unless specifically asked.
Ensure the code is functional, efficient, and follows best practices."""
                messages.append({"role": "system", "content": default_system})

            messages.append({"role": "user", "content": prompt})

            # Make API call
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=self.config.get("timeout", 60),
            )

            generation_time = time.time() - start_time

            # Extract code from response
            content = response.choices[0].message.content
            code = self._extract_code_block(content)

            return LLMResponse(
                code=code,
                model=self.model,
                provider="openai",
                generation_time=generation_time,
                tokens_used=response.usage.total_tokens if response.usage else None,
                success=True,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "prompt_tokens": (
                        response.usage.prompt_tokens if response.usage else None
                    ),
                    "completion_tokens": (
                        response.usage.completion_tokens if response.usage else None
                    ),
                },
            )

        except Exception as e:
            generation_time = time.time() - start_time
            self.logger.error(f"OpenAI generation failed: {e}")

            return LLMResponse(
                code="",
                model=self.model,
                provider="openai",
                generation_time=generation_time,
                success=False,
                error=str(e),
            )

    def _extract_code_block(self, content: str) -> str:
        """Extract code from markdown code blocks."""
        if "```" in content:
            # Find the first code block
            lines = content.split("\n")
            in_code_block = False
            code_lines = []

            for line in lines:
                if line.strip().startswith("```") and not in_code_block:
                    in_code_block = True
                    continue
                elif line.strip().startswith("```") and in_code_block:
                    break
                elif in_code_block:
                    code_lines.append(line)

            if code_lines:
                return "\n".join(code_lines)

        # If no code block found, return the entire content
        return content.strip()


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic not available. Install with: pip install anthropic"
            )

        self.client = anthropic.AsyncAnthropic(
            api_key=config.get("api_key"), timeout=config.get("timeout", 60)
        )
        self.model = config.get("model", "claude-3-sonnet-20240229")

    async def generate_code(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        language: CodeLanguage = CodeLanguage.PYTHON,
        max_tokens: int = 4000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate code using Anthropic Claude."""
        start_time = time.time()

        try:
            # Prepare system prompt
            if not system_prompt:
                system_prompt = f"""You are an expert programmer. {self._get_language_instructions(language)}
                
Generate only the code requested. Do not include explanations unless specifically asked.
Ensure the code is functional, efficient, and follows best practices."""

            # Make API call
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )

            generation_time = time.time() - start_time

            # Extract code from response
            content = response.content[0].text
            code = self._extract_code_block(content)

            return LLMResponse(
                code=code,
                model=self.model,
                provider="anthropic",
                generation_time=generation_time,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                success=True,
                metadata={
                    "stop_reason": response.stop_reason,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
            )

        except Exception as e:
            generation_time = time.time() - start_time
            self.logger.error(f"Anthropic generation failed: {e}")

            return LLMResponse(
                code="",
                model=self.model,
                provider="anthropic",
                generation_time=generation_time,
                success=False,
                error=str(e),
            )

    def _extract_code_block(self, content: str) -> str:
        """Extract code from markdown code blocks."""
        if "```" in content:
            # Find the first code block
            lines = content.split("\n")
            in_code_block = False
            code_lines = []

            for line in lines:
                if line.strip().startswith("```") and not in_code_block:
                    in_code_block = True
                    continue
                elif line.strip().startswith("```") and in_code_block:
                    break
                elif in_code_block:
                    code_lines.append(line)

            if code_lines:
                return "\n".join(code_lines)

        # If no code block found, return the entire content
        return content.strip()


class GoogleProvider(BaseLLMProvider):
    """Google Gemini provider."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if not GOOGLE_AVAILABLE:
            raise ImportError(
                "Google Generative AI not available. Install with: pip install google-generativeai"
            )

        genai.configure(api_key=config.get("api_key"))
        self.model_name = config.get("model", "gemini-pro")
        self.model = genai.GenerativeModel(self.model_name)

    async def generate_code(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        language: CodeLanguage = CodeLanguage.PYTHON,
        max_tokens: int = 4000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate code using Google Gemini."""
        start_time = time.time()

        try:
            # Prepare full prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                default_system = f"""You are an expert programmer. {self._get_language_instructions(language)}
                
Generate only the code requested. Do not include explanations unless specifically asked.
Ensure the code is functional, efficient, and follows best practices."""
                full_prompt = f"{default_system}\n\n{prompt}"

            # Configure generation
            generation_config = genai.types.GenerationConfig(
                temperature=temperature, max_output_tokens=max_tokens
            )

            # Make API call
            response = await self.model.generate_content_async(
                full_prompt, generation_config=generation_config
            )

            generation_time = time.time() - start_time

            # Extract code from response
            content = response.text
            code = self._extract_code_block(content)

            return LLMResponse(
                code=code,
                model=self.model_name,
                provider="google",
                generation_time=generation_time,
                tokens_used=(
                    response.usage_metadata.total_token_count
                    if hasattr(response, "usage_metadata")
                    else None
                ),
                success=True,
                metadata={
                    "finish_reason": (
                        response.candidates[0].finish_reason.name
                        if response.candidates
                        else None
                    ),
                    "safety_ratings": (
                        [
                            rating.category.name
                            for rating in response.candidates[0].safety_ratings
                        ]
                        if response.candidates
                        else None
                    ),
                },
            )

        except Exception as e:
            generation_time = time.time() - start_time
            self.logger.error(f"Google generation failed: {e}")

            return LLMResponse(
                code="",
                model=self.model_name,
                provider="google",
                generation_time=generation_time,
                success=False,
                error=str(e),
            )

    def _extract_code_block(self, content: str) -> str:
        """Extract code from markdown code blocks."""
        if "```" in content:
            # Find the first code block
            lines = content.split("\n")
            in_code_block = False
            code_lines = []

            for line in lines:
                if line.strip().startswith("```") and not in_code_block:
                    in_code_block = True
                    continue
                elif line.strip().startswith("```") and in_code_block:
                    break
                elif in_code_block:
                    code_lines.append(line)

            if code_lines:
                return "\n".join(code_lines)

        # If no code block found, return the entire content
        return content.strip()


class LLMInterface:
    """Main interface for LLM interactions."""

    def __init__(self, config: EngineConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize providers
        self.providers: Dict[LLMProvider, BaseLLMProvider] = {}
        self._init_providers()

        # Rate limiting
        self.request_counts: Dict[str, List[float]] = {}
        self.max_requests_per_minute = config.llm_rate_limit

    def _init_providers(self):
        """Initialize available LLM providers."""
        # OpenAI
        if hasattr(self.config, "openai_config") and OPENAI_AVAILABLE:
            try:
                self.providers[LLMProvider.OPENAI] = OpenAIProvider(
                    self.config.openai_config
                )
                self.logger.info("OpenAI provider initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenAI provider: {e}")

        # Anthropic
        if hasattr(self.config, "anthropic_config") and ANTHROPIC_AVAILABLE:
            try:
                self.providers[LLMProvider.ANTHROPIC] = AnthropicProvider(
                    self.config.anthropic_config
                )
                self.logger.info("Anthropic provider initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Anthropic provider: {e}")

        # Google
        if hasattr(self.config, "google_config") and GOOGLE_AVAILABLE:
            try:
                self.providers[LLMProvider.GOOGLE] = GoogleProvider(
                    self.config.google_config
                )
                self.logger.info("Google provider initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Google provider: {e}")

        if not self.providers:
            self.logger.warning("No LLM providers available!")

    async def generate_code(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        language: CodeLanguage = CodeLanguage.PYTHON,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        provider: Optional[LLMProvider] = None,
        retry_attempts: int = 3,
    ) -> Optional[Dict[str, Any]]:
        """Generate code using the specified or best available provider."""

        # Select provider
        if provider and provider in self.providers:
            selected_provider = self.providers[provider]
            provider_name = provider.value
        else:
            # Auto-select best available provider
            if not self.providers:
                self.logger.error("No LLM providers available")
                return None

            provider_enum, selected_provider = next(iter(self.providers.items()))
            provider_name = provider_enum.value

        # Rate limiting check
        if not await self._check_rate_limit(provider_name):
            self.logger.warning(f"Rate limit exceeded for {provider_name}")
            return None

        # Try generation with retries
        for attempt in range(retry_attempts):
            try:
                response = await selected_provider.generate_code(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    language=language,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

                if response.success and response.code.strip():
                    # Record successful request
                    await self._record_request(provider_name)

                    return {
                        "code": response.code,
                        "model": response.model,
                        "provider": response.provider,
                        "generation_time": response.generation_time,
                        "tokens_used": response.tokens_used,
                        "metadata": response.metadata,
                    }
                else:
                    self.logger.warning(
                        f"Generation failed on attempt {attempt + 1}: {response.error}"
                    )

                    # Add delay before retry
                    if attempt < retry_attempts - 1:
                        await asyncio.sleep(2**attempt)  # Exponential backoff

            except Exception as e:
                self.logger.error(f"Generation attempt {attempt + 1} failed: {e}")
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(2**attempt)

        return None

    async def _check_rate_limit(self, provider_name: str) -> bool:
        """Check if request is within rate limits."""
        current_time = time.time()

        if provider_name not in self.request_counts:
            self.request_counts[provider_name] = []

        # Remove old requests (older than 1 minute)
        self.request_counts[provider_name] = [
            req_time
            for req_time in self.request_counts[provider_name]
            if current_time - req_time < 60
        ]

        # Check if under limit
        return len(self.request_counts[provider_name]) < self.max_requests_per_minute

    async def _record_request(self, provider_name: str):
        """Record a successful request for rate limiting."""
        current_time = time.time()

        if provider_name not in self.request_counts:
            self.request_counts[provider_name] = []

        self.request_counts[provider_name].append(current_time)

    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return [provider.value for provider in self.providers.keys()]

    def get_provider_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all providers."""
        stats = {}
        current_time = time.time()

        for provider_name in self.request_counts:
            recent_requests = [
                req_time
                for req_time in self.request_counts[provider_name]
                if current_time - req_time < 3600  # Last hour
            ]

            stats[provider_name] = {
                "requests_last_hour": len(recent_requests),
                "requests_last_minute": len(
                    [
                        req_time
                        for req_time in recent_requests
                        if current_time - req_time < 60
                    ]
                ),
                "rate_limit": self.max_requests_per_minute,
            }

        return stats

    async def cleanup(self):
        """Cleanup provider resources."""
        for provider in self.providers.values():
            if hasattr(provider, "cleanup"):
                await provider.cleanup()

        self.providers.clear()
        self.request_counts.clear()


# For easy importing
__all__ = ["LLMInterface", "LLMProvider", "LLMResponse"]
