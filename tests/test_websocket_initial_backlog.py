from __future__ import annotations

import json
import asyncio
import threading
from typing import Any
from unittest.mock import Mock, AsyncMock
from concurrent.futures import ThreadPoolExecutor

import pytest
from websockets.frames import Close
from websockets.exceptions import ConnectionClosedOK

from openai import OpenAI, AsyncOpenAI, WebSocketQueueFullError
from openai._send_queue import SendQueue
from tests.lib.test_websocket_redirects import RECONNECTING_RESOURCES, options, resource


def event(label: str) -> dict[str, Any]:
    return {"type": "session.update", "event_id": label, "session": {}}


class InitialWriteFails:
    def __init__(self) -> None:
        self.attempts: list[str | bytes] = []
        self.closed = False
        self.failures: dict[str | bytes, Exception] = {}

    def send(self, data: str | bytes) -> None:
        if self.closed:
            close = Close(1000, "")
            raise ConnectionClosedOK(close, close, True)
        label = json.loads(data)["event_id"] if isinstance(data, str) else data
        self.attempts.append(label)
        if len(self.attempts) == 1:
            raise OSError("initial write fails with the socket still open")
        if label in self.failures:
            raise self.failures[label]

    def close(self, **_kwargs: Any) -> None:
        self.closed = True


@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
@pytest.mark.parametrize("later", ["typed", "empty-raw", "overflow", "after-close"])
def test_public_manager_pending_after_initial_failure(name: str, later: str, monkeypatch: pytest.MonkeyPatch) -> None:
    ws = InitialWriteFails()
    monkeypatch.setattr("websockets.sync.client.connect", Mock(return_value=ws))
    on_reconnecting = Mock()
    with OpenAI(api_key="synthetic-only") as client:
        manager = resource(client, name).connect(
            **options(client, name), max_queue_size=256, on_reconnecting=on_reconnecting
        )
        for label in "ABC":
            manager.send(event(label))
        with manager as connection:
            # Initial failures still warn and enter without an automatic retry.
            assert ws.attempts == ["A"]
            if later == "typed":
                connection.send(event("D"))
                assert ws.attempts == ["A", "B", "C", "D"]
            elif later == "empty-raw":
                connection.send_raw(b"")
                assert ws.attempts == ["A", "B", "C", b""]
            elif later == "overflow":
                with pytest.raises(WebSocketQueueFullError):
                    connection.send_raw(b"D" * 256)
                assert ws.attempts == ["A", "B", "C"]
            else:
                connection.close()
                with pytest.raises(ConnectionClosedOK):
                    connection.send(event("D"))
                assert ws.attempts == ["A"]
        on_reconnecting.assert_not_called()


@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
@pytest.mark.parametrize("later", ["typed", "empty-raw", "overflow", "after-close"])
async def test_async_public_manager_pending_after_initial_failure(
    name: str, later: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    ws = InitialWriteFails()
    transport = Mock(send=AsyncMock(side_effect=ws.send), close=AsyncMock(side_effect=ws.close))
    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", AsyncMock(return_value=transport))
    on_reconnecting = Mock()
    async with AsyncOpenAI(api_key="synthetic-only") as client:
        manager = resource(client, name).connect(
            **options(client, name), max_queue_size=256, on_reconnecting=on_reconnecting
        )
        for label in "ABC":
            manager.send(event(label))
        async with manager as connection:
            assert ws.attempts == ["A"]
            if later == "typed":
                await connection.send(event("D"))
                assert ws.attempts == ["A", "B", "C", "D"]
            elif later == "empty-raw":
                await connection.send_raw(b"")
                assert ws.attempts == ["A", "B", "C", b""]
            elif later == "overflow":
                with pytest.raises(WebSocketQueueFullError):
                    await connection.send_raw(b"D" * 256)
                assert ws.attempts == ["A", "B", "C"]
            else:
                await connection.close()
                with pytest.raises(ConnectionClosedOK):
                    await connection.send(event("D"))
                assert ws.attempts == ["A"]
        on_reconnecting.assert_not_called()


@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
@pytest.mark.parametrize("owner_fails", [False, True], ids=["successful-owner", "failed-owner"])
def test_concurrent_sender_owns_its_joined_frame(name: str, owner_fails: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    ws = InitialWriteFails()
    entered, release, joined = (threading.Event() for _ in range(3))
    error = OSError("owner B failed")
    enqueue = SendQueue.enqueue

    def notified(self: SendQueue, data: str | bytes, **kwargs: Any) -> bool:
        result = enqueue(self, data, **kwargs)
        if data == b"E":
            joined.set()
        return result

    monkeypatch.setattr(SendQueue, "enqueue", notified)

    def send(data: str | bytes) -> None:
        ws.send(data)
        if ws.attempts[-1] == "B":
            entered.set()
            assert release.wait(5)
            if owner_fails:
                raise error

    original = Mock(send=Mock(side_effect=send), close=ws.close)
    monkeypatch.setattr("websockets.sync.client.connect", Mock(return_value=original))
    with OpenAI(api_key="synthetic-only") as client:
        manager = resource(client, name).connect(**options(client, name))
        for label in "ABC":
            manager.send(event(label))
        with manager as connection, ThreadPoolExecutor(max_workers=2) as workers:
            owner = workers.submit(connection.send_raw, b"D")
            joiner = None
            try:
                assert entered.wait(3)
                joiner = workers.submit(connection.send_raw, b"E")
                assert joined.wait(3)
            finally:
                release.set()
                if owner_fails:
                    with pytest.raises(OSError) as got:
                        owner.result(timeout=3)
                    assert got.value is error
                else:
                    owner.result(timeout=3)
                if joiner is not None:
                    joiner.result(timeout=3)
            assert ws.attempts == ["A", "B", "C", b"D", b"E"]


@pytest.mark.asyncio
@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
@pytest.mark.parametrize("owner_fails", [False, True], ids=["successful-owner", "failed-owner"])
async def test_async_concurrent_sender_owns_its_joined_frame(
    name: str, owner_fails: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    ws = InitialWriteFails()
    entered, release, joined = (asyncio.Event() for _ in range(3))
    error = OSError("owner B failed")
    enqueue = SendQueue.enqueue

    def notified(self: SendQueue, data: str | bytes, **kwargs: Any) -> bool:
        result = enqueue(self, data, **kwargs)
        if data == b"E":
            joined.set()
        return result

    monkeypatch.setattr(SendQueue, "enqueue", notified)

    async def send(data: str | bytes) -> None:
        ws.send(data)
        if ws.attempts[-1] == "B":
            entered.set()
            await release.wait()
            if owner_fails:
                raise error

    original = Mock(send=AsyncMock(side_effect=send), close=AsyncMock(side_effect=ws.close))
    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", AsyncMock(return_value=original))
    async with AsyncOpenAI(api_key="synthetic-only") as client:
        manager = resource(client, name).connect(**options(client, name))
        for label in "ABC":
            manager.send(event(label))
        async with manager as connection:
            owner = asyncio.create_task(connection.send_raw(b"D"))
            joiner = None
            try:
                await asyncio.wait_for(entered.wait(), timeout=3)
                joiner = asyncio.create_task(connection.send_raw(b"E"))
                await asyncio.wait_for(joined.wait(), timeout=3)
            finally:
                release.set()
                if owner_fails:
                    with pytest.raises(OSError) as got:
                        await owner
                    assert got.value is error
                else:
                    await owner
                if joiner is not None:
                    await joiner
            assert ws.attempts == ["A", "B", "C", b"D", b"E"]


@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
@pytest.mark.parametrize("failure", ["new-typed", "new-raw", "older", "older-and-overflow"])
def test_public_send_reports_its_drain_failure(name: str, failure: str, monkeypatch: pytest.MonkeyPatch) -> None:
    ws = InitialWriteFails()
    err = OSError("caller-triggered drain failed")
    ws.failures[b"D" if failure == "new-raw" else "D" if failure == "new-typed" else "B"] = err
    monkeypatch.setattr("websockets.sync.client.connect", Mock(return_value=ws))
    on_reconnecting = Mock()
    with OpenAI(api_key="synthetic-only") as client:
        manager = resource(client, name).connect(
            **options(client, name), max_queue_size=256, on_reconnecting=on_reconnecting
        )
        for label in "ABC":
            manager.send(event(label))
        with manager as connection:
            assert ws.attempts == ["A"]
            if failure == "older-and-overflow":
                with pytest.raises(WebSocketQueueFullError):
                    connection.send_raw(b"D" * 256)
                assert ws.attempts == ["A", "B"]
                connection.send_raw(b"E")
                assert ws.attempts == ["A", "B", "C", b"E"]
            else:
                with pytest.raises(OSError) as captured:
                    if failure == "new-raw":
                        connection.send_raw(b"D")
                    else:
                        connection.send(event("D"))
                assert captured.value is err
                if failure == "older":
                    assert ws.attempts == ["A", "B"]
                    connection.send_raw(b"E")
                    assert ws.attempts == ["A", "B", "C", "D", b"E"]
                else:
                    assert ws.attempts == ["A", "B", "C", b"D" if failure == "new-raw" else "D"]
                    connection.send_raw(b"E")
                    assert len(ws.attempts) == 5
        on_reconnecting.assert_not_called()


@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
@pytest.mark.parametrize("failure", ["new-typed", "new-raw", "older", "older-and-overflow"])
async def test_async_public_send_reports_its_drain_failure(
    name: str, failure: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    ws = InitialWriteFails()
    err = OSError("caller-triggered drain failed")
    ws.failures[b"D" if failure == "new-raw" else "D" if failure == "new-typed" else "B"] = err
    transport = Mock(send=AsyncMock(side_effect=ws.send), close=AsyncMock(side_effect=ws.close))
    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", AsyncMock(return_value=transport))
    on_reconnecting = Mock()
    async with AsyncOpenAI(api_key="synthetic-only") as client:
        manager = resource(client, name).connect(
            **options(client, name), max_queue_size=256, on_reconnecting=on_reconnecting
        )
        for label in "ABC":
            manager.send(event(label))
        async with manager as connection:
            assert ws.attempts == ["A"]
            if failure == "older-and-overflow":
                with pytest.raises(WebSocketQueueFullError):
                    await connection.send_raw(b"D" * 256)
                assert ws.attempts == ["A", "B"]
                await connection.send_raw(b"E")
                assert ws.attempts == ["A", "B", "C", b"E"]
            else:
                with pytest.raises(OSError) as captured:
                    if failure == "new-raw":
                        await connection.send_raw(b"D")
                    else:
                        await connection.send(event("D"))
                assert captured.value is err
                if failure == "older":
                    assert ws.attempts == ["A", "B"]
                    await connection.send_raw(b"E")
                    assert ws.attempts == ["A", "B", "C", "D", b"E"]
                else:
                    assert ws.attempts == ["A", "B", "C", b"D" if failure == "new-raw" else "D"]
                    await connection.send_raw(b"E")
                    assert len(ws.attempts) == 5
        on_reconnecting.assert_not_called()


async def test_cancelled_async_joiner_does_not_release_older_flush(monkeypatch: pytest.MonkeyPatch) -> None:
    ws = InitialWriteFails()
    entered, release, joined = (asyncio.Event() for _ in range(3))
    enqueue = SendQueue.enqueue

    def notified(self: SendQueue, data: str | bytes, **kwargs: Any) -> bool:
        result = enqueue(self, data, **kwargs)
        if data == b"E":
            joined.set()
        return result

    monkeypatch.setattr(SendQueue, "enqueue", notified)

    async def send(data: str | bytes) -> None:
        ws.send(data)
        if ws.attempts[-1] == "B":
            entered.set()
            await release.wait()

    monkeypatch.setattr(
        "openai.lib._websocket._WebSocketConnect",
        AsyncMock(return_value=Mock(send=AsyncMock(side_effect=send), close=AsyncMock(side_effect=ws.close))),
    )
    async with AsyncOpenAI(api_key="synthetic-only") as client:
        manager = client.live.connect()
        for label in "ABC":
            manager.send({"type": "session.update", "event_id": label, "session": {}})
        async with manager as connection:
            owner = asyncio.create_task(connection.send_raw(b"D"))
            try:
                await asyncio.wait_for(entered.wait(), timeout=3)
                joiner = asyncio.create_task(connection.send_raw(b"E"))
                await asyncio.wait_for(joined.wait(), timeout=3)
                joiner.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await joiner
                assert ws.attempts == ["A", "B"]
            finally:
                release.set()
                await owner
            # Cancellation after admission does not replay or silently drop E.
            assert ws.attempts == ["A", "B", "C", b"D", b"E"]


async def test_closed_transport_reports_joiner_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    ws = InitialWriteFails()
    entered, release, joined = (asyncio.Event() for _ in range(3))
    enqueue = SendQueue.enqueue

    def notified(self: SendQueue, data: str | bytes, **kwargs: Any) -> bool:
        result = enqueue(self, data, **kwargs)
        if data == b"E":
            joined.set()
        return result

    monkeypatch.setattr(SendQueue, "enqueue", notified)

    async def send(data: str | bytes) -> None:
        ws.send(data)
        if ws.attempts[-1] == "B":
            entered.set()
            await release.wait()
            ws.close()
            raise OSError("older write closed transport")

    monkeypatch.setattr(
        "openai.lib._websocket._WebSocketConnect",
        AsyncMock(return_value=Mock(send=AsyncMock(side_effect=send), close=AsyncMock(side_effect=ws.close))),
    )
    async with AsyncOpenAI(api_key="synthetic-only") as client:
        manager = client.live.connect()
        for label in "ABC":
            manager.send({"type": "session.update", "event_id": label, "session": {}})
        async with manager as connection:
            owner = asyncio.create_task(connection.send_raw(b"D"))
            joiner = None
            try:
                await asyncio.wait_for(entered.wait(), timeout=3)
                joiner = asyncio.create_task(connection.send_raw(b"E"))
                await asyncio.wait_for(joined.wait(), timeout=3)
            finally:
                release.set()
                with pytest.raises(OSError, match="older write closed transport"):
                    await owner
                if joiner is not None:
                    with pytest.raises(ConnectionClosedOK):
                        await joiner
            assert ws.attempts == ["A", "B"]


@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
@pytest.mark.parametrize("failed_index", [1, 2, 3], ids=["fail-E", "fail-F", "fail-G"])
def test_each_joined_sender_observes_only_its_own_failed_frame(
    name: str, failed_index: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    ws = InitialWriteFails()
    entered, release, later_claim = (threading.Event() for _ in range(3))
    joined = [threading.Event() for _ in range(3)]
    delayed: set[threading.Thread] = set()
    enqueue = SendQueue.enqueue
    flush = SendQueue.flush_sync
    count = 0
    first_error = OSError("original B failed")
    joined_error = OSError("identical joined frame failed")

    def notified(self: SendQueue, data: str | bytes, **kwargs: Any) -> bool:
        nonlocal count
        result = enqueue(self, data, **kwargs)
        if data == b"identical":
            joined[count].set()
            count += 1
        return result

    def ordered(self: SendQueue, *args: Any, **kwargs: Any) -> None:
        if threading.current_thread() in delayed:
            assert later_claim.wait(5)
        flush(self, *args, **kwargs)

    monkeypatch.setattr(SendQueue, "enqueue", notified)
    monkeypatch.setattr(SendQueue, "flush_sync", ordered)

    def send(data: str | bytes) -> None:
        ws.send(data)
        if ws.attempts[-1] == "B":
            entered.set()
            assert release.wait(5)
            raise first_error
        if data == b"identical" and ws.attempts.count(b"identical") == failed_index:
            raise joined_error

    monkeypatch.setattr(
        "websockets.sync.client.connect", Mock(return_value=Mock(send=Mock(side_effect=send), close=ws.close))
    )
    with OpenAI(api_key="synthetic-only") as client:
        manager = resource(client, name).connect(**options(client, name))
        for label in "ABC":
            manager.send(event(label))
        with manager as connection, ThreadPoolExecutor(max_workers=4) as workers:

            def join(*, delay: bool) -> None:
                if delay:
                    delayed.add(threading.current_thread())
                connection.send_raw(b"identical")

            owner = workers.submit(connection.send_raw, b"D")
            waiters = []
            try:
                assert entered.wait(3)
                for index in range(3):
                    waiters.append(workers.submit(join, delay=index != 0))
                    assert joined[index].wait(3)
                release.set()
                with pytest.raises(OSError) as got:
                    owner.result(timeout=3)
                assert got.value is first_error
                # E deliberately owns the shared batch and retains its batch error.
                with pytest.raises(OSError) as got:
                    waiters[0].result(timeout=3)
                assert got.value is joined_error
            finally:
                release.set()
                later_claim.set()
            for index, waiter in enumerate(waiters[1:], start=2):
                if index == failed_index:
                    with pytest.raises(OSError) as got:
                        waiter.result(timeout=3)
                    assert got.value is joined_error
                else:
                    waiter.result(timeout=3)
            assert ws.attempts == ["A", "B", "C", b"D", b"identical", b"identical", b"identical"]


@pytest.mark.asyncio
@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
@pytest.mark.parametrize("failed_index", [1, 2, 3], ids=["fail-E", "fail-F", "fail-G"])
async def test_async_each_joined_sender_observes_only_its_own_failed_frame(
    name: str, failed_index: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    ws = InitialWriteFails()
    entered, release, later_claim = (asyncio.Event() for _ in range(3))
    joined = [asyncio.Event() for _ in range(3)]
    delayed: set[asyncio.Task[Any] | None] = set()
    enqueue = SendQueue.enqueue
    flush = SendQueue.flush_async
    count = 0
    first_error = OSError("original B failed")
    joined_error = OSError("identical joined frame failed")

    def notified(self: SendQueue, data: str | bytes, **kwargs: Any) -> bool:
        nonlocal count
        result = enqueue(self, data, **kwargs)
        if data == b"identical":
            joined[count].set()
            count += 1
        return result

    async def ordered(self: SendQueue, *args: Any, **kwargs: Any) -> None:
        if asyncio.current_task() in delayed:
            await later_claim.wait()
        await flush(self, *args, **kwargs)

    monkeypatch.setattr(SendQueue, "enqueue", notified)
    monkeypatch.setattr(SendQueue, "flush_async", ordered)

    async def send(data: str | bytes) -> None:
        ws.send(data)
        if ws.attempts[-1] == "B":
            entered.set()
            await release.wait()
            raise first_error
        if data == b"identical" and ws.attempts.count(b"identical") == failed_index:
            raise joined_error

    monkeypatch.setattr(
        "openai.lib._websocket._WebSocketConnect",
        AsyncMock(return_value=Mock(send=AsyncMock(side_effect=send), close=AsyncMock(side_effect=ws.close))),
    )
    async with AsyncOpenAI(api_key="synthetic-only") as client:
        manager = resource(client, name).connect(**options(client, name))
        for label in "ABC":
            manager.send(event(label))
        async with manager as connection:

            async def join(*, delay: bool) -> None:
                if delay:
                    delayed.add(asyncio.current_task())
                await connection.send_raw(b"identical")

            owner = asyncio.create_task(connection.send_raw(b"D"))
            waiters = []
            try:
                await asyncio.wait_for(entered.wait(), timeout=3)
                for index in range(3):
                    waiters.append(asyncio.create_task(join(delay=index != 0)))
                    await asyncio.wait_for(joined[index].wait(), timeout=3)
                release.set()
                with pytest.raises(OSError) as got:
                    await owner
                assert got.value is first_error
                with pytest.raises(OSError) as got:
                    await waiters[0]
                assert got.value is joined_error
            finally:
                release.set()
                later_claim.set()
            for index, waiter in enumerate(waiters[1:], start=2):
                if index == failed_index:
                    with pytest.raises(OSError) as got:
                        await waiter
                    assert got.value is joined_error
                else:
                    await waiter
            assert ws.attempts == ["A", "B", "C", b"D", b"identical", b"identical", b"identical"]


@pytest.mark.asyncio
async def test_cancelled_send_of_another_waiters_frame_reaches_that_waiter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ws = InitialWriteFails()
    entered_b, release_b, admitted_e, entered_e = (asyncio.Event() for _ in range(4))
    enqueue = SendQueue.enqueue

    def notified(self: SendQueue, data: str | bytes, **kwargs: Any) -> bool:
        result = enqueue(self, data, **kwargs)
        if data == b"E":
            admitted_e.set()
        return result

    monkeypatch.setattr(SendQueue, "enqueue", notified)

    async def send(data: str | bytes) -> None:
        ws.send(data)
        if ws.attempts[-1] == "B":
            entered_b.set()
            await release_b.wait()
        if data == b"E":
            entered_e.set()
            # The owner will be cancelled while writing another caller's frame.
            await asyncio.Event().wait()

    monkeypatch.setattr(
        "openai.lib._websocket._WebSocketConnect",
        AsyncMock(return_value=Mock(send=AsyncMock(side_effect=send), close=AsyncMock(side_effect=ws.close))),
    )
    async with AsyncOpenAI(api_key="synthetic-only") as client:
        manager = resource(client, "realtime").connect(**options(client, "realtime"))
        for label in "ABC":
            manager.send(event(label))
        async with manager as connection:
            owner = asyncio.create_task(connection.send_raw(b"D"))
            await asyncio.wait_for(entered_b.wait(), timeout=3)
            joined = asyncio.create_task(connection.send_raw(b"E"))
            await asyncio.wait_for(admitted_e.wait(), timeout=3)
            release_b.set()
            await asyncio.wait_for(entered_e.wait(), timeout=3)
            owner.cancel("interrupted while sending E")
            # asyncio can produce a distinct CancelledError for each task
            # boundary. Neither sender may report this attempted frame as sent.
            with pytest.raises(asyncio.CancelledError):
                await owner
            with pytest.raises(asyncio.CancelledError):
                await joined
            await connection.send_raw(b"F")
            assert ws.attempts == ["A", "B", "C", b"D", b"E", b"F"]
