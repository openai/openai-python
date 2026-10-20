# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["CommentaryAppendedEvent"]


class CommentaryAppendedEvent(BaseModel):
    """
    Returned when a session.commentary.append command is accepted into the Live session timeline. Acknowledges the added commentary without guaranteeing exact wording or completed audio playback.
    """

    end_ms: int
    """
    The end of this event on the Live session timeline, in milliseconds from the
    beginning of the session. For appended context, this can equal start_ms.
    """

    event_id: str
    """The unique ID of the Live server event."""

    start_ms: int
    """
    The start of this event on the Live session timeline, in milliseconds from the
    beginning of the session.
    """

    type: Literal["session.commentary.appended"]
    """The event type, always `session.commentary.appended`."""

    client_event_id: Optional[str] = None
    """
    The event_id of the client command associated with this server event, when
    supplied.
    """
