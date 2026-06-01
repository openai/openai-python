from __future__ import annotations

import gc
from typing_extensions import TypeVar

import pytest
from respx import MockRouter
from pydantic_core import SchemaValidator
from inline_snapshot import snapshot

from openai import OpenAI, AsyncOpenAI
from openai._types import omit
from openai._utils import assert_signatures_in_sync
from openai._compat import parse_obj
from openai._models import construct_type_unchecked
from openai.types.responses import Response, ResponseCreatedEvent, ResponseCompletedEvent
from openai.lib._parsing._responses import parse_response
from openai.lib.streaming.responses._responses import ResponseStreamState

from ...conftest import base_url
from ..snapshots import make_snapshot_request

_T = TypeVar("_T")


def _minimal_response_data(output: object, *, status: str = "completed") -> dict[str, object]:
    return {
        "id": "resp_test",
        "object": "response",
        "created_at": 1,
        "status": status,
        "model": "gpt-4o-mini",
        "output": output,
        "parallel_tool_calls": True,
        "tool_choice": "auto",
        "tools": [],
    }


def _minimal_response(output: object, *, status: str = "completed") -> Response:
    return construct_type_unchecked(
        type_=Response,
        value=_minimal_response_data(output, status=status),
    )


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
            '{"id": "resp_689a0b2545288193953c892439b42e2800b2e36c65a1fd4b", "object": "response", "created_at": 1754925861, "status": "completed", "background": false, "error": null, "incomplete_details": null, "instructions": null, "max_output_tokens": null, "max_tool_calls": null, "model": "gpt-4o-mini-2024-07-18", "output": [{"id": "msg_689a0b2637b08193ac478e568f49e3f900b2e36c65a1fd4b", "type": "message", "status": "completed", "content": [{"type": "output_text", "annotations": [], "logprobs": [], "text": "I can\'t provide real-time updates, but you can easily check the current weather in San Francisco using a weather website or app. Typically, San Francisco has cool, foggy summers and mild winters, so it\'s good to be prepared for variable weather!"}], "role": "assistant"}], "parallel_tool_calls": true, "previous_response_id": null, "prompt_cache_key": null, "reasoning": {"effort": null, "summary": null}, "safety_identifier": null, "service_tier": "default", "store": true, "temperature": 1.0, "text": {"format": {"type": "text"}, "verbosity": "medium"}, "tool_choice": "auto", "tools": [], "top_logprobs": 0, "top_p": 1.0, "truncation": "disabled", "usage": {"input_tokens": 14, "input_tokens_details": {"cached_tokens": 0}, "output_tokens": 50, "output_tokens_details": {"reasoning_tokens": 0}, "total_tokens": 64}, "user": null, "metadata": {}}'
        ),
        path="/responses",
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert response.output_text == snapshot(
        "I can't provide real-time updates, but you can easily check the current weather in San Francisco using a weather website or app. Typically, San Francisco has cool, foggy summers and mild winters, so it's good to be prepared for variable weather!"
    )


def test_parse_response_handles_null_output() -> None:
    response = _minimal_response(None)

    parsed = parse_response(text_format=omit, input_tools=omit, response=response)

    assert parsed.output == []
    assert parsed.output_text == ""


def test_response_handles_null_output() -> None:
    response = parse_obj(Response, _minimal_response_data(None))

    assert response.output is None
    assert response.output_text == ""


def test_parse_response_does_not_leak_schema_validators() -> None:
    response = _minimal_response(
        [
            {
                "id": "msg_test",
                "type": "message",
                "status": "completed",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "annotations": [],
                        "text": "hello",
                    }
                ],
            }
        ]
    )

    for _ in range(100):
        parse_response(text_format=omit, input_tools=omit, response=response)

    for _ in range(100):
        parse_response(text_format=omit, input_tools=omit, response=response)

    gc.collect()
    validator_count = sum(1 for obj in gc.get_objects() if type(obj) is SchemaValidator)

    for _ in range(100):
        parse_response(text_format=omit, input_tools=omit, response=response)

    gc.collect()
    assert sum(1 for obj in gc.get_objects() if type(obj) is SchemaValidator) == validator_count


def test_response_stream_completed_uses_snapshot_when_event_output_is_null() -> None:
    state = ResponseStreamState(text_format=omit, input_tools=omit)
    created_response = _minimal_response(
        [
            {
                "id": "msg_test",
                "type": "message",
                "status": "completed",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "annotations": [],
                        "text": "hello",
                    }
                ],
            }
        ],
        status="in_progress",
    )
    completed_response = _minimal_response(None)

    state.handle_event(
        construct_type_unchecked(
            type_=ResponseCreatedEvent,
            value={"type": "response.created", "sequence_number": 0, "response": created_response},
        )
    )
    events = state.handle_event(
        construct_type_unchecked(
            type_=ResponseCompletedEvent,
            value={"type": "response.completed", "sequence_number": 1, "response": completed_response},
        )
    )

    completed_event = events[0]
    assert completed_event.type == "response.completed"
    assert completed_event.response.status == "completed"
    assert completed_event.response.output_text == "hello"


def test_response_stream_completed_preserves_function_call_and_compaction_items() -> None:
    state = ResponseStreamState(text_format=omit, input_tools=omit)
    created_response = _minimal_response([], status="in_progress")
    completed_response = _minimal_response(
        [
            {
                "id": "fc_test",
                "type": "function_call",
                "call_id": "call_test",
                "name": "lookup",
                "arguments": "{}",
                "status": "completed",
            },
            {
                "id": "cmp_test",
                "type": "compaction",
                "encrypted_content": "encrypted",
            },
        ]
    )

    state.handle_event(
        construct_type_unchecked(
            type_=ResponseCreatedEvent,
            value={"type": "response.created", "sequence_number": 0, "response": created_response},
        )
    )
    events = state.handle_event(
        construct_type_unchecked(
            type_=ResponseCompletedEvent,
            value={"type": "response.completed", "sequence_number": 1, "response": completed_response},
        )
    )

    completed_event = events[0]
    assert completed_event.type == "response.completed"
    assert [item.type for item in completed_event.response.output] == ["function_call", "compaction"]


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
