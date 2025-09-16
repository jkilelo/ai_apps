"""
Error Recovery Patterns for AI Browser
Provides resilient error handling, retry logic, and fallback mechanisms
"""

import asyncio
import random
import time
from contextlib import asynccontextmanager
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from loguru import logger
from pydantic import BaseModel


T = TypeVar("T")


# =============================================================================
# Error Types
# =============================================================================

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"        # Can retry
    MEDIUM = "medium"  # Need fallback
    HIGH = "high"      # Need recovery
    CRITICAL = "critical"  # Need restart


class RecoverableError(Exception):
    """Base class for recoverable errors"""
    severity = ErrorSeverity.LOW
    max_retries = 3
    

class BrowserError(RecoverableError):
    """Browser-related errors"""
    severity = ErrorSeverity.MEDIUM
    max_retries = 2


class LLMError(RecoverableError):
    """LLM-related errors"""
    severity = ErrorSeverity.MEDIUM
    max_retries = 3


class NetworkError(RecoverableError):
    """Network-related errors"""
    severity = ErrorSeverity.LOW
    max_retries = 5


class RateLimitError(RecoverableError):
    """Rate limit errors"""
    severity = ErrorSeverity.LOW
    max_retries = 10


# =============================================================================
# Retry Strategies
# =============================================================================

class RetryStrategy(BaseModel):
    """Configuration for retry behavior"""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


def exponential_backoff(
    attempt: int,
    strategy: RetryStrategy
) -> float:
    """
    Calculate exponential backoff delay
    
    Args:
        attempt: Current attempt number (0-based)
        strategy: Retry configuration
        
    Returns:
        Delay in seconds
    """
    delay = min(
        strategy.initial_delay * (strategy.exponential_base ** attempt),
        strategy.max_delay
    )
    
    if strategy.jitter:
        # Add random jitter to prevent thundering herd
        delay = delay * (0.5 + random.random())
    
    return delay


def linear_backoff(
    attempt: int,
    strategy: RetryStrategy
) -> float:
    """Linear backoff with optional jitter"""
    delay = min(
        strategy.initial_delay * (attempt + 1),
        strategy.max_delay
    )
    
    if strategy.jitter:
        delay = delay * (0.8 + random.random() * 0.4)
    
    return delay


# =============================================================================
# Retry Decorator
# =============================================================================

def with_retry(
    strategy: Optional[RetryStrategy] = None,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Decorator for automatic retry with backoff
    
    Args:
        strategy: Retry configuration
        exceptions: Tuple of exceptions to catch
        on_retry: Callback on each retry
        
    Example:
        @with_retry(strategy=RetryStrategy(max_attempts=5))
        async def flaky_operation():
            return await external_api_call()
    """
    if strategy is None:
        strategy = RetryStrategy()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(strategy.max_attempts):
                try:
                    return await func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == strategy.max_attempts - 1:
                        logger.error(
                            f"Max retries ({strategy.max_attempts}) exceeded "
                            f"for {func.__name__}: {e}"
                        )
                        raise
                    
                    delay = exponential_backoff(attempt, strategy)
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{strategy.max_attempts} failed "
                        f"for {func.__name__}: {e}. Retrying in {delay:.1f}s..."
                    )
                    
                    if on_retry:
                        await on_retry(attempt, e)
                    
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(strategy.max_attempts):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == strategy.max_attempts - 1:
                        raise
                    
                    delay = exponential_backoff(attempt, strategy)
                    time.sleep(delay)
            
            raise last_exception
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# =============================================================================
# Circuit Breaker Pattern
# =============================================================================

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreaker:
    """
    Circuit breaker for preventing cascading failures
    
    Example:
        breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
        
        async with breaker:
            await risky_operation()
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open"""
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed > self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker entering half-open state")
                    return False
            return True
        return False
    
    def record_success(self):
        """Record successful operation"""
        self.last_success_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info("Circuit breaker closed (recovered)")
        else:
            self.failure_count = max(0, self.failure_count - 1)
    
    def record_failure(self):
        """Record failed operation"""
        self.last_failure_time = time.time()
        self.failure_count += 1
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(
                f"Circuit breaker opened after {self.failure_count} failures"
            )
    
    async def __aenter__(self):
        if self.is_open:
            raise BrowserError("Circuit breaker is open - service unavailable")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.record_failure()
        else:
            self.record_success()


# =============================================================================
# Fallback Mechanisms
# =============================================================================

class FallbackChain:
    """
    Chain of fallback handlers
    
    Example:
        fallback = FallbackChain()
        fallback.add(primary_handler)
        fallback.add(secondary_handler)
        fallback.add(emergency_handler)
        
        result = await fallback.execute(data)
    """
    
    def __init__(self):
        self.handlers: List[Callable] = []
    
    def add(self, handler: Callable) -> "FallbackChain":
        """Add fallback handler to chain"""
        self.handlers.append(handler)
        return self
    
    async def execute(self, *args, **kwargs) -> Any:
        """Execute handlers in order until one succeeds"""
        errors = []
        
        for i, handler in enumerate(self.handlers):
            try:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(*args, **kwargs)
                else:
                    result = handler(*args, **kwargs)
                
                if i > 0:
                    logger.info(f"Fallback {i} succeeded: {handler.__name__}")
                
                return result
                
            except Exception as e:
                errors.append((handler.__name__, str(e)))
                logger.warning(
                    f"Handler {handler.__name__} failed: {e}"
                )
                
                if i == len(self.handlers) - 1:
                    # Last handler failed
                    raise RuntimeError(
                        f"All fallbacks failed: {errors}"
                    )


# =============================================================================
# Recovery Manager
# =============================================================================

class RecoveryManager:
    """
    Centralized error recovery management
    
    Example:
        recovery = RecoveryManager()
        
        @recovery.recoverable
        async def risky_operation():
            return await external_call()
    """
    
    def __init__(self):
        self.strategies: Dict[type, RetryStrategy] = {
            NetworkError: RetryStrategy(max_attempts=5, initial_delay=2.0),
            RateLimitError: RetryStrategy(max_attempts=10, initial_delay=5.0),
            BrowserError: RetryStrategy(max_attempts=3, initial_delay=1.0),
            LLMError: RetryStrategy(max_attempts=3, initial_delay=3.0),
        }
        
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.fallback_chains: Dict[str, FallbackChain] = {}
    
    def add_circuit_breaker(
        self,
        name: str,
        breaker: CircuitBreaker
    ):
        """Register circuit breaker"""
        self.circuit_breakers[name] = breaker
    
    def add_fallback_chain(
        self,
        name: str,
        chain: FallbackChain
    ):
        """Register fallback chain"""
        self.fallback_chains[name] = chain
    
    def recoverable(
        self,
        fallback: Optional[str] = None,
        circuit_breaker: Optional[str] = None
    ):
        """
        Decorator for recoverable operations
        
        Args:
            fallback: Name of fallback chain to use
            circuit_breaker: Name of circuit breaker to use
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Check circuit breaker
                if circuit_breaker and circuit_breaker in self.circuit_breakers:
                    breaker = self.circuit_breakers[circuit_breaker]
                    if breaker.is_open:
                        logger.warning(f"Circuit open for {func.__name__}")
                        
                        # Try fallback if available
                        if fallback and fallback in self.fallback_chains:
                            chain = self.fallback_chains[fallback]
                            return await chain.execute(*args, **kwargs)
                        
                        raise BrowserError("Service unavailable")
                
                # Try primary operation with retry
                try:
                    for error_type, strategy in self.strategies.items():
                        if error_type in func.__annotations__.get('raises', []):
                            return await self._retry_with_strategy(
                                func, strategy, *args, **kwargs
                            )
                    
                    # No specific strategy, use default
                    return await func(*args, **kwargs)
                    
                except Exception as e:
                    logger.error(f"Operation failed: {func.__name__}: {e}")
                    
                    # Try fallback
                    if fallback and fallback in self.fallback_chains:
                        chain = self.fallback_chains[fallback]
                        return await chain.execute(*args, **kwargs)
                    
                    raise
            
            return wrapper
        
        return decorator
    
    async def _retry_with_strategy(
        self,
        func: Callable,
        strategy: RetryStrategy,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with retry strategy"""
        last_exception = None
        
        for attempt in range(strategy.max_attempts):
            try:
                return await func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                if attempt == strategy.max_attempts - 1:
                    raise
                
                delay = exponential_backoff(attempt, strategy)
                await asyncio.sleep(delay)
        
        raise last_exception


# =============================================================================
# Browser-Specific Recovery
# =============================================================================

class BrowserRecovery:
    """Browser-specific recovery patterns"""
    
    @staticmethod
    async def recover_from_crash(browser_manager) -> bool:
        """Recover from browser crash"""
        try:
            logger.info("Attempting browser recovery...")
            
            # Close existing browser if any
            try:
                await browser_manager.close()
            except:
                pass
            
            # Wait before restart
            await asyncio.sleep(2)
            
            # Restart browser
            await browser_manager.launch()
            
            logger.success("Browser recovered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Browser recovery failed: {e}")
            return False
    
    @staticmethod
    async def recover_from_timeout(page, selector: str) -> Optional[Any]:
        """Recover from selector timeout"""
        strategies = [
            # Strategy 1: Wait longer
            lambda: page.wait_for_selector(selector, timeout=60000),
            
            # Strategy 2: Reload page
            lambda: asyncio.gather(
                page.reload(),
                page.wait_for_selector(selector, timeout=30000)
            ),
            
            # Strategy 3: Use alternative selector
            lambda: page.query_selector("body")  # Fallback to body
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                logger.info(f"Trying recovery strategy {i+1}")
                result = await strategy()
                return result if not isinstance(result, tuple) else result[1]
                
            except Exception as e:
                logger.warning(f"Strategy {i+1} failed: {e}")
                continue
        
        return None


# =============================================================================
# LLM-Specific Recovery
# =============================================================================

class LLMRecovery:
    """LLM-specific recovery patterns"""
    
    @staticmethod
    async def switch_provider(
        providers: List[str],
        prompt: str,
        current_provider: str
    ) -> tuple[str, Any]:
        """Switch to alternative LLM provider"""
        for provider in providers:
            if provider == current_provider:
                continue
            
            try:
                logger.info(f"Switching to {provider}")
                # In real implementation, call actual provider
                # response = await call_provider(provider, prompt)
                response = f"Response from {provider}"
                return provider, response
                
            except Exception as e:
                logger.warning(f"Provider {provider} failed: {e}")
                continue
        
        raise LLMError("All LLM providers failed")
    
    @staticmethod
    async def reduce_token_usage(
        prompt: str,
        max_tokens: int = 4000
    ) -> str:
        """Reduce prompt size to fit token limits"""
        # Simple truncation (real implementation would be smarter)
        if len(prompt) > max_tokens:
            logger.info(f"Reducing prompt from {len(prompt)} to {max_tokens}")
            return prompt[:max_tokens] + "..."
        return prompt


# =============================================================================
# Global Recovery Instance
# =============================================================================

recovery_manager = RecoveryManager()

# Configure default strategies
recovery_manager.add_circuit_breaker(
    "browser",
    CircuitBreaker(failure_threshold=3, recovery_timeout=30)
)

recovery_manager.add_circuit_breaker(
    "llm",
    CircuitBreaker(failure_threshold=5, recovery_timeout=60)
)


# Example usage
if __name__ == "__main__":
    async def example():
        # Example 1: Retry decorator
        @with_retry(
            strategy=RetryStrategy(max_attempts=3),
            exceptions=(NetworkError,)
        )
        async def fetch_data():
            # Simulated network call
            if random.random() < 0.7:
                raise NetworkError("Connection failed")
            return "Success!"
        
        try:
            result = await fetch_data()
            print(f"Result: {result}")
        except NetworkError:
            print("Failed after retries")
        
        # Example 2: Circuit breaker
        breaker = CircuitBreaker(failure_threshold=2)
        
        for i in range(5):
            try:
                async with breaker:
                    if i < 2:
                        raise Exception("Simulated failure")
                    print(f"Call {i} succeeded")
            except Exception as e:
                print(f"Call {i} failed: {e}")
        
        # Example 3: Fallback chain
        chain = FallbackChain()
        chain.add(lambda: 1/0)  # Will fail
        chain.add(lambda: "Fallback 1")
        
        result = await chain.execute()
        print(f"Chain result: {result}")
    
    asyncio.run(example())