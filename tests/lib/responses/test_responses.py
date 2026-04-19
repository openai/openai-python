from __future__ import annotations

import json
from typing import cast
from typing_extensions import TypeVar

import httpx
import pytest
from respx import MockRouter
from inline_snapshot import snapshot

from openai import OpenAI, AsyncOpenAI
from openai._utils import assert_signatures_in_sync
from openai._compat import parse_obj
from openai.types.responses import Response, ResponseReasoningItem

from ...conftest import base_url
from ..snapshots import make_snapshot_request

_T = TypeVar("_T")

# all the snapshots in this file are auto-generated from the live API
#
# you can update them with
#
# `OPENAI_LIVE=1 pytest --inline-snapshot=fix -p no:xdist -o addopts=""`


EXPECTED_REPLAYED_OUTPUT_INPUT = [
    {
        "id": "rs_123",
        "summary": [],
        "type": "reasoning",
    },
    {
        "arguments": "{}",
        "call_id": "call_123",
        "id": "fc_123",
        "name": "weather",
        "type": "function_call",
    },
    {
        "content": [
            {
                "annotations": [],
                "text": "The weather is sunny.",
                "type": "output_text",
            }
        ],
        "id": "msg_123",
        "phase": "final_answer",
        "role": "assistant",
        "status": "completed",
        "type": "message",
    },
]


def make_replayed_response() -> Response:
    return parse_obj(
        Response,
        {
            "id": "resp_123",
            "object": "response",
            "created_at": 0,
            "model": "gpt-4o-mini",
            "output": [
                {
                    "id": "rs_123",
                    "type": "reasoning",
                    "summary": [],
                    "encrypted_content": None,
                    "status": None,
                },
                {
                    "arguments": "{}",
                    "call_id": "call_123",
                    "name": "weather",
                    "type": "function_call",
                    "id": "fc_123",
                    "status": None,
                },
                {
                    "id": "msg_123",
                    "type": "message",
                    "status": "completed",
                    "role": "assistant",
                    "phase": "final_answer",
                    "content": [
                        {
                            "type": "output_text",
                            "annotations": [],
                            "logprobs": None,
                            "text": "The weather is sunny.",
                        }
                    ],
                },
            ],
            "parallel_tool_calls": True,
            "tool_choice": "auto",
            "tools": [],
        },
    )


def make_replayed_response_output() -> list[object]:
    return make_replayed_response().output


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


@pytest.mark.respx(base_url=base_url)
def test_response_output_items_can_be_replayed_without_null_only_fields(
    client: OpenAI,
    respx_mock: MockRouter,
) -> None:
    route = respx_mock.post("/responses").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "resp_123",
                "object": "response",
                "created_at": 0,
                "model": "gpt-4o-mini",
                "output": [],
                "parallel_tool_calls": True,
                "tool_choice": "auto",
                "tools": [],
            },
        )
    )

    response = client.responses.create(
        model="gpt-4o-mini",
        input=make_replayed_response_output(),
    )

    assert isinstance(response, Response)

    request_body = json.loads(route.calls[0].request.content.decode("utf-8"))
    assert request_body["input"] == EXPECTED_REPLAYED_OUTPUT_INPUT


@pytest.mark.respx(base_url=base_url)
def test_output_as_input_can_be_replayed_without_losing_phase(
    client: OpenAI,
    respx_mock: MockRouter,
) -> None:
    route = respx_mock.post("/responses").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "resp_456",
                "object": "response",
                "created_at": 0,
                "model": "gpt-4o-mini",
                "output": [],
                "parallel_tool_calls": True,
                "tool_choice": "auto",
                "tools": [],
            },
        )
    )

    replayed_response = make_replayed_response()

    response = client.responses.create(
        model="gpt-4o-mini",
        input=replayed_response.output_as_input,
    )

    assert isinstance(response, Response)

    request_body = json.loads(route.calls[0].request.content.decode("utf-8"))
    assert request_body["input"] == EXPECTED_REPLAYED_OUTPUT_INPUT


@pytest.mark.respx(base_url=base_url)
async def test_async_replayed_response_output_items_can_be_counted_without_null_only_fields(
    async_client: AsyncOpenAI,
    respx_mock: MockRouter,
) -> None:
    route = respx_mock.post("/responses/input_tokens").mock(
        return_value=httpx.Response(
            200,
            json={
                "input_tokens": 3,
                "object": "response.input_tokens",
            },
        )
    )

    response = await async_client.responses.input_tokens.count(
        model="gpt-4o-mini",
        input=make_replayed_response_output(),
    )

    assert response.input_tokens == 3

    request_body = json.loads(route.calls[0].request.content.decode("utf-8"))
    assert request_body["input"] == EXPECTED_REPLAYED_OUTPUT_INPUT


def test_output_as_input_omits_null_only_response_fields() -> None:
    response = Response.construct(
        id="resp_123",
        created_at=1754925861,
        model="o4-mini",
        object="response",
        output=[
            {
                "id": "rs_123",
                "summary": [{"text": "Reasoning summary", "type": "summary_text"}],
                "type": "reasoning",
            },
            {
                "id": "msg_123",
                "type": "message",
                "status": "completed",
                "content": [
                    {
                        "type": "output_text",
                        "annotations": [],
                        "text": "Paris.",
                    }
                ],
                "role": "assistant",
            },
        ],
        parallel_tool_calls=True,
        tool_choice="auto",
        tools=[],
    )

    reasoning_item = cast(ResponseReasoningItem, response.output[0])
    assert reasoning_item.model_dump() == {
        "id": "rs_123",
        "summary": [{"text": "Reasoning summary", "type": "summary_text"}],
        "type": "reasoning",
        "content": None,
        "encrypted_content": None,
        "status": None,
    }

    assert response.output_as_input == [
        {
            "id": "rs_123",
            "summary": [{"text": "Reasoning summary", "type": "summary_text"}],
            "type": "reasoning",
        },
        {
            "id": "msg_123",
            "type": "message",
            "status": "completed",
            "content": [
                {
                    "type": "output_text",
                    "annotations": [],
                    "text": "Paris.",
                }
            ],
            "role": "assistant",
        },
    ]


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
