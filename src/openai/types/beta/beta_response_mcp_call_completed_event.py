# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaResponseMcpCallCompletedEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseMcpCallCompletedEvent(BaseModel):
    """Emitted when an MCP  tool call has completed successfully."""

    item_id: str
    """The ID of the MCP tool call item that completed."""

    output_index: int
    """The index of the output item that completed."""

    sequence_number: int
    """The sequence number of this event."""

    type: Literal["response.mcp_call.completed"]
    """The type of the event. Always 'response.mcp_call.completed'."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
