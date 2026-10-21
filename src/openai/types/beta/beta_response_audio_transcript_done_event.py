# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaResponseAudioTranscriptDoneEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseAudioTranscriptDoneEvent(BaseModel):
    """Emitted when the full audio transcript is completed."""

    sequence_number: int
    """The sequence number of this event."""

    type: Literal["response.audio.transcript.done"]
    """The type of the event. Always `response.audio.transcript.done`."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
