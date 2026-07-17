import logging
import asyncio
from typing import Callable, Dict, List, Any

logger = logging.getLogger("JarvisEventBus")

class EventBus:
    def __init__(self):
        # Maps event topics to registered callback execution hooks
        self._listeners: Dict[str, List[Callable[[Any], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """Registers a listener module to a specific event topic securely."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        if callback not in self._listeners[event_type]:
            self._listeners[event_type].append(callback)
            logger.info(f"Module successfully subscribed to event topic: {event_type}")

    def emit(self, event_type: str, data: Any = None) -> None:
        """Broadcasts payload securely across all registered listener arrays."""
        if event_type not in self._listeners:
            return

        for callback in self._listeners[event_type]:
            try:
                # Execute isolation logic so a failing subscriber doesn't drop the pipeline
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(data))
                else:
                    callback(data)
            except Exception as eval_err:
                logger.error(f"Subscriber handling event '{event_type}' raised an exception: {eval_err}")
