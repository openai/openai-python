# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from ...._models import BaseModel

__all__ = [
    "ConversationItemInputAudioTranscriptionCompletedEvent",
    "Usage",
    "UsageTranscriptTextUsageTokens",
    "UsageTranscriptTextUsageTokensInputTokenDetails",
    "UsageTranscriptTextUsageDuration",
    "Logprob",
]


class UsageTranscriptTextUsageTokensInputTokenDetails(BaseModel):
    audio_tokens: Optional[int] = None
    """Number of audio tokens billed for this request."""

    text_tokens: Optional[int] = None
    """Number of text tokens billed for this request."""


class UsageTranscriptTextUsageTokens(BaseModel):
    input_tokens: int
    """Number of input tokens billed for this request."""

    output_tokens: int
    """Number of output tokens generated."""

    total_tokens: int
    """Total number of tokens used (input + output)."""

    type: Literal["tokens"]
    """The type of the usage object. Always `tokens` for this variant."""

    input_token_details: Optional[UsageTranscriptTextUsageTokensInputTokenDetails] = None
    """Details about the input tokens billed for this request."""


class UsageTranscriptTextUsageDuration(BaseModel):
    seconds: float
    """Duration of the input audio in seconds."""

    type: Literal["duration"]
    """The type of the usage object. Always `duration` for this variant."""


Usage: TypeAlias = Union[UsageTranscriptTextUsageTokens, UsageTranscriptTextUsageDuration]


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

    usage: Usage
    """Usage statistics for the transcription."""

    logprobs: Optional[List[Logprob]] = None
    """The log probabilities of the transcription."""
