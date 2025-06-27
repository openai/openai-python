# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["ConversationItemInputAudioTranscriptionCompletedEvent", "Logprob"]


class Logprob(BaseModel):
    token: str
    """The token that was used to generate the log probability."""

    bytes: List[int]
    """The bytes that were used to generate the log probability."""

    logprob: float
    """The log probability of the token."""


class ConversationItemInputAudioTranscriptionCompletedEvent(BaseModel):
    content_index: int
    """The index of the content part containing the audio."""

    event_id: str
    """The unique ID of the server event."""

    item_id: str
    """The ID of the user message item containing the audio."""

    transcript: str
    """The transcribed text."""

    type: Literal["conversation.item.input_audio_transcription.completed"]
    """
    The event type, must be `conversation.item.input_audio_transcription.completed`.
    """

    logprobs: Optional[List[Logprob]] = None
    """The log probabilities of the transcription."""
