from __future__ import annotations

import json
from typing_extensions import TypeVar

import httpx
import pytest
from respx import MockRouter
from inline_snapshot import snapshot

from openai import OpenAI, AsyncOpenAI
from openai._utils import assert_signatures_in_sync

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
            '{"id": "resp_689a0b2545288193953c892439b42e2800b2e36c65a1fd4b", "object": "response", "created_at": 1754925861, "status": "completed", "background": false, "error": null, "incomplete_details": null, "instructions": null, "max_output_tokens": null, "max_tool_calls": null, "model": "gpt-4o-mini-2024-07-18", "output": [{"id": "msg_689a0b2637b08193ac478e568f49e3f900b2e36c65a1fd4b", "type": "message", "status": "completed", "content": [{"type": "output_text", "annotations": [], "logprobs": [], "text": "I can\'t provide real-time updates, but you can easily check the current weather in San Francisco using a weather website or app. Typically, San Francisco has cool, foggy summers and mild winters, so it\'s good to be prepared for variable weather!"}], "role": "assistant"}], "parallel_tool_calls": true, "previous_response_id": null, "prompt_cache_key": null, "reasoning": {"effort": null, "summary": null}, "safety_identifier": null, "service_tier": "default", "store": true, "temperature": 1.0, "text": {"format": {"type": "text"}, "verbosity": "medium"}, "tool_choice": "auto", "tools": [], "top_logprobs": 0, "top_p": 1.0, "truncation": "disabled", "usage": {"input_tokens": 14, "input_tokens_details": {"cached_tokens": 0}, "output_tokens": 50, "output_tokens_details": {"reasoning_tokens": 0}, "total_tokens": 64}, "user": null, "metadata": {}}'
        ),
        path="/responses",
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert response.output_text == snapshot(
        "I can't provide real-time updates, but you can easily check the current weather in San Francisco using a weather website or app. Typically, San Francisco has cool, foggy summers and mild winters, so it's good to be prepared for variable weather!"
    )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_stream_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.responses.create,
        checking_client.responses.stream,
        exclude_params={"stream", "tools"},
    )


@pytest.mark.respx(base_url=base_url)
@pytest.mark.parametrize("client", [False], indirect=True)
def test_stream_function_call_arguments_done_includes_name(client: OpenAI, respx_mock: MockRouter) -> None:
    response = {
        "id": "resp_123",
        "object": "response",
        "created_at": 1720000000,
        "status": "in_progress",
        "error": None,
        "incomplete_details": None,
        "instructions": None,
        "model": "gpt-4o-mini-2024-07-18",
        "output": [],
        "parallel_tool_calls": True,
        "temperature": 1.0,
        "tool_choice": "auto",
        "tools": [],
        "top_p": 1.0,
        "metadata": {},
    }
    arguments = '{"part_number":"ABC-123"}'
    events = [
        {
            "type": "response.created",
            "sequence_number": 0,
            "response": response,
        },
        {
            "type": "response.output_item.added",
            "sequence_number": 1,
            "output_index": 0,
            "item": {
                "id": "fc_123",
                "type": "function_call",
                "status": "in_progress",
                "call_id": "call_123",
                "name": "search_parts",
                "arguments": "",
            },
        },
        {
            "type": "response.function_call_arguments.done",
            "sequence_number": 2,
            "item_id": "fc_123",
            "output_index": 0,
            "name": None,
            "arguments": arguments,
        },
    ]
    sse = "".join(f"event: {event['type']}\ndata: {json.dumps(event)}\n\n" for event in events)

    respx_mock.post("/responses").mock(
        return_value=httpx.Response(200, text=sse, headers={"Content-Type": "text/event-stream"})
    )

    with client.responses.stream(model="gpt-4o-mini", input="search for a part") as stream:
        streamed_events = list(stream)

    done_event = next(event for event in streamed_events if event.type == "response.function_call_arguments.done")
    assert done_event.name == "search_parts"
    assert done_event.arguments == arguments


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_parse_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.responses.create,
        checking_client.responses.parse,
        exclude_params={"tools"},
    )
