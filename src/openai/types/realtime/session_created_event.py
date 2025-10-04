# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel
from .realtime_session_create_request import RealtimeSessionCreateRequest
from .realtime_transcription_session_create_request import RealtimeTranscriptionSessionCreateRequest

__all__ = ["SessionCreatedEvent", "Session"]

Session: TypeAlias = Union[RealtimeSessionCreateRequest, RealtimeTranscriptionSessionCreateRequest]


class SessionCreatedEvent(BaseModel):
    event_id: str
    """The unique ID of the server event."""

    session: Session
    """The session configuration."""

    type: Literal["session.created"]
    """The event type, must be `session.created`."""
