from __future__ import annotations

import asyncio
import threading
from contextlib import nullcontext
from contextvars import ContextVar
from typing_extensions import override

import httpx2
import pytest
from websockets.sync.server import ServerConnection

from openai import OpenAI, AsyncOpenAI
from openai._models import FinalRequestOptions
from tests.api_resources._websocket_resources import WEBSOCKET_RESOURCES

from .test_websocket_redirects import options, resource
from .responses.test_websocket_session import script_server


@pytest.fixture(autouse=True)
def bypass_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("name", ["http", *WEBSOCKET_RESOURCES])
async def test_request_keeps_its_callable_credential(mode: str, name: str) -> None:
    await check_two_requests(mode, name, first_key="fake-key-A")


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("name", ["http", "responses"])
async def test_empty_credential_never_borrows_another_request_key(mode: str, name: str) -> None:
    await check_two_requests(mode, name, first_key="")


async def check_two_requests(mode: str, name: str, *, first_key: str) -> None:
    # The prepare hook models another request finishing after refresh and before
    # this one builds its headers. Async hooks may legitimately yield here too.
    caller = ContextVar("credential_test_caller", default="")
    a_prepared = threading.Event()
    b_finished = threading.Event()
    provider_calls: list[str] = []
    received: dict[str, list[str]] = {}

    def provider() -> str:
        label = caller.get()
        provider_calls.append(label)
        return first_key if label == "A" else "fake-key-B"

    async def async_provider() -> str:
        await asyncio.sleep(0)
        return provider()

    class PreparedClient(OpenAI):
        @override
        def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
            prepared = super()._prepare_options(options)
            if caller.get() == "A":
                a_prepared.set()
                assert b_finished.wait(5), "B did not finish while A was paused"
            return prepared

    class AsyncPreparedClient(AsyncOpenAI):
        @override
        async def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
            prepared = await super()._prepare_options(options)
            if caller.get() == "A":
                a_prepared.set()
                assert await asyncio.to_thread(b_finished.wait, 5), "B did not finish while A was paused"
            return prepared

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        headers = socket.request.headers
        received[headers["X-Test-Caller"]] = headers.get_all("Authorization")
        # Receipt before recv completes ensures B reached the actual server.
        socket.send('{"type":"response.future"}')

    def http_handler(request: httpx2.Request) -> httpx2.Response:
        received[request.headers["X-Test-Caller"]] = request.headers.get_list("Authorization")
        return httpx2.Response(200, json={"object": "list", "data": [], "has_more": False})

    def request_sync(client: OpenAI, label: str) -> None:
        headers = {"X-Test-Caller": label}
        if name == "http":
            if label == "A" and not first_key:
                with pytest.raises(TypeError, match="Could not resolve authentication"):
                    client.models.list(extra_headers=headers)
            else:
                client.models.list(extra_headers=headers)
        else:
            connect_options = options(client, name)
            connect_options["extra_headers"] = headers
            with resource(client, name).connect(**connect_options) as connection:
                assert connection.recv().type == "response.future"

    async def request_async(client: AsyncOpenAI, label: str) -> None:
        headers = {"X-Test-Caller": label}
        if name == "http":
            if label == "A" and not first_key:
                with pytest.raises(TypeError, match="Could not resolve authentication"):
                    await client.models.list(extra_headers=headers)
            else:
                await client.models.list(extra_headers=headers)
        else:
            connect_options = options(client, name)
            connect_options["extra_headers"] = headers
            async with resource(client, name).connect(**connect_options) as connection:
                assert (await connection.recv()).type == "response.future"

    async def run_requests(client: OpenAI | AsyncOpenAI) -> None:
        async def call(label: str) -> None:
            token = caller.set(label)
            try:
                if isinstance(client, AsyncOpenAI):
                    await request_async(client, label)
                else:
                    await asyncio.to_thread(request_sync, client, label)
            finally:
                caller.reset(token)
                if label == "B":
                    b_finished.set()
                else:
                    # An empty HTTP credential may be rejected in super()
                    # before the hook reaches its pause. That is valid too.
                    a_prepared.set()

        first = asyncio.create_task(call("A"))
        try:
            assert await asyncio.to_thread(a_prepared.wait, 5), "A never prepared its request"
            await asyncio.wait_for(call("B"), 8)
            await asyncio.wait_for(first, 8)
        finally:
            b_finished.set()
            if not first.done():
                await asyncio.wait_for(first, 8)

    server = nullcontext("http://127.0.0.1:1/v1") if name == "http" else script_server(script, expected_connections=2)
    with server as url:
        transport = httpx2.MockTransport(http_handler)
        if mode == "sync":
            with PreparedClient(
                api_key=provider,
                base_url=url,
                http_client=httpx2.Client(transport=transport, trust_env=False),
            ) as client:
                await run_requests(client)
        else:
            async with AsyncPreparedClient(
                api_key=async_provider,
                base_url=url,
                http_client=httpx2.AsyncClient(transport=transport, trust_env=False),
            ) as async_client:
                await run_requests(async_client)

    assert provider_calls == ["A", "B"]
    if first_key:
        assert received == {"A": [f"Bearer {first_key}"], "B": ["Bearer fake-key-B"]}
    elif name == "http":
        assert received == {"B": ["Bearer fake-key-B"]}
    else:
        assert received == {"A": [], "B": ["Bearer fake-key-B"]}


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("name", ["http", "responses"])
@pytest.mark.parametrize("position", ["client", "request"])
@pytest.mark.parametrize(
    "keys",
    [("authorization", "Authorization"), ("Authorization", "authorization")],
    ids=["lower-then-title", "title-then-lower"],
)
async def test_callable_preserves_explicit_case_order(
    mode: str, name: str, position: str, keys: tuple[str, str]
) -> None:
    received: list[list[str]] = []
    # HTTP header names are case-insensitive; keep the normal last-wins order
    # even when bearer authentication is supplied by a callable.
    explicit = {keys[0]: "Bearer fake-first", keys[1]: "Bearer fake-last"}
    defaults = explicit if position == "client" else {}
    per_request = explicit if position == "request" else {}

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        received.append(socket.request.headers.get_all("Authorization"))
        socket.send('{"type":"response.future"}')

    def http_handler(request: httpx2.Request) -> httpx2.Response:
        received.append(request.headers.get_list("Authorization"))
        return httpx2.Response(200, json={"object": "list", "data": [], "has_more": False})

    async def async_provider() -> str:
        return "fake-provider"

    server = nullcontext("http://127.0.0.1:1/v1") if name == "http" else script_server(script)
    with server as url:
        transport = httpx2.MockTransport(http_handler)
        if mode == "sync":
            with OpenAI(
                api_key=lambda: "fake-provider",
                base_url=url,
                default_headers=defaults,
                http_client=httpx2.Client(transport=transport, trust_env=False),
            ) as client:
                if name == "http":
                    client.models.list(extra_headers=per_request)
                else:
                    with client.responses.connect(extra_headers=per_request) as connection:
                        assert connection.recv().type == "response.future"
        else:
            async with AsyncOpenAI(
                api_key=async_provider,
                base_url=url,
                default_headers=defaults,
                http_client=httpx2.AsyncClient(transport=transport, trust_env=False),
            ) as async_client:
                if name == "http":
                    await async_client.models.list(extra_headers=per_request)
                else:
                    async with async_client.responses.connect(extra_headers=per_request) as async_connection:
                        assert (await async_connection.recv()).type == "response.future"

    assert received == [["Bearer fake-last"]]


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_prepare_hook_can_supply_missing_callable_auth(mode: str) -> None:
    received: list[list[str]] = []

    def http_handler(request: httpx2.Request) -> httpx2.Response:
        received.append(request.headers.get_list("Authorization"))
        return httpx2.Response(200, json={"object": "list", "data": [], "has_more": False})

    class PreparedClient(OpenAI):
        @override
        def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
            options = super()._prepare_options(options)
            options.headers = {"Authorization": "Bearer fake-hook-value"}
            return options

    class AsyncPreparedClient(AsyncOpenAI):
        @override
        async def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
            options = await super()._prepare_options(options)
            options.headers = {"Authorization": "Bearer fake-hook-value"}
            return options

    async def async_provider() -> str:
        return ""

    transport = httpx2.MockTransport(http_handler)
    if mode == "sync":
        with PreparedClient(
            api_key=lambda: "",
            base_url="http://127.0.0.1:1/v1",
            http_client=httpx2.Client(transport=transport, trust_env=False),
        ) as client:
            client.models.list()
    else:
        async with AsyncPreparedClient(
            api_key=async_provider,
            base_url="http://127.0.0.1:1/v1",
            http_client=httpx2.AsyncClient(transport=transport, trust_env=False),
        ) as async_client:
            await async_client.models.list()

    assert received == [["Bearer fake-hook-value"]]
