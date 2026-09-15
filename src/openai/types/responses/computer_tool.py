# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ComputerTool"]


class ComputerTool(BaseModel):
    """A tool that controls a virtual computer.

    Learn more about the [computer tool](https://developers.openai.com/api/docs/guides/tools-computer-use).
    """

    type: Literal["computer"]
    """The type of the computer tool. Always `computer`."""
