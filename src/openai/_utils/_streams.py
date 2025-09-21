from typing import Any
from typing_extensions import Iterator, AsyncIterator

def consume_sync_iterator(iterator: Iterator[Any]) -> None:
    if iterator is None:
        return
    for _ in iterator:
        ...

async def consume_async_iterator(iterator: AsyncIterator[Any]) -> None:
    if iterator is None:
        return
    async for _ in iterator:
        ...
