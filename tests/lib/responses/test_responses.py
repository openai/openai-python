from __future__ import annotations

import json
from typing_extensions import Literal, TypeVar

import httpx
import pytest
from respx import MockRouter
from pydantic import BaseModel
from inline_snapshot import snapshot

from openai import OpenAI, AsyncOpenAI
from openai._utils import assert_signatures_in_sync
from openai.types.responses import ParsedResponse

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


@pytest.mark.respx(base_url=base_url)
def test_retrieve_parsed_text_format(client: OpenAI, respx_mock: MockRouter) -> None:
    class Location(BaseModel):
        city: str
        temperature: float
        units: Literal["c", "f"]

    content = json.dumps(
        {
            "id": "resp_bg_123",
            "object": "response",
            "created_at": 1754925861,
            "status": "completed",
            "background": True,
            "error": None,
            "incomplete_details": None,
            "instructions": None,
            "max_output_tokens": None,
            "max_tool_calls": None,
            "model": "gpt-4o-2024-08-06",
            "output": [
                {
                    "id": "msg_123",
                    "type": "message",
                    "status": "completed",
                    "content": [
                        {
                            "type": "output_text",
                            "annotations": [],
                            "text": '{"city": "San Francisco", "temperature": 65, "units": "f"}',
                        }
                    ],
                    "role": "assistant",
                }
            ],
            "parallel_tool_calls": True,
            "previous_response_id": None,
            "prompt_cache_key": None,
            "reasoning": {"effort": None, "summary": None},
            "safety_identifier": None,
            "service_tier": "default",
            "store": True,
            "temperature": 1.0,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "Location",
                    "schema": Location.model_json_schema(),
                },
            },
            "tool_choice": "auto",
            "tools": [],
            "top_logprobs": 0,
            "top_p": 1.0,
            "truncation": "disabled",
            "usage": {
                "input_tokens": 14,
                "input_tokens_details": {"cached_tokens": 0},
                "output_tokens": 20,
                "output_tokens_details": {"reasoning_tokens": 0},
                "total_tokens": 34,
            },
            "user": None,
            "metadata": {},
        }
    )

    respx_mock.get("/responses/resp_bg_123").mock(
        return_value=httpx.Response(200, content=content, headers={"content-type": "application/json"})
    )

    response = client.responses.retrieve_parsed("resp_bg_123", text_format=Location)

    assert isinstance(response, ParsedResponse)
    assert response.output_parsed is not None
    assert isinstance(response.output_parsed, Location)
    assert response.output_parsed.city == "San Francisco"
    assert response.output_parsed.temperature == 65
    assert response.output_parsed.units == "f"


@pytest.mark.respx(base_url=base_url)
async def test_async_retrieve_parsed_text_format(async_client: AsyncOpenAI, respx_mock: MockRouter) -> None:
    class Location(BaseModel):
        city: str
        temperature: float
        units: Literal["c", "f"]

    content = json.dumps(
        {
            "id": "resp_bg_456",
            "object": "response",
            "created_at": 1754925861,
            "status": "completed",
            "background": True,
            "error": None,
            "incomplete_details": None,
            "instructions": None,
            "max_output_tokens": None,
            "max_tool_calls": None,
            "model": "gpt-4o-2024-08-06",
            "output": [
                {
                    "id": "msg_456",
                    "type": "message",
                    "status": "completed",
                    "content": [
                        {
                            "type": "output_text",
                            "annotations": [],
                            "text": '{"city": "New York", "temperature": 72, "units": "f"}',
                        }
                    ],
                    "role": "assistant",
                }
            ],
            "parallel_tool_calls": True,
            "previous_response_id": None,
            "prompt_cache_key": None,
            "reasoning": {"effort": None, "summary": None},
            "safety_identifier": None,
            "service_tier": "default",
            "store": True,
            "temperature": 1.0,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "Location",
                    "schema": Location.model_json_schema(),
                },
            },
            "tool_choice": "auto",
            "tools": [],
            "top_logprobs": 0,
            "top_p": 1.0,
            "truncation": "disabled",
            "usage": {
                "input_tokens": 14,
                "input_tokens_details": {"cached_tokens": 0},
                "output_tokens": 20,
                "output_tokens_details": {"reasoning_tokens": 0},
                "total_tokens": 34,
            },
            "user": None,
            "metadata": {},
        }
    )

    respx_mock.get("/responses/resp_bg_456").mock(
        return_value=httpx.Response(200, content=content, headers={"content-type": "application/json"})
    )

    response = await async_client.responses.retrieve_parsed("resp_bg_456", text_format=Location)

    assert isinstance(response, ParsedResponse)
    assert response.output_parsed is not None
    assert isinstance(response.output_parsed, Location)
    assert response.output_parsed.city == "New York"
    assert response.output_parsed.temperature == 72
    assert response.output_parsed.units == "f"


@pytest.mark.respx(base_url=base_url)
def test_retrieve_parsed_with_function_tool(client: OpenAI, respx_mock: MockRouter) -> None:
    class GetWeather(BaseModel):
        city: str

    content = json.dumps(
        {
            "id": "resp_bg_789",
            "object": "response",
            "created_at": 1754925861,
            "status": "completed",
            "background": True,
            "error": None,
            "incomplete_details": None,
            "instructions": None,
            "max_output_tokens": None,
            "max_tool_calls": None,
            "model": "gpt-4o-2024-08-06",
            "output": [
                {
                    "id": "fc_789",
                    "type": "function_call",
                    "status": "completed",
                    "call_id": "call_123",
                    "name": "get_weather",
                    "arguments": '{"city": "San Francisco"}',
                }
            ],
            "parallel_tool_calls": True,
            "previous_response_id": None,
            "prompt_cache_key": None,
            "reasoning": {"effort": None, "summary": None},
            "safety_identifier": None,
            "service_tier": "default",
            "store": True,
            "temperature": 1.0,
            "text": {"format": {"type": "text"}},
            "tool_choice": "auto",
            "tools": [
                {
                    "type": "function",
                    "name": "get_weather",
                    "parameters": GetWeather.model_json_schema(),
                    "strict": True,
                }
            ],
            "top_logprobs": 0,
            "top_p": 1.0,
            "truncation": "disabled",
            "usage": {
                "input_tokens": 14,
                "input_tokens_details": {"cached_tokens": 0},
                "output_tokens": 20,
                "output_tokens_details": {"reasoning_tokens": 0},
                "total_tokens": 34,
            },
            "user": None,
            "metadata": {},
        }
    )

    respx_mock.get("/responses/resp_bg_789").mock(
        return_value=httpx.Response(200, content=content, headers={"content-type": "application/json"})
    )

    response = client.responses.retrieve_parsed(
        "resp_bg_789",
        tools=[
            {
                "type": "function",
                "name": "get_weather",
                "parameters": GetWeather.model_json_schema(),
                "strict": True,
            }
        ],
    )

    assert isinstance(response, ParsedResponse)
    assert len(response.output) == 1
    output = response.output[0]
    assert output.type == "function_call"
    assert output.parsed_arguments == {"city": "San Francisco"}


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
