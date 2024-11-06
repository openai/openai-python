import logging
from typing import Union, cast
from typing_extensions import Literal, Protocol

import httpx
import pytest
from respx import MockRouter

from openai._utils import SensitiveHeadersFilter, is_dict
from openai._models import FinalRequestOptions
from openai.lib.azure import AzureOpenAI, AsyncAzureOpenAI

Client = Union[AzureOpenAI, AsyncAzureOpenAI]


sync_client = AzureOpenAI(
    api_version="2023-07-01",
    api_key="example API key",
    azure_endpoint="https://example-resource.azure.openai.com",
)

async_client = AsyncAzureOpenAI(
    api_version="2023-07-01",
    api_key="example API key",
    azure_endpoint="https://example-resource.azure.openai.com",
)


class MockRequestCall(Protocol):
    request: httpx.Request


@pytest.mark.parametrize("client", [sync_client, async_client])
def test_implicit_deployment_path(client: Client) -> None:
    req = client._build_request(
        FinalRequestOptions.construct(
            method="post",
            url="/chat/completions",
            json_data={"model": "my-deployment-model"},
        )
    )
    assert (
        req.url
        == "https://example-resource.azure.openai.com/openai/deployments/my-deployment-model/chat/completions?api-version=2023-07-01"
    )


@pytest.mark.parametrize(
    "client,method",
    [
        (sync_client, "copy"),
        (sync_client, "with_options"),
        (async_client, "copy"),
        (async_client, "with_options"),
    ],
)
def test_client_copying(client: Client, method: Literal["copy", "with_options"]) -> None:
    if method == "copy":
        copied = client.copy()
    else:
        copied = client.with_options()

    assert copied._custom_query == {"api-version": "2023-07-01"}


@pytest.mark.parametrize(
    "client",
    [sync_client, async_client],
)
def test_client_copying_override_options(client: Client) -> None:
    copied = client.copy(
        api_version="2022-05-01",
    )
    assert copied._custom_query == {"api-version": "2022-05-01"}


@pytest.mark.respx()
def test_client_token_provider_refresh_sync(respx_mock: MockRouter) -> None:
    respx_mock.post(
        "https://example-resource.azure.openai.com/openai/deployments/gpt-4/chat/completions?api-version=2024-02-01"
    ).mock(
        side_effect=[
            httpx.Response(500, json={"error": "server error"}),
            httpx.Response(200, json={"foo": "bar"}),
        ]
    )

    counter = 0

    def token_provider() -> str:
        nonlocal counter

        counter += 1

        if counter == 1:
            return "first"

        return "second"

    client = AzureOpenAI(
        api_version="2024-02-01",
        azure_ad_token_provider=token_provider,
        azure_endpoint="https://example-resource.azure.openai.com",
    )
    client.chat.completions.create(messages=[], model="gpt-4")

    calls = cast("list[MockRequestCall]", respx_mock.calls)

    assert len(calls) == 2

    assert calls[0].request.headers.get("Authorization") == "Bearer first"
    assert calls[1].request.headers.get("Authorization") == "Bearer second"


@pytest.mark.asyncio
@pytest.mark.respx()
async def test_client_token_provider_refresh_async(respx_mock: MockRouter) -> None:
    respx_mock.post(
        "https://example-resource.azure.openai.com/openai/deployments/gpt-4/chat/completions?api-version=2024-02-01"
    ).mock(
        side_effect=[
            httpx.Response(500, json={"error": "server error"}),
            httpx.Response(200, json={"foo": "bar"}),
        ]
    )

    counter = 0

    def token_provider() -> str:
        nonlocal counter

        counter += 1

        if counter == 1:
            return "first"

        return "second"

    client = AsyncAzureOpenAI(
        api_version="2024-02-01",
        azure_ad_token_provider=token_provider,
        azure_endpoint="https://example-resource.azure.openai.com",
    )

    await client.chat.completions.create(messages=[], model="gpt-4")

    calls = cast("list[MockRequestCall]", respx_mock.calls)

    assert len(calls) == 2

    assert calls[0].request.headers.get("Authorization") == "Bearer first"
    assert calls[1].request.headers.get("Authorization") == "Bearer second"


class TestAzureLogging:

    @pytest.fixture(autouse=True)
    def logger_with_filter(self) -> logging.Logger:
        logger = logging.getLogger("openai")
        logger.setLevel(logging.DEBUG)
        logger.addFilter(SensitiveHeadersFilter())
        return logger

    @pytest.mark.respx()
    def test_azure_api_key_redacted(self, respx_mock: MockRouter, caplog: pytest.LogCaptureFixture) -> None:
        respx_mock.post(
            "https://example-resource.azure.openai.com/openai/deployments/gpt-4/chat/completions?api-version=2024-06-01"
        ).mock(
            return_value=httpx.Response(200, json={"model": "gpt-4"})
        )

        client = AzureOpenAI(
            api_version="2024-06-01",
            api_key="example_api_key",
            azure_endpoint="https://example-resource.azure.openai.com",
        )

        with caplog.at_level(logging.DEBUG):
            client.chat.completions.create(messages=[], model="gpt-4")

        for record in caplog.records:
            if is_dict(record.args) and record.args.get("headers") and is_dict(record.args["headers"]):
                assert record.args["headers"]["api-key"] == "<redacted>"


    @pytest.mark.respx()
    def test_azure_bearer_token_redacted(self, respx_mock: MockRouter, caplog: pytest.LogCaptureFixture) -> None:
        respx_mock.post(
            "https://example-resource.azure.openai.com/openai/deployments/gpt-4/chat/completions?api-version=2024-06-01"
        ).mock(
            return_value=httpx.Response(200, json={"model": "gpt-4"})
        )

        client = AzureOpenAI(
            api_version="2024-06-01",
            azure_ad_token="example_token",
            azure_endpoint="https://example-resource.azure.openai.com",
        )

        with caplog.at_level(logging.DEBUG):
            client.chat.completions.create(messages=[], model="gpt-4")

        for record in caplog.records:
            if is_dict(record.args) and record.args.get("headers") and is_dict(record.args["headers"]):
                assert record.args["headers"]["Authorization"] == "<redacted>"


    @pytest.mark.asyncio
    @pytest.mark.respx()
    async def test_azure_api_key_redacted_async(self, respx_mock: MockRouter, caplog: pytest.LogCaptureFixture) -> None:
        respx_mock.post(
            "https://example-resource.azure.openai.com/openai/deployments/gpt-4/chat/completions?api-version=2024-06-01"
        ).mock(
            return_value=httpx.Response(200, json={"model": "gpt-4"})
        )

        client = AsyncAzureOpenAI(
            api_version="2024-06-01",
            api_key="example_api_key",
            azure_endpoint="https://example-resource.azure.openai.com",
        )

        with caplog.at_level(logging.DEBUG):
            await client.chat.completions.create(messages=[], model="gpt-4")

        for record in caplog.records:
            if is_dict(record.args) and record.args.get("headers") and is_dict(record.args["headers"]):
                assert record.args["headers"]["api-key"] == "<redacted>"


    @pytest.mark.asyncio
    @pytest.mark.respx()
    async def test_azure_bearer_token_redacted_async(self, respx_mock: MockRouter, caplog: pytest.LogCaptureFixture) -> None:
        respx_mock.post(
            "https://example-resource.azure.openai.com/openai/deployments/gpt-4/chat/completions?api-version=2024-06-01"
        ).mock(
            return_value=httpx.Response(200, json={"model": "gpt-4"})
        )

        client = AsyncAzureOpenAI(
            api_version="2024-06-01",
            azure_ad_token="example_token",
            azure_endpoint="https://example-resource.azure.openai.com",
        )

        with caplog.at_level(logging.DEBUG):
            await client.chat.completions.create(messages=[], model="gpt-4")

        for record in caplog.records:
            if is_dict(record.args) and record.args.get("headers") and is_dict(record.args["headers"]):
                assert record.args["headers"]["Authorization"] == "<redacted>"
