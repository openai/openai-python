from __future__ import annotations

import re
from typing import Any, Iterable
from typing_extensions import TypeAlias

import pytest
import pydantic

from ..utils import rich_print_str

ReprArgs: TypeAlias = "Iterable[tuple[str | None, Any]]"


def print_obj(obj: object, monkeypatch: pytest.MonkeyPatch) -> str:
    """Pretty print an object to a string"""

    # monkeypatch pydantic model printing so that model fields
    # are always printed in the same order so we can reliably
    # use this for snapshot tests
    original_repr = pydantic.BaseModel.__repr_args__

    def __repr_args__(self: pydantic.BaseModel) -> ReprArgs:
        return sorted(original_repr(self), key=lambda arg: arg[0] or arg)

    with monkeypatch.context() as m:
        m.setattr(pydantic.BaseModel, "__repr_args__", __repr_args__)

        string = rich_print_str(obj)

        # Pydantic v1 and v2 have different implementations of __repr__ and print out
        # generics differently, so we strip out generic type parameters to ensure
        # consistent snapshot tests across both versions
        return re.sub(r"([A-Za-z_]\w*)\[[^\[\]]+\](?=\()", r"\1", string)
