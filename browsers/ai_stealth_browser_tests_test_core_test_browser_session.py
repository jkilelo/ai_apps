import pytest
from core.browser import BrowserSession, BrowserConfig

pytestmark = pytest.mark.anyio


class DummyPage:
    def __init__(self):
        self._scripts = []

    async def goto(self, url: str, wait_until: str = "load", timeout: int | None = None):  # type: ignore
        self.last_url = url

    async def content(self):  # type: ignore
        return "<html></html>"

    async def evaluate(self, script: str):  # type: ignore
        self._scripts.append(script)
        return 42


class DummySession(BrowserSession):
    async def __aenter__(self):  # type: ignore
        # bypass playwright startup; install dummy page
        self._page = DummyPage()
        return self

    async def __aexit__(self, exc_type, exc, tb):  # type: ignore
        return False

    async def _jitter(self):  # override to skip real sleep
        return


async def test_dummy_session_navigation_and_content():
    async with DummySession(BrowserConfig()) as s:
        await s.navigate("http://example.com")
        html = await s.content()
        assert "html" in html
        val = await s.evaluate("1+41")
        assert val == 42


async def test_dummy_session_requires_enter():
    s = DummySession()
    with pytest.raises(RuntimeError):
        _ = s.page  # access before context
