# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

from .session_config_param import SessionConfigParam

__all__ = ["SessionStartEventParam"]


class SessionStartEventParam(TypedDict, total=False):
    """Start a Live session on a primary WebSocket.

    Send this event before other commands and wait for `session.started`.
    """

    session: Required[SessionConfigParam]
    """Initial configuration for a primary WebSocket.

    Send session.start first and wait for session.started before application
    commands. WebRTC creation already starts the session; do not send this event
    again on its data channel.
    """

    type: Required[Literal["session.start"]]
    """The Live client event type. Always `session.start`."""

    event_id: Optional[str]
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
