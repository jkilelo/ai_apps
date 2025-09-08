import pytest
from pydantic import BaseModel
from core.extraction import ExtractionPlan, run_extraction


class DummyEl:
    def __init__(self, text):
        self._text = text

    async def text_content(self):
        return self._text


class DummyPage:
    def __init__(self):
        self.map = {}

    async def query_selector(self, sel):
        return self.map.get(sel)


class DummySession:
    def __init__(self):
        self.page = DummyPage()


@pytest.mark.asyncio
async def test_run_extraction_basic():
    sess = DummySession()
    sess.page.map["h1"] = DummyEl("Title")
    sess.page.map["p.desc"] = DummyEl(" Description text ")
    plan = ExtractionPlan(items=["h1", "p.desc", "missing"])
    items = await run_extraction(sess, plan)
    by_sel = {i.selector: i.text for i in items}
    assert by_sel["h1"] == "Title"
    assert by_sel["p.desc"] == "Description text"
    assert by_sel["missing"] is None
