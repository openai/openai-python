# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .beta_response import BetaResponse

__all__ = ["BetaResponseFailedEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseFailedEvent(BaseModel):
    """An event that is emitted when a response fails."""

    response: BetaResponse
    """The response that failed."""

    sequence_number: int
    """The sequence number of this event."""

    type: Literal["response.failed"]
    """The type of the event. Always `response.failed`."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
