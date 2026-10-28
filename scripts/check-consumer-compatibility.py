from __future__ import annotations

import os
import sys
import json
import shutil
import tarfile
import tempfile
import subprocess
from typing import Any
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "scripts/pyrightconfig.breaking-changes.json"


def snapshot_baseline(ref: str, destination: Path) -> None:
    commit = subprocess.check_output(
        ["git", "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}"], cwd=ROOT, text=True
    ).strip()
    with tempfile.TemporaryFile() as archive:
        subprocess.run(["git", "archive", commit, "src", "tests"], cwd=ROOT, stdout=archive, check=True)
        archive.seek(0)
        with tarfile.open(fileobj=archive) as contents:
            for member in contents:
                path = Path(member.name)
                if path.is_absolute() or ".." in path.parts or not (member.isfile() or member.isdir()):
                    raise RuntimeError(f"Unsupported baseline archive entry: {member.name}")
                target = destination / path
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    source = contents.extractfile(member)
                    assert source is not None
                    with source, target.open("wb") as output:
                        shutil.copyfileobj(source, output)


def check(snapshot: Path) -> list[dict[str, Any]]:
    # Keep the current checker configuration and dependencies fixed. Only the
    # SDK source changes; all tests and their helpers come from the baseline.
    # Preserve relative include and import paths by keeping the config in scripts/.
    config_path = snapshot / "scripts" / CONFIG.name
    config_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(CONFIG, config_path)
    result = subprocess.run(
        [str(ROOT / "scripts/run-pyright"), "--outputjson", "--pythonpath", sys.executable],
        cwd=ROOT,
        env={**os.environ, "PYRIGHT_PROJECT": str(config_path)},
        capture_output=True,
        text=True,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(f"Pyright failed ({result.returncode}): {result.stderr}\n{result.stdout}")
    report = json.loads(result.stdout)
    errors = [diagnostic for diagnostic in report["generalDiagnostics"] if diagnostic["severity"] == "error"]
    if (
        report["summary"]["filesAnalyzed"] == 0
        or report["summary"]["errorCount"] != len(errors)
        or result.returncode != bool(errors)
    ):
        raise RuntimeError("Pyright returned an incomplete or inconsistent report")
    return errors


def diagnostic_key(diagnostic: dict[str, Any], snapshot: Path) -> str:
    # Compare full messages and locations, not just counts or rule names: a
    # different error on an already failing line is still a regression.
    key = {field: diagnostic.get(field) for field in ("file", "range", "rule", "message", "severity")}
    return json.dumps(key, sort_keys=True).replace(str(snapshot), "<snapshot>")


def new_errors(baseline: list[dict[str, Any]], candidate: list[dict[str, Any]], snapshot: Path) -> list[dict[str, Any]]:
    remaining = Counter(diagnostic_key(diagnostic, snapshot) for diagnostic in baseline)
    added = []
    for diagnostic in candidate:
        key = diagnostic_key(diagnostic, snapshot)
        if remaining[key]:
            remaining[key] -= 1
        else:
            added.append(diagnostic)
    return added


def main(ref: str) -> int:
    with tempfile.TemporaryDirectory(prefix="openai-consumer-compatibility-") as directory:
        snapshot = Path(directory).resolve()
        snapshot_baseline(ref, snapshot)
        print("==> Checking previous callers against the baseline SDK", flush=True)
        baseline = check(snapshot)
        shutil.rmtree(snapshot / "src")
        shutil.copytree(ROOT / "src", snapshot / "src", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        print("==> Checking the same callers against the candidate SDK", flush=True)
        candidate = check(snapshot)
        added = new_errors(baseline, candidate, snapshot)
        print(f"Baseline: {len(baseline)} errors; candidate: {len(candidate)} errors; new: {len(added)}")
        for diagnostic in added:
            path = Path(diagnostic["file"]).relative_to(snapshot)
            start = diagnostic["range"]["start"]
            print(f"{path}:{start['line'] + 1}:{start['character'] + 1}: {diagnostic['message']}")
            print(f"  [{diagnostic.get('rule', 'unknown')}]")
        return 1 if added else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: check-consumer-compatibility.py BASE_REF")
    raise SystemExit(main(sys.argv[1]))
