"""Detection mitigation strategy adjusting risk & suggested stealth score."""

from __future__ import annotations
from .base import Strategy, StrategyContext


class DetectionMitigationStrategy:
    name = "detection_mitigation"

    async def evaluate(self, ctx: StrategyContext) -> StrategyContext:
        # If detection risk is high, raise stealth score aggressively
        if ctx.detection_risk > 0.7:
            ctx.stealth_score = min(1.0, ctx.stealth_score + 0.2)
        return ctx
