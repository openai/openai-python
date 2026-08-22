"""Streaming regression tests for a `response.completed` event with `output: null`.

Some backends deliver the output items through `output_item.added` /
`output_item.done` and then send `output: null` on the final `response.completed`
event. The stream state falls back to the accumulated snapshot in that case, so
the snapshot has to hold the authoritative done-event payloads rather than the
earlier in-progress ones.
"""

from __future__ import annotations

from typing import Any, cast

from openai import omit
from openai._models import construct_type_unchecked
from openai.types.responses import ResponseStreamEvent
from openai.lib.streaming.responses._responses import ResponseStreamState


def _response(output: Any, status: str = "completed") -> dict[str, Any]:
    return {
        "id": "resp_1",
        "object": "response",
        "created_at": 0,
        "status": status,
        "error": None,
        "incomplete_details": None,
        "instructions": None,
        "max_output_tokens": None,
        "model": "gpt-4o-mini",
        "output": output,
        "parallel_tool_calls": True,
        "previous_response_id": None,
        "temperature": 1.0,
        "tool_choice": "auto",
        "tools": [],
        "top_p": 1.0,
        "usage": None,
        "user": None,
        "metadata": {},
    }


def _message(status: str, text: str) -> dict[str, Any]:
    return {
        "id": "msg_1",
        "type": "message",
        "role": "assistant",
        "status": status,
        "content": [{"type": "output_text", "text": text, "annotations": []}],
    }


def _event(value: dict[str, Any]) -> ResponseStreamEvent:
    return cast(
        ResponseStreamEvent,
        construct_type_unchecked(type_=cast(Any, ResponseStreamEvent), value=value),
    )


def _drive(events: list[dict[str, Any]]) -> ResponseStreamState[Any]:
    state: ResponseStreamState[Any] = ResponseStreamState(input_tools=omit, text_format=omit)
    for value in events:
        state.handle_event(_event(value))
    return state


def test_null_completed_uses_done_event_payload() -> None:
    """The fallback must serialise the done payload, not the in_progress one."""
    state = _drive(
        [
            {"type": "response.created", "response": _response([], status="in_progress"), "sequence_number": 0},
            {
                "type": "response.output_item.added",
                "output_index": 0,
                "item": _message("in_progress", ""),
                "sequence_number": 1,
            },
            {
                "type": "response.output_item.done",
                "output_index": 0,
                "item": _message("completed", "hello world"),
                "sequence_number": 2,
            },
            {"type": "response.completed", "response": _response(None), "sequence_number": 3},
        ]
    )

    final = state._completed_response
    assert final is not None
    assert len(final.output) == 1

    item = final.output[0]
    assert item.type == "message"
    # the whole point: `added` said in_progress, `done` said completed
    assert item.status == "completed"
    assert item.content[0].type == "output_text"
    assert item.content[0].text == "hello world"
    assert final.output_text == "hello world"


def test_null_completed_uses_content_part_done_payload() -> None:
    """content_part.done carries annotations that the deltas never send."""
    annotation = {
        "type": "url_citation",
        "url": "https://example.com",
        "title": "Example",
        "start_index": 0,
        "end_index": 5,
    }
    state = _drive(
        [
            {"type": "response.created", "response": _response([], status="in_progress"), "sequence_number": 0},
            {
                "type": "response.output_item.added",
                "output_index": 0,
                "item": {
                    "id": "msg_1",
                    "type": "message",
                    "role": "assistant",
                    "status": "in_progress",
                    "content": [],
                },
                "sequence_number": 1,
            },
            {
                "type": "response.content_part.added",
                "output_index": 0,
                "content_index": 0,
                "item_id": "msg_1",
                "part": {"type": "output_text", "text": "", "annotations": []},
                "sequence_number": 2,
            },
            {
                "type": "response.output_text.delta",
                "output_index": 0,
                "content_index": 0,
                "item_id": "msg_1",
                "delta": "hello",
                "sequence_number": 3,
            },
            {
                "type": "response.content_part.done",
                "output_index": 0,
                "content_index": 0,
                "item_id": "msg_1",
                "part": {"type": "output_text", "text": "hello", "annotations": [annotation]},
                "sequence_number": 4,
            },
            {"type": "response.completed", "response": _response(None), "sequence_number": 5},
        ]
    )

    final = state._completed_response
    assert final is not None
    item = final.output[0]
    assert item.type == "message"
    content = item.content[0]
    assert content.type == "output_text"
    assert content.text == "hello"
    # the annotation only ever arrives on the done event
    assert len(content.annotations) == 1


def test_non_null_completed_is_unchanged() -> None:
    """When the completed event carries output, it is used as-is."""
    state = _drive(
        [
            {"type": "response.created", "response": _response([], status="in_progress"), "sequence_number": 0},
            {
                "type": "response.output_item.added",
                "output_index": 0,
                "item": _message("in_progress", ""),
                "sequence_number": 1,
            },
            {
                "type": "response.output_item.done",
                "output_index": 0,
                "item": _message("completed", "from done"),
                "sequence_number": 2,
            },
            {
                "type": "response.completed",
                "response": _response([_message("completed", "from completed")]),
                "sequence_number": 3,
            },
        ]
    )

    final = state._completed_response
    assert final is not None
    assert final.output_text == "from completed"
