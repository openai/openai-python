from __future__ import annotations

import json
import asyncio
from urllib.parse import parse_qs, urlsplit

import httpx2
import pytest
from websockets.sync.server import ServerConnection

from openai import OpenAI, AsyncOpenAI
from openai.types.live import ServerEvent, SessionStartedEvent, SessionUpdatedEvent, OutputTranscriptDeltaEvent
from openai.resources.live.live import LiveConnection, AsyncLiveConnection
from openai.resources.live.forks import ForksConnection, AsyncForksConnection

from .helpers import FakeClock, Recording, ClockGrouper, AsyncClockGrouper
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


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_disposed_grouper_leaves_dispatcher_other_observers_and_socket_usable(mode: str) -> None:
    session = {"id": "live_fixture", "model": "gpt-live-1", "status": "active", "expires_at": 123}
    first_clock, second_clock = FakeClock(), FakeClock()
    transcripts = [
        {
            "type": "session.output_transcript.delta",
            "event_id": f"part-{index}",
            "delta": value,
            "start_ms": index * 200,
            "end_ms": (index + 1) * 200,
        }
        for index, value in enumerate(["One", " two", " three", " four"])
    ]
    observed: list[ServerEvent] = []
    typed: list[OutputTranscriptDeltaEvent] = []

    def script(socket: ServerConnection) -> None:
        assert json.loads(socket.recv(timeout=5)) == {
            "type": "session.start",
            "event_id": "caller-start",
            "session": {"model": "gpt-live-1"},
        }
        socket.send(json.dumps({"type": "session.started", "event_id": "started", "session": session}))
        for event in transcripts[:2]:
            socket.send(json.dumps(event))
        # Issued only after the caller detaches and closes its first grouper.
        assert json.loads(socket.recv(timeout=5)) == {
            "type": "session.update",
            "event_id": "after-dispose",
            "session": {},
        }
        socket.send(
            json.dumps(
                {
                    "type": "session.updated",
                    "event_id": "updated",
                    "client_event_id": "after-dispose",
                    "session": session,
                    "future_metadata": {"explicit_null": None, "nested": [1, "retained"]},
                }
            )
        )
        for event in transcripts[2:]:
            socket.send(json.dumps(event))
        assert json.loads(socket.recv(timeout=5)) == {"type": "session.close", "event_id": "caller-finish"}
        socket.send(json.dumps({"type": "session.closed", "event_id": "closed", "reason": "client_close"}))
        # The shared fixture rejects extra writes/reconnects and waits for caller close.

    with script_server(script) as url:
        if mode == "sync":
            first = ClockGrouper(first_clock)
            second = ClockGrouper(second_clock)
            first_record, second_record = Recording(first, first_clock), Recording(second, second_clock)
            with OpenAI(api_key="ek_fake_live", base_url=url, http_client=httpx2.Client(trust_env=False)) as client:
                with client.live.connect() as connection:
                    connection.on("session.output_transcript.delta", first.push)
                    connection.on("session.output_transcript.delta", second.push)
                    connection.on("session.output_transcript.delta", typed.append)
                    connection.on("event", observed.append)

                    def manage(event: OutputTranscriptDeltaEvent) -> None:
                        if event.event_id == "part-1":
                            assert first_clock.pending
                            connection.off("session.output_transcript.delta", first.push)
                            first.close()
                            first.close()
                            assert not first_clock.pending
                            connection.session.update(session={}, event_id="after-dispose")
                        elif event.event_id == "part-3":
                            connection.session.close(event_id="caller-finish")

                    connection.on("session.output_transcript.delta", manage)
                    connection.on("session.closed", lambda _event: connection.close())
                    connection.session.start(session={"model": "gpt-live-1"}, event_id="caller-start")
                    connection.dispatch_events()
            second.close()
        else:
            async_first = AsyncClockGrouper(first_clock)
            async_second = AsyncClockGrouper(second_clock)
            first_record, second_record = (
                Recording(async_first, first_clock),
                Recording(async_second, second_clock),
            )
            async with AsyncOpenAI(
                api_key="ek_fake_live", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as async_client:
                async with async_client.live.connect() as async_connection:
                    async_connection.on("session.output_transcript.delta", async_first.push)
                    async_connection.on("session.output_transcript.delta", async_second.push)
                    async_connection.on("session.output_transcript.delta", typed.append)
                    async_connection.on("event", observed.append)

                    async def async_manage(event: OutputTranscriptDeltaEvent) -> None:
                        if event.event_id == "part-1":
                            assert first_clock.pending
                            async_connection.off("session.output_transcript.delta", async_first.push)
                            await async_first.close()
                            await async_first.close()
                            assert not first_clock.pending
                            await async_connection.session.update(session={}, event_id="after-dispose")
                        elif event.event_id == "part-3":
                            await async_connection.session.close(event_id="caller-finish")

                    async_connection.on("session.output_transcript.delta", async_manage)
                    async_connection.on("session.closed", lambda _event: async_connection.close())
                    await async_connection.session.start(session={"model": "gpt-live-1"}, event_id="caller-start")
                    await asyncio.wait_for(async_connection.dispatch_events(), timeout=5)
            await async_second.close()

    assert [event.event_id for event in observed] == [
        "started",
        "part-0",
        "part-1",
        "updated",
        "part-2",
        "part-3",
        "closed",
    ]
    assert [event.to_dict() for event in typed] == transcripts
    updated = observed[3]
    assert isinstance(updated, SessionUpdatedEvent)
    assert updated.to_dict()["future_metadata"] == {"explicit_null": None, "nested": [1, "retained"]}
    assert [(event.segment.text, event.reason) for event in first_record.closed] == [("One two", "manual")]
    assert [(event.segment.text, event.reason) for event in second_record.closed] == [("One two three four", "manual")]
    assert not first_clock.pending and not second_clock.pending
