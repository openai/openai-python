# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["DecisionQuestionInputImage"]


class DecisionQuestionInputImage(BaseModel):
    """An image provided as a base64 data URL or a publicly accessible HTTP(S) URL.

    File IDs are not supported.
    """

    image_url: str
    """
    A base64-encoded image in a data URL or a publicly accessible HTTP(S) image URL.
    """

    type: Literal["input_image"]

    detail: Optional[Literal["low", "high", "auto", "original"]] = None
    """The image detail level, using the selected model's image profile.

    Defaults to auto.
    """
