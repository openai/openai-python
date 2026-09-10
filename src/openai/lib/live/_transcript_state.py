from __future__ import annotations

import math
import itertools
from typing import Callable
from dataclasses import fields, dataclass
from typing_extensions import Literal, TypeGuard

from ._types import GroupingUpdate, TranscriptFragment, TranscriptGrouperOptions
from ...types.live import ServerEvent
from ..._exceptions import OpenAIError
from ._transcript_grouping import TranscriptGrouping

MAX_TIMEOUT_MS = 2_147_483_647
_MAX_SAFE_INTEGER = 9_007_199_254_740_991
_GROUPER_IDS = itertools.count()


def validated_options(options: TranscriptGrouperOptions) -> TranscriptGrouperOptions:
    for field in fields(options):
        if field.name == "additional_acknowledgments":
            continue
        value = getattr(options, field.name)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= MAX_TIMEOUT_MS:
            raise OpenAIError(f"{field.name} must be a finite number between 0 and {MAX_TIMEOUT_MS}")
    return options


@dataclass(frozen=True)
class _ReceivedFragment:
    fragment: TranscriptFragment
    received_at: float


class TranscriptState:
    """Clock-driven state shared by the sync and async adapters; callers serialize access."""

    def __init__(self, options: TranscriptGrouperOptions, now: Callable[[], float]) -> None:
        self._now = now
        self._grouping = TranscriptGrouping(validated_options(options), f"segment_{next(_GROUPER_IDS)}")
        self._seen_ids: set[str] = set()
        self._pending: list[_ReceivedFragment] = []
        self._anchor: tuple[int, float] | None = None
        self._last_start_ms: int | None = None
        self.closed = False

    def push(self, event: ServerEvent) -> list[GroupingUpdate] | None:
        if self.closed:
            raise OpenAIError("Cannot push events after closing the transcript grouper")
        if event.type == "session.closed":
            return self.finish("session_closed")
        if event.type not in ("session.input_transcript.delta", "session.output_transcript.delta"):
            return None
        # SDK events may be constructed without validation. Check only consumed
        # variants and copy their primitive fields before updating any state.
        event_id = getattr(event, "event_id", None)
        text = getattr(event, "delta", None)
        start_ms = getattr(event, "start_ms", None)
        end_ms = getattr(event, "end_ms", None)
        speaker: Literal["user", "assistant"] = (
            "user" if event.type == "session.input_transcript.delta" else "assistant"
        )
        if (
            not isinstance(event_id, str)
            or not event_id
            or not isinstance(text, str)
            or not self._valid_timestamp(start_ms)
            or not self._valid_timestamp(end_ms)
            or end_ms < start_ms
        ):
            raise OpenAIError(
                "Invalid public Live transcript delta: expected an ID, text, and a nonnegative timed interval"
            )
        if event_id in self._seen_ids:
            return None
        self._seen_ids.add(event_id)
        if not text:
            return None
        fragment = TranscriptFragment(speaker, text, int(start_ms), int(end_ms))
        received = _ReceivedFragment(fragment, self._now())
        updates: list[GroupingUpdate] = []
        pending = self._pending[0].fragment if self._pending else None
        if pending is not None and pending.start_ms == start_ms and pending.end_ms == end_ms:
            self._pending.append(received)
            if any(part.fragment.speaker != speaker for part in self._pending):
                updates.extend(self._flush_pending())
        else:
            updates.extend(self._flush_pending())
            if self._grouping.speaker == speaker:
                updates.extend(self._commit([received]))
            else:
                self._pending.append(received)
        return updates

    @staticmethod
    def _valid_timestamp(value: object) -> TypeGuard[int | float]:
        # JavaScript's Number.isSafeInteger also accepts 1.0. Preserve that
        # behavior for unchecked models, but never treat Python bool as a time.
        return (
            not isinstance(value, bool)
            and isinstance(value, (int, float))
            and 0 <= value <= _MAX_SAFE_INTEGER
            and int(value) == value
        )

    def finish(self, reason: Literal["manual", "session_closed"]) -> list[GroupingUpdate]:
        if self.closed:
            return []
        assert reason in ("manual", "session_closed")
        self.closed = True
        updates = self._flush_pending()
        updates.extend(self._grouping.close(self._source_now(), reason))
        self._seen_ids.clear()
        return updates

    def tick(self) -> list[GroupingUpdate]:
        updates = self._flush_pending()
        updates.extend(self._grouping.advance(self._source_now()))
        return updates

    def delay(self) -> int | None:
        if self.closed:
            return None
        deadline = self._grouping.deadline()
        if self._pending:
            delay = self._pending[0].received_at + 50 - self._now()
        elif deadline is not None:
            delay = deadline - self._source_now()
        else:
            return None
        return min(MAX_TIMEOUT_MS, max(0, math.ceil(delay)))

    def _source_now(self) -> float:
        if self._anchor is None:
            return 0
        source_ms, received_at = self._anchor
        return source_ms + max(0, self._now() - received_at)

    def _flush_pending(self) -> list[GroupingUpdate]:
        pending, self._pending = self._pending, []
        return self._commit(pending)

    def _commit(self, fragments: list[_ReceivedFragment]) -> list[GroupingUpdate]:
        if not fragments:
            return []
        first = fragments[0].fragment
        updates: list[GroupingUpdate] = []
        if self._last_start_ms is not None and first.start_ms < self._last_start_ms:
            updates.extend(self._grouping.close(self._source_now(), "timestamp_reset"))
            self._anchor = None
        self._last_start_ms = first.start_ms
        self._anchor = (
            max(self._anchor[0] if self._anchor is not None else 0, *(part.fragment.end_ms for part in fragments)),
            max(part.received_at for part in fragments),
        )
        updates.extend(self._grouping.process([part.fragment for part in fragments]))
        return updates
