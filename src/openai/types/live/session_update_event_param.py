# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

from .session_update_config_param import SessionUpdateConfigParam

__all__ = ["SessionUpdateEventParam"]


class SessionUpdateEventParam(TypedDict, total=False):
    """Update the delegation settings of an active Live session.

    The server acknowledges accepted changes with `session.updated`.
    """

    session: Required[SessionUpdateConfigParam]
    """Sparse delegation updates.

    Omitted settings retain their values. The delegation type cannot change,
    including resetting Responses delegation to null or client. Model, frontend
    instructions, audio, and startup input are immutable.
    """

    type: Required[Literal["session.update"]]
    """The Live client event type. Always `session.update`."""

    event_id: Optional[str]
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
