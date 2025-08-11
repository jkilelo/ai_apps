"""
Event bus implementation for UI Testing Framework v2
Handles async event publishing and subscribing
"""

import asyncio
import logging
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Core event types"""
    # Workflow events
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_STEP_COMPLETED = "workflow.step.completed"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    
    # Test execution events
    TEST_STARTED = "test.started"
    TEST_PASSED = "test.passed"
    TEST_FAILED = "test.failed"
    TEST_SKIPPED = "test.skipped"
    
    # Element extraction events
    EXTRACTION_STARTED = "extraction.started"
    EXTRACTION_COMPLETED = "extraction.completed"
    EXTRACTION_FAILED = "extraction.failed"
    
    # Reporting events
    REPORT_GENERATED = "report.generated"
    METRICS_UPDATED = "metrics.updated"


@dataclass
class Event:
    """Event data structure"""
    type: EventType
    timestamp: datetime
    data: Dict[str, Any]
    source: Optional[str] = None
    correlation_id: Optional[str] = None


class EventBus:
    """
    Async event bus for framework communication
    """
    
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._max_history = 1000
        self._lock = asyncio.Lock()
    
    async def subscribe(self, event_type: EventType, handler: Callable) -> None:
        """
        Subscribe to an event type
        
        Args:
            event_type: Type of event to subscribe to
            handler: Async callable to handle the event
        """
        async with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            
            if handler not in self._subscribers[event_type]:
                self._subscribers[event_type].append(handler)
                logger.debug(f"Handler {handler.__name__} subscribed to {event_type}")
    
    async def unsubscribe(self, event_type: EventType, handler: Callable) -> None:
        """
        Unsubscribe from an event type
        
        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler to remove
        """
        async with self._lock:
            if event_type in self._subscribers:
                if handler in self._subscribers[event_type]:
                    self._subscribers[event_type].remove(handler)
                    logger.debug(f"Handler {handler.__name__} unsubscribed from {event_type}")
    
    async def publish(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        source: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> None:
        """
        Publish an event to all subscribers
        
        Args:
            event_type: Type of event to publish
            data: Event data
            source: Source of the event
            correlation_id: Optional correlation ID for tracking
        """
        event = Event(
            type=event_type,
            timestamp=datetime.now(),
            data=data,
            source=source,
            correlation_id=correlation_id
        )
        
        # Store in history
        async with self._lock:
            self._event_history.append(event)
            
            # Trim history if needed
            if len(self._event_history) > self._max_history:
                self._event_history = self._event_history[-self._max_history:]
        
        # Get subscribers for this event type
        handlers = self._subscribers.get(event_type, [])
        
        # Call all handlers asynchronously
        if handlers:
            logger.debug(f"Publishing {event_type} to {len(handlers)} handlers")
            
            # Execute handlers concurrently
            tasks = []
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        tasks.append(handler(event))
                    else:
                        # Wrap sync handlers
                        tasks.append(asyncio.create_task(
                            asyncio.to_thread(handler, event)
                        ))
                except Exception as e:
                    logger.error(f"Error creating task for handler {handler.__name__}: {e}")
            
            # Wait for all handlers to complete
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Log any exceptions
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(
                            f"Handler {handlers[i].__name__} failed for {event_type}: {result}"
                        )
    
    async def publish_sync(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        source: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> List[Any]:
        """
        Publish an event and wait for all handlers to complete
        Returns results from all handlers
        
        Args:
            event_type: Type of event to publish
            data: Event data
            source: Source of the event
            correlation_id: Optional correlation ID for tracking
            
        Returns:
            List of results from handlers
        """
        event = Event(
            type=event_type,
            timestamp=datetime.now(),
            data=data,
            source=source,
            correlation_id=correlation_id
        )
        
        # Store in history
        async with self._lock:
            self._event_history.append(event)
            
            # Trim history if needed
            if len(self._event_history) > self._max_history:
                self._event_history = self._event_history[-self._max_history:]
        
        # Get subscribers for this event type
        handlers = self._subscribers.get(event_type, [])
        
        if not handlers:
            return []
        
        logger.debug(f"Publishing {event_type} synchronously to {len(handlers)} handlers")
        
        # Execute handlers and collect results
        results = []
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(event)
                else:
                    result = await asyncio.to_thread(handler, event)
                results.append(result)
            except Exception as e:
                logger.error(f"Handler {handler.__name__} failed for {event_type}: {e}")
                results.append(e)
        
        return results
    
    def get_history(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 100
    ) -> List[Event]:
        """
        Get event history
        
        Args:
            event_type: Optional filter by event type
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        history = self._event_history
        
        if event_type:
            history = [e for e in history if e.type == event_type]
        
        return history[-limit:]
    
    def clear_history(self) -> None:
        """Clear event history"""
        self._event_history.clear()
    
    async def reset(self) -> None:
        """Reset the event bus"""
        async with self._lock:
            self._subscribers.clear()
            self._event_history.clear()
            logger.info("Event bus reset")


# Global event bus instance
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get or create the global event bus instance"""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


async def reset_event_bus() -> None:
    """Reset the global event bus"""
    global _event_bus
    if _event_bus:
        await _event_bus.reset()
    _event_bus = None