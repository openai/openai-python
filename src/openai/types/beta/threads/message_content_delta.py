# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ...._utils import PropertyInfo
from ...._compat import PYDANTIC_V2
from ...._models import BaseModel
from .text_delta_block import TextDeltaBlock
from .refusal_delta_block import RefusalDeltaBlock
from .image_url_delta_block import ImageURLDeltaBlock
from .image_file_delta_block import ImageFileDeltaBlock

if PYDANTIC_V2:
    from pydantic import field_serializer


__all__ = ["MessageContentDelta", "BaseDeltaBlock"]


class BaseDeltaBlock(BaseModel):
    index: int
    """The index of the content part in the message."""

    type: Literal["unknown"]
    """The type of content part"""

    if PYDANTIC_V2:

        @field_serializer("type", when_used="always")  # type: ignore
        def serialize_unknown_type(self, type_: str) -> str:
            return type_


MessageContentDelta: TypeAlias = Annotated[
    Union[BaseDeltaBlock, ImageFileDeltaBlock, TextDeltaBlock, RefusalDeltaBlock, ImageURLDeltaBlock],
    PropertyInfo(discriminator="type"),
]
