from __future__ import annotations

import json

import httpx
import pytest
from respx import MockRouter

from openai import OpenAI, AsyncOpenAI
from openai._utils import assert_signatures_in_sync
from openai.types.shared_params.response_format_json_schema import ResponseFormatJSONSchema


def test_assistant_create_sends_json_schema_response_format(client: OpenAI, respx_mock: MockRouter) -> None:
    response_format: ResponseFormatJSONSchema = {
        "type": "json_schema",
        "json_schema": {
            "name": "project_spending",
            "schema": {
                "type": "object",
                "properties": {
                    "authority_name": {"type": "string"},
                    "project_count": {"type": "integer"},
                },
                "required": ["authority_name", "project_count"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
    route = respx_mock.post("/assistants").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "asst_123",
                "created_at": 1,
                "model": "gpt-4o",
                "object": "assistant",
                "tools": [],
                "response_format": response_format,
            },
        )
    )

    with pytest.warns(DeprecationWarning):
        assistant = client.beta.assistants.create(  # pyright: ignore[reportDeprecated]
            model="gpt-4o",
            response_format=response_format,
        )

    assert assistant.response_format is not None
    assert json.loads(route.calls.last.request.content) == {
        "model": "gpt-4o",
        "response_format": response_format,
    }


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_create_and_run_poll_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.beta.threads.create_and_run,  # pyright: ignore[reportDeprecated]
        checking_client.beta.threads.create_and_run_poll,
        exclude_params={"stream"},
    )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_create_and_run_stream_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.beta.threads.create_and_run,  # pyright: ignore[reportDeprecated]
        checking_client.beta.threads.create_and_run_stream,
        exclude_params={"stream"},
    )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_run_stream_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.beta.threads.runs.create,  # pyright: ignore[reportDeprecated]
        checking_client.beta.threads.runs.stream,  # pyright: ignore[reportDeprecated]
        exclude_params={"stream"},
    )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_create_and_poll_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.beta.threads.runs.create,  # pyright: ignore[reportDeprecated]
        checking_client.beta.threads.runs.create_and_poll,  # pyright: ignore[reportDeprecated]
        exclude_params={"stream"},
    )
