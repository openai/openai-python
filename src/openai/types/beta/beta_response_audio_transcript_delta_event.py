# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaResponseAudioTranscriptDeltaEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseAudioTranscriptDeltaEvent(BaseModel):
    """Emitted when there is a partial transcript of audio."""

    delta: str
    """The partial transcript of the audio response."""

    sequence_number: int
    """The sequence number of this event."""

    type: Literal["response.audio.transcript.delta"]
    """The type of the event. Always `response.audio.transcript.delta`."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
