#!/usr/bin/env python3
"""
LLM MODULE V2 - AI-FIRST SYSTEM WITH MANDATORY LIVE LLM CONNECTION
NO MOCK SUPPORT - REQUIRES LIVE LLM CONNECTION TO FUNCTION
Part of PHASE2 implementation following QUANTUM_ENHANCED_PROMPT specifications
"""

import os
import json
import time
import hashlib
from typing import List, Dict, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import asyncio
import sys

# Import local modules
sys.path.append(str(Path(__file__).parent))
from utils import Logger, ErrorHandler, AsyncUtils, FileUtils, PerformanceTimer
from shared import BaseComponent, ComponentStatus, AsyncioConfig
# TODO: Review unused imports: AsyncUtils, ErrorHandler, anthropic, Callable, ChatCompletion, ComponentStatus, FileUtils

# Load default models configuration
DEFAULT_MODELS_PATH = Path(__file__).parent / "default_llm_models.json"
if DEFAULT_MODELS_PATH.exists():
    with open(DEFAULT_MODELS_PATH, 'r') as f:
        DEFAULT_MODELS = json.load(f)
else:
    raise RuntimeError(f"Default LLM models configuration not found at {DEFAULT_MODELS_PATH}")

# Try to load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False

# Third-party imports - REQUIRED for AI-first system
try:
    from openai import OpenAI, AsyncOpenAI
    from openai.types.chat import ChatCompletion
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("[ERROR] OpenAI not installed. Install with: pip install openai")

try:
    import anthropic
    from anthropic import Anthropic, AsyncAnthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    print("[ERROR] Anthropic not installed. Install with: pip install anthropic")

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
    print("[ERROR] Google Generative AI not installed. Install with: pip install google-generativeai")


# ============================================================================
# CONFIGURATION AND DATA MODELS
# ============================================================================

class LLMProvider(Enum):
    """Supported LLM providers - NO MOCK SUPPORT"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"


@dataclass
class LLMConfig:
    """Configuration for LLM module - AI-FIRST"""
    # Provider settings
    default_provider: LLMProvider = LLMProvider.OPENAI
    fallback_providers: List[LLMProvider] = field(default_factory=lambda: [LLMProvider.GEMINI, LLMProvider.ANTHROPIC])
    
    # Model settings from default_llm_models.json
    openai_model: str = DEFAULT_MODELS["openai"]["model"]
    anthropic_model: str = DEFAULT_MODELS["anthropic"]["model"]
    gemini_model: str = DEFAULT_MODELS["gemini"]["model"]
    
    # API keys (will try to load from environment)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0
    
    # Timeout settings
    timeout: int = 60  # seconds
    
    # Cache settings
    enable_cache: bool = True
    cache_ttl: int = 3600  # seconds
    max_cache_size: int = 100
    
    # Default token and temperature from config
    max_tokens: int = DEFAULT_MODELS["openai"]["max_tokens"]
    temperature: float = DEFAULT_MODELS["openai"]["temperature"]
    
    # Logging
    log_requests: bool = True
    log_responses: bool = True
    
    # AI-FIRST: Require live connection
    require_live_connection: bool = True
    verification_prompt: str = "What's the capital of Kenya? Reply with one word only"
    expected_verification_response: str = "Nairobi"
    
    def __post_init__(self):
        """Load API keys from environment if not provided"""
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.anthropic_api_key:
            self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.gemini_api_key:
            self.gemini_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")


@dataclass
class LLMMessage:
    """Standard message format for all providers"""
    role: str  # "system", "user", "assistant"
    content: str
    
    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass
class LLMResponse:
    """Standard response format for all providers"""
    provider: LLMProvider
    model: str
    content: str
    usage: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    cached: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    duration: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider.value,
            "model": self.model,
            "content": self.content,
            "usage": self.usage,
            "metadata": self.metadata,
            "cached": self.cached,
            "timestamp": self.timestamp.isoformat(),
            "duration": self.duration
        }


# ============================================================================
# CACHE SYSTEM
# ============================================================================

class LLMCache:
    """Simple cache for LLM responses"""
    
    def __init__(self, ttl: int = 3600, max_size: int = 100) -> None:
        self.ttl = ttl
        self.max_size = max_size
        self._cache: Dict[str, tuple[LLMResponse, datetime]] = {}
        self.logger = Logger.get_logger("LLMCache")
    
    def _get_key(self, provider: LLMProvider, model: str, messages: List[LLMMessage]) -> str:
        """Generate cache key from request parameters"""
        content = f"{provider.value}:{model}:"
        content += ":".join([f"{m.role}:{m.content}" for m in messages])
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, provider: LLMProvider, model: str, messages: List[LLMMessage]) -> Optional[LLMResponse]:
        """Get cached response if available and not expired"""
        key = self._get_key(provider, model, messages)
        
        if key in self._cache:
            response, timestamp = self._cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                self.logger.debug(f"Cache hit for key: {key}")
                response.cached = True
                return response
            else:
                del self._cache[key]
                self.logger.debug(f"Cache expired for key: {key}")
        
        return None
    
    def set(self, provider: LLMProvider, model: str, messages: List[LLMMessage], response: LLMResponse):
        """Cache a response"""
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]
        
        key = self._get_key(provider, model, messages)
        self._cache[key] = (response, datetime.now())
        self.logger.debug(f"Cached response for key: {key}")
    
    def clear(self):
        """Clear all cached responses"""
        self._cache.clear()
        self.logger.info("Cache cleared")


# ============================================================================
# PROVIDER IMPLEMENTATIONS
# ============================================================================

class OpenAIProvider:
    """OpenAI GPT provider implementation"""
    
    def __init__(self, api_key: str, model: str = None) -> None:
        if not HAS_OPENAI:
            raise RuntimeError("OpenAI library not installed")
        if not api_key:
            raise ValueError("OpenAI API key is required for AI-first system")
        
        self.client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)
        self.model = model or DEFAULT_MODELS["openai"]["model"]
        self.max_tokens = DEFAULT_MODELS["openai"]["max_tokens"]
        self.temperature = DEFAULT_MODELS["openai"]["temperature"]
        self.logger = Logger.get_logger("OpenAIProvider")
    
    def query(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Synchronous query to OpenAI"""
        try:
            with PerformanceTimer("OpenAI Query") as timer:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[m.to_dict() for m in messages],
                )
            
            return LLMResponse(
                provider=LLMProvider.OPENAI,
                model=self.model,
                content=response.choices[0].message.content,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                duration=timer.get_duration()
            )
            
        except Exception as e:
            self.logger.error(f"OpenAI query failed: {e}")
            raise


class AnthropicProvider:
    """Anthropic Claude provider implementation"""
    
    def __init__(self, api_key: str, model: str = None) -> None:
        if not HAS_ANTHROPIC:
            raise RuntimeError("Anthropic library not installed")
        if not api_key:
            raise ValueError("Anthropic API key is required for AI-first system")
        
        # Set higher timeout to avoid streaming requirement for long requests
        self.client = Anthropic(api_key=api_key, timeout=120.0)  # 2 minutes timeout
        self.async_client = AsyncAnthropic(api_key=api_key, timeout=120.0)
        self.model = model or DEFAULT_MODELS["anthropic"]["model"]
        self.max_tokens = DEFAULT_MODELS["anthropic"]["max_tokens"]
        self.temperature = DEFAULT_MODELS["anthropic"]["temperature"]
        self.logger = Logger.get_logger("AnthropicProvider")
    
    def query(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Synchronous query to Anthropic"""
        try:
            with PerformanceTimer("Anthropic Query") as timer:
                system_message = None
                user_messages = []
                
                for msg in messages:
                    if msg.role == "system":
                        system_message = msg.content
                    else:
                        user_messages.append({"role": msg.role, "content": msg.content})
                
                # Use smaller max_tokens for Anthropic to avoid timeout
                max_tokens = kwargs.get("max_tokens", min(4096, self.max_tokens))
                
                response = self.client.messages.create(
                    model=self.model,
                    system=system_message if system_message else "You are a helpful assistant.",
                    messages=user_messages,
                    max_tokens=max_tokens,
                    temperature=kwargs.get("temperature", self.temperature)
                )
            
            return LLMResponse(
                provider=LLMProvider.ANTHROPIC,
                model=self.model,
                content=response.content[0].text if response.content else "",
                usage={
                    "prompt_tokens": response.usage.input_tokens if hasattr(response, 'usage') else 0,
                    "completion_tokens": response.usage.output_tokens if hasattr(response, 'usage') else 0,
                    "total_tokens": (response.usage.input_tokens + response.usage.output_tokens) if hasattr(response, 'usage') else 0
                },
                duration=timer.get_duration()
            )
            
        except Exception as e:
            self.logger.error(f"Anthropic query failed: {e}")
            raise


class GeminiProvider:
    """Google Gemini provider implementation"""
    
    def __init__(self, api_key: str, model: str = None) -> None:
        if not HAS_GEMINI:
            raise RuntimeError("Google Generative AI library not installed")
        if not api_key:
            raise ValueError("Gemini API key is required for AI-first system")
        
        genai.configure(api_key=api_key)
        self.model_name = model or DEFAULT_MODELS["gemini"]["model"]
        self.model = genai.GenerativeModel(self.model_name)
        self.max_tokens = DEFAULT_MODELS["gemini"]["max_tokens"]
        self.temperature = DEFAULT_MODELS["gemini"]["temperature"]
        self.logger = Logger.get_logger("GeminiProvider")
    
    def query(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Synchronous query to Gemini"""
        try:
            with PerformanceTimer("Gemini Query") as timer:
                prompt = "\n".join([f"{msg.role}: {msg.content}" for msg in messages])
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=kwargs.get("max_tokens", self.max_tokens),
                        temperature=kwargs.get("temperature", self.temperature)
                    )
                )
            
            return LLMResponse(
                provider=LLMProvider.GEMINI,
                model=self.model_name,
                content=response.text if response.text else "",
                usage={
                    "prompt_tokens": 0,  # Gemini doesn't provide token counts
                    "completion_tokens": 0,
                    "total_tokens": 0
                },
                duration=timer.get_duration()
            )
            
        except Exception as e:
            self.logger.error(f"Gemini query failed: {e}")
            raise


# ============================================================================
# MAIN LLM CLASS - AI-FIRST WITH MANDATORY LIVE CONNECTION
# ============================================================================

class LLM(BaseComponent):
    """AI-FIRST LLM with mandatory live connection - NO MOCK SUPPORT"""
    
    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        """Initialize LLM module"""
        super().__init__("LLM")
        self.config = config or LLMConfig()
        self._providers: Dict[LLMProvider, Any] = {}
        self._cache = LLMCache(self.config.cache_ttl, self.config.max_cache_size) if self.config.enable_cache else None
        self._total_tokens_used = 0
        self._request_count = 0
        self._verified_providers: List[LLMProvider] = []
    
    async def initialize(self):
        """Initialize and verify LLM providers"""
        await super().initialize()
        
        # Initialize providers based on available API keys
        providers_initialized = []
        
        if self.config.openai_api_key and HAS_OPENAI:
            try:
                self._providers[LLMProvider.OPENAI] = OpenAIProvider(
                    self.config.openai_api_key,
                    self.config.openai_model
                )
                providers_initialized.append(LLMProvider.OPENAI)
                self.logger.info(f"OpenAI provider initialized with model: {self.config.openai_model}")
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenAI: {e}")
        
        if self.config.anthropic_api_key and HAS_ANTHROPIC:
            try:
                self._providers[LLMProvider.ANTHROPIC] = AnthropicProvider(
                    self.config.anthropic_api_key,
                    self.config.anthropic_model
                )
                providers_initialized.append(LLMProvider.ANTHROPIC)
                self.logger.info(f"Anthropic provider initialized with model: {self.config.anthropic_model}")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Anthropic: {e}")
        
        if self.config.gemini_api_key and HAS_GEMINI:
            try:
                self._providers[LLMProvider.GEMINI] = GeminiProvider(
                    self.config.gemini_api_key,
                    self.config.gemini_model
                )
                providers_initialized.append(LLMProvider.GEMINI)
                self.logger.info(f"Gemini provider initialized with model: {self.config.gemini_model}")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Gemini: {e}")
        
        # AI-FIRST: Verify at least one live LLM connection
        if not providers_initialized:
            raise RuntimeError(
                "AI-FIRST SYSTEM ERROR: No LLM providers available!\n"
                "This is an AI-first system that requires live LLM connection.\n"
                "Please set at least one of these environment variables:\n"
                "  - OPENAI_API_KEY for OpenAI GPT\n"
                "  - ANTHROPIC_API_KEY for Claude\n"
                "  - GOOGLE_API_KEY for Gemini"
            )
        
        # Verify live connections with test prompt
        self.logger.info("Verifying live LLM connections...")
        verification_message = [LLMMessage("user", self.config.verification_prompt)]
        
        for provider in providers_initialized:
            try:
                self.logger.info(f"Testing {provider.value} connection...")
                response = self._providers[provider].query(verification_message)
                
                # Check if response is reasonable (contains "Nairobi" or similar)
                if response and response.content:
                    response_lower = response.content.strip().lower()
                    if "nairobi" in response_lower:
                        self._verified_providers.append(provider)
                        self.logger.info(f"[OK] {provider.value} verified: {response.content.strip()}")
                    else:
                        self.logger.warning(f"[WARNING] {provider.value} gave unexpected response: {response.content.strip()}")
                
            except Exception as e:
                self.logger.error(f"[FAIL] {provider.value} verification failed: {e}")
        
        if not self._verified_providers:
            raise RuntimeError(
                "AI-FIRST SYSTEM ERROR: No LLM providers passed verification!\n"
                "Could not verify live connection with any provider.\n"
                "Please check your API keys and internet connection."
            )
        
        self.logger.info(f"[OK] Verified providers: {[p.value for p in self._verified_providers]}")
        
        # Set default provider to first verified one
        if self.config.default_provider not in self._verified_providers:
            self.config.default_provider = self._verified_providers[0]
            self.logger.info(f"Default provider set to: {self.config.default_provider.value}")
    
    def query(self, messages: Union[List[LLMMessage], List[Dict[str, str]]], 
              provider: Optional[LLMProvider] = None, **kwargs) -> LLMResponse:
        """Query LLM with automatic retry and fallback - LIVE ONLY"""
        
        # Ensure we have verified providers
        if not self._verified_providers:
            raise RuntimeError("No verified LLM providers available. System cannot proceed without live LLM.")
        
        # Convert dict messages to LLMMessage objects
        if messages and isinstance(messages[0], dict):
            messages = [LLMMessage(**msg) for msg in messages]
        
        # Use specified provider or default (must be verified)
        provider = provider or self.config.default_provider
        if provider not in self._verified_providers:
            self.logger.warning(f"{provider.value} not verified, using {self._verified_providers[0].value}")
            provider = self._verified_providers[0]
        
        # Check cache first
        if self._cache and self.config.enable_cache:
            cached_response = self._cache.get(
                provider,
                self._get_model_for_provider(provider),
                messages
            )
            if cached_response:
                self.logger.info(f"Returning cached response from {provider.value}")
                self._request_count += 1
                return cached_response
        
        # Try primary provider with retry
        response = self._query_with_retry(provider, messages, **kwargs)
        
        # If failed, try other verified providers
        if not response:
            for fallback_provider in self._verified_providers:
                if fallback_provider != provider:
                    self.logger.info(f"Trying fallback provider: {fallback_provider.value}")
                    response = self._query_with_retry(fallback_provider, messages, **kwargs)
                    if response:
                        break
        
        # If all providers failed, system cannot proceed
        if not response:
            raise RuntimeError(
                "AI-FIRST SYSTEM CRITICAL ERROR: All LLM providers failed!\n"
                "This system requires live LLM connection to function.\n"
                "Please check your internet connection and API keys."
            )
        
        # Cache successful response
        if response and self._cache and self.config.enable_cache and not response.cached:
            self._cache.set(
                response.provider,
                response.model,
                messages,
                response
            )
        
        # Update statistics
        if response:
            self._request_count += 1
            self._total_tokens_used += response.usage.get("total_tokens", 0)
        
        return response
    
    def _query_with_retry(self, provider: LLMProvider, messages: List[LLMMessage], **kwargs) -> Optional[LLMResponse]:
        """Query provider with retry logic"""
        if provider not in self._providers:
            self.logger.warning(f"Provider {provider.value} not available")
            return None
        
        last_error = None
        delay = self.config.retry_delay
        
        for attempt in range(self.config.max_retries):
            try:
                if self.config.log_requests:
                    self.logger.info(f"Querying {provider.value} (attempt {attempt + 1}/{self.config.max_retries})")
                
                response = self._providers[provider].query(messages, **kwargs)
                
                if self.config.log_responses:
                    self.logger.info(f"Response from {provider.value}: {len(response.content)} chars")
                
                return response
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"Query failed (attempt {attempt + 1}): {e}")
                
                if attempt < self.config.max_retries - 1:
                    time.sleep(delay)
                    delay *= self.config.retry_backoff
        
        self.logger.error(f"All retry attempts failed for {provider.value}: {last_error}")
        return None
    
    def _get_model_for_provider(self, provider: LLMProvider) -> str:
        """Get the configured model for a provider"""
        if provider == LLMProvider.OPENAI:
            return self.config.openai_model
        elif provider == LLMProvider.ANTHROPIC:
            return self.config.anthropic_model
        elif provider == LLMProvider.GEMINI:
            return self.config.gemini_model
        else:
            return "unknown"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "request_count": self._request_count,
            "total_tokens_used": self._total_tokens_used,
            "providers_available": list(self._providers.keys()),
            "verified_providers": [p.value for p in self._verified_providers],
            "cache_enabled": self.config.enable_cache,
            "cache_size": len(self._cache._cache) if self._cache else 0
        }
    
    def clear_cache(self):
        """Clear response cache"""
        if self._cache:
            self._cache.clear()
            self.logger.info("Cache cleared")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_message(role: str, content: str) -> LLMMessage:
    """Create an LLM message"""
    return LLMMessage(role=role, content=content)


def create_messages(system: str = None, user: str = None, assistant: str = None) -> List[LLMMessage]:
    """Create a list of messages"""
    messages = []
    if system:
        messages.append(LLMMessage("system", system))
    if user:
        messages.append(LLMMessage("user", user))
    if assistant:
        messages.append(LLMMessage("assistant", assistant))
    return messages


# ============================================================================
# SELF-TEST AND VERIFICATION
# ============================================================================

async def verify_live_connection():
    """Verify live LLM connection - REQUIRED for AI-first system"""
    logger = Logger.get_logger("LLMVerification")
    logger.info("[VERIFICATION] Starting live LLM connection verification...")
    
    try:
        # Initialize LLM with live connection requirement
        config = LLMConfig(require_live_connection=True)
        llm = LLM(config)
        await llm.initialize()
        
        # Test with verification prompt
        test_messages = [LLMMessage("user", config.verification_prompt)]
        response = llm.query(test_messages)
        
        logger.info(f"[VERIFICATION] Response: {response.content}")
        logger.info(f"[VERIFICATION] Provider: {response.provider.value}")
        logger.info(f"[VERIFICATION] Model: {response.model}")
        
        # Verify response contains expected answer
        if "nairobi" in response.content.lower():
            logger.info("[VERIFICATION] [OK] Live LLM connection verified successfully!")
            return True
        else:
            logger.error(f"[VERIFICATION] [FAIL] Unexpected response: {response.content}")
            return False
            
    except Exception as e:
        logger.error(f"[VERIFICATION] [FAIL] Failed to verify live connection: {e}")
        return False


if __name__ == "__main__":
    # Quick test mode for compliance checking
    import os
    if os.environ.get("STANDALONE_TEST") == "1":
        print(f"[OK] {__name__} module loads successfully")
        sys.exit(0)
    
    print("=" * 60)
    print("UI TESTING AUTOMATION FRAMEWORK - LLM MODULE V2")
    print("AI-FIRST SYSTEM WITH MANDATORY LIVE CONNECTION")
    print("=" * 60)
    
    # Run verification
    success = AsyncioConfig.run_async(verify_live_connection())
    
    if success:
        print("\n" + "=" * 60)
        print("[SUCCESS] Live LLM connection verified!")
        print("AI-first system ready for operation.")
        
        # Show configuration
        print("\nDefault Models Configuration:")
        for provider, config in DEFAULT_MODELS.items():
            print(f"  {provider}:")
            print(f"    Model: {config['model']}")
            print(f"    Max Tokens: {config['max_tokens']}")
            print(f"    Temperature: {config['temperature']}")
    else:
        print("\n" + "=" * 60)
        print("[CRITICAL ERROR] Live LLM connection could not be verified!")
        print("This AI-first system cannot proceed without live LLM.")
        print("\nPlease ensure you have set at least one of:")
        print("  - OPENAI_API_KEY")
        print("  - ANTHROPIC_API_KEY") 
        print("  - GOOGLE_API_KEY")
        sys.exit(1)
    
    print("=" * 60)