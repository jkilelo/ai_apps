"""Human simulation strategy adjusting stealth score based on interaction realism."""

from __future__ import annotations
from .base import Strategy, StrategyContext


class HumanSimulationStrategy:
    name = "human_simulation"

    async def evaluate(self, ctx: StrategyContext) -> StrategyContext:
        # Simple heuristic: if detection risk present, increase need for human realism
        if ctx.detection_risk > 0.3:
            ctx.stealth_score = min(1.0, ctx.stealth_score + 0.1)
        return ctx
