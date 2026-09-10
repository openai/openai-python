# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["InputTranscriptDeltaEvent"]


class InputTranscriptDeltaEvent(BaseModel):
    """A transcript fragment for user input audio in the Live session.

    Accumulate fragments in delivery order; these events do not define complete turns or include a transcript-done event.
    """

    delta: str
    """The transcript text fragment for the audio in this time range.

    Append fragments in delivery order to build the transcript.
    """

    end_ms: int
    """
    The end of this event on the Live session timeline, in milliseconds from the
    beginning of the session. For appended context, this can equal start_ms.
    """

    event_id: str
    """The unique ID of the Live server event."""

    start_ms: int
    """
    The start of this event on the Live session timeline, in milliseconds from the
    beginning of the session.
    """

    type: Literal["session.input_transcript.delta"]
    """The event type, always `session.input_transcript.delta`."""

    client_event_id: Optional[str] = None
    """
    The event_id of the client command associated with this server event, when
    supplied.
    """
