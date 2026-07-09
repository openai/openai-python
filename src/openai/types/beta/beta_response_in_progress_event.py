# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .beta_response import BetaResponse

__all__ = ["BetaResponseInProgressEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseInProgressEvent(BaseModel):
    """Emitted when the response is in progress."""

    response: BetaResponse
    """The response that is in progress."""

    sequence_number: int
    """The sequence number of this event."""

    type: Literal["response.in_progress"]
    """The type of the event. Always `response.in_progress`."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
