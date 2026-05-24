# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .realtime_audio_formats_param import RealtimeAudioFormatsParam

__all__ = ["RealtimeResponseCreateAudioOutputParam", "Output", "OutputVoice", "OutputVoiceID"]


class OutputVoiceID(TypedDict, total=False):
    """Custom voice reference."""

    id: Required[str]
    """The custom voice ID, e.g. `voice_1234`."""


OutputVoice: TypeAlias = Union[
    str, Literal["alloy", "ash", "ballad", "coral", "echo", "sage", "shimmer", "verse", "marin", "cedar"], OutputVoiceID
]


class Output(TypedDict, total=False):
    format: RealtimeAudioFormatsParam
    """The format of the output audio."""

    voice: OutputVoice
    """The voice the model uses to respond.

    Supported built-in voices are `alloy`, `ash`, `ballad`, `coral`, `echo`, `sage`,
    `shimmer`, `verse`, `marin`, and `cedar`. You may also provide a custom voice
    object with an `id`, for example `{ "id": "voice_1234" }`. Voice cannot be
    changed during the session once the model has responded with audio at least
    once. We recommend `marin` and `cedar` for best quality.
    """


class RealtimeResponseCreateAudioOutputParam(TypedDict, total=False):
    """Configuration for audio input and output."""

    output: Output
