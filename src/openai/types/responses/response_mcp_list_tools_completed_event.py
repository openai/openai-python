# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseMcpListToolsCompletedEvent"]


class ResponseMcpListToolsCompletedEvent(BaseModel):
    sequence_number: int
    """The sequence number of this event."""

    type: Literal["response.mcp_list_tools.completed"]
    """The type of the event. Always 'response.mcp_list_tools.completed'."""
