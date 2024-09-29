from __future__ import annotations

import inspect
from typing import Any, Iterable
from typing_extensions import TypeAlias

import pytest
import pydantic

from ...utils import rich_print_str

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

        # we remove all `fn_name.<locals>.` occurences
        # so that we can share the same snapshots between
        # pydantic v1 and pydantic v2 as their output for
        # generic models differs, e.g.
        #
        # v2: `ParsedChatCompletion[test_parse_pydantic_model.<locals>.Location]`
        # v1: `ParsedChatCompletion[Location]`
        return clear_locals(string, stacklevel=2)


def get_caller_name(*, stacklevel: int = 1) -> str:
    frame = inspect.currentframe()
    assert frame is not None

    for i in range(stacklevel):
        frame = frame.f_back
        assert frame is not None, f"no {i}th frame"

    return frame.f_code.co_name


def clear_locals(string: str, *, stacklevel: int) -> str:
    caller = get_caller_name(stacklevel=stacklevel + 1)
    return string.replace(f"{caller}.<locals>.", "")
