# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["InputAudioAppendEvent"]


class InputAudioAppendEvent(BaseModel):
    """Send audio to a Live session over its primary WebSocket.

    WebRTC and SIP sessions send audio over their media transport.
    """

    audio: str
    """
    Base64-encoded raw audio in the startup-selected format, without a WAV or other
    container header. Primary WebSocket only; media transports use their audio
    track. Audio appends have no acknowledgment. Reflected sideband server events
    reuse this event type and audio key, with no timestamps or event_id; their audio
    is always mono PCM16LE at 24 kHz.
    """

    type: Literal["session.input_audio.append"]
    """The Live client event type. Always `session.input_audio.append`."""

    event_id: Optional[str] = None
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
