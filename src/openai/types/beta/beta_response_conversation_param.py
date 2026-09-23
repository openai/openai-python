# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["BetaResponseConversationParam"]


class BetaResponseConversationParam(BaseModel):
    """The conversation that this response belongs to."""

    id: str
    """The unique ID of the conversation."""
