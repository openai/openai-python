# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaResponseCompactionCompactingEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseCompactionCompactingEvent(BaseModel):
    """Emitted when new summary content is sampled for a compaction trigger.

    Contains no summary content.
    """

    item_id: str
    """The ID of the compaction output item."""

    output_index: int
    """The index of the compaction output item."""

    sequence_number: int
    """The sequence number of the event that was emitted."""

    type: Literal["response.compaction.compacting"]
    """The type of the event, always `response.compaction.compacting`."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
