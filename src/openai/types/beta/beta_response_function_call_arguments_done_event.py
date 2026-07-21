# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaResponseFunctionCallArgumentsDoneEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseFunctionCallArgumentsDoneEvent(BaseModel):
    """Emitted when function-call arguments are finalized."""

    arguments: str
    """The function-call arguments."""

    item_id: str
    """The ID of the item."""

    output_index: int
    """The index of the output item."""

    sequence_number: int
    """The sequence number of this event."""

    type: Literal["response.function_call_arguments.done"]

    name: Optional[str] = None
    """The name of the function that was called.

    The live Responses API may omit this field on
    `response.function_call_arguments.done` events; correlate via `item_id` when
    absent.
    """

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
