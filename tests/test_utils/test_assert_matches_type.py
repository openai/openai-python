from typing import Any, Literal, Sequence

import pytest

from tests.utils import assert_matches_type
from openai.types import Model
from openai._models import construct_type


@pytest.mark.parametrize(
    ("type_", "value"),
    [
        (list[int], [1, "wrong"]),
        (Sequence[int], (1, "wrong")),
        (list[list[int]], [[1], ["wrong"]]),
        (Sequence[list[int]], ([1], ["wrong"])),
        (list[dict[str, int]], [{"value": "wrong"}]),
        (dict[str, list[int]], {"values": ["wrong"]}),
        (list[Literal["expected"]], ["wrong"]),
    ],
)
def test_rejects_invalid_sequence_members(type_: Any, value: object) -> None:
    with pytest.raises(AssertionError):
        assert_matches_type(type_=type_, value=value, path=["response"])


@pytest.mark.parametrize(
    ("type_", "value"),
    [
        (list[int], [1, 2]),
        (Sequence[int], (1, 2)),
        (list[list[int]], [[1], []]),
        (Sequence[list[int]], ([1], [2])),
        (list[dict[str, int]], [{"value": 1}]),
        (list[Any], [1, "value", None]),
        (Sequence[Any], (1, "value", None)),
    ],
)
def test_accepts_valid_sequence_members(type_: Any, value: object) -> None:
    assert_matches_type(type_=type_, value=value, path=["response"])


def test_rejects_invalid_fields_in_nested_models() -> None:
    model: object = construct_type(
        type_=Model,
        value={
            "id": "test-model",
            "created": "not-an-integer",
            "object": "model",
            "owned_by": "test",
        },
    )
    assert isinstance(model, Model)
    with pytest.raises(AssertionError):
        assert_matches_type(type_=list[Model], value=[model], path=["response", "data"])
