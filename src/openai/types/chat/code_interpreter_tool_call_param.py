# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Union
from typing_extensions import Literal, Required, TypedDict

__all__ = [
    "CodeInterpreterOutputLogParam",
    "CodeInterpreterOutputImageFileParam",
    "CodeInterpreterOutputImageParam",
    "CodeInterpreterOutputParam",
    "CodeInterpreterCallParam",
]


class CodeInterpreterOutputLogParam(TypedDict, total=False):
    type: Required[Literal["logs"]]
    """Always 'logs' for this output type."""

    logs: Required[str]
    """The text output from the Code Interpreter tool call."""


class CodeInterpreterOutputImageFileParam(TypedDict, total=False):
    file_id: Required[str]
    """The file ID of the image."""


class CodeInterpreterOutputImageParam(TypedDict, total=False):
    type: Required[Literal["image"]]
    """Always 'image' for this output type."""

    image: Required[CodeInterpreterOutputImageFileParam]
    """The image output from the Code Interpreter tool call."""


CodeInterpreterOutputParam = Union[CodeInterpreterOutputLogParam, CodeInterpreterOutputImageParam]


class CodeInterpreterCallParam(TypedDict, total=False):
    id: Required[str]
    """The ID of the tool call."""

    type: Required[Literal["code_interpreter"]]
    """Always 'code_interpreter' for this type of tool call."""

    code: Required[str]
    """The input code for the Code Interpreter."""

    outputs: Required[Iterable[CodeInterpreterOutputParam]]
    """The outputs from the Code Interpreter tool call."""
