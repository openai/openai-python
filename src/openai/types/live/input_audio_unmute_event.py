# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["InputAudioUnmuteEvent"]


class InputAudioUnmuteEvent(BaseModel):
    """Resume audio input to a Live model after muting it.

    The server acknowledges with `session.input_audio.unmuted`.
    """

    type: Literal["session.input_audio.unmute"]
    """The Live client event type. Always `session.input_audio.unmute`."""

    event_id: Optional[str] = None
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
