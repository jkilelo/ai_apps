import pytest
from core.browser import BrowserSession, BrowserConfig

pytestmark = pytest.mark.anyio


async def test_verify_stealth_requires_session():
    sess = BrowserSession(BrowserConfig())
    results = await sess.verify_stealth()
    assert results["session_started"] is False
