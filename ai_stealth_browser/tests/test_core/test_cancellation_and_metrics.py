import json
import pytest
from types import SimpleNamespace
from core.facade import AgentFacade
from core.cancellation import CancellationToken
from core.event_logging import LOG_PATH
from agents import registry
from agents.registry import StealthAdvisory

pytestmark = pytest.mark.anyio


def _patch_stealth():
    async def fake_run(prompt: str, deps=None):
        return SimpleNamespace(
            output=StealthAdvisory(risk_level="low", actions=[], justification="ok")
        )

    original = registry.stealth_agent.run
    registry.stealth_agent.run = fake_run  # type: ignore
    return original


async def test_cancellation_short_circuits(monkeypatch, tmp_path):
    original = _patch_stealth()
    try:
        from core import event_logging

        event_logging.LOG_PATH = tmp_path / "events.jsonl"  # type: ignore
        token = CancellationToken()
        token.cancel("testing")
        facade = AgentFacade()
        res = await facade.assess_stealth("ctx", cancellation=token)
        assert res.error == "testing"
        assert res.elapsed_ms == 0.0
        # metrics should still count a run (design choice) or not? currently not incremented on early cancel
        snap = facade.metrics_snapshot()
        assert snap == {}  # no run happened through agent
    finally:
        registry.stealth_agent.run = original  # type: ignore


async def test_metrics_snapshot_immutable(monkeypatch, tmp_path):
    original = _patch_stealth()
    try:
        from core import event_logging

        event_logging.LOG_PATH = tmp_path / "events.jsonl"  # type: ignore
        facade = AgentFacade()
        await facade.assess_stealth("ctx")
        snap = facade.metrics_snapshot()
        assert "stealth" in snap
        snap["stealth"]["runs"] = 999  # mutate external copy
        snap2 = facade.metrics_snapshot()
        assert snap2["stealth"]["runs"] != 999
    finally:
        registry.stealth_agent.run = original  # type: ignore


async def test_correlation_id_propagated(monkeypatch, tmp_path):
    original = _patch_stealth()
    try:
        from core import event_logging

        event_logging.LOG_PATH = tmp_path / "events.jsonl"  # type: ignore
        facade = AgentFacade()
        corr = "abc123"
        await facade.assess_stealth("ctx", correlation_id=corr)
        lines = (tmp_path / "events.jsonl").read_text(encoding="utf-8").splitlines()
        parsed = [json.loads(l) for l in lines]
        # ensure at least one start and complete event has correlation id
        assert any(r["data"].get("correlation_id") == corr for r in parsed)
    finally:
        registry.stealth_agent.run = original  # type: ignore
