# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import Literal

from ..._models import BaseModel
from .server_event_selector import ServerEventSelector

__all__ = ["DataChannelConfig"]


class DataChannelConfig(BaseModel):
    """
    Control which Live events an untrusted WebRTC frontend can send and receive over its data channel. These restrictions do not apply to trusted sideband connections.
    """

    allowed_client_events: Union[Literal["all"], List[str], None] = None
    """Client event types that the frontend data channel may send.

    Use 'all' to allow every client event; an empty array allows none. Omission
    preserves the existing allow-all behavior.
    """

    allowed_server_events: Union[Literal["all"], List[ServerEventSelector], None] = None
    """Server events that may be sent to the frontend data channel.

    Use 'all' to allow every server event; an empty array allows none. Omission
    preserves the existing allow-all behavior. Responses events use an object with
    type 'response.event' and a response_event selector.
    """
