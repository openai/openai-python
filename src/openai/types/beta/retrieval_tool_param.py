# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["RetrievalToolParam"]


class RetrievalToolParam(TypedDict, total=False):
    type: Required[Literal["retrieval"]]
    """The type of tool being defined: `retrieval`"""
