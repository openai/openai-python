# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional, Union

from ..._models import BaseModel
from .transcription_segment import TranscriptionSegment

__all__ = ["TranslationVerbose"]


class TranslationVerbose(BaseModel):
    duration: Union[str, int]
    """The duration of the input audio."""

    language: str
    """The language of the output translation (always `english`)."""

    text: str
    """The translated text."""

    segments: Optional[List[TranscriptionSegment]] = None
    """Segments of the translated text and their corresponding details."""

    def __post_init__(self):
        if isinstance(self.duration, int):
            self.duration = str(self.duration)
