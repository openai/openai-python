# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

from ..responses.response_input_item_param import ResponseInputItemParam

__all__ = ["ResponseItemCreateEventParam"]


class ResponseItemCreateEventParam(TypedDict, total=False):
    """Add an input item to the Live session’s Responses backend.

    Requires Responses delegation; use `response.create` to request a response.
    """

    item: Required[ResponseInputItemParam]
    """
    An input item to append to the Responses backend conversation, such as a user
    message or a function tool result.
    """

    type: Required[Literal["response.item.create"]]
    """The Live client event type. Always `response.item.create`."""

    event_id: Optional[str]
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
