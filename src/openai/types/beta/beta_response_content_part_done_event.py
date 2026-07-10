# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .beta_response_output_text import BetaResponseOutputText
from .beta_response_output_refusal import BetaResponseOutputRefusal

__all__ = ["BetaResponseContentPartDoneEvent", "Part", "PartReasoningText", "Agent"]


class PartReasoningText(BaseModel):
    """Reasoning text from the model."""

    text: str
    """The reasoning text from the model."""

    type: Literal["reasoning_text"]
    """The type of the reasoning text. Always `reasoning_text`."""


Part: TypeAlias = Annotated[
    Union[BetaResponseOutputText, BetaResponseOutputRefusal, PartReasoningText], PropertyInfo(discriminator="type")
]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseContentPartDoneEvent(BaseModel):
    """Emitted when a content part is done."""

    content_index: int
    """The index of the content part that is done."""

    item_id: str
    """The ID of the output item that the content part was added to."""

    output_index: int
    """The index of the output item that the content part was added to."""

    part: Part
    """The content part that is done."""

    sequence_number: int
    """The sequence number of this event."""

    type: Literal["response.content_part.done"]
    """The type of the event. Always `response.content_part.done`."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
