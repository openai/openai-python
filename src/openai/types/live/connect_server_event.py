# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from .info_event import InfoEvent
from .error_event import ErrorEvent
from .response_event import ResponseEvent
from .session_closed_event import SessionClosedEvent
from .session_started_event import SessionStartedEvent
from .session_updated_event import SessionUpdatedEvent
from .input_audio_muted_event import InputAudioMutedEvent
from .thinking_appended_event import ThinkingAppendedEvent
from .delegation_created_event import DelegationCreatedEvent
from .commentary_appended_event import CommentaryAppendedEvent
from .input_audio_unmuted_event import InputAudioUnmutedEvent
from .instructions_appended_event import InstructionsAppendedEvent
from .session_usage_updated_event import SessionUsageUpdatedEvent
from .input_transcript_delta_event import InputTranscriptDeltaEvent
from .output_transcript_delta_event import OutputTranscriptDeltaEvent

__all__ = ["ConnectServerEvent"]

ConnectServerEvent: TypeAlias = Annotated[
    Union[
        SessionStartedEvent,
        SessionUpdatedEvent,
        InputAudioMutedEvent,
        InputAudioUnmutedEvent,
        InstructionsAppendedEvent,
        ThinkingAppendedEvent,
        CommentaryAppendedEvent,
        InputTranscriptDeltaEvent,
        OutputTranscriptDeltaEvent,
        DelegationCreatedEvent,
        ResponseEvent,
        SessionUsageUpdatedEvent,
        SessionClosedEvent,
        ErrorEvent,
        InfoEvent,
    ],
    PropertyInfo(discriminator="type"),
]
