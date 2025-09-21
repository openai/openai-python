from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Callable
from .unified import StreamEvent

async def _map_async_iter(
    source: AsyncIterator[Any],
    fn: Callable[[Any], StreamEvent],
) -> AsyncIterator[StreamEvent]:
    async for item in source:
        yield fn(item)

@asynccontextmanager
async def _wrap_unified(cm, adapter_fn: Callable[[Any], StreamEvent]):
    """
    Wrap an existing async context manager (cm) that yields an async iterator of raw events,
    and expose a context manager that yields an async iterator of adapted StreamEvent.
    """
    async with cm as underlying:
        async def _mapped():
            async for raw in underlying:
                yield adapter_fn(raw)
        yield _mapped()

# Optional alias if something imported the non-underscored name before
map_async_iter = _map_async_iter
