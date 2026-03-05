# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ComputerToolParam"]


class ComputerToolParam(TypedDict, total=False):
    """A tool that controls a virtual computer.

    Learn more about the [computer tool](https://platform.openai.com/docs/guides/tools-computer-use).
    """

    type: Required[Literal["computer"]]
    """The type of the computer tool. Always `computer`."""
