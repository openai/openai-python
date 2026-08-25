from __future__ import annotations

from openai._types import omit
from openai._models import construct_type_unchecked
from openai.types.responses import ResponseStreamEvent as RawResponseStreamEvent
from openai.lib.streaming.responses._responses import ResponseStreamState


def _event(value: dict[str, object]) -> RawResponseStreamEvent:
    return construct_type_unchecked(type_=RawResponseStreamEvent, value=value)


def test_function_call_done_name_falls_back_to_snapshot() -> None:
    state = ResponseStreamState(text_format=omit, input_tools=omit)

    state.handle_event(
        _event(
            {
                "type": "response.created",
                "sequence_number": 0,
                "response": {
                    "id": "resp_123",
                    "object": "response",
                    "created_at": 0,
                    "status": "in_progress",
                    "output": [],
                },
            }
        )
    )
    state.handle_event(
        _event(
            {
                "type": "response.output_item.added",
                "sequence_number": 1,
                "output_index": 0,
                "item": {
                    "id": "fc_123",
                    "type": "function_call",
                    "call_id": "call_123",
                    "name": "search_parts",
                    "arguments": "{}",
                    "status": "in_progress",
                },
            }
        )
    )

    events = state.handle_event(
        _event(
            {
                "type": "response.function_call_arguments.done",
                "sequence_number": 2,
                "item_id": "fc_123",
                "output_index": 0,
                "arguments": "{}",
                "name": None,
            }
        )
    )

    assert len(events) == 1
    event = events[0]
    assert event.type == "response.function_call_arguments.done"
    assert event.name == "search_parts"


def test_function_call_done_preserves_server_name() -> None:
    state = ResponseStreamState(text_format=omit, input_tools=omit)

    state.handle_event(
        _event(
            {
                "type": "response.created",
                "sequence_number": 0,
                "response": {
                    "id": "resp_123",
                    "object": "response",
                    "created_at": 0,
                    "status": "in_progress",
                    "output": [],
                },
            }
        )
    )
    state.handle_event(
        _event(
            {
                "type": "response.output_item.added",
                "sequence_number": 1,
                "output_index": 0,
                "item": {
                    "id": "fc_123",
                    "type": "function_call",
                    "call_id": "call_123",
                    "name": "search_parts",
                    "arguments": "{}",
                    "status": "in_progress",
                },
            }
        )
    )

    events = state.handle_event(
        _event(
            {
                "type": "response.function_call_arguments.done",
                "sequence_number": 2,
                "item_id": "fc_123",
                "output_index": 0,
                "arguments": "{}",
                "name": "server_name",
            }
        )
    )

    assert events[0].name == "server_name"
