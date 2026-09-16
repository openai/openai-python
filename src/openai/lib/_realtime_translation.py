"""Private transport for a future generated Realtime Translation adapter.

Generated resources own models, serialization, event dispatch, and context managers.
This module only opens authenticated sockets and sends/receives serialized messages.
There is no reconnect or replay: a failed send may already have reached the server.
API error events are ordinary received messages, delivered once through ``recv``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from anyio import CancelScope

from .._types import Query, Headers
from .._utils import is_azure_client, is_async_azure_client
from .._httpx2 import normalize_httpx_url
from .._exceptions import OpenAIError, WebSocketConnectionClosedError
from .._send_queue import SendQueue
from .._base_client import _merge_mappings
from ..types.websocket_connection_options import WebSocketConnectionOptions

__all__ = ["_connect", "_async_connect"]

if TYPE_CHECKING:
    from websockets.sync.client import ClientConnection
    from websockets.asyncio.client import ClientConnection as AsyncClientConnection

    from .._client import OpenAI, AsyncOpenAI


def _url(client: OpenAI | AsyncOpenAI, model: str, extra_query: Query) -> str:
    if is_azure_client(client) or is_async_azure_client(client):
        raise OpenAIError("Realtime Translation transport does not support Azure")
    base = (
        normalize_httpx_url(client.websocket_base_url)
        if client.websocket_base_url is not None
        else client.base_url.copy_with(scheme="ws" if client.base_url.scheme == "http" else "wss")
    )
    return str(
        base.copy_with(
            raw_path=base.raw_path.split(b"?", 1)[0].rstrip(b"/") + b"/realtime/translations",
        ).copy_with(
            params={**client.base_url.params, "model": model, **extra_query},
        )
    )


def _unsent(messages: list[str]) -> WebSocketConnectionClosedError:
    return WebSocketConnectionClosedError(
        "Realtime Translation connection closed with unsent messages", unsent_messages=messages
    )


class _TranslationConnection:
    def __init__(self, connection: ClientConnection) -> None:
        self._connection = connection
        self._closed = False

    def recv(self) -> bytes:
        return self._connection.recv(decode=False)

    def send(self, data: str) -> None:
        if self._closed:
            raise _unsent([data])
        try:
            self._connection.send(data)
        except BaseException as exc:
            self._close_after_failure()
            if not isinstance(exc, Exception):
                raise
            raise _unsent([data]) from exc

    def close(self, *, code: int = 1000, reason: str = "") -> None:
        self._closed = True
        self._connection.close(code=code, reason=reason)

    def _close_after_failure(self) -> None:
        try:
            self.close()
        except Exception:
            # A cleanup failure must not hide the failed send and its message.
            pass


class _AsyncTranslationConnection:
    def __init__(self, connection: AsyncClientConnection) -> None:
        self._connection = connection
        self._closed = False

    async def recv(self) -> bytes:
        return await self._connection.recv(decode=False)

    async def send(self, data: str) -> None:
        if self._closed:
            raise _unsent([data])
        try:
            await self._connection.send(data)
        except BaseException as exc:
            await self._close_after_failure()
            if not isinstance(exc, Exception):
                raise
            raise _unsent([data]) from exc

    async def close(self, *, code: int = 1000, reason: str = "") -> None:
        self._closed = True
        await self._connection.close(code=code, reason=reason)

    async def _close_after_failure(self) -> None:
        # AnyIO cancellation is level-triggered: cleanup must be allowed to
        # finish before the original cancellation is propagated to the caller.
        with CancelScope(shield=True):
            try:
                await self.close()
            except Exception:
                pass


def _connect(
    client: OpenAI,
    *,
    model: str,
    extra_query: Query = {},
    extra_headers: Headers = {},
    websocket_connection_options: WebSocketConnectionOptions = {},
    send_queue: SendQueue | None = None,
) -> _TranslationConnection:
    """Open one connection and flush the adapter's optional startup queue.

    On failure the queue is drained into ``unsent_messages``; successful sends
    are excluded. The caller must decide whether retrying is appropriate.
    """
    connection = None
    try:
        try:
            # The synchronous connector doesn't follow redirects.
            from websockets.sync.client import connect
        except ImportError as exc:
            raise OpenAIError("You need to install `openai[realtime]` to use this method") from exc

        url = _url(client, model, extra_query)
        client._refresh_api_key()
        options: WebSocketConnectionOptions = {"max_size": None, **websocket_connection_options}
        connection = _TranslationConnection(
            connect(
                url,
                user_agent_header=client.user_agent,
                additional_headers=_merge_mappings(client.auth_headers, extra_headers),
                **options,
            )
        )
        if send_queue is not None:
            while send_queue:
                send_queue.flush_sync(connection._connection.send)
        return connection
    except BaseException as exc:
        if connection is not None:
            connection._close_after_failure()
        if isinstance(exc, Exception) and send_queue is not None and (unsent := send_queue.drain()):
            raise _unsent(unsent) from exc
        raise


async def _async_connect(
    client: AsyncOpenAI,
    *,
    model: str,
    extra_query: Query = {},
    extra_headers: Headers = {},
    websocket_connection_options: WebSocketConnectionOptions = {},
    send_queue: SendQueue | None = None,
) -> _AsyncTranslationConnection:
    """Async counterpart of ``_connect``; cancellation preserves the caller's queue."""
    connection = None
    try:
        try:
            from ._websocket import _WebSocketConnect
        except ImportError as exc:
            raise OpenAIError("You need to install `openai[realtime]` to use this method") from exc

        url = _url(client, model, extra_query)
        await client._refresh_api_key()
        options: WebSocketConnectionOptions = {"max_size": None, **websocket_connection_options}
        connection = _AsyncTranslationConnection(
            await _WebSocketConnect(
                url,
                user_agent_header=client.user_agent,
                additional_headers=_merge_mappings(client.auth_headers, extra_headers),
                **options,
            )
        )
        if send_queue is not None:
            while send_queue:
                await send_queue.flush_async(connection._connection.send)
        return connection
    except BaseException as exc:
        if connection is not None:
            await connection._close_after_failure()
        if isinstance(exc, Exception) and send_queue is not None and (unsent := send_queue.drain()):
            raise _unsent(unsent) from exc
        raise
