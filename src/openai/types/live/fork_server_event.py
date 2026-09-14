# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .info_event import InfoEvent
from .error_event import ErrorEvent
from .response_event import ResponseEvent
from .session_closed_event import SessionClosedEvent
from .session_started_event import SessionStartedEvent
from .session_updated_event import SessionUpdatedEvent
from .input_audio_muted_event import InputAudioMutedEvent
from .thinking_appended_event import ThinkingAppendedEvent
from .delegation_created_event import DelegationCreatedEvent
from .output_audio_delta_event import OutputAudioDeltaEvent
from .commentary_appended_event import CommentaryAppendedEvent
from .input_audio_unmuted_event import InputAudioUnmutedEvent
from .instructions_appended_event import InstructionsAppendedEvent
from .session_usage_updated_event import SessionUsageUpdatedEvent
from .input_transcript_delta_event import InputTranscriptDeltaEvent
from .output_transcript_delta_event import OutputTranscriptDeltaEvent

__all__ = [
    "ForkServerEvent",
    "SessionInputAudioAppend",
    "TransportDtmfReceived",
    "TransportDtmfSend",
    "TransportRinging",
    "TransportAnswered",
    "TransportFailed",
    "TransportFailedError",
]


class SessionInputAudioAppend(BaseModel):
    """
    Input audio received from the primary transport and reflected to a Live sideband connection before model-input muting.
    """

    audio: str
    """
    Base64-encoded raw mono PCM16LE at 24 kHz received from the primary transport,
    reflected to the sideband before model-input muting. This server event uses the
    same audio key as the client command, but is not an acknowledgment of it.
    """

    type: Literal["session.input_audio.append"]
    """The event type, always `session.input_audio.append`."""


class TransportDtmfReceived(BaseModel):
    """A SIP DTMF keypress received from the caller.

    Delivered only to sideband observers.
    """

    event: str

    event_id: str

    type: Literal["transport.dtmf.received"]


class TransportDtmfSend(BaseModel):
    """A SIP DTMF keypress successfully sent by the hosted tool.

    Delivered only to sideband observers; this is not a client command.
    """

    event: str

    event_id: str

    type: Literal["transport.dtmf.send"]


class TransportRinging(BaseModel):
    """The outbound SIP provider leg is ringing or providing early media.

    Delivered only to sideband observers.
    """

    event_id: str

    session_id: str
    """The canonical Live session ID."""

    type: Literal["transport.ringing"]


class TransportAnswered(BaseModel):
    """The outbound SIP provider leg answered and media is established.

    Delivered only to sideband observers.
    """

    event_id: str

    session_id: str
    """The canonical Live session ID."""

    type: Literal["transport.answered"]


class TransportFailedError(BaseModel):
    code: str
    """The call setup failure code."""

    message: str

    type: Literal["call_error"]

    param: Optional[str] = None
    """The parameter related to the error, if any. Empty when no parameter applies."""


class TransportFailed(BaseModel):
    """An asynchronous outbound SIP setup failure.

    Delivered only to sideband observers.
    """

    error: TransportFailedError

    event_id: str

    session_id: str
    """The canonical Live session ID."""

    type: Literal["transport.failed"]


ForkServerEvent: TypeAlias = Annotated[
    Union[
        SessionStartedEvent,
        SessionUpdatedEvent,
        InputAudioMutedEvent,
        InputAudioUnmutedEvent,
        InstructionsAppendedEvent,
        ThinkingAppendedEvent,
        CommentaryAppendedEvent,
        SessionInputAudioAppend,
        OutputAudioDeltaEvent,
        InputTranscriptDeltaEvent,
        OutputTranscriptDeltaEvent,
        DelegationCreatedEvent,
        ResponseEvent,
        SessionUsageUpdatedEvent,
        SessionClosedEvent,
        ErrorEvent,
        InfoEvent,
        TransportDtmfReceived,
        TransportDtmfSend,
        TransportRinging,
        TransportAnswered,
        TransportFailed,
    ],
    PropertyInfo(discriminator="type"),
]
