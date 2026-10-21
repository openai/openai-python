# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaResponseCustomToolCallInputDoneEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseCustomToolCallInputDoneEvent(BaseModel):
    """Event indicating that input for a custom tool call is complete."""

    input: str
    """The complete input data for the custom tool call."""

    item_id: str
    """Unique identifier for the API item associated with this event."""

    output_index: int
    """The index of the output this event applies to."""

    sequence_number: int
    """The sequence number of this event."""

    type: Literal["response.custom_tool_call_input.done"]
    """The event type identifier."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
