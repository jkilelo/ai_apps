import asyncio
import types
import pytest
from core.actions import Nav, Click, Type, Wait, Extract
from core.action_executor import ActionExecutor


class DummyElement:
    def __init__(self, text=""):
        self._text = text
        self.clicked = False
        self.filled = None

    async def click(self):
        self.clicked = True

    async def fill(self, value):
        self.filled = value

    async def text_content(self):
        return self._text


class DummyPage:
    def __init__(self):
        self.elements = {}

    async def query_selector(self, sel):
        return self.elements.get(sel)


class DummySession:
    def __init__(self):
        self.page = DummyPage()
        self.navigated = []

    async def navigate(self, url):
        self.navigated.append(url)


@pytest.mark.asyncio
async def test_action_executor_flow():
    sess = DummySession()
    sess.page.elements[".btn"] = DummyElement()
    sess.page.elements["input"] = DummyElement()
    sess.page.elements["h1"] = DummyElement("Title Text")

    acts = [
        Nav(raw="NAV https://x", url="https://x"),
        Click(raw="CLICK .btn", selector=".btn"),
        Type(raw="TYPE input => value", selector="input", text="value"),
        Wait(raw="WAIT 10", ms=10),
        Extract(raw="EXTRACT h1", selector="h1"),
    ]
    ex = ActionExecutor(sess)
    out = await ex.run(acts)
    assert out["count"] == 5
    sel_click = [r for r in out["results"] if r["action"] == "CLICK"][0]
    assert sel_click["ok"] is True
    sel_type = [r for r in out["results"] if r["action"] == "TYPE"][0]
    assert sel_type["ok"] is True
    ext = [r for r in out["results"] if r["action"] == "EXTRACT"][0]
    assert ext["text"] == "Title Text"
