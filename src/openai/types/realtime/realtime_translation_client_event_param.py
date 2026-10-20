# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import TypeAlias

from .realtime_translation_session_close_event_param import RealtimeTranslationSessionCloseEventParam
from .realtime_translation_session_update_event_param import RealtimeTranslationSessionUpdateEventParam
from .realtime_translation_input_audio_buffer_append_event_param import (
    RealtimeTranslationInputAudioBufferAppendEventParam,
)

__all__ = ["RealtimeTranslationClientEventParam"]

RealtimeTranslationClientEventParam: TypeAlias = Union[
    RealtimeTranslationSessionUpdateEventParam,
    RealtimeTranslationInputAudioBufferAppendEventParam,
    RealtimeTranslationSessionCloseEventParam,
]
