from __future__ import annotations

from typing import Any, Iterable

from ..._types import Omit, omit
from ..._models import BaseModel


def sanitize_response_input(
    input: str | Iterable[Any] | None | Omit,
) -> str | list[Any] | None | Omit:
    if input is omit or input is None or isinstance(input, str):
        return input

    return [
        item.to_dict(mode="json", exclude_unset=True, exclude_none=True)
        if isinstance(item, BaseModel)
        else item
        for item in input
    ]
