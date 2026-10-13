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

    saved_timeout = cast("dict[str, float | None] | None", response.request.extensions.get("timeout"))
    read_timeout = (saved_timeout or {}).get("read")
    timeout = _DRAIN_TIMEOUT if read_timeout is None else min(_DRAIN_TIMEOUT, read_timeout)

    def interrupt_read() -> None:
        try:
            # Interrupt I/O without mutating SSLSocket's TLS state on this thread.
            socket.socket.shutdown(sock, socket.SHUT_RDWR)
        except OSError:
            pass  # The peer or transport may already have closed the socket.

    # A read timeout alone is insufficient: HTTP trailers can trickle in without
    # yielding body chunks. Interrupt the socket when the total budget expires.
    deadline = time.monotonic() + timeout
    timer = threading.Timer(timeout, interrupt_read)
    timer.daemon = True
    try:
        timer.start()
    except RuntimeError:
        return  # Cleanup is optional if a watchdog thread cannot be started.
    try:
        response.request.extensions["timeout"] = {**(saved_timeout or {}), "read": timeout}
        # Restart the transport iterator so httpcore picks up the cleanup timeout,
        # without passing discarded bytes through SSE or decompression again.
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
        if saved_timeout is None:
            response.request.extensions.pop("timeout", None)
        else:
            response.request.extensions["timeout"] = saved_timeout


async def drain_response_async(response: httpx2.Response) -> None:
    if response.is_closed:
        return
    try:
        with anyio.move_on_after(_DRAIN_TIMEOUT):
            async for _ in cast(AsyncIterator[bytes], response.stream):
                # Also enforce the deadline on transports yielding buffered data.
                await checkpoint()
    except request_exceptions() + stream_consumed_exceptions():
        pass
    finally:
        # Close outside our timeout scope and shield cleanup from caller
        # cancellation. Cancellation still propagates after the response closes.
        with anyio.CancelScope(shield=True):
            await response.aclose()
