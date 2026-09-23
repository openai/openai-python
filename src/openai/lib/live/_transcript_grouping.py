from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing_extensions import Literal

from ._types import (
    GroupingUpdate,
    TranscriptSegment,
    TranscriptFragment,
    TranscriptGrouperOptions,
    TranscriptSegmentClosedEvent,
    TranscriptSegmentCloseReason,
)

# Match ECMAScript \s, including BOM but excluding Python-only whitespace.
_WHITESPACE = "\u0009\u000a\u000b\u000c\u000d\u0020\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000\ufeff"
_ACKNOWLEDGMENTS = (
    "aha",
    "alright",
    "gotcha",
    "hm",
    "hmm",
    "mhm",
    "mm",
    "mm hmm",
    "okay",
    "ok",
    "right",
    "sure",
    "uh huh",
    "yeah",
    "yep",
    "yes",
)


def _normalize_acknowledgment(text: str) -> str:
    text = text.lower().replace("-", " ").strip(_WHITESPACE + ".,!?;:\"'()[]{}")
    return re.sub(f"[{_WHITESPACE}]+", " ", text)


def _letter_or_number(char: str) -> bool:
    return unicodedata.category(char)[0] in ("L", "N")


@dataclass
class _Turn:
    speaker: Literal["user", "assistant"]
    text: str
    start_ms: int
    end_ms: int
    id: str
    previous_id: str | None = None
    emitted: bool = False
    can_drop_as_backchannel: bool = True


class TranscriptGrouping:
    """Direct port of the TypeScript policy; no clocks, callbacks or transport."""

    def __init__(self, options: TranscriptGrouperOptions, id_prefix: str) -> None:
        self._options = options
        self._id_prefix = id_prefix
        self._acknowledgments = _ACKNOWLEDGMENTS + tuple(
            ack for phrase in options.additional_acknowledgments if (ack := _normalize_acknowledgment(phrase))
        )
        self._current: _Turn | None = None
        self._buffered: _Turn | None = None
        self._last_id: str | None = None
        self._next_id = 0
        self._last_assistant_end: int | None = None

    @property
    def speaker(self) -> str | None:
        return self._current.speaker if self._current is not None else None

    def process(self, fragments: list[TranscriptFragment]) -> list[GroupingUpdate]:
        events: list[GroupingUpdate] = []
        preferred = self.speaker or "user"
        ordered = [part for part in fragments if part.speaker == preferred] + [
            part for part in fragments if part.speaker != preferred
        ]
        if not ordered:
            return events
        first = ordered[0]
        deadline = self.deadline()
        while deadline is not None and deadline < first.start_ms:
            events.extend(self.advance(deadline))
            deadline = self.deadline()
        if self._current is not None and not any(part.speaker == self.speaker for part in ordered):
            events.extend(self.advance(first.start_ms, any(part.speaker == "user" for part in ordered)))
        for fragment in ordered:
            events.extend(self._ingest(fragment))
        return events

    def advance(self, time_ms: float, has_incoming_user: bool = False) -> list[GroupingUpdate]:
        if (
            self._current is not None
            and self._buffered is not None
            and time_ms - self._current.end_ms >= self._options.min_turn_separation_ms
            and not self._keep_backchannel(time_ms)
        ):
            self._buffered = self._maybe_drop_backchannel(time_ms)
            if self._buffered is not None:
                return self._promote()
        if (
            self._current is not None
            and self._current.speaker == "assistant"
            and not has_incoming_user
            and time_ms - self._current.end_ms >= self._options.assistant_silence_ms
        ):
            return self._finish_current("inactivity")
        return []

    def deadline(self) -> float | None:
        if self._current is None:
            return None
        if self._buffered is not None:
            separation = self._current.end_ms + self._options.min_turn_separation_ms
            if (
                self._might_be_backchannel()
                and self._buffered.can_drop_as_backchannel
                and not self._user_continued()
                and not self._recent_assistant()
            ):
                return max(separation, self._buffered.end_ms + self._options.backchannel_isolation_ms)
            return separation
        if self._current.speaker == "assistant":
            return self._current.end_ms + self._options.assistant_silence_ms
        return None

    def close(self, time_ms: float, reason: TranscriptSegmentCloseReason) -> list[GroupingUpdate]:
        buffered = self._maybe_drop_backchannel(time_ms)
        events = self._finish_current(reason)
        self._buffered = None
        if buffered is not None and buffered.text:
            events.extend(self._emit(buffered))
            events.extend(self._finish(buffered, reason))
        if reason == "timestamp_reset":
            self._last_assistant_end = None
        return events

    def _ingest(self, fragment: TranscriptFragment) -> list[GroupingUpdate]:
        if self._current is None:
            self._current = self._new_turn(fragment)
            return self._emit(self._current)
        if fragment.speaker == self._current.speaker:
            self._append(self._current, fragment, self._buffered is not None)
            return self._emit(self._current)
        if self._current.speaker == "user" and self._user_continued():
            self._buffered = None
        separation = fragment.start_ms - self._current.end_ms
        if self._current.speaker == "assistant":
            self._buffer(fragment)
            return self._promote()
        if separation < self._options.min_turn_separation_ms:
            self._buffer(fragment, self._possible_acknowledgment(fragment))
            return []
        if self._buffered is not None and self._standalone_acknowledgment(fragment, self._buffered):
            self._buffer(fragment, True)
            return []
        if self._buffered is None and self._standalone_acknowledgment(fragment):
            self._buffer(fragment, False)
            return []
        self._buffered = self._maybe_drop_backchannel(next_fragment=fragment)
        events = self._finish_current("speaker_change")
        if self._buffered is not None:
            self._current = self._buffered
            self._buffered = None
            self._append(self._current, fragment)
        else:
            self._current = self._new_turn(fragment)
        events.extend(self._emit(self._current))
        return events

    def _new_turn(self, fragment: TranscriptFragment) -> _Turn:
        turn = _Turn(
            speaker=fragment.speaker,
            text=fragment.text,
            start_ms=fragment.start_ms,
            end_ms=fragment.end_ms,
            id=f"{self._id_prefix}_{self._next_id}",
        )
        self._next_id += 1
        return turn

    @staticmethod
    def _append(turn: _Turn, fragment: TranscriptFragment, separate: bool = False) -> None:
        separator = (
            " "
            if separate
            and turn.text
            and fragment.text
            and _letter_or_number(turn.text[-1])
            and _letter_or_number(fragment.text[0])
            else ""
        )
        turn.text += separator + fragment.text
        turn.end_ms = max(turn.end_ms, fragment.end_ms)

    def _buffer(self, fragment: TranscriptFragment, can_drop: bool | None = None) -> None:
        if self._buffered is not None:
            self._append(self._buffered, fragment)
        else:
            self._buffered = self._new_turn(fragment)
        if can_drop is not None:
            self._buffered.can_drop_as_backchannel = can_drop

    def _promote(self) -> list[GroupingUpdate]:
        if self._buffered is None:
            return []
        events = self._finish_current("speaker_change")
        self._current = self._buffered
        self._buffered = None
        events.extend(self._emit(self._current))
        return events

    def _finish_current(self, reason: TranscriptSegmentCloseReason) -> list[GroupingUpdate]:
        current, self._current = self._current, None
        return self._finish(current, reason) if current is not None else []

    def _finish(self, turn: _Turn, reason: TranscriptSegmentCloseReason) -> list[GroupingUpdate]:
        if turn.speaker == "assistant":
            self._last_assistant_end = turn.end_ms
        return [TranscriptSegmentClosedEvent(self._snapshot(turn), reason)] if turn.emitted else []

    def _emit(self, turn: _Turn) -> list[GroupingUpdate]:
        if not turn.text:
            return []
        if not turn.emitted:
            turn.previous_id = self._last_id
            self._last_id = turn.id
            turn.emitted = True
        return [self._snapshot(turn)]

    @staticmethod
    def _snapshot(turn: _Turn) -> TranscriptSegment:
        assert turn.speaker in ("user", "assistant")
        return TranscriptSegment(turn.id, turn.previous_id, turn.speaker, turn.text, turn.start_ms, turn.end_ms)

    def _might_be_backchannel(self) -> bool:
        return (
            self._current is not None
            and self._current.speaker == "user"
            and self._buffered is not None
            and self._buffered.speaker == "assistant"
            and self._buffered.end_ms - self._buffered.start_ms < self._options.backchannel_max_duration_ms
        )

    def _user_continued(self) -> bool:
        return (
            self._might_be_backchannel()
            and self._buffered is not None
            and self._buffered.can_drop_as_backchannel
            and self._current is not None
            and self._current.end_ms > self._buffered.end_ms
        )

    def _recent_assistant(self) -> bool:
        return (
            self._current is not None
            and self._buffered is not None
            and self._last_assistant_end is not None
            and self._buffered.start_ms - self._last_assistant_end < self._options.backchannel_isolation_ms
            and self._buffered.start_ms <= self._current.start_ms
        )

    def _keep_backchannel(self, time_ms: float) -> bool:
        return (
            self._might_be_backchannel()
            and self._buffered is not None
            and self._buffered.can_drop_as_backchannel
            and not self._user_continued()
            and not self._recent_assistant()
            and time_ms - self._buffered.end_ms < self._options.backchannel_isolation_ms
        )

    def _maybe_drop_backchannel(
        self, time_ms: float | None = None, next_fragment: TranscriptFragment | None = None
    ) -> _Turn | None:
        if not self._might_be_backchannel() or self._buffered is None:
            return self._buffered
        if self._user_continued():
            return None
        if self._recent_assistant():
            return self._buffered
        if (
            next_fragment is not None
            and next_fragment.start_ms - self._buffered.end_ms < self._options.backchannel_isolation_ms
        ):
            return self._buffered
        if next_fragment is None and (
            time_ms is None or time_ms - self._buffered.end_ms < self._options.backchannel_isolation_ms
        ):
            return self._buffered
        return None if self._buffered.can_drop_as_backchannel else self._buffered

    def _standalone_acknowledgment(self, fragment: TranscriptFragment, previous: _Turn | None = None) -> bool:
        return (
            fragment.end_ms - (previous.start_ms if previous is not None else fragment.start_ms)
            < self._options.backchannel_max_duration_ms
            and _normalize_acknowledgment((previous.text if previous is not None else "") + fragment.text)
            in self._acknowledgments
        )

    def _possible_acknowledgment(self, fragment: TranscriptFragment) -> bool:
        text = _normalize_acknowledgment((self._buffered.text if self._buffered is not None else "") + fragment.text)
        return (
            fragment.end_ms - (self._buffered.start_ms if self._buffered is not None else fragment.start_ms)
            < self._options.backchannel_max_duration_ms
            and bool(text)
            and any(ack.startswith(text) for ack in self._acknowledgments)
        )
