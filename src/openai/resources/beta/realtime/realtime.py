# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import json
import logging
from types import TracebackType
from typing import TYPE_CHECKING, Any, Iterator, cast
from typing_extensions import AsyncIterator

import httpx
from pydantic import BaseModel

from .sessions import (
    Sessions,
    AsyncSessions,
    SessionsWithRawResponse,
    AsyncSessionsWithRawResponse,
    SessionsWithStreamingResponse,
    AsyncSessionsWithStreamingResponse,
)
from ...._types import NOT_GIVEN, Query, Headers, NotGiven
from ...._utils import (
    maybe_transform,
    strip_not_given,
    async_maybe_transform,
)
from ...._compat import cached_property
from ...._models import construct_type_unchecked
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._exceptions import OpenAIError
from ...._base_client import _merge_mappings
from ....types.beta.realtime import session_update_event_param, response_create_event_param
from ....types.websocket_connection_options import WebsocketConnectionOptions
from ....types.beta.realtime.realtime_client_event import RealtimeClientEvent
from ....types.beta.realtime.realtime_server_event import RealtimeServerEvent
from ....types.beta.realtime.conversation_item_param import ConversationItemParam
from ....types.beta.realtime.realtime_client_event_param import RealtimeClientEventParam

if TYPE_CHECKING:
    from websockets.sync.client import ClientConnection as WebsocketConnection
    from websockets.asyncio.client import ClientConnection as AsyncWebsocketConnection

    from ...._client import OpenAI, AsyncOpenAI

__all__ = ["Realtime", "AsyncRealtime"]

log: logging.Logger = logging.getLogger(__name__)


class Realtime(SyncAPIResource):
    @cached_property
    def sessions(self) -> Sessions:
        return Sessions(self._client)

    @cached_property
    def with_raw_response(self) -> RealtimeWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
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
        model: str,
        extra_query: Query = {},
        extra_headers: Headers = {},
        websocket_connection_options: WebsocketConnectionOptions = {},
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
            model=model,
        )


class AsyncRealtime(AsyncAPIResource):
    @cached_property
    def sessions(self) -> AsyncSessions:
        return AsyncSessions(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncRealtimeWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
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
        model: str,
        extra_query: Query = {},
        extra_headers: Headers = {},
        websocket_connection_options: WebsocketConnectionOptions = {},
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
            model=model,
        )


class RealtimeWithRawResponse:
    def __init__(self, realtime: Realtime) -> None:
        self._realtime = realtime

    @cached_property
    def sessions(self) -> SessionsWithRawResponse:
        return SessionsWithRawResponse(self._realtime.sessions)


class AsyncRealtimeWithRawResponse:
    def __init__(self, realtime: AsyncRealtime) -> None:
        self._realtime = realtime

    @cached_property
    def sessions(self) -> AsyncSessionsWithRawResponse:
        return AsyncSessionsWithRawResponse(self._realtime.sessions)


class RealtimeWithStreamingResponse:
    def __init__(self, realtime: Realtime) -> None:
        self._realtime = realtime

    @cached_property
    def sessions(self) -> SessionsWithStreamingResponse:
        return SessionsWithStreamingResponse(self._realtime.sessions)


class AsyncRealtimeWithStreamingResponse:
    def __init__(self, realtime: AsyncRealtime) -> None:
        self._realtime = realtime

    @cached_property
    def sessions(self) -> AsyncSessionsWithStreamingResponse:
        return AsyncSessionsWithStreamingResponse(self._realtime.sessions)


class AsyncRealtimeConnection:
    """Represents a live websocket connection to the Realtime API"""

    session: AsyncRealtimeSessionResource
    response: AsyncRealtimeResponseResource
    conversation: AsyncRealtimeConversationResource
    input_audio_buffer: AsyncRealtimeInputAudioBufferResource

    _connection: AsyncWebsocketConnection

    def __init__(self, connection: AsyncWebsocketConnection) -> None:
        self._connection = connection

        self.session = AsyncRealtimeSessionResource(self)
        self.response = AsyncRealtimeResponseResource(self)
        self.conversation = AsyncRealtimeConversationResource(self)
        self.input_audio_buffer = AsyncRealtimeInputAudioBufferResource(self)

    async def __aiter__(self) -> AsyncIterator[RealtimeServerEvent]:
        """
        An infinite-iterator that will continue to yield events until
        the connection is closed.
        """
        from websockets.exceptions import ConnectionClosedOK

        try:
            while True:
                yield await self.recv()
        except ConnectionClosedOK:
            return

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
        log.debug(f"Received websocket message: %s", message)
        if not isinstance(message, bytes):
            # passing `decode=False` should always result in us getting `bytes` back
            raise TypeError(f"Expected `.recv(decode=False)` to return `bytes` but got {type(message)}")

        return message

    async def send(self, event: RealtimeClientEvent | RealtimeClientEventParam) -> None:
        data = (
            event.to_json(use_api_names=True, exclude_defaults=True, exclude_unset=True)
            if isinstance(event, BaseModel)
            else json.dumps(await async_maybe_transform(event, RealtimeClientEventParam))
        )
        await self._connection.send(data)

    async def close(self, *, code: int = 1000, reason: str = "") -> None:
        await self._connection.close(code=code, reason=reason)

    def parse_event(self, data: str | bytes) -> RealtimeServerEvent:
        """
        Converts a raw `str` or `bytes` message into a `RealtimeServerEvent` object.

        This is helpful if you're using `.recv_bytes()`.
        """
        return cast(
            RealtimeServerEvent, construct_type_unchecked(value=json.loads(data), type_=cast(Any, RealtimeServerEvent))
        )


class AsyncRealtimeConnectionManager:
    """
    Context manager over a `AsyncRealtimeConnection` that is returned by `beta.realtime.connect()`

    This context manager ensures that the connection will be closed when it exits.

    ---

    Note that if your application doesn't work well with the context manager approach then you
    can call the `.enter()` method directly to initiate a connection.

    **Warning**: You must remember to close the connection with `.close()`.

    ```py
    connection = await client.beta.realtime.connect(...).enter()
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
        websocket_connection_options: WebsocketConnectionOptions,
    ) -> None:
        self.__client = client
        self.__model = model
        self.__connection: AsyncRealtimeConnection | None = None
        self.__extra_query = extra_query
        self.__extra_headers = extra_headers
        self.__websocket_connection_options = websocket_connection_options

    async def __aenter__(self) -> AsyncRealtimeConnection:
        """
        👋 If your application doesn't work well with the context manager approach then you
        can call this method directly to initiate a connection.

        **Warning**: You must remember to close the connection with `.close()`.

        ```py
        connection = await client.beta.realtime.connect(...).enter()
        # ...
        await connection.close()
        ```
        """
        try:
            from websockets.asyncio.client import connect
        except ImportError as exc:
            raise OpenAIError("You need to install `openai[realtime]` to use this method") from exc

        url = self._prepare_url().copy_with(
            params={
                **self.__client.base_url.params,
                "model": self.__model,
                **self.__extra_query,
            },
        )
        log.debug("Connecting to %s", url)
        if self.__websocket_connection_options:
            log.debug("Connection options: %s", self.__websocket_connection_options)

        self.__connection = AsyncRealtimeConnection(
            await connect(
                str(url),
                user_agent_header=self.__client.user_agent,
                additional_headers=_merge_mappings(
                    {
                        **self.__client.auth_headers,
                        "OpenAI-Beta": "realtime=v1",
                    },
                    self.__extra_headers,
                ),
                **self.__websocket_connection_options,
            )
        )

        return self.__connection

    enter = __aenter__

    def _prepare_url(self) -> httpx.URL:
        if self.__client.websocket_base_url is not None:
            base_url = httpx.URL(self.__client.websocket_base_url)
        else:
            base_url = self.__client._base_url.copy_with(scheme="wss")

        merge_raw_path = base_url.raw_path.rstrip(b"/") + b"/realtime"
        return base_url.copy_with(raw_path=merge_raw_path)

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        if self.__connection is not None:
            await self.__connection.close()


class RealtimeConnection:
    """Represents a live websocket connection to the Realtime API"""

    session: RealtimeSessionResource
    response: RealtimeResponseResource
    conversation: RealtimeConversationResource
    input_audio_buffer: RealtimeInputAudioBufferResource

    _connection: WebsocketConnection

    def __init__(self, connection: WebsocketConnection) -> None:
        self._connection = connection

        self.session = RealtimeSessionResource(self)
        self.response = RealtimeResponseResource(self)
        self.conversation = RealtimeConversationResource(self)
        self.input_audio_buffer = RealtimeInputAudioBufferResource(self)

    def __iter__(self) -> Iterator[RealtimeServerEvent]:
        """
        An infinite-iterator that will continue to yield events until
        the connection is closed.
        """
        from websockets.exceptions import ConnectionClosedOK

        try:
            while True:
                yield self.recv()
        except ConnectionClosedOK:
            return

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
        log.debug(f"Received websocket message: %s", message)
        if not isinstance(message, bytes):
            # passing `decode=False` should always result in us getting `bytes` back
            raise TypeError(f"Expected `.recv(decode=False)` to return `bytes` but got {type(message)}")

        return message

    def send(self, event: RealtimeClientEvent | RealtimeClientEventParam) -> None:
        data = (
            event.to_json(use_api_names=True, exclude_defaults=True, exclude_unset=True)
            if isinstance(event, BaseModel)
            else json.dumps(maybe_transform(event, RealtimeClientEventParam))
        )
        self._connection.send(data)

    def close(self, *, code: int = 1000, reason: str = "") -> None:
        self._connection.close(code=code, reason=reason)

    def parse_event(self, data: str | bytes) -> RealtimeServerEvent:
        """
        Converts a raw `str` or `bytes` message into a `RealtimeServerEvent` object.

        This is helpful if you're using `.recv_bytes()`.
        """
        return cast(
            RealtimeServerEvent, construct_type_unchecked(value=json.loads(data), type_=cast(Any, RealtimeServerEvent))
        )


class RealtimeConnectionManager:
    """
    Context manager over a `RealtimeConnection` that is returned by `beta.realtime.connect()`

    This context manager ensures that the connection will be closed when it exits.

    ---

    Note that if your application doesn't work well with the context manager approach then you
    can call the `.enter()` method directly to initiate a connection.

    **Warning**: You must remember to close the connection with `.close()`.

    ```py
    connection = client.beta.realtime.connect(...).enter()
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
        websocket_connection_options: WebsocketConnectionOptions,
    ) -> None:
        self.__client = client
        self.__model = model
        self.__connection: RealtimeConnection | None = None
        self.__extra_query = extra_query
        self.__extra_headers = extra_headers
        self.__websocket_connection_options = websocket_connection_options

    def __enter__(self) -> RealtimeConnection:
        """
        👋 If your application doesn't work well with the context manager approach then you
        can call this method directly to initiate a connection.

        **Warning**: You must remember to close the connection with `.close()`.

        ```py
        connection = client.beta.realtime.connect(...).enter()
        # ...
        connection.close()
        ```
        """
        try:
            from websockets.sync.client import connect
        except ImportError as exc:
            raise OpenAIError("You need to install `openai[realtime]` to use this method") from exc

        url = self._prepare_url().copy_with(
            params={
                **self.__client.base_url.params,
                "model": self.__model,
                **self.__extra_query,
            },
        )
        log.debug("Connecting to %s", url)
        if self.__websocket_connection_options:
            log.debug("Connection options: %s", self.__websocket_connection_options)

        self.__connection = RealtimeConnection(
            connect(
                str(url),
                user_agent_header=self.__client.user_agent,
                additional_headers=_merge_mappings(
                    {
                        **self.__client.auth_headers,
                        "OpenAI-Beta": "realtime=v1",
                    },
                    self.__extra_headers,
                ),
                **self.__websocket_connection_options,
            )
        )

        return self.__connection

    enter = __enter__

    def _prepare_url(self) -> httpx.URL:
        if self.__client.websocket_base_url is not None:
            base_url = httpx.URL(self.__client.websocket_base_url)
        else:
            base_url = self.__client._base_url.copy_with(scheme="wss")

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
    def update(self, *, session: session_update_event_param.Session, event_id: str | NotGiven = NOT_GIVEN) -> None:
        """Send this event to update the session’s default configuration.

        The client may
        send this event at any time to update the session configuration, and any
        field may be updated at any time, except for "voice". The server will respond
        with a `session.updated` event that shows the full effective configuration.
        Only fields that are present are updated, thus the correct way to clear a
        field like "instructions" is to pass an empty string.
        """
        self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given({"type": "session.update", "session": session, "event_id": event_id}),
            )
        )


class RealtimeResponseResource(BaseRealtimeConnectionResource):
    def cancel(self, *, event_id: str | NotGiven = NOT_GIVEN, response_id: str | NotGiven = NOT_GIVEN) -> None:
        """Send this event to cancel an in-progress response.

        The server will respond
        with a `response.cancelled` event or an error if there is no response to
        cancel.
        """
        self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given({"type": "response.cancel", "event_id": event_id, "response_id": response_id}),
            )
        )

    def create(
        self,
        *,
        event_id: str | NotGiven = NOT_GIVEN,
        response: response_create_event_param.Response | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        This event instructs the server to create a Response, which means triggering
        model inference. When in Server VAD mode, the server will create Responses
        automatically.

        A Response will include at least one Item, and may have two, in which case
        the second will be a function call. These Items will be appended to the
        conversation history.

        The server will respond with a `response.created` event, events for Items
        and content created, and finally a `response.done` event to indicate the
        Response is complete.

        The `response.create` event includes inference configuration like
        `instructions`, and `temperature`. These fields will override the Session's
        configuration for this Response only.
        """
        self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given({"type": "response.create", "event_id": event_id, "response": response}),
            )
        )


class RealtimeConversationResource(BaseRealtimeConnectionResource):
    @cached_property
    def item(self) -> RealtimeConversationItemResource:
        return RealtimeConversationItemResource(self._connection)


class RealtimeConversationItemResource(BaseRealtimeConnectionResource):
    def delete(self, *, item_id: str, event_id: str | NotGiven = NOT_GIVEN) -> None:
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
        self,
        *,
        item: ConversationItemParam,
        event_id: str | NotGiven = NOT_GIVEN,
        previous_item_id: str | NotGiven = NOT_GIVEN,
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

    def truncate(
        self, *, audio_end_ms: int, content_index: int, item_id: str, event_id: str | NotGiven = NOT_GIVEN
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


class RealtimeInputAudioBufferResource(BaseRealtimeConnectionResource):
    def clear(self, *, event_id: str | NotGiven = NOT_GIVEN) -> None:
        """Send this event to clear the audio bytes in the buffer.

        The server will
        respond with an `input_audio_buffer.cleared` event.
        """
        self._connection.send(
            cast(RealtimeClientEventParam, strip_not_given({"type": "input_audio_buffer.clear", "event_id": event_id}))
        )

    def commit(self, *, event_id: str | NotGiven = NOT_GIVEN) -> None:
        """
        Send this event to commit the user input audio buffer, which will create a
        new user message item in the conversation. This event will produce an error
        if the input audio buffer is empty. When in Server VAD mode, the client does
        not need to send this event, the server will commit the audio buffer
        automatically.

        Committing the input audio buffer will trigger input audio transcription
        (if enabled in session configuration), but it will not create a response
        from the model. The server will respond with an `input_audio_buffer.committed`
        event.
        """
        self._connection.send(
            cast(RealtimeClientEventParam, strip_not_given({"type": "input_audio_buffer.commit", "event_id": event_id}))
        )

    def append(self, *, audio: str, event_id: str | NotGiven = NOT_GIVEN) -> None:
        """Send this event to append audio bytes to the input audio buffer.

        The audio
        buffer is temporary storage you can write to and later commit. In Server VAD
        mode, the audio buffer is used to detect speech and the server will decide
        when to commit. When Server VAD is disabled, you must commit the audio buffer
        manually.

        The client may choose how much audio to place in each event up to a maximum
        of 15 MiB, for example streaming smaller chunks from the client may allow the
        VAD to be more responsive. Unlike made other client events, the server will
        not send a confirmation response to this event.
        """
        self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given({"type": "input_audio_buffer.append", "audio": audio, "event_id": event_id}),
            )
        )


class BaseAsyncRealtimeConnectionResource:
    def __init__(self, connection: AsyncRealtimeConnection) -> None:
        self._connection = connection


class AsyncRealtimeSessionResource(BaseAsyncRealtimeConnectionResource):
    async def update(
        self, *, session: session_update_event_param.Session, event_id: str | NotGiven = NOT_GIVEN
    ) -> None:
        """Send this event to update the session’s default configuration.

        The client may
        send this event at any time to update the session configuration, and any
        field may be updated at any time, except for "voice". The server will respond
        with a `session.updated` event that shows the full effective configuration.
        Only fields that are present are updated, thus the correct way to clear a
        field like "instructions" is to pass an empty string.
        """
        await self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given({"type": "session.update", "session": session, "event_id": event_id}),
            )
        )


class AsyncRealtimeResponseResource(BaseAsyncRealtimeConnectionResource):
    async def cancel(self, *, event_id: str | NotGiven = NOT_GIVEN, response_id: str | NotGiven = NOT_GIVEN) -> None:
        """Send this event to cancel an in-progress response.

        The server will respond
        with a `response.cancelled` event or an error if there is no response to
        cancel.
        """
        await self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given({"type": "response.cancel", "event_id": event_id, "response_id": response_id}),
            )
        )

    async def create(
        self,
        *,
        event_id: str | NotGiven = NOT_GIVEN,
        response: response_create_event_param.Response | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        This event instructs the server to create a Response, which means triggering
        model inference. When in Server VAD mode, the server will create Responses
        automatically.

        A Response will include at least one Item, and may have two, in which case
        the second will be a function call. These Items will be appended to the
        conversation history.

        The server will respond with a `response.created` event, events for Items
        and content created, and finally a `response.done` event to indicate the
        Response is complete.

        The `response.create` event includes inference configuration like
        `instructions`, and `temperature`. These fields will override the Session's
        configuration for this Response only.
        """
        await self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given({"type": "response.create", "event_id": event_id, "response": response}),
            )
        )


class AsyncRealtimeConversationResource(BaseAsyncRealtimeConnectionResource):
    @cached_property
    def item(self) -> AsyncRealtimeConversationItemResource:
        return AsyncRealtimeConversationItemResource(self._connection)


class AsyncRealtimeConversationItemResource(BaseAsyncRealtimeConnectionResource):
    async def delete(self, *, item_id: str, event_id: str | NotGiven = NOT_GIVEN) -> None:
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
        self,
        *,
        item: ConversationItemParam,
        event_id: str | NotGiven = NOT_GIVEN,
        previous_item_id: str | NotGiven = NOT_GIVEN,
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
        self, *, audio_end_ms: int, content_index: int, item_id: str, event_id: str | NotGiven = NOT_GIVEN
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


class AsyncRealtimeInputAudioBufferResource(BaseAsyncRealtimeConnectionResource):
    async def clear(self, *, event_id: str | NotGiven = NOT_GIVEN) -> None:
        """Send this event to clear the audio bytes in the buffer.

        The server will
        respond with an `input_audio_buffer.cleared` event.
        """
        await self._connection.send(
            cast(RealtimeClientEventParam, strip_not_given({"type": "input_audio_buffer.clear", "event_id": event_id}))
        )

    async def commit(self, *, event_id: str | NotGiven = NOT_GIVEN) -> None:
        """
        Send this event to commit the user input audio buffer, which will create a
        new user message item in the conversation. This event will produce an error
        if the input audio buffer is empty. When in Server VAD mode, the client does
        not need to send this event, the server will commit the audio buffer
        automatically.

        Committing the input audio buffer will trigger input audio transcription
        (if enabled in session configuration), but it will not create a response
        from the model. The server will respond with an `input_audio_buffer.committed`
        event.
        """
        await self._connection.send(
            cast(RealtimeClientEventParam, strip_not_given({"type": "input_audio_buffer.commit", "event_id": event_id}))
        )

    async def append(self, *, audio: str, event_id: str | NotGiven = NOT_GIVEN) -> None:
        """Send this event to append audio bytes to the input audio buffer.

        The audio
        buffer is temporary storage you can write to and later commit. In Server VAD
        mode, the audio buffer is used to detect speech and the server will decide
        when to commit. When Server VAD is disabled, you must commit the audio buffer
        manually.

        The client may choose how much audio to place in each event up to a maximum
        of 15 MiB, for example streaming smaller chunks from the client may allow the
        VAD to be more responsive. Unlike made other client events, the server will
        not send a confirmation response to this event.
        """
        await self._connection.send(
            cast(
                RealtimeClientEventParam,
                strip_not_given({"type": "input_audio_buffer.append", "audio": audio, "event_id": event_id}),
            )
        )
