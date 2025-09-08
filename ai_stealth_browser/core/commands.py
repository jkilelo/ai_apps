"""Command objects composing multi-agent workflows.

Each command is a small, explicit, awaitable unit that can be:
 - Sequenced
 - Retries wrapped
 - Logged / audited

They depend only on the AgentFacade interface, not concrete agent instances.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import uuid

from core.facade import AgentFacade, AgentRunResult
from core.session_report import build_report
import time
from core.correlation import correlate, CorrelatedIssue
from core.event_logging import append_event


class CommandError(RuntimeError):
    pass


@dataclass
class BaseCommand:
    facade: AgentFacade
    description: str = ""

    async def execute(self) -> List[AgentRunResult]:  # pragma: no cover (interface)
        raise NotImplementedError


@dataclass
class AssessAndNavigateCommand(BaseCommand):
    target_url: str = ""

    async def execute(self) -> List[AgentRunResult]:
        results: List[AgentRunResult] = []
        correlation_id = uuid.uuid4().hex
        stealth = await self.facade.assess_stealth(
            f"Assess risk before navigating to: {self.target_url}", correlation_id=correlation_id
        )
        results.append(stealth)
        if stealth.error:
            raise CommandError(f"Stealth assessment failed: {stealth.error}")
        nav = await self.facade.plan_navigation(
            f"Plan safe navigation sequence to {self.target_url}", correlation_id=correlation_id
        )
        results.append(nav)
        return results


@dataclass
class FullArchitectureExplorationCommand(BaseCommand):
    feature_request: str = ""
    include_perf: bool = True
    include_security: bool = True

    async def execute(self) -> List[AgentRunResult]:
        results: List[AgentRunResult] = []
        correlation_id = uuid.uuid4().hex
        started_at = time.time()
        arch = await self.facade.architecture_plan(
            self.feature_request, correlation_id=correlation_id
        )
        results.append(arch)
        if arch.error:
            raise CommandError(f"Architecture planning failed: {arch.error}")
        if self.include_perf:
            perf = await self.facade.analyze_performance(
                f"Analyze performance concerns for: {self.feature_request}",
                correlation_id=correlation_id,
            )
            results.append(perf)
        if self.include_security:
            sec = await self.facade.summarize_security(
                f"Assess security implications for: {self.feature_request}",
                correlation_id=correlation_id,
            )
            results.append(sec)
        learn = await self.facade.adaptive_learning_update(
            f"Ingest trace summary after planning: {self.feature_request}",
            correlation_id=correlation_id,
        )
        results.append(learn)
        # Correlate perf + security if both present and successful
        perf_out = next((r for r in results if r.agent == "performance" and not r.error), None)
        sec_out = next((r for r in results if r.agent == "security" and not r.error), None)
        if perf_out and sec_out:
            try:
                correlated: List[CorrelatedIssue] = correlate(perf_out.output, sec_out.output)  # type: ignore[arg-type]
                if correlated:
                    append_event(
                        "correlation_summary",
                        {
                            "count": len(correlated),
                            "top": [c.__dict__ for c in correlated[:5]],
                            "correlation_id": correlation_id,
                        },
                    )
                    # Attach as synthetic AgentRunResult for downstream consumers
                    results.append(
                        AgentRunResult(
                            agent="correlation",
                            input="performance+security",
                            output=correlated,
                            raw=correlated,
                            run_id=correlation_id,
                            elapsed_ms=0.0,
                        )
                    )
            except Exception as e:  # pragma: no cover - defensive
                append_event(
                    "correlation_error",
                    {"error": str(e), "correlation_id": correlation_id},
                )
        finished_at = time.time()
        # Build session report (strategies list currently static placeholder)
        metrics = self.facade.metrics_snapshot()
        corr_issues = []
        for r in results:
            if r.agent == "correlation" and isinstance(r.output, list):
                corr_issues = [getattr(i, "__dict__", i) for i in r.output]
                break
        report = build_report(
            metrics,
            strategies=["navigator", "canvas", "timezone", "webgl", "audio", "font"],
            issues=corr_issues,
            started_at=started_at,
            finished_at=finished_at,
        )
        append_event("session_report", report.to_dict())
        return results


__all__ = [
    "BaseCommand",
    "AssessAndNavigateCommand",
    "FullArchitectureExplorationCommand",
    "CommandError",
]
