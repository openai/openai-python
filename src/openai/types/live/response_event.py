# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseEvent"]


class ResponseEvent(BaseModel):
    """A streaming Responses API event from a backend delegated to by the Live session.

    Use the outer delegation_id to associate the nested stream with its Live delegation.
    """

    event: Dict[str, object]
    """The nested Responses streaming event.

    Dispatch on its type field. Response lifecycle snapshots omit input and clear
    instructions, tools, and output to keep messages small; consume granular output
    events for the generated content.
    """

    event_id: str
    """The unique ID of the Live server event."""

    type: Literal["response.event"]
    """The event type, always `response.event`."""

    client_event_id: Optional[str] = None
    """
    The event_id of the client command associated with this server event, when
    supplied.
    """

    delegation_id: Optional[str] = None
    """The Live delegation associated with the nested Responses event.

    May be null or omitted when the event cannot be correlated with a delegation.
    """
