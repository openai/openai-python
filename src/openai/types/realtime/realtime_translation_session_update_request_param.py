# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

from .noise_reduction_type import NoiseReductionType

__all__ = [
    "RealtimeTranslationSessionUpdateRequestParam",
    "Audio",
    "AudioInput",
    "AudioInputNoiseReduction",
    "AudioInputTranscription",
    "AudioOutput",
]


class AudioInputNoiseReduction(TypedDict, total=False):
    """Optional input noise reduction. Set to `null` to disable it."""

    type: Required[NoiseReductionType]
    """Type of noise reduction.

    `near_field` is for close-talking microphones such as headphones, `far_field` is
    for far-field microphones such as laptop or conference room microphones.
    """


class AudioInputTranscription(TypedDict, total=False):
    """Optional source-language transcription.

    When configured, the server emits
    `session.input_transcript.delta` events. Translation itself still runs from
    the input audio stream.
    """

    model: Required[str]
    """The transcription model to use for source transcript deltas."""


class AudioInput(TypedDict, total=False):
    noise_reduction: Optional[AudioInputNoiseReduction]
    """Optional input noise reduction. Set to `null` to disable it."""

    transcription: Optional[AudioInputTranscription]
    """Optional source-language transcription.

    When configured, the server emits `session.input_transcript.delta` events.
    Translation itself still runs from the input audio stream.
    """


class AudioOutput(TypedDict, total=False):
    language: str
    """Target language for translated output audio and transcript deltas."""


class Audio(TypedDict, total=False):
    """Configuration for translation input and output audio."""

    input: AudioInput

    output: AudioOutput


class RealtimeTranslationSessionUpdateRequestParam(TypedDict, total=False):
    """Realtime translation session fields that can be updated with `session.update`."""

    audio: Audio
    """Configuration for translation input and output audio."""
