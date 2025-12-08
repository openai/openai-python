# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, TypedDict

from .realtime_audio_formats_param import RealtimeAudioFormatsParam

__all__ = ["RealtimeResponseCreateAudioOutputParam", "Output"]


class Output(TypedDict, total=False):
    format: RealtimeAudioFormatsParam
    """The format of the output audio."""

    voice: Union[str, Literal["alloy", "ash", "ballad", "coral", "echo", "sage", "shimmer", "verse", "marin", "cedar"]]
    """The voice the model uses to respond.

    Voice cannot be changed during the session once the model has responded with
    audio at least once. Current voice options are `alloy`, `ash`, `ballad`,
    `coral`, `echo`, `sage`, `shimmer`, `verse`, `marin`, and `cedar`. We recommend
    `marin` and `cedar` for best quality.
    """


class RealtimeResponseCreateAudioOutputParam(TypedDict, total=False):
    """Configuration for audio input and output."""

    output: Output
