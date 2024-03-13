# File generated from our OpenAPI spec by Stainless.

from typing import Optional
from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["RetrievalToolCallDelta"]


class RetrievalToolCallDelta(BaseModel):
    index: int
    """The index of the tool call in the tool calls array."""

    type: Literal["retrieval"]
    """The type of tool call.

    This is always going to be `retrieval` for this type of tool call.
    """

    id: Optional[str] = None
    """The ID of the tool call object."""

    retrieval: Optional[object] = None
    """For now, this is always going to be an empty object."""
