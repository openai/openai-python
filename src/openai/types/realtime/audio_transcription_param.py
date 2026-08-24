# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, TypedDict

from ..._types import SequenceNotStr

__all__ = ["AudioTranscriptionParam"]


class AudioTranscriptionParam(TypedDict, total=False):
    delay: Literal["minimal", "low", "medium", "high", "xhigh"]
    """
    Controls how long the model waits before emitting transcription text. Higher
    values can improve transcription accuracy at the cost of latency. Only supported
    with `gpt-realtime-whisper` in GA Realtime sessions.
    """

    keywords: SequenceNotStr[str]
    """Words or phrases to guide transcription of the input audio.

    Supported by `gpt-transcribe` and `gpt-live-transcribe`.
    """

    language: str
    """The language of the input audio.

    Supplying the input language in
    [ISO-639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) (e.g. `en`)
    format will improve accuracy and latency.
    """

    languages: SequenceNotStr[str]
    """
    Possible languages of the input audio, in
    [ISO-639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) format.
    Supported by `gpt-transcribe` and `gpt-live-transcribe`.
    """

    model: Union[
        str,
        Literal[
            "whisper-1",
            "gpt-transcribe",
            "gpt-live-transcribe",
            "gpt-4o-mini-transcribe",
            "gpt-4o-mini-transcribe-2025-12-15",
            "gpt-4o-transcribe",
            "gpt-4o-transcribe-diarize",
            "gpt-realtime-whisper",
        ],
    ]
    """The model to use for transcription.

    Current options are `whisper-1`, `gpt-transcribe`, `gpt-live-transcribe`,
    `gpt-4o-mini-transcribe`, `gpt-4o-mini-transcribe-2025-12-15`,
    `gpt-4o-transcribe`, `gpt-4o-transcribe-diarize`, and `gpt-realtime-whisper`.
    Use `gpt-4o-transcribe-diarize` when you need diarization with speaker labels.
    """

    prompt: str
    """
    An optional text to guide the model's style or continue a previous audio
    segment. For `whisper-1`, the
    [prompt is a list of keywords](https://platform.openai.com/docs/guides/speech-to-text#prompting).
    For `gpt-4o-transcribe` models (excluding `gpt-4o-transcribe-diarize`), the
    prompt is a free text string, for example "expect words related to technology".
    Prompt is not supported with `gpt-realtime-whisper` in GA Realtime sessions.
    """
