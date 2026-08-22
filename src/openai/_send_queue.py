from __future__ import annotations

import typing
import threading
from collections import deque

import anyio.to_thread

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
        self._flush_done: threading.Event | None = None

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
        while isinstance(pending := self._begin_flush(), threading.Event):
            pending.wait()

        try:
            while pending:
                data, byte_length = pending[0]
                send(data)
                with self._lock:
                    pending.popleft()
                    self._bytes -= byte_length
        finally:
            self._end_flush(pending)

    async def flush_async(self, send: typing.Callable[[str], typing.Awaitable[object]]) -> None:
        """Async variant of :meth:`flush_sync`."""
        while isinstance(pending := self._begin_flush(), threading.Event):
            # Waiting in a worker keeps the event loop responsive. Cancellation
            # cannot strand ownership: the worker only waits, never acquires it.
            await anyio.to_thread.run_sync(pending.wait, abandon_on_cancel=True)

        try:
            while pending:
                data, byte_length = pending[0]
                await send(data)
                with self._lock:
                    pending.popleft()
                    self._bytes -= byte_length
        finally:
            self._end_flush(pending)

    def _begin_flush(self) -> deque[tuple[str, int]] | threading.Event:
        with self._lock:
            if self._flush_done is not None:
                return self._flush_done
            pending = deque(self._queue)
            self._queue.clear()
            self._flush_done = threading.Event()
            # Pending messages remain charged until their sends succeed.
            return pending

    def _end_flush(self, pending: deque[tuple[str, int]]) -> None:
        with self._lock:
            self._queue = list(pending) + self._queue
            assert self._flush_done is not None
            self._flush_done.set()
            self._flush_done = None

    def drain(self) -> list[str]:
        """Remove and return all queued messages."""
        with self._lock:
            items = [data for data, _ in self._queue]
            self._bytes -= sum(byte_length for _, byte_length in self._queue)
            self._queue.clear()
            return items

    def __len__(self) -> int:
        with self._lock:
            return len(self._queue)

    def __bool__(self) -> bool:
        with self._lock:
            return len(self._queue) > 0
