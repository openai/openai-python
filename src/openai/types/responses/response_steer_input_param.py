# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .response_steer_input_content_param import ResponseSteerInputContentParam

__all__ = [
    "ResponseSteerInputParam",
    "ResponseSteerInputItemList",
    "ResponseSteerInputItemListMessage",
]


class ResponseSteerInputItemListMessage(TypedDict, total=False):
    content: Required[Union[Iterable[ResponseSteerInputContentParam], str]]
    """The message content, as an array of content parts."""

    role: Required[Literal["user"]]
    """The message role. Always `user`."""

    type: Literal["message"]
    """The optional item type. When provided, always `message`."""


ResponseSteerInputItemList: TypeAlias = ResponseSteerInputItemListMessage

ResponseSteerInputParam: TypeAlias = Union[str, Iterable[ResponseSteerInputItemList]]
