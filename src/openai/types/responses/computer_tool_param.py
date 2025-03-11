# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ComputerToolParam"]


class ComputerToolParam(TypedDict, total=False):
    display_height: Required[float]
    """The height of the computer display."""

    display_width: Required[float]
    """The width of the computer display."""

    environment: Required[Literal["mac", "windows", "ubuntu", "browser"]]
    """The type of computer environment to control."""

    type: Required[Literal["computer-preview"]]
    """The type of the computer use tool. Always `computer_use_preview`."""
