from __future__ import annotations

import inspect
from types import TracebackType
from typing import Any, List, Generic, Iterable, Awaitable, cast
from typing_extensions import Self, Callable, Iterator, AsyncIterator

from ._types import ParsedResponseSnapshot
from ._events import (
    ResponseStreamEvent,
    ResponseTextDoneEvent,
    ResponseCompletedEvent,
    ResponseTextDeltaEvent,
    ResponseFunctionCallArgumentsDeltaEvent,
)
from ...._types import NOT_GIVEN, NotGiven
from ...._utils import is_given, consume_sync_iterator, consume_async_iterator
from ...._models import build, construct_type_unchecked
from ...._streaming import Stream, AsyncStream
from ....types.responses import ParsedResponse, ResponseStreamEvent as RawResponseStreamEvent
from ..._parsing._responses import TextFormatT, parse_text, parse_response
from ....types.responses.tool_param import ToolParam
from ....types.responses.parsed_response import (
    ParsedContent,
    ParsedResponseOutputMessage,
    ParsedResponseFunctionToolCall,
)


class ResponseStream(Generic[TextFormatT]):
    def __init__(
        self,
        *,
        raw_stream: Stream[RawResponseStreamEvent],
        text_format: type[TextFormatT] | NotGiven,
        input_tools: Iterable[ToolParam] | NotGiven,
    ) -> None:
        self._raw_stream = raw_stream
        self._response = raw_stream.response
        self._iterator = self.__stream__()
        self._state = ResponseStreamState(text_format=text_format, input_tools=input_tools)

    def __next__(self) -> ResponseStreamEvent[TextFormatT]:
        return self._iterator.__next__()

    def __iter__(self) -> Iterator[ResponseStreamEvent[TextFormatT]]:
        for item in self._iterator:
            yield item

    def __enter__(self) -> Self:
        return self

    def __stream__(self) -> Iterator[ResponseStreamEvent[TextFormatT]]:
        for sse_event in self._raw_stream:
            events_to_fire = self._state.handle_event(sse_event)
            for event in events_to_fire:
                yield event

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        """
        Close the response and release the connection.

        Automatically called if the response body is read to completion.
        """
        self._response.close()

    def get_final_response(self) -> ParsedResponse[TextFormatT]:
        """Waits until the stream has been read to completion and returns
        the accumulated `ParsedResponse` object.
        """
        self.until_done()
        response = self._state._completed_response
        if not response:
            raise RuntimeError("Didn't receive a `response.completed` event.")

        return response

    def until_done(self) -> Self:
        """Blocks until the stream has been consumed."""
        consume_sync_iterator(self)
        return self


class ResponseStreamManager(Generic[TextFormatT]):
    def __init__(
        self,
        api_request: Callable[[], Stream[RawResponseStreamEvent]],
        *,
        text_format: type[TextFormatT] | NotGiven,
        input_tools: Iterable[ToolParam] | NotGiven,
    ) -> None:
        self.__stream: ResponseStream[TextFormatT] | None = None
        self.__api_request = api_request
        self.__text_format = text_format
        self.__input_tools = input_tools

    def __enter__(self) -> ResponseStream[TextFormatT]:
        raw_stream = self.__api_request()

        self.__stream = ResponseStream(
            raw_stream=raw_stream,
            text_format=self.__text_format,
            input_tools=self.__input_tools,
        )

        return self.__stream

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.__stream is not None:
            self.__stream.close()


class AsyncResponseStream(Generic[TextFormatT]):
    def __init__(
        self,
        *,
        raw_stream: AsyncStream[RawResponseStreamEvent],
        text_format: type[TextFormatT] | NotGiven,
        input_tools: Iterable[ToolParam] | NotGiven,
    ) -> None:
        self._raw_stream = raw_stream
        self._response = raw_stream.response
        self._iterator = self.__stream__()
        self._state = ResponseStreamState(text_format=text_format, input_tools=input_tools)

    async def __anext__(self) -> ResponseStreamEvent[TextFormatT]:
        return await self._iterator.__anext__()

    async def __aiter__(self) -> AsyncIterator[ResponseStreamEvent[TextFormatT]]:
        async for item in self._iterator:
            yield item

    async def __stream__(self) -> AsyncIterator[ResponseStreamEvent[TextFormatT]]:
        async for sse_event in self._raw_stream:
            events_to_fire = self._state.handle_event(sse_event)
            for event in events_to_fire:
                yield event

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """
        Close the response and release the connection.

        Automatically called if the response body is read to completion.
        """
        await self._response.aclose()

    async def get_final_response(self) -> ParsedResponse[TextFormatT]:
        """Waits until the stream has been read to completion and returns
        the accumulated `ParsedResponse` object.
        """
        await self.until_done()
        response = self._state._completed_response
        if not response:
            raise RuntimeError("Didn't receive a `response.completed` event.")

        return response

    async def until_done(self) -> Self:
        """Blocks until the stream has been consumed."""
        await consume_async_iterator(self)
        return self


class AsyncResponseStreamManager(Generic[TextFormatT]):
    def __init__(
        self,
        api_request: Awaitable[AsyncStream[RawResponseStreamEvent]],
        *,
        text_format: type[TextFormatT] | NotGiven,
        input_tools: Iterable[ToolParam] | NotGiven,
    ) -> None:
        self.__stream: AsyncResponseStream[TextFormatT] | None = None
        self.__api_request = api_request
        self.__text_format = text_format
        self.__input_tools = input_tools

    async def __aenter__(self) -> AsyncResponseStream[TextFormatT]:
        raw_stream = await self.__api_request

        self.__stream = AsyncResponseStream(
            raw_stream=raw_stream,
            text_format=self.__text_format,
            input_tools=self.__input_tools,
        )

        return self.__stream

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.__stream is not None:
            await self.__stream.close()


class ResponseStreamState(Generic[TextFormatT]):
    def __init__(
        self,
        *,
        input_tools: Iterable[ToolParam] | NotGiven,
        text_format: type[TextFormatT] | NotGiven,
    ) -> None:
        self.__current_snapshot: ParsedResponseSnapshot | None = None
        self._completed_response: ParsedResponse[TextFormatT] | None = None
        self._input_tools = [tool for tool in input_tools] if is_given(input_tools) else []
        self._text_format = text_format
        self._rich_text_format: type | NotGiven = text_format if inspect.isclass(text_format) else NOT_GIVEN

    def handle_event(self, event: RawResponseStreamEvent) -> List[ResponseStreamEvent[TextFormatT]]:
        self.__current_snapshot = snapshot = self.accumulate_event(event)

        events: List[ResponseStreamEvent[TextFormatT]] = []

        if event.type == "response.output_text.delta":
            output = snapshot.output[event.output_index]
            assert output.type == "message"

            content = output.content[event.content_index]
            assert content.type == "output_text"

            events.append(
                build(
                    ResponseTextDeltaEvent,
                    content_index=event.content_index,
                    delta=event.delta,
                    item_id=event.item_id,
                    output_index=event.output_index,
                    type="response.output_text.delta",
                    snapshot=content.text,
                )
            )
        elif event.type == "response.output_text.done":
            output = snapshot.output[event.output_index]
            assert output.type == "message"

            content = output.content[event.content_index]
            assert content.type == "output_text"

            events.append(
                build(
                    ResponseTextDoneEvent[TextFormatT],
                    content_index=event.content_index,
                    item_id=event.item_id,
                    output_index=event.output_index,
                    type="response.output_text.done",
                    text=event.text,
                    parsed=parse_text(event.text, text_format=self._text_format),
                )
            )
        elif event.type == "response.function_call_arguments.delta":
            output = snapshot.output[event.output_index]
            assert output.type == "function_call"

            events.append(
                build(
                    ResponseFunctionCallArgumentsDeltaEvent,
                    delta=event.delta,
                    item_id=event.item_id,
                    output_index=event.output_index,
                    type="response.function_call_arguments.delta",
                    snapshot=output.arguments,
                )
            )

        elif event.type == "response.completed":
            response = self._completed_response
            assert response is not None

            events.append(
                build(
                    ResponseCompletedEvent,
                    type="response.completed",
                    response=response,
                )
            )
        else:
            events.append(event)

        return events

    def accumulate_event(self, event: RawResponseStreamEvent) -> ParsedResponseSnapshot:
        snapshot = self.__current_snapshot
        if snapshot is None:
            return self._create_initial_response(event)

        if event.type == "response.output_item.added":
            if event.item.type == "function_call":
                snapshot.output.append(
                    construct_type_unchecked(
                        type_=cast(Any, ParsedResponseFunctionToolCall), value=event.item.to_dict()
                    )
                )
            elif event.item.type == "message":
                snapshot.output.append(
                    construct_type_unchecked(type_=cast(Any, ParsedResponseOutputMessage), value=event.item.to_dict())
                )
            else:
                snapshot.output.append(event.item)
        elif event.type == "response.content_part.added":
            output = snapshot.output[event.output_index]
            if output.type == "message":
                output.content.append(
                    construct_type_unchecked(type_=cast(Any, ParsedContent), value=event.part.to_dict())
                )
        elif event.type == "response.output_text.delta":
            output = snapshot.output[event.output_index]
            if output.type == "message":
                content = output.content[event.content_index]
                assert content.type == "output_text"
                content.text += event.delta
        elif event.type == "response.function_call_arguments.delta":
            output = snapshot.output[event.output_index]
            if output.type == "function_call":
                output.arguments += event.delta
        elif event.type == "response.completed":
            self._completed_response = parse_response(
                text_format=self._text_format,
                response=event.response,
                input_tools=self._input_tools,
            )

        return snapshot

    def _create_initial_response(self, event: RawResponseStreamEvent) -> ParsedResponseSnapshot:
        if event.type != "response.created":
            raise RuntimeError(f"Expected to have received `response.created` before `{event.type}`")

        return construct_type_unchecked(type_=ParsedResponseSnapshot, value=event.response.to_dict())
