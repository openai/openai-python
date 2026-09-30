# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["OutputText"]


class OutputText(BaseModel):
    """A text content part produced by the agent."""

    text: str
    """The text produced by the agent."""

    type: Literal["output_text"]
    """The content type. Always `output_text`."""
