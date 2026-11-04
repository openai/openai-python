from __future__ import annotations

import typing
import threading
from collections import deque

import anyio.to_thread

from ._exceptions import WebSocketQueueFullError, WebSocketConnectionClosedError


class SendReceipt:
    """An admitted ordinary sender's own failure, if another caller sends it."""

    def __init__(self) -> None:
        self.error: BaseException | None = None
        self.unsent: list[str | bytes] | None = None

    def raise_if_failed(self) -> None:
        if self.error is not None:
            raise self.error

    def raise_if_unsent(self) -> None:
        if self.unsent is not None:
            # Construct outside the queue lock: decoding binary frames can
            # invoke user code, and terminal reporting must not block a flush.
            raise WebSocketConnectionClosedError(
                "WebSocket connection closed with unsent messages", unsent_messages=self.unsent
            )


class SendQueue:
    """Bounded byte-size queue for outgoing WebSocket messages.

    Messages retain their text or binary frame type. The queue enforces a
    maximum byte budget so that unbounded buffering cannot occur during
    reconnection windows.
    """

    def __init__(self, max_bytes: int = 1_048_576) -> None:
        self._queue: list[tuple[str | bytes, int, SendReceipt | None]] = []  # (data, byte_length, receipt)
        self._bytes: int = 0
        self._max_bytes = max_bytes
        self._lock = threading.Lock()
        self._flush_done: threading.Event | None = None
        # drain() ends admission to this batch while an in-flight write may
        # still hold _flush_done until it unwinds and releases ownership.
        self._pending: deque[tuple[str | bytes, int, SendReceipt | None]] | None = None
        self._flush_owner: tuple[threading.Thread, int | None] | None = None

    @property
    def has_pending_or_flushing(self) -> bool:
        with self._lock:
            return bool(self._queue) or self._pending is not None

    def is_flush_owner(self, *, task_id: int | None = None) -> bool:
        """Whether this caller already owns the flush and must not wait on itself."""
        with self._lock:
            return self._flush_owner == (threading.current_thread(), task_id)

    def enqueue(self, data: str | bytes, *, only_if_pending: bool = False, receipt: SendReceipt | None = None) -> bool:
        """Append *data* to the queue.

        Raises :class:`WebSocketQueueFullError` if the message would
        exceed the byte-size limit.

        If only_if_pending is true, return False instead of admitting a
        message when there is no buffered or active batch; otherwise return True.
        """
        # Avoid a redundant encoding on direct sends. Recheck below in case
        # the queue drains during encoding, which must stay outside its lock.
        if only_if_pending and not self.has_pending_or_flushing:
            return False
        byte_length = len(data.encode("utf-8") if isinstance(data, str) else data)
        with self._lock:
            if only_if_pending and not self._queue and self._pending is None:
                return False
            if self._bytes + byte_length > self._max_bytes:
                raise WebSocketQueueFullError("send queue is full, message discarded")
            self._queue.append((data, byte_length, receipt))
            self._bytes += byte_length
            return True

    def flush_sync(
        self,
        send: typing.Callable[[str | bytes], object],
        *,
        requeue_failed: bool = True,
        prepare_send: typing.Callable[[], typing.Callable[[str | bytes], object] | None] | None = None,
    ) -> None:
        """Send every queued message via *send*.

        If *send* raises, the failing message and all subsequent messages
        are re-queued and the error is re-raised. When `requeue_failed` is
        false, release the attempted message even on failure or interruption.
        """
        while isinstance(pending := self._begin_flush(), threading.Event):
            pending.wait()

        try:
            with self._lock:
                self._flush_owner = (threading.current_thread(), None)
            while True:
                if prepare_send is not None:
                    # Check ownership outside the queue lock before each frame;
                    # the connection may have changed while the last send ran.
                    with self._lock:
                        if not pending:
                            break
                    prepared = prepare_send()
                    if prepared is None:
                        return
                    send = prepared
                with self._lock:
                    # drain() can run while preparation checks the connection.
                    if not pending:
                        break
                    data, byte_length, receipt = pending.popleft()
                sent = False
                try:
                    send(data)
                    sent = True
                except BaseException as exc:
                    if receipt is not None:
                        # The actual frame's caller may be waiting on this
                        # batch; retain its own error before releasing the lease.
                        receipt.error = exc
                    raise
                finally:
                    with self._lock:
                        if sent or not requeue_failed:
                            self._bytes -= byte_length
                        else:
                            pending.appendleft((data, byte_length, receipt))
        finally:
            self._end_flush(pending)

    async def flush_async(
        self,
        send: typing.Callable[[str | bytes], typing.Awaitable[object]],
        *,
        requeue_failed: bool = True,
        prepare_send: typing.Callable[[], typing.Callable[[str | bytes], typing.Awaitable[object]] | None]
        | None = None,
    ) -> None:
        """Async variant of :meth:`flush_sync`."""
        while isinstance(pending := self._begin_flush(), threading.Event):
            # Waiting in a worker keeps the event loop responsive. Cancellation
            # cannot strand ownership: the worker only waits, never acquires it.
            await anyio.to_thread.run_sync(pending.wait, abandon_on_cancel=True)

        try:
            with self._lock:
                self._flush_owner = (threading.current_thread(), anyio.get_current_task().id)
            while True:
                if prepare_send is not None:
                    # Check ownership outside the queue lock before each frame;
                    # the connection may have changed while the last send ran.
                    with self._lock:
                        if not pending:
                            break
                    prepared = prepare_send()
                    if prepared is None:
                        return
                    send = prepared
                with self._lock:
                    # drain() can run while preparation checks the connection.
                    if not pending:
                        break
                    data, byte_length, receipt = pending.popleft()
                sent = False
                try:
                    await send(data)
                    sent = True
                except BaseException as exc:
                    if receipt is not None:
                        # The actual frame's caller may be waiting on this
                        # batch; retain its own error before releasing the lease.
                        receipt.error = exc
                    raise
                finally:
                    with self._lock:
                        if sent or not requeue_failed:
                            self._bytes -= byte_length
                        else:
                            pending.appendleft((data, byte_length, receipt))
        finally:
            self._end_flush(pending)

    def _begin_flush(self) -> deque[tuple[str | bytes, int, SendReceipt | None]] | threading.Event:
        with self._lock:
            if self._flush_done is not None:
                return self._flush_done
            pending = deque(self._queue)
            self._queue.clear()
            self._flush_done = threading.Event()
            self._pending = pending
            # Messages remain charged while their sends are in flight.
            return pending

    def _end_flush(self, pending: deque[tuple[str | bytes, int, SendReceipt | None]]) -> None:
        with self._lock:
            self._queue = list(pending) + self._queue
            assert self._flush_done is not None
            self._flush_done.set()
            self._flush_done = None
            self._pending = None
            self._flush_owner = None

    def drain(self) -> list[str | bytes]:
        """Remove and return all queued messages."""
        return self.mark_unsent(clear=True)

    def mark_unsent(self, *, clear: bool = False) -> list[str | bytes]:
        """Report retained ordinary frames. A later reader can still drain them after close()."""
        with self._lock:
            pending = list(self._pending) if self._pending is not None else []
            pending.extend(self._queue)
            items = [data for data, _, _ in pending]
            for _, _, receipt in pending:
                if receipt is not None:
                    receipt.unsent = items
            if self._pending is not None:
                if not clear:
                    # An old prepare_send may already have returned. Evacuate
                    # this batch before its next pop but retain it for a reader.
                    self._queue[:0] = self._pending
                self._pending.clear()
                self._pending = None
            if clear:
                self._bytes -= sum(byte_length for _, byte_length, _ in pending)
                self._queue.clear()
            return items

    def __len__(self) -> int:
        with self._lock:
            return len(self._queue)

    def __bool__(self) -> bool:
        with self._lock:
            return len(self._queue) > 0
