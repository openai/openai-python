from typing import Any, Sequence

import pytest
from pydantic import StrictInt, StrictStr, StrictBool, StrictFloat

from tests.utils import assert_matches_type


@pytest.mark.parametrize("expected", [list[int], Sequence[int]])
def test_collection_items_are_validated(expected: Any) -> None:
    assert_matches_type(expected, [1, 2], path=["items"])
    with pytest.raises(AssertionError):
        assert_matches_type(expected, [1, "wrong"], path=["items"])


@pytest.mark.parametrize(
    "expected, valid, invalid",
    [
        (StrictStr, "false", False),
        (StrictBool, False, 0),
        (StrictInt, 9007199254740993, True),
        (StrictInt, -9007199254740993, 1.5),
        (StrictFloat, 1.5, 1),
    ],
)
def test_strict_scalar_annotations(expected: Any, valid: object, invalid: object) -> None:
    assert_matches_type(expected, valid, path=["value"])
    with pytest.raises(AssertionError):
        assert_matches_type(expected, invalid, path=["value"])
