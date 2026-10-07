from __future__ import annotations

import runpy
from pathlib import Path

import griffe
import pytest


@pytest.mark.parametrize("remove_retrieve", [False, True])
def test_moving_public_class_to_a_reexport_detects_actual_removed_methods(
    tmp_path: Path, remove_retrieve: bool
) -> None:
    old_root = tmp_path / "old"
    old_root.mkdir()
    (old_root / "fixture_api.py").write_text("class Turns:\n    def list(self): pass\n    def retrieve(self): pass\n")
    new_root = tmp_path / "new"
    package = new_root / "fixture_api"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("from .turns import Turns as Turns\n")
    (package / "turns.py").write_text(
        "class Turns:\n    def list(self): pass\n" + ("" if remove_retrieve else "    def retrieve(self): pass\n")
    )
    old = griffe.load("fixture_api", search_paths=[old_root])
    new = griffe.load("fixture_api", search_paths=[new_root])
    detector = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts" / "detect-breaking-changes.py"))
    changes = "".join(str(part) for part in detector["find_breaking_changes"](new, old, path=["fixture_api"]))
    assert ("fixture_api.Turns.retrieve" in changes) is remove_retrieve
    assert "fixture_api.Turns.list" not in changes
