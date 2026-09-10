# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["InputAudioMuteEvent"]


class InputAudioMuteEvent(BaseModel):
    """Mute audio input to the Live model without closing the session.

    The server acknowledges with `session.input_audio.muted`.
    """

    type: Literal["session.input_audio.mute"]
    """The Live client event type. Always `session.input_audio.mute`."""

    event_id: Optional[str] = None
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
