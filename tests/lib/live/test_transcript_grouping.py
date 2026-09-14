from __future__ import annotations

import itertools
from typing import Callable, Sequence, AsyncIterator

import pytest

from openai.types.live import ServerEvent

from .helpers import FakeClock, Recording, ClockGrouper, AsyncClockGrouper, push, text, close, event

_ITEM_IDS = itertools.count()


def fragment(speaker: str, value: str, start: int, end: int | None = None) -> ServerEvent:
    return text(
        value, speaker=speaker, start=start, end=start + 200 if end is None else end, item_id=f"item_{next(_ITEM_IDS)}"
    )


class Transcript:
    def __init__(
        self, async_mode: bool, additional_acknowledgments: Sequence[str] | None = None, **options: float
    ) -> None:
        self.clock = FakeClock()
        self.grouper = (AsyncClockGrouper if async_mode else ClockGrouper)(
            self.clock, additional_acknowledgments=additional_acknowledgments, **options
        )
        self.recording = Recording(self.grouper, self.clock)

    async def feed(self, *events: ServerEvent) -> None:
        for incoming in events:
            await push(self.grouper, incoming)

    async def advance(self, milliseconds: float) -> None:
        await self.clock.advance(milliseconds, self.grouper)

    async def finish(self, *expected: tuple[str, str]) -> None:
        await close(self.grouper)
        segments = [closed.segment for closed in self.recording.closed]
        assert [(segment.speaker, segment.text) for segment in segments] == list(expected)
        assert [segment.previous_id for segment in segments] == (
            [None] + [segment.id for segment in segments[:-1]] if segments else []
        )
        assert len(self.recording.finished) == len(self.recording.latest)
        assert not self.clock.pending


Factory = Callable[..., Transcript]


@pytest.fixture(params=[False, True], ids=["sync", "async"])
async def make_transcript(request: pytest.FixtureRequest) -> AsyncIterator[Factory]:
    transcripts: list[Transcript] = []

    def make(additional_acknowledgments: Sequence[str] | None = None, **options: float) -> Transcript:
        transcript = Transcript(request.param, additional_acknowledgments=additional_acknowledgments, **options)
        transcripts.append(transcript)
        return transcript

    yield make
    for transcript in transcripts:
        await close(transcript.grouper)


async def test_append_only_snapshots_and_predecessors(make_transcript: Factory) -> None:
    t = make_transcript()
    await t.feed(
        fragment("user", "Can you ", 0), fragment("user", "run ls?", 200), fragment("assistant", "Sure.", 1000)
    )
    await t.finish(("user", "Can you run ls?"), ("assistant", "Sure."))
    assert t.recording.updated[0].text == "Can you "
    assert t.recording.closed[0].segment.start_ms == 0
    assert t.recording.closed[0].segment.end_ms == 400


@pytest.mark.parametrize("parts", [("mhm",), ("Mm-hmm.",), ("Mm-", "hmm."), ("ye", "ah"), ("uh-", "huh!")])
async def test_overlapping_acknowledgment_when_user_continues(make_transcript: Factory, parts: tuple[str, ...]) -> None:
    t = make_transcript()
    await t.feed(fragment("user", "Tell me", 0))
    for index, part in enumerate(parts):
        await t.feed(fragment("assistant", part, 200 + index * 200))
    await t.feed(fragment("user", "more", 800), fragment("assistant", "Here is the answer.", 2000))
    await t.finish(("user", "Tell me more"), ("assistant", "Here is the answer."))


@pytest.mark.parametrize("parts", [("xy-", "z!"), ("mhm",), ("Mm-hmm.",)])
async def test_additional_acknowledgments_extend_defaults(make_transcript: Factory, parts: tuple[str, ...]) -> None:
    phrases = [" XY-Z! ", "..."]
    t = make_transcript(additional_acknowledgments=phrases)
    phrases.clear()
    await t.feed(fragment("user", "Tell me", 0))
    for index, part in enumerate(parts):
        await t.feed(fragment("assistant", part, 200 + index * 200))
    await t.feed(fragment("user", "more", 800))
    await t.finish(("user", "Tell me more"))


async def test_additional_acknowledgments_are_instance_local(make_transcript: Factory) -> None:
    make_transcript(additional_acknowledgments=["xyz"])
    t = make_transcript()
    await t.feed(fragment("user", "Tell me", 0), fragment("assistant", "xyz", 200), fragment("user", "more", 800))
    await t.finish(("user", "Tell me"), ("assistant", "xyz"), ("user", "more"))


async def test_additional_acknowledgments_respect_disabled_suppression(make_transcript: Factory) -> None:
    t = make_transcript(additional_acknowledgments=["xyz"], backchannel_max_duration_ms=0)
    await t.feed(fragment("user", "Tell me", 0), fragment("assistant", "xyz", 200), fragment("user", "more", 800))
    await t.finish(("user", "Tell me"), ("assistant", "xyz"), ("user", "more"))


async def test_discarded_backchannel_does_not_prefix_answer(make_transcript: Factory) -> None:
    t = make_transcript()
    await t.feed(
        fragment("user", "Tell me", 0),
        fragment("assistant", "mhm", 200),
        fragment("user", "more", 400),
        fragment("assistant", "Here is the answer.", 600),
    )
    await t.finish(("user", "Tell me more"), ("assistant", "Here is the answer."))


async def test_short_substantive_answer_and_trailing_user_text(make_transcript: Factory) -> None:
    t = make_transcript()
    await t.feed(
        fragment("user", "Stop counting", 0), fragment("assistant", "thirteen", 200), fragment("user", ".", 400)
    )
    await t.finish(("user", "Stop counting."), ("assistant", "thirteen"))


async def test_standalone_acknowledgment_after_speaker_gap(make_transcript: Factory) -> None:
    t = make_transcript()
    await t.feed(fragment("user", "Are you there?", 0), fragment("assistant", "yes", 800))
    await t.advance(5000)
    await t.finish(("user", "Are you there?"), ("assistant", "yes"))
    assert [closed.reason for closed in t.recording.closed] == ["speaker_change", "inactivity"]


@pytest.mark.parametrize("input_first", [True, False])
async def test_same_interval_barge_in(make_transcript: Factory, input_first: bool) -> None:
    t = make_transcript()
    await t.feed(fragment("assistant", "The answer is", 0))
    await t.advance(50)
    pair = [fragment("user", "Wait", 200), fragment("assistant", " forty-two.", 200)]
    await t.feed(*(pair if input_first else pair[::-1]), fragment("user", ", stop.", 400))
    await t.finish(("assistant", "The answer is forty-two."), ("user", "Wait, stop."))


@pytest.mark.parametrize("input_first", [True, False])
async def test_first_interval_prefers_user(make_transcript: Factory, input_first: bool) -> None:
    t = make_transcript()
    pair = [fragment("user", "hello", 0), fragment("assistant", "hello there", 0)]
    await t.feed(*(pair if input_first else pair[::-1]))
    await t.finish(("user", "hello"), ("assistant", "hello there"))


async def test_assistant_inactivity_without_another_event(make_transcript: Factory) -> None:
    t = make_transcript()
    await t.feed(fragment("assistant", "Answer", 0))
    await t.advance(1999)
    assert not t.recording.closed
    await t.advance(1)
    assert t.recording.closed[0].reason == "inactivity"
    assert t.recording.closed[0].segment.end_ms == 200
    await t.finish(("assistant", "Answer"))


async def test_user_inactivity_does_not_close(make_transcript: Factory) -> None:
    t = make_transcript()
    await t.feed(fragment("user", "Hello", 0))
    await t.advance(60000)
    assert not t.recording.closed
    assert not t.clock.pending
    await t.feed(fragment("user", " again.", 60000))
    await t.finish(("user", "Hello again."))


async def test_overlapping_intervals_restart_local_inactivity(make_transcript: Factory) -> None:
    t = make_transcript(assistant_silence_ms=200)
    await t.feed(fragment("assistant", "First", 0, 500))
    await t.advance(100)
    await t.feed(fragment("assistant", " overlapping.", 100, 120))
    await t.advance(199)
    assert not t.recording.closed
    await t.advance(1)
    assert t.recording.closed[0].segment.end_ms == 500
    await t.feed(fragment("assistant", "Later.", 150, 200))
    await t.finish(("assistant", "First overlapping."), ("assistant", "Later."))


async def test_timestamp_reset_clears_old_source_clock(make_transcript: Factory) -> None:
    t = make_transcript(assistant_silence_ms=200)
    await t.feed(fragment("assistant", "Old timeline.", 1000, 1500))
    await t.advance(100)
    await t.feed(fragment("assistant", "New timeline.", 0, 100))
    assert t.recording.closed[0].reason == "timestamp_reset"
    await t.advance(199)
    assert len(t.recording.closed) == 1
    await t.advance(1)
    assert t.recording.closed[1].reason == "inactivity"
    assert t.recording.closed[1].segment.end_ms == 100
    await t.finish(("assistant", "Old timeline."), ("assistant", "New timeline."))


async def test_source_time_gaps_when_delivery_is_batched(make_transcript: Factory) -> None:
    t = make_transcript()
    await t.feed(
        fragment("user", "One?", 0),
        fragment("assistant", "First answer.", 1000),
        fragment("assistant", "Second answer.", 4000),
    )
    await t.finish(("user", "One?"), ("assistant", "First answer."), ("assistant", "Second answer."))
    assert t.recording.closed[1].reason == "inactivity"


async def test_settle_window_only_delays_speaker_changes(make_transcript: Factory) -> None:
    t = make_transcript()
    await t.feed(fragment("assistant", "First", 0))
    await t.advance(49)
    assert not t.recording.updated
    await t.advance(1)
    assert len(t.recording.updated) == 1
    await t.feed(fragment("assistant", " next", 200))
    assert [segment.text for segment in t.recording.updated] == ["First", "First next"]
    await t.finish(("assistant", "First next"))


async def test_unrelated_events_do_not_change_the_projection(make_transcript: Factory) -> None:
    t = make_transcript()
    await t.feed(fragment("assistant", "Say [end] literally.", 0))
    await t.advance(50)
    timer = t.clock.pending[0]
    for kind in [
        "turn.created",
        "turn.delta",
        "turn.done",
        "response.completed",
        "delegation.created",
        "output_audio.delta",
    ]:
        await t.feed(event({"type": kind}))
    assert t.clock.pending == [timer]
    assert not t.recording.closed
    assert len(t.recording.updated) == 1
    await t.finish(("assistant", "Say [end] literally."))


async def test_duplicates_and_empty_text_do_not_reset_deadlines(make_transcript: Factory) -> None:
    t = make_transcript()
    incoming = fragment("assistant", "Once.", 0)
    await t.feed(incoming)
    await t.advance(1900.5)
    timer = t.clock.pending[0]
    await t.feed(incoming, fragment("assistant", "", 100000))
    assert t.clock.pending == [timer]
    await t.advance(99.5)
    assert len(t.recording.closed) == 1
    assert t.recording.closed[0].reason == "inactivity"
    await t.finish(("assistant", "Once."))


async def test_empty_transcript_item_still_counts_as_seen(make_transcript: Factory) -> None:
    t = make_transcript()
    await t.feed(
        text("", speaker="user", item_id="same"),
        text("Ignored", speaker="user", item_id="same"),
        fragment("user", "Kept", 400),
    )
    await t.finish(("user", "Kept"))


async def test_late_text_never_reopens_closed_segment(make_transcript: Factory) -> None:
    t = make_transcript()
    await t.feed(fragment("assistant", "First", 0))
    await t.advance(3000)
    await t.feed(fragment("assistant", " late.", 200))
    await t.finish(("assistant", "First"), ("assistant", " late."))
    assert t.recording.closed[0].segment.id != t.recording.closed[1].segment.id


async def test_public_session_closed_flushes_once(make_transcript: Factory) -> None:
    t = make_transcript()
    await t.feed(
        fragment("user", "Question", 0), fragment("assistant", "Answer", 200), event({"type": "session.closed"})
    )
    await t.finish(("user", "Question"), ("assistant", "Answer"))
    assert all(closed.reason == "session_closed" for closed in t.recording.closed)


async def test_zero_disables_suppression(make_transcript: Factory) -> None:
    t = make_transcript(backchannel_max_duration_ms=0)
    await t.feed(fragment("user", "Tell me ", 0), fragment("assistant", "mhm", 200), fragment("user", "more", 400))
    await t.finish(("user", "Tell me more"), ("assistant", "mhm"))


async def test_fractional_timeout_rounds_up(make_transcript: Factory) -> None:
    t = make_transcript(assistant_silence_ms=200.5)
    await t.feed(fragment("assistant", "Fractional.", 0))
    await t.advance(200.5)
    assert not t.recording.closed
    await t.advance(0.5)
    assert len(t.recording.closed) == 1
    await t.finish(("assistant", "Fractional."))


async def test_all_zero_options_terminate_timers(make_transcript: Factory) -> None:
    t = make_transcript(
        min_turn_separation_ms=0, assistant_silence_ms=0, backchannel_max_duration_ms=0, backchannel_isolation_ms=0
    )
    await t.feed(fragment("user", "Hello", 0), fragment("assistant", "yes", 200))
    await t.advance(50)
    await t.finish(("user", "Hello"), ("assistant", "yes"))
    assert [closed.reason for closed in t.recording.closed] == ["speaker_change", "inactivity"]


@pytest.mark.parametrize(
    "ack,suppressed",
    [
        ("\ufeffYEAH\ufeff", True),
        ("\u0085yeah\u0085", False),
        ("\u001cyeah\u001c", False),
        ("\u00a0uh\u2003huh!\u00a0", True),
        ("okay-ish", False),
        ("hm", True),
        ("İ", False),
    ],
)
async def test_acknowledgment_normalization(make_transcript: Factory, ack: str, suppressed: bool) -> None:
    t = make_transcript()
    await t.feed(fragment("user", "Tell me", 0), fragment("assistant", ack, 200), fragment("user", "more", 800))
    await t.advance(5000)
    if suppressed:
        await t.finish(("user", "Tell me more"))
    else:
        await t.finish(("user", "Tell me"), ("assistant", ack), ("user", "more"))


@pytest.mark.parametrize(
    "before,after,joined",
    [("你好", "世界", "你好 世界"), ("Ⅻ", "½", "Ⅻ ½"), ("x😀", "y", "x😀y"), ("a", "\u0301b", "a\u0301b")],
)
async def test_unicode_separator(make_transcript: Factory, before: str, after: str, joined: str) -> None:
    t = make_transcript()
    await t.feed(fragment("user", before, 0), fragment("assistant", "mhm", 200), fragment("user", after, 800))
    await t.finish(("user", joined))


@pytest.mark.parametrize("gap", [499, 500, 501])
async def test_turn_separation_boundary(make_transcript: Factory, gap: int) -> None:
    t = make_transcript()
    await t.feed(fragment("user", "Question", 0), fragment("assistant", "Answer", 200 + gap))
    await t.advance(3000)
    await t.finish(("user", "Question"), ("assistant", "Answer"))


@pytest.mark.parametrize("duration", [999, 1000, 1001])
async def test_backchannel_duration_boundary(make_transcript: Factory, duration: int) -> None:
    t = make_transcript()
    await t.feed(
        fragment("user", "Tell me", 0, 100),
        fragment("assistant", "mhm", 100, 100 + duration),
        fragment("user", "more", 1200, 1400),
    )
    await t.advance(5000)
    if duration < 1000:
        await t.finish(("user", "Tell me more"))
    else:
        await t.finish(("user", "Tell me"), ("assistant", "mhm"), ("user", "more"))


async def test_recent_assistant_continuation(make_transcript: Factory) -> None:
    t = make_transcript()
    await t.feed(fragment("assistant", "Hello", 0))
    await t.advance(50)
    await t.feed(fragment("user", "Wait", 200), fragment("assistant", "yeah", 200))
    await t.advance(3000)
    await t.finish(("assistant", "Helloyeah"), ("user", "Wait"))


async def test_safe_integer_timestamps_are_preserved(make_transcript: Factory) -> None:
    t = make_transcript()
    maximum = 9_007_199_254_740_991
    await t.feed(fragment("assistant", "Far timeline.", maximum - 200, maximum))
    await t.finish(("assistant", "Far timeline."))
    assert t.recording.closed[0].segment.end_ms == maximum
