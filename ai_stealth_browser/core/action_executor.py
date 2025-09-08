"""Execution engine for parsed Actions.

Uses a BrowserSession; each action executed sequentially. For testability, the
session is duck-typed (only needs navigate, page.query_selector, page.type,
page.click, evaluate).

Retry logic (simple): For CLICK & TYPE, one retry if selector not found.
"""

from __future__ import annotations
import asyncio
from typing import List, Dict, Any
from core.actions import ActionT, Nav, Click, Type, Wait, Extract


class ActionExecutor:
    def __init__(self, session) -> None:
        self._session = session

    async def run(self, actions: List[ActionT]) -> Dict[str, Any]:
        results = []
        for act in actions:
            if isinstance(act, Nav):
                await self._session.navigate(act.url)
                results.append({"action": "NAV", "url": act.url})
            elif isinstance(act, Click):
                ok = await self._click_with_retry(act.selector)
                results.append({"action": "CLICK", "selector": act.selector, "ok": ok})
            elif isinstance(act, Type):
                ok = await self._type_with_retry(act.selector, act.text)
                results.append({"action": "TYPE", "selector": act.selector, "ok": ok})
            elif isinstance(act, Wait):
                await asyncio.sleep(act.ms / 1000.0)
                results.append({"action": "WAIT", "ms": act.ms})
            elif isinstance(act, Extract):
                text = await self._extract_text(act.selector)
                results.append({"action": "EXTRACT", "selector": act.selector, "text": text})
        return {"count": len(results), "results": results}

    async def _click_with_retry(self, selector: str) -> bool:
        page = self._session.page
        for attempt in (1, 2):
            el = await page.query_selector(selector)  # type: ignore[attr-defined]
            if el:
                try:
                    await el.click()
                    return True
                except Exception:
                    if attempt == 2:
                        return False
            await asyncio.sleep(0.15)
        return False

    async def _type_with_retry(self, selector: str, text: str) -> bool:
        page = self._session.page
        for attempt in (1, 2):
            el = await page.query_selector(selector)  # type: ignore[attr-defined]
            if el:
                try:
                    await el.fill(text)
                    return True
                except Exception:
                    if attempt == 2:
                        return False
            await asyncio.sleep(0.15)
        return False

    async def _extract_text(self, selector: str) -> str:
        page = self._session.page
        try:
            el = await page.query_selector(selector)  # type: ignore[attr-defined]
            if el:
                txt = await el.text_content()
                return txt.strip() if txt else ""
        except Exception:
            return ""
        return ""


__all__ = ["ActionExecutor"]
