from __future__ import annotations

import json
import asyncio
import threading
from types import TracebackType
from typing import TYPE_CHECKING, Any, Literal, cast

import httpx2
from pydantic import BaseModel

from .._types import Query, Headers
from .._utils import (
    is_dict,
    is_azure_client,
    is_async_azure_client,
)
from .._models import validate_type, construct_type_unchecked
from .._exceptions import OpenAIError
from ..types.realtime import (
    RealtimeTranslationClientEvent,
    RealtimeTranslationServerEvent,
    RealtimeTranslationClientEventParam,
    RealtimeTranslationSessionClosedEvent,
)
from ..types.websocket_connection_options import WebSocketConnectionOptions

__all__ = ["TranslationSession", "AsyncTranslationSession", "TranslationConnection", "AsyncTranslationConnection"]

if TYPE_CHECKING:
    from .._client import OpenAI, AsyncOpenAI
    from ..resources.realtime.translations.translations import (
        Translations,
        AsyncTranslations,
        TranslationsConnection,
        AsyncTranslationsConnection,
    )


def _check_connection(client: OpenAI | AsyncOpenAI, model: str, query: Query) -> None:
    if not model:
        raise ValueError("A translation model is required.")
    if is_azure_client(client) or is_async_azure_client(client) or client._provider_runtime is not None:
        raise OpenAIError("Realtime Translation is not available through this provider.")
    if "intent" in client.base_url.params or "intent" in client.default_query or "intent" in query:
        raise ValueError("Realtime Translation does not accept an intent query parameter.")
    if client.websocket_base_url is not None and "intent" in httpx2.URL(str(client.websocket_base_url)).params:
        raise ValueError("Realtime Translation does not accept an intent query parameter.")


def _connection_query(client: OpenAI | AsyncOpenAI, model: str, query: Query) -> Query:
    # Preserve Translation's base URL query when a separate WebSocket gateway is used.
    params = client.base_url.params.merge(client.qs.stringify(cast(Any, client.default_query)))
    if client.websocket_base_url is not None:
        params = params.merge(httpx2.URL(str(client.websocket_base_url)).params)
    return cast(Query, params.merge({"model": model}).merge(cast(Any, query)))


def _parse(data: str | bytes) -> RealtimeTranslationServerEvent:
    value = json.loads(data)
    # Only a complete terminal event can end the session. Preserve ordinary
    # forward-compatible parsing, including unknown server events, elsewhere.
    if is_dict(value) and value.get("type") == "session.closed":
        return validate_type(type_=RealtimeTranslationSessionClosedEvent, value=value)
    return cast(
        RealtimeTranslationServerEvent,
        construct_type_unchecked(value=value, type_=cast(Any, RealtimeTranslationServerEvent)),
    )


class TranslationConnection:
    def __init__(self, connection: TranslationsConnection) -> None:
        self._connection = connection
        self._send_lock = threading.Lock()
        self._state: Literal["open", "finishing", "closed"] = "open"

    def send(self, event: RealtimeTranslationClientEvent | RealtimeTranslationClientEventParam) -> None:
        is_finish = (event.type if isinstance(event, BaseModel) else event.get("type")) == "session.close"
        with self._send_lock:
            if self._state == "finishing" and is_finish:
                return
            if self._state != "open":
                raise OpenAIError("Realtime Translation input is closed.")
            if is_finish:
                self._state = "finishing"
            try:
                self._connection.send(event)
            except BaseException as error:
                # An uncertain write may already have reached the server; never replay it.
                try:
                    self.close()
                except BaseException as closing:
                    raise error from closing
                raise

    def recv(self, *, timeout: float | None = None) -> RealtimeTranslationServerEvent:
        """Receive a server event, optionally bounded by a timeout in seconds."""
        # Both text and binary are supported, including websockets 13's sync API.
        event = _parse(
            self._connection.recv_bytes() if timeout is None else self._connection._connection.recv(timeout=timeout)
        )
        if isinstance(event, RealtimeTranslationSessionClosedEvent):
            self.close()
        return event

    def close(self) -> None:
        # Do not wait for a blocked writer before aborting the transport.
        self._state = "closed"
        self._connection.close()


class AsyncTranslationConnection:
    def __init__(self, connection: AsyncTranslationsConnection) -> None:
        self._connection = connection
        self._send_lock = asyncio.Lock()
        self._state: Literal["open", "finishing", "closed"] = "open"

    async def send(self, event: RealtimeTranslationClientEvent | RealtimeTranslationClientEventParam) -> None:
        is_finish = (event.type if isinstance(event, BaseModel) else event.get("type")) == "session.close"
        async with self._send_lock:
            if self._state == "finishing" and is_finish:
                return
            if self._state != "open":
                raise OpenAIError("Realtime Translation input is closed.")
            if is_finish:
                self._state = "finishing"
            try:
                await self._connection.send(event)
            except BaseException as error:
                try:
                    await self.close()
                except BaseException as closing:
                    raise error from closing
                raise

    async def recv(self) -> RealtimeTranslationServerEvent:
        event = _parse(await self._connection.recv_bytes())
        if isinstance(event, RealtimeTranslationSessionClosedEvent):
            await self.close()
        return event

    async def close(self) -> None:
        self._state = "closed"
        await self._connection.close()


class TranslationSession:
    """Open a Translation session through its generated binding, without replay.

    Send ``session.close`` once, then receive through ``session.closed`` to keep
    trailing output. Leaving the context closes only this connection.
    """

    def __init__(
        self,
        resource: Translations,
        *,
        model: str,
        extra_query: Query = {},
        extra_headers: Headers = {},
        websocket_connection_options: WebSocketConnectionOptions = {},
    ) -> None:
        self._resource = resource
        self._client = resource._client
        self._model = model
        self._query = extra_query
        self._headers = extra_headers
        self._options = websocket_connection_options
        self._connection: TranslationConnection | None = None
        self._entered = False

    def __enter__(self) -> TranslationConnection:
        if self._entered:
            raise RuntimeError("Translation sessions may only be entered once")
        self._entered = True
        _check_connection(self._client, self._model, self._query)
        manager = self._resource.connect(
            model=self._model,
            extra_query=_connection_query(self._client, self._model, self._query),
            extra_headers=self._headers,
            websocket_connection_options=self._options,
        )
        self._connection = TranslationConnection(manager.enter())
        return self._connection

    enter = __enter__

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        if self._connection is not None:
            try:
                self._connection.close()
            except BaseException as closing:
                if exc is not None:
                    raise exc.with_traceback(exc_tb) from closing
                raise


class AsyncTranslationSession:
    """Async Translation session with caller-owned receiving and no replay."""

    def __init__(
        self,
        resource: AsyncTranslations,
        *,
        model: str,
        extra_query: Query = {},
        extra_headers: Headers = {},
        websocket_connection_options: WebSocketConnectionOptions = {},
    ) -> None:
        self._resource = resource
        self._client = resource._client
        self._model = model
        self._query = extra_query
        self._headers = extra_headers
        self._options = websocket_connection_options
        self._connection: AsyncTranslationConnection | None = None
        self._entered = False

    async def __aenter__(self) -> AsyncTranslationConnection:
        if self._entered:
            raise RuntimeError("Translation sessions may only be entered once")
        self._entered = True
        _check_connection(self._client, self._model, self._query)
        manager = self._resource.connect(
            model=self._model,
            extra_query=_connection_query(self._client, self._model, self._query),
            extra_headers=self._headers,
            websocket_connection_options=self._options,
        )
        self._connection = AsyncTranslationConnection(await manager.enter())
        return self._connection

    enter = __aenter__

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        if self._connection is not None:
            try:
                await self._connection.close()
            except BaseException as closing:
                if exc is not None:
                    raise exc.with_traceback(exc_tb) from closing
                raise
