# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Any, Dict, List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseReasoningItem", "Summary", "Content"]


class Summary(BaseModel):
    """A summary text from the model."""

    text: str
    """A summary of the reasoning output from the model so far."""

    type: Literal["summary_text"]
    """The type of the object. Always `summary_text`."""


class Content(BaseModel):
    """Reasoning text from the model."""

    text: str
    """The reasoning text from the model."""

    type: Literal["reasoning_text"]
    """The type of the reasoning text. Always `reasoning_text`."""


class ResponseReasoningItem(BaseModel):
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

    content: Optional[List[Content]] = None
    """Reasoning text content."""

    encrypted_content: Optional[str] = None
    """
    The encrypted content of the reasoning item - populated when a response is
    generated with `reasoning.encrypted_content` in the `include` parameter.
    """

    status: Optional[Literal["in_progress", "completed", "incomplete"]] = None
    """The status of the item.

    One of `in_progress`, `completed`, or `incomplete`. Populated when items are
    returned via API.
    """

    def as_input(self) -> Dict[str, Any]:
        """Return a dict representation of this item suitable for use as input in a subsequent response.

        This strips output-only fields (``status``, ``encrypted_content``) that the
        API does not accept as input.
        """
        data = self.to_dict()
        data.pop("status", None)
        data.pop("encrypted_content", None)
        return data
