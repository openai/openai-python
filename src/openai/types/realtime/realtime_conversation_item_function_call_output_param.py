# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["RealtimeConversationItemFunctionCallOutputParam"]


class RealtimeConversationItemFunctionCallOutputParam(TypedDict, total=False):
    call_id: Required[str]
    """The ID of the function call this output is for."""

    output: Required[str]
    """The output of the function call."""

    type: Required[Literal["function_call_output"]]
    """The type of the item. Always `function_call_output`."""

    id: str
    """The unique ID of the item."""

    object: Literal["realtime.item"]
    """Identifier for the API object being returned - always `realtime.item`."""

    status: Literal["completed", "incomplete", "in_progress"]
    """The status of the item. Has no effect on the conversation."""
