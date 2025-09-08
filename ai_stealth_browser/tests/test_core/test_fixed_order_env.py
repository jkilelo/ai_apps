import os
import random
from core.browser import BrowserSession, BrowserConfig


def test_fixed_stealth_order_env(monkeypatch):
    monkeypatch.setenv("FIXED_STEALTH_ORDER", "1")
    rng = random.Random(999)
    sess1 = BrowserSession(BrowserConfig(), rng=rng)
    rng2 = random.Random(123)
    sess2 = BrowserSession(BrowserConfig(), rng=rng2)
    order1 = [type(s).__name__ for s in sess1._fp_strategies]
    order2 = [type(s).__name__ for s in sess2._fp_strategies]
    assert order1 == order2  # fixed ordering enforced
