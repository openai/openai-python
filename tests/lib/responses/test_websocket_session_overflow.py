from __future__ import annotations

import json
import asyncio
import threading
from dataclasses import replace

import pytest
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
from websockets.sync.server import ServerConnection

from openai.lib.responses_websocket import ResponsesWebSocketBufferError
from openai.types.websocket_reconnection import ReconnectingEvent, ReconnectingOverrides

from .test_websocket_session import LIMITS, session_for, script_server, response_event


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("limit", ["max_events_per_lane", "max_events", "max_bytes_per_lane", "max_bytes"])
async def test_opt_in_overflow_fails_slow_lane_and_preserves_healthy_final(mode: str, limit: str) -> None:
    slow = {"type": "response.future", "stream_id": "slow", "padding": "x" * 1000}
    final = response_event("completed", "healthy")
    cap = 1 if "events" in limit else len(json.dumps(slow).encode()) + 1

    def script(socket: ServerConnection) -> None:
        try:
            socket.recv(timeout=5)
        except ConnectionClosedOK:
            return
        socket.send(json.dumps(slow))
        socket.send(json.dumps(slow))
        socket.send(json.dumps(final))

    with script_server(script) as url:
        async with session_for(
            mode, url, replace(LIMITS, **{limit: cap}), session_options={"isolate_lane_overflow": True}
        ) as driver:
            slow_lane = driver.session.lane("slow")
            healthy = driver.session.lane("healthy")
            await driver.call(healthy, "send", {"type": "response.create"})
            assert (await driver.call(healthy, "get_final_response")).id == "resp_healthy"
            with pytest.raises(ResponsesWebSocketBufferError) as first:
                await driver.call(slow_lane, "recv")
            slow_lane.close()
            with pytest.raises(ResponsesWebSocketBufferError) as again:
                await driver.call(slow_lane, "get_final_response")
            assert again.value is first.value
            with pytest.raises(ValueError, match="already registered"):
                driver.session.lane("slow")


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("byte_pressure", [False, True])
@pytest.mark.parametrize("tie", [False, True])
async def test_aggregate_pressure_uses_existing_backlog_and_registration_ties(
    mode: str, byte_pressure: bool, tie: bool
) -> None:
    def event(lane: str, value: int) -> dict[str, object]:
        return {"type": "response.future", "stream_id": lane, "value": value, "extra": {"kept": True}}

    frames = (
        [event("one", 1), event("two", 2), event("new", 3)]
        if tie
        else [event("one", 1), event("two", 2), event("two", 3), event("one", 4)]
    )
    capacity = 2 if tie else 3
    limits = replace(
        LIMITS,
        **(
            {"max_bytes": capacity * len(json.dumps(frames[0]).encode())} if byte_pressure else {"max_events": capacity}
        ),
    )

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        for frame in frames:
            socket.send(json.dumps(frame))
        socket.recv(timeout=5)
        socket.send(json.dumps(event("new", 9)))

    with script_server(script) as url:
        async with session_for(mode, url, limits, session_options={"isolate_lane_overflow": True}) as driver:
            one = driver.session.lane("one")
            two = driver.session.lane("two")
            new = driver.session.lane("new")
            await driver.call(new, "send", {"type": "response.create"})
            # Keep all backlogs unconsumed until the reader applies pressure.
            # This is only a scheduling barrier; assertions use public lanes.
            for _ in range(500):
                with driver.session._router.condition:
                    if one._state.closed or two._state.closed:
                        break
                await asyncio.sleep(0.01)
            with pytest.raises(ResponsesWebSocketBufferError):
                await driver.call(one if tie else two, "recv")
            expected = [(two, 2), (new, 3)] if tie else [(one, 1), (one, 4)]
            for lane, value in expected:
                observed = await driver.call(lane, "recv")
                assert observed.value == value
                assert observed.extra == {"kept": True}
            # Freed aggregate capacity admits later traffic on the same socket.
            await driver.call(
                new, "send", {"type": "response.steer", "previous_response_id": "synthetic", "input": "synthetic"}
            )
            assert (await driver.call(new, "recv")).value == 9


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("limit", ["max_bytes_per_lane", "max_bytes"])
async def test_oversized_incoming_wakes_failed_lane_without_evicting_other_backlog(mode: str, limit: str) -> None:
    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(json.dumps({"type": "response.future", "stream_id": "other", "value": 7}))
        socket.send(json.dumps({"type": "response.future", "stream_id": "large", "padding": "x" * 2000}))
        socket.send(json.dumps(response_event("completed", "healthy")))

    with script_server(script) as url:
        async with session_for(
            mode, url, replace(LIMITS, **{limit: 1000}), session_options={"isolate_lane_overflow": True}
        ) as driver:
            large = driver.session.lane("large")
            other = driver.session.lane("other")
            healthy = driver.session.lane("healthy")
            pending = asyncio.create_task(driver.call(large, "recv"))
            await asyncio.sleep(0)
            await driver.call(healthy, "send", {"type": "response.create"})
            with pytest.raises(ResponsesWebSocketBufferError):
                await pending
            assert (await driver.call(healthy, "get_final_response")).id == "resp_healthy"
            assert (await driver.call(other, "recv")).value == 7


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_failed_id_drops_before_fallback_but_manual_detach_remains_visible(mode: str) -> None:
    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        for _ in range(8):
            socket.send(json.dumps({"type": "response.future", "stream_id": "failed"}))
        socket.send(json.dumps({"type": "response.future", "stream_id": "manual", "value": 4}))
        socket.send(json.dumps(response_event("completed", "healthy")))
        socket.recv(timeout=5)
        socket.send(json.dumps({"type": "response.future", "value": 9}))

    with script_server(script) as url:
        async with session_for(
            mode, url, replace(LIMITS, max_events_per_lane=1), session_options={"isolate_lane_overflow": True}
        ) as driver:
            failed = driver.session.lane("failed")
            driver.session.lane("manual").close()
            healthy = driver.session.lane("healthy")
            await driver.call(healthy, "send", {"type": "response.create"})
            await driver.call(healthy, "get_final_response")
            with pytest.raises(ResponsesWebSocketBufferError):
                await driver.call(failed, "recv")
            observed = await driver.call(driver.session.default, "recv")
            assert observed.stream_id == "manual" and observed.value == 4
            await driver.call(driver.session.default, "send", {"type": "response.create"})
            assert (await driver.call(driver.session.default, "recv")).value == 9


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_default_failure_loses_default_controls_but_transport_failure_remains_global(mode: str) -> None:
    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        for _ in range(2):
            socket.send(json.dumps({"type": "response.future"}))
        socket.send(json.dumps({"type": "error", "error": {"type": "synthetic", "message": "control"}}))
        socket.send(json.dumps(response_event("completed", "healthy")))
        socket.close(code=1011, reason="synthetic transport failure")

    with script_server(script) as url:
        async with session_for(
            mode, url, replace(LIMITS, max_events_per_lane=1), session_options={"isolate_lane_overflow": True}
        ) as driver:
            healthy = driver.session.lane("healthy")
            await driver.call(healthy, "send", {"type": "response.create"})
            assert (await driver.call(healthy, "get_final_response")).id == "resp_healthy"
            with pytest.raises(ResponsesWebSocketBufferError) as first:
                await driver.call(driver.session.default, "recv")
            with pytest.raises(ResponsesWebSocketBufferError) as second:
                await driver.call(driver.session.default, "get_final_response")
            assert second.value is first.value
            with pytest.raises(ConnectionClosedError):
                await driver.call(healthy, "recv")


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_explicit_false_keeps_fatal_overflow_policy(mode: str) -> None:
    closed = threading.Event()

    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        for _ in range(2):
            socket.send(json.dumps({"type": "response.future"}))
        with pytest.raises(ConnectionClosedOK):
            socket.recv(timeout=5)
        closed.set()

    with script_server(script) as url:
        async with session_for(
            mode, url, replace(LIMITS, max_events_per_lane=1), session_options={"isolate_lane_overflow": False}
        ) as driver:
            await driver.call(driver.session.default, "send", {"type": "response.create"})
            assert await asyncio.to_thread(closed.wait, 5)
            with pytest.raises(ResponsesWebSocketBufferError):
                while True:
                    await driver.call(driver.session.default, "recv")


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("default_failed", [False, True])
async def test_failed_reservation_releases_only_after_reconnect_and_default_restores_explicitly(
    mode: str, default_failed: bool
) -> None:
    disconnect = threading.Event()
    failed_id = None if default_failed else "worker"
    observer_id = "worker" if default_failed else None

    def reconnect(_event: ReconnectingEvent) -> ReconnectingOverrides:
        return {"extra_headers": {"X-Overflow-Recovery": "fresh"}}

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        if socket.request.headers.get("X-Overflow-Recovery") != "fresh":
            socket.recv(timeout=5)
            for _ in range(2):
                socket.send(json.dumps({"type": "response.future", **({"stream_id": failed_id} if failed_id else {})}))
            socket.send(json.dumps(response_event("completed", observer_id)))
            assert disconnect.wait(5)
            socket.close(code=1011)
            return
        socket.send(
            json.dumps(
                {"type": "response.future", "restored": True, **({"stream_id": observer_id} if observer_id else {})}
            )
        )
        command = json.loads(socket.recv(timeout=5))
        assert command.get("stream_id") == failed_id
        socket.send(json.dumps(response_event("completed", failed_id, id="resp_restored")))

    with script_server(script, expected_connections=2) as url:
        async with session_for(
            mode,
            url,
            replace(LIMITS, max_lanes=2, max_events_per_lane=1),
            connection_options={"on_reconnecting": reconnect, "initial_delay": 0, "max_retries": 1},
            session_options={"isolate_lane_overflow": True},
        ) as driver:
            worker = driver.session.lane("worker")
            failed = driver.session.default if default_failed else worker
            observer = worker if default_failed else driver.session.default
            await driver.call(worker, "send", {"type": "response.create"})
            await driver.call(observer, "get_final_response")
            with pytest.raises(ResponsesWebSocketBufferError) as first:
                await driver.call(failed, "recv")
            with pytest.raises(ValueError, match="already registered"):
                driver.session.lane(failed_id)
            disconnect.set()
            assert (await driver.call(observer, "recv")).restored
            new = driver.session.lane(failed_id)
            if default_failed:
                assert driver.session.default is new
            await driver.call(new, "send", {"type": "response.create"})
            assert (await driver.call(new, "get_final_response")).id == "resp_restored"
            with pytest.raises(ResponsesWebSocketBufferError) as again:
                await driver.call(failed, "get_final_response")
            assert again.value is first.value


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_overflow_invalidates_cached_final_with_first_buffer_error(mode: str) -> None:
    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(json.dumps(response_event("completed", "cached")))
        socket.recv(timeout=5)
        for _ in range(2):
            socket.send(json.dumps({"type": "response.future", "stream_id": "cached"}))
        socket.send(json.dumps(response_event("completed", "healthy")))

    with script_server(script) as url:
        async with session_for(
            mode, url, replace(LIMITS, max_events_per_lane=1), session_options={"isolate_lane_overflow": True}
        ) as driver:
            cached = driver.session.lane("cached")
            healthy = driver.session.lane("healthy")
            await driver.call(cached, "send", {"type": "response.create"})
            assert (await driver.call(cached, "get_final_response")).id == "resp_cached"
            await driver.call(healthy, "send", {"type": "response.create"})
            await driver.call(healthy, "get_final_response")
            with pytest.raises(ResponsesWebSocketBufferError) as first:
                await driver.call(cached, "get_final_response")
            with pytest.raises(ResponsesWebSocketBufferError) as second:
                await driver.call(cached, "recv")
            assert second.value is first.value


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_queue_failure_replaces_prior_response_collection_error(mode: str) -> None:
    def script(socket: ServerConnection) -> None:
        socket.recv(timeout=5)
        socket.send(json.dumps(response_event("created", "large")))
        socket.recv(timeout=5)
        for _ in range(2):
            socket.send(json.dumps({"type": "response.future", "stream_id": "large"}))
        socket.send(json.dumps({"type": "response.future", "stream_id": "healthy", "value": 7}))

    with script_server(script) as url:
        async with session_for(
            mode,
            url,
            replace(LIMITS, max_events_per_lane=1, max_response_bytes=1),
            session_options={"isolate_lane_overflow": True},
        ) as driver:
            large = driver.session.lane("large")
            healthy = driver.session.lane("healthy")
            await driver.call(large, "send", {"type": "response.create"})
            assert (await driver.call(large, "recv")).type == "response.created"
            with pytest.raises(ResponsesWebSocketBufferError, match="max_response_bytes"):
                await driver.call(large, "get_final_response")
            await driver.call(healthy, "send", {"type": "response.create"})
            assert (await driver.call(healthy, "recv")).value == 7
            with pytest.raises(ResponsesWebSocketBufferError, match="buffered event") as first:
                await driver.call(large, "get_final_response")
            with pytest.raises(ResponsesWebSocketBufferError) as again:
                await driver.call(large, "recv")
            assert again.value is first.value
