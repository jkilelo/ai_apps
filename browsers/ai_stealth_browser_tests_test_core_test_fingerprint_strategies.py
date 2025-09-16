import pytest
from types import SimpleNamespace
from core.browser import BrowserSession, BrowserConfig

pytestmark = pytest.mark.anyio


class DummyPage:
    def __init__(self):
        self.scripts = []
        self.mouse = SimpleNamespace(move=lambda x, y: None, wheel=lambda dx, dy: None)

    async def add_init_script(self, script):  # type: ignore
        self.scripts.append(script)


class DummySession(BrowserSession):
    async def __aenter__(self):  # type: ignore
        self._page = DummyPage()
        # manually run fingerprint strategies (bypass playwright launch path)
        if self.config.apply_fp_strategies:
            for strat in self._fp_strategies:
                await strat.apply(self._page)  # type: ignore[arg-type]
        return self

    async def __aexit__(self, *a):  # type: ignore
        return False


async def test_fingerprint_scripts_injected():
    async with DummySession(BrowserConfig()) as s:
        assert s.page.scripts, "Expected fingerprint mitigation scripts injected"
        joined = "\n".join(s.page.scripts)
        assert "navigator" in joined.lower()
        assert "canvas" in joined.lower() or "toBlob" in joined
    # Advanced scripts
    assert "webgl" in joined.lower()
    assert "audiocontext" in joined.lower()
    assert "font" in joined.lower()


async def test_disable_fp_strategies():
    async with DummySession(BrowserConfig(apply_fp_strategies=False)) as s:
        assert not s.page.scripts


async def test_simulate_human_runs():
    async with DummySession(BrowserConfig()) as s:
        count = await s.simulate_human(duration_s=0.2)
        assert isinstance(count, int)
