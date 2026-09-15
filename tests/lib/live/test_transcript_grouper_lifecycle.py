from __future__ import annotations

import asyncio
import threading
from typing import Any
from concurrent.futures import ThreadPoolExecutor

import pytest

from openai import OpenAIError
from openai.lib.live import TranscriptGrouper, TranscriptSegment, AsyncTranscriptGrouper, TranscriptSegmentClosedEvent

from .helpers import FakeClock, Recording, ClockGrouper, AsyncClockGrouper, push, text, close


def test_subscriptions_are_registration_scoped() -> None:
    grouper = ClockGrouper(FakeClock())
    seen: list[str] = []

    def listener(segment: TranscriptSegment) -> None:
        seen.append(segment.text)

    assert grouper.on("segment.updated", listener) is grouper
    assert grouper.once("segment.updated", listener) is grouper
    grouper.push(text("One", speaker="user"))
    grouper.push(text(" two", speaker="user", start=200, end=400, item_id="two"))
    assert seen == ["One", "One", "One two"]
    assert grouper.off("segment.updated", listener) is grouper
    grouper.push(text(" three", speaker="user", start=400, end=600, item_id="three"))
    grouper.close()
    assert seen == ["One", "One", "One two"]


def test_decorators_and_mutating_subscriptions_during_dispatch() -> None:
    grouper = ClockGrouper(FakeClock())
    seen: list[str] = []

    def second(_: TranscriptSegment) -> None:
        seen.append("second")

    @grouper.once("segment.updated")
    def first(_: TranscriptSegment) -> None:
        seen.append("first")
        grouper.off("segment.updated", second)
        grouper.on("segment.updated", lambda _: seen.append("late"))

    grouper.on("segment.updated", second)

    @grouper.on("segment.closed")
    def on_closed(_: TranscriptSegmentClosedEvent) -> None:
        seen.append("closed")

    assert callable(first) and callable(on_closed)
    grouper.push(text("One", speaker="user"))
    grouper.push(text(" two", speaker="user", start=200, end=400, item_id="two"))
    grouper.close()
    assert seen == ["first", "second", "late", "closed"]


@pytest.mark.parametrize("async_mode", [False, True])
async def test_stale_timer_after_reschedule_and_close(async_mode: bool) -> None:
    clock = FakeClock()
    grouper = (AsyncClockGrouper if async_mode else ClockGrouper)(clock)
    recording = Recording(grouper, clock)
    await push(grouper, text("One"))
    old_timer = clock.pending[0]
    await push(grouper, text(" two", start=200, end=400, item_id="two"))
    before = list(recording.events)
    old_timer.callback()  # A cancelled callback may already have been dequeued.
    assert recording.events == before
    last_timer = clock.pending[0]
    await close(grouper)
    after = list(recording.events)
    last_timer.callback()
    assert recording.events == after
    assert len(recording.closed) == 1
    assert not clock.pending


async def test_sync_reentrant_close_preserves_fifo() -> None:
    clock = FakeClock()
    grouper = ClockGrouper(clock)
    order: list[str] = []

    def first(_: TranscriptSegment) -> None:
        order.append("first")
        grouper.close()
        with pytest.raises(OpenAIError):
            grouper.push(text("after"))

    grouper.on("segment.updated", first)
    grouper.on("segment.updated", lambda _: order.append("second"))
    grouper.on("segment.closed", lambda _: order.append("closed"))
    grouper.push(text())
    await clock.advance(50, grouper)
    assert order == ["first", "second", "closed"]
    assert not clock.pending


async def test_async_reentrant_close_preserves_fifo() -> None:
    clock = FakeClock()
    grouper = AsyncClockGrouper(clock)
    order: list[str] = []

    @grouper.on("segment.updated")
    async def first(_: TranscriptSegment) -> None:
        order.append("first")
        await grouper.close()

    assert callable(first)
    grouper.on("segment.updated", lambda _: order.append("second"))
    grouper.on("segment.closed", lambda _: order.append("closed"))
    await grouper.push(text())
    await asyncio.wait_for(clock.advance(50, grouper), 2)
    await grouper.close()
    assert order == ["first", "second", "closed"]
    assert not clock.pending
    assert grouper._dispatch_run is None or (
        grouper._dispatch_run.task is not None and grouper._dispatch_run.task.done()
    )


async def test_async_callbacks_and_concurrent_close_are_serialized() -> None:
    grouper = AsyncClockGrouper(FakeClock())
    entered = asyncio.Event()
    release = asyncio.Event()
    order: list[str] = []

    async def on_updated(segment: TranscriptSegment) -> None:
        order.append(f"start:{segment.text}")
        entered.set()
        await release.wait()
        order.append(f"end:{segment.text}")

    grouper.on("segment.updated", on_updated)
    grouper.on("segment.closed", lambda _: order.append("closed"))
    await grouper.push(text("One", speaker="user"))
    sender = asyncio.create_task(grouper.push(text(" two", start=200, end=400, item_id="two", speaker="user")))
    await asyncio.wait_for(entered.wait(), 2)
    closer = asyncio.create_task(grouper.close())
    await asyncio.sleep(0)
    assert order == ["start:One"]
    assert not closer.done()
    release.set()
    await asyncio.wait_for(asyncio.gather(sender, closer), 2)
    assert order == ["start:One", "end:One", "start:One two", "end:One two", "closed"]


async def test_cancelled_waiter_does_not_cancel_active_dispatch() -> None:
    grouper = AsyncClockGrouper(FakeClock())
    entered, release = asyncio.Event(), asyncio.Event()
    closed: list[TranscriptSegmentClosedEvent] = []

    async def listener(_: TranscriptSegment) -> None:
        entered.set()
        await release.wait()

    grouper.on("segment.updated", listener)
    grouper.on("segment.closed", closed.append)
    await grouper.push(text("One", speaker="user"))
    sender = asyncio.create_task(grouper.push(text(" two", start=200, end=400, item_id="two", speaker="user")))
    await asyncio.wait_for(entered.wait(), 2)
    waiter = asyncio.create_task(grouper.close())
    await asyncio.sleep(0)
    waiter.cancel()
    with pytest.raises(asyncio.CancelledError):
        await waiter
    release.set()
    await asyncio.wait_for(sender, 2)
    await grouper.close()
    assert len(closed) == 1


@pytest.mark.parametrize("operation", ["push", "close"])
async def test_cancelled_dispatch_caller_preserves_remaining_handlers(operation: str) -> None:
    clock = FakeClock()
    grouper = AsyncClockGrouper(clock)
    await grouper.push(text("One", speaker="user"))
    await clock.advance(50, grouper)
    entered, release = asyncio.Event(), asyncio.Event()
    delivered: list[str] = []

    async def first(_: TranscriptSegment | TranscriptSegmentClosedEvent) -> None:
        entered.set()
        await release.wait()
        delivered.append("first")

    if operation == "push":
        grouper.on("segment.updated", first)
        grouper.on("segment.updated", lambda _: delivered.append("second"))
        caller = asyncio.create_task(grouper.push(text(" two", start=200, end=400, item_id="two", speaker="user")))
    else:
        grouper.on("segment.closed", first)
        grouper.on("segment.closed", lambda _: delivered.append("second"))
        caller = asyncio.create_task(grouper.close())
    try:
        await asyncio.wait_for(entered.wait(), 2)
        caller.cancel()
        with pytest.raises(asyncio.CancelledError):
            await caller
    finally:
        release.set()
        await asyncio.wait_for(grouper.close(), 2)
    assert delivered == ["first", "second"]


def test_sync_callbacks_do_not_hold_state_lock_or_run_concurrently() -> None:
    grouper = ClockGrouper(FakeClock())
    entered, release = threading.Event(), threading.Event()
    order: list[str] = []

    def listener(segment: TranscriptSegment) -> None:
        order.append(f"start:{segment.text}")
        entered.set()
        assert release.wait(2)
        order.append(f"end:{segment.text}")

    grouper.on("segment.updated", listener)
    grouper.on("segment.closed", lambda _: order.append("closed"))
    grouper.push(text("One", speaker="user"))
    with ThreadPoolExecutor(max_workers=2) as pool:
        sender = pool.submit(grouper.push, text(" two", start=200, end=400, item_id="two", speaker="user"))
        try:
            assert entered.wait(2)
            pool.submit(grouper.close).result(timeout=2)
            assert order == ["start:One"]
        finally:
            release.set()
        sender.result(timeout=2)
    assert order == ["start:One", "end:One", "start:One two", "end:One two", "closed"]


def test_concurrent_duplicate_delivery_and_close() -> None:
    grouper = TranscriptGrouper()
    snapshots: list[TranscriptSegment] = []
    finished: list[TranscriptSegmentClosedEvent] = []
    grouper.on("segment.updated", snapshots.append)
    grouper.on("segment.closed", finished.append)
    incoming = text("Once")

    def close_one(_: int) -> None:
        grouper.close()

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(grouper.push, [incoming] * 100))
        list(pool.map(close_one, range(20)))
    assert len(snapshots) == len(finished) == 1
    assert finished[0].segment.text == "Once"


def test_real_sync_timer_finishes_without_new_events() -> None:
    finished = threading.Event()
    snapshots: list[TranscriptSegmentClosedEvent] = []

    def listener(value: TranscriptSegmentClosedEvent) -> None:
        snapshots.append(value)
        finished.set()

    with TranscriptGrouper(assistant_silence_ms=75) as grouper:
        grouper.on("segment.closed", listener)
        grouper.push(text())
        assert finished.wait(2)
    assert snapshots[0].reason == "inactivity"
    assert snapshots[0].segment.end_ms == 200
    assert grouper._timer is None


async def test_real_async_timer_stays_on_event_loop() -> None:
    finished = asyncio.Event()
    loop = asyncio.get_running_loop()
    thread_id = threading.get_ident()

    async def listener(value: TranscriptSegmentClosedEvent) -> None:
        assert asyncio.get_running_loop() is loop
        assert threading.get_ident() == thread_id
        assert value.reason == "inactivity"
        await asyncio.sleep(0)
        finished.set()

    async with AsyncTranscriptGrouper(assistant_silence_ms=75) as grouper:
        grouper.on("segment.closed", listener)
        await grouper.push(text())
        await asyncio.wait_for(finished.wait(), 2)
    assert grouper._timer is None
    assert grouper._dispatch_run is None or (
        grouper._dispatch_run.task is not None and grouper._dispatch_run.task.done()
    )


@pytest.mark.parametrize("async_mode", [False, True])
async def test_callback_errors_propagate_and_allow_cleanup(async_mode: bool) -> None:
    clock = FakeClock()
    grouper = (AsyncClockGrouper if async_mode else ClockGrouper)(clock)
    finished: list[TranscriptSegmentClosedEvent] = []

    def failing(_: TranscriptSegment) -> None:
        raise ValueError("synthetic callback failure")

    grouper.once("segment.updated", failing)
    grouper.on("segment.closed", finished.append)
    await push(grouper, text("One", speaker="user"))
    with pytest.raises(ValueError, match="synthetic"):
        await push(grouper, text(" two", start=200, end=400, item_id="two", speaker="user"))
    await close(grouper)
    assert len(finished) == 1
    assert finished[0].segment.text == "One two"
    assert not clock.pending


async def test_async_timer_handler_errors_are_reported() -> None:
    loop = asyncio.get_running_loop()
    previous = loop.get_exception_handler()
    errors: list[dict[str, Any]] = []
    reported = asyncio.Event()

    def exception_handler(_: asyncio.AbstractEventLoop, context: dict[str, Any]) -> None:
        errors.append(context)
        reported.set()

    async def failing(_: TranscriptSegment) -> None:
        raise ValueError("synthetic timer callback failure")

    loop.set_exception_handler(exception_handler)
    try:
        async with AsyncTranscriptGrouper() as grouper:
            grouper.once("segment.updated", failing)
            await grouper.push(text())
            await asyncio.wait_for(reported.wait(), 2)
        assert len(errors) == 1
        assert isinstance(errors[0]["exception"], ValueError)
    finally:
        loop.set_exception_handler(previous)


async def test_context_managers_close_on_body_failure() -> None:
    sync = ClockGrouper(FakeClock())
    with pytest.raises(ValueError):
        with sync:
            sync.push(text())
            raise ValueError("body")
    assert sync._state.closed
    assert not sync.clock.pending
    asynchronous = AsyncClockGrouper(FakeClock())
    with pytest.raises(ValueError):
        async with asynchronous:
            await asynchronous.push(text())
            raise ValueError("body")
    assert asynchronous._state.closed
    assert not asynchronous.clock.pending
