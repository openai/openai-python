# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .beta_response import BetaResponse

__all__ = ["BetaResponseQueuedEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseQueuedEvent(BaseModel):
    """Emitted when a response is queued and waiting to be processed."""

    response: BetaResponse
    """The full response object that is queued."""

    sequence_number: int
    """The sequence number for this event."""

    type: Literal["response.queued"]
    """The type of the event. Always 'response.queued'."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
