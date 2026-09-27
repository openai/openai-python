from __future__ import annotations

import json
import asyncio
from urllib.parse import parse_qs, urlsplit

import httpx2
import pytest
from websockets.sync.server import ServerConnection

from openai import OpenAI, AsyncOpenAI
from openai.types.live import SessionStartedEvent, SessionUpdatedEvent, OutputTranscriptDeltaEvent
from openai.resources.live.live import LiveConnection, AsyncLiveConnection
from openai.resources.live.forks import ForksConnection, AsyncForksConnection

from ..responses.test_websocket_session import script_server


@pytest.fixture(autouse=True)
def bypass_loopback_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")


@pytest.mark.parametrize("role", ["primary", "fork", "sideband"])
@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("base_query", ["", "?tenant=sample"], ids=["custom-path", "custom-path-and-query"])
async def test_live_role_startup_and_routing(role: str, mode: str, base_query: str) -> None:
    session = {"id": "live_fixture", "model": "gpt-live-1", "status": "active", "expires_at": 123}

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        target = urlsplit(socket.request.path)
        expected_path = "/v1/customer/live/sessions"
        if role != "primary":
            expected_path += "/stored%20%2F%3F%23%25/" + ("fork" if role == "fork" else "attach")
        assert target.path == expected_path
        expected_query = {"trace": ["role-contract"]}
        if base_query:
            expected_query["tenant"] = ["sample"]
        if role == "sideband":
            expected_query["graceful_close"] = ["true"]
        assert parse_qs(target.query) == expected_query
        assert socket.request.headers.get_all("Authorization") == ["Bearer ek_fake_live"]

        if role == "sideband":
            # Attach is already active and need not send a fresh session.started.
            socket.send(
                json.dumps(
                    {
                        "type": "session.output_transcript.delta",
                        "event_id": "first",
                        "delta": "Attached",
                        "start_ms": 0,
                        "end_ms": 120,
                    }
                )
            )
        else:
            # This first and only start must come from the caller, with its identifier.
            expected_session = {"model": "gpt-live-1"} if role == "primary" else {}
            assert json.loads(socket.recv(timeout=5)) == {
                "type": "session.start",
                "event_id": "caller-start",
                "session": expected_session,
            }
            socket.send(
                json.dumps(
                    {
                        "type": "session.started",
                        "event_id": "started",
                        "client_event_id": "caller-start",
                        "session": session,
                    }
                )
            )

        assert json.loads(socket.recv(timeout=5)) == {
            "type": "session.update",
            "event_id": "caller-update",
            "session": {},
        }
        socket.send(
            json.dumps(
                {
                    "type": "session.updated",
                    "event_id": "updated",
                    "client_event_id": "caller-update",
                    "session": session,
                }
            )
        )
        # script_server also checks for extra sends, one socket, and caller close.

    with script_server(script) as url:
        base_url = f"{url}/customer{base_query}"
        extra_query = {"trace": "role-contract"}
        if mode == "sync":
            with OpenAI(
                api_key="ek_fake_live",
                base_url=base_url,
                http_client=httpx2.Client(trust_env=False),
            ) as client:
                if role == "primary":
                    manager = client.live.connect(extra_query=extra_query)
                elif role == "fork":
                    manager = client.live.forks.connect(session_id="stored /?#%", extra_query=extra_query)
                else:
                    manager = client.live.sideband.connect(
                        session_id="stored /?#%", graceful_close=True, extra_query=extra_query
                    )
                with manager as connection:
                    if isinstance(connection, LiveConnection):
                        connection.session.start(session={"model": "gpt-live-1"}, event_id="caller-start")
                    elif isinstance(connection, ForksConnection):
                        connection.session.start(session={}, event_id="caller-start")
                    first = connection.recv()
                    if role == "sideband":
                        assert isinstance(first, OutputTranscriptDeltaEvent)
                        assert first.delta == "Attached"
                    else:
                        assert isinstance(first, SessionStartedEvent)
                        assert first.client_event_id == "caller-start"
                    connection.session.update(session={}, event_id="caller-update")
                    updated = connection.recv()
                    assert isinstance(updated, SessionUpdatedEvent)
                    assert updated.client_event_id == "caller-update"
                    assert updated.session.id == "live_fixture"
        else:
            async with AsyncOpenAI(
                api_key="ek_fake_live",
                base_url=base_url,
                http_client=httpx2.AsyncClient(trust_env=False),
            ) as async_client:
                if role == "primary":
                    async_manager = async_client.live.connect(extra_query=extra_query)
                elif role == "fork":
                    async_manager = async_client.live.forks.connect(session_id="stored /?#%", extra_query=extra_query)
                else:
                    async_manager = async_client.live.sideband.connect(
                        session_id="stored /?#%", graceful_close=True, extra_query=extra_query
                    )
                async with async_manager as async_connection:
                    if isinstance(async_connection, AsyncLiveConnection):
                        await async_connection.session.start(session={"model": "gpt-live-1"}, event_id="caller-start")
                    elif isinstance(async_connection, AsyncForksConnection):
                        await async_connection.session.start(session={}, event_id="caller-start")
                    async_first = await asyncio.wait_for(async_connection.recv(), timeout=5)
                    if role == "sideband":
                        assert isinstance(async_first, OutputTranscriptDeltaEvent)
                        assert async_first.delta == "Attached"
                    else:
                        assert isinstance(async_first, SessionStartedEvent)
                        assert async_first.client_event_id == "caller-start"
                    await async_connection.session.update(session={}, event_id="caller-update")
                    async_updated = await asyncio.wait_for(async_connection.recv(), timeout=5)
                    assert isinstance(async_updated, SessionUpdatedEvent)
                    assert async_updated.client_event_id == "caller-update"
                    assert async_updated.session.id == "live_fixture"
