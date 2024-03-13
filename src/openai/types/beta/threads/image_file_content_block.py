# File generated from our OpenAPI spec by Stainless.

from typing_extensions import Literal

from ...._models import BaseModel
from .image_file import ImageFile

__all__ = ["ImageFileContentBlock"]


class ImageFileContentBlock(BaseModel):
    image_file: ImageFile

    type: Literal["image_file"]
    """Always `image_file`."""
