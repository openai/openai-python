from __future__ import annotations

import asyncio
import threading
from typing import cast
from contextlib import nullcontext
from contextvars import ContextVar
from typing_extensions import override

import httpx2
import pytest
from websockets.sync.server import ServerConnection

from openai import AzureOpenAI, AsyncAzureOpenAI
from openai._types import Omit

from .responses.test_websocket_session import script_server


@pytest.fixture(autouse=True)
def bypass_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    # WebSocket traffic must remain on the test's loopback server.
    for scheme in ("all", "http", "https", "ws", "wss", "socks"):
        monkeypatch.delenv(f"{scheme}_proxy", raising=False)
        monkeypatch.delenv(f"{scheme.upper()}_PROXY", raising=False)
    monkeypatch.setenv("NO_PROXY", "*")
    monkeypatch.setenv("no_proxy", "*")


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("route", ["http", "realtime"])
async def test_azure_overlapping_requests_keep_their_callable_keys(mode: str, route: str) -> None:
    await check_azure_overlapping_requests(mode, route, first_key="fake-azure-key-A")


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_empty_azure_key_never_borrows_another_request_key(mode: str) -> None:
    await check_azure_overlapping_requests(
        mode, "http", first_key="", default_headers={"Authorization": "Bearer fake-default"}
    )


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_empty_azure_realtime_key_never_borrows_another_request_key(mode: str) -> None:
    await check_azure_overlapping_requests(mode, "realtime", first_key="")


async def check_azure_overlapping_requests(
    mode: str, route: str, *, first_key: str, default_headers: dict[str, str] | None = None
) -> None:
    caller: ContextVar[str] = ContextVar("azure_credential_caller", default="")
    a_refreshed = threading.Event()
    b_finished = threading.Event()
    provider_calls: list[str] = []
    received: dict[str, tuple[list[str], list[str]]] = {}

    def key() -> str:
        label = caller.get()
        provider_calls.append(label)
        return first_key if label == "A" else "fake-azure-key-B"

    async def async_key() -> str:
        await asyncio.sleep(0)
        return key()

    # Schedule B after A has obtained its key but before A builds HTTP or
    # WebSocket headers. Neither hook replaces the SDK's value or state.
    class SyncClient(AzureOpenAI):
        @override
        def _refresh_api_key(self) -> str:
            resolved = super()._refresh_api_key()
            if caller.get() == "A":
                a_refreshed.set()
                assert b_finished.wait(5), "B did not finish before A resumed"
            return resolved

    class AsyncClient(AsyncAzureOpenAI):
        @override
        async def _refresh_api_key(self) -> str:
            resolved = await super()._refresh_api_key()
            if caller.get() == "A":
                a_refreshed.set()
                assert await asyncio.to_thread(b_finished.wait, 5), "B did not finish before A resumed"
            return resolved

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        headers = socket.request.headers
        received[headers["X-Test-Caller"]] = (headers.get_all("api-key"), headers.get_all("Authorization"))
        socket.send('{"type":"audit.future.event"}')

    def http_handler(request: httpx2.Request) -> httpx2.Response:
        headers = request.headers
        received[headers["X-Test-Caller"]] = (headers.get_list("api-key"), headers.get_list("Authorization"))
        return httpx2.Response(200, json={"object": "list", "data": [], "has_more": False})

    def call_sync(client: AzureOpenAI, label: str) -> None:
        headers = {"X-Test-Caller": label}
        if route == "http":
            client.models.list(extra_headers=headers)
        else:
            with client.realtime.connect(model="fake-deployment", extra_headers=headers) as connection:
                assert connection.recv().type == "audit.future.event"

    async def call_async(client: AsyncAzureOpenAI, label: str) -> None:
        headers = {"X-Test-Caller": label}
        if route == "http":
            await client.models.list(extra_headers=headers)
        else:
            async with client.realtime.connect(model="fake-deployment", extra_headers=headers) as connection:
                assert (await connection.recv()).type == "audit.future.event"

    async def run_calls(client: AzureOpenAI | AsyncAzureOpenAI) -> None:
        async def call(label: str) -> None:
            token = caller.set(label)
            try:
                if isinstance(client, AsyncAzureOpenAI):
                    await call_async(client, label)
                else:
                    await asyncio.to_thread(call_sync, client, label)
            finally:
                caller.reset(token)
                if label == "B":
                    b_finished.set()

        first = asyncio.create_task(call("A"))
        try:
            assert await asyncio.to_thread(a_refreshed.wait, 5), "A never resolved its callable key"
            await asyncio.wait_for(call("B"), 8)
            await asyncio.wait_for(first, 8)
        finally:
            b_finished.set()
            if not first.done():
                await asyncio.wait_for(first, 8)

    # Only WebSocket cases open a server. HTTP uses MockTransport without DNS
    # resolution. The Azure endpoint and every credential are fake.
    server = nullcontext("ws://127.0.0.1:1") if route == "http" else script_server(script, expected_connections=2)
    with server as url:
        transport = httpx2.MockTransport(http_handler)
        ws_url = httpx2.URL(url).copy_with(scheme="ws")
        if mode == "sync":
            with SyncClient(
                azure_endpoint="https://azure.test",
                api_version="2024-02-01",
                api_key=key,
                default_headers=default_headers,
                websocket_base_url=ws_url,
                max_retries=0,
                http_client=httpx2.Client(transport=transport, trust_env=False),
            ) as client:
                await run_calls(client)
        else:
            async with AsyncClient(
                azure_endpoint="https://azure.test",
                api_version="2024-02-01",
                api_key=async_key,
                default_headers=default_headers,
                websocket_base_url=ws_url,
                max_retries=0,
                http_client=httpx2.AsyncClient(transport=transport, trust_env=False),
            ) as async_client:
                await run_calls(async_client)

    assert provider_calls == ["A", "B"]
    authorization = [] if default_headers is None else ["Bearer fake-default"]
    assert received == {
        "A": ([first_key] if first_key else [], authorization),
        "B": (["fake-azure-key-B"], authorization),
    }


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("omitted_header", ["Authorization", "api-key"])
async def test_empty_azure_key_with_omitted_default_still_validates_credentials(mode: str, omitted_header: str) -> None:
    calls = 0

    def key() -> str:
        nonlocal calls
        calls += 1
        return ""

    async def async_key() -> str:
        return key()

    def unexpected_request(_: httpx2.Request) -> httpx2.Response:
        pytest.fail("Azure must validate missing credentials before sending the HTTP request")

    transport = httpx2.MockTransport(unexpected_request)
    # Omit in client defaults is deliberately runtime-only, outside the public
    # Mapping[str, str] signature. Preserve its existing credential validation.
    default_headers = cast("dict[str, str]", {omitted_header: Omit()})
    if mode == "sync":
        with AzureOpenAI(
            azure_endpoint="https://azure.test",
            api_version="2024-02-01",
            api_key=key,
            default_headers=default_headers,
            max_retries=0,
            http_client=httpx2.Client(transport=transport, trust_env=False),
        ) as client:
            with pytest.raises(TypeError, match="Could not resolve authentication"):
                client.models.list()
    else:
        async with AsyncAzureOpenAI(
            azure_endpoint="https://azure.test",
            api_version="2024-02-01",
            api_key=async_key,
            default_headers=default_headers,
            max_retries=0,
            http_client=httpx2.AsyncClient(transport=transport, trust_env=False),
        ) as async_client:
            with pytest.raises(TypeError, match="Could not resolve authentication"):
                await async_client.models.list()

    assert calls == 1
