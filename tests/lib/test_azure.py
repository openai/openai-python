from typing import Union
from typing_extensions import Literal

import pytest
import httpx

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


@pytest.mark.parametrize(
    "client,headers,timeout",
    [
        (sync_client, {"retry-after-ms": "2000"}, 2.0),
        (sync_client, {"retry-after-ms": "2", "retry-after": "1"}, 0.002),
        (sync_client, {"Retry-After-Ms": "2", "Retry-After": "1"}, 0.002),
        (async_client, {"retry-after-ms": "2000"}, 2.0),
        (async_client, {"retry-after-ms": "2", "retry-after": "1"}, 0.002),
        (async_client, {"Retry-After-Ms": "2", "Retry-After": "1"}, 0.002),
    ],
)
def test_parse_retry_after_ms_header(client: Client, headers: httpx.Headers, timeout: float) -> None:
    headers = httpx.Headers(headers)
    options = FinalRequestOptions(method="post", url="/completions")
    retry_timeout = client._calculate_retry_timeout(
        remaining_retries=2,
        options=options,
        response_headers=headers
    )
    assert retry_timeout == timeout


@pytest.mark.parametrize(
    "client,headers",
    [
        (sync_client, {}),
        (async_client, {}),
        (sync_client, None),
        (async_client, None),
    ],
)
def test_no_retry_after_header(client: Client, headers: httpx.Headers) -> None:
    headers = httpx.Headers(headers)
    options = FinalRequestOptions(method="post", url="/completions")
    retry_timeout = client._calculate_retry_timeout(
        remaining_retries=2,
        options=options,
        response_headers=headers
    )
    assert retry_timeout  # uses default retry implementation



@pytest.mark.parametrize(
    "client,headers",
    [
        (sync_client, {"retry-after-ms": "invalid"}),
        (async_client, {"retry-after-ms": "invalid"}),
    ],
)
def test_invalid_retry_after_header(client: Client, headers: httpx.Headers) -> None:
    headers = httpx.Headers(headers)
    options = FinalRequestOptions(method="post", url="/completions")
    retry_timeout = client._calculate_retry_timeout(
        remaining_retries=2,
        options=options,
        response_headers=headers
    )
    assert retry_timeout  # uses default retry implementation
