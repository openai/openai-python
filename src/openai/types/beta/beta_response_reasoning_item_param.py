# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["BetaResponseReasoningItemParam", "Summary", "Agent", "Content"]


class Summary(TypedDict, total=False):
    """A summary text from the model."""

    text: Required[str]
    """A summary of the reasoning output from the model so far."""

    type: Required[Literal["summary_text"]]
    """The type of the object. Always `summary_text`."""


class Agent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class Content(TypedDict, total=False):
    """Reasoning text from the model."""

    text: Required[str]
    """The reasoning text from the model."""

    type: Required[Literal["reasoning_text"]]
    """The type of the reasoning text. Always `reasoning_text`."""


class BetaResponseReasoningItemParam(TypedDict, total=False):
    """
    A description of the chain of thought used by a reasoning model while generating
    a response. Be sure to include these items in your `input` to the Responses API
    for subsequent turns of a conversation if you are manually
    [managing context](https://platform.openai.com/docs/guides/conversation-state).
    """

    id: Required[str]
    """The unique identifier of the reasoning content."""

    summary: Required[Iterable[Summary]]
    """Reasoning summary content."""

    type: Required[Literal["reasoning"]]
    """The type of the object. Always `reasoning`."""

    agent: Optional[Agent]
    """The agent that produced this item."""

    content: Iterable[Content]
    """Reasoning text content."""

    encrypted_content: Optional[str]
    """The encrypted content of the reasoning item.

    This is populated by default for reasoning items returned by
    `POST /v1/responses` and WebSocket `response.create` requests.
    """

    status: Literal["in_progress", "completed", "incomplete"]
    """The status of the item.

    One of `in_progress`, `completed`, or `incomplete`. Populated when items are
    returned via API.
    """
