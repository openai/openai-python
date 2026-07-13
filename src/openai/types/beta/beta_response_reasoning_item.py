# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaResponseReasoningItem", "Summary", "Agent", "Content"]


class Summary(BaseModel):
    """A summary text from the model."""

    text: str
    """A summary of the reasoning output from the model so far."""

    type: Literal["summary_text"]
    """The type of the object. Always `summary_text`."""


class Agent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class Content(BaseModel):
    """Reasoning text from the model."""

    text: str
    """The reasoning text from the model."""

    type: Literal["reasoning_text"]
    """The type of the reasoning text. Always `reasoning_text`."""


class BetaResponseReasoningItem(BaseModel):
    """
    A description of the chain of thought used by a reasoning model while generating
    a response. Be sure to include these items in your `input` to the Responses API
    for subsequent turns of a conversation if you are manually
    [managing context](https://platform.openai.com/docs/guides/conversation-state).
    """

    id: str
    """The unique identifier of the reasoning content."""

    summary: List[Summary]
    """Reasoning summary content."""

    type: Literal["reasoning"]
    """The type of the object. Always `reasoning`."""

    agent: Optional[Agent] = None
    """The agent that produced this item."""

    content: Optional[List[Content]] = None
    """Reasoning text content."""

    encrypted_content: Optional[str] = None
    """The encrypted content of the reasoning item.

    This is populated by default for reasoning items returned by
    `POST /v1/responses` and WebSocket `response.create` requests.
    """

    status: Optional[Literal["in_progress", "completed", "incomplete"]] = None
    """The status of the item.

    One of `in_progress`, `completed`, or `incomplete`. Populated when items are
    returned via API.
    """
