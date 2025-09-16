"""Resilience utilities: retry, timeout, and simple circuit breaker.

Designed to wrap agent and browser operations with consistent policies.

Features:
 - async retry with exponential backoff + jitter
 - timeout wrapper (cancels awaited task if exceeding limit)
 - circuit breaker (open/half-open/closed) with failure threshold & cool-off

Kept self-contained (no external deps) for simplicity and testability.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Awaitable, Callable, TypeVar, Optional, Any, Iterable

T = TypeVar("T")


class RetryError(RuntimeError):
    pass


async def with_timeout(coro: Awaitable[T], timeout_s: float) -> T:
    """Await `coro` with a timeout.

    Raises asyncio.TimeoutError if exceeded.
    """
    return await asyncio.wait_for(coro, timeout=timeout_s)


async def retry(
    func: Callable[[], Awaitable[T]],
    *,
    attempts: int = 3,
    backoff_base: float = 0.2,
    backoff_factor: float = 2.0,
    max_backoff: float = 3.0,
    retry_exceptions: tuple[type[BaseException], ...] = (Exception,),
    give_up: Optional[Callable[[BaseException], bool]] = None,
    jitter: float = 0.1,
) -> T:
    """Retry an async callable with exponential backoff and jitter.

    Args:
        func: async zero-arg callable.
        attempts: total attempts (>=1). Final failure raises RetryError.
        backoff_base: initial delay seconds.
        backoff_factor: multiplier per attempt.
        max_backoff: cap for delay.
        retry_exceptions: exception types to retry on.
        give_up: optional predicate; if returns True for exception, abort early.
        jitter: random jitter upper bound (uniform [0, jitter]).
    """
    if attempts < 1:
        raise ValueError("attempts must be >= 1")
    last_exc: Optional[BaseException] = None
    for attempt in range(1, attempts + 1):
        try:
            return await func()
        except retry_exceptions as e:  # pragma: no cover - exercised indirectly
            last_exc = e
            if give_up and give_up(e):
                break
            if attempt == attempts:
                break
            delay = min(backoff_base * (backoff_factor ** (attempt - 1)), max_backoff)
            if jitter > 0:
                delay += jitter * 0.5  # simple deterministic jitter (avoid random dep here)
            await asyncio.sleep(delay)
    raise RetryError(f"Operation failed after {attempts} attempts: {last_exc}")


@dataclass
class CircuitBreakerState:
    failures: int = 0
    opened_at: float = 0.0
    state: str = "closed"  # closed | open | half-open


class CircuitBreaker:
    """Simple circuit breaker for async operations.

    Transitions:
        closed -> open when failures >= failure_threshold
        open -> half-open after reset_timeout
        half-open -> closed on success or open on failure
    """

    def __init__(
        self,
        *,
        failure_threshold: int = 5,
        reset_timeout: float = 30.0,
        half_open_max_calls: int = 1,
    ) -> None:
        self._cfg = (failure_threshold, reset_timeout, half_open_max_calls)
        self._state = CircuitBreakerState()
        self._half_open_calls = 0

    @property
    def state(self) -> str:
        # Auto transition from open to half-open if time elapsed
        if self._state.state == "open":
            _, reset_timeout, _ = self._cfg
            if (time.time() - self._state.opened_at) >= reset_timeout:
                self._state.state = "half-open"
                self._half_open_calls = 0
        return self._state.state

    def record_success(self) -> None:
        self._state.failures = 0
        prev = self._state.state
        self._state.state = "closed"
        self._half_open_calls = 0
        if prev != "closed":  # transition event hook placeholder
            try:
                from core.event_logging import append_event  # local import to avoid cycle

                append_event("circuit_transition", {"from": prev, "to": "closed"})
            except Exception:  # pragma: no cover
                pass

    def record_failure(self) -> None:
        failure_threshold, _, _ = self._cfg
        self._state.failures += 1
        if self._state.state == "half-open":  # immediate re-open
            prev = self._state.state
            self._state.state = "open"
            self._state.opened_at = time.time()
            try:
                from core.event_logging import append_event

                append_event("circuit_transition", {"from": prev, "to": "open"})
            except Exception:  # pragma: no cover
                pass
            return
        if self._state.failures >= failure_threshold and self._state.state == "closed":
            prev = self._state.state
            self._state.state = "open"
            self._state.opened_at = time.time()
            try:
                from core.event_logging import append_event

                append_event("circuit_transition", {"from": prev, "to": "open"})
            except Exception:  # pragma: no cover
                pass

    async def run(self, func: Callable[[], Awaitable[T]]) -> T:
        st = self.state
        if st == "open":
            raise RuntimeError("circuit_open")
        if st == "half-open":
            _, _, half_open_max_calls = self._cfg
            if self._half_open_calls >= half_open_max_calls:
                raise RuntimeError("circuit_half_open_limit")
            self._half_open_calls += 1
        try:
            result = await func()
        except Exception:
            self.record_failure()
            raise
        else:
            self.record_success()
            return result


@dataclass
class ResiliencePolicy:
    attempts: int = 3
    timeout_s: float = 45.0
    backoff_base: float = 0.4
    backoff_factor: float = 2.0
    max_backoff: float = 5.0
    jitter: float = 0.2
    circuit_failure_threshold: int = 4
    circuit_reset_timeout: float = 20.0
    half_open_max_calls: int = 1

    def create_circuit(self) -> CircuitBreaker:
        return CircuitBreaker(
            failure_threshold=self.circuit_failure_threshold,
            reset_timeout=self.circuit_reset_timeout,
            half_open_max_calls=self.half_open_max_calls,
        )


__all__ = [
    "retry",
    "with_timeout",
    "CircuitBreaker",
    "CircuitBreakerState",
    "RetryError",
    "ResiliencePolicy",
]
