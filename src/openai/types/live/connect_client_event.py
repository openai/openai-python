# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from .session_close_event import SessionCloseEvent
from .session_update_event import SessionUpdateEvent
from .response_create_event import ResponseCreateEvent
from .thinking_append_event import ThinkingAppendEvent
from .input_audio_mute_event import InputAudioMuteEvent
from .commentary_append_event import CommentaryAppendEvent
from .input_audio_unmute_event import InputAudioUnmuteEvent
from .instructions_append_event import InstructionsAppendEvent
from .response_item_create_event import ResponseItemCreateEvent

__all__ = ["ConnectClientEvent"]

ConnectClientEvent: TypeAlias = Annotated[
    Union[
        SessionUpdateEvent,
        InputAudioMuteEvent,
        InputAudioUnmuteEvent,
        InstructionsAppendEvent,
        ThinkingAppendEvent,
        CommentaryAppendEvent,
        ResponseItemCreateEvent,
        ResponseCreateEvent,
        SessionCloseEvent,
    ],
    PropertyInfo(discriminator="type"),
]
