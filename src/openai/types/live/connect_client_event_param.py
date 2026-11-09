# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

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

__all__ = ["ConnectClientEventParam", "TransportDtmfSend"]


class TransportDtmfSend(TypedDict, total=False):
    """Send one DTMF keypress to the SIP trunk through a Live sideband connection.

    This command is supported only for SIP calls. A successful send emits `transport.dtmf.sent` on sideband. If you provide `event_id`, the success notification includes it as `client_event_id`; a failure includes it as `error.client_event_id`. Send separate events for multiple keypresses.
    """

    event: Required[str]
    """The DTMF key to send: one of `0`–`9`, `A`–`D`, `*`, or `#`."""

    type: Required[Literal["transport.dtmf.send"]]

    event_id: Optional[str]
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """


ConnectClientEventParam: TypeAlias = Union[
    SessionUpdateEventParam,
    InputAudioMuteEventParam,
    InputAudioUnmuteEventParam,
    OutputAudioFixturePlayEventParam,
    TransportDtmfSend,
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
