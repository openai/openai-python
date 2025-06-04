# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["TranscriptionTextDoneEvent", "Logprob"]


class Logprob(BaseModel):
    token: Optional[str] = None
    """The token that was used to generate the log probability."""

    bytes: Optional[List[int]] = None
    """The bytes that were used to generate the log probability."""

    logprob: Optional[float] = None
    """The log probability of the token."""


class TranscriptionTextDoneEvent(BaseModel):
    text: str
    """The text that was transcribed."""

    type: Literal["transcript.text.done"]
    """The type of the event. Always `transcript.text.done`."""

    logprobs: Optional[List[Logprob]] = None
    """The log probabilities of the individual tokens in the transcription.

    Only included if you
    [create a transcription](https://platform.openai.com/docs/api-reference/audio/create-transcription)
    with the `include[]` parameter set to `logprobs`.
    """
