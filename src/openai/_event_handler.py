# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import threading
from typing import Any, Callable

EventHandler = Callable[..., Any]


class EventHandlerRegistry:
    """Thread-safe (optional) registry of event handlers."""

    def __init__(self, *, use_lock: bool = False) -> None:
        self._handlers: dict[str, list[EventHandler]] = {}
        self._once_ids: set[int] = set()
        self._lock: threading.Lock | None = threading.Lock() if use_lock else None

    def _acquire(self) -> None:
        if self._lock is not None:
            self._lock.acquire()

    def _release(self) -> None:
        if self._lock is not None:
            self._lock.release()

    def add(self, event_type: str, handler: EventHandler, *, once: bool = False) -> None:
        self._acquire()
        try:
            handlers = self._handlers.setdefault(event_type, [])
            handlers.append(handler)
            if once:
                self._once_ids.add(id(handler))
        finally:
            self._release()

    def remove(self, event_type: str, handler: EventHandler) -> None:
        self._acquire()
        try:
            handlers = self._handlers.get(event_type)
            if handlers is not None:
                try:
                    handlers.remove(handler)
                except ValueError:
                    pass
                self._once_ids.discard(id(handler))
        finally:
            self._release()

    def get_handlers(self, event_type: str) -> list[EventHandler]:
        """Return a snapshot of handlers for the given event type, removing once-handlers."""
        self._acquire()
        try:
            handlers = self._handlers.get(event_type)
            if not handlers:
                return []
            result = list(handlers)
            to_remove = [h for h in result if id(h) in self._once_ids]
            for h in to_remove:
                handlers.remove(h)
                self._once_ids.discard(id(h))
            return result
        finally:
            self._release()

    def has_handlers(self, event_type: str) -> bool:
        self._acquire()
        try:
            handlers = self._handlers.get(event_type)
            return bool(handlers)
        finally:
            self._release()

    def merge_into(self, target: EventHandlerRegistry) -> None:
        """Move all handlers from this registry into *target*, then clear self."""
        self._acquire()
        try:
            for event_type, handlers in self._handlers.items():
                for handler in handlers:
                    once = id(handler) in self._once_ids
                    target.add(event_type, handler, once=once)
            self._handlers.clear()
            self._once_ids.clear()
        finally:
            self._release()
