# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, TypeAlias

from ...types import shared_params

__all__ = ["AssistantResponseFormatOptionParam"]

AssistantResponseFormatOptionParam: TypeAlias = Union[
    Literal["auto"],
    shared_params.ResponseFormatText,
    shared_params.ResponseFormatJSONObject,
    shared_params.ResponseFormatJSONSchema,
]
