# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["TranscriptionLanguage"]


class TranscriptionLanguage(BaseModel):
    """A language detected in transcribed audio."""

    code: str
    """The code of a language detected in the audio."""
