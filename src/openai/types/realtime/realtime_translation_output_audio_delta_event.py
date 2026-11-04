# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["RealtimeTranslationOutputAudioDeltaEvent"]


class RealtimeTranslationOutputAudioDeltaEvent(BaseModel):
    """Returned when translated output audio is available.

    The `delta` contains a
    PCM16 audio chunk whose length can vary. Clients should decode and queue the
    complete delta instead of assuming a fixed byte or sample count.
    """

    delta: str
    """Base64-encoded translated audio data."""

    event_id: str
    """The unique ID of the server event."""

    type: Literal["session.output_audio.delta"]
    """The event type, must be `session.output_audio.delta`."""

    channels: Optional[int] = None
    """Number of audio channels."""

    elapsed_ms: Optional[int] = None
    """
    Timing metadata for stream alignment, derived from the translation frame when
    available. Treat `elapsed_ms` as alignment metadata, not a unique event
    identifier.
    """

    format: Optional[Literal["pcm16"]] = None
    """Audio encoding for `delta`."""

    sample_rate: Optional[int] = None
    """Sample rate of the audio delta."""
