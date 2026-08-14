import time
import asyncio
import threading
from typing import Any, Optional
from typing_extensions import Iterator, AsyncIterator


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
    """
    if iterator is None:
        return

    loop = asyncio.get_running_loop()
    deadline = loop.time() + (timeout_ms / 1000.0)
    while True:
        remaining = deadline - loop.time()
        if remaining <= 0:
            break
        try:
            await asyncio.wait_for(iterator.__anext__(), timeout=remaining)
        except StopAsyncIteration:
            return
        except asyncio.TimeoutError:
            break
        except Exception:
            break
