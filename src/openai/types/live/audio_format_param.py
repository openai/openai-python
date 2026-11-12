# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = ["AudioFormatParam", "AudioPCM", "AudioPCMU", "AudioPCMA"]


class AudioPCM(TypedDict, total=False):
    """Raw, mono 16-bit little-endian PCM audio for a Live WebSocket connection."""

    rate: Required[Literal[16000, 24000]]
    """Audio sample rate in hertz.

    Live WebSocket PCM audio supports 16000 or 24000 Hz.
    """

    type: Required[Literal["audio/pcm"]]
    """The audio encoding. Always `audio/pcm`."""


class AudioPCMU(TypedDict, total=False):
    """Raw, mono G.711 μ-law audio for a Live WebSocket connection."""

    rate: Required[int]
    """Audio sample rate in hertz. G.711 audio uses 8000 Hz."""

    type: Required[Literal["audio/pcmu"]]
    """The audio encoding. Always `audio/pcmu`."""


class AudioPCMA(TypedDict, total=False):
    """Raw, mono G.711 A-law audio for a Live WebSocket connection."""

    rate: Required[int]
    """Audio sample rate in hertz. G.711 audio uses 8000 Hz."""

    type: Required[Literal["audio/pcma"]]
    """The audio encoding. Always `audio/pcma`."""


AudioFormatParam: TypeAlias = Union[AudioPCM, AudioPCMU, AudioPCMA]
