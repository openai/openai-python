# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["InputAudioBufferTimeoutTriggered"]


class InputAudioBufferTimeoutTriggered(BaseModel):
    audio_end_ms: int
    """
    Millisecond offset of audio written to the input audio buffer at the time the
    timeout was triggered.
    """

    audio_start_ms: int
    """
    Millisecond offset of audio written to the input audio buffer that was after the
    playback time of the last model response.
    """

    event_id: str
    """The unique ID of the server event."""

    item_id: str
    """The ID of the item associated with this segment."""

    type: Literal["input_audio_buffer.timeout_triggered"]
    """The event type, must be `input_audio_buffer.timeout_triggered`."""
