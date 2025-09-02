# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .log_prob_properties import LogProbProperties

__all__ = ["ConversationItemInputAudioTranscriptionDeltaEvent"]


class ConversationItemInputAudioTranscriptionDeltaEvent(BaseModel):
    event_id: str
    """The unique ID of the server event."""

    item_id: str
    """The ID of the item."""

    type: Literal["conversation.item.input_audio_transcription.delta"]
    """The event type, must be `conversation.item.input_audio_transcription.delta`."""

    content_index: Optional[int] = None
    """The index of the content part in the item's content array."""

    delta: Optional[str] = None
    """The text delta."""

    logprobs: Optional[List[LogProbProperties]] = None
    """The log probabilities of the transcription."""
