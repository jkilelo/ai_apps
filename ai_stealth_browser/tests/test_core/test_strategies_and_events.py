import json
import pytest
from types import SimpleNamespace
from core.facade import AgentFacade
from core.event_logging import LOG_PATH
from agents import registry
from agents.registry import StealthAdvisory

pytestmark = pytest.mark.anyio


def _patch():
    async def fake_run(prompt: str, deps=None):
        return SimpleNamespace(
            output=StealthAdvisory(risk_level="low", actions=[], justification="ok")
        )

    orig = registry.stealth_agent.run
    registry.stealth_agent.run = fake_run  # type: ignore
    return orig


async def test_strategy_pipeline_adjusts_scores(tmp_path, monkeypatch):
    orig = _patch()
    try:
        facade = AgentFacade()
        ctx = await facade.evaluate_strategies(detection_risk=0.9)
        assert ctx.stealth_score >= 0.7  # combined adjustments
    finally:
        registry.stealth_agent.run = orig  # type: ignore


async def test_event_logging_creates_jsonl(tmp_path, monkeypatch):
    orig = _patch()
    try:
        # Redirect log path
        from core import event_logging

        new_path = tmp_path / "events.jsonl"
        event_logging.LOG_PATH = new_path  # type: ignore
        facade = AgentFacade()
        await facade.assess_stealth("context")
        assert new_path.exists()
        lines = new_path.read_text(encoding="utf-8").strip().splitlines()
        assert any("agent_run_start" in l for l in lines)
        parsed = [json.loads(l) for l in lines]
        assert all("ts" in r for r in parsed)
    finally:
        registry.stealth_agent.run = orig  # type: ignore
