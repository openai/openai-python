# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["InputAudioBufferDtmfEventReceivedEvent"]


class InputAudioBufferDtmfEventReceivedEvent(BaseModel):
    event: str
    """The telephone keypad that was pressed by the user."""

    received_at: int
    """UTC Unix Timestamp when DTMF Event was received by server."""

    type: Literal["input_audio_buffer.dtmf_event_received"]
    """The event type, must be `input_audio_buffer.dtmf_event_received`."""
