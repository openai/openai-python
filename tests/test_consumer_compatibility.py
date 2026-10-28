from __future__ import annotations

import json
import runpy
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check-consumer-compatibility.py"


@pytest.mark.parametrize("change", ["none", "message", "location", "duplicate"])
def test_existing_diagnostics_do_not_hide_new_errors(tmp_path: Path, change: str) -> None:
    detector = runpy.run_path(str(SCRIPT))
    original = {
        "file": str(tmp_path / "consumer.py"),
        "range": {"start": {"line": 3, "character": 0}, "end": {"line": 3, "character": 10}},
        "severity": "error",
        "rule": "reportMissingTypeArgument",
        "message": 'Expected type arguments for generic class "dict"',
    }
    changed = dict(original)
    if change == "message":
        changed["message"] = 'Expected type arguments for generic class "Model"'
    elif change == "location":
        changed["file"] = str(tmp_path / "another_consumer.py")
    candidate = [original, changed] if change == "duplicate" else [changed]
    assert detector["new_errors"]([original], candidate, tmp_path) == ([] if change == "none" else [changed])


@pytest.mark.parametrize("failure", ["crash", "invalid_json", "no_files", "missing_errors"])
def test_checker_failures_cannot_pass_the_gate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str) -> None:
    detector = runpy.run_path(str(SCRIPT))
    output = json.dumps({"generalDiagnostics": [], "summary": {"filesAnalyzed": 0, "errorCount": 0}})
    if failure == "invalid_json":
        output = "not JSON"
    elif failure == "missing_errors":
        output = json.dumps({"generalDiagnostics": [], "summary": {"filesAnalyzed": 1, "errorCount": 1}})
    result = subprocess.CompletedProcess([], 2 if failure == "crash" else 0, stdout=output, stderr="")
    monkeypatch.setattr(subprocess, "run", lambda *_args, **_kwargs: result)
    with pytest.raises((RuntimeError, ValueError)):
        detector["check"](tmp_path)
