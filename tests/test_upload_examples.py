from __future__ import annotations

import os
import sys
import stat
import runpy
import base64
import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "examples/generate_file.sh"
FIXTURE_NAMES = ("small_test_file.txt", "big_test_file.txt")


@pytest.fixture
def fixture_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    if os.name != "posix" or any(
        shutil.which(tool) is None for tool in ("bash", "mktemp", "head", "base64", "truncate")
    ):
        pytest.skip("The fixture generator requires POSIX shell tools")
    root = tmp_path / "fixtures with spaces"
    root.mkdir()
    monkeypatch.setenv("TMPDIR", str(root))
    return root


def generate(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["bash", str(GENERATOR), *args], capture_output=True, text=True, timeout=10, check=False)


def fake_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str, body: str) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    executable = bin_dir / name
    executable.write_text("#!/bin/sh\nset -eu\n" + body + "\n")
    executable.chmod(0o700)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])


def test_generator_uses_unique_private_directories(fixture_root: Path) -> None:
    target = fixture_root / "untouched"
    target.write_bytes(b"harmless sentinel")
    for name in FIXTURE_NAMES:
        (fixture_root / name).symlink_to(target)

    directories: set[Path] = set()
    for _ in range(2):
        result = generate("24")
        assert result.returncode == 0, result.stderr
        directory = Path(result.stdout.strip())
        assert directory.parent == fixture_root
        assert directory not in directories
        directories.add(directory)
        assert stat.S_IMODE(directory.stat().st_mode) == 0o700
        assert {path.name for path in directory.iterdir()} == set(FIXTURE_NAMES)
        for name in FIXTURE_NAMES:
            assert stat.S_IMODE((directory / name).stat().st_mode) == 0o600
        text = (directory / FIXTURE_NAMES[0]).read_bytes()
        assert len(base64.b64decode(text)) == 27
        assert (directory / FIXTURE_NAMES[1]).read_bytes() == bytes(24)
        shutil.rmtree(directory)

    assert target.read_bytes() == b"harmless sentinel"
    assert all((fixture_root / name).is_symlink() for name in FIXTURE_NAMES)


@pytest.mark.parametrize("name", FIXTURE_NAMES)
@pytest.mark.parametrize("kind", ["file", "symlink", "dangling-symlink"])
def test_generator_refuses_existing_fixture(
    fixture_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str, kind: str
) -> None:
    # Simulate an unexpected entry inside the newly allocated private directory.
    # The only possible link target is a harmless file owned by this test.
    directory = fixture_root / "allocated"
    directory.mkdir(mode=0o700)
    target = fixture_root / "sentinel"
    if kind != "dangling-symlink":
        target.write_bytes(b"harmless sentinel")
    entry = directory / name
    if kind == "file":
        entry.write_bytes(b"existing fixture")
    else:
        entry.symlink_to(target)
    monkeypatch.setenv("ALLOCATED_FIXTURE_DIR", str(directory))
    fake_command(tmp_path, monkeypatch, "mktemp", 'printf "%s\\n" "$ALLOCATED_FIXTURE_DIR"')

    result = generate("24")
    assert result.returncode != 0
    assert result.stdout == ""
    assert not directory.exists()
    if kind == "dangling-symlink":
        assert not target.exists()
    else:
        assert target.read_bytes() == b"harmless sentinel"


@pytest.mark.parametrize("command", ["head", "base64", "truncate"])
def test_generator_cleans_up_on_failure(
    fixture_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, command: str
) -> None:
    fake_command(tmp_path, monkeypatch, command, "exit 9")
    result = generate("24")
    assert result.returncode != 0
    assert result.stdout == ""
    assert list(fixture_root.iterdir()) == []


@pytest.mark.parametrize("args", [("",), ("0",), ("-1",), ("024",), ("1073741825",), ("x",), ("24", "extra")])
def test_generator_rejects_invalid_size(fixture_root: Path, args: tuple[str, ...]) -> None:
    result = generate(*args)
    assert result.returncode == 2
    assert result.stdout == ""
    assert list(fixture_root.iterdir()) == []


@pytest.mark.parametrize("mode", ["disk", "memory"])
def test_upload_example_consumes_explicit_path(fixture_root: Path, monkeypatch: pytest.MonkeyPatch, mode: str) -> None:
    result = generate("24")
    assert result.returncode == 0, result.stderr
    directory = Path(result.stdout.strip())
    file = directory / "big_test_file.txt"
    args = [str(ROOT / "examples/uploads.py"), str(file)]
    if mode == "memory":
        args.append(mode)
    monkeypatch.setattr(sys, "argv", args)

    with patch("openai.OpenAI") as constructor, patch("rich.print"):
        client = constructor.return_value.__enter__.return_value
        runpy.run_path(str(ROOT / "examples/uploads.py"), run_name="__main__")
        if mode == "memory":
            client.uploads.upload_file_chunked.assert_called_once_with(
                file=bytes(24), filename="my_file.txt", bytes=24, mime_type="txt", purpose="batch"
            )
        else:
            client.uploads.upload_file_chunked.assert_called_once_with(file=file, mime_type="txt", purpose="batch")
        constructor.return_value.__exit__.assert_called_once()

    # The example does not delete caller-owned files; the documented caller cleans up.
    assert file.read_bytes() == bytes(24)
    shutil.rmtree(directory)
    assert list(fixture_root.iterdir()) == []


def test_upload_example_requires_a_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", [str(ROOT / "examples/uploads.py")])
    with patch("openai.OpenAI") as constructor, pytest.raises(SystemExit) as exc:
        runpy.run_path(str(ROOT / "examples/uploads.py"), run_name="__main__")
    assert exc.value.code == 2
    constructor.assert_not_called()
