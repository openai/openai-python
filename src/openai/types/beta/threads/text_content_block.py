# File generated from our OpenAPI spec by Stainless.

from typing_extensions import Literal

from .text import Text
from ...._models import BaseModel

__all__ = ["TextContentBlock"]


class TextContentBlock(BaseModel):
    text: Text

    type: Literal["text"]
    """Always `text`."""
