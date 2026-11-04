# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import json
import logging
from types import TracebackType
from typing import TYPE_CHECKING, Any, Union, Callable, Iterator, Optional, Awaitable, cast
from typing_extensions import AsyncIterator

import httpx2
from pydantic import BaseModel

from ..._types import Omit, Query, Headers, omit
from ..._utils import is_given, path_template, maybe_transform, strip_not_given, async_maybe_transform
from ..._compat import cached_property
from ..._models import FinalRequestOptions, construct_type_unchecked
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._constants import DEFAULT_LIVE_SEND_QUEUE_MAX_BYTES
from ...types.live import decision_item_create_event_param
from ..._exceptions import OpenAIError, WebSocketConnectionClosedError
from ..._send_queue import SendQueue
from ..._base_client import _merge_mappings
from ..._event_handler import EventHandlerRegistry
from ..._websocket_connection import WebSocketConnectionBase, AsyncWebSocketConnectionBase
from ...types.live.error_event import ErrorEvent
from ...types.live.fork_client_event import ForkClientEvent
from ...types.live.fork_server_event import ForkServerEvent
from ...types.websocket_reconnection import ReconnectingEvent, ReconnectingOverrides
from ...types.live.fork_client_event_param import ForkClientEventParam
from ...types.websocket_connection_options import WebSocketConnectionOptions, SyncWebSocketConnectionOptions
from ...types.live.fork_session_config_param import ForkSessionConfigParam
from ...types.live.session_update_config_param import SessionUpdateConfigParam
from ...types.responses.response_input_item_param import ResponseInputItemParam

if TYPE_CHECKING:
    from websockets.sync.client import ClientConnection as WebSocketConnection
    from websockets.asyncio.client import ClientConnection as AsyncWebSocketConnection

    from ..._client import OpenAI, AsyncOpenAI

__all__ = ["Forks", "AsyncForks"]

log: logging.Logger = logging.getLogger(__name__)


class Forks(SyncAPIResource):
    def connect(
        self,
        *,
        session_id: str,
        extra_query: Query = {},
        extra_headers: Headers = {},
        websocket_connection_options: SyncWebSocketConnectionOptions = {},
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        max_queue_size: int = DEFAULT_LIVE_SEND_QUEUE_MAX_BYTES,
    ) -> ForksConnectionManager:
        """Fork a stored Live session over WebSocket.

        Send session.start with an overrides object (which may be empty), then wait for session.started. The model is inherited.
        """
        return ForksConnectionManager(
            client=self._client,
            extra_query=extra_query,
            extra_headers=extra_headers,
            websocket_connection_options=websocket_connection_options,
            on_reconnecting=on_reconnecting,
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay,
            max_queue_size=max_queue_size,
            session_id=session_id,
        )


class AsyncForks(AsyncAPIResource):
    def connect(
        self,
        *,
        session_id: str,
        extra_query: Query = {},
        extra_headers: Headers = {},
        websocket_connection_options: WebSocketConnectionOptions = {},
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        max_queue_size: int = DEFAULT_LIVE_SEND_QUEUE_MAX_BYTES,
    ) -> AsyncForksConnectionManager:
        """Fork a stored Live session over WebSocket.

        Send session.start with an overrides object (which may be empty), then wait for session.started. The model is inherited.
        """
        return AsyncForksConnectionManager(
            client=self._client,
            extra_query=extra_query,
            extra_headers=extra_headers,
            websocket_connection_options=websocket_connection_options,
            on_reconnecting=on_reconnecting,
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay,
            max_queue_size=max_queue_size,
            session_id=session_id,
        )


class AsyncForksConnection(AsyncWebSocketConnectionBase):
    """Represents a live WebSocket connection to the Forks API"""

    session: AsyncForksSessionResource
    decision: AsyncForksDecisionResource
    response: AsyncForksResponseResource

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
            send_queue=send_queue if send_queue is not None else SendQueue(max_bytes=DEFAULT_LIVE_SEND_QUEUE_MAX_BYTES),
            logger=log,
        )
        self._event_handler_registry = EventHandlerRegistry(use_lock=False)

        self.session = AsyncForksSessionResource(self)
        self.decision = AsyncForksDecisionResource(self)
        self.response = AsyncForksResponseResource(self)

    async def __aiter__(self) -> AsyncIterator[ForkServerEvent]:
        """
        An infinite-iterator that will continue to yield events until
        the connection is closed.
        """
        from websockets.exceptions import ConnectionClosed, ConnectionClosedOK, ConnectionClosedError

        while True:
            try:
                yield await self.recv()
            except ConnectionClosed as exc:
                # Older SDK bases read close codes only from ConnectionClosedError.
                # Adapt the policy input; keep the original close for EOF and errors.
                reconnect_exc = (
                    ConnectionClosedError(exc.rcvd, exc.sent, exc.rcvd_then_sent)
                    if isinstance(exc, ConnectionClosedOK)
                    else exc
                )
                if not await self._reconnect(reconnect_exc):
                    unsent = self._send_queue.drain()
                    if unsent:
                        raise WebSocketConnectionClosedError(
                            "WebSocket connection closed with unsent messages",
                            unsent_messages=unsent,
                        ) from exc
                    if isinstance(exc, ConnectionClosedOK):
                        return
                    raise

    async def recv(self) -> ForkServerEvent:
        """
        Receive the next message from the connection and parses it into a `ForkServerEvent` object.

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

        If you want to parse the message into a `ForkServerEvent` object like `.recv()` does,
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

    async def send(self, event: ForkClientEvent | ForkClientEventParam) -> None:
        data = (
            event.to_json(use_api_names=True, exclude_unset=True)
            if isinstance(event, BaseModel)
            else json.dumps(await async_maybe_transform(event, ForkClientEventParam))
        )
        await AsyncWebSocketConnectionBase.send_raw(self, data)

    def parse_event(self, data: str | bytes) -> ForkServerEvent:
        """
        Converts a raw `str` or `bytes` message into a `ForkServerEvent` object.

        This is helpful if you're using `.recv_bytes()`.
        """
        return cast(ForkServerEvent, construct_type_unchecked(value=json.loads(data), type_=cast(Any, ForkServerEvent)))

    def on(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[AsyncForksConnection, Callable[[Callable[..., Any]], Callable[..., Any]]]:
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

    def off(self, event_type: str, handler: Callable[..., Any]) -> AsyncForksConnection:
        """Remove a previously registered event handler."""
        self._event_handler_registry.remove(event_type, handler)
        return self

    def once(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[AsyncForksConnection, Callable[[Callable[..., Any]], Callable[..., Any]]]:
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


class AsyncForksConnectionManager:
    """
    Context manager over a `AsyncForksConnection` that is returned by `live.forks.connect()`

    This context manager ensures that the connection will be closed when it exits.

    ---

    Note that if your application doesn't work well with the context manager approach then you
    can call the `.enter()` method directly to initiate a connection.

    **Warning**: You must remember to close the connection with `.close()`.

    ```py
    connection = await client.live.forks.connect(...).enter()
    # ...
    await connection.close()
    ```
    """

    def __init__(
        self,
        *,
        client: AsyncOpenAI,
        session_id: str,
        extra_query: Query,
        extra_headers: Headers,
        websocket_connection_options: WebSocketConnectionOptions,
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        max_queue_size: int = DEFAULT_LIVE_SEND_QUEUE_MAX_BYTES,
    ) -> None:
        self.__client = client
        self.__session_id = session_id
        self.__connection: AsyncForksConnection | None = None
        self.__extra_query = extra_query
        self.__extra_headers = extra_headers
        self.__websocket_connection_options = websocket_connection_options
        self.__on_reconnecting = on_reconnecting
        self.__max_retries = max_retries
        self.__initial_delay = initial_delay
        self.__max_delay = max_delay
        self.__send_queue = SendQueue(max_bytes=max_queue_size)
        self.__event_handler_registry = EventHandlerRegistry(use_lock=False)

    def send(self, event: ForkClientEvent | ForkClientEventParam) -> None:
        """Queue a message to be sent when the connection is established.

        This can be called before entering the context manager. Queued messages
        are automatically sent once the WebSocket connection opens.
        """
        data = (
            event.to_json(use_api_names=True, exclude_unset=True)
            if isinstance(event, BaseModel)
            else json.dumps(maybe_transform(event, ForkClientEventParam))
        )
        self.__send_queue.enqueue(data)

    def on(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[AsyncForksConnectionManager, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register an event handler before the connection is established.

        Handlers are transferred to the connection on enter. Supports the
        same method and decorator forms as ``AsyncForksConnection.on``.
        """
        if handler is not None:
            self.__event_handler_registry.add(event_type, handler)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.__event_handler_registry.add(event_type, fn)
            return fn

        return decorator

    def off(self, event_type: str, handler: Callable[..., Any]) -> AsyncForksConnectionManager:
        """Remove a previously registered event handler."""
        self.__event_handler_registry.remove(event_type, handler)
        return self

    def once(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[AsyncForksConnectionManager, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register a one-time event handler before the connection is established."""
        if handler is not None:
            self.__event_handler_registry.add(event_type, handler, once=True)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.__event_handler_registry.add(event_type, fn, once=True)
            return fn

        return decorator

    async def __aenter__(self) -> AsyncForksConnection:
        """
        If your application doesn't work well with the context manager approach then you
        can call this method directly to initiate a connection.

        **Warning**: You must remember to close the connection with `.close()`.

        ```py
        connection = await client.live.forks.connect(...).enter()
        # ...
        await connection.close()
        ```
        """
        ws = await self._connect_ws(self.__extra_query, self.__extra_headers)

        try:
            self.__connection = AsyncForksConnection(
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
        except BaseException:
            self.__connection = None
            try:
                await ws.close()
            except BaseException:
                # Preserve the exception that prevented successful entry.
                pass
            raise

        return self.__connection

    enter = __aenter__

    async def _connect_ws(self, extra_query: Query, extra_headers: Headers) -> AsyncWebSocketConnection:
        try:
            from ...lib._websocket import _WebSocketConnect as connect
        except ImportError as exc:
            raise OpenAIError("You need to install `openai[realtime]` to use this method") from exc

        url = self._prepare_url()
        try:
            # Older runtimes do not declare this optional helper.
            query_params = getattr(self.__client, "_websocket_query_params")  # noqa: B009
        except AttributeError:
            query_params = self.__client._websocket_query_params_fallback
        url = url.copy_with(
            params=query_params(
                url,
                extra_query,
            ),
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

        websocket_options = self.__websocket_connection_options.copy()
        websocket_options.setdefault("max_size", None)
        if websocket_options.get("max_size") is None:
            websocket_options.setdefault("compression", None)

        return await connect(
            str(url),
            user_agent_header=None,
            additional_headers=_merge_mappings(dict(headers.values()), {}),
            **websocket_options,
        )

    def _prepare_url(self) -> httpx2.URL:
        if self.__client.websocket_base_url is not None:
            base_url = httpx2.URL(self.__client.websocket_base_url)
        else:
            scheme = self.__client._base_url.scheme
            ws_scheme = "ws" if scheme == "http" else "wss"
            base_url = self.__client._base_url.copy_with(scheme=ws_scheme)

        path, separator, query = base_url.raw_path.partition(b"?")
        merge_raw_path = (
            path.rstrip(b"/")
            + path_template("/live/sessions/{session_id}/fork", session_id=self.__session_id).encode("utf-8")
            + separator
            + query
        )
        return base_url.copy_with(raw_path=merge_raw_path)

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        if self.__connection is not None:
            try:
                await self.__connection.close()
            except Exception:
                if exc is None:
                    raise


class ForksConnection(WebSocketConnectionBase):
    """Represents a live WebSocket connection to the Forks API"""

    session: ForksSessionResource
    decision: ForksDecisionResource
    response: ForksResponseResource

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
            send_queue=send_queue if send_queue is not None else SendQueue(max_bytes=DEFAULT_LIVE_SEND_QUEUE_MAX_BYTES),
            logger=log,
        )
        self._event_handler_registry = EventHandlerRegistry(use_lock=True)

        self.session = ForksSessionResource(self)
        self.decision = ForksDecisionResource(self)
        self.response = ForksResponseResource(self)

    def __iter__(self) -> Iterator[ForkServerEvent]:
        """
        An infinite-iterator that will continue to yield events until
        the connection is closed.
        """
        from websockets.exceptions import ConnectionClosed, ConnectionClosedOK, ConnectionClosedError

        while True:
            try:
                yield self.recv()
            except ConnectionClosed as exc:
                # Older SDK bases read close codes only from ConnectionClosedError.
                # Adapt the policy input; keep the original close for EOF and errors.
                reconnect_exc = (
                    ConnectionClosedError(exc.rcvd, exc.sent, exc.rcvd_then_sent)
                    if isinstance(exc, ConnectionClosedOK)
                    else exc
                )
                if not self._reconnect(reconnect_exc):
                    unsent = self._send_queue.drain()
                    if unsent:
                        raise WebSocketConnectionClosedError(
                            "WebSocket connection closed with unsent messages",
                            unsent_messages=unsent,
                        ) from exc
                    if isinstance(exc, ConnectionClosedOK):
                        return
                    raise

    def recv(self) -> ForkServerEvent:
        """
        Receive the next message from the connection and parses it into a `ForkServerEvent` object.

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

        If you want to parse the message into a `ForkServerEvent` object like `.recv()` does,
        then you can call `.parse_event(data)`.
        """
        from ...lib._websocket import _recv_bytes

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

    def send(self, event: ForkClientEvent | ForkClientEventParam) -> None:
        data = (
            event.to_json(use_api_names=True, exclude_unset=True)
            if isinstance(event, BaseModel)
            else json.dumps(maybe_transform(event, ForkClientEventParam))
        )
        WebSocketConnectionBase.send_raw(self, data)

    def parse_event(self, data: str | bytes) -> ForkServerEvent:
        """
        Converts a raw `str` or `bytes` message into a `ForkServerEvent` object.

        This is helpful if you're using `.recv_bytes()`.
        """
        return cast(ForkServerEvent, construct_type_unchecked(value=json.loads(data), type_=cast(Any, ForkServerEvent)))

    def on(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[ForksConnection, Callable[[Callable[..., Any]], Callable[..., Any]]]:
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

    def off(self, event_type: str, handler: Callable[..., Any]) -> ForksConnection:
        """Remove a previously registered event handler."""
        self._event_handler_registry.remove(event_type, handler)
        return self

    def once(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[ForksConnection, Callable[[Callable[..., Any]], Callable[..., Any]]]:
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


class ForksConnectionManager:
    """
    Context manager over a `ForksConnection` that is returned by `live.forks.connect()`

    This context manager ensures that the connection will be closed when it exits.

    ---

    Note that if your application doesn't work well with the context manager approach then you
    can call the `.enter()` method directly to initiate a connection.

    **Warning**: You must remember to close the connection with `.close()`.

    ```py
    connection = client.live.forks.connect(...).enter()
    # ...
    connection.close()
    ```
    """

    def __init__(
        self,
        *,
        client: OpenAI,
        session_id: str,
        extra_query: Query,
        extra_headers: Headers,
        websocket_connection_options: SyncWebSocketConnectionOptions,
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        max_queue_size: int = DEFAULT_LIVE_SEND_QUEUE_MAX_BYTES,
    ) -> None:
        self.__client = client
        self.__session_id = session_id
        self.__connection: ForksConnection | None = None
        self.__extra_query = extra_query
        self.__extra_headers = extra_headers
        self.__websocket_connection_options = websocket_connection_options
        self.__on_reconnecting = on_reconnecting
        self.__max_retries = max_retries
        self.__initial_delay = initial_delay
        self.__max_delay = max_delay
        self.__send_queue = SendQueue(max_bytes=max_queue_size)
        self.__event_handler_registry = EventHandlerRegistry(use_lock=True)

    def send(self, event: ForkClientEvent | ForkClientEventParam) -> None:
        """Queue a message to be sent when the connection is established.

        This can be called before entering the context manager. Queued messages
        are automatically sent once the WebSocket connection opens.
        """
        data = (
            event.to_json(use_api_names=True, exclude_unset=True)
            if isinstance(event, BaseModel)
            else json.dumps(maybe_transform(event, ForkClientEventParam))
        )
        self.__send_queue.enqueue(data)

    def on(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[ForksConnectionManager, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register an event handler before the connection is established.

        Handlers are transferred to the connection on enter. Supports the
        same method and decorator forms as ``ForksConnection.on``.
        """
        if handler is not None:
            self.__event_handler_registry.add(event_type, handler)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.__event_handler_registry.add(event_type, fn)
            return fn

        return decorator

    def off(self, event_type: str, handler: Callable[..., Any]) -> ForksConnectionManager:
        """Remove a previously registered event handler."""
        self.__event_handler_registry.remove(event_type, handler)
        return self

    def once(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[ForksConnectionManager, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register a one-time event handler before the connection is established."""
        if handler is not None:
            self.__event_handler_registry.add(event_type, handler, once=True)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.__event_handler_registry.add(event_type, fn, once=True)
            return fn

        return decorator

    def __enter__(self) -> ForksConnection:
        """
        If your application doesn't work well with the context manager approach then you
        can call this method directly to initiate a connection.

        **Warning**: You must remember to close the connection with `.close()`.

        ```py
        connection = client.live.forks.connect(...).enter()
        # ...
        connection.close()
        ```
        """
        ws = self._connect_ws(self.__extra_query, self.__extra_headers)

        try:
            self.__connection = ForksConnection(
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
        except BaseException:
            self.__connection = None
            try:
                ws.close()
            except BaseException:
                # Preserve the exception that prevented successful entry.
                pass
            raise

        return self.__connection

    enter = __enter__

    def _connect_ws(self, extra_query: Query, extra_headers: Headers) -> WebSocketConnection:
        try:
            from websockets.sync.client import connect
        except ImportError as exc:
            raise OpenAIError("You need to install `openai[realtime]` to use this method") from exc

        url = self._prepare_url()
        try:
            # Older runtimes do not declare this optional helper.
            query_params = getattr(self.__client, "_websocket_query_params")  # noqa: B009
        except AttributeError:
            query_params = self.__client._websocket_query_params_fallback
        url = url.copy_with(
            params=query_params(
                url,
                extra_query,
            ),
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

        websocket_options = self.__websocket_connection_options.copy()
        websocket_options.setdefault("max_size", None)
        if websocket_options.get("max_size") is None:
            websocket_options.setdefault("compression", None)

        return connect(
            str(url),
            user_agent_header=None,
            additional_headers=_merge_mappings(dict(headers.values()), {}),
            **websocket_options,
        )

    def _prepare_url(self) -> httpx2.URL:
        if self.__client.websocket_base_url is not None:
            base_url = httpx2.URL(self.__client.websocket_base_url)
        else:
            scheme = self.__client._base_url.scheme
            ws_scheme = "ws" if scheme == "http" else "wss"
            base_url = self.__client._base_url.copy_with(scheme=ws_scheme)

        path, separator, query = base_url.raw_path.partition(b"?")
        merge_raw_path = (
            path.rstrip(b"/")
            + path_template("/live/sessions/{session_id}/fork", session_id=self.__session_id).encode("utf-8")
            + separator
            + query
        )
        return base_url.copy_with(raw_path=merge_raw_path)

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        if self.__connection is not None:
            try:
                self.__connection.close()
            except Exception:
                if exc is None:
                    raise


class BaseForksConnectionResource:
    def __init__(self, connection: ForksConnection) -> None:
        self._connection = connection


class ForksSessionResource(BaseForksConnectionResource):
    @cached_property
    def commentary(self) -> ForksSessionCommentaryResource:
        return ForksSessionCommentaryResource(self._connection)

    @cached_property
    def input_audio(self) -> ForksSessionInputAudioResource:
        return ForksSessionInputAudioResource(self._connection)

    @cached_property
    def instructions(self) -> ForksSessionInstructionsResource:
        return ForksSessionInstructionsResource(self._connection)

    @cached_property
    def output_audio(self) -> ForksSessionOutputAudioResource:
        return ForksSessionOutputAudioResource(self._connection)

    @cached_property
    def thinking(self) -> ForksSessionThinkingResource:
        return ForksSessionThinkingResource(self._connection)

    def start(self, *, session: ForkSessionConfigParam, event_id: Optional[str] | Omit = omit) -> None:
        """
        Start a Live session after connecting to a stored session’s fork WebSocket.

        Send an empty `session` object to use the stored configuration.
        """
        self._connection.send(
            cast(
                ForkClientEventParam,
                strip_not_given({"type": "session.start", "session": session, "event_id": event_id}),
            )
        )

    def close(self, *, event_id: Optional[str] | Omit = omit) -> None:
        """Request that the Live session close.

        The terminal `session.closed` event contains the close reason and final usage.
        """
        self._connection.send(
            cast(ForkClientEventParam, strip_not_given({"type": "session.close", "event_id": event_id}))
        )

    def update(self, *, session: SessionUpdateConfigParam, event_id: Optional[str] | Omit = omit) -> None:
        """
        Update the delegation settings or transcript triggers of an active Live session.

        The server acknowledges accepted changes with `session.updated`.
        """
        self._connection.send(
            cast(
                ForkClientEventParam,
                strip_not_given({"type": "session.update", "session": session, "event_id": event_id}),
            )
        )


class ForksSessionCommentaryResource(BaseForksConnectionResource):
    def append(self, *, content: str, delegation_id: Optional[str], event_id: Optional[str] | Omit = omit) -> None:
        """
        Provide context the Live model can communicate to the user, optionally for an
        existing client delegation.

        Rejected while an audio fixture is active.
        """
        self._connection.send(
            cast(
                ForkClientEventParam,
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


class ForksSessionInputAudioResource(BaseForksConnectionResource):
    def append(self, *, audio: str, event_id: Optional[str] | Omit = omit) -> None:
        """Send audio to a Live session over its primary WebSocket.

        WebRTC and SIP sessions send audio over their media transport.
        """
        self._connection.send(
            cast(
                ForkClientEventParam,
                strip_not_given({"type": "session.input_audio.append", "audio": audio, "event_id": event_id}),
            )
        )

    def mute(self, *, event_id: Optional[str] | Omit = omit) -> None:
        """Mute audio input to the Live model without closing the session.

        The server acknowledges with `session.input_audio.muted`.
        """
        self._connection.send(
            cast(ForkClientEventParam, strip_not_given({"type": "session.input_audio.mute", "event_id": event_id}))
        )

    def unmute(self, *, event_id: Optional[str] | Omit = omit) -> None:
        """Resume audio input to a Live model after muting it.

        The server acknowledges with `session.input_audio.unmuted`. An active audio fixture still pauses inference until playback finishes.
        """
        self._connection.send(
            cast(ForkClientEventParam, strip_not_given({"type": "session.input_audio.unmute", "event_id": event_id}))
        )


class ForksSessionInstructionsResource(BaseForksConnectionResource):
    def append(self, *, content: str, delegation_id: Optional[str], event_id: Optional[str] | Omit = omit) -> None:
        """Append developer instructions to the Live conversation while it is running,
        optionally associating them with an existing client delegation.

        Rejected while an audio fixture is active. These instructions remain in conversation history through compaction and are included in future backend delegations. For external audio, describe content already delivered so the assistant does not repeat it.
        """
        self._connection.send(
            cast(
                ForkClientEventParam,
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


class ForksSessionOutputAudioResource(BaseForksConnectionResource):
    @cached_property
    def fixture(self) -> ForksSessionOutputAudioFixtureResource:
        return ForksSessionOutputAudioFixtureResource(self._connection)


class ForksSessionThinkingResource(BaseForksConnectionResource):
    def append(self, *, content: str, delegation_id: Optional[str], event_id: Optional[str] | Omit = omit) -> None:
        """
        Provide silent reasoning or progress context to the Live model, optionally for
        an existing client delegation.

        Rejected while an audio fixture is active.
        """
        self._connection.send(
            cast(
                ForkClientEventParam,
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


class ForksSessionOutputAudioFixtureResource(BaseForksConnectionResource):
    def play(self, *, audio: str, event_id: Optional[str] | Omit = omit) -> None:
        """Play one complete audio fixture through the session output.

        Send this event over the primary WebSocket or a server sideband. Audio must be raw mono PCM16 little-endian at 24 kHz, regardless of the session audio format, and at most 30 seconds. The entire payload is validated before model speech is interrupted and input is muted. Only one fixture can be active. fixture.playing acknowledges acceptance and fixture.played reports server mixer drain. These notifications are not exact transport-media boundaries. Input arriving during playback is dropped and not replayed.
        """
        self._connection.send(
            cast(
                ForkClientEventParam,
                strip_not_given({"type": "session.output_audio.fixture.play", "audio": audio, "event_id": event_id}),
            )
        )


class ForksDecisionResource(BaseForksConnectionResource):
    @cached_property
    def item(self) -> ForksDecisionItemResource:
        return ForksDecisionItemResource(self._connection)

    def create(self, *, event_id: str) -> None:
        """
        Evaluate the configured questions using the current conversation and Decision
        inputs.

        Reusing an event_id is rejected for the lifetime of the session.
        """
        self._connection.send({"type": "decision.create", "event_id": event_id})


class ForksResponseResource(BaseForksConnectionResource):
    @cached_property
    def item(self) -> ForksResponseItemResource:
        return ForksResponseItemResource(self._connection)

    def create(self, *, event_id: Optional[str] | Omit = omit) -> None:
        """
        Request a response from the Live session’s Responses backend, or continue a
        delegated response waiting for tool results.

        Requires Responses delegation.
        """
        self._connection.send(
            cast(ForkClientEventParam, strip_not_given({"type": "response.create", "event_id": event_id}))
        )


class ForksDecisionItemResource(BaseForksConnectionResource):
    def delete(self, *, item_id: str, event_id: Optional[str] | Omit = omit) -> None:
        """
        Delete an input item from future decisions without starting an evaluation or changing Live voice context.
        """
        self._connection.send(
            cast(
                ForkClientEventParam,
                strip_not_given({"type": "decision.item.delete", "item_id": item_id, "event_id": event_id}),
            )
        )

    def create(
        self, *, item: decision_item_create_event_param.ItemUnion, event_id: Optional[str] | Omit = omit
    ) -> None:
        """
        Append an input item for future decisions without starting an evaluation or changing Live voice context.
        """
        self._connection.send(
            cast(
                ForkClientEventParam,
                strip_not_given({"type": "decision.item.create", "item": item, "event_id": event_id}),
            )
        )


class ForksResponseItemResource(BaseForksConnectionResource):
    def create(self, *, item: ResponseInputItemParam, event_id: Optional[str] | Omit = omit) -> None:
        """Add an input item to the Live session’s Responses backend.

        Requires Responses delegation; use `response.create` to request a response.
        """
        self._connection.send(
            cast(
                ForkClientEventParam,
                strip_not_given({"type": "response.item.create", "item": item, "event_id": event_id}),
            )
        )


class BaseAsyncForksConnectionResource:
    def __init__(self, connection: AsyncForksConnection) -> None:
        self._connection = connection


class AsyncForksSessionResource(BaseAsyncForksConnectionResource):
    @cached_property
    def commentary(self) -> AsyncForksSessionCommentaryResource:
        return AsyncForksSessionCommentaryResource(self._connection)

    @cached_property
    def input_audio(self) -> AsyncForksSessionInputAudioResource:
        return AsyncForksSessionInputAudioResource(self._connection)

    @cached_property
    def instructions(self) -> AsyncForksSessionInstructionsResource:
        return AsyncForksSessionInstructionsResource(self._connection)

    @cached_property
    def output_audio(self) -> AsyncForksSessionOutputAudioResource:
        return AsyncForksSessionOutputAudioResource(self._connection)

    @cached_property
    def thinking(self) -> AsyncForksSessionThinkingResource:
        return AsyncForksSessionThinkingResource(self._connection)

    async def start(self, *, session: ForkSessionConfigParam, event_id: Optional[str] | Omit = omit) -> None:
        """
        Start a Live session after connecting to a stored session’s fork WebSocket.

        Send an empty `session` object to use the stored configuration.
        """
        await self._connection.send(
            cast(
                ForkClientEventParam,
                strip_not_given({"type": "session.start", "session": session, "event_id": event_id}),
            )
        )

    async def close(self, *, event_id: Optional[str] | Omit = omit) -> None:
        """Request that the Live session close.

        The terminal `session.closed` event contains the close reason and final usage.
        """
        await self._connection.send(
            cast(ForkClientEventParam, strip_not_given({"type": "session.close", "event_id": event_id}))
        )

    async def update(self, *, session: SessionUpdateConfigParam, event_id: Optional[str] | Omit = omit) -> None:
        """
        Update the delegation settings or transcript triggers of an active Live session.

        The server acknowledges accepted changes with `session.updated`.
        """
        await self._connection.send(
            cast(
                ForkClientEventParam,
                strip_not_given({"type": "session.update", "session": session, "event_id": event_id}),
            )
        )


class AsyncForksSessionCommentaryResource(BaseAsyncForksConnectionResource):
    async def append(
        self, *, content: str, delegation_id: Optional[str], event_id: Optional[str] | Omit = omit
    ) -> None:
        """
        Provide context the Live model can communicate to the user, optionally for an
        existing client delegation.

        Rejected while an audio fixture is active.
        """
        await self._connection.send(
            cast(
                ForkClientEventParam,
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


class AsyncForksSessionInputAudioResource(BaseAsyncForksConnectionResource):
    async def append(self, *, audio: str, event_id: Optional[str] | Omit = omit) -> None:
        """Send audio to a Live session over its primary WebSocket.

        WebRTC and SIP sessions send audio over their media transport.
        """
        await self._connection.send(
            cast(
                ForkClientEventParam,
                strip_not_given({"type": "session.input_audio.append", "audio": audio, "event_id": event_id}),
            )
        )

    async def mute(self, *, event_id: Optional[str] | Omit = omit) -> None:
        """Mute audio input to the Live model without closing the session.

        The server acknowledges with `session.input_audio.muted`.
        """
        await self._connection.send(
            cast(ForkClientEventParam, strip_not_given({"type": "session.input_audio.mute", "event_id": event_id}))
        )

    async def unmute(self, *, event_id: Optional[str] | Omit = omit) -> None:
        """Resume audio input to a Live model after muting it.

        The server acknowledges with `session.input_audio.unmuted`. An active audio fixture still pauses inference until playback finishes.
        """
        await self._connection.send(
            cast(ForkClientEventParam, strip_not_given({"type": "session.input_audio.unmute", "event_id": event_id}))
        )


class AsyncForksSessionInstructionsResource(BaseAsyncForksConnectionResource):
    async def append(
        self, *, content: str, delegation_id: Optional[str], event_id: Optional[str] | Omit = omit
    ) -> None:
        """Append developer instructions to the Live conversation while it is running,
        optionally associating them with an existing client delegation.

        Rejected while an audio fixture is active. These instructions remain in conversation history through compaction and are included in future backend delegations. For external audio, describe content already delivered so the assistant does not repeat it.
        """
        await self._connection.send(
            cast(
                ForkClientEventParam,
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


class AsyncForksSessionOutputAudioResource(BaseAsyncForksConnectionResource):
    @cached_property
    def fixture(self) -> AsyncForksSessionOutputAudioFixtureResource:
        return AsyncForksSessionOutputAudioFixtureResource(self._connection)


class AsyncForksSessionThinkingResource(BaseAsyncForksConnectionResource):
    async def append(
        self, *, content: str, delegation_id: Optional[str], event_id: Optional[str] | Omit = omit
    ) -> None:
        """
        Provide silent reasoning or progress context to the Live model, optionally for
        an existing client delegation.

        Rejected while an audio fixture is active.
        """
        await self._connection.send(
            cast(
                ForkClientEventParam,
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


class AsyncForksSessionOutputAudioFixtureResource(BaseAsyncForksConnectionResource):
    async def play(self, *, audio: str, event_id: Optional[str] | Omit = omit) -> None:
        """Play one complete audio fixture through the session output.

        Send this event over the primary WebSocket or a server sideband. Audio must be raw mono PCM16 little-endian at 24 kHz, regardless of the session audio format, and at most 30 seconds. The entire payload is validated before model speech is interrupted and input is muted. Only one fixture can be active. fixture.playing acknowledges acceptance and fixture.played reports server mixer drain. These notifications are not exact transport-media boundaries. Input arriving during playback is dropped and not replayed.
        """
        await self._connection.send(
            cast(
                ForkClientEventParam,
                strip_not_given({"type": "session.output_audio.fixture.play", "audio": audio, "event_id": event_id}),
            )
        )


class AsyncForksDecisionResource(BaseAsyncForksConnectionResource):
    @cached_property
    def item(self) -> AsyncForksDecisionItemResource:
        return AsyncForksDecisionItemResource(self._connection)

    async def create(self, *, event_id: str) -> None:
        """
        Evaluate the configured questions using the current conversation and Decision
        inputs.

        Reusing an event_id is rejected for the lifetime of the session.
        """
        await self._connection.send({"type": "decision.create", "event_id": event_id})


class AsyncForksResponseResource(BaseAsyncForksConnectionResource):
    @cached_property
    def item(self) -> AsyncForksResponseItemResource:
        return AsyncForksResponseItemResource(self._connection)

    async def create(self, *, event_id: Optional[str] | Omit = omit) -> None:
        """
        Request a response from the Live session’s Responses backend, or continue a
        delegated response waiting for tool results.

        Requires Responses delegation.
        """
        await self._connection.send(
            cast(ForkClientEventParam, strip_not_given({"type": "response.create", "event_id": event_id}))
        )


class AsyncForksDecisionItemResource(BaseAsyncForksConnectionResource):
    async def delete(self, *, item_id: str, event_id: Optional[str] | Omit = omit) -> None:
        """
        Delete an input item from future decisions without starting an evaluation or changing Live voice context.
        """
        await self._connection.send(
            cast(
                ForkClientEventParam,
                strip_not_given({"type": "decision.item.delete", "item_id": item_id, "event_id": event_id}),
            )
        )

    async def create(
        self, *, item: decision_item_create_event_param.ItemUnion, event_id: Optional[str] | Omit = omit
    ) -> None:
        """
        Append an input item for future decisions without starting an evaluation or changing Live voice context.
        """
        await self._connection.send(
            cast(
                ForkClientEventParam,
                strip_not_given({"type": "decision.item.create", "item": item, "event_id": event_id}),
            )
        )


class AsyncForksResponseItemResource(BaseAsyncForksConnectionResource):
    async def create(self, *, item: ResponseInputItemParam, event_id: Optional[str] | Omit = omit) -> None:
        """Add an input item to the Live session’s Responses backend.

        Requires Responses delegation; use `response.create` to request a response.
        """
        await self._connection.send(
            cast(
                ForkClientEventParam,
                strip_not_given({"type": "response.item.create", "item": item, "event_id": event_id}),
            )
        )
