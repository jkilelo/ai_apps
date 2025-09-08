"""Session report aggregation utilities."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import time


@dataclass
class AppliedStrategy:
    name: str
    description: str | None = None


@dataclass
class AgentRunStat:
    agent: str
    runs: int
    errors: int
    total_ms: float


@dataclass
class SessionReport:
    started_at: float
    finished_at: float
    agent_stats: List[AgentRunStat]
    applied_strategies: List[AppliedStrategy]
    correlation_issues: List[Dict[str, Any]]
    stealth_checks: Dict[str, bool] | None = None
    navigation_plan: List[str] | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "elapsed_ms": (self.finished_at - self.started_at) * 1000,
            "agent_stats": [asdict(s) for s in self.agent_stats],
            "applied_strategies": [asdict(s) for s in self.applied_strategies],
            "correlation_issues": self.correlation_issues,
            "stealth_checks": self.stealth_checks or {},
            "navigation_plan": self.navigation_plan or [],
        }


def build_report(
    metrics_snapshot: Dict[str, Dict[str, float]],
    *,
    strategies: List[str],
    issues: List[Dict[str, Any]],
    started_at: float,
    finished_at: float,
    stealth_checks: Dict[str, bool] | None = None,
    navigation_plan: List[str] | None = None,
) -> SessionReport:
    stats = [
        AgentRunStat(
            agent=k,
            runs=int(v.get("runs", 0)),
            errors=int(v.get("errors", 0)),
            total_ms=float(v.get("total_ms", 0.0)),
        )
        for k, v in metrics_snapshot.items()
    ]
    applied = [AppliedStrategy(name=s) for s in strategies]
    return SessionReport(
        started_at=started_at,
        finished_at=finished_at,
        agent_stats=stats,
        applied_strategies=applied,
        correlation_issues=issues,
        stealth_checks=stealth_checks,
        navigation_plan=navigation_plan,
    )


__all__ = ["SessionReport", "build_report"]
