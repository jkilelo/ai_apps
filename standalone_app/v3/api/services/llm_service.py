"""LLM Service with OpenAI integration and fallback support"""
import os
import asyncio
from typing import Dict, Any, List, AsyncGenerator
import logging
from openai import AsyncOpenAI
import aiohttp

logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM interactions with multiple provider support"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set. LLM features will be limited.")
        
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
        self.default_model = "gpt-4"
        self.fallback_model = "gpt-3.5-turbo"
        
    async def query(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        model: str = None
    ) -> Dict[str, Any]:
        """Query LLM with fallback support"""
        model = model or self.default_model
        
        if not self.client:
            return {
                "response": "LLM service is not configured. Please set OPENAI_API_KEY.",
                "model": "error",
                "tokens_used": 0
            }
        
        try:
            # Try primary model
            response = await self._make_request(prompt, temperature, max_tokens, model)
            return response
            
        except Exception as e:
            logger.error(f"Primary model {model} failed: {e}")
            
            # Try fallback model
            if model != self.fallback_model:
                try:
                    logger.info(f"Trying fallback model: {self.fallback_model}")
                    response = await self._make_request(
                        prompt, temperature, max_tokens, self.fallback_model
                    )
                    response["model"] = f"{self.fallback_model} (fallback)"
                    return response
                except Exception as fallback_error:
                    logger.error(f"Fallback model also failed: {fallback_error}")
            
            # Return error response
            return {
                "response": f"LLM query failed: {str(e)}",
                "model": "error",
                "tokens_used": 0
            }
    
    async def _make_request(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        model: str
    ) -> Dict[str, Any]:
        """Make actual API request to OpenAI"""
        response = await self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            n=1
        )
        
        return {
            "response": response.choices[0].message.content,
            "model": response.model,
            "tokens_used": response.usage.total_tokens if response.usage else None
        }
    
    async def stream(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        model: str = None
    ) -> AsyncGenerator[str, None]:
        """Stream LLM response"""
        model = model or self.default_model
        
        if not self.client:
            yield "LLM service is not configured. Please set OPENAI_API_KEY."
            return
        
        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            yield f"\n\nError: {str(e)}"
    
    async def get_available_models(self) -> List[str]:
        """Get list of available models"""
        if not self.client:
            return ["error: API key not configured"]
        
        try:
            models = await self.client.models.list()
            # Filter for chat models
            chat_models = [
                model.id for model in models.data
                if 'gpt' in model.id.lower()
            ]
            return sorted(chat_models)
        except Exception as e:
            logger.error(f"Failed to get models: {e}")
            return [self.default_model, self.fallback_model]
    
    async def validate_api_key(self) -> bool:
        """Validate API key is working"""
        if not self.api_key:
            return False
        
        try:
            # Make a minimal request to validate
            await self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"API key validation failed: {e}")
            return False

# Global LLM service instance
llm_service = LLMService()