# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypedDict

__all__ = ["SpeechCreateParams"]


class SpeechCreateParams(TypedDict, total=False):
    input: Required[str]
    """The text to generate audio for. The maximum length is 4096 characters."""

    model: Required[Union[str, Literal["tts-1", "tts-1-hd"]]]
    """
    One of the available [TTS models](https://platform.openai.com/docs/models/tts):
    `tts-1` or `tts-1-hd`
    """

    voice: Required[Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]]
    """The voice to use when generating the audio.

    Supported voices are `alloy`, `echo`, `fable`, `onyx`, `nova`, and `shimmer`.
    Previews of the voices are available in the
    [Text to speech guide](https://platform.openai.com/docs/guides/text-to-speech/voice-options).
    """

    response_format: Literal["mp3", "opus", "aac", "flac", "pcm", "wav"]
    """The format to return audio in.

    Supported formats are `mp3`, `opus`, `aac`, `flac`, `pcm`, and `wav`.

    The `pcm` audio format, similar to `wav` but without a header, utilizes a 24kHz
    sample rate, mono channel, and 16-bit depth in signed little-endian format.
    """

    speed: float
    """The speed of the generated audio.

    Select a value from `0.25` to `4.0`. `1.0` is the default.
    """
