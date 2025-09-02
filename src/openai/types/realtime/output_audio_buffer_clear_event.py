# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["OutputAudioBufferClearEvent"]


class OutputAudioBufferClearEvent(BaseModel):
    type: Literal["output_audio_buffer.clear"]
    """The event type, must be `output_audio_buffer.clear`."""

    event_id: Optional[str] = None
    """The unique ID of the client event used for error handling."""
