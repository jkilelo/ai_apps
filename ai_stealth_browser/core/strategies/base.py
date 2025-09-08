"""Base Strategy abstractions."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class StrategyContext:
    stealth_score: float = 0.5
    detection_risk: float = 0.0
    metadata: dict[str, Any] | None = None


class Strategy(Protocol):  # structural typing
    name: str

    async def evaluate(
        self, ctx: StrategyContext
    ) -> StrategyContext:  # pragma: no cover (interface)
        ...
