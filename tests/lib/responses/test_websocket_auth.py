from __future__ import annotations

import json
import asyncio
from typing import Any
from typing_extensions import override

import httpx2
import pytest
from websockets.sync.server import ServerConnection
from websockets.datastructures import Headers as WebSocketHeaders

from openai import OpenAI, AsyncOpenAI, OpenAIError, omit
from openai.auth import WorkloadIdentity
from openai._types import Headers
from openai._models import FinalRequestOptions
from openai.providers import bedrock
from openai.types.websocket_reconnection import ReconnectingEvent

from .test_websocket_session import script_server, response_event


@pytest.fixture(autouse=True)
def bypass_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("authorization", ["provider", "cached_provider", "client", "connection", "omit"])
async def test_callable_auth_refreshes_each_physical_handshake(mode: str, authorization: str) -> None:
    calls: list[str] = []
    received: list[WebSocketHeaders] = []

    def provider() -> str:
        token = f"fake-provider-key-{len(calls) + 1}"
        calls.append(token)
        return token

    async def async_provider() -> str:
        await asyncio.sleep(0)
        return provider()

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        received.append(socket.request.headers)
        socket.send(json.dumps({"type": "response.future", "handshake": len(received)}))
        if len(received) == 1:
            socket.close(code=1011)

    def http_handler(request: httpx2.Request) -> httpx2.Response:
        assert request.headers["Authorization"] == "Bearer fake-provider-key-1"
        return httpx2.Response(200, json=response_event("completed")["response"])

    client_headers = {"X-Customer-Header": "client value", "X-Client-Only": "retained", "X-Omit-Me": "removed"}
    connection_headers: Headers = {"x-customer-header": "connection value", "x-omit-me": omit}
    if authorization in {"client", "connection"}:
        client_headers["authorization"] = "Bearer fake-client-override"
    if authorization == "connection":
        connection_headers["AUTHORIZATION"] = "Bearer fake-connection-override"
    elif authorization == "omit":
        connection_headers["authorization"] = omit

    def reconnect(_event: ReconnectingEvent) -> None:
        return None

    options: dict[str, Any] = {
        "extra_headers": connection_headers,
        "on_reconnecting": reconnect,
        "initial_delay": 0,
        "max_retries": 1,
    }
    with script_server(script, expected_connections=2) as url:
        if mode == "sync":
            with OpenAI(
                api_key=provider,
                base_url=url,
                default_headers=client_headers,
                http_client=httpx2.Client(transport=httpx2.MockTransport(http_handler), trust_env=False),
            ) as client:
                if authorization == "cached_provider":
                    client.responses.create(model="gpt-4o-mini", input="synthetic")
                with client.responses.connect(**options) as connection:
                    events = iter(connection)
                    assert next(events).type == "response.future"
                    assert next(events).type == "response.future"
        else:
            async with AsyncOpenAI(
                api_key=async_provider,
                base_url=url,
                default_headers=client_headers,
                http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(http_handler), trust_env=False),
            ) as async_client:
                if authorization == "cached_provider":
                    await async_client.responses.create(model="gpt-4o-mini", input="synthetic")
                async with async_client.responses.connect(**options) as async_connection:
                    async_events = aiter(async_connection)
                    assert (await anext(async_events)).type == "response.future"
                    assert (await anext(async_events)).type == "response.future"

    offset = 1 if authorization == "cached_provider" else 0
    assert len(calls) == offset + 2
    for index, headers in enumerate(received):
        expected_auth = {
            "client": "Bearer fake-client-override",
            "connection": "Bearer fake-connection-override",
            "omit": None,
        }.get(authorization, f"Bearer fake-provider-key-{offset + index + 1}")
        assert headers.get_all("Authorization") == ([expected_auth] if expected_auth is not None else [])
        assert headers.get_all("X-Customer-Header") == ["connection value"]
        assert headers["X-Client-Only"] == "retained"
        assert "X-Omit-Me" not in headers


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_handshake_honors_prepared_url_query_and_headers(mode: str) -> None:
    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        assert socket.request.path == "/prepared?before=kept&prepared=yes"
        assert socket.request.headers["X-Prepared"] == "hook value"
        assert socket.request.headers["Authorization"] == "Bearer fake-hook-key"
        assert "X-Removed" not in socket.request.headers
        socket.send(json.dumps({"type": "response.future"}))

    with script_server(script) as url:

        def prepare(options: FinalRequestOptions) -> FinalRequestOptions:
            assert options.method == "get"
            assert options.security == {"bearer_auth": True}
            assert options.url.startswith("ws://127.0.0.1:1/")
            options.url = url.removesuffix("/v1") + "/prepared?before=kept"
            options.params = {"prepared": "yes"}
            options.headers = {"X-Prepared": "hook value", "X-Removed": omit}
            return options

        class PreparedClient(OpenAI):
            @override
            def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
                return prepare(super()._prepare_options(options))

        class AsyncPreparedClient(AsyncOpenAI):
            @override
            async def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
                return prepare(await super()._prepare_options(options))

        if mode == "sync":
            with PreparedClient(
                api_key="fake-hook-key",
                base_url="http://127.0.0.1:1/v1",
                default_headers={"X-Removed": "client value"},
                http_client=httpx2.Client(trust_env=False),
            ) as client:
                with client.responses.connect() as connection:
                    assert connection.recv().type == "response.future"
        else:
            async with AsyncPreparedClient(
                api_key="fake-hook-key",
                base_url="http://127.0.0.1:1/v1",
                default_headers={"X-Removed": "client value"},
                http_client=httpx2.AsyncClient(trust_env=False),
            ) as async_client:
                async with async_client.responses.connect() as async_connection:
                    assert (await async_connection.recv()).type == "response.future"


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("authentication", ["provider", "workload_identity"])
async def test_http_only_auth_refused_before_credentials_or_transport(mode: str, authentication: str) -> None:
    credential_calls: list[bool] = []

    def forbidden_provider() -> str:
        credential_calls.append(True)
        raise AssertionError("WebSocket must refuse HTTP-only authentication before credential resolution")

    auth: dict[str, Any]
    if authentication == "provider":
        auth = {"provider": bedrock(region="us-east-1", token_provider=forbidden_provider)}
    else:
        auth = {
            "workload_identity": WorkloadIdentity(
                identity_provider_id="idp_synthetic",
                service_account_id="sa_synthetic",
                provider={"token_type": "jwt", "get_token": forbidden_provider},
            )
        }

    with script_server(lambda _: None, expected_connections=0) as url:
        if mode == "sync":
            with OpenAI(**auth, websocket_base_url=url, http_client=httpx2.Client(trust_env=False)) as client:
                with pytest.raises(OpenAIError, match="not supported by WebSocket"):
                    with client.responses.connect():
                        pytest.fail("Unsupported authentication opened a socket")
        else:
            async with AsyncOpenAI(
                **auth, websocket_base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as async_client:
                with pytest.raises(OpenAIError, match="not supported by WebSocket"):
                    async with async_client.responses.connect():
                        pytest.fail("Unsupported authentication opened a socket")
    assert not credential_calls
