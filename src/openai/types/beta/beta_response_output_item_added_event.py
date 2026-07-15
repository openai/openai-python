# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .beta_response_output_item import BetaResponseOutputItem

__all__ = ["BetaResponseOutputItemAddedEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseOutputItemAddedEvent(BaseModel):
    """Emitted when a new output item is added."""

    item: BetaResponseOutputItem
    """The output item that was added."""

    output_index: int
    """The index of the output item that was added."""

    sequence_number: int
    """The sequence number of this event."""

    type: Literal["response.output_item.added"]
    """The type of the event. Always `response.output_item.added`."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
