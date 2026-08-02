# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .beta_response import BetaResponse

__all__ = ["BetaResponseCompletedEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseCompletedEvent(BaseModel):
    """Emitted when the model response is complete."""

    response: BetaResponse
    """Properties of the completed response."""

    sequence_number: int
    """The sequence number for this event."""

    type: Literal["response.completed"]
    """The type of the event. Always `response.completed`."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
