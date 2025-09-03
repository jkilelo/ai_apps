#!/usr/bin/env python3
"""
Native LLM Provider Abstraction - Lean DRY Implementation
Uses native SDKs for XAI, OpenAI, Anthropic, and Google directly
"""

import asyncio
import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, AsyncGenerator
from enum import Enum
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Native SDK imports
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from xai_sdk import AsyncClient as XAIAsyncClient
    from xai_sdk.chat import user, system
    XAI_AVAILABLE = True
except ImportError:
    XAI_AVAILABLE = False

try:
    from google import genai
    from google.genai import types
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

logger = logging.getLogger(__name__)

class ProviderType(Enum):
    XAI = "xai"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"

@dataclass
class LLMRequest:
    """Unified request structure for all providers"""
    prompt: str
    system_prompt: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    stream: bool = False

@dataclass
class LLMResponse:
    """Unified response structure for all providers"""
    content: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    metadata: Dict[str, Any] = None

class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers using DRY principles"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.client = None
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the provider client"""
        pass
    
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate completion using native SDK"""
        pass
    
    @abstractmethod
    async def stream_generate(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Stream completion using native SDK"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider name"""
        pass

class XAIProvider(BaseLLMProvider):
    """XAI Grok provider using native xAI SDK"""
    
    async def initialize(self) -> bool:
        if not XAI_AVAILABLE:
            logger.error("XAI SDK not available. Install with: pip install xai-sdk")
            return False
        
        try:
            self.client = XAIAsyncClient(api_key=self.api_key)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize XAI client: {e}")
            return False
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        if not self.client:
            raise RuntimeError("XAI client not initialized")
        
        try:
            chat = self.client.chat.create(
                model=self.model,
                temperature=request.temperature
            )
            
            if request.system_prompt:
                chat.append(system(request.system_prompt))
            
            chat.append(user(request.prompt))
            response = await chat.sample()
            
            # Debug the actual response structure
            logger.debug(f"XAI response type: {type(response)}")
            logger.debug(f"XAI response attributes: {dir(response)}")
            logger.debug(f"XAI response: {response}")
            
            # Handle different response structures
            content = ""
            tokens_used = None
            response_id = None
            
            if hasattr(response, 'content'):
                content = response.content
            elif hasattr(response, 'text'):
                content = response.text
            else:
                content = str(response)
            
            # Try to get usage info safely
            if hasattr(response, 'usage') and response.usage:
                if hasattr(response.usage, 'total_tokens'):
                    tokens_used = response.usage.total_tokens
                elif isinstance(response.usage, dict):
                    tokens_used = response.usage.get('total_tokens')
            
            # Try to get response ID safely
            if hasattr(response, 'id'):
                response_id = response.id
            elif hasattr(response, 'request_id'):
                response_id = response.request_id
            
            return LLMResponse(
                content=content,
                provider="xai",
                model=self.model,
                tokens_used=tokens_used,
                metadata={'response_id': response_id, 'raw_response_type': str(type(response))}
            )
        except Exception as e:
            logger.error(f"XAI generation failed: {e}")
            raise
    
    async def stream_generate(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        if not self.client:
            raise RuntimeError("XAI client not initialized")
        
        try:
            chat = self.client.chat.create(
                model=self.model,
                temperature=request.temperature
            )
            
            if request.system_prompt:
                chat.append(system(request.system_prompt))
                
            chat.append(user(request.prompt))
            
            async for chunk in chat.stream():
                if hasattr(chunk, 'content') and chunk.content:
                    yield chunk.content
                    
        except Exception as e:
            logger.error(f"XAI streaming failed: {e}")
            raise
    
    def get_provider_name(self) -> str:
        return "XAI/Grok"

class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider using native OpenAI SDK"""
    
    async def initialize(self) -> bool:
        if not OPENAI_AVAILABLE:
            logger.error("OpenAI SDK not available. Install with: pip install openai")
            return False
        
        try:
            self.client = AsyncOpenAI(api_key=self.api_key)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            return False
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
        
        try:
            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            messages.append({"role": "user", "content": request.prompt})
            
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=request.temperature,
                stream=request.stream
            )
            
            return LLMResponse(
                content=completion.choices[0].message.content,
                provider="openai",
                model=self.model,
                tokens_used=completion.usage.total_tokens if completion.usage else None,
                metadata={'finish_reason': completion.choices[0].finish_reason}
            )
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise
    
    async def stream_generate(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
        
        try:
            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            messages.append({"role": "user", "content": request.prompt})
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=request.temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            raise
    
    def get_provider_name(self) -> str:
        return "OpenAI"

class AnthropicProvider(BaseLLMProvider):
    """Anthropic provider using native Anthropic SDK"""
    
    async def initialize(self) -> bool:
        if not ANTHROPIC_AVAILABLE:
            logger.error("Anthropic SDK not available. Install with: pip install anthropic")
            return False
        
        try:
            self.client = AsyncAnthropic(api_key=self.api_key)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            return False
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        if not self.client:
            raise RuntimeError("Anthropic client not initialized")
        
        try:
            messages = [{"role": "user", "content": request.prompt}]
            
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": request.temperature,
                "max_tokens": 4096  # Anthropic requires max_tokens
            }
            
            if request.system_prompt:
                kwargs["system"] = request.system_prompt
            
            message = await self.client.messages.create(**kwargs)
            
            return LLMResponse(
                content=message.content[0].text if message.content else "",
                provider="anthropic",
                model=self.model,
                tokens_used=message.usage.input_tokens + message.usage.output_tokens if message.usage else None,
                metadata={'stop_reason': message.stop_reason}
            )
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise
    
    async def stream_generate(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        if not self.client:
            raise RuntimeError("Anthropic client not initialized")
        
        try:
            messages = [{"role": "user", "content": request.prompt}]
            
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": request.temperature,
                "stream": True,
                "max_tokens": 4096  # Anthropic requires max_tokens
            }
            
            if request.system_prompt:
                kwargs["system"] = request.system_prompt
            
            async with self.client.messages.stream(**kwargs) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            logger.error(f"Anthropic streaming failed: {e}")
            raise
    
    def get_provider_name(self) -> str:
        return "Anthropic"

class GoogleProvider(BaseLLMProvider):
    """Google Gemini provider using native Google Gen AI SDK"""
    
    async def initialize(self) -> bool:
        if not GOOGLE_AVAILABLE:
            logger.error("Google Gen AI SDK not available. Install with: pip install google-genai")
            return False
        
        try:
            self.client = genai.Client(api_key=self.api_key)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Google client: {e}")
            return False
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        if not self.client:
            raise RuntimeError("Google client not initialized")
        
        try:
            config = types.GenerateContentConfig(
                temperature=request.temperature,
            )
            
            if request.system_prompt:
                config.system_instruction = request.system_prompt
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=request.prompt,
                config=config
            )
            
            return LLMResponse(
                content=response.text if hasattr(response, 'text') else str(response),
                provider="google",
                model=self.model,
                metadata={'response': str(response)}
            )
        except Exception as e:
            logger.error(f"Google generation failed: {e}")
            raise
    
    async def stream_generate(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        # Note: Google Gen AI SDK streaming would need to be implemented based on latest API
        # For now, fallback to regular generation
        response = await self.generate(request)
        yield response.content
    
    def get_provider_name(self) -> str:
        return "Google/Gemini"

class LLMProviderManager:
    """Manager class for all LLM providers with automatic provider selection and connection pooling"""
    
    def __init__(self, llm_db_path: str = None):
        self.providers: Dict[ProviderType, BaseLLMProvider] = {}
        self.llm_db_path = llm_db_path or "llm_models_database.json"
        self.model_database = self._load_model_database()
        
        # Connection pooling for high-throughput scenarios
        self.connection_pools: Dict[ProviderType, asyncio.Semaphore] = {}
        self.max_concurrent_requests = 10  # Default limit per provider
        self.request_stats = {
            'total_requests': 0,
            'concurrent_requests': 0,
            'provider_usage': {},
            'response_times': []
        }
        
        # Intelligent provider selection
        self.provider_performance = {}  # Track performance per provider
        self.selection_strategy = "cheapest"  # Default: cheapest, fastest, balanced, reliable
        
    def _load_model_database(self) -> Dict[str, Any]:
        """Load the LLM models database"""
        if not os.path.exists(self.llm_db_path):
            logger.debug(f"Model database not found at {self.llm_db_path}, using empty database")
            return {}
        try:
            with open(self.llm_db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load model database: {e}")
            return {}
    
    async def add_provider(self, provider_type: ProviderType, api_key: str, model: str) -> bool:
        """Add and initialize a provider"""
        try:
            if provider_type == ProviderType.XAI:
                provider = XAIProvider(api_key, model)
            elif provider_type == ProviderType.OPENAI:
                provider = OpenAIProvider(api_key, model)
            elif provider_type == ProviderType.ANTHROPIC:
                provider = AnthropicProvider(api_key, model)
            elif provider_type == ProviderType.GOOGLE:
                provider = GoogleProvider(api_key, model)
            else:
                logger.error(f"Unknown provider type: {provider_type}")
                return False
            
            success = await provider.initialize()
            if success:
                self.providers[provider_type] = provider
                
                # Initialize connection pool for this provider
                self.connection_pools[provider_type] = asyncio.Semaphore(self.max_concurrent_requests)
                self.request_stats['provider_usage'][provider_type.value] = 0
                
                logger.info(f"[OK] {provider.get_provider_name()} initialized with model {model}")
                return True
            else:
                logger.error(f"❌ Failed to initialize {provider_type.value}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding provider {provider_type.value}: {e}")
            return False
    
    async def generate(self, provider_type: ProviderType, request: LLMRequest) -> LLMResponse:
        """Generate using specified provider with connection pooling"""
        if provider_type not in self.providers:
            raise ValueError(f"Provider {provider_type.value} not initialized")
        
        # Use connection pool to limit concurrent requests
        async with self.connection_pools[provider_type]:
            self.request_stats['total_requests'] += 1
            self.request_stats['concurrent_requests'] += 1
            self.request_stats['provider_usage'][provider_type.value] += 1
            
            import time
            start_time = time.time()
            
            try:
                response = await self.providers[provider_type].generate(request)
                
                # Track response time and performance
                response_time = time.time() - start_time
                self.request_stats['response_times'].append(response_time)
                self._update_provider_performance(provider_type, response_time, True)
                
                return response
            except Exception as e:
                # Track failure
                response_time = time.time() - start_time
                self._update_provider_performance(provider_type, response_time, False)
                raise
            finally:
                self.request_stats['concurrent_requests'] -= 1
    
    async def stream_generate(self, provider_type: ProviderType, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Stream generate using specified provider"""
        if provider_type not in self.providers:
            raise ValueError(f"Provider {provider_type.value} not initialized")
        
        async for chunk in self.providers[provider_type].stream_generate(request):
            yield chunk
    
    def set_max_concurrent_requests(self, max_requests: int):
        """Configure maximum concurrent requests per provider"""
        self.max_concurrent_requests = max_requests
        
        # Update existing semaphores
        for provider_type in self.connection_pools:
            self.connection_pools[provider_type] = asyncio.Semaphore(max_requests)
        
        logger.info(f"📊 Updated connection pool size to {max_requests} per provider")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection pool and performance statistics"""
        import statistics
        
        stats = self.request_stats.copy()
        
        # Calculate additional metrics
        if stats['response_times']:
            stats['avg_response_time'] = statistics.mean(stats['response_times'])
            stats['median_response_time'] = statistics.median(stats['response_times'])
            stats['min_response_time'] = min(stats['response_times'])
            stats['max_response_time'] = max(stats['response_times'])
        
        # Add pool information
        stats['max_concurrent_per_provider'] = self.max_concurrent_requests
        stats['active_providers'] = list(self.providers.keys())
        stats['pool_sizes'] = {
            provider.value: semaphore._value 
            for provider, semaphore in self.connection_pools.items()
        }
        
        return stats
    
    def reset_stats(self):
        """Reset performance statistics"""
        self.request_stats = {
            'total_requests': 0,
            'concurrent_requests': 0,
            'provider_usage': {p.value: 0 for p in self.providers.keys()},
            'response_times': []
        }
        logger.info("📊 Connection pool statistics reset")
    
    def set_selection_strategy(self, strategy: str):
        """Set intelligent provider selection strategy"""
        valid_strategies = ["cheapest", "fastest", "balanced", "reliable"]
        if strategy not in valid_strategies:
            raise ValueError(f"Strategy must be one of: {valid_strategies}")
        
        self.selection_strategy = strategy
        logger.info(f"🎯 Provider selection strategy set to: {strategy}")
    
    def _update_provider_performance(self, provider_type: ProviderType, response_time: float, success: bool):
        """Update performance tracking for a provider"""
        if provider_type not in self.provider_performance:
            self.provider_performance[provider_type] = {
                'response_times': [],
                'success_count': 0,
                'failure_count': 0,
                'avg_response_time': 0,
                'reliability_score': 1.0
            }
        
        perf = self.provider_performance[provider_type]
        perf['response_times'].append(response_time)
        
        if success:
            perf['success_count'] += 1
        else:
            perf['failure_count'] += 1
        
        # Calculate rolling averages (keep last 50 requests)
        if len(perf['response_times']) > 50:
            perf['response_times'] = perf['response_times'][-50:]
        
        perf['avg_response_time'] = sum(perf['response_times']) / len(perf['response_times'])
        total_requests = perf['success_count'] + perf['failure_count']
        perf['reliability_score'] = perf['success_count'] / total_requests if total_requests > 0 else 1.0
    
    def _get_provider_cost_score(self, provider_type: ProviderType) -> float:
        """Get cost score for provider (lower = cheaper)"""
        # Cost per input token from cheap reasoning models config
        cost_mapping = {
            ProviderType.GOOGLE: 7.5e-08,    # Cheapest
            ProviderType.OPENAI: 1.0e-07,    # Second cheapest
            ProviderType.XAI: 1.5e-07,       # Third cheapest
            ProviderType.ANTHROPIC: 8.0e-07, # Most expensive
        }
        return cost_mapping.get(provider_type, 1e-06)
    
    def select_best_provider(self, task_hint: str = None) -> ProviderType:
        """Intelligently select the best provider based on strategy"""
        if not self.providers:
            raise RuntimeError("No providers available")
        
        available_providers = list(self.providers.keys())
        
        if len(available_providers) == 1:
            return available_providers[0]
        
        if self.selection_strategy == "cheapest":
            # Select cheapest provider
            return min(available_providers, key=self._get_provider_cost_score)
        
        elif self.selection_strategy == "fastest":
            # Select fastest provider based on performance history
            fastest_provider = None
            fastest_time = float('inf')
            
            for provider in available_providers:
                if provider in self.provider_performance:
                    avg_time = self.provider_performance[provider]['avg_response_time']
                    if avg_time < fastest_time:
                        fastest_time = avg_time
                        fastest_provider = provider
            
            return fastest_provider or available_providers[0]
        
        elif self.selection_strategy == "reliable":
            # Select most reliable provider
            most_reliable = None
            best_reliability = 0
            
            for provider in available_providers:
                if provider in self.provider_performance:
                    reliability = self.provider_performance[provider]['reliability_score']
                    if reliability > best_reliability:
                        best_reliability = reliability
                        most_reliable = provider
            
            return most_reliable or available_providers[0]
        
        elif self.selection_strategy == "balanced":
            # Balanced selection considering cost, speed, and reliability
            best_provider = None
            best_score = float('-inf')
            
            for provider in available_providers:
                # Cost score (inverted - lower cost is better)
                cost = self._get_provider_cost_score(provider)
                cost_score = 1.0 / (cost * 1000000)  # Normalize
                
                # Speed score (inverted - lower time is better)
                speed_score = 1.0
                if provider in self.provider_performance:
                    avg_time = self.provider_performance[provider]['avg_response_time']
                    speed_score = 1.0 / max(avg_time, 0.1)  # Avoid division by zero
                
                # Reliability score
                reliability_score = 1.0
                if provider in self.provider_performance:
                    reliability_score = self.provider_performance[provider]['reliability_score']
                
                # Combined score (weighted average)
                combined_score = (cost_score * 0.4 + speed_score * 0.3 + reliability_score * 0.3)
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_provider = provider
            
            return best_provider or available_providers[0]
        
        # Default fallback
        return available_providers[0]
    
    async def auto_generate(self, request: LLMRequest, task_hint: str = None) -> LLMResponse:
        """Generate using intelligently selected provider"""
        provider_type = self.select_best_provider(task_hint)
        logger.info(f"🎯 Selected {provider_type.value} provider using '{self.selection_strategy}' strategy")
        return await self.generate(provider_type, request)
    
    def get_available_providers(self) -> List[str]:
        """Get list of initialized providers"""
        return [provider.get_provider_name() for provider in self.providers.values()]
    
    async def test_all_providers(self, test_prompt: str = "Hello, world!") -> Dict[str, Any]:
        """Test all initialized providers"""
        results = {}
        
        for provider_type, provider in self.providers.items():
            try:
                request = LLMRequest(prompt=test_prompt)
                response = await provider.generate(request)
                results[provider_type.value] = {
                    "success": True,
                    "response": response.content[:100] + "..." if len(response.content) > 100 else response.content,
                    "tokens": response.tokens_used,
                    "provider_name": provider.get_provider_name()
                }
            except Exception as e:
                results[provider_type.value] = {
                    "success": False,
                    "error": str(e),
                    "provider_name": provider.get_provider_name()
                }
        
        return results

    @classmethod
    async def create_from_env(cls) -> 'LLMProviderManager':
        """Create manager with providers from environment variables"""
        manager = cls()
        
        # Add providers based on available API keys
        providers_to_add = [
            (ProviderType.XAI, os.getenv('XAI_API_KEY'), 'grok-code-fast-1'),
            (ProviderType.OPENAI, os.getenv('OPENAI_API_KEY'), 'gpt-4.1-nano'),
            (ProviderType.ANTHROPIC, os.getenv('ANTHROPIC_API_KEY'), 'claude-3-5-haiku-20241022'),
            (ProviderType.GOOGLE, os.getenv('GOOGLE_API_KEY'), 'gemini-2.0-flash'),
        ]
        
        for provider_type, api_key, model in providers_to_add:
            if api_key:
                await manager.add_provider(provider_type, api_key, model)
        
        return manager
    
    @classmethod
    async def create_from_config(cls, config_path: str = "./cheap_reasoning_models_config.json") -> 'LLMProviderManager':
        """Create manager with cheapest reasoning models from configuration"""
        manager = cls()
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            models_config = config['cheap_reasoning_models']['models']
            
            # Map provider names to ProviderType
            provider_map = {
                'xai': ProviderType.XAI,
                'openai': ProviderType.OPENAI, 
                'anthropic': ProviderType.ANTHROPIC,
                'google': ProviderType.GOOGLE
            }
            
            # Add providers based on configuration and available API keys
            for provider_name, model_config in models_config.items():
                if provider_name in provider_map:
                    api_key = os.getenv(f'{provider_name.upper()}_API_KEY')
                    if api_key:
                        provider_type = provider_map[provider_name]
                        model_name = model_config['sdk_model_id']
                        await manager.add_provider(provider_type, api_key, model_name)
                        logger.info(f"[OK] Added {provider_name} with {model_name} from config")
                    else:
                        logger.warning(f"⚠️ {provider_name.upper()}_API_KEY not found, skipping {provider_name}")
            
            logger.info("[OK] Manager created from cheap reasoning models configuration")
            return manager
            
        except Exception as e:
            logger.error(f"❌ Failed to load config from {config_path}: {e}")
            # Fallback to environment-based creation
            logger.info("🔄 Falling back to environment-based configuration")
            return await cls.create_from_env()


# Simple workplace-style LLM interface
_default_manager = None

async def call_default_llm(messages: List[Dict[str, str]], 
                          temperature: float = 0.2,
                          max_tokens: Optional[int] = None,
                          stream: bool = False) -> str:
    """
    Simple LLM interface that mimics workplace API usage.
    Just send messages and get a response - no provider/model selection needed.
    
    Args:
        messages: List of message dicts with 'role' and 'content' keys
        temperature: Sampling temperature (0-1)
        max_tokens: Maximum tokens in response
        stream: Whether to stream the response
        
    Returns:
        str: The LLM response content
        
    Example:
        response = await call_default_llm([
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "What's the capital of Kenya?"}
        ])
    """
    global _default_manager
    
    # Initialize manager on first use
    if _default_manager is None:
        _default_manager = LLMProviderManager()
        
        # Try to add providers in order of preference (cheapest first)
        providers_config = [
            (ProviderType.GOOGLE, os.getenv('GOOGLE_API_KEY'), os.getenv('GOOGLE_GENAI_MODEL', 'gemini-2.0-flash')),
            (ProviderType.OPENAI, os.getenv('OPENAI_API_KEY'), os.getenv('OPENAI_MODEL', 'gpt-4')),
            (ProviderType.ANTHROPIC, os.getenv('ANTHROPIC_API_KEY'), os.getenv('ANTHROPIC_MODEL', 'claude-3-haiku-20240307')),
            (ProviderType.XAI, os.getenv('XAI_API_KEY'), 'grok-beta'),
        ]
        
        for provider_type, api_key, model in providers_config:
            if api_key:
                success = await _default_manager.add_provider(provider_type, api_key, model)
                if success:
                    break  # Use first successful provider
        
        if not _default_manager.providers:
            raise RuntimeError("No LLM providers available. Please set at least one API key in .env file")
    
    # Convert messages to prompt format
    system_prompt = None
    user_prompts = []
    
    for msg in messages:
        if msg['role'] == 'system':
            system_prompt = msg['content']
        elif msg['role'] == 'user':
            user_prompts.append(msg['content'])
        elif msg['role'] == 'assistant':
            # For multi-turn conversations, append assistant responses
            user_prompts.append(f"Assistant: {msg['content']}")
    
    # Combine user prompts
    prompt = "\n".join(user_prompts)
    
    # Create request
    request = LLMRequest(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=stream
    )
    
    # Use the first available provider (or auto-select if multiple)
    if len(_default_manager.providers) == 1:
        provider_type = list(_default_manager.providers.keys())[0]
        response = await _default_manager.generate(provider_type, request)
    else:
        # Auto-select best provider
        response = await _default_manager.auto_generate(request)
    
    return response.content


def call_default_llm_sync(messages: List[Dict[str, str]], 
                         temperature: float = 0.7,
                         max_tokens: Optional[int] = None) -> str:
    """
    Synchronous version of call_default_llm for non-async code.
    
    Args:
        messages: List of message dicts with 'role' and 'content' keys
        temperature: Sampling temperature (0-1)
        max_tokens: Maximum tokens in response
        
    Returns:
        str: The LLM response content
        
    Example:
        response = call_default_llm_sync([
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "What's the capital of Kenya?"}
        ])
    """
    import asyncio
    
    # Get or create event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Run async function
    if loop.is_running():
        # If loop is already running (e.g., in Jupyter), create a task
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, call_default_llm(messages, temperature, max_tokens))
            return future.result()
    else:
        return loop.run_until_complete(call_default_llm(messages, temperature, max_tokens))