from __future__ import annotations

import io
import json
import time
import asyncio
import threading
from typing import Any, cast
from contextvars import Context
from typing_extensions import override
from concurrent.futures import ThreadPoolExecutor

import httpx2
import pytest

import openai.auth._x509 as x509_auth
from openai import OpenAI, OAuthError, AsyncOpenAI, OpenAIError, APIConnectionError
from openai.auth import X509WorkloadIdentity, x509_workload_identity
from openai.providers import bedrock

_TOKEN_URL = "https://mtls.auth.openai.com/oauth/token"
_API_URL = "https://mtls.api.openai.com/v1/models"
_REGIONAL_MTLS_URLS = {
    "global": "https://mtls.api.openai.com/v1/",
    "us": "https://mtls-us.api.openai.com/v1/",
    "eu": "https://mtls-eu.api.openai.com/v1/",
}


class _RequestlessConnectError(httpx2.ConnectError):
    @property
    @override
    def request(self) -> httpx2.Request:
        raise RuntimeError("The .request property has not been set.")

    @request.setter
    def request(self, request: httpx2.Request) -> None:
        del request
        return None


def _identity() -> X509WorkloadIdentity:
    return x509_workload_identity(identity_provider_id="idp_example", service_account_id="svc_example")


def _response(request: httpx2.Request, *, token: str = "access-token") -> httpx2.Response:
    if str(request.url) == _TOKEN_URL:
        return httpx2.Response(200, request=request, json={"access_token": token, "expires_in": 3600})
    return httpx2.Response(200, request=request, json={"object": "list", "data": []})


def test_sync_x509_ignores_ambient_authorization_without_changing_explicit_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requests: list[httpx2.Request] = []
    monkeypatch.setenv("OPENAI_CUSTOM_HEADERS", "Authorization: Bearer ambient-secret\nX-Custom: retained")
    http_client = httpx2.Client(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert client.models.list().object == "list"

    assert [str(request.url) for request in requests] == [_TOKEN_URL, _API_URL]
    assert requests[-1].headers["Authorization"] == "Bearer access-token"
    assert requests[-1].headers["X-Custom"] == "retained"


@pytest.mark.parametrize("header_name", ["Authorization", "aUtHoRiZaTiOn"])
def test_sync_switch_to_x509_discards_inherited_ambient_authorization(
    monkeypatch: pytest.MonkeyPatch, header_name: str
) -> None:
    requests: list[httpx2.Request] = []
    monkeypatch.setenv("OPENAI_CUSTOM_HEADERS", f"{header_name}: Bearer ambient-secret")
    http_client = httpx2.Client(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

    with OpenAI(api_key="original-api-key", http_client=http_client, max_retries=0) as original:
        original.with_options(workload_identity=_identity()).models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL, _API_URL]
    assert requests[-1].headers["Authorization"] == "Bearer access-token"


@pytest.mark.parametrize("header_name", ["Authorization", "aUtHoRiZaTiOn"])
async def test_async_switch_to_x509_discards_inherited_ambient_authorization(
    monkeypatch: pytest.MonkeyPatch, header_name: str
) -> None:
    requests: list[httpx2.Request] = []
    monkeypatch.setenv("OPENAI_CUSTOM_HEADERS", f"{header_name}: Bearer ambient-secret")
    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

    async with AsyncOpenAI(api_key="original-api-key", http_client=http_client, max_retries=0) as original:
        await original.with_options(workload_identity=_identity()).models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL, _API_URL]
    assert requests[-1].headers["Authorization"] == "Bearer access-token"


@pytest.mark.parametrize("ambient_header", ["authorization", "aUtHoRiZaTiOn"])
def test_sync_switch_to_x509_discards_ambient_authorization_from_an_explicit_intermediate_copy(
    monkeypatch: pytest.MonkeyPatch, ambient_header: str
) -> None:
    requests: list[httpx2.Request] = []
    monkeypatch.setenv("OPENAI_CUSTOM_HEADERS", f"{ambient_header}: Bearer ambient-secret")
    http_client = httpx2.Client(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

    with OpenAI(api_key="original-api-key", http_client=http_client, max_retries=0) as original:
        intermediate = original.with_options(default_headers={"Authorization": "Bearer workload-identity-auth"})
        assert httpx2.Headers(intermediate._custom_headers).get_list("Authorization") == [
            "Bearer workload-identity-auth"
        ]
        copied = intermediate.with_options(workload_identity=_identity())
        assert httpx2.Headers(copied._custom_headers).get_list("Authorization") == ["Bearer workload-identity-auth"]
        assert copied.models.list().object == "list"

    assert [str(request.url) for request in requests] == [_TOKEN_URL, _API_URL]
    assert requests[-1].headers.get_list("Authorization") == ["Bearer access-token"]


@pytest.mark.parametrize("ambient_header", ["authorization", "aUtHoRiZaTiOn"])
async def test_async_switch_to_x509_discards_ambient_authorization_from_an_explicit_intermediate_copy(
    monkeypatch: pytest.MonkeyPatch, ambient_header: str
) -> None:
    requests: list[httpx2.Request] = []
    monkeypatch.setenv("OPENAI_CUSTOM_HEADERS", f"{ambient_header}: Bearer ambient-secret")
    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

    async with AsyncOpenAI(api_key="original-api-key", http_client=http_client, max_retries=0) as original:
        intermediate = original.with_options(default_headers={"Authorization": "Bearer workload-identity-auth"})
        assert httpx2.Headers(intermediate._custom_headers).get_list("Authorization") == [
            "Bearer workload-identity-auth"
        ]
        copied = intermediate.with_options(workload_identity=_identity())
        assert httpx2.Headers(copied._custom_headers).get_list("Authorization") == ["Bearer workload-identity-auth"]
        assert (await copied.models.list()).object == "list"

    assert [str(request.url) for request in requests] == [_TOKEN_URL, _API_URL]
    assert requests[-1].headers.get_list("Authorization") == ["Bearer access-token"]


def test_sync_switch_to_x509_discards_every_mixed_case_ambient_authorization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requests: list[httpx2.Request] = []
    monkeypatch.setenv(
        "OPENAI_CUSTOM_HEADERS", "Authorization: Bearer first-ambient\nAUTHORIZATION: Bearer second-ambient"
    )
    http_client = httpx2.Client(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

    with OpenAI(api_key="original-api-key", http_client=http_client, max_retries=0) as original:
        original.with_options(workload_identity=_identity()).models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL, _API_URL]
    assert requests[-1].headers.get_list("Authorization") == ["Bearer access-token"]


async def test_async_switch_to_x509_discards_every_mixed_case_ambient_authorization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requests: list[httpx2.Request] = []
    monkeypatch.setenv(
        "OPENAI_CUSTOM_HEADERS", "Authorization: Bearer first-ambient\nAUTHORIZATION: Bearer second-ambient"
    )
    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

    async with AsyncOpenAI(api_key="original-api-key", http_client=http_client, max_retries=0) as original:
        await original.with_options(workload_identity=_identity()).models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL, _API_URL]
    assert requests[-1].headers.get_list("Authorization") == ["Bearer access-token"]


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
def test_x509_mode_switch_preserves_explicit_authorization_override(
    client_type: type[OpenAI] | type[AsyncOpenAI], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("OPENAI_CUSTOM_HEADERS", "Authorization: Bearer ambient-secret")
    original = client_type(api_key="original-api-key")
    copied = original.with_options(
        workload_identity=_identity(), default_headers={"Authorization": "Bearer intentional-override"}
    )
    assert copied.default_headers["Authorization"] == "Bearer intentional-override"


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
@pytest.mark.parametrize("header_name", ["Authorization", "authorization", "AUTHORIZATION"])
def test_x509_mode_switch_preserves_inherited_explicit_authorization_override(
    client_type: type[OpenAI] | type[AsyncOpenAI], monkeypatch: pytest.MonkeyPatch, header_name: str
) -> None:
    monkeypatch.setenv("OPENAI_CUSTOM_HEADERS", "Authorization: Bearer ambient-secret")
    original = client_type(api_key="original-api-key", default_headers={header_name: "Bearer intentional-override"})
    copied = original.with_options(workload_identity=_identity())
    assert httpx2.Headers(copied._custom_headers).get_list("authorization") == ["Bearer intentional-override"]


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
@pytest.mark.parametrize("header_option", ["default_headers", "set_default_headers"])
def test_x509_mode_switch_preserves_explicit_override_matching_ambient_authorization(
    client_type: type[OpenAI] | type[AsyncOpenAI], monkeypatch: pytest.MonkeyPatch, header_option: str
) -> None:
    monkeypatch.setenv("OPENAI_CUSTOM_HEADERS", "Authorization: Bearer ambient-secret")
    original = client_type(api_key="original-api-key")
    headers = {"Authorization": "Bearer ambient-secret"}
    explicitly_overridden = (
        original.with_options(default_headers=headers)
        if header_option == "default_headers"
        else original.with_options(set_default_headers=headers)
    )

    copied = explicitly_overridden.with_options(workload_identity=_identity())

    assert httpx2.Headers(copied._custom_headers).get_list("authorization") == ["Bearer ambient-secret"]


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
def test_x509_mode_switch_discards_ambient_authorization_after_intermediate_copy(
    client_type: type[OpenAI] | type[AsyncOpenAI], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("OPENAI_CUSTOM_HEADERS", "Authorization: Bearer ambient-secret")
    original = client_type(api_key="original-api-key")
    copied = original.with_options(timeout=2).with_options(workload_identity=_identity())
    assert not any(name.lower() == "authorization" for name in copied._custom_headers)


async def test_async_x509_ignores_ambient_authorization_without_changing_explicit_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requests: list[httpx2.Request] = []
    monkeypatch.setenv("OPENAI_CUSTOM_HEADERS", "aUtHoRiZaTiOn: Bearer ambient-secret\nX-Custom: retained")
    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert (await client.models.list()).object == "list"

    assert [str(request.url) for request in requests] == [_TOKEN_URL, _API_URL]
    assert requests[-1].headers["Authorization"] == "Bearer access-token"
    assert requests[-1].headers["X-Custom"] == "retained"


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
@pytest.mark.parametrize(("region", "expected_url"), _REGIONAL_MTLS_URLS.items())
def test_x509_data_residency_uses_confirmed_regional_mtls_endpoints(
    client_type: type[OpenAI] | type[AsyncOpenAI], region: str, expected_url: str
) -> None:
    client = client_type(workload_identity=_identity(), data_residency=cast(Any, region))
    assert str(client.base_url) == expected_url


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
@pytest.mark.parametrize(("region", "expected_url"), _REGIONAL_MTLS_URLS.items())
def test_x509_copy_uses_confirmed_regional_mtls_endpoints(
    client_type: type[OpenAI] | type[AsyncOpenAI], region: str, expected_url: str
) -> None:
    client = client_type(workload_identity=_identity())
    copied = client.with_options(data_residency=cast(Any, region))
    assert str(copied.base_url) == expected_url
    assert str(client.base_url) == _REGIONAL_MTLS_URLS["global"]


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
def test_switching_from_provider_to_regional_x509_uses_the_mtls_endpoint(
    client_type: type[OpenAI] | type[AsyncOpenAI],
) -> None:
    client = client_type(provider=bedrock(region="us-east-1", api_key="bedrock-token"))
    copied = client.with_options(provider=None, workload_identity=_identity(), data_residency="eu")
    assert str(copied.base_url) == _REGIONAL_MTLS_URLS["eu"]


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
@pytest.mark.parametrize("region", ["global", "us", "eu"])
@pytest.mark.parametrize("base_url_mode", ["omitted", "none", "intermediate_none"])
def test_switching_regional_api_key_client_to_x509_preserves_residency(
    client_type: type[OpenAI] | type[AsyncOpenAI], region: str, base_url_mode: str
) -> None:
    original = client_type(api_key="original-api-key", data_residency=cast(Any, region))
    if base_url_mode == "intermediate_none":
        original = original.with_options(base_url=None)
    copied = (
        original.with_options(workload_identity=_identity(), base_url=None)
        if base_url_mode == "none"
        else original.with_options(workload_identity=_identity())
    )
    assert str(copied.base_url) == _REGIONAL_MTLS_URLS[region]
    assert str(copied.with_options(timeout=1).base_url) == _REGIONAL_MTLS_URLS[region]


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
@pytest.mark.parametrize("region", ["global", "us", "eu"])
@pytest.mark.parametrize("base_url_mode", ["omitted", "none", "intermediate_none"])
def test_switching_regional_x509_client_to_api_key_preserves_residency(
    client_type: type[OpenAI] | type[AsyncOpenAI], region: str, base_url_mode: str
) -> None:
    original = client_type(workload_identity=_identity(), data_residency=cast(Any, region))
    if base_url_mode == "intermediate_none":
        original = original.with_options(base_url=None)
    copied = (
        original.with_options(api_key="replacement-api-key", base_url=None)
        if base_url_mode == "none"
        else original.with_options(api_key="replacement-api-key")
    )
    expected_host = "api.openai.com" if region == "global" else f"{region}.api.openai.com"
    assert str(copied.base_url) == f"https://{expected_host}/v1/"
    assert str(copied.with_options(timeout=1).base_url) == f"https://{expected_host}/v1/"


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
def test_authentication_switch_preserves_explicit_custom_origin(
    client_type: type[OpenAI] | type[AsyncOpenAI],
) -> None:
    original = client_type(api_key="original-api-key", base_url="https://private.example/v1")
    copied = original.with_options(workload_identity=_identity())
    assert str(copied.base_url) == "https://private.example/v1/"


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
def test_x509_rejects_data_residency_without_a_confirmed_mtls_endpoint(
    client_type: type[OpenAI] | type[AsyncOpenAI],
) -> None:
    with pytest.raises(OpenAIError, match="mTLS endpoint"):
        client_type(workload_identity=_identity(), data_residency="ae")

    client = client_type(workload_identity=_identity())
    with pytest.raises(OpenAIError, match="mTLS endpoint"):
        client.with_options(data_residency="ae")


@pytest.mark.parametrize("headers", [{"x-should-retry": "false"}, {"retry-after-ms": "120001"}])
def test_sync_x509_token_exchange_honors_server_retry_refusals(headers: dict[str, str]) -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(503, request=request, headers=headers)

    with OpenAI(
        workload_identity=_identity(), http_client=httpx2.Client(transport=httpx2.MockTransport(handler)), max_retries=2
    ) as client:
        with pytest.raises(OpenAIError, match="503"):
            client.models.list()

    assert len(requests) == 1


@pytest.mark.parametrize("headers", [{"x-should-retry": "false"}, {"retry-after-ms": "120001"}])
async def test_async_x509_token_exchange_honors_server_retry_refusals(headers: dict[str, str]) -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(503, request=request, headers=headers)

    async with AsyncOpenAI(
        workload_identity=_identity(),
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler)),
        max_retries=2,
    ) as client:
        with pytest.raises(OpenAIError, match="503"):
            await client.models.list()

    assert len(requests) == 1


def test_sync_x509_honors_millisecond_retry_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    delays: list[float] = []
    attempts = 0
    monkeypatch.setattr(x509_auth.time, "sleep", delays.append)

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal attempts
        if str(request.url) == _TOKEN_URL:
            attempts += 1
            if attempts == 1:
                return httpx2.Response(429, request=request, headers={"retry-after-ms": "250"})
        return _response(request)

    with OpenAI(
        workload_identity=_identity(), http_client=httpx2.Client(transport=httpx2.MockTransport(handler))
    ) as client:
        assert client.models.list().object == "list"

    assert delays == [0.25]


async def test_async_x509_honors_millisecond_retry_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    delays: list[float] = []
    attempts = 0

    async def record_sleep(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr(x509_auth.anyio, "sleep", record_sleep)

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal attempts
        if str(request.url) == _TOKEN_URL:
            attempts += 1
            if attempts == 1:
                return httpx2.Response(429, request=request, headers={"retry-after-ms": "250"})
        return _response(request)

    async with AsyncOpenAI(
        workload_identity=_identity(), http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
    ) as client:
        assert (await client.models.list()).object == "list"

    assert delays == [0.25]


@pytest.mark.parametrize("status_code", [418, 425])
def test_sync_x509_honors_explicit_server_retry_requests(monkeypatch: pytest.MonkeyPatch, status_code: int) -> None:
    def no_sleep(_delay: float) -> None:
        return None

    monkeypatch.setattr(x509_auth.time, "sleep", no_sleep)
    attempts = 0

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal attempts
        if str(request.url) == _TOKEN_URL:
            attempts += 1
            if attempts == 1:
                return httpx2.Response(status_code, request=request, headers={"x-should-retry": "true"})
        return _response(request)

    with OpenAI(
        workload_identity=_identity(), http_client=httpx2.Client(transport=httpx2.MockTransport(handler))
    ) as client:
        assert client.models.list().object == "list"

    assert attempts == 2


@pytest.mark.parametrize("status_code", [418, 425])
async def test_async_x509_honors_explicit_server_retry_requests(
    monkeypatch: pytest.MonkeyPatch, status_code: int
) -> None:
    async def no_sleep(_delay: float) -> None:
        return None

    monkeypatch.setattr(x509_auth.anyio, "sleep", no_sleep)
    attempts = 0

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal attempts
        if str(request.url) == _TOKEN_URL:
            attempts += 1
            if attempts == 1:
                return httpx2.Response(status_code, request=request, headers={"x-should-retry": "true"})
        return _response(request)

    async with AsyncOpenAI(
        workload_identity=_identity(), http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
    ) as client:
        assert (await client.models.list()).object == "list"

    assert attempts == 2


def test_sync_x509_client_copies_keep_authentication_caches_independent() -> None:
    requests: list[httpx2.Request] = []
    http_client = httpx2.Client(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        client.models.list()
        copied = client.with_options(timeout=1)
        sibling = client.with_options(timeout=2)
        assert client._workload_identity_auth is not None
        assert copied._workload_identity_auth is not None
        assert sibling._workload_identity_auth is not None
        assert copied._workload_identity_auth is not client._workload_identity_auth
        assert sibling._workload_identity_auth is not client._workload_identity_auth
        assert sibling._workload_identity_auth is not copied._workload_identity_auth
        copied.models.list()
        sibling.models.list()

        copied._workload_identity_auth.invalidate_token("access-token")
        assert copied._workload_identity_auth._cached_token is None
        assert client._workload_identity_auth._cached_token == "access-token"
        assert sibling._workload_identity_auth._cached_token == "access-token"
        copied.models.list()

        changed_identity = x509_workload_identity(identity_provider_id="other", service_account_id="svc_example")
        client.with_options(workload_identity=changed_identity).models.list()

    exchanges = [request for request in requests if str(request.url) == _TOKEN_URL]
    assert len(exchanges) == 5


async def test_async_x509_client_copies_keep_authentication_caches_independent() -> None:
    requests: list[httpx2.Request] = []
    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        await client.models.list()
        copied = client.with_options(timeout=1)
        sibling = client.with_options(timeout=2)
        assert client._workload_identity_auth is not None
        assert copied._workload_identity_auth is not None
        assert sibling._workload_identity_auth is not None
        assert copied._workload_identity_auth is not client._workload_identity_auth
        assert sibling._workload_identity_auth is not client._workload_identity_auth
        assert sibling._workload_identity_auth is not copied._workload_identity_auth
        await copied.models.list()
        await sibling.models.list()

        copied._workload_identity_auth.invalidate_token("access-token")
        assert copied._workload_identity_auth._cached_token is None
        assert client._workload_identity_auth._cached_token == "access-token"
        assert sibling._workload_identity_auth._cached_token == "access-token"
        await copied.models.list()

        changed_identity = x509_workload_identity(identity_provider_id="other", service_account_id="svc_example")
        await client.with_options(workload_identity=changed_identity).models.list()

    exchanges = [request for request in requests if str(request.url) == _TOKEN_URL]
    assert len(exchanges) == 5


@pytest.mark.parametrize("requestless", [False, True])
def test_sync_x509_uses_unexpired_token_when_proactive_refresh_temporarily_fails(requestless: bool) -> None:
    requests: list[httpx2.Request] = []
    exchange_count = 0

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_count
        requests.append(request)
        if str(request.url) == _TOKEN_URL:
            exchange_count += 1
            if exchange_count > 1:
                if requestless:
                    raise _RequestlessConnectError("temporary failure")
                raise httpx2.ConnectError("temporary failure", request=request)
        return _response(request)

    with OpenAI(
        workload_identity=_identity(), http_client=httpx2.Client(transport=httpx2.MockTransport(handler)), max_retries=0
    ) as client:
        client.models.list()
        assert client._workload_identity_auth is not None
        client._workload_identity_auth._cached_token_refresh_at_monotonic = time.monotonic() - 1
        assert client.models.list().object == "list"
        client._workload_identity_auth._cached_token_expires_at_monotonic = time.monotonic() - 1
        with pytest.raises(APIConnectionError):
            client.models.list()


@pytest.mark.parametrize("requestless", [False, True])
async def test_async_x509_uses_unexpired_token_when_proactive_refresh_temporarily_fails(requestless: bool) -> None:
    requests: list[httpx2.Request] = []
    exchange_count = 0

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_count
        requests.append(request)
        if str(request.url) == _TOKEN_URL:
            exchange_count += 1
            if exchange_count > 1:
                if requestless:
                    raise _RequestlessConnectError("temporary failure")
                raise httpx2.ConnectError("temporary failure", request=request)
        return _response(request)

    async with AsyncOpenAI(
        workload_identity=_identity(),
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler)),
        max_retries=0,
    ) as client:
        await client.models.list()
        assert client._workload_identity_auth is not None
        client._workload_identity_auth._cached_token_refresh_at_monotonic = time.monotonic() - 1
        assert (await client.models.list()).object == "list"
        client._workload_identity_auth._cached_token_expires_at_monotonic = time.monotonic() - 1
        with pytest.raises(APIConnectionError):
            await client.models.list()


def test_sync_x509_shares_failed_proactive_refresh_across_concurrent_requests(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    exchange_count = 0
    count_lock = threading.Lock()
    fallback_started = threading.Event()
    release_fallback = threading.Event()

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_count
        if str(request.url) == _TOKEN_URL:
            with count_lock:
                exchange_count += 1
                current_count = exchange_count
            if current_count > 1:
                time.sleep(0.025)
                raise httpx2.ConnectError("temporary failure", request=request)
        return _response(request)

    with OpenAI(
        workload_identity=_identity(), http_client=httpx2.Client(transport=httpx2.MockTransport(handler)), max_retries=0
    ) as client:
        client.models.list()
        auth = client._workload_identity_auth
        assert isinstance(auth, x509_auth.SyncX509WorkloadIdentityAuth)
        auth._cached_token_refresh_at_monotonic = time.monotonic() - 1
        fallback = auth._usable_token_after_transient_failure

        def delayed_fallback() -> str | None:
            fallback_started.set()
            assert release_fallback.wait(timeout=5)
            return fallback()

        monkeypatch.setattr(auth, "_usable_token_after_transient_failure", delayed_fallback)

        with ThreadPoolExecutor(max_workers=6) as executor:
            first = executor.submit(client.models.list)
            assert fallback_started.wait(timeout=5)
            waiters = [executor.submit(client.models.list) for _ in range(5)]
            time.sleep(0.05)
            release_fallback.set()
            assert [result.result(timeout=5).object for result in [first, *waiters]] == ["list"] * 6

    assert exchange_count == 2


async def test_async_x509_shares_failed_proactive_refresh_across_concurrent_requests() -> None:
    exchange_count = 0

    async def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_count
        if str(request.url) == _TOKEN_URL:
            exchange_count += 1
            if exchange_count > 1:
                await asyncio.sleep(0.025)
                raise httpx2.ConnectError("temporary failure", request=request)
        return _response(request)

    async with AsyncOpenAI(
        workload_identity=_identity(),
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler)),
        max_retries=0,
    ) as client:
        await client.models.list()
        auth = client._workload_identity_auth
        assert auth is not None
        auth._cached_token_refresh_at_monotonic = time.monotonic() - 1

        async def list_models() -> str:
            return (await client.models.list()).object

        assert await asyncio.gather(*(list_models() for _ in range(6))) == ["list"] * 6

    assert exchange_count == 2


@pytest.mark.parametrize(
    ("status_code", "headers"),
    [(429, {}), (500, {}), (503, {}), (418, {"x-should-retry": "true"}), (425, {"x-should-retry": "true"})],
)
def test_sync_x509_uses_unexpired_token_when_proactive_refresh_gets_transient_status(
    monkeypatch: pytest.MonkeyPatch, status_code: int, headers: dict[str, str]
) -> None:
    def no_sleep(_delay: float) -> None:
        return None

    monkeypatch.setattr(x509_auth.time, "sleep", no_sleep)
    exchange_count = 0

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_count
        if str(request.url) == _TOKEN_URL:
            exchange_count += 1
            if exchange_count > 1:
                return httpx2.Response(status_code, request=request, headers=headers)
        return _response(request)

    with OpenAI(
        workload_identity=_identity(), http_client=httpx2.Client(transport=httpx2.MockTransport(handler)), max_retries=2
    ) as client:
        client.models.list()
        assert client._workload_identity_auth is not None
        client._workload_identity_auth._cached_token_refresh_at_monotonic = time.monotonic() - 1
        assert client.models.list().object == "list"
        client._workload_identity_auth._cached_token_expires_at_monotonic = time.monotonic() - 1
        with pytest.raises(OpenAIError, match=str(status_code)):
            client.models.list()


@pytest.mark.parametrize(
    ("status_code", "headers"),
    [(429, {}), (500, {}), (503, {}), (418, {"x-should-retry": "true"}), (425, {"x-should-retry": "true"})],
)
async def test_async_x509_uses_unexpired_token_when_proactive_refresh_gets_transient_status(
    monkeypatch: pytest.MonkeyPatch, status_code: int, headers: dict[str, str]
) -> None:
    async def no_sleep(_delay: float) -> None:
        return None

    monkeypatch.setattr(x509_auth.anyio, "sleep", no_sleep)
    exchange_count = 0

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_count
        if str(request.url) == _TOKEN_URL:
            exchange_count += 1
            if exchange_count > 1:
                return httpx2.Response(status_code, request=request, headers=headers)
        return _response(request)

    async with AsyncOpenAI(
        workload_identity=_identity(),
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler)),
        max_retries=2,
    ) as client:
        await client.models.list()
        assert client._workload_identity_auth is not None
        client._workload_identity_auth._cached_token_refresh_at_monotonic = time.monotonic() - 1
        assert (await client.models.list()).object == "list"
        client._workload_identity_auth._cached_token_expires_at_monotonic = time.monotonic() - 1
        with pytest.raises(OpenAIError, match=str(status_code)):
            await client.models.list()


@pytest.mark.parametrize("status_code", [400, 401, 403])
@pytest.mark.parametrize("server_requests_retry", [False, True])
def test_sync_x509_never_falls_back_after_permanent_oauth_rejection(
    status_code: int, server_requests_retry: bool
) -> None:
    exchange_count = 0

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_count
        if str(request.url) == _TOKEN_URL:
            exchange_count += 1
            if exchange_count > 1:
                headers = {"x-should-retry": "true"} if server_requests_retry else {}
                return httpx2.Response(status_code, request=request, headers=headers, json={"error": "invalid_grant"})
        return _response(request)

    with OpenAI(
        workload_identity=_identity(), http_client=httpx2.Client(transport=httpx2.MockTransport(handler)), max_retries=0
    ) as client:
        client.models.list()
        assert client._workload_identity_auth is not None
        client._workload_identity_auth._cached_token_refresh_at_monotonic = time.monotonic() - 1
        with pytest.raises(OAuthError):
            client.models.list()


@pytest.mark.parametrize("status_code", [400, 401, 403])
@pytest.mark.parametrize("server_requests_retry", [False, True])
async def test_async_x509_never_falls_back_after_permanent_oauth_rejection(
    status_code: int, server_requests_retry: bool
) -> None:
    exchange_count = 0

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_count
        if str(request.url) == _TOKEN_URL:
            exchange_count += 1
            if exchange_count > 1:
                headers = {"x-should-retry": "true"} if server_requests_retry else {}
                return httpx2.Response(status_code, request=request, headers=headers, json={"error": "invalid_grant"})
        return _response(request)

    async with AsyncOpenAI(
        workload_identity=_identity(),
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler)),
        max_retries=0,
    ) as client:
        await client.models.list()
        assert client._workload_identity_auth is not None
        client._workload_identity_auth._cached_token_refresh_at_monotonic = time.monotonic() - 1
        with pytest.raises(OAuthError):
            await client.models.list()


@pytest.mark.parametrize("timeout", [0.125, 2.5])
def test_sync_x509_token_exchange_uses_configured_timeout(timeout: float) -> None:
    requests: list[httpx2.Request] = []
    http_client = httpx2.Client(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

    with OpenAI(workload_identity=_identity(), http_client=http_client, timeout=timeout, max_retries=0) as client:
        client.models.list()

    assert requests[0].extensions["timeout"]["connect"] == timeout
    assert requests[0].extensions["timeout"]["read"] == timeout


@pytest.mark.parametrize("timeout", [0.125, 2.5])
async def test_async_x509_token_exchange_uses_configured_timeout(timeout: float) -> None:
    requests: list[httpx2.Request] = []
    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

    async with AsyncOpenAI(
        workload_identity=_identity(), http_client=http_client, timeout=timeout, max_retries=0
    ) as client:
        await client.models.list()

    assert requests[0].extensions["timeout"]["connect"] == timeout
    assert requests[0].extensions["timeout"]["read"] == timeout


class _UnreadableSeekability(io.BytesIO):
    @override
    def seekable(self) -> bool:
        raise io.UnsupportedOperation("seekability metadata unavailable")


def test_sync_x509_still_sends_uploads_when_seekability_inspection_fails() -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        if str(request.url) == _TOKEN_URL:
            return _response(request)
        return httpx2.Response(200, request=request, json={"id": "file_123", "object": "file"})

    with OpenAI(
        workload_identity=_identity(), http_client=httpx2.Client(transport=httpx2.MockTransport(handler)), max_retries=0
    ) as client:
        result = client.files.create(file=("payload.txt", _UnreadableSeekability(b"payload")), purpose="assistants")

    assert result.id == "file_123"
    assert len(requests) == 2


async def test_async_x509_still_sends_uploads_when_seekability_inspection_fails() -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        if str(request.url) == _TOKEN_URL:
            return _response(request)
        return httpx2.Response(200, request=request, json={"id": "file_123", "object": "file"})

    async with AsyncOpenAI(
        workload_identity=_identity(),
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler)),
        max_retries=0,
    ) as client:
        result = await client.files.create(
            file=("payload.txt", _UnreadableSeekability(b"payload")), purpose="assistants"
        )

    assert result.id == "file_123"
    assert len(requests) == 2


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
@pytest.mark.parametrize("field", ["identity_provider_id", "service_account_id"])
@pytest.mark.parametrize("invalid", [True, 42, {"nested": "value"}, ["value"]])
def test_x509_rejects_non_string_identity_identifiers(
    client_type: type[OpenAI] | type[AsyncOpenAI], field: str, invalid: object
) -> None:
    identity = cast(X509WorkloadIdentity, {**_identity(), field: invalid})
    with pytest.raises(OpenAIError, match="identity-provider and service-account IDs"):
        client_type(workload_identity=identity)


@pytest.mark.parametrize("replace_authorization", [False, True])
@pytest.mark.parametrize("overlapping_tokens", [False, True])
def test_sync_x509_pins_concurrent_reconstructed_requests_to_the_correct_identity(
    replace_authorization: bool, overlapping_tokens: bool
) -> None:
    arrived = threading.Barrier(2)
    tokens = (
        {"one": "token", "two": "token.extended"} if overlapping_tokens else {"one": "token-one", "two": "token-two"}
    )

    def handler(request: httpx2.Request) -> httpx2.Response:
        if str(request.url) == _TOKEN_URL:
            identity = json.loads(request.content)["identity_provider_id"]
            return _response(request, token=tokens[identity.rsplit("-", 1)[-1]])
        return _response(request)

    def replace(request: httpx2.Request) -> None:
        if replace_authorization and request.headers.get("Authorization") == f"Bearer {tokens['two']}":
            request.headers["Authorization"] = f"Bearer {tokens['one']}"

    class CrossThreadClient(httpx2.Client):
        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            arrived.wait(timeout=5)
            copied = httpx2.Request(request.method, request.url, headers=dict(request.headers))
            with ThreadPoolExecutor(max_workers=1) as executor:
                return executor.submit(super().send, copied, **kwargs).result()

    transport = CrossThreadClient(transport=httpx2.MockTransport(handler), event_hooks={"request": [replace]})
    clients = [
        OpenAI(
            workload_identity=x509_workload_identity(identity_provider_id=f"idp-{suffix}", service_account_id="svc"),
            http_client=transport,
            max_retries=0,
        )
        for suffix in ("one", "two")
    ]

    with ThreadPoolExecutor(max_workers=2) as executor:
        requests = [executor.submit(client.models.list) for client in clients]
        assert requests[0].result(timeout=5).object == "list"
        if replace_authorization:
            with pytest.raises(OpenAIError, match="authorization cannot be changed"):
                requests[1].result(timeout=5)
        else:
            assert requests[1].result(timeout=5).object == "list"


@pytest.mark.parametrize("replace_authorization", [False, True])
@pytest.mark.parametrize("overlapping_tokens", [False, True])
async def test_async_x509_pins_concurrent_reconstructed_requests_to_the_correct_identity(
    replace_authorization: bool, overlapping_tokens: bool
) -> None:
    arrived = 0
    both_arrived = asyncio.Event()
    tokens = (
        {"one": "token", "two": "token.extended"} if overlapping_tokens else {"one": "token-one", "two": "token-two"}
    )

    def handler(request: httpx2.Request) -> httpx2.Response:
        if str(request.url) == _TOKEN_URL:
            identity = json.loads(request.content)["identity_provider_id"]
            return _response(request, token=tokens[identity.rsplit("-", 1)[-1]])
        return _response(request)

    async def replace(request: httpx2.Request) -> None:
        if replace_authorization and request.headers.get("Authorization") == f"Bearer {tokens['two']}":
            request.headers["Authorization"] = f"Bearer {tokens['one']}"

    class CrossContextClient(httpx2.AsyncClient):
        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            nonlocal arrived
            arrived += 1
            if arrived == 2:
                both_arrived.set()
            await asyncio.wait_for(both_arrived.wait(), timeout=5)
            copied = httpx2.Request(request.method, request.url, headers=dict(request.headers))
            return await Context().run(asyncio.create_task, super().send(copied, **kwargs))

    transport = CrossContextClient(transport=httpx2.MockTransport(handler), event_hooks={"request": [replace]})
    clients = [
        AsyncOpenAI(
            workload_identity=x509_workload_identity(identity_provider_id=f"idp-{suffix}", service_account_id="svc"),
            http_client=transport,
            max_retries=0,
        )
        for suffix in ("one", "two")
    ]

    responses = await asyncio.gather(*(client.models.list() for client in clients), return_exceptions=True)
    first = responses[0]
    assert not isinstance(first, BaseException)
    assert first.object == "list"
    if replace_authorization:
        assert isinstance(responses[1], OpenAIError)
        assert "authorization cannot be changed" in str(responses[1])
    else:
        second = responses[1]
        assert not isinstance(second, BaseException)
        assert second.object == "list"


def _record(requests: list[httpx2.Request], request: httpx2.Request) -> httpx2.Response:
    requests.append(request)
    return _response(request)
