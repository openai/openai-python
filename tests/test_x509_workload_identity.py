from __future__ import annotations

import io
import os
import ssl
import json
import runpy
import asyncio
import inspect
import logging
import importlib
import threading
from typing import Any, Callable, Iterable, Iterator, AsyncIterator, cast
from pathlib import Path
from typing_extensions import override
from concurrent.futures import ThreadPoolExecutor

import anyio
import httpx2
import pytest

import openai.auth._x509 as x509_auth
from openai import OpenAI, OAuthError, AsyncOpenAI, OpenAIError, APIStatusError, APITimeoutError, APIConnectionError
from openai.auth import X509WorkloadIdentity, x509_workload_identity
from openai._client import WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER

_TOKEN_URL = "https://mtls.auth.openai.com/oauth/token"
_API_URL = "https://mtls.api.openai.com/v1/models"
_MTLS_FIXTURES = Path(__file__).parent / "fixtures" / "mtls"


def _identity(**kwargs: Any) -> X509WorkloadIdentity:
    return x509_workload_identity(
        identity_provider_id="idp_123",
        service_account_id="svc_acct_123",
        **kwargs,
    )


def _token_response(
    request: httpx2.Request, *, token: str = "access-token", expires_in: object = 3600
) -> httpx2.Response:
    return httpx2.Response(200, request=request, json={"access_token": token, "expires_in": expires_in})


def _models_response(request: httpx2.Request, status_code: int = 200) -> httpx2.Response:
    return httpx2.Response(status_code, request=request, json={"object": "list", "data": []})


def test_x509_helper_returns_only_typed_identity_configuration() -> None:
    assert _identity() == {
        "type": "x509",
        "identity_provider_id": "idp_123",
        "service_account_id": "svc_acct_123",
    }
    assert _identity(refresh_buffer_seconds=45.0).get("refresh_buffer_seconds") == 45.0
    assert "token_exchange_url" not in inspect.signature(x509_workload_identity).parameters


@pytest.mark.parametrize("invalid_key", ["provider", "client_id"])
def test_x509_rejects_subject_token_configuration(invalid_key: str) -> None:
    identity = cast(X509WorkloadIdentity, {**_identity(), invalid_key: "not-allowed"})
    with pytest.raises(OpenAIError, match="does not accept a subject-token provider or client ID"):
        OpenAI(workload_identity=identity)


@pytest.mark.parametrize(
    "invalid_key",
    ["certificate", "certificate_chain", "private_key", "password", "subject_token", "token_exchange_url"],
)
def test_x509_rejects_certificate_and_token_material_without_leaking_it(invalid_key: str) -> None:
    secret = "certificate-or-token-material-never-visible"
    identity = cast(X509WorkloadIdentity, {**_identity(), invalid_key: secret})
    with pytest.raises(OpenAIError, match="only identity IDs and an optional refresh buffer") as error:
        OpenAI(workload_identity=identity)
    assert secret not in str(error.value)


@pytest.mark.parametrize("refresh_buffer", [-1.0, float("inf"), float("nan"), True, 10**400])
def test_x509_rejects_invalid_refresh_buffer(refresh_buffer: float) -> None:
    with pytest.raises(OpenAIError, match="finite, non-negative refresh buffer"):
        OpenAI(workload_identity=_identity(refresh_buffer_seconds=refresh_buffer))


def test_sync_x509_uses_one_transport_pinned_endpoint_and_cached_token() -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        if str(request.url) == _TOKEN_URL:
            return _token_response(request)
        return _models_response(request)

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    client = OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0)
    assert requests == []
    assert str(client.base_url) == "https://mtls.api.openai.com/v1/"

    assert client.models.list().object == "list"
    assert client.models.list().object == "list"
    assert [str(request.url) for request in requests] == [_TOKEN_URL, _API_URL, _API_URL]
    assert json.loads(requests[0].content) == {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subject_token_type": "urn:openai:params:oauth:token-type:x509",
        "identity_provider_id": "idp_123",
        "service_account_id": "svc_acct_123",
    }
    assert "subject_token" not in json.loads(requests[0].content)
    assert [request.headers["authorization"] for request in requests[1:]] == ["Bearer access-token"] * 2
    assert not http_client.is_closed
    client.close()


def test_sync_x509_does_not_mutate_or_independently_close_caller_transport() -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        return _token_response(request) if str(request.url) == _TOKEN_URL else _models_response(request)

    tls_context = ssl.create_default_context(cafile=_MTLS_FIXTURES / "root.pem")
    tls_context.load_cert_chain(_MTLS_FIXTURES / "client-chain.pem", _MTLS_FIXTURES / "client.key")
    transport = httpx2.MockTransport(handler)
    http_client = httpx2.Client(transport=transport, verify=tls_context, follow_redirects=True, trust_env=False)
    initial_timeout = http_client.timeout
    initial_headers = dict(http_client.headers)

    client = OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0)
    assert client.models.list().object == "list"
    assert http_client._transport is transport
    assert http_client.follow_redirects is True
    assert http_client.timeout == initial_timeout
    assert dict(http_client.headers) == initial_headers
    assert not http_client.is_closed
    auth = client._workload_identity_auth
    assert auth is not None
    assert all(not isinstance(value, ssl.SSLContext) for value in vars(auth).values())

    client.close()
    assert http_client.is_closed


async def test_async_x509_uses_one_transport_without_threaded_exchange(monkeypatch: pytest.MonkeyPatch) -> None:
    requests: list[httpx2.Request] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        if str(request.url) == _TOKEN_URL:
            return _token_response(request)
        return _models_response(request)

    async def reject_thread(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("X.509 exchange must not use a worker thread")

    monkeypatch.setattr("openai.auth._workload.to_thread", reject_thread)
    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert requests == []
        assert str(client.base_url) == "https://mtls.api.openai.com/v1/"
        assert (await client.models.list()).object == "list"
        assert (await client.models.list()).object == "list"
        assert not http_client.is_closed

    assert [str(request.url) for request in requests] == [_TOKEN_URL, _API_URL, _API_URL]
    assert "subject_token" not in json.loads(requests[0].content)


async def test_async_x509_does_not_mutate_or_independently_close_caller_transport() -> None:
    async def handler(request: httpx2.Request) -> httpx2.Response:
        return _token_response(request) if str(request.url) == _TOKEN_URL else _models_response(request)

    tls_context = ssl.create_default_context(cafile=_MTLS_FIXTURES / "root.pem")
    tls_context.load_cert_chain(_MTLS_FIXTURES / "client-chain.pem", _MTLS_FIXTURES / "client.key")
    transport = httpx2.MockTransport(handler)
    http_client = httpx2.AsyncClient(transport=transport, verify=tls_context, follow_redirects=True, trust_env=False)
    initial_timeout = http_client.timeout
    initial_headers = dict(http_client.headers)

    client = AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0)
    assert (await client.models.list()).object == "list"
    assert http_client._transport is transport
    assert http_client.follow_redirects is True
    assert http_client.timeout == initial_timeout
    assert dict(http_client.headers) == initial_headers
    assert not http_client.is_closed
    auth = client._workload_identity_auth
    assert auth is not None
    assert all(not isinstance(value, ssl.SSLContext) for value in vars(auth).values())

    await client.close()
    assert http_client.is_closed


@pytest.mark.parametrize("base_url", ["https://custom.example/v1", "https://eu.api.openai.com/v1"])
def test_x509_preserves_explicit_base_url(base_url: str) -> None:
    client = OpenAI(workload_identity=_identity(), base_url=base_url)
    assert str(client.base_url) == f"{base_url}/"
    client.close()


def test_x509_preserves_environment_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_BASE_URL", "https://custom.example/v1")
    client = OpenAI(workload_identity=_identity())
    assert str(client.base_url) == "https://custom.example/v1/"
    client.close()


def test_api_key_clients_keep_ordinary_api_endpoint() -> None:
    with OpenAI(api_key="ordinary-api-key") as client:
        assert str(client.base_url) == "https://api.openai.com/v1/"


@pytest.mark.parametrize("expires_in", [0, -1, True, "3600", None, 10**400])
def test_x509_rejects_nonpositive_or_nonnumeric_expiration(expires_in: object) -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        return _token_response(request, expires_in=expires_in)

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="expires_in"):
            client.models.list()


def test_x509_short_lived_token_clamps_refresh_buffer_to_half_ttl() -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        return _token_response(request, expires_in=8) if str(request.url) == _TOKEN_URL else _models_response(request)

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(refresh_buffer_seconds=1200), http_client=http_client) as client:
        client.models.list()
        auth = client._workload_identity_auth
        assert auth is not None
        assert auth._cached_token_expires_at_monotonic is not None
        assert auth._cached_token_refresh_at_monotonic is not None
        assert abs(auth._cached_token_expires_at_monotonic - auth._cached_token_refresh_at_monotonic - 4.0) < 0.001


@pytest.mark.parametrize("deadline", ["_cached_token_expires_at_monotonic", "_cached_token_refresh_at_monotonic"])
def test_sync_x509_refreshes_expired_or_proactively_stale_token(deadline: str) -> None:
    token_count = 0

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal token_count
        if str(request.url) == _TOKEN_URL:
            token_count += 1
            return _token_response(request, token=f"token-{token_count}")
        return _models_response(request)

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        client.models.list()
        auth = client._workload_identity_auth
        assert auth is not None
        setattr(auth, deadline, 0.0)
        client.models.list()

    assert token_count == 2


@pytest.mark.parametrize("deadline", ["_cached_token_expires_at_monotonic", "_cached_token_refresh_at_monotonic"])
async def test_async_x509_refreshes_expired_or_proactively_stale_token(deadline: str) -> None:
    token_count = 0

    async def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal token_count
        if str(request.url) == _TOKEN_URL:
            token_count += 1
            return _token_response(request, token=f"token-{token_count}")
        return _models_response(request)

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        await client.models.list()
        auth = client._workload_identity_auth
        assert auth is not None
        setattr(auth, deadline, 0.0)
        await client.models.list()

    assert token_count == 2


def test_sync_x509_concurrent_requests_share_one_exchange() -> None:
    exchange_calls = 0
    lock = threading.Lock()

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_calls
        if str(request.url) == _TOKEN_URL:
            with lock:
                exchange_calls += 1
            threading.Event().wait(0.03)
            return _token_response(request)
        return _models_response(request)

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:

        def list_models(_: int) -> str:
            return client.models.list().object

        with ThreadPoolExecutor(max_workers=8) as executor:
            assert list(executor.map(list_models, range(8))) == ["list"] * 8

    assert exchange_calls == 1


async def test_async_x509_concurrent_requests_share_one_exchange() -> None:
    exchange_calls = 0

    async def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_calls
        if str(request.url) == _TOKEN_URL:
            exchange_calls += 1
            await anyio.sleep(0.03)
            return _token_response(request)
        return _models_response(request)

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        responses = await asyncio.gather(*(client.models.list() for _ in range(8)))

    assert [response.object for response in responses] == ["list"] * 8
    assert exchange_calls == 1


async def test_async_x509_cancelled_waiter_does_not_cancel_shared_refresh() -> None:
    exchange_started = anyio.Event()
    finish_exchange = anyio.Event()
    exchange_calls = 0

    async def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_calls
        if str(request.url) == _TOKEN_URL:
            exchange_calls += 1
            exchange_started.set()
            await finish_exchange.wait()
            return _token_response(request)
        return _models_response(request)

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:

        async def list_models() -> str:
            return (await client.models.list()).object

        owner = asyncio.create_task(list_models())
        await exchange_started.wait()
        waiter = asyncio.create_task(list_models())
        await anyio.sleep(0)
        waiter.cancel()
        await asyncio.gather(waiter, return_exceptions=True)
        assert waiter.cancelled()
        finish_exchange.set()
        assert await owner == "list"
        assert (await client.models.list()).object == "list"

    assert exchange_calls == 1


async def test_async_x509_cancelled_refresh_owner_releases_waiters() -> None:
    exchange_started = anyio.Event()
    exchange_calls = 0

    async def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_calls
        if str(request.url) == _TOKEN_URL:
            exchange_calls += 1
            if exchange_calls == 1:
                exchange_started.set()
                await anyio.Event().wait()
            return _token_response(request)
        return _models_response(request)

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:

        async def list_models() -> str:
            return (await client.models.list()).object

        owner = asyncio.create_task(list_models())
        await exchange_started.wait()
        waiter = asyncio.create_task(list_models())
        await anyio.sleep(0)
        owner.cancel()
        await asyncio.gather(owner, return_exceptions=True)
        assert owner.cancelled()
        assert await waiter == "list"

    assert exchange_calls == 2


@pytest.mark.parametrize("status_code", [408, 409, 429, 500, 503])
def test_sync_x509_retries_transient_exchange_and_honors_retry_after(
    status_code: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    exchange_calls = 0
    delays: list[float] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_calls
        if str(request.url) != _TOKEN_URL:
            return _models_response(request)
        exchange_calls += 1
        if exchange_calls == 1:
            return httpx2.Response(status_code, request=request, headers={"retry-after": "0.25"})
        return _token_response(request)

    monkeypatch.setattr(x509_auth.time, "sleep", delays.append)
    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=2) as client:
        assert client.models.list().object == "list"

    assert exchange_calls == 2
    assert delays == [0.25]


async def test_async_x509_retries_transient_exchange() -> None:
    exchange_calls = 0

    async def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_calls
        if str(request.url) != _TOKEN_URL:
            return _models_response(request)
        exchange_calls += 1
        if exchange_calls == 1:
            return httpx2.Response(429, request=request, headers={"retry-after": "0"})
        return _token_response(request)

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=2) as client:
        assert (await client.models.list()).object == "list"

    assert exchange_calls == 2


async def test_async_x509_honors_retry_after_without_blocking(monkeypatch: pytest.MonkeyPatch) -> None:
    exchange_calls = 0
    delays: list[float] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_calls
        if str(request.url) != _TOKEN_URL:
            return _models_response(request)
        exchange_calls += 1
        if exchange_calls == 1:
            return httpx2.Response(429, request=request, headers={"retry-after": "0.25"})
        return _token_response(request)

    async def record_sleep(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr(x509_auth.anyio, "sleep", record_sleep)
    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=2) as client:
        assert (await client.models.list()).object == "list"

    assert delays == [0.25]


def test_x509_exchange_retries_are_bounded(monkeypatch: pytest.MonkeyPatch) -> None:
    exchange_calls = 0

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_calls
        exchange_calls += 1
        return httpx2.Response(503, request=request)

    def skip_sleep(_: float) -> None:
        return None

    monkeypatch.setattr(x509_auth.time, "sleep", skip_sleep)
    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=20) as client:
        with pytest.raises(OpenAIError, match="status 503"):
            client.models.list()

    assert exchange_calls == 3


@pytest.mark.parametrize(
    ("failure", "expected_error"),
    [(httpx2.ConnectError, APIConnectionError), (httpx2.ReadTimeout, APITimeoutError)],
)
def test_x509_connection_retries_are_bounded_without_outer_api_retries(
    failure: type[httpx2.TransportError], expected_error: type[APIConnectionError], monkeypatch: pytest.MonkeyPatch
) -> None:
    exchange_calls = 0

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_calls
        exchange_calls += 1
        raise failure("exchange unavailable", request=request)

    def skip_sleep(_: float) -> None:
        return None

    monkeypatch.setattr(x509_auth.time, "sleep", skip_sleep)
    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=20) as client:
        with pytest.raises(expected_error) as error:
            client.models.list()

    assert isinstance(error.value.__cause__, failure)
    assert exchange_calls == 3


async def test_async_x509_exchange_connection_error_preserves_original_cause() -> None:
    async def handler(request: httpx2.Request) -> httpx2.Response:
        raise httpx2.ConnectError("exchange unavailable", request=request)

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(APIConnectionError) as error:
            await client.models.list()

    assert isinstance(error.value.__cause__, httpx2.ConnectError)


@pytest.mark.parametrize("status_code", [400, 401, 403])
def test_x509_does_not_retry_oauth_failures(status_code: int) -> None:
    exchange_calls = 0

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_calls
        exchange_calls += 1
        return httpx2.Response(status_code, request=request, json={"error": "invalid_grant"})

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=2) as client:
        with pytest.raises(OAuthError):
            client.models.list()

    assert exchange_calls == 1


@pytest.mark.parametrize("status_code", [400, 401, 403])
def test_x509_oauth_errors_redact_untrusted_descriptions(status_code: int, caplog: pytest.LogCaptureFixture) -> None:
    token_secret = "bearer-token-never-visible"
    certificate_secret = "certificate-subject-never-visible"

    def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(
            status_code,
            request=request,
            json={
                "error": "invalid_grant",
                "error_description": f"{token_secret} {certificate_secret}",
                "access_token": token_secret,
            },
        )

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with caplog.at_level(logging.DEBUG):
        with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=2) as client:
            with pytest.raises(OAuthError) as error:
                client.models.list()

    assert error.value.error == "invalid_grant"
    assert error.value.body == {"error": "invalid_grant"}
    assert token_secret not in str(error.value)
    assert certificate_secret not in str(error.value)
    assert token_secret not in caplog.text
    assert certificate_secret not in caplog.text


def test_x509_success_logs_and_auth_repr_do_not_leak_tokens(caplog: pytest.LogCaptureFixture) -> None:
    token_secret = "bearer-token-never-visible"

    def handler(request: httpx2.Request) -> httpx2.Response:
        return (
            _token_response(request, token=token_secret)
            if str(request.url) == _TOKEN_URL
            else _models_response(request)
        )

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with caplog.at_level(logging.DEBUG):
        with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
            assert client.models.list().object == "list"
            assert token_secret not in repr(client._workload_identity_auth)

    assert token_secret not in caplog.text


def test_x509_never_falls_back_to_environment_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    requests: list[httpx2.Request] = []
    monkeypatch.setenv("OPENAI_API_KEY", "api-key-never-used")

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(401, request=request, json={"error": "invalid_grant"})

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OAuthError):
            client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


def test_x509_refuses_exchange_redirects_even_when_transport_follows_them() -> None:
    urls: list[str] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        urls.append(str(request.url))
        return httpx2.Response(302, request=request, headers={"location": "https://other.example/oauth/token"})

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), follow_redirects=True, trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="status 302"):
            client.models.list()

    assert urls == [_TOKEN_URL]


def test_x509_refuses_api_redirects_even_when_transport_follows_them() -> None:
    urls: list[str] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        urls.append(str(request.url))
        if str(request.url) == _TOKEN_URL:
            return _token_response(request)
        return httpx2.Response(302, request=request, headers={"location": "https://other.example/v1/models"})

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), follow_redirects=True, trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(APIStatusError):
            client.models.list()

    assert urls == [_TOKEN_URL, _API_URL]


def test_sync_x509_retries_replayable_401_request_once() -> None:
    requests: list[httpx2.Request] = []
    api_authorizations: list[str] = []
    token_count = 0

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal token_count
        requests.append(request)
        if str(request.url) == _TOKEN_URL:
            token_count += 1
            return _token_response(request, token=f"token-{token_count}")
        api_authorizations.append(request.headers["authorization"])
        return _models_response(request, 401 if token_count == 1 else 200)

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert client.models.list().object == "list"

    assert [str(request.url) for request in requests] == [_TOKEN_URL, _API_URL, _TOKEN_URL, _API_URL]
    assert api_authorizations == ["Bearer token-1", "Bearer token-2"]


async def test_async_x509_retries_replayable_401_request_once() -> None:
    api_authorizations: list[str] = []
    token_count = 0

    async def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal token_count
        if str(request.url) == _TOKEN_URL:
            token_count += 1
            return _token_response(request, token=f"token-{token_count}")
        api_authorizations.append(request.headers["authorization"])
        return _models_response(request, 401 if token_count == 1 else 200)

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert (await client.models.list()).object == "list"

    assert api_authorizations == ["Bearer token-1", "Bearer token-2"]


@pytest.mark.parametrize("seekable", [True, False])
def test_sync_x509_401_retries_only_replayable_uploads(seekable: bool) -> None:
    requests: list[httpx2.Request] = []

    class Upload(io.BytesIO):
        @override
        def seekable(self) -> bool:
            return seekable

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        if str(request.url) == _TOKEN_URL:
            return _token_response(request, token=f"token-{len(requests)}")
        return httpx2.Response(401, request=request, json={"error": {"message": "unauthorized"}})

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(APIStatusError):
            client.files.create(file=("document.txt", Upload(b"contents")), purpose="assistants")

    assert len(requests) == (4 if seekable else 2)


def test_sync_x509_rewinds_seekable_request_stream_to_its_original_position() -> None:
    request_bodies: list[bytes] = []
    token_count = 0

    class StreamingTransport(httpx2.BaseTransport):
        @override
        def handle_request(self, request: httpx2.Request) -> httpx2.Response:
            nonlocal token_count
            if str(request.url) == _TOKEN_URL:
                token_count += 1
                return _token_response(request, token=f"token-{token_count}")

            request_bodies.append(b"".join(cast(Iterable[bytes], request.stream)))
            return _models_response(request, 401 if token_count == 1 else 200)

    stream = io.BytesIO(b"prefix-body")
    stream.seek(len(b"prefix-"))
    request = httpx2.Request(
        "POST",
        _API_URL,
        content=stream,
        headers={"authorization": f"Bearer {WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER}"},
    )
    http_client = httpx2.Client(transport=StreamingTransport(), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        response = client._send_request(request, stream=False)

    assert response.status_code == 200
    assert request_bodies == [b"body", b"body"]


@pytest.mark.parametrize("seekable", [True, False])
async def test_async_x509_401_retries_only_replayable_uploads(seekable: bool) -> None:
    requests: list[httpx2.Request] = []

    class Upload(io.BytesIO):
        @override
        def seekable(self) -> bool:
            return seekable

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        if str(request.url) == _TOKEN_URL:
            return _token_response(request, token=f"token-{len(requests)}")
        return httpx2.Response(401, request=request, json={"error": {"message": "unauthorized"}})

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(APIStatusError):
            await client.files.create(file=("document.txt", Upload(b"contents")), purpose="assistants")

    assert len(requests) == (4 if seekable else 2)


def test_x509_does_not_retry_one_shot_sync_request_stream() -> None:
    def chunks() -> Iterator[bytes]:
        yield b"body"

    request = httpx2.Request("POST", _API_URL, content=chunks())
    assert not x509_auth._is_replayable_request(request)


async def test_x509_does_not_retry_one_shot_async_request_stream() -> None:
    async def chunks() -> AsyncIterator[bytes]:
        yield b"body"

    request = httpx2.Request("POST", _API_URL, content=chunks())
    assert not x509_auth._is_replayable_request(request)


@pytest.mark.skipif(os.getenv("OPENAI_TEST_LEGACY_HTTPX") != "1", reason="requires legacy HTTPX compatibility lane")
def test_sync_x509_reuses_legacy_httpx_transport() -> None:
    httpx = cast(Any, importlib.import_module("httpx"))
    requests: list[Any] = []

    def handler(request: Any) -> Any:
        requests.append(request)
        if str(request.url) == _TOKEN_URL:
            return httpx.Response(200, request=request, json={"access_token": "legacy-token", "expires_in": 3600})
        return httpx.Response(200, request=request, json={"object": "list", "data": []})

    http_client = httpx.Client(transport=httpx.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert client.models.list().object == "list"

    assert [str(request.url) for request in requests] == [_TOKEN_URL, _API_URL]


@pytest.mark.skipif(os.getenv("OPENAI_TEST_LEGACY_HTTPX") != "1", reason="requires legacy HTTPX compatibility lane")
async def test_async_x509_reuses_legacy_httpx_transport() -> None:
    httpx = cast(Any, importlib.import_module("httpx"))
    requests: list[Any] = []

    async def handler(request: Any) -> Any:
        requests.append(request)
        if str(request.url) == _TOKEN_URL:
            return httpx.Response(200, request=request, json={"access_token": "legacy-token", "expires_in": 3600})
        return httpx.Response(200, request=request, json={"object": "list", "data": []})

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert (await client.models.list()).object == "list"

    assert [str(request.url) for request in requests] == [_TOKEN_URL, _API_URL]


def test_x509_copy_reuses_effective_transport_and_preserves_identity() -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        return _token_response(request) if str(request.url) == _TOKEN_URL else _models_response(request)

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    client = OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0)
    copied = client.with_options()
    assert copied._client is http_client
    assert copied.workload_identity == client.workload_identity
    assert copied.models.list().object == "list"
    client.close()


@pytest.mark.parametrize("example", ["x509_workload_identity.py", "x509_workload_identity_async.py"])
@pytest.mark.parametrize("mode", ["api_key", "x509"])
def test_x509_rollout_examples_construct_clients_without_network(
    example: str, mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("OPENAI_AUTH_MODE", mode)
    monkeypatch.setenv("OPENAI_API_KEY", "example-api-key")
    monkeypatch.setenv("OPENAI_IDENTITY_PROVIDER_ID", "idp_example")
    monkeypatch.setenv("OPENAI_SERVICE_ACCOUNT_ID", "svc_acct_example")
    monkeypatch.setenv("OPENAI_MTLS_CA_BUNDLE", str(_MTLS_FIXTURES / "root.pem"))
    monkeypatch.setenv("OPENAI_MTLS_CERTIFICATE_CHAIN", str(_MTLS_FIXTURES / "client-chain.pem"))
    monkeypatch.setenv("OPENAI_MTLS_PRIVATE_KEY", str(_MTLS_FIXTURES / "client.key"))

    namespace = runpy.run_path(str(Path(__file__).parent.parent / "examples" / example))
    create_client = cast(Callable[[], OpenAI | AsyncOpenAI], namespace["create_client"])
    client = create_client()
    if mode == "x509":
        assert client.workload_identity == {
            "type": "x509",
            "identity_provider_id": "idp_example",
            "service_account_id": "svc_acct_example",
        }
        assert client._client.follow_redirects is False
    else:
        assert client.api_key == "example-api-key"

    if isinstance(client, OpenAI):
        client.close()
    else:
        anyio.run(client.close)
