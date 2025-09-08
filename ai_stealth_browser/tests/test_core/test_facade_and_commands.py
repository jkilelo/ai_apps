import pytest
from types import SimpleNamespace

from core.facade import AgentFacade
from core.commands import (
    AssessAndNavigateCommand,
    FullArchitectureExplorationCommand,
)
from agents import registry
from agents.registry import (
    StealthAdvisory,
    NavigationPlan,
    ArchitecturePlan,
    PerfAnalysis,
    SecuritySummary,
    LearningUpdate,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def facade():
    return AgentFacade()


def _patch_all():
    originals = {}
    mapping = {
        "stealth_agent": StealthAdvisory(risk_level="low", actions=[], justification="ok"),
        "navigation_agent": NavigationPlan(steps=["open"], target_url="http://x"),
        "architect_agent": ArchitecturePlan(tasks=["t1"], risks=["r1"], validation=["v1"]),
        "performance_agent": PerfAnalysis(bottlenecks=[], quick_wins=[]),
        "security_agent": SecuritySummary(risk_level="low", findings=[]),
        "learning_agent": LearningUpdate(
            new_hypotheses=[], strategy_adjustments=[], metrics_to_watch=[]
        ),
    }
    for attr, output in mapping.items():
        agent = getattr(registry, attr)
        originals[attr] = agent.run

        async def _run(prompt: str, deps=None, _output=output):
            return SimpleNamespace(output=_output)

        agent.run = _run  # type: ignore
    return originals


def _restore_all(originals):
    for attr, fn in originals.items():
        getattr(registry, attr).run = fn  # type: ignore


async def test_facade_basic_runs(facade):
    originals = _patch_all()
    try:
        res = await facade.assess_stealth("context")
        assert res.output.risk_level == "low"
        nav = await facade.plan_navigation("goal")
        assert nav.output.steps
    finally:
        _restore_all(originals)


async def test_assess_and_navigate_command(facade):
    originals = _patch_all()
    try:
        cmd = AssessAndNavigateCommand(facade=facade, target_url="http://x")
        results = await cmd.execute()
        assert len(results) == 2
    finally:
        _restore_all(originals)


async def test_full_architecture_exploration_command(facade):
    originals = _patch_all()
    try:
        cmd = FullArchitectureExplorationCommand(facade=facade, feature_request="feature X")
        results = await cmd.execute()
        # architecture + perf + security + learning
        assert len(results) == 4
    finally:
        _restore_all(originals)
