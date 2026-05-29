from __future__ import annotations

from openai._types import omit as _omit
from openai._models import construct_type_unchecked
from openai.types.responses import Response
from openai.lib._parsing._responses import parse_response
from openai.lib.streaming.responses._responses import ResponseStreamState
from openai.types.responses.response_stream_event import (
    ResponseCreatedEvent,
    ResponseCompletedEvent,
    ResponseOutputItemAddedEvent,
)


def _make_response(**overrides: object) -> Response:
    base = {
        "id": "resp_1",
        "object": "response",
        "created_at": 1700000000.0,
        "model": "gpt-5.2",
        "output": [],
        "status": "completed",
        "parallel_tool_calls": True,
        "tool_choice": "auto",
        "tools": [],
        "text": {"format": {"type": "text"}},
        "truncation": "disabled",
    }
    base.update(overrides)
    return construct_type_unchecked(type_=Response, value=base)


class TestParseResponseNullOutput:
    def test_null_output_does_not_crash(self) -> None:
        response = _make_response(output=None)
        # Force output to None (bypassing Pydantic validation)
        object.__setattr__(response, "output", None)

        parsed = parse_response(
            text_format=_omit,
            input_tools=None,
            response=response,
        )
        assert parsed.output == []

    def test_empty_output_returns_empty(self) -> None:
        response = _make_response(output=[])
        parsed = parse_response(
            text_format=_omit,
            input_tools=None,
            response=response,
        )
        assert parsed.output == []


class TestStreamAccumulatorSnapshotFallback:
    def test_snapshot_fallback_when_completed_output_is_null(self) -> None:
        state = ResponseStreamState(text_format=_omit, input_tools=[])

        created_response = _make_response(output=[])
        created_event = construct_type_unchecked(
            type_=ResponseCreatedEvent,
            value={
                "type": "response.created",
                "response": created_response.to_dict(),
                "sequence_number": 0,
            },
        )
        state.handle_event(created_event)

        message_item = {
            "id": "msg_1",
            "type": "message",
            "status": "completed",
            "role": "assistant",
            "content": [
                {
                    "type": "output_text",
                    "text": "Hello world",
                    "annotations": [],
                }
            ],
        }
        added_event = construct_type_unchecked(
            type_=ResponseOutputItemAddedEvent,
            value={
                "type": "response.output_item.added",
                "output_index": 0,
                "item": message_item,
                "sequence_number": 1,
            },
        )
        state.handle_event(added_event)

        completed_response_dict = created_response.to_dict()
        completed_response_dict["output"] = None
        completed_response_dict["status"] = "completed"

        completed_event = construct_type_unchecked(
            type_=ResponseCompletedEvent,
            value={
                "type": "response.completed",
                "response": completed_response_dict,
                "sequence_number": 2,
            },
        )
        object.__setattr__(completed_event.response, "output", None)

        state.handle_event(completed_event)

        assert state._completed_response is not None
        assert len(state._completed_response.output) == 1
        assert state._completed_response.output[0].type == "message"
