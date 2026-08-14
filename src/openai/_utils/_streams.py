import asyncio
from typing import Any
from typing_extensions import Iterator, AsyncIterator


def consume_sync_iterator(iterator: Iterator[Any]) -> None:
    for _ in iterator:
        ...


async def consume_async_iterator(iterator: AsyncIterator[Any]) -> None:
    async for _ in iterator:
        ...


def drain_sync_iterator(iterator: Iterator[Any], timeout_ms: int = 50) -> None:
    """Drain trailing bytes from iterator with bounded timeout.

    Attempts to drain all remaining items from iterator to enable connection
    reuse, but gives up after timeout_ms to avoid indefinite blocking when
    server holds connection open after [DONE].
    """
    import time

    deadline = time.monotonic() + (timeout_ms / 1000.0)
    try:
        while time.monotonic() < deadline:
            try:
                next(iterator)
            except StopIteration:
                return
    except Exception:
        pass


async def drain_async_iterator(iterator: AsyncIterator[Any], timeout_ms: int = 50) -> None:
    """Drain trailing bytes from async iterator with bounded timeout.

    Attempts to drain all remaining items from iterator to enable connection
    reuse, but gives up after timeout_ms to avoid indefinite blocking when
    server holds connection open after [DONE].
    """
    try:
        while True:
            try:
                await asyncio.wait_for(iterator.__anext__(), timeout=timeout_ms / 1000.0)
            except StopAsyncIteration:
                return
    except asyncio.TimeoutError:
        pass
    except Exception:
        pass
