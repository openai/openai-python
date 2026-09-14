from __future__ import annotations

import threading
from typing import Any, Generic, TypeVar, Callable, overload
from dataclasses import dataclass
from typing_extensions import Self, Literal

from ._types import GroupingUpdate, TranscriptSegment, TranscriptSegmentClosedEvent

_ReturnT = TypeVar("_ReturnT")
_EventName = Literal["segment.updated", "segment.closed"]


@dataclass(eq=False)
class _Registration(Generic[_ReturnT]):
    handler: Callable[..., _ReturnT]
    once: bool


class TranscriptListeners(Generic[_ReturnT]):
    """Typed, session-local callbacks; listener registration never holds the state lock."""

    def __init__(self) -> None:
        self._listeners: dict[str, list[_Registration[_ReturnT]]] = {}
        self._listeners_lock = threading.Lock()

    @overload
    def on(self, event_type: Literal["segment.updated"], handler: Callable[[TranscriptSegment], _ReturnT]) -> Self: ...

    @overload
    def on(
        self, event_type: Literal["segment.closed"], handler: Callable[[TranscriptSegmentClosedEvent], _ReturnT]
    ) -> Self: ...

    @overload
    def on(
        self, event_type: Literal["segment.updated"]
    ) -> Callable[[Callable[[TranscriptSegment], _ReturnT]], Callable[[TranscriptSegment], _ReturnT]]: ...

    @overload
    def on(
        self, event_type: Literal["segment.closed"]
    ) -> Callable[
        [Callable[[TranscriptSegmentClosedEvent], _ReturnT]], Callable[[TranscriptSegmentClosedEvent], _ReturnT]
    ]: ...

    def on(self, event_type: _EventName, handler: Callable[..., _ReturnT] | None = None) -> Any:
        """Register a callback, or use as a decorator. Return self when given a handler."""
        return self._register(event_type, handler, once=False)

    @overload
    def once(
        self, event_type: Literal["segment.updated"], handler: Callable[[TranscriptSegment], _ReturnT]
    ) -> Self: ...

    @overload
    def once(
        self, event_type: Literal["segment.closed"], handler: Callable[[TranscriptSegmentClosedEvent], _ReturnT]
    ) -> Self: ...

    @overload
    def once(
        self, event_type: Literal["segment.updated"]
    ) -> Callable[[Callable[[TranscriptSegment], _ReturnT]], Callable[[TranscriptSegment], _ReturnT]]: ...

    @overload
    def once(
        self, event_type: Literal["segment.closed"]
    ) -> Callable[
        [Callable[[TranscriptSegmentClosedEvent], _ReturnT]], Callable[[TranscriptSegmentClosedEvent], _ReturnT]
    ]: ...

    def once(self, event_type: _EventName, handler: Callable[..., _ReturnT] | None = None) -> Any:
        """Register a callback for the next event only, optionally as a decorator."""
        return self._register(event_type, handler, once=True)

    def _register(self, event_type: _EventName, handler: Callable[..., _ReturnT] | None, *, once: bool) -> Any:
        def register(fn: Callable[..., _ReturnT]) -> Callable[..., _ReturnT]:
            with self._listeners_lock:
                self._listeners.setdefault(event_type, []).append(_Registration(fn, once))
            return fn

        if handler is None:
            return register
        register(handler)
        return self

    def off(self, event_type: _EventName, handler: Callable[..., _ReturnT]) -> Self:
        """Remove the first matching registration, if present."""
        with self._listeners_lock:
            listeners = self._listeners.get(event_type, [])
            for index, registration in enumerate(listeners):
                if registration.handler == handler:
                    del listeners[index]
                    break
        return self

    def _handlers(self, update: GroupingUpdate) -> list[Callable[..., _ReturnT]]:
        event_type = "segment.updated" if isinstance(update, TranscriptSegment) else "segment.closed"
        with self._listeners_lock:
            listeners = self._listeners.get(event_type, [])
            self._listeners[event_type] = [registration for registration in listeners if not registration.once]
            return [registration.handler for registration in listeners]
