# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .realtime_session_create_request_param import RealtimeSessionCreateRequestParam

__all__ = ["SessionUpdateEventParam"]


class SessionUpdateEventParam(TypedDict, total=False):
    session: Required[RealtimeSessionCreateRequestParam]
    """Realtime session object configuration."""

    type: Required[Literal["session.update"]]
    """The event type, must be `session.update`."""

    event_id: str
    """Optional client-generated ID used to identify this event."""
