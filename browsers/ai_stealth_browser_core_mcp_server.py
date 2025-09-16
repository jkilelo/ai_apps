"""Minimal MCP-like server stub.

Not a full protocol implementation—just a facade to call internal tools.
This is a placeholder for future real MCP compliance.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict
from pydantic import BaseModel

from core.browser import BrowserSession, BrowserConfig
from core.extraction import ExtractionPlan, run_extraction


class ToolResponse(BaseModel):
    ok: bool
    data: Any = None
    error: str | None = None


async def _tool_navigate(url: str) -> ToolResponse:
    async with BrowserSession(BrowserConfig(headless=False, apply_fp_strategies=True)) as session:
        await session.navigate(url)
        content = await session.content()
    return ToolResponse(ok=True, data={"length": len(content)})


async def _tool_extract(url: str, selectors: list[str]) -> ToolResponse:
    async with BrowserSession(BrowserConfig(headless=False, apply_fp_strategies=True)) as session:
        await session.navigate(url)
        plan = ExtractionPlan(items=selectors)
        items = await run_extraction(session, plan)
    return ToolResponse(ok=True, data=[i.model_dump() for i in items])


async def call_tool(name: str, **params) -> ToolResponse:
    try:
        if name == "navigate":
            return await _tool_navigate(params["url"])
        if name == "extract":
            return await _tool_extract(params["url"], params.get("selectors", []))
        return ToolResponse(ok=False, error="unknown_tool")
    except Exception as e:  # pragma: no cover - defensive
        return ToolResponse(ok=False, error=str(e))


def list_tools() -> list[dict[str, Any]]:
    return [
        {"name": "navigate", "params": ["url"], "desc": "Navigate to URL and return page length"},
        {"name": "extract", "params": ["url", "selectors"], "desc": "Extract text for selectors"},
    ]


__all__ = ["call_tool", "list_tools", "ToolResponse"]
