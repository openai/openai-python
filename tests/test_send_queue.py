from __future__ import annotations

import asyncio
import threading
from typing import Callable

import pytest

from openai._exceptions import WebSocketQueueFullError
from openai._send_queue import SendQueue


class TestSendQueue:
    def test_enqueue_and_drain(self) -> None:
        q = SendQueue()
        q.enqueue('{"type": "session.update"}')
        q.enqueue('{"type": "response.create"}')
        assert len(q) == 2

        items = q.drain()
        assert items == ['{"type": "session.update"}', '{"type": "response.create"}']
        assert len(q) == 0

    def test_enqueue_respects_byte_limit(self) -> None:
        q = SendQueue(max_bytes=10)
        q.enqueue("12345")  # 5 bytes, fits
        with pytest.raises(WebSocketQueueFullError):
            q.enqueue("123456")  # 6 bytes, would exceed 10
        assert len(q) == 1

    def test_drain_empties_queue(self) -> None:
        q = SendQueue()
        q.enqueue("hello")
        q.drain()
        assert len(q) == 0
        assert not q

    def test_bool(self) -> None:
        q = SendQueue()
        assert not q
        q.enqueue("x")
        assert q

    def test_flush_sync(self) -> None:
        q = SendQueue()
        q.enqueue("a")
        q.enqueue("b")
        q.enqueue("c")

        sent: list[str] = []
        q.flush_sync(sent.append)
        assert sent == ["a", "b", "c"]
        assert len(q) == 0

    def test_flush_sync_requeues_on_failure(self) -> None:
        q = SendQueue()
        q.enqueue("a")
        q.enqueue("b")
        q.enqueue("c")

        sent: list[str] = []

        def failing_send(data: str) -> None:
            if data == "b":
                raise RuntimeError("send failed")
            sent.append(data)

        with pytest.raises(RuntimeError, match="send failed"):
            q.flush_sync(failing_send)

        assert sent == ["a"]
        # b and c should be re-queued
        remaining = q.drain()
        assert remaining == ["b", "c"]

    @pytest.mark.asyncio
    async def test_flush_async(self) -> None:
        q = SendQueue()
        q.enqueue("a")
        q.enqueue("b")

        sent: list[str] = []

        async def async_send(data: str) -> None:
            sent.append(data)

        await q.flush_async(async_send)
        assert sent == ["a", "b"]
        assert len(q) == 0

    @pytest.mark.asyncio
    async def test_flush_async_requeues_on_failure(self) -> None:
        q = SendQueue()
        q.enqueue("a")
        q.enqueue("b")
        q.enqueue("c")

        sent: list[str] = []

        async def failing_send(data: str) -> None:
            if data == "b":
                raise RuntimeError("send failed")
            sent.append(data)

        with pytest.raises(RuntimeError, match="send failed"):
            await q.flush_async(failing_send)

        assert sent == ["a"]
        remaining = q.drain()
        assert remaining == ["b", "c"]

    def test_flush_sync_preserves_new_items_on_failure(self) -> None:
        """If items are enqueued after flush starts and flush fails,
        the re-queued items should come before the new items."""
        q = SendQueue()
        q.enqueue("a")
        q.enqueue("b")

        def failing_send(data: str) -> None:
            if data == "b":
                # Simulate another thread enqueuing during flush
                q.enqueue("new")
                raise RuntimeError("fail")

        with pytest.raises(RuntimeError):
            q.flush_sync(failing_send)

        # "b" (failed) should come before "new" (added during flush)
        remaining = q.drain()
        assert remaining == ["b", "new"]


async def flush_in_background(q: SendQueue, send: Callable[[str], None], asynchronous: bool) -> None:
    if asynchronous:

        async def async_send(data: str) -> None:
            await asyncio.to_thread(send, data)

        await q.flush_async(async_send)
    else:
        await asyncio.to_thread(q.flush_sync, send)


async def wait_for_event(event: threading.Event) -> None:
    assert await asyncio.to_thread(event.wait, 5), "send did not start"


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.asyncio
async def test_repeated_failed_flushes_remain_bounded(asynchronous: bool) -> None:
    q = SendQueue(max_bytes=6)
    q.enqueue("éé")  # Four UTF-8 bytes.
    q.enqueue("a")

    for attempt in range(3):
        entered, release = threading.Event(), threading.Event()

        def send(data: str, entered: threading.Event = entered, release: threading.Event = release) -> None:
            assert data == "éé"
            entered.set()
            assert release.wait(5)
            raise RuntimeError("fake send failure")

        task = asyncio.create_task(flush_in_background(q, send, asynchronous))
        try:
            await wait_for_event(entered)
            if attempt == 0:
                q.enqueue("b")
            with pytest.raises(WebSocketQueueFullError):
                q.enqueue("c")
        finally:
            release.set()
            with pytest.raises(RuntimeError, match="fake send failure"):
                await task
        assert q._bytes == 6

    sent: list[str] = []
    await flush_in_background(q, sent.append, asynchronous)
    assert sent == ["éé", "a", "b"]
    assert q._bytes == 0
    q.enqueue("123456")


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("fail", [False, True], ids=["success", "failure"])
@pytest.mark.asyncio
async def test_partial_flush_releases_only_successful_bytes(asynchronous: bool, fail: bool) -> None:
    q = SendQueue(max_bytes=4)
    q.enqueue("é")
    q.enqueue("bb")
    entered, release = threading.Event(), threading.Event()
    sent: list[str] = []

    def send(data: str) -> None:
        if data == "bb":
            entered.set()
            assert release.wait(5)
            if fail:
                raise RuntimeError("fake send failure")
        sent.append(data)

    task = asyncio.create_task(flush_in_background(q, send, asynchronous))
    try:
        await wait_for_event(entered)
        assert q._bytes == 2
        q.enqueue("cc")
        with pytest.raises(WebSocketQueueFullError):
            q.enqueue("d")
    finally:
        release.set()
        if fail:
            with pytest.raises(RuntimeError, match="fake send failure"):
                await task
        else:
            await task
    assert sent == (["é"] if fail else ["é", "bb"])
    assert q.drain() == (["bb", "cc"] if fail else ["cc"])
    assert q._bytes == 0


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.asyncio
async def test_drain_during_flush_keeps_pending_bytes_charged(asynchronous: bool) -> None:
    q = SendQueue(max_bytes=4)
    q.enqueue("aaa")
    entered, release = threading.Event(), threading.Event()

    def send(_data: str) -> None:
        entered.set()
        assert release.wait(5)
        raise RuntimeError("fake send failure")

    task = asyncio.create_task(flush_in_background(q, send, asynchronous))
    try:
        await wait_for_event(entered)
        q.enqueue("b")
        assert q.drain() == ["b"]
        assert q._bytes == 3
        q.enqueue("c")
        with pytest.raises(WebSocketQueueFullError):
            q.enqueue("d")
    finally:
        release.set()
        with pytest.raises(RuntimeError, match="fake send failure"):
            await task
    assert q.drain() == ["aaa", "c"]
    assert q._bytes == 0


@pytest.mark.parametrize("first_async", [False, True], ids=["sync-first", "async-first"])
@pytest.mark.parametrize("second_async", [False, True], ids=["sync-second", "async-second"])
@pytest.mark.parametrize("fail", [False, True], ids=["success", "failure"])
@pytest.mark.asyncio
async def test_overlapping_flushes_preserve_order(first_async: bool, second_async: bool, fail: bool) -> None:
    q = SendQueue(max_bytes=3)
    q.enqueue("a")
    q.enqueue("b")
    entered, release, second_sent = threading.Event(), threading.Event(), threading.Event()
    sent: list[str] = []

    def first_send(data: str) -> None:
        if data == "a":
            entered.set()
            assert release.wait(5)
            if fail:
                raise RuntimeError("fake send failure")
        sent.append(data)

    def second_send(data: str) -> None:
        second_sent.set()
        sent.append(data)

    first = asyncio.create_task(flush_in_background(q, first_send, first_async))
    await wait_for_event(entered)
    q.enqueue("c")
    second = asyncio.create_task(flush_in_background(q, second_send, second_async))
    try:
        # Neither kind of waiter may overtake the active flush.
        assert not await asyncio.to_thread(second_sent.wait, 0.05)
    finally:
        release.set()
        if fail:
            with pytest.raises(RuntimeError, match="fake send failure"):
                await first
        else:
            await first
        await asyncio.wait_for(second, 5)
    assert sent == ["a", "b", "c"]
    assert q._bytes == 0


@pytest.mark.asyncio
async def test_cancelled_flush_restores_unsent_messages() -> None:
    q = SendQueue(max_bytes=3)
    q.enqueue("a")
    q.enqueue("b")
    entered = asyncio.Event()

    async def send(data: str) -> None:
        if data == "b":
            entered.set()
            await asyncio.Event().wait()

    task = asyncio.create_task(q.flush_async(send))
    await asyncio.wait_for(entered.wait(), 5)
    q.enqueue("cc")
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    with pytest.raises(WebSocketQueueFullError):
        q.enqueue("d")
    sent: list[str] = []
    q.flush_sync(sent.append)
    assert sent == ["b", "cc"]
    assert q._bytes == 0


@pytest.mark.asyncio
async def test_cancelled_flush_waiter_does_not_strand_ownership() -> None:
    q = SendQueue(max_bytes=2)
    q.enqueue("a")
    entered, release = asyncio.Event(), asyncio.Event()
    sent: list[str] = []

    async def first_send(data: str) -> None:
        entered.set()
        await release.wait()
        sent.append(data)

    async def second_send(data: str) -> None:
        sent.append(data)

    first = asyncio.create_task(q.flush_async(first_send))
    await asyncio.wait_for(entered.wait(), 5)
    q.enqueue("b")
    second = asyncio.create_task(q.flush_async(second_send))
    await asyncio.sleep(0)
    second.cancel()
    with pytest.raises(asyncio.CancelledError):
        await second
    release.set()
    await first
    await asyncio.wait_for(q.flush_async(second_send), 5)
    assert sent == ["a", "b"]
    assert q._bytes == 0


def test_interrupted_sync_flush_restores_unsent_messages() -> None:
    q = SendQueue(max_bytes=2)
    q.enqueue("a")
    q.enqueue("b")

    def send(data: str) -> None:
        if data == "b":
            raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        q.flush_sync(send)
    q.enqueue("c")
    with pytest.raises(WebSocketQueueFullError):
        q.enqueue("d")
    sent: list[str] = []
    q.flush_sync(sent.append)
    assert sent == ["b", "c"]
    assert q._bytes == 0
