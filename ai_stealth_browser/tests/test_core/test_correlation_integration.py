import pytest
from types import SimpleNamespace

from core.commands import FullArchitectureExplorationCommand
from core.facade import AgentFacade
from agents import registry
from agents.registry import (
    ArchitecturePlan,
    PerfAnalysis,
    PerfBottleneck,
    SecuritySummary,
    SecurityFinding,
    LearningUpdate,
    LearningAdjustment,
)

pytestmark = pytest.mark.anyio


def _patch_all_for_correlation(perf_bottleneck_area: str = "db"):
    originals = {}
    outputs = {
        "architect_agent": ArchitecturePlan(tasks=["t"], risks=["r"], validation=["v"]),
        "performance_agent": PerfAnalysis(
            bottlenecks=[
                PerfBottleneck(
                    area=perf_bottleneck_area,
                    metric="latency",
                    baseline=100.0,
                    observed=150.0,
                    suggestion="index",
                )
            ],
            quick_wins=[],
        ),
        "security_agent": SecuritySummary(
            risk_level="low",
            findings=[
                SecurityFinding(
                    id=f"{perf_bottleneck_area}_exposure",
                    severity="medium",
                    description=f"{perf_bottleneck_area} privilege issue",
                    recommendation="lockdown",
                )
            ],
        ),
        "learning_agent": LearningUpdate(
            new_hypotheses=[],
            strategy_adjustments=[LearningAdjustment(area="x", change="y", expected_effect="z")],
            metrics_to_watch=[],
        ),
    }
    for attr, output in outputs.items():
        agent = getattr(registry, attr)
        originals[attr] = agent.run

        async def _run(prompt: str, deps=None, _output=output):
            return SimpleNamespace(output=_output)

        agent.run = _run  # type: ignore
    return originals


def _restore(originals):
    for attr, fn in originals.items():
        getattr(registry, attr).run = fn  # type: ignore


async def test_full_architecture_command_includes_correlation(tmp_path, monkeypatch):
    from core import event_logging

    event_logging.LOG_PATH = tmp_path / "events.jsonl"  # type: ignore
    facade = AgentFacade()
    originals = _patch_all_for_correlation()
    try:
        cmd = FullArchitectureExplorationCommand(facade=facade, feature_request="feature X")
        results = await cmd.execute()
        # Ensure correlation synthetic result present
        correlation_results = [r for r in results if r.agent == "correlation"]
        assert correlation_results, "Expected correlation synthetic result"
        corr = correlation_results[0].output
        assert corr and corr[0].area == "db"
        # Check events file has correlation_summary
        lines = (tmp_path / "events.jsonl").read_text(encoding="utf-8").splitlines()
        assert any("correlation_summary" in l for l in lines)
    finally:
        _restore(originals)
