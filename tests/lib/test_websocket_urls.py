from __future__ import annotations

from typing import Any
from urllib.parse import parse_qs, urlsplit

import httpx2
import pytest
from websockets.sync.server import ServerConnection

from openai import OpenAI, AsyncOpenAI, AzureOpenAI, AsyncAzureOpenAI

from .test_websocket_redirects import resource, reconnect
from .responses.test_websocket_session import script_server


@pytest.fixture(autouse=True)
def bypass_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("with_query", [False, True], ids=["query-free", "with-query"])
@pytest.mark.parametrize(
    "name,source,endpoint",
    [
        ("responses", "rest", "/responses"),
        ("beta.responses", "rest", "/responses"),
        ("responses", "websocket", "/responses"),
        ("beta.responses", "websocket", "/responses"),
        ("realtime", "websocket", "/realtime"),
        ("beta.realtime", "websocket", "/realtime"),
        ("live", "websocket", "/live/sessions"),
        ("live.sideband", "websocket", "/live/sessions/fake-session/attach"),
        ("live.forks", "websocket", "/live/sessions/fake-session/fork"),
        ("realtime", "azure", "/realtime"),
        ("beta.realtime", "azure", "/realtime"),
    ],
)
async def test_actual_upgrade_target(mode: str, with_query: bool, name: str, source: str, endpoint: str) -> None:
    received: list[str] = []
    # The legacy beta Realtime API has no reconnect contract.
    handshakes = 1 if name == "beta.realtime" else 2

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        received.append(socket.request.path)
        if source == "azure":
            assert socket.request.headers.get_all("api-key") == ["fake-websocket-url-test-key"]
        socket.send('{"type":"response.future"}')
        if len(received) < handshakes:
            socket.close(code=1011)

    with script_server(script, expected_connections=handshakes) as url:
        host = url.rsplit("/", 1)[0]
        query = "?route=x&route=y&priority=url&selected=url" if with_query else ""
        client_options: dict[str, Any] = {"api_key": "fake-websocket-url-test-key"}
        connect_options: dict[str, Any] = {}
        if source == "rest":
            client_options["base_url"] = host + "/customer" + query
        else:
            # None of this REST URL query belongs to the selected WebSocket URL.
            client_options["base_url"] = host + "/rest" + ("?rest_only=never" if with_query else "")
            client_options["websocket_base_url"] = host.replace("http:", "ws:") + "/customer" + query

        if with_query:
            client_options["default_query"] = {"priority": "default", "selected": "default", "client": "kept"}
            connect_options["extra_query"] = {"priority": "connection", "request": "kept"}
        if source == "azure":
            client_options.update(api_version="fake-version")
            if with_query:
                connect_options["extra_query"].update({"api-version": "ignored", "deployment": "ignored"})
        if "realtime" in name:
            connect_options["model"] = "fake-model"
        if name.startswith("live."):
            connect_options["session_id"] = "fake-session"
        if handshakes > 1:
            connect_options.update(on_reconnecting=reconnect, initial_delay=0, max_retries=1)

        if mode == "sync":
            client_class = AzureOpenAI if source == "azure" else OpenAI
            with client_class(**client_options, http_client=httpx2.Client(trust_env=False)) as client:
                with resource(client, name).connect(**connect_options) as connection:
                    events = iter(connection)
                    for _ in range(handshakes):
                        assert next(events).type == "response.future"
        else:
            async_client_class = AsyncAzureOpenAI if source == "azure" else AsyncOpenAI
            async with async_client_class(
                **client_options, http_client=httpx2.AsyncClient(trust_env=False)
            ) as async_client:
                async with resource(async_client, name).connect(**connect_options) as async_connection:
                    async_events = aiter(async_connection)
                    for _ in range(handshakes):
                        assert (await anext(async_events)).type == "response.future"

    expected: dict[str, list[str]] = {}
    if with_query:
        expected.update(route=["x", "y"], priority=["connection"], selected=["url"], client=["kept"], request=["kept"])
    if source == "azure":
        expected.update({"api-version": ["fake-version"], "deployment": ["fake-model"]})
    elif "realtime" in name:
        expected["model"] = ["fake-model"]
    for target in received:
        split = urlsplit(target)
        assert split.path == "/customer" + endpoint
        assert parse_qs(split.query) == expected
