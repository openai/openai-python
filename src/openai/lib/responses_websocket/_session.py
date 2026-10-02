from __future__ import annotations

import re
import json
import time
import asyncio
import threading
from types import TracebackType
from typing import Any, cast
from weakref import WeakSet
from collections import deque
from dataclasses import dataclass
from typing_extensions import Self

from ..._types import omit
from ..._utils import maybe_transform
from ..._compat import model_copy
from ..._models import BaseModel
from ..._exceptions import WebSocketConnectionClosedError
from ...types.responses import Response, ResponseStreamEvent
from ..streaming.responses import ResponseStreamState
from ...resources.responses.responses import ResponsesConnection, AsyncResponsesConnection
from ...types.responses.responses_client_event import ResponsesClientEvent
from ...types.responses.responses_server_event import ResponsesServerEvent
from ...types.responses.responses_client_event_param import ResponsesClientEventParam


@dataclass(frozen=True)
class ResponsesWebSocketLimits:
    """Application-selected limits for the opt-in session, not server limits.

    Byte counts use received message bytes, before parsing. They bound
    buffered event data, not transport framing, decoding, or Python object overhead.
    ``max_response_bytes`` optionally bounds the total event data fed into one
    accumulator; its default of ``None`` leaves response accumulation uncapped.
    Choose values appropriate to your output, including images and tool results.
    """

    max_lanes: int
    max_events_per_lane: int
    max_events: int
    max_bytes_per_lane: int
    max_bytes: int
    max_response_bytes: int | None = None

    def __post_init__(self) -> None:
        for name, value in vars(self).items():
            if name == "max_response_bytes" and value is None:
                continue
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError("WebSocket session limits must be positive integers")


class ResponsesWebSocketBufferError(RuntimeError):
    """A session or response exceeded an application-selected buffer limit."""


class ResponsesWebSocketError(RuntimeError):
    """A request-scoped protocol error. The original event is available as ``event``."""

    def __init__(self, event: ResponsesServerEvent) -> None:
        super().__init__("The Responses WebSocket request returned an error event")
        self.event = event


_claimed: WeakSet[object] = WeakSet()
_claim_lock = threading.Lock()


def _claim(connection: object) -> None:
    with _claim_lock:
        if connection in _claimed:
            raise RuntimeError("This connection already has a WebSocket session")
        _claimed.add(connection)


def _release(connection: object) -> None:
    with _claim_lock:
        _claimed.discard(connection)


def _field(event: object, name: str) -> Any:
    return cast("dict[str, Any]", event).get(name) if isinstance(event, dict) else getattr(event, name, None)


def _command(event: ResponsesClientEvent | ResponsesClientEventParam, stream_id: str | None) -> tuple[str, bool]:
    data = event.to_dict(exclude_unset=True) if isinstance(event, BaseModel) else dict(event)
    is_create = bool(data.get("type") == "response.create")
    if is_create:
        if "stream_id" in data and data["stream_id"] != stream_id:
            raise ValueError("The command stream_id does not match its lane")
        if stream_id is not None:
            data["stream_id"] = stream_id
    return json.dumps(maybe_transform(data, ResponsesClientEventParam)), is_create


class _Accumulator:
    def __init__(self, limit: int | None) -> None:
        self.limit = limit
        self.size = 0
        self.state: ResponseStreamState[object] | None = None
        self.final: Response | None = None
        self.error: Exception | None = None

    def add(self, event: ResponsesServerEvent, size: int) -> None:
        kind = _field(event, "type")
        if kind == "response.created":
            self.size = 0
            self.final = None
            self.error = None
            self.state = ResponseStreamState(input_tools=omit, text_format=omit)
        if kind == "error":
            self.state = None
            self.size = 0
            self.final = None
            self.error = ResponsesWebSocketError(event)
            return
        if self.error is not None:
            return
        # Finalized items and the terminal response are authoritative. WebSocket
        # deltas need not include all of the SSE item/part setup events, so feed
        # only these compatible events to the existing final-response accumulator.
        # Unknown events and deltas remain available untouched to the caller.
        compatible = kind in {
            "response.created",
            "response.output_item.done",
            "response.completed",
        }
        terminal = kind in {"response.completed", "response.failed", "response.incomplete"}
        if terminal and _field(event, "response") is None:
            raise ValueError("Terminal WebSocket event is missing response")
        if compatible or terminal:
            self.size += size
            if self.limit is not None and self.size > self.limit:
                self.state = None
                self.final = None
                raise ResponsesWebSocketBufferError("Response accumulation exceeded max_response_bytes")
        if self.state is not None and compatible:
            # Accumulation must not mutate the raw event visible to callers.
            self.state.handle_event(cast(ResponseStreamEvent, model_copy(event, deep=True)))
        if terminal:
            self.final = cast(Response, _field(event, "response"))
            if kind == "response.completed" and self.state is not None:
                self.final = self.state._completed_response
            elif self.state is not None and getattr(self.final, "output", None) is None:
                self.final = model_copy(self.final)
                self.final.output = [
                    self.state._completed_output[index] for index in sorted(self.state._completed_output)
                ]
            self.state = None
            self.size = 0


class _LaneState:
    def __init__(self, stream_id: str | None, limit: int | None) -> None:
        self.stream_id = stream_id
        self.queue: deque[tuple[ResponsesServerEvent, int]] = deque()
        self.size = 0
        self.closed = False
        self.in_flight = False
        self.closed_connection: object | None = None
        self.received_generation = 0
        self.consumed_generation = 0
        self.wake = asyncio.Event()
        self.accumulator = _Accumulator(limit)


class _Router:
    def __init__(
        self, limits: ResponsesWebSocketLimits, connection: ResponsesConnection | AsyncResponsesConnection
    ) -> None:
        self.connection = connection
        self.limits = limits
        self.condition = threading.Condition()
        self.lanes: dict[str | None, _LaneState] = {}
        self.events = 0
        self.size = 0
        self.ended = False
        self.error: BaseException | None = None
        self.default = self.register(None)

    def register(self, stream_id: object) -> _LaneState:
        if stream_id is not None and (
            not isinstance(stream_id, str) or re.fullmatch(r"[A-Za-z0-9_.-]{1,256}", stream_id) is None
        ):
            raise ValueError("stream_id must be None or 1–256 ASCII letters, digits, underscores, hyphens or periods")
        with self.condition:
            if self.ended:
                raise RuntimeError("The WebSocket session has ended")
            if stream_id in self.lanes:
                raise ValueError("A lane with this stream_id is already registered")
            if len(self.lanes) >= self.limits.max_lanes:
                raise ResponsesWebSocketBufferError("The session exceeded max_lanes")
            lane = _LaneState(stream_id, self.limits.max_response_bytes)
            self.lanes[stream_id] = lane
            if stream_id is None:
                self.default = lane
            return lane

    def detach(self, lane: _LaneState) -> None:
        with self.condition:
            if lane.closed:
                return
            lane.closed = True
            lane.closed_connection = self.connection._connection
            self.events -= len(lane.queue)
            self.size -= lane.size
            lane.queue.clear()
            lane.size = 0
            lane.accumulator = _Accumulator(self.limits.max_response_bytes)
            # A terminal can be followed by an automatic steering successor.
            # Keep every registered ID and its max_lanes slot until reconnect.
            lane.wake.set()
            self.condition.notify_all()

    def reconnected(self, connection: object) -> None:
        with self.condition:
            for stream_id, lane in list(self.lanes.items()):
                if lane.closed and lane.closed_connection is not connection:
                    # A lane closed on the new socket must survive cleanup,
                    # including when it was registered before reconnect.
                    del self.lanes[stream_id]

    def dispatch(self, event: ResponsesServerEvent, size: int) -> None:
        with self.condition:
            if self.ended:
                return
            stream_id = _field(event, "stream_id")
            lane = self.lanes.get(stream_id, self.default)
            if lane.closed:
                lane = self.default
            if lane.closed:
                return
            if (
                len(lane.queue) >= self.limits.max_events_per_lane
                or self.events >= self.limits.max_events
                or lane.size + size > self.limits.max_bytes_per_lane
                or self.size + size > self.limits.max_bytes
            ):
                raise ResponsesWebSocketBufferError("The session exceeded its buffered event limits")
            lane.queue.append((event, size))
            if _field(event, "stream_id") == lane.stream_id and _field(event, "type") == "response.created":
                lane.received_generation += 1
                lane.in_flight = True
            lane.size += size
            self.size += size
            self.events += 1
            lane.wake.set()
            self.condition.notify_all()

    def finish(self, error: BaseException | None = None) -> None:
        with self.condition:
            self.ended = True
            if self.error is None:
                self.error = error
            for lane in self.lanes.values():
                lane.wake.set()
            self.condition.notify_all()

    def pop(self, lane: _LaneState) -> ResponsesServerEvent | None:
        # The caller holds the condition. No await occurs after dequeueing.
        if lane.closed:
            raise EOFError("The WebSocket lane is detached")
        if lane.queue:
            event, size = lane.queue.popleft()
            lane.size -= size
            self.size -= size
            self.events -= 1
            # Unregistered named streams remain visible on the default lane,
            # but cannot change that lane's response or in-flight state.
            if _field(event, "stream_id") != lane.stream_id:
                return event
            try:
                lane.accumulator.add(event, size)
            except Exception as exc:
                lane.accumulator.error = exc
                lane.accumulator.state = None
            if _field(event, "type") == "response.created":
                lane.consumed_generation += 1
                lane.in_flight = True
            elif _field(event, "type") in {"response.completed", "response.failed", "response.incomplete", "error"}:
                lane.in_flight = lane.received_generation > lane.consumed_generation
            return event
        if self.ended:
            if self.error is not None:
                raise self.error
            raise EOFError("The WebSocket connection closed")
        return None

    def prepare(self, lane: _LaneState, is_create: bool) -> None:
        with self.condition:
            if self.ended or lane.closed:
                raise RuntimeError("The WebSocket session or lane is not active")
            if is_create:
                if lane.in_flight:
                    raise RuntimeError("Consume the current response before sending another create on this lane")
                lane.accumulator = _Accumulator(self.limits.max_response_bytes)
                lane.in_flight = True


class ResponsesWebSocketLane:
    """A routed view of one session. ``close`` detaches it without closing the socket.

    Use a single consumer per lane. Cancel a synchronous wait with ``recv(timeout=...)``;
    a timeout never consumes an event. Different lanes may be consumed concurrently.
    """

    def __init__(self, session: ResponsesWebSocketSession, state: _LaneState) -> None:
        self._session = session
        self._state = state

    def send(self, event: ResponsesClientEvent | ResponsesClientEventParam) -> None:
        # Pin the transport before checking recovery so this write cannot migrate.
        connection = self._session.connection._connection
        self._session._check_send(self._state)
        # Serializing supported iterables can call back into the connection.
        data, is_create = _command(event, self._state.stream_id)
        with self._session.connection._connection_lock:
            if self._session.connection._is_reconnecting:
                raise RuntimeError("The WebSocket connection is reconnecting; restore state before sending")
            if connection is not self._session.connection._connection:
                raise RuntimeError("The WebSocket connection changed; restore state before sending")
            # Reserve the lane before recovery can publish a replacement socket.
            self._session._router.prepare(self._state, is_create)
        # The legacy send_raw recovery queue can replay uncertain writes.
        # Send directly to this physical socket so lane requests never enter it.
        connection.send(data)

    def recv(self, *, timeout: float | None = None) -> ResponsesServerEvent:
        if self._session._thread is None:
            raise RuntimeError("Enter the WebSocket session before receiving events")
        deadline = None if timeout is None else time.monotonic() + timeout
        router = self._session._router
        with router.condition:
            while True:
                event = router.pop(self._state)
                if event is not None:
                    return event
                remaining = None if deadline is None else deadline - time.monotonic()
                if remaining is not None and remaining <= 0:
                    raise TimeoutError("Timed out waiting for a Responses WebSocket event")
                router.condition.wait(remaining)

    def get_final_response(self, *, timeout: float | None = None) -> Response:
        """Consume this response's remaining events; failed/incomplete are final results."""
        deadline = None if timeout is None else time.monotonic() + timeout
        generation = self._state.consumed_generation
        while (
            self._state.accumulator.final is not None
            and self._state.consumed_generation == generation
            and self._state.received_generation > generation
        ):
            remaining = None if deadline is None else max(0.0, deadline - time.monotonic())
            self.recv(timeout=remaining)
        while self._state.accumulator.final is None:
            if self._state.accumulator.error is not None:
                raise self._state.accumulator.error
            remaining = None if deadline is None else max(0.0, deadline - time.monotonic())
            self.recv(timeout=remaining)
        return self._state.accumulator.final

    def close(self) -> None:
        self._session._router.detach(self._state)


class ResponsesWebSocketSession:
    """Own one existing connection and route its events with one background reader.

    Enter the session before sending. While active, consume events only through
    its lanes, not the connection's recv/iterator/dispatch_events. Closing the
    session closes its connection; closing a lane does not. Register lanes before
    sending requests. Events for unregistered lanes go to the default lane for
    inspection, without changing its response state. Every registered lane, including
    the default and closed lanes, reserves its ID and max_lanes slot until reconnect.
    Keep a lane open for sequential responses. Reconnect releases closed lanes;
    open lanes remain registered on the new socket.

    Recovery remains the existing connection's opt-in policy. Reconnecting a
    transport does not restore server-side response state or replay lane sends.
    """

    def __init__(self, connection: ResponsesConnection, *, limits: ResponsesWebSocketLimits) -> None:
        self.connection = connection
        self._router = _Router(limits, connection)
        self._thread: threading.Thread | None = None
        self._closed = False
        self._owns_connection = False
        self.default = ResponsesWebSocketLane(self, self._router.default)

    def __enter__(self) -> Self:
        if self._thread is not None or self._closed:
            raise RuntimeError("A WebSocket session can only be entered once")
        _claim(self.connection)
        self._owns_connection = True
        self._thread = threading.Thread(target=self._read, name="responses-websocket", daemon=True)
        try:
            self._thread.start()
        except Exception:
            self._release_connection()
            self._thread = None
            raise
        return self

    def _release_connection(self) -> None:
        # The reader and close caller may both finish cleanup. Release only our claim.
        with _claim_lock:
            if self._owns_connection:
                _claimed.discard(self.connection)
                self._owns_connection = False

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, traceback: TracebackType | None
    ) -> None:
        try:
            self.close()
        except Exception:
            if exc is None:
                raise

    def lane(self, stream_id: str | None = None) -> ResponsesWebSocketLane:
        lane = ResponsesWebSocketLane(self, self._router.register(stream_id))
        if stream_id is None:
            self.default = lane
        return lane

    def _check_send(self, lane: _LaneState) -> None:
        if self._thread is None or self._closed or self._router.ended or lane.closed:
            raise RuntimeError("The WebSocket session or lane is not active")
        if self.connection._is_reconnecting:
            raise RuntimeError("The WebSocket connection is reconnecting; restore state before sending")

    def _read(self) -> None:
        from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

        try:
            while True:
                try:
                    data = self.connection.recv_bytes()
                except ConnectionClosedOK:
                    break
                except ConnectionClosedError as exc:
                    if self.connection._reconnect(exc):
                        self._router.reconnected(self.connection._connection)
                        continue
                    unsent = self.connection._send_queue.drain()
                    if unsent:
                        raise WebSocketConnectionClosedError(
                            "WebSocket connection closed with unsent messages", unsent_messages=unsent
                        ) from exc
                    raise
                self._router.dispatch(self.connection.parse_event(data), len(data))
                del data
        except Exception as exc:
            self._router.finish(exc)
            try:
                self.connection.close()
            except Exception:
                pass  # Preserve the original reader/overflow failure.
        finally:
            self._router.finish()
            if self._closed:
                self._release_connection()

    def close(self) -> None:
        if self._closed and (self._thread is None or not self._thread.is_alive()):
            return
        self._closed = True
        self._router.finish()
        if self._thread is None:
            return
        try:
            self.connection.close()
        finally:
            if self._thread is not threading.current_thread():
                self._thread.join(timeout=5)
                if self._thread.is_alive():
                    raise RuntimeError("The Responses WebSocket reader did not stop after close")
                self._release_connection()


class AsyncResponsesWebSocketLane:
    """An async routed lane. Canceling a recv/final-response wait never closes it."""

    def __init__(self, session: AsyncResponsesWebSocketSession, state: _LaneState) -> None:
        self._session = session
        self._state = state

    async def send(self, event: ResponsesClientEvent | ResponsesClientEventParam) -> None:
        # Pin the transport before checking recovery so this write cannot migrate.
        connection = self._session.connection._connection
        self._session._check_send(self._state)
        data, is_create = _command(event, self._state.stream_id)
        self._session._router.prepare(self._state, is_create)
        # Bypass the legacy recovery queue, including a reconnect starting now.
        await connection.send(data)

    async def recv(self) -> ResponsesServerEvent:
        if self._session._task is None:
            raise RuntimeError("Enter the WebSocket session before receiving events")
        router = self._session._router
        while True:
            with router.condition:
                event = router.pop(self._state)
                if event is not None:
                    return event
                self._state.wake.clear()
            await self._state.wake.wait()

    async def get_final_response(self) -> Response:
        generation = self._state.consumed_generation
        while (
            self._state.accumulator.final is not None
            and self._state.consumed_generation == generation
            and self._state.received_generation > generation
        ):
            await self.recv()
        while self._state.accumulator.final is None:
            if self._state.accumulator.error is not None:
                raise self._state.accumulator.error
            await self.recv()
        return self._state.accumulator.final

    def close(self) -> None:
        self._session._router.detach(self._state)


class AsyncResponsesWebSocketSession:
    """Async counterpart of ResponsesWebSocketSession, owning the connection lifetime."""

    def __init__(self, connection: AsyncResponsesConnection, *, limits: ResponsesWebSocketLimits) -> None:
        self.connection = connection
        self._router = _Router(limits, connection)
        self._task: asyncio.Task[None] | None = None
        self._close_task: asyncio.Task[None] | None = None
        self._closed = False
        self.default = AsyncResponsesWebSocketLane(self, self._router.default)

    async def __aenter__(self) -> Self:
        if self._task is not None or self._closed:
            raise RuntimeError("A WebSocket session can only be entered once")
        _claim(self.connection)
        self._task = asyncio.create_task(self._read(), name="responses-websocket")
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, traceback: TracebackType | None
    ) -> None:
        try:
            await self.close()
        except Exception:
            if exc is None:
                raise

    def lane(self, stream_id: str | None = None) -> AsyncResponsesWebSocketLane:
        lane = AsyncResponsesWebSocketLane(self, self._router.register(stream_id))
        if stream_id is None:
            self.default = lane
        return lane

    def _check_send(self, lane: _LaneState) -> None:
        if self._task is None or self._closed or self._router.ended or lane.closed:
            raise RuntimeError("The WebSocket session or lane is not active")
        if self.connection._is_reconnecting:
            raise RuntimeError("The WebSocket connection is reconnecting; restore state before sending")

    async def _read(self) -> None:
        from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

        try:
            while True:
                try:
                    data = await self.connection.recv_bytes()
                except ConnectionClosedOK:
                    break
                except ConnectionClosedError as exc:
                    if await self.connection._reconnect(exc):
                        self._router.reconnected(self.connection._connection)
                        continue
                    unsent = self.connection._send_queue.drain()
                    if unsent:
                        raise WebSocketConnectionClosedError(
                            "WebSocket connection closed with unsent messages", unsent_messages=unsent
                        ) from exc
                    raise
                self._router.dispatch(self.connection.parse_event(data), len(data))
                del data
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self._router.finish(exc)
            try:
                await self.connection.close()
            except Exception:
                # Preserve the reader failure already delivered to every lane.
                pass
        finally:
            self._router.finish()

    async def close(self) -> None:
        if self._close_task is None:
            self._closed = True
            self._router.finish()
            if self._task is None:
                return
            self._close_task = asyncio.create_task(self._close(self._task), name="responses-websocket-close")
        # Cancellation stops this caller's wait, not cleanup or its ownership claim.
        await asyncio.shield(self._close_task)

    async def _close(self, reader: asyncio.Task[None]) -> None:
        try:
            reader.cancel()
            try:
                await reader
            except asyncio.CancelledError:
                # Cancellation is expected after stopping the reader above.
                pass
            await self.connection.close()
        finally:
            _release(self.connection)
