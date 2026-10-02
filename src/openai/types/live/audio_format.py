# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = ["AudioFormat", "AudioPCM", "AudioPCMU", "AudioPCMA"]


class AudioPCM(BaseModel):
    """Raw, mono 16-bit little-endian PCM audio for a Live WebSocket connection."""

    rate: Literal[16000, 24000]
    """Audio sample rate in hertz.

    Live WebSocket PCM audio supports 16000 or 24000 Hz.
    """

    type: Literal["audio/pcm"]
    """The audio encoding. Always `audio/pcm`."""


class AudioPCMU(BaseModel):
    """Raw, mono G.711 μ-law audio for a Live WebSocket connection."""

    rate: int
    """Audio sample rate in hertz. G.711 audio uses 8000 Hz."""

    type: Literal["audio/pcmu"]
    """The audio encoding. Always `audio/pcmu`."""


class AudioPCMA(BaseModel):
    """Raw, mono G.711 A-law audio for a Live WebSocket connection."""

    rate: int
    """Audio sample rate in hertz. G.711 audio uses 8000 Hz."""

    type: Literal["audio/pcma"]
    """The audio encoding. Always `audio/pcma`."""


AudioFormat: TypeAlias = Annotated[Union[AudioPCM, AudioPCMU, AudioPCMA], PropertyInfo(discriminator="type")]
