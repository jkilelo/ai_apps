#!/usr/bin/env python3
"""Minimal basic usage examples aligned with current architecture.

Removed legacy managers; each task:
 - Optionally asks the navigation agent to plan (LLM call – requires ANTHROPIC_API_KEY)
 - Executes directly with BrowserSession (stealth + human simulation available)
 - Produces a compact dict result

Only the essential task logic remains (navigation / form / extraction / multi-tab / waits / recovery).
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List

from core.browser import BrowserSession
from core.facade import AgentFacade

OUTPUT_DIR = Path("examples/outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def _plan(facade: AgentFacade, goal: str) -> str:
    """Invoke navigation agent; surface plain text or error string."""
    run = await facade.plan_navigation(goal)
    return (run.output or "").strip() if not run.error else f"ERROR: {run.error}"  # type: ignore[arg-type]


async def example_simple_navigation(facade: AgentFacade) -> Dict[str, Any]:
    plan = await _plan(facade, "Visit https://example.com and report the page title")
    async with BrowserSession() as session:
        await session.navigate("https://example.com")
        title = await session.page.title()
        shot = OUTPUT_DIR / "example_com.png"
        await session.page.screenshot(path=str(shot))
        return {"task": "simple_navigation", "title": title, "screenshot": str(shot), "plan": plan}


async def example_form_submission(facade: AgentFacade) -> Dict[str, Any]:
    plan = await _plan(facade, "Fill the demo form at httpbin and submit it")
    async with BrowserSession() as session:
        await session.navigate("https://httpbin.org/forms/post")
        p = session.page
        await p.fill('input[name="custname"]', "John Doe")
        await p.fill('input[name="custtel"]', "555-1234")
        await p.fill('input[name="custemail"]', "john@example.com")
        await p.check('input[name="size"][value="medium"]')
        await p.select_option('select[name="topping"]', "mushroom")
        pre_shot = OUTPUT_DIR / "form_filled.png"
        await p.screenshot(path=str(pre_shot))
        await p.click('input[type="submit"]')
        await p.wait_for_load_state("networkidle")
        content_len = len(await p.content())
        return {
            "task": "form_submission",
            "html_length": content_len,
            "plan": plan,
            "screenshot": str(pre_shot),
        }


async def example_json_extraction(facade: AgentFacade) -> Dict[str, Any]:
    plan = await _plan(facade, "Open the httpbin JSON endpoint and capture raw text length")
    async with BrowserSession() as session:
        await session.navigate("https://httpbin.org/json")
        pre = await session.page.query_selector("pre")
        text = (await pre.inner_text()) if pre else ""  # type: ignore[union-attr]
        return {"task": "json_extraction", "chars": len(text), "plan": plan}


async def example_multi_tab(facade: AgentFacade) -> Dict[str, Any]:
    plan = await _plan(facade, "Open two pages: httpbin root and user-agent; report titles")
    # Each BrowserSession currently wraps one page; create two sequentially (simpler than extending API now)
    async with BrowserSession() as s1:
        await s1.navigate("https://httpbin.org/")
        t1 = await s1.page.title()
    async with BrowserSession() as s2:
        await s2.navigate("https://httpbin.org/user-agent")
        t2 = await s2.page.title()
    return {"task": "multi_tab", "titles": [t1, t2], "plan": plan}


async def example_waits(facade: AgentFacade) -> Dict[str, Any]:
    plan = await _plan(facade, "Demonstrate waiting strategies on httpbin delay and root page")
    async with BrowserSession() as session:
        await session.navigate("https://httpbin.org/delay/2")  # networkidle by default after load
        await session.navigate("https://httpbin.org/")
        await session.page.wait_for_selector("h1")
        await session.page.wait_for_function("document.readyState === 'complete'")
        return {"task": "waiting_strategies", "status": "completed", "plan": plan}


async def example_error_recovery(facade: AgentFacade) -> Dict[str, Any]:
    plan = await _plan(facade, "Attempt a failing navigation then recover with a valid page")
    async with BrowserSession() as session:
        errors: List[str] = []
        try:
            await session.navigate("https://httpbin.org/nonexistent")
        except Exception as e:  # pragma: no cover - network/site variance
            errors.append(str(e))
        # Recovery
        await session.navigate("https://httpbin.org/")
        title = await session.page.title()
        return {"task": "error_recovery", "errors": errors, "recovered_title": title, "plan": plan}


async def run_all() -> List[Dict[str, Any]]:
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise SystemExit("HALT: ANTHROPIC_API_KEY missing – live LLM required for examples")
    facade = AgentFacade()
    tasks = [
        example_simple_navigation,
        example_form_submission,
        example_json_extraction,
        example_multi_tab,
        example_waits,
        example_error_recovery,
    ]
    results: List[Dict[str, Any]] = []
    for fn in tasks:
        try:
            results.append(await fn(facade))
        except Exception as e:  # continue executing remaining tasks
            results.append({"task": fn.__name__, "error": str(e)})
    return results


def main() -> None:
    print("AI-Stealth Browser Minimal Examples (Visible Browser enforced)")
    print("=" * 70)
    try:
        results = asyncio.run(run_all())
        for r in results:
            print(r)
        print("\nCompleted examples.")
    except SystemExit as se:
        print(str(se))
        raise
    except KeyboardInterrupt:  # pragma: no cover
        print("Interrupted.")
    except Exception as e:  # pragma: no cover
        print(f"Failure: {e}")


if __name__ == "__main__":  # pragma: no cover
    main()
