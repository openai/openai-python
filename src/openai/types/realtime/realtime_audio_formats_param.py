# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, TypeAlias, TypedDict

__all__ = ["RealtimeAudioFormatsParam", "AudioPCM", "AudioPCMU", "AudioPCMA"]


class AudioPCM(TypedDict, total=False):
    rate: Literal[24000]
    """The sample rate of the audio. Always `24000`."""

    type: Literal["audio/pcm"]
    """The audio format. Always `audio/pcm`."""


class AudioPCMU(TypedDict, total=False):
    type: Literal["audio/pcmu"]
    """The audio format. Always `audio/pcmu`."""


class AudioPCMA(TypedDict, total=False):
    type: Literal["audio/pcma"]
    """The audio format. Always `audio/pcma`."""


RealtimeAudioFormatsParam: TypeAlias = Union[AudioPCM, AudioPCMU, AudioPCMA]
