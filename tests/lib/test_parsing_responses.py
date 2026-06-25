"""Tests for parse_response handling of null/None output fields."""

from __future__ import annotations

from openai._models import construct_type_unchecked
from openai._types import Omit
from openai.lib._parsing._responses import parse_response
from openai.lib.streaming.responses._responses import ResponseStreamState
from openai.types.responses import Response, ParsedResponse
from openai.types.responses.response_created_event import ResponseCreatedEvent
from openai.types.responses.response_completed_event import ResponseCompletedEvent
from openai.types.responses.response_output_item_added_event import ResponseOutputItemAddedEvent
from openai.types.responses.response_content_part_added_event import ResponseContentPartAddedEvent
from openai.types.responses.response_text_delta_event import ResponseTextDeltaEvent


def _make_response(output=None, **kwargs):
    """Helper to construct a Response with a given output field."""
    base = {
        "id": "resp_test123",
        "created_at": 1234567890.0,
        "model": "gpt-4o",
        "object": "response",
        "status": "completed",
        "output": output,
        "parallel_tool_calls": True,
        "tool_choice": "auto",
        "tools": [],
        "temperature": 1.0,
        "top_p": 1.0,
    }
    base.update(kwargs)
    return construct_type_unchecked(type_=Response, value=base)


def test_parse_response_with_none_output():
    """Test that parse_response handles null output without crashing."""
    response = _make_response(output=None)
    assert response.output is None

    result = parse_response(
        text_format=None,
        input_tools=None,
        response=response,
    )

    assert isinstance(result, ParsedResponse)
    assert result.output == []


def test_parse_response_with_empty_list_output():
    """Test that parse_response handles empty list output correctly."""
    response = _make_response(output=[])
    assert response.output == []

    result = parse_response(
        text_format=None,
        input_tools=None,
        response=response,
    )

    assert isinstance(result, ParsedResponse)
    assert result.output == []


def test_parse_response_with_message_output():
    """Test that parse_response still works correctly with actual output items."""
    output_data = [
        {
            "id": "msg_test123",
            "type": "message",
            "status": "completed",
            "role": "assistant",
            "content": [
                {
                    "type": "output_text",
                    "text": "Hello, world!",
                    "annotations": [],
                }
            ],
        }
    ]
    response = _make_response(output=output_data)

    result = parse_response(
        text_format=Omit(),
        input_tools=None,
        response=response,
    )

    assert isinstance(result, ParsedResponse)
    assert len(result.output) == 1
    assert result.output[0].type == "message"


def test_streaming_accumulated_items_preserved_on_null_output():
    """When response.completed arrives with null output, items accumulated
    from prior streaming events should be preserved in get_final_response()."""
    state = ResponseStreamState(text_format=Omit(), input_tools=Omit())

    response_created = _make_response(output=[], status="in_progress")
    created_event = construct_type_unchecked(
        type_=ResponseCreatedEvent,
        value={
            "type": "response.created",
            "response": response_created.to_dict(),
            "sequence_number": 0,
        },
    )
    state.handle_event(created_event)

    item_added_event = construct_type_unchecked(
        type_=ResponseOutputItemAddedEvent,
        value={
            "type": "response.output_item.added",
            "output_index": 0,
            "item": {
                "id": "msg_abc",
                "type": "message",
                "status": "in_progress",
                "role": "assistant",
                "content": [],
            },
            "sequence_number": 1,
        },
    )
    state.handle_event(item_added_event)

    part_added_event = construct_type_unchecked(
        type_=ResponseContentPartAddedEvent,
        value={
            "type": "response.content_part.added",
            "output_index": 0,
            "content_index": 0,
            "item_id": "msg_abc",
            "part": {"type": "output_text", "text": "", "annotations": []},
            "sequence_number": 2,
        },
    )
    state.handle_event(part_added_event)

    delta_event_1 = construct_type_unchecked(
        type_=ResponseTextDeltaEvent,
        value={
            "type": "response.output_text.delta",
            "output_index": 0,
            "content_index": 0,
            "item_id": "msg_abc",
            "delta": "Hello, ",
            "logprobs": [],
            "sequence_number": 3,
        },
    )
    state.handle_event(delta_event_1)

    delta_event_2 = construct_type_unchecked(
        type_=ResponseTextDeltaEvent,
        value={
            "type": "response.output_text.delta",
            "output_index": 0,
            "content_index": 0,
            "item_id": "msg_abc",
            "delta": "world!",
            "logprobs": [],
            "sequence_number": 4,
        },
    )
    state.handle_event(delta_event_2)

    response_completed = _make_response(output=None, status="completed")
    completed_event = construct_type_unchecked(
        type_=ResponseCompletedEvent,
        value={
            "type": "response.completed",
            "response": response_completed.to_dict(),
            "sequence_number": 5,
        },
    )
    state.handle_event(completed_event)

    assert state._completed_response is not None
    assert len(state._completed_response.output) == 1
    assert state._completed_response.output[0].type == "message"
    msg = state._completed_response.output[0]
    assert msg.content[0].text == "Hello, world!"