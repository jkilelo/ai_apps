import pytest
from core.resilience import CircuitBreaker
from core.event_logging import LOG_PATH
import json

pytestmark = pytest.mark.anyio


async def test_circuit_transition_events(tmp_path, monkeypatch):
    # Redirect log path
    monkeypatch.setattr("core.event_logging.LOG_PATH", tmp_path / "events.jsonl")
    from core.event_logging import append_event  # re-import to bind new LOG_PATH

    cb = CircuitBreaker(failure_threshold=2, reset_timeout=0.01)

    async def boom():
        raise RuntimeError("fail")

    # Two failures -> open
    for _ in range(2):
        with pytest.raises(RuntimeError):
            await cb.run(boom)

    # Force half-open by manipulating time
    import time as _t

    _t.sleep(0.02)
    try:
        await cb.run(boom)
    except RuntimeError:
        pass

    # Read events
    data = []
    with (tmp_path / "events.jsonl").open("r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("event") == "circuit_transition":
                data.append(rec["data"])
    assert any(d["to"] == "open" for d in data)


async def test_fingerprint_strategy_shuffle(monkeypatch):
    from core.browser import BrowserSession, BrowserConfig, _default_fp_strategies

    # Fixed RNG seeds yield reproducible but potentially different orders
    import random

    rng1 = random.Random(1234)
    rng2 = random.Random(4321)
    s1 = BrowserSession(BrowserConfig(), rng=rng1)
    s2 = BrowserSession(BrowserConfig(), rng=rng2)
    names = lambda sess: [type(s).__name__ for s in sess._fp_strategies]
    order1 = names(s1)
    order2 = names(s2)
    assert order1 != order2 or len(order1) == 1  # allow equality only if single strategy
