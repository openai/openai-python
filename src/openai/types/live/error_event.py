# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .error import Error
from ..._models import BaseModel

__all__ = ["ErrorEvent"]


class ErrorEvent(BaseModel):
    """Reports an error in the Live session, such as an invalid client command.

    Use error.client_event_id, when present, to identify the command that caused the error.
    """

    error: Error
    """Details of the Live error and the client command that caused it, when known."""

    event_id: str
    """The unique ID of the Live server event."""

    type: Literal["error"]
    """The event type, always `error`."""

    client_event_id: Optional[str] = None
    """
    The event_id of the client command associated with this server event, when
    supplied.
    """
