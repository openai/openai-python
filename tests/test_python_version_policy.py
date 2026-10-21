from __future__ import annotations

import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHECK = runpy.run_path(str(ROOT / "scripts/check-python-version-policy.py"))["check_pr_runtimes"]
WORKFLOW = (ROOT / ".github/workflows/ci.yml").read_text()


def test_required_runtimes() -> None:
    CHECK(WORKFLOW)


@pytest.mark.parametrize("version", ["3.10", "3.14"])
@pytest.mark.parametrize("defect", ["missing", "wrong", "duplicate"])
def test_rejects_invalid_required_runtime(version: str, defect: str) -> None:
    declaration = f"python-version: '{version}'"
    if defect == "missing":
        candidate = WORKFLOW.replace(f"test-python{version.replace('.', '')}:\n", "missing-runtime:\n")
    elif defect == "wrong":
        candidate = WORKFLOW.replace(declaration, "python-version: '3.11'")
    else:
        candidate = WORKFLOW.replace(declaration, declaration + "\n          " + declaration)
    with pytest.raises(RuntimeError):
        CHECK(candidate)
