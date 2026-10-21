# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .beta_response_output_text import BetaResponseOutputText
from .beta_response_output_refusal import BetaResponseOutputRefusal

__all__ = ["BetaResponseOutputMessage", "Content", "Agent"]

Content: TypeAlias = Annotated[
    Union[BetaResponseOutputText, BetaResponseOutputRefusal], PropertyInfo(discriminator="type")
]


class Agent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseOutputMessage(BaseModel):
    """An output message from the model."""

    id: str
    """The unique ID of the output message."""

    content: List[Content]
    """The content of the output message."""

    role: Literal["assistant"]
    """The role of the output message. Always `assistant`."""

    status: Literal["in_progress", "completed", "incomplete"]
    """The status of the message input.

    One of `in_progress`, `completed`, or `incomplete`. Populated when input items
    are returned via API.
    """

    type: Literal["message"]
    """The type of the output message. Always `message`."""

    agent: Optional[Agent] = None
    """The agent that produced this item."""

    phase: Optional[Literal["commentary", "final_answer"]] = None
    """
    Labels an `assistant` message as intermediate commentary (`commentary`) or the
    final answer (`final_answer`). For models like `gpt-5.3-codex` and beyond, when
    sending follow-up requests, preserve and resend phase on all assistant messages
    — dropping it can degrade performance. Not used for user messages.
    """
