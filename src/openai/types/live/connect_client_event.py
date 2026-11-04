# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
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

__all__ = ["ConnectClientEvent", "TransportDtmfSend"]


class TransportDtmfSend(BaseModel):
    """Send one DTMF keypress to the SIP trunk through a Live sideband connection.

    This command is supported only for SIP calls. A successful send emits `transport.dtmf.sent` on sideband. If you provide `event_id`, the success notification includes it as `client_event_id`; a failure includes it as `error.client_event_id`. Send separate events for multiple keypresses.
    """

    event: str
    """The DTMF key to send: one of `0`–`9`, `A`–`D`, `*`, or `#`."""

    type: Literal["transport.dtmf.send"]

    event_id: Optional[str] = None
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """


ConnectClientEvent: TypeAlias = Annotated[
    Union[
        SessionUpdateEvent,
        InputAudioMuteEvent,
        InputAudioUnmuteEvent,
        OutputAudioFixturePlayEvent,
        TransportDtmfSend,
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
