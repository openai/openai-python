from __future__ import annotations

import threading
from typing import Any
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing_extensions import override

import httpx2
import pytest
from websockets.http11 import Request, Response
from websockets.exceptions import InvalidStatus, SecurityError
from websockets.asyncio.client import connect
from websockets.asyncio.server import ServerConnection, serve
from websockets.datastructures import Headers

from openai import AzureOpenAI, AsyncAzureOpenAI
from openai.lib.azure import API_KEY_SENTINEL
from openai.lib._azure_websocket import _AzureWebSocketConnect


def azure_options(base_url: str, bearer: bool) -> dict[str, Any]:
    return {
        "api_key": API_KEY_SENTINEL if bearer else "fake-websocket-key",
        "azure_ad_token": "fake-websocket-token" if bearer else None,
        "azure_endpoint": "https://origin.test",
        "websocket_base_url": base_url,
        "api_version": "2024-01-01",
        "max_retries": 0,
    }


@pytest.fixture(autouse=True)
def no_proxies(monkeypatch: pytest.MonkeyPatch) -> None:
    for scheme in ("all", "http", "https", "ws", "wss", "socks"):
        monkeypatch.delenv(f"{scheme}_proxy", raising=False)
        monkeypatch.delenv(f"{scheme.upper()}_PROXY", raising=False)
    # Also bypass proxies discovered from platform settings, not just the env.
    monkeypatch.setenv("no_proxy", "*")
    monkeypatch.setenv("NO_PROXY", "*")


@pytest.mark.parametrize("beta", [False, True], ids=["stable", "beta"])
@pytest.mark.parametrize("bearer", [False, True], ids=["api-key", "bearer"])
@pytest.mark.parametrize("redirect", ["none", "same-origin", "cross-origin"])
async def test_async_azure_websocket_redirects(beta: bool, bearer: bool, redirect: str) -> None:
    if redirect == "same-origin" and not hasattr(connect, "process_redirect"):
        pytest.skip("This websockets version does not follow handshake redirects")

    source_headers: list[Headers] = []
    target_headers: list[Headers] = []

    async def connected(connection: ServerConnection) -> None:
        await connection.wait_closed()

    def record_target(_connection: ServerConnection, request: Request) -> None:
        target_headers.append(request.headers)

    async with serve(connected, "127.0.0.1", 0, process_request=record_target) as target:
        target_url = f"ws://127.0.0.1:{next(iter(target.sockets)).getsockname()[1]}/final"

        def process_source(_connection: ServerConnection, request: Request) -> Response | None:
            source_headers.append(request.headers)
            if redirect != "none" and request.path.startswith("/realtime?"):
                location = "/final" if redirect == "same-origin" else target_url
                return Response(302, "Found", Headers({"Location": location}))
            return None

        async with serve(connected, "127.0.0.1", 0, process_request=process_source) as source:
            base_url = f"ws://127.0.0.1:{next(iter(source.sockets)).getsockname()[1]}"
            async with AsyncAzureOpenAI(
                **azure_options(base_url, bearer), http_client=httpx2.AsyncClient(trust_env=False)
            ) as client:
                resource = client.beta.realtime if beta else client.realtime
                if redirect == "cross-origin":
                    expected = (
                        SecurityError if hasattr(connect, "process_redirect") else (InvalidStatus, ConnectionError)
                    )
                    with pytest.raises(expected):
                        async with resource.connect(model="fake-model"):
                            pytest.fail("Cross-origin redirect must not connect")
                else:
                    async with resource.connect(model="fake-model"):
                        pass

    assert len(source_headers) == (2 if redirect == "same-origin" else 1)
    assert target_headers == []
    for headers in source_headers:
        assert headers.get("api-key") == (None if bearer else "fake-websocket-key")
        assert headers.get("Authorization") == ("Bearer fake-websocket-token" if bearer else None)


@pytest.mark.parametrize("beta", [False, True], ids=["stable", "beta"])
@pytest.mark.parametrize("bearer", [False, True], ids=["api-key", "bearer"])
def test_sync_azure_websocket_does_not_follow_redirects(beta: bool, bearer: bool) -> None:
    received: list[tuple[str, str | None, str | None]] = []

    class RedirectHandler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_GET(self) -> None:
            received.append((self.path, self.headers.get("api-key"), self.headers.get("Authorization")))
            self.send_response(302)
            self.send_header("Location", "/final")
            self.send_header("Content-Length", "0")
            self.end_headers()

        @override
        def log_message(self, *_args: object, **_kwargs: object) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), RedirectHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        with AzureOpenAI(
            **azure_options(f"ws://127.0.0.1:{server.server_port}", bearer),
            http_client=httpx2.Client(trust_env=False),
        ) as client:
            resource = client.beta.realtime if beta else client.realtime
            with pytest.raises(InvalidStatus):
                with resource.connect(model="fake-model"):
                    pytest.fail("Synchronous WebSocket redirects must not connect")
    finally:
        server.shutdown()
        thread.join()
        server.server_close()

    assert len(received) == 1
    assert received[0][0].startswith("/realtime?")
    assert received[0][1:] == (
        None if bearer else "fake-websocket-key",
        "Bearer fake-websocket-token" if bearer else None,
    )


@pytest.mark.skipif(not hasattr(connect, "process_redirect"), reason="No automatic handshake redirects")
@pytest.mark.parametrize(
    "target,allowed",
    [
        ("/final", True),
        ("wss://ORIGIN.test:443/final", True),
        ("wss://other.test/final", False),
        ("wss://origin.test:444/final", False),
        ("ws://origin.test/final", False),
    ],
)
def test_websocket_redirect_origin(target: str, allowed: bool) -> None:
    connection = _AzureWebSocketConnect("wss://origin.test/realtime")
    result = connection.process_redirect(InvalidStatus(Response(302, "Found", Headers({"Location": target}))))
    assert isinstance(result, str) is allowed
    if not allowed:
        assert isinstance(result, SecurityError)


@pytest.mark.skipif(not hasattr(connect, "process_redirect"), reason="No automatic handshake redirects")
def test_websocket_non_redirect_error_is_preserved() -> None:
    error = InvalidStatus(Response(401, "Unauthorized", Headers()))
    assert _AzureWebSocketConnect("wss://origin.test/realtime").process_redirect(error) is error
