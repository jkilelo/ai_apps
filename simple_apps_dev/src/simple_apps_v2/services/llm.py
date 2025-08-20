"""
Modern LLM service with type safety and error handling.
"""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional, Union

from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletion
from pydantic import BaseModel, Field

from simple_apps_v2.core.config import get_settings
from simple_apps_v2.core.logging import get_logger

logger = get_logger(__name__)


class LLMMessage(BaseModel):
    """LLM message model."""
    role: str = Field(..., description="Message role (system, user, assistant)")
    content: str = Field(..., description="Message content")


class LLMResponse(BaseModel):
    """LLM response model."""
    content: str = Field(..., description="Response content")
    model: str = Field(..., description="Model used")
    provider: str = Field(..., description="Provider used")
    tokens_used: Optional[int] = Field(None, description="Tokens consumed")
    response_time: float = Field(..., description="Response time in seconds")
    success: bool = Field(default=True, description="Whether request succeeded")
    error: Optional[str] = Field(None, description="Error message if failed")


class LLMProvider:
    """Base class for LLM providers."""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
        self._client: Optional[Union[OpenAI, AsyncOpenAI]] = None
        self._async_client: Optional[AsyncOpenAI] = None
    
    def get_sync_client(self) -> OpenAI:
        """Get synchronous client."""
        if self._client is None:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client
    
    def get_async_client(self) -> AsyncOpenAI:
        """Get asynchronous client."""
        if self._async_client is None:
            self._async_client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._async_client


class OpenAIProvider(LLMProvider):
    """OpenAI provider."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.name = "openai"


class GeminiProvider(LLMProvider):
    """Google Gemini provider."""
    
    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.name = "gemini"


class ClaudeProvider(LLMProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            base_url="https://api.anthropic.com/v1/"
        )
        self.name = "claude"


class LLMService:
    """Modern LLM service with multiple provider support."""
    
    def __init__(self):
        self.settings = get_settings()
        self.providers: Dict[str, LLMProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize available providers."""
        if self.settings.openai_api_key:
            self.providers["openai"] = OpenAIProvider(self.settings.openai_api_key)
            
        if self.settings.google_api_key:
            self.providers["gemini"] = GeminiProvider(self.settings.google_api_key)
            
        if self.settings.anthropic_api_key:
            self.providers["claude"] = ClaudeProvider(self.settings.anthropic_api_key)
        
        logger.info(f"Initialized LLM providers: {list(self.providers.keys())}")
    
    def get_provider(self, provider_name: str) -> LLMProvider:
        """Get provider by name."""
        if provider_name not in self.providers:
            available = list(self.providers.keys())
            raise ValueError(f"Provider '{provider_name}' not available. Available: {available}")
        return self.providers[provider_name]
    
    async def query_async(
        self,
        messages: List[LLMMessage],
        provider: str = None,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Query LLM asynchronously."""
        provider_name = provider or self.settings.default_llm_provider
        model_name = model or self.settings.default_llm_model
        
        start_time = time.time()
        
        try:
            llm_provider = self.get_provider(provider_name)
            client = llm_provider.get_async_client()
            
            # Convert messages to dict format
            message_dicts = [{"role": msg.role, "content": msg.content} for msg in messages]
            
            logger.info(f"Querying {provider_name} with model {model_name}")
            
            # Make the API call
            response = await client.chat.completions.create(
                model=model_name,
                messages=message_dicts,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            response_time = time.time() - start_time
            
            # Extract response content
            content = response.choices[0].message.content or ""
            tokens_used = getattr(response.usage, "total_tokens", None) if response.usage else None
            
            logger.info(f"LLM response received in {response_time:.2f}s")
            
            return LLMResponse(
                content=content,
                model=model_name,
                provider=provider_name,
                tokens_used=tokens_used,
                response_time=response_time,
                success=True
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = str(e)
            logger.error(f"LLM query failed: {error_msg}")
            
            return LLMResponse(
                content="",
                model=model_name,
                provider=provider_name,
                response_time=response_time,
                success=False,
                error=error_msg
            )
    
    def query_sync(
        self,
        messages: List[LLMMessage],
        provider: str = None,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Query LLM synchronously."""
        provider_name = provider or self.settings.default_llm_provider
        model_name = model or self.settings.default_llm_model
        
        start_time = time.time()
        
        try:
            llm_provider = self.get_provider(provider_name)
            client = llm_provider.get_sync_client()
            
            # Convert messages to dict format
            message_dicts = [{"role": msg.role, "content": msg.content} for msg in messages]
            
            logger.info(f"Querying {provider_name} with model {model_name}")
            
            # Make the API call
            response = client.chat.completions.create(
                model=model_name,
                messages=message_dicts,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            response_time = time.time() - start_time
            
            # Extract response content
            content = response.choices[0].message.content or ""
            tokens_used = getattr(response.usage, "total_tokens", None) if response.usage else None
            
            logger.info(f"LLM response received in {response_time:.2f}s")
            
            return LLMResponse(
                content=content,
                model=model_name,
                provider=provider_name,
                tokens_used=tokens_used,
                response_time=response_time,
                success=True
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = str(e)
            logger.error(f"LLM query failed: {error_msg}")
            
            return LLMResponse(
                content="",
                model=model_name,
                provider=provider_name,
                response_time=response_time,
                success=False,
                error=error_msg
            )
    
    async def analyze_elements(
        self,
        elements: List[Dict[str, Any]],
        url: str,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Analyze extracted elements using LLM."""
        
        # Prepare elements summary for LLM
        elements_summary = []
        for elem in elements[:50]:  # Limit for prompt size
            elements_summary.append({
                "selector": elem.get("selector", ""),
                "tag": elem.get("tag_name", ""),
                "text": elem.get("text", "")[:100],  # Limit text length
                "type": elem.get("element_type", ""),
                "visible": elem.get("visible", True),
                "clickable": elem.get("clickable", False)
            })
        
        prompt = f"""
Analyze the following web elements extracted from {url}.

Elements ({len(elements_summary)} total):
{json.dumps(elements_summary, indent=2)}

Please provide a comprehensive analysis including:
1. Element categorization and prioritization
2. Potential test scenarios for critical elements  
3. Interaction patterns and user workflows
4. Accessibility and usability considerations
5. Recommendations for test automation

Return your analysis as a JSON object with the following structure:
{{
  "summary": "Brief overview",
  "categories": {{"category": count}},
  "critical_elements": ["selector1", "selector2"],
  "test_scenarios": ["scenario1", "scenario2"],
  "recommendations": ["rec1", "rec2"],
  "complexity_score": 0.0-1.0
}}
"""
        
        messages = [
            LLMMessage(role="system", content="You are an expert in web UI testing and automation."),
            LLMMessage(role="user", content=prompt)
        ]
        
        response = await self.query_async(messages)
        
        if response.success:
            try:
                # Try to parse JSON from response
                analysis = json.loads(response.content)
                return analysis
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM analysis as JSON")
                return {
                    "summary": response.content[:500],
                    "raw_analysis": response.content,
                    "parsed": False
                }
        else:
            return {
                "error": response.error,
                "success": False
            }


# Backward compatibility functions
async def query_llm_async(
    provider: str,
    model: str, 
    messages: List[Dict[str, str]]
) -> ChatCompletion:
    """Backward compatibility function for async LLM queries."""
    llm_service = LLMService()
    
    # Convert to new format
    llm_messages = [LLMMessage(**msg) for msg in messages]
    
    response = await llm_service.query_async(
        messages=llm_messages,
        provider=provider,
        model=model
    )
    
    # Mock ChatCompletion for compatibility
    class MockChoice:
        def __init__(self, content: str):
            self.message = MockMessage(content)
    
    class MockMessage:
        def __init__(self, content: str):
            self.content = content
    
    class MockCompletion:
        def __init__(self, content: str):
            self.choices = [MockChoice(content)]
    
    return MockCompletion(response.content)


def query_llm(
    provider: str,
    model: str,
    messages: List[Dict[str, str]]
) -> ChatCompletion:
    """Backward compatibility function for sync LLM queries."""
    llm_service = LLMService()
    
    # Convert to new format
    llm_messages = [LLMMessage(**msg) for msg in messages]
    
    response = llm_service.query_sync(
        messages=llm_messages,
        provider=provider,
        model=model
    )
    
    # Mock ChatCompletion for compatibility
    class MockChoice:
        def __init__(self, content: str):
            self.message = MockMessage(content)
    
    class MockMessage:
        def __init__(self, content: str):
            self.content = content
    
    class MockCompletion:
        def __init__(self, content: str):
            self.choices = [MockChoice(content)]
    
    return MockCompletion(response.content)