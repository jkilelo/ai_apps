#!/usr/bin/env python3
"""Minimal Google search example aligned with current architecture.

Replaces legacy mock-based implementation. Performs a single live Google search:
 - Uses navigation agent to plan
 - Uses BrowserSession to execute (visible browser enforced)
 - Extracts top N result titles + URLs (best-effort selectors)
 - HALTs if ANTHROPIC_API_KEY missing (live LLM required)

Note: Google may present consent / bot-detection interstitials; this example keeps
logic intentionally simple and best-effort — it will return whatever results it can
collect without complex flows. Adjust selectors if Google markup shifts.
"""

from __future__ import annotations

import asyncio
import os
import sys
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import quote_plus

# Ensure project root (containing 'core') is on sys.path when run directly
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.browser import BrowserSession  # type: ignore
from core.facade import AgentFacade  # type: ignore

OUTPUT_DIR = Path("examples/outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class SimpleSearchResult:
    title: str
    url: str
    position: int


async def _plan(facade: AgentFacade, query: str) -> str:
    prompt = f"Plan minimal steps to perform a Google search for: {query}. Emphasize speed."
    run = await facade.plan_navigation(prompt)
    if run.error:
        return f"ERROR: {run.error}"
    # run.output is a NavigationPlan pydantic model; serialize steps succinctly
    try:  # type: ignore[attr-defined]
        steps = getattr(run.output, "steps", []) or []
        target = getattr(run.output, "target_url", None)
        core = "; ".join(steps)
        return core + (f" | target={target}" if target else "")
    except Exception:  # pragma: no cover - defensive
        return str(run.output)


async def google_search(query: str, max_results: int = 5) -> Dict[str, Any]:
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise SystemExit(
            "HALT: ANTHROPIC_API_KEY missing – live LLM required for google_search example"
        )
    facade = AgentFacade()
    plan = await _plan(facade, query)
    results: List[SimpleSearchResult] = []
    blocked = False
    engine = "google"
    async with BrowserSession() as session:
        p = session.page
        await session.navigate("https://www.google.com")
        # Consent best-effort
        for sel in ["button:has-text('Accept all')", "button:has-text('I agree')"]:
            try:  # pragma: no cover - environment dependent
                await p.locator(sel).first.click(timeout=2000)
                break
            except Exception:
                continue
        try:
            await p.wait_for_selector("textarea[name='q']", timeout=8000)
            # Human-like pre-move / jitter (cursor & scroll)
            try:
                await session.simulate_human(duration_s=1.2)
            except Exception:
                pass
            # Type with random per-character delays (20-120ms)
            for ch in query:
                await p.fill(
                    "textarea[name='q']", (await p.input_value("textarea[name='q']")) + ch
                )  # incremental build
                await asyncio.sleep(random.uniform(0.02, 0.12))
            await asyncio.sleep(random.uniform(0.15, 0.4))
            await p.keyboard.press("Enter")
            # Wait for either results or bot block 'sorry' page
            # Poll for up to 10s instead of a single selector wait
            end_time = time.time() + 10
            while time.time() < end_time:
                url = p.url
                if "sorry/" in url.lower():
                    blocked = True
                    break
                # If main results container present, proceed
                try:
                    if await p.query_selector("#search"):
                        break
                except Exception:
                    pass
                await asyncio.sleep(0.5)
        except Exception:
            # Likely bot detection / captcha
            blocked = True
        if blocked:
            engine = "duckduckgo"
            ddg_url = f"https://duckduckgo.com/?q={quote_plus(query)}"
            await p.goto(ddg_url)
            try:
                await p.wait_for_selector("form#search_form_homepage", timeout=8000)
            except Exception:
                pass  # proceed regardless
            # Results container (best-effort; DDG markup can change)
            await asyncio.sleep(1.5)  # small settle delay
        # Screenshot after whichever path
        shot = OUTPUT_DIR / f"{engine}_{query.replace(' ','_')}.png"
        try:
            await p.screenshot(path=str(shot))
        except Exception:  # pragma: no cover
            shot = Path("(screenshot failed)")
        if engine == "google" and not blocked:
            anchors = await p.query_selector_all("a h3")
        else:
            # DuckDuckGo selectors (try a few variants)
            anchors = []
            for sel in ["a[data-testid='result-title-a']", "h2 a", "a.result__a"]:
                nodes = await p.query_selector_all(sel)
                if nodes:
                    anchors = nodes
                    break
        for h3 in anchors[: max_results * 3]:  # oversample, de-dup
            try:
                title = (await h3.inner_text()).strip()
                parent = await h3.evaluate_handle("el => el.closest('a')")  # type: ignore[arg-type]
                href = await parent.get_property("href")  # type: ignore[attr-defined]
                url = str(await href.json_value()) if href else ""  # type: ignore[attr-defined]
                if not url or any(r.url == url for r in results):
                    continue
                results.append(SimpleSearchResult(title=title, url=url, position=len(results) + 1))
                if len(results) >= max_results:
                    break
            except Exception:  # pragma: no cover
                continue
    return {
        "task": "google_search",
        "query": query,
        "plan": plan,
        "results": [r.__dict__ for r in results],
        "count": len(results),
        "engine": engine,
        "blocked_google": blocked,
        "screenshot": str(shot),
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Minimal Google search example (AI-Stealth Browser)"
    )
    parser.add_argument(
        "query",
        nargs="?",
        default="playwright python",
        help="Search query (default: playwright python)",
    )
    parser.add_argument("--max", type=int, default=5, dest="max_results", help="Max results")
    args = parser.parse_args()
    try:
        out = asyncio.run(google_search(args.query, max_results=args.max_results))
        print(out)
    except SystemExit as se:
        print(str(se))
        raise
    except KeyboardInterrupt:  # pragma: no cover
        print("Interrupted")
    except Exception as e:  # pragma: no cover
        print(f"Failure: {e}")


if __name__ == "__main__":  # pragma: no cover
    main()
