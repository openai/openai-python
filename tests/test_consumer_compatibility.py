from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.skipif(os.name != "posix", reason="The compatibility gate runs in Bash on CI")
@pytest.mark.parametrize("also_change", [None, "src/model.py", "pyproject.toml"])
def test_compatibility_gate_selects_callers(tmp_path: Path, also_change: str | None) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    gate = scripts / "detect-breaking-changes"
    shutil.copy(Path(__file__).resolve().parents[1] / "scripts" / gate.name, gate)
    (scripts / "pyrightconfig.breaking-changes.json").write_text("{}")
    (tmp_path / "tests").mkdir()
    (tmp_path / "src").mkdir()
    (tmp_path / "src/model.py").write_text("original SDK\n")
    caller = tmp_path / "tests/caller.py"
    caller.write_text("previous caller\n")

    # Record the checker inputs to exercise the real Git and snapshot routing.
    uv = tmp_path / "uv"
    uv.write_text(
        "#!/bin/sh\nset -eu\nconfig=${PYRIGHT_PROJECT:-scripts/pyrightconfig.breaking-changes.json}\n"
        'root=$(dirname "$config")/..\ncat "$root/tests/caller.py" "$root/src/model.py"\n'
    )
    uv.chmod(0o755)
    subprocess.run(["git", "init", "--quiet"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.org", "commit", "--no-gpg-sign", "-qm", "base"],
        cwd=tmp_path,
        check=True,
    )

    caller.write_text("current caller\n")
    if also_change is not None:
        (tmp_path / also_change).write_text("changed input\n")
        subprocess.run(["git", "add", also_change], cwd=tmp_path, check=True)
    result = subprocess.run(
        [str(gate), "HEAD"],
        cwd=tmp_path,
        env={**os.environ, "PATH": f"{tmp_path}{os.pathsep}{os.environ['PATH']}"},
        text=True,
        capture_output=True,
        check=True,
    )
    sdk = "changed input" if also_change == "src/model.py" else "original SDK"
    expected = ["current caller", sdk]
    if also_change is not None:
        expected.extend(["previous caller", sdk])
    assert [line for line in result.stdout.splitlines() if not line.startswith("==>")] == expected
    assert caller.read_text() == "current caller\n"
