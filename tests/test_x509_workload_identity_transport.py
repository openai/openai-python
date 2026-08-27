from __future__ import annotations

import os
import sys
import json
import asyncio
import importlib
import threading
import subprocess
from typing import Any, cast
from textwrap import dedent
from contextvars import Context
from typing_extensions import override
from concurrent.futures import ThreadPoolExecutor

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, OpenAIError
from openai.auth import X509WorkloadIdentity, x509_workload_identity
from openai.auth._x509 import (
    _ACTIVE_AUXILIARY_TRANSPORT_MARKERS,
    _ACTIVE_UNPROTECTED_TRANSPORT_SCOPES,
    _client_transport_scope,
    _FinalizingRequestHooks,
)

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


@pytest.mark.parametrize("hook_mutation", ["clear", "append"])
def test_sync_x509_validates_destination_after_request_hooks_mutate_the_hook_list(hook_mutation: str) -> None:
    requests: list[httpx2.Request] = []
    http_client = httpx2.Client(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

    def redirect(request: httpx2.Request) -> None:
        request.url = httpx2.URL("https://attacker.invalid/capture")
        request.headers["host"] = "attacker.invalid"
        http_client._transport = httpx2.MockTransport(lambda redirected: _record(requests, redirected))
        http_client._mounts.clear()

    def hook(request: httpx2.Request) -> None:
        if hook_mutation == "clear":
            http_client.event_hooks["request"].clear()
            redirect(request)
        else:
            http_client.event_hooks["request"].append(redirect)

    http_client.event_hooks["request"].append(hook)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="configured API origin"):
            client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


@pytest.mark.parametrize("hook_mutation", ["clear", "append"])
async def test_async_x509_validates_destination_after_request_hooks_mutate_the_hook_list(hook_mutation: str) -> None:
    requests: list[httpx2.Request] = []
    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

    async def redirect(request: httpx2.Request) -> None:
        request.url = httpx2.URL("https://attacker.invalid/capture")
        request.headers["host"] = "attacker.invalid"
        http_client._transport = httpx2.MockTransport(lambda redirected: _record(requests, redirected))
        http_client._mounts.clear()

    async def hook(request: httpx2.Request) -> None:
        if hook_mutation == "clear":
            http_client.event_hooks["request"].clear()
            await redirect(request)
        else:
            http_client.event_hooks["request"].append(redirect)

    http_client.event_hooks["request"].append(hook)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="configured API origin"):
            await client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


@pytest.mark.parametrize(
    ("redirect", "authorization", "copy_extensions"),
    [
        (False, None, True),
        (False, None, False),
        (True, None, True),
        (True, None, False),
        (True, "bearer access-token", True),
        (True, "bearer access-token", False),
        (True, "Bearer substituted-token", True),
        (True, "Bearer substituted-token", False),
        (True, "Basic access-token", False),
        (True, "Bearer access%2Dtoken", False),
    ],
)
def test_sync_x509_validates_requests_reconstructed_by_custom_clients(
    redirect: bool, authorization: str | None, copy_extensions: bool
) -> None:
    requests: list[httpx2.Request] = []

    class ReconstructingClient(httpx2.Client):
        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            url = "https://attacker.invalid/capture" if redirect else str(request.url)
            extensions = request.extensions if copy_extensions else None
            copied = httpx2.Request(request.method, url, headers=dict(request.headers), extensions=extensions)
            if redirect:
                copied.headers["host"] = "attacker.invalid"
            if authorization is not None:
                copied.headers["authorization"] = authorization
            return super().send(copied, **kwargs)

    http_client = ReconstructingClient(
        transport=httpx2.MockTransport(lambda request: _record(requests, request)), trust_env=False
    )
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        if redirect:
            with pytest.raises(OpenAIError, match="configured API origin"):
                client.models.list()
        else:
            assert client.models.list().object == "list"

    expected = [_TOKEN_URL] if redirect else [_TOKEN_URL, _API_URL]
    assert [str(request.url) for request in requests] == expected


@pytest.mark.parametrize(
    ("redirect", "authorization", "copy_extensions"),
    [
        (False, None, True),
        (False, None, False),
        (True, None, True),
        (True, None, False),
        (True, "bearer access-token", True),
        (True, "bearer access-token", False),
        (True, "Bearer substituted-token", True),
        (True, "Bearer substituted-token", False),
        (True, "Basic access-token", False),
        (True, "Bearer access%2Dtoken", False),
    ],
)
async def test_async_x509_validates_requests_reconstructed_by_custom_clients(
    redirect: bool, authorization: str | None, copy_extensions: bool
) -> None:
    requests: list[httpx2.Request] = []

    class ReconstructingClient(httpx2.AsyncClient):
        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            url = "https://attacker.invalid/capture" if redirect else str(request.url)
            extensions = request.extensions if copy_extensions else None
            copied = httpx2.Request(request.method, url, headers=dict(request.headers), extensions=extensions)
            if redirect:
                copied.headers["host"] = "attacker.invalid"
            if authorization is not None:
                copied.headers["authorization"] = authorization
            return await super().send(copied, **kwargs)

    http_client = ReconstructingClient(
        transport=httpx2.MockTransport(lambda request: _record(requests, request)), trust_env=False
    )
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        if redirect:
            with pytest.raises(OpenAIError, match="configured API origin"):
                await client.models.list()
        else:
            assert (await client.models.list()).object == "list"

    expected = [_TOKEN_URL] if redirect else [_TOKEN_URL, _API_URL]
    assert [str(request.url) for request in requests] == expected


@pytest.mark.parametrize("authorization", ["Bearer substituted-token", "Bearer access%2Dtoken"])
@pytest.mark.parametrize("copy_access_token", [False, True])
def test_sync_x509_rejects_recursively_reconstructed_protected_requests(
    authorization: str, copy_access_token: bool
) -> None:
    requests: list[httpx2.Request] = []

    class ReconstructingClient(httpx2.Client):
        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if request.url.host == "mtls.api.openai.com":
                copied = httpx2.Request(
                    request.method, "https://attacker.invalid/capture", headers=dict(request.headers)
                )
                copied.headers["host"] = "attacker.invalid"
                copied.headers["Authorization"] = authorization
                if copy_access_token:
                    copied.headers["X-Copied-Credential"] = request.headers["Authorization"]
                return self.send(copied, **kwargs)
            return super().send(request, **kwargs)

    http_client = ReconstructingClient(transport=httpx2.MockTransport(lambda request: _record(requests, request)))
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="configured API origin|authorization"):
            client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


@pytest.mark.parametrize("authorization", ["Bearer substituted-token", "Bearer access%2Dtoken"])
@pytest.mark.parametrize("copy_access_token", [False, True])
async def test_async_x509_rejects_recursively_reconstructed_protected_requests(
    authorization: str, copy_access_token: bool
) -> None:
    requests: list[httpx2.Request] = []

    class ReconstructingClient(httpx2.AsyncClient):
        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if request.url.host == "mtls.api.openai.com":
                copied = httpx2.Request(
                    request.method, "https://attacker.invalid/capture", headers=dict(request.headers)
                )
                copied.headers["host"] = "attacker.invalid"
                copied.headers["Authorization"] = authorization
                if copy_access_token:
                    copied.headers["X-Copied-Credential"] = request.headers["Authorization"]
                return await self.send(copied, **kwargs)
            return await super().send(request, **kwargs)

    http_client = ReconstructingClient(transport=httpx2.MockTransport(lambda request: _record(requests, request)))
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="configured API origin|authorization"):
            await client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


@pytest.mark.parametrize("redirect", [False, True])
@pytest.mark.parametrize("delegate_storage", ["attribute", "slot", "private_slot", "list", "dict"])
@pytest.mark.parametrize("reconstruct", [False, True])
def test_sync_x509_validates_requests_delegated_to_another_http_client(
    redirect: bool, delegate_storage: str, reconstruct: bool
) -> None:
    requests: list[httpx2.Request] = []

    def redirect_request(request: httpx2.Request) -> None:
        if redirect:
            request.url = httpx2.URL("https://attacker.invalid/capture")
            request.headers["host"] = "attacker.invalid"

    class PrivateSlotClient(httpx2.Client):
        __slots__ = ("__private_inner",)

        def set_private_inner(self, inner: httpx2.Client) -> None:
            self.__private_inner = inner

        def private_inner(self) -> httpx2.Client:
            return self.__private_inner

    class DelegatingClient(PrivateSlotClient):
        __slots__ = ("slotted_inner",)

        def __init__(self) -> None:
            inner = httpx2.Client(
                transport=httpx2.MockTransport(lambda request: _record(requests, request)),
                event_hooks={"request": [redirect_request]},
            )
            if delegate_storage == "slot":
                self.slotted_inner = inner
            elif delegate_storage == "private_slot":
                self.set_private_inner(inner)
            elif delegate_storage == "list":
                self.clients = [inner]
            elif delegate_storage == "dict":
                self.client_mapping = {"inner": inner}
            else:
                self.inner = inner
            super().__init__(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if delegate_storage == "slot":
                inner = self.slotted_inner
            elif delegate_storage == "private_slot":
                inner = self.private_inner()
            elif delegate_storage == "list":
                inner = self.clients[0]
            elif delegate_storage == "dict":
                inner = self.client_mapping["inner"]
            else:
                inner = self.inner
            if reconstruct:
                reconstructed = inner.build_request(request.method, request.url)
                reconstructed.headers.update(request.headers)
                request = reconstructed
            return inner.send(request, **kwargs)

    http_client = DelegatingClient()
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        if redirect:
            with pytest.raises(OpenAIError, match="configured API origin"):
                client.models.list()
        else:
            assert client.models.list().object == "list"

    expected = [_TOKEN_URL] if redirect else [_TOKEN_URL, _API_URL]
    assert [str(request.url) for request in requests] == expected


@pytest.mark.parametrize("redirect", [False, True])
@pytest.mark.parametrize("delegate_storage", ["attribute", "slot", "private_slot", "list", "dict"])
@pytest.mark.parametrize("reconstruct", [False, True])
async def test_async_x509_validates_requests_delegated_to_another_http_client(
    redirect: bool, delegate_storage: str, reconstruct: bool
) -> None:
    requests: list[httpx2.Request] = []

    async def redirect_request(request: httpx2.Request) -> None:
        if redirect:
            request.url = httpx2.URL("https://attacker.invalid/capture")
            request.headers["host"] = "attacker.invalid"

    class PrivateSlotClient(httpx2.AsyncClient):
        __slots__ = ("__private_inner",)

        def set_private_inner(self, inner: httpx2.AsyncClient) -> None:
            self.__private_inner = inner

        def private_inner(self) -> httpx2.AsyncClient:
            return self.__private_inner

    class DelegatingClient(PrivateSlotClient):
        __slots__ = ("slotted_inner",)

        def __init__(self) -> None:
            inner = httpx2.AsyncClient(
                transport=httpx2.MockTransport(lambda request: _record(requests, request)),
                event_hooks={"request": [redirect_request]},
            )
            if delegate_storage == "slot":
                self.slotted_inner = inner
            elif delegate_storage == "private_slot":
                self.set_private_inner(inner)
            elif delegate_storage == "list":
                self.clients = [inner]
            elif delegate_storage == "dict":
                self.client_mapping = {"inner": inner}
            else:
                self.inner = inner
            super().__init__(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if delegate_storage == "slot":
                inner = self.slotted_inner
            elif delegate_storage == "private_slot":
                inner = self.private_inner()
            elif delegate_storage == "list":
                inner = self.clients[0]
            elif delegate_storage == "dict":
                inner = self.client_mapping["inner"]
            else:
                inner = self.inner
            if reconstruct:
                reconstructed = inner.build_request(request.method, request.url)
                reconstructed.headers.update(request.headers)
                request = reconstructed
            return await inner.send(request, **kwargs)

    http_client = DelegatingClient()
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        if redirect:
            with pytest.raises(OpenAIError, match="configured API origin"):
                await client.models.list()
        else:
            assert (await client.models.list()).object == "list"

    expected = [_TOKEN_URL] if redirect else [_TOKEN_URL, _API_URL]
    assert [str(request.url) for request in requests] == expected


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


@pytest.mark.parametrize("redirect", [False, True])
@pytest.mark.parametrize("delegate_source", ["factory", "lazy", "bound", "dispatch"])
@pytest.mark.parametrize("reconstruct", [False, True])
def test_sync_x509_validates_lazily_delegated_http_client_requests(
    redirect: bool, delegate_source: str, reconstruct: bool
) -> None:
    requests: list[httpx2.Request] = []

    def redirect_request(request: httpx2.Request) -> None:
        if redirect:
            request.url = httpx2.URL("https://attacker.invalid/capture")
            request.headers["host"] = "attacker.invalid"

    def make_delegate() -> httpx2.Client:
        return httpx2.Client(
            transport=httpx2.MockTransport(lambda request: _record(requests, request)),
            event_hooks={"request": [redirect_request]},
        )

    factory_delegate = make_delegate() if delegate_source in ("factory", "bound", "dispatch") else None
    bound_send = factory_delegate.send if delegate_source == "bound" and factory_delegate is not None else None
    if delegate_source == "dispatch" and factory_delegate is not None:
        vars(factory_delegate)["_send_single_request"] = factory_delegate._send_single_request

    class DelegatingClient(httpx2.Client):
        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            inner = factory_delegate if factory_delegate is not None else make_delegate()
            if reconstruct:
                reconstructed = inner.build_request(request.method, request.url)
                reconstructed.headers.update(request.headers)
                request = reconstructed
            return bound_send(request, **kwargs) if bound_send is not None else inner.send(request, **kwargs)

    original_send = httpx2.Client.send
    original_dispatch = httpx2.Client._send_single_request
    http_client = DelegatingClient(transport=httpx2.MockTransport(lambda request: _record(requests, request)))
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        if redirect:
            with pytest.raises(OpenAIError, match="configured API origin"):
                client.models.list()
        else:
            assert client.models.list().object == "list"

    expected = [_TOKEN_URL] if redirect else [_TOKEN_URL, _API_URL]
    assert [str(request.url) for request in requests] == expected
    assert httpx2.Client.send is original_send
    assert httpx2.Client._send_single_request is original_dispatch
    if factory_delegate is not None:
        assert factory_delegate.event_hooks["request"] == [redirect_request]


@pytest.mark.parametrize("credential_location", ["query", "body"])
def test_sync_x509_rejects_lazy_delegate_hooks_that_move_credentials_outside_headers(
    credential_location: str,
) -> None:
    requests: list[httpx2.Request] = []

    def relocate_credential(request: httpx2.Request) -> None:
        token = request.headers.pop("Authorization").removeprefix("Bearer ")
        request.url = httpx2.URL(f"https://attacker.invalid/capture?credential={token}")
        if credential_location == "body":
            request.url = httpx2.URL("https://attacker.invalid/capture")
            request._content = token.encode()
        request.headers["host"] = "attacker.invalid"
        request.extensions.clear()

    class DelegatingClient(httpx2.Client):
        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            delegate = httpx2.Client(
                transport=httpx2.MockTransport(lambda value: _record(requests, value)),
                event_hooks={"request": [relocate_credential]},
            )
            reconstructed = delegate.build_request(request.method, request.url)
            reconstructed.headers.update(request.headers)
            return delegate.send(reconstructed, **kwargs)

    transport = DelegatingClient(transport=httpx2.MockTransport(lambda request: _record(requests, request)))
    with OpenAI(workload_identity=_identity(), http_client=transport, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="configured API origin|authorization"):
            client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


@pytest.mark.parametrize("redirect", [False, True])
@pytest.mark.parametrize("delegate_source", ["factory", "lazy", "bound", "dispatch"])
@pytest.mark.parametrize("reconstruct", [False, True])
async def test_async_x509_validates_lazily_delegated_http_client_requests(
    redirect: bool, delegate_source: str, reconstruct: bool
) -> None:
    requests: list[httpx2.Request] = []

    async def redirect_request(request: httpx2.Request) -> None:
        if redirect:
            request.url = httpx2.URL("https://attacker.invalid/capture")
            request.headers["host"] = "attacker.invalid"

    def make_delegate() -> httpx2.AsyncClient:
        return httpx2.AsyncClient(
            transport=httpx2.MockTransport(lambda request: _record(requests, request)),
            event_hooks={"request": [redirect_request]},
        )

    factory_delegate = make_delegate() if delegate_source in ("factory", "bound", "dispatch") else None
    bound_send = factory_delegate.send if delegate_source == "bound" and factory_delegate is not None else None
    if delegate_source == "dispatch" and factory_delegate is not None:
        vars(factory_delegate)["_send_single_request"] = factory_delegate._send_single_request

    class DelegatingClient(httpx2.AsyncClient):
        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            inner = factory_delegate if factory_delegate is not None else make_delegate()
            if reconstruct:
                reconstructed = inner.build_request(request.method, request.url)
                reconstructed.headers.update(request.headers)
                request = reconstructed
            return await (bound_send(request, **kwargs) if bound_send is not None else inner.send(request, **kwargs))

    original_send = httpx2.AsyncClient.send
    original_dispatch = httpx2.AsyncClient._send_single_request
    http_client = DelegatingClient(transport=httpx2.MockTransport(lambda request: _record(requests, request)))
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        if redirect:
            with pytest.raises(OpenAIError, match="configured API origin"):
                await client.models.list()
        else:
            assert (await client.models.list()).object == "list"

    expected = [_TOKEN_URL] if redirect else [_TOKEN_URL, _API_URL]
    assert [str(request.url) for request in requests] == expected
    assert httpx2.AsyncClient.send is original_send
    assert httpx2.AsyncClient._send_single_request is original_dispatch
    if factory_delegate is not None:
        assert factory_delegate.event_hooks["request"] == [redirect_request]


@pytest.mark.parametrize("credential_location", ["query", "body"])
async def test_async_x509_rejects_lazy_delegate_hooks_that_move_credentials_outside_headers(
    credential_location: str,
) -> None:
    requests: list[httpx2.Request] = []

    async def relocate_credential(request: httpx2.Request) -> None:
        token = request.headers.pop("Authorization").removeprefix("Bearer ")
        request.url = httpx2.URL(f"https://attacker.invalid/capture?credential={token}")
        if credential_location == "body":
            request.url = httpx2.URL("https://attacker.invalid/capture")
            request._content = token.encode()
        request.headers["host"] = "attacker.invalid"
        request.extensions.clear()

    class DelegatingClient(httpx2.AsyncClient):
        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            delegate = httpx2.AsyncClient(
                transport=httpx2.MockTransport(lambda value: _record(requests, value)),
                event_hooks={"request": [relocate_credential]},
            )
            reconstructed = delegate.build_request(request.method, request.url)
            reconstructed.headers.update(request.headers)
            return await delegate.send(reconstructed, **kwargs)

    transport = DelegatingClient(transport=httpx2.MockTransport(lambda request: _record(requests, request)))
    async with AsyncOpenAI(workload_identity=_identity(), http_client=transport, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="configured API origin|authorization"):
            await client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


@pytest.mark.parametrize("authorization", [None, "Bearer telemetry-token"])
def test_sync_x509_allows_telemetry_from_a_separately_created_http_client(authorization: str | None) -> None:
    requests: list[httpx2.Request] = []

    class TelemetryClient(httpx2.Client):
        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            telemetry = httpx2.Client(transport=httpx2.MockTransport(lambda value: _record(requests, value)))
            headers = {} if authorization is None else {"Authorization": authorization}
            telemetry.get("https://telemetry.example/collect", headers=headers)
            return super().send(request, **kwargs)

    http_client = TelemetryClient(transport=httpx2.MockTransport(lambda request: _record(requests, request)))
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert client.models.list().object == "list"

    assert [str(request.url) for request in requests] == [_TOKEN_URL, "https://telemetry.example/collect", _API_URL]


@pytest.mark.parametrize("authorization", [None, "Bearer telemetry-token"])
async def test_async_x509_allows_telemetry_from_a_separately_created_http_client(authorization: str | None) -> None:
    requests: list[httpx2.Request] = []

    class TelemetryClient(httpx2.AsyncClient):
        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            telemetry = httpx2.AsyncClient(transport=httpx2.MockTransport(lambda value: _record(requests, value)))
            headers = {} if authorization is None else {"Authorization": authorization}
            await telemetry.get("https://telemetry.example/collect", headers=headers)
            return await super().send(request, **kwargs)

    http_client = TelemetryClient(transport=httpx2.MockTransport(lambda request: _record(requests, request)))
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert (await client.models.list()).object == "list"

    assert [str(request.url) for request in requests] == [_TOKEN_URL, "https://telemetry.example/collect", _API_URL]


@pytest.mark.skipif(os.getenv("OPENAI_TEST_LEGACY_HTTPX") != "1", reason="requires legacy HTTPX compatibility lane")
@pytest.mark.parametrize("lazy", [False, True])
def test_sync_x509_validates_requests_delegated_to_legacy_httpx_clients(lazy: bool) -> None:
    legacy_httpx = cast(Any, importlib.import_module("httpx"))
    requests: list[Any] = []

    def handler(request: Any) -> Any:
        requests.append(request)
        if str(request.url) == _TOKEN_URL:
            return legacy_httpx.Response(
                200, request=request, json={"access_token": "access-token", "expires_in": 3600}
            )
        return legacy_httpx.Response(200, request=request, json={"object": "list", "data": []})

    def redirect(request: Any) -> None:
        request.url = legacy_httpx.URL("https://attacker.invalid/capture")
        request.headers["host"] = "attacker.invalid"

    outer = legacy_httpx.Client(transport=legacy_httpx.MockTransport(handler))
    if not lazy:
        outer.inner = legacy_httpx.Client(
            transport=legacy_httpx.MockTransport(handler), event_hooks={"request": [redirect]}
        )

    def delegate(request: Any, **kwargs: Any) -> Any:
        inner = (
            legacy_httpx.Client(transport=legacy_httpx.MockTransport(handler), event_hooks={"request": [redirect]})
            if lazy
            else outer.inner
        )
        return inner.send(request, **kwargs)

    outer.send = delegate
    with OpenAI(workload_identity=_identity(), http_client=outer, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="configured API origin"):
            client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


@pytest.mark.skipif(os.getenv("OPENAI_TEST_LEGACY_HTTPX") != "1", reason="requires legacy HTTPX compatibility lane")
@pytest.mark.parametrize("lazy", [False, True])
async def test_async_x509_validates_requests_delegated_to_legacy_httpx_clients(lazy: bool) -> None:
    legacy_httpx = cast(Any, importlib.import_module("httpx"))
    requests: list[Any] = []

    def handler(request: Any) -> Any:
        requests.append(request)
        if str(request.url) == _TOKEN_URL:
            return legacy_httpx.Response(
                200, request=request, json={"access_token": "access-token", "expires_in": 3600}
            )
        return legacy_httpx.Response(200, request=request, json={"object": "list", "data": []})

    async def redirect(request: Any) -> None:
        request.url = legacy_httpx.URL("https://attacker.invalid/capture")
        request.headers["host"] = "attacker.invalid"

    outer = legacy_httpx.AsyncClient(transport=legacy_httpx.MockTransport(handler))
    if not lazy:
        outer.inner = legacy_httpx.AsyncClient(
            transport=legacy_httpx.MockTransport(handler), event_hooks={"request": [redirect]}
        )

    async def delegate(request: Any, **kwargs: Any) -> Any:
        inner = (
            legacy_httpx.AsyncClient(transport=legacy_httpx.MockTransport(handler), event_hooks={"request": [redirect]})
            if lazy
            else outer.inner
        )
        return await inner.send(request, **kwargs)

    outer.send = delegate
    async with AsyncOpenAI(workload_identity=_identity(), http_client=outer, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="configured API origin"):
            await client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


@pytest.mark.skipif(os.getenv("OPENAI_TEST_LEGACY_HTTPX") != "1", reason="requires legacy HTTPX compatibility lane")
@pytest.mark.parametrize("is_async", [False, True])
def test_x509_guards_legacy_httpx_imported_by_a_lazy_delegate(is_async: bool) -> None:
    script = dedent(
        """
        import asyncio
        import importlib
        import sys

        import httpx2
        from openai import AsyncOpenAI, OpenAI, OpenAIError
        from openai.auth import x509_workload_identity

        assert "httpx" not in sys.modules
        captures = []

        def handler(request):
            captures.append(str(request.url))
            if request.url.host == "mtls.auth.openai.com":
                return httpx2.Response(
                    200, request=request, json={"access_token": "fake-access-token", "expires_in": 3600}
                )
            return httpx2.Response(200, request=request, json={"object": "list", "data": []})

        def redirect(request):
            legacy = importlib.import_module("httpx")
            request.url = legacy.URL("https://attacker.invalid/capture")
            request.headers["host"] = "attacker.invalid"

        identity = x509_workload_identity(identity_provider_id="idp_example", service_account_id="svc_example")

        if sys.argv[1] == "async":
            class Outer(httpx2.AsyncClient):
                async def send(self, request, **kwargs):
                    legacy = importlib.import_module("httpx")

                    async def hook(value):
                        redirect(value)

                    inner = legacy.AsyncClient(transport=legacy.MockTransport(handler), event_hooks={"request": [hook]})
                    copied = legacy.Request(request.method, str(request.url), headers=dict(request.headers))
                    kwargs["auth"] = None
                    return await inner.send(copied, **kwargs)

            async def run():
                outer = Outer(transport=httpx2.MockTransport(handler))
                async with AsyncOpenAI(workload_identity=identity, http_client=outer, max_retries=0) as client:
                    try:
                        await client.models.list()
                    except OpenAIError:
                        return
                    raise AssertionError("redirected X.509 request was not blocked")

            asyncio.run(run())
        else:
            class Outer(httpx2.Client):
                def send(self, request, **kwargs):
                    legacy = importlib.import_module("httpx")
                    inner = legacy.Client(transport=legacy.MockTransport(handler), event_hooks={"request": [redirect]})
                    copied = legacy.Request(request.method, str(request.url), headers=dict(request.headers))
                    kwargs["auth"] = None
                    return inner.send(copied, **kwargs)

            outer = Outer(transport=httpx2.MockTransport(handler))
            with OpenAI(workload_identity=identity, http_client=outer, max_retries=0) as client:
                try:
                    client.models.list()
                except OpenAIError:
                    pass
                else:
                    raise AssertionError("redirected X.509 request was not blocked")

        assert captures == ["https://mtls.auth.openai.com/oauth/token"], captures
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", script, "async" if is_async else "sync"], capture_output=True, check=False, text=True
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("reconstruct", [False, True])
def test_sync_x509_validates_requests_dispatched_by_custom_clients_in_another_thread(reconstruct: bool) -> None:
    requests: list[httpx2.Request] = []

    class ThreadDispatchClient(httpx2.Client):
        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if reconstruct:
                request = httpx2.Request(request.method, request.url, headers=dict(request.headers))
            with ThreadPoolExecutor(max_workers=1) as executor:
                return executor.submit(super().send, request, **kwargs).result()

    def redirect(request: httpx2.Request) -> None:
        request.url = httpx2.URL("https://attacker.invalid/capture")
        request.headers["host"] = "attacker.invalid"

    http_client = ThreadDispatchClient(
        transport=httpx2.MockTransport(lambda request: _record(requests, request)),
        event_hooks={"request": [redirect]},
        trust_env=False,
    )
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="configured API origin"):
            client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


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


def test_sync_x509_preserves_request_hooks_added_during_send() -> None:
    calls: list[str] = []
    http_client = httpx2.Client(transport=httpx2.MockTransport(_response))

    def appended(_request: httpx2.Request) -> None:
        calls.append("appended")

    def initial(_request: httpx2.Request) -> None:
        calls.append("initial")
        if appended not in http_client.event_hooks["request"]:
            http_client.event_hooks["request"].append(appended)

    http_client.event_hooks["request"].append(initial)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        client.models.list()
        assert len(http_client.event_hooks["request"]) == 2
        client.models.list()

    assert calls == ["initial", "appended", "initial", "appended"]


async def test_async_x509_preserves_request_hooks_added_during_send() -> None:
    calls: list[str] = []
    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(_response))

    async def appended(_request: httpx2.Request) -> None:
        calls.append("appended")

    async def initial(_request: httpx2.Request) -> None:
        calls.append("initial")
        if appended not in http_client.event_hooks["request"]:
            http_client.event_hooks["request"].append(appended)

    http_client.event_hooks["request"].append(initial)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        await client.models.list()
        assert len(http_client.event_hooks["request"]) == 2
        await client.models.list()

    assert calls == ["initial", "appended", "initial", "appended"]


@pytest.mark.parametrize(
    "mutation",
    [
        "remove",
        "append",
        "mixed",
        "extend",
        "insert",
        "pop",
        "setitem",
        "slice",
        "delete",
        "iadd",
        "imul",
        "self_extend",
        "self_iadd",
        "self_slice",
    ],
)
def test_sync_x509_preserves_mutations_through_retained_request_hook_lists(mutation: str) -> None:
    calls: list[str] = []
    http_client = httpx2.Client(transport=httpx2.MockTransport(_response))
    retained_hooks = http_client.event_hooks["request"]

    def appended(_request: httpx2.Request) -> None:
        calls.append("appended")

    def initial(_request: httpx2.Request) -> None:
        calls.append("initial")
        scoped_hooks = http_client.event_hooks["request"]
        if mutation == "remove":
            retained_hooks.remove(initial)
        elif mutation == "append":
            if appended not in retained_hooks:
                retained_hooks.append(appended)
            assert scoped_hooks == retained_hooks
            assert scoped_hooks + [] == retained_hooks
            assert [] + scoped_hooks == retained_hooks
            assert scoped_hooks * 2 == retained_hooks * 2
            assert 2 * scoped_hooks == 2 * retained_hooks
            assert list(reversed(scoped_hooks)) == list(reversed(retained_hooks))
            assert repr(scoped_hooks) == repr(retained_hooks)
        elif mutation == "mixed":
            retained_hooks.remove(initial)
            scoped_hooks.append(appended)
        elif mutation == "extend" and appended not in scoped_hooks:
            scoped_hooks.extend([appended])
        elif mutation == "insert" and appended not in scoped_hooks:
            scoped_hooks.insert(len(scoped_hooks), appended)
        elif mutation == "pop":
            scoped_hooks.pop(0)
        elif mutation == "setitem":
            scoped_hooks[0] = appended
        elif mutation == "slice":
            scoped_hooks[:] = [appended]
        elif mutation == "delete":
            del scoped_hooks[0]
        elif mutation == "iadd" and appended not in scoped_hooks:
            scoped_hooks += [appended]
        elif mutation == "imul" and len(scoped_hooks) == 1:
            scoped_hooks *= 2
        elif mutation == "self_extend" and len(scoped_hooks) == 1:
            scoped_hooks.extend(scoped_hooks)
        elif mutation == "self_iadd" and len(scoped_hooks) == 1:
            scoped_hooks += scoped_hooks
        elif mutation == "self_slice":
            scoped_hooks[:] = scoped_hooks

    retained_hooks.append(initial)
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        client.models.list()
        assert http_client.event_hooks["request"] is retained_hooks
        expected_hooks = (
            []
            if mutation in ("remove", "pop", "delete")
            else [appended]
            if mutation in ("mixed", "setitem", "slice")
            else [initial, initial]
            if mutation in ("imul", "self_extend", "self_iadd")
            else [initial]
            if mutation == "self_slice"
            else [initial, appended]
        )
        assert retained_hooks == expected_hooks
        client.models.list()

    expected_calls = (
        ["initial"]
        if mutation in ("remove", "pop", "delete")
        else ["initial", "appended"]
        if mutation in ("mixed", "setitem", "slice")
        else ["initial"] * 4
        if mutation in ("imul", "self_extend", "self_iadd")
        else ["initial", "initial"]
        if mutation == "self_slice"
        else ["initial", "appended", "initial", "appended"]
    )
    assert calls == expected_calls


@pytest.mark.parametrize(
    "mutation",
    [
        "remove",
        "append",
        "mixed",
        "extend",
        "insert",
        "pop",
        "setitem",
        "slice",
        "delete",
        "iadd",
        "imul",
        "self_extend",
        "self_iadd",
        "self_slice",
    ],
)
async def test_async_x509_preserves_mutations_through_retained_request_hook_lists(mutation: str) -> None:
    calls: list[str] = []
    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(_response))
    retained_hooks = http_client.event_hooks["request"]

    async def appended(_request: httpx2.Request) -> None:
        calls.append("appended")

    async def initial(_request: httpx2.Request) -> None:
        calls.append("initial")
        scoped_hooks = http_client.event_hooks["request"]
        if mutation == "remove":
            retained_hooks.remove(initial)
        elif mutation == "append":
            if appended not in retained_hooks:
                retained_hooks.append(appended)
            assert scoped_hooks == retained_hooks
            assert scoped_hooks + [] == retained_hooks
            assert [] + scoped_hooks == retained_hooks
            assert scoped_hooks * 2 == retained_hooks * 2
            assert 2 * scoped_hooks == 2 * retained_hooks
            assert list(reversed(scoped_hooks)) == list(reversed(retained_hooks))
            assert repr(scoped_hooks) == repr(retained_hooks)
        elif mutation == "mixed":
            retained_hooks.remove(initial)
            scoped_hooks.append(appended)
        elif mutation == "extend" and appended not in scoped_hooks:
            scoped_hooks.extend([appended])
        elif mutation == "insert" and appended not in scoped_hooks:
            scoped_hooks.insert(len(scoped_hooks), appended)
        elif mutation == "pop":
            scoped_hooks.pop(0)
        elif mutation == "setitem":
            scoped_hooks[0] = appended
        elif mutation == "slice":
            scoped_hooks[:] = [appended]
        elif mutation == "delete":
            del scoped_hooks[0]
        elif mutation == "iadd" and appended not in scoped_hooks:
            scoped_hooks += [appended]
        elif mutation == "imul" and len(scoped_hooks) == 1:
            scoped_hooks *= 2
        elif mutation == "self_extend" and len(scoped_hooks) == 1:
            scoped_hooks.extend(scoped_hooks)
        elif mutation == "self_iadd" and len(scoped_hooks) == 1:
            scoped_hooks += scoped_hooks
        elif mutation == "self_slice":
            scoped_hooks[:] = scoped_hooks

    retained_hooks.append(initial)
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        await client.models.list()
        assert http_client.event_hooks["request"] is retained_hooks
        expected_hooks = (
            []
            if mutation in ("remove", "pop", "delete")
            else [appended]
            if mutation in ("mixed", "setitem", "slice")
            else [initial, initial]
            if mutation in ("imul", "self_extend", "self_iadd")
            else [initial]
            if mutation == "self_slice"
            else [initial, appended]
        )
        assert retained_hooks == expected_hooks
        await client.models.list()

    expected_calls = (
        ["initial"]
        if mutation in ("remove", "pop", "delete")
        else ["initial", "appended"]
        if mutation in ("mixed", "setitem", "slice")
        else ["initial"] * 4
        if mutation in ("imul", "self_extend", "self_iadd")
        else ["initial", "initial"]
        if mutation == "self_slice"
        else ["initial", "appended", "initial", "appended"]
    )
    assert calls == expected_calls


@pytest.mark.parametrize("mutation", ["extend", "iadd", "slice"])
def test_x509_hook_list_composition_never_retains_private_validation_callbacks(mutation: str) -> None:
    first_hooks: list[Any] = [object()]
    second_hooks: list[Any] = [object()]
    first_validator = object()
    second_validator = object()
    first = _FinalizingRequestHooks(first_hooks, first_validator)
    second = _FinalizingRequestHooks(second_hooks, second_validator)

    if mutation == "extend":
        first.extend(second)
    elif mutation == "iadd":
        first += second
    else:
        first[:] = second

    assert first_validator not in first_hooks
    assert second_validator not in first_hooks
    expected = second_hooks if mutation == "slice" else [first_hooks[0], *second_hooks]
    assert first_hooks == expected


@pytest.mark.parametrize("instance_send", [False, True])
def test_sync_x509_preserves_custom_client_send_and_response_encoding(instance_send: bool) -> None:
    class RecordingClient(httpx2.Client):
        def __init__(self) -> None:
            self.sent: list[str] = []
            self.send_count = 0
            self.lifecycle: list[str] = []
            super().__init__(
                default_encoding="latin-1",
                transport=httpx2.MockTransport(
                    lambda request: (
                        _response(request)
                        if str(request.url) == _TOKEN_URL
                        else httpx2.Response(200, request=request, content=b"caf\xe9")
                    )
                ),
            )

        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            assert self is http_client
            self.sent.append(str(request.url))
            self.send_count += 1
            return super().send(request, **kwargs)

        @override
        def __enter__(self) -> RecordingClient:
            self.lifecycle.append("enter")
            return super().__enter__()

        @override
        def __exit__(self, *args: Any) -> None:
            self.lifecycle.append("exit")
            super().__exit__(*args)

    http_client = RecordingClient()
    original_send = http_client.send
    if instance_send:
        vars(http_client)["send"] = original_send
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        response = client.get("/models", cast_to=httpx2.Response)
        assert response.text == "café"
        assert http_client.sent == [_API_URL]
        assert http_client.send_count == 1
        assert http_client.lifecycle == []
        assert http_client._state.name == "OPENED"
        assert (vars(http_client).get("send") is original_send) is instance_send


@pytest.mark.parametrize("instance_send", [False, True])
async def test_async_x509_preserves_custom_client_send_and_response_encoding(instance_send: bool) -> None:
    class RecordingClient(httpx2.AsyncClient):
        def __init__(self) -> None:
            self.sent: list[str] = []
            self.send_count = 0
            self.lifecycle: list[str] = []
            super().__init__(
                default_encoding="latin-1",
                transport=httpx2.MockTransport(
                    lambda request: (
                        _response(request)
                        if str(request.url) == _TOKEN_URL
                        else httpx2.Response(200, request=request, content=b"caf\xe9")
                    )
                ),
            )

        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            assert self is http_client
            self.sent.append(str(request.url))
            self.send_count += 1
            return await super().send(request, **kwargs)

        @override
        async def __aenter__(self) -> RecordingClient:
            self.lifecycle.append("enter")
            return await super().__aenter__()

        @override
        async def __aexit__(self, *args: Any) -> None:
            self.lifecycle.append("exit")
            await super().__aexit__(*args)

    http_client = RecordingClient()
    original_send = http_client.send
    if instance_send:
        vars(http_client)["send"] = original_send
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        response = await client.get("/models", cast_to=httpx2.Response)
        assert response.text == "café"
        assert http_client.sent == [_API_URL]
        assert http_client.send_count == 1
        assert http_client.lifecycle == []
        assert http_client._state.name == "OPENED"
        assert (vars(http_client).get("send") is original_send) is instance_send


def test_sync_x509_preserves_custom_client_state_across_concurrent_requests() -> None:
    barrier = threading.Barrier(2)

    class CountingClient(httpx2.Client):
        def __init__(self) -> None:
            self.send_count = 0
            super().__init__(transport=httpx2.MockTransport(_response))

        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            self.send_count += 1
            barrier.wait(timeout=5)
            return super().send(request, **kwargs)

    http_client = CountingClient()
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(client.models.list) for _ in range(2)]
            assert [future.result().object for future in futures] == ["list", "list"]

    assert http_client.send_count == 2


async def test_async_x509_preserves_custom_client_state_across_concurrent_requests() -> None:
    ready = asyncio.Event()
    started = 0

    class CountingClient(httpx2.AsyncClient):
        def __init__(self) -> None:
            self.send_count = 0
            super().__init__(transport=httpx2.MockTransport(_response))

        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            nonlocal started
            self.send_count += 1
            started += 1
            if started == 2:
                ready.set()
            await ready.wait()
            return await super().send(request, **kwargs)

    http_client = CountingClient()
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        responses = await asyncio.gather(client.models.list(), client.models.list())
        assert [response.object for response in responses] == ["list", "list"]

    assert http_client.send_count == 2


def test_sync_x509_preserves_slotted_custom_client_state() -> None:
    class SlottedClient(httpx2.Client):
        __slots__ = ("send_count",)

        def __init__(self) -> None:
            self.send_count = 0
            super().__init__(transport=httpx2.MockTransport(_response))

        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            self.send_count += 1
            return super().send(request, **kwargs)

    http_client = SlottedClient()
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        client.models.list()

    assert http_client.send_count == 1


async def test_async_x509_preserves_slotted_custom_client_state() -> None:
    class SlottedClient(httpx2.AsyncClient):
        __slots__ = ("send_count",)

        def __init__(self) -> None:
            self.send_count = 0
            super().__init__(transport=httpx2.MockTransport(_response))

        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            self.send_count += 1
            return await super().send(request, **kwargs)

    http_client = SlottedClient()
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        await client.models.list()

    assert http_client.send_count == 1


def test_sync_x509_preserves_immutable_custom_client_state_across_concurrent_requests() -> None:
    barrier = threading.Barrier(2)

    class RecordingClient(httpx2.Client):
        def __init__(self) -> None:
            self.history: tuple[str, ...] = ()
            super().__init__(transport=httpx2.MockTransport(_response))

        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            self.history += (str(request.url),)
            barrier.wait(timeout=5)
            return super().send(request, **kwargs)

    http_client = RecordingClient()
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(client.models.list) for _ in range(2)]
            assert [future.result().object for future in futures] == ["list", "list"]

    assert http_client.history == (_API_URL, _API_URL)


async def test_async_x509_preserves_immutable_custom_client_state_across_concurrent_requests() -> None:
    ready = asyncio.Event()
    started = 0

    class RecordingClient(httpx2.AsyncClient):
        def __init__(self) -> None:
            self.history: tuple[str, ...] = ()
            super().__init__(transport=httpx2.MockTransport(_response))

        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            nonlocal started
            self.history += (str(request.url),)
            started += 1
            if started == 2:
                ready.set()
            await ready.wait()
            return await super().send(request, **kwargs)

    http_client = RecordingClient()
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        responses = await asyncio.gather(client.models.list(), client.models.list())
        assert [response.object for response in responses] == ["list", "list"]

    assert http_client.history == (_API_URL, _API_URL)


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


@pytest.mark.parametrize(
    "nested_mode",
    [
        "x509",
        "api_key",
        "matching_api_key",
        "direct",
        "direct_prebuilt",
        "direct_prebuilt_authorized",
        "direct_prebuilt_propagated",
        "direct_prebuilt_authorized_propagated",
        "direct_authorized",
        "direct_propagated",
        "direct_authorized_propagated",
        "direct_reconstructed",
        "direct_authorized_reconstructed",
        "direct_propagated_reconstructed",
        "direct_authorized_propagated_reconstructed",
        "direct_hook_authorized_reconstructed",
        "direct_hook_authorized_propagated_reconstructed",
        "direct_hook_redirected_reconstructed",
        "direct_hook_redirected_authorized_reconstructed",
    ],
)
def test_sync_x509_allows_nested_requests_using_the_same_http_client(nested_mode: str) -> None:
    requests: list[httpx2.Request] = []

    class NestedClient(httpx2.Client):
        def __init__(self) -> None:
            self.nested: OpenAI | None = None
            self.nested_completed = False

            def authorize_telemetry(request: httpx2.Request) -> None:
                if request.url.host == "telemetry.example":
                    if "hook_authorized" in nested_mode:
                        request.headers["Authorization"] = "Bearer telemetry-token"
                    if "hook_redirected" in nested_mode:
                        request.url = httpx2.URL("https://collector.example/v1/models")
                        request.headers["host"] = "collector.example"

            super().__init__(
                transport=httpx2.MockTransport(lambda request: _record(requests, request)),
                event_hooks={"request": [authorize_telemetry]},
            )

        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if not self.nested_completed and (self.nested is not None or nested_mode.startswith("direct")):
                self.nested_completed = True
                if nested_mode.startswith("direct"):
                    headers = (
                        {
                            name: value
                            for name, value in request.headers.items()
                            if name.lower() not in ("authorization", "host")
                        }
                        if "propagated" in nested_mode
                        else {}
                    )
                    if "authorized" in nested_mode and "hook_authorized" not in nested_mode:
                        headers["Authorization"] = "Bearer telemetry-token"
                    if "prebuilt" in nested_mode:
                        auxiliary = httpx2.Request("GET", "https://telemetry.example/v1/models", headers=headers)
                        response = self.send(auxiliary)
                    else:
                        response = self.get("https://telemetry.example/v1/models", headers=headers)
                    assert response.json()["object"] == "list"
                else:
                    assert self.nested is not None
                    assert self.nested.models.list().object == "list"
            if request.url.host == "telemetry.example" and "reconstructed" in nested_mode:
                request = httpx2.Request(request.method, request.url, headers=dict(request.headers))
            return super().send(request, **kwargs)

    http_client = NestedClient()
    if nested_mode == "x509":
        nested_identity = x509_workload_identity(identity_provider_id="nested-idp", service_account_id="nested-svc")
        http_client.nested = OpenAI(workload_identity=nested_identity, http_client=http_client, max_retries=0)
    elif not nested_mode.startswith("direct"):
        api_key = "access-token" if nested_mode == "matching_api_key" else "nested-api-key"
        http_client.nested = OpenAI(
            api_key=api_key, base_url="https://nested.example/v1", http_client=http_client, max_retries=0
        )

    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        if nested_mode == "direct_prebuilt_authorized_propagated":
            with pytest.raises(OpenAIError, match="configured API origin"):
                client.models.list()
        else:
            assert client.models.list().object == "list"

    assert http_client.nested_completed


@pytest.mark.parametrize(
    "nested_mode",
    [
        "x509",
        "api_key",
        "matching_api_key",
        "direct",
        "direct_prebuilt",
        "direct_prebuilt_authorized",
        "direct_prebuilt_propagated",
        "direct_prebuilt_authorized_propagated",
        "direct_authorized",
        "direct_propagated",
        "direct_authorized_propagated",
        "direct_reconstructed",
        "direct_authorized_reconstructed",
        "direct_propagated_reconstructed",
        "direct_authorized_propagated_reconstructed",
        "direct_hook_authorized_reconstructed",
        "direct_hook_authorized_propagated_reconstructed",
        "direct_hook_redirected_reconstructed",
        "direct_hook_redirected_authorized_reconstructed",
    ],
)
async def test_async_x509_allows_nested_requests_using_the_same_http_client(nested_mode: str) -> None:
    requests: list[httpx2.Request] = []

    class NestedClient(httpx2.AsyncClient):
        def __init__(self) -> None:
            self.nested: AsyncOpenAI | None = None
            self.nested_completed = False

            async def authorize_telemetry(request: httpx2.Request) -> None:
                if request.url.host == "telemetry.example":
                    if "hook_authorized" in nested_mode:
                        request.headers["Authorization"] = "Bearer telemetry-token"
                    if "hook_redirected" in nested_mode:
                        request.url = httpx2.URL("https://collector.example/v1/models")
                        request.headers["host"] = "collector.example"

            super().__init__(
                transport=httpx2.MockTransport(lambda request: _record(requests, request)),
                event_hooks={"request": [authorize_telemetry]},
            )

        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if not self.nested_completed and (self.nested is not None or nested_mode.startswith("direct")):
                self.nested_completed = True
                if nested_mode.startswith("direct"):
                    headers = (
                        {
                            name: value
                            for name, value in request.headers.items()
                            if name.lower() not in ("authorization", "host")
                        }
                        if "propagated" in nested_mode
                        else {}
                    )
                    if "authorized" in nested_mode and "hook_authorized" not in nested_mode:
                        headers["Authorization"] = "Bearer telemetry-token"
                    if "prebuilt" in nested_mode:
                        auxiliary = httpx2.Request("GET", "https://telemetry.example/v1/models", headers=headers)
                        response = await self.send(auxiliary)
                    else:
                        response = await self.get("https://telemetry.example/v1/models", headers=headers)
                    assert response.json()["object"] == "list"
                else:
                    assert self.nested is not None
                    assert (await self.nested.models.list()).object == "list"
            if request.url.host == "telemetry.example" and "reconstructed" in nested_mode:
                request = httpx2.Request(request.method, request.url, headers=dict(request.headers))
            return await super().send(request, **kwargs)

    http_client = NestedClient()
    if nested_mode == "x509":
        nested_identity = x509_workload_identity(identity_provider_id="nested-idp", service_account_id="nested-svc")
        http_client.nested = AsyncOpenAI(workload_identity=nested_identity, http_client=http_client, max_retries=0)
    elif not nested_mode.startswith("direct"):
        api_key = "access-token" if nested_mode == "matching_api_key" else "nested-api-key"
        http_client.nested = AsyncOpenAI(
            api_key=api_key, base_url="https://nested.example/v1", http_client=http_client, max_retries=0
        )

    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        if nested_mode == "direct_prebuilt_authorized_propagated":
            with pytest.raises(OpenAIError, match="configured API origin"):
                await client.models.list()
        else:
            assert (await client.models.list()).object == "list"

    assert http_client.nested_completed


@pytest.mark.parametrize("prebuilt", [False, True])
@pytest.mark.parametrize("credential_header", ["Authorization", "X-Copied-Credential"])
def test_sync_x509_rejects_auxiliary_hooks_that_add_the_active_access_token(
    prebuilt: bool, credential_header: str
) -> None:
    requests: list[httpx2.Request] = []

    def inject_token(request: httpx2.Request) -> None:
        if request.url.host == "telemetry.example":
            request.headers[credential_header] = "Bearer access-token"
            request.url = httpx2.URL("https://attacker.invalid/capture")
            request.headers["host"] = "attacker.invalid"

    class NestedClient(httpx2.Client):
        def __init__(self) -> None:
            self.sent_auxiliary = False
            super().__init__(
                transport=httpx2.MockTransport(lambda request: _record(requests, request)),
                event_hooks={"request": [inject_token]},
            )

        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if not self.sent_auxiliary:
                self.sent_auxiliary = True
                if prebuilt:
                    self.send(httpx2.Request("GET", "https://telemetry.example/v1/models"))
                else:
                    self.get("https://telemetry.example/v1/models")
            return super().send(request, **kwargs)

    http_client = NestedClient()
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="configured API origin|authorization"):
            client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


@pytest.mark.parametrize("prebuilt", [False, True])
@pytest.mark.parametrize("credential_header", ["Authorization", "X-Copied-Credential"])
async def test_async_x509_rejects_auxiliary_hooks_that_add_the_active_access_token(
    prebuilt: bool, credential_header: str
) -> None:
    requests: list[httpx2.Request] = []

    async def inject_token(request: httpx2.Request) -> None:
        if request.url.host == "telemetry.example":
            request.headers[credential_header] = "Bearer access-token"
            request.url = httpx2.URL("https://attacker.invalid/capture")
            request.headers["host"] = "attacker.invalid"

    class NestedClient(httpx2.AsyncClient):
        def __init__(self) -> None:
            self.sent_auxiliary = False
            super().__init__(
                transport=httpx2.MockTransport(lambda request: _record(requests, request)),
                event_hooks={"request": [inject_token]},
            )

        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if not self.sent_auxiliary:
                self.sent_auxiliary = True
                if prebuilt:
                    await self.send(httpx2.Request("GET", "https://telemetry.example/v1/models"))
                else:
                    await self.get("https://telemetry.example/v1/models")
            return await super().send(request, **kwargs)

    http_client = NestedClient()
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="configured API origin|authorization"):
            await client.models.list()

    assert [str(request.url) for request in requests] == [_TOKEN_URL]


def test_sync_x509_releases_auxiliary_markers_while_protected_requests_overlap() -> None:
    first_active = threading.Event()
    release_first = threading.Event()
    original_markers = set(_ACTIVE_AUXILIARY_TRANSPORT_MARKERS)

    class ConcurrentClient(httpx2.Client):
        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if request.url.host == "mtls.api.openai.com":
                if request.headers.get("Authorization") == "Bearer token-one":
                    first_active.set()
                    assert release_first.wait(timeout=10)
                else:
                    for _ in range(8):
                        assert self.get("https://telemetry.example/collect").status_code == 200
                        assert _ACTIVE_AUXILIARY_TRANSPORT_MARKERS == original_markers
                    self.build_request("GET", "https://telemetry.example/unsent")
            return super().send(request, **kwargs)

    def response(request: httpx2.Request) -> httpx2.Response:
        if str(request.url) == _TOKEN_URL:
            suffix = json.loads(request.content)["identity_provider_id"].rsplit("-", 1)[-1]
            return httpx2.Response(200, request=request, json={"access_token": f"token-{suffix}", "expires_in": 3600})
        return httpx2.Response(200, request=request, json={"object": "list", "data": []})

    transport = ConcurrentClient(transport=httpx2.MockTransport(response))
    clients = [
        OpenAI(
            workload_identity=x509_workload_identity(identity_provider_id=f"idp-{suffix}", service_account_id="svc"),
            http_client=transport,
            max_retries=0,
        )
        for suffix in ("one", "two")
    ]

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(clients[0].models.list)
        assert first_active.wait(timeout=5)
        second = executor.submit(clients[1].models.list)
        assert second.result(timeout=5).object == "list"
        assert _ACTIVE_AUXILIARY_TRANSPORT_MARKERS == original_markers
        assert not _client_transport_scope(transport, is_async=False)._auxiliary_request_markers
        release_first.set()
        assert first.result(timeout=5).object == "list"

    assert not any(marker not in original_markers for marker in _ACTIVE_UNPROTECTED_TRANSPORT_SCOPES)


async def test_async_x509_releases_auxiliary_markers_while_protected_requests_overlap() -> None:
    first_active = asyncio.Event()
    release_first = asyncio.Event()
    original_markers = set(_ACTIVE_AUXILIARY_TRANSPORT_MARKERS)

    class ConcurrentClient(httpx2.AsyncClient):
        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if request.url.host == "mtls.api.openai.com":
                if request.headers.get("Authorization") == "Bearer token-one":
                    first_active.set()
                    await asyncio.wait_for(release_first.wait(), timeout=10)
                else:
                    for _ in range(8):
                        assert (await self.get("https://telemetry.example/collect")).status_code == 200
                        assert _ACTIVE_AUXILIARY_TRANSPORT_MARKERS == original_markers
                    self.build_request("GET", "https://telemetry.example/unsent")
            return await super().send(request, **kwargs)

    def response(request: httpx2.Request) -> httpx2.Response:
        if str(request.url) == _TOKEN_URL:
            suffix = json.loads(request.content)["identity_provider_id"].rsplit("-", 1)[-1]
            return httpx2.Response(200, request=request, json={"access_token": f"token-{suffix}", "expires_in": 3600})
        return httpx2.Response(200, request=request, json={"object": "list", "data": []})

    transport = ConcurrentClient(transport=httpx2.MockTransport(response))
    clients = [
        AsyncOpenAI(
            workload_identity=x509_workload_identity(identity_provider_id=f"idp-{suffix}", service_account_id="svc"),
            http_client=transport,
            max_retries=0,
        )
        for suffix in ("one", "two")
    ]

    async def request_first() -> Any:
        return await clients[0].models.list()

    first = asyncio.create_task(request_first())
    await asyncio.wait_for(first_active.wait(), timeout=5)
    assert (await clients[1].models.list()).object == "list"
    assert _ACTIVE_AUXILIARY_TRANSPORT_MARKERS == original_markers
    assert not _client_transport_scope(transport, is_async=True)._auxiliary_request_markers
    release_first.set()
    assert (await asyncio.wait_for(first, timeout=5)).object == "list"

    assert not any(marker not in original_markers for marker in _ACTIVE_UNPROTECTED_TRANSPORT_SCOPES)


def test_sync_x509_allows_concurrent_origins_with_the_same_access_token() -> None:
    both_active = threading.Barrier(2)

    class ConcurrentClient(httpx2.Client):
        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            both_active.wait(timeout=5)
            return super().send(request, **kwargs)

    transport = ConcurrentClient(transport=httpx2.MockTransport(_response))
    clients = [
        OpenAI(workload_identity=_identity(), http_client=transport, base_url=origin, max_retries=0)
        for origin in ("https://mtls.api.openai.com/v1", "https://mtls-us.api.openai.com/v1")
    ]

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = [executor.submit(client.models.list) for client in clients]
        assert [result.result(timeout=5).object for result in results] == ["list", "list"]


async def test_async_x509_allows_concurrent_origins_with_the_same_access_token() -> None:
    active_count = 0
    both_active = asyncio.Event()

    class ConcurrentClient(httpx2.AsyncClient):
        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            nonlocal active_count
            active_count += 1
            if active_count == 2:
                both_active.set()
            await asyncio.wait_for(both_active.wait(), timeout=5)
            return await super().send(request, **kwargs)

    transport = ConcurrentClient(transport=httpx2.MockTransport(_response))
    clients = [
        AsyncOpenAI(workload_identity=_identity(), http_client=transport, base_url=origin, max_retries=0)
        for origin in ("https://mtls.api.openai.com/v1", "https://mtls-us.api.openai.com/v1")
    ]

    assert [result.object for result in await asyncio.gather(*(client.models.list() for client in clients))] == [
        "list",
        "list",
    ]


@pytest.mark.parametrize("cross_origin", [False, True])
def test_sync_x509_rejects_auxiliary_requests_with_another_active_identity_token(cross_origin: bool) -> None:
    requests: list[httpx2.Request] = []
    both_active = threading.Barrier(2)
    release_second = threading.Event()

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        if str(request.url) == _TOKEN_URL:
            identity = json.loads(request.content)["identity_provider_id"]
            token = f"token-{identity.rsplit('-', 1)[-1]}"
            return httpx2.Response(200, request=request, json={"access_token": token, "expires_in": 3600})
        return httpx2.Response(200, request=request, json={"object": "list", "data": []})

    def redirect_telemetry(request: httpx2.Request) -> None:
        if request.url.host == "telemetry.example":
            request.url = httpx2.URL("https://attacker.invalid/capture")
            request.headers["host"] = "attacker.invalid"

    class ConcurrentClient(httpx2.Client):
        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if request.url.host in ("mtls.api.openai.com", "mtls-us.api.openai.com"):
                both_active.wait(timeout=5)
                if request.headers.get("Authorization") == "Bearer token-one":
                    try:
                        if cross_origin:
                            self.get(
                                "https://mtls-us.api.openai.com/v1/models",
                                headers={
                                    "Authorization": "Bearer token-two",
                                    "X-Copied-Credential": "Bearer token-one",
                                },
                            )
                        else:
                            self.get(
                                "https://telemetry.example/v1/models", headers={"Authorization": "Bearer token-two"}
                            )
                    finally:
                        release_second.set()
                else:
                    assert release_second.wait(timeout=5)
            return super().send(request, **kwargs)

    transport = ConcurrentClient(transport=httpx2.MockTransport(handler), event_hooks={"request": [redirect_telemetry]})
    clients = [
        OpenAI(
            workload_identity=x509_workload_identity(identity_provider_id=f"idp-{suffix}", service_account_id="svc"),
            http_client=transport,
            base_url="https://mtls-us.api.openai.com/v1" if cross_origin and suffix == "two" else None,
            max_retries=0,
        )
        for suffix in ("one", "two")
    ]

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = [executor.submit(client.models.list) for client in clients]
        with pytest.raises(OpenAIError, match="configured API origin|authorization|single API origin"):
            results[0].result(timeout=5)
        assert results[1].result(timeout=5).object == "list"

    assert all(request.url.host != "attacker.invalid" for request in requests)


@pytest.mark.parametrize("cross_origin", [False, True])
async def test_async_x509_rejects_auxiliary_requests_with_another_active_identity_token(cross_origin: bool) -> None:
    requests: list[httpx2.Request] = []
    active_count = 0
    both_active = asyncio.Event()
    release_second = asyncio.Event()

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        if str(request.url) == _TOKEN_URL:
            identity = json.loads(request.content)["identity_provider_id"]
            token = f"token-{identity.rsplit('-', 1)[-1]}"
            return httpx2.Response(200, request=request, json={"access_token": token, "expires_in": 3600})
        return httpx2.Response(200, request=request, json={"object": "list", "data": []})

    async def redirect_telemetry(request: httpx2.Request) -> None:
        if request.url.host == "telemetry.example":
            request.url = httpx2.URL("https://attacker.invalid/capture")
            request.headers["host"] = "attacker.invalid"

    class ConcurrentClient(httpx2.AsyncClient):
        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            nonlocal active_count
            if request.url.host in ("mtls.api.openai.com", "mtls-us.api.openai.com"):
                active_count += 1
                if active_count == 2:
                    both_active.set()
                await asyncio.wait_for(both_active.wait(), timeout=5)
                if request.headers.get("Authorization") == "Bearer token-one":
                    try:
                        if cross_origin:
                            await self.get(
                                "https://mtls-us.api.openai.com/v1/models",
                                headers={
                                    "Authorization": "Bearer token-two",
                                    "X-Copied-Credential": "Bearer token-one",
                                },
                            )
                        else:
                            await self.get(
                                "https://telemetry.example/v1/models", headers={"Authorization": "Bearer token-two"}
                            )
                    finally:
                        release_second.set()
                else:
                    await asyncio.wait_for(release_second.wait(), timeout=5)
            return await super().send(request, **kwargs)

    transport = ConcurrentClient(transport=httpx2.MockTransport(handler), event_hooks={"request": [redirect_telemetry]})
    clients = [
        AsyncOpenAI(
            workload_identity=x509_workload_identity(identity_provider_id=f"idp-{suffix}", service_account_id="svc"),
            http_client=transport,
            base_url="https://mtls-us.api.openai.com/v1" if cross_origin and suffix == "two" else None,
            max_retries=0,
        )
        for suffix in ("one", "two")
    ]

    first, second = await asyncio.gather(*(client.models.list() for client in clients), return_exceptions=True)
    assert isinstance(first, OpenAIError)
    assert any(message in str(first) for message in ("configured API origin", "authorization", "single API origin"))
    assert not isinstance(second, BaseException)
    assert second.object == "list"
    assert all(request.url.host != "attacker.invalid" for request in requests)


@pytest.mark.parametrize(
    ("ordinary_origin", "ordinary_api_key"),
    [("https://nested.example/v1", "nested-api-key"), ("https://attacker.invalid/v1", "access-token")],
)
@pytest.mark.parametrize("copy_ordinary_marker", [False, True])
def test_sync_x509_rejects_redirected_protected_requests_nested_inside_ordinary_requests(
    ordinary_origin: str, ordinary_api_key: str, copy_ordinary_marker: bool
) -> None:
    requests: list[httpx2.Request] = []
    ordinary_host = httpx2.URL(ordinary_origin).host

    class MixedNestedClient(httpx2.Client):
        def __init__(self) -> None:
            self.depth = 0
            self.ordinary: OpenAI | None = None
            self.protected: OpenAI | None = None
            self.ordinary_extensions: dict[str, Any] = {}
            super().__init__(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if request.url.host == "mtls.api.openai.com" and self.depth == 0 and self.ordinary is not None:
                self.depth = 1
                self.ordinary.models.list()
            elif request.url.host == ordinary_host and self.depth == 1 and self.protected is not None:
                self.depth = 2
                self.ordinary_extensions = dict(request.extensions)
                self.protected.models.list()
            elif request.url.host == "mtls.api.openai.com" and self.depth == 2:
                request = httpx2.Request(
                    request.method,
                    "https://attacker.invalid/capture",
                    headers=dict(request.headers),
                    extensions=self.ordinary_extensions if copy_ordinary_marker else None,
                )
                request.headers["host"] = "attacker.invalid"
            return super().send(request, **kwargs)

    http_client = MixedNestedClient()
    http_client.ordinary = OpenAI(
        api_key=ordinary_api_key, base_url=ordinary_origin, http_client=http_client, max_retries=0
    )
    http_client.protected = OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0)

    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="configured API origin"):
            client.models.list()

    assert all(request.url.host != "attacker.invalid" for request in requests)


@pytest.mark.parametrize(
    ("ordinary_origin", "ordinary_api_key"),
    [("https://nested.example/v1", "nested-api-key"), ("https://attacker.invalid/v1", "access-token")],
)
@pytest.mark.parametrize("copy_ordinary_marker", [False, True])
async def test_async_x509_rejects_redirected_protected_requests_nested_inside_ordinary_requests(
    ordinary_origin: str, ordinary_api_key: str, copy_ordinary_marker: bool
) -> None:
    requests: list[httpx2.Request] = []
    ordinary_host = httpx2.URL(ordinary_origin).host

    class MixedNestedClient(httpx2.AsyncClient):
        def __init__(self) -> None:
            self.depth = 0
            self.ordinary: AsyncOpenAI | None = None
            self.protected: AsyncOpenAI | None = None
            self.ordinary_extensions: dict[str, Any] = {}
            super().__init__(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if request.url.host == "mtls.api.openai.com" and self.depth == 0 and self.ordinary is not None:
                self.depth = 1
                await self.ordinary.models.list()
            elif request.url.host == ordinary_host and self.depth == 1 and self.protected is not None:
                self.depth = 2
                self.ordinary_extensions = dict(request.extensions)
                await self.protected.models.list()
            elif request.url.host == "mtls.api.openai.com" and self.depth == 2:
                request = httpx2.Request(
                    request.method,
                    "https://attacker.invalid/capture",
                    headers=dict(request.headers),
                    extensions=self.ordinary_extensions if copy_ordinary_marker else None,
                )
                request.headers["host"] = "attacker.invalid"
            return await super().send(request, **kwargs)

    http_client = MixedNestedClient()
    http_client.ordinary = AsyncOpenAI(
        api_key=ordinary_api_key, base_url=ordinary_origin, http_client=http_client, max_retries=0
    )
    http_client.protected = AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0)

    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        with pytest.raises(OpenAIError, match="configured API origin"):
            await client.models.list()

    assert all(request.url.host != "attacker.invalid" for request in requests)


@pytest.mark.parametrize("direct_request", [False, True])
def test_sync_x509_allows_ordinary_requests_that_start_before_a_concurrent_protected_request(
    direct_request: bool,
) -> None:
    ordinary_started = threading.Event()
    protected_started = threading.Event()
    allow_ordinary = threading.Event()
    allow_protected = threading.Event()

    class CoordinatedClient(httpx2.Client):
        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if request.url.host == "nested.example":
                ordinary_started.set()
                assert allow_ordinary.wait(timeout=5)
            elif request.url.host == "mtls.api.openai.com":
                protected_started.set()
                assert allow_protected.wait(timeout=5)
            return super().send(request, **kwargs)

    http_client = CoordinatedClient(transport=httpx2.MockTransport(_response))
    ordinary = OpenAI(api_key="ordinary-key", base_url="https://nested.example/v1", http_client=http_client)
    protected = OpenAI(workload_identity=_identity(), http_client=http_client)

    def list_ordinary() -> str:
        if direct_request:
            return cast(str, http_client.get("https://nested.example/v1/models").json()["object"])
        return ordinary.models.list().object

    with ThreadPoolExecutor(max_workers=2) as executor:
        ordinary_result = executor.submit(list_ordinary)
        assert ordinary_started.wait(timeout=5)
        protected_result = executor.submit(protected.models.list)
        assert protected_started.wait(timeout=5)
        allow_ordinary.set()
        try:
            assert ordinary_result.result(timeout=5) == "list"
        finally:
            allow_protected.set()
        assert protected_result.result(timeout=5).object == "list"


@pytest.mark.parametrize("direct_request", [False, True])
async def test_async_x509_allows_ordinary_requests_that_start_before_a_concurrent_protected_request(
    direct_request: bool,
) -> None:
    ordinary_started = asyncio.Event()
    protected_started = asyncio.Event()
    allow_ordinary = asyncio.Event()
    allow_protected = asyncio.Event()

    class CoordinatedClient(httpx2.AsyncClient):
        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if request.url.host == "nested.example":
                ordinary_started.set()
                await asyncio.wait_for(allow_ordinary.wait(), timeout=5)
            elif request.url.host == "mtls.api.openai.com":
                protected_started.set()
                await asyncio.wait_for(allow_protected.wait(), timeout=5)
            return await super().send(request, **kwargs)

    http_client = CoordinatedClient(transport=httpx2.MockTransport(_response))
    ordinary = AsyncOpenAI(api_key="ordinary-key", base_url="https://nested.example/v1", http_client=http_client)
    protected = AsyncOpenAI(workload_identity=_identity(), http_client=http_client)

    async def list_models(client: AsyncOpenAI) -> str:
        return (await client.models.list()).object

    async def list_ordinary() -> str:
        if direct_request:
            response = await http_client.get("https://nested.example/v1/models")
            return cast(str, response.json()["object"])
        return await list_models(ordinary)

    ordinary_result = asyncio.create_task(list_ordinary())
    await asyncio.wait_for(ordinary_started.wait(), timeout=5)
    protected_result = asyncio.create_task(list_models(protected))
    await asyncio.wait_for(protected_started.wait(), timeout=5)
    allow_ordinary.set()
    try:
        assert await asyncio.wait_for(ordinary_result, timeout=5) == "list"
    finally:
        allow_protected.set()
    assert await asyncio.wait_for(protected_result, timeout=5) == "list"


@pytest.mark.parametrize("shared_client", [False, True])
@pytest.mark.parametrize("lowercase_bearer", [False, True])
def test_sync_x509_never_trusts_a_matching_concurrent_ordinary_request(
    shared_client: bool, lowercase_bearer: bool
) -> None:
    requests: list[httpx2.Request] = []
    ordinary_started = threading.Event()
    allow_ordinary = threading.Event()

    def handle(request: httpx2.Request) -> httpx2.Response:
        if request.url.path == "/v1/models" and request.url.host == "attacker.invalid":
            ordinary_started.set()
            assert allow_ordinary.wait(timeout=5)
        return _record(requests, request)

    def redirect(request: httpx2.Request) -> None:
        if request.url.host == "mtls.api.openai.com":
            request.url = httpx2.URL("https://attacker.invalid/capture")
            request.headers["host"] = "attacker.invalid"

    class CrossThreadClient(httpx2.Client):
        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if request.url.host == "mtls.api.openai.com":
                request = httpx2.Request(request.method, request.url, headers=dict(request.headers))
                if lowercase_bearer:
                    request.headers["authorization"] = "bearer access-token"
                with ThreadPoolExecutor(max_workers=1) as executor:
                    return executor.submit(super().send, request, **kwargs).result()
            return super().send(request, **kwargs)

    protected_transport = CrossThreadClient(transport=httpx2.MockTransport(handle), event_hooks={"request": [redirect]})
    ordinary_transport = protected_transport if shared_client else httpx2.Client(transport=httpx2.MockTransport(handle))
    ordinary = OpenAI(api_key="access-token", base_url="https://attacker.invalid/v1", http_client=ordinary_transport)
    protected = OpenAI(workload_identity=_identity(), http_client=protected_transport, max_retries=0)

    with ThreadPoolExecutor(max_workers=1) as executor:
        ordinary_result = executor.submit(ordinary.models.list)
        assert ordinary_started.wait(timeout=5)
        try:
            with pytest.raises(OpenAIError, match="configured API origin|authorization"):
                protected.models.list()
        finally:
            allow_ordinary.set()
        assert ordinary_result.result(timeout=5).object == "list"

    assert all(request.url.path != "/capture" for request in requests)


@pytest.mark.parametrize("shared_client", [False, True])
@pytest.mark.parametrize("lowercase_bearer", [False, True])
async def test_async_x509_never_trusts_a_matching_concurrent_ordinary_request(
    shared_client: bool, lowercase_bearer: bool
) -> None:
    requests: list[httpx2.Request] = []
    ordinary_started = asyncio.Event()
    allow_ordinary = asyncio.Event()

    async def handle(request: httpx2.Request) -> httpx2.Response:
        if request.url.path == "/v1/models" and request.url.host == "attacker.invalid":
            ordinary_started.set()
            await asyncio.wait_for(allow_ordinary.wait(), timeout=5)
        return _record(requests, request)

    async def redirect(request: httpx2.Request) -> None:
        if request.url.host == "mtls.api.openai.com":
            request.url = httpx2.URL("https://attacker.invalid/capture")
            request.headers["host"] = "attacker.invalid"

    class CrossContextClient(httpx2.AsyncClient):
        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if request.url.host == "mtls.api.openai.com":
                copied = httpx2.Request(request.method, request.url, headers=dict(request.headers))
                if lowercase_bearer:
                    copied.headers["authorization"] = "bearer access-token"
                coroutine = super().send(copied, **kwargs)
                return await Context().run(asyncio.create_task, coroutine)
            return await super().send(request, **kwargs)

    protected_transport = CrossContextClient(
        transport=httpx2.MockTransport(handle), event_hooks={"request": [redirect]}
    )
    ordinary_transport = (
        protected_transport if shared_client else httpx2.AsyncClient(transport=httpx2.MockTransport(handle))
    )
    ordinary = AsyncOpenAI(
        api_key="access-token", base_url="https://attacker.invalid/v1", http_client=ordinary_transport
    )
    protected = AsyncOpenAI(workload_identity=_identity(), http_client=protected_transport, max_retries=0)

    async def run_ordinary() -> str:
        return (await ordinary.models.list()).object

    ordinary_result = asyncio.create_task(run_ordinary())
    await asyncio.wait_for(ordinary_started.wait(), timeout=5)
    try:
        with pytest.raises(OpenAIError, match="configured API origin|authorization"):
            await protected.models.list()
    finally:
        allow_ordinary.set()
    assert await asyncio.wait_for(ordinary_result, timeout=5) == "list"
    assert all(request.url.path != "/capture" for request in requests)
