# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .realtime_session_create_request import RealtimeSessionCreateRequest
from .realtime_transcription_session_create_request import RealtimeTranscriptionSessionCreateRequest

__all__ = ["SessionUpdatedEvent", "Session"]

Session: TypeAlias = Annotated[
    Union[RealtimeSessionCreateRequest, RealtimeTranscriptionSessionCreateRequest], PropertyInfo(discriminator="type")
]


class SessionUpdatedEvent(BaseModel):
    """
    Returned when a session is updated with a `session.update` event, unless
    there is an error.
    """

    event_id: str
    """The unique ID of the server event."""

    session: Session
    """The session configuration."""

    type: Literal["session.updated"]
    """The event type, must be `session.updated`."""
