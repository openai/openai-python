from typing import Any, Callable

import httpx2 as httpx


class TransportHandler:
    def __init__(self, transport: httpx.BaseTransport) -> None:
        self.transport = transport

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if not isinstance(
            request.stream,
            httpx.SyncByteStream,
        ):  # pragma: nocover
            raise RuntimeError("Attempted to route an async request to a sync app.")

        return self.transport.handle_request(request)


class AsyncTransportHandler:
    def __init__(self, transport: httpx.AsyncBaseTransport) -> None:
        self.transport = transport

    async def __call__(self, request: httpx.Request) -> httpx.Response:
        if not isinstance(
            request.stream,
            httpx.AsyncByteStream,
        ):  # pragma: nocover
            raise RuntimeError("Attempted to route a sync request to an async app.")

        return await self.transport.handle_async_request(request)


class WSGIHandler(TransportHandler):
    def __init__(self, app: Callable, **kwargs: Any) -> None:
        super().__init__(httpx.WSGITransport(app=app, **kwargs))


class ASGIHandler(AsyncTransportHandler):
    def __init__(self, app: Callable, **kwargs: Any) -> None:
        super().__init__(httpx.ASGITransport(app=app, **kwargs))
