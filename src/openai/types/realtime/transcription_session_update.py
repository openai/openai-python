# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .realtime_transcription_session_create_request import RealtimeTranscriptionSessionCreateRequest

__all__ = ["TranscriptionSessionUpdate"]


class TranscriptionSessionUpdate(BaseModel):
    session: RealtimeTranscriptionSessionCreateRequest
    """Realtime transcription session object configuration."""

    type: Literal["transcription_session.update"]
    """The event type, must be `transcription_session.update`."""

    event_id: Optional[str] = None
    """Optional client-generated ID used to identify this event."""
