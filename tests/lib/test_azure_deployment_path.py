from __future__ import annotations

import json

import httpx2
import pytest

from openai._models import FinalRequestOptions
from openai.lib.azure import AzureOpenAI, AsyncAzureOpenAI, _deployments_endpoints

_ENDPOINT = "https://azure.example.invalid"
_API_VERSION = "2024-02-01"
_MODELS = [
    ("my-deployment_1.2", "my-deployment_1.2"),
    (".hidden", ".hidden"),
    ("...", "..."),
    ("a/b", "a%2Fb"),
    ("../other/operation#", "..%2Fother%2Foperation%23"),
    ("a/./b/../c", "a%2F.%2Fb%2F..%2Fc"),
    ("%2e%2E%2fother%3fquery%23fragment", "%252e%252E%252fother%253fquery%2523fragment"),
    ("%252e%252e%252fother", "%25252e%25252e%25252fother"),
    ("%2e", "%252e"),
    (".%2E", ".%252E"),
    ("%2e.", "%252e."),
    ("a?api-version=other&x=y", "a%3Fapi-version=other&x=y"),
    ("a#fragment", "a%23fragment"),
    ("a\\b", "a%5Cb"),
    ("a\r\n/b", "a%0D%0A%2Fb"),
    ("a b", "a%20b"),
]


def _assert_request(request: httpx2.Request, path: str, model: str) -> None:
    assert request.method == "POST"
    assert str(request.url) == f"{_ENDPOINT}/openai{path}?api-version={_API_VERSION}"
    assert request.url.raw_path == f"/openai{path}?api-version={_API_VERSION}".encode()
    assert not request.url.fragment
    assert json.loads(request.content)["model"] == model


@pytest.mark.parametrize("client_type", [AzureOpenAI, AsyncAzureOpenAI])
@pytest.mark.parametrize("endpoint", sorted(_deployments_endpoints))
@pytest.mark.parametrize("model,encoded", _MODELS)
def test_deployment_model_is_one_path_segment(
    client_type: type[AzureOpenAI] | type[AsyncAzureOpenAI], endpoint: str, model: str, encoded: str
) -> None:
    client = client_type(api_key="fake-key", api_version=_API_VERSION, azure_endpoint=_ENDPOINT)
    request = client._build_request(
        FinalRequestOptions.construct(method="post", url=endpoint, json_data={"model": model})
    )
    _assert_request(request, f"/deployments/{encoded}{endpoint}", model)


@pytest.mark.parametrize("client_type", [AzureOpenAI, AsyncAzureOpenAI])
@pytest.mark.parametrize("endpoint", sorted(_deployments_endpoints))
@pytest.mark.parametrize("model", [".", ".."])
def test_deployment_model_rejects_dot_segments(
    client_type: type[AzureOpenAI] | type[AsyncAzureOpenAI], endpoint: str, model: str
) -> None:
    client = client_type(api_key="fake-key", api_version=_API_VERSION, azure_endpoint=_ENDPOINT)
    with pytest.raises(ValueError, match="dot-segment"):
        client._build_request(FinalRequestOptions.construct(method="post", url=endpoint, json_data={"model": model}))


@pytest.mark.parametrize("client_type", [AzureOpenAI, AsyncAzureOpenAI])
@pytest.mark.parametrize("deployment", [None, "fixed-deployment"])
@pytest.mark.parametrize("endpoint", ["/chat/completions", "/responses", "/files"])
def test_deployment_rewrite_preserves_existing_routes(
    client_type: type[AzureOpenAI] | type[AsyncAzureOpenAI], deployment: str | None, endpoint: str
) -> None:
    client = client_type(
        api_key="fake-key", api_version=_API_VERSION, azure_endpoint=_ENDPOINT, azure_deployment=deployment
    )
    model = ".." if deployment is not None or endpoint != "/chat/completions" else "ordinary-model"
    request = client._build_request(
        FinalRequestOptions.construct(method="post", url=endpoint, json_data={"model": model})
    )
    prefix = f"/deployments/{deployment or model}" if endpoint == "/chat/completions" else ""
    _assert_request(request, prefix + endpoint, model)


@pytest.mark.parametrize("model,encoded", _MODELS)
def test_sync_deployment_request(model: str, encoded: str) -> None:
    requests: list[httpx2.Request] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, json={"id": "fake-completion", "choices": []})

    with AzureOpenAI(
        api_key="fake-key",
        api_version=_API_VERSION,
        azure_endpoint=_ENDPOINT,
        http_client=httpx2.Client(transport=httpx2.MockTransport(handle)),
    ) as client:
        client.chat.completions.create(model=model, messages=[])

    assert len(requests) == 1
    _assert_request(requests[0], f"/deployments/{encoded}/chat/completions", model)


@pytest.mark.parametrize("model,encoded", _MODELS)
async def test_async_deployment_request(model: str, encoded: str) -> None:
    requests: list[httpx2.Request] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, json={"id": "fake-completion", "choices": []})

    async with AsyncAzureOpenAI(
        api_key="fake-key",
        api_version=_API_VERSION,
        azure_endpoint=_ENDPOINT,
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handle)),
    ) as client:
        await client.chat.completions.create(model=model, messages=[])

    assert len(requests) == 1
    _assert_request(requests[0], f"/deployments/{encoded}/chat/completions", model)


@pytest.mark.parametrize("model", [".", ".."])
def test_sync_dot_segment_is_rejected_before_send(model: str) -> None:
    def handle(_request: httpx2.Request) -> httpx2.Response:
        pytest.fail("Unexpected HTTP request")

    with AzureOpenAI(
        api_key="fake-key",
        api_version=_API_VERSION,
        azure_endpoint=_ENDPOINT,
        http_client=httpx2.Client(transport=httpx2.MockTransport(handle)),
    ) as client:
        with pytest.raises(ValueError, match="dot-segment"):
            client.chat.completions.create(model=model, messages=[])


@pytest.mark.parametrize("model", [".", ".."])
async def test_async_dot_segment_is_rejected_before_send(model: str) -> None:
    def handle(_request: httpx2.Request) -> httpx2.Response:
        pytest.fail("Unexpected HTTP request")

    async with AsyncAzureOpenAI(
        api_key="fake-key",
        api_version=_API_VERSION,
        azure_endpoint=_ENDPOINT,
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handle)),
    ) as client:
        with pytest.raises(ValueError, match="dot-segment"):
            await client.chat.completions.create(model=model, messages=[])
