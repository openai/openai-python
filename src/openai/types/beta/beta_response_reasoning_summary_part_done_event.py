# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaResponseReasoningSummaryPartDoneEvent", "Part", "Agent"]


class Part(BaseModel):
    """The completed summary part."""

    text: str
    """The text of the summary part."""

    type: Literal["summary_text"]
    """The type of the summary part. Always `summary_text`."""


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseReasoningSummaryPartDoneEvent(BaseModel):
    """Emitted when a reasoning summary part is completed."""

    item_id: str
    """The ID of the item this summary part is associated with."""

    output_index: int
    """The index of the output item this summary part is associated with."""

    part: Part
    """The completed summary part."""

    sequence_number: int
    """The sequence number of this event."""

    summary_index: int
    """The index of the summary part within the reasoning summary."""

    type: Literal["response.reasoning_summary_part.done"]
    """The type of the event. Always `response.reasoning_summary_part.done`."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""

    status: Optional[Literal["incomplete"]] = None
    """The completion status of the summary part.

    Omitted when the part completed normally and set to `incomplete` when generation
    was interrupted.
    """
