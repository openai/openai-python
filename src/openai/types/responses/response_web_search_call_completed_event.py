# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseWebSearchCallCompletedEvent"]


class ResponseWebSearchCallCompletedEvent(BaseModel):
    item_id: str
    """Unique ID for the output item associated with the web search call."""

    output_index: int
    """The index of the output item that the web search call is associated with."""

    type: Literal["response.web_search_call.completed"]
    """The type of the event. Always `response.web_search_call.completed`."""
