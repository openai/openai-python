from __future__ import annotations

import threading
from typing import Any, Callable
from dataclasses import dataclass

EventHandler = Callable[..., Any]


@dataclass(eq=False)
class _Registration:
    handler: EventHandler
    once: bool


class EventHandlerRegistry:
    """Thread-safe (optional) registry of event handlers."""

    def __init__(self, *, use_lock: bool = False) -> None:
        self._handlers: dict[str, list[_Registration]] = {}
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
            handlers.append(_Registration(handler, once))
        finally:
            self._release()

    def remove(self, event_type: str, handler: EventHandler) -> None:
        self._acquire()
        try:
            handlers = self._handlers.get(event_type)
            if handlers is not None:
                for index, registration in enumerate(handlers):
                    if registration.handler == handler:
                        del handlers[index]
                        break
        finally:
            self._release()

    def get_handlers(self, event_type: str) -> list[EventHandler]:
        """Return a snapshot of handlers for the given event type, removing once-handlers."""
        self._acquire()
        try:
            handlers = self._handlers.get(event_type)
            if not handlers:
                return []
            self._handlers[event_type] = [registration for registration in handlers if not registration.once]
            return [registration.handler for registration in handlers]
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
                for registration in handlers:
                    target.add(event_type, registration.handler, once=registration.once)
            self._handlers.clear()
        finally:
            self._release()
