# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaResponseAudioDeltaEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseAudioDeltaEvent(BaseModel):
    """Emitted when there is a partial audio response."""

    delta: str
    """A chunk of Base64 encoded response audio bytes."""

    sequence_number: int
    """A sequence number for this chunk of the stream response."""

    type: Literal["response.audio.delta"]
    """The type of the event. Always `response.audio.delta`."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
