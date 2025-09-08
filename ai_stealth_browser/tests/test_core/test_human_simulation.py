import pytest
from core.human_simulation import HumanInteractionSimulator

pytestmark = pytest.mark.anyio


async def test_generate_events_non_empty():
    sim = HumanInteractionSimulator()
    events = sim.generate_events(duration_s=1.0, target_points=5)
    assert events, "Expected events generated"
    assert any(e.kind == "move" for e in events)


async def test_generate_zero_duration():
    sim = HumanInteractionSimulator()
    assert sim.generate_events(duration_s=0) == []
