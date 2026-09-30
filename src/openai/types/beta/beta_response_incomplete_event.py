# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .beta_response import BetaResponse

__all__ = ["BetaResponseIncompleteEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseIncompleteEvent(BaseModel):
    """An event that is emitted when a response finishes as incomplete.

    Over WebSocket, steering can finish a response with
    `response.incomplete_details.reason` set to `steered`, followed automatically
    by a successor `response.created` that commits the queued steering input.
    """

    response: BetaResponse
    """The response that was incomplete."""

    sequence_number: int
    """The sequence number of this event."""

    type: Literal["response.incomplete"]
    """The type of the event. Always `response.incomplete`."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
