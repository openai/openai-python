from __future__ import annotations

import pydantic
import pytest

from openai.types.beta.beta_response_function_call_arguments_done_event import (
    BetaResponseFunctionCallArgumentsDoneEvent,
)
from openai.types.responses.response_function_call_arguments_done_event import (
    ResponseFunctionCallArgumentsDoneEvent,
)
from openai.types.responses.response_stream_event import ResponseStreamEvent


PAYLOAD_WITHOUT_NAME = {
    "type": "response.function_call_arguments.done",
    "arguments": "{\"city\": \"Paris\"}",
    "item_id": "fc_test_item",
    "output_index": 2,
    "sequence_number": 10,
}


def test_function_call_arguments_done_accepts_missing_name() -> None:
    """Live Responses API may omit `name` on done events (issue #3472)."""
    event = ResponseFunctionCallArgumentsDoneEvent.model_validate(PAYLOAD_WITHOUT_NAME)
    assert event.type == "response.function_call_arguments.done"
    assert event.item_id == "fc_test_item"
    assert event.name is None
    assert event.arguments == '{"city": "Paris"}'


def test_function_call_arguments_done_keeps_name_when_present() -> None:
    event = ResponseFunctionCallArgumentsDoneEvent.model_validate(
        {**PAYLOAD_WITHOUT_NAME, "name": "get_weather"}
    )
    assert event.name == "get_weather"


def test_response_stream_event_union_accepts_done_without_name() -> None:
    # Strict union validation previously failed with missing: name.
    event = pydantic.TypeAdapter(ResponseStreamEvent).validate_python(PAYLOAD_WITHOUT_NAME)
    assert isinstance(event, ResponseFunctionCallArgumentsDoneEvent)
    assert event.name is None


def test_beta_function_call_arguments_done_accepts_missing_name() -> None:
    event = BetaResponseFunctionCallArgumentsDoneEvent.model_validate(PAYLOAD_WITHOUT_NAME)
    assert event.name is None
