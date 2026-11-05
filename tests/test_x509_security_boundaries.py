from __future__ import annotations

import json
from typing import Any, Callable, cast
from contextvars import ContextVar
from typing_extensions import override

import anyio
import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, OpenAIError
from openai.auth import X509WorkloadIdentity, x509_workload_identity
from openai.lib.azure import AzureOpenAI, AsyncAzureOpenAI
from openai.auth._x509 import is_x509_workload_identity

_TOKEN_URL = "https://mtls.auth.openai.com/oauth/token"
_API_URL = "https://mtls.api.openai.com/v1/models"
_TARGET_CREDENTIAL_HEADERS = [
    "api-key",
    "API-Key",
    "api_key",
    "API_KEY",
    "X-API-Key",
    "x-aPi-kEy",
    "x_api_key",
    "X_API_KEY",
    "X_ApI-Key",
    "x-aPi_keY",
    "Proxy-Authorization",
    "proxy-authorization",
    "proxy_authorization",
    "PROXY_AUTHORIZATION",
]


def _identity() -> X509WorkloadIdentity:
    return x509_workload_identity(identity_provider_id="idp_original", service_account_id="svc_original")


def _mutate_identity(identity: X509WorkloadIdentity, field: str, value: object) -> None:
    if field == "identity_provider_id":
        assert isinstance(value, str)
        identity["identity_provider_id"] = value
    elif field == "service_account_id":
        assert isinstance(value, str)
        identity["service_account_id"] = value
    else:
        assert field == "refresh_buffer_seconds"
        assert isinstance(value, float)
        identity["refresh_buffer_seconds"] = value


def _response(request: httpx2.Request) -> httpx2.Response:
    if str(request.url) == _TOKEN_URL:
        return httpx2.Response(200, request=request, json={"access_token": "trusted-token", "expires_in": 3600})
    return httpx2.Response(200, request=request, json={"object": "list", "data": []})


@pytest.mark.parametrize("token_type", ["Basic", "MAC", "DPoP", "", None, 42])
def test_sync_x509_rejects_non_bearer_token_types_before_caching(token_type: object) -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(
            200,
            request=request,
            json={"access_token": "trusted-token", "expires_in": 3600, "token_type": token_type},
        )

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="Bearer token type"):
            client.models.list()
        assert client._workload_identity_auth is not None
        assert client._workload_identity_auth._cached_token is None

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


@pytest.mark.parametrize("token_type", ["Basic", "MAC", "DPoP", "", None, 42])
async def test_async_x509_rejects_non_bearer_token_types_before_caching(token_type: object) -> None:
    requests: list[httpx2.Request] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(
            200,
            request=request,
            json={"access_token": "trusted-token", "expires_in": 3600, "token_type": token_type},
        )

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="Bearer token type"):
            await client.models.list()
        assert client._workload_identity_auth is not None
        assert client._workload_identity_auth._cached_token is None

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


_UNSAFE_ACCESS_TOKENS = [
    "trusted\r\nInjected: secret",
    "trusted\nInjected: secret",
    "trusted\x00token",
    "trusted\ttoken",
    "trusted token",
    " trusted-token",
    "trusted-token ",
    "trusted-\u00e9-token",
    "trusted,token",
    "trusted=token",
]


@pytest.mark.parametrize("access_token", _UNSAFE_ACCESS_TOKENS)
def test_sync_x509_rejects_unsafe_access_tokens_before_caching(access_token: str) -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json={"access_token": access_token, "expires_in": 3600})

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="valid Bearer access_token"):
            client.models.list()
        assert client._workload_identity_auth is not None
        assert client._workload_identity_auth._cached_token is None

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


@pytest.mark.parametrize("access_token", _UNSAFE_ACCESS_TOKENS)
async def test_async_x509_rejects_unsafe_access_tokens_before_caching(access_token: str) -> None:
    requests: list[httpx2.Request] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json={"access_token": access_token, "expires_in": 3600})

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="valid Bearer access_token"):
            await client.models.list()
        assert client._workload_identity_auth is not None
        assert client._workload_identity_auth._cached_token is None

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


@pytest.mark.parametrize("token_type", ["Bearer", "bearer", "BEARER"])
def test_sync_x509_accepts_explicit_bearer_token_types(token_type: str) -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        if str(request.url) == _TOKEN_URL:
            return httpx2.Response(
                200,
                request=request,
                json={"access_token": "safe.jwt_token~+/==", "expires_in": 3600, "token_type": token_type},
            )
        assert request.headers["Authorization"] == "Bearer safe.jwt_token~+/=="
        return _response(request)

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert client.models.list().object == "list"


@pytest.mark.parametrize("token_type", ["Bearer", "bearer", "BEARER"])
async def test_async_x509_accepts_explicit_bearer_token_types(token_type: str) -> None:
    async def handler(request: httpx2.Request) -> httpx2.Response:
        if str(request.url) == _TOKEN_URL:
            return httpx2.Response(
                200,
                request=request,
                json={"access_token": "safe.jwt_token~+/==", "expires_in": 3600, "token_type": token_type},
            )
        assert request.headers["Authorization"] == "Bearer safe.jwt_token~+/=="
        return _response(request)

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert (await client.models.list()).object == "list"


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
@pytest.mark.parametrize("base_url", ["http://attacker.invalid/v1", "ftp://attacker.invalid/v1"])
def test_x509_constructor_rejects_insecure_api_base(
    client_type: type[OpenAI] | type[AsyncOpenAI], base_url: str
) -> None:
    with pytest.raises(OpenAIError, match="HTTPS"):
        client_type(workload_identity=_identity(), base_url=base_url)


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
def test_x509_constructor_rejects_insecure_environment_base(
    client_type: type[OpenAI] | type[AsyncOpenAI], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("OPENAI_BASE_URL", "http://attacker.invalid/v1")
    with pytest.raises(OpenAIError, match="HTTPS"):
        client_type(workload_identity=_identity())


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
def test_x509_base_url_setter_rejects_insecure_origin(client_type: type[OpenAI] | type[AsyncOpenAI]) -> None:
    client = client_type(workload_identity=_identity())
    try:
        original_url = client.base_url
        with pytest.raises(OpenAIError, match="HTTPS"):
            client.base_url = "http://attacker.invalid/v1"
        assert client.base_url == original_url
    finally:
        if isinstance(client, OpenAI):
            client.close()
        else:
            anyio.run(client.close)


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
def test_api_key_clients_keep_supported_plaintext_local_origins(client_type: type[OpenAI] | type[AsyncOpenAI]) -> None:
    client = client_type(api_key="local-api-key", base_url="http://localhost:8080/v1")
    try:
        assert str(client.base_url) == "http://localhost:8080/v1/"
    finally:
        if isinstance(client, OpenAI):
            client.close()
        else:
            anyio.run(client.close)


@pytest.mark.parametrize("method", ["copy", "with_options"])
def test_sync_copy_rejects_insecure_x509_api_base(method: str) -> None:
    with OpenAI(workload_identity=_identity()) as client:
        with pytest.raises(OpenAIError, match="HTTPS"):
            getattr(client, method)(base_url="http://attacker.invalid/v1")

    with OpenAI(api_key="local-api-key", base_url="http://localhost:8080/v1") as client:
        with pytest.raises(OpenAIError, match="HTTPS"):
            getattr(client, method)(workload_identity=_identity())


@pytest.mark.parametrize("method", ["copy", "with_options"])
async def test_async_copy_rejects_insecure_x509_api_base(method: str) -> None:
    async with AsyncOpenAI(workload_identity=_identity()) as client:
        with pytest.raises(OpenAIError, match="HTTPS"):
            getattr(client, method)(base_url="http://attacker.invalid/v1")

    async with AsyncOpenAI(api_key="local-api-key", base_url="http://localhost:8080/v1") as client:
        with pytest.raises(OpenAIError, match="HTTPS"):
            getattr(client, method)(workload_identity=_identity())


_ATTACKER_URLS = [
    "http://attacker.invalid/v1/models",
    "https://attacker.invalid/v1/models",
    "https://mtls.api.openai.com.@attacker.invalid/v1/models",
    "https://mtls.api.openai.com\\@attacker.invalid/v1/models",
    "https://mtls.api.openai.com:8443/v1/models",
]


@pytest.mark.parametrize("url", _ATTACKER_URLS)
def test_sync_x509_rejects_attacker_origin_before_token_exchange(url: str) -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="HTTPS|origin|credentials"):
            client.get(url, cast_to=object)

    assert requests == []


@pytest.mark.parametrize("url", _ATTACKER_URLS)
async def test_async_x509_rejects_attacker_origin_before_token_exchange(url: str) -> None:
    requests: list[httpx2.Request] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="HTTPS|origin|credentials"):
            await client.get(url, cast_to=object)

    assert requests == []


def test_sync_x509_rejects_subclass_mutated_origin_before_token_exchange() -> None:
    requests: list[httpx2.Request] = []

    class RedirectingOpenAI(OpenAI):
        @override
        def _prepare_request(self, request: httpx2.Request) -> None:
            request.url = httpx2.URL("https://subclass-attacker.invalid/v1/models")

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with RedirectingOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="origin"):
            client.models.list()

    assert requests == []


async def test_async_x509_rejects_subclass_mutated_origin_before_token_exchange() -> None:
    requests: list[httpx2.Request] = []

    class RedirectingAsyncOpenAI(AsyncOpenAI):
        @override
        async def _prepare_request(self, request: httpx2.Request) -> None:
            request.url = httpx2.URL("https://subclass-attacker.invalid/v1/models")

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with RedirectingAsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="origin"):
            await client.models.list()

    assert requests == []


def test_sync_x509_token_exchange_skips_caller_hooks_and_preserves_api_hooks() -> None:
    requests: list[httpx2.Request] = []
    hooked_urls: list[str] = []

    def hook(request: httpx2.Request) -> None:
        hooked_urls.append(str(request.url))
        request.headers["X-Request-ID"] = "caller-request-id"
        request.headers["Cookie"] = "session=caller-cookie"

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    http_client = httpx2.Client(
        transport=httpx2.MockTransport(handler), event_hooks={"request": [hook]}, trust_env=False
    )
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert client.models.list().object == "list"

    assert hooked_urls == [_API_URL]
    assert requests[0].headers.get("Authorization") is None
    assert requests[0].headers.get("X-Request-ID") is None
    assert requests[0].headers.get("Cookie") is None
    assert requests[1].headers["X-Request-ID"] == "caller-request-id"
    assert requests[1].headers["Cookie"] == "session=caller-cookie"


async def test_async_x509_token_exchange_skips_caller_hooks_and_preserves_api_hooks() -> None:
    requests: list[httpx2.Request] = []
    hooked_urls: list[str] = []

    async def hook(request: httpx2.Request) -> None:
        hooked_urls.append(str(request.url))
        request.headers["X-Request-ID"] = "caller-request-id"
        request.headers["Cookie"] = "session=caller-cookie"

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    http_client = httpx2.AsyncClient(
        transport=httpx2.MockTransport(handler), event_hooks={"request": [hook]}, trust_env=False
    )
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert (await client.models.list()).object == "list"

    assert hooked_urls == [_API_URL]
    assert requests[0].headers.get("Authorization") is None
    assert requests[0].headers.get("X-Request-ID") is None
    assert requests[0].headers.get("Cookie") is None
    assert requests[1].headers["X-Request-ID"] == "caller-request-id"
    assert requests[1].headers["Cookie"] == "session=caller-cookie"


@pytest.mark.parametrize("header", _TARGET_CREDENTIAL_HEADERS)
@pytest.mark.parametrize("source", ["client", "request"])
def test_sync_x509_rejects_target_credentials_before_token_exchange(header: str, source: str) -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    http_client = httpx2.Client(
        transport=httpx2.MockTransport(handler),
        headers={header: "provider-secret"} if source == "client" else None,
        trust_env=False,
    )
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="API.key"):
            if source == "request":
                client.models.list(extra_headers={header: "provider-secret"})
            else:
                client.models.list()

    assert requests == []


@pytest.mark.parametrize("header", _TARGET_CREDENTIAL_HEADERS)
@pytest.mark.parametrize("source", ["client", "request"])
async def test_async_x509_rejects_target_credentials_before_token_exchange(header: str, source: str) -> None:
    requests: list[httpx2.Request] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    http_client = httpx2.AsyncClient(
        transport=httpx2.MockTransport(handler),
        headers={header: "provider-secret"} if source == "client" else None,
        trust_env=False,
    )
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="API.key"):
            if source == "request":
                await client.models.list(extra_headers={header: "provider-secret"})
            else:
                await client.models.list()

    assert requests == []


@pytest.mark.parametrize("header", _TARGET_CREDENTIAL_HEADERS)
def test_sync_x509_rejects_hook_injected_target_credentials_at_transport(header: str) -> None:
    requests: list[httpx2.Request] = []

    def hook(request: httpx2.Request) -> None:
        request.headers[header] = "provider-secret"

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    http_client = httpx2.Client(
        transport=httpx2.MockTransport(handler), event_hooks={"request": [hook]}, trust_env=False
    )
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="API.key"):
            client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


@pytest.mark.parametrize("header", _TARGET_CREDENTIAL_HEADERS)
async def test_async_x509_rejects_hook_injected_target_credentials_at_transport(header: str) -> None:
    requests: list[httpx2.Request] = []

    async def hook(request: httpx2.Request) -> None:
        request.headers[header] = "provider-secret"

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    http_client = httpx2.AsyncClient(
        transport=httpx2.MockTransport(handler), event_hooks={"request": [hook]}, trust_env=False
    )
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="API.key"):
            await client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


@pytest.mark.parametrize("mutation", ["origin", "plaintext", "authorization", "remove_authorization"])
def test_sync_x509_rejects_hook_mutated_api_request_at_transport(mutation: str) -> None:
    requests: list[httpx2.Request] = []

    def hook(request: httpx2.Request) -> None:
        if mutation == "authorization":
            request.headers["Authorization"] = "Bearer hook-override"
        elif mutation == "remove_authorization":
            del request.headers["Authorization"]
        elif mutation == "plaintext":
            request.url = httpx2.URL("http://hook-attacker.invalid/v1/models")
        else:
            request.url = httpx2.URL("https://hook-attacker.invalid/v1/models")

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    http_client = httpx2.Client(
        transport=httpx2.MockTransport(handler), event_hooks={"request": [hook]}, trust_env=False
    )
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="HTTPS|origin|authorization"):
            client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


@pytest.mark.parametrize("mutation", ["origin", "plaintext", "authorization", "remove_authorization"])
async def test_async_x509_rejects_hook_mutated_api_request_at_transport(mutation: str) -> None:
    requests: list[httpx2.Request] = []

    async def hook(request: httpx2.Request) -> None:
        if mutation == "authorization":
            request.headers["Authorization"] = "Bearer hook-override"
        elif mutation == "remove_authorization":
            del request.headers["Authorization"]
        elif mutation == "plaintext":
            request.url = httpx2.URL("http://hook-attacker.invalid/v1/models")
        else:
            request.url = httpx2.URL("https://hook-attacker.invalid/v1/models")

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    http_client = httpx2.AsyncClient(
        transport=httpx2.MockTransport(handler), event_hooks={"request": [hook]}, trust_env=False
    )
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="HTTPS|origin|authorization"):
            await client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


def test_sync_x509_snapshots_original_identity_and_rejects_client_identity_mutation() -> None:
    identity = _identity()
    payloads: list[dict[str, Any]] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        if str(request.url) == _TOKEN_URL:
            payloads.append(json.loads(request.content))
        return _response(request)

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=identity, http_client=http_client, max_retries=0) as client:
        identity["identity_provider_id"] = "idp_attacker"
        identity["service_account_id"] = "svc_attacker"
        assert client.models.list().object == "list"
        assert client.workload_identity is not None
        assert client.workload_identity["identity_provider_id"] == "idp_original"

        client.workload_identity["identity_provider_id"] = "idp_changed"
        with pytest.raises(OpenAIError, match="cannot be changed"):
            client.models.list()

    assert len(payloads) == 1
    assert payloads[0]["identity_provider_id"] == "idp_original"


async def test_async_x509_snapshots_original_identity_and_rejects_client_identity_mutation() -> None:
    identity = _identity()
    payloads: list[dict[str, Any]] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        if str(request.url) == _TOKEN_URL:
            payloads.append(json.loads(request.content))
        return _response(request)

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=identity, http_client=http_client, max_retries=0) as client:
        identity["identity_provider_id"] = "idp_attacker"
        identity["service_account_id"] = "svc_attacker"
        assert (await client.models.list()).object == "list"
        assert client.workload_identity is not None
        assert client.workload_identity["identity_provider_id"] == "idp_original"

        client.workload_identity["identity_provider_id"] = "idp_changed"
        with pytest.raises(OpenAIError, match="cannot be changed"):
            await client.models.list()

    assert len(payloads) == 1
    assert payloads[0]["identity_provider_id"] == "idp_original"


@pytest.mark.parametrize(
    "field,value",
    [
        ("identity_provider_id", "idp_changed"),
        ("service_account_id", "svc_changed"),
        ("refresh_buffer_seconds", float("nan")),
    ],
)
def test_sync_x509_rejects_mutated_cached_identity_before_network(field: str, value: object) -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        client.models.list()
        assert is_x509_workload_identity(client.workload_identity)
        _mutate_identity(client.workload_identity, field, value)
        with pytest.raises(OpenAIError, match="cannot be changed"):
            client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL, _API_URL]


@pytest.mark.parametrize(
    "field,value",
    [
        ("identity_provider_id", "idp_changed"),
        ("service_account_id", "svc_changed"),
        ("refresh_buffer_seconds", float("nan")),
    ],
)
async def test_async_x509_rejects_mutated_cached_identity_before_network(field: str, value: object) -> None:
    requests: list[httpx2.Request] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        await client.models.list()
        assert is_x509_workload_identity(client.workload_identity)
        _mutate_identity(client.workload_identity, field, value)
        with pytest.raises(OpenAIError, match="cannot be changed"):
            await client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL, _API_URL]


def test_sync_x509_preserves_caller_mounts_response_hooks_and_api_cookie_jar() -> None:
    routed: list[str] = []
    hook_hosts: list[str] = []
    tenant_context: ContextVar[str] = ContextVar("tenant", default="missing")
    tenant_context.set("tenant-original")

    def auth_handler(request: httpx2.Request) -> httpx2.Response:
        routed.append("auth:" + str(request.url))
        assert tenant_context.get() == "tenant-original"
        return httpx2.Response(
            200,
            request=request,
            headers={"set-cookie": "auth_poison=secret; Domain=.openai.com; Path=/"},
            json={"access_token": "trusted-token", "expires_in": 3600},
        )

    def api_handler(request: httpx2.Request) -> httpx2.Response:
        routed.append("api:" + str(request.url))
        assert tenant_context.get() == "tenant-original"
        assert "auth_poison" not in request.headers.get("cookie", "")
        return httpx2.Response(
            200,
            request=request,
            headers={"set-cookie": "api_session=trusted; Path=/"},
            json={"object": "list", "data": []},
        )

    def response_hook(response: httpx2.Response) -> None:
        hook_hosts.append(str(response.request.url.host))

    default_transport = httpx2.MockTransport(lambda _: pytest.fail("unexpected default transport"))
    http_client = httpx2.Client(
        transport=default_transport,
        mounts={
            "https://mtls.auth.openai.com": httpx2.MockTransport(auth_handler),
            "https://mtls.api.openai.com": httpx2.MockTransport(api_handler),
        },
        event_hooks={"response": [response_hook]},
        trust_env=False,
    )
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert client.models.list().object == "list"
        assert http_client.cookies.get("api_session") == "trusted"
        assert http_client.cookies.get("auth_poison") is None

    assert routed == ["auth:" + _TOKEN_URL, "api:" + _API_URL]
    assert hook_hosts == ["mtls.api.openai.com"]


async def test_async_x509_preserves_caller_mounts_response_hooks_and_api_cookie_jar() -> None:
    routed: list[str] = []
    hook_hosts: list[str] = []
    tenant_context: ContextVar[str] = ContextVar("tenant", default="missing")
    tenant_context.set("tenant-original")

    async def auth_handler(request: httpx2.Request) -> httpx2.Response:
        routed.append("auth:" + str(request.url))
        assert tenant_context.get() == "tenant-original"
        return httpx2.Response(
            200,
            request=request,
            headers={"set-cookie": "auth_poison=secret; Domain=.openai.com; Path=/"},
            json={"access_token": "trusted-token", "expires_in": 3600},
        )

    async def api_handler(request: httpx2.Request) -> httpx2.Response:
        routed.append("api:" + str(request.url))
        assert tenant_context.get() == "tenant-original"
        assert "auth_poison" not in request.headers.get("cookie", "")
        return httpx2.Response(
            200,
            request=request,
            headers={"set-cookie": "api_session=trusted; Path=/"},
            json={"object": "list", "data": []},
        )

    async def response_hook(response: httpx2.Response) -> None:
        hook_hosts.append(str(response.request.url.host))

    default_transport = httpx2.MockTransport(lambda _: pytest.fail("unexpected default transport"))
    http_client = httpx2.AsyncClient(
        transport=default_transport,
        mounts={
            "https://mtls.auth.openai.com": httpx2.MockTransport(auth_handler),
            "https://mtls.api.openai.com": httpx2.MockTransport(api_handler),
        },
        event_hooks={"response": [response_hook]},
        trust_env=False,
    )
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert (await client.models.list()).object == "list"
        assert http_client.cookies.get("api_session") == "trusted"
        assert http_client.cookies.get("auth_poison") is None

    assert routed == ["auth:" + _TOKEN_URL, "api:" + _API_URL]
    assert hook_hosts == ["mtls.api.openai.com"]


def test_sync_x509_keeps_supported_admin_credentials_separate() -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(
        workload_identity=_identity(),
        admin_api_key="admin-customer-secret",
        http_client=http_client,
        max_retries=0,
    ) as client:
        client.models.list()
        client.get("/organization/projects", cast_to=object, options={"security": {"admin_api_key_auth": True}})
        with pytest.raises(OpenAIError, match="origin"):
            client.get(
                "https://attacker.invalid/organization/projects",
                cast_to=object,
                options={"security": {"admin_api_key_auth": True}},
            )

    assert len(requests) == 3
    assert requests[0].headers.get("Authorization") is None
    assert requests[1].headers["Authorization"] == "Bearer trusted-token"
    assert requests[2].headers["Authorization"] == "Bearer admin-customer-secret"


async def test_async_x509_keeps_supported_admin_credentials_separate() -> None:
    requests: list[httpx2.Request] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(
        workload_identity=_identity(),
        admin_api_key="admin-customer-secret",
        http_client=http_client,
        max_retries=0,
    ) as client:
        await client.models.list()
        await client.get("/organization/projects", cast_to=object, options={"security": {"admin_api_key_auth": True}})
        with pytest.raises(OpenAIError, match="origin"):
            await client.get(
                "https://attacker.invalid/organization/projects",
                cast_to=object,
                options={"security": {"admin_api_key_auth": True}},
            )

    assert len(requests) == 3
    assert requests[0].headers.get("Authorization") is None
    assert requests[1].headers["Authorization"] == "Bearer trusted-token"
    assert requests[2].headers["Authorization"] == "Bearer admin-customer-secret"


@pytest.mark.parametrize("authorization", ["Basic Y3VzdG9tZXI6c2VjcmV0", "Bearer substituted-admin-secret"])
def test_sync_x509_rejects_hook_overriding_separate_admin_authorization(authorization: str) -> None:
    requests: list[httpx2.Request] = []

    def hook(request: httpx2.Request) -> None:
        request.headers["Authorization"] = authorization

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    http_client = httpx2.Client(
        transport=httpx2.MockTransport(handler), event_hooks={"request": [hook]}, trust_env=False
    )
    with OpenAI(
        workload_identity=_identity(),
        admin_api_key="expected-admin-secret",
        http_client=http_client,
        max_retries=0,
    ) as client:
        with pytest.raises(OpenAIError, match="authorization"):
            client.get("/organization/projects", cast_to=object, options={"security": {"admin_api_key_auth": True}})

    assert requests == []


@pytest.mark.parametrize("authorization", ["Basic Y3VzdG9tZXI6c2VjcmV0", "Bearer substituted-admin-secret"])
async def test_async_x509_rejects_hook_overriding_separate_admin_authorization(authorization: str) -> None:
    requests: list[httpx2.Request] = []

    async def hook(request: httpx2.Request) -> None:
        request.headers["Authorization"] = authorization

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return _response(request)

    http_client = httpx2.AsyncClient(
        transport=httpx2.MockTransport(handler), event_hooks={"request": [hook]}, trust_env=False
    )
    async with AsyncOpenAI(
        workload_identity=_identity(),
        admin_api_key="expected-admin-secret",
        http_client=http_client,
        max_retries=0,
    ) as client:
        with pytest.raises(OpenAIError, match="authorization"):
            await client.get(
                "/organization/projects", cast_to=object, options={"security": {"admin_api_key_auth": True}}
            )

    assert requests == []


@pytest.mark.parametrize("client_type", [AzureOpenAI, AsyncAzureOpenAI])
def test_azure_constructors_reject_x509_instead_of_downgrading_to_api_key(
    client_type: type[AzureOpenAI] | type[AsyncAzureOpenAI],
) -> None:
    constructor = cast(Callable[..., object], client_type)
    with pytest.raises(OpenAIError, match="X.509 workload identity is not supported by Azure clients"):
        constructor(
            api_version="2024-02-01",
            api_key="azure-customer-secret",
            azure_endpoint="https://example-resource.azure.openai.com",
            workload_identity=_identity(),
        )


@pytest.mark.parametrize(
    "base_url,url",
    [
        ("https://MTLS.API.OPENAI.COM/v1", "https://mtls.api.openai.com/v1/models"),
        ("https://mtls.api.openai.com:443/v1", "https://MTLS.API.OPENAI.COM/v1/models"),
        ("https://custom.example:8443/v1", "https://custom.example:8443/v1/models"),
    ],
)
def test_sync_x509_accepts_normalized_trusted_origin(base_url: str, url: str) -> None:
    http_client = httpx2.Client(transport=httpx2.MockTransport(_response), trust_env=False)
    with OpenAI(workload_identity=_identity(), base_url=base_url, http_client=http_client, max_retries=0) as client:
        assert client.get(url, cast_to=object) is not None


@pytest.mark.parametrize(
    "base_url,url",
    [
        ("https://MTLS.API.OPENAI.COM/v1", "https://mtls.api.openai.com/v1/models"),
        ("https://mtls.api.openai.com:443/v1", "https://MTLS.API.OPENAI.COM/v1/models"),
        ("https://custom.example:8443/v1", "https://custom.example:8443/v1/models"),
    ],
)
async def test_async_x509_accepts_normalized_trusted_origin(base_url: str, url: str) -> None:
    async def handler(request: httpx2.Request) -> httpx2.Response:
        return _response(request)

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(
        workload_identity=_identity(), base_url=base_url, http_client=http_client, max_retries=0
    ) as client:
        assert await client.get(url, cast_to=object) is not None
