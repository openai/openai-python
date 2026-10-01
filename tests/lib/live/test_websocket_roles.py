from __future__ import annotations

import json
import asyncio
from urllib.parse import parse_qs, urlsplit

import httpx2
import pytest
from websockets.sync.client import ClientConnection
from websockets.sync.server import ServerConnection
from websockets.asyncio.client import ClientConnection as AsyncClientConnection

from openai import OpenAI, AsyncOpenAI
from openai.types.live import (
    ErrorEvent,
    ServerEvent,
    SessionClosedEvent,
    SessionStartedEvent,
    SessionUpdatedEvent,
    OutputTranscriptDeltaEvent,
)
from openai._exceptions import WebSocketQueueFullError
from openai.resources.live.live import LiveConnection, AsyncLiveConnection
from openai.resources.live.forks import ForksConnection, AsyncForksConnection
from openai.types.websocket_reconnection import ReconnectingEvent

from .helpers import FakeClock, Recording, ClockGrouper, AsyncClockGrouper
from ..responses.test_websocket_session import script_server


@pytest.fixture(autouse=True)
def bypass_loopback_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")


@pytest.mark.parametrize("role", ["primary", "fork", "sideband"])
@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_empty_live_manager_queue_keeps_budget_and_caller_messages(role: str, mode: str) -> None:
    opened = 0

    def script(socket: ServerConnection) -> None:
        nonlocal opened
        opened += 1
        if opened == 1:
            socket.close(code=1011, reason="synthetic restart")
            return
        # Read first event without blocking on a lost manager queue.
        socket.send('{"type": "session.output_transcript.delta", "event_id": "ready", "delta": "go"}')
        assert json.loads(socket.recv(timeout=5)) == {"type": "session.update", "event_id": "queued", "session": {}}

    with script_server(script, expected_connections=2) as url:
        if mode == "sync":
            with OpenAI(api_key="fake-live-key", base_url=url, http_client=httpx2.Client(trust_env=False)) as client:

                def on_retry(_event: ReconnectingEvent) -> None:
                    manager.send({"type": "session.update", "event_id": "queued", "session": {}})
                    with pytest.raises(WebSocketQueueFullError):
                        manager.send({"type": "session.update", "event_id": "large" * 150, "session": {}})

                if role == "primary":
                    manager = client.live.connect(max_queue_size=100, on_reconnecting=on_retry, initial_delay=0)
                elif role == "fork":
                    manager = client.live.forks.connect(
                        session_id="stored", max_queue_size=100, on_reconnecting=on_retry, initial_delay=0
                    )
                else:
                    manager = client.live.sideband.connect(
                        session_id="stored", max_queue_size=100, on_reconnecting=on_retry, initial_delay=0
                    )
                with manager as connection:
                    assert next(iter(connection)).type == "session.output_transcript.delta"
        else:
            async with AsyncOpenAI(
                api_key="fake-live-key", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as async_client:

                def on_async_retry(_event: ReconnectingEvent) -> None:
                    async_manager.send({"type": "session.update", "event_id": "queued", "session": {}})
                    with pytest.raises(WebSocketQueueFullError):
                        async_manager.send({"type": "session.update", "event_id": "large" * 150, "session": {}})

                if role == "primary":
                    async_manager = async_client.live.connect(
                        max_queue_size=100, on_reconnecting=on_async_retry, initial_delay=0
                    )
                elif role == "fork":
                    async_manager = async_client.live.forks.connect(
                        session_id="stored", max_queue_size=100, on_reconnecting=on_async_retry, initial_delay=0
                    )
                else:
                    async_manager = async_client.live.sideband.connect(
                        session_id="stored", max_queue_size=100, on_reconnecting=on_async_retry, initial_delay=0
                    )
                async with async_manager as async_connection:
                    assert (
                        await asyncio.wait_for(anext(aiter(async_connection)), 5)
                    ).type == "session.output_transcript.delta"


@pytest.mark.parametrize("role", ["primary", "fork", "sideband"])
@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("preopen", [True, False], ids=["preopen-flush", "direct"])
async def test_live_recovery_never_replays_an_attempted_command(
    role: str, mode: str, preopen: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    opened = 0
    recorded: list[tuple[int, str]] = []

    def script(socket: ServerConnection) -> None:
        nonlocal opened
        opened += 1
        current = opened
        if current == 1:
            for _ in range(2 if preopen else 1):
                recorded.append((current, json.loads(socket.recv(timeout=5))["event_id"]))
            socket.close(code=1011, reason="synthetic restart")
            return
        socket.send('{"type": "session.output_transcript.delta", "event_id": "ready", "delta": "go"}')
        for _ in range(2 if preopen else 1):
            recorded.append((current, json.loads(socket.recv(timeout=5))["event_id"]))

    # Complete the actual wire send and then raise, so delivery cannot be inferred
    # from the SDK-visible error. The real server checks what each socket received.
    original = ClientConnection.send
    original_async = AsyncClientConnection.send

    def send_then_interrupt(self: ClientConnection, message: object, *args: object, **kwargs: object) -> None:
        original(self, message, *args, **kwargs)  # type: ignore[arg-type]
        if json.loads(message)["event_id"] == "attempted":  # type: ignore[arg-type]
            raise OSError("synthetic interruption after send")

    async def async_send_then_interrupt(
        self: AsyncClientConnection, message: object, *args: object, **kwargs: object
    ) -> None:
        await original_async(self, message, *args, **kwargs)  # type: ignore[arg-type]
        if json.loads(message)["event_id"] == "attempted":  # type: ignore[arg-type]
            raise OSError("synthetic interruption after send")

    if mode == "sync":
        monkeypatch.setattr(ClientConnection, "send", send_then_interrupt)
    else:
        monkeypatch.setattr(AsyncClientConnection, "send", async_send_then_interrupt)
    with script_server(script, expected_connections=2) as url:
        if mode == "sync":
            with OpenAI(api_key="fake-live-key", base_url=url, http_client=httpx2.Client(trust_env=False)) as client:

                def on_retry(_event: ReconnectingEvent) -> None:
                    manager.send({"type": "session.update", "event_id": "during-recovery", "session": {}})

                if role == "primary":
                    manager = client.live.connect(on_reconnecting=on_retry, initial_delay=0)
                elif role == "fork":
                    manager = client.live.forks.connect(session_id="stored", on_reconnecting=on_retry, initial_delay=0)
                else:
                    manager = client.live.sideband.connect(
                        session_id="stored", on_reconnecting=on_retry, initial_delay=0
                    )
                if preopen:
                    for identity in ("first", "attempted", "unattempted"):
                        manager.send({"type": "session.update", "event_id": identity, "session": {}})
                with manager as connection:
                    if not preopen:
                        with pytest.raises(OSError, match="synthetic interruption after send"):
                            connection.send({"type": "session.update", "event_id": "attempted", "session": {}})
                    assert next(iter(connection)).type == "session.output_transcript.delta"
        else:
            async with AsyncOpenAI(
                api_key="fake-live-key", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as async_client:

                def on_async_retry(_event: ReconnectingEvent) -> None:
                    async_manager.send({"type": "session.update", "event_id": "during-recovery", "session": {}})

                if role == "primary":
                    async_manager = async_client.live.connect(on_reconnecting=on_async_retry, initial_delay=0)
                elif role == "fork":
                    async_manager = async_client.live.forks.connect(
                        session_id="stored", on_reconnecting=on_async_retry, initial_delay=0
                    )
                else:
                    async_manager = async_client.live.sideband.connect(
                        session_id="stored", on_reconnecting=on_async_retry, initial_delay=0
                    )
                if preopen:
                    for identity in ("first", "attempted", "unattempted"):
                        async_manager.send({"type": "session.update", "event_id": identity, "session": {}})
                async with async_manager as async_connection:
                    if not preopen:
                        with pytest.raises(OSError, match="synthetic interruption after send"):
                            await async_connection.send(
                                {"type": "session.update", "event_id": "attempted", "session": {}}
                            )
                    event = await asyncio.wait_for(anext(aiter(async_connection)), 5)
                    assert event.type == "session.output_transcript.delta"
    expected = [(1, "first"), (1, "attempted"), (2, "unattempted"), (2, "during-recovery")]
    assert recorded == (expected if preopen else [(1, "attempted"), (2, "during-recovery")])


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
@pytest.mark.parametrize("role", ["primary", "fork", "sideband"])
async def test_disposed_grouper_leaves_dispatcher_other_observers_and_socket_usable(mode: str, role: str) -> None:
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
        if role != "sideband":
            assert json.loads(socket.recv(timeout=5)) == {
                "type": "session.start",
                "event_id": "caller-start",
                "session": {"model": "gpt-live-1"} if role == "primary" else {},
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
                if role == "primary":
                    manager = client.live.connect()
                elif role == "fork":
                    manager = client.live.forks.connect(session_id="stored")
                else:
                    manager = client.live.sideband.connect(session_id="stored")
                with manager as connection:
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

                    def close_connection(_event: SessionClosedEvent) -> None:
                        connection.close()

                    connection.on("session.output_transcript.delta", manage)
                    connection.on("session.closed", close_connection)
                    if isinstance(connection, LiveConnection):
                        connection.session.start(session={"model": "gpt-live-1"}, event_id="caller-start")
                    elif isinstance(connection, ForksConnection):
                        connection.session.start(session={}, event_id="caller-start")
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
                if role == "primary":
                    async_manager = async_client.live.connect()
                elif role == "fork":
                    async_manager = async_client.live.forks.connect(session_id="stored")
                else:
                    async_manager = async_client.live.sideband.connect(session_id="stored")
                async with async_manager as async_connection:
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

                    async def close_async_connection(_event: SessionClosedEvent) -> None:
                        await async_connection.close()

                    async_connection.on("session.output_transcript.delta", async_manage)
                    async_connection.on("session.closed", close_async_connection)
                    if isinstance(async_connection, AsyncLiveConnection):
                        await async_connection.session.start(session={"model": "gpt-live-1"}, event_id="caller-start")
                    elif isinstance(async_connection, AsyncForksConnection):
                        await async_connection.session.start(session={}, event_id="caller-start")
                    await asyncio.wait_for(async_connection.dispatch_events(), timeout=5)
            await async_second.close()

    ids = ["part-0", "part-1", "updated", "part-2", "part-3", "closed"]
    assert [event.to_dict().get("event_id") for event in observed] == (ids if role == "sideband" else ["started", *ids])
    assert [event.to_dict() for event in typed] == transcripts
    updated = observed[2 if role == "sideband" else 3]
    assert isinstance(updated, SessionUpdatedEvent)
    assert updated.to_dict()["future_metadata"] == {"explicit_null": None, "nested": [1, "retained"]}
    assert [(event.segment.text, event.reason) for event in first_record.closed] == [("One two", "manual")]
    assert [(event.segment.text, event.reason) for event in second_record.closed] == [("One two three four", "manual")]
    assert not first_clock.pending and not second_clock.pending


@pytest.mark.parametrize("role", ["primary", "fork", "sideband"])
@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_live_wire_preserves_unknown_events_and_storage_failure_before_closed(role: str, mode: str) -> None:
    wire_events = [
        {
            "type": "future.live.event",
            "event_id": "future",
            "nested": {"explicit_null": None, "values": ["東京🙂", 1]},
        },
        {
            "type": "error",
            "event_id": "storage",
            "client_event_id": "caller-finish",
            "error": {
                "type": "server_error",
                "code": "session_storage_failed",
                "message": "synthetic recording failure",
                "param": None,
                "future_detail": {"retry_allowed": False},
            },
        },
        {
            "type": "session.closed",
            "event_id": "closed",
            "reason": "close_requested",
            "session": {"id": "live_fixture", "model": "gpt-live-1", "status": "closed", "expires_at": 123},
            "usage": {"future_counter": 0},
        },
    ]

    def script(socket: ServerConnection) -> None:
        if role != "sideband":
            start = json.loads(socket.recv(timeout=5))
            assert start == {
                "type": "session.start",
                "event_id": "caller-start",
                "session": {"model": "gpt-live-1"} if role == "primary" else {},
            }
            socket.send('{"type": "session.started", "event_id": "started"}')
        assert json.loads(socket.recv(timeout=5)) == {"type": "session.close", "event_id": "caller-finish"}
        for event in wire_events:
            socket.send(json.dumps(event))

    with script_server(script) as url:
        if mode == "sync":
            with OpenAI(api_key="fake-live-key", base_url=url, http_client=httpx2.Client(trust_env=False)) as client:
                if role == "primary":
                    manager = client.live.connect()
                elif role == "fork":
                    manager = client.live.forks.connect(session_id="stored")
                else:
                    manager = client.live.sideband.connect(session_id="stored")
                with manager as connection:
                    if isinstance(connection, LiveConnection):
                        connection.session.start(session={"model": "gpt-live-1"}, event_id="caller-start")
                        assert isinstance(connection.recv(), SessionStartedEvent)
                    elif isinstance(connection, ForksConnection):
                        connection.session.start(session={}, event_id="caller-start")
                        assert isinstance(connection.recv(), SessionStartedEvent)
                    connection.session.close(event_id="caller-finish")
                    events = [connection.recv() for _ in wire_events]
        else:
            async with AsyncOpenAI(
                api_key="fake-live-key", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as async_client:
                if role == "primary":
                    async_manager = async_client.live.connect()
                elif role == "fork":
                    async_manager = async_client.live.forks.connect(session_id="stored")
                else:
                    async_manager = async_client.live.sideband.connect(session_id="stored")
                async with async_manager as async_connection:
                    if isinstance(async_connection, AsyncLiveConnection):
                        await async_connection.session.start(session={"model": "gpt-live-1"}, event_id="caller-start")
                        assert isinstance(await asyncio.wait_for(async_connection.recv(), 5), SessionStartedEvent)
                    elif isinstance(async_connection, AsyncForksConnection):
                        await async_connection.session.start(session={}, event_id="caller-start")
                        assert isinstance(await asyncio.wait_for(async_connection.recv(), 5), SessionStartedEvent)
                    await async_connection.session.close(event_id="caller-finish")
                    events = [await asyncio.wait_for(async_connection.recv(), 5) for _ in wire_events]

    # The final close must never replace the actionable recording failure.
    assert [event.to_dict(exclude_unset=True) for event in events] == wire_events
    assert isinstance(events[1], ErrorEvent)
    assert events[1].error.code == "session_storage_failed"
    assert isinstance(events[2], SessionClosedEvent)
