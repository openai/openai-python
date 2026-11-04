"""Check local container admission and interrupted creation with in-process Docker responses."""

from __future__ import annotations

import os
import sys
import json
import shutil
import signal
import socket
import platform
import subprocess
from types import SimpleNamespace
from typing import Any
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from collections.abc import Callable

import container_runtime as runtime

IMAGE = "sha256:" + "a" * 64
CONTAINER = "b" * 64


def prepare(root: Path) -> None:
    root.mkdir(mode=0o700)
    (root / "runs").mkdir(mode=0o700)
    (root / "build").mkdir(mode=0o700)
    context = root / "build/context"
    context.mkdir(mode=0o700)
    for name, source in runtime.FILES.items():
        shutil.copyfile(source, context / name)
        (context / name).chmod(0o600)
    runtime.write_new(
        root / "setup.json",
        {
            "backend": "container",
            "owner": runtime.identity(root),
            "image": IMAGE,
            "recipe": runtime.recipe(),
            "base": runtime.IMAGE,
        },
    )
    (root / "runs/unrelated").mkdir(mode=0o700)
    (root / "runs/unrelated/sentinel").write_text("other run")


class Docker:
    def __init__(
        self,
        root: Path,
        *,
        available: bool,
        receipt: bool,
        start_failure: bool = False,
        foreign_after_start: bool = False,
        renamed: bool = False,
    ) -> None:
        self.root = root
        self.available = available
        self.receipt = receipt
        self.start_failure = start_failure
        self.foreign_after_start = foreign_after_start
        self.renamed = renamed
        self.started = False
        self.cancelled = False
        self.removed = False
        self.directory: Path | None = None
        self.calls: list[list[str]] = []
        self.create: subprocess.Popen[bytes] | None = None
        self.real_popen = subprocess.Popen[bytes]

    @property
    def drained(self) -> bool:
        return self.create is not None and self.create.poll() is not None

    def is_cancelled(self) -> bool:
        return self.cancelled

    def popen(self, args: list[str], **kwargs: Any) -> subprocess.Popen[bytes]:
        command = args[5:]
        self.calls.append(command)
        kind = command[0]
        response = b""
        code = 0
        if kind == "image":
            code = 0 if self.available else 1
            response = (IMAGE + "\n").encode()
        elif kind == "create":
            cid = Path(command[command.index("--cidfile") + 1])
            self.directory = cid.parent
            if self.receipt:
                cid.write_text(CONTAINER)
            if self.start_failure:
                self.create = self.real_popen([sys.executable, "-c", "pass"], **kwargs)
                return self.create
            self.create = self.real_popen([sys.executable, "-c", "import time;time.sleep(60)"], **kwargs)
            self.cancelled = True
            return self.create
        elif kind == "ps":
            assert self.drained, "lookup raced a live create CLI"
            if not self.removed and self.receipt:
                response = (CONTAINER + "\n").encode()
        elif kind == "inspect":
            assert self.directory is not None
            intent = json.loads((self.directory / "intent.json").read_text())
            profile = json.loads((self.root / "build/context/seccomp.json").read_text())
            response = json.dumps(
                [
                    {
                        "Id": CONTAINER,
                        "State": {"Running": True},
                        "Image": IMAGE,
                        "Name": "/renamed-owned" if self.renamed else "/" + intent["name"],
                        "Config": {
                            "Labels": {
                                runtime.LABEL: "another-owner"
                                if self.started and self.foreign_after_start
                                else intent["nonce"]
                            },
                            "User": "0:0",
                            "Cmd": ["python3", "-I", "/opt/desktop/start.py"],
                            "Entrypoint": None,
                        },
                        "HostConfig": {
                            "NetworkMode": "none",
                            "IpcMode": "private",
                            "ReadonlyRootfs": True,
                            "Privileged": False,
                            "CapDrop": ["ALL"],
                            "CapAdd": ["CAP_SETUID", "CAP_SETGID", "CAP_KILL"],
                            "NanoCpus": 2000000000,
                            "Memory": 2 * 1024**3,
                            "MemorySwap": 2 * 1024**3,
                            "ShmSize": 256 * 1024**2,
                            "PidsLimit": 512,
                            "Tmpfs": {
                                "/tmp": "rw,nosuid,nodev,size=256m,mode=1777",
                                "/run/desktop": "rw,nosuid,nodev,size=64m,uid=1000,gid=1000,mode=0755",
                                "/run/desktop-owner": "rw,nosuid,nodev,size=8m,uid=0,gid=0,mode=0700",
                                "/home/desktop": "rw,nosuid,nodev,size=768m,uid=1000,gid=1000,mode=0700",
                            },
                            "SecurityOpt": ["no-new-privileges", "seccomp=" + json.dumps(profile)],
                        },
                    }
                ]
            ).encode()
        elif kind == "start":
            assert self.start_failure and command == ["start", CONTAINER]
            self.started = True
            code = 1
        elif kind == "rm":
            assert self.receipt and self.drained and command == ["rm", "-f", CONTAINER]
            self.removed = True
        else:
            raise AssertionError(f"Unplanned Docker call: {command!r}")
        return self.real_popen(
            [
                sys.executable,
                "-c",
                "import sys;sys.stdout.buffer.write(bytes.fromhex(sys.argv[1]));sys.exit(int(sys.argv[2]))",
                response.hex(),
                str(code),
            ],
            **kwargs,
        )


def startup_failure() -> None:
    for foreign, renamed in ((False, False), (True, False), (False, True), (True, True)):
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve() / "runtime"
            prepare(root)
            driver = Docker(
                root, available=True, receipt=True, start_failure=True, foreign_after_start=foreign, renamed=renamed
            )
            with (
                patch.object(runtime, "local_only", return_value="/unused/local-docker"),
                patch.object(runtime.subprocess, "Popen", side_effect=driver.popen),
            ):
                try:
                    runtime.start(root)
                except RuntimeError as error:
                    assert ("exact image" if foreign else "Local Docker command failed") in str(error)
                else:
                    raise AssertionError("A failed Docker start returned a guest")
            assert driver.started and driver.drained and driver.directory is not None
            assert driver.removed is not foreign
            assert driver.directory.exists() is foreign
            assert (root / "runs/unrelated/sentinel").read_text() == "other run"


def create_cancelled_before_launch(*, timeout: bool) -> None:
    with TemporaryDirectory() as temporary:
        root = Path(temporary).resolve() / "runtime"
        prepare(root)
        driver = Docker(root, available=True, receipt=False)
        elapsed = 0.0
        real_fsync = os.fsync

        def fsync(fd: int) -> None:
            nonlocal elapsed
            real_fsync(fd)
            if timeout:
                elapsed = 61
            else:
                driver.cancelled = True

        with (
            patch.object(runtime, "local_only", return_value="/unused/local-docker"),
            patch.object(runtime.subprocess, "Popen", side_effect=driver.popen),
            patch.object(runtime, "time", SimpleNamespace(monotonic=lambda: elapsed)),
            patch.object(runtime.os, "fsync", side_effect=fsync),
        ):
            try:
                runtime.start(root, cancelled=driver.is_cancelled)
            except runtime.StartupCancelled:
                pass
            else:
                raise AssertionError("Cancellation before launch returned a guest")
        assert [call[0] for call in driver.calls] == ["image"]
        assert list((root / "runs").iterdir()) == [root / "runs/unrelated"]
        assert (root / "runs/unrelated/sentinel").read_text() == "other run"


def initial_intent_failure(boundary: str) -> None:
    with TemporaryDirectory() as temporary:
        root = Path(temporary).resolve() / "runtime"
        prepare(root)
        driver = Docker(root, available=True, receipt=False)
        original_open: Callable[..., Any] = Path.open
        real_fsync = os.fsync
        real_fchmod = os.fchmod
        real_fstat = os.fstat
        failure = OSError("controlled receipt failure")
        attempted: Path | None = None
        interrupted = False
        prior_mask = signal.pthread_sigmask(signal.SIG_BLOCK, set())

        def open_receipt(path: Path, *args: Any, **kwargs: Any) -> Any:
            nonlocal attempted
            if path.name == "intent.json" and args and args[0] == "x":
                attempted = path.parent
                if boundary == "missing":
                    raise failure
            return original_open(path, *args, **kwargs)

        def dump(_value: object, output: Any, **_kwargs: Any) -> None:
            assert attempted is not None
            output.write('{"owner":')
            output.flush()
            if boundary == "directory":
                attempted.rename(root / "runs/original")
                attempted.mkdir(mode=0o700)
                (attempted / "sentinel").write_text("replacement directory")
            elif boundary == "file":
                receipt = attempted / "intent.json"
                receipt.rename(attempted / "original")
                receipt.write_text("replacement receipt")
            if boundary != "sync":
                raise failure

        def fsync(fd: int) -> None:
            if attempted is not None:
                raise failure
            real_fsync(fd)

        def fchmod(fd: int, mode: int) -> None:
            if attempted is not None and boundary == "chmod":
                raise failure
            real_fchmod(fd, mode)

        def fstat(fd: int) -> os.stat_result:
            nonlocal interrupted
            if attempted is not None and boundary == "signal" and not interrupted:
                interrupted = True
                os.kill(os.getpid(), signal.SIGINT)
            return real_fstat(fd)

        with (
            patch.object(runtime, "local_only", return_value="/unused/local-docker"),
            patch.object(runtime.subprocess, "Popen", side_effect=driver.popen),
            patch.object(Path, "open", open_receipt),
            patch.object(runtime.json, "dump", side_effect=dump),
            patch.object(runtime.os, "fsync", side_effect=fsync),
            patch.object(runtime.os, "fchmod", side_effect=fchmod),
            patch.object(runtime.os, "fstat", side_effect=fstat),
        ):
            try:
                runtime.start(root)
            except (OSError, ValueError, KeyboardInterrupt) as error:
                if boundary == "signal":
                    assert isinstance(error, KeyboardInterrupt), "Cleanup replaced the initial SIGINT"
                if boundary in {"missing", "partial", "sync", "chmod"}:
                    assert error is failure
            else:
                raise AssertionError("Pre-create receipt failure returned a run")
        assert attempted is not None
        assert signal.pthread_sigmask(signal.SIG_BLOCK, set()) == prior_mask
        assert [call[0] for call in driver.calls] == ["image"]
        assert (root / "runs/unrelated/sentinel").read_text() == "other run"
        if boundary in {"missing", "partial", "sync", "chmod", "signal"}:
            assert not attempted.exists(), "Pre-create failure retained its fresh directory"
        elif boundary == "directory":
            assert (attempted / "sentinel").read_text() == "replacement directory"
        else:
            assert (attempted / "intent.json").read_text() == "replacement receipt"


def cleanup_replacement(*, replace: bool, after_move: bool = False, after_open: bool = False) -> None:
    with TemporaryDirectory() as temporary:
        root = Path(temporary).resolve() / "runtime"
        prepare(root)
        run_id = "123456789abc"
        directory = root / "runs" / run_id
        directory.mkdir(mode=0o700)
        runtime.write_new(
            directory / "intent.json",
            {
                "owner": runtime.identity(directory),
                "name": "openai-desktop-" + run_id,
                "nonce": "fixture",
                "image": IMAGE,
            },
        )
        (directory / "container-id").write_text(CONTAINER)
        (directory / "original").write_text("keep this run")
        (directory / "nested").mkdir()
        (directory / "nested/detail").write_text("owned")
        (directory / "external").symlink_to(root / "runs/unrelated", target_is_directory=True)
        original_owned = runtime.owned
        original_unlink = os.unlink
        original_fstat = os.fstat
        original = directory.stat()
        looked_up = False
        changed = False
        attempts = 0

        def docker(_root: Path, args: list[str], **_kwargs: Any) -> bytes:
            nonlocal looked_up
            assert args[0] == "ps"
            looked_up = True
            return b""

        def owned(path: Path, mode: int, is_directory: bool = False) -> os.stat_result:
            nonlocal changed
            result = original_owned(path, mode, is_directory)
            target = root / "runs" / (".cleanup-" + run_id) / "run" if after_move else directory
            if replace and not after_open and path == target and looked_up and not changed:
                target.rename(root / "runs" / "original")
                target.mkdir(mode=0o700)
                (target / "sentinel").write_text("unexpected replacement")
                changed = True
            return result

        def fstat(fd: int) -> os.stat_result:
            nonlocal changed
            result = original_fstat(fd)
            if after_open and not changed and result.st_ino == original.st_ino and result.st_dev == original.st_dev:
                target = root / "runs" / (".cleanup-" + run_id) / "run"
                target.rename(root / "runs" / "original")
                target.mkdir(mode=0o700)
                (target / "sentinel").write_text("unexpected replacement")
                changed = True
            return result

        def unlink(path: str | bytes | os.PathLike[str], *args: Any, **kwargs: Any) -> None:
            nonlocal attempts
            if path == "original" and kwargs.get("dir_fd") is not None:
                attempts += 1
                if not replace and attempts == 1:
                    raise OSError("controlled cleanup interruption")
            original_unlink(path, *args, **kwargs)

        with (
            patch.object(runtime, "docker", side_effect=docker),
            patch.object(runtime, "owned", side_effect=owned),
            patch.object(runtime.os, "unlink", side_effect=unlink),
            patch.object(runtime.os, "fstat", side_effect=fstat),
        ):
            try:
                runtime.remove(root, run_id)
            except (RuntimeError, ValueError) as error:
                assert replace and "changed" in str(error)
            except OSError as error:
                assert not replace and "controlled cleanup interruption" in str(error)
                runtime.remove(root, run_id)
            else:
                raise AssertionError("Expected replacement refusal or the controlled cleanup interruption")
        if replace:
            assert changed and attempts == (1 if after_open else 0)
            if not after_open:
                assert (root / "runs/original/original").read_text() == "keep this run"
            matches = list((root / "runs").rglob("sentinel"))
            assert sorted(path.read_text() for path in matches) == ["other run", "unexpected replacement"]
        else:
            assert attempts == 2 and not directory.exists()
            assert list((root / "runs").iterdir()) == [root / "runs/unrelated"]
        assert (root / "runs/unrelated/sentinel").read_text() == "other run"


def cleanup_marker_interruption(*, before_write: bool, foreign: bool = False, partial: bool = False) -> None:
    with TemporaryDirectory() as temporary:
        root = Path(temporary).resolve() / "runtime"
        prepare(root)
        run_id = "123456789abc"
        directory = root / "runs" / run_id
        directory.mkdir(mode=0o700)
        runtime.write_new(
            directory / "intent.json",
            {
                "owner": runtime.identity(directory),
                "name": "openai-desktop-" + run_id,
                "nonce": "fixture",
                "image": IMAGE,
            },
        )
        (directory / "container-id").write_text(CONTAINER)
        cleanup = root / "runs" / (".cleanup-" + run_id)
        marker = cleanup / "owner.json"
        real_write = runtime.write_new
        real_rmdir = Path.rmdir
        interrupted = False
        lookups = 0

        def docker(_root: Path, args: list[str], **_kwargs: Any) -> bytes:
            nonlocal lookups
            assert args[0] == "ps"
            lookups += 1
            return b""

        def write(path: Path, value: object) -> None:
            nonlocal interrupted
            if before_write and path == marker and not interrupted:
                interrupted = True
                if partial:
                    with marker.open("x") as output:
                        os.fchmod(output.fileno(), 0o600)
                        output.write('{"path":')
                        output.flush()
                raise OSError("controlled marker interruption")
            real_write(path, value)

        def rmdir(path: Path) -> None:
            nonlocal interrupted
            if not before_write and path == cleanup and not interrupted:
                interrupted = True
                raise OSError("controlled marker interruption")
            real_rmdir(path)

        with (
            patch.object(runtime, "docker", side_effect=docker),
            patch.object(runtime, "write_new", side_effect=write),
            patch.object(Path, "rmdir", rmdir),
        ):
            try:
                runtime.remove(root, run_id)
            except OSError as error:
                assert "controlled marker interruption" in str(error)
            else:
                raise AssertionError("The controlled interruption was not reached")
            assert interrupted and marker.exists() is partial and directory.exists() is before_write
            if foreign:
                (cleanup / "sentinel").write_text("unexpected data")
                try:
                    runtime.remove(root, run_id)
                except (OSError, RuntimeError, ValueError):
                    pass
                else:
                    raise AssertionError("Nonempty markerless cleanup must remain unreconciled")
                assert (cleanup / "sentinel").read_text() == "unexpected data"
                assert lookups == 1 and directory.exists() is before_write
                if partial:
                    assert marker.read_text() == '{"path":'
            else:
                runtime.remove(root, run_id)
                assert lookups == (2 if before_write else 1)
                assert list((root / "runs").iterdir()) == [root / "runs/unrelated"]
            assert (root / "runs/unrelated/sentinel").read_text() == "other run"


def cleanup_deadline(*, hold_rm: bool) -> None:
    with TemporaryDirectory() as temporary:
        root = Path(temporary).resolve() / "runtime"
        prepare(root)
        driver = Docker(root, available=True, receipt=True)
        run_id = "e" * 12
        directory = root / "runs" / run_id
        directory.mkdir(mode=0o700)
        runtime.write_new(
            directory / "intent.json",
            {
                "owner": runtime.identity(directory),
                "name": "openai-desktop-" + run_id,
                "nonce": "f" * 48,
                "image": IMAGE,
            },
        )
        (directory / "container-id").write_text(CONTAINER)
        driver.directory = directory
        driver.create = driver.real_popen([sys.executable, "-c", "pass"])
        driver.create.wait()
        elapsed = 0.0
        held: subprocess.Popen[bytes] | None = None
        original_docker = runtime.docker

        def docker(command_root: Path, args: list[str], **kwargs: Any) -> bytes:
            nonlocal elapsed
            result = original_docker(command_root, args, **kwargs)
            elapsed += 6
            return result

        def popen(args: list[str], **kwargs: Any) -> subprocess.Popen[bytes]:
            nonlocal elapsed, held
            if hold_rm and args[5] == "rm" and held is None:
                driver.calls.append(args[5:])
                held = driver.real_popen([sys.executable, "-c", "import time;time.sleep(60)"], **kwargs)
                elapsed = 31
                return held
            return driver.popen(args, **kwargs)

        with (
            patch.object(runtime, "local_only", return_value="/unused/local-docker"),
            patch.object(runtime.subprocess, "Popen", side_effect=popen),
            patch.object(runtime, "time", SimpleNamespace(monotonic=lambda: elapsed)),
            patch.object(runtime, "docker", side_effect=docker),
        ):
            try:
                runtime.remove(root, run_id)
            except subprocess.TimeoutExpired:
                pass
            else:
                raise AssertionError("Cleanup ignored its aggregate budget")
            assert directory.is_dir() and (directory / "container-id").read_text() == CONTAINER
            assert [call[0] for call in driver.calls] == ["ps", "inspect", "ps", "inspect", "rm"]
            assert driver.removed is not hold_rm
            if hold_rm:
                assert held is not None and held.poll() is not None
        # A separate retry revalidates the receipt; it is not bound to the expired operation.
        with (
            patch.object(runtime, "local_only", return_value="/unused/local-docker"),
            patch.object(runtime.subprocess, "Popen", side_effect=driver.popen),
        ):
            runtime.remove(root, run_id)
        assert not directory.exists()
        assert (root / "runs/unrelated/sentinel").read_text() == "other run"


def startup_deadline(boundary: str | None) -> None:
    with TemporaryDirectory() as temporary:
        root = Path(temporary).resolve() / "runtime"
        prepare(root)
        driver = Docker(root, available=True, receipt=True, start_failure=True)
        elapsed = 0.0
        original_docker = runtime.docker

        def popen(args: list[str], **kwargs: Any) -> subprocess.Popen[bytes]:
            if args[5] == "start":
                driver.calls.append(args[5:])
                driver.started = True
                return driver.real_popen([sys.executable, "-c", "pass"], **kwargs)
            return driver.popen(args, **kwargs)

        def docker(command_root: Path, args: list[str], **kwargs: Any) -> bytes:
            nonlocal elapsed
            result = original_docker(command_root, args, **kwargs)
            if kwargs.get("cancelled") is not None:
                if boundary == "cumulative":
                    elapsed += 25
                elif args[0] == boundary:
                    elapsed = 60
                elif boundary == "caller" and args[0] == "start":
                    driver.cancelled = True
            return result

        with (
            patch.object(runtime, "local_only", return_value="/unused/local-docker"),
            patch.object(runtime.subprocess, "Popen", side_effect=popen),
            patch.object(runtime, "time", SimpleNamespace(monotonic=lambda: elapsed)),
            patch.object(runtime, "docker", side_effect=docker),
        ):
            if boundary is None:
                id = runtime.start(root, cancelled=driver.is_cancelled)
                assert driver.started and driver.directory == root / "runs" / id
                runtime.remove(root, id)
            else:
                try:
                    runtime.start(root, cancelled=driver.is_cancelled)
                except runtime.StartupCancelled:
                    pass
                else:
                    raise AssertionError(f"Startup returned after {boundary} exceeded its admission window")
            assert list((root / "runs").iterdir()) == [root / "runs/unrelated"]
            if boundary == "image":
                assert driver.directory is None
            else:
                assert driver.drained and driver.removed
            assert (root / "runs/unrelated/sentinel").read_text() == "other run"


def output_bounds(stream: str, cap: int) -> None:
    real_popen = subprocess.Popen[bytes]
    real_read = os.read
    with TemporaryDirectory() as temporary:
        root = Path(temporary).resolve() / "runtime"
        prepare(root)
        marker = root / "completed-excess"
        children: list[subprocess.Popen[bytes]] = []
        output_fds: set[int] = set()
        consumed = 0
        largest_read = 0

        def popen(_args: list[str], **kwargs: Any) -> subprocess.Popen[bytes]:
            target = 2 if stream == "stderr" else 1
            script = (
                "import os,sys;from pathlib import Path; "
                "chunk=b'x'*65536; "
                "[os.write(int(sys.argv[1]),chunk) for _ in range(int(sys.argv[2]))]; "
                "Path(sys.argv[3]).write_text('excess finished')"
            )
            child = real_popen(
                [sys.executable, "-c", script, str(target), str((cap * 8) // 65536 + 1), str(marker)], **kwargs
            )
            assert child.stdout is not None and child.stderr is not None
            output_fds.update((child.stdout.fileno(), child.stderr.fileno()))
            children.append(child)
            return child

        def bounded_read(fd: int, count: int) -> bytes:
            nonlocal consumed, largest_read
            result = real_read(fd, count)
            if fd in output_fds:
                consumed += len(result)
                largest_read = max(largest_read, count)
            return result

        with (
            patch.object(runtime, "local_only", return_value="/unused/local-docker"),
            patch.object(runtime.subprocess, "Popen", side_effect=popen),
            patch.object(runtime.os, "read", side_effect=bounded_read),
        ):
            try:
                runtime.docker(root, ["controlled-output"], limit=cap if stream != "stderr" else 65536)
            except RuntimeError as error:
                assert "exceeded" in str(error)
            else:
                raise AssertionError(f"{stream} exceeded its command output cap")
        assert len(children) == 1 and children[0].poll() is not None, f"{stream} child not reaped"
        assert not marker.exists(), f"{stream} excess was fully consumed before termination"
        assert consumed <= cap + 1 and largest_read <= 65536, (stream, consumed, largest_read)
        assert (root / "runs/unrelated/sentinel").read_text() == "other run"


def pipe_lifetimes() -> None:
    real_popen = subprocess.Popen[bytes]
    with TemporaryDirectory() as temporary:
        root = Path(temporary).resolve() / "runtime"
        prepare(root)
        closed = root / "closed"
        data = bytes(range(256)) * 2048
        scripts = {
            "duplex": (
                "import sys;sys.stderr.buffer.write(b'warn'*20000);sys.stderr.buffer.flush();"
                "sys.stdout.buffer.write(b'prefix'*15000);sys.stdout.buffer.flush();"
                "sys.stdout.buffer.write(sys.stdin.buffer.read())"
            ),
            "broken": "import os;os.close(0);os.write(1,b'closed stdin')",
            "eof": (
                "import os,sys,time;from pathlib import Path;"
                "os.close(1);os.close(2);Path(sys.argv[1]).write_text('closed');time.sleep(60)"
            ),
        }
        children: list[subprocess.Popen[bytes]] = []

        def popen(args: list[str], **kwargs: Any) -> subprocess.Popen[bytes]:
            child = real_popen([sys.executable, "-c", scripts[args[5]], str(closed)], **kwargs)
            children.append(child)
            return child

        with (
            patch.object(runtime, "local_only", return_value="/unused/local-docker"),
            patch.object(runtime.subprocess, "Popen", side_effect=popen),
        ):
            expected = b"prefix" * 15000 + data
            assert runtime.docker(root, ["duplex"], data=data, limit=len(expected)) == expected
            assert runtime.docker(root, ["broken"], data=data) == b"closed stdin"
            try:
                runtime.docker(root, ["eof"], timeout=2)
            except subprocess.TimeoutExpired:
                assert closed.exists()
            else:
                raise AssertionError("EOF with a live child skipped the deadline")
            closed.unlink()
            try:
                runtime.docker(root, ["eof"], cancelled=closed.exists)
            except runtime.StartupCancelled:
                assert closed.exists()
            else:
                raise AssertionError("EOF with a live child skipped cancellation")
        assert len(children) == 4 and all(child.poll() is not None for child in children)
        assert (root / "runs/unrelated/sentinel").read_text() == "other run"


def preflight_admission() -> None:
    def path_only_docker(_name: str, path: str | None = None) -> str | None:
        return "/fixture-only/docker" if path is None else None

    with TemporaryDirectory() as temporary:
        socket_path = str(Path(temporary) / "docker.sock")
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as daemon:
            daemon.bind(socket_path)
            with (
                patch.object(runtime.sys, "platform", "linux"),
                patch.object(platform, "machine", return_value="x86_64"),
                patch.object(runtime, "DOCKER_SOCKET", socket_path),
                patch.dict(os.environ, {}, clear=True),
                patch.object(runtime.shutil, "which", return_value="/usr/bin/docker"),
                patch.object(runtime, "docker", side_effect=AssertionError("Admission must not run Docker")),
            ):
                runtime.preflight()
                for variable in ("DOCKER_HOST", "DOCKER_CONTEXT", "BUILDX_BUILDER"):
                    with patch.dict(os.environ, {variable: "remote-fixture"}):
                        try:
                            runtime.preflight()
                        except ValueError:
                            pass
                        else:
                            raise AssertionError(f"Remote configuration admitted: {variable}")
                with patch.object(
                    runtime.shutil,
                    "which",
                    side_effect=path_only_docker,
                ):
                    try:
                        runtime.preflight()
                    except ValueError:
                        pass
                    else:
                        raise AssertionError("An arbitrary PATH-only Docker executable was admitted")


def cancelled_health(boundary: str, *, exchange: bool = False) -> None:
    with TemporaryDirectory() as temporary:
        root = Path(temporary).resolve() / "runtime"
        prepare(root)
        driver = Docker(root, available=True, receipt=True)
        id = "e" * 12
        directory = root / "runs" / id
        directory.mkdir(mode=0o700)
        runtime.write_new(
            directory / "intent.json",
            {
                "owner": runtime.identity(directory),
                "name": "openai-desktop-" + id,
                "nonce": "f" * 48,
                "image": IMAGE,
            },
        )
        (directory / "container-id").write_text(CONTAINER)
        driver.directory = directory
        # The already completed create is distinct from this held health read.
        driver.create = driver.real_popen([sys.executable, "-c", "pass"])
        driver.create.wait()
        held: subprocess.Popen[bytes] | None = None
        elapsed = 0.0
        original_docker = runtime.docker

        def docker(command_root: Path, args: list[str], **kwargs: Any) -> bytes:
            nonlocal elapsed
            result = original_docker(command_root, args, **kwargs)
            if boundary == "cumulative":
                elapsed += 0.11 if exchange else 31
            return result

        def popen(args: list[str], **kwargs: Any) -> subprocess.Popen[bytes]:
            nonlocal held
            if args[5] == boundary and held is None:
                driver.calls.append(args[5:])
                held = driver.real_popen([sys.executable, "-c", "import time;time.sleep(60)"], **kwargs)
                driver.cancelled = not exchange
                return held
            return driver.popen(args, **kwargs)

        with (
            patch.object(runtime, "local_only", return_value="/unused/local-docker"),
            patch.object(runtime.subprocess, "Popen", side_effect=popen),
            patch.object(runtime, "docker", side_effect=docker),
        ):
            try:
                if boundary == "cumulative":
                    with patch.object(runtime, "time", SimpleNamespace(monotonic=lambda: elapsed)):
                        if exchange:
                            runtime.exchange(root, id, b'{"action":"verify"}\n', timeout=0.2, limit=65536)
                        else:
                            runtime.healthy(root, id, cancelled=driver.is_cancelled)
                elif exchange:
                    runtime.exchange(root, id, b'{"action":"verify"}\n', timeout=0.2, limit=65536)
                else:
                    runtime.healthy(root, id, cancelled=driver.is_cancelled)
            except subprocess.TimeoutExpired:
                assert exchange or boundary == "cumulative"
                if boundary == "cumulative":
                    assert held is None and all(call[0] != "exec" for call in driver.calls)
                    if not exchange:
                        assert all(call[0] != "inspect" for call in driver.calls)
                else:
                    assert held is not None and held.poll() is not None
            except runtime.StartupCancelled:
                assert not exchange and held is not None and held.poll() is not None
            else:
                raise AssertionError("A stopped health lookup returned a ready guest")
            before_remove = (directory.exists(), driver.removed)
            assert before_remove == (True, False)
            # Remove verifies this exact ID and ignores the Stop that interrupted admission.
            runtime.remove(root, id)
        assert driver.removed and not directory.exists()
        assert (root / "runs/unrelated/sentinel").read_text() == "other run"


def setup_snapshot(changed: str | None) -> None:
    with TemporaryDirectory() as temporary:
        area = Path(temporary)
        sources = area / "source"
        sources.mkdir()
        inputs: dict[str, Path] = {}
        for name, source in runtime.FILES.items():
            inputs[name] = sources / name
            shutil.copyfile(source, inputs[name])
        root = area / "runtime"
        docker_calls: list[list[str]] = []
        original_copy = shutil.copyfile

        def copying(src: Path, dest: Path) -> str:
            result = original_copy(src, dest)
            if changed == "copy-" + dest.name:
                dest.write_bytes(b"altered synthetic copy")
            return str(result)

        def docker(_root: Path, args: list[str], **_kwargs: Any) -> bytes:
            docker_calls.append(args)
            assert args[0] == "build"
            context = root / "build/context"
            assert {name: runtime.digest(context / name) for name in inputs} == initial
            if changed == "build-context":
                (context / "Dockerfile").write_bytes(b"changed while mocked build ran")
            if changed == "build-checkout":
                inputs["start.py"].write_bytes(b"changed while mocked build ran")
            Path(args[args.index("--iidfile") + 1]).write_text(IMAGE)
            return b""

        with (
            patch.object(runtime, "FILES", inputs),
            patch.object(runtime, "local_only", return_value="/unused/local-docker"),
            patch.object(runtime.shutil, "copyfile", side_effect=copying),
            patch.object(runtime, "docker", side_effect=docker),
        ):
            initial = runtime.recipe()
            if changed is None:
                runtime.setup(root)
                assert runtime.runtime(root)["recipe"] == initial
            else:
                try:
                    runtime.setup(root)
                except ValueError:
                    pass
                else:
                    raise AssertionError("Setup published a receipt for changed provisioning")
                assert not (root / "setup.json").exists()
            assert len(docker_calls) == (0 if changed and changed.startswith("copy-") else 1)


def runtime_paths() -> None:
    with TemporaryDirectory(prefix="desktop-paths-") as temporary:
        parent = Path(temporary).resolve()
        root = parent / "runtime"
        prepare(root)
        parent.chmod(0o777)
        try:
            with patch.object(runtime, "local_only", side_effect=AssertionError("Untrusted path reached Docker")):
                for operation, path in (
                    (runtime.setup, parent / "fresh"),
                    (runtime.setup, root),
                    (runtime.start, root),
                ):
                    try:
                        operation(path)
                    except ValueError as exc:
                        assert "ancestor" in str(exc)
                    else:
                        raise AssertionError("Container admitted a writable runtime ancestor")
            assert not (parent / "fresh").exists()
        finally:
            parent.chmod(0o700)
        alias = parent / "runtime-link"
        alias.symlink_to(root, target_is_directory=True)
        value = runtime.runtime(alias)
        assert value["owner"]["path"] == str(root)
        with patch.object(runtime, "check_image") as inspect:
            runtime.setup(alias)
            inspect.assert_called_once_with(root, value)
        with patch.object(runtime, "check_image", side_effect=RuntimeError("stop at checked image")) as inspect:
            try:
                runtime.start(alias)
            except RuntimeError as exc:
                assert str(exc) == "stop at checked image"
            else:
                raise AssertionError("Test image refusal was ignored")
            assert inspect.call_args.args == (root, value)
        assert (root / "runs/unrelated/sentinel").read_text() == "other run"
        foreign = parent / "other"
        prepare(foreign)
        id = "0123456789ab"
        cleanup = ".cleanup-" + id
        (root / "runs" / cleanup).mkdir(mode=0o700)
        (foreign / "runs" / cleanup).mkdir(mode=0o700)
        verify = runtime.runtime

        def swap_after_receipt(path: Path) -> dict[str, Any]:
            result = verify(path)
            alias.unlink()
            alias.symlink_to(foreign, target_is_directory=True)
            return result

        with patch.object(runtime, "runtime", side_effect=swap_after_receipt):
            runtime.remove(alias, id)
        assert not (root / "runs" / cleanup).exists(), "Recovery must finish on the verified root"
        assert (foreign / "runs" / cleanup).is_dir(), "Alias redirection must not remove another root"
        assert (foreign / "runs/unrelated/sentinel").read_text() == "other run"


def main() -> None:
    runtime_paths()
    preflight_admission()
    startup_failure()
    create_cancelled_before_launch(timeout=False)
    create_cancelled_before_launch(timeout=True)
    for boundary in ("missing", "partial", "sync", "chmod", "signal", "directory", "file"):
        initial_intent_failure(boundary)
    cleanup_replacement(replace=True)
    cleanup_replacement(replace=True, after_move=True)
    cleanup_replacement(replace=True, after_open=True)
    cleanup_replacement(replace=False)
    cleanup_marker_interruption(before_write=True)
    cleanup_marker_interruption(before_write=False)
    cleanup_marker_interruption(before_write=True, foreign=True)
    cleanup_marker_interruption(before_write=True, partial=True)
    cleanup_marker_interruption(before_write=True, partial=True, foreign=True)
    cleanup_deadline(hold_rm=False)
    cleanup_deadline(hold_rm=True)
    for boundary in (None, "image", "create", "inspect", "start", "cumulative", "caller"):
        startup_deadline(boundary)
    for changed in (None, "copy-Dockerfile", "copy-seccomp.json", "build-context", "build-checkout"):
        setup_snapshot(changed)
    for boundary in ("ps", "inspect"):
        cancelled_health(boundary)
        cancelled_health(boundary, exchange=True)
    cancelled_health("cumulative", exchange=True)
    cancelled_health("cumulative")
    for stream, cap in (("stdout", 65536), ("build", 4 * 1024 * 1024), ("stderr", 1024 * 1024)):
        output_bounds(stream, cap)
    pipe_lifetimes()
    with patch.object(runtime.sys, "platform", "linux"), patch.object(platform, "machine", return_value="aarch64"):
        try:
            runtime.local_only()
        except ValueError as error:
            assert "x86-64" in str(error)
        else:
            raise AssertionError("Unsupported ARM host reached Docker lookup")
    for available, receipt in ((False, False), (True, False), (True, True)):
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve() / "runtime"
            prepare(root)
            driver = Docker(root, available=available, receipt=receipt)
            with (
                patch.object(runtime, "local_only", return_value="/unused/local-docker"),
                patch.object(runtime.subprocess, "Popen", side_effect=driver.popen),
            ):
                if not available:
                    for operation in (runtime.preflight, runtime.setup, runtime.start):
                        try:
                            operation(root)
                        except RuntimeError:
                            pass
                        else:
                            raise AssertionError("Missing image admitted setup or startup")
                    assert all(call[0] == "image" for call in driver.calls)
                    assert list((root / "runs").iterdir()) == [root / "runs/unrelated"]
                else:
                    runtime.preflight(root)
                    assert all(call[0] == "image" for call in driver.calls)
                    try:
                        runtime.start(root, cancelled=driver.is_cancelled)
                    except runtime.StartupCancelled:
                        assert receipt
                    except RuntimeError as error:
                        assert not receipt and "indeterminate" in str(error)
                    else:
                        raise AssertionError("Stopped creation returned an active guest")
                    assert driver.drained and driver.directory is not None
                    assert driver.removed is receipt
                    assert driver.directory.exists() is not receipt
            assert (root / "runs/unrelated/sentinel").read_text() == "other run"
    print(
        "PASS bounded stdout/build/stderr reads, duplex and broken stdin, EOF cancellation/deadline, "
        "Linux ARM guard, missing image, cancelled create reaped, known CID removed, ambiguous intent and sentinel retained"
    )


if __name__ == "__main__":
    main()
