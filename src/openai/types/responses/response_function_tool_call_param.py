# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ResponseFunctionToolCallParam"]


class ResponseFunctionToolCallParam(TypedDict, total=False):
    id: Required[str]
    """The unique ID of the function tool call."""

    arguments: Required[str]
    """A JSON string of the arguments to pass to the function."""

    call_id: Required[str]
    """The unique ID of the function tool call generated by the model."""

    name: Required[str]
    """The name of the function to run."""

    type: Required[Literal["function_call"]]
    """The type of the function tool call. Always `function_call`."""

    status: Literal["in_progress", "completed", "incomplete"]
    """The status of the item.

    One of `in_progress`, `completed`, or `incomplete`. Populated when items are
    returned via API.
    """
