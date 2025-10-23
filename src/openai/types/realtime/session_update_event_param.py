# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .realtime_session_create_request_param import RealtimeSessionCreateRequestParam
from .realtime_transcription_session_create_request_param import RealtimeTranscriptionSessionCreateRequestParam

__all__ = ["SessionUpdateEventParam", "Session"]

Session: TypeAlias = Union[RealtimeSessionCreateRequestParam, RealtimeTranscriptionSessionCreateRequestParam]


class SessionUpdateEventParam(TypedDict, total=False):
    session: Required[Session]
    """Update the Realtime session.

    Choose either a realtime session or a transcription session.
    """

    type: Required[Literal["session.update"]]
    """The event type, must be `session.update`."""

    event_id: str
    """Optional client-generated ID used to identify this event.

    This is an arbitrary string that a client may assign. It will be passed back if
    there is an error with the event, but the corresponding `session.updated` event
    will not include it.
    """
