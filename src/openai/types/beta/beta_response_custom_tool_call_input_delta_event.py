# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaResponseCustomToolCallInputDeltaEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseCustomToolCallInputDeltaEvent(BaseModel):
    """Event representing a delta (partial update) to the input of a custom tool call."""

    delta: str
    """The incremental input data (delta) for the custom tool call."""

    item_id: str
    """Unique identifier for the API item associated with this event."""

    output_index: int
    """The index of the output this delta applies to."""

    sequence_number: int
    """The sequence number of this event."""

    type: Literal["response.custom_tool_call_input.delta"]
    """The event type identifier."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
