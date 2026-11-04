# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from .realtime_error_event import RealtimeErrorEvent
from .realtime_translation_session_closed_event import RealtimeTranslationSessionClosedEvent
from .realtime_translation_session_created_event import RealtimeTranslationSessionCreatedEvent
from .realtime_translation_session_updated_event import RealtimeTranslationSessionUpdatedEvent
from .realtime_translation_output_audio_delta_event import RealtimeTranslationOutputAudioDeltaEvent
from .realtime_translation_input_transcript_delta_event import RealtimeTranslationInputTranscriptDeltaEvent
from .realtime_translation_output_transcript_delta_event import RealtimeTranslationOutputTranscriptDeltaEvent

__all__ = ["RealtimeTranslationServerEvent"]

RealtimeTranslationServerEvent: TypeAlias = Annotated[
    Union[
        RealtimeErrorEvent,
        RealtimeTranslationSessionCreatedEvent,
        RealtimeTranslationSessionUpdatedEvent,
        RealtimeTranslationSessionClosedEvent,
        RealtimeTranslationInputTranscriptDeltaEvent,
        RealtimeTranslationOutputTranscriptDeltaEvent,
        RealtimeTranslationOutputAudioDeltaEvent,
    ],
    PropertyInfo(discriminator="type"),
]
