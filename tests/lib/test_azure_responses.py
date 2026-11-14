from __future__ import annotations

import json
from typing import Iterator, AsyncIterator

import httpx2
import pytest

from tests.respx2 import MockRouter
from openai.lib.azure import AzureOpenAI, AsyncAzureOpenAI

AZURE_ENDPOINT = "https://example-resource.azure.openai.com"
AZURE_API_VERSION = "2024-02-01"
AZURE_RESPONSES_URL = f"{AZURE_ENDPOINT}/openai/responses?api-version={AZURE_API_VERSION}"
AZURE_CHAT_COMPLETIONS_URL = (
    f"{AZURE_ENDPOINT}/openai/deployments/gpt-4/chat/completions?api-version={AZURE_API_VERSION}"
)
AZURE_DEPLOYMENT_MODEL = "gpt-5-nano"
AZURE_SERVED_MODEL = "gpt-5-nano-2025-08-07"


def make_sync_client(*, azure_deployment: str | None = None) -> AzureOpenAI:
    return AzureOpenAI(
        api_version=AZURE_API_VERSION,
        api_key="example API key",
        azure_endpoint=AZURE_ENDPOINT,
        azure_deployment=azure_deployment,
    )


def make_async_client(*, azure_deployment: str | None = None) -> AsyncAzureOpenAI:
    return AsyncAzureOpenAI(
        api_version=AZURE_API_VERSION,
        api_key="example API key",
        azure_endpoint=AZURE_ENDPOINT,
        azure_deployment=azure_deployment,
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
    respx2_mock: MockRouter,
    *,
    served_model_header: str | None,
    stream: bool = False,
) -> None:
    headers = {"x-ms-served-model": served_model_header} if served_model_header is not None else {}
    if stream:
        headers["content-type"] = "text/event-stream"
        respx2_mock.post(AZURE_RESPONSES_URL).mock(
            return_value=httpx2.Response(
                200,
                headers=headers,
                content=response_created_stream_body(),
            )
        )
    else:
        respx2_mock.post(AZURE_RESPONSES_URL).mock(
            return_value=httpx2.Response(
                200,
                headers=headers,
                json=azure_response_payload(),
            )
        )


@pytest.mark.respx2()
def test_azure_responses_uses_served_model_header(respx2_mock: MockRouter) -> None:
    mock_responses_create(respx2_mock, served_model_header=f" {AZURE_SERVED_MODEL} ")

    response = make_sync_client().responses.create(model=AZURE_DEPLOYMENT_MODEL, input="ping")

    assert response.model == AZURE_SERVED_MODEL


@pytest.mark.asyncio
@pytest.mark.respx2()
async def test_async_azure_responses_uses_served_model_header(respx2_mock: MockRouter) -> None:
    mock_responses_create(respx2_mock, served_model_header=AZURE_SERVED_MODEL)

    response = await make_async_client().responses.create(model=AZURE_DEPLOYMENT_MODEL, input="ping")

    assert response.model == AZURE_SERVED_MODEL


@pytest.mark.respx2()
def test_azure_responses_stream_uses_served_model_header(respx2_mock: MockRouter) -> None:
    mock_responses_create(respx2_mock, served_model_header=AZURE_SERVED_MODEL, stream=True)

    stream = make_sync_client().responses.create(model=AZURE_DEPLOYMENT_MODEL, input="ping", stream=True)
    event = next(stream)

    assert event.type == "response.created"
    assert event.response.model == AZURE_SERVED_MODEL


@pytest.mark.asyncio
@pytest.mark.respx2()
async def test_async_azure_responses_stream_uses_served_model_header(respx2_mock: MockRouter) -> None:
    respx2_mock.post(AZURE_RESPONSES_URL).mock(
        return_value=httpx2.Response(
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
@pytest.mark.respx2()
def test_azure_responses_preserves_body_model_without_served_model_header(
    respx2_mock: MockRouter,
    served_model_header: str | None,
) -> None:
    mock_responses_create(respx2_mock, served_model_header=served_model_header)

    response = make_sync_client().responses.create(model=AZURE_DEPLOYMENT_MODEL, input="ping")

    assert response.model == AZURE_DEPLOYMENT_MODEL


@pytest.mark.respx2()
def test_azure_served_model_header_does_not_apply_to_non_responses_resources(respx2_mock: MockRouter) -> None:
    respx2_mock.post(AZURE_CHAT_COMPLETIONS_URL).mock(
        return_value=httpx2.Response(
            200,
            headers={"x-ms-served-model": AZURE_SERVED_MODEL},
            json={"model": "gpt-4"},
        )
    )

    response = make_sync_client().chat.completions.create(messages=[], model="gpt-4")

    assert response.model == "gpt-4"


def mock_chat_completions(respx2_mock: MockRouter, *, deployment_path: str, stream: bool) -> None:
    payload = {
        "id": "chatcmpl_example",
        "object": "chat.completion.chunk" if stream else "chat.completion",
        "created": 0,
        "model": "gpt-4-body",
        "choices": [],
    }
    headers = {"x-ms-served-model": AZURE_SERVED_MODEL}
    if stream:
        headers["content-type"] = "text/event-stream"
        response = httpx2.Response(
            200, headers=headers, content=b"data: " + json.dumps(payload).encode() + b"\n\ndata: [DONE]\n\n"
        )
    else:
        response = httpx2.Response(200, headers=headers, json=payload)
    respx2_mock.post(
        f"{AZURE_ENDPOINT}/openai/deployments/{deployment_path}/chat/completions?api-version={AZURE_API_VERSION}"
    ).mock(return_value=response)


@pytest.mark.parametrize(
    "model,azure_deployment,deployment_path",
    [
        ("responses", None, "responses"),
        ("responses", "responses", "responses"),
        ("prefix/responses", None, "prefix%2Fresponses"),
    ],
)
@pytest.mark.parametrize("stream", [False, True])
@pytest.mark.respx2()
def test_chat_model_is_preserved_when_deployment_contains_responses(
    respx2_mock: MockRouter, model: str, azure_deployment: str | None, deployment_path: str, stream: bool
) -> None:
    mock_chat_completions(respx2_mock, deployment_path=deployment_path, stream=stream)

    with make_sync_client(azure_deployment=azure_deployment) as client:
        if stream:
            with client.chat.completions.create(messages=[], model=model, stream=True) as chunks:
                assert next(chunks).model == "gpt-4-body"
        else:
            response = client.chat.completions.create(messages=[], model=model)
            assert response.model == "gpt-4-body"


@pytest.mark.parametrize(
    "model,azure_deployment,deployment_path",
    [
        ("responses", None, "responses"),
        ("responses", "responses", "responses"),
        ("prefix/responses", None, "prefix%2Fresponses"),
    ],
)
@pytest.mark.parametrize("stream", [False, True])
@pytest.mark.asyncio
@pytest.mark.respx2()
async def test_async_chat_model_is_preserved_when_deployment_contains_responses(
    respx2_mock: MockRouter, model: str, azure_deployment: str | None, deployment_path: str, stream: bool
) -> None:
    mock_chat_completions(respx2_mock, deployment_path=deployment_path, stream=stream)

    async with make_async_client(azure_deployment=azure_deployment) as client:
        if stream:
            async with await client.chat.completions.create(messages=[], model=model, stream=True) as chunks:
                assert (await chunks.__anext__()).model == "gpt-4-body"
        else:
            response = await client.chat.completions.create(messages=[], model=model)
            assert response.model == "gpt-4-body"


@pytest.mark.parametrize("base_path", ["/openai", "/openai/deployments/responses", "/gateway/deployments/blue/openai"])
@pytest.mark.respx2()
def test_azure_responses_retrieve_uses_served_model_header(respx2_mock: MockRouter, base_path: str) -> None:
    respx2_mock.get(f"{AZURE_ENDPOINT}{base_path}/responses/resp_123?api-version={AZURE_API_VERSION}").mock(
        return_value=httpx2.Response(
            200, headers={"x-ms-served-model": AZURE_SERVED_MODEL}, json=azure_response_payload()
        )
    )

    with AzureOpenAI(
        api_version=AZURE_API_VERSION, api_key="example API key", base_url=f"{AZURE_ENDPOINT}{base_path}"
    ) as client:
        assert client.responses.retrieve("resp_123").model == AZURE_SERVED_MODEL


@pytest.mark.parametrize("base_path", ["/openai", "/openai/deployments/responses", "/gateway/deployments/blue/openai"])
@pytest.mark.asyncio
@pytest.mark.respx2()
async def test_async_azure_responses_retrieve_uses_served_model_header(respx2_mock: MockRouter, base_path: str) -> None:
    respx2_mock.get(f"{AZURE_ENDPOINT}{base_path}/responses/resp_123?api-version={AZURE_API_VERSION}").mock(
        return_value=httpx2.Response(
            200, headers={"x-ms-served-model": AZURE_SERVED_MODEL}, json=azure_response_payload()
        )
    )

    async with AsyncAzureOpenAI(
        api_version=AZURE_API_VERSION, api_key="example API key", base_url=f"{AZURE_ENDPOINT}{base_path}"
    ) as client:
        response = await client.responses.retrieve("resp_123")
        assert response.model == AZURE_SERVED_MODEL
