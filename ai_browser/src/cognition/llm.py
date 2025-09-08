"""LLM provider interface and manager"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Type, Dict, List, Union
from pydantic import BaseModel
from loguru import logger
import json


class ILLMProvider(ABC):
    """Abstract interface for LLM providers"""
    
    @abstractmethod
    async def generate(self, prompt: str, temperature: float = 0.7, 
                      max_tokens: int = 2000, **kwargs) -> str:
        """Generate free-form text response"""
        pass
    
    async def generate_text(self, prompt: str, temperature: float = 0.7, 
                           max_tokens: int = 2000, **kwargs) -> str:
        """Alias for generate method for ReAct compatibility"""
        return await self.generate(prompt, temperature, max_tokens, **kwargs)
    
    @abstractmethod
    async def generate_structured(self, prompt: str, output_model: Type[BaseModel],
                                 temperature: float = 0.7, max_tokens: int = 2000,
                                 **kwargs) -> BaseModel:
        """Generate structured response conforming to Pydantic model"""
        pass
    
    @abstractmethod
    async def generate_with_images(self, prompt: str, images: List[Union[str, bytes]],
                                  temperature: float = 0.7, max_tokens: int = 2000,
                                  **kwargs) -> str:
        """Generate response with image inputs"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get provider name"""
        pass
    
    @abstractmethod
    def get_model(self) -> str:
        """Get model identifier"""
        pass
    
    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        pass
    
    @abstractmethod
    def get_max_context_window(self) -> int:
        """Get maximum context window size"""
        pass


class LLMManager:
    """Manages multiple LLM providers and routing"""
    
    def __init__(self, default_provider: Optional[str] = None, auto_load: bool = True):
        self.providers: Dict[str, ILLMProvider] = {}
        self.default_provider = default_provider
        self._usage_stats = {}
        
        # Auto-load available providers
        if auto_load:
            self._load_providers()
    
    def _load_providers(self) -> None:
        """Auto-load available providers based on API keys"""
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        # Priority order: XAI (grok-code-fast-1), then Gemini (gemini-2.5-flash-lite)
        providers_loaded = []
        
        # Try to load XAI provider first (highest priority)
        if os.getenv("XAI_API_KEY"):
            try:
                from .providers.xai_provider import XAIProvider
                self.register_provider("xai", XAIProvider(model="grok-code-fast-1"))
                logger.info("Loaded XAI provider with grok-code-fast-1")
                providers_loaded.append("xai")
            except Exception as e:
                logger.warning(f"Failed to load XAI provider: {e}")
        
        # Try to load Gemini provider second (second priority)
        if os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"):
            try:
                from .providers.gemini_provider import GeminiProvider
                self.register_provider("gemini", GeminiProvider(model="gemini-2.5-flash-lite"))
                logger.info("Loaded Gemini provider with gemini-2.5-flash-lite")
                providers_loaded.append("gemini")
            except Exception as e:
                logger.warning(f"Failed to load Gemini provider: {e}")
        
        # Set default provider based on priority
        if "xai" in providers_loaded:
            self.default_provider = "xai"
            logger.info("Default provider set to XAI (grok-code-fast-1)")
        elif "gemini" in providers_loaded:
            self.default_provider = "gemini"
            logger.info("Default provider set to Gemini (gemini-2.5-flash-lite)")
        
        # DO NOT load other providers (OpenAI, Anthropic) as per requirements
    
    def register_provider(self, name: str, provider: ILLMProvider) -> None:
        """Register an LLM provider"""
        self.providers[name] = provider
        self._usage_stats[name] = {
            'requests': 0,
            'tokens': 0,
            'errors': 0
        }
        logger.info(f"Registered LLM provider: {name} ({provider.get_model()})")
        
        # Set as default if it's the first provider
        if not self.default_provider:
            self.default_provider = name
    
    def get_provider(self, name: Optional[str] = None) -> ILLMProvider:
        """Get a specific provider or the default"""
        if name:
            if name not in self.providers:
                raise ValueError(f"Provider {name} not registered")
            return self.providers[name]
        
        if not self.default_provider:
            raise ValueError("No default provider set")
        
        return self.providers[self.default_provider]
    
    async def generate(self, prompt: str, provider: Optional[str] = None,
                      temperature: float = 0.7, max_tokens: int = 2000,
                      **kwargs) -> str:
        """Generate text using specified or default provider"""
        llm = self.get_provider(provider)
        provider_name = provider or self.default_provider
        
        try:
            self._usage_stats[provider_name]['requests'] += 1
            result = await llm.generate(prompt, temperature, max_tokens, **kwargs)
            self._usage_stats[provider_name]['tokens'] += llm.estimate_tokens(prompt) + llm.estimate_tokens(result)
            return result
        except Exception as e:
            self._usage_stats[provider_name]['errors'] += 1
            logger.error(f"LLM generation failed ({provider_name}): {e}")
            raise
    
    async def generate_structured(self, prompt: str, output_model: Type[BaseModel],
                                 provider: Optional[str] = None,
                                 temperature: float = 0.7, max_tokens: int = 2000,
                                 **kwargs) -> BaseModel:
        """Generate structured output using specified or default provider"""
        llm = self.get_provider(provider)
        provider_name = provider or self.default_provider
        
        try:
            self._usage_stats[provider_name]['requests'] += 1
            result = await llm.generate_structured(
                prompt, output_model, temperature, max_tokens, **kwargs
            )
            self._usage_stats[provider_name]['tokens'] += llm.estimate_tokens(prompt)
            return result
        except Exception as e:
            self._usage_stats[provider_name]['errors'] += 1
            logger.error(f"Structured generation failed ({provider_name}): {e}")
            raise
    
    async def generate_with_images(self, prompt: str, images: List[Union[str, bytes]],
                                  provider: Optional[str] = None,
                                  temperature: float = 0.7, max_tokens: int = 2000,
                                  **kwargs) -> str:
        """Generate response with image inputs"""
        llm = self.get_provider(provider)
        provider_name = provider or self.default_provider
        
        try:
            self._usage_stats[provider_name]['requests'] += 1
            result = await llm.generate_with_images(
                prompt, images, temperature, max_tokens, **kwargs
            )
            self._usage_stats[provider_name]['tokens'] += llm.estimate_tokens(prompt) + llm.estimate_tokens(result)
            return result
        except Exception as e:
            self._usage_stats[provider_name]['errors'] += 1
            logger.error(f"Image generation failed ({provider_name}): {e}")
            raise
    
    def get_usage_stats(self) -> Dict[str, Dict]:
        """Get usage statistics for all providers"""
        return self._usage_stats
    
    def list_providers(self) -> List[str]:
        """List all registered providers"""
        return list(self.providers.keys())
    
    def set_default_provider(self, name: str) -> None:
        """Set default provider"""
        if name not in self.providers:
            raise ValueError(f"Provider {name} not registered")
        self.default_provider = name
        logger.info(f"Default LLM provider set to: {name}")
    
    async def fallback_generate(self, prompt: str, output_model: Optional[Type[BaseModel]] = None,
                               temperature: float = 0.7, max_tokens: int = 2000,
                               **kwargs) -> Union[str, BaseModel]:
        """
        Try generation with fallback to other providers if primary fails
        """
        # Priority order: xai first, then gemini
        priority_order = ["xai", "gemini"]
        providers_to_try = [p for p in priority_order if p in self.providers]
        
        last_error = None
        for provider_name in providers_to_try:
            try:
                if output_model:
                    return await self.generate_structured(
                        prompt, output_model, provider_name, 
                        temperature, max_tokens, **kwargs
                    )
                else:
                    return await self.generate(
                        prompt, provider_name, temperature, max_tokens, **kwargs
                    )
            except Exception as e:
                last_error = e
                logger.warning(f"Provider {provider_name} failed, trying next: {e}")
                continue
        
        raise Exception(f"All providers failed. Last error: {last_error}")
    
    def check_prompt_fit(self, prompt: str, provider: Optional[str] = None) -> bool:
        """Check if prompt fits within provider's context window"""
        llm = self.get_provider(provider)
        tokens = llm.estimate_tokens(prompt)
        max_tokens = llm.get_max_context_window()
        
        if tokens > max_tokens * 0.9:  # Leave 10% buffer
            logger.warning(f"Prompt uses {tokens}/{max_tokens} tokens (>90% of context window)")
            return False
        return True
    
    def truncate_to_fit(self, prompt: str, provider: Optional[str] = None,
                       reserve_tokens: int = 500) -> str:
        """Truncate prompt to fit within context window"""
        llm = self.get_provider(provider)
        max_tokens = llm.get_max_context_window() - reserve_tokens
        
        # Rough estimation: 1 token ≈ 4 characters
        max_chars = max_tokens * 4
        
        if len(prompt) > max_chars:
            logger.warning(f"Truncating prompt from {len(prompt)} to {max_chars} characters")
            return prompt[:max_chars]
        
        return prompt