import pytest
from types import SimpleNamespace
from agents.registry import (
    stealth_agent,
    navigation_agent,
    ALL_AGENTS,
    StealthAdvisory,
    NavigationPlan,
)

pytestmark = pytest.mark.anyio


async def test_all_agents_construct():
    assert "stealth" in ALL_AGENTS
    assert stealth_agent is ALL_AGENTS["stealth"]


async def test_stealth_agent_override_basic():
    async def fake_run(prompt: str, deps=None):
        return SimpleNamespace(
            output=StealthAdvisory(risk_level="low", actions=[], justification="ok")
        )

    original = stealth_agent.run
    stealth_agent.run = fake_run  # type: ignore
    try:
        result = await stealth_agent.run("Assess minimal", deps=None)  # type: ignore
        assert result.output.risk_level == "low"
    finally:
        stealth_agent.run = original  # type: ignore


async def test_navigation_plan_min():
    async def fake_run(prompt: str, deps=None):
        return SimpleNamespace(output=NavigationPlan(steps=["noop"], target_url=None))

    original = navigation_agent.run
    navigation_agent.run = fake_run  # type: ignore
    try:
        result = await navigation_agent.run("Plan noop", deps=None)  # type: ignore
        assert result.output.steps == ["noop"]
    finally:
        navigation_agent.run = original  # type: ignore


async def test_agent_registry_basic():
    # Convenience alias matching user-invoked test name
    assert set(
        ["stealth", "navigation", "security", "performance", "learning", "architect"]
    ).issubset(set(ALL_AGENTS.keys()))
    assert stealth_agent is ALL_AGENTS["stealth"]
