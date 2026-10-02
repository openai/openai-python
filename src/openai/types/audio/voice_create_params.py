# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..._types import FileTypes

__all__ = ["VoiceCreateParams", "CreateVoiceRequestAudioSample", "CreateVoiceRequestPrompt"]


class CreateVoiceRequestAudioSample(TypedDict, total=False):
    audio_sample: Required[FileTypes]

    consent: Required[str]

    name: Required[str]

    type: Literal["audio_sample"]


class CreateVoiceRequestPrompt(TypedDict, total=False):
    name: Required[str]

    prompt: Required[str]

    type: Required[Literal["prompt"]]

    model: Union[str, Union[Literal["auto"], Literal["2026-10-01"]]]

    script_hint: str


VoiceCreateParams: TypeAlias = Union[CreateVoiceRequestAudioSample, CreateVoiceRequestPrompt]
