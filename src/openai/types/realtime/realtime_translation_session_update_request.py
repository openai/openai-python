# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .noise_reduction_type import NoiseReductionType

__all__ = [
    "RealtimeTranslationSessionUpdateRequest",
    "Audio",
    "AudioInput",
    "AudioInputNoiseReduction",
    "AudioInputTranscription",
    "AudioOutput",
]


class AudioInputNoiseReduction(BaseModel):
    """Optional input noise reduction. Set to `null` to disable it."""

    type: NoiseReductionType
    """Type of noise reduction.

    `near_field` is for close-talking microphones such as headphones, `far_field` is
    for far-field microphones such as laptop or conference room microphones.
    """


class AudioInputTranscription(BaseModel):
    """Optional source-language transcription.

    When configured, the server emits
    `session.input_transcript.delta` events. Translation itself still runs from
    the input audio stream.
    """

    model: str
    """The transcription model to use for source transcript deltas."""


class AudioInput(BaseModel):
    noise_reduction: Optional[AudioInputNoiseReduction] = None
    """Optional input noise reduction. Set to `null` to disable it."""

    transcription: Optional[AudioInputTranscription] = None
    """Optional source-language transcription.

    When configured, the server emits `session.input_transcript.delta` events.
    Translation itself still runs from the input audio stream.
    """


class AudioOutput(BaseModel):
    language: Optional[str] = None
    """Target language for translated output audio and transcript deltas."""


class Audio(BaseModel):
    """Configuration for translation input and output audio."""

    input: Optional[AudioInput] = None

    output: Optional[AudioOutput] = None


class RealtimeTranslationSessionUpdateRequest(BaseModel):
    """Realtime translation session fields that can be updated with `session.update`."""

    audio: Optional[Audio] = None
    """Configuration for translation input and output audio."""
