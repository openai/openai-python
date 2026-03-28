from __future__ import annotations

from typing_extensions import TypeVar

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


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_parse_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.responses.create,
        checking_client.responses.parse,
        exclude_params={"tools"},
    )


@pytest.mark.respx(base_url=base_url)
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_parse_content_filter_error(
    sync: bool, client: OpenAI, async_client: AsyncOpenAI, respx_mock: MockRouter
) -> None:
    """Test that content moderation responses raise ContentFilterFinishReasonError."""
    from pydantic import BaseModel
    from openai._exceptions import ContentFilterFinishReasonError

    class TestSchema(BaseModel):
        name: str
        value: int

    # Mock response with content filter and plain text refusal
    response_data = {
        "id": "resp_test123",
        "object": "response",
        "created_at": 1234567890,
        "status": "completed",
        "background": False,
        "error": None,
        "incomplete_details": {"reason": "content_filter"},
        "instructions": None,
        "max_output_tokens": None,
        "max_tool_calls": None,
        "model": "gpt-4.1",
        "output": [
            {
                "id": "msg_test123",
                "type": "message",
                "status": "completed",
                "content": [
                    {
                        "type": "output_text",
                        "annotations": [],
                        "logprobs": [],
                        "text": "I'm sorry, but I cannot assist you with that request.",
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
            "format": {"type": "json_schema", "strict": True, "name": "TestSchema", "schema": {}},
            "verbosity": "medium",
        },
        "tool_choice": "auto",
        "tools": [],
        "top_logprobs": 0,
        "top_p": 1.0,
        "truncation": "disabled",
        "usage": {
            "input_tokens": 10,
            "input_tokens_details": {"cached_tokens": 0},
            "output_tokens": 20,
            "output_tokens_details": {"reasoning_tokens": 0},
            "total_tokens": 30,
        },
        "user": None,
        "metadata": {},
    }

    import json

    respx_mock.post("/responses").mock(return_value=MockRouter.Response(200, json=response_data))

    with pytest.raises(ContentFilterFinishReasonError) as exc_info:
        if sync:
            client.responses.parse(
                model="gpt-4.1",
                input="problematic content",
                text_format=TestSchema,
            )
        else:
            await async_client.responses.parse(
                model="gpt-4.1",
                input="problematic content",
                text_format=TestSchema,
            )

    assert "content filter" in str(exc_info.value).lower()


@pytest.mark.respx(base_url=base_url)
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_parse_validation_error(
    sync: bool, client: OpenAI, async_client: AsyncOpenAI, respx_mock: MockRouter
) -> None:
    """Test that invalid JSON responses raise APIResponseValidationError."""
    from pydantic import BaseModel
    from openai._exceptions import APIResponseValidationError

    class TestSchema(BaseModel):
        name: str
        value: int

    # Mock response with invalid JSON (but no content filter)
    response_data = {
        "id": "resp_test456",
        "object": "response",
        "created_at": 1234567890,
        "status": "completed",
        "background": False,
        "error": None,
        "incomplete_details": None,  # No content filter
        "instructions": None,
        "max_output_tokens": None,
        "max_tool_calls": None,
        "model": "gpt-4.1",
        "output": [
            {
                "id": "msg_test456",
                "type": "message",
                "status": "completed",
                "content": [
                    {
                        "type": "output_text",
                        "annotations": [],
                        "logprobs": [],
                        "text": "This is plain text, not JSON",
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
            "format": {"type": "json_schema", "strict": True, "name": "TestSchema", "schema": {}},
            "verbosity": "medium",
        },
        "tool_choice": "auto",
        "tools": [],
        "top_logprobs": 0,
        "top_p": 1.0,
        "truncation": "disabled",
        "usage": {
            "input_tokens": 10,
            "input_tokens_details": {"cached_tokens": 0},
            "output_tokens": 20,
            "output_tokens_details": {"reasoning_tokens": 0},
            "total_tokens": 30,
        },
        "user": None,
        "metadata": {},
    }

    import json

    respx_mock.post("/responses").mock(return_value=MockRouter.Response(200, json=response_data))

    with pytest.raises(APIResponseValidationError) as exc_info:
        if sync:
            client.responses.parse(
                model="gpt-4.1",
                input="test input",
                text_format=TestSchema,
            )
        else:
            await async_client.responses.parse(
                model="gpt-4.1",
                input="test input",
                text_format=TestSchema,
            )

    error_msg = str(exc_info.value)
    assert "TestSchema" in error_msg
    assert "This is plain text, not JSON" in error_msg
