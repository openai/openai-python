from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from typing_extensions import assert_never

from ..._types import Omit
from ...types.audio.translation import Translation
from ...types.audio.transcription import Transcription
from ...types.audio_response_format import AudioResponseFormat
from ...types.audio.translation_verbose import TranslationVerbose
from ...types.audio.transcription_verbose import TranscriptionVerbose
from ...types.audio.transcription_diarized import TranscriptionDiarized


def get_transcription_response_format_type(
    response_format: AudioResponseFormat | Omit,
    *,
    log: logging.Logger,
) -> type[Transcription | TranscriptionVerbose | TranscriptionDiarized | str]:
    if isinstance(response_format, Omit) or response_format is None:  # pyright: ignore[reportUnnecessaryComparison]
        return Transcription

    if response_format == "json":
        return Transcription
    elif response_format == "verbose_json":
        return TranscriptionVerbose
    elif response_format == "diarized_json":
        return TranscriptionDiarized
    elif response_format == "srt" or response_format == "text" or response_format == "vtt":
        return str
    elif TYPE_CHECKING:  # type: ignore[unreachable]
        assert_never(response_format)
    else:
        log.warn("Unexpected audio response format: %s", response_format)
        return Transcription


def get_translation_response_format_type(
    response_format: AudioResponseFormat | Omit,
    *,
    log: logging.Logger,
) -> type[Translation | TranslationVerbose | str]:
    if isinstance(response_format, Omit) or response_format is None:  # pyright: ignore[reportUnnecessaryComparison]
        return Translation

    if response_format == "json":
        return Translation
    elif response_format == "verbose_json":
        return TranslationVerbose
    elif response_format == "srt" or response_format == "text" or response_format == "vtt":
        return str
    elif TYPE_CHECKING and response_format != "diarized_json":  # type: ignore[unreachable]
        assert_never(response_format)
    else:
        log.warning("Unexpected audio response format: %s", response_format)
        return Translation
