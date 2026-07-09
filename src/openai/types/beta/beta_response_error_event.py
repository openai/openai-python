# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaResponseErrorEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseErrorEvent(BaseModel):
    """Emitted when an error occurs."""

    code: Optional[str] = None
    """The error code."""

    message: str
    """The error message."""

    param: Optional[str] = None
    """The error parameter."""

    sequence_number: int
    """The sequence number of this event."""

    type: Literal["error"]
    """The type of the event. Always `error`."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
