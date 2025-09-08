import pytest
from core import mcp_server as mcp


def test_list_tools_contains_expected():
    tools = mcp.list_tools()
    names = {t["name"] for t in tools}
    assert "navigate" in names and "extract" in names


@pytest.mark.asyncio
async def test_call_tool_unknown():
    r = await mcp.call_tool("nope")
    assert not r.ok and r.error == "unknown_tool"
