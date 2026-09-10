# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["InputAudioUnmutedEvent"]


class InputAudioUnmutedEvent(BaseModel):
    """Returned when a session.input_audio.unmute command is accepted.

    Input audio is sent to the model again.
    """

    event_id: str
    """The unique ID of the Live server event."""

    type: Literal["session.input_audio.unmuted"]
    """The event type, always `session.input_audio.unmuted`."""

    client_event_id: Optional[str] = None
    """
    The event_id of the client command associated with this server event, when
    supplied.
    """
