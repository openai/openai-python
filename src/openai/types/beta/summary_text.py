# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["SummaryText"]


class SummaryText(BaseModel):
    """A reasoning summary content part."""

    text: str
    """The reasoning summary text."""

    type: Literal["summary_text"]
    """The content type. Always `summary_text`."""
