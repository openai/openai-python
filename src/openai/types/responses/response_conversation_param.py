# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["ResponseConversationParam"]


class ResponseConversationParam(BaseModel):
    """The conversation that this response belongs to."""

    id: str
    """The unique ID of the conversation."""
