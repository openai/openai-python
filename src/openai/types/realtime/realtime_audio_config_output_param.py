# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .realtime_audio_formats_param import RealtimeAudioFormatsParam

__all__ = ["RealtimeAudioConfigOutputParam", "Voice", "VoiceID"]


class VoiceID(TypedDict, total=False):
    """Custom voice reference."""

    id: Required[str]
    """The custom voice ID, e.g. `voice_1234`."""


Voice: TypeAlias = Union[
    str, Literal["alloy", "ash", "ballad", "coral", "echo", "sage", "shimmer", "verse", "marin", "cedar"], VoiceID
]


class RealtimeAudioConfigOutputParam(TypedDict, total=False):
    format: RealtimeAudioFormatsParam
    """The format of the output audio."""

    speed: float
    """
    The speed of the model's spoken response as a multiple of the original speed.
    1.0 is the default speed. 0.25 is the minimum speed. 1.5 is the maximum speed.
    This value can only be changed in between model turns, not while a response is
    in progress.

    This parameter is a post-processing adjustment to the audio after it is
    generated, it's also possible to prompt the model to speak faster or slower.
    """

    voice: Voice
    """The voice the model uses to respond.

    Supported built-in voices are `alloy`, `ash`, `ballad`, `coral`, `echo`, `sage`,
    `shimmer`, `verse`, `marin`, and `cedar`. You may also provide a custom voice
    object with an `id`, for example `{ "id": "voice_1234" }`. Voice cannot be
    changed during the session once the model has responded with audio at least
    once. We recommend `marin` and `cedar` for best quality.
    """
