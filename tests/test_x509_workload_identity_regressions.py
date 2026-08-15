from __future__ import annotations

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

import anyio
import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, OpenAIError
from openai.auth import X509WorkloadIdentity, x509_workload_identity

_TOKEN_URL = "https://mtls.auth.openai.com/oauth/token"
_API_URL = "https://mtls.api.openai.com/v1/models"


def _identity() -> X509WorkloadIdentity:
    return x509_workload_identity(identity_provider_id="idp_123", service_account_id="svc_acct_123")


@pytest.mark.parametrize("authorization", [None, "Bearer caller-override"])
def test_sync_x509_disables_redirects_without_placeholder_authorization(authorization: str | None) -> None:
    urls: list[str] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        urls.append(str(request.url))
        return httpx2.Response(302, request=request, headers={"location": "https://other.example/v1/models"})

    headers = {} if authorization is None else {"Authorization": authorization}
    request = httpx2.Request("GET", _API_URL, headers=headers)
    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), follow_redirects=True, trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        response = client._send_request(request, stream=False)

    assert response.status_code == 302
    assert urls == [_API_URL]


@pytest.mark.parametrize("authorization", [None, "Bearer caller-override"])
async def test_async_x509_disables_redirects_without_placeholder_authorization(authorization: str | None) -> None:
    urls: list[str] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        urls.append(str(request.url))
        return httpx2.Response(302, request=request, headers={"location": "https://other.example/v1/models"})

    headers = {} if authorization is None else {"Authorization": authorization}
    request = httpx2.Request("GET", _API_URL, headers=headers)
    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), follow_redirects=True, trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        response = await client._send_request(request, stream=False)

    assert response.status_code == 302
    assert urls == [_API_URL]


@pytest.mark.parametrize("response_body", [[], "not-an-object", 42, True])
def test_sync_x509_rejects_non_object_token_responses(response_body: object) -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(200, request=request, json=response_body)

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="response body was not a JSON object"):
            client.models.list()


@pytest.mark.parametrize("response_body", [[], "not-an-object", 42, True])
async def test_async_x509_rejects_non_object_token_responses(response_body: object) -> None:
    async def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(200, request=request, json=response_body)

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="response body was not a JSON object"):
            await client.models.list()


def test_sync_x509_concurrent_stale_401_responses_share_one_replacement_token() -> None:
    exchange_calls = 0
    stale_requests = 0
    state_lock = threading.Lock()
    both_stale_requests = threading.Barrier(2)
    replacement_issued = threading.Event()

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_calls, stale_requests
        if str(request.url) == _TOKEN_URL:
            with state_lock:
                exchange_calls += 1
                token_number = exchange_calls
            if token_number == 2:
                replacement_issued.set()
            return httpx2.Response(
                200, request=request, json={"access_token": f"token-{token_number}", "expires_in": 3600}
            )

        authorization = request.headers["Authorization"]
        if authorization == "Bearer token-1":
            with state_lock:
                stale_requests += 1
                request_number = stale_requests
            both_stale_requests.wait(timeout=5)
            if request_number == 2:
                assert replacement_issued.wait(timeout=5)
            return httpx2.Response(401, request=request, json={"error": {"message": "unauthorized"}})

        assert authorization == "Bearer token-2"
        return httpx2.Response(200, request=request, json={"object": "list", "data": []})

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:

        def list_models(_: int) -> str:
            return client.models.list().object

        with ThreadPoolExecutor(max_workers=2) as executor:
            responses = list(executor.map(list_models, range(2)))

    assert responses == ["list", "list"]
    assert exchange_calls == 2


async def test_async_x509_concurrent_stale_401_responses_share_one_replacement_token() -> None:
    exchange_calls = 0
    stale_requests = 0
    both_stale_requests = anyio.Event()
    replacement_issued = anyio.Event()

    async def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_calls, stale_requests
        if str(request.url) == _TOKEN_URL:
            exchange_calls += 1
            if exchange_calls == 2:
                replacement_issued.set()
            return httpx2.Response(
                200, request=request, json={"access_token": f"token-{exchange_calls}", "expires_in": 3600}
            )

        authorization = request.headers["Authorization"]
        if authorization == "Bearer token-1":
            stale_requests += 1
            request_number = stale_requests
            if stale_requests == 2:
                both_stale_requests.set()
            await both_stale_requests.wait()
            if request_number == 2:
                await replacement_issued.wait()
            return httpx2.Response(401, request=request, json={"error": {"message": "unauthorized"}})

        assert authorization == "Bearer token-2"
        return httpx2.Response(200, request=request, json={"object": "list", "data": []})

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        responses = await asyncio.gather(client.models.list(), client.models.list())

    assert [response.object for response in responses] == ["list", "list"]
    assert exchange_calls == 2
