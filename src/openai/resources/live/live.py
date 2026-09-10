# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import json
import time
import random
import logging
from types import TracebackType
from typing import TYPE_CHECKING, Any, Union, Callable, Iterator, Optional, Awaitable, cast
from typing_extensions import AsyncIterator

import httpx2
from pydantic import BaseModel

from ... import _legacy_response
from .forks import Forks, AsyncForks
from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, strip_not_given, async_maybe_transform
from .sessions import (
    Sessions,
    AsyncSessions,
    SessionsWithRawResponse,
    AsyncSessionsWithRawResponse,
    SessionsWithStreamingResponse,
    AsyncSessionsWithStreamingResponse,
)
from .sideband import Sideband, AsyncSideband
from ..._compat import cached_property
from ..._models import construct_type_unchecked
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ...types.live import live_create_params
from ..._exceptions import OpenAIError, WebSocketConnectionClosedError
from ..._send_queue import SendQueue
from ..._base_client import _merge_mappings, make_request_options
from ..._event_handler import EventHandlerRegistry
from ...types.live.error_event import ErrorEvent
from ...types.live.client_event import ClientEvent
from ...types.live.server_event import ServerEvent
from ...types.websocket_reconnection import ReconnectingEvent, ReconnectingOverrides, is_recoverable_close
from ...types.live.client_event_param import ClientEventParam
from ...types.live.live_create_response import LiveCreateResponse
from ...types.live.session_config_param import SessionConfigParam
from ...types.websocket_connection_options import WebSocketConnectionOptions
from ...types.live.media_session_config_param import MediaSessionConfigParam
from ...types.live.session_update_config_param import SessionUpdateConfigParam
from ...types.responses.response_input_item_param import ResponseInputItemParam

if TYPE_CHECKING:
    from websockets.sync.client import ClientConnection as WebSocketConnection
    from websockets.asyncio.client import ClientConnection as AsyncWebSocketConnection

    from ..._client import OpenAI, AsyncOpenAI

__all__ = ["Live", "AsyncLive"]

log: logging.Logger = logging.getLogger(__name__)


class Live(SyncAPIResource):
    @cached_property
    def sideband(self) -> Sideband:
        return Sideband(self._client)

    @cached_property
    def forks(self) -> Forks:
        return Forks(self._client)

    @cached_property
    def sessions(self) -> Sessions:
        return Sessions(self._client)

    @cached_property
    def with_raw_response(self) -> LiveWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return LiveWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LiveWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return LiveWithStreamingResponse(self)

    def create(
        self,
        *,
        session: MediaSessionConfigParam,
        transport: live_create_params.Transport,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> LiveCreateResponse:
        """Create a Live WebRTC session.

        Start with the
        [Live prompting guide](https://developers.openai.com/api/docs/guides/live-prompting).

        Args:
          session: Startup configuration for the Live session.

          transport: WebRTC transport with the browser's SDP offer.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/live/sessions",
            body=maybe_transform(
                {
                    "session": session,
                    "transport": transport,
                },
                live_create_params.LiveCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=LiveCreateResponse,
        )

    def connect(
        self,
        extra_query: Query = {},
        extra_headers: Headers = {},
        websocket_connection_options: WebSocketConnectionOptions = {},
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        max_queue_size: int = 1_048_576,
    ) -> LiveConnectionManager:
        """Connect to Live without query parameters.

        Send session.start with model and session configuration, then wait for session.started. Follow the [Live prompting guide](https://developers.openai.com/api/docs/guides/live-prompting) before writing instructions.
        """
        return LiveConnectionManager(
            client=self._client,
            extra_query=extra_query,
            extra_headers=extra_headers,
            websocket_connection_options=websocket_connection_options,
            on_reconnecting=on_reconnecting,
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay,
            max_queue_size=max_queue_size,
        )


class AsyncLive(AsyncAPIResource):
    @cached_property
    def sideband(self) -> AsyncSideband:
        return AsyncSideband(self._client)

    @cached_property
    def forks(self) -> AsyncForks:
        return AsyncForks(self._client)

    @cached_property
    def sessions(self) -> AsyncSessions:
        return AsyncSessions(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncLiveWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncLiveWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLiveWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncLiveWithStreamingResponse(self)

    async def create(
        self,
        *,
        session: MediaSessionConfigParam,
        transport: live_create_params.Transport,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> LiveCreateResponse:
        """Create a Live WebRTC session.

        Start with the
        [Live prompting guide](https://developers.openai.com/api/docs/guides/live-prompting).

        Args:
          session: Startup configuration for the Live session.

          transport: WebRTC transport with the browser's SDP offer.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/live/sessions",
            body=await async_maybe_transform(
                {
                    "session": session,
                    "transport": transport,
                },
                live_create_params.LiveCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=LiveCreateResponse,
        )

    def connect(
        self,
        extra_query: Query = {},
        extra_headers: Headers = {},
        websocket_connection_options: WebSocketConnectionOptions = {},
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        max_queue_size: int = 1_048_576,
    ) -> AsyncLiveConnectionManager:
        """Connect to Live without query parameters.

        Send session.start with model and session configuration, then wait for session.started. Follow the [Live prompting guide](https://developers.openai.com/api/docs/guides/live-prompting) before writing instructions.
        """
        return AsyncLiveConnectionManager(
            client=self._client,
            extra_query=extra_query,
            extra_headers=extra_headers,
            websocket_connection_options=websocket_connection_options,
            on_reconnecting=on_reconnecting,
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay,
            max_queue_size=max_queue_size,
        )


class LiveWithRawResponse:
    def __init__(self, live: Live) -> None:
        self._live = live

        self.create = _legacy_response.to_raw_response_wrapper(
            live.create,
        )

    @cached_property
    def sessions(self) -> SessionsWithRawResponse:
        return SessionsWithRawResponse(self._live.sessions)


class AsyncLiveWithRawResponse:
    def __init__(self, live: AsyncLive) -> None:
        self._live = live

        self.create = _legacy_response.async_to_raw_response_wrapper(
            live.create,
        )

    @cached_property
    def sessions(self) -> AsyncSessionsWithRawResponse:
        return AsyncSessionsWithRawResponse(self._live.sessions)


class LiveWithStreamingResponse:
    def __init__(self, live: Live) -> None:
        self._live = live

        self.create = to_streamed_response_wrapper(
            live.create,
        )

    @cached_property
    def sessions(self) -> SessionsWithStreamingResponse:
        return SessionsWithStreamingResponse(self._live.sessions)


class AsyncLiveWithStreamingResponse:
    def __init__(self, live: AsyncLive) -> None:
        self._live = live

        self.create = async_to_streamed_response_wrapper(
            live.create,
        )

    @cached_property
    def sessions(self) -> AsyncSessionsWithStreamingResponse:
        return AsyncSessionsWithStreamingResponse(self._live.sessions)


class AsyncLiveConnection:
    """Represents a live WebSocket connection to the Live API"""

    session: AsyncLiveSessionResource
    response: AsyncLiveResponseResource

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
        self._reconnect_attempt = 0
        self._initial_delay = initial_delay
        self._max_delay = max_delay
        self._extra_query = extra_query
        self._extra_headers = extra_headers
        self._intentionally_closed = False
        self._is_reconnecting = False
        self._send_queue = send_queue or SendQueue()
        self._event_handler_registry = EventHandlerRegistry(use_lock=False)

        self.session = AsyncLiveSessionResource(self)
        self.response = AsyncLiveResponseResource(self)

    async def __aiter__(self) -> AsyncIterator[ServerEvent]:
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

    async def recv(self) -> ServerEvent:
        """
        Receive the next message from the connection and parses it into a `ServerEvent` object.

        Canceling this method is safe. There's no risk of losing data.
        """
        event = self.parse_event(await self.recv_bytes())
        event_type = (
            cast("dict[str, object]", event).get("type")
            if isinstance(cast(object, event), dict)
            else getattr(event, "type", None)
        )
        # A successful upgrade can still be followed by an admission error.
        # Reset the budget only after receiving a non-error application event.
        if isinstance(event_type, str) and event_type and event_type != "error":
            self._reconnect_attempt = 0
        return event

    async def recv_bytes(self) -> bytes:
        """Receive the next message from the connection as raw bytes.

        Canceling this method is safe. There's no risk of losing data.

        If you want to parse the message into a `ServerEvent` object like `.recv()` does,
        then you can call `.parse_event(data)`.
        """
        message = await self._connection.recv(decode=False)
        log.debug(f"Received WebSocket message: %s", message)
        if self._reconnect_attempt:
            # Account for raw application progress without changing frame delivery.
            try:
                event_data: object = json.loads(message)
            except (ValueError, RecursionError):
                return message
            event_type = cast("dict[str, object]", event_data).get("type") if isinstance(event_data, dict) else None
            if isinstance(event_type, str) and event_type and event_type != "error":
                self._reconnect_attempt = 0
        return message

    async def send(self, event: ClientEvent | ClientEventParam) -> None:
        data = (
            event.to_json(use_api_names=True, exclude_defaults=True, exclude_unset=True)
            if isinstance(event, BaseModel)
            else json.dumps(await async_maybe_transform(event, ClientEventParam))
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

    def parse_event(self, data: str | bytes) -> ServerEvent:
        """
        Converts a raw `str` or `bytes` message into a `ServerEvent` object.

        This is helpful if you're using `.recv_bytes()`.
        """
        return cast(ServerEvent, construct_type_unchecked(value=json.loads(data), type_=cast(Any, ServerEvent)))

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

        for attempt in range(self._reconnect_attempt + 1, self._max_retries + 1):
            self._reconnect_attempt = attempt
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
    ) -> Union[AsyncLiveConnection, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Adds the handler to the end of the handlers list for the given event type.

        No checks are made to see if the handler has already been added. Multiple calls
        passing the same combination of event type and handler will result in the handler
        being added, and called, multiple times.

        Can be used as a method (returns ``self`` for chaining)::

            connection.on("session.started", my_handler)

        Or as a decorator::

            @connection.on("session.started")
            async def my_handler(event): ...
        """
        if handler is not None:
            self._event_handler_registry.add(event_type, handler)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self._event_handler_registry.add(event_type, fn)
            return fn

        return decorator

    def off(self, event_type: str, handler: Callable[..., Any]) -> AsyncLiveConnection:
        """Remove a previously registered event handler."""
        self._event_handler_registry.remove(event_type, handler)
        return self

    def once(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[AsyncLiveConnection, Callable[[Callable[..., Any]], Callable[..., Any]]]:
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
                if isinstance(event, ErrorEvent):
                    raise OpenAIError(f"WebSocket error: {event}")

            for handler in specific:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result

            for handler in generic:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result


class AsyncLiveConnectionManager:
    """
    Context manager over a `AsyncLiveConnection` that is returned by `live.connect()`

    This context manager ensures that the connection will be closed when it exits.

    ---

    Note that if your application doesn't work well with the context manager approach then you
    can call the `.enter()` method directly to initiate a connection.

    **Warning**: You must remember to close the connection with `.close()`.

    ```py
    connection = await client.live.connect(...).enter()
    # ...
    await connection.close()
    ```
    """

    def __init__(
        self,
        *,
        client: AsyncOpenAI,
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
        self.__connection: AsyncLiveConnection | None = None
        self.__extra_query = extra_query
        self.__extra_headers = extra_headers
        self.__websocket_connection_options = websocket_connection_options
        self.__on_reconnecting = on_reconnecting
        self.__max_retries = max_retries
        self.__initial_delay = initial_delay
        self.__max_delay = max_delay
        self.__send_queue = SendQueue(max_bytes=max_queue_size)
        self.__event_handler_registry = EventHandlerRegistry(use_lock=False)

    def send(self, event: ClientEvent | ClientEventParam) -> None:
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
    ) -> Union[AsyncLiveConnectionManager, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register an event handler before the connection is established.

        Handlers are transferred to the connection on enter. Supports the
        same method and decorator forms as ``AsyncLiveConnection.on``.
        """
        if handler is not None:
            self.__event_handler_registry.add(event_type, handler)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.__event_handler_registry.add(event_type, fn)
            return fn

        return decorator

    def off(self, event_type: str, handler: Callable[..., Any]) -> AsyncLiveConnectionManager:
        """Remove a previously registered event handler."""
        self.__event_handler_registry.remove(event_type, handler)
        return self

    def once(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[AsyncLiveConnectionManager, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register a one-time event handler before the connection is established."""
        if handler is not None:
            self.__event_handler_registry.add(event_type, handler, once=True)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.__event_handler_registry.add(event_type, fn, once=True)
            return fn

        return decorator

    async def __aenter__(self) -> AsyncLiveConnection:
        """
        If your application doesn't work well with the context manager approach then you
        can call this method directly to initiate a connection.

        **Warning**: You must remember to close the connection with `.close()`.

        ```py
        connection = await client.live.connect(...).enter()
        # ...
        await connection.close()
        ```
        """
        ws = await self._connect_ws(self.__extra_query, self.__extra_headers)

        self.__connection = AsyncLiveConnection(
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
            from ...lib._websocket import _WebSocketConnect as connect
        except ImportError as exc:
            raise OpenAIError("You need to install `openai[realtime]` to use this method") from exc

        url = self._prepare_url().copy_with(
            params={
                **self.__client.base_url.params,
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
                    **self.__client.auth_headers,
                },
                extra_headers,
            ),
            **self.__websocket_connection_options,
        )

    def _prepare_url(self) -> httpx2.URL:
        if self.__client.websocket_base_url is not None:
            base_url = httpx2.URL(self.__client.websocket_base_url)
        else:
            scheme = self.__client._base_url.scheme
            ws_scheme = "ws" if scheme == "http" else "wss"
            base_url = self.__client._base_url.copy_with(scheme=ws_scheme)

        merge_raw_path = base_url.raw_path.rstrip(b"/") + b"/live/sessions"
        return base_url.copy_with(raw_path=merge_raw_path)

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        if self.__connection is not None:
            await self.__connection.close()


class LiveConnection:
    """Represents a live WebSocket connection to the Live API"""

    session: LiveSessionResource
    response: LiveResponseResource

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
        self._reconnect_attempt = 0
        self._initial_delay = initial_delay
        self._max_delay = max_delay
        self._extra_query = extra_query
        self._extra_headers = extra_headers
        self._intentionally_closed = False
        self._is_reconnecting = False
        self._send_queue = send_queue or SendQueue()
        self._event_handler_registry = EventHandlerRegistry(use_lock=True)

        self.session = LiveSessionResource(self)
        self.response = LiveResponseResource(self)

    def __iter__(self) -> Iterator[ServerEvent]:
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

    def recv(self) -> ServerEvent:
        """
        Receive the next message from the connection and parses it into a `ServerEvent` object.

        Canceling this method is safe. There's no risk of losing data.
        """
        event = self.parse_event(self.recv_bytes())
        event_type = (
            cast("dict[str, object]", event).get("type")
            if isinstance(cast(object, event), dict)
            else getattr(event, "type", None)
        )
        # A successful upgrade can still be followed by an admission error.
        # Reset the budget only after receiving a non-error application event.
        if isinstance(event_type, str) and event_type and event_type != "error":
            self._reconnect_attempt = 0
        return event

    def recv_bytes(self) -> bytes:
        """Receive the next message from the connection as raw bytes.

        Canceling this method is safe. There's no risk of losing data.

        If you want to parse the message into a `ServerEvent` object like `.recv()` does,
        then you can call `.parse_event(data)`.
        """
        message = self._connection.recv(decode=False)
        log.debug(f"Received WebSocket message: %s", message)
        if self._reconnect_attempt:
            # Account for raw application progress without changing frame delivery.
            try:
                event_data: object = json.loads(message)
            except (ValueError, RecursionError):
                return message
            event_type = cast("dict[str, object]", event_data).get("type") if isinstance(event_data, dict) else None
            if isinstance(event_type, str) and event_type and event_type != "error":
                self._reconnect_attempt = 0
        return message

    def send(self, event: ClientEvent | ClientEventParam) -> None:
        data = (
            event.to_json(use_api_names=True, exclude_defaults=True, exclude_unset=True)
            if isinstance(event, BaseModel)
            else json.dumps(maybe_transform(event, ClientEventParam))
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

    def parse_event(self, data: str | bytes) -> ServerEvent:
        """
        Converts a raw `str` or `bytes` message into a `ServerEvent` object.

        This is helpful if you're using `.recv_bytes()`.
        """
        return cast(ServerEvent, construct_type_unchecked(value=json.loads(data), type_=cast(Any, ServerEvent)))

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

        for attempt in range(self._reconnect_attempt + 1, self._max_retries + 1):
            self._reconnect_attempt = attempt
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
    ) -> Union[LiveConnection, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Adds the handler to the end of the handlers list for the given event type.

        No checks are made to see if the handler has already been added. Multiple calls
        passing the same combination of event type and handler will result in the handler
        being added, and called, multiple times.

        Can be used as a method (returns ``self`` for chaining)::

            connection.on("session.started", my_handler)

        Or as a decorator::

            @connection.on("session.started")
            def my_handler(event): ...
        """
        if handler is not None:
            self._event_handler_registry.add(event_type, handler)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self._event_handler_registry.add(event_type, fn)
            return fn

        return decorator

    def off(self, event_type: str, handler: Callable[..., Any]) -> LiveConnection:
        """Remove a previously registered event handler."""
        self._event_handler_registry.remove(event_type, handler)
        return self

    def once(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[LiveConnection, Callable[[Callable[..., Any]], Callable[..., Any]]]:
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
                if isinstance(event, ErrorEvent):
                    raise OpenAIError(f"WebSocket error: {event}")

            for handler in specific:
                handler(event)

            for handler in generic:
                handler(event)


class LiveConnectionManager:
    """Context manager over a `LiveConnection` that is returned by `live.connect()`

    This context manager ensures that the connection will be closed when it exits.

    ---

    Note that if your application doesn't work well with the context manager approach then you
    can call the `.enter()` method directly to initiate a connection.

    **Warning**: You must remember to close the connection with `.close()`.

    ```py
    connection = client.live.connect(...).enter()
    # ...
    connection.close()
    ```
    """

    def __init__(
        self,
        *,
        client: OpenAI,
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
        self.__connection: LiveConnection | None = None
        self.__extra_query = extra_query
        self.__extra_headers = extra_headers
        self.__websocket_connection_options = websocket_connection_options
        self.__on_reconnecting = on_reconnecting
        self.__max_retries = max_retries
        self.__initial_delay = initial_delay
        self.__max_delay = max_delay
        self.__send_queue = SendQueue(max_bytes=max_queue_size)
        self.__event_handler_registry = EventHandlerRegistry(use_lock=True)

    def send(self, event: ClientEvent | ClientEventParam) -> None:
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
    ) -> Union[LiveConnectionManager, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register an event handler before the connection is established.

        Handlers are transferred to the connection on enter. Supports the
        same method and decorator forms as ``LiveConnection.on``.
        """
        if handler is not None:
            self.__event_handler_registry.add(event_type, handler)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.__event_handler_registry.add(event_type, fn)
            return fn

        return decorator

    def off(self, event_type: str, handler: Callable[..., Any]) -> LiveConnectionManager:
        """Remove a previously registered event handler."""
        self.__event_handler_registry.remove(event_type, handler)
        return self

    def once(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[LiveConnectionManager, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register a one-time event handler before the connection is established."""
        if handler is not None:
            self.__event_handler_registry.add(event_type, handler, once=True)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.__event_handler_registry.add(event_type, fn, once=True)
            return fn

        return decorator

    def __enter__(self) -> LiveConnection:
        """
        If your application doesn't work well with the context manager approach then you
        can call this method directly to initiate a connection.

        **Warning**: You must remember to close the connection with `.close()`.

        ```py
        connection = client.live.connect(...).enter()
        # ...
        connection.close()
        ```
        """
        ws = self._connect_ws(self.__extra_query, self.__extra_headers)

        self.__connection = LiveConnection(
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

        url = self._prepare_url().copy_with(
            params={
                **self.__client.base_url.params,
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
                    **self.__client.auth_headers,
                },
                extra_headers,
            ),
            **self.__websocket_connection_options,
        )

    def _prepare_url(self) -> httpx2.URL:
        if self.__client.websocket_base_url is not None:
            base_url = httpx2.URL(self.__client.websocket_base_url)
        else:
            scheme = self.__client._base_url.scheme
            ws_scheme = "ws" if scheme == "http" else "wss"
            base_url = self.__client._base_url.copy_with(scheme=ws_scheme)

        merge_raw_path = base_url.raw_path.rstrip(b"/") + b"/live/sessions"
        return base_url.copy_with(raw_path=merge_raw_path)

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        if self.__connection is not None:
            self.__connection.close()


class BaseLiveConnectionResource:
    def __init__(self, connection: LiveConnection) -> None:
        self._connection = connection


class LiveSessionResource(BaseLiveConnectionResource):
    @cached_property
    def commentary(self) -> LiveSessionCommentaryResource:
        return LiveSessionCommentaryResource(self._connection)

    @cached_property
    def input_audio(self) -> LiveSessionInputAudioResource:
        return LiveSessionInputAudioResource(self._connection)

    @cached_property
    def instructions(self) -> LiveSessionInstructionsResource:
        return LiveSessionInstructionsResource(self._connection)

    @cached_property
    def thinking(self) -> LiveSessionThinkingResource:
        return LiveSessionThinkingResource(self._connection)

    def close(self, *, event_id: Optional[str] | Omit = omit) -> None:
        """Request that the Live session close.

        The terminal `session.closed` event contains the close reason and final usage.
        """
        self._connection.send(cast(ClientEventParam, strip_not_given({"type": "session.close", "event_id": event_id})))

    def update(self, *, session: SessionUpdateConfigParam, event_id: Optional[str] | Omit = omit) -> None:
        """Update the delegation settings of an active Live session.

        The server acknowledges accepted changes with `session.updated`.
        """
        self._connection.send(
            cast(
                ClientEventParam, strip_not_given({"type": "session.update", "session": session, "event_id": event_id})
            )
        )

    def start(self, *, session: SessionConfigParam, event_id: Optional[str] | Omit = omit) -> None:
        """Start a Live session on a primary WebSocket.

        Send this event before other commands and wait for `session.started`.
        """
        self._connection.send(
            cast(ClientEventParam, strip_not_given({"type": "session.start", "session": session, "event_id": event_id}))
        )


class LiveSessionCommentaryResource(BaseLiveConnectionResource):
    def append(self, *, content: str, delegation_id: Optional[str], event_id: Optional[str] | Omit = omit) -> None:
        """
        Provide context the Live model can communicate to the user, optionally for an existing client delegation.
        """
        self._connection.send(
            cast(
                ClientEventParam,
                strip_not_given(
                    {
                        "type": "session.commentary.append",
                        "content": content,
                        "delegation_id": delegation_id,
                        "event_id": event_id,
                    }
                ),
            )
        )


class LiveSessionInputAudioResource(BaseLiveConnectionResource):
    def append(self, *, audio: str, event_id: Optional[str] | Omit = omit) -> None:
        """Send audio to a Live session over its primary WebSocket.

        WebRTC and SIP sessions send audio over their media transport.
        """
        self._connection.send(
            cast(
                ClientEventParam,
                strip_not_given({"type": "session.input_audio.append", "audio": audio, "event_id": event_id}),
            )
        )

    def mute(self, *, event_id: Optional[str] | Omit = omit) -> None:
        """Mute audio input to the Live model without closing the session.

        The server acknowledges with `session.input_audio.muted`.
        """
        self._connection.send(
            cast(ClientEventParam, strip_not_given({"type": "session.input_audio.mute", "event_id": event_id}))
        )

    def unmute(self, *, event_id: Optional[str] | Omit = omit) -> None:
        """Resume audio input to a Live model after muting it.

        The server acknowledges with `session.input_audio.unmuted`.
        """
        self._connection.send(
            cast(ClientEventParam, strip_not_given({"type": "session.input_audio.unmute", "event_id": event_id}))
        )


class LiveSessionInstructionsResource(BaseLiveConnectionResource):
    def append(self, *, content: str, delegation_id: Optional[str], event_id: Optional[str] | Omit = omit) -> None:
        """
        Append instructions to the Live conversation while it is running, optionally associating them with an existing client delegation.
        """
        self._connection.send(
            cast(
                ClientEventParam,
                strip_not_given(
                    {
                        "type": "session.instructions.append",
                        "content": content,
                        "delegation_id": delegation_id,
                        "event_id": event_id,
                    }
                ),
            )
        )


class LiveSessionThinkingResource(BaseLiveConnectionResource):
    def append(self, *, content: str, delegation_id: Optional[str], event_id: Optional[str] | Omit = omit) -> None:
        """
        Provide silent reasoning or progress context to the Live model, optionally for an existing client delegation.
        """
        self._connection.send(
            cast(
                ClientEventParam,
                strip_not_given(
                    {
                        "type": "session.thinking.append",
                        "content": content,
                        "delegation_id": delegation_id,
                        "event_id": event_id,
                    }
                ),
            )
        )


class LiveResponseResource(BaseLiveConnectionResource):
    @cached_property
    def item(self) -> LiveResponseItemResource:
        return LiveResponseItemResource(self._connection)

    def create(self, *, event_id: Optional[str] | Omit = omit) -> None:
        """
        Request a response from the Live session’s Responses backend, or continue a
        delegated response waiting for tool results.

        Requires Responses delegation.
        """
        self._connection.send(
            cast(ClientEventParam, strip_not_given({"type": "response.create", "event_id": event_id}))
        )


class LiveResponseItemResource(BaseLiveConnectionResource):
    def create(self, *, item: ResponseInputItemParam, event_id: Optional[str] | Omit = omit) -> None:
        """Add an input item to the Live session’s Responses backend.

        Requires Responses delegation; use `response.create` to request a response.
        """
        self._connection.send(
            cast(
                ClientEventParam, strip_not_given({"type": "response.item.create", "item": item, "event_id": event_id})
            )
        )


class BaseAsyncLiveConnectionResource:
    def __init__(self, connection: AsyncLiveConnection) -> None:
        self._connection = connection


class AsyncLiveSessionResource(BaseAsyncLiveConnectionResource):
    @cached_property
    def commentary(self) -> AsyncLiveSessionCommentaryResource:
        return AsyncLiveSessionCommentaryResource(self._connection)

    @cached_property
    def input_audio(self) -> AsyncLiveSessionInputAudioResource:
        return AsyncLiveSessionInputAudioResource(self._connection)

    @cached_property
    def instructions(self) -> AsyncLiveSessionInstructionsResource:
        return AsyncLiveSessionInstructionsResource(self._connection)

    @cached_property
    def thinking(self) -> AsyncLiveSessionThinkingResource:
        return AsyncLiveSessionThinkingResource(self._connection)

    async def close(self, *, event_id: Optional[str] | Omit = omit) -> None:
        """Request that the Live session close.

        The terminal `session.closed` event contains the close reason and final usage.
        """
        await self._connection.send(
            cast(ClientEventParam, strip_not_given({"type": "session.close", "event_id": event_id}))
        )

    async def update(self, *, session: SessionUpdateConfigParam, event_id: Optional[str] | Omit = omit) -> None:
        """Update the delegation settings of an active Live session.

        The server acknowledges accepted changes with `session.updated`.
        """
        await self._connection.send(
            cast(
                ClientEventParam, strip_not_given({"type": "session.update", "session": session, "event_id": event_id})
            )
        )

    async def start(self, *, session: SessionConfigParam, event_id: Optional[str] | Omit = omit) -> None:
        """Start a Live session on a primary WebSocket.

        Send this event before other commands and wait for `session.started`.
        """
        await self._connection.send(
            cast(ClientEventParam, strip_not_given({"type": "session.start", "session": session, "event_id": event_id}))
        )


class AsyncLiveSessionCommentaryResource(BaseAsyncLiveConnectionResource):
    async def append(
        self, *, content: str, delegation_id: Optional[str], event_id: Optional[str] | Omit = omit
    ) -> None:
        """
        Provide context the Live model can communicate to the user, optionally for an existing client delegation.
        """
        await self._connection.send(
            cast(
                ClientEventParam,
                strip_not_given(
                    {
                        "type": "session.commentary.append",
                        "content": content,
                        "delegation_id": delegation_id,
                        "event_id": event_id,
                    }
                ),
            )
        )


class AsyncLiveSessionInputAudioResource(BaseAsyncLiveConnectionResource):
    async def append(self, *, audio: str, event_id: Optional[str] | Omit = omit) -> None:
        """Send audio to a Live session over its primary WebSocket.

        WebRTC and SIP sessions send audio over their media transport.
        """
        await self._connection.send(
            cast(
                ClientEventParam,
                strip_not_given({"type": "session.input_audio.append", "audio": audio, "event_id": event_id}),
            )
        )

    async def mute(self, *, event_id: Optional[str] | Omit = omit) -> None:
        """Mute audio input to the Live model without closing the session.

        The server acknowledges with `session.input_audio.muted`.
        """
        await self._connection.send(
            cast(ClientEventParam, strip_not_given({"type": "session.input_audio.mute", "event_id": event_id}))
        )

    async def unmute(self, *, event_id: Optional[str] | Omit = omit) -> None:
        """Resume audio input to a Live model after muting it.

        The server acknowledges with `session.input_audio.unmuted`.
        """
        await self._connection.send(
            cast(ClientEventParam, strip_not_given({"type": "session.input_audio.unmute", "event_id": event_id}))
        )


class AsyncLiveSessionInstructionsResource(BaseAsyncLiveConnectionResource):
    async def append(
        self, *, content: str, delegation_id: Optional[str], event_id: Optional[str] | Omit = omit
    ) -> None:
        """
        Append instructions to the Live conversation while it is running, optionally associating them with an existing client delegation.
        """
        await self._connection.send(
            cast(
                ClientEventParam,
                strip_not_given(
                    {
                        "type": "session.instructions.append",
                        "content": content,
                        "delegation_id": delegation_id,
                        "event_id": event_id,
                    }
                ),
            )
        )


class AsyncLiveSessionThinkingResource(BaseAsyncLiveConnectionResource):
    async def append(
        self, *, content: str, delegation_id: Optional[str], event_id: Optional[str] | Omit = omit
    ) -> None:
        """
        Provide silent reasoning or progress context to the Live model, optionally for an existing client delegation.
        """
        await self._connection.send(
            cast(
                ClientEventParam,
                strip_not_given(
                    {
                        "type": "session.thinking.append",
                        "content": content,
                        "delegation_id": delegation_id,
                        "event_id": event_id,
                    }
                ),
            )
        )


class AsyncLiveResponseResource(BaseAsyncLiveConnectionResource):
    @cached_property
    def item(self) -> AsyncLiveResponseItemResource:
        return AsyncLiveResponseItemResource(self._connection)

    async def create(self, *, event_id: Optional[str] | Omit = omit) -> None:
        """
        Request a response from the Live session’s Responses backend, or continue a
        delegated response waiting for tool results.

        Requires Responses delegation.
        """
        await self._connection.send(
            cast(ClientEventParam, strip_not_given({"type": "response.create", "event_id": event_id}))
        )


class AsyncLiveResponseItemResource(BaseAsyncLiveConnectionResource):
    async def create(self, *, item: ResponseInputItemParam, event_id: Optional[str] | Omit = omit) -> None:
        """Add an input item to the Live session’s Responses backend.

        Requires Responses delegation; use `response.create` to request a response.
        """
        await self._connection.send(
            cast(
                ClientEventParam, strip_not_given({"type": "response.item.create", "item": item, "event_id": event_id})
            )
        )
