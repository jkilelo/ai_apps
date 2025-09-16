import pytest
from types import SimpleNamespace
import builtins

from core.facade import AgentFacade
from core.browser import BrowserSession, BrowserConfig
from core import correlation
from core.correlation import correlate
from agents.registry import PerfAnalysis, PerfBottleneck, SecuritySummary, SecurityFinding

pytestmark = pytest.mark.anyio


async def test_strategy_threshold_edges():
    f = AgentFacade()
    # detection_risk below thresholds => minimal bump (only initial 0.5)
    ctx_low = await f.evaluate_strategies(detection_risk=0.2)
    assert ctx_low.stealth_score == 0.5
    # between 0.3 and 0.7 triggers only human simulation +0.1
    ctx_mid = await f.evaluate_strategies(detection_risk=0.5)
    assert 0.59 <= ctx_mid.stealth_score <= 0.61  # allow float nuance
    # high risk triggers both (+0.1 then +0.2)
    ctx_hi = await f.evaluate_strategies(detection_risk=0.95)
    assert ctx_hi.stealth_score >= 0.79


def test_correlation_escalation_severity():
    perf = PerfAnalysis(
        bottlenecks=[
            PerfBottleneck(
                area="api", metric="latency", baseline=100, observed=140, suggestion="cache"
            )
        ]
    )
    sec = SecuritySummary(
        risk_level="low",
        findings=[
            SecurityFinding(
                id="api_access", severity="medium", description="api issue", recommendation="lock"
            )
        ],
    )
    issues = correlate(perf, sec)
    # gap 40 > 25% baseline -> one escalation step: medium -> high
    assert issues and issues[0].severity in {"high", "critical"}


async def test_browser_session_jitter_disabled(monkeypatch):
    # Avoid playwright by using Dummy pattern via subclass
    class NoJitterSession(BrowserSession):
        async def __aenter__(self):  # type: ignore
            async def _goto(*a, **k):
                return None

            async def _content():
                return "<html></html>"

            async def _evaluate(script):
                return 1

            self._page = SimpleNamespace(
                goto=_goto,
                content=_content,
                evaluate=_evaluate,
            )
            return self

        async def __aexit__(self, *a):  # type: ignore
            return False

    cfg = BrowserConfig(jitter_range=(0.0, 0.0))
    async with NoJitterSession(cfg) as s:
        await s.navigate("http://x")  # should not sleep
        assert (await s.content()).startswith("<html>")


@pytest.mark.anyio
async def test_event_logging_io_error(monkeypatch, tmp_path):
    from core import event_logging

    event_logging.LOG_PATH = tmp_path / "events.jsonl"  # type: ignore
    f = AgentFacade()
    # Patch agent to avoid network call
    from agents import registry as reg

    orig_run = reg.stealth_agent.run

    async def fake_run(prompt: str, deps=None):
        return SimpleNamespace(
            output=SimpleNamespace(risk_level="low", actions=[], justification="ok")
        )

    reg.stealth_agent.run = fake_run  # type: ignore
    # Patch append_event to raise after first call
    from core import event_logging as ev

    orig_append = ev.append_event
    first = True

    def bad_append(event_type, payload):  # type: ignore
        nonlocal first
        if first:
            first = False
            orig_append(event_type, payload)
        else:
            raise OSError("disk full")

    monkeypatch.setattr(ev, "append_event", bad_append)
    try:
        # Should not raise despite logging failure on second event
        res = await f.assess_stealth("ctx")
        assert res.output.risk_level == "low"
    finally:
        reg.stealth_agent.run = orig_run  # type: ignore
        monkeypatch.setattr(ev, "append_event", orig_append)
