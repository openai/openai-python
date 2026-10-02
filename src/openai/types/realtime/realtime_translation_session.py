# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .noise_reduction_type import NoiseReductionType

__all__ = [
    "RealtimeTranslationSession",
    "Audio",
    "AudioInput",
    "AudioInputNoiseReduction",
    "AudioInputTranscription",
    "AudioOutput",
]


class AudioInputNoiseReduction(BaseModel):
    """Optional input noise reduction."""

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
    """The transcription model used for source transcript deltas."""


class AudioInput(BaseModel):
    noise_reduction: Optional[AudioInputNoiseReduction] = None
    """Optional input noise reduction."""

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


class RealtimeTranslationSession(BaseModel):
    """A Realtime translation session.

    Translation sessions continuously translate input
    audio into the configured output language.
    """

    id: str
    """Unique identifier for the session that looks like `sess_1234567890abcdef`."""

    audio: Audio
    """Configuration for translation input and output audio."""

    expires_at: int
    """Expiration timestamp for the session, in seconds since epoch."""

    model: str
    """The Realtime translation model used for this session.

    This field is set at session creation and cannot be changed with
    `session.update`.
    """

    type: Literal["translation"]
    """The session type. Always `translation` for Realtime translation sessions."""
