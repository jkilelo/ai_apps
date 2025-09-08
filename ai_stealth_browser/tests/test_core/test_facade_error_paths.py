import json
import pytest
from types import SimpleNamespace

from core.facade import AgentFacade
from core.cancellation import CancellationToken
from core.commands import AssessAndNavigateCommand, FullArchitectureExplorationCommand, CommandError
from agents import registry

pytestmark = pytest.mark.anyio


def _patch_agent_success(name: str, output_obj):
    agent = getattr(registry, f"{name}_agent")
    original = agent.run

    async def _run(prompt: str, deps=None):
        return SimpleNamespace(output=output_obj)

    agent.run = _run  # type: ignore
    return original


def _patch_agent_error(name: str, exc: Exception):
    agent = getattr(registry, f"{name}_agent")
    original = agent.run

    async def _run(prompt: str, deps=None):  # type: ignore
        raise exc

    agent.run = _run  # type: ignore
    return original


async def test_unknown_agent_raises():
    f = AgentFacade()
    with pytest.raises(ValueError):
        await f.run("not_real", "x")


async def test_agent_exception_captured_and_metrics(tmp_path):
    from core import event_logging

    event_logging.LOG_PATH = tmp_path / "events.jsonl"  # type: ignore
    f = AgentFacade()
    original = _patch_agent_error("stealth", RuntimeError("boom"))
    try:
        res = await f.assess_stealth("ctx")
        assert res.error == "boom"
        snap = f.metrics_snapshot()["stealth"]
        assert snap["runs"] == 1 and snap["errors"] == 1
        lines = (tmp_path / "events.jsonl").read_text(encoding="utf-8").splitlines()
        parsed = [json.loads(l) for l in lines if l.strip()]
        assert any(
            r["event"] == "agent_run_complete" and r["data"].get("success") is False for r in parsed
        )
    finally:
        getattr(registry, "stealth_agent").run = original  # type: ignore


async def test_cancellation_before_run_no_metrics_increment(tmp_path):
    from core import event_logging

    event_logging.LOG_PATH = tmp_path / "events.jsonl"  # type: ignore
    f = AgentFacade()
    token = CancellationToken()
    token.cancel("stop")
    res = await f.assess_stealth("ctx", cancellation=token)
    assert res.error == "stop"
    assert f.metrics_snapshot() == {}


async def test_command_raises_on_stealth_error(tmp_path):
    from core import event_logging

    event_logging.LOG_PATH = tmp_path / "events.jsonl"  # type: ignore
    f = AgentFacade()
    err_original = _patch_agent_error("stealth", RuntimeError("stealth_fail"))
    nav_original = _patch_agent_success(
        "navigation", registry.NavigationPlan(steps=["noop"], target_url=None)
    )
    try:
        cmd = AssessAndNavigateCommand(facade=f, target_url="http://x")
        with pytest.raises(CommandError):
            await cmd.execute()
    finally:
        getattr(registry, "stealth_agent").run = err_original  # type: ignore
        getattr(registry, "navigation_agent").run = nav_original  # type: ignore


async def test_correlation_error_event_logged(monkeypatch, tmp_path):
    """Force correlate() to raise and ensure correlation_error event is recorded."""
    from core import event_logging
    from core import commands as cmd_mod

    event_logging.LOG_PATH = tmp_path / "events.jsonl"  # type: ignore
    f = AgentFacade()

    # Patch required agents to return minimal valid outputs
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

    def boom(*a, **kw):
        raise RuntimeError("corr_fail")

    monkeypatch.setattr(cmd_mod, "correlate", boom)
    try:
        cmd = FullArchitectureExplorationCommand(facade=f, feature_request="feat")
        results = await cmd.execute()
        # No correlation synthetic result due to failure
        assert all(r.agent != "correlation" for r in results)
        lines = (tmp_path / "events.jsonl").read_text(encoding="utf-8").splitlines()
        assert any("correlation_error" in l for l in lines)
    finally:
        getattr(registry, "architect_agent").run = arch_o  # type: ignore
        getattr(registry, "performance_agent").run = perf_o  # type: ignore
        getattr(registry, "security_agent").run = sec_o  # type: ignore
        getattr(registry, "learning_agent").run = learn_o  # type: ignore
