# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaResponseMcpListToolsInProgressEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseMcpListToolsInProgressEvent(BaseModel):
    """
    Emitted when the system is in the process of retrieving the list of available MCP tools.
    """

    item_id: str
    """The ID of the MCP tool call item that is being processed."""

    output_index: int
    """The index of the output item that is being processed."""

    sequence_number: int
    """The sequence number of this event."""

    type: Literal["response.mcp_list_tools.in_progress"]
    """The type of the event. Always 'response.mcp_list_tools.in_progress'."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
