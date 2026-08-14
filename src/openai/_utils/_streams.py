import threading
from typing import Any, Optional
from typing_extensions import Iterator, AsyncIterator

import anyio


def consume_sync_iterator(iterator: Iterator[Any]) -> None:
    for _ in iterator:
        ...


async def consume_async_iterator(iterator: AsyncIterator[Any]) -> None:
    async for _ in iterator:
        ...


def drain_sync_iterator(iterator: Optional[Iterator[Any]], timeout_ms: int = 50) -> None:
    """Drain trailing bytes from iterator with bounded timeout.

    Attempts to drain all remaining items from iterator to enable connection
    reuse, but gives up after timeout_ms to avoid indefinite blocking when
    server holds connection open after [DONE].

    Runs in background thread to prevent blocking on iterator.__next__().
    """
    if iterator is None:
        return

    def _drain() -> None:
        try:
            while True:
                try:
                    next(iterator)
                except StopIteration:
                    return
                except Exception:
                    break
        except Exception:
            pass

    thread = threading.Thread(target=_drain, daemon=True)
    thread.start()
    thread.join(timeout=timeout_ms / 1000.0)


async def drain_async_iterator(iterator: Optional[AsyncIterator[Any]], timeout_ms: int = 50) -> None:
    """Drain trailing bytes from async iterator with bounded timeout.

    Attempts to drain all remaining items from iterator to enable connection
    reuse, but gives up after timeout_ms to avoid indefinite blocking when
    server holds connection open after [DONE].

    Uses anyio for async backend compatibility (works with asyncio and Trio).
    """
    if iterator is None:
        return

    with anyio.move_on_after(timeout_ms / 1000.0):
        try:
            async for _ in iterator:
                pass
        except Exception:
            pass
