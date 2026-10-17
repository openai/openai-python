# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from .realtime_translation_session_close_event import RealtimeTranslationSessionCloseEvent
from .realtime_translation_session_update_event import RealtimeTranslationSessionUpdateEvent
from .realtime_translation_input_audio_buffer_append_event import RealtimeTranslationInputAudioBufferAppendEvent

__all__ = ["RealtimeTranslationClientEvent"]

RealtimeTranslationClientEvent: TypeAlias = Annotated[
    Union[
        RealtimeTranslationSessionUpdateEvent,
        RealtimeTranslationInputAudioBufferAppendEvent,
        RealtimeTranslationSessionCloseEvent,
    ],
    PropertyInfo(discriminator="type"),
]
