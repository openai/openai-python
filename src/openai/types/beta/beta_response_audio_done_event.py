# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaResponseAudioDoneEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseAudioDoneEvent(BaseModel):
    """Emitted when the audio response is complete."""

    sequence_number: int
    """The sequence number of the delta."""

    type: Literal["response.audio.done"]
    """The type of the event. Always `response.audio.done`."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
