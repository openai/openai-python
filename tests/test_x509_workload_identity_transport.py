from __future__ import annotations

import asyncio
import threading
from typing import Any, cast
from contextvars import Context
from typing_extensions import override
from concurrent.futures import ThreadPoolExecutor

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


def test_sync_x509_preserves_custom_client_send_and_response_encoding() -> None:
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
    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        response = client.get("/models", cast_to=httpx2.Response)
        assert response.text == "café"
        assert http_client.sent == [_API_URL]
        assert http_client.send_count == 1
        assert http_client.lifecycle == []
        assert http_client._state.name == "OPENED"


async def test_async_x509_preserves_custom_client_send_and_response_encoding() -> None:
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
    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        response = await client.get("/models", cast_to=httpx2.Response)
        assert response.text == "café"
        assert http_client.sent == [_API_URL]
        assert http_client.send_count == 1
        assert http_client.lifecycle == []
        assert http_client._state.name == "OPENED"


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


@pytest.mark.parametrize("nested_mode", ["x509", "api_key", "matching_api_key"])
def test_sync_x509_allows_nested_requests_using_the_same_http_client(nested_mode: str) -> None:
    requests: list[httpx2.Request] = []

    class NestedClient(httpx2.Client):
        def __init__(self) -> None:
            self.nested: OpenAI | None = None
            self.nested_completed = False
            super().__init__(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if not self.nested_completed and self.nested is not None:
                self.nested_completed = True
                assert self.nested.models.list().object == "list"
            return super().send(request, **kwargs)

    http_client = NestedClient()
    if nested_mode == "x509":
        nested_identity = x509_workload_identity(identity_provider_id="nested-idp", service_account_id="nested-svc")
        http_client.nested = OpenAI(workload_identity=nested_identity, http_client=http_client, max_retries=0)
    else:
        api_key = "access-token" if nested_mode == "matching_api_key" else "nested-api-key"
        http_client.nested = OpenAI(
            api_key=api_key, base_url="https://nested.example/v1", http_client=http_client, max_retries=0
        )

    with OpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert client.models.list().object == "list"

    assert http_client.nested_completed


@pytest.mark.parametrize("nested_mode", ["x509", "api_key", "matching_api_key"])
async def test_async_x509_allows_nested_requests_using_the_same_http_client(nested_mode: str) -> None:
    requests: list[httpx2.Request] = []

    class NestedClient(httpx2.AsyncClient):
        def __init__(self) -> None:
            self.nested: AsyncOpenAI | None = None
            self.nested_completed = False
            super().__init__(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if not self.nested_completed and self.nested is not None:
                self.nested_completed = True
                assert (await self.nested.models.list()).object == "list"
            return await super().send(request, **kwargs)

    http_client = NestedClient()
    if nested_mode == "x509":
        nested_identity = x509_workload_identity(identity_provider_id="nested-idp", service_account_id="nested-svc")
        http_client.nested = AsyncOpenAI(workload_identity=nested_identity, http_client=http_client, max_retries=0)
    else:
        api_key = "access-token" if nested_mode == "matching_api_key" else "nested-api-key"
        http_client.nested = AsyncOpenAI(
            api_key=api_key, base_url="https://nested.example/v1", http_client=http_client, max_retries=0
        )

    async with AsyncOpenAI(workload_identity=_identity(), http_client=http_client, max_retries=0) as client:
        assert (await client.models.list()).object == "list"

    assert http_client.nested_completed


@pytest.mark.parametrize(
    ("ordinary_origin", "ordinary_api_key"),
    [("https://nested.example/v1", "nested-api-key"), ("https://attacker.invalid/v1", "access-token")],
)
def test_sync_x509_rejects_redirected_protected_requests_nested_inside_ordinary_requests(
    ordinary_origin: str, ordinary_api_key: str
) -> None:
    requests: list[httpx2.Request] = []
    ordinary_host = httpx2.URL(ordinary_origin).host

    class MixedNestedClient(httpx2.Client):
        def __init__(self) -> None:
            self.depth = 0
            self.ordinary: OpenAI | None = None
            self.protected: OpenAI | None = None
            super().__init__(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

        @override
        def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if request.url.host == "mtls.api.openai.com" and self.depth == 0 and self.ordinary is not None:
                self.depth = 1
                self.ordinary.models.list()
            elif request.url.host == ordinary_host and self.depth == 1 and self.protected is not None:
                self.depth = 2
                self.protected.models.list()
            elif request.url.host == "mtls.api.openai.com" and self.depth == 2:
                request = httpx2.Request(
                    request.method, "https://attacker.invalid/capture", headers=dict(request.headers)
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
async def test_async_x509_rejects_redirected_protected_requests_nested_inside_ordinary_requests(
    ordinary_origin: str, ordinary_api_key: str
) -> None:
    requests: list[httpx2.Request] = []
    ordinary_host = httpx2.URL(ordinary_origin).host

    class MixedNestedClient(httpx2.AsyncClient):
        def __init__(self) -> None:
            self.depth = 0
            self.ordinary: AsyncOpenAI | None = None
            self.protected: AsyncOpenAI | None = None
            super().__init__(transport=httpx2.MockTransport(lambda request: _record(requests, request)))

        @override
        async def send(self, request: httpx2.Request, **kwargs: Any) -> httpx2.Response:
            if request.url.host == "mtls.api.openai.com" and self.depth == 0 and self.ordinary is not None:
                self.depth = 1
                await self.ordinary.models.list()
            elif request.url.host == ordinary_host and self.depth == 1 and self.protected is not None:
                self.depth = 2
                await self.protected.models.list()
            elif request.url.host == "mtls.api.openai.com" and self.depth == 2:
                request = httpx2.Request(
                    request.method, "https://attacker.invalid/capture", headers=dict(request.headers)
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
