# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["FunctionToolParam"]


class FunctionToolParam(TypedDict, total=False):
    """
    A function tool available to the Responses backend when the Live model delegates a task.
    """

    name: Required[str]
    """The name the delegated Responses model uses when calling this function."""

    type: Required[Literal["function"]]
    """The tool type. Always `function`."""

    description: Optional[str]
    """What the function does and when the delegated Responses model should call it."""

    parameters: Optional[Dict[str, object]]
    """A JSON Schema object describing the arguments accepted by the function."""

    strict: Optional[bool]
    """
    Whether the delegated Responses model must follow the function’s parameter
    schema exactly.
    """
