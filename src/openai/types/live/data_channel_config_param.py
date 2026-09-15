# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, TypedDict

from ..._types import SequenceNotStr
from .server_event_selector_param import ServerEventSelectorParam

__all__ = ["DataChannelConfigParam"]


class DataChannelConfigParam(TypedDict, total=False):
    """
    Control which Live events an untrusted WebRTC frontend can send and receive over its data channel. These restrictions do not apply to trusted sideband connections.
    """

    allowed_client_events: Union[Literal["all"], SequenceNotStr[str]]
    """Client event types that the frontend data channel may send.

    Use 'all' to allow every client event; an empty array allows none. Omission
    preserves the existing allow-all behavior.
    """

    allowed_server_events: Union[Literal["all"], Iterable[ServerEventSelectorParam]]
    """Server events that may be sent to the frontend data channel.

    Use 'all' to allow every server event; an empty array allows none. Omission
    preserves the existing allow-all behavior. Responses events use an object with
    type 'response.event' and a response_event selector.
    """
