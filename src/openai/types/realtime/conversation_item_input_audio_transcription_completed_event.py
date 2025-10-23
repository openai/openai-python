# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel
from .log_prob_properties import LogProbProperties

__all__ = [
    "ConversationItemInputAudioTranscriptionCompletedEvent",
    "Usage",
    "UsageTranscriptTextUsageTokens",
    "UsageTranscriptTextUsageTokensInputTokenDetails",
    "UsageTranscriptTextUsageDuration",
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


class ConversationItemInputAudioTranscriptionCompletedEvent(BaseModel):
    content_index: int
    """The index of the content part containing the audio."""

    event_id: str
    """The unique ID of the server event."""

    item_id: str
    """The ID of the item containing the audio that is being transcribed."""

    transcript: str
    """The transcribed text."""

    type: Literal["conversation.item.input_audio_transcription.completed"]
    """
    The event type, must be `conversation.item.input_audio_transcription.completed`.
    """

    usage: Usage
    """
    Usage statistics for the transcription, this is billed according to the ASR
    model's pricing rather than the realtime model's pricing.
    """

    logprobs: Optional[List[LogProbProperties]] = None
    """The log probabilities of the transcription."""
