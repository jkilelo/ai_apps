"""
Event-driven communication between components
Zero external dependencies - pure Python implementation
"""

from __future__ import annotations

import contextlib
import secrets
from collections import defaultdict
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

# Constants
MAX_HISTORY_SIZE = 1000
HISTORY_TRIM_SIZE = 500


class EventBus:
    """
    Lightweight event bus for decoupled communication

    Features:
    - Publish/subscribe pattern
    - Event middleware
    - Event history
    - Type-safe events
    """

    def __init__(self) -> None:
        """Initialize event bus"""
        self._handlers: dict[str, list[Callable[..., None]]] = defaultdict(list)
        self._middleware: list[Callable[[str, Any], Any]] = []
        self._history: list[dict[str, Any]] = []

    def on(self, event_type: str) -> Callable[[Callable[..., None]], Callable[..., None]]:
        """
        Decorator to register event handler

        Usage:
            @event_bus.on('extraction.complete')
            def handle_extraction(data):
                print(f"Extracted {data['count']} elements")
        """

        def decorator(handler: Callable[..., None]) -> Callable[..., None]:
            self._handlers[event_type].append(handler)
            return handler

        return decorator

    def emit(self, event_type: str, data: Any = None) -> str:
        """
        Emit an event

        Args:
            event_type: Event type
            data: Event data

        Returns:
            Event ID for tracking
        """
        # Generate event ID
        event_id = secrets.token_hex(8)

        # Create event record
        event: dict[str, Any] = {
            "id": event_id,
            "type": event_type,
            "data": data,
            "timestamp": datetime.now(tz=UTC).isoformat(),
        }

        # Apply middleware
        processed_data = data
        for middleware in self._middleware:
            processed_data = middleware(event_type, processed_data)

        # Store in history
        self._history.append(event)

        # Limit history size
        if len(self._history) > MAX_HISTORY_SIZE:
            self._history = self._history[-HISTORY_TRIM_SIZE:]  # Keep last 500

        # Call handlers
        for handler in self._handlers[event_type]:
            try:
                handler(processed_data, event_id=event_id)
            except Exception as e:
                print(f"Event handler error: {e}")

        return event_id

    def use(self, middleware: Callable[[str, Any], Any]) -> None:
        """Add middleware for all events"""
        self._middleware.append(middleware)

    def get_history(self, event_type: str | None = None) -> list[dict[str, Any]]:
        """Get event history"""
        if event_type:
            return [e for e in self._history if e["type"] == event_type]
        return self._history.copy()

    def clear_history(self) -> None:
        """Clear event history"""
        self._history.clear()

    def remove_handler(self, event_type: str, handler: Callable[..., None]) -> None:
        """Remove a specific handler"""
        if event_type in self._handlers:
            with contextlib.suppress(ValueError):
                self._handlers[event_type].remove(handler)


# Global event bus
event_bus = EventBus()
