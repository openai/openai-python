from typing import Any, Sequence

import pytest

from tests.utils import assert_matches_type


@pytest.mark.parametrize("expected", [list[int], Sequence[int]])
def test_collection_items_are_validated(expected: Any) -> None:
    assert_matches_type(expected, [1, 2], path=["items"])
    with pytest.raises(AssertionError):
        assert_matches_type(expected, [1, "wrong"], path=["items"])
