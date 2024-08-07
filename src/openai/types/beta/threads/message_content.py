# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ...._utils import PropertyInfo
from ...._compat import PYDANTIC_V2
from ...._models import BaseModel
from .text_content_block import TextContentBlock
from .refusal_content_block import RefusalContentBlock
from .image_url_content_block import ImageURLContentBlock
from .image_file_content_block import ImageFileContentBlock

if PYDANTIC_V2:
    from pydantic import field_serializer


__all__ = ["MessageContent", "BaseContentBlock"]


class BaseContentBlock(BaseModel):
    type: Literal["unknown"]
    """The type of content part"""

    if PYDANTIC_V2:

        @field_serializer("type", when_used="always")  # type: ignore
        def serialize_unknown_type(self, type_: str) -> str:
            return type_


MessageContent: TypeAlias = Annotated[
    Union[BaseContentBlock, ImageFileContentBlock, ImageURLContentBlock, TextContentBlock, RefusalContentBlock],
    PropertyInfo(discriminator="type"),
]
