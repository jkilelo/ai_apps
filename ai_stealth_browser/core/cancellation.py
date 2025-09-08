"""Simple cancellation token for cooperative async aborts."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import asyncio


@dataclass
class CancellationToken:
    _event: asyncio.Event = field(default_factory=asyncio.Event)
    reason: Optional[str] = None

    def cancel(self, reason: str = "cancelled") -> None:
        if not self._event.is_set():
            self.reason = reason
            self._event.set()

    def is_cancelled(self) -> bool:
        return self._event.is_set()

    async def wait(self) -> None:
        await self._event.wait()


__all__ = ["CancellationToken"]
