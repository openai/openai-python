# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["VectorStoreExpirationAfterParam"]


class VectorStoreExpirationAfterParam(TypedDict, total=False):
    anchor: Required[Literal["last_active_at"]]
    """Anchor timestamp after which the expiration policy applies.

    Supported anchors: `last_active_at`.
    """

    days: Required[int]
    """The number of days after the anchor time that the vector store will expire."""
