from __future__ import annotations

import json
import asyncio
import threading
from typing import Any
from unittest.mock import Mock, AsyncMock
from concurrent.futures import ThreadPoolExecutor

import pytest
from websockets.frames import Close
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

from openai import OpenAI, AsyncOpenAI, WebSocketConnectionClosedError
from openai._send_queue import SendQueue
from tests.lib.test_websocket_redirects import RECONNECTING_RESOURCES, options, resource
from tests.test_websocket_initial_backlog import InitialWriteFails, event


def close_error(code: int) -> ConnectionClosedOK | ConnectionClosedError:
    frame = Close(code, "synthetic")
    cls = ConnectionClosedOK if code == 1000 else ConnectionClosedError
    return cls(frame, frame, True)


@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
@pytest.mark.parametrize("observe", ["unsent", "post-terminal-send"])
def test_reader_closes_while_public_backlog_write_blocks(
    name: str, observe: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    ws = InitialWriteFails()
    started, release = threading.Event(), threading.Event()
    terminal = close_error(1000)

    def send(data: str | bytes) -> None:
        ws.send(data)
        if ws.attempts[-1] == "B":
            started.set()
            assert release.wait(5)
            raise OSError("blocked write failed after closure")

    def recv(**_kwargs: Any) -> bytes:
        ws.closed = True
        raise terminal

    transport = Mock(send=Mock(side_effect=send), recv=Mock(side_effect=recv), close=ws.close)
    monkeypatch.setattr("websockets.sync.client.connect", Mock(return_value=transport))
    with OpenAI(api_key="synthetic-only") as client:
        manager = resource(client, name).connect(**options(client, name))
        for label in "ABC":
            manager.send(event(label))
        with manager as connection, ThreadPoolExecutor(max_workers=2) as workers:
            writing = workers.submit(connection.send_raw, b"D")
            try:
                assert started.wait(3), "retained write did not start"
                try:
                    next(iter(connection))
                    pytest.fail("terminal recv yielded an event")
                except (WebSocketConnectionClosedError, StopIteration) as err:
                    if observe == "unsent":
                        assert isinstance(err, WebSocketConnectionClosedError)
                        assert err.__cause__ is terminal
                        assert [json.loads(f)["event_id"] if isinstance(f, str) else f for f in err.unsent_frames] == [
                            "C",
                            b"D",
                        ]
                    else:
                        with pytest.raises(ConnectionClosedOK):
                            workers.submit(connection.send_raw, b"E").result(timeout=3)
            finally:
                release.set()
                with pytest.raises(OSError, match="blocked write"):
                    writing.result(timeout=3)
            assert ws.attempts == ["A", "B"]


def test_terminal_drain_wins_when_new_send_waits_for_queue_admission(monkeypatch: pytest.MonkeyPatch) -> None:
    ws = InitialWriteFails()
    writing_b, release_b = threading.Event(), threading.Event()
    admitting_e, release_e = threading.Event(), threading.Event()
    enqueue = SendQueue.enqueue

    def paused_enqueue(queue: SendQueue, data: str | bytes, **kwargs: Any) -> Any:
        if data == b"E":
            # Pause immediately before the real queue lock/admission operation.
            admitting_e.set()
            assert release_e.wait(5)
        return enqueue(queue, data, **kwargs)

    def send(data: str | bytes) -> None:
        ws.send(data)
        if ws.attempts[-1] == "B":
            writing_b.set()
            assert release_b.wait(5)
            raise OSError("blocked write failed after closure")

    def recv(**_kwargs: Any) -> bytes:
        ws.closed = True
        raise close_error(1000)

    monkeypatch.setattr(SendQueue, "enqueue", paused_enqueue)
    transport = Mock(send=Mock(side_effect=send), recv=Mock(side_effect=recv), close=ws.close)
    monkeypatch.setattr("websockets.sync.client.connect", Mock(return_value=transport))
    with OpenAI(api_key="synthetic-only") as client:
        manager = client.live.connect()
        for label in "ABC":
            manager.send({"type": "session.update", "event_id": label, "session": {}})
        with manager as connection, ThreadPoolExecutor(max_workers=2) as workers:
            writing = workers.submit(connection.send_raw, b"D")
            sending = None
            try:
                assert writing_b.wait(3)
                sending = workers.submit(connection.send_raw, b"E")
                assert admitting_e.wait(3)
                try:
                    next(iter(connection))
                except (StopIteration, WebSocketConnectionClosedError):
                    pass
                release_e.set()
                with pytest.raises(ConnectionClosedOK):
                    sending.result(timeout=3)
            finally:
                release_e.set()
                release_b.set()
                if sending is not None and not sending.done():
                    sending.result(timeout=3)
                with pytest.raises(OSError, match="blocked write"):
                    writing.result(timeout=3)


@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
@pytest.mark.parametrize("observe", ["unsent", "post-terminal-send"])
async def test_async_reader_closes_while_public_backlog_write_blocks(
    name: str, observe: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    ws = InitialWriteFails()
    started, release = asyncio.Event(), asyncio.Event()
    terminal = close_error(1000)

    async def send(data: str | bytes) -> None:
        ws.send(data)
        if ws.attempts[-1] == "B":
            started.set()
            await release.wait()
            raise OSError("blocked write failed after closure")

    def recv(**_kwargs: Any) -> bytes:
        ws.closed = True
        raise terminal

    transport = Mock(
        send=AsyncMock(side_effect=send), recv=AsyncMock(side_effect=recv), close=AsyncMock(side_effect=ws.close)
    )
    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", AsyncMock(return_value=transport))
    async with AsyncOpenAI(api_key="synthetic-only") as client:
        manager = resource(client, name).connect(**options(client, name))
        for label in "ABC":
            manager.send(event(label))
        async with manager as connection:
            writing = asyncio.create_task(connection.send_raw(b"D"))
            try:
                await asyncio.wait_for(started.wait(), timeout=3)
                try:
                    await anext(aiter(connection))
                    pytest.fail("terminal recv yielded an event")
                except (WebSocketConnectionClosedError, StopAsyncIteration) as err:
                    if observe == "unsent":
                        assert isinstance(err, WebSocketConnectionClosedError)
                        assert err.__cause__ is terminal
                        assert [json.loads(f)["event_id"] if isinstance(f, str) else f for f in err.unsent_frames] == [
                            "C",
                            b"D",
                        ]
                    else:
                        with pytest.raises(ConnectionClosedOK):
                            await asyncio.wait_for(connection.send_raw(b"E"), timeout=3)
            finally:
                release.set()
                with pytest.raises(OSError, match="blocked write"):
                    await writing
            assert ws.attempts == ["A", "B"]


@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
def test_close_with_recoverable_code_during_public_recovery_flush(name: str, monkeypatch: pytest.MonkeyPatch) -> None:
    initial = close_error(1012)
    interrupted = close_error(1011)
    callbacks: list[int] = []
    attempted: list[str | bytes] = []
    original = Mock(recv=Mock(side_effect=initial))

    def send(data: str | bytes) -> None:
        attempted.append(data)
        connection.close(code=1011)
        raise interrupted

    replacement = Mock(send=Mock(side_effect=send))

    def reconnect(e: Any) -> None:
        callbacks.append(e.close_code)

    def dial(*_args: Any, **_kwargs: Any) -> Any:
        if callbacks:
            connection.send(event("B"))
            connection.send_raw(b"C")
            return replacement
        return original

    monkeypatch.setattr("websockets.sync.client.connect", Mock(side_effect=dial))
    with OpenAI(api_key="synthetic-only") as client:
        manager = resource(client, name).connect(
            **options(client, name), on_reconnecting=reconnect, max_retries=3, initial_delay=0
        )
        with manager as connection:
            with pytest.raises(WebSocketConnectionClosedError) as captured:
                next(iter(connection))
            assert captured.value.__cause__ is initial
            assert captured.value.unsent_frames == [b"C"]
            assert callbacks == [1012]
            assert len(attempted) == 1


@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
async def test_async_close_with_recoverable_code_during_public_recovery_flush(
    name: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    initial = close_error(1012)
    interrupted = close_error(1011)
    callbacks: list[int] = []
    attempted: list[str | bytes] = []
    original = Mock(recv=AsyncMock(side_effect=initial), close=AsyncMock())

    async def send(data: str | bytes) -> None:
        attempted.append(data)
        await connection.close(code=1011)
        raise interrupted

    replacement = Mock(send=AsyncMock(side_effect=send), close=AsyncMock())

    def reconnect(e: Any) -> None:
        callbacks.append(e.close_code)

    async def dial(*_args: Any, **_kwargs: Any) -> Any:
        if callbacks:
            await connection.send(event("B"))
            await connection.send_raw(b"C")
            return replacement
        return original

    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", AsyncMock(side_effect=dial))
    async with AsyncOpenAI(api_key="synthetic-only") as client:
        manager = resource(client, name).connect(
            **options(client, name), on_reconnecting=reconnect, max_retries=3, initial_delay=0
        )
        async with manager as connection:
            with pytest.raises(WebSocketConnectionClosedError) as captured:
                await anext(aiter(connection))
            assert captured.value.__cause__ is initial
            assert captured.value.unsent_frames == [b"C"]
            assert callbacks == [1012]
            assert len(attempted) == 1


def test_recovery_waits_for_older_public_flush_owner(monkeypatch: pytest.MonkeyPatch) -> None:
    ws = InitialWriteFails()
    started, release, opened, replacement_read = (threading.Event() for _ in range(4))
    sent: list[str | bytes] = []

    def send(data: str | bytes) -> None:
        ws.send(data)
        if ws.attempts[-1] == "B":
            started.set()
            assert release.wait(5)
            raise OSError("old owner interrupted")

    def read_replacement(**_kwargs: Any) -> bytes:
        replacement_read.set()
        return b'{"type":"session.created","session":{"id":"synthetic"}}'

    original = Mock(send=Mock(side_effect=send), recv=Mock(side_effect=close_error(1012)), close=ws.close)
    replacement = Mock(send=sent.append, recv=Mock(side_effect=read_replacement))
    calls = 0

    def dial(*_args: Any, **_kwargs: Any) -> Any:
        nonlocal calls
        calls += 1
        if calls == 1:
            return original
        opened.set()
        return replacement

    monkeypatch.setattr("websockets.sync.client.connect", Mock(side_effect=dial))
    with OpenAI(api_key="synthetic-only") as client:
        manager = client.live.connect(on_reconnecting=lambda _e: None, initial_delay=0)
        for label in "ABC":
            manager.send({"type": "session.update", "event_id": label, "session": {}})
        with manager as connection, ThreadPoolExecutor(max_workers=2) as workers:
            writing = workers.submit(connection.send_raw, b"D")
            reading = None
            try:
                assert started.wait(3)
                reading = workers.submit(lambda: next(iter(connection)))
                assert opened.wait(3)
                assert not replacement_read.wait(0.15), "replacement was declared ready with old frames still owned"
            finally:
                release.set()
                with pytest.raises(OSError, match="old owner"):
                    writing.result(timeout=3)
                if reading is not None:
                    reading.result(timeout=3)
            assert [json.loads(f)["event_id"] if isinstance(f, str) else f for f in sent] == ["C", b"D"]


async def test_async_recovery_waits_for_older_public_flush_owner(monkeypatch: pytest.MonkeyPatch) -> None:
    ws = InitialWriteFails()
    started, release, opened, replacement_read = (asyncio.Event() for _ in range(4))
    sent: list[str | bytes] = []

    async def send(data: str | bytes) -> None:
        ws.send(data)
        if ws.attempts[-1] == "B":
            started.set()
            await release.wait()
            raise OSError("old owner interrupted")

    def read_replacement(**_kwargs: Any) -> bytes:
        replacement_read.set()
        return b'{"type":"session.created","session":{"id":"synthetic"}}'

    original = Mock(send=AsyncMock(side_effect=send), recv=AsyncMock(side_effect=close_error(1012)), close=AsyncMock())
    replacement = Mock(
        send=AsyncMock(side_effect=sent.append), recv=AsyncMock(side_effect=read_replacement), close=AsyncMock()
    )
    calls = 0

    async def dial(*_args: Any, **_kwargs: Any) -> Any:
        nonlocal calls
        calls += 1
        if calls == 1:
            return original
        opened.set()
        return replacement

    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", AsyncMock(side_effect=dial))
    async with AsyncOpenAI(api_key="synthetic-only") as client:
        manager = client.live.connect(on_reconnecting=lambda _e: None, initial_delay=0)
        for label in "ABC":
            manager.send({"type": "session.update", "event_id": label, "session": {}})
        async with manager as connection:
            writing = asyncio.create_task(connection.send_raw(b"D"))
            reading = None
            try:
                await asyncio.wait_for(started.wait(), timeout=3)
                reading = asyncio.ensure_future(anext(aiter(connection)))
                await asyncio.wait_for(opened.wait(), timeout=3)
                with pytest.raises(asyncio.TimeoutError):
                    await asyncio.wait_for(replacement_read.wait(), timeout=0.15)
            finally:
                release.set()
                with pytest.raises(OSError, match="old owner"):
                    await writing
                if reading is not None:
                    await reading
            assert [json.loads(f)["event_id"] if isinstance(f, str) else f for f in sent] == ["C", b"D"]


@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
@pytest.mark.parametrize("timing", ["during-write", "after-write"])
def test_ordinary_flush_hands_recovery_frames_to_reader(
    name: str, timing: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    ws = InitialWriteFails()
    started, release_write = threading.Event(), threading.Event()
    handshake, release_handshake = threading.Event(), threading.Event()
    recovered: list[str | bytes] = []
    ready = b'{"type":"error","event_id":"fixture","error":{"type":"fixture","message":"ready"}}'

    def send(data: str | bytes) -> None:
        ws.send(data)
        if data == b"C":
            started.set()
            assert release_write.wait(5)

    def recv(**_kwargs: Any) -> bytes:
        ws.closed = True
        raise close_error(1012)

    original = Mock(send=Mock(side_effect=send), recv=Mock(side_effect=recv), close=ws.close)
    replacement = Mock(send=Mock(side_effect=recovered.append), recv=Mock(return_value=ready))
    dials = 0

    def dial(*_args: Any, **_kwargs: Any) -> Any:
        nonlocal dials
        dials += 1
        if dials == 1:
            return original
        handshake.set()
        assert release_handshake.wait(5)
        return replacement

    monkeypatch.setattr("websockets.sync.client.connect", Mock(side_effect=dial))
    with OpenAI(api_key="synthetic-only") as client:
        manager = resource(client, name).connect(
            **options(client, name), on_reconnecting=lambda _e: None, initial_delay=0, max_retries=1
        )
        for value in "AB":
            manager.send(event(value))
        with manager as connection, ThreadPoolExecutor(max_workers=2) as pool:
            writing = pool.submit(connection.send_raw, b"C")
            reading = None
            try:
                assert started.wait(3)
                reading = pool.submit(lambda: next(iter(connection)))
                assert handshake.wait(3)
                if timing == "during-write":
                    connection.send_raw(b"D")
                release_write.set()
                writing.result(timeout=3)
                if timing == "after-write":
                    connection.send_raw(b"D")
                assert recovered == []
            finally:
                release_write.set()
                release_handshake.set()
            assert reading is not None
            assert reading.result(timeout=3).type == "error"
            assert ws.attempts == ["A", "B", b"C"]
            assert recovered == [b"D"]
            connection.send_raw(b"E")
            assert recovered == [b"D", b"E"]


@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
@pytest.mark.parametrize("timing", ["during-write", "after-write"])
async def test_async_ordinary_flush_hands_recovery_frames_to_reader(
    name: str, timing: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    ws = InitialWriteFails()
    started, release_write = asyncio.Event(), asyncio.Event()
    handshake, release_handshake = asyncio.Event(), asyncio.Event()
    recovered: list[str | bytes] = []
    ready = b'{"type":"error","event_id":"fixture","error":{"type":"fixture","message":"ready"}}'

    async def send(data: str | bytes) -> None:
        ws.send(data)
        if data == b"C":
            started.set()
            await release_write.wait()

    async def recv(**_kwargs: Any) -> bytes:
        ws.closed = True
        raise close_error(1012)

    original = Mock(
        send=AsyncMock(side_effect=send), recv=AsyncMock(side_effect=recv), close=AsyncMock(side_effect=ws.close)
    )
    replacement = Mock(
        send=AsyncMock(side_effect=recovered.append), recv=AsyncMock(return_value=ready), close=AsyncMock()
    )
    dials = 0

    async def dial(*_args: Any, **_kwargs: Any) -> Any:
        nonlocal dials
        dials += 1
        if dials == 1:
            return original
        handshake.set()
        await release_handshake.wait()
        return replacement

    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", AsyncMock(side_effect=dial))
    async with AsyncOpenAI(api_key="synthetic-only") as client:
        manager = resource(client, name).connect(
            **options(client, name), on_reconnecting=lambda _e: None, initial_delay=0, max_retries=1
        )
        for value in "AB":
            manager.send(event(value))
        async with manager as connection:
            writing = asyncio.create_task(connection.send_raw(b"C"))
            reading = None
            try:
                await asyncio.wait_for(started.wait(), 3)
                reading = asyncio.ensure_future(anext(aiter(connection)))
                await asyncio.wait_for(handshake.wait(), 3)
                if timing == "during-write":
                    await connection.send_raw(b"D")
                release_write.set()
                await asyncio.wait_for(writing, 3)
                if timing == "after-write":
                    await connection.send_raw(b"D")
                assert recovered == []
            finally:
                release_write.set()
                release_handshake.set()
            assert reading is not None
            assert (await asyncio.wait_for(reading, 3)).type == "error"
            assert ws.attempts == ["A", "B", b"C"]
            assert recovered == [b"D"]
            await connection.send_raw(b"E")
            assert recovered == [b"D", b"E"]


@pytest.mark.parametrize("owner_state", ["waiting", "released"])
def test_recovery_takes_frame_from_ordinary_flusher_with_stale_socket(
    owner_state: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    ws = InitialWriteFails()
    first_entered, resume_first = threading.Event(), threading.Event()
    last_write, resume_last = threading.Event(), threading.Event()
    first_waiting = threading.Event()
    handshake, finish_handshake = threading.Event(), threading.Event()
    first_ident: int | None = None
    recovered: list[str | bytes] = []
    ready = b'{"type":"error","event_id":"fixture","error":{"type":"fixture","message":"ready"}}'
    original_flush = SendQueue.flush_sync
    original_begin = SendQueue._begin_flush

    def delayed_flush(queue: SendQueue, *args: Any, **kwargs: Any) -> None:
        if threading.get_ident() == first_ident:
            first_entered.set()
            assert resume_first.wait(5)
        original_flush(queue, *args, **kwargs)

    def observed_begin(queue: SendQueue) -> Any:
        batch = original_begin(queue)
        if threading.get_ident() == first_ident and isinstance(batch, threading.Event):
            first_waiting.set()
        return batch

    def send(data: str | bytes) -> None:
        ws.send(data)
        if data == b"D":
            last_write.set()
            assert resume_last.wait(5)

    def recv(**_kwargs: Any) -> bytes:
        ws.closed = True
        raise close_error(1012)

    original = Mock(send=Mock(side_effect=send), recv=Mock(side_effect=recv), close=ws.close)
    replacement = Mock(send=Mock(side_effect=recovered.append), recv=Mock(return_value=ready))
    dials = 0

    def dial(*_args: Any, **_kwargs: Any) -> Any:
        nonlocal dials
        dials += 1
        if dials == 1:
            return original
        handshake.set()
        assert finish_handshake.wait(5)
        return replacement

    def first_send(connection: Any) -> None:
        nonlocal first_ident
        first_ident = threading.get_ident()
        connection.send_raw(b"C")

    monkeypatch.setattr("websockets.sync.client.connect", Mock(side_effect=dial))
    monkeypatch.setattr(SendQueue, "flush_sync", delayed_flush)
    monkeypatch.setattr(SendQueue, "_begin_flush", observed_begin)
    with OpenAI(api_key="synthetic-only") as client:
        manager = client.live.connect(on_reconnecting=lambda _e: None, initial_delay=0, max_retries=1)
        for value in "AB":
            manager.send({"type": "session.update", "event_id": value, "session": {}})
        with manager as connection, ThreadPoolExecutor(max_workers=3) as pool:
            first = pool.submit(first_send, connection)
            reading = None
            try:
                assert first_entered.wait(3)
                second = pool.submit(connection.send_raw, b"D")
                assert last_write.wait(3)
                if owner_state == "waiting":
                    resume_first.set()
                    assert first_waiting.wait(3)
                reading = pool.submit(lambda: next(iter(connection)))
                assert handshake.wait(3)
                connection.send_raw(b"E")
                resume_last.set()
                if owner_state == "released":
                    second.result(timeout=3)
                    resume_first.set()
                first.result(timeout=3)
                second.result(timeout=3)
            finally:
                resume_first.set()
                resume_last.set()
                finish_handshake.set()
            assert reading is not None
            assert reading.result(timeout=3).type == "error"
            assert ws.attempts == ["A", "B", b"C", b"D"]
            assert recovered == [b"E"]
            connection.send_raw(b"F")
            assert recovered == [b"E", b"F"]


@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
@pytest.mark.parametrize("old_closed", [False, True], ids=["old-still-writable", "old-closed"])
def test_successful_frame_hands_unattempted_batch_tail_to_reader(
    name: str, old_closed: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    ws = InitialWriteFails()
    started, release, opened = (threading.Event() for _ in range(3))
    sent: list[str | bytes] = []

    def send(data: str | bytes) -> None:
        ws.send(data)
        if ws.attempts[-1] == "B":
            started.set()
            assert release.wait(5)

    def recv(**_kwargs: Any) -> bytes:
        if old_closed:
            ws.close()
        raise close_error(1012)

    original = Mock(send=Mock(side_effect=send), recv=Mock(side_effect=recv), close=ws.close)
    replacement = Mock(send=sent.append, recv=Mock(return_value=b'{"type":"error","error":{"message":"fixture"}}'))
    calls = 0

    def dial(*_args: Any, **_kwargs: Any) -> Any:
        nonlocal calls
        calls += 1
        if calls == 1:
            return original
        opened.set()
        return replacement

    monkeypatch.setattr("websockets.sync.client.connect", Mock(side_effect=dial))
    with OpenAI(api_key="synthetic-only") as client:
        manager = resource(client, name).connect(
            **options(client, name), on_reconnecting=lambda _e: None, initial_delay=0
        )
        for label in "ABC":
            manager.send(event(label))
        with manager as connection, ThreadPoolExecutor(max_workers=2) as workers:
            writing = workers.submit(connection.send_raw, b"D")
            reading = None
            try:
                assert started.wait(3)
                reading = workers.submit(lambda: next(iter(connection)))
                assert opened.wait(3)
                connection.send_raw(b"E")
            finally:
                release.set()
                # B completed successfully. Only unattempted C/D/E remain.
                writing.result(timeout=3)
                if reading is not None:
                    reading.result(timeout=3)
            assert ws.attempts == ["A", "B"]
            assert [json.loads(f)["event_id"] if isinstance(f, str) else f for f in sent] == ["C", b"D", b"E"]
            connection.send_raw(b"F")
            assert sent[-1] == b"F"


@pytest.mark.asyncio
@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
@pytest.mark.parametrize("old_closed", [False, True], ids=["old-still-writable", "old-closed"])
async def test_async_successful_frame_hands_unattempted_batch_tail_to_reader(
    name: str, old_closed: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    ws = InitialWriteFails()
    started, release, opened = (asyncio.Event() for _ in range(3))
    sent: list[str | bytes] = []

    async def send(data: str | bytes) -> None:
        ws.send(data)
        if ws.attempts[-1] == "B":
            started.set()
            await release.wait()

    def recv(**_kwargs: Any) -> bytes:
        if old_closed:
            ws.close()
        raise close_error(1012)

    original = Mock(
        send=AsyncMock(side_effect=send),
        recv=AsyncMock(side_effect=recv),
        close=AsyncMock(side_effect=ws.close),
    )
    replacement = Mock(
        send=AsyncMock(side_effect=sent.append),
        recv=AsyncMock(return_value=b'{"type":"error","error":{"message":"fixture"}}'),
        close=AsyncMock(),
    )
    calls = 0

    async def dial(*_args: Any, **_kwargs: Any) -> Any:
        nonlocal calls
        calls += 1
        if calls == 1:
            return original
        opened.set()
        return replacement

    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", AsyncMock(side_effect=dial))
    async with AsyncOpenAI(api_key="synthetic-only") as client:
        manager = resource(client, name).connect(
            **options(client, name), on_reconnecting=lambda _e: None, initial_delay=0
        )
        for label in "ABC":
            manager.send(event(label))
        async with manager as connection:
            writing = asyncio.create_task(connection.send_raw(b"D"))
            reading = None
            try:
                await asyncio.wait_for(started.wait(), timeout=3)
                reading = asyncio.ensure_future(anext(aiter(connection)))
                await asyncio.wait_for(opened.wait(), timeout=3)
                await connection.send_raw(b"E")
            finally:
                release.set()
                await writing
                if reading is not None:
                    await reading
            assert ws.attempts == ["A", "B"]
            assert [json.loads(f)["event_id"] if isinstance(f, str) else f for f in sent] == ["C", b"D", b"E"]
            await connection.send_raw(b"F")
            assert sent[-1] == b"F"


def test_reentrant_sync_sender_does_not_wait_for_itself(monkeypatch: pytest.MonkeyPatch) -> None:
    ws = InitialWriteFails()

    def send(data: str | bytes) -> None:
        ws.send(data)
        if ws.attempts[-1] == "B":
            connection.send_raw(b"E")

    monkeypatch.setattr(
        "websockets.sync.client.connect", Mock(return_value=Mock(send=Mock(side_effect=send), close=ws.close))
    )
    with OpenAI(api_key="synthetic-only") as client:
        manager = client.live.connect()
        for label in "ABC":
            manager.send({"type": "session.update", "event_id": label, "session": {}})
        with manager as connection:
            connection.send_raw(b"D")
            assert ws.attempts == ["A", "B", "C", b"D", b"E"]


@pytest.mark.asyncio
async def test_reentrant_async_sender_does_not_wait_for_itself(monkeypatch: pytest.MonkeyPatch) -> None:
    ws = InitialWriteFails()

    async def send(data: str | bytes) -> None:
        ws.send(data)
        if ws.attempts[-1] == "B":
            await connection.send_raw(b"E")

    monkeypatch.setattr(
        "openai.lib._websocket._WebSocketConnect",
        AsyncMock(return_value=Mock(send=AsyncMock(side_effect=send), close=AsyncMock(side_effect=ws.close))),
    )
    async with AsyncOpenAI(api_key="synthetic-only") as client:
        manager = client.live.connect()
        for label in "ABC":
            manager.send({"type": "session.update", "event_id": label, "session": {}})
        async with manager as connection:
            await asyncio.wait_for(connection.send_raw(b"D"), timeout=3)
            assert ws.attempts == ["A", "B", "C", b"D", b"E"]


@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
@pytest.mark.parametrize("ending", ["terminal-reader", "explicit-close"])
def test_waiting_ordinary_sender_reports_terminal_unsent_frame(
    name: str, ending: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    ws = InitialWriteFails()
    entered, release, queued = (threading.Event() for _ in range(3))
    terminal = close_error(1000)
    write_error = OSError("older attempted B failed")
    original_enqueue = SendQueue.enqueue

    def enqueue(self: SendQueue, data: str | bytes, **kwargs: Any) -> bool:
        admitted = original_enqueue(self, data, **kwargs)
        if data == b"E":
            queued.set()
        return admitted

    def send(data: str | bytes) -> None:
        ws.send(data)
        if ws.attempts[-1] == "B":
            entered.set()
            assert release.wait(5)
            raise write_error

    def recv(**_kwargs: Any) -> bytes:
        ws.closed = True
        raise terminal

    monkeypatch.setattr(SendQueue, "enqueue", enqueue)
    monkeypatch.setattr(
        "websockets.sync.client.connect",
        Mock(return_value=Mock(send=Mock(side_effect=send), recv=Mock(side_effect=recv), close=ws.close)),
    )
    with OpenAI(api_key="synthetic-only") as client:
        manager = resource(client, name).connect(**options(client, name))
        for label in "ABC":
            manager.send(event(label))
        with manager as connection, ThreadPoolExecutor(max_workers=2) as workers:
            owner = workers.submit(connection.send_raw, b"D")
            try:
                assert entered.wait(3)
                waiting = workers.submit(connection.send_raw, b"E")
                assert queued.wait(3)
                if ending == "terminal-reader":
                    with pytest.raises(WebSocketConnectionClosedError) as got:
                        next(iter(connection))
                    assert got.value.__cause__ is terminal
                    assert [
                        json.loads(f)["event_id"] if isinstance(f, str) else f for f in got.value.unsent_frames
                    ] == ["C", b"D", b"E"]
                else:
                    connection.close()
            finally:
                release.set()
            # The active owner must keep the original send error. Its unattempted
            # D frame still appears in the reader's unsent report.
            with pytest.raises(OSError) as got:
                owner.result(timeout=3)
            assert got.value is write_error
            with pytest.raises(WebSocketConnectionClosedError) as got:
                waiting.result(timeout=3)
            assert [json.loads(f)["event_id"] if isinstance(f, str) else f for f in got.value.unsent_frames] == [
                "C",
                b"D",
                b"E",
            ]
            assert ws.attempts == ["A", "B"]


@pytest.mark.asyncio
@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
@pytest.mark.parametrize("ending", ["terminal-reader", "explicit-close"])
async def test_async_waiting_ordinary_sender_reports_terminal_unsent_frame(
    name: str, ending: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    ws = InitialWriteFails()
    entered, release, queued = (asyncio.Event() for _ in range(3))
    terminal = close_error(1000)
    write_error = OSError("older attempted B failed")
    original_enqueue = SendQueue.enqueue

    def enqueue(self: SendQueue, data: str | bytes, **kwargs: Any) -> bool:
        admitted = original_enqueue(self, data, **kwargs)
        if data == b"E":
            queued.set()
        return admitted

    async def send(data: str | bytes) -> None:
        ws.send(data)
        if ws.attempts[-1] == "B":
            entered.set()
            await release.wait()
            raise write_error

    def recv(**_kwargs: Any) -> bytes:
        ws.closed = True
        raise terminal

    monkeypatch.setattr(SendQueue, "enqueue", enqueue)
    monkeypatch.setattr(
        "openai.lib._websocket._WebSocketConnect",
        AsyncMock(
            return_value=Mock(
                send=AsyncMock(side_effect=send),
                recv=AsyncMock(side_effect=recv),
                close=AsyncMock(side_effect=ws.close),
            )
        ),
    )
    async with AsyncOpenAI(api_key="synthetic-only") as client:
        manager = resource(client, name).connect(**options(client, name))
        for label in "ABC":
            manager.send(event(label))
        async with manager as connection:
            owner = asyncio.create_task(connection.send_raw(b"D"))
            try:
                await asyncio.wait_for(entered.wait(), timeout=3)
                waiting = asyncio.create_task(connection.send_raw(b"E"))
                await asyncio.wait_for(queued.wait(), timeout=3)
                if ending == "terminal-reader":
                    with pytest.raises(WebSocketConnectionClosedError) as got:
                        await anext(aiter(connection))
                    assert got.value.__cause__ is terminal
                    assert [
                        json.loads(f)["event_id"] if isinstance(f, str) else f for f in got.value.unsent_frames
                    ] == ["C", b"D", b"E"]
                else:
                    await connection.close()
            finally:
                release.set()
            with pytest.raises(OSError) as got:
                await owner
            assert got.value is write_error
            with pytest.raises(WebSocketConnectionClosedError) as got:
                await waiting
            assert [json.loads(f)["event_id"] if isinstance(f, str) else f for f in got.value.unsent_frames] == [
                "C",
                b"D",
                b"E",
            ]
            assert ws.attempts == ["A", "B"]


@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
def test_reader_owns_senders_deferred_during_recovery_takeover(name: str, monkeypatch: pytest.MonkeyPatch) -> None:
    ws = InitialWriteFails()
    entered, release, queued, handshake, finish = (threading.Event() for _ in range(5))
    terminal = close_error(1001)
    write_error = OSError("older attempted B failed")
    original_enqueue = SendQueue.enqueue
    dials = 0

    def enqueue(self: SendQueue, data: str | bytes, **kwargs: Any) -> bool:
        admitted = original_enqueue(self, data, **kwargs)
        if data == b"E":
            queued.set()
        return admitted

    def send(data: str | bytes) -> None:
        ws.send(data)
        if ws.attempts[-1] == "B":
            entered.set()
            assert release.wait(5)
            raise write_error

    def dial(*_args: Any, **_kwargs: Any) -> Any:
        nonlocal dials
        dials += 1
        if dials == 1:
            return Mock(send=Mock(side_effect=send), recv=Mock(side_effect=terminal), close=ws.close)
        handshake.set()
        assert finish.wait(5)
        raise OSError("replacement setup failed")

    monkeypatch.setattr(SendQueue, "enqueue", enqueue)
    monkeypatch.setattr("websockets.sync.client.connect", Mock(side_effect=dial))
    with OpenAI(api_key="synthetic-only") as client:
        manager = resource(client, name).connect(
            **options(client, name), on_reconnecting=lambda _: None, max_retries=1, initial_delay=0
        )
        for label in "ABC":
            manager.send(event(label))
        with manager as connection, ThreadPoolExecutor(max_workers=3) as workers:
            owner = workers.submit(connection.send_raw, b"D")
            try:
                assert entered.wait(3)
                waiting = workers.submit(connection.send_raw, b"E")
                assert queued.wait(3)
                reading = workers.submit(next, iter(connection))
                assert handshake.wait(3)
                connection.send_raw(b"F")
                release.set()
                with pytest.raises(OSError) as got:
                    owner.result(timeout=3)
                assert got.value is write_error
                # Recovery owns E and F until its outcome; this cannot block
                # the caller that may need to let recovery proceed.
                waiting.result(timeout=3)
            finally:
                release.set()
                finish.set()
            with pytest.raises(WebSocketConnectionClosedError) as got:
                reading.result(timeout=3)
            assert got.value.__cause__ is terminal
            assert [json.loads(f)["event_id"] if isinstance(f, str) else f for f in got.value.unsent_frames] == [
                "C",
                b"D",
                b"E",
                b"F",
            ]
            assert ws.attempts == ["A", "B"]


@pytest.mark.asyncio
@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
async def test_async_reader_owns_senders_deferred_during_recovery_takeover(
    name: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    ws = InitialWriteFails()
    entered, release, queued, handshake, finish = (asyncio.Event() for _ in range(5))
    terminal = close_error(1001)
    write_error = OSError("older attempted B failed")
    original_enqueue = SendQueue.enqueue
    dials = 0

    def enqueue(self: SendQueue, data: str | bytes, **kwargs: Any) -> bool:
        admitted = original_enqueue(self, data, **kwargs)
        if data == b"E":
            queued.set()
        return admitted

    async def send(data: str | bytes) -> None:
        ws.send(data)
        if ws.attempts[-1] == "B":
            entered.set()
            await release.wait()
            raise write_error

    async def dial(*_args: Any, **_kwargs: Any) -> Any:
        nonlocal dials
        dials += 1
        if dials == 1:
            return Mock(
                send=AsyncMock(side_effect=send),
                recv=AsyncMock(side_effect=terminal),
                close=AsyncMock(side_effect=ws.close),
            )
        handshake.set()
        await finish.wait()
        raise OSError("replacement setup failed")

    monkeypatch.setattr(SendQueue, "enqueue", enqueue)
    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", AsyncMock(side_effect=dial))
    async with AsyncOpenAI(api_key="synthetic-only") as client:
        manager = resource(client, name).connect(
            **options(client, name), on_reconnecting=lambda _: None, max_retries=1, initial_delay=0
        )
        for label in "ABC":
            manager.send(event(label))
        async with manager as connection:
            owner = asyncio.create_task(connection.send_raw(b"D"))
            try:
                await asyncio.wait_for(entered.wait(), timeout=3)
                waiting = asyncio.create_task(connection.send_raw(b"E"))
                await asyncio.wait_for(queued.wait(), timeout=3)
                reading = asyncio.create_task(anext(aiter(connection)))
                await asyncio.wait_for(handshake.wait(), timeout=3)
                await connection.send_raw(b"F")
                release.set()
                with pytest.raises(OSError) as got:
                    await owner
                assert got.value is write_error
                await asyncio.wait_for(waiting, timeout=3)
            finally:
                release.set()
                finish.set()
            with pytest.raises(WebSocketConnectionClosedError) as got:
                await reading
            assert got.value.__cause__ is terminal
            assert [json.loads(f)["event_id"] if isinstance(f, str) else f for f in got.value.unsent_frames] == [
                "C",
                b"D",
                b"E",
                b"F",
            ]
            assert ws.attempts == ["A", "B"]


def test_closing_after_prepare_retains_unattempted_manager_and_waiting_frames(monkeypatch: pytest.MonkeyPatch) -> None:
    ws = InitialWriteFails()
    prepared, release, queued, closing, close_done = (threading.Event() for _ in range(5))
    original_flush = SendQueue.flush_sync
    original_enqueue = SendQueue.enqueue

    def flush(self: SendQueue, send: Any, **kwargs: Any) -> None:
        original_prepare = kwargs["prepare_send"]

        def prepare() -> Any:
            result = original_prepare()
            if ws.attempts == ["A", "B"] and not prepared.is_set():
                prepared.set()
                assert release.wait(5)
            return result

        kwargs["prepare_send"] = prepare
        original_flush(self, send, **kwargs)

    def enqueue(self: SendQueue, data: str | bytes, **kwargs: Any) -> bool:
        admitted = original_enqueue(self, data, **kwargs)
        if data == b"E":
            queued.set()
        return admitted

    def close(**_kwargs: Any) -> None:
        closing.set()
        assert close_done.wait(5)
        ws.close()

    monkeypatch.setattr(SendQueue, "flush_sync", flush)
    monkeypatch.setattr(SendQueue, "enqueue", enqueue)
    terminal = close_error(1000)
    monkeypatch.setattr(
        "websockets.sync.client.connect",
        Mock(
            return_value=Mock(
                send=Mock(side_effect=ws.send),
                recv=Mock(side_effect=terminal),
                close=Mock(side_effect=close),
            )
        ),
    )
    with OpenAI(api_key="synthetic-only") as client:
        manager = resource(client, "realtime").connect(**options(client, "realtime"))
        for label in "ABC":
            manager.send(event(label))
        with manager as connection, ThreadPoolExecutor(max_workers=3) as workers:
            owner = workers.submit(connection.send_raw, b"D")
            try:
                assert prepared.wait(3)
                waiting = workers.submit(connection.send_raw, b"E")
                assert queued.wait(3)
                shutdown = workers.submit(connection.close)
                assert closing.wait(3)
                release.set()
                with pytest.raises(WebSocketConnectionClosedError):
                    owner.result(timeout=3)
                with pytest.raises(WebSocketConnectionClosedError):
                    waiting.result(timeout=3)
                # The physical close has not completed. The prepared old socket
                # remains writable, but no marked unsent frame can be started.
                assert ws.attempts == ["A", "B"]
            finally:
                release.set()
                close_done.set()
            shutdown.result(timeout=3)
            with pytest.raises(WebSocketConnectionClosedError) as got:
                next(iter(connection))
            assert [json.loads(f)["event_id"] if isinstance(f, str) else f for f in got.value.unsent_frames] == [
                "C",
                b"D",
                b"E",
            ]


@pytest.mark.asyncio
async def test_async_close_with_successful_inflight_write_retains_waiting_frames(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ws = InitialWriteFails()
    prepared, queued, closing, close_done = (asyncio.Event() for _ in range(4))
    # Async preparation and pop do not await. A sibling close can take over
    # when B yields to the transport; successful B stays out of the report.
    release_b = asyncio.Event()
    original_enqueue = SendQueue.enqueue

    def enqueue(self: SendQueue, data: str | bytes, **kwargs: Any) -> bool:
        admitted = original_enqueue(self, data, **kwargs)
        if data == b"E":
            queued.set()
        return admitted

    async def send(data: str | bytes) -> None:
        ws.send(data)
        if ws.attempts[-1] == "B":
            prepared.set()
            await release_b.wait()

    async def close(**_kwargs: Any) -> None:
        closing.set()
        await close_done.wait()
        ws.close()

    monkeypatch.setattr(SendQueue, "enqueue", enqueue)
    terminal = close_error(1000)
    monkeypatch.setattr(
        "openai.lib._websocket._WebSocketConnect",
        AsyncMock(
            return_value=Mock(
                send=AsyncMock(side_effect=send),
                recv=AsyncMock(side_effect=terminal),
                close=AsyncMock(side_effect=close),
            )
        ),
    )
    async with AsyncOpenAI(api_key="synthetic-only") as client:
        manager = resource(client, "realtime").connect(**options(client, "realtime"))
        for label in "ABC":
            manager.send(event(label))
        async with manager as connection:
            owner = asyncio.create_task(connection.send_raw(b"D"))
            try:
                await asyncio.wait_for(prepared.wait(), timeout=3)
                waiting = asyncio.create_task(connection.send_raw(b"E"))
                await asyncio.wait_for(queued.wait(), timeout=3)
                shutdown = asyncio.create_task(connection.close())
                await asyncio.wait_for(closing.wait(), timeout=3)
                release_b.set()
                with pytest.raises(WebSocketConnectionClosedError):
                    await owner
                with pytest.raises(WebSocketConnectionClosedError):
                    await waiting
                assert ws.attempts == ["A", "B"]
            finally:
                release_b.set()
                close_done.set()
            await shutdown
            with pytest.raises(WebSocketConnectionClosedError) as got:
                await anext(aiter(connection))
            assert [json.loads(f)["event_id"] if isinstance(f, str) else f for f in got.value.unsent_frames] == [
                "C",
                b"D",
                b"E",
            ]
