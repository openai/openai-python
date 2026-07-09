# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaResponseImageGenCallInProgressEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseImageGenCallInProgressEvent(BaseModel):
    """Emitted when an image generation tool call is in progress."""

    item_id: str
    """The unique identifier of the image generation item being processed."""

    output_index: int
    """The index of the output item in the response's output array."""

    sequence_number: int
    """The sequence number of the image generation item being processed."""

    type: Literal["response.image_generation_call.in_progress"]
    """The type of the event. Always 'response.image_generation_call.in_progress'."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
