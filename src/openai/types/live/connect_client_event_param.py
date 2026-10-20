# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import TypeAlias

from .session_close_event_param import SessionCloseEventParam
from .session_update_event_param import SessionUpdateEventParam
from .decision_create_event_param import DecisionCreateEventParam
from .response_create_event_param import ResponseCreateEventParam
from .thinking_append_event_param import ThinkingAppendEventParam
from .input_audio_mute_event_param import InputAudioMuteEventParam
from .commentary_append_event_param import CommentaryAppendEventParam
from .input_audio_unmute_event_param import InputAudioUnmuteEventParam
from .instructions_append_event_param import InstructionsAppendEventParam
from .decision_item_create_event_param import DecisionItemCreateEventParam
from .decision_item_delete_event_param import DecisionItemDeleteEventParam
from .response_item_create_event_param import ResponseItemCreateEventParam
from .output_audio_fixture_play_event_param import OutputAudioFixturePlayEventParam

__all__ = ["ConnectClientEventParam"]

ConnectClientEventParam: TypeAlias = Union[
    SessionUpdateEventParam,
    InputAudioMuteEventParam,
    InputAudioUnmuteEventParam,
    OutputAudioFixturePlayEventParam,
    InstructionsAppendEventParam,
    ThinkingAppendEventParam,
    CommentaryAppendEventParam,
    DecisionCreateEventParam,
    DecisionItemCreateEventParam,
    DecisionItemDeleteEventParam,
    ResponseItemCreateEventParam,
    ResponseCreateEventParam,
    SessionCloseEventParam,
]
