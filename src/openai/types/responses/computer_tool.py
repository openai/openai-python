# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ComputerTool"]


class ComputerTool(BaseModel):
    display_height: float
    """The height of the computer display."""

    display_width: float
    """The width of the computer display."""

    environment: Literal["mac", "windows", "ubuntu", "browser"]
    """The type of computer environment to control."""

    type: Literal["computer-preview"]
    """The type of the computer use tool. Always `computer_use_preview`."""
