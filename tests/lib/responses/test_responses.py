from __future__ import annotations

from typing_extensions import TypeVar

import pytest
from respx import MockRouter
from inline_snapshot import snapshot

from openai import OpenAI, AsyncOpenAI
from openai._types import omit
from openai._utils import assert_signatures_in_sync
from openai._models import construct_type_unchecked
from openai.types.responses import Response
from openai.lib._parsing._responses import parse_response

from ...conftest import base_url
from ..snapshots import make_snapshot_request

_T = TypeVar("_T")

# all the snapshots in this file are auto-generated from the live API
#
# you can update them with
#
# `OPENAI_LIVE=1 pytest --inline-snapshot=fix -p no:xdist -o addopts=""`


@pytest.mark.respx(base_url=base_url)
def test_output_text(client: OpenAI, respx_mock: MockRouter) -> None:
    response = make_snapshot_request(
        lambda c: c.responses.create(
            model="gpt-4o-mini",
            input="What's the weather like in SF?",
        ),
        content_snapshot=snapshot(
            '{"id": "resp_689a0b2545288193953c892439b42e2800b2e36c65a1fd4b", "object": "response", "created_at": 1754925861, "status": "completed", "background": false, "error": null, "incomplete_details": null, "instructions": null, "max_output_tokens": null, "max_tool_calls": null, "model": "gpt-4o-mini-2024-07-18", "output": [{"id": "msg_689a0b2637b08193ac478e568f49e3f900b2e36c65a1fd4b", "type": "message", "status": "completed", "content": [{"type": "output_text", "annotations": [], "logprobs": [], "text": "I can\'t provide real-time updates, but you can easily check the current weather in San Francisco using a weather website or app. Typically, San Francisco has cool, foggy summers and mild winters, so it\'s good to be prepared for variable weather!"}], "role": "assistant"}], "parallel_tool_calls": true, "previous_response_id": null, "prompt_cache_key": null, "reasoning": {"effort": null, "summary": null}, "safety_identifier": null, "service_tier": "default", "store": true, "temperature": 1.0, "text": {"format": {"type": "text"}, "verbosity": "medium"}, "tool_choice": "auto", "tools": [], "top_logprobs": 0, "top_p": 1.0, "truncation": "disabled", "usage": {"input_tokens": 14, "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0}, "output_tokens": 50, "output_tokens_details": {"reasoning_tokens": 0}, "total_tokens": 64}, "user": null, "metadata": {}}'
        ),
        path="/responses",
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert response.output_text == snapshot(
        "I can't provide real-time updates, but you can easily check the current weather in San Francisco using a weather website or app. Typically, San Francisco has cool, foggy summers and mild winters, so it's good to be prepared for variable weather!"
    )


@pytest.mark.parametrize(
    "item",
    [
        {
            "id": "prog_123",
            "call_id": "call_123",
            "code": "return 42",
            "fingerprint": "fp_123",
            "type": "program",
        },
        {
            "id": "prog_out_123",
            "call_id": "call_123",
            "result": "42",
            "status": "completed",
            "type": "program_output",
        },
    ],
)
def test_parse_response_preserves_program_items(item: dict[str, object]) -> None:
    response = construct_type_unchecked(type_=Response, value={"output": [item]})

    parsed = parse_response(text_format=omit, input_tools=omit, response=response)

    assert parsed.output[0].to_dict() == item


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_stream_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.responses.create,
        checking_client.responses.stream,
        exclude_params={"stream", "tools"},
    )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_parse_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.responses.create,
        checking_client.responses.parse,
        exclude_params={"tools"},
    )


def test_parse_response_handles_null_output() -> None:
    from openai._types import omit
    from openai._models import construct_type_unchecked
    from openai.types.responses import Response
    from openai.lib._parsing._responses import parse_response

    response = construct_type_unchecked(
        type_=Response,
        value={
            "id": "resp_test",
            "object": "response",
            "created_at": 0,
            "model": "gpt-4o-mini",
            "output": None,
            "parallel_tool_calls": True,
            "temperature": 1,
            "tool_choice": "auto",
            "tools": [],
            "top_p": 1,
            "metadata": {},
            "reasoning": {},
            "status": "completed",
            "text": {"format": {"type": "text"}},
        },
    )

    parsed = parse_response(text_format=omit, input_tools=None, response=response)

    assert parsed.output == []


def test_stream_completed_event_with_null_output_preserves_accumulated_output() -> None:
    from openai._types import omit
    from openai._models import construct_type_unchecked
    from openai.lib.streaming.responses._responses import ResponseStreamState
    from openai.types.responses.response_created_event import ResponseCreatedEvent
    from openai.types.responses.response_completed_event import ResponseCompletedEvent
    from openai.types.responses.response_text_delta_event import ResponseTextDeltaEvent
    from openai.types.responses.response_output_item_added_event import ResponseOutputItemAddedEvent
    from openai.types.responses.response_content_part_added_event import ResponseContentPartAddedEvent

    def event(type_: object, value: object):
        return construct_type_unchecked(type_=type_, value=value)

    response = {
        "id": "resp_test",
        "object": "response",
        "created_at": 0,
        "model": "gpt-4o-mini",
        "output": [],
        "parallel_tool_calls": True,
        "temperature": 1,
        "tool_choice": "auto",
        "tools": [],
        "top_p": 1,
        "metadata": {},
        "reasoning": {},
        "status": "completed",
        "text": {"format": {"type": "text"}},
    }
    state = ResponseStreamState(text_format=omit, input_tools=omit)

    for type_, value in [
        (ResponseCreatedEvent, {"type": "response.created", "sequence_number": 0, "response": response}),
        (
            ResponseOutputItemAddedEvent,
            {
                "type": "response.output_item.added",
                "sequence_number": 1,
                "output_index": 0,
                "item": {
                    "id": "msg_test",
                    "type": "message",
                    "status": "in_progress",
                    "role": "assistant",
                    "content": [],
                },
            },
        ),
        (
            ResponseContentPartAddedEvent,
            {
                "type": "response.content_part.added",
                "sequence_number": 2,
                "item_id": "msg_test",
                "output_index": 0,
                "content_index": 0,
                "part": {"type": "output_text", "text": "", "annotations": []},
            },
        ),
        (
            ResponseTextDeltaEvent,
            {
                "type": "response.output_text.delta",
                "sequence_number": 3,
                "item_id": "msg_test",
                "output_index": 0,
                "content_index": 0,
                "delta": "Hello",
                "logprobs": [],
            },
        ),
    ]:
        state.handle_event(event(type_, value))

    events = state.handle_event(
        event(
            ResponseCompletedEvent,
            {
                "type": "response.completed",
                "sequence_number": 4,
                "response": {
                    **response,
                    "output": None,
                    "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
                },
            },
        )
    )

    assert state._completed_response is not None
    assert state._completed_response.output_text == "Hello"
    assert state._completed_response.usage is not None
    assert state._completed_response.usage.total_tokens == 2
    assert events[0].type == "response.completed"
    assert events[0].response.output_text == "Hello"
