# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["ResponseCreateEventParam"]


class ResponseCreateEventParam(TypedDict, total=False):
    """
    Request a response from the Live session’s Responses backend, or continue a delegated response waiting for tool results. Requires Responses delegation.
    """

    type: Required[Literal["response.create"]]
    """The Live client event type. Always `response.create`."""

    event_id: Optional[str]
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
