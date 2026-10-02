from __future__ import annotations

import inspect
from typing import Any, Callable, Sequence, cast
from dataclasses import dataclass
from typing_extensions import override

from openai._models import construct_type_unchecked
from openai.lib.live import TranscriptGrouper, TranscriptSegment, AsyncTranscriptGrouper, TranscriptSegmentClosedEvent
from openai.types.live import ServerEvent


def event(data: dict[str, Any]) -> ServerEvent:
    # Exercise the same unchecked construction used by the generated transport.
    return cast(ServerEvent, construct_type_unchecked(value=data, type_=cast(Any, ServerEvent)))


def text(
    value: str = "Hello", *, start: int = 0, end: int = 200, item_id: str = "item_0", speaker: str = "assistant"
) -> ServerEvent:
    direction = "input" if speaker == "user" else "output"
    return event(
        {
            "type": f"session.{direction}_transcript.delta",
            "start_ms": start,
            "end_ms": end,
            "event_id": item_id,
            "delta": value,
        }
    )


@dataclass
class FakeTimer:
    due: float
    callback: Callable[[], None]
    cancelled: bool = False
    fired: bool = False

    def cancel(self) -> None:
        self.cancelled = True


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0
        self.timers: list[FakeTimer] = []

    def call_later(self, delay_ms: int, callback: Callable[[], None]) -> FakeTimer:
        timer = FakeTimer(self.now + delay_ms, callback)
        self.timers.append(timer)
        return timer

    @property
    def pending(self) -> list[FakeTimer]:
        return [timer for timer in self.timers if not timer.cancelled and not timer.fired]

    def next_before(self, target: float) -> FakeTimer | None:
        timers = sorted((timer for timer in self.pending if timer.due <= target), key=lambda timer: timer.due)
        return timers[0] if timers else None

    async def advance(self, delta: float, grouper: TranscriptGrouper | AsyncTranscriptGrouper) -> None:
        target = self.now + delta
        count = 0
        while (timer := self.next_before(target)) is not None:
            count += 1
            assert count < 10000, "non-progressing timer"
            self.now = timer.due
            timer.fired = True
            timer.callback()
            if isinstance(grouper, AsyncTranscriptGrouper):
                await grouper._dispatch()
        self.now = target


class ClockGrouper(TranscriptGrouper):
    def __init__(
        self, clock: FakeClock, additional_acknowledgments: Sequence[str] | None = None, **options: float
    ) -> None:
        self.clock = clock
        super().__init__(additional_acknowledgments=additional_acknowledgments, **options)

    @override
    def _now(self) -> float:
        return self.clock.now

    @override
    def _call_later(self, delay_ms: int, callback: Callable[[], None]) -> FakeTimer:
        return self.clock.call_later(delay_ms, callback)


class AsyncClockGrouper(AsyncTranscriptGrouper):
    def __init__(
        self, clock: FakeClock, additional_acknowledgments: Sequence[str] | None = None, **options: float
    ) -> None:
        self.clock = clock
        super().__init__(additional_acknowledgments=additional_acknowledgments, **options)

    @override
    def _now(self) -> float:
        return self.clock.now

    @override
    def _call_later(self, delay_ms: int, callback: Callable[[], None]) -> FakeTimer:
        return self.clock.call_later(delay_ms, callback)


async def push(grouper: TranscriptGrouper | AsyncTranscriptGrouper, value: ServerEvent) -> None:
    result = grouper.push(value)
    if inspect.isawaitable(result):
        await result


async def close(grouper: TranscriptGrouper | AsyncTranscriptGrouper) -> None:
    result = grouper.close()
    if inspect.isawaitable(result):
        await result


class Recording:
    def __init__(self, grouper: TranscriptGrouper | AsyncTranscriptGrouper, clock: FakeClock) -> None:
        self.clock = clock
        self.events: list[tuple[float, TranscriptSegment | TranscriptSegmentClosedEvent]] = []
        self.updated: list[TranscriptSegment] = []
        self.closed: list[TranscriptSegmentClosedEvent] = []
        self.latest: dict[str, TranscriptSegment] = {}
        self.finished: set[str] = set()
        grouper.on("segment.updated", self.on_updated)
        grouper.on("segment.closed", self.on_closed)

    def on_updated(self, segment: TranscriptSegment) -> None:
        assert segment.id not in self.finished
        previous = self.latest.get(segment.id)
        assert previous is None or segment.text.startswith(previous.text)
        self.latest[segment.id] = segment
        self.updated.append(segment)
        self.events.append((self.clock.now, segment))

    def on_closed(self, closed: TranscriptSegmentClosedEvent) -> None:
        segment = closed.segment
        assert segment.id not in self.finished
        assert segment == self.latest[segment.id]
        self.finished.add(segment.id)
        self.closed.append(closed)
        self.events.append((self.clock.now, closed))
