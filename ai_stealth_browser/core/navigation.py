"""Navigation execution helpers.

Takes a list of steps (strings) produced by the navigation agent
and executes a bounded subset against a BrowserSession.

Each step is heuristically classified:
 - Absolute URL (http/https) -> direct navigate
 - sleep:<ms> -> delay
 - js: <expr> -> evaluate snippet
Other steps currently skipped but retained for reporting.
"""

from __future__ import annotations

import asyncio
from typing import List, Dict, Any

from core.browser import BrowserSession
from core.config import RuntimeConfig


class NavigationExecutor:
    def __init__(self, session: BrowserSession, config: RuntimeConfig) -> None:
        self._session = session
        self._config = config

    async def run(
        self, steps: List[str]
    ) -> Dict[str, Any]:  # pragma: no cover - minimal orchestrator
        executed = []
        skipped = []
        errors = []
        limit = min(len(steps), self._config.navigation_max_steps)
        for raw in steps[:limit]:
            step = raw.strip()
            try:
                if step.startswith("http://") or step.startswith("https://"):
                    await self._session.navigate(step)
                    executed.append({"type": "navigate", "value": step})
                elif step.lower().startswith("sleep:"):
                    ms = int(step.split(":", 1)[1])
                    await asyncio.sleep(ms / 1000.0)
                    executed.append({"type": "sleep", "value": ms})
                elif step.lower().startswith("js:"):
                    snippet = step.split(":", 1)[1].strip()
                    await self._session.evaluate(snippet)
                    executed.append({"type": "js", "value": snippet})
                else:
                    skipped.append(step)
                # Optional human simulation per step
                if self._config.enable_human_sim:
                    pause_min, pause_max = self._config.human_pause_range_ms
                    # Use jitter already inside human simulator; just small await here
                    await asyncio.sleep((pause_min) / 1000.0)
            except Exception as e:  # pragma: no cover - defensive
                errors.append({"step": step, "error": str(e)})
        return {"executed": executed, "skipped": skipped, "errors": errors, "limit": limit}


__all__ = ["NavigationExecutor"]
