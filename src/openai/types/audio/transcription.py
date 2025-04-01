# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["Transcription", "Logprob"]


class Logprob(BaseModel):
    token: Optional[str] = None
    """The token in the transcription."""

    bytes: Optional[List[float]] = None
    """The bytes of the token."""

    logprob: Optional[float] = None
    """The log probability of the token."""


class Transcription(BaseModel):
    text: str
    """The transcribed text."""

    logprobs: Optional[List[Logprob]] = None
    """The log probabilities of the tokens in the transcription.

    Only returned with the models `gpt-4o-transcribe` and `gpt-4o-mini-transcribe`
    if `logprobs` is added to the `include` array.
    """
