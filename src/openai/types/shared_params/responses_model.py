# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, TypeAlias

from ..shared.chat_model import ChatModel

__all__ = ["ResponsesModel"]

ResponsesModel: TypeAlias = Union[
    str, ChatModel, Literal["o1-pro", "o1-pro-2025-03-19", "computer-use-preview", "computer-use-preview-2025-03-11"]
]
