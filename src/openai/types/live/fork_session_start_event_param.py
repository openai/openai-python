# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

from .fork_session_config_param import ForkSessionConfigParam

__all__ = ["ForkSessionStartEventParam"]


class ForkSessionStartEventParam(TypedDict, total=False):
    """Start a Live session after connecting to a stored session’s fork WebSocket.

    Send an empty `session` object to use the stored configuration.
    """

    session: Required[ForkSessionConfigParam]
    """Overrides for a stored session after connecting to the fork WebSocket.

    An empty object inherits the stored configuration; do not supply a new model.
    audio.format applies only to the new WebSocket connection. client overrides are
    only supported for WebRTC forks.
    """

    type: Required[Literal["session.start"]]
    """The Live client event type. Always `session.start`."""

    event_id: Optional[str]
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
