# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from ..responses.response_input_item import ResponseInputItem

__all__ = ["ResponseItemCreateEvent"]


class ResponseItemCreateEvent(BaseModel):
    """Add an input item to the Live session’s Responses backend.

    Requires Responses delegation; use `response.create` to request a response.
    """

    item: ResponseInputItem
    """
    An input item to append to the Responses backend conversation, such as a user
    message or a function tool result.
    """

    type: Literal["response.item.create"]
    """The Live client event type. Always `response.item.create`."""

    event_id: Optional[str] = None
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
