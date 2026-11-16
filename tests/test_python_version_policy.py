from __future__ import annotations

import runpy
from typing import cast
from pathlib import Path
from collections.abc import Callable

import pytest


@pytest.fixture
def check_dependency() -> Callable[[str, str], None]:
    namespace = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/check-python-version-policy.py"))
    return cast(Callable[[str, str], None], namespace["require_unmarked_dependency"])


@pytest.mark.parametrize("bounds", [">=1.40.0,<2", "<2,>=1.40.0", " <2, >=1.40.0 "])
def test_unmarked_dependency_accepts_equivalent_bound_order(
    check_dependency: Callable[[str, str], None], bounds: str
) -> None:
    check_dependency(f'bedrock = ["botocore{bounds}"]', "botocore>=1.40.0,<2")


@pytest.mark.parametrize(
    "requirement",
    [
        "botocore>=1.39.0,<2",
        "botocore>=1.40.0,<3",
        "botocore>=1.40.0",
        "botocore<2",
        "botocore<2,>=1.40.0,!=1.41.0",
        "botocore[extra]>=1.40.0,<2",
        "botocore @ https://example.invalid/botocore.whl",
        "botocore<2,>=1.40.0; python_version >= '3.11'",
        "botocore<2,>=1.40.0; sys_platform == 'linux'",
    ],
)
def test_unmarked_dependency_rejects_changed_bounds_extras_sources_and_markers(
    check_dependency: Callable[[str, str], None], requirement: str
) -> None:
    with pytest.raises(RuntimeError):
        check_dependency(f'bedrock = ["{requirement}"]', "botocore>=1.40.0,<2")


def test_unmarked_dependency_rejects_marked_duplicate_with_reordered_bounds(
    check_dependency: Callable[[str, str], None],
) -> None:
    metadata = 'bedrock = ["botocore>=1.40.0,<2", "botocore<2,>=1.40.0; python_version < \'3.11\'"]'
    with pytest.raises(RuntimeError, match="still contains a Python marker"):
        check_dependency(metadata, "botocore>=1.40.0,<2")
