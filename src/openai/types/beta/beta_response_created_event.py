# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .beta_response import BetaResponse

__all__ = ["BetaResponseCreatedEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseCreatedEvent(BaseModel):
    """An event that is emitted when a response is created."""

    response: BetaResponse
    """The response that was created."""

    sequence_number: int
    """The sequence number for this event."""

    type: Literal["response.created"]
    """The type of the event. Always `response.created`."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
