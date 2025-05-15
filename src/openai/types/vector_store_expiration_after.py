# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["VectorStoreExpirationAfter"]


class VectorStoreExpirationAfter(BaseModel):
    anchor: Literal["last_active_at"]
    """Anchor timestamp after which the expiration policy applies.

    Supported anchors: `last_active_at`.
    """

    days: int
    """The number of days after the anchor time that the vector store will expire."""
