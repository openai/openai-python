from typing import Any
from typing_extensions import Iterator, AsyncIterator


def consume_sync_iterator(iterator: Iterator[Any]) -> None:
    for _ in iterator:
        ...


async def consume_async_iterator(iterator: AsyncIterator[Any]) -> None:
    async for _ in iterator:
        ...


def drain_sync_iterator(iterator: Iterator[Any], max_items: int = 16) -> None:
    """Drain a bounded number of items from an iterator without blocking indefinitely.

    Used after stream termination signals like [DONE] to attempt connection reuse
    without waiting for the entire response body.
    """
    for _ in range(max_items):
        try:
            next(iterator)
        except StopIteration:
            break


async def drain_async_iterator(iterator: AsyncIterator[Any], max_items: int = 16) -> None:
    """Drain a bounded number of items from an async iterator without blocking indefinitely.

    Used after stream termination signals like [DONE] to attempt connection reuse
    without waiting for the entire response body.
    """
    for _ in range(max_items):
        try:
            await iterator.__anext__()
        except StopAsyncIteration:
            break
