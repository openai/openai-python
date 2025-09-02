# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["RealtimeConversationItemFunctionCallParam"]


class RealtimeConversationItemFunctionCallParam(TypedDict, total=False):
    arguments: Required[str]
    """The arguments of the function call."""

    name: Required[str]
    """The name of the function being called."""

    type: Required[Literal["function_call"]]
    """The type of the item. Always `function_call`."""

    id: str
    """The unique ID of the item."""

    call_id: str
    """The ID of the function call."""

    object: Literal["realtime.item"]
    """Identifier for the API object being returned - always `realtime.item`."""

    status: Literal["completed", "incomplete", "in_progress"]
    """The status of the item. Has no effect on the conversation."""
