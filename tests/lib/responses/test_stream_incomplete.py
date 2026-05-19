from __future__ import annotations

from pydantic import BaseModel

from openai._types import omit
from openai._models import construct_type_unchecked
from openai.types.responses import Response
from openai.lib.streaming.responses._responses import ResponseStreamState
from openai.types.responses.response_created_event import ResponseCreatedEvent
from openai.types.responses.response_text_done_event import ResponseTextDoneEvent as RawResponseTextDoneEvent
from openai.types.responses.response_incomplete_event import ResponseIncompleteEvent
from openai.types.responses.response_text_delta_event import ResponseTextDeltaEvent as RawResponseTextDeltaEvent
from openai.types.responses.response_output_item_added_event import ResponseOutputItemAddedEvent
from openai.types.responses.response_content_part_added_event import ResponseContentPartAddedEvent


def _make_response(**overrides: object) -> Response:
    defaults = {
        "id": "resp_test",
        "created_at": 1700000000.0,
        "model": "gpt-4o-mini",
        "object": "response",
        "output": [],
        "parallel_tool_calls": True,
        "tool_choice": "auto",
        "tools": [],
        "status": "in_progress",
    }
    defaults.update(overrides)
    return construct_type_unchecked(type_=Response, value=defaults)


class Payload(BaseModel):
    value: str


def test_incomplete_response_does_not_raise_on_parse() -> None:
    """When a response is incomplete (e.g. truncated by max_output_tokens),
    the output text done event should set parsed=None instead of raising
    a JSON validation error, allowing the response.incomplete event to
    still be delivered to the caller.
    """
    state = ResponseStreamState(text_format=Payload, input_tools=omit)

    response = _make_response()

    # 1. response.created
    state.handle_event(
        construct_type_unchecked(
            type_=ResponseCreatedEvent,
            value={
                "type": "response.created",
                "response": response.to_dict(),
                "sequence_number": 0,
            },
        )
    )

    # 2. response.output_item.added (message)
    state.handle_event(
        construct_type_unchecked(
            type_=ResponseOutputItemAddedEvent,
            value={
                "type": "response.output_item.added",
                "output_index": 0,
                "item": {
                    "id": "msg_test",
                    "type": "message",
                    "status": "in_progress",
                    "content": [],
                    "role": "assistant",
                },
                "sequence_number": 1,
            },
        )
    )

    # 3. response.content_part.added
    state.handle_event(
        construct_type_unchecked(
            type_=ResponseContentPartAddedEvent,
            value={
                "type": "response.content_part.added",
                "output_index": 0,
                "content_index": 0,
                "item_id": "msg_test",
                "part": {
                    "type": "output_text",
                    "text": "",
                    "annotations": [],
                    "logprobs": [],
                },
                "sequence_number": 2,
            },
        )
    )

    # 4. response.output_text.delta with truncated text
    state.handle_event(
        construct_type_unchecked(
            type_=RawResponseTextDeltaEvent,
            value={
                "type": "response.output_text.delta",
                "output_index": 0,
                "content_index": 0,
                "item_id": "msg_test",
                "delta": '{"val',
                "logprobs": [],
                "sequence_number": 3,
            },
        )
    )

    # 5. response.output_text.done with incomplete JSON — should NOT raise
    events = state.handle_event(
        construct_type_unchecked(
            type_=RawResponseTextDoneEvent,
            value={
                "type": "response.output_text.done",
                "output_index": 0,
                "content_index": 0,
                "item_id": "msg_test",
                "text": '{"val',
                "logprobs": [],
                "sequence_number": 4,
            },
        )
    )

    assert len(events) == 1
    text_done_event = events[0]
    assert text_done_event.type == "response.output_text.done"
    assert text_done_event.text == '{"val'  # type: ignore[union-attr]
    assert text_done_event.parsed is None  # type: ignore[union-attr]

    # 6. response.incomplete should still be delivered
    events = state.handle_event(
        construct_type_unchecked(
            type_=ResponseIncompleteEvent,
            value={
                "type": "response.incomplete",
                "response": {
                    **response.to_dict(),
                    "status": "incomplete",
                    "incomplete_details": {"reason": "max_output_tokens"},
                },
                "sequence_number": 5,
            },
        )
    )

    assert len(events) == 1
    assert events[0].type == "response.incomplete"


def test_complete_response_still_parses() -> None:
    """When the response completes successfully, structured output should
    still be parsed normally on the output_text.done event.
    """
    state = ResponseStreamState(text_format=Payload, input_tools=omit)

    response = _make_response()

    state.handle_event(
        construct_type_unchecked(
            type_=ResponseCreatedEvent,
            value={
                "type": "response.created",
                "response": response.to_dict(),
                "sequence_number": 0,
            },
        )
    )

    state.handle_event(
        construct_type_unchecked(
            type_=ResponseOutputItemAddedEvent,
            value={
                "type": "response.output_item.added",
                "output_index": 0,
                "item": {
                    "id": "msg_test",
                    "type": "message",
                    "status": "in_progress",
                    "content": [],
                    "role": "assistant",
                },
                "sequence_number": 1,
            },
        )
    )

    state.handle_event(
        construct_type_unchecked(
            type_=ResponseContentPartAddedEvent,
            value={
                "type": "response.content_part.added",
                "output_index": 0,
                "content_index": 0,
                "item_id": "msg_test",
                "part": {
                    "type": "output_text",
                    "text": "",
                    "annotations": [],
                    "logprobs": [],
                },
                "sequence_number": 2,
            },
        )
    )

    valid_json = '{"value": "hello"}'

    state.handle_event(
        construct_type_unchecked(
            type_=RawResponseTextDeltaEvent,
            value={
                "type": "response.output_text.delta",
                "output_index": 0,
                "content_index": 0,
                "item_id": "msg_test",
                "delta": valid_json,
                "logprobs": [],
                "sequence_number": 3,
            },
        )
    )

    events = state.handle_event(
        construct_type_unchecked(
            type_=RawResponseTextDoneEvent,
            value={
                "type": "response.output_text.done",
                "output_index": 0,
                "content_index": 0,
                "item_id": "msg_test",
                "text": valid_json,
                "logprobs": [],
                "sequence_number": 4,
            },
        )
    )

    assert len(events) == 1
    text_done_event = events[0]
    assert text_done_event.type == "response.output_text.done"
    assert text_done_event.parsed is not None  # type: ignore[union-attr]
    assert text_done_event.parsed.value == "hello"  # type: ignore[union-attr]
