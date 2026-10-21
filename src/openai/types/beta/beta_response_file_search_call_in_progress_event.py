# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaResponseFileSearchCallInProgressEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseFileSearchCallInProgressEvent(BaseModel):
    """Emitted when a file search call is initiated."""

    item_id: str
    """The ID of the output item that the file search call is initiated."""

    output_index: int
    """The index of the output item that the file search call is initiated."""

    sequence_number: int
    """The sequence number of this event."""

    type: Literal["response.file_search_call.in_progress"]
    """The type of the event. Always `response.file_search_call.in_progress`."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
