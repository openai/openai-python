from __future__ import annotations

import json

import httpx2
import pytest

from openai import (
    OpenAI,
    AsyncOpenAI,
    AzureOpenAI,
    OpenAIError,
    BedrockOpenAI,
    DataResidency,
    AsyncAzureOpenAI,
    AsyncBedrockOpenAI,
)
from openai.providers import bedrock
from openai._data_residency import _DATA_RESIDENCY_BASE_URLS

REGIONS: list[tuple[DataResidency, str]] = [
    (region, url.rstrip("/") + "/") for region, url in _DATA_RESIDENCY_BASE_URLS.items()
]


@pytest.fixture(autouse=True)
def clear_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("OPENAI_API_KEY", "OPENAI_ADMIN_KEY", "OPENAI_BASE_URL", "OPENAI_CUSTOM_HEADERS"):
        monkeypatch.delenv(name, raising=False)


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
def test_provider_conflicts_and_explicit_switch(client_type: type[OpenAI] | type[AsyncOpenAI]) -> None:
    provider = bedrock(region="us-east-1", api_key="test-bedrock-key")
    with pytest.raises(OpenAIError, match="`data_residency` and `provider`"):
        client_type(provider=provider, data_residency="eu")
    original = client_type(provider=provider)
    with pytest.raises(OpenAIError, match="`data_residency` and `provider`"):
        original.with_options(data_residency="eu")
    with pytest.raises(OpenAIError, match="`data_residency` and `provider`"):
        client_type(api_key="test-key").with_options(provider=provider, data_residency="eu")
    assert original.with_options(data_residency=None).base_url == original.base_url
    assert original.with_options(provider=None, api_key="test-key", data_residency="eu").base_url == httpx2.URL(
        "https://eu.api.openai.com/v1/"
    )
    regional = client_type(api_key="test-key", data_residency="eu")
    assert regional.with_options(provider=provider).base_url == original.base_url


@pytest.mark.parametrize("client_type", [AzureOpenAI, AsyncAzureOpenAI])
def test_legacy_azure_rejects_residency(client_type: type[AzureOpenAI] | type[AsyncAzureOpenAI]) -> None:
    client = client_type(api_key="test-azure-key", api_version="test", azure_endpoint="https://azure.example")
    with pytest.raises(OpenAIError, match="only supported by OpenAI clients"):
        client.with_options(data_residency="eu")
    assert client.with_options(data_residency=None).base_url == client.base_url


@pytest.mark.parametrize("client_type", [BedrockOpenAI, AsyncBedrockOpenAI])
def test_legacy_bedrock_rejects_residency(client_type: type[BedrockOpenAI] | type[AsyncBedrockOpenAI]) -> None:
    client = client_type(api_key="test-bedrock-key", aws_region="us-east-1")
    with pytest.raises(OpenAIError, match="only supported by OpenAI clients"):
        client.with_options(data_residency="eu")
    assert client.with_options(data_residency=None).base_url == client.base_url


def check_request(request: httpx2.Request) -> httpx2.Response:
    assert request.url == httpx2.URL("https://eu.api.openai.com/v1/responses")
    assert json.loads(request.content) == {"input": "Hello", "model": "gpt-5.6-sol"}
    assert not any("residency" in name for name in request.headers)
    assert request.headers["Authorization"] == "Bearer test-key"
    return httpx2.Response(200, request=request, json={"id": "resp_test", "output": []})


def test_sync_request_only_changes_destination() -> None:
    with httpx2.Client(transport=httpx2.MockTransport(check_request), trust_env=False) as transport:
        client = OpenAI(api_key="test-key", http_client=transport)
        response = client.with_options(data_residency="eu").responses.create(model="gpt-5.6-sol", input="Hello")
        assert response.id == "resp_test"
        assert client.base_url == httpx2.URL("https://api.openai.com/v1/")


async def test_async_request_only_changes_destination() -> None:
    async with httpx2.AsyncClient(transport=httpx2.MockTransport(check_request), trust_env=False) as transport:
        client = AsyncOpenAI(api_key="test-key", http_client=transport)
        response = await client.with_options(data_residency="eu").responses.create(model="gpt-5.6-sol", input="Hello")
        assert response.id == "resp_test"
        assert client.base_url == httpx2.URL("https://api.openai.com/v1/")


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
@pytest.mark.parametrize(("region", "url"), REGIONS)
def test_residency_replaces_inherited_websocket_routing(
    client_type: type[OpenAI] | type[AsyncOpenAI], region: DataResidency, url: str
) -> None:
    original = client_type(api_key="test-key", websocket_base_url="wss://third-party.example/v1")
    regional = original.with_options(data_residency=region)
    assert original.copy().websocket_base_url == original.websocket_base_url
    assert original.copy(data_residency=None).websocket_base_url == original.websocket_base_url
    assert original.realtime.connect()._prepare_url() == httpx2.URL("wss://third-party.example/v1/realtime")
    assert original.responses.connect()._prepare_url() == httpx2.URL("wss://third-party.example/v1/responses")

    for client in (regional, regional.copy(), client_type(api_key="test-key", data_residency=region)):
        assert client.websocket_base_url is None
        ws_url = url.replace("https://", "wss://")
        assert client.realtime.connect()._prepare_url() == httpx2.URL(ws_url + "realtime")
        assert client.responses.connect()._prepare_url() == httpx2.URL(ws_url + "responses")
        assert client.beta.realtime.connect(model="gpt-4o")._prepare_url() == httpx2.URL(ws_url + "realtime")
        assert client.beta.responses.connect()._prepare_url() == httpx2.URL(ws_url + "responses")
