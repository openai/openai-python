# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel
from .response_steer_input_content import ResponseSteerInputContent

__all__ = [
    "ResponseSteerInput",
    "ResponseSteerInputItemList",
    "ResponseSteerInputItemListMessage",
]


class ResponseSteerInputItemListMessage(BaseModel):
    content: Union[List[ResponseSteerInputContent], str]
    """The message content, as an array of content parts."""

    role: Literal["user"]
    """The message role. Always `user`."""

    type: Optional[Literal["message"]] = None
    """The item type, when provided. Always `message`."""


ResponseSteerInputItemList: TypeAlias = ResponseSteerInputItemListMessage

ResponseSteerInput: TypeAlias = Union[str, List[ResponseSteerInputItemList]]
