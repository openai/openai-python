# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .beta_response_input_message_content_list import BetaResponseInputMessageContentList

__all__ = ["BetaResponseInputMessageItem", "Agent"]


class Agent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseInputMessageItem(BaseModel):
    id: str
    """The unique ID of the message input."""

    content: BetaResponseInputMessageContentList
    """
    A list of one or many input items to the model, containing different content
    types.
    """

    role: Literal["user", "system", "developer"]
    """The role of the message input. One of `user`, `system`, or `developer`."""

    type: Literal["message"]
    """The type of the message input. Always set to `message`."""

    agent: Optional[Agent] = None
    """The agent that produced this item."""

    status: Optional[Literal["in_progress", "completed", "incomplete"]] = None
    """The status of item.

    One of `in_progress`, `completed`, or `incomplete`. Populated when items are
    returned via API.
    """
