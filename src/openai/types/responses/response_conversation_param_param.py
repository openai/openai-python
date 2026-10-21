# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ResponseConversationParamParam"]


class ResponseConversationParamParam(TypedDict, total=False):
    """The conversation that this response belongs to."""

    id: Required[str]
    """The unique ID of the conversation."""
