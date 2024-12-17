# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["InputAudioBufferCommittedEvent"]


class InputAudioBufferCommittedEvent(BaseModel):
    event_id: str
    """The unique ID of the server event."""

    item_id: str
    """The ID of the user message item that will be created."""

    previous_item_id: str
    """The ID of the preceding item after which the new item will be inserted."""

    type: Literal["input_audio_buffer.committed"]
    """The event type, must be `input_audio_buffer.committed`."""
