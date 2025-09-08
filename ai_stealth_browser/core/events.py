"""Simple EventBus (Observer pattern) for agent and system events."""

from __future__ import annotations
from typing import Callable, Dict, List, Any, DefaultDict
from collections import defaultdict

EventHandler = Callable[[Dict[str, Any]], None]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: DefaultDict[str, List[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._subscribers[event_type].append(handler)

    def publish(self, event_type: str, payload: Dict[str, Any]) -> None:
        for handler in list(self._subscribers.get(event_type, [])):
            try:
                handler(payload)
            except Exception as e:  # pragma: no cover
                # Log placeholder - integrate structured logger later
                print(f"Event handler error for {event_type}: {e}")


__all__ = ["EventBus"]
