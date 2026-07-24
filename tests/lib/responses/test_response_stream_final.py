from __future__ import annotations

from typing import Any, Iterator, AsyncIterator, cast

import httpx
import pytest
import pydantic

from openai import omit
from openai._models import construct_type_unchecked
from openai.types.responses import (
    ResponseFailedEvent,
    ResponseStreamEvent as RawResponseStreamEvent,
    ResponseCreatedEvent,
    ResponseCompletedEvent,
    ResponseIncompleteEvent,
)
from openai.lib.streaming.responses import ResponseStream, AsyncResponseStream
from openai.lib.streaming.responses._responses import ResponseStreamState


class _Answer(pydantic.BaseModel):
    value: str


def _response_payload(*, status: str, text: str = "partial answer", **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": "resp_test",
        "object": "response",
        "created_at": 0,
        "model": "gpt-4o-mini",
        "output": [
            {
                "id": "msg_test",
                "type": "message",
                "role": "assistant",
                "status": status if status != "failed" else "incomplete",
                "content": [
                    {
                        "type": "output_text",
                        "text": text,
                        "annotations": [],
                        "logprobs": [],
                    }
                ],
            }
        ],
        "parallel_tool_calls": True,
        "tool_choice": "auto",
        "tools": [],
        "status": status,
    }
    payload.update(extra)
    return payload


def _event(type_: type[Any], value: dict[str, Any]) -> RawResponseStreamEvent:
    return cast(RawResponseStreamEvent, construct_type_unchecked(type_=type_, value=value))


def _drive_state_to_terminal(
    event_type: str,
    *,
    status: str,
    text: str = "partial answer",
    text_format: type[Any] | Any = omit,
    **extra: Any,
) -> ResponseStreamState[Any]:
    state: ResponseStreamState[Any] = ResponseStreamState(input_tools=omit, text_format=text_format)
    state.handle_event(
        _event(
            ResponseCreatedEvent,
            {
                "type": "response.created",
                "sequence_number": 0,
                "response": _response_payload(status="in_progress", text=""),
            },
        )
    )

    terminal_type: type[Any]
    if event_type == "response.completed":
        terminal_type = ResponseCompletedEvent
    elif event_type == "response.incomplete":
        terminal_type = ResponseIncompleteEvent
    elif event_type == "response.failed":
        terminal_type = ResponseFailedEvent
    else:
        raise AssertionError(f"unexpected event type: {event_type}")

    state.handle_event(
        _event(
            terminal_type,
            {
                "type": event_type,
                "sequence_number": 1,
                "response": _response_payload(status=status, text=text, **extra),
            },
        )
    )
    return state


@pytest.mark.parametrize(
    ("event_type", "status", "extra"),
    [
        ("response.completed", "completed", {}),
        ("response.incomplete", "incomplete", {"incomplete_details": {"reason": "max_output_tokens"}}),
        ("response.failed", "failed", {"error": {"code": "server_error", "message": "boom"}}),
    ],
)
def test_stream_state_stores_final_response_for_terminal_events(
    event_type: str,
    status: str,
    extra: dict[str, Any],
) -> None:
    state = _drive_state_to_terminal(event_type, status=status, **extra)

    assert state._completed_response is not None
    assert state._completed_response.status == status
    assert state._completed_response.output_text == "partial answer"


@pytest.mark.parametrize(
    ("event_type", "status", "extra"),
    [
        ("response.incomplete", "incomplete", {"incomplete_details": {"reason": "max_output_tokens"}}),
        ("response.failed", "failed", {"error": {"code": "server_error", "message": "boom"}}),
    ],
)
def test_stream_state_preserves_truncated_output_on_non_completed_terminal_events(
    event_type: str,
    status: str,
    extra: dict[str, Any],
) -> None:
    truncated = '{"value":'
    state = _drive_state_to_terminal(
        event_type,
        status=status,
        text=truncated,
        text_format=_Answer,
        **extra,
    )

    assert state._completed_response is not None
    assert state._completed_response.status == status
    assert state._completed_response.output_text == truncated

    content = state._completed_response.output[0]
    assert content.type == "message"
    assert content.content[0].type == "output_text"
    assert content.content[0].parsed is None


def test_stream_state_parses_structured_output_on_completed_event() -> None:
    state = _drive_state_to_terminal(
        "response.completed",
        status="completed",
        text='{"value":"done"}',
        text_format=_Answer,
    )

    assert state._completed_response is not None
    content = state._completed_response.output[0]
    assert content.type == "message"
    assert content.content[0].type == "output_text"
    assert content.content[0].parsed == _Answer(value="done")


def test_stream_state_without_terminal_event_has_no_final_response() -> None:
    state: ResponseStreamState[None] = ResponseStreamState(input_tools=omit, text_format=omit)
    state.handle_event(
        _event(
            ResponseCreatedEvent,
            {
                "type": "response.created",
                "sequence_number": 0,
                "response": _response_payload(status="in_progress"),
            },
        )
    )

    assert state._completed_response is None


class _FakeRawStream:
    def __init__(self, events: list[RawResponseStreamEvent], response: httpx.Response) -> None:
        self._events = events
        self.response = response

    def __iter__(self) -> Iterator[RawResponseStreamEvent]:
        return iter(self._events)

    def close(self) -> None:
        self.response.close()


class _FakeAsyncRawStream:
    def __init__(self, events: list[RawResponseStreamEvent], response: httpx.Response) -> None:
        self._events = events
        self.response = response

    async def __aiter__(self) -> AsyncIterator[RawResponseStreamEvent]:
        for event in self._events:
            yield event

    async def aclose(self) -> None:
        self.response.close()


def _terminal_events(
    event_type: str,
    *,
    status: str,
    text: str = "partial answer",
    **extra: Any,
) -> list[RawResponseStreamEvent]:
    created = _event(
        ResponseCreatedEvent,
        {
            "type": "response.created",
            "sequence_number": 0,
            "response": _response_payload(status="in_progress", text=""),
        },
    )
    terminal_type: type[Any]
    if event_type == "response.completed":
        terminal_type = ResponseCompletedEvent
    elif event_type == "response.incomplete":
        terminal_type = ResponseIncompleteEvent
    else:
        terminal_type = ResponseFailedEvent

    terminal = _event(
        terminal_type,
        {
            "type": event_type,
            "sequence_number": 1,
            "response": _response_payload(status=status, text=text, **extra),
        },
    )
    return [created, terminal]


@pytest.mark.parametrize(
    ("event_type", "status", "extra"),
    [
        ("response.completed", "completed", {}),
        ("response.incomplete", "incomplete", {"incomplete_details": {"reason": "max_output_tokens"}}),
        ("response.failed", "failed", {"error": {"code": "server_error", "message": "boom"}}),
    ],
)
def test_sync_get_final_response_accepts_terminal_events(
    event_type: str,
    status: str,
    extra: dict[str, Any],
) -> None:
    response = httpx.Response(200, content=b"")
    raw_stream = _FakeRawStream(_terminal_events(event_type, status=status, **extra), response)
    stream = ResponseStream(
        raw_stream=raw_stream,  # type: ignore[arg-type]
        text_format=omit,
        input_tools=omit,
        starting_after=None,
    )

    final = stream.get_final_response()

    assert final.status == status
    assert final.output_text == "partial answer"


@pytest.mark.parametrize(
    ("event_type", "status", "extra"),
    [
        ("response.incomplete", "incomplete", {"incomplete_details": {"reason": "max_output_tokens"}}),
        ("response.failed", "failed", {"error": {"code": "server_error", "message": "boom"}}),
    ],
)
def test_sync_get_final_response_preserves_truncated_structured_output(
    event_type: str,
    status: str,
    extra: dict[str, Any],
) -> None:
    truncated = '{"value":'
    response = httpx.Response(200, content=b"")
    stream = ResponseStream(
        raw_stream=_FakeRawStream(  # type: ignore[arg-type]
            _terminal_events(event_type, status=status, text=truncated, **extra),
            response,
        ),
        text_format=_Answer,
        input_tools=omit,
        starting_after=None,
    )

    final = stream.get_final_response()

    assert final.status == status
    assert final.output_text == truncated
    content = final.output[0]
    assert content.type == "message"
    assert content.content[0].type == "output_text"
    assert content.content[0].parsed is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("event_type", "status", "extra"),
    [
        ("response.completed", "completed", {}),
        ("response.incomplete", "incomplete", {"incomplete_details": {"reason": "max_output_tokens"}}),
        ("response.failed", "failed", {"error": {"code": "server_error", "message": "boom"}}),
    ],
)
async def test_async_get_final_response_accepts_terminal_events(
    event_type: str,
    status: str,
    extra: dict[str, Any],
) -> None:
    response = httpx.Response(200, content=b"")
    raw_stream = _FakeAsyncRawStream(_terminal_events(event_type, status=status, **extra), response)
    stream = AsyncResponseStream(
        raw_stream=raw_stream,  # type: ignore[arg-type]
        text_format=omit,
        input_tools=omit,
        starting_after=None,
    )

    final = await stream.get_final_response()

    assert final.status == status
    assert final.output_text == "partial answer"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("event_type", "status", "extra"),
    [
        ("response.incomplete", "incomplete", {"incomplete_details": {"reason": "max_output_tokens"}}),
        ("response.failed", "failed", {"error": {"code": "server_error", "message": "boom"}}),
    ],
)
async def test_async_get_final_response_preserves_truncated_structured_output(
    event_type: str,
    status: str,
    extra: dict[str, Any],
) -> None:
    truncated = '{"value":'
    response = httpx.Response(200, content=b"")
    stream = AsyncResponseStream(
        raw_stream=_FakeAsyncRawStream(  # type: ignore[arg-type]
            _terminal_events(event_type, status=status, text=truncated, **extra),
            response,
        ),
        text_format=_Answer,
        input_tools=omit,
        starting_after=None,
    )

    final = await stream.get_final_response()

    assert final.status == status
    assert final.output_text == truncated
    content = final.output[0]
    assert content.type == "message"
    assert content.content[0].type == "output_text"
    assert content.content[0].parsed is None


def test_sync_get_final_response_requires_terminal_event() -> None:
    response = httpx.Response(200, content=b"")
    created = _event(
        ResponseCreatedEvent,
        {
            "type": "response.created",
            "sequence_number": 0,
            "response": _response_payload(status="in_progress"),
        },
    )
    stream = ResponseStream(
        raw_stream=_FakeRawStream([created], response),  # type: ignore[arg-type]
        text_format=omit,
        input_tools=omit,
        starting_after=None,
    )

    with pytest.raises(RuntimeError, match="terminal response event"):
        stream.get_final_response()


@pytest.mark.asyncio
async def test_async_get_final_response_requires_terminal_event() -> None:
    response = httpx.Response(200, content=b"")
    created = _event(
        ResponseCreatedEvent,
        {
            "type": "response.created",
            "sequence_number": 0,
            "response": _response_payload(status="in_progress"),
        },
    )
    stream = AsyncResponseStream(
        raw_stream=_FakeAsyncRawStream([created], response),  # type: ignore[arg-type]
        text_format=omit,
        input_tools=omit,
        starting_after=None,
    )

    with pytest.raises(RuntimeError, match="terminal response event"):
        await stream.get_final_response()
