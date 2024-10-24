# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ChatCompletionAudioParam"]


class ChatCompletionAudioParam(TypedDict, total=False):
    format: Required[Literal["wav", "mp3", "flac", "opus", "pcm16"]]
    """Specifies the output audio format.

    Must be one of `wav`, `mp3`, `flac`, `opus`, or `pcm16`.
    """

    voice: Required[Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]]
    """Specifies the voice type.

    Supported voices are `alloy`, `echo`, `fable`, `onyx`, `nova`, and `shimmer`.
    """
