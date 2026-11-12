"""Check receipt verifier startup without executing vfkit or Docker."""

from __future__ import annotations

import os
import sys
import json
import stat
import shutil
import tempfile
import subprocess
from typing import Any
from pathlib import Path
from unittest.mock import patch

from guest import Guest

from openai.lib.computer import ComputerUseError


def cleanup(change: str) -> None:
    with tempfile.TemporaryDirectory(prefix="sdk-cleanup-") as directory:
        root = Path(directory)
        public = root / "run"
        public.mkdir(mode=0o700)
        saved = root / "saved"
        guest = Guest.__new__(Guest)
        guest.container_root = None
        guest.directory = public
        guest.original = public.lstat()
        guest.readers = []
        with subprocess.Popen([sys.executable, "-c", "pass"], stdout=subprocess.PIPE) as child:
            child.wait(timeout=5)
            guest.process = child
            original_lstat = Path.lstat
            original_rm = shutil.rmtree
            original_rename = Path.rename
            injected = False
            obstructed = False

            def lstat(path: Path) -> os.stat_result:
                nonlocal injected
                info = original_lstat(path)
                if not injected and change == "before-move" and path == public:
                    injected = True
                    public.rename(saved)
                    public.mkdir(mode=0o700)
                    (public / "sentinel").write_text("stranger")
                if not injected and change == "lstat-retry" and path.parent.name.startswith(".cleanup-"):
                    injected = True
                    raise KeyboardInterrupt("fixture lstat interruption")
                if not injected and change == "after-move" and path.parent.name.startswith(".cleanup-"):
                    injected = True
                    public.mkdir(mode=0o700)
                    (public / "sentinel").write_text("stranger")
                return info

            def rename(path: Path, target: Path) -> Path:
                nonlocal injected
                if path == public and change == "before-rename-retry" and not injected:
                    injected = True
                    raise KeyboardInterrupt("fixture before-rename interruption")
                result = original_rename(path, target)
                if path == public and change == "rename-retry" and not injected:
                    injected = True
                    raise KeyboardInterrupt("fixture post-rename interruption")
                return result

            def remove(path: Path) -> None:
                nonlocal injected, obstructed
                if not injected and change == "remove-retry":
                    injected = True
                    raise OSError("fixture removal failure")
                original_rm(path)
                if not obstructed and change == "remove-retry":
                    obstructed = True
                    (path.parent / "sentinel").write_text("stranger")

            with (
                patch.object(Path, "lstat", lstat),
                patch.object(Path, "rename", rename),
                patch("guest.shutil.rmtree", remove),
            ):
                if change in ("rename-retry", "lstat-retry", "before-rename-retry"):
                    (public / "owned").write_text("owned original")
                    try:
                        guest.remove()
                    except KeyboardInterrupt:
                        pass
                    else:
                        raise AssertionError("Injected interruption was swallowed")
                    assert injected
                    guest.remove()
                    assert list(root.iterdir()) == [], "Retry stranded its run after interruption"
                elif change == "device":
                    correct = guest.original
                    record = list(correct)
                    record[2] += 1
                    guest.original = os.stat_result(record)
                    try:
                        guest.remove()
                    except ComputerUseError:
                        pass
                    else:
                        raise AssertionError("Changed device must be rejected")
                    assert public.is_dir()
                    guest.original = correct
                    guest.remove()
                elif change == "before-move":
                    try:
                        guest.remove()
                    except ComputerUseError:
                        pass
                    else:
                        raise AssertionError("Replaced run must never be deleted")
                    assert saved.is_dir()
                    assert (public / "sentinel").read_text() == "stranger"
                elif change == "after-move":
                    guest.remove()
                    assert injected and (public / "sentinel").read_text() == "stranger"
                else:
                    try:
                        guest.remove()
                    except OSError as exc:
                        assert str(exc) == "fixture removal failure"
                    else:
                        raise AssertionError("Actual removal failure must remain visible")
                    try:
                        guest.remove()
                    except OSError:
                        pass
                    else:
                        raise AssertionError("Nonempty quarantine must not be removed recursively")
                    extra = guest.directory.parent / "sentinel"
                    assert extra.read_text() == "stranger"
                    extra.unlink()
                    guest.remove()
                    assert list(root.iterdir()) == []


def main() -> None:
    sentinels = {
        "OPENAI_API_KEY": "fixture-openai",
        "BROWSERBASE_API_KEY": "fixture-browserbase",
        "E2B_API_KEY": "fixture-e2b",
        "DAYTONA_API_KEY": "fixture-daytona",
        "PYTHONPATH": "fixture-python",
        "HTTP_PROXY": "fixture-proxy",
        "DOCKER_CONTEXT": "fixture-context",
    }
    with tempfile.TemporaryDirectory(
        dir="/private/tmp" if sys.platform == "darwin" else None, prefix="sge-"
    ) as directory:
        root = Path(directory)
        root.chmod(stat.S_IRWXU)
        (root / "runs").mkdir(mode=0o700)
        launches: list[tuple[list[str], dict[str, str]]] = []

        def verifier(command: list[str], **options: Any) -> subprocess.Popen[bytes]:
            launches.append((command, options.get("env", {})))
            raise OSError("Synthetic receipt verifier refusal")

        with patch.dict(os.environ, sentinels), patch("guest.subprocess.Popen", verifier):
            try:
                Guest(root)
            except ComputerUseError:
                pass
            else:
                raise AssertionError("Fixture verifier must refuse before a guest starts")
        assert len(launches) == 1
        args, env = launches[0]
        assert args[1:3] == ["-I", "-S"]
        assert env["TMPDIR"] == str(root.resolve()) and env["LANG"] == "C"
        assert set(env) == {"PATH", "LANG", "TMPDIR"}
        assert not (set(sentinels) & set(env))
        (root / "bin").mkdir(mode=0o700)
        binary = root / "bin/vfkit"
        binary.write_text("#!/bin/sh\nexit 7\n")
        binary.chmod(0o700)
        original_popen = subprocess.Popen

        def controlled(command: list[str], **options: Any) -> subprocess.Popen[bytes]:
            if "guest/setup.py" in command[3]:
                return original_popen[bytes]([sys.executable, "-I", "-S", "-c", "pass"], **options)
            return original_popen[bytes](command, **options)

        with patch("guest.subprocess.Popen", controlled):
            owner = Guest(root)
            assert owner.process.stdin is not None
            assert owner.process.wait(timeout=5) == 7
            owner.remove()
            assert owner.process.stdin.closed, "Stopped owner retained its liveness pipe"
        assert list((root / "runs").iterdir()) == []
    for change in (
        "device",
        "before-move",
        "after-move",
        "remove-retry",
        "rename-retry",
        "lstat-retry",
        "before-rename-retry",
    ):
        cleanup(change)
    print(json.dumps({"checks": 8, "api_calls": 0, "vendor_calls": 0, "vm_starts": 0}))


if __name__ == "__main__":
    main()
