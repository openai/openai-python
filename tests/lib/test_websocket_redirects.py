from __future__ import annotations

import asyncio
from typing import Any, Callable
from unittest.mock import Mock, AsyncMock

import httpx2
import pytest
from websockets.uri import WebSocketURI
from websockets.http11 import Response
from websockets.exceptions import InvalidStatus, SecurityError
from websockets.asyncio.client import connect
from websockets.datastructures import Headers, HeadersLike

from openai import OpenAI, AsyncOpenAI, AsyncAzureOpenAI
from openai.lib._websocket import _WebSocketConnect
from openai.types.websocket_reconnection import ReconnectingEvent

RESOURCES = ["realtime", "beta.realtime", "responses", "beta.responses"]
RECONNECTING_RESOURCES = [name for name in RESOURCES if name != "beta.realtime"]
EXTRA_HEADERS = {"api-key": "fake-key", "Cookie": "fake-cookie", "X-Custom": "fake-private-header"}
FOLLOWS_REDIRECTS = hasattr(connect, "process_redirect")


def unexpected_http(_request: httpx2.Request) -> httpx2.Response:
    pytest.fail("Unexpected HTTP request")


def async_http_client() -> httpx2.AsyncClient:
    return httpx2.AsyncClient(transport=httpx2.MockTransport(unexpected_http))


def resource(client: Any, name: str) -> Any:
    for part in name.split("."):
        client = getattr(client, part)
    return client


def options(name: str) -> dict[str, Any]:
    return {"extra_headers": EXTRA_HEADERS, **({"model": "fake-model"} if name.endswith("realtime") else {})}


def redirect_error(location: str) -> InvalidStatus:
    return InvalidStatus(Response(302, "Found", Headers({"Location": location})))


def no_proxy(_uri: WebSocketURI) -> None:
    return None


def reconnect(_event: ReconnectingEvent) -> None:
    return None


class Handshakes:
    """Exercise the installed connector's handshake loop without opening sockets."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch, redirects: list[str | None]) -> None:
        self.redirects = iter(redirects)
        self.attempts: list[tuple[WebSocketURI, Headers]] = []
        self.sent: list[tuple[WebSocketURI, str]] = []
        monkeypatch.setattr(asyncio.get_running_loop(), "create_connection", self.create_connection)
        # websockets 15 can discover proxies before reaching create_connection.
        monkeypatch.setattr("websockets.asyncio.client.get_proxy", no_proxy, raising=False)

    async def create_connection(self, factory: Callable[[], Any], **_kwargs: Any) -> tuple[Mock, Mock]:
        protocol = factory().protocol
        # The Sans-I/O protocol renamed wsuri to uri in websockets 15.
        uri: WebSocketURI = protocol.uri if hasattr(protocol, "uri") else protocol.wsuri
        websocket = Mock()

        async def handshake(headers: HeadersLike | None, _user_agent: str | None) -> None:
            self.attempts.append((uri, Headers(headers or {})))
            location = next(self.redirects)
            if location is not None:
                raise redirect_error(location)

        async def send(data: str) -> None:
            self.sent.append((uri, data))

        websocket.handshake = AsyncMock(side_effect=handshake)
        websocket.send = AsyncMock(side_effect=send)
        websocket.close = AsyncMock()
        return websocket.transport, websocket


@pytest.mark.parametrize("name", RESOURCES)
@pytest.mark.parametrize(
    "base,target,allowed",
    [
        ("wss://origin.test", None, True),
        ("wss://origin.test", "/final", True),
        ("wss://origin.test", "wss://ORIGIN.test:443/final", True),
        ("wss://origin.test", "wss://other.test/final", False),
        ("wss://origin.test", "//other.test/final", False),
        ("wss://origin.test", "wss://origin.test:444/final", False),
        ("wss://origin.test", "ws://origin.test/final", False),
        ("ws://origin.test", "wss://origin.test/final", False),
    ],
)
async def test_async_websocket_redirects(
    monkeypatch: pytest.MonkeyPatch, name: str, base: str, target: str | None, allowed: bool
) -> None:
    handshakes = Handshakes(monkeypatch, [target, None])
    succeeds = allowed and (target is None or FOLLOWS_REDIRECTS)
    async with AsyncOpenAI(
        api_key="fake-entra-token",
        websocket_base_url=base,
        http_client=async_http_client(),
    ) as client:
        manager = resource(client, name).connect(**options(name))
        if name in RECONNECTING_RESOURCES:
            manager.send({"type": "response.create"})
        if succeeds:
            async with manager as connection:
                await connection.send({"type": "response.create"})
        else:
            expected = SecurityError if FOLLOWS_REDIRECTS else InvalidStatus
            with pytest.raises(expected):
                async with manager:
                    pytest.fail("Unexpected connection")

    assert len(handshakes.attempts) == (2 if succeeds and target else 1)
    for uri, headers in handshakes.attempts:
        assert (uri.secure, uri.host, uri.port) == (
            base.startswith("wss:"),
            "origin.test",
            443 if base.startswith("wss:") else 80,
        )
        assert headers["Authorization"] == "Bearer fake-entra-token"
        for key, value in EXTRA_HEADERS.items():
            assert headers[key] == value
    assert bool(handshakes.sent) is succeeds
    assert all(uri.host == "origin.test" for uri, _ in handshakes.sent)


@pytest.mark.skipif(not FOLLOWS_REDIRECTS, reason="No automatic handshake redirects")
@pytest.mark.parametrize("name", RESOURCES)
async def test_later_cross_origin_redirect_is_rejected(monkeypatch: pytest.MonkeyPatch, name: str) -> None:
    handshakes = Handshakes(monkeypatch, ["/intermediate", "wss://other.test/final", None])
    async with AsyncOpenAI(
        api_key="fake-key", websocket_base_url="wss://origin.test", http_client=async_http_client()
    ) as client:
        with pytest.raises(SecurityError):
            async with resource(client, name).connect(**options(name)):
                pytest.fail("Unexpected connection")
    assert len(handshakes.attempts) == 2
    assert all(uri.host == "origin.test" for uri, _ in handshakes.attempts)
    assert handshakes.sent == []


@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
@pytest.mark.parametrize(
    "target", ["/final", "wss://other.test/final", "wss://origin.test:444/final", "ws://origin.test/final"]
)
async def test_async_websocket_reconnect_redirects(monkeypatch: pytest.MonkeyPatch, name: str, target: str) -> None:
    handshakes = Handshakes(monkeypatch, [None, target, None])
    succeeds = target == "/final" and FOLLOWS_REDIRECTS
    async with AsyncOpenAI(
        api_key="fake-key", websocket_base_url="wss://origin.test", http_client=async_http_client()
    ) as client:
        manager = resource(client, name).connect(
            **options(name), on_reconnecting=reconnect, initial_delay=0, max_retries=1
        )
        async with manager as connection:
            connection._send_queue.enqueue("fake-queued-message")
            assert await connection._reconnect(RuntimeError("fake disconnect")) is succeeds
            assert (connection._send_queue._bytes == 0) is succeeds

    assert len(handshakes.attempts) == (3 if succeeds else 2)
    assert all((uri.secure, uri.host, uri.port) == (True, "origin.test", 443) for uri, _ in handshakes.attempts)
    assert [data for _, data in handshakes.sent] == (["fake-queued-message"] if succeeds else [])
    for _, headers in handshakes.attempts:
        assert headers["Authorization"] == "Bearer fake-key"


@pytest.mark.parametrize("name", ["realtime", "beta.realtime"])
@pytest.mark.parametrize("target", ["/final", "wss://other.test/final"])
async def test_async_azure_guard_is_preserved(monkeypatch: pytest.MonkeyPatch, name: str, target: str) -> None:
    handshakes = Handshakes(monkeypatch, [target, None])
    succeeds = target == "/final" and FOLLOWS_REDIRECTS
    async with AsyncAzureOpenAI(
        api_key="fake-key",
        azure_endpoint="https://origin.test",
        api_version="2024-01-01",
        http_client=async_http_client(),
    ) as client:
        manager = resource(client, name).connect(model="fake-model")
        if succeeds:
            async with manager:
                pass
        else:
            expected = SecurityError if FOLLOWS_REDIRECTS else InvalidStatus
            with pytest.raises(expected):
                async with manager:
                    pytest.fail("Unexpected connection")
    assert len(handshakes.attempts) == (2 if succeeds else 1)
    assert all(uri.host == "origin.test" and headers["api-key"] == "fake-key" for uri, headers in handshakes.attempts)


@pytest.mark.parametrize("name", RESOURCES)
def test_sync_websocket_connector_is_unchanged(monkeypatch: pytest.MonkeyPatch, name: str) -> None:
    websocket = Mock()
    connect_mock = Mock(return_value=websocket)
    monkeypatch.setattr("websockets.sync.client.connect", connect_mock)
    with OpenAI(
        api_key="fake-key",
        websocket_base_url="wss://origin.test",
        http_client=httpx2.Client(transport=httpx2.MockTransport(unexpected_http)),
    ) as client:
        with resource(client, name).connect(**options(name)):
            pass
        error = redirect_error("wss://other.test/final")
        connect_mock.side_effect = error
        with pytest.raises(InvalidStatus) as caught:
            with resource(client, name).connect(**options(name)):
                pytest.fail("Unexpected connection")
        assert caught.value is error
    assert connect_mock.call_count == 2
    assert connect_mock.call_args.kwargs["additional_headers"]["Authorization"] == "Bearer fake-key"


@pytest.mark.skipif(not FOLLOWS_REDIRECTS, reason="No automatic handshake redirects")
def test_non_redirect_error_is_preserved() -> None:
    error = InvalidStatus(Response(401, "Unauthorized", Headers()))
    assert _WebSocketConnect("wss://origin.test/realtime").process_redirect(error) is error
