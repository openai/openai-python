# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import json
import time
import random
import logging
from types import TracebackType
from typing import TYPE_CHECKING, Any, Union, Callable, Iterator, Awaitable, cast
from typing_extensions import AsyncIterator

import httpx
from pydantic import BaseModel

from .calls import (
    Calls,
    AsyncCalls,
    CallsWithRawResponse,
    AsyncCallsWithRawResponse,
    CallsWithStreamingResponse,
    AsyncCallsWithStreamingResponse,
)
from ..._types import Omit, Query, Headers, omit
from ..._utils import (
    is_azure_client,
    maybe_transform,
    strip_not_given,
    async_maybe_transform,
    is_async_azure_client,
)
from ..._compat import cached_property
from ..._models import construct_type_unchecked
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._exceptions import OpenAIError, WebSocketConnectionClosedError
from ..._send_queue import SendQueue
from ..._base_client import _merge_mappings
from .client_secrets import (
    ClientSecrets,
    AsyncClientSecrets,
    ClientSecretsWithRawResponse,
    AsyncClientSecretsWithRawResponse,
    ClientSecretsWithStreamingResponse,
    AsyncClientSecretsWithStreamingResponse,
)
from ..._event_handler import EventHandlerRegistry
from ...types.realtime import session_update_event_param
from ...types.websocket_reconnection import ReconnectingEvent, ReconnectingOverrides, is_recoverable_close
from ...types.websocket_connection_options import WebSocketConnectionOptions
from ...types.realtime.realtime_error_event import RealtimeErrorEvent
from ...types.realtime.realtime_client_event import RealtimeClientEvent
from ...types.realtime.realtime_server_event import RealtimeServerEvent
from ...types.realtime.conversation_item_param import ConversationItemParam
from ...types.realtime.realtime_client_event_param import RealtimeClientEventParam
from ...types.realtime.realtime_response_create_params_param import RealtimeResponseCreateParamsParam

if TYPE_CHECKING:
    from websockets.sync.client import ClientConnection as WebSocketConnection
    from websockets.asyncio.client import ClientConnection as AsyncWebSocketConnection

    from ..._client import OpenAI, AsyncOpenAI

__all__ = ["Realtime", "AsyncRealtime"]

log: logging.Logger = logging.getLogger(__name__)


class Realtime(SyncAPIResource):
    @cached_property
    def client_secrets(self) -> ClientSecrets:
        return ClientSecrets(self._client)

    @cached_property
    def calls(self) -> Calls:
        from ...lib._realtime import _Calls

        return _Calls(self._client)

    @cached_property
    def with_raw_response(self) -> RealtimeWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return RealtimeWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RealtimeWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return RealtimeWithStreamingResponse(self)

    def connect(
        self,
        *,
        call_id: str | Omit = omit,
        model: str | Omit = omit,
        extra_query: Query = {},
        extra_headers: Headers = {},
        websocket_connection_options: WebSocketConnectionOptions = {},
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        max_queue_size: int = 1_048_576,
    ) -> RealtimeConnectionManager:
        """
        The Realtime API enables you to build low-latency, multi-modal conversational experiences. It currently supports text and audio as both input and output, as well as function calling.

        Some notable benefits of the API include:

        - Native speech-to-speech: Skipping an intermediate text format means low latency and nuanced output.
        - Natural, steerable voices: The models have natural inflection and can laugh, whisper, and adhere to tone direction.
        - Simultaneous multimodal output: Text is useful for moderation; faster-than-realtime audio ensures stable playback.

        The Realtime API is a stateful, event-based API that communicates over a WebSocket.
        """
        return RealtimeConnectionManager(
            client=self._client,
            extra_query=extra_query,
            extra_headers=extra_headers,
            websocket_connection_options=websocket_connection_options,
            on_reconnecting=on_reconnecting,
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay,
            max_queue_size=max_queue_size,
            call_id=call_id,
            model=model,
        )


class AsyncRealtime(AsyncAPIResource):
    @cached_property
    def client_secrets(self) -> AsyncClientSecrets:
        return AsyncClientSecrets(self._client)

    @cached_property
    def calls(self) -> AsyncCalls:
        from ...lib._realtime import _AsyncCalls

        return _AsyncCalls(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncRealtimeWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRealtimeWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRealtimeWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncRealtimeWithStreamingResponse(self)

    def connect(
        self,
        *,
        call_id: str | Omit = omit,
        model: str | Omit = omit,
        extra_query: Query = {},
        extra_headers: Headers = {},
        websocket_connection_options: WebSocketConnectionOptions = {},
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        max_queue_size: int = 1_048_576,
    ) -> AsyncRealtimeConnectionManager:
        """
        The Realtime API enables you to build low-latency, multi-modal conversational experiences. It currently supports text and audio as both input and output, as well as function calling.

        Some notable benefits of the API include:

        - Native speech-to-speech: Skipping an intermediate text format means low latency and nuanced output.
        - Natural, steerable voices: The models have natural inflection and can laugh, whisper, and adhere to tone direction.
        - Simultaneous multimodal output: Text is useful for moderation; faster-than-realtime audio ensures stable playback.

        The Realtime API is a stateful, event-based API that communicates over a WebSocket.
        """
        return AsyncRealtimeConnectionManager(
            client=self._client,
            extra_query=extra_query,
            extra_headers=extra_headers,
            websocket_connection_options=websocket_connection_options,
            on_reconnecting=on_reconnecting,
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay,
            max_queue_size=max_queue_size,
            call_id=call_id,
            model=model,
        )


class RealtimeWithRawResponse:
    def __init__(self, realtime: Realtime) -> None:
        self._realtime = realtime

    @cached_property
    def client_secrets(self) -> ClientSecretsWithRawResponse:
        return ClientSecretsWithRawResponse(self._realtime.client_secrets)

    @cached_property
    def calls(self) -> CallsWithRawResponse:
        return CallsWithRawResponse(self._realtime.calls)


class AsyncRealtimeWithRawResponse:
    def __init__(self, realtime: AsyncRealtime) -> None:
        self._realtime = realtime

    @cached_property
    def client_secrets(self) -> AsyncClientSecretsWithRawResponse:
        return AsyncClientSecretsWithRawResponse(self._realtime.client_secrets)

    @cached_property
    def calls(self) -> AsyncCallsWithRawResponse:
        return AsyncCallsWithRawResponse(self._realtime.calls)


class RealtimeWithStreamingResponse:
    def __init__(self, realtime: Realtime) -> None:
        self._realtime = realtime

    @cached_property
    def client_secrets(self) -> ClientSecretsWithStreamingResponse:
        return ClientSecretsWithStreamingResponse(self._realtime.client_secrets)

    @cached_property
    def calls(self) -> CallsWithStreamingResponse:
        return CallsWithStreamingResponse(self._realtime.calls)


class AsyncRealtimeWithStreamingResponse:
    def __init__(self, realtime: AsyncRealtime) -> None:
        self._realtime = realtime

    @cached_property
    def client_secrets(self) -> AsyncClientSecretsWithStreamingResponse:
        return AsyncClientSecretsWithStreamingResponse(self._realtime.client_secrets)

    @cached_property
    def calls(self) -> AsyncCallsWithStreamingResponse:
        return AsyncCallsWithStreamingResponse(self._realtime.calls)


class AsyncRealtimeConnection:
    """Represents a live WebSocket connection to the Realtime API"""

    session: AsyncRealtimeSessionResource
    response: AsyncRealtimeResponseResource
    input_audio_buffer: AsyncRealtimeInputAudioBufferResource
    conversation: AsyncRealtimeConversationResource
    output_audio_buffer: AsyncRealtimeOutputAudioBufferResource

    _connection: AsyncWebSocketConnection

    def __init__(
        self,
        connection: AsyncWebSocketConnection,
        *,
        make_ws: Callable[[Query, Headers], Awaitable[AsyncWebSocketConnection]] | None = None,
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        extra_query: Query = {},
        extra_headers: Headers = {},
        send_queue: SendQueue | None = None,
    ) -> None:
        self._connection = connection
        self._make_ws = make_ws
        self._on_reconnecting = on_reconnecting
        self._max_retries = max_retries
        self._initial_delay = initial_delay
        self._max_delay = max_delay
        self._extra_query = extra_query
        self._extra_headers = extra_headers
        self._intentionally_closed = False
        self._is_reconnecting = False
        self._send_queue = send_queue or SendQueue()
        self._event_handler_registry = EventHandlerRegistry(use_lock=False)

        self.session = AsyncRealtimeSessionResource(self)
        self.response = AsyncRealtimeResponseResource(self)
        self.input_audio_buffer = AsyncRealtimeInputAudioBufferResource(self)
        self.conversation = AsyncRealtimeConversationResource(self)
        self.output_audio_buffer = AsyncRealtimeOutputAudioBufferResource(self)

    async def __aiter__(self) -> AsyncIterator[RealtimeServerEvent]:
        """
        An infinite-iterator that will continue to yield events until
        the connection is closed.
        """
        from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

        while True:
            try:
                yield await self.recv()
            except ConnectionClosedOK:
                return
            except ConnectionClosedError as exc:
                if not await self._reconnect(exc):
                    unsent = self._send_queue.drain()
                    if unsent:
                        raise WebSocketConnectionClosedError(
                            "WebSocket connection closed with unsent messages",
                            unsent_messages=unsent,
                        ) from exc
                    raise

    async def recv(self) -> RealtimeServerEvent:
        """
        Receive the next message from the connection and parses it into a `RealtimeServerEvent` object.

        Canceling this method is safe. There's no risk of losing data.
        """
        return self.parse_event(await self.recv_bytes())

    async def recv_bytes(self) -> bytes:
        """Receive the next message from the connection as raw bytes.

        Canceling this method is safe. There's no risk of losing data.

        If you want to parse the message into a `RealtimeServerEvent` object like `.recv()` does,
        then you can call `.parse_event(data)`.
        """
        message = await self._connection.recv(decode=False)
        log.debug(f"Received WebSocket message: %s", message)
        return message

    async def send(self, event: RealtimeClientEvent | RealtimeClientEventParam) -> None:
        data = (
            event.to_json(use_api_names=True, exclude_defaults=True, exclude_unset=True)
            if isinstance(event, BaseModel)
            else json.dumps(await async_maybe_transform(event, RealtimeClientEventParam))
        )
        if self._is_reconnecting:
            self._send_queue.enqueue(data)
            return
        try:
            await self._connection.send(data)
        except Exception:
            self._send_queue.enqueue(data)
            raise

    async def send_raw(self, data: bytes | str) -> None:
        if self._is_reconnecting:
            raw = data if isinstance(data, str) else data.decode("utf-8")
            self._send_queue.enqueue(raw)
            return
        await self._connection.send(data)

    async def close(self, *, code: int = 1000, reason: str = "") -> None:
        self._intentionally_closed = True
        await self._connection.close(code=code, reason=reason)

    def parse_event(self, data: str | bytes) -> RealtimeServerEvent:
        """
        Converts a raw `str` or `bytes` message into a `RealtimeServerEvent` object.

        This is helpful if you're using `.recv_bytes()`.
        """
        return cast(
            RealtimeServerEvent, construct_type_unchecked(value=json.loads(data), type_=cast(Any, RealtimeServerEvent))
        )

    async def _reconnect(self, exc: Exception) -> bool:
        """Attempt to reconnect after a connection failure.

        Returns ``True`` if a new connection was established, ``False`` if the
        caller should re-raise the original exception.
        """
        import asyncio

        if self._on_reconnecting is None or self._make_ws is None:
            return False

        from websockets.exceptions import ConnectionClosedError

        close_code = 1006
        if isinstance(exc, ConnectionClosedError) and exc.rcvd is not None:
            close_code = exc.rcvd.code

        if not is_recoverable_close(close_code):
            return False

        self._is_reconnecting = True

        for attempt in range(1, self._max_retries + 1):
            base_delay = min(self._initial_delay * (2 ** (attempt - 1)), self._max_delay)
            jitter = 0.75 + random.random() * 0.25
            delay = base_delay * jitter

            event = ReconnectingEvent(
                attempt=attempt,
                max_attempts=self._max_retries,
                delay=delay,
                close_code=close_code,
                extra_query=self._extra_query,
                extra_headers=self._extra_headers,
            )

            try:
                result = self._on_reconnecting(event)
            except Exception:
                self._is_reconnecting = False
                return False

            if result is not None and result.get("abort"):
                self._is_reconnecting = False
                return False

            if result is not None:
                if "extra_query" in result:
                    self._extra_query = result["extra_query"]
                if "extra_headers" in result:
                    self._extra_headers = result["extra_headers"]

            log.info(
                "Reconnecting to WebSocket API (attempt %d/%d) after %.1fs delay",
                attempt,
                self._max_retries,
                delay,
            )
            await asyncio.sleep(delay)

            if self._intentionally_closed:
                self._is_reconnecting = False
                return False

            try:
                self._connection = await self._make_ws(self._extra_query, self._extra_headers)
                log.info("Reconnected to WebSocket API")
                self._is_reconnecting = False
                await self._flush_send_queue()
                return True
            except Exception:
                pass

        self._is_reconnecting = False
        return False

    async def _flush_send_queue(self) -> None:
        """Send all queued messages over the current connection."""

        async def _send(data: str) -> None:
            await self._connection.send(data)

        try:
            await self._send_queue.flush_async(_send)
        except Exception:
            log.warning("Failed to flush send queue after reconnect", exc_info=True)

    def on(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[AsyncRealtimeConnection, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Adds the handler to the end of the handlers list for the given event type.

        No checks are made to see if the handler has already been added. Multiple calls
        passing the same combination of event type and handler will result in the handler
        being added, and called, multiple times.

        Can be used as a method (returns ``self`` for chaining)::

            connection.on("conversation.created", my_handler)

        Or as a decorator::

            @connection.on("conversation.created")
            async def my_handler(event): ...
        """
        if handler is not None:
            self._event_handler_registry.add(event_type, handler)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self._event_handler_registry.add(event_type, fn)
            return fn

        return decorator

    def off(self, event_type: str, handler: Callable[..., Any]) -> AsyncRealtimeConnection:
        """Remove a previously registered event handler."""
        self._event_handler_registry.remove(event_type, handler)
        return self

    def once(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[AsyncRealtimeConnection, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register a one-time event handler.

        Automatically removed after first invocation.
        """
        if handler is not None:
            self._event_handler_registry.add(event_type, handler, once=True)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self._event_handler_registry.add(event_type, fn, once=True)
            return fn

        return decorator

    async def dispatch_events(self) -> None:
        """Run the event loop, dispatching received events to registered handlers.

        Blocks until the connection is closed. This is the push-based
        alternative to iterating with ``async for event in connection``.

        If an ``"error"`` event arrives and no handler is registered for
        ``"error"`` or ``"event"``, an ``OpenAIError`` is raised.
        """
        import asyncio

        async for event in self:
            event_type = event.type
            specific = self._event_handler_registry.get_handlers(event_type)
            generic = self._event_handler_registry.get_handlers("event")

            if event_type == "error" and not specific and not generic:
                if isinstance(event, RealtimeErrorEvent):
                    raise OpenAIError(f"WebSocket error: {event}")

            for handler in specific:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result

            for handler in generic:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result


class AsyncRealtimeConnectionManager:
    """
    Context manager over a `AsyncRealtimeConnection` that is returned by `realtime.connect()`

    This context manager ensures that the connection will be closed when it exits.

    ---

    Note that if your application doesn't work well with the context manager approach then you
    can call the `.enter()` method directly to initiate a connection.

    **Warning**: You must remember to close the connection with `.close()`.

    ```py
    connection = await client.realtime.connect(...).enter()
    # ...
    await connection.close()
    ```
    """

    def __init__(
        self,
        *,
        client: AsyncOpenAI,
        call_id: str | Omit = omit,
        model: str | Omit = omit,
        extra_query: Query,
        extra_headers: Headers,
        websocket_connection_options: WebSocketConnectionOptions,
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        max_queue_size: int = 1_048_576,
    ) -> None:
        self.__client = client
        self.__call_id = call_id
        self.__model = model
        self.__connection: AsyncRealtimeConnection | None = None
        self.__extra_query = extra_query
        self.__extra_headers = extra_headers
        self.__websocket_connection_options = websocket_connection_options
        self.__on_reconnecting = on_reconnecting
        self.__max_retries = max_retries
        self.__initial_delay = initial_delay
        self.__max_delay = max_delay
        self.__send_queue = SendQueue(max_bytes=max_queue_size)
        self.__event_handler_registry = EventHandlerRegistry(use_lock=False)

    def send(self, event: RealtimeClientEvent | RealtimeClientEventParam) -> None:
        """Queue a message to be sent when the connection is established.

        This can be called before entering the context manager. Queued messages
        are automatically sent once the WebSocket connection opens.
        """
        data = (
            event.to_json(use_api_names=True, exclude_defaults=True, exclude_unset=True)
            if isinstance(event, BaseModel)
            else json.dumps(event)
        )
        self.__send_queue.enqueue(data)

    def on(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[AsyncRealtimeConnectionManager, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register an event handler before the connection is established.

        Handlers are transferred to the connection on enter. Supports the
        same method and decorator forms as ``AsyncRealtimeConnection.on``.
        """
        if handler is not None:
            self.__event_handler_registry.add(event_type, handler)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.__event_handler_registry.add(event_type, fn)
            return fn

        return decorator

    def off(self, event_type: str, handler: Callable[..., Any]) -> AsyncRealtimeConnectionManager:
        """Remove a previously registered event handler."""
        self.__event_handler_registry.remove(event_type, handler)
        return self

    def once(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[AsyncRealtimeConnectionManager, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register a one-time event handler before the connection is established."""
        if handler is not None:
            self.__event_handler_registry.add(event_type, handler, once=True)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.__event_handler_registry.add(event_type, fn, once=True)
            return fn

        return decorator

    async def __aenter__(self) -> AsyncRealtimeConnection:
        """
        If your application doesn't work well with the context manager approach then you
        can call this method directly to initiate a connection.

        **Warning**: You must remember to close the connection with `.close()`.

        ```py
        connection = await client.realtime.connect(...).enter()
        # ...
        await connection.close()
        ```
        """
        ws = await self._connect_ws(self.__extra_query, self.__extra_headers)

        self.__connection = AsyncRealtimeConnection(
            ws,
            make_ws=self._connect_ws if self.__on_reconnecting is not None else None,
            on_reconnecting=self.__on_reconnecting,
            max_retries=self.__max_retries,
            initial_delay=self.__initial_delay,
            max_delay=self.__max_delay,
            extra_query=self.__extra_query,
            extra_headers=self.__extra_headers,
            send_queue=self.__send_queue,
        )

        self.__event_handler_registry.merge_into(self.__connection._event_handler_registry)
        await self.__connection._flush_send_queue()

        return self.__connection

    enter = __aenter__

    async def _connect_ws(self, extra_query: Query, extra_headers: Headers) -> AsyncWebSocketConnection:
        try:
            from websockets.asyncio.client import connect
        except ImportError as exc:
            raise OpenAIError("You need to install `openai[realtime]` to use this method") from exc

        await self.__client._refresh_api_key()
        auth_headers = self.__client.auth_headers
        if self.__call_id is not omit:
            extra_query = {**extra_query, "call_id": self.__call_id}
        if is_async_azure_client(self.__client):
            model = self.__model
            if not model:
                raise OpenAIError("`model` is required for Azure Realtime API")
            else:
                url, auth_headers = await self.__client._configure_realtime(model, extra_query)
        else:
            url = self._prepare_url().copy_with(
                params={
                    **self.__client.base_url.params,
                    **({"model": self.__model} if self.__model is not omit else {}),
                    **extra_query,
                },
            )
        log.debug("Connecting to %s", url)
        if self.__websocket_connection_options:
            log.debug("Connection options: %s", self.__websocket_connection_options)

        return await connect(
            str(url),
            user_agent_header=self.__client.user_agent,
            additional_headers=_merge_mappings(
                {
                    **auth_headers,
                },
                extra_headers,
            ),
            **self.__websocket_connection_options,
        )

    def _prepare_url(self) -> httpx.URL:
        if self.__client.websocket_base_url is not None:
            base_url = httpx.URL(self.__client.websocket_base_url)
        else:
            scheme = self.__client._base_url.scheme
            ws_scheme = "ws" if scheme == "http" else "wss"
            base_url = self.__client._base_url.copy_with(scheme=ws_scheme)

        merge_raw_path = base_url.raw_path.rstrip(b"/") + b"/realtime"
        return base_url.copy_with(raw_path=merge_raw_path)

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        if self.__connection is not None:
            await self.__connection.close()


class RealtimeConnection:
    """Represents a live WebSocket connection to the Realtime API"""

    session: RealtimeSessionResource
    response: RealtimeResponseResource
    input_audio_buffer: RealtimeInputAudioBufferResource
    conversation: RealtimeConversationResource
    output_audio_buffer: RealtimeOutputAudioBufferResource

    _connection: WebSocketConnection

    def __init__(
        self,
        connection: WebSocketConnection,
        *,
        make_ws: Callable[[Query, Headers], WebSocketConnection] | None = None,
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        extra_query: Query = {},
        extra_headers: Headers = {},
        send_queue: SendQueue | None = None,
    ) -> None:
        self._connection = connection
        self._make_ws = make_ws
        self._on_reconnecting = on_reconnecting
        self._max_retries = max_retries
        self._initial_delay = initial_delay
        self._max_delay = max_delay
        self._extra_query = extra_query
        self._extra_headers = extra_headers
        self._intentionally_closed = False
        self._is_reconnecting = False
        self._send_queue = send_queue or SendQueue()
        self._event_handler_registry = EventHandlerRegistry(use_lock=True)

        self.session = RealtimeSessionResource(self)
        self.response = RealtimeResponseResource(self)
        self.input_audio_buffer = RealtimeInputAudioBufferResource(self)
        self.conversation = RealtimeConversationResource(self)
        self.output_audio_buffer = RealtimeOutputAudioBufferResource(self)

    def __iter__(self) -> Iterator[RealtimeServerEvent]:
        """
        An infinite-iterator that will continue to yield events until
        the connection is closed.
        """
        from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

        while True:
            try:
                yield self.recv()
            except ConnectionClosedOK:
                return
            except ConnectionClosedError as exc:
                if not self._reconnect(exc):
                    unsent = self._send_queue.drain()
                    if unsent:
                        raise WebSocketConnectionClosedError(
                            "WebSocket connection closed with unsent messages",
                            unsent_messages=unsent,
                        ) from exc
                    raise

    def recv(self) -> RealtimeServerEvent:
        """
        Receive the next message from the connection and parses it into a `RealtimeServerEvent` object.

        Canceling this method is safe. There's no risk of losing data.
        """
        return self.parse_event(self.recv_bytes())

    def recv_bytes(self) -> bytes:
        """Receive the next message from the connection as raw bytes.

        Canceling this method is safe. There's no risk of losing data.

        If you want to parse the message into a `RealtimeServerEvent` object like `.recv()` does,
        then you can call `.parse_event(data)`.
        """
        message = self._connection.recv(decode=False)
        log.debug(f"Received WebSocket message: %s", message)
        return message

    def send(self, event: RealtimeClientEvent | RealtimeClientEventParam) -> None:
        data = (
            event.to_json(use_api_names=True, exclude_defaults=True, exclude_unset=True)
            if isinstance(event, BaseModel)
            else json.dumps(maybe_transform(event, RealtimeClientEventParam))
        )
        if self._is_reconnecting:
            self._send_queue.enqueue(data)
            return
        try:
            self._connection.send(data)
        except Exception:
            self._send_queue.enqueue(data)
            raise

    def send_raw(self, data: bytes | str) -> None:
        if self._is_reconnecting:
            raw = data if isinstance(data, str) else data.decode("utf-8")
            self._send_queue.enqueue(raw)
            return
        self._connection.send(data)

    def close(self, *, code: int = 1000, reason: str = "") -> None:
        self._intentionally_closed = True
        self._connection.close(code=code, reason=reason)

    def parse_event(self, data: str | bytes) -> RealtimeServerEvent:
        """
        Converts a raw `str` or `bytes` message into a `RealtimeServerEvent` object.

        This is helpful if you're using `.recv_bytes()`.
        """
        return cast(
            RealtimeServerEvent, construct_type_unchecked(value=json.loads(data), type_=cast(Any, RealtimeServerEvent))
        )

    def _reconnect(self, exc: Exception) -> bool:
        """Attempt to reconnect after a connection failure.

        Returns ``True`` if a new connection was established, ``False`` if the
        caller should re-raise the original exception.
        """
        if self._on_reconnecting is None or self._make_ws is None:
            return False

        from websockets.exceptions import ConnectionClosedError

        close_code = 1006
        if isinstance(exc, ConnectionClosedError) and exc.rcvd is not None:
            close_code = exc.rcvd.code

        if not is_recoverable_close(close_code):
            return False

        self._is_reconnecting = True

        for attempt in range(1, self._max_retries + 1):
            base_delay = min(self._initial_delay * (2 ** (attempt - 1)), self._max_delay)
            jitter = 0.75 + random.random() * 0.25
            delay = base_delay * jitter

            event = ReconnectingEvent(
                attempt=attempt,
                max_attempts=self._max_retries,
                delay=delay,
                close_code=close_code,
                extra_query=self._extra_query,
                extra_headers=self._extra_headers,
            )

            try:
                result = self._on_reconnecting(event)
            except Exception:
                self._is_reconnecting = False
                return False

            if result is not None and result.get("abort"):
                self._is_reconnecting = False
                return False

            if result is not None:
                if "extra_query" in result:
                    self._extra_query = result["extra_query"]
                if "extra_headers" in result:
                    self._extra_headers = result["extra_headers"]

            log.info(
                "Reconnecting to WebSocket API (attempt %d/%d) after %.1fs delay",
                attempt,
                self._max_retries,
                delay,
            )
            time.sleep(delay)

            if self._intentionally_closed:
                self._is_reconnecting = False
                return False

            try:
                self._connection = self._make_ws(self._extra_query, self._extra_headers)
                log.info("Reconnected to WebSocket API")
                self._is_reconnecting = False
                self._flush_send_queue()
                return True
            except Exception:
                pass

        self._is_reconnecting = False
        return False

    def _flush_send_queue(self) -> None:
        """Send all queued messages over the current connection."""
        try:
            self._send_queue.flush_sync(lambda data: self._connection.send(data))
        except Exception:
            log.warning("Failed to flush send queue after reconnect", exc_info=True)

    def on(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[RealtimeConnection, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Adds the handler to the end of the handlers list for the given event type.

        No checks are made to see if the handler has already been added. Multiple calls
        passing the same combination of event type and handler will result in the handler
        being added, and called, multiple times.

        Can be used as a method (returns ``self`` for chaining)::

            connection.on("conversation.created", my_handler)

        Or as a decorator::

            @connection.on("conversation.created")
            def my_handler(event): ...
        """
        if handler is not None:
            self._event_handler_registry.add(event_type, handler)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self._event_handler_registry.add(event_type, fn)
            return fn

        return decorator

    def off(self, event_type: str, handler: Callable[..., Any]) -> RealtimeConnection:
        """Remove a previously registered event handler."""
        self._event_handler_registry.remove(event_type, handler)
        return self

    def once(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[RealtimeConnection, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register a one-time event handler.

        Automatically removed after first invocation.
        """
        if handler is not None:
            self._event_handler_registry.add(event_type, handler, once=True)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self._event_handler_registry.add(event_type, fn, once=True)
            return fn

        return decorator

    def dispatch_events(self) -> None:
        """Run the event loop, dispatching received events to registered handlers.

        Blocks the current thread until the connection is closed. This is the push-based
        alternative to iterating with ``for event in connection``.

        If an ``"error"`` event arrives and no handler is registered for
        ``"error"`` or ``"event"``, an ``OpenAIError`` is raised.
        """
        for event in self:
            event_type = event.type
            specific = self._event_handler_registry.get_handlers(event_type)
            generic = self._event_handler_registry.get_handlers("event")

            if event_type == "error" and not specific and not generic:
                if isinstance(event, RealtimeErrorEvent):
                    raise OpenAIError(f"WebSocket error: {event}")

            for handler in specific:
                handler(event)

            for handler in generic:
                handler(event)


class RealtimeConnectionManager:
    """
    Context manager over a `RealtimeConnection` that is returned by `realtime.connect()`

    This context manager ensures that the connection will be closed when it exits.

    ---

    Note that if your application doesn't work well with the context manager approach then you
    can call the `.enter()` method directly to initiate a connection.

    **Warning**: You must remember to close the connection with `.close()`.

    ```py
    connection = client.realtime.connect(...).enter()
    # ...
    connection.close()
    ```
    """

    def __init__(
        self,
        *,
        client: OpenAI,
        call_id: str | Omit = omit,
        model: str | Omit = omit,
        extra_query: Query,
        extra_headers: Headers,
        websocket_connection_options: WebSocketConnectionOptions,
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        max_queue_size: int = 1_048_576,
    ) -> None:
        self.__client = client
        self.__call_id = call_id
        self.__model = model
        self.__connection: RealtimeConnection | None = None
        self.__extra_query = extra_query
        self.__extra_headers = extra_headers
        self.__websocket_connection_options = websocket_connection_options
        self.__on_reconnecting = on_reconnecting
        self.__max_retries = max_retries
        self.__initial_delay = initial_delay
        self.__max_delay = max_delay
        self.__send_queue = SendQueue(max_bytes=max_queue_size)
        self.__event_handler_registry = EventHandlerRegistry(use_lock=True)

    def send(self, event: RealtimeClientEvent | RealtimeClientEventParam) -> None:
        """Queue a message to be sent when the connection is established.

        This can be called before entering the context manager. Queued messages
        are automatically sent once the WebSocket connection opens.
        """
        data = (
            event.to_json(use_api_names=True, exclude_defaults=True, exclude_unset=True)
            if isinstance(event, BaseModel)
            else json.dumps(event)
        )
        self.__send_queue.enqueue(data)

    def on(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[RealtimeConnectionManager, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register an event handler before the connection is established.

        Handlers are transferred to the connection on enter. Supports the
        same method and decorator forms as ``RealtimeConnection.on``.
        """
        if handler is not None:
            self.__event_handler_registry.add(event_type, handler)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.__event_handler_registry.add(event_type, fn)
            return fn

        return decorator

    def off(self, event_type: str, handler: Callable[..., Any]) -> RealtimeConnectionManager:
        """Remove a previously registered event handler."""
        self.__event_handler_registry.remove(event_type, handler)
        return self

    def once(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[RealtimeConnectionManager, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register a one-time event handler before the connection is established."""
        if handler is not None:
            self.__event_handler_registry.add(event_type, handler, once=True)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.__event_handler_registry.add(event_type, fn, once=True)
            return fn

        return decorator

    def __enter__(self) -> RealtimeConnection:
        """
        If your application doesn't work well with the context manager approach then you
        can call this method directly to initiate a connection.

        **Warning**: You must remember to close the connection with `.close()`.

        ```py
        connection = client.realtime.connect(...).enter()
        # ...
        connection.close()
        ```
        """
        ws = self._connect_ws(self.__extra_query, self.__extra_headers)

        self.__connection = RealtimeConnection(
            ws,
            make_ws=self._connect_ws if self.__on_reconnecting is not None else None,
            on_reconnecting=self.__on_reconnecting,
            max_retries=self.__max_retries,
            initial_delay=self.__initial_delay,
            max_delay=self.__max_delay,
            extra_query=self.__extra_query,
            extra_headers=self.__extra_headers,
            send_queue=self.__send_queue,
        )

        self.__event_handler_registry.merge_into(self.__connection._event_handler_registry)
        self.__connection._flush_send_queue()

        return self.__connection

    enter = __enter__

    def _connect_ws(self, extra_query: Query, extra_headers: Headers) -> WebSocketConnection:
        try:
            from websockets.sync.client import connect
        except ImportError as exc:
            raise OpenAIError("You need to install `openai[realtime]` to use this method") from exc

        self.__client._refresh_api_key()
        auth_headers = self.__client.auth_headers
        if self.__call_id is not omit:
            extra_query = {**extra_query, "call_id": self.__call_id}
        if is_azure_client(self.__client):
            model = self.__model
            if not model:
                raise OpenAIError("`model` is required for Azure Realtime API")
            else:
                url, auth_headers = self.__client._configure_realtime(model, extra_query)
        else:
            url = self._prepare_url().copy_with(
                params={
                    **self.__client.base_url.params,
                    **({"model": self.__model} if self.__model is not omit else {}),
                    **extra_query,
                },
            )
        log.debug("Connecting to %s", url)
        if self.__websocket_connection_options:
            log.debug("Connection options: %s", self.__websocket_connection_options)

        return connect(
            str(url),
            user_agent_header=self.__client.user_agent,
            additional_headers=_merge_mappings(
                {
                    **auth_headers,
                },
                extra_headers,
            ),
            **self.__websocket_connection_options,
        )

    def _prepare_url(self) -> httpx.URL:
        if self.__client.websocket_base_url is not None:
            base_url = httpx.URL(self.__client.websocket_base_url)
        else:
            scheme = self.__client._base_url.scheme
            ws_scheme = "ws" if scheme == "http" else "wss"
            base_url = self.__client._base_url.copy_with(scheme=ws_scheme)

        merge_raw_path = base_url.raw_path.rstrip(b"/") + b"/realtime"
        return base_url.copy_with(raw_path=merge_raw_path)

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        if self.__connection is not None:
            self.__connection.close()


class BaseRealtimeConnectionResource:
    def __init__(self, connection: RealtimeConnection) -> None:
        self._connection = connection


class RealtimeSessionResource(BaseRealtimeConnectionResource):
    def update(self, *, session: session_update_event_param.Session, event_id: str | Omit = omit) -> None:
        """
        Send this event to update the session’s configuration.
        The client may send this event at any time to update any field
        except for `voice` and `model`. `voice` can be updated only if there have been no other audio outputs yet.

        When the server receives a `session.update`, it will respond
        with a `session.updated` event showing the full, effective configuration.
        Only the fields that are present in the `session.update` are updated. To clear a field like
        `instructions`, pass an empty string. To clear a field like `tools`, pass an empty array.
        To clear a field like `turn_detection`, pass `null`.
        """
        self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given({"type": "session.update", "session": session, "event_id": event_id}),
            )
        )


class RealtimeResponseResource(BaseRealtimeConnectionResource):
    def create(self, *, event_id: str | Omit = omit, response: RealtimeResponseCreateParamsParam | Omit = omit) -> None:
        """
        This event instructs the server to create a Response, which means triggering
        model inference. When in Server VAD mode, the server will create Responses
        automatically.

        A Response will include at least one Item, and may have two, in which case
        the second will be a function call. These Items will be appended to the
        conversation history by default.

        The server will respond with a `response.created` event, events for Items
        and content created, and finally a `response.done` event to indicate the
        Response is complete.

        The `response.create` event includes inference configuration like
        `instructions` and `tools`. If these are set, they will override the Session's
        configuration for this Response only.

        Responses can be created out-of-band of the default Conversation, meaning that they can
        have arbitrary input, and it's possible to disable writing the output to the Conversation.
        Only one Response can write to the default Conversation at a time, but otherwise multiple
        Responses can be created in parallel. The `metadata` field is a good way to disambiguate
        multiple simultaneous Responses.

        Clients can set `conversation` to `none` to create a Response that does not write to the default
        Conversation. Arbitrary input can be provided with the `input` field, which is an array accepting
        raw Items and references to existing Items.
        """
        self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given({"type": "response.create", "event_id": event_id, "response": response}),
            )
        )

    def cancel(self, *, event_id: str | Omit = omit, response_id: str | Omit = omit) -> None:
        """Send this event to cancel an in-progress response.

        The server will respond
        with a `response.done` event with a status of `response.status=cancelled`. If
        there is no response to cancel, the server will respond with an error. It's safe
        to call `response.cancel` even if no response is in progress, an error will be
        returned the session will remain unaffected.
        """
        self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given({"type": "response.cancel", "event_id": event_id, "response_id": response_id}),
            )
        )


class RealtimeInputAudioBufferResource(BaseRealtimeConnectionResource):
    def clear(self, *, event_id: str | Omit = omit) -> None:
        """Send this event to clear the audio bytes in the buffer.

        The server will
        respond with an `input_audio_buffer.cleared` event.
        """
        self._connection.send(
            cast(RealtimeClientEventParam, strip_not_given({"type": "input_audio_buffer.clear", "event_id": event_id}))
        )

    def commit(self, *, event_id: str | Omit = omit) -> None:
        """
        Send this event to commit the user input audio buffer, which will create a  new user message item in the conversation. This event will produce an error  if the input audio buffer is empty. When in Server VAD mode, the client does  not need to send this event, the server will commit the audio buffer  automatically.

        Committing the input audio buffer will trigger input audio transcription  (if enabled in session configuration), but it will not create a response  from the model. The server will respond with an `input_audio_buffer.committed` event.
        """
        self._connection.send(
            cast(RealtimeClientEventParam, strip_not_given({"type": "input_audio_buffer.commit", "event_id": event_id}))
        )

    def append(self, *, audio: str, event_id: str | Omit = omit) -> None:
        """Send this event to append audio bytes to the input audio buffer.

        The audio
        buffer is temporary storage you can write to and later commit. A "commit" will create a new
        user message item in the conversation history from the buffer content and clear the buffer.
        Input audio transcription (if enabled) will be generated when the buffer is committed.

        If VAD is enabled the audio buffer is used to detect speech and the server will decide
        when to commit. When Server VAD is disabled, you must commit the audio buffer
        manually. Input audio noise reduction operates on writes to the audio buffer.

        The client may choose how much audio to place in each event up to a maximum
        of 15 MiB, for example streaming smaller chunks from the client may allow the
        VAD to be more responsive. Unlike most other client events, the server will
        not send a confirmation response to this event.
        """
        self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given({"type": "input_audio_buffer.append", "audio": audio, "event_id": event_id}),
            )
        )


class RealtimeConversationResource(BaseRealtimeConnectionResource):
    @cached_property
    def item(self) -> RealtimeConversationItemResource:
        return RealtimeConversationItemResource(self._connection)


class RealtimeConversationItemResource(BaseRealtimeConnectionResource):
    def delete(self, *, item_id: str, event_id: str | Omit = omit) -> None:
        """Send this event when you want to remove any item from the conversation
        history.

        The server will respond with a `conversation.item.deleted` event,
        unless the item does not exist in the conversation history, in which case the
        server will respond with an error.
        """
        self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given({"type": "conversation.item.delete", "item_id": item_id, "event_id": event_id}),
            )
        )

    def create(
        self, *, item: ConversationItemParam, event_id: str | Omit = omit, previous_item_id: str | Omit = omit
    ) -> None:
        """
        Add a new Item to the Conversation's context, including messages, function
        calls, and function call responses. This event can be used both to populate a
        "history" of the conversation and to add new items mid-stream, but has the
        current limitation that it cannot populate assistant audio messages.

        If successful, the server will respond with a `conversation.item.created`
        event, otherwise an `error` event will be sent.
        """
        self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given(
                    {
                        "type": "conversation.item.create",
                        "item": item,
                        "event_id": event_id,
                        "previous_item_id": previous_item_id,
                    }
                ),
            )
        )

    def truncate(self, *, audio_end_ms: int, content_index: int, item_id: str, event_id: str | Omit = omit) -> None:
        """Send this event to truncate a previous assistant message’s audio.

        The server
        will produce audio faster than realtime, so this event is useful when the user
        interrupts to truncate audio that has already been sent to the client but not
        yet played. This will synchronize the server's understanding of the audio with
        the client's playback.

        Truncating audio will delete the server-side text transcript to ensure there
        is not text in the context that hasn't been heard by the user.

        If successful, the server will respond with a `conversation.item.truncated`
        event.
        """
        self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given(
                    {
                        "type": "conversation.item.truncate",
                        "audio_end_ms": audio_end_ms,
                        "content_index": content_index,
                        "item_id": item_id,
                        "event_id": event_id,
                    }
                ),
            )
        )

    def retrieve(self, *, item_id: str, event_id: str | Omit = omit) -> None:
        """
        Send this event when you want to retrieve the server's representation of a specific item in the conversation history. This is useful, for example, to inspect user audio after noise cancellation and VAD.
        The server will respond with a `conversation.item.retrieved` event,
        unless the item does not exist in the conversation history, in which case the
        server will respond with an error.
        """
        self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given({"type": "conversation.item.retrieve", "item_id": item_id, "event_id": event_id}),
            )
        )


class RealtimeOutputAudioBufferResource(BaseRealtimeConnectionResource):
    def clear(self, *, event_id: str | Omit = omit) -> None:
        """**WebRTC/SIP Only:** Emit to cut off the current audio response.

        This will trigger the server to
        stop generating audio and emit a `output_audio_buffer.cleared` event. This
        event should be preceded by a `response.cancel` client event to stop the
        generation of the current response.
        [Learn more](https://platform.openai.com/docs/guides/realtime-conversations#client-and-server-events-for-audio-in-webrtc).
        """
        self._connection.send(
            cast(RealtimeClientEventParam, strip_not_given({"type": "output_audio_buffer.clear", "event_id": event_id}))
        )


class BaseAsyncRealtimeConnectionResource:
    def __init__(self, connection: AsyncRealtimeConnection) -> None:
        self._connection = connection


class AsyncRealtimeSessionResource(BaseAsyncRealtimeConnectionResource):
    async def update(self, *, session: session_update_event_param.Session, event_id: str | Omit = omit) -> None:
        """
        Send this event to update the session’s configuration.
        The client may send this event at any time to update any field
        except for `voice` and `model`. `voice` can be updated only if there have been no other audio outputs yet.

        When the server receives a `session.update`, it will respond
        with a `session.updated` event showing the full, effective configuration.
        Only the fields that are present in the `session.update` are updated. To clear a field like
        `instructions`, pass an empty string. To clear a field like `tools`, pass an empty array.
        To clear a field like `turn_detection`, pass `null`.
        """
        await self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given({"type": "session.update", "session": session, "event_id": event_id}),
            )
        )


class AsyncRealtimeResponseResource(BaseAsyncRealtimeConnectionResource):
    async def create(
        self, *, event_id: str | Omit = omit, response: RealtimeResponseCreateParamsParam | Omit = omit
    ) -> None:
        """
        This event instructs the server to create a Response, which means triggering
        model inference. When in Server VAD mode, the server will create Responses
        automatically.

        A Response will include at least one Item, and may have two, in which case
        the second will be a function call. These Items will be appended to the
        conversation history by default.

        The server will respond with a `response.created` event, events for Items
        and content created, and finally a `response.done` event to indicate the
        Response is complete.

        The `response.create` event includes inference configuration like
        `instructions` and `tools`. If these are set, they will override the Session's
        configuration for this Response only.

        Responses can be created out-of-band of the default Conversation, meaning that they can
        have arbitrary input, and it's possible to disable writing the output to the Conversation.
        Only one Response can write to the default Conversation at a time, but otherwise multiple
        Responses can be created in parallel. The `metadata` field is a good way to disambiguate
        multiple simultaneous Responses.

        Clients can set `conversation` to `none` to create a Response that does not write to the default
        Conversation. Arbitrary input can be provided with the `input` field, which is an array accepting
        raw Items and references to existing Items.
        """
        await self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given({"type": "response.create", "event_id": event_id, "response": response}),
            )
        )

    async def cancel(self, *, event_id: str | Omit = omit, response_id: str | Omit = omit) -> None:
        """Send this event to cancel an in-progress response.

        The server will respond
        with a `response.done` event with a status of `response.status=cancelled`. If
        there is no response to cancel, the server will respond with an error. It's safe
        to call `response.cancel` even if no response is in progress, an error will be
        returned the session will remain unaffected.
        """
        await self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given({"type": "response.cancel", "event_id": event_id, "response_id": response_id}),
            )
        )


class AsyncRealtimeInputAudioBufferResource(BaseAsyncRealtimeConnectionResource):
    async def clear(self, *, event_id: str | Omit = omit) -> None:
        """Send this event to clear the audio bytes in the buffer.

        The server will
        respond with an `input_audio_buffer.cleared` event.
        """
        await self._connection.send(
            cast(RealtimeClientEventParam, strip_not_given({"type": "input_audio_buffer.clear", "event_id": event_id}))
        )

    async def commit(self, *, event_id: str | Omit = omit) -> None:
        """
        Send this event to commit the user input audio buffer, which will create a  new user message item in the conversation. This event will produce an error  if the input audio buffer is empty. When in Server VAD mode, the client does  not need to send this event, the server will commit the audio buffer  automatically.

        Committing the input audio buffer will trigger input audio transcription  (if enabled in session configuration), but it will not create a response  from the model. The server will respond with an `input_audio_buffer.committed` event.
        """
        await self._connection.send(
            cast(RealtimeClientEventParam, strip_not_given({"type": "input_audio_buffer.commit", "event_id": event_id}))
        )

    async def append(self, *, audio: str, event_id: str | Omit = omit) -> None:
        """Send this event to append audio bytes to the input audio buffer.

        The audio
        buffer is temporary storage you can write to and later commit. A "commit" will create a new
        user message item in the conversation history from the buffer content and clear the buffer.
        Input audio transcription (if enabled) will be generated when the buffer is committed.

        If VAD is enabled the audio buffer is used to detect speech and the server will decide
        when to commit. When Server VAD is disabled, you must commit the audio buffer
        manually. Input audio noise reduction operates on writes to the audio buffer.

        The client may choose how much audio to place in each event up to a maximum
        of 15 MiB, for example streaming smaller chunks from the client may allow the
        VAD to be more responsive. Unlike most other client events, the server will
        not send a confirmation response to this event.
        """
        await self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given({"type": "input_audio_buffer.append", "audio": audio, "event_id": event_id}),
            )
        )


class AsyncRealtimeConversationResource(BaseAsyncRealtimeConnectionResource):
    @cached_property
    def item(self) -> AsyncRealtimeConversationItemResource:
        return AsyncRealtimeConversationItemResource(self._connection)


class AsyncRealtimeConversationItemResource(BaseAsyncRealtimeConnectionResource):
    async def delete(self, *, item_id: str, event_id: str | Omit = omit) -> None:
        """Send this event when you want to remove any item from the conversation
        history.

        The server will respond with a `conversation.item.deleted` event,
        unless the item does not exist in the conversation history, in which case the
        server will respond with an error.
        """
        await self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given({"type": "conversation.item.delete", "item_id": item_id, "event_id": event_id}),
            )
        )

    async def create(
        self, *, item: ConversationItemParam, event_id: str | Omit = omit, previous_item_id: str | Omit = omit
    ) -> None:
        """
        Add a new Item to the Conversation's context, including messages, function
        calls, and function call responses. This event can be used both to populate a
        "history" of the conversation and to add new items mid-stream, but has the
        current limitation that it cannot populate assistant audio messages.

        If successful, the server will respond with a `conversation.item.created`
        event, otherwise an `error` event will be sent.
        """
        await self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given(
                    {
                        "type": "conversation.item.create",
                        "item": item,
                        "event_id": event_id,
                        "previous_item_id": previous_item_id,
                    }
                ),
            )
        )

    async def truncate(
        self, *, audio_end_ms: int, content_index: int, item_id: str, event_id: str | Omit = omit
    ) -> None:
        """Send this event to truncate a previous assistant message’s audio.

        The server
        will produce audio faster than realtime, so this event is useful when the user
        interrupts to truncate audio that has already been sent to the client but not
        yet played. This will synchronize the server's understanding of the audio with
        the client's playback.

        Truncating audio will delete the server-side text transcript to ensure there
        is not text in the context that hasn't been heard by the user.

        If successful, the server will respond with a `conversation.item.truncated`
        event.
        """
        await self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given(
                    {
                        "type": "conversation.item.truncate",
                        "audio_end_ms": audio_end_ms,
                        "content_index": content_index,
                        "item_id": item_id,
                        "event_id": event_id,
                    }
                ),
            )
        )

    async def retrieve(self, *, item_id: str, event_id: str | Omit = omit) -> None:
        """
        Send this event when you want to retrieve the server's representation of a specific item in the conversation history. This is useful, for example, to inspect user audio after noise cancellation and VAD.
        The server will respond with a `conversation.item.retrieved` event,
        unless the item does not exist in the conversation history, in which case the
        server will respond with an error.
        """
        await self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given({"type": "conversation.item.retrieve", "item_id": item_id, "event_id": event_id}),
            )
        )


class AsyncRealtimeOutputAudioBufferResource(BaseAsyncRealtimeConnectionResource):
    async def clear(self, *, event_id: str | Omit = omit) -> None:
        """**WebRTC/SIP Only:** Emit to cut off the current audio response.

        This will trigger the server to
        stop generating audio and emit a `output_audio_buffer.cleared` event. This
        event should be preceded by a `response.cancel` client event to stop the
        generation of the current response.
        [Learn more](https://platform.openai.com/docs/guides/realtime-conversations#client-and-server-events-for-audio-in-webrtc).
        """
        await self._connection.send(
            cast(RealtimeClientEventParam, strip_not_given({"type": "output_audio_buffer.clear", "event_id": event_id}))
        )
