from __future__ import annotations

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
        ).mock(return_value=httpx.Response(200, json={"model": "gpt-4"}))

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
        ).mock(return_value=httpx.Response(200, json={"model": "gpt-4"}))

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
        ).mock(return_value=httpx.Response(200, json={"model": "gpt-4"}))

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
    async def test_azure_bearer_token_redacted_async(
        self, respx_mock: MockRouter, caplog: pytest.LogCaptureFixture
    ) -> None:
        respx_mock.post(
            "https://example-resource.azure.openai.com/openai/deployments/gpt-4/chat/completions?api-version=2024-06-01"
        ).mock(return_value=httpx.Response(200, json={"model": "gpt-4"}))

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


@pytest.mark.parametrize(
    "client,base_url,api,json_data,expected",
    [
        # Deployment-based endpoints
        # AzureOpenAI: No deployment specified
        (
            AzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
            ),
            "https://example-resource.azure.openai.com/openai/",
            "/chat/completions",
            {"model": "deployment-body"},
            "https://example-resource.azure.openai.com/openai/deployments/deployment-body/chat/completions?api-version=2024-02-01",
        ),
        # AzureOpenAI: Deployment specified
        (
            AzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
                azure_deployment="deployment-client",
            ),
            "https://example-resource.azure.openai.com/openai/deployments/deployment-client/",
            "/chat/completions",
            {"model": "deployment-body"},
            "https://example-resource.azure.openai.com/openai/deployments/deployment-client/chat/completions?api-version=2024-02-01",
        ),
        # AzureOpenAI: "deployments" in the DNS name
        (
            AzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://deployments.example-resource.azure.openai.com",
            ),
            "https://deployments.example-resource.azure.openai.com/openai/",
            "/chat/completions",
            {"model": "deployment-body"},
            "https://deployments.example-resource.azure.openai.com/openai/deployments/deployment-body/chat/completions?api-version=2024-02-01",
        ),
        # AzureOpenAI: Deployment called deployments
        (
            AzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
                azure_deployment="deployments",
            ),
            "https://example-resource.azure.openai.com/openai/deployments/deployments/",
            "/chat/completions",
            {"model": "deployment-body"},
            "https://example-resource.azure.openai.com/openai/deployments/deployments/chat/completions?api-version=2024-02-01",
        ),
        # AzureOpenAI: base_url and azure_deployment specified; ignored b/c not supported
        (
            AzureOpenAI(  # type: ignore
                api_version="2024-02-01",
                api_key="example API key",
                base_url="https://example.azure-api.net/PTU/",
                azure_deployment="deployment-client",
            ),
            "https://example.azure-api.net/PTU/",
            "/chat/completions",
            {"model": "deployment-body"},
            "https://example.azure-api.net/PTU/deployments/deployment-body/chat/completions?api-version=2024-02-01",
        ),
        # AsyncAzureOpenAI: No deployment specified
        (
            AsyncAzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
            ),
            "https://example-resource.azure.openai.com/openai/",
            "/chat/completions",
            {"model": "deployment-body"},
            "https://example-resource.azure.openai.com/openai/deployments/deployment-body/chat/completions?api-version=2024-02-01",
        ),
        # AsyncAzureOpenAI: Deployment specified
        (
            AsyncAzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
                azure_deployment="deployment-client",
            ),
            "https://example-resource.azure.openai.com/openai/deployments/deployment-client/",
            "/chat/completions",
            {"model": "deployment-body"},
            "https://example-resource.azure.openai.com/openai/deployments/deployment-client/chat/completions?api-version=2024-02-01",
        ),
        # AsyncAzureOpenAI: "deployments" in the DNS name
        (
            AsyncAzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://deployments.example-resource.azure.openai.com",
            ),
            "https://deployments.example-resource.azure.openai.com/openai/",
            "/chat/completions",
            {"model": "deployment-body"},
            "https://deployments.example-resource.azure.openai.com/openai/deployments/deployment-body/chat/completions?api-version=2024-02-01",
        ),
        # AsyncAzureOpenAI: Deployment called deployments
        (
            AsyncAzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
                azure_deployment="deployments",
            ),
            "https://example-resource.azure.openai.com/openai/deployments/deployments/",
            "/chat/completions",
            {"model": "deployment-body"},
            "https://example-resource.azure.openai.com/openai/deployments/deployments/chat/completions?api-version=2024-02-01",
        ),
        # AsyncAzureOpenAI: base_url and azure_deployment specified; azure_deployment ignored b/c not supported
        (
            AsyncAzureOpenAI(  # type: ignore
                api_version="2024-02-01",
                api_key="example API key",
                base_url="https://example.azure-api.net/PTU/",
                azure_deployment="deployment-client",
            ),
            "https://example.azure-api.net/PTU/",
            "/chat/completions",
            {"model": "deployment-body"},
            "https://example.azure-api.net/PTU/deployments/deployment-body/chat/completions?api-version=2024-02-01",
        ),
    ],
)
def test_prepare_url_deployment_endpoint(
    client: Client, base_url: str, api: str, json_data: dict[str, str], expected: str
) -> None:
    req = client._build_request(
        FinalRequestOptions.construct(
            method="post",
            url=api,
            json_data=json_data,
        )
    )
    assert req.url == expected
    assert client.base_url == base_url


@pytest.mark.parametrize(
    "client,base_url,api,json_data,expected",
    [
        # Non-deployment endpoints
        # AzureOpenAI: No deployment specified
        (
            AzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
            ),
            "https://example-resource.azure.openai.com/openai/",
            "/models",
            {},
            "https://example-resource.azure.openai.com/openai/models?api-version=2024-02-01",
        ),
        # AzureOpenAI: No deployment specified
        (
            AzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
            ),
            "https://example-resource.azure.openai.com/openai/",
            "/assistants",
            {"model": "deployment-body"},
            "https://example-resource.azure.openai.com/openai/assistants?api-version=2024-02-01",
        ),
        # AzureOpenAI: Deployment specified
        (
            AzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
                azure_deployment="deployment-client",
            ),
            "https://example-resource.azure.openai.com/openai/deployments/deployment-client/",
            "/models",
            {},
            "https://example-resource.azure.openai.com/openai/models?api-version=2024-02-01",
        ),
        # AzureOpenAI: Deployment specified
        (
            AzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
                azure_deployment="deployment-client",
            ),
            "https://example-resource.azure.openai.com/openai/deployments/deployment-client/",
            "/assistants",
            {"model": "deployment-body"},
            "https://example-resource.azure.openai.com/openai/assistants?api-version=2024-02-01",
        ),
        # AzureOpenAI: "deployments" in the DNS name
        (
            AzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://deployments.example-resource.azure.openai.com",
            ),
            "https://deployments.example-resource.azure.openai.com/openai/",
            "/models",
            {},
            "https://deployments.example-resource.azure.openai.com/openai/models?api-version=2024-02-01",
        ),
        # AzureOpenAI: Deployment called "deployments"
        (
            AzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
                azure_deployment="deployments",
            ),
            "https://example-resource.azure.openai.com/openai/deployments/deployments/",
            "/models",
            {},
            "https://example-resource.azure.openai.com/openai/models?api-version=2024-02-01",
        ),
        # AzureOpenAI: base_url and azure_deployment specified; azure_deployment ignored b/c not supported
        (
            AzureOpenAI(  # type: ignore
                api_version="2024-02-01",
                api_key="example API key",
                base_url="https://example.azure-api.net/PTU/",
                azure_deployment="deployment-client",
            ),
            "https://example.azure-api.net/PTU/",
            "/models",
            {},
            "https://example.azure-api.net/PTU/models?api-version=2024-02-01",
        ),
        # AsyncAzureOpenAI: No deployment specified
        (
            AsyncAzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
            ),
            "https://example-resource.azure.openai.com/openai/",
            "/models",
            {},
            "https://example-resource.azure.openai.com/openai/models?api-version=2024-02-01",
        ),
        # AsyncAzureOpenAI: No deployment specified
        (
            AsyncAzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
            ),
            "https://example-resource.azure.openai.com/openai/",
            "/assistants",
            {"model": "deployment-body"},
            "https://example-resource.azure.openai.com/openai/assistants?api-version=2024-02-01",
        ),
        # AsyncAzureOpenAI: Deployment specified
        (
            AsyncAzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
                azure_deployment="deployment-client",
            ),
            "https://example-resource.azure.openai.com/openai/deployments/deployment-client/",
            "/models",
            {},
            "https://example-resource.azure.openai.com/openai/models?api-version=2024-02-01",
        ),
        # AsyncAzureOpenAI: Deployment specified
        (
            AsyncAzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
                azure_deployment="deployment-client",
            ),
            "https://example-resource.azure.openai.com/openai/deployments/deployment-client/",
            "/assistants",
            {"model": "deployment-body"},
            "https://example-resource.azure.openai.com/openai/assistants?api-version=2024-02-01",
        ),
        # AsyncAzureOpenAI: "deployments" in the DNS name
        (
            AsyncAzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://deployments.example-resource.azure.openai.com",
            ),
            "https://deployments.example-resource.azure.openai.com/openai/",
            "/models",
            {},
            "https://deployments.example-resource.azure.openai.com/openai/models?api-version=2024-02-01",
        ),
        # AsyncAzureOpenAI: Deployment called "deployments"
        (
            AsyncAzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
                azure_deployment="deployments",
            ),
            "https://example-resource.azure.openai.com/openai/deployments/deployments/",
            "/models",
            {},
            "https://example-resource.azure.openai.com/openai/models?api-version=2024-02-01",
        ),
        # AsyncAzureOpenAI: base_url and azure_deployment specified; azure_deployment ignored b/c not supported
        (
            AsyncAzureOpenAI(  # type: ignore
                api_version="2024-02-01",
                api_key="example API key",
                base_url="https://example.azure-api.net/PTU/",
                azure_deployment="deployment-client",
            ),
            "https://example.azure-api.net/PTU/",
            "/models",
            {},
            "https://example.azure-api.net/PTU/models?api-version=2024-02-01",
        ),
    ],
)
def test_prepare_url_nondeployment_endpoint(
    client: Client, base_url: str, api: str, json_data: dict[str, str], expected: str
) -> None:
    req = client._build_request(
        FinalRequestOptions.construct(
            method="post",
            url=api,
            json_data=json_data,
        )
    )
    assert req.url == expected
    assert client.base_url == base_url


@pytest.mark.parametrize(
    "client,base_url,json_data,expected",
    [
        # Realtime endpoint
        # AzureOpenAI: No deployment specified
        (
            AzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
            ),
            "https://example-resource.azure.openai.com/openai/",
            {"model": "deployment-body"},
            "wss://example-resource.azure.openai.com/openai/realtime?api-version=2024-02-01&deployment=deployment-body",
        ),
        # AzureOpenAI: Deployment specified
        (
            AzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
                azure_deployment="deployment-client",
            ),
            "https://example-resource.azure.openai.com/openai/deployments/deployment-client/",
            {"model": "deployment-body"},
            "wss://example-resource.azure.openai.com/openai/realtime?api-version=2024-02-01&deployment=deployment-client",
        ),
        # AzureOpenAI: "deployments" in the DNS name
        (
            AzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://deployments.azure.openai.com",
            ),
            "https://deployments.azure.openai.com/openai/",
            {"model": "deployment-body"},
            "wss://deployments.azure.openai.com/openai/realtime?api-version=2024-02-01&deployment=deployment-body",
        ),
        # AzureOpenAI: Deployment called "deployments"
        (
            AzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
                azure_deployment="deployments",
            ),
            "https://example-resource.azure.openai.com/openai/deployments/deployments/",
            {"model": "deployment-body"},
            "wss://example-resource.azure.openai.com/openai/realtime?api-version=2024-02-01&deployment=deployments",
        ),
        # AzureOpenAI: base_url and azure_deployment specified; azure_deployment ignored b/c not supported
        (
            AzureOpenAI(  # type: ignore
                api_version="2024-02-01",
                api_key="example API key",
                base_url="https://example.azure-api.net/PTU/",
                azure_deployment="my-deployment",
            ),
            "https://example.azure-api.net/PTU/",
            {"model": "deployment-body"},
            "wss://example.azure-api.net/PTU/realtime?api-version=2024-02-01&deployment=deployment-body",
        ),
        # AzureOpenAI: websocket_base_url specified
        (
            AzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
                websocket_base_url="wss://example-resource.azure.openai.com/base",
            ),
            "https://example-resource.azure.openai.com/openai/",
            {"model": "deployment-body"},
            "wss://example-resource.azure.openai.com/base/realtime?api-version=2024-02-01&deployment=deployment-body",
        ),
    ],
)
def test_prepare_url_realtime(client: AzureOpenAI, base_url: str, json_data: dict[str, str], expected: str) -> None:
    url, _ = client._configure_realtime(json_data["model"], {})
    assert str(url) == expected
    assert client.base_url == base_url


@pytest.mark.parametrize(
    "client,base_url,json_data,expected",
    [
        # AsyncAzureOpenAI: No deployment specified
        (
            AsyncAzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
            ),
            "https://example-resource.azure.openai.com/openai/",
            {"model": "deployment-body"},
            "wss://example-resource.azure.openai.com/openai/realtime?api-version=2024-02-01&deployment=deployment-body",
        ),
        # AsyncAzureOpenAI: Deployment specified
        (
            AsyncAzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
                azure_deployment="deployment-client",
            ),
            "https://example-resource.azure.openai.com/openai/deployments/deployment-client/",
            {"model": "deployment-body"},
            "wss://example-resource.azure.openai.com/openai/realtime?api-version=2024-02-01&deployment=deployment-client",
        ),
        # AsyncAzureOpenAI: "deployments" in the DNS name
        (
            AsyncAzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://deployments.azure.openai.com",
            ),
            "https://deployments.azure.openai.com/openai/",
            {"model": "deployment-body"},
            "wss://deployments.azure.openai.com/openai/realtime?api-version=2024-02-01&deployment=deployment-body",
        ),
        # AsyncAzureOpenAI: Deployment called "deployments"
        (
            AsyncAzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
                azure_deployment="deployments",
            ),
            "https://example-resource.azure.openai.com/openai/deployments/deployments/",
            {"model": "deployment-body"},
            "wss://example-resource.azure.openai.com/openai/realtime?api-version=2024-02-01&deployment=deployments",
        ),
        # AsyncAzureOpenAI: base_url and azure_deployment specified; azure_deployment ignored b/c not supported
        (
            AsyncAzureOpenAI(  # type: ignore
                api_version="2024-02-01",
                api_key="example API key",
                base_url="https://example.azure-api.net/PTU/",
                azure_deployment="deployment-client",
            ),
            "https://example.azure-api.net/PTU/",
            {"model": "deployment-body"},
            "wss://example.azure-api.net/PTU/realtime?api-version=2024-02-01&deployment=deployment-body",
        ),
        # AsyncAzureOpenAI: websocket_base_url specified
        (
            AsyncAzureOpenAI(
                api_version="2024-02-01",
                api_key="example API key",
                azure_endpoint="https://example-resource.azure.openai.com",
                websocket_base_url="wss://example-resource.azure.openai.com/base",
            ),
            "https://example-resource.azure.openai.com/openai/",
            {"model": "deployment-body"},
            "wss://example-resource.azure.openai.com/base/realtime?api-version=2024-02-01&deployment=deployment-body",
        ),
    ],
)
async def test_prepare_url_realtime_async(
    client: AsyncAzureOpenAI, base_url: str, json_data: dict[str, str], expected: str
) -> None:
    url, _ = await client._configure_realtime(json_data["model"], {})
    assert str(url) == expected
    assert client.base_url == base_url


def test_client_sets_base_url(client: Client) -> None:
    client = AzureOpenAI(
        api_version="2024-02-01",
        api_key="example API key",
        azure_endpoint="https://example-resource.azure.openai.com",
        azure_deployment="my-deployment",
    )
    assert client.base_url == "https://example-resource.azure.openai.com/openai/deployments/my-deployment/"

    # (not recommended) user sets base_url to target different deployment
    client.base_url = "https://example-resource.azure.openai.com/openai/deployments/different-deployment/"
    req = client._build_request(
        FinalRequestOptions.construct(
            method="post",
            url="/chat/completions",
            json_data={"model": "placeholder"},
        )
    )
    assert (
        req.url
        == "https://example-resource.azure.openai.com/openai/deployments/different-deployment/chat/completions?api-version=2024-02-01"
    )
    req = client._build_request(
        FinalRequestOptions.construct(
            method="post",
            url="/models",
            json_data={},
        )
    )
    assert req.url == "https://example-resource.azure.openai.com/openai/models?api-version=2024-02-01"

    # (not recommended) user sets base_url to remove deployment
    client.base_url = "https://example-resource.azure.openai.com/openai/"
    req = client._build_request(
        FinalRequestOptions.construct(
            method="post",
            url="/chat/completions",
            json_data={"model": "deployment"},
        )
    )
    assert (
        req.url
        == "https://example-resource.azure.openai.com/openai/deployments/deployment/chat/completions?api-version=2024-02-01"
    )
    req = client._build_request(
        FinalRequestOptions.construct(
            method="post",
            url="/models",
            json_data={},
        )
    )
    assert req.url == "https://example-resource.azure.openai.com/openai/models?api-version=2024-02-01"
