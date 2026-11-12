# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ..._types import FileTypes

__all__ = ["VoiceConsentCreateParams"]


class VoiceConsentCreateParams(TypedDict, total=False):
    language: Required[str]
    """The BCP 47 language tag for the consent phrase (for example, `en-US`)."""

    name: Required[str]
    """The label to use for this consent recording."""

    recording: Required[FileTypes]
    """The consent audio recording file. Maximum size is 10 MiB.

    Supported MIME types: `audio/mpeg`, `audio/wav`, `audio/x-wav`, `audio/ogg`,
    `audio/aac`, `audio/flac`, `audio/webm`, `audio/mp4`.
    """
