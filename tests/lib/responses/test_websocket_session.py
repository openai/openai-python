from __future__ import annotations

import json
import asyncio
import threading
from typing import Any, Callable, Generator, AsyncGenerator
from contextlib import contextmanager, asynccontextmanager
from dataclasses import replace

import httpx2
import pytest
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
from websockets.sync.server import ServerConnection, serve

from openai import OpenAI, AsyncOpenAI, omit
from openai._types import Headers
from openai.lib.responses_websocket import (
    ResponsesWebSocketError,
    ResponsesWebSocketLimits,
    ResponsesWebSocketSession,
    ResponsesWebSocketBufferError,
    AsyncResponsesWebSocketSession,
)
from openai.types.websocket_reconnection import ReconnectingEvent, ReconnectingOverrides
from openai.types.responses.responses_server_event import ResponseWsError

from .test_websocket_contract import SCENARIOS, scenario_server

LIMITS = ResponsesWebSocketLimits(
    max_lanes=8,
    max_events_per_lane=32,
    max_events=64,
    max_bytes_per_lane=256_000,
    max_bytes=512_000,
    max_response_bytes=512_000,
)


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("beta", [False, True])
async def test_raw_receive_preserves_text_utf8_and_binary_bytes(mode: str, beta: bool) -> None:
    text_message = ' { "type": "response.future", "text": "東京🙂" }\n'
    binary_message = b"\x00\xff\x80"

    def script(socket: ServerConnection) -> None:
        for message in [text_message, binary_message]:
            socket.send(message)

    with script_server(script) as url:
        if mode == "sync":
            with OpenAI(api_key="fake-raw-key", base_url=url, http_client=httpx2.Client(trust_env=False)) as client:
                resource = client.beta.responses if beta else client.responses
                with resource.connect() as connection:
                    assert connection.recv_bytes() == text_message.encode("utf-8")
                    assert connection.recv_bytes() == binary_message
        else:
            async with AsyncOpenAI(
                api_key="fake-raw-key", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as async_client:
                async_resource = async_client.beta.responses if beta else async_client.responses
                async with async_resource.connect() as async_connection:
                    assert await async_connection.recv_bytes() == text_message.encode("utf-8")
                    assert await async_connection.recv_bytes() == binary_message


@pytest.fixture(autouse=True)
def bypass_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")


class Driver:
    def __init__(self, session: Any, mode: str) -> None:
        self.session = session
        self.mode = mode

    async def call(self, lane: Any, method: str, *args: Any, **kwargs: Any) -> Any:
        if self.mode == "async":
            return await asyncio.wait_for(getattr(lane, method)(*args, **kwargs), timeout=5)
        if method in {"recv", "get_final_response"}:
            kwargs.setdefault("timeout", 5)
        return await asyncio.to_thread(getattr(lane, method), *args, **kwargs)


@asynccontextmanager
async def session_for(
    mode: str,
    url: str,
    limits: ResponsesWebSocketLimits = LIMITS,
    connection_options: dict[str, Any] | None = None,
    client_headers: dict[str, str] | None = None,
    connection_headers: Headers | None = None,
) -> AsyncGenerator[Driver]:
    options = connection_options or {}
    headers = {"X-Contract-Test": "synthetic", **(connection_headers or {})}
    if mode == "sync":
        with (
            OpenAI(
                api_key="fake-contract-key",
                base_url=url,
                default_headers=client_headers,
                http_client=httpx2.Client(trust_env=False),
            ) as client,
            client.responses.connect(extra_query={"contract": "1"}, extra_headers=headers, **options) as connection,
            ResponsesWebSocketSession(connection, limits=limits) as session,
        ):
            yield Driver(session, mode)
    else:
        async with (
            AsyncOpenAI(
                api_key="fake-contract-key",
                base_url=url,
                default_headers=client_headers,
                http_client=httpx2.AsyncClient(trust_env=False),
            ) as async_client,
            async_client.responses.connect(
                extra_query={"contract": "1"}, extra_headers=headers, **options
            ) as async_connection,
            AsyncResponsesWebSocketSession(async_connection, limits=limits) as async_session,
        ):
            yield Driver(async_session, mode)


@contextmanager
def script_server(
    script: Callable[[ServerConnection], None], *, expected_connections: int = 1
) -> Generator[str, None, None]:
    failures: list[Exception] = []
    sockets: list[ServerConnection] = []
    finished: list[threading.Event] = []

    def handle(socket: ServerConnection) -> None:
        sockets.append(socket)
        done = threading.Event()
        finished.append(done)
        try:
            script(socket)
            if socket.protocol.close_code is None:
                with pytest.raises(ConnectionClosedOK):
                    socket.recv(timeout=5)
        except Exception as exc:
            failures.append(exc)
        finally:
            socket.close()
            done.set()

    with serve(handle, "127.0.0.1", 0, close_timeout=1) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.socket.getsockname()[1]}/v1"
        finally:
            for socket in sockets:
                socket.close()
            server.shutdown()
            thread.join(timeout=5)
            assert not thread.is_alive()
            for done in finished:
                assert done.wait(5)
            assert len(sockets) == expected_connections
            assert not failures, failures


def response_event(kind: str, lane: str | None = None, **response_fields: Any) -> dict[str, Any]:
    response: dict[str, Any] = {
        "id": f"resp_{lane or 'default'}",
        "object": "response",
        "created_at": 1,
        "model": "gpt-4o-mini",
        "output": [],
        "parallel_tool_calls": False,
        "tool_choice": "auto",
        "tools": [],
        "status": "in_progress" if kind == "created" else kind,
        **response_fields,
    }
    return {
        "type": f"response.{kind}",
        "sequence_number": 1,
        "response": response,
        **({"stream_id": lane} if lane else {}),
    }


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("typed", [False, True])
async def test_named_lane_preserves_reference_routed_steering(mode: str, typed: bool) -> None:
    from openai.types.responses import ResponseSteerEvent

    command = {"type": "response.steer", "previous_response_id": "resp_parent", "input": "Change course"}

    def script(socket: ServerConnection) -> None:
        assert json.loads(socket.recv()) == command
        socket.send(json.dumps(response_event("incomplete", "steering", id="resp_parent")))
        socket.send(json.dumps(response_event("created", "steering", id="resp_successor")))
        socket.send(json.dumps(response_event("completed", "steering", id="resp_successor")))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.lane("steering")
            event = (
                ResponseSteerEvent(type="response.steer", previous_response_id="resp_parent", input="Change course")
                if typed
                else command
            )
            await driver.call(lane, "send", event)
            assert (await driver.call(lane, "get_final_response")).id == "resp_parent"
            assert (await driver.call(lane, "recv")).type == "response.created"
            with pytest.raises(RuntimeError, match="Consume the current response"):
                await driver.call(lane, "send", {"type": "response.create", "input": "Too early"})
            assert (await driver.call(lane, "get_final_response")).id == "resp_successor"
            assert "stream_id" not in command


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("delayed", [False, True])
@pytest.mark.parametrize("check_send", [False, True])
async def test_observed_successor_advances_cached_final_and_keeps_lane_owned(
    mode: str, delayed: bool, check_send: bool
) -> None:
    allow_successor = threading.Event()

    def script(socket: ServerConnection) -> None:
        assert json.loads(socket.recv(timeout=5))["type"] == "response.steer"
        socket.send(json.dumps(response_event("incomplete", "steering", id="resp_parent")))
        if delayed:
            assert allow_successor.wait(5)
        socket.send(json.dumps(response_event("created", "steering", id="resp_successor")))
        # Receiving this on the default lane proves the single reader has already
        # observed the successor, without consuming any of its own lane events.
        socket.send(json.dumps({"type": "response.future", "successor_observed": True}))
        socket.send(json.dumps(response_event("completed", "steering", id="resp_successor")))
        assert json.loads(socket.recv(timeout=5))["input"] == "after successor"
        socket.send(json.dumps(response_event("completed", "steering", id="resp_after")))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.lane("steering")
            await driver.call(
                lane, "send", {"type": "response.steer", "previous_response_id": "resp_parent", "input": "Steer"}
            )
            try:
                if not delayed:
                    assert (await driver.call(driver.session.default, "recv")).successor_observed
                parent = await driver.call(lane, "get_final_response")
                assert parent.id == "resp_parent"
                if delayed:
                    # No observed successor: preserve the existing cached getter.
                    assert (await driver.call(lane, "get_final_response")) is parent
                    allow_successor.set()
                    assert (await driver.call(driver.session.default, "recv")).successor_observed
                if check_send:
                    with pytest.raises(RuntimeError, match="Consume the current response"):
                        await driver.call(lane, "send", {"type": "response.create", "input": "too early"})
                successor = await driver.call(lane, "get_final_response")
                assert successor.id == "resp_successor"
                assert (await driver.call(lane, "get_final_response")) is successor
                await driver.call(lane, "send", {"type": "response.create", "input": "after successor"})
                assert (await driver.call(lane, "get_final_response")).id == "resp_after"
            finally:
                allow_successor.set()


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("scenario", SCENARIOS[:4], ids=lambda scenario: scenario["id"])
async def test_terminal_results_and_reuse(mode: str, scenario: Any) -> None:
    with scenario_server(scenario) as url:
        async with session_for(mode, url) as driver:
            lanes: dict[str | None, Any] = {None: driver.session.default}
            for turn in scenario["turns"]:
                stream_id = turn["request"].get("stream_id")
                if stream_id not in lanes:
                    lanes[stream_id] = driver.session.lane(stream_id)
                lane = lanes[stream_id]
                await driver.call(lane, "send", turn["request"])
                terminal = turn["frames"][-1]
                if terminal["type"] == "error":
                    with pytest.raises(ResponsesWebSocketError) as raised:
                        await driver.call(lane, "get_final_response")
                    assert isinstance(raised.value.event, ResponseWsError)
                    assert raised.value.event.error.code == "invalid_value"
                    assert raised.value.event.to_dict(exclude_unset=True) == terminal
                else:
                    response = await driver.call(lane, "get_final_response")
                    assert response.id == terminal["response"]["id"]
                    assert response.status == terminal["response"]["status"]


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("kind", ["completed", "failed", "incomplete"])
@pytest.mark.parametrize("include_null", [False, True], ids=["missing", "null"])
async def test_terminal_without_response_fails_while_socket_remains_open(
    mode: str, kind: str, include_null: bool
) -> None:
    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        event: dict[str, Any] = {"type": f"response.{kind}", "sequence_number": 1}
        if include_null:
            event["response"] = None
        socket.send(json.dumps(event))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create", "model": "gpt-4o-mini", "input": "Hello"})
            with pytest.raises(ValueError, match="Terminal WebSocket event is missing response"):
                await driver.call(lane, "get_final_response")


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_interleaved_lanes_default_unknown_and_detach(mode: str) -> None:
    def script(socket: ServerConnection) -> None:
        first = json.loads(socket.recv(timeout=5))
        second = json.loads(socket.recv(timeout=5))
        assert first["stream_id"] == "left"
        assert second["stream_id"] == "right"
        assert second["previous_response_id"] == "resp_ancestor"
        for event in [
            response_event("created", "left"),
            response_event("created", "right"),
            {"type": "response.future", "stream_id": "right", "new_field": {"nested": True}},
            response_event("completed", "left"),
            {"type": "response.future", "unclaimed": 1},
        ]:
            socket.send(json.dumps(event))
        assert json.loads(socket.recv(timeout=5))["type"] == "response.create"
        socket.send(json.dumps(response_event("completed", "right")))
        socket.send(json.dumps(response_event("completed")))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            left = driver.session.lane("left")
            right = driver.session.lane("right")
            await driver.call(left, "send", {"type": "response.create", "model": "gpt-4o-mini", "input": "left"})
            await driver.call(right, "send", {"type": "response.create", "previous_response_id": "resp_ancestor"})
            assert (await driver.call(right, "recv")).type == "response.created"
            unknown = await driver.call(right, "recv")
            assert unknown.to_dict(exclude_unset=True)["new_field"] == {"nested": True}
            assert (await driver.call(left, "get_final_response")).id == "resp_left"
            left.close()
            left.close()
            assert (await driver.call(driver.session.default, "recv")).unclaimed == 1
            await driver.call(driver.session.default, "send", {"type": "response.create"})
            assert (await driver.call(right, "get_final_response")).id == "resp_right"
            assert (await driver.call(driver.session.default, "get_final_response")).id == "resp_default"
            with pytest.raises(EOFError, match="detached"):
                await driver.call(left, "recv")


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_wait_cancellation_does_not_lose_event_or_close_other_lane(mode: str) -> None:
    release = threading.Event()

    def script(socket: ServerConnection) -> None:
        assert release.wait(5)
        socket.send(json.dumps(response_event("completed", "waiter")))
        socket.send(json.dumps(response_event("completed", "other")))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            waiter = driver.session.lane("waiter")
            other = driver.session.lane("other")
            if mode == "async":
                pending = asyncio.create_task(waiter.get_final_response())
                await asyncio.sleep(0)
                pending.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await pending
            else:
                with pytest.raises(TimeoutError):
                    await asyncio.to_thread(waiter.recv, timeout=0.01)
            release.set()
            assert (await driver.call(waiter, "get_final_response")).id == "resp_waiter"
            waiter.close()
            assert (await driver.call(other, "get_final_response")).id == "resp_other"


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("limit", ["max_events_per_lane", "max_events", "max_bytes_per_lane", "max_bytes"])
async def test_queue_overflow_is_explicit_and_stops_reader(mode: str, limit: str) -> None:
    sent = threading.Event()

    def script(socket: ServerConnection) -> None:
        socket.send(json.dumps({"type": "response.future", "padding": "x" * 100}))
        if limit in {"max_events_per_lane", "max_events"}:
            socket.send(json.dumps({"type": "response.future", "padding": "y" * 100}))
        sent.set()

    with script_server(script) as url:
        async with session_for(mode, url, replace(LIMITS, **{limit: 1})) as driver:
            assert await asyncio.to_thread(sent.wait, 5)
            # Wait for the physical reader to observe the overflow, independently
            # of whether one event fit before the configured overflow.
            for _ in range(500):
                if driver.session._router.ended:
                    break
                await asyncio.sleep(0.01)
            with pytest.raises(ResponsesWebSocketBufferError):
                while True:
                    await driver.call(driver.session.default, "recv")


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_accumulation_bound_preserves_raw_event_and_socket(mode: str) -> None:
    def script(socket: ServerConnection) -> None:
        assert json.loads(socket.recv(timeout=5))["stream_id"] == "large"
        socket.send(json.dumps(response_event("created", "large")))
        assert json.loads(socket.recv(timeout=5))["stream_id"] == "small"
        socket.send(json.dumps({"type": "response.future", "stream_id": "small", "value": 7}))

    with script_server(script) as url:
        async with session_for(mode, url, replace(LIMITS, max_response_bytes=1)) as driver:
            large = driver.session.lane("large")
            small = driver.session.lane("small")
            await driver.call(large, "send", {"type": "response.create"})
            raw = await driver.call(large, "recv")
            assert raw.type == "response.created"
            with pytest.raises(ResponsesWebSocketBufferError, match="max_response_bytes"):
                await driver.call(large, "get_final_response")
            large.close()
            await driver.call(small, "send", {"type": "response.create"})
            assert (await driver.call(small, "recv")).value == 7


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_accumulates_final_items_and_multipart_output_without_mutating_events(mode: str) -> None:
    message: dict[str, Any] = {
        "id": "msg_text",
        "type": "message",
        "role": "assistant",
        "status": "completed",
        "content": [
            {"type": "output_text", "text": "one", "annotations": [], "logprobs": []},
            {"type": "output_text", "text": "two", "annotations": [], "logprobs": []},
        ],
    }
    tool = {"id": "fc_1", "type": "function_call", "call_id": "call_1", "name": "lookup", "arguments": '{"x":1}'}

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        frames: list[dict[str, Any]] = [
            response_event("created"),
            {"type": "response.output_item.done", "output_index": 0, "sequence_number": 2, "item": message},
            {"type": "response.output_item.done", "output_index": 1, "sequence_number": 3, "item": tool},
            response_event("completed"),
        ]
        del frames[-1]["response"]["output"]
        for frame in frames:
            socket.send(json.dumps(frame))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create"})
            for _ in range(3):
                await driver.call(lane, "recv")
            terminal = await driver.call(lane, "recv")
            assert "output" not in terminal.response.to_dict(exclude_unset=True)
            final = await driver.call(lane, "get_final_response")
            assert final.output[0].content[0].text == "one"
            assert final.output[0].content[1].text == "two"
            assert final.output[1].arguments == '{"x":1}'


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_one_session_per_connection_and_duplicate_lane_rejected(mode: str) -> None:
    connected = threading.Event()
    with script_server(lambda _: connected.set()) as url:
        async with session_for(mode, url) as driver:
            assert await asyncio.to_thread(connected.wait, 5)
            lane = driver.session.lane("existing")
            with pytest.raises(ValueError, match="already registered"):
                driver.session.lane("existing")
            with pytest.raises(ValueError, match="does not match"):
                await driver.call(lane, "send", {"type": "response.create", "stream_id": "other"})
            duplicate = type(driver.session)(driver.session.connection, limits=LIMITS)
            with pytest.raises(RuntimeError, match="already has"):
                if mode == "sync":
                    duplicate.__enter__()
                else:
                    await duplicate.__aenter__()


@pytest.mark.parametrize(
    "limit", ["max_lanes", "max_events_per_lane", "max_events", "max_bytes_per_lane", "max_bytes", "max_response_bytes"]
)
@pytest.mark.parametrize("value", [0, -1, True, 1.5, "1"])
def test_invalid_limits_rejected(limit: str, value: Any) -> None:
    with pytest.raises(ValueError, match="positive integers"):
        replace(LIMITS, **{limit: value})


@pytest.mark.parametrize("limit", ["max_lanes", "max_events_per_lane", "max_events", "max_bytes_per_lane", "max_bytes"])
def test_queue_and_lane_limits_cannot_be_unbounded(limit: str) -> None:
    with pytest.raises(ValueError, match="positive integers"):
        replace(LIMITS, **{limit: None})


async def test_async_cancelled_close_retains_ownership_until_cleanup(monkeypatch: pytest.MonkeyPatch) -> None:
    close_started = asyncio.Event()
    finish_close = asyncio.Event()
    close_finished = asyncio.Event()
    peer_closed = threading.Event()

    def script(socket: ServerConnection) -> None:
        with pytest.raises(ConnectionClosedOK):
            socket.recv(timeout=5)
        peer_closed.set()

    with script_server(script) as url:
        async with session_for("async", url) as driver:
            session = driver.session
            connection = session.connection
            transport_close = connection._connection.close

            async def delayed_close(*, code: int = 1000, reason: str = "") -> None:
                close_started.set()
                await finish_close.wait()
                await transport_close(code=code, reason=reason)
                close_finished.set()

            monkeypatch.setattr(connection._connection, "close", delayed_close)
            closing = asyncio.create_task(session.close())
            duplicate = AsyncResponsesWebSocketSession(connection, limits=LIMITS)
            try:
                await asyncio.wait_for(close_started.wait(), timeout=5)
                closing.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await closing
                with pytest.raises(RuntimeError, match="already has a WebSocket session"):
                    await duplicate.__aenter__()

                retry = asyncio.create_task(session.close())
                await asyncio.sleep(0)
                assert not retry.done()
                finish_close.set()
                await asyncio.wait_for(retry, timeout=5)
                assert close_finished.is_set()
                assert await asyncio.to_thread(peer_closed.wait, 5)

                async with AsyncResponsesWebSocketSession(connection, limits=LIMITS):
                    # Re-closing the old session cannot release its successor's claim.
                    await session.close()
                    with pytest.raises(RuntimeError, match="already has a WebSocket session"):
                        await AsyncResponsesWebSocketSession(connection, limits=LIMITS).__aenter__()
            finally:
                finish_close.set()
                await session.close()
                if duplicate._task is not None:
                    await duplicate.close()


async def test_sync_close_interrupts_reconnect_backoff() -> None:
    reconnecting = threading.Event()

    def reconnect(_event: ReconnectingEvent) -> None:
        reconnecting.set()

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.close(code=1011)

    with script_server(script) as url:
        async with session_for(
            "sync", url, connection_options={"on_reconnecting": reconnect, "initial_delay": 10, "max_delay": 10}
        ) as driver:
            session = driver.session
            await driver.call(session.default, "send", {"type": "response.create", "input": "close during backoff"})
            assert await asyncio.to_thread(reconnecting.wait, 5)
            await asyncio.to_thread(session.close)
            assert not session._thread.is_alive()
            # A stopped reader must no longer own the connection's session claim.
            with ResponsesWebSocketSession(session.connection, limits=LIMITS):
                pass


@pytest.mark.parametrize("close_deadline", [False, True])
async def test_sync_close_during_replacement_handshake(monkeypatch: pytest.MonkeyPatch, close_deadline: bool) -> None:
    disconnect = threading.Event()
    opening = threading.Event()
    release_open = threading.Event()
    closing = threading.Event()
    replacement_accepted = threading.Event()

    def reconnect(_event: ReconnectingEvent) -> ReconnectingOverrides:
        return {"extra_headers": {"X-Recovery": "fresh"}}

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        if socket.request.headers.get("X-Recovery") != "fresh":
            assert disconnect.wait(5)
            socket.close(code=1011)
        else:
            replacement_accepted.set()

    with script_server(script, expected_connections=2) as url:
        async with session_for(
            "sync", url, connection_options={"on_reconnecting": reconnect, "initial_delay": 0}
        ) as driver:
            session = driver.session
            connection = session.connection
            make_ws = connection._make_ws
            close = connection.close
            join = session._thread.join

            def delayed_open(query: Any, headers: Any) -> Any:
                opening.set()
                assert release_open.wait(5)
                socket = make_ws(query, headers)
                assert replacement_accepted.wait(5)
                return socket

            def observed_close() -> None:
                try:
                    close()
                finally:
                    closing.set()

            monkeypatch.setattr(connection, "_make_ws", delayed_open)
            monkeypatch.setattr(connection, "close", observed_close)
            if close_deadline:
                # Exercise the bounded-close failure without waiting five seconds.
                def bounded_join(timeout: float) -> None:
                    join(timeout=min(timeout, 0.01))

                monkeypatch.setattr(session._thread, "join", bounded_join)
            disconnect.set()
            assert await asyncio.to_thread(opening.wait, 5)
            stopped = asyncio.create_task(asyncio.to_thread(session.close))
            try:
                assert await asyncio.to_thread(closing.wait, 5)
                if close_deadline:
                    with pytest.raises(RuntimeError, match="reader did not stop"):
                        await stopped
                    # A still-running reader retains ownership until it actually exits.
                    with pytest.raises(RuntimeError, match="already has a WebSocket session"):
                        ResponsesWebSocketSession(connection, limits=LIMITS).__enter__()
                release_open.set()
                await asyncio.to_thread(join, 5)
                if not close_deadline:
                    await stopped
                assert not session._thread.is_alive()
                await asyncio.to_thread(session.close)
                with ResponsesWebSocketSession(connection, limits=LIMITS):
                    pass
            finally:
                release_open.set()
                await asyncio.to_thread(join, 5)
                monkeypatch.setattr(session._thread, "join", join)


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_default_lane_can_be_recreated_after_recovery(mode: str) -> None:
    disconnect = threading.Event()

    def reconnect(_event: ReconnectingEvent) -> ReconnectingOverrides:
        return {"extra_headers": {"X-Recovery": "fresh"}}

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        if socket.request.headers.get("X-Recovery") != "fresh":
            assert json.loads(socket.recv(timeout=5))["input"] == "lost response"
            assert disconnect.wait(5)
            socket.close(code=1011)
            return
        socket.send(json.dumps({"type": "response.future", "stream_id": "observer", "restored": True}))
        assert json.loads(socket.recv(timeout=5)) == {"type": "response.create", "input": "restored context"}
        socket.send(json.dumps({"type": "response.future", "stream_id": "unregistered"}))
        socket.send(json.dumps(response_event("completed", id="resp_restored")))

    with script_server(script, expected_connections=2) as url:
        async with session_for(
            mode, url, connection_options={"on_reconnecting": reconnect, "initial_delay": 0, "max_retries": 1}
        ) as driver:
            observer = driver.session.lane("observer")
            old = driver.session.default
            await driver.call(old, "send", {"type": "response.create", "input": "lost response"})
            old.close()
            disconnect.set()
            assert (await driver.call(observer, "recv")).restored is True
            restored = driver.session.lane()
            assert restored is driver.session.default
            assert restored is not old
            with pytest.raises(EOFError, match="detached"):
                await driver.call(old, "recv")
            await driver.call(restored, "send", {"type": "response.create", "input": "restored context"})
            assert (await driver.call(restored, "recv")).stream_id == "unregistered"
            assert (await driver.call(restored, "get_final_response")).id == "resp_restored"


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_recovery_send_is_rejected_without_reserving_or_queueing(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    start = threading.Event()
    recovering = threading.Event()
    allow_reconnect = threading.Event()

    def reconnect(_event: ReconnectingEvent) -> ReconnectingOverrides:
        recovering.set()
        return {"extra_headers": {"X-Recovery": "ready"}}

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        if socket.request.headers.get("X-Recovery") != "ready":
            assert start.wait(5)
            socket.close(code=1011)
            return
        socket.send(json.dumps({"type": "response.future", "ready": True}))
        assert json.loads(socket.recv(timeout=5))["input"] == "accepted after recovery"
        socket.send(json.dumps({"type": "response.future", "accepted": True}))

    with script_server(script, expected_connections=2) as url:
        async with session_for(
            mode, url, connection_options={"on_reconnecting": reconnect, "initial_delay": 0, "max_retries": 1}
        ) as driver:
            connection = driver.session.connection
            original_make = connection._make_ws
            if mode == "sync":

                def make(*args: Any) -> Any:
                    assert allow_reconnect.wait(5)
                    return original_make(*args)

                monkeypatch.setattr(connection, "_make_ws", make)
            else:

                async def make_async(*args: Any) -> Any:
                    assert await asyncio.to_thread(allow_reconnect.wait, 5)
                    return await original_make(*args)

                monkeypatch.setattr(connection, "_make_ws", make_async)
            start.set()
            assert await asyncio.to_thread(recovering.wait, 5)
            lane = driver.session.default
            try:
                with pytest.raises(RuntimeError, match="reconnecting"):
                    await driver.call(lane, "send", {"type": "response.create", "input": "must not be queued"})
            finally:
                allow_reconnect.set()
            assert (await driver.call(lane, "recv")).ready is True
            await driver.call(lane, "send", {"type": "response.create", "input": "accepted after recovery"})
            assert (await driver.call(lane, "recv")).accepted is True


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_uncertain_send_is_not_replayed_after_existing_recovery(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    def reconnect(_event: ReconnectingEvent) -> ReconnectingOverrides:
        return {"extra_headers": {"X-Recovery": "fresh"}}

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        assert socket.request.headers["Authorization"] == "Bearer fake-contract-key"
        assert socket.request.headers["X-Client-Only"] == "retained"
        if socket.request.headers.get("X-Recovery") == "fresh":
            # The first create reached the peer, but the client saw a write
            # failure. Recovery must not execute the same request a second time.
            with pytest.raises(TimeoutError):
                socket.recv(timeout=0.1)
            socket.send(json.dumps({"type": "response.future", "restored": True}))
        else:
            assert json.loads(socket.recv(timeout=5))["input"] == "synthetic uncertain request"
            socket.close(code=1011)

    with script_server(script, expected_connections=2) as url:
        async with session_for(
            mode,
            url,
            connection_options={
                "on_reconnecting": reconnect,
                "initial_delay": 0,
                "max_retries": 1,
            },
            client_headers={"x-recovery": "client", "X-Client-Only": "retained"},
        ) as driver:
            transport = driver.session.connection._connection
            original_send = transport.send
            if mode == "sync":

                def uncertain_send(data: Any) -> None:
                    original_send(data)
                    raise OSError("Synthetic failure after write")

                monkeypatch.setattr(transport, "send", uncertain_send)
            else:

                async def uncertain_async_send(data: Any) -> None:
                    await original_send(data)
                    raise OSError("Synthetic failure after write")

                monkeypatch.setattr(transport, "send", uncertain_async_send)
            lane = driver.session.default
            with pytest.raises(OSError, match="Synthetic failure after write"):
                await driver.call(lane, "send", {"type": "response.create", "input": "synthetic uncertain request"})
            assert (await driver.call(lane, "recv")).restored is True
            with pytest.raises(RuntimeError, match="current response"):
                await driver.call(lane, "send", {"type": "response.create"})


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_early_clean_close_is_not_a_completed_response(mode: str) -> None:
    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(json.dumps(response_event("created")))
        socket.close()

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            lane = driver.session.default
            await driver.call(lane, "send", {"type": "response.create"})
            with pytest.raises(EOFError, match="connection closed"):
                await driver.call(lane, "get_final_response")


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_closed_idle_lanes_keep_their_ids_and_capacity(mode: str) -> None:
    connected = threading.Event()
    with script_server(lambda _: connected.set()) as url:
        async with session_for(mode, url, replace(LIMITS, max_lanes=2)) as driver:
            assert await asyncio.to_thread(connected.wait, 5)
            lane = driver.session.lane("one")
            with pytest.raises(ResponsesWebSocketBufferError, match="max_lanes"):
                driver.session.lane("two")
            lane.close()
            driver.session.default.close()
            for stream_id in [None, "one"]:
                with pytest.raises(ValueError, match="already registered"):
                    driver.session.lane(stream_id)
            with pytest.raises(ResponsesWebSocketBufferError, match="max_lanes"):
                driver.session.lane("two")


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("terminal", ["completed", "failed", "incomplete", "error"])
async def test_detached_active_lane_reserves_id_and_capacity_after_terminal(mode: str, terminal: str) -> None:
    release = threading.Event()

    def script(socket: ServerConnection) -> None:
        assert json.loads(socket.recv(timeout=5))["stream_id"] == "worker"
        assert release.wait(5)
        socket.send(json.dumps(response_event("created", "worker", id="resp_old")))
        event = (
            {"type": "error", "stream_id": "worker", "error": {"code": "invalid_value", "message": "synthetic"}}
            if terminal == "error"
            else response_event(terminal, "worker", id="resp_old")
        )
        socket.send(json.dumps(event))

    with script_server(script) as url:
        async with session_for(mode, url, replace(LIMITS, max_lanes=2)) as driver:
            old = driver.session.lane("worker")
            await driver.call(old, "send", {"type": "response.create"})
            old.close()
            try:
                with pytest.raises(ValueError, match="already registered"):
                    driver.session.lane("worker")
                with pytest.raises(ResponsesWebSocketBufferError, match="max_lanes"):
                    driver.session.lane("another")
            finally:
                release.set()
            # Detached named events remain inspectable without owning a new lane.
            assert (await driver.call(driver.session.default, "recv")).response.id == "resp_old"
            assert (await driver.call(driver.session.default, "recv")).type == (
                "error" if terminal == "error" else f"response.{terminal}"
            )
            with pytest.raises(ValueError, match="already registered"):
                driver.session.lane("worker")
            with pytest.raises(ResponsesWebSocketBufferError, match="max_lanes"):
                driver.session.lane("another")


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("successor", [False, True])
async def test_detached_lane_reservation_survives_unconsumed_terminal(mode: str, successor: bool) -> None:
    release = threading.Event()

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(json.dumps(response_event("created", "worker", id="resp_old")))
        socket.send(json.dumps(response_event("completed", "worker", id="resp_old")))
        if successor:
            socket.send(json.dumps(response_event("created", "worker", id="resp_successor")))
        socket.send(json.dumps({"type": "response.future", "checkpoint": True}))
        assert release.wait(5)
        if successor:
            socket.send(json.dumps(response_event("completed", "worker", id="resp_successor")))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            old = driver.session.lane("worker")
            await driver.call(old, "send", {"type": "response.create"})
            assert (await driver.call(driver.session.default, "recv")).checkpoint
            old.close()
            try:
                with pytest.raises(ValueError, match="already registered"):
                    driver.session.lane("worker")
            finally:
                release.set()
            if successor:
                assert (await driver.call(driver.session.default, "recv")).response.id == "resp_successor"
            with pytest.raises(ValueError, match="already registered"):
                driver.session.lane("worker")


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("terminal", ["completed", "incomplete"])
@pytest.mark.parametrize("stream_id", [None, "worker"])
async def test_closed_lane_cannot_be_reassigned_before_delayed_steering_successor(
    mode: str, terminal: str, stream_id: str | None
) -> None:
    release = threading.Event()

    def script(socket: ServerConnection) -> None:
        assert json.loads(socket.recv(timeout=5)).get("stream_id") == stream_id
        socket.send(json.dumps(response_event("created", stream_id, id="resp_parent")))
        assert json.loads(socket.recv(timeout=5)) == {
            "type": "response.steer",
            "previous_response_id": "resp_parent",
            "input": "Change course",
        }
        socket.send(json.dumps(response_event(terminal, stream_id, id="resp_parent")))
        assert release.wait(5)
        socket.send(json.dumps(response_event("created", stream_id, id="resp_successor")))
        socket.send(json.dumps(response_event("completed", stream_id, id="resp_successor")))
        socket.send(json.dumps({"type": "response.future", "stream_id": "observer", "finished": True}))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            observer = driver.session.lane("observer")
            old = driver.session.default if stream_id is None else driver.session.lane(stream_id)
            await driver.call(old, "send", {"type": "response.create"})
            assert (await driver.call(old, "recv")).response.id == "resp_parent"
            await driver.call(
                old,
                "send",
                {"type": "response.steer", "previous_response_id": "resp_parent", "input": "Change course"},
            )
            assert (await driver.call(old, "get_final_response")).id == "resp_parent"
            old.close()
            try:
                with pytest.raises(ValueError, match="already registered"):
                    driver.session.lane(stream_id)
            finally:
                release.set()
            if stream_id is not None:
                for kind in ["created", "completed"]:
                    event = await driver.call(driver.session.default, "recv")
                    assert event.type == f"response.{kind}"
                    assert event.response.id == "resp_successor"
            assert (await driver.call(observer, "recv")).finished
            with pytest.raises(ValueError, match="already registered"):
                driver.session.lane(stream_id)


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_lane_ids_are_validated_before_reserving_capacity(mode: str) -> None:
    def script(socket: ServerConnection) -> None:
        for stream_id in ["a", "AZaz09_.-" + "x" * 247]:
            assert json.loads(socket.recv(timeout=5))["stream_id"] == stream_id
            socket.send(json.dumps(response_event("completed", stream_id)))

    with script_server(script) as url:
        async with session_for(mode, url, replace(LIMITS, max_lanes=3)) as driver:
            invalid_ids: list[object] = [
                0,
                False,
                [],
                {},
                b"worker",
                "",
                "x" * 257,
                "bad id",
                "bad\n",
                "bad\x00",
                "café",
                "K",
            ]
            for invalid in invalid_ids:
                with pytest.raises(ValueError, match="stream_id"):
                    driver.session.lane(invalid)
            for stream_id in ["a", "AZaz09_.-" + "x" * 247]:
                lane = driver.session.lane(stream_id)
                await driver.call(lane, "send", {"type": "response.create"})
                assert (await driver.call(lane, "get_final_response")).id == f"resp_{stream_id}"


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("active", [False, True])
async def test_detached_lane_is_released_after_reconnect(mode: str, active: bool) -> None:
    disconnect = threading.Event()

    def reconnect(_event: ReconnectingEvent) -> ReconnectingOverrides:
        return {"extra_headers": {"X-Recovery": "fresh"}}

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        if socket.request.headers.get("X-Recovery") != "fresh":
            if active:
                socket.recv(timeout=5)
            assert disconnect.wait(5)
            socket.close(code=1011)
            return
        socket.send(json.dumps({"type": "response.future", "restored": True}))
        assert json.loads(socket.recv(timeout=5))["stream_id"] == "worker"
        socket.send(json.dumps(response_event("completed", "worker", id="resp_restored")))

    with script_server(script, expected_connections=2) as url:
        async with session_for(
            mode,
            url,
            replace(LIMITS, max_lanes=2),
            connection_options={"on_reconnecting": reconnect, "initial_delay": 0, "max_retries": 1},
        ) as driver:
            old = driver.session.lane("worker")
            if active:
                await driver.call(old, "send", {"type": "response.create"})
            old.close()
            disconnect.set()
            assert (await driver.call(driver.session.default, "recv")).restored
            new = driver.session.lane("worker")
            await driver.call(new, "send", {"type": "response.create"})
            assert (await driver.call(new, "get_final_response")).id == "resp_restored"


@pytest.mark.parametrize("send", [False, True])
@pytest.mark.parametrize("registered_before_reconnect", [False, True])
async def test_sync_reconnect_preserves_lanes_registered_on_replacement_socket(
    send: bool,
    registered_before_reconnect: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    disconnect = threading.Event()
    cleanup_started = threading.Event()
    allow_cleanup = threading.Event()

    def reconnect(_event: ReconnectingEvent) -> ReconnectingOverrides:
        return {"extra_headers": {"X-Recovery": "fresh"}}

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        if socket.request.headers.get("X-Recovery") != "fresh":
            assert disconnect.wait(5)
            socket.close(code=1011)
            return
        if send:
            assert json.loads(socket.recv(timeout=5))["stream_id"] == "new"
        socket.send(json.dumps({"type": "response.future", "restored": True}))

    with script_server(script, expected_connections=2) as url:
        async with session_for(
            "sync",
            url,
            connection_options={"on_reconnecting": reconnect, "initial_delay": 0, "max_retries": 1},
        ) as driver:
            router = driver.session._router
            reconnected = router.reconnected
            new = driver.session.lane("new") if registered_before_reconnect else None

            def delayed_cleanup(connection: object) -> None:
                cleanup_started.set()
                assert allow_cleanup.wait(5)
                reconnected(connection)

            monkeypatch.setattr(router, "reconnected", delayed_cleanup)
            disconnect.set()
            try:
                assert await asyncio.to_thread(cleanup_started.wait, 5)
                if new is None:
                    new = driver.session.lane("new")
                if send:
                    await driver.call(new, "send", {"type": "response.create"})
                new.close()
            finally:
                allow_cleanup.set()
            assert (await driver.call(driver.session.default, "recv")).restored
            with pytest.raises(ValueError, match="already registered"):
                driver.session.lane("new")


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_custom_upgrade_headers_preserve_auth_and_connection_precedence(mode: str) -> None:
    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        headers = socket.request.headers
        assert headers["Authorization"] == "Bearer fake-contract-key"
        assert headers["X-Customer-Header"] == "connection value"
        assert headers["X-Client-Only"] == "from client"
        assert headers["X-Connection-Only"] == "from connection"
        assert headers.get_all("X-Customer-Header") == ["connection value"]
        assert "X-Omit-Me" not in headers
        assert "User-Agent" not in headers
        socket.recv(timeout=5)
        socket.send(json.dumps(response_event("completed")))

    with script_server(script) as url:
        async with session_for(
            mode,
            url,
            client_headers={
                "x-customer-header": "client value",
                "X-Client-Only": "from client",
                "X-Omit-Me": "removed",
            },
            connection_headers={
                "X-Customer-Header": "connection value",
                "X-Connection-Only": "from connection",
                "x-omit-me": omit,
                "user-agent": omit,
            },
        ) as driver:
            await driver.call(driver.session.default, "send", {"type": "response.create"})
            assert (await driver.call(driver.session.default, "get_final_response")).id == "resp_default"


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("inspect_raw", [False, True])
async def test_detached_lane_events_do_not_change_default_response(mode: str, inspect_raw: bool) -> None:
    release = threading.Event()
    orphaned = [
        response_event("created", "detached"),
        response_event("completed", "detached"),
        {"type": "error", "stream_id": "detached", "error": {"code": "invalid_value", "message": "synthetic"}},
    ]

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.recv(timeout=5)
        socket.send(json.dumps(response_event("created")))
        socket.send(
            json.dumps(
                {
                    "type": "response.output_item.done",
                    "output_index": 0,
                    "sequence_number": 2,
                    "item": {
                        "type": "function_call",
                        "id": "fc_1",
                        "call_id": "call_1",
                        "name": "lookup",
                        "arguments": "{}",
                    },
                }
            )
        )
        assert release.wait(5)
        for event in orphaned:
            socket.send(json.dumps(event))
        terminal = response_event("completed")
        del terminal["response"]["output"]
        socket.send(json.dumps(terminal))

    with script_server(script) as url:
        async with session_for(mode, url) as driver:
            default = driver.session.default
            detached = driver.session.lane("detached")
            await driver.call(default, "send", {"type": "response.create"})
            await driver.call(detached, "send", {"type": "response.create"})
            await driver.call(default, "recv")
            await driver.call(default, "recv")
            detached.close()
            release.set()
            if inspect_raw:
                for expected in orphaned:
                    assert (await driver.call(default, "recv")).to_dict(exclude_unset=True) == expected
                with pytest.raises(RuntimeError, match="current response"):
                    await driver.call(default, "send", {"type": "response.create"})
            final = await driver.call(default, "get_final_response")
            assert final.id == "resp_default"
            assert final.output[0].call_id == "call_1"


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("overflow", [False, True])
async def test_queue_budget_counts_received_utf8_bytes(mode: str, overflow: bool) -> None:
    frame = json.dumps(
        {"type": "response.future", "value": "\u00e9\U0001f600"}, ensure_ascii=False, separators=(",", ":")
    )
    budget = len(frame.encode("utf-8")) - int(overflow)

    def script(socket: ServerConnection) -> None:
        socket.send(frame)

    with script_server(script) as url:
        async with session_for(mode, url, replace(LIMITS, max_bytes_per_lane=budget)) as driver:
            if overflow:
                with pytest.raises(ResponsesWebSocketBufferError):
                    await driver.call(driver.session.default, "recv")
            else:
                assert (await driver.call(driver.session.default, "recv")).value == "\u00e9\U0001f600"


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("response_limit", ["default", "unlimited", "exact", "overflow"])
async def test_large_response_with_documented_transport_options(mode: str, response_limit: str) -> None:
    text = "x" * (2 * 1024 * 1024)
    output: list[dict[str, Any]] = [
        {
            "type": "message",
            "id": "msg_large",
            "role": "assistant",
            "status": "completed",
            "content": [{"type": "output_text", "text": text, "annotations": [], "logprobs": []}],
        }
    ]
    created = json.dumps(response_event("created")).encode("utf-8")
    frame = json.dumps(response_event("completed", output=output)).encode("utf-8")
    release = threading.Event()
    limits = ResponsesWebSocketLimits(
        max_lanes=LIMITS.max_lanes,
        max_events_per_lane=LIMITS.max_events_per_lane,
        max_events=LIMITS.max_events,
        max_bytes_per_lane=len(frame),
        max_bytes=len(frame),
    )
    if response_limit != "default":
        budget = (
            None if response_limit == "unlimited" else len(created) + len(frame) - int(response_limit == "overflow")
        )
        limits = replace(limits, max_response_bytes=budget)

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(created)
        # Drain the first event so queue limits do not mask accumulation behavior.
        assert release.wait(5)
        socket.send(frame)

    with script_server(script) as url:
        async with session_for(
            mode,
            url,
            limits,
            connection_options={"websocket_connection_options": {"max_size": None}},
        ) as driver:
            await driver.call(driver.session.default, "send", {"type": "response.create"})
            assert (await driver.call(driver.session.default, "recv")).type == "response.created"
            release.set()
            if response_limit == "overflow":
                with pytest.raises(ResponsesWebSocketBufferError, match="max_response_bytes"):
                    await driver.call(driver.session.default, "get_final_response")
            else:
                response = await driver.call(driver.session.default, "get_final_response")
                assert response.output[0].content[0].text == text


async def test_sync_close_progresses_while_command_iterable_is_paused() -> None:
    entered = threading.Event()
    release = threading.Event()

    def tools() -> Generator[dict[str, Any], None, None]:
        entered.set()
        assert release.wait(10)
        yield {"type": "web_search"}

    def script(socket: ServerConnection) -> None:
        # Closing during serialization must not send a request.
        with pytest.raises(ConnectionClosedOK):
            socket.recv(timeout=10)

    with script_server(script) as url:
        async with session_for("sync", url) as driver:
            send = asyncio.create_task(
                driver.call(driver.session.default, "send", {"type": "response.create", "tools": tools()})
            )
            close = None
            try:
                assert await asyncio.to_thread(entered.wait, 5)
                close = asyncio.create_task(asyncio.to_thread(driver.session.close))
                await asyncio.wait_for(asyncio.shield(close), timeout=5)
            finally:
                release.set()
                if close is not None:
                    await close
                with pytest.raises(RuntimeError, match="not active"):
                    await send


async def test_sync_recovery_start_during_serialization_preserves_lane() -> None:
    disconnect = threading.Event()
    reconnecting = threading.Event()
    continue_recovery = threading.Event()

    def reconnect(_event: ReconnectingEvent) -> ReconnectingOverrides:
        reconnecting.set()
        assert continue_recovery.wait(10)
        return {"extra_headers": {"X-Recovery": "fresh"}}

    def tools() -> Generator[dict[str, Any], None, None]:
        disconnect.set()
        assert reconnecting.wait(5)
        yield {"type": "web_search"}

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        if socket.request.headers.get("X-Recovery") != "fresh":
            assert disconnect.wait(5)
            socket.close(code=1011)
            return
        socket.send(json.dumps({"type": "response.future", "ready": True}))
        assert json.loads(socket.recv(timeout=5)) == {"type": "response.create", "input": "restored context"}
        socket.send(json.dumps(response_event("completed", id="resp_restored")))

    with script_server(script, expected_connections=2) as url:
        async with session_for(
            "sync", url, connection_options={"on_reconnecting": reconnect, "initial_delay": 0, "max_retries": 1}
        ) as driver:
            session = driver.session
            try:
                with pytest.raises(RuntimeError, match="reconnecting"):
                    await driver.call(session.default, "send", {"type": "response.create", "tools": tools()})
            finally:
                continue_recovery.set()
            assert (await driver.call(session.default, "recv")).ready is True
            await driver.call(session.default, "send", {"type": "response.create", "input": "restored context"})
            assert (await driver.call(session.default, "get_final_response")).id == "resp_restored"


@pytest.mark.parametrize("recover_before_check", [False, True])
async def test_sync_recovery_before_send_preparation_preserves_lane(
    monkeypatch: pytest.MonkeyPatch, recover_before_check: bool
) -> None:
    disconnect = threading.Event()
    recovered = threading.Event()

    def reconnect(_event: ReconnectingEvent) -> ReconnectingOverrides:
        return {"extra_headers": {"X-Recovery": "fresh"}}

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        if socket.request.headers.get("X-Recovery") != "fresh":
            assert disconnect.wait(5)
            socket.close(code=1011)
            return
        recovered.set()
        socket.send(json.dumps({"type": "response.future", "ready": True}))
        assert json.loads(socket.recv(timeout=5)) == {"type": "response.create", "input": "restored context"}
        socket.send(json.dumps(response_event("completed", id="resp_restored")))

    with script_server(script, expected_connections=2) as url:
        async with session_for(
            "sync", url, connection_options={"on_reconnecting": reconnect, "initial_delay": 0, "max_retries": 1}
        ) as driver:
            session = driver.session
            previous = session.connection._connection
            check_send = session._check_send

            def check_then_reconnect(state: Any) -> None:
                if not recover_before_check:
                    check_send(state)
                disconnect.set()
                assert recovered.wait(5)
                with session._router.condition:
                    assert session._router.condition.wait_for(
                        lambda: session.connection._connection is not previous
                        and not session.connection._is_reconnecting,
                        timeout=5,
                    )
                if recover_before_check:
                    check_send(state)

            monkeypatch.setattr(session, "_check_send", check_then_reconnect)
            with pytest.raises(RuntimeError, match="restore state"):
                await driver.call(session.default, "send", {"type": "response.create", "input": "must not migrate"})
            monkeypatch.setattr(session, "_check_send", check_send)
            assert (await driver.call(session.default, "recv")).ready is True
            await driver.call(session.default, "send", {"type": "response.create", "input": "restored context"})
            assert (await driver.call(session.default, "get_final_response")).id == "resp_restored"


async def test_sync_recovery_cannot_replace_socket_during_send_preparation(monkeypatch: pytest.MonkeyPatch) -> None:
    disconnect = threading.Event()
    replacement_waiting = threading.Event()
    replacement_blocked = threading.Event()
    recovered = threading.Event()

    def reconnect(_event: ReconnectingEvent) -> ReconnectingOverrides:
        return {"extra_headers": {"X-Recovery": "fresh"}}

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        if socket.request.headers.get("X-Recovery") != "fresh":
            assert disconnect.wait(5)
            socket.close(code=1011)
            return
        socket.send(json.dumps({"type": "response.future", "ready": True}))
        # A send prepared on the retired socket must not migrate or be replayed.

    with script_server(script, expected_connections=2) as url:
        async with session_for(
            "sync", url, connection_options={"on_reconnecting": reconnect, "initial_delay": 0, "max_retries": 1}
        ) as driver:
            session = driver.session
            connection_lock = session.connection._connection_lock
            prepare = session._router.prepare
            reconnected = session._router.reconnected
            send = session.connection._connection.send

            class ObservedLock:
                def __enter__(self) -> None:
                    if threading.current_thread() is session._thread:
                        acquired = connection_lock.acquire(blocking=False)
                        if not acquired:
                            replacement_blocked.set()
                        replacement_waiting.set()
                        if acquired:
                            return
                    connection_lock.acquire()

                def __exit__(self, *_args: object) -> None:
                    connection_lock.release()

            def prepare_during_recovery(state: Any, is_create: bool) -> None:
                disconnect.set()
                assert replacement_waiting.wait(5)
                assert replacement_blocked.is_set()
                prepare(state, is_create)

            def observe_recovery(connection: object) -> None:
                reconnected(connection)
                recovered.set()

            def send_after_recovery(data: str) -> None:
                assert recovered.wait(5)
                send(data)

            monkeypatch.setattr(session.connection, "_connection_lock", ObservedLock())
            monkeypatch.setattr(session._router, "prepare", prepare_during_recovery)
            monkeypatch.setattr(session._router, "reconnected", observe_recovery)
            monkeypatch.setattr(session.connection._connection, "send", send_after_recovery)
            with pytest.raises(ConnectionClosedError):
                await driver.call(session.default, "send", {"type": "response.create", "input": "must not migrate"})
            monkeypatch.setattr(session._router, "prepare", prepare)
            assert (await driver.call(session.default, "recv")).ready is True
            # Once preparation finishes, a failed write retains the existing
            # uncertain-delivery contract instead of permitting a duplicate.
            with pytest.raises(RuntimeError, match="Consume the current response"):
                await driver.call(session.default, "send", {"type": "response.create"})
            session.default.close()
            with pytest.raises(ValueError, match="already registered"):
                session.lane()
