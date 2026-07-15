# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import typing
import threading

from ._exceptions import WebSocketQueueFullError


class SendQueue:
    """Bounded byte-size queue for outgoing WebSocket messages.

    Messages are stored as pre-serialized strings. The queue enforces a
    maximum byte budget so that unbounded buffering cannot occur during
    reconnection windows.
    """

    def __init__(self, max_bytes: int = 1_048_576) -> None:
        self._queue: list[tuple[str, int]] = []  # (data, byte_length)
        self._bytes: int = 0
        self._max_bytes = max_bytes
        self._lock = threading.Lock()

    def enqueue(self, data: str) -> None:
        """Append *data* to the queue.

        Raises :class:`WebSocketQueueFullError` if the message would
        exceed the byte-size limit.
        """
        byte_length = len(data.encode("utf-8"))
        with self._lock:
            if self._bytes + byte_length > self._max_bytes:
                raise WebSocketQueueFullError("send queue is full, message discarded")
            self._queue.append((data, byte_length))
            self._bytes += byte_length

    def flush_sync(self, send: typing.Callable[[str], object]) -> None:
        """Send every queued message via *send*.

        If *send* raises, the failing message and all subsequent messages
        are re-queued and the error is re-raised.
        """
        with self._lock:
            pending = list(self._queue)
            self._queue.clear()
            self._bytes = 0

        for i, (data, _byte_length) in enumerate(pending):
            try:
                send(data)
            except Exception:
                with self._lock:
                    remaining = pending[i:]
                    self._queue = remaining + self._queue
                    self._bytes = sum(bl for _, bl in self._queue)
                raise

    async def flush_async(self, send: typing.Callable[[str], typing.Awaitable[object]]) -> None:
        """Async variant of :meth:`flush_sync`."""
        with self._lock:
            pending = list(self._queue)
            self._queue.clear()
            self._bytes = 0

        for i, (data, _byte_length) in enumerate(pending):
            try:
                await send(data)
            except Exception:
                with self._lock:
                    remaining = pending[i:]
                    self._queue = remaining + self._queue
                    self._bytes = sum(bl for _, bl in self._queue)
                raise

    def drain(self) -> list[str]:
        """Remove and return all queued messages."""
        with self._lock:
            items = [data for data, _ in self._queue]
            self._queue.clear()
            self._bytes = 0
            return items

    def __len__(self) -> int:
        with self._lock:
            return len(self._queue)

    def __bool__(self) -> bool:
        with self._lock:
            return len(self._queue) > 0
