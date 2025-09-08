"""Performance & security correlation heuristics.

Takes structured outputs from performance and security agents and produces
joined insights highlighting where performance bottlenecks and security risks
coincide (higher priority for remediation).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List
from agents.registry import PerfAnalysis, SecuritySummary, PerfBottleneck, SecurityFinding


@dataclass
class CorrelatedIssue:
    area: str
    security_risk: str
    perf_gap: float
    severity: str
    recommendation: str


SEVERITY_ORDER = ["low", "medium", "high", "critical"]


def _normalize(sev: str) -> str:
    sev_l = sev.lower()
    if sev_l not in SEVERITY_ORDER:
        return "low"
    return sev_l


def correlate(perf: PerfAnalysis, security: SecuritySummary) -> List[CorrelatedIssue]:
    issues: List[CorrelatedIssue] = []
    # Build quick lookup from security finding id/description tokens
    findings: List[SecurityFinding] = security.findings
    for b in perf.bottlenecks:
        # Heuristic: match if bottleneck area token appears in finding description or id
        area_token = b.area.lower()
        matched = [
            f for f in findings if area_token in f.description.lower() or area_token in f.id.lower()
        ]
        for f in matched:
            gap = max(0.0, b.observed - b.baseline)
            base_sev = _normalize(f.severity)
            # escalate severity if perf gap proportionally large
            escalation_steps = 1 if gap > b.baseline * 0.25 else 0
            sev_index = min(
                len(SEVERITY_ORDER) - 1, SEVERITY_ORDER.index(base_sev) + escalation_steps
            )
            sev_final = SEVERITY_ORDER[sev_index]
            issues.append(
                CorrelatedIssue(
                    area=b.area,
                    security_risk=f.id,
                    perf_gap=gap,
                    severity=sev_final,
                    recommendation=f"Address security finding '{f.id}' alongside optimizing {b.area} (gap {gap:.2f}).",
                )
            )
    # Sort highest severity first then by perf gap descending
    issues.sort(key=lambda x: (SEVERITY_ORDER.index(x.severity), -x.perf_gap))
    return issues


__all__ = ["CorrelatedIssue", "correlate"]
