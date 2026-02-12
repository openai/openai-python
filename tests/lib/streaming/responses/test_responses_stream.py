from __future__ import annotations

from openai._types import omit
from openai.lib.streaming.responses._responses import ResponseStreamState
from openai.types.responses import Response
from openai.types.responses.response_created_event import ResponseCreatedEvent
from openai.types.responses.response_text_delta_event import ResponseTextDeltaEvent


def _minimal_response_created_event() -> ResponseCreatedEvent:
    response = Response.model_construct(
        id="resp-test",
        created_at=0.0,
        model="gpt-4o",
        object="response",
        output=[],
        parallel_tool_calls=False,
        tool_choice="auto",
        tools=[],
    )
    return ResponseCreatedEvent(
        response=response,
        sequence_number=0,
        type="response.created",
    )


def _delta_event_before_output_item_added() -> ResponseTextDeltaEvent:
    return ResponseTextDeltaEvent(
        content_index=0,
        delta="x",
        item_id="item-1",
        logprobs=[],
        output_index=0,
        sequence_number=1,
        type="response.output_text.delta",
    )


def test_responses_stream_accumulate_handles_out_of_range_output_index() -> None:
    state = ResponseStreamState(input_tools=omit, text_format=omit)

    state.handle_event(_minimal_response_created_event())

    events = state.handle_event(_delta_event_before_output_item_added())

    assert isinstance(events, list)
