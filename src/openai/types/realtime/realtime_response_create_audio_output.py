# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel
from .realtime_audio_formats import RealtimeAudioFormats

__all__ = ["RealtimeResponseCreateAudioOutput", "Output", "OutputVoice", "OutputVoiceID"]


class OutputVoiceID(BaseModel):
    """Custom voice reference."""

    id: str
    """The custom voice ID, e.g. `voice_1234`."""


OutputVoice: TypeAlias = Union[
    str, Literal["alloy", "ash", "ballad", "coral", "echo", "sage", "shimmer", "verse", "marin", "cedar"], OutputVoiceID
]


class Output(BaseModel):
    format: Optional[RealtimeAudioFormats] = None
    """The format of the output audio."""

    voice: Optional[OutputVoice] = None
    """The voice the model uses to respond.

    Supported built-in voices are `alloy`, `ash`, `ballad`, `coral`, `echo`, `sage`,
    `shimmer`, `verse`, `marin`, and `cedar`. You may also provide a custom voice
    object with an `id`, for example `{ "id": "voice_1234" }`. Voice cannot be
    changed during the session once the model has responded with audio at least
    once. We recommend `marin` and `cedar` for best quality.
    """


class RealtimeResponseCreateAudioOutput(BaseModel):
    """Configuration for audio input and output."""

    output: Optional[Output] = None
