# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from .session_close_event import SessionCloseEvent
from .session_update_event import SessionUpdateEvent
from .decision_create_event import DecisionCreateEvent
from .response_create_event import ResponseCreateEvent
from .thinking_append_event import ThinkingAppendEvent
from .input_audio_mute_event import InputAudioMuteEvent
from .commentary_append_event import CommentaryAppendEvent
from .input_audio_unmute_event import InputAudioUnmuteEvent
from .instructions_append_event import InstructionsAppendEvent
from .decision_item_create_event import DecisionItemCreateEvent
from .decision_item_delete_event import DecisionItemDeleteEvent
from .response_item_create_event import ResponseItemCreateEvent
from .output_audio_fixture_play_event import OutputAudioFixturePlayEvent

__all__ = ["ConnectClientEvent"]

ConnectClientEvent: TypeAlias = Annotated[
    Union[
        SessionUpdateEvent,
        InputAudioMuteEvent,
        InputAudioUnmuteEvent,
        OutputAudioFixturePlayEvent,
        InstructionsAppendEvent,
        ThinkingAppendEvent,
        CommentaryAppendEvent,
        DecisionCreateEvent,
        DecisionItemCreateEvent,
        DecisionItemDeleteEvent,
        ResponseItemCreateEvent,
        ResponseCreateEvent,
        SessionCloseEvent,
    ],
    PropertyInfo(discriminator="type"),
]
