# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..._types import FileTypes

__all__ = ["VoiceCreateParams", "CreateVoiceRequestAudioSample"]


class CreateVoiceRequestAudioSample(TypedDict, total=False):
    audio_sample: Required[FileTypes]

    consent: Required[str]

    name: Required[str]

    type: Literal["audio_sample"]


VoiceCreateParams: TypeAlias = CreateVoiceRequestAudioSample
