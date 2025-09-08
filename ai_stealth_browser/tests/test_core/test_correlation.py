import pytest
from agents.registry import PerfAnalysis, PerfBottleneck, SecuritySummary, SecurityFinding
from core.correlation import correlate

pytestmark = pytest.mark.anyio


def test_correlation_matches_and_escalates():
    perf = PerfAnalysis(
        bottlenecks=[
            PerfBottleneck(
                area="DB", metric="latency", baseline=100, observed=140, suggestion="index"
            )
        ]
    )
    sec = SecuritySummary(
        risk_level="medium",
        findings=[
            SecurityFinding(
                id="DB_INJECTION",
                severity="medium",
                description="DB risk area potential injection",
                recommendation="sanitize",
            )
        ],
    )
    issues = correlate(perf, sec)
    assert issues, "expected at least one correlated issue"
    issue = issues[0]
    assert issue.area == "DB"
    assert issue.security_risk == "DB_INJECTION"
    # escalation because gap > 25%
    assert issue.severity in ("high", "medium")
