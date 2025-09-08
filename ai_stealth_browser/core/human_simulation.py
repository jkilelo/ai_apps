"""Human interaction simulation utilities.

Lightweight generator of cursor movement + scroll events to reduce
deterministic automation signatures. Intentionally simple; can be
extended with keystrokes and dwell-time heuristics later.
"""

from __future__ import annotations

import math
import random
import asyncio
import inspect
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Any


@dataclass
class HumanEvent:
    kind: str  # move|scroll
    x: float
    y: float
    delay: float  # seconds after previous event
    meta: Dict[str, float] | None = None


class HumanInteractionSimulator:
    def __init__(self, *, rng: Optional[random.Random] = None) -> None:
        self._rng = rng or random.Random()

    def generate_events(
        self,
        duration_s: float = 1.5,
        *,
        viewport: Tuple[int, int] = (1920, 1080),
        target_points: int = 15,
    ) -> List[HumanEvent]:
        if duration_s <= 0:
            return []
        w, h = viewport
        pts = max(2, target_points)
        # Random anchor points
        anchors = [
            (self._rng.uniform(0.1, 0.9) * w, self._rng.uniform(0.1, 0.9) * h) for _ in range(pts)
        ]
        total_length = (
            sum(math.dist(anchors[i], anchors[i + 1]) for i in range(len(anchors) - 1)) or 1.0
        )
        # Convert path length segments to timing shares
        events: List[HumanEvent] = []
        remaining = duration_s
        last_x, last_y = anchors[0]
        # Initial move
        events.append(HumanEvent("move", last_x, last_y, delay=0.0))
        for (ax, ay), (bx, by) in zip(anchors, anchors[1:]):
            seg_len = math.dist((ax, ay), (bx, by))
            share = seg_len / total_length
            seg_time = share * duration_s
            steps = max(2, int(seg_len / 80))
            for s in range(1, steps + 1):
                t = s / steps
                # Ease in-out cubic
                tt = 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
                nx = ax + (bx - ax) * tt + self._rng.uniform(-1.5, 1.5)
                ny = ay + (by - ay) * tt + self._rng.uniform(-1.5, 1.5)
                delay = seg_time / steps
                remaining -= delay
                events.append(HumanEvent("move", nx, ny, delay=delay))
                last_x, last_y = nx, ny
            # Occasional scroll injection
            if self._rng.random() < 0.15:
                scroll_delta = self._rng.uniform(-200, 400)
                events.append(
                    HumanEvent(
                        "scroll",
                        last_x,
                        last_y,
                        delay=self._rng.uniform(0.02, 0.08),
                        meta={"dy": scroll_delta},
                    )
                )
        return events

    async def perform(
        self,
        page: Any,
        *,
        duration_s: float = 1.0,
        sleep: bool = False,
    ) -> int:
        """Execute generated events against a Playwright-like page.

        Returns number of events applied.
        Set sleep=True to honor delays (disabled in tests for speed).
        """
        events = self.generate_events(duration_s=duration_s)
        mouse = getattr(page, "mouse", None)
        move_fn = getattr(mouse, "move", None) if mouse else None
        wheel_fn = getattr(mouse, "wheel", None) if mouse else None
        moves = 0
        for ev in events:
            if sleep and ev.delay > 0:
                await asyncio.sleep(ev.delay)
            if ev.kind == "move" and move_fn:
                result = move_fn(ev.x, ev.y)  # type: ignore[arg-type]
                if inspect.isawaitable(result):
                    await result  # pragma: no cover - depends on async mouse impl
                moves += 1
            elif ev.kind == "scroll" and wheel_fn:
                dy = (ev.meta or {}).get("dy", 0)
                result = wheel_fn(0, dy)  # type: ignore[arg-type]
                if inspect.isawaitable(result):
                    await result  # pragma: no cover
        return moves


__all__ = ["HumanInteractionSimulator", "HumanEvent"]
