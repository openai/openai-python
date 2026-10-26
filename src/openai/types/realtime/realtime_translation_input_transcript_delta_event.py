# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["RealtimeTranslationInputTranscriptDeltaEvent"]


class RealtimeTranslationInputTranscriptDeltaEvent(BaseModel):
    """Returned when optional source-language transcript text is available.

    This event
    is emitted only when `audio.input.transcription` is configured.

    Transcript deltas are append-only text fragments. Clients should not insert
    unconditional spaces between deltas.
    """

    delta: str
    """Append-only source-language transcript text."""

    event_id: str
    """The unique ID of the server event."""

    type: Literal["session.input_transcript.delta"]
    """The event type, must be `session.input_transcript.delta`."""

    elapsed_ms: Optional[int] = None
    """
    Timing metadata for stream alignment, derived from the translation frame when
    available. It advances in 200 ms increments, but multiple transcript deltas may
    share the same `elapsed_ms`. Treat it as alignment metadata, not a unique
    transcript-delta identifier.
    """
