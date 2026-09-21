# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ServerEventSelectorParam"]


class ServerEventSelectorParam(TypedDict, total=False):
    """A Live server event selector for the WebRTC frontend data channel."""

    type: Required[str]
    """The outer Live server event type. Use 'response.event' for Responses events."""

    response_event: str
    """The nested Responses event type.

    Required when type is 'response.event'; forbidden for other event types.
    """
