# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["TranscriptionTextSegmentEvent"]


class TranscriptionTextSegmentEvent(BaseModel):
    id: str
    """Unique identifier for the segment."""

    end: float
    """End timestamp of the segment in seconds."""

    speaker: str
    """Speaker label for this segment."""

    start: float
    """Start timestamp of the segment in seconds."""

    text: str
    """Transcript text for this segment."""

    type: Literal["transcript.text.segment"]
    """The type of the event. Always `transcript.text.segment`."""
