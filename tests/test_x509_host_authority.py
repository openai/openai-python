from __future__ import annotations

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, OpenAIError
from openai.auth import x509_workload_identity

_AUTH_HOST = "mtls.auth.openai.com"


def _response(request: httpx2.Request) -> httpx2.Response:
    if request.url.host == _AUTH_HOST:
        return httpx2.Response(200, request=request, json={"access_token": "trusted-token", "expires_in": 3600})
    return httpx2.Response(200, request=request, json={"object": "list", "data": []})


@pytest.mark.parametrize("source", ["client", "request", "hook"])
@pytest.mark.parametrize(
    "host",
    [
        "attacker.invalid",
        "mtls.api.openai.com:8443",
        "user@mtls.api.openai.com",
        "mtls.api.openai.com/",
        "mtls.api.openai.com?",
        "mtls.api.openai.com#",
    ],
)
def test_sync_x509_rejects_mismatched_effective_host(source: str, host: str) -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    def hook(request: httpx2.Request) -> None:
        request.headers["Host"] = host

    http_client = httpx2.Client(
        transport=httpx2.MockTransport(handler),
        headers={"Host": host} if source == "client" else None,
        event_hooks={"request": [hook]} if source == "hook" else None,
        trust_env=False,
    )
    identity = x509_workload_identity(identity_provider_id="provider", service_account_id="account")
    with OpenAI(workload_identity=identity, http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="Host|authority|credentials"):
            client.models.list(extra_headers={"Host": host} if source == "request" else None)

    assert [request.url.host for request in requests] == ([_AUTH_HOST] if source == "hook" else [])


@pytest.mark.parametrize("source", ["client", "request", "hook"])
@pytest.mark.parametrize(
    "host",
    [
        "attacker.invalid",
        "mtls.api.openai.com:8443",
        "user@mtls.api.openai.com",
        "mtls.api.openai.com/",
        "mtls.api.openai.com?",
        "mtls.api.openai.com#",
    ],
)
async def test_async_x509_rejects_mismatched_effective_host(source: str, host: str) -> None:
    requests: list[httpx2.Request] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    async def hook(request: httpx2.Request) -> None:
        request.headers["Host"] = host

    http_client = httpx2.AsyncClient(
        transport=httpx2.MockTransport(handler),
        headers={"Host": host} if source == "client" else None,
        event_hooks={"request": [hook]} if source == "hook" else None,
        trust_env=False,
    )
    identity = x509_workload_identity(identity_provider_id="provider", service_account_id="account")
    async with AsyncOpenAI(workload_identity=identity, http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="Host|authority|credentials"):
            await client.models.list(extra_headers={"Host": host} if source == "request" else None)

    assert [request.url.host for request in requests] == ([_AUTH_HOST] if source == "hook" else [])


@pytest.mark.parametrize("host", ["mtls.api.openai.com", "MTLS.API.OPENAI.COM", "mtls.api.openai.com:443"])
def test_sync_x509_accepts_normalized_matching_host(host: str) -> None:
    http_client = httpx2.Client(transport=httpx2.MockTransport(_response), trust_env=False)
    identity = x509_workload_identity(identity_provider_id="provider", service_account_id="account")
    with OpenAI(workload_identity=identity, http_client=http_client, max_retries=0) as client:
        assert client.models.list(extra_headers={"Host": host}).object == "list"


@pytest.mark.parametrize("host", ["mtls.api.openai.com", "MTLS.API.OPENAI.COM", "mtls.api.openai.com:443"])
async def test_async_x509_accepts_normalized_matching_host(host: str) -> None:
    async def handler(request: httpx2.Request) -> httpx2.Response:
        return _response(request)

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    identity = x509_workload_identity(identity_provider_id="provider", service_account_id="account")
    async with AsyncOpenAI(workload_identity=identity, http_client=http_client, max_retries=0) as client:
        assert (await client.models.list(extra_headers={"Host": host})).object == "list"


def test_sync_x509_rejects_duplicate_host_headers_at_final_transport() -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    def hook(request: httpx2.Request) -> None:
        request.headers = httpx2.Headers([*request.headers.multi_items(), ("Host", "attacker.invalid")])

    http_client = httpx2.Client(
        transport=httpx2.MockTransport(handler), event_hooks={"request": [hook]}, trust_env=False
    )
    identity = x509_workload_identity(identity_provider_id="provider", service_account_id="account")
    with OpenAI(workload_identity=identity, http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="Host|authority"):
            client.models.list()

    assert [request.url.host for request in requests] == [_AUTH_HOST]


async def test_async_x509_rejects_duplicate_host_headers_at_final_transport() -> None:
    requests: list[httpx2.Request] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    async def hook(request: httpx2.Request) -> None:
        request.headers = httpx2.Headers([*request.headers.multi_items(), ("Host", "attacker.invalid")])

    http_client = httpx2.AsyncClient(
        transport=httpx2.MockTransport(handler), event_hooks={"request": [hook]}, trust_env=False
    )
    identity = x509_workload_identity(identity_provider_id="provider", service_account_id="account")
    async with AsyncOpenAI(workload_identity=identity, http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="Host|authority"):
            await client.models.list()

    assert [request.url.host for request in requests] == [_AUTH_HOST]
