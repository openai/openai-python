# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import TypeAlias

from .session_close_event_param import SessionCloseEventParam
from .session_start_event_param import SessionStartEventParam
from .session_update_event_param import SessionUpdateEventParam
from .response_create_event_param import ResponseCreateEventParam
from .thinking_append_event_param import ThinkingAppendEventParam
from .input_audio_mute_event_param import InputAudioMuteEventParam
from .commentary_append_event_param import CommentaryAppendEventParam
from .input_audio_append_event_param import InputAudioAppendEventParam
from .input_audio_unmute_event_param import InputAudioUnmuteEventParam
from .instructions_append_event_param import InstructionsAppendEventParam
from .response_item_create_event_param import ResponseItemCreateEventParam

__all__ = ["ClientEventParam"]

ClientEventParam: TypeAlias = Union[
    SessionStartEventParam,
    SessionUpdateEventParam,
    InputAudioAppendEventParam,
    InputAudioMuteEventParam,
    InputAudioUnmuteEventParam,
    InstructionsAppendEventParam,
    ThinkingAppendEventParam,
    CommentaryAppendEventParam,
    ResponseItemCreateEventParam,
    ResponseCreateEventParam,
    SessionCloseEventParam,
]
