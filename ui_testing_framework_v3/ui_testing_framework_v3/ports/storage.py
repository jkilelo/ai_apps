"""Port for storage/persistence."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class IStorage(Protocol):
    async def save(self, key: str, data: Any) -> bool:
        """Save data for a key."""

    async def load(self, key: str) -> Any | None:
        """Load data by key or None if missing."""

    async def delete(self, key: str) -> bool:
        """Delete data by key."""

    async def exists(self, key: str) -> bool:
        """Return True if a key exists."""
