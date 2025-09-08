"""Facade for interacting with registered pydantic-ai agents.

Provides:
 - Event publication
 - Metrics (runs/errors/total_ms per agent)
 - Cancellation support
 - Strategy evaluation pipeline
 - Convenience wrappers
"""

from __future__ import annotations

import time
import asyncio
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional

from agents.registry import ALL_AGENTS
from core.cancellation import CancellationToken
from core.event_logging import append_event
from core.events import EventBus
from core.strategies import (
    DetectionMitigationStrategy,
    HumanSimulationStrategy,
    StrategyContext,
)
from core.resilience import retry, with_timeout, CircuitBreaker, RetryError, ResiliencePolicy


@dataclass
class AgentRunResult:
    agent: str
    input: str
    output: Any
    raw: Any
    error: Optional[str] = None
    run_id: Optional[str] = None
    elapsed_ms: Optional[float] = None


class AgentFacade:
    def __init__(
        self, event_bus: Optional[EventBus] = None, policy: Optional[ResiliencePolicy] = None
    ) -> None:
        self._agents = ALL_AGENTS
        self._event_bus = event_bus or EventBus()
        self._strategies = [HumanSimulationStrategy(), DetectionMitigationStrategy()]
        self._metrics: Dict[str, Dict[str, float]] = {}
        self._event_bus.subscribe("agent_run_start", lambda p: append_event("agent_run_start", p))
        self._event_bus.subscribe(
            "agent_run_complete", lambda p: append_event("agent_run_complete", p)
        )
        self._policy = policy or ResiliencePolicy()
        self._circuit_breaker = self._policy.create_circuit()

    # Introspection -------------------------------------------------------------
    @property
    def event_bus(self) -> EventBus:
        return self._event_bus

    def has_agent(self, name: str) -> bool:
        return name in self._agents

    def list_agents(self) -> Dict[str, str]:
        return {k: v.name for k, v in self._agents.items()}

    def metrics_snapshot(self) -> Dict[str, Dict[str, float]]:
        return {k: v.copy() for k, v in self._metrics.items()}

    # Core run ------------------------------------------------------------------
    async def run(
        self,
        agent_name: str,
        prompt: str,
        *,
        deps: Any = None,
        cancellation: Optional[CancellationToken] = None,
        correlation_id: Optional[str] = None,
    ) -> AgentRunResult:
        if agent_name not in self._agents:
            raise ValueError(f"Unknown agent: {agent_name}")
        agent = self._agents[agent_name]
        run_id = uuid.uuid4().hex
        start = time.perf_counter()
        base_event = {"agent": agent_name, "prompt": prompt, "run_id": run_id}
        if correlation_id:
            base_event["correlation_id"] = correlation_id
        self._event_bus.publish("agent_run_start", base_event)
        if cancellation and cancellation.is_cancelled():
            return AgentRunResult(
                agent=agent_name,
                input=prompt,
                output=None,
                raw=None,
                error=cancellation.reason or "cancelled",
                run_id=run_id,
                elapsed_ms=0.0,
            )

        async def _invoke():
            # Wrap actual agent.run with circuit breaker
            async def inner():
                return await agent.run(prompt, deps=deps)

            return await self._circuit_breaker.run(inner)

        async def _resilient_call():
            return await with_timeout(
                retry(
                    _invoke,
                    attempts=self._policy.attempts,
                    backoff_base=self._policy.backoff_base,
                    backoff_factor=self._policy.backoff_factor,
                    max_backoff=self._policy.max_backoff,
                    retry_exceptions=(Exception,),
                ),
                timeout_s=self._policy.timeout_s,
            )

        try:
            result = await _resilient_call()
            elapsed = (time.perf_counter() - start) * 1000
            out = AgentRunResult(
                agent=agent_name,
                input=prompt,
                output=result.output,
                raw=result,
                run_id=run_id,
                elapsed_ms=elapsed,
            )
            m = self._metrics.setdefault(agent_name, {"runs": 0, "errors": 0, "total_ms": 0})
            m["runs"] += 1
            m["total_ms"] += elapsed
            success_event = {
                "agent": agent_name,
                "prompt": prompt,
                "success": True,
                "run_id": run_id,
                "elapsed_ms": elapsed,
            }
            if correlation_id:
                success_event["correlation_id"] = correlation_id
            self._event_bus.publish("agent_run_complete", success_event)
            return out
        except (
            RetryError,
            asyncio.TimeoutError,
            RuntimeError,
            Exception,
        ) as e:  # pragma: no cover - defensive
            elapsed = (time.perf_counter() - start) * 1000
            m = self._metrics.setdefault(agent_name, {"runs": 0, "errors": 0, "total_ms": 0})
            m["runs"] += 1
            m["errors"] += 1
            m["total_ms"] += elapsed
            # Unwrap RetryError to surface original underlying message for caller expectations
            err_msg = str(e)
            if isinstance(e, RetryError):
                parts = err_msg.rsplit(": ", 1)
                if len(parts) == 2:
                    err_msg = parts[1]
            error_event = {
                "agent": agent_name,
                "prompt": prompt,
                "success": False,
                "error": err_msg,
                "run_id": run_id,
                "elapsed_ms": elapsed,
            }
            if correlation_id:
                error_event["correlation_id"] = correlation_id
            self._event_bus.publish("agent_run_complete", error_event)
            return AgentRunResult(
                agent=agent_name,
                input=prompt,
                output=None,
                raw=None,
                error=err_msg,
                run_id=run_id,
                elapsed_ms=elapsed,
            )

    async def evaluate_strategies(self, detection_risk: float) -> StrategyContext:
        ctx = StrategyContext(stealth_score=0.5, detection_risk=detection_risk)
        for strat in self._strategies:
            ctx = await strat.evaluate(ctx)
        return ctx

    # Convenience typed wrappers -------------------------------------------------
    async def assess_stealth(self, context: str, **kw) -> AgentRunResult:
        return await self.run("stealth", context, **kw)

    async def plan_navigation(self, goal: str, **kw) -> AgentRunResult:
        return await self.run("navigation", goal, **kw)

    async def summarize_security(self, surface: str, **kw) -> AgentRunResult:
        return await self.run("security", surface, **kw)

    async def analyze_performance(self, snapshot: str, **kw) -> AgentRunResult:
        return await self.run("performance", snapshot, **kw)

    async def adaptive_learning_update(self, trace_summary: str, **kw) -> AgentRunResult:
        return await self.run("learning", trace_summary, **kw)

    async def architecture_plan(self, feature: str, **kw) -> AgentRunResult:
        return await self.run("architect", feature, **kw)


__all__ = ["AgentFacade", "AgentRunResult"]
