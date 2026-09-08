from typing import Any, Optional
from typing_extensions import Iterator, AsyncIterator

import anyio


def consume_sync_iterator(iterator: Iterator[Any]) -> None:
    for _ in iterator:
        ...


async def consume_async_iterator(iterator: AsyncIterator[Any]) -> None:
    async for _ in iterator:
        ...


async def drain_async_iterator(
    iterator: Optional[AsyncIterator[Any]], response: Any = None, timeout_ms: int = 50
) -> None:
    """Drain trailing bytes from async iterator with bounded timeout.

    Bounds cancellation-cooperative async streams to enable connection reuse after [DONE].
    Uses anyio for backend compatibility (asyncio and Trio). Cannot guarantee termination
    for custom iterators that block the event loop or suppress cancellation.
    """
    if iterator is None:
        return

    try:
        with anyio.move_on_after(timeout_ms / 1000.0):
            try:
                async for _ in iterator:
                    pass
            except Exception:
                pass
    finally:
        # Close response to interrupt any blocked iterator reads on timeout
        if response is not None:
            try:
                await response.aclose()
            except Exception:
                pass
