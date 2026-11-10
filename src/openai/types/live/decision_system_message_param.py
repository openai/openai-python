# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

from .decision_input_text_param import DecisionInputTextParam

__all__ = ["DecisionSystemMessageParam"]


class DecisionSystemMessageParam(TypedDict, total=False):
    content: Required[Union[str, Iterable[DecisionInputTextParam]]]
    """The text input to the model."""

    role: Required[Literal["system"]]

    id: Optional[str]
    """The unique ID of this message item."""

    type: Literal["message"]
