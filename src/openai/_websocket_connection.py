from __future__ import annotations

import time
import random
import logging
import threading
import contextlib
from typing import TYPE_CHECKING, Callable, Awaitable

import anyio

from ._types import Query, Headers
from ._send_queue import SendQueue, SendReceipt
from .types.websocket_reconnection import ReconnectingEvent, ReconnectingOverrides, is_recoverable_close

if TYPE_CHECKING:
    from websockets.sync.client import ClientConnection as WebSocketConnection
    from websockets.asyncio.client import ClientConnection as AsyncWebSocketConnection


class WebSocketConnectionBase:
    def __init__(
        self,
        connection: WebSocketConnection,
        *,
        make_ws: Callable[[Query, Headers], WebSocketConnection] | None = None,
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        extra_query: Query = {},
        extra_headers: Headers = {},
        send_queue: SendQueue | None = None,
        logger: logging.Logger,
        interruptible_reconnect: bool = True,
    ) -> None:
        self._connection = connection
        self._make_ws = make_ws
        self._on_reconnecting = on_reconnecting
        self._max_retries = max_retries
        self._reconnect_attempt = 0
        self._initial_delay = initial_delay
        self._max_delay = max_delay
        self._extra_query = extra_query
        self._extra_headers = extra_headers
        self._intentionally_closed = False
        self._is_reconnecting = False
        self._send_queue = send_queue if send_queue is not None else SendQueue()
        self._logger = logger
        self._interruptible_reconnect = interruptible_reconnect
        self._connection_lock = threading.Lock()
        if interruptible_reconnect:
            self._close_event = threading.Event()

    def send_raw(self, data: bytes | str) -> None:
        self._send(data)

    def _send(self, data: bytes | str) -> None:
        # Admission and the empty-queue transition share this lock. Never keep
        # it across transport I/O: close must be able to interrupt a slow send.
        flush_backlog = False
        admitted = False
        receipt = SendReceipt()
        try:
            with self._connection_lock:
                if not self._intentionally_closed:
                    if self._is_reconnecting:
                        self._send_queue.enqueue(data)
                        return
                    try:
                        admitted = self._send_queue.enqueue(data, only_if_pending=True, receipt=receipt)
                    finally:
                        # Do not wait on an active flush: send() can be reentrant.
                        flush_backlog = not self._send_queue.is_flush_owner() and bool(self._send_queue)
                    if admitted:
                        return
                connection = self._connection
        finally:
            if flush_backlog:
                # Rejected admissions still allow the older backlog to progress.
                try:
                    self._flush_send_queue(raise_on_error=admitted)
                except BaseException:
                    receipt.raise_if_failed()
                    raise
                receipt.raise_if_failed()
                receipt.raise_if_unsent()
        connection.send(data)

    def close(self, *, code: int = 1000, reason: str = "") -> None:
        if self._interruptible_reconnect:
            self._close_event.set()
        with self._connection_lock:
            self._intentionally_closed = True
            self._is_reconnecting = False
            self._send_queue.mark_unsent()
            connection = self._connection
        connection.close(code=code, reason=reason)

    def _reconnect(self, exc: Exception) -> bool:
        """Attempt to reconnect after a connection failure.

        Returns ``True`` if a new connection was established, ``False`` if the
        caller should re-raise the original exception.
        """
        if self._on_reconnecting is None or self._make_ws is None or self._intentionally_closed:
            return False

        from websockets.exceptions import ConnectionClosed

        close_code = 1006
        if isinstance(exc, ConnectionClosed) and exc.rcvd is not None:
            close_code = exc.rcvd.code

        if not is_recoverable_close(close_code):
            return False

        with self._connection_lock:
            if self._intentionally_closed:
                return False
            self._is_reconnecting = True

        try:
            for attempt in range(self._reconnect_attempt + 1, self._max_retries + 1):
                if self._intentionally_closed:
                    return False
                self._reconnect_attempt = attempt
                base_delay = min(self._initial_delay * (2 ** (attempt - 1)), self._max_delay)
                jitter = 0.75 + random.random() * 0.25
                delay = base_delay * jitter

                event = ReconnectingEvent(
                    attempt=attempt,
                    max_attempts=self._max_retries,
                    delay=delay,
                    close_code=close_code,
                    extra_query=self._extra_query,
                    extra_headers=self._extra_headers,
                )

                try:
                    result = self._on_reconnecting(event)
                except Exception:
                    return False

                if result is not None and result.get("abort"):
                    return False

                if result is not None:
                    if "extra_query" in result:
                        self._extra_query = result["extra_query"]
                    if "extra_headers" in result:
                        self._extra_headers = result["extra_headers"]

                self._logger.info(
                    "Reconnecting to WebSocket API (attempt %d/%d) after %.1fs delay",
                    attempt,
                    self._max_retries,
                    delay,
                )
                if self._interruptible_reconnect:
                    closed = self._close_event.wait(delay)
                else:
                    time.sleep(delay)
                    closed = self._intentionally_closed
                if closed:
                    return False

                try:
                    connection = self._make_ws(self._extra_query, self._extra_headers)
                    with self._connection_lock:
                        closed = self._intentionally_closed
                        if not closed:
                            self._connection = connection
                    if closed:
                        connection.close()
                        return False
                    try:
                        self._flush_send_queue(raise_on_error=True, finish_recovery=True)
                    except Exception as flush_exc:
                        with contextlib.suppress(Exception):
                            connection.close()
                        if isinstance(flush_exc, ConnectionClosed):
                            close_code = flush_exc.rcvd.code if flush_exc.rcvd is not None else 1006
                            if not is_recoverable_close(close_code):
                                return False
                        raise
                    if self._intentionally_closed:
                        return False
                    self._logger.info("Reconnected to WebSocket API")
                    return True
                except Exception:
                    # Ordinary setup failures consume an attempt. The outer
                    # finally ends queue admission when recovery exits.
                    pass

            return False
        finally:
            with self._connection_lock:
                self._is_reconnecting = False

    def _flush_send_queue(self, *, raise_on_error: bool = False, finish_recovery: bool = False) -> None:
        """Send all queued messages over the current connection."""

        def prepare_send() -> Callable[[str | bytes], object] | None:
            with self._connection_lock:
                if self._intentionally_closed or (not finish_recovery and self._is_reconnecting):
                    return None
                return self._connection.send

        try:
            while True:
                with self._connection_lock:
                    # An ordinary flush must hand new batches to the reader
                    # once recovery owns admission and transport replacement.
                    if not finish_recovery and self._is_reconnecting:
                        return
                    if self._intentionally_closed or not self._send_queue.has_pending_or_flushing:
                        if finish_recovery:
                            self._is_reconnecting = False
                        return
                    connection = self._connection
                self._send_queue.flush_sync(connection.send, requeue_failed=False, prepare_send=prepare_send)
        except Exception:
            self._logger.warning("Failed to flush send queue after reconnect")
            # Managers also flush messages queued before the initial connection.
            # Preserve that path's behavior; only recovery owns retry policy.
            if raise_on_error:
                raise


class AsyncWebSocketConnectionBase:
    def __init__(
        self,
        connection: AsyncWebSocketConnection,
        *,
        make_ws: Callable[[Query, Headers], Awaitable[AsyncWebSocketConnection]] | None = None,
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        extra_query: Query = {},
        extra_headers: Headers = {},
        send_queue: SendQueue | None = None,
        logger: logging.Logger,
    ) -> None:
        self._connection = connection
        self._make_ws = make_ws
        self._on_reconnecting = on_reconnecting
        self._max_retries = max_retries
        self._reconnect_attempt = 0
        self._initial_delay = initial_delay
        self._max_delay = max_delay
        self._extra_query = extra_query
        self._extra_headers = extra_headers
        self._intentionally_closed = False
        self._is_reconnecting = False
        self._send_queue = send_queue if send_queue is not None else SendQueue()
        self._logger = logger

    async def send_raw(self, data: bytes | str) -> None:
        await self._send(data)

    async def _send(self, data: bytes | str) -> None:
        flush_backlog = False
        admitted = False
        receipt = SendReceipt()
        try:
            if not self._intentionally_closed:
                if self._is_reconnecting:
                    self._send_queue.enqueue(data)
                    return
                try:
                    admitted = self._send_queue.enqueue(data, only_if_pending=True, receipt=receipt)
                finally:
                    flush_backlog = not self._send_queue.is_flush_owner(task_id=anyio.get_current_task().id) and bool(
                        self._send_queue
                    )
                if admitted:
                    return
        finally:
            if flush_backlog:
                try:
                    await self._flush_send_queue(raise_on_error=admitted)
                except BaseException:
                    receipt.raise_if_failed()
                    raise
                receipt.raise_if_failed()
                receipt.raise_if_unsent()
        await self._connection.send(data)

    async def close(self, *, code: int = 1000, reason: str = "") -> None:
        self._intentionally_closed = True
        self._is_reconnecting = False
        self._send_queue.mark_unsent()
        await self._connection.close(code=code, reason=reason)

    async def _reconnect(self, exc: Exception) -> bool:
        """Attempt to reconnect after a connection failure.

        Returns ``True`` if a new connection was established, ``False`` if the
        caller should re-raise the original exception.
        """
        if self._on_reconnecting is None or self._make_ws is None or self._intentionally_closed:
            return False

        from websockets.exceptions import ConnectionClosed

        close_code = 1006
        if isinstance(exc, ConnectionClosed) and exc.rcvd is not None:
            close_code = exc.rcvd.code

        if not is_recoverable_close(close_code):
            return False

        self._is_reconnecting = True
        try:
            return await self._attempt_reconnect(close_code)
        finally:
            self._is_reconnecting = False

    async def _attempt_reconnect(self, close_code: int) -> bool:
        import asyncio

        from websockets.exceptions import ConnectionClosed

        assert self._on_reconnecting is not None
        assert self._make_ws is not None
        for attempt in range(self._reconnect_attempt + 1, self._max_retries + 1):
            if self._intentionally_closed:
                return False
            self._reconnect_attempt = attempt
            base_delay = min(self._initial_delay * (2 ** (attempt - 1)), self._max_delay)
            jitter = 0.75 + random.random() * 0.25
            delay = base_delay * jitter

            event = ReconnectingEvent(
                attempt=attempt,
                max_attempts=self._max_retries,
                delay=delay,
                close_code=close_code,
                extra_query=self._extra_query,
                extra_headers=self._extra_headers,
            )

            try:
                result = self._on_reconnecting(event)
            except Exception:
                return False

            if result is not None and result.get("abort"):
                return False

            if result is not None:
                if "extra_query" in result:
                    self._extra_query = result["extra_query"]
                if "extra_headers" in result:
                    self._extra_headers = result["extra_headers"]

            self._logger.info(
                "Reconnecting to WebSocket API (attempt %d/%d) after %.1fs delay",
                attempt,
                self._max_retries,
                delay,
            )
            await asyncio.sleep(delay)

            # The flag may change again while the following handshake awaits.
            if bool(self._intentionally_closed):
                return False

            try:
                connection = await self._make_ws(self._extra_query, self._extra_headers)
                if self._intentionally_closed:
                    # A close that completed during the handshake owns the
                    # lifetime. Keep disposal running if its reader is canceled.
                    await asyncio.shield(connection.close())
                    return False
                self._connection = connection
                try:
                    await self._flush_send_queue(raise_on_error=True, finish_recovery=True)
                except Exception as flush_exc:
                    with contextlib.suppress(Exception):
                        await connection.close()
                    if isinstance(flush_exc, ConnectionClosed):
                        close_code = flush_exc.rcvd.code if flush_exc.rcvd is not None else 1006
                        if not is_recoverable_close(close_code):
                            return False
                    raise
                if self._intentionally_closed:
                    return False
                self._logger.info("Reconnected to WebSocket API")
                return True
            except Exception:
                pass

        return False

    async def _flush_send_queue(self, *, raise_on_error: bool = False, finish_recovery: bool = False) -> None:
        """Send all queued messages over the current connection."""

        def prepare_send() -> Callable[[str | bytes], Awaitable[object]] | None:
            if self._intentionally_closed or (not finish_recovery and self._is_reconnecting):
                return None
            return self._connection.send

        try:
            while True:
                # No await separates admission from this handoff/empty transition.
                if not finish_recovery and self._is_reconnecting:
                    return
                if self._intentionally_closed or not self._send_queue.has_pending_or_flushing:
                    if finish_recovery:
                        self._is_reconnecting = False
                    return
                await self._send_queue.flush_async(
                    self._connection.send, requeue_failed=False, prepare_send=prepare_send
                )
        except Exception:
            self._logger.warning("Failed to flush send queue after reconnect")
            if raise_on_error:
                raise
