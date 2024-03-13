# File generated from our OpenAPI spec by Stainless.

from typing import Union
from typing_extensions import Annotated

from ...._utils import PropertyInfo
from .text_content_block import TextContentBlock
from .image_file_content_block import ImageFileContentBlock

__all__ = ["MessageContent"]

MessageContent = Annotated[Union[ImageFileContentBlock, TextContentBlock], PropertyInfo(discriminator="type")]
