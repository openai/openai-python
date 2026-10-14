from __future__ import annotations

import time
import socket
import threading
from typing import Iterable, AsyncIterator, cast

import anyio
import httpx2
from anyio.lowlevel import checkpoint

from ._httpx2 import request_exceptions, stream_consumed_exceptions

_DRAIN_TIMEOUT = 0.1


def drain_response(response: httpx2.Response) -> None:
    # The standard HTTPX transports expose their socket through this extension.
    # Other sync transports cannot be interrupted safely; just close them.
    network_stream = response.extensions.get("network_stream")
    sock = network_stream.get_extra_info("socket") if network_stream is not None else None
    if not isinstance(sock, socket.socket) or response.is_closed:
        return

    def interrupt_read() -> None:
        try:
            # Interrupt I/O without mutating SSLSocket's TLS state on this thread.
            socket.socket.shutdown(sock, socket.SHUT_RDWR)
        except OSError:
            pass  # The peer or transport may already have closed the socket.

    # A read timeout alone is insufficient: HTTP trailers can trickle in without
    # yielding body chunks. Interrupt the socket when the total budget expires.
    deadline = time.monotonic() + _DRAIN_TIMEOUT
    timer = threading.Timer(_DRAIN_TIMEOUT, interrupt_read)
    timer.daemon = True
    try:
        timer.start()
    except RuntimeError:
        return  # Cleanup is optional if a watchdog thread cannot be started.
    try:
        # Drain below Response.iter_bytes() without decoding discarded bytes.
        # The watchdog supplies the deadline; the request's read timeout stays intact.
        for _ in cast(Iterable[bytes], response.stream):
            if time.monotonic() >= deadline:
                break
    except request_exceptions() + stream_consumed_exceptions():
        pass  # Cleanup must not turn completed output into a request error.
    finally:
        timer.cancel()
        # The watchdog must finish before close() can return this connection to
        # the pool, or it could interrupt a subsequent request on the same socket.
        timer.join()


async def drain_response_async(response: httpx2.Response) -> None:
    if response.is_closed:
        return
    try:
        with anyio.move_on_after(_DRAIN_TIMEOUT):
            async for _ in cast(AsyncIterator[bytes], response.stream):
                # Also enforce the deadline on transports yielding buffered data.
                await checkpoint()
    except request_exceptions() + stream_consumed_exceptions():
        pass  # Cleanup must not turn completed output into a request error.
    finally:
        # Close outside our timeout scope and shield cleanup from caller
        # cancellation. Cancellation still propagates after the response closes.
        with anyio.CancelScope(shield=True):
            await response.aclose()
