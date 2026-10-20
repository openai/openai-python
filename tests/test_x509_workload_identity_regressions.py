from __future__ import annotations

import io
import asyncio
import threading
from typing import cast, get_args, get_type_hints
from typing_extensions import override
from concurrent.futures import ThreadPoolExecutor

import anyio
import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, OpenAIError, APIStatusError
from openai.auth import X509WorkloadIdentity, x509_workload_identity
from openai._client import WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER
from openai.auth._workload import _WorkloadIdentityAuth

_TOKEN_URL = "https://mtls.auth.openai.com/oauth/token"
_API_URL = "https://mtls.api.openai.com/v1/models"


def _identity() -> X509WorkloadIdentity:
    return x509_workload_identity(identity_provider_id="idp_123", service_account_id="svc_acct_123")


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
def test_x509_auth_initializes_its_typed_common_superclass(client_type: type[OpenAI] | type[AsyncOpenAI]) -> None:
    client = client_type(workload_identity=_identity())
    auth = client._workload_identity_auth

    assert isinstance(auth, _WorkloadIdentityAuth)
    assert auth.workload_identity == _identity()
    assert auth._cached_token is None
    assert auth._follow_redirects is False

    if isinstance(client, OpenAI):
        client.close()
    else:
        anyio.run(client.close)


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
def test_copy_signatures_accept_typed_x509_workload_identities(client_type: type[OpenAI] | type[AsyncOpenAI]) -> None:
    assert X509WorkloadIdentity in get_args(get_type_hints(client_type.copy)["workload_identity"])
    assert X509WorkloadIdentity in get_args(get_type_hints(client_type.with_options)["workload_identity"])


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
@pytest.mark.parametrize(
    "identity",
    [
        {"identity_provider_id": "idp_123", "service_account_id": "svc_acct_123"},
        {"type": "x590", "identity_provider_id": "idp_123", "service_account_id": "svc_acct_123"},
        {},
    ],
)
def test_client_rejects_unrecognized_workload_identity_shapes(
    client_type: type[OpenAI] | type[AsyncOpenAI], identity: dict[str, str]
) -> None:
    with pytest.raises(OpenAIError, match="Invalid `workload_identity` configuration"):
        client_type(workload_identity=cast(X509WorkloadIdentity, identity))


@pytest.mark.parametrize("client_type", [OpenAI, AsyncOpenAI])
@pytest.mark.parametrize("missing_key", ["identity_provider_id", "service_account_id"])
def test_client_rejects_x509_identity_missing_a_required_id(
    client_type: type[OpenAI] | type[AsyncOpenAI], missing_key: str
) -> None:
    identity = {key: value for key, value in _identity().items() if key != missing_key}

    with pytest.raises(OpenAIError, match="requires identity-provider and service-account IDs"):
        client_type(workload_identity=cast(X509WorkloadIdentity, identity))


@pytest.mark.parametrize("method", ["copy", "with_options"])
def test_sync_copy_accepts_an_explicit_x509_identity(method: str) -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        if str(request.url) == _TOKEN_URL:
            return httpx2.Response(200, request=request, json={"access_token": "copied-token", "expires_in": 3600})
        return httpx2.Response(200, request=request, json={"object": "list", "data": []})

    replacement = x509_workload_identity(identity_provider_id="idp_replacement", service_account_id="svc_replacement")
    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        copied = (
            client.copy(workload_identity=replacement)
            if method == "copy"
            else client.with_options(workload_identity=replacement)
        )
        assert copied.workload_identity == replacement
        assert copied._client is http_client
        assert copied.models.list().object == "list"


@pytest.mark.parametrize("method", ["copy", "with_options"])
async def test_async_copy_accepts_an_explicit_x509_identity(method: str) -> None:
    async def handler(request: httpx2.Request) -> httpx2.Response:
        if str(request.url) == _TOKEN_URL:
            return httpx2.Response(200, request=request, json={"access_token": "copied-token", "expires_in": 3600})
        return httpx2.Response(200, request=request, json={"object": "list", "data": []})

    replacement = x509_workload_identity(identity_provider_id="idp_replacement", service_account_id="svc_replacement")
    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        copied = (
            client.copy(workload_identity=replacement)
            if method == "copy"
            else client.with_options(workload_identity=replacement)
        )
        assert copied.workload_identity == replacement
        assert copied._client is http_client
        assert (await copied.models.list()).object == "list"


@pytest.mark.parametrize("method", ["copy", "with_options"])
@pytest.mark.parametrize("base_url", [None, "https://custom.example/v1", "https://api.openai.com/v1"])
def test_sync_copy_can_switch_from_api_key_to_x509_identity(method: str, base_url: str | None) -> None:
    api_authorizations: list[str] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        if str(request.url) == _TOKEN_URL:
            return httpx2.Response(200, request=request, json={"access_token": "switched-token", "expires_in": 3600})
        api_authorizations.append(request.headers["Authorization"])
        return httpx2.Response(200, request=request, json={"object": "list", "data": []})

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(api_key="original-api-key", base_url=base_url, http_client=http_client, max_retries=0) as client:
        copied = (
            client.copy(workload_identity=_identity())
            if method == "copy"
            else client.with_options(workload_identity=_identity())
        )
        assert client.api_key == "original-api-key"
        assert copied.api_key == WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER
        assert str(copied.base_url) == f"{base_url or 'https://mtls.api.openai.com/v1'}/"
        assert copied._client is http_client
        assert copied.models.list().object == "list"

    assert api_authorizations == ["Bearer switched-token"]


@pytest.mark.parametrize("method", ["copy", "with_options"])
@pytest.mark.parametrize("base_url", [None, "https://custom.example/v1", "https://api.openai.com/v1"])
async def test_async_copy_can_switch_from_api_key_to_x509_identity(method: str, base_url: str | None) -> None:
    api_authorizations: list[str] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        if str(request.url) == _TOKEN_URL:
            return httpx2.Response(200, request=request, json={"access_token": "switched-token", "expires_in": 3600})
        api_authorizations.append(request.headers["Authorization"])
        return httpx2.Response(200, request=request, json={"object": "list", "data": []})

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(
        api_key="original-api-key", base_url=base_url, http_client=http_client, max_retries=0
    ) as client:
        copied = (
            client.copy(workload_identity=_identity())
            if method == "copy"
            else client.with_options(workload_identity=_identity())
        )
        assert client.api_key == "original-api-key"
        assert copied.api_key == WORKLOAD_IDENTITY_API_KEY_PLACEHOLDER
        assert str(copied.base_url) == f"{base_url or 'https://mtls.api.openai.com/v1'}/"
        assert copied._client is http_client
        assert (await copied.models.list()).object == "list"

    assert api_authorizations == ["Bearer switched-token"]


@pytest.mark.parametrize("method", ["copy", "with_options"])
@pytest.mark.parametrize("base_url", [None, "https://custom.example/v1", "https://mtls.api.openai.com/v1"])
def test_sync_copy_can_switch_from_x509_identity_to_api_key(method: str, base_url: str | None) -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json={"object": "list", "data": []})

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), base_url=base_url, http_client=http_client, max_retries=0) as client:
        copied = (
            client.copy(api_key="replacement-api-key")
            if method == "copy"
            else client.with_options(api_key="replacement-api-key")
        )
        assert client.workload_identity == _identity()
        assert copied.workload_identity is None
        assert copied.api_key == "replacement-api-key"
        assert str(copied.base_url) == f"{base_url or 'https://api.openai.com/v1'}/"
        assert copied._client is http_client
        assert copied.models.list().object == "list"

    assert len(requests) == 1
    assert requests[0].headers["Authorization"] == "Bearer replacement-api-key"


@pytest.mark.parametrize("method", ["copy", "with_options"])
@pytest.mark.parametrize("base_url", [None, "https://custom.example/v1", "https://mtls.api.openai.com/v1"])
async def test_async_copy_can_switch_from_x509_identity_to_api_key(method: str, base_url: str | None) -> None:
    requests: list[httpx2.Request] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, request=request, json={"object": "list", "data": []})

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(
        workload_identity=_identity(), base_url=base_url, http_client=http_client, max_retries=0
    ) as client:
        copied = (
            client.copy(api_key="replacement-api-key")
            if method == "copy"
            else client.with_options(api_key="replacement-api-key")
        )
        assert client.workload_identity == _identity()
        assert copied.workload_identity is None
        assert copied.api_key == "replacement-api-key"
        assert str(copied.base_url) == f"{base_url or 'https://api.openai.com/v1'}/"
        assert copied._client is http_client
        assert (await copied.models.list()).object == "list"

    assert len(requests) == 1
    assert requests[0].headers["Authorization"] == "Bearer replacement-api-key"


def test_sync_copy_preserves_implicit_base_url_provenance_across_chained_copies() -> None:
    http_client = httpx2.Client(trust_env=False)
    with OpenAI(api_key="original-api-key", http_client=http_client) as client:
        copied = client.copy(timeout=1).copy(workload_identity=_identity())

    assert str(copied.base_url) == "https://mtls.api.openai.com/v1/"


async def test_async_copy_preserves_implicit_base_url_provenance_across_chained_copies() -> None:
    http_client = httpx2.AsyncClient(trust_env=False)
    async with AsyncOpenAI(api_key="original-api-key", http_client=http_client) as client:
        copied = client.copy(timeout=1).copy(workload_identity=_identity())

    assert str(copied.base_url) == "https://mtls.api.openai.com/v1/"


@pytest.mark.parametrize("starts_with_x509", [False, True])
def test_sync_copy_preserves_base_url_assigned_through_setter(starts_with_x509: bool) -> None:
    http_client = httpx2.Client(trust_env=False)
    client = (
        OpenAI(workload_identity=_identity(), http_client=http_client)
        if starts_with_x509
        else OpenAI(api_key="original-api-key", http_client=http_client)
    )
    with client:
        client.base_url = "https://assigned.example/v1"
        same_mode_copy = client.copy(timeout=1)
        copied = (
            same_mode_copy.copy(api_key="replacement-api-key")
            if starts_with_x509
            else same_mode_copy.copy(workload_identity=_identity())
        )

    assert str(same_mode_copy.base_url) == "https://assigned.example/v1/"
    assert str(copied.base_url) == "https://assigned.example/v1/"


@pytest.mark.parametrize("starts_with_x509", [False, True])
async def test_async_copy_preserves_base_url_assigned_through_setter(starts_with_x509: bool) -> None:
    http_client = httpx2.AsyncClient(trust_env=False)
    client = (
        AsyncOpenAI(workload_identity=_identity(), http_client=http_client)
        if starts_with_x509
        else AsyncOpenAI(api_key="original-api-key", http_client=http_client)
    )
    async with client:
        client.base_url = "https://assigned.example/v1"
        same_mode_copy = client.copy(timeout=1)
        copied = (
            same_mode_copy.copy(api_key="replacement-api-key")
            if starts_with_x509
            else same_mode_copy.copy(workload_identity=_identity())
        )

    assert str(same_mode_copy.base_url) == "https://assigned.example/v1/"
    assert str(copied.base_url) == "https://assigned.example/v1/"


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


def test_sync_x509_exchange_does_not_inherit_caller_http_auth() -> None:
    exchange_authorizations: list[str | None] = []
    api_authorizations: list[str | None] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        if str(request.url) == _TOKEN_URL:
            exchange_authorizations.append(request.headers.get("Authorization"))
            return httpx2.Response(200, request=request, json={"access_token": "safe-token", "expires_in": 3600})
        api_authorizations.append(request.headers.get("Authorization"))
        return httpx2.Response(200, request=request, json={"object": "list", "data": []})

    http_client = httpx2.Client(
        transport=httpx2.MockTransport(handler),
        auth=httpx2.BasicAuth("caller", "private-api-credential"),
        trust_env=False,
    )
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert client.models.list().object == "list"

    assert exchange_authorizations == [None]
    assert api_authorizations == ["Bearer safe-token"]


async def test_async_x509_exchange_does_not_inherit_caller_http_auth() -> None:
    exchange_authorizations: list[str | None] = []
    api_authorizations: list[str | None] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        if str(request.url) == _TOKEN_URL:
            exchange_authorizations.append(request.headers.get("Authorization"))
            return httpx2.Response(200, request=request, json={"access_token": "safe-token", "expires_in": 3600})
        api_authorizations.append(request.headers.get("Authorization"))
        return httpx2.Response(200, request=request, json={"object": "list", "data": []})

    http_client = httpx2.AsyncClient(
        transport=httpx2.MockTransport(handler),
        auth=httpx2.BasicAuth("caller", "private-api-credential"),
        trust_env=False,
    )
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert (await client.models.list()).object == "list"

    assert exchange_authorizations == [None]
    assert api_authorizations == ["Bearer safe-token"]


def test_sync_x509_exchange_does_not_inherit_caller_request_state() -> None:
    exchange_headers: list[httpx2.Headers] = []
    api_headers: list[httpx2.Headers] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        if str(request.url) == _TOKEN_URL:
            exchange_headers.append(request.headers)
            return httpx2.Response(200, request=request, json={"access_token": "safe-token", "expires_in": 3600})
        api_headers.append(request.headers)
        return httpx2.Response(200, request=request, json={"object": "list", "data": []})

    http_client = httpx2.Client(
        transport=httpx2.MockTransport(handler),
        headers={
            "Authorization": "Bearer private-api-credential",
            "X-Customer-Metadata": "private-api-metadata",
            "Content-Type": "application/private",
        },
        cookies={"session": "private-cookie"},
        trust_env=False,
    )
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert client.models.list().object == "list"

    assert len(exchange_headers) == 1
    assert exchange_headers[0].get("Authorization") is None
    assert exchange_headers[0].get("X-Customer-Metadata") is None
    assert exchange_headers[0].get("Cookie") is None
    assert exchange_headers[0]["Content-Type"] == "application/json"
    assert len(api_headers) == 1
    assert api_headers[0]["Authorization"] == "Bearer safe-token"
    assert api_headers[0]["X-Customer-Metadata"] == "private-api-metadata"
    assert api_headers[0]["Cookie"] == "session=private-cookie"
    assert api_headers[0]["Content-Type"] == "application/private"


async def test_async_x509_exchange_does_not_inherit_caller_request_state() -> None:
    exchange_headers: list[httpx2.Headers] = []
    api_headers: list[httpx2.Headers] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        if str(request.url) == _TOKEN_URL:
            exchange_headers.append(request.headers)
            return httpx2.Response(200, request=request, json={"access_token": "safe-token", "expires_in": 3600})
        api_headers.append(request.headers)
        return httpx2.Response(200, request=request, json={"object": "list", "data": []})

    http_client = httpx2.AsyncClient(
        transport=httpx2.MockTransport(handler),
        headers={
            "Authorization": "Bearer private-api-credential",
            "X-Customer-Metadata": "private-api-metadata",
            "Content-Type": "application/private",
        },
        cookies={"session": "private-cookie"},
        trust_env=False,
    )
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert (await client.models.list()).object == "list"

    assert len(exchange_headers) == 1
    assert exchange_headers[0].get("Authorization") is None
    assert exchange_headers[0].get("X-Customer-Metadata") is None
    assert exchange_headers[0].get("Cookie") is None
    assert exchange_headers[0]["Content-Type"] == "application/json"
    assert len(api_headers) == 1
    assert api_headers[0]["Authorization"] == "Bearer safe-token"
    assert api_headers[0]["X-Customer-Metadata"] == "private-api-metadata"
    assert api_headers[0]["Cookie"] == "session=private-cookie"
    assert api_headers[0]["Content-Type"] == "application/private"


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


def test_sync_x509_invalidates_rejected_token_without_replaying_one_shot_upload() -> None:
    exchange_calls = 0
    api_authorizations: list[str] = []

    class OneShotUpload(io.BytesIO):
        @override
        def seekable(self) -> bool:
            return False

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_calls
        if str(request.url) == _TOKEN_URL:
            exchange_calls += 1
            return httpx2.Response(
                200, request=request, json={"access_token": f"token-{exchange_calls}", "expires_in": 3600}
            )

        api_authorizations.append(request.headers["Authorization"])
        if exchange_calls == 1:
            return httpx2.Response(401, request=request, json={"error": {"message": "unauthorized"}})
        return httpx2.Response(200, request=request, json={"id": "file_123", "object": "file"})

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(APIStatusError):
            client.files.create(file=("first.txt", OneShotUpload(b"first")), purpose="assistants")
        assert client.files.create(file=("second.txt", OneShotUpload(b"second")), purpose="assistants").id == "file_123"

    assert exchange_calls == 2
    assert api_authorizations == ["Bearer token-1", "Bearer token-2"]


async def test_async_x509_invalidates_rejected_token_without_replaying_one_shot_upload() -> None:
    exchange_calls = 0
    api_authorizations: list[str] = []

    class OneShotUpload(io.BytesIO):
        @override
        def seekable(self) -> bool:
            return False

    async def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_calls
        if str(request.url) == _TOKEN_URL:
            exchange_calls += 1
            return httpx2.Response(
                200, request=request, json={"access_token": f"token-{exchange_calls}", "expires_in": 3600}
            )

        api_authorizations.append(request.headers["Authorization"])
        if exchange_calls == 1:
            return httpx2.Response(401, request=request, json={"error": {"message": "unauthorized"}})
        return httpx2.Response(200, request=request, json={"id": "file_123", "object": "file"})

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(APIStatusError):
            await client.files.create(file=("first.txt", OneShotUpload(b"first")), purpose="assistants")
        uploaded = await client.files.create(file=("second.txt", OneShotUpload(b"second")), purpose="assistants")

    assert uploaded.id == "file_123"
    assert exchange_calls == 2
    assert api_authorizations == ["Bearer token-1", "Bearer token-2"]


def test_sync_x509_rewinds_seekable_multipart_upload_to_its_original_position() -> None:
    upload = io.BytesIO(b"prefix-upload-payload")
    upload.seek(len(b"prefix-"))
    initial_position = upload.tell()
    positions: list[int] = []
    bodies: list[bytes] = []
    exchange_calls = 0

    class ConsumingTransport(httpx2.BaseTransport):
        @override
        def handle_request(self, request: httpx2.Request) -> httpx2.Response:
            nonlocal exchange_calls
            if str(request.url) == _TOKEN_URL:
                exchange_calls += 1
                return httpx2.Response(
                    200, request=request, json={"access_token": f"token-{exchange_calls}", "expires_in": 3600}
                )

            positions.append(upload.tell())
            bodies.append(request.read())
            if exchange_calls == 1:
                return httpx2.Response(401, request=request, json={"error": {"message": "unauthorized"}})
            return httpx2.Response(200, request=request, json={"id": "file_123", "object": "file"})

    http_client = httpx2.Client(transport=ConsumingTransport(), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        uploaded = client.files.create(file=("upload.txt", upload), purpose="assistants")

    assert uploaded.id == "file_123"
    assert positions == [initial_position, initial_position]
    assert len(bodies) == 2 and bodies[0] == bodies[1]
    assert b"upload-payload" in bodies[0]


async def test_async_x509_rewinds_seekable_multipart_upload_to_its_original_position() -> None:
    upload = io.BytesIO(b"prefix-upload-payload")
    upload.seek(len(b"prefix-"))
    initial_position = upload.tell()
    positions: list[int] = []
    bodies: list[bytes] = []
    exchange_calls = 0

    class ConsumingTransport(httpx2.AsyncBaseTransport):
        @override
        async def handle_async_request(self, request: httpx2.Request) -> httpx2.Response:
            nonlocal exchange_calls
            if str(request.url) == _TOKEN_URL:
                exchange_calls += 1
                return httpx2.Response(
                    200, request=request, json={"access_token": f"token-{exchange_calls}", "expires_in": 3600}
                )

            positions.append(upload.tell())
            bodies.append(await request.aread())
            if exchange_calls == 1:
                return httpx2.Response(401, request=request, json={"error": {"message": "unauthorized"}})
            return httpx2.Response(200, request=request, json={"id": "file_123", "object": "file"})

    http_client = httpx2.AsyncClient(transport=ConsumingTransport(), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        uploaded = await client.files.create(file=("upload.txt", upload), purpose="assistants")

    assert uploaded.id == "file_123"
    assert positions == [initial_position, initial_position]
    assert len(bodies) == 2 and bodies[0] == bodies[1]
    assert b"upload-payload" in bodies[0]


def test_sync_x509_invalidates_a_rejected_replay_token() -> None:
    exchange_calls = 0
    api_authorizations: list[str] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_calls
        if str(request.url) == _TOKEN_URL:
            exchange_calls += 1
            return httpx2.Response(
                200, request=request, json={"access_token": f"token-{exchange_calls}", "expires_in": 3600}
            )

        api_authorizations.append(request.headers["Authorization"])
        if exchange_calls < 3:
            return httpx2.Response(401, request=request, json={"error": {"message": "unauthorized"}})
        return httpx2.Response(200, request=request, json={"object": "list", "data": []})

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(APIStatusError, match="401"):
            client.models.list()
        assert client.models.list().object == "list"

    assert exchange_calls == 3
    assert api_authorizations == ["Bearer token-1", "Bearer token-2", "Bearer token-3"]


async def test_async_x509_invalidates_a_rejected_replay_token() -> None:
    exchange_calls = 0
    api_authorizations: list[str] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal exchange_calls
        if str(request.url) == _TOKEN_URL:
            exchange_calls += 1
            return httpx2.Response(
                200, request=request, json={"access_token": f"token-{exchange_calls}", "expires_in": 3600}
            )

        api_authorizations.append(request.headers["Authorization"])
        if exchange_calls < 3:
            return httpx2.Response(401, request=request, json={"error": {"message": "unauthorized"}})
        return httpx2.Response(200, request=request, json={"object": "list", "data": []})

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(APIStatusError, match="401"):
            await client.models.list()
        assert (await client.models.list()).object == "list"

    assert exchange_calls == 3
    assert api_authorizations == ["Bearer token-1", "Bearer token-2", "Bearer token-3"]


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
