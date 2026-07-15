# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ChatCompletionContentPartInputAudioParam", "InputAudio", "PromptCacheBreakpoint"]


class InputAudio(TypedDict, total=False):
    data: Required[str]
    """Base64 encoded audio data."""

    format: Required[Literal["wav", "mp3"]]
    """The format of the encoded audio data. Currently supports "wav" and "mp3"."""


class PromptCacheBreakpoint(TypedDict, total=False):
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`; the boundary is not rounded to a token block.
    """

    mode: Required[Literal["explicit"]]
    """The breakpoint mode. Always `explicit`."""


class ChatCompletionContentPartInputAudioParam(TypedDict, total=False):
    """Learn about [audio inputs](https://platform.openai.com/docs/guides/audio)."""

    input_audio: Required[InputAudio]

    type: Required[Literal["input_audio"]]
    """The type of the content part. Always `input_audio`."""

    prompt_cache_breakpoint: PromptCacheBreakpoint
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`;
    the boundary is not rounded to a token block.
    """
