from __future__ import annotations

from typing_extensions import TypeVar

import pytest
from respx import MockRouter
from inline_snapshot import snapshot

from openai import OpenAI, AsyncOpenAI
from openai._utils import assert_signatures_in_sync
from openai._models import construct_type_unchecked
from openai.lib._parsing._responses import parse_response
from openai.types.responses import Response

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


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_parse_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.responses.create,
        checking_client.responses.parse,
        exclude_params={"tools"},
    )


def test_parse_response_with_none_output() -> None:
    response_data = {
        "id": "resp_test123",
        "created_at": 1754925861,
        "model": "gpt-4o-mini",
        "object": "response",
        "output": None,
        "parallel_tool_calls": True,
        "tool_choice": "auto",
        "tools": [],
        "status": "completed",
    }

    response = construct_type_unchecked(type_=Response, value=response_data)
    parsed = parse_response(response=response, text_format=None, input_tools=None)

    assert parsed.id == "resp_test123"
    assert parsed.output == []
    assert parsed.status == "completed"


def test_output_text_with_null_text() -> None:
    """Test that output_text property handles null text values gracefully."""
    response_data = {
        "id": "resp_null_text",
        "object": "response",
        "created_at": 0,
        "status": "completed",
        "model": "gpt-4o-mini",
        "output": [
            {
                "id": "msg_null_text",
                "type": "message",
                "status": "completed",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "annotations": [],
                        "logprobs": [],
                        "text": None,
                    },
                    {
                        "type": "output_text",
                        "annotations": [],
                        "logprobs": [],
                        "text": '{"message":"hello"}',
                    },
                ],
            }
        ],
        "parallel_tool_calls": True,
        "tool_choice": "auto",
        "tools": [],
    }

    response = construct_type_unchecked(type_=Response, value=response_data)
    # Should not raise TypeError and should skip null text values
    assert response.output_text == '{"message":"hello"}'


def test_parse_response_with_null_text() -> None:
    """Test that parse_response handles null text values in output_text items."""
    response_data = {
        "id": "resp_null_text_parse",
        "object": "response",
        "created_at": 0,
        "status": "completed",
        "model": "gpt-4o-mini",
        "output": [
            {
                "id": "msg_null_text_parse",
                "type": "message",
                "status": "completed",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "annotations": [],
                        "logprobs": [],
                        "text": None,
                    },
                    {
                        "type": "output_text",
                        "annotations": [],
                        "logprobs": [],
                        "text": "Hello world",
                    },
                ],
            }
        ],
        "parallel_tool_calls": True,
        "tool_choice": "auto",
        "tools": [],
    }

    response = construct_type_unchecked(type_=Response, value=response_data)
    parsed = parse_response(response=response, text_format=None, input_tools=None)

    assert parsed.id == "resp_null_text_parse"
    assert len(parsed.output) == 1
    message = parsed.output[0]
    assert message.type == "message"
    assert len(message.content) == 2
    # First content item should have null text and parsed=None
    assert message.content[0].text is None
    assert message.content[0].parsed is None
    # Second content item should have normal text
    assert message.content[1].text == "Hello world"
