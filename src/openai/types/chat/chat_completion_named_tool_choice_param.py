# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ChatCompletionNamedToolChoiceParam", "Function"]


class Function(TypedDict, total=False):
    name: Required[str]
    """The name of the function to call."""


class ChatCompletionNamedToolChoiceParam(TypedDict, total=False):
    function: Required[Function]

    type: Required[Literal["function"]]
    """The type of the tool. Currently, only `function` is supported."""
