# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from .info_event import InfoEvent
from .error_event import ErrorEvent
from .decision_event import DecisionEvent
from .response_event import ResponseEvent
from .session_closed_event import SessionClosedEvent
from .session_started_event import SessionStartedEvent
from .session_updated_event import SessionUpdatedEvent
from .input_audio_muted_event import InputAudioMutedEvent
from .thinking_appended_event import ThinkingAppendedEvent
from .delegation_created_event import DelegationCreatedEvent
from .commentary_appended_event import CommentaryAppendedEvent
from .input_audio_unmuted_event import InputAudioUnmutedEvent
from .decision_item_created_event import DecisionItemCreatedEvent
from .decision_item_deleted_event import DecisionItemDeletedEvent
from .instructions_appended_event import InstructionsAppendedEvent
from .session_usage_updated_event import SessionUsageUpdatedEvent
from .input_transcript_delta_event import InputTranscriptDeltaEvent
from .output_transcript_delta_event import OutputTranscriptDeltaEvent
from .output_audio_fixture_played_event import OutputAudioFixturePlayedEvent
from .output_audio_fixture_playing_event import OutputAudioFixturePlayingEvent

__all__ = ["ConnectServerEvent"]

ConnectServerEvent: TypeAlias = Annotated[
    Union[
        SessionStartedEvent,
        SessionUpdatedEvent,
        InputAudioMutedEvent,
        InputAudioUnmutedEvent,
        OutputAudioFixturePlayingEvent,
        OutputAudioFixturePlayedEvent,
        InstructionsAppendedEvent,
        ThinkingAppendedEvent,
        CommentaryAppendedEvent,
        InputTranscriptDeltaEvent,
        OutputTranscriptDeltaEvent,
        DelegationCreatedEvent,
        DecisionEvent,
        DecisionItemCreatedEvent,
        DecisionItemDeletedEvent,
        ResponseEvent,
        SessionUsageUpdatedEvent,
        SessionClosedEvent,
        ErrorEvent,
        InfoEvent,
    ],
    PropertyInfo(discriminator="type"),
]
