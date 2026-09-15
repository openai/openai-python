# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseCreateEvent"]


class ResponseCreateEvent(BaseModel):
    """
    Request a response from the Live session’s Responses backend, or continue a delegated response waiting for tool results. Requires Responses delegation.
    """

    type: Literal["response.create"]
    """The Live client event type. Always `response.create`."""

    event_id: Optional[str] = None
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
