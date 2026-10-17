# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import json
import logging
from types import TracebackType
from typing import TYPE_CHECKING, Any, Union, Callable, Iterator, Awaitable, cast
from typing_extensions import AsyncIterator

import httpx2
from pydantic import BaseModel

from ...._types import Omit, Query, Headers, omit
from ...._utils import is_given, maybe_transform, strip_not_given, async_maybe_transform
from ...._compat import cached_property
from ...._models import FinalRequestOptions, construct_type_unchecked
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._exceptions import OpenAIError, WebSocketConnectionClosedError
from ...._send_queue import SendQueue
from .client_secrets import (
    ClientSecrets,
    AsyncClientSecrets,
    ClientSecretsWithRawResponse,
    AsyncClientSecretsWithRawResponse,
    ClientSecretsWithStreamingResponse,
    AsyncClientSecretsWithStreamingResponse,
)
from ...._base_client import _merge_mappings
from ...._event_handler import EventHandlerRegistry
from ...._websocket_connection import WebSocketConnectionBase, AsyncWebSocketConnectionBase
from ....types.websocket_reconnection import ReconnectingEvent, ReconnectingOverrides
from ....types.websocket_connection_options import WebSocketConnectionOptions
from ....types.realtime.realtime_error_event import RealtimeErrorEvent
from ....types.realtime.realtime_translation_client_event import RealtimeTranslationClientEvent
from ....types.realtime.realtime_translation_server_event import RealtimeTranslationServerEvent
from ....types.realtime.realtime_translation_client_event_param import RealtimeTranslationClientEventParam
from ....types.realtime.realtime_translation_session_update_request_param import (
    RealtimeTranslationSessionUpdateRequestParam,
)

if TYPE_CHECKING:
    from websockets.sync.client import ClientConnection as WebSocketConnection
    from websockets.asyncio.client import ClientConnection as AsyncWebSocketConnection

    from ...._client import OpenAI, AsyncOpenAI

__all__ = ["Translations", "AsyncTranslations"]

log: logging.Logger = logging.getLogger(__name__)


class Translations(SyncAPIResource):
    @cached_property
    def client_secrets(self) -> ClientSecrets:
        return ClientSecrets(self._client)

    @cached_property
    def with_raw_response(self) -> TranslationsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return TranslationsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TranslationsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return TranslationsWithStreamingResponse(self)

    def connect(
        self,
        model: str,
        extra_query: Query = {},
        extra_headers: Headers = {},
        websocket_connection_options: WebSocketConnectionOptions = {},
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        max_queue_size: int = 1_048_576,
    ) -> TranslationsConnectionManager:

        return TranslationsConnectionManager(
            client=self._client,
            model=model,
            extra_query=extra_query,
            extra_headers=extra_headers,
            websocket_connection_options=websocket_connection_options,
            on_reconnecting=on_reconnecting,
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay,
            max_queue_size=max_queue_size,
        )


class AsyncTranslations(AsyncAPIResource):
    @cached_property
    def client_secrets(self) -> AsyncClientSecrets:
        return AsyncClientSecrets(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncTranslationsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTranslationsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTranslationsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncTranslationsWithStreamingResponse(self)

    def connect(
        self,
        model: str,
        extra_query: Query = {},
        extra_headers: Headers = {},
        websocket_connection_options: WebSocketConnectionOptions = {},
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        max_queue_size: int = 1_048_576,
    ) -> AsyncTranslationsConnectionManager:

        return AsyncTranslationsConnectionManager(
            client=self._client,
            model=model,
            extra_query=extra_query,
            extra_headers=extra_headers,
            websocket_connection_options=websocket_connection_options,
            on_reconnecting=on_reconnecting,
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay,
            max_queue_size=max_queue_size,
        )


class TranslationsWithRawResponse:
    def __init__(self, translations: Translations) -> None:
        self._translations = translations

    @cached_property
    def client_secrets(self) -> ClientSecretsWithRawResponse:
        return ClientSecretsWithRawResponse(self._translations.client_secrets)


class AsyncTranslationsWithRawResponse:
    def __init__(self, translations: AsyncTranslations) -> None:
        self._translations = translations

    @cached_property
    def client_secrets(self) -> AsyncClientSecretsWithRawResponse:
        return AsyncClientSecretsWithRawResponse(self._translations.client_secrets)


class TranslationsWithStreamingResponse:
    def __init__(self, translations: Translations) -> None:
        self._translations = translations

    @cached_property
    def client_secrets(self) -> ClientSecretsWithStreamingResponse:
        return ClientSecretsWithStreamingResponse(self._translations.client_secrets)


class AsyncTranslationsWithStreamingResponse:
    def __init__(self, translations: AsyncTranslations) -> None:
        self._translations = translations

    @cached_property
    def client_secrets(self) -> AsyncClientSecretsWithStreamingResponse:
        return AsyncClientSecretsWithStreamingResponse(self._translations.client_secrets)


class AsyncTranslationsConnection(AsyncWebSocketConnectionBase):
    """Represents a live WebSocket connection to the Translations API"""

    session: AsyncTranslationsSessionResource

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
        super().__init__(
            connection,
            make_ws=make_ws,
            on_reconnecting=on_reconnecting,
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay,
            extra_query=extra_query,
            extra_headers=extra_headers,
            send_queue=send_queue,
            logger=log,
        )
        self._event_handler_registry = EventHandlerRegistry(use_lock=False)

        self.session = AsyncTranslationsSessionResource(self)

    async def __aiter__(self) -> AsyncIterator[RealtimeTranslationServerEvent]:
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

    async def recv(self) -> RealtimeTranslationServerEvent:
        """
        Receive the next message from the connection and parses it into a `RealtimeTranslationServerEvent` object.

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

        If you want to parse the message into a `RealtimeTranslationServerEvent` object like `.recv()` does,
        then you can call `.parse_event(data)`.
        """
        message = await self._connection.recv(decode=False)
        log.debug("Received WebSocket message: %i bytes", len(message))
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

    async def send(self, event: RealtimeTranslationClientEvent | RealtimeTranslationClientEventParam) -> None:
        data = (
            event.to_json(use_api_names=True, exclude_unset=True)
            if isinstance(event, BaseModel)
            else json.dumps(await async_maybe_transform(event, RealtimeTranslationClientEventParam))
        )
        if self._is_reconnecting:
            self._send_queue.enqueue(data)
            return
        await self._connection.send(data)

    def parse_event(self, data: str | bytes) -> RealtimeTranslationServerEvent:
        """
        Converts a raw `str` or `bytes` message into a `RealtimeTranslationServerEvent` object.

        This is helpful if you're using `.recv_bytes()`.
        """
        return cast(
            RealtimeTranslationServerEvent,
            construct_type_unchecked(value=json.loads(data), type_=cast(Any, RealtimeTranslationServerEvent)),
        )

    def on(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[AsyncTranslationsConnection, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Adds the handler to the end of the handlers list for the given event type.

        No checks are made to see if the handler has already been added. Multiple calls
        passing the same combination of event type and handler will result in the handler
        being added, and called, multiple times.

        Can be used as a method (returns ``self`` for chaining)::

            connection.on("session.created", my_handler)

        Or as a decorator::

            @connection.on("session.created")
            async def my_handler(event): ...
        """
        if handler is not None:
            self._event_handler_registry.add(event_type, handler)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self._event_handler_registry.add(event_type, fn)
            return fn

        return decorator

    def off(self, event_type: str, handler: Callable[..., Any]) -> AsyncTranslationsConnection:
        """Remove a previously registered event handler."""
        self._event_handler_registry.remove(event_type, handler)
        return self

    def once(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[AsyncTranslationsConnection, Callable[[Callable[..., Any]], Callable[..., Any]]]:
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


class AsyncTranslationsConnectionManager:
    """
    Context manager over a `AsyncTranslationsConnection` that is returned by `realtime.translations.connect()`

    This context manager ensures that the connection will be closed when it exits.

    ---

    Note that if your application doesn't work well with the context manager approach then you
    can call the `.enter()` method directly to initiate a connection.

    **Warning**: You must remember to close the connection with `.close()`.

    ```py
    connection = await client.realtime.translations.connect(...).enter()
    # ...
    await connection.close()
    ```
    """

    def __init__(
        self,
        *,
        client: AsyncOpenAI,
        model: str,
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
        self.__connection: AsyncTranslationsConnection | None = None
        self.__model = model
        self.__extra_query = extra_query
        self.__extra_headers = extra_headers
        self.__websocket_connection_options: WebSocketConnectionOptions = {
            "max_size": None,
            **websocket_connection_options,
        }
        self.__on_reconnecting = on_reconnecting
        self.__max_retries = max_retries
        self.__initial_delay = initial_delay
        self.__max_delay = max_delay
        self.__send_queue = SendQueue(max_bytes=max_queue_size)
        self.__event_handler_registry = EventHandlerRegistry(use_lock=False)

    def send(self, event: RealtimeTranslationClientEvent | RealtimeTranslationClientEventParam) -> None:
        """Queue a message to be sent when the connection is established.

        This can be called before entering the context manager. Queued messages
        are automatically sent once the WebSocket connection opens.
        """
        data = (
            event.to_json(use_api_names=True, exclude_unset=True)
            if isinstance(event, BaseModel)
            else json.dumps(maybe_transform(event, RealtimeTranslationClientEventParam))
        )
        self.__send_queue.enqueue(data)

    def on(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[AsyncTranslationsConnectionManager, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register an event handler before the connection is established.

        Handlers are transferred to the connection on enter. Supports the
        same method and decorator forms as ``AsyncTranslationsConnection.on``.
        """
        if handler is not None:
            self.__event_handler_registry.add(event_type, handler)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.__event_handler_registry.add(event_type, fn)
            return fn

        return decorator

    def off(self, event_type: str, handler: Callable[..., Any]) -> AsyncTranslationsConnectionManager:
        """Remove a previously registered event handler."""
        self.__event_handler_registry.remove(event_type, handler)
        return self

    def once(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[AsyncTranslationsConnectionManager, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register a one-time event handler before the connection is established."""
        if handler is not None:
            self.__event_handler_registry.add(event_type, handler, once=True)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.__event_handler_registry.add(event_type, fn, once=True)
            return fn

        return decorator

    async def __aenter__(self) -> AsyncTranslationsConnection:
        """
        If your application doesn't work well with the context manager approach then you
        can call this method directly to initiate a connection.

        **Warning**: You must remember to close the connection with `.close()`.

        ```py
        connection = await client.realtime.translations.connect(...).enter()
        # ...
        await connection.close()
        ```
        """
        ws = await self._connect_ws(self.__extra_query, self.__extra_headers)

        self.__connection = AsyncTranslationsConnection(
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
            from ....lib._websocket import _WebSocketConnect as connect
        except ImportError as exc:
            raise OpenAIError("You need to install `openai[realtime]` to use this method") from exc

        url = self._prepare_url()
        url = url.copy_with(
            params=httpx2.QueryParams(self.__client.qs.stringify(cast(Any, self.__client.default_query)))
            .merge(url.params)
            .merge({"model": self.__model})
            .merge(cast(Any, extra_query)),
        )
        url = url.copy_with(scheme={"http": "ws", "https": "wss"}.get(url.scheme, url.scheme))
        options = await self.__client._prepare_options(
            FinalRequestOptions.construct(
                method="get",
                url=str(url),
                headers=dict(extra_headers),
                security={"bearer_auth": True},
            )
        )
        url = self.__client._prepare_url(options.url).copy_merge_params(
            self.__client.qs.stringify(cast(Any, options.params))
        )
        url = url.copy_with(scheme={"http": "ws", "https": "wss"}.get(url.scheme, url.scheme))
        headers = {
            key.lower(): (key, value)
            for header_set in (
                self.__client.auth_headers,
                {},
                self.__client.default_headers,
                options.headers if is_given(options.headers) else {},
            )
            for key, value in header_set.items()
        }
        log.debug("Connecting to WebSocket API")
        if self.__websocket_connection_options:
            log.debug("Custom WebSocket connection options provided")

        return await connect(
            str(url),
            user_agent_header=None,
            additional_headers=_merge_mappings(dict(headers.values()), {}),
            **self.__websocket_connection_options,
        )

    def _prepare_url(self) -> httpx2.URL:
        if self.__client.websocket_base_url is not None:
            base_url = httpx2.URL(self.__client.websocket_base_url)
        else:
            scheme = self.__client._base_url.scheme
            ws_scheme = "ws" if scheme == "http" else "wss"
            base_url = self.__client._base_url.copy_with(scheme=ws_scheme)

        path, separator, query = base_url.raw_path.partition(b"?")
        merge_raw_path = path.rstrip(b"/") + b"/realtime/translations" + separator + query
        return base_url.copy_with(raw_path=merge_raw_path)

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        if self.__connection is not None:
            await self.__connection.close()


class TranslationsConnection(WebSocketConnectionBase):
    """Represents a live WebSocket connection to the Translations API"""

    session: TranslationsSessionResource

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
        super().__init__(
            connection,
            make_ws=make_ws,
            on_reconnecting=on_reconnecting,
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay,
            extra_query=extra_query,
            extra_headers=extra_headers,
            send_queue=send_queue,
            logger=log,
        )
        self._event_handler_registry = EventHandlerRegistry(use_lock=True)

        self.session = TranslationsSessionResource(self)

    def __iter__(self) -> Iterator[RealtimeTranslationServerEvent]:
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

    def recv(self) -> RealtimeTranslationServerEvent:
        """
        Receive the next message from the connection and parses it into a `RealtimeTranslationServerEvent` object.

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

        If you want to parse the message into a `RealtimeTranslationServerEvent` object like `.recv()` does,
        then you can call `.parse_event(data)`.
        """
        from ....lib._websocket import _recv_bytes

        message = _recv_bytes(self._connection)
        log.debug("Received WebSocket message: %i bytes", len(message))
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

    def send(self, event: RealtimeTranslationClientEvent | RealtimeTranslationClientEventParam) -> None:
        data = (
            event.to_json(use_api_names=True, exclude_unset=True)
            if isinstance(event, BaseModel)
            else json.dumps(maybe_transform(event, RealtimeTranslationClientEventParam))
        )
        if self._is_reconnecting:
            self._send_queue.enqueue(data)
            return
        self._connection.send(data)

    def parse_event(self, data: str | bytes) -> RealtimeTranslationServerEvent:
        """
        Converts a raw `str` or `bytes` message into a `RealtimeTranslationServerEvent` object.

        This is helpful if you're using `.recv_bytes()`.
        """
        return cast(
            RealtimeTranslationServerEvent,
            construct_type_unchecked(value=json.loads(data), type_=cast(Any, RealtimeTranslationServerEvent)),
        )

    def on(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[TranslationsConnection, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Adds the handler to the end of the handlers list for the given event type.

        No checks are made to see if the handler has already been added. Multiple calls
        passing the same combination of event type and handler will result in the handler
        being added, and called, multiple times.

        Can be used as a method (returns ``self`` for chaining)::

            connection.on("session.created", my_handler)

        Or as a decorator::

            @connection.on("session.created")
            def my_handler(event): ...
        """
        if handler is not None:
            self._event_handler_registry.add(event_type, handler)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self._event_handler_registry.add(event_type, fn)
            return fn

        return decorator

    def off(self, event_type: str, handler: Callable[..., Any]) -> TranslationsConnection:
        """Remove a previously registered event handler."""
        self._event_handler_registry.remove(event_type, handler)
        return self

    def once(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[TranslationsConnection, Callable[[Callable[..., Any]], Callable[..., Any]]]:
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


class TranslationsConnectionManager:
    """
    Context manager over a `TranslationsConnection` that is returned by `realtime.translations.connect()`

    This context manager ensures that the connection will be closed when it exits.

    ---

    Note that if your application doesn't work well with the context manager approach then you
    can call the `.enter()` method directly to initiate a connection.

    **Warning**: You must remember to close the connection with `.close()`.

    ```py
    connection = client.realtime.translations.connect(...).enter()
    # ...
    connection.close()
    ```
    """

    def __init__(
        self,
        *,
        client: OpenAI,
        model: str,
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
        self.__connection: TranslationsConnection | None = None
        self.__model = model
        self.__extra_query = extra_query
        self.__extra_headers = extra_headers
        self.__websocket_connection_options: WebSocketConnectionOptions = {
            "max_size": None,
            **websocket_connection_options,
        }
        self.__on_reconnecting = on_reconnecting
        self.__max_retries = max_retries
        self.__initial_delay = initial_delay
        self.__max_delay = max_delay
        self.__send_queue = SendQueue(max_bytes=max_queue_size)
        self.__event_handler_registry = EventHandlerRegistry(use_lock=True)

    def send(self, event: RealtimeTranslationClientEvent | RealtimeTranslationClientEventParam) -> None:
        """Queue a message to be sent when the connection is established.

        This can be called before entering the context manager. Queued messages
        are automatically sent once the WebSocket connection opens.
        """
        data = (
            event.to_json(use_api_names=True, exclude_unset=True)
            if isinstance(event, BaseModel)
            else json.dumps(maybe_transform(event, RealtimeTranslationClientEventParam))
        )
        self.__send_queue.enqueue(data)

    def on(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[TranslationsConnectionManager, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register an event handler before the connection is established.

        Handlers are transferred to the connection on enter. Supports the
        same method and decorator forms as ``TranslationsConnection.on``.
        """
        if handler is not None:
            self.__event_handler_registry.add(event_type, handler)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.__event_handler_registry.add(event_type, fn)
            return fn

        return decorator

    def off(self, event_type: str, handler: Callable[..., Any]) -> TranslationsConnectionManager:
        """Remove a previously registered event handler."""
        self.__event_handler_registry.remove(event_type, handler)
        return self

    def once(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[TranslationsConnectionManager, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register a one-time event handler before the connection is established."""
        if handler is not None:
            self.__event_handler_registry.add(event_type, handler, once=True)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.__event_handler_registry.add(event_type, fn, once=True)
            return fn

        return decorator

    def __enter__(self) -> TranslationsConnection:
        """
        If your application doesn't work well with the context manager approach then you
        can call this method directly to initiate a connection.

        **Warning**: You must remember to close the connection with `.close()`.

        ```py
        connection = client.realtime.translations.connect(...).enter()
        # ...
        connection.close()
        ```
        """
        ws = self._connect_ws(self.__extra_query, self.__extra_headers)

        self.__connection = TranslationsConnection(
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

        url = self._prepare_url()
        url = url.copy_with(
            params=httpx2.QueryParams(self.__client.qs.stringify(cast(Any, self.__client.default_query)))
            .merge(url.params)
            .merge({"model": self.__model})
            .merge(cast(Any, extra_query)),
        )
        url = url.copy_with(scheme={"http": "ws", "https": "wss"}.get(url.scheme, url.scheme))
        options = self.__client._prepare_options(
            FinalRequestOptions.construct(
                method="get",
                url=str(url),
                headers=dict(extra_headers),
                security={"bearer_auth": True},
            )
        )
        url = self.__client._prepare_url(options.url).copy_merge_params(
            self.__client.qs.stringify(cast(Any, options.params))
        )
        url = url.copy_with(scheme={"http": "ws", "https": "wss"}.get(url.scheme, url.scheme))
        headers = {
            key.lower(): (key, value)
            for header_set in (
                self.__client.auth_headers,
                {},
                self.__client.default_headers,
                options.headers if is_given(options.headers) else {},
            )
            for key, value in header_set.items()
        }
        log.debug("Connecting to WebSocket API")
        if self.__websocket_connection_options:
            log.debug("Custom WebSocket connection options provided")

        return connect(
            str(url),
            user_agent_header=None,
            additional_headers=_merge_mappings(dict(headers.values()), {}),
            **self.__websocket_connection_options,
        )

    def _prepare_url(self) -> httpx2.URL:
        if self.__client.websocket_base_url is not None:
            base_url = httpx2.URL(self.__client.websocket_base_url)
        else:
            scheme = self.__client._base_url.scheme
            ws_scheme = "ws" if scheme == "http" else "wss"
            base_url = self.__client._base_url.copy_with(scheme=ws_scheme)

        path, separator, query = base_url.raw_path.partition(b"?")
        merge_raw_path = path.rstrip(b"/") + b"/realtime/translations" + separator + query
        return base_url.copy_with(raw_path=merge_raw_path)

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        if self.__connection is not None:
            self.__connection.close()


class BaseTranslationsConnectionResource:
    def __init__(self, connection: TranslationsConnection) -> None:
        self._connection = connection


class TranslationsSessionResource(BaseTranslationsConnectionResource):
    @cached_property
    def input_audio_buffer(self) -> TranslationsSessionInputAudioBufferResource:
        return TranslationsSessionInputAudioBufferResource(self._connection)

    def close(self, *, event_id: str | Omit = omit) -> None:
        """Gracefully close the realtime translation session.

        The server flushes pending
        input audio and emits any remaining translated output before closing the
        session.
        """
        self._connection.send(
            cast(RealtimeTranslationClientEventParam, strip_not_given({"type": "session.close", "event_id": event_id}))
        )

    def update(self, *, session: RealtimeTranslationSessionUpdateRequestParam, event_id: str | Omit = omit) -> None:
        """Send this event to update the translation session configuration.

        Translation
        sessions support updates to `audio.output.language`, `audio.input.transcription`,
        and `audio.input.noise_reduction`.
        """
        self._connection.send(
            cast(
                RealtimeTranslationClientEventParam,
                strip_not_given({"type": "session.update", "session": session, "event_id": event_id}),
            )
        )


class TranslationsSessionInputAudioBufferResource(BaseTranslationsConnectionResource):
    def append(self, *, audio: str, event_id: str | Omit = omit) -> None:
        """
        Send this event to append audio bytes to the translation session input audio buffer.

        WebSocket translation sessions accept base64-encoded 24 kHz PCM16 mono
        little-endian raw audio bytes. Unsupported websocket audio formats return a
        validation error because lower-quality audio materially degrades translation
        quality.

        Translation consumes 200 ms engine frames. For best realtime behavior, append
        audio in 200 ms chunks. If a chunk is shorter, the server buffers it until it
        has enough audio for one frame. If a chunk is longer, the server splits it into
        200 ms frames and enqueues them back-to-back.

        Keep appending silence while the session is active. If a client stops sending
        audio and later resumes, model time treats the resumed audio as contiguous with
        the previous audio rather than as a real-world pause.
        """
        self._connection.send(
            cast(
                RealtimeTranslationClientEventParam,
                strip_not_given({"type": "session.input_audio_buffer.append", "audio": audio, "event_id": event_id}),
            )
        )


class BaseAsyncTranslationsConnectionResource:
    def __init__(self, connection: AsyncTranslationsConnection) -> None:
        self._connection = connection


class AsyncTranslationsSessionResource(BaseAsyncTranslationsConnectionResource):
    @cached_property
    def input_audio_buffer(self) -> AsyncTranslationsSessionInputAudioBufferResource:
        return AsyncTranslationsSessionInputAudioBufferResource(self._connection)

    async def close(self, *, event_id: str | Omit = omit) -> None:
        """Gracefully close the realtime translation session.

        The server flushes pending
        input audio and emits any remaining translated output before closing the
        session.
        """
        await self._connection.send(
            cast(RealtimeTranslationClientEventParam, strip_not_given({"type": "session.close", "event_id": event_id}))
        )

    async def update(
        self, *, session: RealtimeTranslationSessionUpdateRequestParam, event_id: str | Omit = omit
    ) -> None:
        """Send this event to update the translation session configuration.

        Translation
        sessions support updates to `audio.output.language`, `audio.input.transcription`,
        and `audio.input.noise_reduction`.
        """
        await self._connection.send(
            cast(
                RealtimeTranslationClientEventParam,
                strip_not_given({"type": "session.update", "session": session, "event_id": event_id}),
            )
        )


class AsyncTranslationsSessionInputAudioBufferResource(BaseAsyncTranslationsConnectionResource):
    async def append(self, *, audio: str, event_id: str | Omit = omit) -> None:
        """
        Send this event to append audio bytes to the translation session input audio buffer.

        WebSocket translation sessions accept base64-encoded 24 kHz PCM16 mono
        little-endian raw audio bytes. Unsupported websocket audio formats return a
        validation error because lower-quality audio materially degrades translation
        quality.

        Translation consumes 200 ms engine frames. For best realtime behavior, append
        audio in 200 ms chunks. If a chunk is shorter, the server buffers it until it
        has enough audio for one frame. If a chunk is longer, the server splits it into
        200 ms frames and enqueues them back-to-back.

        Keep appending silence while the session is active. If a client stops sending
        audio and later resumes, model time treats the resumed audio as contiguous with
        the previous audio rather than as a real-world pause.
        """
        await self._connection.send(
            cast(
                RealtimeTranslationClientEventParam,
                strip_not_given({"type": "session.input_audio_buffer.append", "audio": audio, "event_id": event_id}),
            )
        )
