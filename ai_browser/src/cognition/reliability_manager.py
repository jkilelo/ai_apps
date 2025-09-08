"""Advanced Reliability and Failover Management for Multi-Model LLM Systems

This module implements production-ready reliability mechanisms:
- Intelligent failover with provider health tracking
- Circuit breakers with adaptive thresholds
- Load balancing and request distribution
- Retry strategies with exponential backoff
- Health monitoring and auto-recovery
- Graceful degradation patterns
"""

from typing import Dict, Any, List, Optional, Tuple, Callable, Union
from pydantic import BaseModel, Field
from loguru import logger
from enum import Enum
import asyncio
import time
import statistics
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import random
import json


class FailoverStrategy(str, Enum):
    """Failover strategies"""
    IMMEDIATE = "immediate"      # Switch immediately on first failure
    CIRCUIT_BREAKER = "circuit_breaker"  # Use circuit breaker pattern
    GRACEFUL = "graceful"        # Try to recover before switching
    LOAD_BALANCED = "load_balanced"  # Distribute across healthy providers
    ADAPTIVE = "adaptive"        # Learn optimal strategy over time


class HealthStatus(str, Enum):
    """Provider health status"""
    HEALTHY = "healthy"          # Operating normally
    DEGRADED = "degraded"        # Slower than normal but working
    UNSTABLE = "unstable"        # Intermittent failures
    UNHEALTHY = "unhealthy"      # High failure rate
    OFFLINE = "offline"          # Not responding
    RECOVERING = "recovering"    # Coming back online


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"            # Normal operation
    OPEN = "open"                # Blocking requests
    HALF_OPEN = "half_open"      # Testing recovery


@dataclass
class ProviderHealth:
    """Comprehensive provider health metrics"""
    provider_name: str
    status: HealthStatus = HealthStatus.HEALTHY
    success_rate: float = 1.0
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    error_rate: float = 0.0
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    recent_latencies: deque = field(default_factory=lambda: deque(maxlen=100))
    recent_errors: deque = field(default_factory=lambda: deque(maxlen=50))
    health_score: float = 1.0  # Composite health score (0-1)
    last_health_check: Optional[datetime] = None
    recovery_attempts: int = 0
    max_recovery_attempts: int = 5
    
    def update_metrics(self):
        """Update derived health metrics"""
        # Calculate success rate
        if self.total_requests > 0:
            self.success_rate = 1.0 - (self.failed_requests / self.total_requests)
            self.error_rate = self.failed_requests / self.total_requests
        
        # Calculate latency percentiles
        if len(self.recent_latencies) >= 10:
            sorted_latencies = sorted(self.recent_latencies)
            self.avg_latency_ms = statistics.mean(sorted_latencies)
            
            if len(sorted_latencies) >= 20:
                p95_idx = int(0.95 * len(sorted_latencies))
                p99_idx = int(0.99 * len(sorted_latencies))
                self.p95_latency_ms = sorted_latencies[p95_idx]
                self.p99_latency_ms = sorted_latencies[p99_idx]
        
        # Update health status based on metrics
        self._update_health_status()
        
        # Calculate composite health score
        self._calculate_health_score()
    
    def _update_health_status(self):
        """Update health status based on current metrics"""
        now = datetime.now()
        
        # Check if provider is offline (no successful requests in 5 minutes)
        if (self.last_success_time is None or 
            now - self.last_success_time > timedelta(minutes=5)):
            if self.total_requests > 0:  # Only if we've tried requests
                self.status = HealthStatus.OFFLINE
                return
        
        # Check consecutive failures
        if self.consecutive_failures >= 10:
            self.status = HealthStatus.UNHEALTHY
        elif self.consecutive_failures >= 5:
            self.status = HealthStatus.UNSTABLE
        elif self.success_rate < 0.8:  # Less than 80% success rate
            self.status = HealthStatus.UNSTABLE
        elif self.success_rate < 0.95:  # Less than 95% success rate
            self.status = HealthStatus.DEGRADED
        elif self.avg_latency_ms > 10000:  # More than 10 seconds average
            self.status = HealthStatus.DEGRADED
        elif self.p95_latency_ms > 30000:  # P95 over 30 seconds
            self.status = HealthStatus.DEGRADED
        else:
            # Check if recovering
            if (self.status in [HealthStatus.UNHEALTHY, HealthStatus.OFFLINE, HealthStatus.UNSTABLE] and
                self.consecutive_successes >= 3):
                self.status = HealthStatus.RECOVERING
            elif self.consecutive_successes >= 5:  # Stable recovery
                self.status = HealthStatus.HEALTHY
            elif self.status == HealthStatus.RECOVERING:
                # Stay in recovering state until proven stable
                pass
            else:
                self.status = HealthStatus.HEALTHY
    
    def _calculate_health_score(self):
        """Calculate composite health score (0.0 to 1.0)"""
        # Base score from success rate
        success_score = self.success_rate
        
        # Latency score (penalty for high latency)
        if self.avg_latency_ms > 0:
            # Normalize latency score (5 seconds = 0.5 score, 10+ seconds = 0.0)
            latency_score = max(0.0, 1.0 - (self.avg_latency_ms / 10000))
        else:
            latency_score = 1.0
        
        # Stability score (penalty for consecutive failures)
        if self.consecutive_failures > 0:
            stability_score = max(0.0, 1.0 - (self.consecutive_failures / 10))
        else:
            stability_score = 1.0
        
        # Recency score (penalty for old last success)
        if self.last_success_time:
            minutes_since_success = (datetime.now() - self.last_success_time).total_seconds() / 60
            recency_score = max(0.0, 1.0 - (minutes_since_success / 60))  # 1 hour = 0.0
        else:
            recency_score = 0.0 if self.total_requests > 0 else 1.0
        
        # Weighted combination
        self.health_score = (
            success_score * 0.35 +
            latency_score * 0.25 +
            stability_score * 0.25 +
            recency_score * 0.15
        )


@dataclass
class CircuitBreaker:
    """Circuit breaker for provider reliability"""
    provider_name: str
    failure_threshold: int = 5
    recovery_timeout_seconds: int = 60
    success_threshold: int = 3  # Successes needed to close from half-open
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_state_change: Optional[datetime] = field(default_factory=datetime.now)
    total_blocked_requests: int = 0
    
    def can_execute(self) -> bool:
        """Check if request can be executed through this circuit"""
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if (self.last_failure_time and 
                datetime.now() - self.last_failure_time >= timedelta(seconds=self.recovery_timeout_seconds)):
                self._transition_to_half_open()
                return True
            else:
                self.total_blocked_requests += 1
                return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self):
        """Record a successful request"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self._transition_to_closed()
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
    
    def record_failure(self):
        """Record a failed request"""
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.CLOSED:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self._transition_to_open()
        elif self.state == CircuitState.HALF_OPEN:
            # Immediate transition back to open on failure
            self._transition_to_open()
    
    def _transition_to_open(self):
        """Transition to OPEN state"""
        self.state = CircuitState.OPEN
        self.last_state_change = datetime.now()
        logger.warning(f"Circuit breaker OPENED for {self.provider_name} after {self.failure_count} failures")
    
    def _transition_to_half_open(self):
        """Transition to HALF_OPEN state"""
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
        self.failure_count = 0
        self.last_state_change = datetime.now()
        logger.info(f"Circuit breaker HALF_OPEN for {self.provider_name} - testing recovery")
    
    def _transition_to_closed(self):
        """Transition to CLOSED state"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_state_change = datetime.now()
        logger.info(f"Circuit breaker CLOSED for {self.provider_name} - service recovered")
    
    def force_open(self, reason: str = "Manual intervention"):
        """Manually open circuit breaker"""
        self._transition_to_open()
        logger.warning(f"Circuit breaker manually opened for {self.provider_name}: {reason}")
    
    def force_close(self, reason: str = "Manual intervention"):
        """Manually close circuit breaker"""
        self._transition_to_closed()
        logger.info(f"Circuit breaker manually closed for {self.provider_name}: {reason}")


class LoadBalancer:
    """Intelligent load balancing across providers"""
    
    def __init__(self, providers: List[str]):
        self.providers = providers
        self.request_counts = defaultdict(int)
        self.weighted_scores = defaultdict(lambda: 1.0)
        self.last_selected = defaultdict(float)  # Timestamp of last selection
    
    def select_provider(
        self,
        available_providers: List[str],
        health_data: Dict[str, ProviderHealth],
        strategy: str = "weighted_round_robin"
    ) -> Optional[str]:
        """Select optimal provider using specified strategy"""
        if not available_providers:
            return None
        
        if strategy == "round_robin":
            return self._round_robin_selection(available_providers)
        elif strategy == "weighted_round_robin":
            return self._weighted_round_robin(available_providers, health_data)
        elif strategy == "least_connections":
            return self._least_connections(available_providers)
        elif strategy == "random":
            return random.choice(available_providers)
        elif strategy == "health_weighted":
            return self._health_weighted_selection(available_providers, health_data)
        else:
            # Default to weighted round robin
            return self._weighted_round_robin(available_providers, health_data)
    
    def _round_robin_selection(self, providers: List[str]) -> str:
        """Simple round-robin selection"""
        # Find provider with lowest request count
        return min(providers, key=lambda p: self.request_counts[p])
    
    def _weighted_round_robin(self, providers: List[str], health_data: Dict[str, ProviderHealth]) -> str:
        """Weighted round-robin based on health scores"""
        # Calculate weights based on health scores
        weights = {}
        for provider in providers:
            health = health_data.get(provider)
            if health:
                # Higher health score = higher weight
                base_weight = health.health_score
                # Adjust for recent usage (spread load)
                usage_factor = 1.0 / max(1, self.request_counts[provider] / 10)
                weights[provider] = base_weight * usage_factor
            else:
                weights[provider] = 0.1  # Low weight for unknown health
        
        # Select based on weighted probabilities
        total_weight = sum(weights.values())
        if total_weight == 0:
            return providers[0]
        
        # Normalize and select
        rand = random.random() * total_weight
        cumulative = 0.0
        for provider, weight in weights.items():
            cumulative += weight
            if rand <= cumulative:
                return provider
        
        return providers[-1]  # Fallback
    
    def _least_connections(self, providers: List[str]) -> str:
        """Select provider with least active requests"""
        return min(providers, key=lambda p: self.request_counts[p])
    
    def _health_weighted_selection(self, providers: List[str], health_data: Dict[str, ProviderHealth]) -> str:
        """Select provider purely based on health scores"""
        health_scores = {}
        for provider in providers:
            health = health_data.get(provider)
            if health:
                health_scores[provider] = health.health_score
            else:
                health_scores[provider] = 0.1
        
        # Select provider with highest health score
        return max(health_scores.items(), key=lambda x: x[1])[0]
    
    def record_request(self, provider: str):
        """Record that a request was sent to provider"""
        self.request_counts[provider] += 1
        self.last_selected[provider] = time.time()
    
    def record_completion(self, provider: str):
        """Record that a request completed (for connection counting)"""
        self.request_counts[provider] = max(0, self.request_counts[provider] - 1)


class ReliabilityManager:
    """Comprehensive reliability management for multi-model LLM systems"""
    
    def __init__(
        self,
        providers: List[str],
        config: Optional[Dict[str, Any]] = None
    ):
        self.providers = providers
        self.config = config or {}
        
        # Health monitoring
        self.health_data: Dict[str, ProviderHealth] = {
            provider: ProviderHealth(provider_name=provider)
            for provider in providers
        }
        
        # Circuit breakers
        self.circuit_breakers: Dict[str, CircuitBreaker] = {
            provider: CircuitBreaker(
                provider_name=provider,
                failure_threshold=self.config.get('circuit_breaker_failure_threshold', 5),
                recovery_timeout_seconds=self.config.get('circuit_breaker_timeout', 60)
            )
            for provider in providers
        }
        
        # Load balancer
        self.load_balancer = LoadBalancer(providers)
        
        # Failover configuration
        self.failover_strategy = FailoverStrategy(
            self.config.get('failover_strategy', FailoverStrategy.CIRCUIT_BREAKER)
        )
        
        # Retry configuration
        self.max_retries = self.config.get('max_retries', 3)
        self.base_retry_delay = self.config.get('base_retry_delay', 1.0)
        self.max_retry_delay = self.config.get('max_retry_delay', 30.0)
        
        # Health check configuration
        self.health_check_interval = self.config.get('health_check_interval', 60)
        self.health_check_enabled = self.config.get('health_check_enabled', True)
        
        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        if self.health_check_enabled:
            task = asyncio.create_task(self._health_monitor())
            self._background_tasks.append(task)
        
        # Metrics calculation task
        task = asyncio.create_task(self._metrics_updater())
        self._background_tasks.append(task)
    
    def get_available_providers(
        self,
        exclude_unhealthy: bool = True,
        min_health_score: float = 0.3
    ) -> List[str]:
        """Get list of available providers based on health criteria"""
        available = []
        
        for provider in self.providers:
            health = self.health_data[provider]
            circuit = self.circuit_breakers[provider]
            
            # Check circuit breaker
            if not circuit.can_execute():
                continue
            
            # Check health criteria
            if exclude_unhealthy:
                if health.status == HealthStatus.OFFLINE:
                    continue
                if health.status == HealthStatus.UNHEALTHY:
                    continue
                if health.health_score < min_health_score:
                    continue
            
            available.append(provider)
        
        return available
    
    def select_provider(
        self,
        task_context: Optional[Dict[str, Any]] = None,
        exclude_providers: Optional[List[str]] = None
    ) -> Optional[str]:
        """Select optimal provider using current reliability strategy"""
        # Get available providers
        available = self.get_available_providers()
        
        # Remove excluded providers
        if exclude_providers:
            available = [p for p in available if p not in exclude_providers]
        
        if not available:
            logger.warning("No healthy providers available")
            # Fallback to all providers if none are healthy
            available = [p for p in self.providers if p not in (exclude_providers or [])]
            if not available:
                return None
        
        # Apply load balancing strategy
        load_balance_strategy = self.config.get('load_balance_strategy', 'weighted_round_robin')
        selected = self.load_balancer.select_provider(
            available,
            self.health_data,
            load_balance_strategy
        )
        
        if selected:
            self.load_balancer.record_request(selected)
            logger.debug(f"Selected provider: {selected} from {len(available)} available")
        
        return selected
    
    async def execute_with_reliability(
        self,
        provider_executor: Callable,  # Function to execute with provider
        task_context: Optional[Dict[str, Any]] = None,
        max_retries: Optional[int] = None,
        exclude_providers: Optional[List[str]] = None
    ) -> Tuple[bool, Any, Dict[str, Any]]:
        """Execute task with full reliability management
        
        Returns:
            (success, result, metadata)
        """
        max_retries = max_retries or self.max_retries
        attempt = 0
        last_error = None
        providers_tried = set()
        
        metadata = {
            "attempts": 0,
            "providers_tried": [],
            "total_latency_ms": 0,
            "failover_occurred": False,
            "circuit_breaker_triggered": False
        }
        
        start_time = time.time()
        
        while attempt <= max_retries:
            attempt += 1
            metadata["attempts"] = attempt
            
            # Select provider
            provider = self.select_provider(task_context, exclude_providers)
            if not provider:
                last_error = "No providers available"
                break
            
            if provider in providers_tried:
                metadata["failover_occurred"] = True
            
            providers_tried.add(provider)
            metadata["providers_tried"].append(provider)
            
            # Check circuit breaker
            circuit = self.circuit_breakers[provider]
            if not circuit.can_execute():
                metadata["circuit_breaker_triggered"] = True
                logger.debug(f"Circuit breaker open for {provider}, trying next")
                continue
            
            # Execute request
            request_start = time.time()
            try:
                result = await provider_executor(provider)
                request_latency = (time.time() - request_start) * 1000
                
                # Record success
                self._record_success(provider, request_latency)
                self.load_balancer.record_completion(provider)
                
                # Calculate total latency
                metadata["total_latency_ms"] = (time.time() - start_time) * 1000
                
                return True, result, metadata
                
            except Exception as e:
                request_latency = (time.time() - request_start) * 1000
                last_error = str(e)
                
                # Record failure
                self._record_failure(provider, request_latency, str(e))
                self.load_balancer.record_completion(provider)
                
                logger.warning(f"Provider {provider} failed (attempt {attempt}): {e}")
                
                # Check if we should retry with same provider or switch
                if self._should_retry_with_same_provider(e, attempt, max_retries):
                    # Apply exponential backoff
                    delay = min(self.base_retry_delay * (2 ** (attempt - 1)), self.max_retry_delay)
                    await asyncio.sleep(delay)
                    continue
                else:
                    # Switch to next provider
                    exclude_providers = (exclude_providers or []) + [provider]
                    continue
        
        # All attempts failed
        metadata["total_latency_ms"] = (time.time() - start_time) * 1000
        return False, None, {**metadata, "error": last_error}
    
    def _record_success(self, provider: str, latency_ms: float):
        """Record successful request"""
        health = self.health_data[provider]
        circuit = self.circuit_breakers[provider]
        
        # Update health metrics
        health.total_requests += 1
        health.consecutive_successes += 1
        health.consecutive_failures = 0
        health.last_success_time = datetime.now()
        health.recent_latencies.append(latency_ms)
        
        # Update circuit breaker
        circuit.record_success()
        
        # Trigger metrics update
        health.update_metrics()
    
    def _record_failure(self, provider: str, latency_ms: float, error: str):
        """Record failed request"""
        health = self.health_data[provider]
        circuit = self.circuit_breakers[provider]
        
        # Update health metrics
        health.total_requests += 1
        health.failed_requests += 1
        health.consecutive_failures += 1
        health.consecutive_successes = 0
        health.last_failure_time = datetime.now()
        health.recent_latencies.append(latency_ms)  # Include failed request latency
        health.recent_errors.append((datetime.now(), error))
        
        # Update circuit breaker
        circuit.record_failure()
        
        # Trigger metrics update
        health.update_metrics()
    
    def _should_retry_with_same_provider(
        self,
        error: Exception,
        attempt: int,
        max_retries: int
    ) -> bool:
        """Determine if we should retry with the same provider"""
        error_str = str(error).lower()
        
        # Don't retry with same provider for these errors
        switch_provider_errors = [
            'authentication',
            'authorization', 
            'invalid_api_key',
            'quota_exceeded',
            'rate_limit',
            'model_not_found'
        ]
        
        for switch_error in switch_provider_errors:
            if switch_error in error_str:
                return False
        
        # Retry with same provider for transient errors, but limit attempts
        transient_errors = [
            'timeout',
            'connection',
            'network',
            'temporary',
            '502',  # Bad gateway
            '503',  # Service unavailable
            '504'   # Gateway timeout
        ]
        
        is_transient = any(error_pattern in error_str for error_pattern in transient_errors)
        
        # Retry same provider max 2 times for transient errors
        if is_transient and attempt <= 2:
            return True
        
        return False
    
    async def _health_monitor(self):
        """Background task for health monitoring"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                for provider_name in self.providers:
                    health = self.health_data[provider_name]
                    
                    # Perform lightweight health check
                    try:
                        # This would be implemented to do actual health check
                        # For now, just update based on recent activity
                        health.last_health_check = datetime.now()
                        
                        # Auto-recovery logic
                        if (health.status in [HealthStatus.UNHEALTHY, HealthStatus.OFFLINE] and
                            health.recovery_attempts < health.max_recovery_attempts):
                            
                            # Try to recover by forcing circuit breaker to half-open
                            circuit = self.circuit_breakers[provider_name]
                            if circuit.state == CircuitState.OPEN:
                                circuit._transition_to_half_open()
                                health.recovery_attempts += 1
                                logger.info(f"Attempting recovery for {provider_name} (attempt {health.recovery_attempts})")
                        
                    except Exception as e:
                        logger.debug(f"Health check failed for {provider_name}: {e}")
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _metrics_updater(self):
        """Background task for updating metrics"""
        while True:
            try:
                await asyncio.sleep(30)  # Update every 30 seconds
                
                for provider_name in self.providers:
                    health = self.health_data[provider_name]
                    health.update_metrics()
                
            except Exception as e:
                logger.error(f"Metrics updater error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    def get_reliability_status(self) -> Dict[str, Any]:
        """Get comprehensive reliability status"""
        status = {
            "providers": {},
            "circuit_breakers": {},
            "load_balancer": {
                "request_counts": dict(self.load_balancer.request_counts),
                "strategy": self.config.get('load_balance_strategy', 'weighted_round_robin')
            },
            "failover": {
                "strategy": self.failover_strategy.value,
                "max_retries": self.max_retries
            },
            "overall_health": self._calculate_overall_health()
        }
        
        # Provider health details
        for provider_name, health in self.health_data.items():
            status["providers"][provider_name] = {
                "status": health.status.value,
                "health_score": health.health_score,
                "success_rate": health.success_rate,
                "error_rate": health.error_rate,
                "avg_latency_ms": health.avg_latency_ms,
                "p95_latency_ms": health.p95_latency_ms,
                "consecutive_failures": health.consecutive_failures,
                "consecutive_successes": health.consecutive_successes,
                "total_requests": health.total_requests,
                "last_success": health.last_success_time.isoformat() if health.last_success_time else None,
                "last_failure": health.last_failure_time.isoformat() if health.last_failure_time else None
            }
        
        # Circuit breaker status
        for provider_name, circuit in self.circuit_breakers.items():
            status["circuit_breakers"][provider_name] = {
                "state": circuit.state.value,
                "failure_count": circuit.failure_count,
                "success_count": circuit.success_count,
                "total_blocked_requests": circuit.total_blocked_requests,
                "last_failure": circuit.last_failure_time.isoformat() if circuit.last_failure_time else None,
                "last_state_change": circuit.last_state_change.isoformat() if circuit.last_state_change else None
            }
        
        return status
    
    def _calculate_overall_health(self) -> Dict[str, Any]:
        """Calculate overall system health"""
        if not self.health_data:
            return {"score": 0.0, "status": "unknown", "healthy_providers": 0}
        
        healthy_count = sum(
            1 for health in self.health_data.values()
            if health.status in [HealthStatus.HEALTHY, HealthStatus.RECOVERING]
        )
        
        total_providers = len(self.health_data)
        avg_health_score = sum(h.health_score for h in self.health_data.values()) / total_providers
        
        # Determine overall status
        if healthy_count == 0:
            overall_status = "critical"
        elif healthy_count < total_providers * 0.5:
            overall_status = "degraded"
        elif healthy_count < total_providers:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        return {
            "score": avg_health_score,
            "status": overall_status,
            "healthy_providers": healthy_count,
            "total_providers": total_providers,
            "availability_percentage": (healthy_count / total_providers) * 100
        }
    
    def force_provider_status(self, provider: str, status: HealthStatus, reason: str = "Manual override"):
        """Manually override provider status"""
        if provider in self.health_data:
            old_status = self.health_data[provider].status
            self.health_data[provider].status = status
            logger.info(f"Provider {provider} status changed from {old_status} to {status}: {reason}")
        else:
            logger.warning(f"Provider {provider} not found for status override")
    
    def reset_provider_health(self, provider: str):
        """Reset health metrics for a provider"""
        if provider in self.health_data:
            self.health_data[provider] = ProviderHealth(provider_name=provider)
            self.circuit_breakers[provider] = CircuitBreaker(
                provider_name=provider,
                failure_threshold=self.config.get('circuit_breaker_failure_threshold', 5),
                recovery_timeout_seconds=self.config.get('circuit_breaker_timeout', 60)
            )
            logger.info(f"Reset health metrics for provider: {provider}")
    
    async def shutdown(self):
        """Gracefully shutdown reliability manager"""
        logger.info("Shutting down reliability manager")
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        logger.info("Reliability manager shutdown complete")
