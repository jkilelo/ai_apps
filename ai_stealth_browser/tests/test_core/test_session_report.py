import json
import pytest
from core.commands import FullArchitectureExplorationCommand
from core.facade import AgentFacade
from agents import registry

pytestmark = pytest.mark.anyio


def _patch_agent_success(name: str, output_obj):
    agent = getattr(registry, f"{name}_agent")
    original = agent.run

    async def _run(prompt: str, deps=None):
        return type("R", (), {"output": output_obj})()

    agent.run = _run  # type: ignore
    return original


async def test_session_report_event(tmp_path):
    from core import event_logging

    event_logging.LOG_PATH = tmp_path / "events.jsonl"  # type: ignore
    f = AgentFacade()
    arch_o = _patch_agent_success(
        "architect", registry.ArchitecturePlan(tasks=["t"], risks=["r"], validation=["v"])
    )
    perf_o = _patch_agent_success(
        "performance", registry.PerfAnalysis(bottlenecks=[], quick_wins=[])
    )
    sec_o = _patch_agent_success(
        "security", registry.SecuritySummary(risk_level="low", findings=[])
    )
    learn_o = _patch_agent_success(
        "learning",
        registry.LearningUpdate(new_hypotheses=[], strategy_adjustments=[], metrics_to_watch=[]),
    )
    try:
        cmd = FullArchitectureExplorationCommand(facade=f, feature_request="feat")
        await cmd.execute()
        lines = (tmp_path / "events.jsonl").read_text(encoding="utf-8").splitlines()
        payloads = [json.loads(l) for l in lines if l.strip()]
        assert any(p["event"] == "session_report" for p in payloads)
    finally:
        getattr(registry, "architect_agent").run = arch_o  # type: ignore
        getattr(registry, "performance_agent").run = perf_o  # type: ignore
        getattr(registry, "security_agent").run = sec_o  # type: ignore
        getattr(registry, "learning_agent").run = learn_o  # type: ignore
