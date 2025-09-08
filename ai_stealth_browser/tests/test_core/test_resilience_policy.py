import pytest
from core.facade import AgentFacade
from core.resilience import ResiliencePolicy
from agents import registry

pytestmark = pytest.mark.anyio


async def test_custom_policy_attempts(monkeypatch):
    # Patch stealth agent to fail twice then succeed
    agent = getattr(registry, "stealth_agent")
    calls = {"n": 0}
    original = agent.run

    async def _run(prompt: str, deps=None):
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("temp")
        return type("X", (), {"output": type("O", (), {})()})()

    agent.run = _run  # type: ignore
    try:
        policy = ResiliencePolicy(attempts=4, timeout_s=5.0)
        f = AgentFacade(policy=policy)
        res = await f.assess_stealth("ctx")
        assert res.error is None
        assert calls["n"] == 3
    finally:
        agent.run = original  # type: ignore
