from __future__ import annotations

from dataclasses import dataclass
from typing_extensions import Literal

TranscriptSegmentCloseReason = Literal["speaker_change", "inactivity", "timestamp_reset", "session_closed", "manual"]


@dataclass(frozen=True)
class TranscriptSegment:
    """An immutable display snapshot, not a server conversation item or turn.

    Replace the displayed text on each update. IDs are local to this projection;
    start/end times describe public transcript intervals, not audio playback.
    """

    id: str
    previous_id: str | None
    speaker: Literal["user", "assistant"]
    text: str
    start_ms: int
    end_ms: int


@dataclass(frozen=True)
class TranscriptSegmentClosedEvent:
    """The final segment snapshot and the local reason it was closed."""

    segment: TranscriptSegment
    reason: TranscriptSegmentCloseReason


@dataclass(frozen=True)
class TranscriptGrouperOptions:
    """Resolved options for the grouping policy; timing thresholds are in milliseconds."""

    min_turn_separation_ms: float = 500
    assistant_silence_ms: float = 2000
    backchannel_max_duration_ms: float = 1000
    backchannel_isolation_ms: float = 2000
    additional_acknowledgments: tuple[str, ...] = ()


@dataclass(frozen=True)
class TranscriptFragment:
    speaker: Literal["user", "assistant"]
    text: str
    start_ms: int
    end_ms: int


GroupingUpdate = TranscriptSegment | TranscriptSegmentClosedEvent
