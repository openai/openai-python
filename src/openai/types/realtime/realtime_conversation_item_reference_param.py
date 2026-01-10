# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["RealtimeConversationItemReferenceParam"]


class RealtimeConversationItemReferenceParam(TypedDict, total=False):
    """A reference to an existing conversation item in a Realtime prompt."""

    id: Required[str]
    """The unique ID of the conversation item being referenced."""

    type: Required[Literal["item_reference"]]
    """The type of the reference. Always `item_reference`."""
