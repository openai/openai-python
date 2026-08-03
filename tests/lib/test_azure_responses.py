from __future__ import annotations

import json
from typing import Iterator, AsyncIterator

import httpx
import pytest
from respx import MockRouter

from openai.lib.azure import AzureOpenAI, AsyncAzureOpenAI

AZURE_ENDPOINT = "https://example-resource.azure.openai.com"
AZURE_API_VERSION = "2024-02-01"
AZURE_RESPONSES_URL = f"{AZURE_ENDPOINT}/openai/responses?api-version={AZURE_API_VERSION}"
AZURE_CHAT_COMPLETIONS_URL = (
    f"{AZURE_ENDPOINT}/openai/deployments/gpt-4/chat/completions?api-version={AZURE_API_VERSION}"
)
AZURE_DEPLOYMENT_MODEL = "gpt-5-nano"
AZURE_SERVED_MODEL = "gpt-5-nano-2025-08-07"


def make_sync_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_version=AZURE_API_VERSION,
        api_key="example API key",
        azure_endpoint=AZURE_ENDPOINT,
    )


def make_async_client() -> AsyncAzureOpenAI:
    return AsyncAzureOpenAI(
        api_version=AZURE_API_VERSION,
        api_key="example API key",
        azure_endpoint=AZURE_ENDPOINT,
    )


def azure_response_payload(*, model: str = AZURE_DEPLOYMENT_MODEL) -> dict[str, object]:
    return {
        "id": "resp_123",
        "object": "response",
        "created_at": 0,
        "model": model,
        "output": [],
        "parallel_tool_calls": True,
        "tool_choice": "auto",
        "tools": [],
    }


def response_created_stream_body() -> Iterator[bytes]:
    yield b"event: response.created\n"
    yield (
        b'data: {"type":"response.created","sequence_number":0,"response":'
        + json.dumps(azure_response_payload(), separators=(",", ":")).encode()
        + b"}\n\n"
    )
    yield b"data: [DONE]\n\n"


async def async_response_created_stream_body() -> AsyncIterator[bytes]:
    for chunk in response_created_stream_body():
        yield chunk


def mock_responses_create(
    respx_mock: MockRouter,
    *,
    served_model_header: str | None,
    stream: bool = False,
) -> None:
    headers = {"x-ms-served-model": served_model_header} if served_model_header is not None else {}
    if stream:
        headers["content-type"] = "text/event-stream"
        respx_mock.post(AZURE_RESPONSES_URL).mock(
            return_value=httpx.Response(
                200,
                headers=headers,
                content=response_created_stream_body(),
            )
        )
    else:
        respx_mock.post(AZURE_RESPONSES_URL).mock(
            return_value=httpx.Response(
                200,
                headers=headers,
                json=azure_response_payload(),
            )
        )


@pytest.mark.respx()
def test_azure_responses_uses_served_model_header(respx_mock: MockRouter) -> None:
    mock_responses_create(respx_mock, served_model_header=f" {AZURE_SERVED_MODEL} ")

    response = make_sync_client().responses.create(model=AZURE_DEPLOYMENT_MODEL, input="ping")

    assert response.model == AZURE_SERVED_MODEL


@pytest.mark.asyncio
@pytest.mark.respx()
async def test_async_azure_responses_uses_served_model_header(respx_mock: MockRouter) -> None:
    mock_responses_create(respx_mock, served_model_header=AZURE_SERVED_MODEL)

    response = await make_async_client().responses.create(model=AZURE_DEPLOYMENT_MODEL, input="ping")

    assert response.model == AZURE_SERVED_MODEL


@pytest.mark.respx()
def test_azure_responses_stream_uses_served_model_header(respx_mock: MockRouter) -> None:
    mock_responses_create(respx_mock, served_model_header=AZURE_SERVED_MODEL, stream=True)

    stream = make_sync_client().responses.create(model=AZURE_DEPLOYMENT_MODEL, input="ping", stream=True)
    event = next(stream)

    assert event.type == "response.created"
    assert event.response.model == AZURE_SERVED_MODEL


@pytest.mark.asyncio
@pytest.mark.respx()
async def test_async_azure_responses_stream_uses_served_model_header(respx_mock: MockRouter) -> None:
    respx_mock.post(AZURE_RESPONSES_URL).mock(
        return_value=httpx.Response(
            200,
            headers={
                "content-type": "text/event-stream",
                "x-ms-served-model": AZURE_SERVED_MODEL,
            },
            content=async_response_created_stream_body(),
        )
    )

    stream = await make_async_client().responses.create(model=AZURE_DEPLOYMENT_MODEL, input="ping", stream=True)
    event = await stream.__anext__()

    assert event.type == "response.created"
    assert event.response.model == AZURE_SERVED_MODEL


@pytest.mark.parametrize("served_model_header", [None, "   "])
@pytest.mark.respx()
def test_azure_responses_preserves_body_model_without_served_model_header(
    respx_mock: MockRouter,
    served_model_header: str | None,
) -> None:
    mock_responses_create(respx_mock, served_model_header=served_model_header)

    response = make_sync_client().responses.create(model=AZURE_DEPLOYMENT_MODEL, input="ping")

    assert response.model == AZURE_DEPLOYMENT_MODEL


@pytest.mark.respx()
def test_azure_served_model_header_does_not_apply_to_non_responses_resources(respx_mock: MockRouter) -> None:
    respx_mock.post(AZURE_CHAT_COMPLETIONS_URL).mock(
        return_value=httpx.Response(
            200,
            headers={"x-ms-served-model": AZURE_SERVED_MODEL},
            json={"model": "gpt-4"},
        )
    )

    response = make_sync_client().chat.completions.create(messages=[], model="gpt-4")

    assert response.model == "gpt-4"
