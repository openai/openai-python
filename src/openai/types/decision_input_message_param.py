# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, TypedDict

from .decision_input_part_union_param import DecisionInputPartUnionParam

__all__ = ["DecisionInputMessageParam"]


class DecisionInputMessageParam(TypedDict, total=False):
    """A user message containing text or inline images."""

    content: Required[Union[str, Iterable[DecisionInputPartUnionParam]]]
    """Text evidence or an ordered list of text and inline image parts."""

    role: Required[Literal["user"]]

    type: Literal["message"]
