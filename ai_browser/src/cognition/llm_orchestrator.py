
"""LLM Orchestrator for intelligent provider selection and fallback handling"""

import asyncio
import hashlib
import json
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union

from loguru import logger
from pydantic import BaseModel, Field

from cognition.llm import LLMManager


class TaskType(str, Enum):
    """Types of tasks for routing decisions"""
    CONVERSATIONAL = "conversational"
    CODING = "coding"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    REASONING = "reasoning"
    MULTIMODAL = "multimodal"
    PLANNING = "planning"


class RoutingStrategy(str, Enum):
    """Routing strategies for provider selection"""
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    BALANCED = "balanced"
    RELIABILITY_OPTIMIZED = "reliability_optimized"


class ProviderCapability(str, Enum):
    """Capabilities that providers may support"""
    TEXT_GENERATION = "text_generation"
    STRUCTURED_OUTPUT = "structured_output"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"
    STREAMING = "streaming"
    LONG_CONTEXT = "long_context"
    FAST_INFERENCE = "fast_inference"


class RequestContext(BaseModel):
    """Context for orchestration request"""
    task_type: TaskType = Field(default=TaskType.CONVERSATIONAL)
    routing_strategy: RoutingStrategy = Field(default=RoutingStrategy.BALANCED)
    max_cost: Optional[float] = Field(None, description="Maximum cost constraint")
    max_latency_ms: Optional[float] = Field(None, description="Maximum latency constraint")
    min_quality_score: float = Field(default=0.7, description="Minimum quality score")
    retry_on_failure: bool = Field(default=True)
    max_retries: int = Field(default=2)
    cache_ttl_seconds: int = Field(default=300)
    priority: int = Field(default=5, ge=1, le=10)
    user_id: Optional[str] = Field(None)
    prefer_provider: Optional[str] = Field(None)
    avoid_providers: List[str] = Field(default_factory=list)


class ProviderSelection(BaseModel):
    """Selected provider configuration"""
    primary_provider: str
    fallback_providers: List[str] = Field(default_factory=list)
    estimated_cost: float = Field(default=0.0)
    estimated_latency_ms: float = Field(default=0.0)
    selection_reason: str = Field(default="")


class OrchestrationResult(BaseModel):
    """Result from orchestration"""
    success: bool
    response: Optional[Any] = None
    provider_used: Optional[str] = None
    fallback_used: bool = Field(default=False)
    attempts: int = Field(default=1)
    total_latency_ms: float = Field(default=0.0)
    actual_cost: float = Field(default=0.0)
    tokens_used: int = Field(default=0)
    quality_score: float = Field(default=0.0)
    error: Optional[str] = None
    provider_selection: Optional[ProviderSelection] = None


@dataclass
class ProviderMetrics:
    """Metrics for a provider"""
    provider_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    recent_latencies: List[float] = field(default_factory=list)
    last_success_time: Optional[datetime] = None
    last_error: Optional[str] = None
    health_score: float = 1.0
    quota_exhausted: bool = False
    
    def calculate_metrics(self):
        """Calculate derived metrics"""
        if self.total_requests > 0:
            self.success_rate = self.successful_requests / self.total_requests
            
            if self.recent_latencies:
                self.avg_latency_ms = sum(self.recent_latencies) / len(self.recent_latencies)
                self.p95_latency_ms = sorted(self.recent_latencies)[int(len(self.recent_latencies) * 0.95)] if len(self.recent_latencies) > 1 else self.recent_latencies[0]
            else:
                self.avg_latency_ms = 0.0
                self.p95_latency_ms = 0.0
            
            # Calculate health score (0-1)
            success_weight = 0.5
            latency_weight = 0.3
            recency_weight = 0.2
            
            # Success component
            success_score = self.success_rate
            
            # Latency component (lower is better, normalize to 0-1)
            latency_score = max(0, 1 - (self.avg_latency_ms / 10000))  # 10s as worst case
            
            # Recency component (more recent is better)
            recency_score = 1.0
            if self.last_success_time:
                hours_since_success = (datetime.now() - self.last_success_time).total_seconds() / 3600
                recency_score = max(0, 1 - (hours_since_success / 24))  # 24h as worst case
            
            self.health_score = (
                success_weight * success_score +
                latency_weight * latency_score +
                recency_weight * recency_score
            )
        else:
            self.success_rate = 0.0
            self.avg_latency_ms = 0.0
            self.p95_latency_ms = 0.0
            self.health_score = 0.5  # Neutral for untested providers


@dataclass
class CostModel:
    """Cost model for a provider"""
    provider_name: str
    input_cost_per_1k: float
    output_cost_per_1k: float
    image_cost_per_unit: float = 0.0
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, image_count: int = 0) -> float:
        """Calculate cost for a request"""
        input_cost = (input_tokens / 1000) * self.input_cost_per_1k
        output_cost = (output_tokens / 1000) * self.output_cost_per_1k
        image_cost = image_count * self.image_cost_per_unit
        return input_cost + output_cost + image_cost


class LLMOrchestrator:
    """Intelligent LLM orchestrator with provider selection and fallback"""
    
    # Cost models for different providers (USD per 1K tokens)
    COST_MODELS = {
        "openai": CostModel("openai", input_cost_per_1k=0.03, output_cost_per_1k=0.06, image_cost_per_unit=0.02),
        "anthropic": CostModel("anthropic", input_cost_per_1k=0.025, output_cost_per_1k=0.125, image_cost_per_unit=0.0),
        "gemini": CostModel("gemini", input_cost_per_1k=0.0005, output_cost_per_1k=0.0015, image_cost_per_unit=0.002),
        "groq": CostModel("groq", input_cost_per_1k=0.001, output_cost_per_1k=0.002, image_cost_per_unit=0.0),
        "together": CostModel("together", input_cost_per_1k=0.0008, output_cost_per_1k=0.0016, image_cost_per_unit=0.0),
        "local": CostModel("local", input_cost_per_1k=0.0, output_cost_per_1k=0.0, image_cost_per_unit=0.0)
    }
    
    # Provider capabilities
    PROVIDER_CAPABILITIES = {
        "openai": {"multimodal": True, "structured": True, "streaming": True, "max_tokens": 128000},
        "anthropic": {"multimodal": False, "structured": True, "streaming": True, "max_tokens": 200000},
        "gemini": {"multimodal": True, "structured": True, "streaming": True, "max_tokens": 1000000},
        "groq": {"multimodal": False, "structured": True, "streaming": True, "max_tokens": 32000},
        "together": {"multimodal": False, "structured": True, "streaming": True, "max_tokens": 32000},
        "local": {"multimodal": False, "structured": False, "streaming": False, "max_tokens": 8192}
    }
    
    def __init__(self, llm_manager: LLMManager, config: Optional[Dict[str, Any]] = None):
        """Initialize orchestrator"""
        self.llm_manager = llm_manager
        self.config = config or {}
        
        # Provider metrics
        self.provider_metrics = {}
        for provider in llm_manager.list_providers():
            self.provider_metrics[provider] = ProviderMetrics(provider_name=provider)
        
        # Rate limiting
        self.rate_limiters = defaultdict(deque)
        
        # Circuit breakers
        self.circuit_breakers = {}
        
        # Response cache
        self.response_cache = {}
        self.cache_stats = {"hits": 0, "misses": 0, "evictions": 0}
        
        # Start background tasks
        self._background_tasks = []
        asyncio.create_task(self._metrics_calculator())
        asyncio.create_task(self._cache_cleanup())
        asyncio.create_task(self._health_checker())
        
        logger.info(f"LLM Orchestrator initialized with {len(self.provider_metrics)} providers")
    
    async def orchestrate(
        self,
        prompt: str,
        context: Optional[RequestContext] = None,
        output_model: Optional[Type[BaseModel]] = None,
        images: Optional[List[Union[str, bytes]]] = None,
        **kwargs
    ) -> OrchestrationResult:
        """Main orchestration method with intelligent routing"""
        context = context or RequestContext()
        
        # Check cache first
        if context.cache_ttl_seconds > 0:
            cached_response = self._check_cache(prompt, context, output_model)
            if cached_response:
                logger.debug(f"Cache hit for request (user: {context.user_id})")
                return OrchestrationResult(
                    success=True,
                    response=cached_response,
                    provider_used="cache",
                    total_latency_ms=0.0,
                    actual_cost=0.0,
                    tokens_used=0
                )
        
        # Select providers based on context
        selection = self._select_providers(context, images is not None)
        
        # Execute with fallback
        result = await self._execute_with_fallback(
            prompt=prompt,
            context=context,
            selection=selection,
            output_model=output_model,
            images=images,
            **kwargs
        )
        
        # Cache successful responses
        if result.success and context.cache_ttl_seconds > 0:
            self._cache_response(prompt, context, output_model, result.response)
        
        return result
    
    def _select_providers(self, context: RequestContext, needs_multimodal: bool) -> ProviderSelection:
        """Select primary and fallback providers based on context"""
        available_providers = []
        
        for provider_name in self.llm_manager.list_providers():
            # Skip if explicitly avoided
            if provider_name in context.avoid_providers:
                continue
            
            # Check if provider supports multimodal if needed
            if needs_multimodal:
                capabilities = self.PROVIDER_CAPABILITIES.get(provider_name, {})
                if not capabilities.get("multimodal", False):
                    continue
            
            # Check if provider is healthy
            if not self._is_provider_healthy(provider_name):
                logger.debug(f"Skipping unhealthy provider: {provider_name}")
                continue
            
            available_providers.append(provider_name)
        
        if not available_providers:
            # Fallback to any available provider
            available_providers = self.llm_manager.list_providers()
        
        # Sort providers based on routing strategy
        sorted_providers = self._sort_providers_by_strategy(
            available_providers,
            context.routing_strategy,
            context
        )
        
        # Use preferred provider if specified and available
        if context.prefer_provider and context.prefer_provider in sorted_providers:
            sorted_providers.remove(context.prefer_provider)
            sorted_providers.insert(0, context.prefer_provider)
        
        # Select primary and fallbacks
        primary = sorted_providers[0] if sorted_providers else "openai"
        fallbacks = sorted_providers[1:3] if len(sorted_providers) > 1 else []
        
        # Estimate costs and latency
        estimated_cost = 0.0
        estimated_latency = 0.0
        
        if primary in self.COST_MODELS:
            # Rough estimate based on average request
            estimated_cost = self.COST_MODELS[primary].calculate_cost(500, 500)
        
        if primary in self.provider_metrics:
            metrics = self.provider_metrics[primary]
            if hasattr(metrics, 'avg_latency_ms'):
                estimated_latency = metrics.avg_latency_ms
        
        return ProviderSelection(
            primary_provider=primary,
            fallback_providers=fallbacks,
            estimated_cost=estimated_cost,
            estimated_latency_ms=estimated_latency,
            selection_reason=f"Selected based on {context.routing_strategy.value} strategy"
        )
    
    def _sort_providers_by_strategy(
        self,
        providers: List[str],
        strategy: RoutingStrategy,
        context: RequestContext
    ) -> List[str]:
        """Sort providers based on routing strategy"""
        if strategy == RoutingStrategy.COST_OPTIMIZED:
            # Sort by cost (ascending)
            return sorted(providers, key=lambda p: self.COST_MODELS.get(p, CostModel(p, 999, 999)).input_cost_per_1k)
        
        elif strategy == RoutingStrategy.PERFORMANCE_OPTIMIZED:
            # Sort by latency (ascending)
            def get_latency(p):
                metrics = self.provider_metrics.get(p)
                if metrics and hasattr(metrics, 'avg_latency_ms'):
                    return metrics.avg_latency_ms
                return 999999
            return sorted(providers, key=get_latency)
        
        elif strategy == RoutingStrategy.RELIABILITY_OPTIMIZED:
            # Sort by health score (descending)
            return sorted(providers, key=lambda p: self.provider_metrics.get(p, ProviderMetrics(p)).health_score, reverse=True)
        
        else:  # BALANCED
            # Sort by composite score
            def get_balanced_score(p):
                metrics = self.provider_metrics.get(p, ProviderMetrics(p))
                cost_model = self.COST_MODELS.get(p, CostModel(p, 1, 1))
                
                # Normalize factors (0-1, lower is better)
                cost_factor = min(1.0, cost_model.input_cost_per_1k / 0.1)  # Normalize to 0.1 max
                latency_factor = min(1.0, getattr(metrics, 'avg_latency_ms', 5000) / 10000)  # Normalize to 10s max
                reliability_factor = 1.0 - metrics.health_score
                
                # Weighted average (lower is better)
                return (cost_factor * 0.3 + latency_factor * 0.3 + reliability_factor * 0.4)
            
            return sorted(providers, key=get_balanced_score)

    async def _execute_with_fallback(
        self,
        prompt: str,
        context: RequestContext,
        selection: ProviderSelection,
        output_model: Optional[Type[BaseModel]] = None,
        images: Optional[List[Union[str, bytes]]] = None,
        **kwargs
    ) -> OrchestrationResult:
        """Execute request with fallback logic"""
        providers_to_try = [selection.primary_provider] + selection.fallback_providers
        attempts = 0
        last_error = None
        fallback_used = False
        
        for provider_name in providers_to_try:
            if attempts >= context.max_retries + 1:
                break
                
            attempts += 1
            
            # Check rate limits and circuit breaker
            if not self._can_use_provider(provider_name, context):
                logger.warning(f"Provider {provider_name} unavailable (rate limit or circuit breaker)")
                fallback_used = True
                continue
            
            try:
                start_time = time.time()
                
                # Execute the request
                provider = self.llm_manager.get_provider(provider_name)
                
                if images and hasattr(provider, 'generate_with_images'):
                    response = await provider.generate_with_images(
                        prompt=prompt,
                        images=images,
                        **kwargs
                    )
                elif output_model:
                    response = await provider.generate_structured(
                        prompt=prompt,
                        output_model=output_model,
                        **kwargs
                    )
                else:
                    response = await provider.generate(
                        prompt=prompt,
                        **kwargs
                    )
                
                latency_ms = (time.time() - start_time) * 1000
                
                # Estimate cost and tokens
                tokens_used = provider.estimate_tokens(prompt)
                if hasattr(response, '__str__'):
                    tokens_used += provider.estimate_tokens(str(response))
                
                actual_cost = 0.0
                if provider_name in self.COST_MODELS:
                    cost_model = self.COST_MODELS[provider_name]
                    input_tokens = provider.estimate_tokens(prompt)
                    output_tokens = provider.estimate_tokens(str(response)) if hasattr(response, '__str__') else 100
                    image_count = len(images) if images else 0
                    actual_cost = cost_model.calculate_cost(input_tokens, output_tokens, image_count)
                
                # Update metrics
                self._update_provider_metrics(
                    provider_name=provider_name,
                    success=True,
                    latency_ms=latency_ms,
                    tokens_used=tokens_used,
                    cost=actual_cost
                )
                
                # Quality assessment (basic implementation)
                quality_score = self._assess_response_quality(response, context)
                
                return OrchestrationResult(
                    success=True,
                    response=response,
                    provider_used=provider_name,
                    fallback_used=fallback_used,
                    attempts=attempts,
                    total_latency_ms=latency_ms,
                    actual_cost=actual_cost,
                    tokens_used=tokens_used,
                    provider_selection=selection,
                    quality_score=quality_score
                )
                
            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                last_error = str(e)
                
                logger.warning(f"Provider {provider_name} failed (attempt {attempts}): {e}")
                
                # Update metrics for failure
                self._update_provider_metrics(
                    provider_name=provider_name,
                    success=False,
                    latency_ms=latency_ms,
                    error=str(e)
                )
                
                # Update circuit breaker
                self._update_circuit_breaker(provider_name, success=False)
                
                # Check if we should retry with same provider
                if attempts <= context.max_retries and provider_name == selection.primary_provider:
                    if context.retry_on_failure and self._should_retry_error(e):
                        await asyncio.sleep(min(2 ** (attempts - 1), 10))  # Exponential backoff
                        continue
                
                fallback_used = True
                continue
        
        # All providers failed
        return OrchestrationResult(
            success=False,
            fallback_used=fallback_used,
            attempts=attempts,
            total_latency_ms=0.0,
            actual_cost=0.0,
            tokens_used=0,
            error=last_error or "All providers failed",
            provider_selection=selection
        )
    
    def _can_use_provider(self, provider_name: str, context: RequestContext) -> bool:
        """Check if provider can be used (rate limits, circuit breaker)"""
        # Check circuit breaker
        if self._is_circuit_breaker_open(provider_name):
            return False
        
        # Check rate limits
        if not self._check_rate_limit(provider_name, context):
            return False
        
        # Check quota
        if self.provider_metrics[provider_name].quota_exhausted:
            return False
        
        return True
    
    def _check_rate_limit(self, provider_name: str, context: RequestContext) -> bool:
        """Check if provider is within rate limits"""
        now = time.time()
        window_start = now - 60  # 1-minute window
        
        # Clean old requests
        rate_limiter = self.rate_limiters[provider_name]
        while rate_limiter and rate_limiter[0] < window_start:
            rate_limiter.popleft()
        
        # Check limits from config
        config_limits = self.config.get('cognition', {}).get('providers', {})
        provider_config = config_limits.get(provider_name, {})
        rate_limit = provider_config.get('rate_limit', {}).get('requests_per_minute', 60)
        
        if len(rate_limiter) >= rate_limit:
            logger.warning(f"Rate limit exceeded for {provider_name}: {len(rate_limiter)}/{rate_limit} requests")
            return False
        
        # Add current request to rate limiter
        rate_limiter.append(now)
        return True
    
    def _is_circuit_breaker_open(self, provider_name: str) -> bool:
        """Check if circuit breaker is open for provider"""
        breaker = self.circuit_breakers.get(provider_name)
        if not breaker:
            return False
        
        if breaker['state'] == 'closed':
            return False
        elif breaker['state'] == 'open':
            # Check if enough time has passed to try half-open
            if time.time() - breaker['last_failure'] > breaker['timeout']:
                breaker['state'] = 'half-open'
                return False
            return True
        else:  # half-open
            return False
    
    def _update_circuit_breaker(self, provider_name: str, success: bool):
        """Update circuit breaker state"""
        if provider_name not in self.circuit_breakers:
            self.circuit_breakers[provider_name] = {
                'state': 'closed',
                'failure_count': 0,
                'last_failure': 0,
                'timeout': 60  # 1 minute timeout
            }
        
        breaker = self.circuit_breakers[provider_name]
        
        if success:
            if breaker['state'] == 'half-open':
                breaker['state'] = 'closed'
                breaker['failure_count'] = 0
                logger.info(f"Circuit breaker closed for {provider_name}")
            elif breaker['state'] == 'closed':
                breaker['failure_count'] = 0
        else:
            breaker['failure_count'] += 1
            breaker['last_failure'] = time.time()
            
            # Open circuit breaker after 5 consecutive failures
            if breaker['failure_count'] >= 5 and breaker['state'] == 'closed':
                breaker['state'] = 'open'
                logger.warning(f"Circuit breaker opened for {provider_name} after {breaker['failure_count']} failures")
    
    def _should_retry_error(self, error: Exception) -> bool:
        """Determine if error is retryable"""
        error_str = str(error).lower()
        
        # Retryable errors
        retryable_patterns = [
            'timeout',
            'connection',
            'network',
            'temporary',
            '429',  # Rate limit
            '502',  # Bad gateway
            '503',  # Service unavailable
            '504'   # Gateway timeout
        ]
        
        for pattern in retryable_patterns:
            if pattern in error_str:
                return True
        
        return False
    
    def _update_provider_metrics(
        self,
        provider_name: str,
        success: bool,
        latency_ms: float,
        tokens_used: int = 0,
        cost: float = 0.0,
        error: Optional[str] = None
    ):
        """Update comprehensive provider metrics"""
        metrics = self.provider_metrics[provider_name]
        
        metrics.total_requests += 1
        
        if success:
            metrics.successful_requests += 1
            metrics.last_success_time = datetime.now()
        else:
            metrics.failed_requests += 1
            metrics.last_error = error
        
        metrics.total_tokens += tokens_used
        metrics.total_cost += cost
        
        # Update latency tracking
        metrics.recent_latencies.append(latency_ms)
        if len(metrics.recent_latencies) > 100:  # Keep last 100 latencies
            metrics.recent_latencies.pop(0)
        
        # Recalculate derived metrics
        metrics.calculate_metrics()
    
    def _assess_response_quality(self, response: Any, context: RequestContext) -> float:
        """Basic response quality assessment"""
        try:
            # Basic quality checks
            quality_score = 0.8  # Base score
            
            if response is None or (isinstance(response, str) and not response.strip()):
                return 0.0
            
            response_str = str(response)
            
            # Length check (too short might be incomplete)
            if len(response_str) < 10:
                quality_score -= 0.3
            
            # Check for obvious errors
            error_indicators = ['error', 'failed', 'unable', 'cannot', 'sorry']
            if any(indicator in response_str.lower() for indicator in error_indicators):
                quality_score -= 0.2
            
            # For structured output, check if it matches expected format
            if isinstance(response, BaseModel):
                quality_score += 0.1  # Bonus for structured response
            
            # Check for task-specific quality indicators
            if context.task_type == TaskType.CODING:
                if 'def ' in response_str or 'function' in response_str or 'class ' in response_str:
                    quality_score += 0.1
            elif context.task_type == TaskType.ANALYTICAL:
                if 'analysis' in response_str.lower() or 'conclusion' in response_str.lower():
                    quality_score += 0.1
            
            return max(0.0, min(1.0, quality_score))
            
        except Exception:
            return 0.5  # Neutral score if assessment fails
    
    def _check_cache(self, prompt: str, context: RequestContext, output_model: Optional[Type[BaseModel]]) -> Any:
        """Check response cache"""
        cache_key = self._generate_cache_key(prompt, context, output_model)
        
        if cache_key in self.response_cache:
            cached_response, cached_time = self.response_cache[cache_key]
            
            # Check if cache is still valid
            if datetime.now() - cached_time < timedelta(seconds=context.cache_ttl_seconds):
                self.cache_stats["hits"] += 1
                return cached_response
            else:
                # Expired cache entry
                del self.response_cache[cache_key]
                self.cache_stats["evictions"] += 1
        
        self.cache_stats["misses"] += 1
        return None
    
    def _cache_response(
        self,
        prompt: str,
        context: RequestContext,
        output_model: Optional[Type[BaseModel]],
        response: Any
    ):
        """Cache response"""
        cache_key = self._generate_cache_key(prompt, context, output_model)
        self.response_cache[cache_key] = (response, datetime.now())
        
        # Limit cache size
        if len(self.response_cache) > 1000:
            # Remove oldest entries
            oldest_key = min(self.response_cache.keys(), key=lambda k: self.response_cache[k][1])
            del self.response_cache[oldest_key]
            self.cache_stats["evictions"] += 1
    
    def _generate_cache_key(
        self,
        prompt: str,
        context: RequestContext,
        output_model: Optional[Type[BaseModel]]
    ) -> str:
        """Generate cache key for request"""
        cache_data = {
            "prompt": prompt,
            "task_type": context.task_type.value,
            "output_model": output_model.__name__ if output_model else None,
            "user_id": context.user_id
        }
        
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()[:16]
    
    def _is_provider_healthy(self, provider_name: str) -> bool:
        """Check if provider is healthy"""
        metrics = self.provider_metrics[provider_name]
        
        # Consider unhealthy if:
        # 1. Health score is too low
        if metrics.health_score < 0.3:
            return False
        
        # 2. Circuit breaker is open
        if self._is_circuit_breaker_open(provider_name):
            return False
        
        # 3. Quota is exhausted
        if metrics.quota_exhausted:
            return False
        
        return True
    
    async def _metrics_calculator(self):
        """Background task to calculate metrics"""
        while True:
            try:
                for provider_name, metrics in self.provider_metrics.items():
                    metrics.calculate_metrics()
                
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                logger.error(f"Metrics calculation failed: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _cache_cleanup(self):
        """Background task to clean up cache"""
        while True:
            try:
                now = datetime.now()
                expired_keys = []
                
                for cache_key, (response, cached_time) in self.response_cache.items():
                    if now - cached_time > timedelta(hours=1):  # Max cache age
                        expired_keys.append(cache_key)
                
                for key in expired_keys:
                    del self.response_cache[key]
                    self.cache_stats["evictions"] += 1
                
                await asyncio.sleep(300)  # Cleanup every 5 minutes
            except Exception as e:
                logger.error(f"Cache cleanup failed: {e}")
                await asyncio.sleep(600)  # Wait longer on error
    
    async def _health_checker(self):
        """Background task to perform health checks"""
        while True:
            try:
                for provider_name in self.llm_manager.list_providers():
                    # Perform lightweight health check
                    try:
                        provider = self.llm_manager.get_provider(provider_name)
                        
                        # Simple health check - try to estimate tokens
                        test_tokens = provider.estimate_tokens("test")
                        
                        if test_tokens > 0:
                            # Provider is responsive
                            self._update_circuit_breaker(provider_name, success=True)
                        
                    except Exception as e:
                        logger.debug(f"Health check failed for {provider_name}: {e}")
                        # Don't update circuit breaker for health check failures
                
                await asyncio.sleep(120)  # Health check every 2 minutes
            except Exception as e:
                logger.error(f"Health checker failed: {e}")
                await asyncio.sleep(300)  # Wait longer on error
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        summary = {
            "providers": {},
            "cache": self.cache_stats.copy(),
            "circuit_breakers": {}
        }
        
        for provider_name, metrics in self.provider_metrics.items():
            summary["providers"][provider_name] = asdict(metrics)
        
        for provider_name, breaker in self.circuit_breakers.items():
            summary["circuit_breakers"][provider_name] = breaker.copy()
        
        return summary
    
    async def reset_provider_metrics(self, provider_name: Optional[str] = None):
        """Reset metrics for a provider or all providers"""
        if provider_name:
            if provider_name in self.provider_metrics:
                self.provider_metrics[provider_name] = ProviderMetrics(provider_name=provider_name)
                logger.info(f"Reset metrics for provider: {provider_name}")
        else:
            for provider in self.provider_metrics:
                self.provider_metrics[provider] = ProviderMetrics(provider_name=provider)
            logger.info("Reset metrics for all providers")
    
    async def shutdown(self):
        """Gracefully shutdown orchestrator"""
        logger.info("Shutting down LLM orchestrator")
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        # Clear cache
        self.response_cache.clear()
        
        logger.info("LLM orchestrator shutdown complete")


# Utility functions for common orchestration patterns

def create_smart_context(
    task_description: str,
    user_preferences: Optional[Dict[str, Any]] = None,
    performance_requirements: Optional[Dict[str, Any]] = None
) -> RequestContext:
    """Create intelligent request context based on task analysis"""
    # Analyze task to determine type
    task_lower = task_description.lower()
    
    # Task type detection
    task_type = TaskType.CONVERSATIONAL  # Default
    
    if any(word in task_lower for word in ['code', 'program', 'function', 'debug', 'script']):
        task_type = TaskType.CODING
    elif any(word in task_lower for word in ['analyze', 'examine', 'study', 'evaluate']):
        task_type = TaskType.ANALYTICAL
    elif any(word in task_lower for word in ['create', 'write', 'compose', 'generate']):
        task_type = TaskType.CREATIVE
    elif any(word in task_lower for word in ['reason', 'logic', 'solve', 'problem']):
        task_type = TaskType.REASONING
    elif any(word in task_lower for word in ['image', 'picture', 'visual', 'photo']):
        task_type = TaskType.MULTIMODAL
    elif any(word in task_lower for word in ['plan', 'strategy', 'approach', 'steps']):
        task_type = TaskType.PLANNING
    
    # Determine routing strategy
    routing_strategy = RoutingStrategy.BALANCED
    if user_preferences:
        if user_preferences.get('optimize_for') == 'cost':
            routing_strategy = RoutingStrategy.COST_OPTIMIZED
        elif user_preferences.get('optimize_for') == 'speed':
            routing_strategy = RoutingStrategy.PERFORMANCE_OPTIMIZED
        elif user_preferences.get('optimize_for') == 'reliability':
            routing_strategy = RoutingStrategy.RELIABILITY_OPTIMIZED
    
    # Set constraints from performance requirements
    max_cost = None
    max_latency_ms = None
    if performance_requirements:
        max_cost = performance_requirements.get('max_cost')
        max_latency_ms = performance_requirements.get('max_latency_ms')
    
    return RequestContext(
        task_type=task_type,
        routing_strategy=routing_strategy,
        max_cost=max_cost,
        max_latency_ms=max_latency_ms,
        priority=user_preferences.get('priority', 5) if user_preferences else 5
    )


async def orchestrate_with_auto_context(
    orchestrator: LLMOrchestrator,
    prompt: str,
    task_description: Optional[str] = None,
    user_preferences: Optional[Dict[str, Any]] = None,
    **kwargs
) -> OrchestrationResult:
    """Orchestrate request with automatically generated context"""
    context = await create_smart_context(
        task_description or prompt,
        user_preferences
    )
    
    return await orchestrator.orchestrate(
        prompt=prompt,
        context=context,
        **kwargs
    )
