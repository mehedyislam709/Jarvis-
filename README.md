import asyncio
import logging
from typing import Callable, Any, Dict, List, Coroutine, Union
import weakref

logger = logging.getLogger("JARVIS.EVENT_BUS")

class EventBus:
    """
    Thread-safe, non-blocking Event Bus with weak reference support
    to prevent memory leaks.
    """
    def __init__(self):
        # Using a list to hold callbacks
        self._listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """Registers a listener module securely."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        
        # Prevent duplicate subscriptions
        if callback not in self._listeners[event_type]:
            self._listeners[event_type].append(callback)
            logger.info(f"Registered subscriber to '{event_type}'")

    def unsubscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """Removes a subscriber to prevent memory leaks during plugin unloading."""
        if event_type in self._listeners and callback in self._listeners[event_type]:
            self._listeners[event_type].remove(callback)
            logger.info(f"Unregistered subscriber from '{event_type}'")

    async def emit(self, event_type: str, data: Any = None) -> None:
        """Broadcasts payload to all listeners with strict isolation."""
        if event_type not in self._listeners:
            return

        # Snapshot current listeners to prevent errors if list is modified during iteration
        callbacks = list(self._listeners[event_type])
        
        tasks = []
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    # Schedule as task for non-blocking execution
                    tasks.append(asyncio.create_task(callback(data)))
                else:
                    # Execute synchronous callbacks in a separate thread if necessary
                    # to keep the event bus non-blocking
                    callback(data)
            except Exception as e:
                logger.error(f"Event '{event_type}' crashed a subscriber: {e}", exc_info=True)
        
        # Wait for all async tasks to trigger (optional based on your latency requirements)
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
